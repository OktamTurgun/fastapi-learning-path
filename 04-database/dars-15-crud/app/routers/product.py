from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.crud import product as crud_product

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    return crud_product.create_product(db, product)


@router.get("/", response_model=list[ProductResponse])
def read_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud_product.get_products(db, skip=skip, limit=limit)


@router.get("/{product_id}", response_model=ProductResponse)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = crud_product.get_product(db, product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    return db_product


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    db_product = crud_product.update_product(db, product_id, product)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
    return db_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    success = crud_product.delete_product(db, product_id)
    if not success:
        raise HTTPException(status_code=404, detail="Mahsulot topilmadi")