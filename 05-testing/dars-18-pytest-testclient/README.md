# Dars 18 — pytest & TestClient (Storely)

Bu dars — kodingizga **ishonch** qo'shadigan bosqich: har bir endpoint
uchun avtomatik test yozib, keyingi darslarda (Auth, Service Layer)
kod o'zgarganda ham eski funksionallik buzilmaganini kafolatlaysiz.

## 1. Nega test kerak? (Django bilan solishtirib)

Django'da `TestCase` + `Client` bilan test yozgan bo'lsangiz kerak.
FastAPI'da bir xil g'oya — **`TestClient`** (Starlette asosida) +
**`pytest`** (Python'ning standart test freymvorki, Django'ning o'z
ichki test runneridan farqli, universal).

| Django | FastAPI |
|---|---|
| `django.test.TestCase` | oddiy Python klass yoki funksiya |
| `self.client.get(...)` | `client.get(...)` (`TestClient` orqali) |
| `self.assertEqual(...)` | `assert ... == ...` (oddiy Python `assert`) |
| `setUp()` / `tearDown()` | pytest **fixture**lar (`@pytest.fixture`) |
| Test DB avtomatik yaratiladi | siz **qo'lda** alohida test DB sozlaysiz |

## 2. O'rnatish

```powershell
pip install pytest httpx
```

**`httpx` nima uchun kerak?** `TestClient` — ichida `httpx` kutubxonasidan
foydalanadi (HTTP so'rovlarni simulyatsiya qilish uchun). FastAPI buni
avtomatik talab qiladi.

`requirements.txt`ga qo'shing:

```text
pytest
httpx
```
## 3. Test uchun **alohida DB** — eng muhim tamoyil

**HECH QACHON** asosiy `storely.db`ga test yozmang! Testlar har safar
ma'lumot qo'shadi/o'chiradi — bu asosiy DB'ni "iflos" qiladi. Buning
o'rniga **test uchun alohida DB** (yoki xotieadagi SQLite) ishlatiladi.

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db

# Test uchun alohida, vaqtinchalik SQLite fayli
TEST_DATABASE_URL = "sqlite:///./test_storely.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Har bir test uchun toza DB — jadval yaratiladi, test tugagach o'chiriladi"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Asosiy get_db'ni test DB bilan almashtiradigan TestClient"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```

**`app.dependency_overrides`** — bu FastAPI'ning eng kuchli xususiyatlaridan
biri: `Depends(get_db)`ni **butun ilova doirasida** almashtirib, test
paytida asosiy DB o'rniga test DB ishlatilishini ta'minlaydi. Bu —
Django'da `override_settings` bilan bir xil g'oya.

**MUHIM:** Bu dars sinxron (`Session`) misolida yozilgan — chunki
Dars 17'da async'ga o'tgan bo'lsangiz ham, testlash tamoyili bir xil,
faqat `async def` test funksiyalari va `AsyncClient` kerak bo'ladi
(pastda alohida ko'rsatiladi).

## 4. Birinchi test — `test_products.py`

```python
# tests/test_products.py

def test_create_category(client):
    response = client.post("/categories/", json={
        "name": "Elektronika",
        "description": "Elektron qurilmalar",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Elektronika"
    assert "id" in data


def test_create_product(client):
    # Avval kategoriya kerak
    category_response = client.post("/categories/", json={"name": "Elektronika"})
    category_id = category_response.json()["id"]

    response = client.post("/products/", json={
        "name": "Simli sichqoncha",
        "price": 45000,
        "quantity": 15,
        "category_id": category_id,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Simli sichqoncha"
    assert data["price"] == 45000


def test_read_product_not_found(client):
    response = client.get("/products/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Mahsulot topilmadi"


def test_update_product(client):
    category_response = client.post("/categories/", json={"name": "Elektronika"})
    category_id = category_response.json()["id"]

    create_response = client.post("/products/", json={
        "name": "Klaviatura", "price": 100000, "category_id": category_id,
    })
    product_id = create_response.json()["id"]

    update_response = client.patch(f"/products/{product_id}", json={"price": 90000})
    assert update_response.status_code == 200
    assert update_response.json()["price"] == 90000
    assert update_response.json()["name"] == "Klaviatura"   # o'zgarmagan


def test_delete_product(client):
    category_response = client.post("/categories/", json={"name": "Elektronika"})
    category_id = category_response.json()["id"]

    create_response = client.post("/products/", json={
        "name": "Monitor", "price": 950000, "category_id": category_id,
    })
    product_id = create_response.json()["id"]

    delete_response = client.delete(f"/products/{product_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/products/{product_id}")
    assert get_response.status_code == 404
```

## 5. Testlarni ishga tushirish

```powershell
pytest
```

Yoki batafsil (`-v` — verbose):
```powershell
pytest -v
```

Faqat bitta faylni:
```powershell
pytest tests/test_products.py -v
```

Faqat bitta funksiyani:
```powershell
pytest tests/test_products.py::test_create_product -v
```

## 6. Pagination/filtering'ni sinash

```python
def test_products_filtering(client):
    category_response = client.post("/categories/", json={"name": "Elektronika"})
    category_id = category_response.json()["id"]

    client.post("/products/", json={"name": "Arzon mahsulot", "price": 10000, "category_id": category_id})
    client.post("/products/", json={"name": "Qimmat mahsulot", "price": 500000, "category_id": category_id})

    response = client.get("/products/?min_price=100000")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["name"] == "Qimmat mahsulot"


def test_products_pagination(client):
    category_response = client.post("/categories/", json={"name": "Elektronika"})
    category_id = category_response.json()["id"]

    for i in range(5):
        client.post("/products/", json={"name": f"Mahsulot {i}", "price": 10000, "category_id": category_id})

    response = client.get("/products/?limit=2")
    data = response.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
```

## 7. Async endpointlar uchun test (agar Dars 17'dan keyin davom etsangiz)

Agar `app/`ingiz **async** bo'lsa (Dars 17'dagidek), `TestClient` baribir
ishlaydi (u sync/async ikkalasini ham qo'llab-quvvatlaydi), lekin
`conftest.py`da `AsyncSession` va `async_sessionmaker` ishlatish kerak:

```python
# tests/conftest.py (async versiya)
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_storely.db"

engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```

Bu holatda qo'shimcha kutubxona kerak: `pip install pytest-asyncio`.

**Test funksiyalarining o'zi** (`test_create_product` va h.k.) — **o'zgarishsiz** qoladi, chunki `TestClient` sinxron interfeys taqdim etadi, hatto ilova async bo'lsa ham (ichida event loop'ni o'zi boshqaradi).

## 8. `pytest.ini` — konfiguratsiya (ixtiyoriy, lekin tavsiya etiladi)

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
```

## Xulosa

- **`TestClient`** — real serverni ishga tushirmasdan, HTTP so'rovlarni simulyatsiya qiladi
- **`app.dependency_overrides`** — asosiy DB'ni test DB bilan almashtirish uchun
- **Har bir test — mustaqil** (`scope="function"` fixture) — bitta test boshqasiga ta'sir qilmasligi kerak
- **`assert response.status_code == ...`** — Django'dagi `self.assertEqual`ning FastAPI/pytest ekvivalenti
- **Async ilova uchun** — faqat `conftest.py` o'zgaradi, test funksiyalari o'zi emas

## Amaliy struktura

```text
dars-18-pytest-testclient/
├── README.md
├── requirements.txt
├── pytest.ini
├── alembic.ini
├── alembic/
├── app/
│   └── (Dars 17'dagi to'liq struktura)
└── tests/
    ├── __init__.py
    ├── conftest.py
    ├── test_categories.py
    └── test_products.py
```
