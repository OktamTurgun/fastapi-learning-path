import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Numeric, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.user import User


class OrderType(str, enum.Enum):
    FOOD = "food"
    PARCEL = "parcel"


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(Base):
    """
    Parent table — joined table inheritance uchun asos.

    `order_type` ustuni polymorphic_on sifatida ishlatiladi:
    SQLAlchemy shu ustunga qarab qaysi child klassni
    (FoodOrder yoki ParcelOrder) yuklashni aniqlaydi.
    """
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    order_type: Mapped[OrderType] = mapped_column(
        SAEnum(OrderType), nullable=False
    )
    status: Mapped[OrderStatus] = mapped_column(
        SAEnum(OrderStatus), default=OrderStatus.PENDING, nullable=False
    )
    total_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow
    )

    __mapper_args__ = {
        "polymorphic_on": order_type,
        "polymorphic_identity": "order",
    }

    customer: Mapped["User"] = relationship(back_populates="orders", lazy="selectin")

class FoodOrder(Order):
    __tablename__ = "food_orders"

    id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id"), primary_key=True
    )
    restaurant_id: Mapped[uuid.UUID] = mapped_column(nullable=False)
    delivery_address: Mapped[str] = mapped_column(String, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "food",
    }

class ParcelOrder(Order):
    __tablename__ = "parcel_orders"

    id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id"), primary_key=True
    )
    weight_kg: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    pickup_address: Mapped[str] = mapped_column(String, nullable=False)
    dropoff_address: Mapped[str] = mapped_column(String, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "parcel",
    }
