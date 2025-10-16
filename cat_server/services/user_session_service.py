import asyncio
from datetime import datetime
from typing import List
import uuid

from cat_server.domain.interfaces import IUserSessionService, SessionData, ImageData



class UserSessionService(IUserSessionService):
    def __init__(self):
        self._lock = asyncio.Lock()
        self._sessions = {}
        self.session_id = None
    
    async def create_session(self) -> str:
        self.session_id = str(uuid.uuid4())
        async with self._lock:
            self._sessions[self.session_id] = SessionData(
                session_id=self.session_id,
                created_at=datetime.now(),
                images=[],
                status='active'
            )

            return self.session_id
    
    async def get_session(self, session_id : str) -> SessionData:
        async with self._lock:
            return self._sessions.get(session_id)

    async def add_images_to_session(self, session_id : str, images_data : List[ImageData]) -> bool:
        async with self._lock:
            if session_id not in self._sessions:
                return False
            for image in images_data:
                image.uploaded_at = datetime.now()
            self._sessions[session_id].images.extend(images_data)
            return True

    async def delete_session(self, session_id : str) -> bool:
        async with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
                return True
            return False
    
    







