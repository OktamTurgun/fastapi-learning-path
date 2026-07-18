from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse
from app.crud import order as crud_order

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    return crud_order.create_order(db, order)


@router.get("/", response_model=list[OrderResponse])
def read_orders(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud_order.get_orders(db, skip=skip, limit=limit)


@router.get("/{order_id}", response_model=OrderResponse)
def read_order(order_id: int, db: Session = Depends(get_db)):
    db_order = crud_order.get_order(db, order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    return db_order


@router.patch("/{order_id}", response_model=OrderResponse)
def update_order(order_id: int, order: OrderUpdate, db: Session = Depends(get_db)):
    db_order = crud_order.update_order(db, order_id, order)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    return db_order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    success = crud_order.delete_order(db, order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")