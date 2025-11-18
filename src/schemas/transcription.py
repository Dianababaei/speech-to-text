from datetime import datetime
from typing import Optional, List, Literal
from pydantic import BaseModel, Field, validator


class TranscriptionResponse(BaseModel):
    """Response schema for a single transcription."""
    id: int
    audio_file_path: str
    transcription_text: Optional[str] = None
    language_detected: Optional[str] = None
    duration: Optional[float] = None
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TranscriptionListResponse(BaseModel):
    """Response schema for list of transcriptions with pagination metadata."""
    transcriptions: List[TranscriptionResponse]
    total: int
    offset: int
    limit: int


class TranscriptionQueryParams(BaseModel):
    """Query parameters for listing transcriptions."""
    offset: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum number of records to return (max: 100)")
    date_from: Optional[datetime] = Field(default=None, description="Filter by created_at >= date_from (ISO 8601)")
    date_to: Optional[datetime] = Field(default=None, description="Filter by created_at <= date_to (ISO 8601)")
    status: Optional[str] = Field(default=None, description="Filter by status (e.g., 'completed', 'failed')")
    sort_by: Literal["created_at", "updated_at"] = Field(default="created_at", description="Field to sort by")
    order: Literal["asc", "desc"] = Field(default="desc", description="Sort order")

    @validator("limit")
    def validate_limit(cls, v):
        """Enforce maximum limit of 100."""
        if v > 100:
            raise ValueError("Limit cannot exceed 100")
        return v

    @validator("date_to")
    def validate_date_range(cls, v, values):
        """Ensure date_to is after date_from if both are provided."""
        if v and "date_from" in values and values["date_from"]:
            if v < values["date_from"]:
                raise ValueError("date_to must be after date_from")
        return v
