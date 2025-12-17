from datetime import datetime
from typing import Optional

from pydantic import Field

from cat_server.domain.dto import (
    BaseModel,
    HaircutRecommendation,
)


#  API Request Schemas
class ImageUploadRequest(BaseModel):
    cat_id: Optional[int] = Field(
        None, description="ID кота. Если 0 или None — создать нового."
    )


class ProcessCatRequest(BaseModel):
    processing_type: str = Field(
        "analysis", description="Тип обработки: analysis, enhancement, segmentation"
    )


# API Response Schema
class ImageUploadResponse(BaseModel):
    session_id: str
    cat_id: int
    file_name: str
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
    image: str
    recommendation: "HaircutRecommendation"


class SessionCreateResponse(BaseModel):
    session_id: str
    status: str = "created"
