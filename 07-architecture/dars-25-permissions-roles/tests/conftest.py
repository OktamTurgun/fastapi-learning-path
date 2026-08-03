import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.models.user import User, UserRole
from app.core.security import hash_password, create_access_token

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


# --- Rol-based yordamchi fixture'lar (Dars 25 uchun) ---

async def _create_user_with_role(db_session, email: str, role: UserRole) -> User:
    """DB ga to'g'ridan-to'g'ri berilgan rol bilan foydalanuvchi yaratadi."""
    user = User(
        email=email,
        hashed_password=hash_password("TestParol123"),
        full_name=f"{role.value.capitalize()} User",
        is_active=True,
        role=role,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def admin_user(db_session):
    """ADMIN roli bilan foydalanuvchi."""
    return await _create_user_with_role(db_session, "admin@test.com", UserRole.ADMIN)


@pytest_asyncio.fixture(scope="function")
async def manager_user(db_session):
    """MANAGER roli bilan foydalanuvchi."""
    return await _create_user_with_role(db_session, "manager@test.com", UserRole.MANAGER)


@pytest_asyncio.fixture(scope="function")
async def customer_user(db_session):
    """CUSTOMER roli bilan foydalanuvchi (default rol)."""
    return await _create_user_with_role(db_session, "customer@test.com", UserRole.CUSTOMER)


def make_auth_headers(user: User) -> dict:
    """User uchun Bearer token yasab, header dict qaytaradi."""
    token = create_access_token(data={"sub": str(user.id)})
    return {"Authorization": f"Bearer {token}"}
