from typing import List, Optional
import asyncpg

class AppDbContext:
    def __init__(self, connection_string : str):
        self.connection_string = connection_string
        self.pool = Optional[asyncpg.Pool] = None
    
    async def connect(self):
        self.pool = await asyncpg.create_pool(self.connection_string)
    
    async def disconnect(self):
        if self.pool:
            return await self.pool.close

    # INSERT/UPDATE/DELETE (вернёт статус)
    async def execute(self, query : str, *args) -> str:
        async with self.pool.acquire() as conn:
            return await conn.execute(query, *args)

    # Выборка
    async def fetch_all(self, query : str, *args) -> List[asyncpg.Record]:
        async with self.pool.fetch() as conn:
            return await conn.fetch(query, *args)
    
    async def fetch_one(self, query : str, *args) -> Optional[asyncpg.Record]:
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)
    
    # INSERT с возвратом ID
    async def execute_returning_id(self, query : str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchval(query, *args)
    
