import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from sqlalchemy import select

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User, Role
from app.models.restaurant import Restaurant, MenuItem
from app.core.security import create_access_token


@pytest_asyncio.fixture(scope="function")
async def test_session_factory():
    """
    Har bir test uchun alohida in-memory SQLite bazasini yaratadi
    va barcha kerakli jadvallarni ochib, standart rollarni kiritadi.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    # Standart rollarni kiritish
    async with session_factory() as session:
        session.add_all([
            Role(name="customer"),
            Role(name="courier"),
            Role(name="admin"),
        ])
        await session.commit()

    yield session_factory

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_session_factory):
    """
    Test ichida to'g'ridan-to'g'ri DB bilan ishlash uchun sessiya.
    """
    async with test_session_factory() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def client(test_session_factory):
    """
    FastAPI ilovasiga so'rov yuborish uchun httpx.AsyncClient.
    Baza sessiyasi avtomatik ravishda test bazasiga yo'naltiriladi.
    """
    async def override_get_db():
        async with test_session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()


# ==========================================
# USER VA AUTH FIXTURE'LARI
# ==========================================

# Pre-hashed bcrypt for 'password123'
PASSWORD_HASH = "$2b$12$pI8YYBoMQQ2/rTs4Sab.fuiiWNIBWmFfDq8p5FdWVv6cmPsPqd51G"


@pytest_asyncio.fixture(scope="function")
async def customer_user(db_session):
    stmt = select(Role).where(Role.name == "customer")
    role = (await db_session.execute(stmt)).scalar_one()
    user = User(
        email="customer@test.com",
        hashed_password=PASSWORD_HASH,
        full_name="Test Customer",
        roles=[role],
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def customer_token(customer_user):
    return create_access_token(data={"sub": str(customer_user.id)})


@pytest.fixture
def customer_headers(customer_token):
    return {"Authorization": f"Bearer {customer_token}"}


@pytest_asyncio.fixture(scope="function")
async def courier_user(db_session):
    stmt = select(Role).where(Role.name == "courier")
    role = (await db_session.execute(stmt)).scalar_one()
    user = User(
        email="courier@test.com",
        hashed_password=PASSWORD_HASH,
        full_name="Test Courier",
        roles=[role],
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def courier_token(courier_user):
    return create_access_token(data={"sub": str(courier_user.id)})


@pytest.fixture
def courier_headers(courier_token):
    return {"Authorization": f"Bearer {courier_token}"}


@pytest_asyncio.fixture(scope="function")
async def admin_user(db_session):
    stmt = select(Role).where(Role.name == "admin")
    role = (await db_session.execute(stmt)).scalar_one()
    user = User(
        email="admin@test.com",
        hashed_password=PASSWORD_HASH,
        full_name="Test Admin",
        roles=[role],
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def admin_token(admin_user):
    return create_access_token(data={"sub": str(admin_user.id)})


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


# ==========================================
# RESTORAN VA MENYU FIXTURE'LARI
# ==========================================

@pytest_asyncio.fixture(scope="function")
async def sample_restaurant(db_session):
    restaurant = Restaurant(
        name="Rayhon Milliy Taomlar",
        address="Chilonzor 9-mavze, Toshkent",
        is_active=True,
    )
    db_session.add(restaurant)
    await db_session.commit()
    await db_session.refresh(restaurant)
    return restaurant


@pytest_asyncio.fixture(scope="function")
async def sample_menu_item(db_session, sample_restaurant):
    item = MenuItem(
        restaurant_id=sample_restaurant.id,
        name="Osh (To'y oshi)",
        price=45000.0,
        is_available=True,
    )
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(item)
    return item
