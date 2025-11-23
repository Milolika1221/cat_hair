import asyncio
import io
from pathlib import Path

from PIL import Image

from cat_server.core.database import AsyncSessionLocal
from cat_server.infrastructure import HaircutsRepository, IHaircutsRepository


async def add_haircut_in_db(
    haircut_repo: IHaircutsRepository,
    name: str,
    description: str,
    image_bytes: bytes,
) -> None:
    await haircut_repo.create(
        name=name,
        description=description,
        image_bytes=image_bytes,
    )


haircuts_dir = Path(__file__).parent / "haircut_images"
haircuts_dict = {}

for p in haircuts_dir.iterdir():
    if p.is_file():
        with Image.open(p) as img:
            buf = io.BytesIO()
            img.save(buf, format=img.format or "PNG")
            haircuts_dict[p.stem] = buf.getvalue()


async def main():
    async with AsyncSessionLocal() as session:
        repo = HaircutsRepository(session)
        await asyncio.gather(
            *(
                add_haircut_in_db(repo, name, f"Описание {name}", img_bytes)
                for name, img_bytes in haircuts_dict.items()
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
