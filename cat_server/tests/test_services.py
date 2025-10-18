import pytest
import asyncio
import  io
from PIL import  Image
from unittest.mock import AsyncMock
from cat_server.services.image_processing_service import ImageProcessingService
from cat_server.services.user_session_service import UserSessionService
from cat_server.domain.dto import ImageData

class TestUserSessionService:
    def setup_method(self):
        self.service = UserSessionService()
    
    @pytest.mark.asyncio
    async def test_create_session(self):
        session_id = await self.service.create_session() # строковый ID
        
        assert isinstance(session_id, str)
        assert len(session_id) == 36  # UUID длина
        
        # Проверяем, что сессия создалась
        session = await self.service.get_session(session_id)
        assert session is not None
        assert session.session_id == session_id
        assert session.status == 'active'
    
    @pytest.mark.asyncio 
    async def test_add_images_to_session(self):
        """Тест добавления изображений в сессию"""
        session_id = await self.service.create_session()

        img = Image.new('RGB', (1, 1), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        # Создаем тестовые изображения
        test_images = [
            ImageData(
                file_name="test1.jpg",
                data=img_bytes.getvalue(),
                size=1000,
                format="JPEG"
            )
        ]
        
        success = await self.service.add_images_to_session(session_id, test_images)
        assert success is True
        
        # Проверяем, что изображения добавились
        session = await self.service.get_session(session_id)
        assert len(session.images) == 1
        assert session.images[0].file_name == "test1.jpg"

class TestImageProcessingService:
    def setup_method(self):
        self.mock_session_service = AsyncMock()
        self.mock_neural_client = AsyncMock()
        
        self.service = ImageProcessingService(
            user_session_service=self.mock_session_service,
            cats_repo=AsyncMock(),
            images_repo=AsyncMock(),
            characteristics_repo=AsyncMock(),
            neural_client=self.mock_neural_client
        )
    
    @pytest.mark.asyncio
    async def test_validate_images_success(self):
        """Тест успешной валидации изображений"""
        img = Image.new('RGB', (1920, 1080), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        valid_images = [
            ImageData(
                file_name="test.jpg",
                data=img_bytes.getvalue(),
                size=5 * 1024 * 1024,  # 5MB
                format="JPEG"
            )
        ]
        
        result = await self.service.validate_images(valid_images)
        assert result.is_valid is True
        assert len(result.errors) == 0
    
    @pytest.mark.asyncio
    async def test_validate_images_too_large(self):
        """Тест валидации слишком большого изображения"""
        large_images = [
            ImageData(
                file_name="large.jpg",
                data=b"fake_data",
                size=15 * 1024 * 1024,  # 15MB - больше лимита
                format="JPEG"
            )
        ]
        
        result = await self.service.validate_images(large_images)
        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "превышает" in result.errors[0].message