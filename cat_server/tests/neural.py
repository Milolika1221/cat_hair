import base64
import json
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Form

app = FastAPI(title="Neural Network Stub API", version="1.0.0")

@app.post("/", summary="Обработка изображений (заглушка)")
async def process_images(
    image: UploadFile = File(..., description="Изображение кота"),
    metadata: str = Form(..., description="Метаданные в формате JSON")
):
    """
    Эмулирует обработку изображений нейросетью.

    Возвращает фиктивный результат анализа.
    """
    # Парсим метаданные
    try:
        meta = json.loads(metadata)
    except json.JSONDecodeError:
        meta = {}

    # Эмулируем "обработку"
    fake_analysis_result = {
        "color": "черный",
        "hair_length": "длинная",
        "confidence": 0.95,
        "analysis_timestamp": datetime.now().isoformat()
    }

    # Создаем фиктивное обработанное изображение (в виде base64)
    fake_image_data = b"fake_processed_image_data_placeholder"
    encoded_image = base64.b64encode(fake_image_data).decode('utf-8')

    fake_processed_images = [
        {
            "filename": image.filename,
            "data": encoded_image,
            "format": "JPEG",
            "resolution": "1920x1080"
        }
    ]

    response_data = {
        "analysis_result": fake_analysis_result,
        "processed_images": fake_processed_images,
        "processing_time_ms": 1234,
        "processing_metadata": {"stub": True, "source": "neural_stub_server"}
    }

    return response_data

if __name__ == "__main__":
    import uvicorn
    print("🚀 Запуск нейросервера-заглушки на http://localhost:8050")
    uvicorn.run(app, host="0.0.0.0", port=8050, log_level="info")