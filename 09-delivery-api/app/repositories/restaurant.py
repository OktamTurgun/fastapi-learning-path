import uuid
from sqlalchemy import select
from sqlalchemy.orm import selectinload
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
        return await self.get(obj.id)

    async def get(self, id) -> Restaurant | None:
        if isinstance(id, str):
            try:
                id = uuid.UUID(id)
            except ValueError:
                return None
        stmt = select(Restaurant).where(Restaurant.id == id).options(selectinload(Restaurant.menu_items))
        result = await self.session.execute(stmt)
        return result.scalars().first()

class OrderItemRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_bulk(self, items: list[dict]) -> list[OrderItem]:
        objs = [OrderItem(**item) for item in items]
        self.session.add_all(objs)
        await self.session.flush()
        return objs   