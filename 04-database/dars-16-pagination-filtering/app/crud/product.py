from sqlalchemy.orm import Session
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate

ALLOWED_SORT_FIELDS = {"id", "name", "price", "quantity"}


def get_product(db: Session, product_id: int) -> Product | None:
    return db.query(Product).filter(Product.id == product_id).first()


def get_products_filtered(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: str | None = None,
    category_id: int | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    sort_by: str = "id",
    order: str = "asc",
) -> tuple[list[Product], int]:
    query = db.query(Product)

    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))

    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    total = query.count()

    if sort_by not in ALLOWED_SORT_FIELDS:
        sort_by = "id"
    sort_column = getattr(Product, sort_by)
    if order == "desc":
        sort_column = sort_column.desc()
    query = query.order_by(sort_column)

    items = query.offset(skip).limit(limit).all()

    return items, total


def create_product(db: Session, product: ProductCreate) -> Product:
    db_product = Product(**product.model_dump())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product


def update_product(db: Session, product_id: int, product: ProductUpdate) -> Product | None:
    db_product = get_product(db, product_id)
    if not db_product:
        return None

    update_data = product.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    return db_product


def delete_product(db: Session, product_id: int) -> bool:
    db_product = get_product(db, product_id)
    if not db_product:
        return False

    db.delete(db_product)
    db.commit()
    return True