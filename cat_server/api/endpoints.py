from datetime import datetime
from typing import Annotated, List

from fastapi import APIRouter, Depends, File, HTTPException, Path, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from cat_server.api.schemas import (
    CatRecommendationsResponse,
    ImageUploadResponse,
    SessionCreateResponse,
)
from cat_server.core.dependencies import (
    get_db_session,
    get_image_processing_service,
    get_recommendation_service,
    get_user_session_service,
)
from cat_server.domain.dto import ImageData, ProcessingException
from cat_server.infrastructure.repositories import CatsRepository
from cat_server.services.image_processing_service import ImageProcessingService
from cat_server.services.recommendation_service import RecommendationService
from cat_server.services.user_session_service import UserSessionService

router = APIRouter()


@router.post("/sessions", response_model=SessionCreateResponse)
async def create_session(
    user_session_service: UserSessionService = Depends(get_user_session_service),
):
    session_id = await user_session_service.create_session()
    return SessionCreateResponse(session_id=session_id)


@router.post("/{session_id}/{cat_id}/images", response_model=List[ImageUploadResponse])
async def upload_images(
    session_id: str,  # session_id передаётся в URL
    cat_id: Annotated[
        int, Path(..., ge=0)
    ],  # Основной тип параметра int; Path - доп метаданные (валидация), ge (greater or equal) не даст ввести неправильный id
    files: List[UploadFile] = File(..., max_files=5),
    user_session_service: UserSessionService = Depends(get_user_session_service),
    image_processing_service: ImageProcessingService = Depends(
        get_image_processing_service
    ),
    db_session: AsyncSession = Depends(get_db_session),
):
    start_time = datetime.now()
    images_data = []
    for file in files:
        image_bytes = await file.read()

        content_type = file.content_type or "unknown"
        format = (
            content_type.split("/")[-1].upper() if "/" in content_type else "UNKNOWN"
        )

        image_data = ImageData(
            file_name=file.filename,  # pyright: ignore[reportArgumentType]
            data=image_bytes,
            size=len(image_bytes),
            format=format,
            uploaded_at=datetime.now(),
        )
        images_data.append(image_data)

    success = await user_session_service.add_images_to_session(
        session_id=session_id, images_data=images_data
    )
    if not success:
        raise HTTPException(status_code=404, detail="Failed to store images in session")

    cat_repo = CatsRepository(db_session)

    #  cat_id: новый или существующий
    if cat_id == 0:
        cat = await cat_repo.create()
        cat_id = cat.id  # pyright: ignore[reportAssignmentType]
    else:
        cat = await cat_repo.get_by_id(cat_id)
        if cat is None:
            raise HTTPException(status_code=404, detail="Cat not found")

    try:
        result = await image_processing_service.process_images(
            session_id=session_id, cat_id=cat_id, images_data=images_data
        )
        if result.status == "error":
            raise HTTPException(
                status_code=400,
                detail=result.error.message if result.error else "Processing Failed",
            )
        responses = []
        curr_time = datetime.now().timestamp() - start_time.timestamp()
        for i, img in enumerate(images_data):
            responses.append(
                ImageUploadResponse(
                    cat_id=cat_id,
                    session_id=session_id,
                    file_name=img.file_name,
                    upload_timestamp=curr_time,
                )
            )
        return responses

    except ProcessingException as e:
        raise HTTPException(
            status_code=400,
            detail=f"Processing error {400}: {e.error.message if e.error else 'Unknown processing error'}",
        )
    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")


@router.get(
    "/{session_id}/{cat_id}/recommendations", response_model=CatRecommendationsResponse
)
async def get_cat_recommendations(
    session_id: str,
    cat_id: int,
    recommendation_service: RecommendationService = Depends(get_recommendation_service),
    image_processing_service: ImageProcessingService = Depends(
        get_image_processing_service
    ),
):
    proc_result = await image_processing_service.get_processing_result(
        session_id=session_id, cat_id=cat_id
    )
    if not proc_result:
        raise HTTPException(
            status_code=404,
            detail="No processing result found for this cat. Upload images first.",
        )

    # Получаем рекомендации
    rec_result = await recommendation_service.get_recommendations(cat_id=cat_id)

    return CatRecommendationsResponse(
        cat_id=cat_id,
        recommendations=rec_result.recommendations,
        characteristics=proc_result.characteristics,
        processed_images=proc_result.processed_images,
    )
