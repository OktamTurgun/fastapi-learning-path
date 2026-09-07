from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.order import (
    ParcelOrderCreate,
    ParcelOrderRead,
    OrderStatusUpdate,
    FoodOrderCreate,
    FoodOrderRead,
)
from app.services.order import OrderService
from app.models.user import User
from app.api.v1.deps import get_order_service, get_current_user, require_role

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post(
    "/parcel",
    response_model=ParcelOrderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Pochta buyurtmasi yaratish (himoyalangan)",
    description=(
        "Yangi pochta buyurtmasini yaratadi. "
        "Faqat login bo'lgan foydalanuvchilar kirishi mumkin. "
        "customer_id avtomatik ravishda JWT token'dan olinadi — "
        "so'rov body'sidan emas."
    ),
)
async def create_parcel_order(
    data: ParcelOrderCreate,
    current_user: User = Depends(get_current_user),   # ← himoya shu yerda
    service: OrderService = Depends(get_order_service),
):
    """
    customer_id hech qachon body'dan olinmaydi — bu xavfsizlik talabi.
    Kimligingizni JWT token aniqlaydi.
    """
    order = await service.create_parcel_order(data, customer_id=current_user.id)
    return order


@router.post(
    "/food",
    response_model=FoodOrderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Taom buyurtmasi yaratish (himoyalangan)",
    description=(
        "Yangi taom buyurtmasini yaratadi. "
        "Faqat login bo'lgan foydalanuvchilar kirishi mumkin. "
        "customer_id avtomatik ravishda JWT token'dan olinadi."
    ),
)
async def create_food_order(
    data: FoodOrderCreate,
    current_user: User = Depends(get_current_user),
    service: OrderService = Depends(get_order_service),
):
    try:
        order = await service.create_food_order(data, customer_id=current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return order


@router.patch(
    "/parcel/{order_id}/status",
    response_model=ParcelOrderRead,
    summary="Pochta buyurtmasi maqomini yangilash (kuryer/admin)",
)
async def update_parcel_status(
    order_id: UUID,
    data: OrderStatusUpdate,
    service: OrderService = Depends(get_order_service),
    current_user: User = Depends(require_role("courier", "admin")),
):
    try:
        order = await service.update_parcel_status(order_id, data.status)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return order


@router.patch(
    "/food/{order_id}/status",
    response_model=FoodOrderRead,
    summary="Taom buyurtmasi maqomini yangilash (kuryer/admin)",
)
async def update_food_status(
    order_id: UUID,
    data: OrderStatusUpdate,
    service: OrderService = Depends(get_order_service),
    current_user: User = Depends(require_role("courier", "admin")),
):
    try:
        order = await service.update_food_status(order_id, data.status)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return order