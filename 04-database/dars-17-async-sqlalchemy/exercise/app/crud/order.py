from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import Order
from app.schemas.order import OrderCreate, OrderUpdate

ALLOWED_SORT_FIELDS = {"id", "total_amount", "status"}


async def get_order(db: AsyncSession, order_id: int) -> Order | None:
    result = await db.execute(
        select(Order)
        .options(selectinload(Order.customer))   # <- MUHIM: customer oldindan yuklanadi
        .where(Order.id == order_id)
    )
    return result.scalar_one_or_none()


async def get_orders_filtered(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
    min_total_amount: float | None = None,
    max_total_amount: float | None = None,
    status: str | None = None,
    sort_by: str = "id",
    order: str = "asc",
) -> tuple[list[Order], int]:
    query = select(Order).options(selectinload(Order.customer))   # <- bu yerda ham

    if search:
        query = query.where(Order.delivery_address.ilike(f"%{search}%"))
    if min_total_amount is not None:
        query = query.where(Order.total_amount >= min_total_amount)
    if max_total_amount is not None:
        query = query.where(Order.total_amount <= max_total_amount)
    if status is not None:
        query = query.where(Order.status == status)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    if sort_by not in ALLOWED_SORT_FIELDS:
        sort_by = "id"
    sort_column = getattr(Order, sort_by)
    if order == "desc":
        sort_column = sort_column.desc()
    query = query.order_by(sort_column).offset(skip).limit(limit)

    result = await db.execute(query)
    items = result.scalars().all()

    return list(items), total


async def create_order(db: AsyncSession, order: OrderCreate) -> Order:
    db_order = Order(**order.model_dump())
    db.add(db_order)
    await db.commit()
    await db.refresh(db_order)
    # refresh'dan keyin ham customer'ni yuklash kerak (chunki refresh uni yangilamaydi)
    return await get_order(db, db_order.id)


async def update_order(db: AsyncSession, order_id: int, order: OrderUpdate) -> Order | None:
    db_order = await get_order(db, order_id)
    if not db_order:
        return None

    update_data = order.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_order, key, value)

    await db.commit()
    await db.refresh(db_order)
    return await get_order(db, order_id)


async def delete_order(db: AsyncSession, order_id: int) -> bool:
    db_order = await get_order(db, order_id)
    if not db_order:
        return False

    await db.delete(db_order)
    await db.commit()
    return True