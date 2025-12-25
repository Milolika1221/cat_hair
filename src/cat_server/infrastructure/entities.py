from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    LargeBinary,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cat_server.core.base import Base


class Cats(Base):
    __tablename__ = "Cats"

    id = Column("CatID", Integer, primary_key=True, autoincrement=True)
    created_at = Column("CreatedAt", DateTime, default=datetime.now)

    processing_logs = relationship("ProcessingLogs", back_populates="cats")
    recommendations = relationship("Recommendations", back_populates="cats")


class Recommendations(Base):
    __tablename__ = "Recommendations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cat_id: Mapped[int] = mapped_column(ForeignKey("Cats.CatID"))
    haircut_id: Mapped[int] = mapped_column(ForeignKey("Haircuts.HaircutID"))
    confidence: Mapped[float]

    cats = relationship("Cats", back_populates="recommendations")
    haircuts = relationship("Haircuts", back_populates="recommendations")


class Haircuts(Base):
    __tablename__ = "Haircuts"

    id = Column("HaircutID", Integer, primary_key=True, autoincrement=True)
    name = Column("Name", String, unique=True)
    description = Column("Description", String)
    image_bytes = Column("ImageBytes", LargeBinary)

    recommendations = relationship("Recommendations", back_populates="haircuts")


class ProcessingLogs(Base):
    __tablename__ = "ProcessingLogs"

    id = Column("LogID", Integer, primary_key=True, autoincrement=True)
    cat_id = Column("CatID", Integer, ForeignKey("Cats.CatID"), nullable=False)
    processing_time = Column("ProcessingTime", Float)  # Float - секунды
    status = Column("Status", String)  # "success", "error", "processing"
    error_message = Column("ErrorMessage", String)
    processed_at = Column("ProcessedAt", DateTime)

    cats = relationship("Cats", back_populates="processing_logs")
