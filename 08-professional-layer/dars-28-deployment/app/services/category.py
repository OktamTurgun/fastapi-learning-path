from fastapi import HTTPException, status
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    def __init__(self, repo: CategoryRepository):
        self.repo = repo

    async def get_categories(self, skip: int = 0, limit: int = 100):
        return await self.repo.get_all(skip=skip, limit=limit)

    async def get_category(self, category_id: int):
        cat = await self.repo.get_by_id(category_id)
        if not cat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kategoriya topilmadi")
        return cat

    async def create_category(self, cat_in: CategoryCreate):
        existing = await self.repo.get_by_name(cat_in.name)
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Bunday nomli kategoriya mavjud")
        return await self.repo.create(cat_in.model_dump())

    async def update_category(self, category_id: int, cat_in: CategoryUpdate):
        cat = await self.get_category(category_id)
        return await self.repo.update(cat, cat_in.model_dump(exclude_unset=True))

    async def delete_category(self, category_id: int):
        cat = await self.get_category(category_id)
        await self.repo.delete(cat)
        return {"detail": "Kategoriya o'chirildi"}
