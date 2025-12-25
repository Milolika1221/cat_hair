from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ImageData(BaseModel):
    file_name: str
    data: bytes
    size: int
    format: str
    resolution: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    is_processed: Optional[bool] = False


class SessionData(BaseModel):
    session_id: str
    created_at: datetime
    image: Optional["ImageData"] = None
    cat_id: Optional[int] = None
    status: str  # 'active', 'processing', 'completed', 'error'


class AnalysisResult(BaseModel):
    confidence: float  # 0.0-1.0
    analyzed_at: datetime
    predicted_class: str


class ProcessingError(BaseModel):
    error_id: str
    error_type: str  # 'validation', 'neural_api', 'database'
    message: str
    details: Optional[str] = None
    suggestions: Optional[List[str]] = []


class ProcessingException(Exception):
    def __init__(self, error: ProcessingError):
        super().__init__(error.message)
        self.error = error


class ImageProcessingResponse(BaseModel):
    file_name: str
    format: str
    resolution: str
    processing_type: str  # "enhanced", "segmented", "annotated"

    @classmethod
    def from_cat_images(cls, cat_image: "ImageData", processing_type: str):
        return cls(
            file_name=cat_image.file_name,
            format=cat_image.format,
            resolution=cat_image.resolution or "unknown",
            processing_type=processing_type,
        )


class ProcessingResult(BaseModel):
    session_id: str
    cat_id: int
    analysis_result: AnalysisResult | str = "nothing"
    processing_time_ms: int
    status: str
    error: Optional["ProcessingError"]


class ValidationResult(BaseModel):
    is_valid: bool
    errors: List["ProcessingError"]


# GET/POST из веб-сервиса ИИ
class NeuralNetworkRequest(BaseModel):
    session_id: str
    cat_id: int
    image: "ImageData"
    processing_type: str = "analysis"  # "analysis", "enhancement", "segmentation"


class NeuralNetworkResponse(BaseModel):
    analysis_result: "AnalysisResult"
    processed_image: "ImageData"
    processing_time_ms: int
    processing_metadata: Dict[str, Any]


class HaircutRecommendation(BaseModel):
    haircut_name: str
    haircut_description: str


class ScoredHaircut(BaseModel):
    haircut_id: int
    haircut_name: str
    confidence: float
    match_reasons: List[str]


class AnalysisWithRecommendations(BaseModel):
    analysis_result: AnalysisResult
    recommendations: List[ScoredHaircut]


class RecommendationResult(BaseModel):
    cat_id: int
    recommendations: List["HaircutRecommendation"]
    total_processing_time: int
