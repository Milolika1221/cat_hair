from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime

@dataclass
class ImageData:
    filename: str
    data: bytes
    size: int
    format: str
    resolution: Optional[str] = None  # "1920x1080"
    uploaded_at: Optional[datetime] = None

@dataclass
class SessionData:
    session_id: str
    created_at: datetime
    images: List[ImageData]
    status: str  # 'active', 'processing', 'completed', 'error'

@dataclass
class AnalysisResult:
    color: str
    body_type: str  
    hair_length: str
    confidence: float  # 0.0-1.0
    analysis_timestamp: datetime

@dataclass
class ProcessingResult:
    session_id: str
    cat_id: int
    characteristics: AnalysisResult
    processing_time_ms: int
    status: str

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
    total_processing_time_ms: int

@dataclass
class ProcessingError:
    error_id: str
    error_type: str  # 'validation', 'neural_api', 'database'
    message: str
    details: Optional[str] = None
    suggestions: List[str] = None

