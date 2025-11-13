"""
Database models for the transcription service.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Transcription(Base):
    """
    SQLAlchemy model for storing transcription data.
    """
    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    audio_path = Column(String(500), nullable=False)
    text = Column(Text, nullable=False)
    language = Column(String(50), nullable=True)
    duration = Column(Float, nullable=True)
    status = Column(String(50), nullable=False, default="completed")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Transcription(id={self.id}, audio_path='{self.audio_path}', status='{self.status}')>"
