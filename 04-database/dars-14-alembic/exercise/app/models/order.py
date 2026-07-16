from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    total_amount = Column(Float, nullable=False)
    status = Column(String, default="pending")
    delivery_address = Column(String, nullable=True) 
    customer_id = Column(Integer, ForeignKey("customers.id"))
    customer = relationship("Customer", back_populates="orders")

    def __repr__(self):
        return f"<Order(id={self.id}, total_amount={self.total_amount}, status='{self.status}')>"
    