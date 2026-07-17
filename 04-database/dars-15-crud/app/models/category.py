"""
Category modeli — Product bilan One-to-Many munosabatda
(bir kategoriya — ko'p mahsulot).
"""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    description = Column(String, nullable=True)

    # Bir kategoriyaning ko'p mahsuloti bo'lishi mumkin
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"