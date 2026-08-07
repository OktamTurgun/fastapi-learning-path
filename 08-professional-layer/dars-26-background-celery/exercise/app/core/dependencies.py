from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.repositories.customer_repository import SQLAlchemyCustomerRepository
from app.repositories.order_repository import SQLAlchemyOrderRepository
from app.services.order_service import OrderService


async def get_customer_repository(
    db: AsyncSession = Depends(get_db),
) -> SQLAlchemyCustomerRepository:
    return SQLAlchemyCustomerRepository(db)


async def get_order_repository(
    db: AsyncSession = Depends(get_db),
) -> SQLAlchemyOrderRepository:
    return SQLAlchemyOrderRepository(db)


async def get_order_service(
    order_repo: SQLAlchemyOrderRepository = Depends(get_order_repository),
    customer_repo: SQLAlchemyCustomerRepository = Depends(get_customer_repository),
) -> OrderService:
    return OrderService(order_repo, customer_repo)