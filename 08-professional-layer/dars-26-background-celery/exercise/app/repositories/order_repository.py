from typing import List, Optional, Tuple

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order
from app.schemas.order import OrderCreate, OrderUpdate
from app.repositories.base import AbstractRepository

ALLOWED_SORT_FIELDS = {"id", "total_amount", "status"}


class SQLAlchemyOrderRepository(AbstractRepository[Order, OrderCreate, OrderUpdate]):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, id: int) -> Optional[Order]:
        result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.customer))
            .where(Order.id == id)
        )
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> List[Order]:
        result = await self.db.execute(
            select(Order).options(selectinload(Order.customer)).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def list_filtered(
            self,
            skip: int = 0,
            limit: int = 10,
            search: Optional[str] = None,
            min_total: Optional[float] = None,
            max_total: Optional[float] = None,
            status: Optional[str] = None,
            sort_by: str = "id",
            order: str = "asc",
    ) -> Tuple[List[Order], int]:
        query = select(Order).options(selectinload(Order.customer))

        if search:
            query = query.where(Order.delivery_address.ilike(f"%{search}%"))
        if min_total is not None:
            query = query.where(Order.total_amount >= min_total)
        if max_total is not None:
            query = query.where(Order.total_amount <= max_total)
        if status is not None:
            query = query.where(Order.status == status)

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.db.execute(count_query)).scalar_one()

        if sort_by not in ALLOWED_SORT_FIELDS:
            sort_by = "id"
        sort_column = getattr(Order, sort_by)
        if order == "desc":
            sort_column = sort_column.desc()

        query = query.order_by(sort_column).offset(skip).limit(limit)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return items, total

    async def create(self, data: OrderCreate) -> Order:
        order = Order(**data.model_dump())
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        # refresh'dan keyin customer'ni to'liq yuklash uchun get() chaqiramiz
        return await self.get(order.id)

    async def update(self, id: int, data: OrderUpdate) -> Optional[Order]:
        order = await self.get(id)
        if not order:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(order, key, value)
        await self.db.commit()
        await self.db.refresh(order)
        return await self.get(id)

    async def delete(self, id: int) -> bool:
        order = await self.get(id)
        if not order:
            return False
        await self.db.delete(order)
        await self.db.commit()
        return True