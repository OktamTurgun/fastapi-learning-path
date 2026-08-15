from typing import Generic, TypeVar, Type
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import FoodOrder, ParcelOrder

T = TypeVar("T")  # T — "har qanday model turi" degani

class BaseOrderRepository(Generic[T]):
    model: Type[T]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, **kwargs) -> T:
        obj = self.model(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def get(self, id) -> T | None:
        return await self.session.get(self.model, id)

    async def list(self) -> list[T]:
        stmt = select(self.model)
        result = await self.session.execute(stmt)
        return result.scalars().all()


class FoodOrderRepository(BaseOrderRepository[FoodOrder]):
    model = FoodOrder


class ParcelOrderRepository(BaseOrderRepository[ParcelOrder]):
    model = ParcelOrder