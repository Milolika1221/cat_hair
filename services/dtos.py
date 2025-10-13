from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
import base64


@dataclass
class ImageData:
    filename: str
    data: bytes
    size: int
    format: str
    resolution: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    is_processed: bool = False  # False - исходное, True - обработанное

@dataclass
class ProcessedImageResponse:
    filename: str
    data: str           # base64 
    format: str
    resolution: str
    processing_type: str  # "enhanced", "segmented", "annotated"
    
    @classmethod
    def from_image_data(cls, image_data: ImageData, processing_type: str):
        return cls(
            filename=image_data.filename,
            data=base64.b64encode(image_data.data).decode('utf-8'),
            format=image_data.format,
            resolution=image_data.resolution or "unknown",
            processing_type=processing_type
        )




# Анализ изображения (RecommendationService), обращения в бд всякое сравнение
@dataclass
class AnalysisResult:
    color: str
    body_type: str  
    hair_length: str
    confidence: float  # 0.0-1.0
    analysis_timestamp: datetime
@dataclass
class HaircutRecommendation:
    haircut_name: str
    haircut_description: str
    suitability_reason: str
    is_no_haircut_required: bool
@dataclass
class RecommendationResult:
    cat_id: int
    recommendations: List[HaircutRecommendation]
    processing_steps: List[str]
    total_processing_time: int
@dataclass
class ScoredHaircut:
    haircut_id : int
    score : float
    match_reasons : List[str]
    confidence : bool



# Результат валидации изображения

@dataclass
class ProcessingError:
    error_id: str
    error_type: str  # 'validation', 'neural_api', 'database'
    message: str
    details: Optional[str] = None
    suggestions: List[str] = None


@dataclass
class ProcessingResult:
    session_id: str
    cat_id: int
    characteristics: AnalysisResult
    processed_images: List[ProcessedImageResponse]  # Для ответа пользователю
    processing_time_ms: int
    status: str
    error: Optional[ProcessingError] = None

@dataclass
class ProcessingResult:
    session_id: str
    cat_id: int
    characteristics: AnalysisResult
    processed_images : List[ProcessedImageResponse]
    processing_time: int
    status: str
    error: Optional[ProcessingError] = None

@dataclass
class SessionData:
    session_id: str
    created_at: datetime
    images: List[ImageData]
    status: str  # 'active', 'processing', 'completed', 'error'

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[ProcessingError]


# GET/POST из веб-сервиса ИИ
@dataclass
class NeutralNetworkRequest:
    session_id: str
    cat_id : int
    images: List[ImageData]
    processing_type: str = "analysis"  # "analysis", "enhancement", "segmentation"
@dataclass
class NeutralNetworkResponse:
    analysis_result: AnalysisResult
    processed_images: List[ImageData]  # изменённые изображения
    processing_time_ms: int
    processing_metadata: Dict[str, Any]  # доп. метаданные обработки
