from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    orders = relationship("Order", back_populates="customer")   # bir mijoz — ko'p buyurtma

    def __repr__(self):
        return f"<Customer(id={self.id}, full_name='{self.full_name}')>"
    