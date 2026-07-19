"""
Product modeli — Category bilan Many-to-One munosabatda
(ko'p mahsulot — bitta kategoriya).
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=0)
    in_stock = Column(Boolean, default=True)
    discount_percent = Column(Integer, default=0)   # <- YANGI ustun

    category_id = Column(Integer, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="products")

    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}')>"