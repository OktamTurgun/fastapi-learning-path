from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.repositories.product import ProductRepository
from app.services.product import ProductService
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.routers.user import require_roles
from app.models.user import UserRole

router = APIRouter(prefix="/products", tags=["Products"])


def get_product_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    repo = ProductRepository(db)
    return ProductService(repo)


@router.get("", response_model=List[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    service: ProductService = Depends(get_product_service)
):
    return await service.get_products(skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    service: ProductService = Depends(get_product_service)
):
    return await service.get_product(product_id)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER]))]
)
async def create_product(
    prod_in: ProductCreate,
    service: ProductService = Depends(get_product_service)
):
    return await service.create_product(prod_in)


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER]))]
)
async def update_product(
    product_id: int,
    prod_in: ProductUpdate,
    service: ProductService = Depends(get_product_service)
):
    return await service.update_product(product_id, prod_in)


@router.delete(
    "/{product_id}",
    dependencies=[Depends(require_roles([UserRole.ADMIN]))]
)
async def delete_product(
    product_id: int,
    service: ProductService = Depends(get_product_service)
):
    return await service.delete_product(product_id)
