from app.repositories.user import UserRepository, RoleRepository
from app.schemas.user import UserCreate
from app.core.security import hash_password

class UserService:
    def __init__(self, session):
        self.user_repo = UserRepository(session)
        self.role_repo = RoleRepository(session)

    async def register(self, data: UserCreate):
        existing = await self.user_repo.get_by_email(data.email)
        if existing:
            raise ValueError("Email allaqachon ro'yxatdan o'tgan")

        hashed = hash_password(data.password)

        user = await self.user_repo.add(
            email=data.email,
            full_name=data.full_name,
            hashed_password=hashed,
        )

        customer_role = await self.role_repo.get_by_name("customer")
        if not customer_role:
            raise ValueError("'customer' roli topilmadi — DB seed qilinmagan")

        await self.user_repo.assign_role(user, customer_role)

        return user