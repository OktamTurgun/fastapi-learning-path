"""
SQLAlchemyProductRepository — AbstractRepository interfeysining
haqiqiy, SQLAlchemy bilan ishlaydigan implementatsiyasi.
"""

from typing import List, Optional, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.repositories.base import AbstractRepository

ALLOWED_SORT_FIELDS = {"id", "name", "price", "quantity"}


class SQLAlchemyProductRepository(AbstractRepository[Product, ProductCreate, ProductUpdate]):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, id: int) -> Optional[Product]:
        result = await self.db.execute(select(Product).where(Product.id == id))
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> List[Product]:
        result = await self.db.execute(select(Product).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def list_filtered(
        self,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        sort_by: str = "id",
        order: str = "asc",
    ) -> Tuple[List[Product], int]:
        query = select(Product)
        if search:
            query = query.where(Product.name.ilike(f"%{search}%"))
        if category_id is not None:
            query = query.where(Product.category_id == category_id)
        if min_price is not None:
            query = query.where(Product.price >= min_price)
        if max_price is not None:
            query = query.where(Product.price <= max_price)

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()

        if sort_by not in ALLOWED_SORT_FIELDS:
            sort_by = "id"
        sort_column = getattr(Product, sort_by)
        if order == "desc":
            sort_column = sort_column.desc()

        query = query.order_by(sort_column).offset(skip).limit(limit)
        result = await self.db.execute(query)
        items = result.scalars().all()
        return list(items), total

    async def create(self, data: ProductCreate) -> Product:
        db_product = Product(**data.model_dump())
        self.db.add(db_product)
        await self.db.commit()
        await self.db.refresh(db_product)
        return db_product

    async def update(self, id: int, data: ProductUpdate) -> Optional[Product]:
        db_product = await self.get(id)
        if not db_product:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_product, key, value)
        await self.db.commit()
        await self.db.refresh(db_product)
        return db_product

    async def delete(self, id: int) -> bool:
        db_product = await self.get(id)
        if not db_product:
            return False
        await self.db.delete(db_product)
        await self.db.commit()
        return True