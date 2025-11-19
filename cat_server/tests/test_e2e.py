import io

import aiohttp
import pytest
from PIL import Image


class TestFullFlow:
    """End-to-end тесты полного потока работы"""

    @pytest.mark.asyncio
    async def test_complete_grooming_flow(self):
        """сессия → загрузка → обработка → рекомендации"""
        base_url = "http://localhost:8000/api/v1"

        async with aiohttp.ClientSession() as session:
            # 1. Создаем сессию
            async with session.post(f"{base_url}/sessions") as resp:
                assert resp.status == 200
                session_data = await resp.json()
                session_id = session_data["session_id"]
                print(f"✅ Session created: {session_id}. {resp.text()}")

            img = Image.new("RGB", (1920, 1080), color="red")
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG")
            img_bytes.seek(0)

            # 2. Загружаем тестовое изображение

            form_data = aiohttp.FormData()
            form_data.add_field(
                "files",
                value=img_bytes.getvalue(),
                filename="test.jpg",
                content_type="image/jpeg",
            )

            cat_id = 0

            async with session.post(
                f"{base_url}/{session_id}/{cat_id}/images", data=form_data
            ) as resp:
                error_detail = await resp.text()
                print(f"❌ Ошибка: {resp.status}, детали: {error_detail}")
                assert resp.status == 200
                upload_result = await resp.json()
                returned_cat_id = upload_result[0]["cat_id"]
                assert returned_cat_id != 0
                assert len(upload_result) == 1
                print("✅ Image uploaded")

            # 3. Запускаем обработку
            async with session.get(
                f"{base_url}/{session_id}/{upload_result[0]['cat_id']}/recommendations"
            ) as resp:
                assert resp.status == 200
                process_result = await resp.json()
                assert "cat_id" in process_result
                assert "characteristics" in process_result
                cat_id = process_result["cat_id"]
                print(f"✅ Processing completed, cat_id: {cat_id}")

            # 4. Получаем рекомендации
            async with session.get(f"{base_url}/cats/{cat_id}/recommendations") as resp:
                assert resp.status == 200
                recommendations = await resp.json()
                assert "recommendations" in recommendations
                print(
                    f"✅ Recommendations received: {len(recommendations['recommendations'])}"
                )
