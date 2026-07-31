from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.crud import product as crud_product
from app.crud import category as crud_category


class ProductService:
    """Product bilan bog'liq barcha biznes-mantiq shu yerda joylashadi"""

    @staticmethod
    async def create_product(db: AsyncSession, product_data: ProductCreate) -> Product:
        # Biznes qoida: kategoriya mavjud bo'lishi shart
        category = await crud_category.get_category(db, product_data.category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with id {product_data.category_id} does not exist",
            )

        return await crud_product.create_product(db, product_data)

    @staticmethod
    async def update_product(
        db: AsyncSession, product_id: int, product_data: ProductUpdate
    ) -> Product:
        # Biznes qoida: agar category_id yangilansa, u ham mavjud bo'lishi kerak
        if product_data.category_id is not None:
            category = await crud_category.get_category(db, product_data.category_id)
            if category is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Category with id {product_data.category_id} does not exist",
                )

        updated = await crud_product.update_product(db, product_id, product_data)
        if updated is None:
            raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
        return updated

    @staticmethod
    async def delete_product(db: AsyncSession, product_id: int) -> None:
        success = await crud_product.delete_product(db, product_id)
        if not success:
            raise HTTPException(status_code=404, detail="Mahsulot topilmadi")