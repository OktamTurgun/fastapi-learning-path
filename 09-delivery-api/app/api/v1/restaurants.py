from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.restaurant import (
    RestaurantCreate,
    RestaurantRead,
    MenuItemCreate,
    MenuItemRead,
)
from app.services.restaurant import RestaurantService
from app.models.user import User
from app.api.v1.deps import (
    get_restaurant_service,
    get_current_user,
    require_role,
)

router = APIRouter(prefix="/restaurants", tags=["restaurants"])


@router.post(
    "/",
    response_model=RestaurantRead,
    status_code=status.HTTP_201_CREATED,
    summary="Yangi restoran yaratish (admin)",
)
async def create_restaurant(
    data: RestaurantCreate,
    current_user: User = Depends(require_role("admin")),
    service: RestaurantService = Depends(get_restaurant_service),
):
    try:
        restaurant = await service.create_restaurant(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return restaurant


@router.post(
    "/{restaurant_id}/menu-items",
    response_model=MenuItemRead,
    status_code=status.HTTP_201_CREATED,
    summary="Restoranga yangi taom qo'shish (admin)",
)
async def add_menu_item(
    restaurant_id: UUID,
    data: MenuItemCreate,
    current_user: User = Depends(require_role("admin")),
    service: RestaurantService = Depends(get_restaurant_service),
):
    try:
        menu_item = await service.add_menu_item(restaurant_id, data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return menu_item


@router.get(
    "/{restaurant_id}",
    response_model=RestaurantRead,
    summary="Restoran va uning menyusini olish (barcha login qilgan foydalanuvchilar)",
)
async def get_restaurant(
    restaurant_id: UUID,
    service: RestaurantService = Depends(get_restaurant_service),
    current_user: User = Depends(get_current_user),
):
    try:
        restaurant = await service.get_restaurant(restaurant_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    return restaurant
