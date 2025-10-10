from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime, time

@dataclass
class UserSession:
    id : int
    user_id : int
    created_at : datetime
    images : List[str] # полагаю в сессии может быть несколько запросов, потому листик


"""
Ниже просто классы сущностей из БД 
"""
@dataclass
class Haircut:
    haircut_id : int
    name : str
    description : str
    suitable_body_types : str
    suitable_colors : str
    suitable_hair_lengths : str

@dataclass
class Cat:
    cat_id : int
    created_at : datetime

@dataclass 
class CatImage:
    image_id : int
    cat_id : int
    file_path : str
    resolution : str
    format : str
    uploadedAt : datetime
    
@dataclass
class CatCharacteristics:
    characteristics_id : int
    cat_id : int
    color : str
    body_type : str 
    hair_length : str
    confidence_level : float
    analyzedAt : datetime

@dataclass
class Recommendation:
    recommendation_id : int
    cat_id : int
    haircut_id : int
    is_no_haircut_required : bool
    reason : str
    createdAt : datetime

@dataclass
class ProcessingLogs:
    log_id : int
    cat_id : int
    processing_time : time
    status : str
    error_message : str
    processed_at : datetime