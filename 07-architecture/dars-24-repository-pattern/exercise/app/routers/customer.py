from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.repositories.customer_repository import SQLAlchemyCustomerRepository
from app.core.dependencies import get_customer_repository

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer: CustomerCreate,
    repo: SQLAlchemyCustomerRepository = Depends(get_customer_repository),
):
    return await repo.create(customer)


@router.get("/", response_model=list[CustomerResponse])
async def read_customers(
    skip: int = 0,
    limit: int = 10,
    repo: SQLAlchemyCustomerRepository = Depends(get_customer_repository),
):
    return await repo.list(skip=skip, limit=limit)


@router.get("/{customer_id}", response_model=CustomerResponse)
async def read_customer(
    customer_id: int,
    repo: SQLAlchemyCustomerRepository = Depends(get_customer_repository),
):
    db_customer = await repo.get(customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Mijoz topilmadi")
    return db_customer


@router.patch("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer: CustomerUpdate,
    repo: SQLAlchemyCustomerRepository = Depends(get_customer_repository),
):
    db_customer = await repo.update(customer_id, customer)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Mijoz topilmadi")
    return db_customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: int,
    repo: SQLAlchemyCustomerRepository = Depends(get_customer_repository),
):
    success = await repo.delete(customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Mijoz topilmadi")