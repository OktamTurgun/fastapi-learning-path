from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    name: str
    price: float
    quantity: int = 0
    in_stock: bool = True
    category_id: int


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    quantity: int | None = None
    in_stock: bool | None = None
    category_id: int | None = None


class ProductResponse(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class PaginatedProducts(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[ProductResponse]