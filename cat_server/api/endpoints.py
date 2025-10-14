from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse
from typing import List

from domain.dtos import ImageData, ImageProcessingResponse
from services.user_session_service import UserSessionService
from services.image_processing_service import ImageProcessingService
from services.recommendation_service import RecommendationService
from core.dependencies import get_user_session_service, get_image_processing_service, get_recommendation_service

router = APIRouter()

@router.post("/session")
async def create_session(
        user_session_service : UserSessionService 
    ):
    try:
        session_id = await user_session_service.create_session()
        return {'session_id' : session_id, 'status' : 'created' }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/{session_id}/images")
async def upload_images(
        session_id : str,
        files : List[UploadFile] = File(...),
        user_session_service : UserSessionService = Depends(get_user_session_service)
    ):
    try:
        images_data = []
        for file in files:
            image_bytes = file.read()

            image_data = ImageData(
                filename=file.filename,
                data=image_bytes,
                size=len(image_bytes),
                format=file.content_type.split('/')[-1].upper(),
                uploaded_at=datetime.now()
            )
            images_data.append(image_data)
        
        success = await user_session_service.add_images_to_session(session_id=session_id, images_data=images_data)

        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return { "status" : "success" , "image_uploaded" : len(images_data) }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sessions/{session_id}/process")
async def image_process(
        session_id : str,
        image_processing_service : ImageProcessingService = Depends(get_image_processing_service)
    ):
    try:
        result = await image_processing_service.process_images(session_id=session_id)
        if result.status == 'error':
            raise HTTPException(
                status_code=400,
                detail=result.error.message if result.error else "Processing Failed"
                )
        
        # КАКОЙ БОЛЬШОЙ ЖИСОН ЕМАЕ, ХЗ ЧТО ЕЩЁ НАДО ОТДАТЬ
        return {
            "session_id": result.session_id,
            "cat_id": result.cat_id,
            "characteristics": {
                "color": result.characteristics.color,
                "body_type": result.characteristics.body_type,
                "hair_length": result.characteristics.hair_length,
                "confidence": result.characteristics.confidence
            },
            "processed_images": [
                {
                    "filename": img.filename,
                    "data": img.data,  # base64
                    "format": img.format,
                    "processing_type": img.processing_type
                } for img in result.processed_images
            ],
            "processing_time_ms": result.processing_time_ms,
            "status": result.status
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get('/cats/{cat_id}/recommendations')
async def get_recommendations(
        cat_id : int,
        recommendation_service : RecommendationService = Depends(get_recommendation_service)
    ):
    try:
        result = await recommendation_service.get_recommendations(cat_id=cat_id)

        return {
            'cat_id' : result.cat_id,
            'recommendations' : [
                {
                    'haircut_name' : rec.haircut_name,
                    'haircut_description' : rec.haircut_description,
                    'suitability_reason' : rec.suitability_reason,
                    'is_no_haircut_required' : rec.is_no_haircut_required
                } for rec in result.recommendations
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




