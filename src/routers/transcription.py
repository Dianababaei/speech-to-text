"""
FastAPI router for transcription endpoints.
"""

from typing import Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse

from ..schemas.transcription import TranscriptionResponse, ErrorResponse
from ..services.transcription import (
    format_transcription_response,
    format_error_response,
    extract_whisper_metadata
)


router = APIRouter(prefix="/v1", tags=["transcription"])


# Custom exception classes for different error types
class ValidationError(Exception):
    """Raised for validation errors (400)"""
    def __init__(self, code: str, message: str, details: Dict[str, Any] = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ServerError(Exception):
    """Raised for server-side errors (500)"""
    def __init__(self, code: str, message: str, details: Dict[str, Any] = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


@router.post(
    "/transcribe",
    response_model=TranscriptionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {
            "description": "Successful transcription",
            "content": {
                "application/json": {
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
            }
        },
        400: {
            "description": "Validation error",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_file_type": {
                            "summary": "Invalid file type",
                            "value": {
                                "error": {
                                    "code": "invalid_file_type",
                                    "message": "Unsupported file format. Please upload WAV, MP3, or M4A files.",
                                    "details": {"provided_type": "application/pdf"}
                                }
                            }
                        },
                        "file_size_exceeded": {
                            "summary": "File size exceeded",
                            "value": {
                                "error": {
                                    "code": "file_size_exceeded",
                                    "message": "File size exceeds maximum allowed limit",
                                    "details": {"max_size_mb": 25, "provided_size_mb": 30}
                                }
                            }
                        },
                        "missing_file": {
                            "summary": "Missing required field",
                            "value": {
                                "error": {
                                    "code": "missing_field",
                                    "message": "Audio file is required",
                                    "details": {}
                                }
                            }
                        }
                    }
                }
            }
        },
        500: {
            "description": "Server error",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "examples": {
                        "api_failure": {
                            "summary": "OpenAI API failure",
                            "value": {
                                "error": {
                                    "code": "api_failure",
                                    "message": "OpenAI API request failed after multiple retries",
                                    "details": {"attempts": 3}
                                }
                            }
                        },
                        "database_error": {
                            "summary": "Database error",
                            "value": {
                                "error": {
                                    "code": "database_error",
                                    "message": "Failed to store transcription in database",
                                    "details": {}
                                }
                            }
                        },
                        "storage_failure": {
                            "summary": "Storage failure",
                            "value": {
                                "error": {
                                    "code": "storage_failure",
                                    "message": "Failed to store audio file",
                                    "details": {}
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    summary="Transcribe audio file",
    description="""
    Upload an audio file and receive a transcription.
    
    **Supported formats:** WAV, MP3, M4A
    
    **Maximum file size:** 25 MB
    
    **Response:** Returns transcription text with metadata including duration, 
    detected language, and optional confidence score.
    
    **Error handling:**
    - 400: Validation errors (invalid file type, size exceeded, missing fields)
    - 500: Server errors (OpenAI API failure after retries, database errors, storage failures)
    """
)
async def transcribe_audio(
    file: UploadFile = File(..., description="Audio file to transcribe (WAV, MP3, or M4A)")
) -> JSONResponse:
    """
    Transcribe an audio file to text using OpenAI Whisper API.
    
    This endpoint:
    1. Validates the uploaded file (type and size)
    2. Sends the audio to OpenAI Whisper API with retry logic
    3. Extracts metadata from the response
    4. Formats and returns the transcription with metadata
    
    Args:
        file: Uploaded audio file
    
    Returns:
        JSONResponse with transcription data and 200 status code
    
    Raises:
        ValidationError: For validation failures (returns 400)
        ServerError: For server-side failures (returns 500)
    """
    try:
        # Validate file is present
        if not file:
            raise ValidationError(
                code="missing_field",
                message="Audio file is required",
                details={}
            )
        
        # Validate file type
        allowed_types = ["audio/wav", "audio/mpeg", "audio/mp4", "audio/x-m4a"]
        allowed_extensions = [".wav", ".mp3", ".m4a"]
        
        file_extension = file.filename.lower().split('.')[-1] if file.filename else ""
        content_type = file.content_type
        
        if content_type not in allowed_types and f".{file_extension}" not in allowed_extensions:
            raise ValidationError(
                code="invalid_file_type",
                message="Unsupported file format. Please upload WAV, MP3, or M4A files.",
                details={"provided_type": content_type or "unknown"}
            )
        
        # Validate file size (placeholder - actual size checking would be done during upload)
        # This assumes file size validation happens at upload endpoint (Task #25)
        
        # TODO: Integration with actual OpenAI Whisper API call
        # This would use the retry logic from Task #27
        # For now, this is a placeholder showing the expected flow:
        
        # Example placeholder for API call:
        # whisper_response = await call_whisper_api_with_retry(file)
        
        # Mock response structure (to be replaced with actual API integration)
        whisper_response = {
            "text": "Transcribed audio content would appear here.",
            "duration": 123.45,
            "language": "en",
            "confidence": 0.95
        }
        
        # Extract metadata from Whisper response
        try:
            text, duration, language_detected, confidence = extract_whisper_metadata(whisper_response)
        except ValueError as e:
            raise ServerError(
                code="invalid_api_response",
                message=f"Invalid response from Whisper API: {str(e)}",
                details={}
            )
        
        # Format the response
        response_data = format_transcription_response(
            text=text,
            duration=duration,
            language_detected=language_detected,
            confidence=confidence
        )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_data
        )
    
    except ValidationError as e:
        # Handle validation errors (400)
        error_response = format_error_response(
            code=e.code,
            message=e.message,
            details=e.details
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_response
        )
    
    except ServerError as e:
        # Handle server errors (500)
        error_response = format_error_response(
            code=e.code,
            message=e.message,
            details=e.details
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response
        )
    
    except Exception as e:
        # Handle unexpected errors (500)
        error_response = format_error_response(
            code="internal_error",
            message="An unexpected error occurred during transcription",
            details={"error": str(e)}
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response
        )
