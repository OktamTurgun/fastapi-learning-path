from app.repositories.order import FoodOrderRepository, ParcelOrderRepository
from app.repositories.restaurant import MenuItemRepository, OrderItemRepository
from app.schemas.order import FoodOrderCreate, ParcelOrderCreate
from app.core.config import settings

class OrderService:
    def __init__(self, session):
        self.session = session
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

    async def create_food_order(self, data: FoodOrderCreate, customer_id):
        menu_item_repo = MenuItemRepository(self.session)

        requested_ids = [item.menu_item_id for item in data.items]
        menu_items = await menu_item_repo.get_by_ids(requested_ids)

        if len(menu_items) != len(requested_ids):
            raise ValueError("Ba'zi menu_item_id lar noto'g'ri yoki mavjud emas")

        # menu_item_id -> MenuItem tez qidirish uchun lug'at
        menu_item_map = {mi.id: mi for mi in menu_items}

        total_price = 0
        order_items_data = []
        for item in data.items:
            menu_item = menu_item_map[item.menu_item_id]
            unit_price = float(menu_item.price)
            total_price += unit_price * item.quantity
            order_items_data.append({
                "menu_item_id": item.menu_item_id,
                "quantity": item.quantity,
                "unit_price": unit_price,
            })

        order = await self.food_repo.add(
            customer_id=customer_id,
            restaurant_id=data.restaurant_id,
            delivery_address=data.delivery_address,
            total_price=total_price,
        )

        for item in order_items_data:
            item["food_order_id"] = order.id  # endi order.id mavjud

        order_item_repo = OrderItemRepository(self.session)
        await order_item_repo.add_bulk(order_items_data)

        return order

    async def update_food_status(self, order_id, new_status):
        order = await self.food_repo.update_status(order_id, new_status)
        if order is None:
            raise ValueError("Buyurtma topilmadi")
        return order
