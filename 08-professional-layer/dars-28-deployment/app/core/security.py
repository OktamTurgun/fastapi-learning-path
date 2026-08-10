from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt  # type: ignore[import]
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict) -> str:
    """JWT token yaratish — settings'dan parametrlar olinadi"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """Token'ni tekshirish va ichidagi ma'lumotni olish"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def hash_password(password: str) -> str:
    """Parolni xeshlash — ro'yxatdan o'tishda ishlatiladi"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiritilgan parolni saqlangan xesh bilan solishtirish — login'da ishlatiladi"""
    return pwd_context.verify(plain_password, hashed_password)
