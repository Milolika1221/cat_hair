import asyncio

from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.sql import text

from cat_server.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Логирование SQL-запросов
    future=True,
)

TEST_DATABASE_URL = (
    "postgresql+asyncpg://postgres:123456789@localhost:5432/test_cat_haircut"
)

test_engine = create_async_engine(TEST_DATABASE_URL, echo=True, future=True)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def check_database_connection(max_retries=10, delay=2):
    for attempt in range(1, max_retries + 1):
        try:
            async with AsyncSessionLocal() as session:
                await session.execute(text("SELECT 1"))
            print(f"✅ Database connected on attempt {attempt}")
            return
        except OperationalError as e:
            if attempt == max_retries:
                raise e
            print(
                f"⏳ DB not ready (attempt {attempt}/{max_retries}), retrying in {delay}s..."
            )
            await asyncio.sleep(delay)
