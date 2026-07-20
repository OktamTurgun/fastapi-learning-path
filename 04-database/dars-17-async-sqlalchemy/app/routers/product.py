from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, PaginatedProducts
from app.crud import product as crud_product

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductCreate, db: AsyncSession = Depends(get_db)):
    return await crud_product.create_product(db, product)


@router.get("/", response_model=PaginatedProducts)
async def read_products(
    skip: int = Query(0, ge=0, description="Nechta yozuvni o'tkazib yuborish"),
    limit: int = Query(10, ge=1, le=100, description="Nechta yozuv qaytarish"),
    search: str | None = Query(None, description="Mahsulot nomi bo'yicha qidiruv"),
    category_id: int | None = Query(None, description="Kategoriya bo'yicha filtr"),
    min_price: float | None = Query(None, ge=0, description="Minimal narx"),
    max_price: float | None = Query(None, ge=0, description="Maksimal narx"),
    sort_by: str = Query("id", description="Saralash ustuni: id, name, price, quantity"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="asc yoki desc"),
    db: AsyncSession = Depends(get_db),
):
    items, total = await crud_product.get_products_filtered(
        db, skip=skip, limit=limit, search=search,
        category_id=category_id, min_price=min_price, max_price=max_price,
        sort_by=sort_by, order=order,
    )
    return PaginatedProducts(total=total, skip=skip, limit=limit, items=items)


@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(product_id: int, db: AsyncSession = Depends(get_db)):
    db_product = await crud_product.get_product(db, product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    return db_product


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: int, product: ProductUpdate, db: AsyncSession = Depends(get_db)):
    db_product = await crud_product.update_product(db, product_id, product)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud_product.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")