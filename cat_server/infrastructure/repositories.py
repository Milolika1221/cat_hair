# cat_server/infrastructure/repositories.py

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cat_server.infrastructure.entities import (
    Cats,
    Haircuts,
    ProcessingLogs,
    Recommendations,
)

# Настройка логгера
logger = logging.getLogger(__name__)


# --- Интерфейсы (Contracts) ---
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


# --- Реализации (Implementations) ---


class CatsRepository(ICatsRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        logger.debug("CatsRepository инициализирован")

    async def create(self) -> Cats:
        logger.debug("Создание нового кота")
        cat = Cats()
        self.session.add(cat)
        await self.session.commit()
        await self.session.refresh(cat)
        logger.info(f"Кот создан с ID: {cat.id}")
        return cat

    async def get_by_id(self, cat_id: int) -> Optional[Cats]:
        logger.debug(f"Получение кота по ID: {cat_id}")
        cat = await self.session.get(Cats, cat_id)
        if cat:
            logger.debug(f"Кот найден: ID={cat.id}")
        else:
            logger.warning(f"Кот с ID {cat_id} не найден")
        return cat

    async def delete(self, cat_id: int) -> bool:
        logger.debug(f"Удаление кота по ID: {cat_id}")
        cat = await self.session.get(Cats, cat_id)
        if not cat:
            logger.warning(f"Кот с ID {cat_id} не найден для удаления")
            return False
        await self.session.delete(cat)
        await self.session.commit()
        logger.info(f"Кот с ID {cat_id} удален")
        return True


class RecommendationsRepository(IRecommendationsRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self, cat_id: int, haircut: int | str, confidence: float
    ) -> Recommendations:
        haircut_id = None
        if isinstance(haircut, str):
            haircut_id = select(Haircuts.id).where(Haircuts.name == haircut)
        else:
            haircut_id = haircut
        recommendation = Recommendations(
            cat_id=cat_id, haircut_id=haircut_id, confidence=confidence
        )
        self.session.add(recommendation)
        await self.session.commit()
        await self.session.refresh(recommendation)
        return recommendation

    async def get_by_id(self, recommendation_id: int) -> Optional[Recommendations]:
        logger.debug(f"Получение рекомендации по ID: {recommendation_id}")
        recommendation = await self.session.get(Recommendations, recommendation_id)
        return recommendation

    async def get_by_cat_id(self, cat_id: int) -> Recommendations | None:
        try:
            stmt = select(Recommendations).where(Recommendations.cat_id == cat_id)
            result = await self.session.execute(stmt)
            recommendation = result.scalar()
            return recommendation
        except Exception as e:
            logger.error(f"Ошибка при получении рекомендаций для cat_id={cat_id}: {e}")
            return None

    async def get_by_cat_id_and_haircut(
        self, cat_id: int, haircut: int | str
    ) -> Recommendations | None:
        try:
            if isinstance(haircut, int):
                stmt = select(Recommendations).where(
                    Recommendations.cat_id == cat_id,
                    Recommendations.haircut_id == haircut,
                )
            else:
                stmt = select(Recommendations).where(
                    Recommendations.cat_id == cat_id,
                    Recommendations.haircut_id == Haircuts.get_id_by_name(haircut),
                )
            result = await self.session.execute(stmt)
            recommendation = result.scalar_one_or_none()
            return recommendation
        except Exception as e:
            logger.error(
                f"Ошибка при получении рекомендации для cat_id={cat_id} и haircut={haircut}: {e}"
            )
            return None

    async def delete(self, recommendation_id: int) -> bool:
        recommendation = await self.session.get(Recommendations, recommendation_id)
        if not recommendation:
            logger.warning(
                f"Рекомендация с ID {recommendation_id} не найдена для удаления"
            )
            return False
        await self.session.delete(recommendation)
        await self.session.commit()
        return True


class ProcessingLogsRepository(IProcessingLogsRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        cat_id: int,
        processing_time: float,
        status: str,
        error_message: Optional[str],
        processed_at: datetime,
    ) -> ProcessingLogs:
        logger.debug(f"Создание лога обработки для cat_id={cat_id}")
        log = ProcessingLogs(
            cat_id=cat_id,
            processing_time=processing_time,
            status=status,
            error_message=error_message,
            processed_at=processed_at,
        )
        self.session.add(log)
        await self.session.commit()
        await self.session.refresh(log)
        logger.info(f"Лог обработки создан: ID={log.id}, cat_id={log.cat_id}")
        return log

    async def get_by_id(self, log_id: int) -> Optional[ProcessingLogs]:
        logger.debug(f"Получение лога обработки по ID: {log_id}")
        log = await self.session.get(ProcessingLogs, log_id)
        if log:
            logger.debug(f"Лог обработки найден: ID={log.id}")
        else:
            logger.warning(f"Лог обработки с ID {log_id} не найден")
        return log

    async def get_by_cat_id(self, cat_id: int) -> List[ProcessingLogs]:
        logger.debug(f"Получение логов обработки по cat_id: {cat_id}")
        try:
            stmt = select(ProcessingLogs).where(ProcessingLogs.cat_id == cat_id)
            result = await self.session.execute(stmt)
            logs = list(result.scalars().all())
            logger.debug(f"Найдено {len(logs)} логов для cat_id={cat_id}")
            return logs
        except Exception as e:
            logger.error(f"Ошибка при получении логов для cat_id={cat_id}: {e}")
            return []

    async def delete(self, log_id: int) -> bool:
        logger.debug(f"Удаление лога обработки по ID: {log_id}")
        log = await self.session.get(ProcessingLogs, log_id)
        if not log:
            logger.warning(f"Лог обработки с ID {log_id} не найден для удаления")
            return False
        await self.session.delete(log)
        await self.session.commit()
        logger.info(f"Лог обработки с ID {log_id} удален")
        return True


class HaircutsRepository(IHaircutsRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        logger.debug("HaircutsRepository инициализирован")

    async def create(
        self,
        name: str,
        description: str,
        image_bytes: bytes,
    ) -> Haircuts:
        haircut = Haircuts(
            name=name,
            description=description,
            image_bytes=image_bytes,
        )
        logger.debug(f"Создание стрижки с ID/рекомендацией: {haircut.id}")
        self.session.add(haircut)
        await self.session.commit()
        await self.session.refresh(haircut)
        logger.info(f"Стрижка создана: ID={haircut.id}")
        return haircut

    async def get_by_id(self, haircut_id: int) -> Optional[Haircuts]:
        logger.debug(f"Получение стрижки по ID: {haircut_id}")
        haircut = await self.session.get(Haircuts, haircut_id)
        if haircut:
            logger.debug(f"Стрижка найдена: ID={haircut.id}")
        else:
            logger.warning(f"Стрижка с ID {haircut_id} не найдена")
        return haircut

    async def get_all(self) -> List[Haircuts]:
        logger.debug("Получение всех стрижек")
        try:
            stmt = select(Haircuts)
            result = await self.session.execute(stmt)
            haircuts = list(result.scalars().all())
            logger.debug(f"Получено {len(haircuts)} стрижек")
            return haircuts
        except Exception as e:
            logger.error(f"Ошибка при получении всех стрижек: {e}")
            return []

    async def get_all_by_haircuts(self, cat_id: int) -> List[Haircuts]:
        logger.debug(f"Получение стрижек по рекомендациям для cat_id: {cat_id}")
        try:
            # Получаем рекомендации для кота
            rec_stmt = select(Recommendations).where(Recommendations.cat_id == cat_id)
            rec_result = await self.session.execute(rec_stmt)
            recommendations = rec_result.scalars().all()

            if not recommendations:
                logger.warning(f"Рекомендации для cat_id={cat_id} не найдены")
                return []

            haircut_ids = [
                rec.haircut_id for rec in recommendations if rec.haircut_id is not None
            ]
            if not haircut_ids:
                logger.warning(
                    f"Рекомендации для cat_id={cat_id} не содержат действительных haircut_id"
                )
                return []

            # Получаем стрижки по списку ID
            haircut_stmt = select(Haircuts).where(Haircuts.id.in_(haircut_ids))
            haircut_result = await self.session.execute(haircut_stmt)
            haircuts = list(haircut_result.scalars().all())

            logger.debug(
                f"Найдено {len(haircuts)} стрижек по рекомендациям для cat_id={cat_id}"
            )
            return haircuts

        except Exception as e:
            logger.error(
                f"Ошибка при получении стрижек по рекомендациям для cat_id={cat_id}: {e}"
            )
            return []

    async def get_by_cat_id(self, cat_id: int) -> Haircuts | None:
        stmt = (
            select(Haircuts)
            .join(Recommendations)
            .where(
                Recommendations.cat_id == cat_id
                and Recommendations.haircut_id == Haircuts.id
            )
        )
        result = await self.session.execute(stmt)

        haircut = result.scalar_one_or_none()
        return haircut

    async def get_by_haircut_name(self, name: str) -> Optional[Haircuts]:
        stmt = select(Haircuts).where(Haircuts.name == name)
        result = await self.session.execute(stmt)
        return result.scalar()

    async def delete(self, haircut_id: int) -> bool:
        logger.debug(f"Удаление стрижки по ID: {haircut_id}")
        haircut = await self.session.get(Haircuts, haircut_id)
        if not haircut:
            logger.warning(f"Стрижка с ID {haircut_id} не найдена для удаления")
            return False
        await self.session.delete(haircut)
        await self.session.commit()
        logger.info(f"Стрижка с ID {haircut_id} удалена")
        return True
