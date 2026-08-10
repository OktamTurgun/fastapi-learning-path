from fastapi import HTTPException, status
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate
from app.core.security import hash_password, verify_password, create_access_token
from app.tasks import send_welcome_email


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def register(self, user_in: UserCreate):
        existing = await self.repo.get_by_email(user_in.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bu email bilan foydalanuvchi allaqachon mavjud"
            )
        
        user_data = user_in.model_dump()
        user_data["hashed_password"] = hash_password(user_data.pop("password"))
        user = await self.repo.create(user_data)
        
        # Async background task: send welcome email via Celery
        # Broker mavjud bo'lmasa (test/dev muhitda) xatolik bermaslik uchun
        try:
            send_welcome_email.delay(user.email)
        except Exception:
            pass  # Redis/Celery ishlamasa ham registration muvaffaqiyatli bo'ladi

        return user

    async def authenticate(self, email: str, password: str) -> str:
        user = await self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email yoki parol noto'g'ri",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Foydalanuvchi akkaunti faol emas"
            )
        
        access_token = create_access_token(data={"sub": user.email, "role": user.role.value})
        return access_token
