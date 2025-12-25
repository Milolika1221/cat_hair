import uuid
from datetime import datetime

import redis.asyncio as aioredis

from cat_server.domain.dto import ImageData, SessionData


class UserSessionService:
    def __init__(self, redis: aioredis.Redis, session_ttl: int = 3600):
        self.redis = redis
        self.session_ttl = session_ttl

    async def create_session(self) -> str:
        session_id = str(uuid.uuid4())
        session = SessionData(
            session_id=session_id,
            created_at=datetime.now(),
            status="active",
        )
        await self._save_session(session_id, session)
        print(f"✅ Session created and stored in Redis: {session_id}")
        return session_id

    async def get_session(self, session_id: str) -> SessionData:
        data = await self.redis.get(f"session:{session_id}")
        if data is None:
            raise ValueError(f"Session {session_id} not found")
        return SessionData.model_validate_json(data)

    async def add_image_to_session(
        self, session_id: str, image_data: ImageData
    ) -> bool:
        try:
            session = await self.get_session(session_id)
            session.status = "processing"
            session.image = image_data
            await self._save_session(session_id, session)
            return True
        except ValueError:
            return False

    async def link_cat_to_session(self, session_id: str, cat_id: int) -> bool:
        try:
            session = await self.get_session(session_id)
            session.cat_id = cat_id
            await self._save_session(session_id, session)
            return True
        except ValueError:
            return False

    async def delete_session(self, session_id: str) -> bool:
        result = await self.redis.delete(f"session:{session_id}")
        return result > 0

    async def _save_session(self, session_id: str, session: SessionData) -> None:
        await self.redis.setex(
            f"session:{session_id}",
            self.session_ttl,
            session.model_dump_json(),
        )
