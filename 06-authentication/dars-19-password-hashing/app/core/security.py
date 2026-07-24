from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Parolni xeshlash — ro'yxatdan o'tishda ishlatiladi"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Kiritilgan parolni saqlangan xesh bilan solishtirish — login'da ishlatiladi"""
    return pwd_context.verify(plain_password, hashed_password)