from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.crud import customer as crud_customer

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(customer: CustomerCreate, db: AsyncSession = Depends(get_db)):
    return await crud_customer.create_customer(db, customer)


@router.get("/", response_model=list[CustomerResponse])
async def read_customers(skip: int = 0, limit: int = 10, db: AsyncSession = Depends(get_db)):
    return await crud_customer.get_customers(db, skip=skip, limit=limit)


@router.get("/{customer_id}", response_model=CustomerResponse)
async def read_customer(customer_id: int, db: AsyncSession = Depends(get_db)):
    db_customer = await crud_customer.get_customer(db, customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Mijoz topilmadi")
    return db_customer


@router.patch("/{customer_id}", response_model=CustomerResponse)
async def update_customer(customer_id: int, customer: CustomerUpdate, db: AsyncSession = Depends(get_db)):
    db_customer = await crud_customer.update_customer(db, customer_id, customer)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Mijoz topilmadi")
    return db_customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(customer_id: int, db: AsyncSession = Depends(get_db)):
    success = await crud_customer.delete_customer(db, customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Mijoz topilmadi")