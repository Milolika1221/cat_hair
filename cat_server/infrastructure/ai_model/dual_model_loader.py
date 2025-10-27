import tensorflow as tf
import numpy as np
import json
import os
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

class DualModelLoader:
    # Загрузчик двух моделей: фильтр кота и основная модель стрижек
    
    def __init__(self, 
                main_model_dir: str = "cat_server\infrastructure\models\main_model", 
                 cat_filter_model_dir: str = "cat_server\infrastructure\models\cat_filter"):  
        self.main_model_dir = main_model_dir
        self.cat_filter_model_dir = cat_filter_model_dir
        self.main_model = None
        self.cat_filter_model = None
        self.main_metadata = None
        self.cat_filter_metadata = None
        
    def load_models(self) -> bool:
        try:
            logger.info("Загрузка моделей...")
            
            # Загружаем модель-фильтр кота
            if not os.path.exists(os.path.join(self.cat_filter_model_dir, "saved_model.pb")):
                logger.error("❌ Модель-фильтр кота не найдена")
                return False
            
            self.cat_filter_model = tf.saved_model.load(self.cat_filter_model_dir)
            logger.info("✅ Модель-фильтр кота загружена")
            
            # Загружаем основную модель стрижек
            if not os.path.exists(os.path.join(self.main_model_dir, "saved_model.pb")):
                logger.error("❌ Основная модель стрижек не найдена")
                return False
            
            self.main_model = tf.saved_model.load(self.main_model_dir)
            logger.info("✅ Основная модель стрижек загружена")
            
            # Загружаем метаданные
            self._load_metadata()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка загрузки моделей: {e}")
            return False
    
    def _load_metadata(self):
        # Метаданные модели-фильтра
        cat_metadata_path = os.path.join(self.cat_filter_model_dir, "metadata.json")
        if os.path.exists(cat_metadata_path):
            with open(cat_metadata_path, 'r', encoding='utf-8') as f:
                self.cat_filter_metadata = json.load(f)
            logger.info(f"📊 Классы фильтра: {self.cat_filter_metadata.get('labels', [])}")
        
        # Метаданные основной модели
        main_metadata_path = os.path.join(self.main_model_dir, "metadata.json")
        if os.path.exists(main_metadata_path):
            with open(main_metadata_path, 'r', encoding='utf-8') as f:
                self.main_metadata = json.load(f)
            logger.info(f"📊 Классы основной модели: {self.main_metadata.get('labels', [])}")
    
    def preprocess_image(self, image_data: bytes) -> np.ndarray:
        # Предобработка изображения
        try:
            image = tf.image.decode_image(image_data, channels=3)
            image = tf.image.resize(image, [224, 224])
            image = tf.cast(image, tf.float32) / 255.0
            image = tf.expand_dims(image, axis=0)
            return image.numpy()
        except Exception as e:
            logger.error(f"❌ Ошибка предобработки изображения: {e}")
            raise
    
    def is_cat_image(self, image_data: bytes, confidence_threshold: float = 0.8) -> Tuple[bool, float]:
        # Определяет, является ли изображение котом с помощью модели-фильтра
        try:
            processed_image = self.preprocess_image(image_data)
            input_tensor = tf.constant(processed_image)

            predictions = self.cat_filter_model.signatures["serving_default"](input_tensor)
            output_key = list(predictions.keys())[0]
            scores = predictions[output_key].numpy()[0]
            
            filter_labels = self.cat_filter_metadata.get('labels', ['cat', 'not_cat'])
            
            cat_confidence = 0.0
            for i, label in enumerate(filter_labels):
                if i < len(scores):
                    if label.lower() == 'cat':
                        cat_confidence = float(scores[i])
                        break
            else:
                cat_confidence = float(scores[0])
            
            is_cat = cat_confidence >= confidence_threshold
            logger.info(f"Определение кота: {is_cat} (уверенность: {cat_confidence:.2f}, порог: {confidence_threshold})")
            
            return is_cat, cat_confidence
            
        except Exception as e:
            logger.error(f"❌ Ошибка определения кота: {e}")
            return False, 0.0
    
    def predict_hairstyle(self, image_data: bytes) -> Dict[str, Any]:
        # Предсказание стрижки
        if self.main_model is None:
            if not self.load_models():
                raise Exception("Модели не загружены")
        
        try:
            processed_image = self.preprocess_image(image_data)
            input_tensor = tf.constant(processed_image)
            
            predictions = self.main_model.signatures["serving_default"](input_tensor)
            output_key = list(predictions.keys())[0]
            scores = predictions[output_key].numpy()[0]
            
            labels = self.main_metadata.get('labels', [f'Class_{i}' for i in range(len(scores))])
            
            results = []
            for i, score in enumerate(scores):
                results.append({
                    "class_name": labels[i] if i < len(labels) else f"Class_{i}",
                    "confidence": float(score),
                    "percentage": f"{float(score) * 100:.2f}%"
                })
            
            results.sort(key=lambda x: x["confidence"], reverse=True)
            
            return {
                "success": True,
                "predictions": results,
                "top_prediction": results[0] if results else None
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка предсказания стрижки: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def predict(self, image_data: bytes, require_cat: bool = True) -> Dict[str, Any]:
        # Комбинированное предсказание с проверкой кота
        if self.main_model is None or self.cat_filter_model is None:
            if not self.load_models():
                raise Exception("Модели не загружены")
        
        try:
            # Проверяем, является ли изображение котом
            if require_cat:
                is_cat, cat_confidence = self.is_cat_image(image_data)
                if not is_cat:
                    return {
                        "success": False,
                        "error": "not_a_cat",
                        "message": "На изображении не обнаружен кот. Пожалуйста, загрузите фото кота.",
                        "cat_confidence": cat_confidence,
                        "required_confidence": 0.8
                    }
            
            # Если это кот или проверка отключена - делаем предсказание стрижки
            hairstyle_result = self.predict_hairstyle(image_data)
            
            if hairstyle_result["success"]:
                hairstyle_result["is_cat"] = True if require_cat else None
                if require_cat:
                    hairstyle_result["cat_confidence"] = cat_confidence
            
            return hairstyle_result
            
        except Exception as e:
            logger.error(f"❌ Ошибка комбинированного предсказания: {e}")
            return {
                "success": False,
                "error": str(e)
            }