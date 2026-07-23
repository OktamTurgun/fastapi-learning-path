from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, PaginatedOrders
from app.crud import order as crud_order

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(order: OrderCreate, db: AsyncSession = Depends(get_db)):
    return await crud_order.create_order(db, order)


@router.get("/", response_model=PaginatedOrders)
async def read_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None),
    min_total_amount: float | None = Query(None, ge=0),
    max_total_amount: float | None = Query(None, ge=0),
    status: str | None = Query(None),
    sort_by: str = Query("id"),
    order: str = Query("asc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    items, total = await crud_order.get_orders_filtered(
        db, skip=skip, limit=limit, search=search,
        min_total_amount=min_total_amount, max_total_amount=max_total_amount,
        status=status, sort_by=sort_by, order=order,
    )
    return PaginatedOrders(total=total, skip=skip, limit=limit, items=items)


@router.get("/{order_id}", response_model=OrderResponse)
async def read_order(order_id: int, db: AsyncSession = Depends(get_db)):
    db_order = await crud_order.get_order(db, order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    return db_order


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order(order_id: int, order: OrderUpdate, db: AsyncSession = Depends(get_db)):
    db_order = await crud_order.update_order(db, order_id, order)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    return db_order


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud_order.delete_order(db, order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")