from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.order import Order
from app.schemas.order import OrderCreate, OrderUpdate
from app.crud import order as crud_order
from app.crud import customer as crud_customer


class OrderService:
    """Buyurtma bilan bog'liq barcha biznes-mantiq shu yerda joylashadi"""

    @staticmethod
    async def create_order(db: AsyncSession, order_data: OrderCreate) -> Order:
        # Biznes qoida: buyurtma yaratishdan oldin mijoz mavjudligini tekshirish
        customer = await crud_customer.get_customer(db, order_data.customer_id)
        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Customer with id {order_data.customer_id} does not exist",
            )

        return await crud_order.create_order(db, order_data)

    @staticmethod
    async def update_order(
        db: AsyncSession, order_id: int, order_data: OrderUpdate
    ) -> Order:
        # Biznes qoida: agar customer_id yangilansa, yangi mijoz ham mavjud bo'lishi kerak
        if order_data.customer_id is not None:
            customer = await crud_customer.get_customer(db, order_data.customer_id)
            if customer is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Customer with id {order_data.customer_id} does not exist",
                )

        updated = await crud_order.update_order(db, order_id, order_data)
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buyurtma topilmadi")
        return updated

    @staticmethod
    async def delete_order(db: AsyncSession, order_id: int) -> None:
        success = await crud_order.delete_order(db, order_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buyurtma topilmadi")
