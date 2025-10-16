import pytest
import asyncio
from PIL import Image
from fastapi.testclient import TestClient
from cat_server.main import app

client = TestClient(app)

class TestSessionAPI:
    def test_create_session(self):
        """Тест создания сессии через API"""
        response = client.post("/api/v1/sessions")
        
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["status"] == "created"
    
    def test_upload_images_no_session(self):
        """Тест загрузки изображений в несуществующую сессию"""
        image = Image.new("RGB", (100, 100))
        response = client.post(
            "/api/v1/invalid_session/0/images",
            files=[("files", ("test.jpg", b"fake_data", "image/jpeg"))]
        )
        
        assert response.status_code == 404
    
    def test_health_check(self):
        """Тест health check эндпоинта"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

class TestProcessingAPI:
    def test_process_images_invalid_session(self):
        """Тест обработки несуществующей сессии"""
        response = client.post("/api/v1/sessions/invalid_session/process")
        
        assert response.status_code == 404



