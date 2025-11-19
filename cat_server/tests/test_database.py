# Проверка подключения к БД

import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from cat_server.core.database import AsyncSessionLocal, engine
from cat_server.domain.entities import Base
from cat_server.infrastructure.repositories import CatsRepository

# async def test_connection() :
# try :
#     async with engine.begin() as conn :
#         await conn.run_sync(Base.metadata.create_all)
#     print('успэх')
#
#     async with AsyncSessionLocal() as session :
#         cat = Cats()
#         session.add(cat)
#         await session.commit()
#         await session.refresh(cat)
#         print(f'Гатова: ID={cat.id}')
# except Exception as e:
#     print(f'Ошибка: {e}')
#


async def test_search():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        async with AsyncSessionLocal() as session:
            cat_repo = CatsRepository(session)
            cat = await cat_repo.get_by_id(cat_id=1)
            print(f"HAHHAHAHAHHAHAH: {cat.id}")  # pyright: ignore[reportOptionalMemberAccess]
    except Exception as e:
        print(f"Ошибка: {str(e)}")


if __name__ == "__main__":
    asyncio.run(test_search())
