from typing import Optional, Tuple, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from src.models.transcription import Transcription
from src.schemas.transcription import TranscriptionQueryParams


class TranscriptionService:
    """Service layer for transcription operations."""

    def __init__(self, db: Session):
        self.db = db

    def list_transcriptions(
        self,
        query_params: TranscriptionQueryParams
    ) -> Tuple[List[Transcription], int]:
        """
        List transcriptions with filtering, pagination, and sorting.

        Args:
            query_params: Query parameters including filters, pagination, and sorting options

        Returns:
            Tuple of (list of transcriptions, total count)
        """
        # Build base query
        query = self.db.query(Transcription)

        # Apply filters
        filters = []

        if query_params.date_from:
            filters.append(Transcription.created_at >= query_params.date_from)

        if query_params.date_to:
            filters.append(Transcription.created_at <= query_params.date_to)

        if query_params.status:
            filters.append(Transcription.status == query_params.status)

        if filters:
            query = query.filter(and_(*filters))

        # Get total count before pagination
        total = query.count()

        # Apply sorting
        sort_column = getattr(Transcription, query_params.sort_by)
        if query_params.order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        query = query.offset(query_params.offset).limit(query_params.limit)

        # Execute query
        transcriptions = query.all()

        return transcriptions, total
