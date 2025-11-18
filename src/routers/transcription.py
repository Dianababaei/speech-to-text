from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import ValidationError

from src.database import get_db
from src.services.transcription_service import TranscriptionService
from src.schemas.transcription import (
    TranscriptionListResponse,
    TranscriptionResponse,
    TranscriptionQueryParams
)

router = APIRouter(prefix="/v1/transcriptions", tags=["transcriptions"])


@router.get(
    "",
    response_model=TranscriptionListResponse,
    summary="List transcriptions",
    description="Get a paginated list of transcriptions with optional filtering and sorting",
    responses={
        200: {
            "description": "Successful response with transcriptions list",
            "content": {
                "application/json": {
                    "example": {
                        "transcriptions": [
                            {
                                "id": 1,
                                "audio_file_path": "/path/to/audio.mp3",
                                "transcription_text": "Hello world",
                                "language_detected": "en",
                                "duration": 5.2,
                                "status": "completed",
                                "created_at": "2024-01-01T12:00:00",
                                "updated_at": "2024-01-01T12:05:00"
                            }
                        ],
                        "total": 1,
                        "offset": 0,
                        "limit": 20
                    }
                }
            }
        },
        400: {
            "description": "Invalid query parameters",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Limit cannot exceed 100"
                    }
                }
            }
        }
    }
)
async def list_transcriptions(
    offset: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=20, ge=1, le=100, description="Maximum number of records to return (max: 100)"),
    date_from: Optional[datetime] = Query(default=None, description="Filter by created_at >= date_from (ISO 8601 format)"),
    date_to: Optional[datetime] = Query(default=None, description="Filter by created_at <= date_to (ISO 8601 format)"),
    status: Optional[str] = Query(default=None, description="Filter by status (e.g., 'completed', 'failed', 'processing')"),
    sort_by: str = Query(default="created_at", regex="^(created_at|updated_at)$", description="Field to sort by"),
    order: str = Query(default="desc", regex="^(asc|desc)$", description="Sort order (asc or desc)"),
    db: Session = Depends(get_db)
):
    """
    List transcriptions with pagination, filtering, and sorting.

    **Pagination:**
    - `offset`: Number of records to skip (default: 0)
    - `limit`: Maximum records to return (default: 20, max: 100)

    **Filtering:**
    - `date_from`: Filter by created_at >= date_from (ISO 8601 format, e.g., 2024-01-01T00:00:00)
    - `date_to`: Filter by created_at <= date_to (ISO 8601 format)
    - `status`: Filter by status value

    **Sorting:**
    - `sort_by`: Field to sort by (created_at or updated_at)
    - `order`: Sort order (asc or desc)

    **Returns:**
    - List of transcriptions matching the criteria
    - Total count of matching records
    - Pagination metadata (offset, limit)
    """
    try:
        # Validate and create query parameters model
        query_params = TranscriptionQueryParams(
            offset=offset,
            limit=limit,
            date_from=date_from,
            date_to=date_to,
            status=status,
            sort_by=sort_by,
            order=order
        )
    except ValidationError as e:
        # Extract validation error messages
        error_messages = []
        for error in e.errors():
            field = ".".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            error_messages.append(f"{field}: {message}")
        
        raise HTTPException(
            status_code=400,
            detail="; ".join(error_messages)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    # Create service and get transcriptions
    service = TranscriptionService(db)
    transcriptions, total = service.list_transcriptions(query_params)

    # Build response
    return TranscriptionListResponse(
        transcriptions=[TranscriptionResponse.from_orm(t) for t in transcriptions],
        total=total,
        offset=offset,
        limit=limit
    )
