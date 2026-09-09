from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserCreate, UserRead, RoleAssignRequest
from app.schemas.token import Token
from app.schemas.auth import LoginData
from app.services.user import UserService
from app.api.v1.deps import get_user_service, require_role
from app.models.user import User
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserCreate,
    service: UserService = Depends(get_user_service),
):
    try:
        user = await service.register(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return user


@router.post("/login", response_model=Token)
async def login(
    data: LoginData,
    service: UserService = Depends(get_user_service),
):
    try:
        user = await service.authenticate(email=data.email, password=data.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=access_token, token_type="bearer")


@router.post(
    "/assign-role",
    response_model=UserRead,
    summary="Foydalanuvchiga yangi rol biriktirish (faqat admin)",
    description="Faqat admin huquqiga ega foydalanuvchilar boshqa foydalanuvchilarga rol biriktirishi mumkin.",
)
async def assign_role(
    data: RoleAssignRequest,
    service: UserService = Depends(get_user_service),
    current_user: User = Depends(require_role("admin")),
):
    try:
        user = await service.assign_role_to_user(data.user_id, data.role.value)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return user
