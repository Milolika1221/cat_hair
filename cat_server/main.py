from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from datetime import datetime

from cat_server.api.endpoints import router
from cat_server.core.config import settings
from cat_server.core.database import check_database_connection
from cat_server.services.neural_service import neural_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Starting Cat AI API...")
    
    try:
        await check_database_connection()
        print("✅ Database connection OK")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        raise

    # Инициализация нейросети
    try:
        await neural_service.initialize()
        print("✅ Neural network loaded OK")
    except Exception as e:
        print(f"⚠️ Neural network loading failed: {e}")
    
    print(f"✅ API is ready at http://localhost:8000")
    print(f"📚 Documentation: http://localhost:8000/docs")
    
    yield  # Здесь приложение работает
    
    print("🛑 Shutting down Cat Grooming API...")

app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.APP_VERSION,
    description="API для подбора стрижек котов на основе анализа изображений",
    lifespan=lifespan
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
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": settings.APP_VERSION
    }

if __name__ == "__main__":
    # Запуск из корня проекта: python -m cat_server.main
    # Или через uvicorn: uvicorn cat_server.main:app --host 0.0.0.0 --port 8050 --reload
    uvicorn.run(
        "cat_server.main:app",  #
        host="0.0.0.0",  
        port=8000,
        reload=True,  
        log_level="info",

    )