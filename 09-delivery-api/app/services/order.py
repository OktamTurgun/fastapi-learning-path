from app.repositories.order import FoodOrderRepository, ParcelOrderRepository
from app.schemas.order import ParcelOrderCreate
from app.core.config import settings

class OrderService:
    def __init__(self, session):
        self.parcel_repo = ParcelOrderRepository(session)
        self.food_repo = FoodOrderRepository(session)

    async def create_parcel_order(self, data: ParcelOrderCreate, customer_id):
        total_price = settings.parcel_base_fee + (float(data.weight_kg) * settings.parcel_rate_per_kg)

        order = await self.parcel_repo.add(
            customer_id=customer_id,
            weight_kg=data.weight_kg,
            pickup_address=data.pickup_address,
            dropoff_address=data.dropoff_address,
            total_price=total_price,
        )
        return order

    async def update_parcel_status(self, order_id, new_status):
        order = await self.parcel_repo.update_status(order_id, new_status)
        if order is None:
            raise ValueError("Buyurtma topilmadi")
        return order