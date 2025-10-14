from datetime import datetime
from typing import List
from PIL import Image
import aiofiles
import io
import os
from infrastructure.neural_client import NeuralNetworkClient
from domain.dtos import ImageData, NeuralNetworkRequest, ImageProcessingResponse, ProcessingError, ProcessingResult, ValidationResult
from domain.interfaces import ICatCharacteristicsRepository, ICatImagesRepository, ICatsRepository, IImageProcessingService, IUserSessionService

class ImageProcessingService(IImageProcessingService):
    def __init__(
        self,
        user_session_service: IUserSessionService,
        cats_repository: ICatsRepository,
        images_repository: ICatImagesRepository,
        characteristics_repository: ICatCharacteristicsRepository,
        neural_client: NeuralNetworkClient,
        upload_dir: str = "uploads"
    ):
        self.user_session_service = user_session_service
        self.cats_repository = cats_repository
        self.images_repository = images_repository
        self.characteristics_repository = characteristics_repository
        self.neural_client = neural_client
        self.upload_dir = upload_dir
        
        os.makedirs(upload_dir, exist_ok=True)

    async def process_images(self, session_id : str) -> ProcessingResult:
        start_time = datetime.now()
        try:
            session = await self.user_session_service.get_session(session_id=session_id)
            if not session:
                raise ProcessingError("Сессия не найдена")
            validation = await self.validate_images(session.images)
            if not validation:
                raise ProcessingError('Валидация не пройдена', details=str(validation.error))
            
            cat = await self.cats_repository.create()

            orig_images_info = []
            for image_data in session.images:
                image_info = await self._save_original_image(cat.id, image_data)
                orig_images_info.append(image_info)
            
            neutral_request = NeuralNetworkRequest(
                session_id=session.session_id,
                cat_id=cat.id,
                images=session.images,
                processing_type='analysis_and_enhancement'
            )
            neutral_response = await self.neural_client.analyze_and_process_image(neutral_request)

            processed_images_info = []
            for processed_image in neutral_response.processed_images:
                image_info = await self._save_processed_image(cat.id, processed_image)
                processed_images_info.append(image_info)
            
            # характеристики просто ушуршат в БД
            characteristic = await self.characteristics_repository.create(
                cat_id=cat.id,
                color=neutral_response.analysis_result.color,
                hair_length=neutral_response.analysis_result.hair_length,
                confidence_level=neutral_response.analysis_result.confidence,
                analyzed_at=neutral_response.analysis_result.analysis_timestamp
                )
            
            # ответ пользователю
            processed_responses = [
                ImageProcessingResponse.from_image_data(img, 'enhanced')
                for img in neutral_response.processed_images
            ] # фоты после обработки 

            processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

            return ProcessingResult(
                session_id=session.session_id,
                cat_id=cat.id,
                characteristics=neutral_response.analysis_result,
                processed_images=processed_responses,
                processing_time=processing_time_ms,
                status='completed'
            )
        except Exception as e:
            processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return ProcessingResult(
                session_id=session_id,
                cat_id=0,
                characteristics=None,
                processed_images=[],
                processing_time=processing_time_ms,
                status='error',
                error=ProcessingError(
                    error_id="UNKNOWN_ERROR",
                    error_type="system",
                    message="Внутренняя ошибка сервера",
                    details=str(e)
                )
            )







    async def _save_original_image(self, cat_id: int, image_data: ImageData) -> dict:
        cat_dir = os.path.join(self.upload_dir, str(cat_id), "original")
        os.makedirs(cat_dir, exist_ok=True)
        
        # Сохраняем файл
        file_path = os.path.join(cat_dir, image_data.filename)
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(image_data.data)
        
        # Сохраняем в БД
        image_record = await self.images_repository.create(
            cat_id=cat_id,
            file_name=image_data.filename,
            file_path=file_path,
            file_size=image_data.size,
            resolution=image_data.resolution,
            format=image_data.format,
            is_processed=False
        )
        
        return {"id": image_record.id, "path": file_path}
    
    async def _save_processed_image(self, cat_id: int, image_data: ImageData) -> dict:
        # Создаем папку для обработанных изображений
        cat_dir = os.path.join(self.upload_dir, str(cat_id), "processed")
        os.makedirs(cat_dir, exist_ok=True)
        
        file_path = os.path.join(cat_dir, image_data.filename)
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(image_data.data)
        
        image_record = await self.images_repository.create(
            cat_id=cat_id,
            file_name=image_data.filename,
            file_path=file_path,
            file_size=image_data.size,
            resolution=image_data.resolution,
            format=image_data.format,
            is_processed=True
        )
        return {"id": image_record.id, "path": file_path}
    
    async def validate_images(self, images_data: List[ImageData]) -> ValidationResult:
        errors = []
        
        for image in images_data:
            # Проверка размера
            if image.size > 10 * 1024 * 1024:
                errors.append(ProcessingError(
                    error_id="VALIDATION_SIZE",
                    error_type="validation",
                    message=f"Изображение {image.filename} превышает 10MB",
                    suggestions=["Используйте изображение размером до 10MB"]
                ))
                continue
            
            try:
                with Image.open(io.BytesIO(image.data)) as img:
                    width, height = img.size
                    if width < 640 or height < 480:
                        errors.append(ProcessingError(
                            error_id="VALIDATION_RESOLUTION",
                            error_type="validation",
                            message=f"Изображение {image.filename} имеет недостаточное разрешение",
                            details=f"Текущее: {width}x{height}, минимальное: 640x480",
                            suggestions=["Используйте изображение с более высоким разрешением"]
                        ))
                    
                    image.resolution = f"{width}x{height}"
                    
            except Exception as e:
                errors.append(ProcessingError(
                    error_id="VALIDATION_FORMAT",
                    error_type="validation",
                    message=f"Неверный формат изображения {image.filename}",
                    details=str(e),
                    suggestions=["Используйте формат JPEG или PNG"]
                ))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )


