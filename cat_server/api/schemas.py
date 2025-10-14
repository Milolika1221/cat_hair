from dataclasses import dataclass
from pydantic import BaseModel
from typing import List

@dataclass
class SessionCreateResponse(BaseModel):
    session_id: str
    
@dataclass
class ImageUploadResponse(BaseModel):
    session_id: str
    cat_id : int
    upload_timestamp : float # секунды
    image_count : int

@dataclass
class ProcessImagesResponse(BaseModel):
    cat_id: int
    status: str

@dataclass
class RecommendationResponse(BaseModel):
    haircuts: List[str]
    reasoning: str