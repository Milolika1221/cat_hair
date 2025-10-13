from sqlalchemy import select
from sqlalchemy.orm import selectinload
from domain.interfaces import * 
from domain.entities import CatImages, Cats
from sqlalchemy.ext.asyncio import AsyncSession


class CatsRepository(ICatsRepository):
    def __init__(self, session : AsyncSession):
        self.session = session

    async def create(self, create):
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
        self.session.delete(cat)
        self.session.commit()
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
        self.session.commit()
        self.session.refresh(cat_images)
        return cat_images
        

    async def get_by_id(self, image_id):
        return await self.session.get(CatImages, image_id)

    async def save(self, cat_image):
        self.session.commit()
        self.session.refresh(cat_image)
        return cat_image
    
    async def delete(self, image_id):
        cat_image = await self.session.get(CatImages, image_id)
        if not cat_image : return False
        self.session.commit()
        self.session.delete(cat_image)
        return True

class CatCharacteristicsRepository(ICatCharacteristicsRepository):
    def __init__(self, session : AsyncSession):
        self.session = session

    async def create(self, cat_id: int, color: str, body_type: str, 
                    hair_length: str, confidence_level: float, 
                    analyzed_at: datetime) -> CatCharacteristics:
        characteristic = CatCharacteristics(
            cat_id=cat_id,
            color=color,
            body_type=body_type,
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
        result = await self.session.get(Recommendations, cat_id=cat_id)
        return result  

    async def save(self, cat_characteristic):
        self.session.commit()
        self.session.refresh(cat_characteristic)
        return cat_characteristic
    
    async def delete(self, characteristic_id):
        cat_image = await self.session.get(CatCharacteristics, characteristic_id)
        if not cat_image : return False
        self.session.commit()
        self.session.delete(cat_image)
        return True


class RecommendationRepository(IRecommendationRepository):
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
        self.session.commit()
        self.session.refresh(recommendation)
        return recommendation
    
    async def delete(self, recommendation_id):
        recommendation = await self.session.get(Recommendations, recommendation_id)
        if not recommendation : return False
        self.session.commit()
        self.session.delete(recommendation)
        return True
    
class ProcessingLogsRepository(IProcessingLogsRepository):
    def __init__(self, session : AsyncSession):
        self.session = session
    
    async def create(self, cat_id : int):
        logs = ProcessingLogs(cat_id=cat_id)
        self.session.add(logs)
        await self.session.commit()
        await self.session.refresh(logs)
        return logs
    
    async def get_by_id(self, log_id):
        return  await self.session.get(ProcessingLogs, log_id)

    async def save(self, logs):
        self.session.commit()
        self.session.refresh(logs)
        return logs
    
    async def delete(self, log_id):
        logs = await self.session.get(ProcessingLogs, log_id)
        if not logs : return False
        self.session.commit()
        self.session.delete(logs)
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
        sr = select(Haircuts)
        result = await self.session.execute(sr)
        return result

    async def get_all_by_recommendations(self, cat_id) -> List[Haircuts]:
        recommendation = RecommendationRepository.get_by_cat_id(cat_id)
        if not recommendation:
            return []
        haircuts_response = (
            select(Haircuts)
            .options(selectinload(Haircuts.id)
            .where(Haircuts.id == recommendation.id)
            )
        )
        result = await self.session.execute(haircuts_response)
        haircuts = result.scalars().all()
        return haircuts

    async def delete(self, haircut_id):
        haircut = await self.sessions.get(Haircuts, haircut_id)
        if not haircut: return False
        self.session.commit()
        self.session.delete(haircut)
        return True






