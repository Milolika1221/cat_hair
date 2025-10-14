import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import engine, Base

async def create_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Все таблицы созданы!")

async def drop_database():
    async with engine.begin() as conn :
        await conn.run_sync(Base.metadata.drop_all)
    print ('deleted')


if __name__ == '__main__':
    asyncio.run(create_database())

# if __name__ == '__main__':
#   asyncio.run(drop_database())