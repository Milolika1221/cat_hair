import asyncio
import uuid
from datetime import datetime
from typing import Dict

from cat_server.domain.interfaces import ImageData, IUserSessionService, SessionData


class UserSessionService(IUserSessionService):
    def __init__(self):
        self._lock = asyncio.Lock()
        self._sessions: Dict[str, SessionData] = {}
        self.session_id = None

    async def create_session(self) -> str:
        self.session_id = str(uuid.uuid4())
        async with self._lock:
            self._sessions[self.session_id] = SessionData(
                session_id=self.session_id,
                created_at=datetime.now(),
                image=None,
                status="active",
            )
            print(f"✅ Session created and stored: {self.session_id}")
            return self.session_id

    async def get_session(self, session_id: str) -> SessionData:
        async with self._lock:
            if session_id not in self._sessions:
                raise ValueError(f"Session {session_id} not found")
            return self._sessions[session_id]

    async def add_image_to_session(
        self, session_id: str, image_data: ImageData
    ) -> bool:
        async with self._lock:
            if session_id not in self._sessions:
                return False
            self._sessions[session_id].status = "processing"
            self._sessions[session_id].image = image_data
            return True

    async def link_cat_to_session(self, session_id: str, cat_id: int) -> bool:
        async with self._lock:
            if session_id not in self._sessions:
                return False
            self._sessions[session_id].cat_id = cat_id
            return True

    async def delete_session(self, session_id: str) -> bool:
        async with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False
