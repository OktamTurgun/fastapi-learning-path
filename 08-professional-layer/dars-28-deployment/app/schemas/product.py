from pydantic import BaseModel, ConfigDict
from app.schemas.category import CategoryResponse


class ProductCreate(BaseModel):
    title: str
    price: float
    description: str | None = None
    category_id: int


class ProductUpdate(BaseModel):
    title: str | None = None
    price: float | None = None
    description: str | None = None
    category_id: int | None = None


class ProductResponse(BaseModel):
    id: int
    title: str
    price: float
    description: str | None = None
    category_id: int
    category: CategoryResponse | None = None

    model_config = ConfigDict(from_attributes=True)
