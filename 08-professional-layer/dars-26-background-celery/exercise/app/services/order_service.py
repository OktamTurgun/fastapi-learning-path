from fastapi import HTTPException, status

from app.models.order import Order
from app.schemas.order import OrderCreate, OrderUpdate
from app.repositories.order_repository import SQLAlchemyOrderRepository
from app.repositories.customer_repository import SQLAlchemyCustomerRepository


class OrderService:
    def __init__(
        self,
        order_repo: SQLAlchemyOrderRepository,
        customer_repo: SQLAlchemyCustomerRepository,  # ← bog'liq repo
    ):
        self.order_repo = order_repo
        self.customer_repo = customer_repo

    async def create_order(self, order_data: OrderCreate) -> Order:
        # Biznes qoida: mijoz mavjud bo'lishi shart
        customer = await self.customer_repo.get(order_data.customer_id)
        if customer is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Customer with id {order_data.customer_id} does not exist",
            )
        return await self.order_repo.create(order_data)

    async def update_order(self, order_id: int, order_data: OrderUpdate) -> Order:
        # Biznes qoida: yangi customer_id ham mavjud bo'lishi kerak
        if order_data.customer_id is not None:
            customer = await self.customer_repo.get(order_data.customer_id)
            if customer is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Customer with id {order_data.customer_id} does not exist",
                )
        updated = await self.order_repo.update(order_id, order_data)
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buyurtma topilmadi")
        return updated

    async def delete_order(self, order_id: int) -> None:
        success = await self.order_repo.delete(order_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Buyurtma topilmadi")
