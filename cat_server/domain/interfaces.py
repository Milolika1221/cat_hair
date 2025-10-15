from typing import List
from abc import ABC, abstractmethod

from domain.dtos import ImageData, ProcessingResult, RecommendationResult, SessionData, ValidationResult


class IUserSessionService(ABC):
    @abstractmethod
    async def create_session(self) -> str:  # возвращает session_id
        pass
    
    @abstractmethod 
    async def get_session(self, session_id: str) -> SessionData:
        pass

    @abstractmethod
    async def add_images_to_session(self, session_id: str, images_data: List[ImageData]) -> bool:
        pass

    @abstractmethod
    async def delete_session(self, session_id: str) -> bool:
        pass

class IImageProcessingService(ABC):
    @abstractmethod
    async def process_images(self, session_id: str) -> ProcessingResult:
        pass

    @abstractmethod
    async def validate_images(self, images_data: List[ImageData]) -> ValidationResult:
        pass

class IRecommendationService(ABC):
    @abstractmethod
    async def get_recommendations(self, cat_id: int) -> RecommendationResult:
        pass


