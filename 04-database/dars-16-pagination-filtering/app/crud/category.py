from sqlalchemy.orm import Session
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def get_category(db: Session, category_id: int) -> Category | None:
    return db.query(Category).filter(Category.id == category_id).first()


def get_categories(db: Session, skip: int = 0, limit: int = 10) -> list[Category]:
    return db.query(Category).offset(skip).limit(limit).all()


def create_category(db: Session, category: CategoryCreate) -> Category:
    db_category = Category(**category.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def update_category(db: Session, category_id: int, category: CategoryUpdate) -> Category | None:
    db_category = get_category(db, category_id)
    if not db_category:
        return None

    update_data = category.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)

    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int) -> bool:
    db_category = get_category(db, category_id)
    if not db_category:
        return False

    db.delete(db_category)
    db.commit()
    return True