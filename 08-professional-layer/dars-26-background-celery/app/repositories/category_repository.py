"""
SQLAlchemyCategoryRepository — AbstractRepository interfeysining
Category uchun implementatsiyasi.
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.repositories.base import AbstractRepository


class SQLAlchemyCategoryRepository(AbstractRepository[Category, CategoryCreate, CategoryUpdate]):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, id: int) -> Optional[Category]:
        result = await self.db.execute(select(Category).where(Category.id == id))
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> List[Category]:
        result = await self.db.execute(select(Category).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, data: CategoryCreate) -> Category:
        db_category = Category(**data.model_dump())
        self.db.add(db_category)
        await self.db.commit()
        await self.db.refresh(db_category)
        return db_category

    async def update(self, id: int, data: CategoryUpdate) -> Optional[Category]:
        db_category = await self.get(id)
        if not db_category:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_category, key, value)
        await self.db.commit()
        await self.db.refresh(db_category)
        return db_category

    async def delete(self, id: int) -> bool:
        db_category = await self.get(id)
        if not db_category:
            return False
        await self.db.delete(db_category)
        await self.db.commit()
        return True