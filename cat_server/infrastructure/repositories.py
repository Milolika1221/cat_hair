from abc import ABC, abstractmethod
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime

from cat_server.domain.entities import CatImages, Cats, CatCharacteristics, Recommendations, ProcessingLogs, Haircuts


# Контракты для работы с репозиториями (сущностями БД)
class ICatsRepository(ABC):
    @abstractmethod
    async def create(self) : pass
    
    @abstractmethod
    async def get_by_id(self, cat_id : int) -> Cats : pass

    @abstractmethod
    async def save(self, cat : Cats) -> Cats : pass

    @abstractmethod
    async def delete(self, cat_id : int) -> bool : pass


class ICatImagesRepository(ABC):
    @abstractmethod
    async def create(self,
                    cat_id: int,
                    file_name: str,
                    file_path: str,
                    file_size: int,
                    resolution: str,
                    format: str) -> CatImages:
        pass

    @abstractmethod
    async def get_by_id(self, cat_id : int) -> CatImages : pass

    @abstractmethod
    async def save(self, cat_image : CatImages) -> CatImages : pass
    
    @abstractmethod
    async def delete(self, image_id : int) -> bool : pass


class ICatCharacteristicsRepository(ABC):
    @abstractmethod
    async def create(self, 
                    cat_id: int,
                    color: str,
                    hair_length: str,
                    confidence_level: float,
                    analyzed_at: datetime) -> CatCharacteristics:
        pass
    
    @abstractmethod
    async def get_by_id(self, characteristic_id : int) -> CatCharacteristics : pass
    
    @abstractmethod
    async def get_by_cat_id(self, cat_id : int) -> CatCharacteristics : pass
    
    @abstractmethod
    async def save(self, characteristic: CatCharacteristics) -> CatCharacteristics : pass

    @abstractmethod
    async def delete(self, characteristic_id : int) -> bool : pass

class IRecommendationRepository(ABC):
    @abstractmethod
    async def create(self, cat_id : int, haircut_id : int,
                    is_no_haircut_required : bool, reason : str, created_at : datetime) -> Recommendations : pass 
    
    @abstractmethod
    async def get_by_id(self, recommendation_id : int) -> Recommendations : pass

    @abstractmethod
    async def get_by_cat_id(self, cat_id : int) -> Recommendations : pass

    @abstractmethod
    async def save(self, recommendation : Recommendations) -> Recommendations : pass

    @abstractmethod
    async def delete(self, recommendation_id : int) -> bool : pass


class IHaircutsRepository(ABC):
    @abstractmethod
    async def create(self, recommendation_id : int, name : str, description : str,
                    suitable_colors : str, suitable_hair_length) -> Haircuts : pass 
    
    @abstractmethod
    async def get_all(self) -> List[Haircuts]: pass 

    @abstractmethod
    async def get_all_by_recommendations(self, cat_id : int) -> List[Haircuts] : pass

    @abstractmethod
    async def get_by_id(self, haircut_id : int) -> Haircuts : pass

    @abstractmethod
    async def save(self, haircut : Haircuts) -> Haircuts : pass

    @abstractmethod
    async def delete(self, haircut_id : int) -> bool : pass


class IProcessingLogsRepository(ABC):
    @abstractmethod
    async def create(self, cat_id : int, processing_time : float,
                    status : str, error_message : str, processed_at) -> ProcessingLogs : pass

    @abstractmethod
    async def get_by_id(self, log_id : int) -> ProcessingLogs : pass

    @abstractmethod
    async def get_by_cat_id(self, cat_id : int) -> ProcessingLogs : pass

    @abstractmethod
    async def save(self, log : ProcessingLogs) -> ProcessingLogs : pass

    @abstractmethod
    async def delete(self, log_id : int) -> bool : pass




class CatsRepository(ICatsRepository):
    def __init__(self, session : AsyncSession):
        self.session = session

    async def create(self):
        cat = Cats()
        self.session.add(cat)
        await self.session.commit()
        await self.session.refresh(cat)
        return cat
    
    async def save(self, cat):
        await self.session.commit()
        await self.session.refresh(cat)
        return cat
    
    async def get_by_id(self, cat_id):
        return await self.session.get(Cats, cat_id)
    
    async def delete(self, cat_id):
        cat = await self.session.get(Cats, cat_id)
        if not cat : return False
        await self.session.delete(cat)
        await self.session.commit()
        return True


class CatImagesRepository(ICatImagesRepository):
    def __init__(self, session : AsyncSession):
        self.session = session
    
    async def create(self, cat_id : int, file_path : str,
                    file_size : int, resolution : str, format : str, 
                    uploaded_at : str) -> CatImages : 
        cat_images = CatImages(cat_id=cat_id, file_path=file_path,
                                file_size=file_size, resolution=resolution,
                                format=format, uploaded_at=uploaded_at)
        self.session.add(cat_images)
        await self.session.commit()
        await self.session.refresh(cat_images)
        return cat_images
        

    async def get_by_id(self, image_id):
        return await self.session.get(CatImages, image_id)

    async def save(self, cat_image):
        await self.session.commit()
        await self.session.refresh(cat_image)
        return cat_image
    
    async def delete(self, image_id):
        cat_image = await self.session.get(CatImages, image_id)
        if not cat_image : return False
        await self.session.commit()
        await self.session.delete(cat_image)
        return True

class CatCharacteristicsRepository(ICatCharacteristicsRepository):
    def __init__(self, session : AsyncSession):
        self.session = session

    async def create(self, cat_id: int, color: str,
                    hair_length: str, confidence_level: float, 
                    analyzed_at: datetime) -> CatCharacteristics:

        characteristic = CatCharacteristics(
            cat_id=cat_id,
            color=color,
            hair_length=hair_length,
            confidence_level=confidence_level,
            analyzed_at=analyzed_at
        )

        self.session.add(characteristic)
        await self.session.commit()
        await self.session.refresh(characteristic)
        return characteristic
    
    async def get_by_id(self, cat_characteristic_id):
        return await self.session.get(CatCharacteristics, cat_characteristic_id)

    async def get_by_cat_id(self, cat_id) -> CatCharacteristics:
        result = await self.session.get(CatCharacteristics, cat_id)
        return result  

    async def save(self, cat_characteristic):
        await self.session.commit()
        await self.session.refresh(cat_characteristic)
        return cat_characteristic
    
    async def delete(self, characteristic_id):
        cat_image = await self.session.get(CatCharacteristics, characteristic_id)
        if not cat_image : return False
        await self.session.commit()
        await self.session.delete(cat_image)
        return True


class RecommendationRepository(IRecommendationRepository, ABC):
    def __init__(self, session : AsyncSession):
        self.session = session
    
    async def create(self, cat_id, haircut_id, is_no_haircut_required, reason, created_at) -> Recommendations:
        recommendations = Recommendations(cat_id=cat_id, haircut_id=haircut_id,
                                        is_no_haircut_required=is_no_haircut_required, reason=reason,
                                        created_at=created_at)
        self.session.add(recommendations)
        await self.session.commit()
        await self.session.refresh(recommendations)
        return recommendations

    async def get_by_id(self, recommendation_id):
        return await self.session.get(Recommendations, recommendation_id)

    async def save(self, recommendation):
        await self.session.commit()
        await self.session.refresh(recommendation)
        return recommendation
    
    async def delete(self, recommendation_id):
        recommendation = await self.session.get(Recommendations, recommendation_id)
        if not recommendation : return False
        await self.session.commit()
        await self.session.delete(recommendation)
        return True
    
class ProcessingLogsRepository(IProcessingLogsRepository):
    def __init__(self, session : AsyncSession):
        self.session = session


    async def create(self, cat_id : int, processing_time : float,
                    status : str, error_message : str, processed_at : datetime):

        logs = ProcessingLogs(cat_id=cat_id, processing_time=processing_time, status=status,
                              error_message=error_message, processed_at=processed_at)
        self.session.add(logs)
        await self.session.commit()
        await self.session.refresh(logs)
        return logs
    
    async def get_by_id(self, log_id):
        return  await self.session.get(ProcessingLogs, log_id)

    async def save(self, logs):
        await self.session.commit()
        await self.session.refresh(logs)
        return logs

    async def get_by_cat_id(self, cat_id : int) -> ProcessingLogs:
        return await self.session.get(ProcessingLogs, cat_id=cat_id)
    
    async def delete(self, log_id):
        logs = await self.session.get(ProcessingLogs, log_id)
        if not logs : return False
        await self.session.commit()
        await self.session.delete(logs)
        return True
    

class HaircutsRepository(IHaircutsRepository):
    def __init__(self, session : AsyncSession):
        self.session = session

    async def create(self, recommendation_id, name, description, suitable_colors, suitable_hair_length):
        haircut = Haircuts(id=recommendation_id, 
                        name=name, description=description,
                        suitable_colors=suitable_colors,
                        suitable_hair_length=suitable_hair_length)
        self.session.add(haircut)
        await self.session.commit()
        await self.session.refresh(haircut)
        return haircut
    
    async def get_by_id(self, haircut_id):
        return await self.session.get(Haircuts, haircut_id)

    async def get_all(self):
        result = await self.session.execute(select(Haircuts))
        return result

    async def get_all_by_recommendations(self, cat_id) -> List[Haircuts]:
        recommendation = RecommendationRepository.get_by_cat_id(cat_id)
        if not recommendation:
            return []
        result = await self.session.execute(select(Haircuts)
            .options(selectinload(Haircuts.id)
            .where(Haircuts.id == recommendation.id)))
        haircuts = result.scalars().all()
        return haircuts

    async def get_by_criteria(self, hair_length: str, colors: str) -> List[Haircuts]:
        result = await self.session.execute(
            select(Haircuts).where(
                Haircuts.suitable_hair_lengths.contains([hair_length]),
                Haircuts.suitable_color.contains([colors])
            )
        )
        return result

    async  def save(self, haircut : Haircuts) -> Haircuts:
        await self.session.commit()
        await self.session.refresh(haircut)
        return haircut

    async def delete(self, haircut_id):
        haircut = await self.session.get(Haircuts, haircut_id)
        if not haircut: return False
        await self.session.commit()
        await self.session.delete(haircut)
        return True






