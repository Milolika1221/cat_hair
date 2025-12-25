from typing import Annotated

import redis.asyncio as aioredis
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from cat_server.core.config import settings
from cat_server.core.database import AsyncSessionLocal
from cat_server.services.user_session_service import UserSessionService


async def get_redis() -> aioredis.Redis:
    redis = await aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis


RedisDep = Annotated[aioredis.Redis, Depends(get_redis)]


async def get_db_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def get_user_session_service(
    redis: RedisDep,
) -> UserSessionService:
    return UserSessionService(redis=redis, session_ttl=3600)


def get_image_processing_service(
    user_session: UserSessionService = Depends(get_user_session_service),
    db_session: AsyncSession = Depends(get_db_session),
):
    from cat_server.infrastructure.repositories import (
        CatsRepository,
        HaircutsRepository,
        RecommendationsRepository,
    )
    from cat_server.services.image_processing_service import (
        ImageProcessingService,
        NeuralNetworkClient,
    )

    cats_repo = CatsRepository(db_session)
    haircuts_repo = HaircutsRepository(db_session)
    recommendations_repo = RecommendationsRepository(db_session)

    neural_client = NeuralNetworkClient(
        base_url=settings.NEURAL_API_URL, timeout=settings.NEURAL_API_TIMEOUT
    )

    return ImageProcessingService(
        cats_repo=cats_repo,
        haircut_repo=haircuts_repo,
        recommendations_repo=recommendations_repo,
        user_session_service=user_session,
        neural_client=neural_client,
    )
