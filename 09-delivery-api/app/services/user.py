from uuid import UUID
from app.repositories.user import UserRepository, RoleRepository
from app.schemas.user import UserCreate, UserRole
from app.core.security import hash_password, verify_password
from app.core.config import settings
from app.models.user import User

class UserService:
    def __init__(self, session):
        self.user_repo = UserRepository(session)
        self.role_repo = RoleRepository(session)

    async def register(self, data: UserCreate):
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise ValueError("Email allaqachon ro'yxatdan o'tgan")

        # Admin roliga xavfsizlik tekshiruvi
        if data.role == UserRole.ADMIN:
            if not data.admin_secret or data.admin_secret != settings.admin_secret_key:
                raise ValueError(
                    "Admin sifatida ro'yxatdan o'tish uchun maxfiy kalit (admin_secret) noto'g'ri yoki ko'rsatilmagan"
                )

        target_role = await self.role_repo.get_by_name(data.role.value)
        if not target_role:
            raise ValueError(f"'{data.role.value}' roli topilmadi — DB seed qilinmagan")

        hashed = hash_password(data.password)

        user = await self.user_repo.add(
            email=data.email,
            full_name=data.full_name,
            hashed_password=hashed,
        )

        await self.user_repo.assign_role(user, target_role)

        # Aniq eager-loading bilan qaytadan olish — roles kafolatli to'g'ri keladi
        return await self.user_repo.get_with_roles(user.id)

    async def assign_role_to_user(self, user_id: UUID, role_name: str) -> User:
        user = await self.user_repo.get(user_id)
        if not user:
            raise ValueError("Foydalanuvchi topilmadi")

        target_role = await self.role_repo.get_by_name(role_name)
        if not target_role:
            raise ValueError(f"'{role_name}' roli topilmadi")

        await self.user_repo.assign_role(user, target_role)
        return await self.user_repo.get_with_roles(user.id)

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise ValueError("Email yoki parol noto'g'ri")

        if not verify_password(password, user.hashed_password):
            raise ValueError("Email yoki parol noto'g'ri")

        return user