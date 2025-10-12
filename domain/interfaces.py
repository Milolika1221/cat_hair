from domain.entities import CatCharacteristics, CatImages, Cats, Haircuts, ProcessingLogs, Recommendations
from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession 

# Контракты для работы с репозиториями (сущностями БД)
class ICatsRepository(ABC):
    @abstractmethod
    async def create(self) -> Cats : pass 
    
    @abstractmethod
    async def get_by_id(self, cat_id : int) -> Cats : pass

    @abstractmethod
    async def save(self, cat : Cats) -> Cats : pass

    @abstractmethod
    async def delete(self, cat_id : int) -> bool : pass


class ICatImagesRepository(ABC):
    @abstractmethod
    async def create(self) -> CatImages : pass

    @abstractmethod
    async def get_by_id(self, cat_id : int) -> CatImages : pass

    @abstractmethod
    async def save(self, cat_image : CatImages) -> CatImages : pass
    
    @abstractmethod
    async def delete(self, image_id : int) -> bool : pass


class ICatCharacteristicsRepository(ABC):
    @abstractmethod
    async def create(self) -> Cats : pass 
    
    @abstractmethod
    async def get_by_id(self, characteristic_id : int) -> CatCharacteristics : pass

    @abstractmethod
    async def save(self, characteristic: CatCharacteristics) -> CatCharacteristics : pass

    @abstractmethod
    async def delete(self, characteristic_id : int) -> bool : pass

class IRecommendationRepository(ABC):
    @abstractmethod
    async def create(self) -> Recommendations : pass 
    
    @abstractmethod
    async def get_by_id(self, recommendation_id : int) -> Recommendations : pass

    @abstractmethod
    async def save(self, recommendation : Recommendations) -> Recommendations : pass

    @abstractmethod
    async def delete(self, recommendation_id : int) -> bool : pass


class IHaircutsRepository(ABC):
    @abstractmethod
    async def create(self) -> Haircuts : pass 
    
    @abstractmethod
    async def get_by_id(self, haircut_id : int) -> Haircuts : pass

    @abstractmethod
    async def save(self, haircut : Haircuts) -> Haircuts : pass

    @abstractmethod
    async def delete(self, haircut_id : int) -> bool : pass


class IProcessingLogsRepository(ABC):
    @abstractmethod
    async def create(self) -> ProcessingLogs : pass 
    
    @abstractmethod
    async def get_by_id(self, log_id : int) -> ProcessingLogs : pass

    @abstractmethod
    async def save(self, log : ProcessingLogs) -> ProcessingLogs : pass

    @abstractmethod
    async def delete(self, log_id : int) -> bool : pass


# Контракты для сервисов (UserSession, RecommendationService, ImageProcessingService)


