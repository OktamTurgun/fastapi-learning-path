from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


async def get_customer(db: AsyncSession, customer_id: int) -> Customer | None:
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    return result.scalar_one_or_none()


async def get_customers(db: AsyncSession, skip: int = 0, limit: int = 10) -> list[Customer]:
    result = await db.execute(select(Customer).offset(skip).limit(limit))
    return list(result.scalars().all())


async def create_customer(db: AsyncSession, customer: CustomerCreate) -> Customer:
    db_customer = Customer(**customer.model_dump())
    db.add(db_customer)
    await db.commit()
    await db.refresh(db_customer)
    return db_customer


async def update_customer(db: AsyncSession, customer_id: int, customer: CustomerUpdate) -> Customer | None:
    db_customer = await get_customer(db, customer_id)
    if not db_customer:
        return None

    update_data = customer.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_customer, key, value)

    await db.commit()
    await db.refresh(db_customer)
    return db_customer


async def delete_customer(db: AsyncSession, customer_id: int) -> bool:
    db_customer = await get_customer(db, customer_id)
    if not db_customer:
        return False

    db.delete(db_customer)
    await db.commit()
    return True