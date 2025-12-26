import base64
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, File, HTTPException, UploadFile

from cat_server.core.dependencies import get_neural_service

neural_service = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🧠 Инициализация нейросети...")
    global neural_service

    neural_service = await get_neural_service()
    success = await neural_service.initialize()
    if success:
        print("✅ Нейросеть готова к работе")
        app.state.neural_service = neural_service
    else:
        logger.error("❌ Не удалось загрузить нейросеть")

    yield

    print(" Неросеть ушла спать")


app = FastAPI(title="Real Neural Network API", version="1.0.0", lifespan=lifespan)
logger = logging.getLogger(__name__)


@app.post("/", summary="Обработка изображений нейросетью")
async def process_images(
    image: UploadFile = File(..., description="Изображение кота"),
):
    # Проверяем что нейросеть загружена
    if not neural_service.is_loaded:  # pyright: ignore[reportOptionalMemberAccess]
        raise HTTPException(status_code=500, detail="Нейросеть не загружена")

    try:
        # Читаем изображение
        image_data = await image.read()

        # Обрабатываем через нейросеть
        start_time = datetime.now()
        result = await neural_service.process_image(image_data)  # pyright: ignore[reportOptionalMemberAccess]
        processing_time_ms = int((datetime.now() - start_time).total_seconds() * 1000)

        # Если на изображении не кот - сообщаем об этом
        if not result["success"] and result.get("error") == "not_a_cat":
            return {
                "success": False,
                "message": " Это не кот! Пожалуйста, загрузите фото кота для анализа стрижки.",
                "is_cat": False,
                "cat_confidence": result.get("cat_confidence", 0),
                "processing_time_ms": processing_time_ms,
                "analysis_timestamp": datetime.now().isoformat(),
            }

        if not result["success"]:
            raise HTTPException(
                status_code=500, detail=result.get("error", "Ошибка обработки")
            )

        # Если это кот, то форматируем рекомендацию стрижки
        top_prediction = result["top_prediction"]

        # Создаем обработанное изображение (можно вернуть оригинал или обработать)
        encoded_image = base64.b64encode(image_data).decode("utf-8")

        processed_image = {
            "filename": image.filename,
            "data": encoded_image,
            "format": "JPEG",
            "resolution": "224x224",  # Размер который использует модель
        }

        response_data = {
            "success": True,
            "is_cat": True,
            "message": f"Рекомендуемая стрижка: {top_prediction['class_name']} (уверенность: {top_prediction['percentage']})",
            "analysis_result": {
                "confidence": top_prediction["confidence"],
                "analysis_timestamp": datetime.now().isoformat(),
                "predicted_class": top_prediction["class_name"],
            },
            "processed_image": processed_image,
            "processing_time_ms": processing_time_ms,
            "processing_metadata": {
                "stub": False,
                "source": "real_neural_network",
                "predictions": result["predictions"],
                "top_prediction": top_prediction,
            },
        }

        print(
            f"✅ Успешная обработка: {top_prediction['class_name']} ({top_prediction['confidence']:.2%})"
        )
        return response_data

    except Exception as e:
        logger.error(f"❌ Ошибка обработки изображения: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    # Проверка статуса нейросети
    try:
        status = {
            "status": "ready" if neural_service.is_loaded else "not_loaded",  # pyright: ignore[reportOptionalMemberAccess]
            "model_loaded": neural_service.is_loaded,  # pyright: ignore[reportOptionalMemberAccess]
            "timestamp": datetime.now().isoformat(),
        }

        # Добавляем дополнительную информацию для диагностики
        if hasattr(neural_service, "model_loader") and neural_service.model_loader:  # pyright: ignore[reportOptionalMemberAccess]
            status["main_model_loaded"] = (
                neural_service.model_loader.main_model is not None  # pyright: ignore[reportOptionalMemberAccess]
            )
            status["cat_filter_loaded"] = (
                neural_service.model_loader.cat_filter_model is not None  # pyright: ignore[reportOptionalMemberAccess]
            )

        return status

    except Exception as e:
        logger.error(f"❌ Ошибка в /health: {e}")
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
        }


@app.get("/model-info")
async def model_info():
    # Информация о загруженной модели
    try:
        if not neural_service.is_loaded:  # pyright: ignore[reportOptionalMemberAccess]
            return {"loaded": False, "error": "Нейросеть не загружена"}

        if not neural_service.model_loader:  # pyright: ignore[reportOptionalMemberAccess]
            return {"loaded": False, "error": "Загрузчик моделей не инициализирован"}

        # Проверяем наличие метаданных для обеих моделей
        main_metadata = None
        cat_filter_metadata = None

        if hasattr(neural_service.model_loader, "main_metadata"):  # pyright: ignore[reportOptionalMemberAccess]
            main_metadata = neural_service.model_loader.main_metadata  # pyright: ignore[reportOptionalMemberAccess]

        if hasattr(neural_service.model_loader, "cat_filter_metadata"):  # pyright: ignore[reportOptionalMemberAccess]
            cat_filter_metadata = neural_service.model_loader.cat_filter_metadata  # pyright: ignore[reportOptionalMemberAccess]

        response = {
            "loaded": neural_service.is_loaded,  # pyright: ignore[reportOptionalMemberAccess]
            "main_model_loaded": neural_service.model_loader.main_model is not None  # pyright: ignore[reportOptionalMemberAccess]
            if neural_service.model_loader  # pyright: ignore[reportOptionalMemberAccess]
            else False,
            "cat_filter_loaded": neural_service.model_loader.cat_filter_model  # pyright: ignore[reportOptionalMemberAccess]
            is not None
            if neural_service.model_loader  # pyright: ignore[reportOptionalMemberAccess]
            else False,
        }

        # Добавляем информацию о классах, если есть метаданные
        if main_metadata:
            response["main_model_classes"] = main_metadata.get("labels", [])
            response["main_model_image_size"] = main_metadata.get("imageSize", 224)

        if cat_filter_metadata:
            response["cat_filter_classes"] = cat_filter_metadata.get("labels", [])
            response["cat_filter_image_size"] = cat_filter_metadata.get(
                "imageSize", 224
            )

        return response

    except Exception as e:
        logger.error(f"❌ Ошибка в /model-info: {e}")
        return {
            "loaded": False,
            "error": str(e),
            "is_loaded": neural_service.is_loaded  # pyright: ignore[reportOptionalMemberAccess]
            if hasattr(neural_service, "is_loaded")
            else None,
            "has_model_loader": hasattr(neural_service, "model_loader")
            and neural_service.model_loader is not None,  # pyright: ignore[reportOptionalMemberAccess]
        }


def run_neural():
    import uvicorn

    print("🚀 Запуск реальной нейросети на http://localhost:8050/docs")
    uvicorn.run(
        "cat_server.neural:app",
        host="0.0.0.0",
        port=8050,
        # reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    run_neural()
