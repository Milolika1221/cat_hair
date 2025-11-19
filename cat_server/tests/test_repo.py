import asyncio
from datetime import datetime

from cat_server.core.database import AsyncSessionLocal
from cat_server.infrastructure.repositories import (
    CatCharacteristicsRepository,
    CatsRepository,
)


async def test_create_cat():
    async with AsyncSessionLocal() as session:
        repo = CatsRepository(session)
        cat = await repo.create()
        print(f"Created cat with ID: {cat.id}")

        characteristic_repo = CatCharacteristicsRepository(session=session)
        characteristic = await characteristic_repo.create(
            cat_id=cat.id,  # pyright: ignore[reportArgumentType]
            color="black",
            hair_length="long",
            analyzed_at=datetime.now(),
            confidence_level=0.6,
        )
        print(f"Created char with ID: {characteristic.id}")


if __name__ == "__main__":
    asyncio.run(test_create_cat())
