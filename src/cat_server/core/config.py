from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:123456789@localhost:5432/cat-haircut"
    )

    NEURAL_API_URL: str = "http://localhost:8050"
    NEURAL_API_TIMEOUT: int = 60

    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    APP_TITLE: str = "Cat AI API"
    APP_VERSION: str = "1.0.0"

    class Config:
        env_file = ".venv"


settings = Settings()
