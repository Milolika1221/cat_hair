import io

from fastapi.testclient import TestClient
from PIL import Image

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
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        image_bytes.seek(0)

        response = client.post(
            "/api/v1/invalid_session/0/images",
            files=[("files", ("test.jpg", image_bytes, "image/jpeg"))],
        )

        assert response.status_code == 404

    def test_health_check(self):
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestProcessingAPI:
    def test_process_images_invalid_session(self):
        """Тест обработки несуществующей сессии"""
        response = client.post("/api/v1/invalid_session/0/process")

        assert response.status_code == 404
