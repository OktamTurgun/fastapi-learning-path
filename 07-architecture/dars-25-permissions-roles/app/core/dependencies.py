from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import oauth2_scheme, decode_access_token
from app.crud import user as crud_user
from app.models.user import User

from app.repositories.product_repository import SQLAlchemyProductRepository
from app.repositories.category_repository import SQLAlchemyCategoryRepository
from app.services.product_service import ProductService

from typing import List
from app.models.user import User, UserRole


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Kirish huquqi tasdiqlanmadi",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = await crud_user.get_user_by_id(db, int(user_id))
    if user is None:
        raise credentials_exception

    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Foydalanuvchi faol emas")
    return current_user


def get_product_repository(db: AsyncSession = Depends(get_db)) -> SQLAlchemyProductRepository:
    return SQLAlchemyProductRepository(db)


def get_category_repository(db: AsyncSession = Depends(get_db)) -> SQLAlchemyCategoryRepository:
    return SQLAlchemyCategoryRepository(db)


def get_product_service(
    product_repo: SQLAlchemyProductRepository = Depends(get_product_repository),
    category_repo: SQLAlchemyCategoryRepository = Depends(get_category_repository),
) -> ProductService:
    return ProductService(product_repo, category_repo)

def require_role(*allowed_roles: UserRole):
    """
    Factory function — ruxsat berilgan rollar ro'yxatini qabul qiladi
    va shu rollarni tekshiradigan dependency function qaytaradi.

    Ishlatilishi: Depends(require_role(UserRole.ADMIN, UserRole.MANAGER))
    """
    async def role_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bu amal uchun ruxsat yo'q. Talab qilinadi: {[r.value for r in allowed_roles]}",
            )
        return current_user
    return role_checker