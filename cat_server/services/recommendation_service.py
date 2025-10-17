from datetime import datetime
from typing import List

from cat_server.api.schemas import (
    AnalysisResult,
    HaircutRecommendation,
    ProcessingError,
    RecommendationResult,
    ScoredHaircut,
    AnalysisWithRecommendations  # ✅ Импортируем
)
from cat_server.domain import ProcessingException
from cat_server.domain.interfaces import IRecommendationService
from cat_server.infrastructure.repositories import (
    ICatCharacteristicsRepository,
    IHaircutsRepository,
    IRecommendationRepository
)


class RecommendationService(IRecommendationService):
    def __init__(
            self,
            characteristics_repository: ICatCharacteristicsRepository,
            haircuts_repository: IHaircutsRepository,
            recommendations_repository: IRecommendationRepository
    ):
        self.characteristics_repo = characteristics_repository
        self.haircuts_repo = haircuts_repository
        self.recommendations_repo = recommendations_repository

    async def get_recommendations(self, cat_id: int) -> RecommendationResult:
        start_time = datetime.now()
        processing_steps = []
        try:
            processing_steps.append("Получение характеристик кота")
            characteristics = await self.characteristics_repo.get_by_cat_id(cat_id)
            if not characteristics:
                raise ProcessingException(ProcessingError(
                    error_id="CHARACTERISTICS_EXCEPTION",
                    error_type="Server Error",
                    message="Характеристики не найдены")
                )

            processing_steps.append("Загрузка каталога стрижек")
            all_haircuts = await self.haircuts_repo.get_all()

            processing_steps.append("Применение правил подбора")

            characteristics_dto_list = [
                AnalysisResult(
                    color=characteristic.color,
                    hair_length=characteristic.hair_length,
                    confidence=characteristic.confidence_level,
                    analyzed_at=characteristic.analyzed_at,
                ) for characteristic in characteristics
            ]

            analyzed_haircuts = await self._apply_rules(characteristics_dto_list, all_haircuts)

            processing_steps.append("Ранжирование результатов")
            top_recommendations = await self._rank_recommendations(analyzed_haircuts)

            processing_steps.append("Сохранение рекомендаций")
            for analysis_with_rec in analyzed_haircuts:
                for recommendation in analysis_with_rec.recommendations:
                    haircut_id = None
                    if not recommendation.is_no_haircut_required:
                        haircut = next((h for h in all_haircuts if h.name == recommendation.haircut_name), None)
                        haircut_id = haircut.id if haircut else None

                    await self.recommendations_repo.create(
                        cat_id=cat_id,
                        haircut_id=haircut_id,
                        is_no_haircut_required=recommendation.is_no_haircut_required,
                        reason=recommendation.suitability_reason,
                        created_at=datetime.now(),
                    )

            processing_time = (datetime.now() - start_time).total_seconds() * 1000

            return RecommendationResult(
                cat_id=cat_id,
                recommendations=top_recommendations,
                processing_steps=processing_steps,
                total_processing_time=int(processing_time)
            )

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            return RecommendationResult(
                cat_id=cat_id,
                recommendations=[],
                processing_steps=processing_steps + [f"Ошибка: {str(e)}"],
                total_processing_time=int(processing_time)
            )

    @staticmethod
    async def _apply_rules(
            characteristics: List[AnalysisResult],
            haircuts: List  # Предполагаем, что это ORM модели
    ) -> List[AnalysisWithRecommendations]:
        """
        Применяет правила подбора для каждой AnalysisResult.
        Возвращает список AnalysisWithRecommendations, где каждая запись
        содержит AnalysisResult и список подходящих ScoredHaircut.
        """
        results = []
        for analysis_res in characteristics:
            recommendations = []
            for haircut in haircuts:
                score = 0
                reasons = []

                # Проверяем, подходит ли стрижка для данной AnalysisResult
                if analysis_res.hair_length in (getattr(haircut, 'suitable_hair_lengths', []) or []):
                    score += 1
                    reasons.append(f"Подходит для \"{analysis_res.hair_length}\" шерсти")

                if analysis_res.color in (getattr(haircut, 'suitable_colors', []) or []):
                    score += 1
                    reasons.append(f"Подходит для окраса \"{analysis_res.color}\"")

                if score >= 1:
                    recommendations.append(ScoredHaircut(
                        haircut_id=haircut.id,
                        haircut_name=haircut.name,
                        score=score,
                        match_reasons=reasons,
                        confidence=False  # Уточни, откуда брать confidence
                    ))

            # Добавляем пару AnalysisResult + её рекомендации в общий список
            results.append(AnalysisWithRecommendations(
                analysis_result=analysis_res,
                recommendations=recommendations
            ))

        return results

    @staticmethod
    async def _rank_recommendations(analyzed_haircuts: List[AnalysisWithRecommendations]) -> List[
        HaircutRecommendation]:
        """
        Ранжирует рекомендации из всех AnalysisWithRecommendations.
        """
        # Собираем все рекомендации в один список
        all_recommendations: List[ScoredHaircut] = []
        for analysis_with_rec in analyzed_haircuts:
            all_recommendations.extend(analysis_with_rec.recommendations)

        if not all_recommendations:
            return [HaircutRecommendation(
                haircut_name="Не стричь",
                haircut_description="Рекомендуется оставить шерсть без изменений",
                suitability_reason="Не найдено подходящих стрижек по текущим характеристикам",
                is_no_haircut_required=True,
            )]

        sorted_recommendations = sorted(all_recommendations, key=lambda x: x.score, reverse=True)

        top_3 = sorted_recommendations[:3]

        recommendations = []
        for scored_haircut in top_3:
            reasons_text = ". ".join(scored_haircut.match_reasons)
            confidence_text = "Высокая уверенность" if scored_haircut.confidence else "Средняя/Низкая уверенность"
            suitability_reason = f"{reasons_text}. {confidence_text} в рекомендации (оценка: {scored_haircut.score})."

            haircut_description = f"Описание для {scored_haircut.haircut_name}"

            recommendations.append(HaircutRecommendation(
                haircut_name=scored_haircut.haircut_name,
                haircut_description=haircut_description,
                suitability_reason=suitability_reason,
                is_no_haircut_required=False,
            ))

        return recommendations

    @staticmethod
    def _format_reason(match_reasons: List[str], score: float, confidence: float) -> str:
        reasons_text = ". ".join(match_reasons)

        confidence_text = "Высокая уверенность" if confidence > 0.8 else \
            "Средняя уверенность" if confidence > 0.5 else \
                "Низкая уверенность"

        return f"{reasons_text}. {confidence_text} в рекомендации (оценка: {score:.1%})."