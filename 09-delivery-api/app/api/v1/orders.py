from fastapi import APIRouter, Depends, status

from app.schemas.order import ParcelOrderCreate, ParcelOrderRead
from app.services.order import OrderService
from app.models.user import User
from app.api.v1.deps import get_order_service, get_current_user

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
