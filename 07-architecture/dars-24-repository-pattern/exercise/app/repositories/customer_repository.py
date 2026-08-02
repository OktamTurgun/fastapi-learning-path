from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate
from app.repositories.base import AbstractRepository


class SQLAlchemyCustomerRepository(AbstractRepository[Customer, CustomerCreate, CustomerUpdate]):

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, id: int) -> Optional[Customer]:
        result = await self.db.execute(select(Customer).where(Customer.id == id))
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> List[Customer]:
        result = await self.db.execute(select(Customer).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, data: CustomerCreate) -> Customer:
        customer = Customer(**data.model_dump())
        self.db.add(customer)
        await self.db.commit()
        await self.db.refresh(customer)
        return customer

    async def update(self, id: int, data: CustomerUpdate) -> Optional[Customer]:
        customer = await self.get(id)
        if not customer:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(customer, key, value)
        await self.db.commit()
        await self.db.refresh(customer)
        return customer

    async def delete(self, id: int) -> bool:
        customer = await self.get(id)
        if not customer:
            return False
        await self.db.delete(customer)
        await self.db.commit()
        return True