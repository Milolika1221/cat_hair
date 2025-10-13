from pydantic_settings import BaseSettings

class Settings(BaseSettings): # класс настроек будет меняться 
    DATABASE_URL: str =\
    "postgresql+asyncpg://postgres:123456789@localhost:5432/cat_haircut" # 

    NEUTRAL_API_URL: str = "https://neutral-api.example.com"
    UPLOAD_DIR: str = "uploads"
    NEURAL_API_TIMEOUT: int = 60
    
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    APP_TITLE: str = "Cat Grooming API"
    APP_VERSION: str = "1.0.0"
    
    class Config:
        env_file = ".venv"

settings = Settings()

