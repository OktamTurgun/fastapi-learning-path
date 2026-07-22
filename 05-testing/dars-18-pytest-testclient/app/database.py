from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# MUHIM: "sqlite:///" emas, "sqlite+aiosqlite:///" — drayver nomi ko'rsatilishi shart
DATABASE_URL = "sqlite+aiosqlite:///./storely.db"

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session