from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List
import uuid

from services.dtos import ImageData, ProcessedImageResponse
from services.user_session_service import UserSessionService
from services.image_processing_service import ImageProcessingService
from services.recommendation_service import RecommendationService
from core.dependencies import get_user_session_service, get_image_processing_service, get_recommendation_service

router = APIRouter()

# @router.post("/session")
# async def create_session(
#     user_session_service : UserSessionService 
# )

