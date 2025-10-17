from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from cat_server.infrastructure.repositories import CatsRepository, CatImagesRepository, CatCharacteristicsRepository, HaircutsRepository,RecommendationRepository
from cat_server.services.image_processing_service import ImageProcessingService, NeuralNetworkClient, UserSessionService
from cat_server.services.recommendation_service import RecommendationService
from cat_server.core.database import AsyncSessionLocal
from cat_server.core.config import settings


USER_SESSION_SERVICE = UserSessionService()

async def get_db_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

def get_user_session_service() -> UserSessionService :
    return USER_SESSION_SERVICE

def get_image_processing_service(
        user_session : UserSessionService = Depends(get_user_session_service),
        db_session : AsyncSession= Depends(get_db_session)
    ) -> ImageProcessingService:
    cats_repo = CatsRepository(db_session)
    images_repo = CatImagesRepository(db_session)
    characteristic_repo = CatCharacteristicsRepository(db_session)

    neural_client = NeuralNetworkClient(base_url=settings.NEUTRAL_API_URL, timeout=settings.NEURAL_API_TIMEOUT)

    return ImageProcessingService(
        user_session_service=user_session,
        cats_repo=cats_repo,
        images_repo=images_repo,
        characteristics_repo=characteristic_repo,
        neural_client=neural_client
        )

def get_recommendation_service(
        db_session = Depends(get_db_session)
    ) -> RecommendationService:
    characteristics_repo = CatCharacteristicsRepository(db_session)
    haircuts_repo = HaircutsRepository(db_session)
    recommendations_repo = RecommendationRepository(db_session)

    return RecommendationService(
        characteristics_repository=characteristics_repo,
        haircuts_repository=haircuts_repo,
        recommendations_repository=recommendations_repo
    )