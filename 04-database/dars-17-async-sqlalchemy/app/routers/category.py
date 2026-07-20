from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.crud import category as crud_category

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreate, db: AsyncSession = Depends(get_db)):
    return await crud_category.create_category(db, category)


@router.get("/", response_model=list[CategoryResponse])
async def read_categories(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await crud_category.get_categories(db, skip=skip, limit=limit)


@router.get("/{category_id}", response_model=CategoryResponse)
async def read_category(category_id: int, db: AsyncSession = Depends(get_db)):
    db_category = await crud_category.get_category(db, category_id)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Kategoriya topilmadi")
    return db_category


@router.patch("/{category_id}", response_model=CategoryResponse)
async def update_category(category_id: int, category: CategoryUpdate, db: AsyncSession = Depends(get_db)):
    db_category = await crud_category.update_category(db, category_id, category)
    if db_category is None:
        raise HTTPException(status_code=404, detail="Kategoriya topilmadi")
    return db_category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud_category.delete_category(db, category_id)
    if not success:
        raise HTTPException(status_code=404, detail="Kategoriya topilmadi")