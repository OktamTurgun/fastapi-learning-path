from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.repositories.category import CategoryRepository
from app.services.category import CategoryService
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.routers.user import require_roles
from app.models.user import UserRole

router = APIRouter(prefix="/categories", tags=["Categories"])


def get_category_service(db: AsyncSession = Depends(get_db)) -> CategoryService:
    repo = CategoryRepository(db)
    return CategoryService(repo)


@router.get("", response_model=List[CategoryResponse])
async def list_categories(
    skip: int = 0,
    limit: int = 100,
    service: CategoryService = Depends(get_category_service)
):
    return await service.get_categories(skip=skip, limit=limit)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service)
):
    return await service.get_category(category_id)


@router.post(
    "",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER]))]
)
async def create_category(
    cat_in: CategoryCreate,
    service: CategoryService = Depends(get_category_service)
):
    return await service.create_category(cat_in)


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    dependencies=[Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER]))]
)
async def update_category(
    category_id: int,
    cat_in: CategoryUpdate,
    service: CategoryService = Depends(get_category_service)
):
    return await service.update_category(category_id, cat_in)


@router.delete(
    "/{category_id}",
    dependencies=[Depends(require_roles([UserRole.ADMIN]))]
)
async def delete_category(
    category_id: int,
    service: CategoryService = Depends(get_category_service)
):
    return await service.delete_category(category_id)
