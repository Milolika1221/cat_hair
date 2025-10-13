from datetime import datetime
from sqlalchemy import String, Integer, ARRAY, DateTime, Boolean, Column, JSON, Float, ForeignKey
from sqlalchemy.orm import relationship
from core.database import Base

class Cats(Base):
    __tablename__ = "Cats"

    id = Column('CatID', Integer, primary_key=True, autoincrement=True)
    created_at = Column('CreatedAt', DateTime, default=datetime.now)

    processing_logs = relationship('ProcessingLogs', back_populates='cats')
    cat_images = relationship('CatImages', back_populates='cats')
    cat_characteristics = relationship('CatCharacteristics', back_populates='cats')
    recommendations = relationship('Recommendations', back_populates='cats')

class CatImages(Base):
    __tablename__ = 'CatImages'

    id = Column('CatImageID', Integer, primary_key=True, autoincrement=True)
    cat_id = Column('CatID', Integer, ForeignKey('Cats.CatID'), nullable=False)
    file_name = Column("FileName", String)
    file_path = Column('FilePath', String, nullable=False)
    file_size = Column('FileSize', Integer) # Размер в байтах
    resolution = Column('Resolution', String) # Разрешение фото
    format = Column('Format', String) # "JPEG", "PNG"
    uploaded_at = Column('UploadedAt', DateTime, default=datetime.now)

    cats = relationship('Cats', back_populates='cat_images')

class CatCharacteristics(Base):
    __tablename__ = 'CatCharacteristics'

    id = Column('CharacteristicID', Integer, primary_key=True, autoincrement=True)
    cat_id = Column('CatID', Integer, ForeignKey('Cats.CatID'), nullable=False)
    color = Column('Color', String)
    body_type = Column('BodyType', String)
    hair_length = Column("HairLength", String)
    confidence_level = Column("ConfidenceLevel", Float)

    cats = relationship('Cats', back_populates='cat_characteristics')

class Recommendations(Base):
    __tablename__ = 'Recommendations'
    
    id = Column('RecommendationID', Integer, primary_key=True, autoincrement=True)
    cat_id = Column('CatID', Integer, ForeignKey('Cats.CatID'), nullable=False)
    haircut_id = Column('HaircutID', Integer, ForeignKey('Haircuts.HaircutID'), nullable=False)
    is_no_haircut_required = Column('IsNoHaircutRequired', Boolean)
    reason = Column('Reason', String)
    created_at = Column('CreatedAt', DateTime)

    cats = relationship('Cats', back_populates='recommendations')
    haircuts = relationship('Haircuts', back_populates='recommendations')
class Haircuts(Base):
    __tablename__ = 'Haircuts'

    id = Column('HaircutID', Integer, primary_key=True)
    name = Column('Name', String)
    description = Column('Description', String)
    # suitable_body_types = Column('SuitableBodyTypes', String)
    suitable_colors = Column('SuitableColors', String)
    suitable_hair_lengths = Column('SuitableHairLengths', String)

    recommendations = relationship('Recommendations', back_populates='haircuts')

class ProcessingLogs(Base):
    __tablename__ = "ProcessingLogs"

    id = Column('LogID', Integer, primary_key=True, autoincrement=True)
    cat_id = Column('CatID', Integer, ForeignKey('Cats.CatID'), nullable=False)
    processing_time = Column('ProcessingTime', Float) # Float - секунды, в бд нет правильной реализации таймеров
    status = Column('Status', String) # "success", "error", "processing"
    error_message = Column('ErrorMessage', String)
    processed_at = Column('ProcessedAt', DateTime)

    cats = relationship('Cats', back_populates='processing_logs')
