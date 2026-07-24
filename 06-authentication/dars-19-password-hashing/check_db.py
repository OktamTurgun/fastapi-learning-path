import asyncio
from app.database import engine
from sqlalchemy import text

async def check():
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
        tables = [r[0] for r in result]
        print("Tables:", tables)

        if "users" in tables:
            result = await conn.execute(text("PRAGMA table_info(users)"))
            cols = [r for r in result]
            print("Users columns:", cols)

asyncio.run(check())
