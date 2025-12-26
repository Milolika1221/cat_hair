from contextlib import asynccontextmanager
from datetime import datetime

import redis.asyncio as aioredis
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cat_server.api.endpoints import router
from cat_server.core.config import settings
from cat_server.core.database import check_database_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting Cat AI API...")

    # Инициализация Redis
    redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    app.state.redis = redis_client  # ← сохраняем в состоянии приложения
    try:
        await check_database_connection()
        print("✅ Database connection OK")
    except Exception as e:
        await redis_client.aclose()
        print(f"❌ Startup failed: {e}")
        raise

    print("✅ API is ready at http://localhost:8000")
    print("📚 Docs at http://localhost:8000/docs")
    yield

    # Очистка
    await app.state.redis.aclose()
    print("🛑 Shutting down Cat Grooming API...")


app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description="API для подбора стрижек котов на основе анализа изображений",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "message": "Cat AI API",
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.APP_VERSION,
    }


def run_server():
    """Запуск сервера через uvicorn (для uv run cat-hair-server)"""
    uvicorn.run(
        "cat_server.main:app",
        host="0.0.0.0",
        port=8000,
        # reload=True,
        log_level="info",
    )


if __name__ == "__main__":
    run_server()
