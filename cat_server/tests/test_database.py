# Проверка подключения к БД
import asyncio

from cat_server.core.database import AsyncSessionLocal, test_engine, engine
from cat_server.domain.entities import Cats, Base, Recommendations
# from cat_server.infrastructure.repositories import IRecommendationRepository, RecommendationRepository


async def test_connection() :
    try :
        async with engine.begin() as conn :
            await conn.run_sync(Base.metadata.create_all)
        print('успэх')
    
        async with AsyncSessionLocal() as session : 
            cat = Cats()
            session.add(cat)
            await session.commit()
            await session.refresh(cat)
            print(f'Гатова: ID={cat.id}')


    except Exception as e:
        print(f'Ошибка: {e}')

if __name__ == '__main__':
    asyncio.run(test_connection())
