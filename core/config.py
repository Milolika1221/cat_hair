from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "postgresql://user:pass@localhost/cat_haircut" # 
    neutral_api_url: str = "http://localhost:8001"
    upload_dir: str = "uploads"

settings = Settings()
