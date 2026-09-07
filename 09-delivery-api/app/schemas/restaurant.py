from pydantic import BaseModel
import uuid
from uuid import UUID


class MenuItemRead(BaseModel):
    id: uuid.UUID
    restaurant_id: UUID
    name: str
    price: float
    is_available: bool
    class Config:
        from_attributes = True

class MenuItemCreate(BaseModel):
    name: str
    price: float
    is_available: bool = True

class RestaurantRead(BaseModel):
    id: UUID
    name: str
    address: str
    is_active: bool
    menu_items: list[MenuItemRead] = []
    class Config:
        from_attributes = True

class RestaurantCreate(BaseModel):
    name: str
    address: str
    is_active: bool = True

class OrderItemRead(BaseModel):
    id: UUID
    food_order_id: UUID
    menu_item_id: UUID
    quantity: int
    unit_price: float
    class Config:
        from_attributes = True

class OrderItemCreate(BaseModel):
    menu_item_id: UUID
    quantity: int