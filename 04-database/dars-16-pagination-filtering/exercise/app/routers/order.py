from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, PaginatedOrders
from app.crud import order as crud_order

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    return crud_order.create_order(db, order)

@router.get("/", response_model=PaginatedOrders)
def read_orders(
    skip: int = Query(0, ge=0, description="Nechta yozuvni o'tkazib yuborish"),
    limit: int = Query(10, ge=1, le=100, description="Nechta yozuv qaytarish"),
    search: str | None = Query(None, description="Buyurtma manzili bo'yicha qidiruv"),
    min_total_amount: float | None = Query(None, ge=0, description="Minimal umumiy miqdor"),
    max_total_amount: float | None = Query(None, ge=0, description="Maksimal umumiy miqdor"),
    status: str | None = Query(None, description="Buyurtma holati"),
    sort_by: str = Query("id", description="Saralash ustuni: id, total_amount, status"),
    order: str = Query("asc", pattern="^(asc|desc)$", description="asc yoki desc"),
    db: Session = Depends(get_db),
):
    items, total = crud_order.get_orders_filtered(
        db, skip=skip, limit=limit, search=search,
        min_total_amount=min_total_amount, max_total_amount=max_total_amount, status=status,
        sort_by=sort_by, order=order,
    )
    return PaginatedOrders(total=total, skip=skip, limit=limit, items=items)


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