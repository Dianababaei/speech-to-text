"""
Pydantic schemas for transcription API responses and errors.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from uuid import UUID


class TranscriptionMetadata(BaseModel):
    """
    Metadata extracted from the transcription process.
    """
    duration: float = Field(..., description="Audio duration in seconds")
    language_detected: str = Field(..., description="Detected language code (e.g., 'en', 'es')")
    confidence: Optional[float] = Field(None, description="Confidence score from Whisper API (0.0 to 1.0)")

    class Config:
        json_schema_extra = {
            "example": {
                "duration": 123.45,
                "language_detected": "en",
                "confidence": 0.95
            }
        }


class TranscriptionResponse(BaseModel):
    """
    Successful transcription response model.
    
    Example:
        {
            "transcription_id": "550e8400-e29b-41d4-a716-446655440000",
            "text": "This is the transcribed content from the audio file.",
            "metadata": {
                "duration": 123.45,
                "language_detected": "en",
                "confidence": 0.95
            },
            "created_at": "2024-01-15T10:30:00Z"
        }
    """
    transcription_id: UUID = Field(..., description="Unique identifier for the transcription")
    text: str = Field(..., description="Transcribed text content")
    metadata: TranscriptionMetadata = Field(..., description="Transcription metadata")
    created_at: str = Field(..., description="ISO 8601 timestamp of creation")

    class Config:
        json_schema_extra = {
            "example": {
                "transcription_id": "550e8400-e29b-41d4-a716-446655440000",
                "text": "This is the transcribed content from the audio file.",
                "metadata": {
                    "duration": 123.45,
                    "language_detected": "en",
                    "confidence": 0.95
                },
                "created_at": "2024-01-15T10:30:00Z"
            }
        }


class ErrorDetail(BaseModel):
    """
    Error detail structure.
    """
    code: str = Field(..., description="Error type code")
    message: str = Field(..., description="Human-readable error description")
    details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional error context")

    class Config:
        json_schema_extra = {
            "example": {
                "code": "invalid_file_type",
                "message": "Unsupported file format. Please upload WAV, MP3, or M4A files.",
                "details": {"provided_type": "application/pdf"}
            }
        }


class ErrorResponse(BaseModel):
    """
    Error response model for API errors.
    
    Examples:
        Validation Error (400):
        {
            "error": {
                "code": "invalid_file_type",
                "message": "Unsupported file format. Please upload WAV, MP3, or M4A files.",
                "details": {"provided_type": "application/pdf"}
            }
        }
        
        Server Error (500):
        {
            "error": {
                "code": "api_failure",
                "message": "OpenAI API request failed after multiple retries",
                "details": {"attempts": 3}
            }
        }
    """
    error: ErrorDetail = Field(..., description="Error information")

    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "code": "api_failure",
                    "message": "OpenAI API request failed after multiple retries",
                    "details": {"attempts": 3}
                }
            }
        }
