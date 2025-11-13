"""
Service layer for transcription operations including response formatting.
"""

from datetime import datetime, timezone
from typing import Dict, Any, Optional
from uuid import uuid4, UUID

from ..schemas.transcription import (
    TranscriptionResponse,
    TranscriptionMetadata,
    ErrorResponse,
    ErrorDetail
)


def format_transcription_response(
    text: str,
    duration: float,
    language_detected: str,
    confidence: Optional[float] = None,
    transcription_id: Optional[UUID] = None
) -> Dict[str, Any]:
    """
    Format transcription data into the standardized API response format.
    
    Args:
        text: The transcribed text content
        duration: Audio duration in seconds
        language_detected: Detected language code (e.g., 'en', 'es')
        confidence: Optional confidence score from Whisper API (0.0 to 1.0)
        transcription_id: Optional UUID, will be generated if not provided
    
    Returns:
        Dictionary conforming to TranscriptionResponse schema
    
    Example:
        >>> format_transcription_response(
        ...     text="Hello world",
        ...     duration=5.5,
        ...     language_detected="en",
        ...     confidence=0.98
        ... )
        {
            "transcription_id": "550e8400-e29b-41d4-a716-446655440000",
            "text": "Hello world",
            "metadata": {
                "duration": 5.5,
                "language_detected": "en",
                "confidence": 0.98
            },
            "created_at": "2024-01-15T10:30:00Z"
        }
    """
    # Generate UUID if not provided
    if transcription_id is None:
        transcription_id = uuid4()
    
    # Create ISO 8601 timestamp
    created_at = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    # Build metadata object
    metadata = TranscriptionMetadata(
        duration=duration,
        language_detected=language_detected,
        confidence=confidence
    )
    
    # Create response object
    response = TranscriptionResponse(
        transcription_id=transcription_id,
        text=text,
        metadata=metadata,
        created_at=created_at
    )
    
    return response.model_dump()


def format_error_response(
    code: str,
    message: str,
    details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Format error information into the standardized error response format.
    
    Args:
        code: Error type code (e.g., 'invalid_file_type', 'api_failure')
        message: Human-readable error description
        details: Optional dictionary with additional error context
    
    Returns:
        Dictionary conforming to ErrorResponse schema
    
    Example:
        >>> format_error_response(
        ...     code="invalid_file_type",
        ...     message="Unsupported file format",
        ...     details={"provided_type": "application/pdf"}
        ... )
        {
            "error": {
                "code": "invalid_file_type",
                "message": "Unsupported file format",
                "details": {"provided_type": "application/pdf"}
            }
        }
    """
    if details is None:
        details = {}
    
    error_detail = ErrorDetail(
        code=code,
        message=message,
        details=details
    )
    
    error_response = ErrorResponse(error=error_detail)
    
    return error_response.model_dump()


def extract_whisper_metadata(
    whisper_response: Dict[str, Any]
) -> tuple[str, float, str, Optional[float]]:
    """
    Extract metadata from OpenAI Whisper API response.
    
    Handles edge cases like missing metadata fields or null values.
    
    Args:
        whisper_response: Raw response from OpenAI Whisper API
    
    Returns:
        Tuple of (text, duration, language_detected, confidence)
    
    Raises:
        ValueError: If required fields are missing from the response
    """
    # Extract required fields
    text = whisper_response.get('text')
    if text is None:
        raise ValueError("Whisper response missing 'text' field")
    
    # Extract duration (may need to be calculated or provided separately)
    duration = whisper_response.get('duration', 0.0)
    
    # Extract language (default to 'en' if not provided)
    language_detected = whisper_response.get('language', 'en')
    
    # Extract optional confidence score
    confidence = whisper_response.get('confidence')
    
    return text, duration, language_detected, confidence
