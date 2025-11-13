"""
Transcription model for storing audio transcription data
"""
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, DateTime, Enum, Index
from sqlalchemy.dialects.postgresql import UUID
import uuid
import enum

from src.database import Base


class TranscriptionStatus(enum.Enum):
    """Enum for transcription status values"""
    pending = "pending"
    completed = "completed"
    failed = "failed"


class Transcription(Base):
    """
    Transcription model for storing audio transcription data
    
    Attributes:
        id: UUID primary key
        audio_file_path: Relative path to stored audio file
        transcription_text: Transcribed content (supports Persian/multi-language Unicode)
        language_detected: ISO language code (e.g., 'en', 'fa', 'multi')
        duration: Audio duration in seconds
        status: Transcription status (pending, completed, failed)
        created_at: Record creation time
        updated_at: Last update time
    """
    __tablename__ = "transcriptions"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )
    audio_file_path = Column(String(500), nullable=False)
    transcription_text = Column(Text, nullable=True)  # Nullable until transcription completes
    language_detected = Column(String(10), nullable=True)
    duration = Column(Float, nullable=True)
    status = Column(
        Enum(TranscriptionStatus, name="transcription_status"),
        nullable=False,
        default=TranscriptionStatus.pending
    )
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow
    )
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Indexes for frequently queried columns
    __table_args__ = (
        Index('idx_transcription_status', 'status'),
        Index('idx_transcription_created_at', 'created_at'),
        Index('idx_transcription_text', 'transcription_text', postgresql_using='gin',
              postgresql_ops={'transcription_text': 'gin_trgm_ops'}),
    )
    
    def __repr__(self):
        return (
            f"<Transcription(id={self.id}, "
            f"audio_file_path='{self.audio_file_path}', "
            f"status='{self.status.value}', "
            f"language_detected='{self.language_detected}', "
            f"created_at='{self.created_at}')>"
        )
