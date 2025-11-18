from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Transcription(Base):
    """
    SQLAlchemy model for transcriptions table.
    
    This model represents the database table structure for storing transcription records.
    """
    __tablename__ = "transcriptions"

    id = Column(Integer, primary_key=True, index=True)
    audio_file_path = Column(String(512), nullable=False)
    transcription_text = Column(Text, nullable=True)
    language_detected = Column(String(50), nullable=True)
    duration = Column(Float, nullable=True)
    status = Column(String(50), nullable=False, default="pending", index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<Transcription(id={self.id}, status={self.status}, audio_file_path={self.audio_file_path})>"
