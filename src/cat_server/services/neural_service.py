import logging
from pathlib import Path
from typing import Any, Dict

from cat_server.infrastructure.ai_model.dual_model_loader import DualModelLoader

logger = logging.getLogger(__name__)

base_dir = Path(__file__).resolve().parent.parent


class NeuralService:
    def __init__(self):
        self.model_loader = None
        self.is_loaded = False

    async def initialize(self) -> bool:
        try:
            main_model_path = str(base_dir / "infrastructure" / "models" / "main_model")
            cat_filter_path = str(base_dir / "infrastructure" / "models" / "cat_filter")

            self.model_loader = DualModelLoader(
                main_model_dir=main_model_path, cat_filter_model_dir=cat_filter_path
            )
            self.is_loaded = self.model_loader.load_models()

            if self.is_loaded:
                logger.info("✅ Двойная нейросеть успешно инициализирована")
            else:
                logger.error("❌ Не удалось загрузить нейросети")

            return self.is_loaded

        except Exception as e:
            logger.error(f"❌ Ошибка инициализации нейросети: {e}")
            return False

    async def process_image(
        self, image_data: bytes, check_cat: bool = True
    ) -> Dict[str, Any]:
        if not self.is_loaded or self.model_loader is None:
            success = await self.initialize()
            if not success:
                return {"success": False, "error": "Нейросеть не загружена"}

        return self.model_loader.predict(image_data, require_cat=check_cat)  # pyright: ignore[reportOptionalMemberAccess]
