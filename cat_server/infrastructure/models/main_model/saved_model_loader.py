import tensorflow as tf
import numpy as np
import json
import os
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SavedModelLoader:
    """Загрузчик для моделей в формате SavedModel из Teachable Machine"""
    
    def __init__(self, model_dir: str = "infrastructure/models"):
        self.model_dir = model_dir
        self.model = None
        self.metadata = None
        
    def load_model(self) -> bool:
        """Загрузка модели в формате SavedModel"""
        try:
            logger.info(f"🔄 Загрузка SavedModel из: {self.model_dir}")
            
            # Проверяем существование модели
            if not os.path.exists(os.path.join(self.model_dir, "saved_model.pb")):
                logger.error("❌ Файл saved_model.pb не найден")
                return False
            
            # Загружаем модель
            self.model = tf.saved_model.load(self.model_dir)
            logger.info("✅ SavedModel загружена успешно")
            
            # Загружаем метаданные если есть
            metadata_path = os.path.join(self.model_dir, "metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                logger.info(f"📊 Классы модели: {self.metadata.get('labels', [])}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки SavedModel: {e}")
            return False
    
    def preprocess_image(self, image_data: bytes) -> np.ndarray:
        """Предобработка изображения для модели"""
        try:
            # Декодируем изображение
            image = tf.image.decode_image(image_data, channels=3)
            
            # Изменяем размер до 224x224 (стандарт для Teachable Machine)
            image = tf.image.resize(image, [224, 224])
            
            # Нормализуем [0, 1]
            image = tf.cast(image, tf.float32) / 255.0
            
            # Добавляем batch dimension
            image = tf.expand_dims(image, axis=0)
            
            return image.numpy()
            
        except Exception as e:
            logger.error(f"❌ Ошибка предобработки изображения: {e}")
            raise
    
    def predict(self, image_data: bytes) -> Dict[str, Any]:
        """Выполнение предсказания"""
        if self.model is None:
            if not self.load_model():
                raise Exception("Модель не загружена")
        
        try:
            # Предобработка изображения
            processed_image = self.preprocess_image(image_data)
            
            # Конвертируем в тензор TensorFlow
            input_tensor = tf.constant(processed_image)
            
            # Выполняем предсказание
            # Для SavedModel используем serving_default сигнатуру
            predictions = self.model.signatures["serving_default"](input_tensor)
            
            # Извлекаем результаты (имя выходного тензора может отличаться)
            output_key = list(predictions.keys())[0]
            scores = predictions[output_key].numpy()[0]
            
            # Форматируем результаты
            labels = self.metadata.get('labels', [f'Class_{i}' for i in range(len(scores))])
            
            results = []
            for i, score in enumerate(scores):
                results.append({
                    "class_name": labels[i] if i < len(labels) else f"Class_{i}",
                    "confidence": float(score),
                    "percentage": f"{float(score) * 100:.2f}%"
                })
            
            # Сортируем по уверенности
            results.sort(key=lambda x: x["confidence"], reverse=True)
            
            return {
                "success": True,
                "predictions": results,
                "top_prediction": results[0] if results else None
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка предсказания: {e}")
            return {
                "success": False,
                "error": str(e)
            }