import base64
from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel

from cat_server.domain import Haircuts


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
    hair_length: str
    confidence: float  # 0.0-1.0
    analysis_timestamp: datetime

class ProcessingError(BaseModel):
    error_id: str
    error_type: str  # 'validation', 'neural_api', 'database'
    message: str
    details: Optional[str] = None
    suggestions: Optional[List[str]] = []

class ProcessingException(Exception):
    def __init__(self, error : ProcessingError):
        super().__init__(error.message)



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
    characteristics: 'AnalysisResult' = None
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
    processed_images: List['ImageData']
    processing_time_ms: int
    processing_metadata: Dict[str, Any]

class HaircutRecommendation(BaseModel):
    haircut_name: str
    haircut_description: str
    suitability_reason: str
    is_no_haircut_required: bool

class ScoredHaircut(BaseModel):
    haircut_id: int
    haircut_name: str  # или как у тебя называется модель стрижки
    score: float
    match_reasons: List[str]
    # confidence_boost: float  # например, от 0.0 до 1.0
    confidence: bool  # или убери, если не используется

class RecommendationResult(BaseModel):
    cat_id: int
    recommendations: List['HaircutRecommendation']
    processing_steps: List[str]
    total_processing_time: int
