# services/image_processing_service.py

import asyncio
import base64
import json
import os
import io
from datetime import datetime
from typing import Dict, Optional, List, Any
import logging

import aiohttp
from PIL import Image as PILImage
import aiofiles

from cat_server.api.schemas import (
    ImageData,
    NeuralNetworkRequest,
    ProcessingResult,
    ProcessingError,
    ProcessingException,
    ImageProcessingResponse,
    ValidationResult,
)
from cat_server.domain.dto import NeuralNetworkResponse, AnalysisResult
from cat_server.infrastructure.repositories import ICatsRepository, ICatImagesRepository, ICatCharacteristicsRepository
from cat_server.services.user_session_service import UserSessionService

# ✅ Настройка логгера
logger = logging.getLogger(__name__)

class NeuralNetworkClient:
    def __init__(self, base_url : str, timeout : int = 60):
        self.base_url = base_url
        self.timeout = timeout
        logger.info(f"🔧 NeuralNetworkClient инициализирован с URL: {base_url}, timeout: {timeout}")

    async def analyze_and_process_image(self, request : NeuralNetworkRequest) -> NeuralNetworkResponse | None :
        logger.info(f"📤 Отправка запроса в нейросеть: session_id={request.session_id}, cat_id={request.cat_id}")
        async with aiohttp.ClientSession() as session :
            form_data = aiohttp.FormData()
            for image in request.images:
                form_data.add_field(
                    name='image',
                    value=image.data,
                    filename=f'{image.filename}',
                    content_type=f'image/{image.format.lower()}'
                )

            metadata = {
                'session_id' : request.session_id,
                'cat_id' : request.cat_id,
                'processed_at' : request.processing_type,
                'total_image' : len(request.images),
                'image_metadata' : [
                    {
                        'filename' : img.filename,
                        'format' : img.format,
                        'size' : img.size,
                        'resolution' : img.resolution
                    } for img in request.images
                ]
            }
            form_data.add_field('metadata', json.dumps(metadata))
            try :
                logger.debug(f"📡 Отправка POST-запроса на {self.base_url}")
                async with session.post(
                        f'{self.base_url}',
                        data=form_data,
                        timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response :
                    logger.info(f"📥 Получен ответ от нейросети: статус {response.status}")
                    if response.status == 200 :
                        response_data = await response.json()
                        logger.debug(f"✅ Успешный ответ от нейросети: {response_data}")
                        return self._parse_success_response(response_data)
                    else:
                        await self._handle_http_error(response)
            except asyncio.TimeoutError:
                logger.error("⏰ Таймаут при запросе к нейросети")
                raise ProcessingException(ProcessingError(
                    error_id="NEURAL_API_TIMEOUT",
                    error_type="neural_api",
                    message="Нейросеть не ответила вовремя",
                    suggestions=["Увеличьте timeout", "Попробуйте позже"]
                ))

            except aiohttp.ClientError as e:
                logger.exception("🔌 Ошибка подключения к нейросети")
                raise ProcessingException(ProcessingError(
                    error_id="NEURAL_API_CONNECTION",
                    error_type="neural_api",
                    message="Ошибка подключения к нейросети",
                    details=str(e),
                    suggestions=["Проверьте интернет-соединение", "Проверьте URL API"]
                ))

    @staticmethod
    def _parse_success_response(data: Dict[str, Any]) -> NeuralNetworkResponse:
        logger.debug("🔄 Парсинг успешного ответа от нейросети")
        analysis_data = data.get('analysis_result', {})
        analysis_result = AnalysisResult(
            color=analysis_data.get('color', 'не определен'),
            hair_length=analysis_data.get('hair_length', 'не определен'),
            confidence=analysis_data.get('confidence', 0.0),
            analysis_timestamp=datetime.fromisoformat(
                analysis_data.get('analysis_timestamp', datetime.now().isoformat())
            )
        )

        processed_images = []
        for img_data in data.get('processed_images', []):
            image_bytes = base64.b64decode(img_data['data'])
            processed_images.append(ImageData(
                filename=img_data['filename'],
                data=image_bytes,
                size=len(image_bytes),
                format=img_data['format'],
                resolution=img_data.get('resolution'),
                is_processed=True
            ))

        result = NeuralNetworkResponse(
            analysis_result=analysis_result,
            processed_images=processed_images,
            processing_time_ms=data.get('processing_time_ms', 0),
            processing_metadata=data.get('processing_metadata', {})
        )
        logger.info("✅ Ответ от нейросети успешно распарсен")
        return result

    @staticmethod
    async def _handle_http_error(response: aiohttp.ClientResponse):
        error_text = await response.text()
        logger.warning(f"⚠️ Нейросеть вернула ошибку: статус {response.status}, текст: {error_text}")

        error_mapping = {
            400: ("NEURAL_API_BAD_REQUEST", "Некорректный запрос"),
            401: ("NEURAL_API_UNAUTHORIZED", "Неавторизованный доступ"),
            403: ("NEURAL_API_FORBIDDEN", "Доступ запрещен"),
            404: ("NEURAL_API_NOT_FOUND", "Ресурс не найден"),
            429: ("NEURAL_API_RATE_LIMIT", "Превышен лимит запросов"),
            500: ("NEURAL_API_SERVER_ERROR", "Внутренняя ошибка нейросети"),
            503: ("NEURAL_API_UNAVAILABLE", "Сервис недоступен")
        }

        error_id, default_message = error_mapping.get(
            response.status,
            ("NEURAL_API_UNKNOWN", "Неизвестная ошибка")
        )

        raise ProcessingException(ProcessingError(
            error_id=error_id,
            error_type="neural_api",
            message=f"{default_message} (статус: {response.status})",
            details=error_text[:500],
            suggestions=NeuralNetworkClient._get_error_suggestions(response.status)
        ))

    @staticmethod
    def _get_error_suggestions(status_code: int) -> List[str]:
        """Возвращает подсказки по устранению ошибок"""
        suggestions = {
            400: ["Проверьте формат отправляемых изображений", "Убедитесь в корректности метаданных"],
            429: ["Уменьшите частоту запросов", "Попробуйте позже"],
            500: ["Попробуйте позже", "Свяжитесь с поддержкой ИИ сервиса"],
            503: ["Сервис временно недоступен", "Попробуйте через несколько минут"]
        }
        return suggestions.get(status_code, ["Попробуйте позже", "Обратитесь в поддержку"])


class ImageProcessingService:
    def __init__(
        self,
        user_session_service: UserSessionService,
        cats_repo: ICatsRepository,
        images_repo: ICatImagesRepository,
        characteristics_repo: ICatCharacteristicsRepository,
        neural_client: NeuralNetworkClient,
        upload_dir: str = "uploads"
    ):
        self.user_session_service = user_session_service
        self.cats_repo = cats_repo
        self.images_repo = images_repo
        self.characteristics_repo = characteristics_repo
        self.neural_client = neural_client
        self.upload_dir = upload_dir

        os.makedirs(upload_dir, exist_ok=True)
        logger.info(f"📁 ImageProcessingService инициализирован, upload_dir: {upload_dir}")

    async def process_images(self, session_id: str, cat_id: int, images_data: List[ImageData]) -> ProcessingResult:
        start_time = datetime.now()
        logger.info(f"🚀 Начало обработки изображений: session_id={session_id}, cat_id={cat_id}, images={len(images_data)}")
        try:
            session_images = images_data

            validation = await self.validate_images(session_images)
            if not validation.is_valid:
                logger.warning(f"❌ Валидация не пройдена: {[err.message for err in validation.errors]}")
                raise ProcessingException(ProcessingError(
                    error_id="VALIDATION_FAILED",
                    error_type="validation",
                    message="Валидация не пройдена",
                    details=str([err.message for err in validation.errors])
                ))

            cat = await self.cats_repo.get_by_id(cat_id)
            if not cat:
                logger.warning(f"🐱 Кот не найден: cat_id={cat_id}")
                raise ProcessingException(ProcessingError(
                    error_id="CAT_NOT_FOUND",
                    error_type="database",
                    message="Кот не найден"
                ))

            logger.info("💾 Сохранение оригинальных изображений...")
            orig_images_info = []
            for image_data in session_images:
                image_info = await self._save_original_image(cat_id, image_data)
                orig_images_info.append(image_info)

            nn_request = NeuralNetworkRequest(
                session_id=session_id,
                cat_id=cat_id,
                images=session_images,
                processing_type='analysis_and_enhancement'
            )
            logger.info("🧠 Отправка изображений в нейросеть...")
            nn_response = await self.neural_client.analyze_and_process_image(nn_request)

            logger.info("💾 Сохранение обработанных изображений...")
            processed_images_info = []
            for processed_image in nn_response.processed_images:
                image_info = await self._save_processed_image(cat_id, processed_image)
                processed_images_info.append(image_info)

            logger.info("📊 Сохранение характеристик кота в БД...")
            characteristic = await self.characteristics_repo.create(
                cat_id=cat_id,
                color=nn_response.analysis_result.color,
                hair_length=nn_response.analysis_result.hair_length,
                confidence_level=nn_response.analysis_result.confidence,
                analyzed_at=nn_response.analysis_result.analysis_timestamp
            )

            logger.info("📦 Формирование ответа пользователю...")
            processed_responses = [
                ImageProcessingResponse.from_image_data(img, 'enhanced')
                for img in nn_response.processed_images
            ]

            processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            logger.info(f"✅ Обработка завершена успешно: время={processing_time_ms}ms")

            return ProcessingResult(
                session_id=session_id,
                cat_id=cat.id,
                characteristics=nn_response.analysis_result,
                processed_images=processed_responses,
                processing_time_ms=processing_time_ms,
                status='completed',
                error=None
            )
        except ProcessingException as e:
            logger.warning(f"⚠️ Обработка завершена с ошибкой (ожидаемой): {e.error.message}")
            processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return ProcessingResult(
                session_id=session_id,
                cat_id=cat_id,
                processed_images=[],
                processing_time_ms=processing_time_ms,
                status='error',
                error=e.error  # передаём только ошибку, не объект ProcessingException
            )
        except Exception as e:
            logger.exception("💥 Неожиданная ошибка при обработке изображений")
            processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)
            return ProcessingResult(
                session_id=session_id,
                cat_id=cat_id,
                processed_images=[],
                processing_time_ms=processing_time_ms,
                status='error',
                error=ProcessingError(
                    error_id="UNKNOWN_ERROR",
                    error_type="system",
                    message="Внутренняя ошибка сервера",
                    details=str(e)
                )
            )

    @staticmethod
    async def get_processing_result(self, cat_id: int) -> Optional[ProcessingResult] | None:
        logger.debug(f"🔍 Запрос результата обработки для cat_id={cat_id}")
        return None

    async def _save_original_image(self, cat_id: int, image_data: ImageData) -> dict:
        cat_dir = os.path.join(self.upload_dir, str(cat_id), "original")
        os.makedirs(cat_dir, exist_ok=True)

        file_path = os.path.join(cat_dir, image_data.filename)
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(image_data.data)

        image_record = await self.images_repo.create(
            cat_id=cat_id,
            file_name=image_data.filename,
            file_path=file_path,
            file_size=image_data.size,
            resolution=image_data.resolution,
            format=image_data.format,
            uploaded_at=datetime.now()
        )

        logger.debug(f"💾 Оригинальное изображение сохранено: {file_path}")
        return {"id": image_record.id, "path": file_path}

    async def _save_processed_image(self, cat_id: int, image_data: ImageData) -> dict:
        cat_dir = os.path.join(self.upload_dir, str(cat_id), "processed")
        os.makedirs(cat_dir, exist_ok=True)

        file_path = os.path.join(cat_dir, image_data.filename)
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(image_data.data)

        image_record = await self.images_repo.create(
            cat_id=cat_id,
            file_name=image_data.filename,
            file_path=file_path,
            file_size=image_data.size,
            resolution=image_data.resolution,
            format=image_data.format,
            uploaded_at=datetime.now()
        )
        logger.debug(f"💾 Обработанное изображение сохранено: {file_path}")
        return {"id": image_record.id, "path": file_path}

    @staticmethod
    async def validate_images(images_data: List[ImageData]) -> ValidationResult:
        logger.debug("🔍 Начало валидации изображений...")
        errors = []

        for image in images_data:
            if image.size > 10 * 1024 * 1024:  # 10MB
                errors.append(ProcessingError(
                    error_id="VALIDATION_SIZE",
                    error_type="validation",
                    message=f"Изображение {image.filename} превышает 10MB",
                    suggestions=["Используйте изображение размером до 10MB"]
                ))
                continue

            try:
                with PILImage.open(io.BytesIO(image.data)) as img:
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

        logger.debug(f"🔍 Валидация завершена: ошибок={len(errors)}")
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )