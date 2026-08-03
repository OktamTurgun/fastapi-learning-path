from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional

from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, PaginatedProducts
from app.core.dependencies import (
    get_current_active_user,
    get_product_repository,
    get_product_service,
    require_role,
)
from app.models.user import User, UserRole
from app.services.product_service import ProductService
from app.repositories.product_repository import SQLAlchemyProductRepository

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product: ProductCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN, UserRole.MANAGER)),
    service: ProductService = Depends(get_product_service),
):
    return await service.create_product(product)


@router.get("/", response_model=PaginatedProducts)
async def read_products(
    skip: int = Query(0, ge=0, description="Nechta yozuvni o'tkazib yuborish"),
    limit: int = Query(10, ge=1, le=100, description="Nechta yozuv qaytarish"),
    search: Optional[str] = Query(None, description="Mahsulot nomi bo'yicha qidiruv"),
    category_id: Optional[int] = Query(None, description="Kategoriya bo'yicha filtr"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimal narx"),
    max_price: Optional[float] = Query(None, ge=0, description="Maksimal narx"),
    sort_by: str = Query("id", description="Saralash ustuni: id, name, price, quantity"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="asc yoki desc"),
    product_repo: SQLAlchemyProductRepository = Depends(get_product_repository),
):
    items, total = await product_repo.list_filtered(
        skip=skip, limit=limit, search=search,
        category_id=category_id, min_price=min_price, max_price=max_price,
        sort_by=sort_by, order=order,
    )
    return PaginatedProducts(total=total, skip=skip, limit=limit, items=items)


@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(
    product_id: int,
    product_repo: SQLAlchemyProductRepository = Depends(get_product_repository),
):
    db_product = await product_repo.get(product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    return db_product


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    service: ProductService = Depends(get_product_service),
):
    return await service.update_product(product_id, product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: User = Depends(require_role(UserRole.ADMIN)),  # <- faqat admin
    service: ProductService = Depends(get_product_service),
):
    await service.delete_product(product_id)