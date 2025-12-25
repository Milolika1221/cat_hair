import base64
from datetime import datetime
from typing import Annotated

import redis.asyncio as aioredis
from fastapi import APIRouter, Depends, File, HTTPException, Path, Request, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from cat_server.api.schemas import (
    CatRecommendationsResponse,
    ImageUploadResponse,
    SessionCreateResponse,
)
from cat_server.core.dependencies import (
    get_db_session,
    get_image_processing_service,
    get_redis,
    get_user_session_service,
)
from cat_server.domain.dto import ImageData, ProcessingException
from cat_server.infrastructure import HaircutsRepository
from cat_server.infrastructure.repositories import CatsRepository
from cat_server.services.image_processing_service import ImageProcessingService
from cat_server.services.user_session_service import UserSessionService

router = APIRouter()


@router.get("/session", response_model=SessionCreateResponse)
async def create_session(
    request: Request,
    user_session_service: UserSessionService = Depends(get_user_session_service),
    redis: aioredis.Redis = Depends(get_redis),
):
    client_ip = request.client.host if request.client else "unknown"

    redis_key = f"u_ip:{client_ip}"

    existing_session = await redis.get(redis_key)
    if existing_session:
        return SessionCreateResponse(session_id=existing_session)

    session_id = await user_session_service.create_session()
    await redis.setex(redis_key, 3600, session_id)
    return SessionCreateResponse(session_id=session_id)


@router.post("/{session_id}/{cat_id}/images", response_model=ImageUploadResponse)
async def upload_images(
    session_id: str,  # session_id передаётся в URL
    cat_id: Annotated[
        int, Path(..., ge=0)
    ],  # Основной тип параметра int; Path - доп метаданные (валидация), ge (greater or equal) не даст ввести неправильный id
    file: UploadFile = File(...),
    user_session_service: UserSessionService = Depends(get_user_session_service),
    image_processing_service: ImageProcessingService = Depends(
        get_image_processing_service
    ),
    db_session: AsyncSession = Depends(get_db_session),
):
    """Функция для загрузки изображений кота в сервис нейросети и получения результатов"""
    start_time = datetime.now()

    # Заполнение данных изображений
    image_bytes = await file.read()
    content_type = file.content_type or "unknown"
    format = content_type.split("/")[-1].upper() if "/" in content_type else "unknown"
    image_data = ImageData(
        file_name=file.filename or "unnamed.jpg",  # pyright: ignore[reportArgumentType]
        data=image_bytes,
        size=len(image_bytes),
        format=format,
        uploaded_at=datetime.now(),
    )
    await file.close()

    image_is_valid = await image_processing_service.validate_image(image_data)
    if not image_is_valid.is_valid:
        raise HTTPException(status_code=400, detail="Invalid image")

    # Добавляем изображения в сессию
    success = await user_session_service.add_image_to_session(
        session_id=session_id, image_data=image_data
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
        await user_session_service.link_cat_to_session(session_id, cat_id)
        haircut_repo = HaircutsRepository(db_session)
        haircut = await haircut_repo.get_by_cat_id(cat_id)
        return ImageUploadResponse(
            cat_id=cat_id,
            session_id=session_id,
            file_name=f"{haircut.name}.jpg" if haircut is not None else "unknown.jpg",  # pyright: ignore[reportAttributeAccessIssue]
            upload_timestamp=datetime.now().timestamp() - start_time.timestamp(),
        )

    await user_session_service.link_cat_to_session(session_id, cat_id)

    try:
        result = await image_processing_service.process_images(
            session_id=session_id, cat_id=cat_id, image_data=image_data
        )
        if result.status == "error":
            raise HTTPException(
                status_code=400,
                detail=result.error.message if result.error else "Processing Failed",
            )

        # Формируем ответы пользователю
        curr_time = datetime.now().timestamp() - start_time.timestamp()
        response = ImageUploadResponse(
            cat_id=cat_id,
            session_id=session_id,
            file_name=image_data.file_name,
            upload_timestamp=curr_time,
        )
        return response

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
    user_session_service: UserSessionService = Depends(get_user_session_service),
    image_processing_service: ImageProcessingService = Depends(
        get_image_processing_service
    ),
):
    try:
        session_data = await user_session_service.get_session(session_id)
    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")

    if session_data.cat_id is None:
        raise HTTPException(status_code=400, detail="No cat linked to this session")

    if session_data.cat_id != cat_id:
        raise HTTPException(status_code=403, detail="Cat ID does not match the session")

    rec_result = await image_processing_service.get_processing_result(cat_id)
    if rec_result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Recommendations for cat_id={cat_id} not found",
        )

    return CatRecommendationsResponse(
        cat_id=rec_result["cat_id"],
        image=base64.b64encode(rec_result["image"]).decode("utf-8"),
        recommendation=rec_result["recommendation"],
    )
