from typing import Optional

from fastapi import HTTPException, status

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.repositories.product_repository import SQLAlchemyProductRepository
from app.repositories.category_repository import SQLAlchemyCategoryRepository


class ProductService:
    """Product bilan bog'liq barcha biznes-mantiq shu yerda joylashadi"""

    def __init__(
        self,
        product_repo: SQLAlchemyProductRepository,
        category_repo: SQLAlchemyCategoryRepository,
    ):
        self.product_repo = product_repo
        self.category_repo = category_repo

    async def create_product(self, product_data: ProductCreate) -> Product:
        # Biznes qoida: kategoriya mavjud bo'lishi shart
        category = await self.category_repo.get(product_data.category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with id {product_data.category_id} does not exist",
            )
        return await self.product_repo.create(product_data)

    async def update_product(self, product_id: int, product_data: ProductUpdate) -> Product:
        # Biznes qoida: agar category_id yangilansa, u ham mavjud bo'lishi kerak
        if product_data.category_id is not None:
            category = await self.category_repo.get(product_data.category_id)
            if category is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category with id {product_data.category_id} does not exist",
                )

        updated = await self.product_repo.update(product_id, product_data)
        if updated is None:
            raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
        return updated

    async def delete_product(self, product_id: int) -> None:
        success = await self.product_repo.delete(product_id)
        if not success:
            raise HTTPException(status_code=404, detail="Mahsulot topilmadi")