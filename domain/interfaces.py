from domain.entities import UserSession, CatCharacteristics
from abc import ABC, abstractmethod
from typing import Optional, List


class ISessionRepository(ABC):
    @abstractmethod
    async def create_session(self, user_id: int) -> UserSession : pass

    # Поиск сессии
    @abstractmethod
    async def get_session(self, session_id :int) -> Optional[UserSession] : pass

    @abstractmethod
    async def update_session(self, session: UserSession) -> UserSession : pass 

    @abstractmethod
    async def delete_session(self, session_id : int) -> bool : pass

    @abstractmethod
    async def add_image_to_session(self, session_id : int, image_data : dict) -> bool : pass



class IRecommendationEngine(ABC):
    @abstractmethod
    async def get_recommendations(self, characteristics : CatCharacteristics) -> List[str] : pass



class IImageProcessingService(ABC):
    @abstractmethod
    async def analyze_image(self, image : bytes) -> CatCharacteristics : pass

    @abstractmethod
    async def validate_image(self, image : bytes) -> bool : pass

