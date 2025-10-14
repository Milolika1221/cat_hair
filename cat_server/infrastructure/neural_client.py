import asyncio
import base64
from datetime import datetime
import aiohttp
import json
from typing import Dict, List, Optional, Any

from domain.dtos import AnalysisResult, ImageData, NeuralNetworkRequest, NeuralNetworkResponse, ProcessingError


class NeuralNetworkClient:
    def __init__(self, base_url : str, timeout : int = 60):
        self.base_url - base_url # ai_localhost
        self.timeout = timeout
    
    async def analyze_and_process_image(self, request : NeuralNetworkRequest) -> NeuralNetworkResponse : 
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
                async with session.post(
                    f'{self.base_url}',
                    data=form_data,
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as response :
                    if response.status == 200 :
                        response_data = await response.json()
                        return self._parse_success_response(response_data)
                    else:
                        await self._handle_http_error(response, request.session_id)
            except asyncio.TimeoutError:
                raise ProcessingError(
                    error_id="NEURAL_API_TIMEOUT",
                    error_type="neural_api",
                    message="Нейросеть не ответила вовремя",
                    suggestions=["Увеличьте timeout", "Попробуйте позже"]
                )
                
            except aiohttp.ClientError as e:
                raise ProcessingError(
                    error_id="NEURAL_API_CONNECTION",
                    error_type="neural_api", 
                    message="Ошибка подключения к нейросети",
                    details=str(e),
                    suggestions=["Проверьте интернет-соединение", "Проверьте URL API"]
                )

    def _parse_success_response(self, data: Dict[str, Any]) -> NeuralNetworkResponse:
        """"""
        analysis_data = data.get('analysis_result', {})
        analysis_result = AnalysisResult(
            color=analysis_data.get('color', 'не определен'),
            body_type=analysis_data.get('body_type', 'не определен'),
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
        
        return NeuralNetworkResponse(
            analysis_result=analysis_result,
            processed_images=processed_images,
            processing_time_ms=data.get('processing_time_ms', 0),
            processing_metadata=data.get('processing_metadata', {})
        )



    async def _handle_http_error(self, response: aiohttp.ClientResponse, session_id: str):
            error_text = await response.text()
            
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
            
            raise ProcessingError(
                error_id=error_id,
                error_type="neural_api",
                message=f"{default_message} (статус: {response.status})",
                details=error_text[:500],  # Ограничиваем длину для безопасности
                suggestions=self._get_error_suggestions(response.status)
            )
    def _get_error_suggestions(self, status_code: int) -> List[str]:
        """Возвращает подсказки по устранению ошибок"""
        suggestions = {
            400: ["Проверьте формат отправляемых изображений", "Убедитесь в корректности метаданных"],
            401: ["Проверьте API ключ", "Обновите токен авторизации"],
            429: ["Уменьшите частоту запросов", "Попробуйте позже"],
            500: ["Попробуйте позже", "Свяжитесь с поддержкой ИИ сервиса"],
            503: ["Сервис временно недоступен", "Попробуйте через несколько минут"]
        }
        return suggestions.get(status_code, ["Попробуйте позже", "Обратитесь в поддержку"])