# Dars 24 — Repository Pattern (Storely)

Dars 23'da Service Layer qo'shdik: `Router → Service → CRUD → Database`.
Lekin `ProductService` ichida hali ham to'g'ridan-to'g'ri `crud_product`
va `crud_category` modullariga bog'langan holat qoldi — bu **konkret
implementatsiyaga qattiq bog'liqlik (tight coupling)**. Bugun shu
bog'liqlikni yumshatamiz.

## 1. Repository Pattern nima?

**Repository** — ma'lumotlarga kirish mantiqini interfeys orqali
abstraktsiyalaydigan qatlam. Service endi "qanday SQL so'rov yozish
kerak"ni bilmaydi — u faqat "menga ID bo'yicha mahsulot ber" deb
so'raydi.

```
Avval (Dars 23):  Service → crud_product.get_product(db, id)   [SQLAlchemy'ga bevosita bog'liq]
Endi (Dars 24):   Service → ProductRepository.get(id)           [interfeys orqali, DB'dan mustaqil]
```

**Django solishtirma:** Django'da bunga o'xshash ehtiyoj kamdan-kam
seziladi, chunki ORM'ning o'zi (`Product.objects.filter(...)`)
allaqachon shunga o'xshash abstraktsiya beradi. FastAPI + SQLAlchemy'da
bunday tayyor qatlam yo'q — shuning uchun o'zimiz quramiz.

## 2. Nega Service Layer o'zi yetarli emas?

- `ProductService`ni **unit test** qilish uchun hozircha haqiqiy
  PostgreSQL kerak (chunki u to'g'ridan-to'g'ri `crud_product`ni
  chaqiradi).
- Repository interfeysi bo'lsa, testda **soxta (fake) repository**
  berish mumkin — DB'siz, faqat Python lug'ati bilan ishlaydigan
  versiya.
- Ertaga PostgreSQL o'rniga boshqa manba qo'shilsa (masalan cache),
  faqat Repository implementatsiyasi o'zgaradi — Service kodiga
  tegilmaydi.

## 3. Abstract Repository (interfeys)

```python
# app/repositories/base.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class AbstractRepository(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Barcha repository'lar amalga oshirishi shart bo'lgan shartnoma (contract)"""

    @abstractmethod
    async def get(self, id: int) -> Optional[ModelType]:
        ...

    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        ...

    @abstractmethod
    async def create(self, data: CreateSchemaType) -> ModelType:
        ...

    @abstractmethod
    async def update(self, id: int, data: UpdateSchemaType) -> Optional[ModelType]:
        ...

    @abstractmethod
    async def delete(self, id: int) -> bool:
        ...
```

`ABC` va `@abstractmethod` — Python'ning "interfeys" ekvivalenti: bu
klassdan meros olgan har qanday klass barcha metodlarni **majburiy**
amalga oshirishi kerak, aks holda obyekt yaratib bo'lmaydi.

## 4. Konkret implementatsiya — `SQLAlchemyProductRepository`

```python
# app/repositories/product_repository.py
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.repositories.base import AbstractRepository


class SQLAlchemyProductRepository(AbstractRepository[Product, ProductCreate, ProductUpdate]):
    """Repository interfeysining SQLAlchemy bilan ishlaydigan haqiqiy implementatsiyasi"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, id: int) -> Optional[Product]:
        result = await self.db.execute(select(Product).where(Product.id == id))
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> List[Product]:
        result = await self.db.execute(select(Product).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, data: ProductCreate) -> Product:
        product = Product(**data.model_dump())
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def update(self, id: int, data: ProductUpdate) -> Optional[Product]:
        product = await self.get(id)
        if product is None:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(product, field, value)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def delete(self, id: int) -> bool:
        product = await self.get(id)
        if product is None:
            return False
        await self.db.delete(product)
        await self.db.commit()
        return True
```

**E'tibor bering:** bu — Dars 23'dagi `crud_product.py` funksiyalarining
deyarli aynan o'zi, faqat endi **klass ichiga** joylashtirilgan va
`AbstractRepository`dan meros oladi. Amalda, bu darsda siz Dars 15-17'dagi
`crud/` modullaringizni Repository klasslariga "ko'chirasiz".

## 5. Service — endi Repository orqali ishlaydi

```python
# app/services/product_service.py
from app.repositories.base import AbstractRepository
from app.repositories.category_repository import SQLAlchemyCategoryRepository
from app.schemas.product import ProductCreate, ProductUpdate
from fastapi import HTTPException, status


class ProductService:
    def __init__(
        self,
        product_repo: AbstractRepository,
        category_repo: SQLAlchemyCategoryRepository,
    ):
        self.product_repo = product_repo
        self.category_repo = category_repo

    async def create_product(self, product_data: ProductCreate):
        category = await self.category_repo.get(product_data.category_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Category with id {product_data.category_id} does not exist",
            )
        return await self.product_repo.create(product_data)

    async def update_product(self, product_id: int, product_data: ProductUpdate):
        if product_data.category_id is not None:
            category = await self.category_repo.get(product_data.category_id)
            if category is None:
                raise HTTPException(status_code=400, detail="Category does not exist")

        updated = await self.product_repo.update(product_id, product_data)
        if updated is None:
            raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
        return updated

    async def delete_product(self, product_id: int) -> None:
        success = await self.product_repo.delete(product_id)
        if not success:
            raise HTTPException(status_code=404, detail="Mahsulot topilmadi")
```

**Muhim o'zgarish:** `ProductService` endi `@staticmethod` emas —
chunki endi u **holat saqlaydi** (`self.product_repo`,
`self.category_repo`). Bu — Dars 23'dagi dizayndan tubdan farq: o'sha
safar metodlar hech narsa saqlamagani uchun `@staticmethod` mantiqiy
edi, endi esa Repository'lar **dependency** sifatida klass ichiga
"in'ektsiya qilinadi" (dependency injection).

## 6. Router — Dependency Injection orqali ulash

```python
# app/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.repositories.product_repository import SQLAlchemyProductRepository
from app.repositories.category_repository import SQLAlchemyCategoryRepository
from app.services.product_service import ProductService


def get_product_service(db: AsyncSession = Depends(get_db)) -> ProductService:
    product_repo = SQLAlchemyProductRepository(db)
    category_repo = SQLAlchemyCategoryRepository(db)
    return ProductService(product_repo, category_repo)
```

```python
# app/routers/product.py
from app.dependencies import get_product_service
from app.services.product_service import ProductService

@router.post("/", response_model=ProductResponse, status_code=201)
async def create_product(
    product: ProductCreate,
    service: ProductService = Depends(get_product_service),
):
    return await service.create_product(product)
```

E'tibor bering — router endi `ProductService.create_product(db, product)`
deb emas, `service.create_product(product)` deb chaqiradi. `db`
parametri butunlay Router qatlamidan yashiringan — u faqat
`get_product_service` ichida qoladi.

## 7. Testda soxta Repository ishlatish (bu qatlamning asosiy foydasi)

```python
# tests/fakes.py
class FakeProductRepository:
    def __init__(self):
        self.products = {}
        self._next_id = 1

    async def get(self, id):
        return self.products.get(id)

    async def create(self, data):
        product = {"id": self._next_id, **data.model_dump()}
        self.products[self._next_id] = product
        self._next_id += 1
        return product

    # ... list, update, delete shunga o'xshash
```

```python
# tests/test_product_service.py
import pytest
from app.services.product_service import ProductService

@pytest.mark.asyncio
async def test_create_product_without_db():
    fake_products = FakeProductRepository()
    fake_categories = FakeCategoryRepository(existing_ids=[1])
    service = ProductService(fake_products, fake_categories)

    result = await service.create_product(ProductCreate(name="Sichqoncha", price=45000, category_id=1))

    assert result["name"] == "Sichqoncha"
```

**Mana shu — Repository Pattern'ning asosiy g'oyasi:** hech qanday
PostgreSQL, hech qanday `AsyncSession` kerak emas, lekin biznes-mantiq
(`ProductService`) to'liq tekshirilyapti.

## 8. Qachon kerak, qachon ortiqcha?

**Kerak, agar:**
- Service Layer'ni haqiqiy DB'siz test qilish muhim bo'lsa
- Kelajakda ma'lumot manbasi almashishi mumkin bo'lsa (masalan boshqa
  DB, tashqi API)
- Loyiha kattalashib, bir nechta developer parallel ishlayotgan bo'lsa

**Ortiqcha, agar:**
- Kichik loyiha, DB har doim bitta va o'zgarmaydi
- Service Layer allaqachon yetarli abstraktsiya beryapti

Storely uchun bu — **o'quv maqsadida** kiritilmoqda (chunki Delivery API
va E-commerce loyihalarida foydali bo'ladi), lekin har doim majburiy
emas.

## Xulosa

- **Repository** — Service bilan ma'lumotlar manbai (DB) orasidagi
  interfeys
- **`AbstractRepository`** — shartnoma (contract), `ABC` +
  `@abstractmethod` orqali
- **`SQLAlchemyProductRepository`** — Dars 23'dagi CRUD
  funksiyalarining klass shaklidagi versiyasi
- **Service endi holat saqlaydi** (`__init__`da repository qabul
  qiladi) — `@staticmethod` emas
- Asosiy foyda: **DB'siz unit test** qilish imkoniyati

## Amaliy struktura

```
dars-24-repository-pattern/
├── README.md
└── app/
    ├── repositories/          <- YANGI papka
    │   ├── __init__.py
    │   ├── base.py
    │   ├── product_repository.py
    │   └── category_repository.py
    ├── services/
    │   └── product_service.py   <- YANGILANADI (Repository orqali)
    ├── dependencies.py           <- YANGI (DI helper)
    └── routers/
        └── product.py            <- YANGILANADI (Service orqali)
```