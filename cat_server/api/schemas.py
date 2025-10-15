# cat_server/api/schemas.py

from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import base64

#  API Request Schemas
class ImageUploadRequest(BaseModel):
    cat_id: Optional[int] = Field(None, description="ID кота. Если 0 или None — создать нового.")

class ProcessCatRequest(BaseModel):
    processing_type: str = Field("analysis", description="Тип обработки: analysis, enhancement, segmentation")

# API Response Schema
class ImageUploadResponse(BaseModel):
    cat_id: int
    session_id: str
    image_count: int
    upload_timestamp: float  # секунды

class ProcessCatResponse(BaseModel):
    cat_id: int
    status: str  # "processing", "completed", "error"

class CatProcessingStatusResponse(BaseModel):
    cat_id: int
    status: str  # "pending", "processing", "completed", "error"
    error_message: Optional[str] = None
    updated_at: datetime

class CatRecommendationsResponse(BaseModel):
    cat_id: int
    recommendations: List['HaircutRecommendation']
    characteristics: Optional['AnalysisResult'] = None
    processed_images: Optional[List['ImageProcessingResponse']] = None

class SessionCreateResponse(BaseModel):
    session_id: str
    status: str = "created"

#  Внутренние DTO (теперь тоже BaseModel)
class ImageData(BaseModel):
    filename: str
    data: bytes
    size: int
    format: str
    resolution: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    is_processed: bool = False  # False - исходное, True - обработанное

class SessionData(BaseModel):
    session_id: str
    created_at: datetime
    images: List['ImageData']
    status: str  # 'active', 'processing', 'completed', 'error'

class AnalysisResult(BaseModel):
    color: str
    body_type: str
    hair_length: str
    confidence: float  # 0.0-1.0
    analysis_timestamp: datetime

class ProcessingError(BaseModel, Exception):
    error_id: str
    error_type: str  # 'validation', 'neural_api', 'database'
    message: str
    details: Optional[str] = None
    suggestions: List[str] = []

class ImageProcessingResponse(BaseModel):
    filename: str
    data: str  # base64
    format: str
    resolution: str
    processing_type: str  # "enhanced", "segmented", "annotated"

    @classmethod
    def from_image_data(cls, image_data: 'ImageData', processing_type: str):
        return cls(
            filename=image_data.filename,
            data=base64.b64encode(image_data.data).decode('utf-8'),
            format=image_data.format,
            resolution=image_data.resolution or "unknown",
            processing_type=processing_type
        )

class ProcessingResult(BaseModel):
    session_id: str
    cat_id: int
    characteristics: 'AnalysisResult'
    processed_images: List[ImageProcessingResponse]  # Для ответа пользователю
    processing_time_ms: int
    status: str
    error: Optional['ProcessingError'] = None

class ValidationResult(BaseModel):
    is_valid: bool
    errors: List['ProcessingError']

# GET/POST из веб-сервиса ИИ
class NeuralNetworkRequest(BaseModel):
    session_id: str
    cat_id: int
    images: List['ImageData']
    processing_type: str = "analysis"  # "analysis", "enhancement", "segmentation"

class NeuralNetworkResponse(BaseModel):
    analysis_result: 'AnalysisResult'
    processed_images: List['ImageData']  # изменённые изображения
    processing_time_ms: int
    processing_metadata: Dict[str, Any]  # доп. метаданные обработки

class HaircutRecommendation(BaseModel):
    haircut_name: str
    haircut_description: str
    suitability_reason: str
    is_no_haircut_required: bool

class ScoredHaircut(BaseModel):
    haircut_id: int
    score: float
    match_reasons: List[str]
    confidence: bool

class RecommendationResult(BaseModel):
    cat_id: int
    recommendations: List['HaircutRecommendation']
    processing_steps: List[str]
    total_processing_time: int
