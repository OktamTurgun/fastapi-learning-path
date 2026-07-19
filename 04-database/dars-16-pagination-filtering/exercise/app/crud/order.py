from sqlalchemy.orm import Session
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderUpdate


def get_order(db: Session, order_id: int) -> Order | None:
    return db.query(Order).filter(Order.id == order_id).first()

ALLOWED_SORT_FIELDS = {"id", "total_amount", "status"}

def get_orders_filtered(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        search: str | None = None,
        min_total_amount: float | None = None,
        max_total_amount: float | None = None,
        status: str | None = None,
        sort_by: str = "id",
        order: str = "asc",
) -> tuple[list[Order], int]:
    query = db.query(Order)

    if search:
        query = query.filter(Order.delivery_address.ilike(f"%{search}%"))

    if min_total_amount is not None:
        query = query.filter(Order.total_amount >= min_total_amount)

    if max_total_amount is not None:
        query = query.filter(Order.total_amount <= max_total_amount)

    if status is not None:
        query = query.filter(Order.status == status)

    # Apply sorting
    if sort_by not in ALLOWED_SORT_FIELDS:
        sort_by = "id"
    sort_column = getattr(Order, sort_by)
    if order == "desc":
        sort_column = sort_column.desc()
    query = query.order_by(sort_column)

    # Get total count before pagination
    total_count = query.count()

    # Apply pagination
    query = query.offset(skip).limit(limit)

    return query.all(), total_count


def create_order(db: Session, order: OrderCreate) -> Order:
    db_order = Order(**order.model_dump())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order


def update_order(db: Session, order_id: int, order: OrderUpdate) -> Order | None:
    db_order = get_order(db, order_id)
    if not db_order:
        return None

    update_data = order.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)

    db.commit()
    db.refresh(db_order)
    return db_order


def delete_order(db: Session, order_id: int) -> bool:
    db_order = get_order(db, order_id)
    if not db_order:
        return False

    db.delete(db_order)
    db.commit()
    return True