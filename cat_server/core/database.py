from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from cat_server.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,  # Логирование SQL-запросов
    future=True
)

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:123456789@localhost:5432/test_cat_haircut"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=True, future=True
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def check_database_connection():
    async with AsyncSessionLocal() as session:
        try:
            await session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            raise

