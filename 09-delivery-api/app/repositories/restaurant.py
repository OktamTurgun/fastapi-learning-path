from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.restaurant import OrderItem, Restaurant, MenuItem

class MenuItemRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_ids(self, ids: list) -> list[MenuItem]:
        stmt = select(MenuItem).where(MenuItem.id.in_(ids))
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def add(self, **kwargs) -> MenuItem:
        obj = MenuItem(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        return obj


class RestaurantRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def add(self, **kwargs) -> Restaurant:
        obj = Restaurant(**kwargs)
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def get(self, id) -> Restaurant | None:
        return await self.session.get(Restaurant, id)

class OrderItemRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_bulk(self, items: list[dict]) -> list[OrderItem]:
        objs = [OrderItem(**item) for item in items]
        self.session.add_all(objs)
        await self.session.flush()
        return objs   