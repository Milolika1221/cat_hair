from sqlalchemy import create_engine
from domain.entities import Base
from core.config import settings

def create_database():
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    print("Все таблицы созданы!")

def drop_database():
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.drop_all(bind=engine)
    print("Все таблицы удалены!")