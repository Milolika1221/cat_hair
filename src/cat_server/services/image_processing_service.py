# services/image_processing_service.py

import asyncio
import base64
import io
import json
import logging
from datetime import datetime
from typing import Any, Dict, List

import aiohttp
from PIL import Image as PILImage

from cat_server.domain.dto import (
    AnalysisResult,
    HaircutRecommendation,
    ImageData,
    NeuralNetworkRequest,
    NeuralNetworkResponse,
    ProcessingError,
    ProcessingException,
    ProcessingResult,
    ValidationResult,
)
from cat_server.infrastructure.repositories import (
    ICatsRepository,
    IHaircutsRepository,
    IRecommendationsRepository,
)
from cat_server.services.neural_service import NeuralService
from cat_server.services.user_session_service import UserSessionService

logger = logging.getLogger(__name__)


class NeuralNetworkClient:
    def __init__(self, base_url: str, timeout: int = 60):
        self.base_url = base_url
        self.timeout = timeout
        print(
            f"🔧 NeuralNetworkClient инициализирован с URL: {base_url}, timeout: {timeout}"
        )

    async def _process_with_local_neural(
        self, image_data: ImageData, neural_service: NeuralService
    ) -> NeuralNetworkResponse | None:
        """Обработка изображений локальной нейросетью"""
        print("🧠 Обработка локальной нейросетью...")

        neural_result = await neural_service.process_image(image_data.data)

        if not neural_result["success"]:
            raise ProcessingException(
                ProcessingError(
                    error_id="LOCAL_NEURAL_ERROR",
                    error_type="neural_local",
                    message=neural_result.get("error", "Local neural network error"),
                )
            )

        top_prediction = neural_result.get("top_prediction", {})

        # Создаем AnalysisResult
        analysis_result = AnalysisResult(
            confidence=top_prediction.get("confidence", 0.0),
            analyzed_at=datetime.now(),
            predicted_class=top_prediction["class_name"],
        )

        processed_image = ImageData(
            file_name=f"processed_{image_data.file_name}",
            data=image_data.data,
            size=image_data.size,
            format=image_data.format,
            resolution=image_data.resolution,
            is_processed=True,
        )

        return NeuralNetworkResponse(
            analysis_result=analysis_result,
            processed_image=processed_image,
            processing_time_ms=0,
            processing_metadata={
                "model_type": "teachable_machine",
                "predictions": neural_result.get("predictions", []),
                "top_prediction": top_prediction,
            },
        )

    async def analyze_and_process_image(
        self, request: NeuralNetworkRequest
    ) -> NeuralNetworkResponse | None:
        async with aiohttp.ClientSession() as session:
            form_data = aiohttp.FormData()
            form_data.add_field(
                name="image",
                value=request.image.data,
                filename=f"{request.image.file_name}",
                content_type=f"image/{request.image.format.lower()}",
            )

            metadata = {
                "processed_at": request.processing_type,
                "image_metadata": {
                    "filename": request.image.file_name,
                    "format": request.image.format,
                    "size": request.image.size,
                    "resolution": request.image.resolution,
                },
            }
            form_data.add_field("metadata", json.dumps(metadata))
            try:
                print(f"📡 Отправка POST-запроса на {self.base_url}")
                async with session.post(
                    f"{self.base_url}",
                    data=form_data,
                    timeout=aiohttp.ClientTimeout(total=self.timeout),
                ) as response:
                    print(f"📥 Получен ответ от нейросети: статус {response.status}")
                    if response.status == 200:
                        response_data = await response.json()
                        print(f"✅ Успешный ответ от нейросети: {response_data}")
                        return self._parse_success_response(response_data)
                    else:
                        processing_error = await self._handle_http_error(response)
                        raise ProcessingException(processing_error)

            except asyncio.TimeoutError:
                logger.error("⏰ Таймаут при запросе к нейросети")
                raise ProcessingException(
                    ProcessingError(
                        error_id="NEURAL_API_TIMEOUT",
                        error_type="neural_api",
                        message="Нейросеть не ответила вовремя",
                        suggestions=["Увеличьте timeout", "Попробуйте позже"],
                    )
                )

            except aiohttp.ClientError as e:
                logger.exception("🔌 Ошибка подключения к нейросети")
                raise ProcessingException(
                    ProcessingError(
                        error_id="NEURAL_API_CONNECTION",
                        error_type="neural_api",
                        message="Ошибка подключения к нейросети",
                        details=str(e),
                        suggestions=[
                            "Проверьте интернет-соединение",
                            "Проверьте URL API",
                        ],
                    )
                )

    @staticmethod
    def _parse_success_response(
        neural_data: Dict[str, Any],
    ) -> NeuralNetworkResponse | None:
        print("🔄 Парсинг успешного ответа от нейросети")
        analysis_data = neural_data.get("analysis_result", {})
        analysis_result = AnalysisResult(
            confidence=analysis_data.get("confidence", 0.0),
            analyzed_at=datetime.fromisoformat(
                analysis_data.get("analysis_timestamp", datetime.now().isoformat())
            ),
            predicted_class=analysis_data.get("predicted_class", ""),
        )

        image_data = (
            neural_data["processed_image"] if "processed_image" in neural_data else {}
        )

        if len(image_data) == 0:
            return None

        image_bytes = base64.b64decode(image_data["data"])
        processed_image = ImageData(
            file_name=image_data["filename"],
            data=image_bytes,
            size=len(image_bytes),
            format=image_data["format"],
            resolution=image_data["resolution"],
            is_processed=True,
        )

        result = NeuralNetworkResponse(
            analysis_result=analysis_result,
            processed_image=processed_image,
            processing_time_ms=neural_data.get("processing_time_ms", 0),
            processing_metadata=neural_data.get("processing_metadata", {}),
        )
        print("✅ Ответ от нейросети успешно распарсен")
        return result

    @staticmethod
    async def _handle_http_error(response: aiohttp.ClientResponse) -> ProcessingError:
        error_text = await response.text()
        logger.warning(
            f"⚠️ Нейросеть вернула ошибку: статус {response.status}, текст: {error_text}"
        )

        error_mapping = {
            400: ("NEURAL_API_BAD_REQUEST", "Некорректный запрос"),
            401: ("NEURAL_API_UNAUTHORIZED", "Неавторизованный доступ"),
            403: ("NEURAL_API_FORBIDDEN", "Доступ запрещен"),
            404: ("NEURAL_API_NOT_FOUND", "Ресурс не найден"),
            429: ("NEURAL_API_RATE_LIMIT", "Превышен лимит запросов"),
            500: ("NEURAL_API_SERVER_ERROR", "Внутренняя ошибка нейросети"),
            503: ("NEURAL_API_UNAVAILABLE", "Сервис недоступен"),
        }

        error_id, default_message = error_mapping.get(
            response.status, ("NEURAL_API_UNKNOWN", "Неизвестная ошибка")
        )

        return ProcessingError(
            error_id=error_id,
            error_type="neural_api",
            message=f"{default_message} (статус: {response.status})",
            details=error_text[:500],
            suggestions=NeuralNetworkClient._get_error_suggestions(response.status),
        )

    @staticmethod
    def _get_error_suggestions(status_code: int) -> List[str]:
        """Возвращает подсказки по устранению ошибок"""
        suggestions = {
            400: [
                "Проверьте формат отправляемых изображений",
                "Убедитесь в корректности метаданных",
            ],
            429: ["Уменьшите частоту запросов", "Попробуйте позже"],
            500: ["Попробуйте позже", "Свяжитесь с поддержкой ИИ сервиса"],
            503: ["Сервис временно недоступен", "Попробуйте через несколько минут"],
        }
        return suggestions.get(
            status_code, ["Попробуйте позже", "Обратитесь в поддержку"]
        )


class ImageProcessingService:
    def __init__(
        self,
        cats_repo: ICatsRepository,
        haircut_repo: IHaircutsRepository,
        recommendations_repo: IRecommendationsRepository,
        user_session_service: UserSessionService,
        neural_client: NeuralNetworkClient,
    ):
        self.cats_repo = cats_repo
        self.haircut_repo = haircut_repo
        self.recommendations_repo = recommendations_repo
        self.user_session_service = user_session_service
        self.neural_client = neural_client

    async def process_images(
        self,
        image_data: ImageData,
    ) -> ProcessingResult:
        start_time = datetime.now()
        try:
            nn_request = NeuralNetworkRequest(
                image=image_data,
                processing_type="analysis and enhancement",
            )
            print("🧠 Отправка изображений в нейросеть...")
            nn_response = await self.neural_client.analyze_and_process_image(nn_request)

            if nn_response is None:
                processing_time_ms = int(
                    (datetime.now() - start_time).total_seconds() * 1000
                )
                return ProcessingResult(
                    analysis_result="nothing",
                    processing_time_ms=processing_time_ms,
                    status="error",
                    error=ProcessingError(
                        error_id="NEURAL_NETWORK_ERROR",
                        error_type="neural_network",
                        message="Ошибка нейросети",
                        details="Кот не определён",
                    ),
                )

            cat = await self.cats_repo.create()

            recommendation = await self.recommendations_repo.create(
                cat.id,  # pyright: ignore[reportArgumentType]
                nn_response.analysis_result.predicted_class,
                nn_response.analysis_result.confidence,
            )
            del recommendation

            processing_time_ms = int(
                (datetime.now() - start_time).total_seconds() * 1000
            )
            print(f"✅ Обработка завершена успешно: время={processing_time_ms}ms")

            return ProcessingResult(
                cat_id=cat.id,  # pyright: ignore[reportArgumentType]
                analysis_result=nn_response.analysis_result,
                processing_time_ms=processing_time_ms,
                status="completed",
                error=None,
            )

        except ProcessingException as e:
            logger.warning(
                f"⚠️ Обработка завершена с ошибкой (ожидаемой): {e.error.message}"
            )
            processing_time_ms = int(
                (datetime.now() - start_time).total_seconds() * 1000
            )
            return ProcessingResult(
                processing_time_ms=processing_time_ms,
                status="error",
                error=e.error,
            )
        except Exception as e:
            logger.exception("💥 Неожиданная ошибка при обработке изображений")
            processing_time_ms = int(
                (datetime.now() - start_time).total_seconds() * 1000
            )
            return ProcessingResult(
                analysis_result="nothing",
                processing_time_ms=processing_time_ms,
                status="error",
                error=ProcessingError(
                    error_id="UNKNOWN_ERROR",
                    error_type="system",
                    message="Внутренняя ошибка сервера",
                    details=str(e),
                ),
            )

    async def validate_image(self, image_data: ImageData) -> ValidationResult:
        print("🔍 Начало валидации изображений...")
        errors = []

        if image_data.size > 10 * 1024 * 1024:  # 10MB
            errors.append(
                ProcessingError(
                    error_id="VALIDATION_SIZE",
                    error_type="validation",
                    message=f"Изображение {image_data.file_name} превышает 10MB",
                    suggestions=["Используйте изображение размером до 10MB"],
                )
            )

        try:
            with PILImage.open(io.BytesIO(image_data.data)) as img:
                width, height = img.size
                if width < 640 or height < 480:
                    errors.append(
                        ProcessingError(
                            error_id="VALIDATION_RESOLUTION",
                            error_type="validation",
                            message=f"Изображение {image_data.file_name} имеет недостаточное разрешение",
                            details=f"Текущее: {width}x{height}, минимальное: 640x480",
                            suggestions=[
                                "Используйте изображение с более высоким разрешением"
                            ],
                        )
                    )

                image_data.resolution = f"{width}x{height}"

        except Exception as e:
            errors.append(
                ProcessingError(
                    error_id="VALIDATION_FORMAT",
                    error_type="validation",
                    message=f"Неверный формат изображения {image_data.file_name}",
                    details=str(e),
                    suggestions=["Используйте формат JPEG или PNG"],
                )
            )

        print(f"🔍 Валидация завершена: ошибок={len(errors)}")
        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    async def get_processing_result(self, cat_id: int) -> Dict[str, Any] | None:
        recommendation = await self.recommendations_repo.get_by_cat_id(cat_id)
        if recommendation is None:
            return None

        haircut = await self.haircut_repo.get_by_id(recommendation.haircut_id)
        if haircut is None:
            return None

        return {
            "cat_id": cat_id,
            "image": haircut.image_bytes,
            "recommendation": HaircutRecommendation(
                haircut_name=haircut.name,  # pyright: ignore[reportArgumentType]
                haircut_description=haircut.description,  # pyright: ignore[reportArgumentType]
            ),
        }
