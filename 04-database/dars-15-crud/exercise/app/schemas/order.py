from pydantic import BaseModel, ConfigDict
from app.schemas.customer import CustomerResponse


class OrderBase(BaseModel):
    total_amount: float
    status: str = "pending"
    delivery_address: str | None = None
    customer_id: int


class OrderCreate(OrderBase):
    pass


class OrderUpdate(BaseModel):
    total_amount: float | None = None
    status: str | None = None
    delivery_address: str | None = None
    customer_id: int | None = None


class OrderResponse(BaseModel):
    id: int
    total_amount: float
    status: str
    delivery_address: str | None
    customer: CustomerResponse   # <- nested schema (bonus)

    model_config = ConfigDict(from_attributes=True)