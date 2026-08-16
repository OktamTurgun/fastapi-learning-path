from typing import Annotated, Union, Literal
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from app.models.order import OrderStatus


class OrderBaseRead(BaseModel):
    id: UUID
    customer_id: UUID
    status: OrderStatus
    total_price: float
    created_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy obyektidan to'g'ridan-to'g'ri o'qish uchun

class FoodOrderRead(OrderBaseRead):
    order_type: Literal["food"] = "food"
    restaurant_id: UUID
    delivery_address: str

class ParcelOrderRead(OrderBaseRead):
    order_type: Literal["parcel"] = "parcel"
    weight_kg: float
    pickup_address: str
    dropoff_address: str

class FoodOrderCreate(BaseModel):
    order_type: Literal["food"] = "food"
    restaurant_id: UUID
    delivery_address: str
    total_price: float

class ParcelOrderCreate(BaseModel):
    order_type: Literal["parcel"] = "parcel"
    weight_kg: float
    pickup_address: str
    dropoff_address: str

OrderCreate = Annotated[
    Union[FoodOrderCreate, ParcelOrderCreate],
    Field(discriminator="order_type"),
]      