from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import hash_password


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user: UserCreate) -> User:
    hashed = hash_password(user.password)   # <- parol shu yerda xeshlanadi
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user