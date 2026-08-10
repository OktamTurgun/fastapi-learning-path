from fastapi import HTTPException, status
from app.repositories.product import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    async def get_products(self, skip: int = 0, limit: int = 100):
        return await self.repo.get_all_with_category(skip=skip, limit=limit)

    async def get_product(self, product_id: int):
        prod = await self.repo.get_by_id_with_category(product_id)
        if not prod:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mahsulot topilmadi")
        return prod

    async def create_product(self, prod_in: ProductCreate):
        created = await self.repo.create(prod_in.model_dump())
        # Yaratilgan mahsulotni category bilan birga qayta olamiz
        return await self.repo.get_by_id_with_category(created.id)

    async def update_product(self, product_id: int, prod_in: ProductUpdate):
        prod = await self.repo.get_by_id(product_id)
        if not prod:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mahsulot topilmadi")
        return await self.repo.update(prod, prod_in.model_dump(exclude_unset=True))

    async def delete_product(self, product_id: int):
        prod = await self.repo.get_by_id(product_id)
        if not prod:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mahsulot topilmadi")
        await self.repo.delete(prod)
        return {"detail": "Mahsulot o'chirildi"}
