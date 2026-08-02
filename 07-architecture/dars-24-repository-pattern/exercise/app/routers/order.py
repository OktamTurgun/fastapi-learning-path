from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, PaginatedOrders
from app.repositories.order_repository import SQLAlchemyOrderRepository
from app.services.order_service import OrderService
from app.core.dependencies import get_order_repository, get_order_service

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order: OrderCreate,
    service: OrderService = Depends(get_order_service),
):
    return await service.create_order(order)


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
    repo: SQLAlchemyOrderRepository = Depends(get_order_repository),
):
    items, total = await repo.list_filtered(
        skip=skip, limit=limit, search=search,
        min_total=min_total_amount, max_total=max_total_amount,
        status=status, sort_by=sort_by, order=order,
    )
    return PaginatedOrders(total=total, skip=skip, limit=limit, items=items)


@router.get("/{order_id}", response_model=OrderResponse)
async def read_order(
    order_id: int,
    repo: SQLAlchemyOrderRepository = Depends(get_order_repository),
):
    db_order = await repo.get(order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Buyurtma topilmadi")
    return db_order


@router.patch("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order: OrderUpdate,
    service: OrderService = Depends(get_order_service),
):
    return await service.update_order(order_id, order)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(
    order_id: int,
    service: OrderService = Depends(get_order_service),
):
    await service.delete_order(order_id)