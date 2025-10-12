from pydantic_settings import BaseSettings

class Settings(BaseSettings): # класс настроек будет меняться 
    DATABASE_URL: str =\
    "postgresql+psycopg2://postgres:123456789@localhost:5432/cat_haircut" # 
    NEUTRAL_API_URL: str = "http://localhost:5050"
    UPLOAD_DIR: str = "uploads"

settings = Settings()
