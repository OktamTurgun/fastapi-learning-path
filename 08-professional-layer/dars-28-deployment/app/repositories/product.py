from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models.product import Product
from app.repositories.base import BaseRepository


class ProductRepository(BaseRepository[Product]):
    def __init__(self, db: AsyncSession):
        super().__init__(Product, db)

    async def get_all_with_category(self, skip: int = 0, limit: int = 100):
        stmt = select(Product).options(selectinload(Product.category)).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_by_id_with_category(self, id: int):
        stmt = select(Product).options(selectinload(Product.category)).where(Product.id == id)
        result = await self.db.execute(stmt)
        return result.scalars().first()
