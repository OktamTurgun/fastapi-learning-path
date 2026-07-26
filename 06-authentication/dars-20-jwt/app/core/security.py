from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt  # type: ignore[import]

SECRET_KEY = "your-secret-key-CHANGE-THIS-IN-PRODUCTION"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict) -> str:
    """JWT token yaratish — login muvaffaqiyatli bo'lganda chaqiriladi"""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """Token'ni tekshirish va ichidagi ma'lumotni olish"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def hash_password(password: str) -> str:
    """Parolni xeshlash — ro'yxatdan o'tishda ishlatiladi"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiritilgan parolni saqlangan xesh bilan solishtirish — login'da ishlatiladi"""
    return pwd_context.verify(plain_password, hashed_password)