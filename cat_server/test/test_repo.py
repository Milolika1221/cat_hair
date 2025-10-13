import sys
import os
import asyncio

# Добавляем корневую директорию в путь Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import AsyncSessionLocal
from infrastructure.repositories import CatsRepository

async def test_create_cat():
    async with AsyncSessionLocal() as session:
        repo = CatsRepository(session)
        cat = await repo.create()
        print(f"Created cat with ID: {cat.id}")

if __name__ == "__main__":
    asyncio.run(test_create_cat())