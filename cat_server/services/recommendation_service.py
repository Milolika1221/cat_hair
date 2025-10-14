from datetime import datetime
from typing import List
from domain.dtos import AnalysisResult, HaircutRecommendation, ProcessingError, RecommendationResult, ScoredHaircut
from domain.interfaces import ICatCharacteristicsRepository, IHaircutsRepository, IRecommendationRepository, IRecommendationService


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
        """
        Основной метод получения рекомендаций
        """
        start_time = datetime.now()
        processing_steps = []
        
        try:
            processing_steps.append("Получение характеристик кота")
            characteristics = await self.characteristics_repo.get_by_cat_id(cat_id)
            if not characteristics:
                raise ProcessingError("Характеристики не найдены")
            
            processing_steps.append("Загрузка каталога стрижек")
            all_haircuts = await self.haircuts_repo.get_all()
            
            processing_steps.append("Применение правил подбора")
            scored_haircuts = await self._apply_rules(characteristics, all_haircuts)
            
            processing_steps.append("Ранжирование результатов")
            top_recommendations = await self._rank_recommendations(scored_haircuts)
            
            processing_steps.append("Сохранение рекомендаций")
            for recommendation in top_recommendations:
                # ID стрижки по имени (или сохраняем без ID если "Не стричь")
                haircut_id = None
                if not recommendation.is_no_haircut_required:
                    haircut = next((h for h in all_haircuts if h.name == recommendation.haircut_name), None)
                    haircut_id = haircut.id if haircut else None
                
                await self.recommendations_repo.create(
                    cat_id=cat_id,
                    haircut_id=haircut_id,
                    is_no_haircut_required=recommendation.is_no_haircut_required,
                    reason=recommendation.suitability_reason
                )
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return RecommendationResult(
                cat_id=cat_id,
                recommendations=top_recommendations,
                processing_steps=processing_steps,
                total_processing_time_ms=int(processing_time)
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            return RecommendationResult(
                cat_id=cat_id,
                recommendations=[],
                processing_steps=processing_steps + [f"Ошибка: {str(e)}"],
                total_processing_time_ms=int(processing_time)
            )
        

    async def _apply_rules(self, characteristics: AnalysisResult, haircuts: List) -> List[HaircutRecommendation]:
        recommendations = []
        
        for haircut in haircuts:
            score = 0
            reasons = []
            
            if characteristics.hair_length in haircut.suitable_hair_lengths:
                score += 1
                reasons.append(f"Подходит для \"{characteristics.hair_length}\" шерсти")
            
            if characteristics.color in haircut.suitable_colors:
                score += 1
                reasons.append(f"Подходит для окраса \"{characteristics.color}\"")
            
            if score >= 1: 
                recommendations.append(HaircutRecommendation(
                    haircut_name=haircut.name,
                    haircut_description=haircut.description,
                    suitability_reason="; ".join(reasons),
                    is_no_haircut_required=False
                ))
        
        return recommendations
    
    async def _rank_recommendations(self, scored_haircuts: List[ScoredHaircut]) -> List[HaircutRecommendation]:
        if not scored_haircuts:
            # нет подходящих стрижек - возвращаем рекомендацию не стричь
            return [HaircutRecommendation(
                haircut_name="Не стричь",
                haircut_description="Рекомендуется оставить шерсть без изменений",
                suitability_reason="Не найдено подходящих стрижек по текущим характеристикам",
                is_no_haircut_required=True
            )]
        
        sorted_haircuts = sorted(scored_haircuts, key=lambda x: x.score, reverse=True)
        
        top_haircuts = sorted_haircuts[:3]
        
        recommendations = []
        for scored in top_haircuts:
            suitability_reason = self._format_reason(
                scored.match_reasons, 
                scored.score,
                scored.confidence_boost
            )
            recommendations.append(HaircutRecommendation(
                haircut_name=scored.haircut.name,
                haircut_description=scored.haircut.description,
                suitability_reason=suitability_reason,
                is_no_haircut_required=False
            ))
        
        return recommendations
    
    def _format_reason(self, match_reasons: List[str], score: float, confidence: float) -> str:
        reasons_text = ". ".join(match_reasons)
        
        confidence_text = "Высокая уверенность" if confidence > 0.8 else \
                        "Средняя уверенность" if confidence > 0.5 else \
                        "Низкая уверенность"
        
        return f"{reasons_text}. {confidence_text} в рекомендации (оценка: {score:.1%})."