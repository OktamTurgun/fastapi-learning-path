from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


async def get_category(db: AsyncSession, category_id: int) -> Category | None:
    result = await db.execute(select(Category).where(Category.id == category_id))
    return result.scalar_one_or_none()


async def get_categories(db: AsyncSession, skip: int = 0, limit: int = 10) -> list[Category]:
    result = await db.execute(select(Category).offset(skip).limit(limit))
    return list(result.scalars().all())


async def create_category(db: AsyncSession, category: CategoryCreate) -> Category:
    db_category = Category(**category.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


async def update_category(db: AsyncSession, category_id: int, category: CategoryUpdate) -> Category | None:
    db_category = await get_category(db, category_id)
    if not db_category:
        return None

    update_data = category.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)

    await db.commit()
    await db.refresh(db_category)
    return db_category


async def delete_category(db: AsyncSession, category_id: int) -> bool:
    db_category = await get_category(db, category_id)
    if not db_category:
        return False

    await db.delete(db_category)
    await db.commit()
    return True