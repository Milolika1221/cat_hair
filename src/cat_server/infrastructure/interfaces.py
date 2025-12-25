from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from cat_server.infrastructure.entities import (
    Cats,
    Haircuts,
    ProcessingLogs,
    Recommendations,
)


class ICatsRepository(ABC):
    @abstractmethod
    async def create(self) -> Cats:
        pass

    @abstractmethod
    async def get_by_id(self, cat_id: int) -> Optional[Cats]:
        pass

    @abstractmethod
    async def delete(self, cat_id: int) -> bool:
        pass


class IRecommendationsRepository(ABC):
    @abstractmethod
    async def create(
        self, cat_id: int, haircut: int | str, confidence: float
    ) -> Recommendations:
        pass

    @abstractmethod
    async def get_by_id(self, recommendation_id: int) -> Optional[Recommendations]:
        pass

    @abstractmethod
    async def get_by_cat_id(self, cat_id: int) -> Recommendations | None:
        pass

    @abstractmethod
    async def get_by_cat_id_and_haircut(
        self, cat_id: int, haircut: int | str
    ) -> Recommendations | None:
        pass

    @abstractmethod
    async def delete(self, recommendation_id: int) -> bool:
        pass


class IHaircutsRepository(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    async def create(
        self,
        name: str,
        description: str,
        image_bytes: bytes,
    ) -> Haircuts:
        pass

    @abstractmethod
    async def get_all(self) -> List[Haircuts]:
        pass

    @abstractmethod
    async def get_by_id(self, haircut_id: int) -> Optional[Haircuts]:
        pass

    @abstractmethod
    async def get_by_cat_id(self, cat_id: int) -> Haircuts:
        pass

    @abstractmethod
    async def get_by_haircut_name(self, name: str) -> Optional[Haircuts]:
        pass

    @abstractmethod
    async def delete(self, haircut_id: int) -> bool:
        pass


class IProcessingLogsRepository(ABC):
    @abstractmethod
    async def create(
        self,
        cat_id: int,
        processing_time: float,
        status: str,
        error_message: Optional[str],
        processed_at: datetime,
    ) -> ProcessingLogs:
        pass

    @abstractmethod
    async def get_by_id(self, log_id: int) -> Optional[ProcessingLogs]:
        pass

    @abstractmethod
    async def get_by_cat_id(self, cat_id: int) -> List[ProcessingLogs]:  # Всегда список
        pass

    @abstractmethod
    async def delete(self, log_id: int) -> bool:
        pass
