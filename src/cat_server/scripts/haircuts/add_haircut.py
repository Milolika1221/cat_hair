import asyncio
import io
from importlib import resources
from pathlib import Path

from PIL import Image

from cat_server.core.database import AsyncSessionLocal
from cat_server.infrastructure import HaircutsRepository

# --- Описания стрижек ---
HAIRCUT_DESCRIPTIONS = {
    "Лев": "Классическая гигиеническая стрижка. Шерсть полностью сбривается на теле, оставляя «гриву» на голове и шее, пушистые «сапожки» на лапах и кисточку на хвосте. Идеально подходит для длинношерстных кошек, склонных к колтунам.",
    "Пума": "Укороченная версия «Льва». Шерсть по телу не сбривается, а коротко подстригается, что делает образ более естественным и спортивным. «Грива» и «кисточка» на хвосте выражены слабее или могут отсутствовать. Хороший компромисс между эстетикой и практичностью.",
    "Сапожки": "Практичный и щадящий вариант. Шерсть на теле укорачивается, но при этом на лапах оставляют характерные пушистые «сапожки» разной длины. Голова и хвост остаются пушистыми. Помогает справиться с колтунами, сохранив кошке более привычный вид.",
    "Дракон": "Самый креативный и экстравагантный вариант. Шерсть на теле сбривается, а вдоль спины оставляют полосу шерсти («гребень»), которая может быть ровной или с узорами. Часто дополняется рисунками (молнии, зигзаги) на боках. Это чисто декоративная стрижка для смелых владельцев.",
}


def load_haircut_data():
    """Загружает данные о стрижках из ресурсов пакета."""
    haircuts_data = []

    # Используем importlib.resources для надёжного доступа к ресурсам
    with resources.path(
        "cat_server.scripts.haircuts", "haircut_images"
    ) as haircuts_dir:
        for p in Path(haircuts_dir).iterdir():
            if p.is_file():
                name = p.stem
                description = HAIRCUT_DESCRIPTIONS.get(name)
                if description is None:
                    print(f"Нет описания для стрижки: {name}. Пропускаем.")
                    continue

                try:
                    with Image.open(p) as img:
                        buf = io.BytesIO()
                        img_format = img.format or "PNG"
                        img.save(buf, format=img_format)
                        haircuts_data.append((name, description, buf.getvalue()))
                except Exception as e:
                    print(f"Ошибка при обработке изображения {p.name}: {e}")
                    continue

    return haircuts_data


async def add_haircut_in_db(
    repo, name: str, description: str, image_bytes: bytes
) -> None:
    await repo.create(
        name=name,
        description=description,
        image_bytes=image_bytes,
    )


async def main():
    haircuts_data = load_haircut_data()
    if not haircuts_data:
        print("⚠️ Нет данных о стрижках для загрузки.")
        return

    async with AsyncSessionLocal() as session:
        repo = HaircutsRepository(session)
        for name, desc, img_bytes in haircuts_data:
            print(f"Загружаем стрижку: {name}")
            await add_haircut_in_db(repo, name, desc, img_bytes)
    print("✅ Все стрижки успешно загружены.")


def run_add_haircuts():
    """Точка входа для CLI скрипта (например, при вызове add-haircuts)."""
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
