from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from app.core.database import get_db
from app.services.user import UserService
from app.services.order import OrderService


async def get_user_service(session: AsyncSession = Depends(get_db)) -> UserService:
    return UserService(session)


async def get_order_service(session: AsyncSession = Depends(get_db)) -> OrderService:
    return OrderService(session)