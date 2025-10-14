from fastapi import Depends
from infrastructure.repositories import CatsRepository, CatImagesRepository, CatCharacteristicsRepository, HaircutsRepository,RecommendationRepository
from services.user_session_service import UserSessionService
from services.image_processing_service import ImageProcessingService
from services.recommendation_service import RecommendationService
from core.database import AsyncSessionLocal
from core.config import settings


async def get_db_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            session.close

def get_user_session_service() -> UserSessionService :
    return UserSessionService()

def get_image_processing_service(
        user_session : UserSessionService = Depends(get_user_session_service),
        db_session = Depends(get_db_session)
    ) -> ImageProcessingService:
    from infrastructure.neural_client import NeuralNetworkClient
    cats_repo = CatsRepository(db_session)
    images_repo = CatImagesRepository(db_session)
    characteristic_repo = CatCharacteristicsRepository(db_session)
    
    neutral_client = NeuralNetworkClient(base_url=settings.NEUTRAL_API_URL, timeout=settings.NEURAL_API_TIMEOUT)

    return ImageProcessingService(
        user_session_service=user_session,
        cats_repository=cats_repo,
        images_repository=images_repo,
        characteristics_repository=characteristic_repo,
        neutral_client=neutral_client
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