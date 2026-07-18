from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse
from app.crud import customer as crud_customer

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    return crud_customer.create_customer(db, customer)


@router.get("/", response_model=list[CustomerResponse])
def read_customers(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud_customer.get_customers(db, skip=skip, limit=limit)


@router.get("/{customer_id}", response_model=CustomerResponse)
def read_customer(customer_id: int, db: Session = Depends(get_db)):
    db_customer = crud_customer.get_customer(db, customer_id)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Mijoz topilmadi")
    return db_customer


@router.patch("/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: int, customer: CustomerUpdate, db: Session = Depends(get_db)):
    db_customer = crud_customer.update_customer(db, customer_id, customer)
    if db_customer is None:
        raise HTTPException(status_code=404, detail="Mijoz topilmadi")
    return db_customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    success = crud_customer.delete_customer(db, customer_id)
    if not success:
        raise HTTPException(status_code=404, detail="Mijoz topilmadi")