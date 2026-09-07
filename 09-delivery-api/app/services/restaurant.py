from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.restaurant import Restaurant, MenuItem
from app.repositories.restaurant import RestaurantRepository, MenuItemRepository
from app.schemas.restaurant import RestaurantCreate, MenuItemCreate


class RestaurantService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.restaurant_repo = RestaurantRepository(session)
        self.menu_item_repo = MenuItemRepository(session)

    async def create_restaurant(self, data: RestaurantCreate) -> Restaurant:
        restaurant = await self.restaurant_repo.add(**data.model_dump())
        return restaurant

    async def add_menu_item(self, restaurant_id: UUID, data: MenuItemCreate) -> MenuItem:
        restaurant = await self.restaurant_repo.get(restaurant_id)
        if not restaurant:
            raise ValueError("Restoran topilmadi")

        menu_item = await self.menu_item_repo.add(
            restaurant_id=restaurant_id,
            **data.model_dump(),
        )
        return menu_item

    async def get_restaurant(self, restaurant_id: UUID) -> Restaurant:
        restaurant = await self.restaurant_repo.get(restaurant_id)
        if not restaurant:
            raise ValueError("Restoran topilmadi")
        return restaurant
