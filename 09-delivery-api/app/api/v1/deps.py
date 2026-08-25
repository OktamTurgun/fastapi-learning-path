from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.core.database import get_db
from app.core.config import settings
from app.repositories.user import UserRepository
from app.models.user import User
from app.services.user import UserService
from app.services.order import OrderService

# tokenUrl — bu Swagger UI'da "Authorize" tugmasi bosganda qaysi endpoint'ga borishini ko'rsatadi
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_user_service(session: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(session)


async def get_order_service(session: AsyncSession = Depends(get_db)) -> OrderService:
    return OrderService(session)


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_db),
) -> User:
    """
    JWT token'ni tekshirib, joriy foydalanuvchini qaytaradi.

    - Authorization: Bearer <token> header'dan tokenni oladi
    - Token'ni decode qilib, 'sub' (user_id) ni chiqarib oladi
    - Bazadan foydalanuvchini topadi va qaytaradi
    - Xato bo'lsa → 401 Unauthorized
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token tekshirib bo'lmadi",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_repo = UserRepository(session)
    user = await user_repo.get(user_id)
    if user is None:
        raise credentials_exception

    return user