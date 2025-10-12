# Проверка подключения к БД

import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from core.database import AsyncSessionLocal, engine
from domain.entities import Cats, Base


async def test_connection() :
    try :
        async with engine.begin() as conn :
            await conn.run_sync(Base.metadata.create_all)
        print('успэх')
    
        async with AsyncSessionLocal() as session : 
            cat = Cats(user_id='test_id_123')
            session.add(cat)
            await session.commit()
            await session.refresh(cat)
            print(f'Гатова: ID={cat.id}, UserID={cat.user_id}')
    except Exception as e:
        print(f'Ошибка: {e}')

if __name__ == '__main__':
    asyncio.run(test_connection())
