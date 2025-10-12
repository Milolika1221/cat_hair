from domain.interfaces import * 
from domain.entities import CatImages, Cats
from sqlalchemy.ext.asyncio import AsyncSession


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
        result = await self.session.get(Cats, cat_id)
        return result 
    
    async def delete(self, cat_id):
        cat = await self.session.get(Cats, cat_id)
        if not cat : return False
        
        self.session.delete(cat)
        self.session.commit()
        return True


class CatImagesRepository(ICatImagesRepository):
    def __init__(self, session : AsyncSession):
        self.session = session
    
    async def create(self):
        cat_image = CatImages()
        self.session.add(cat_image)
        await self.session.commit()
        await self.session.refresh(cat_image)
        return cat_image
    
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



