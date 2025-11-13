"""
Service layer for transcription CRUD operations.

This module provides a TranscriptionService class that encapsulates all database
operations related to transcriptions. It follows the repository pattern and handles
transaction management, error handling, and logging.
"""
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime

from src.models import Transcription
from src.exceptions import TranscriptionNotFoundError, DatabaseOperationError

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class TranscriptionService:
    """
    Service class for managing transcription database operations.
    
    This class encapsulates all CRUD operations for transcriptions and provides
    proper transaction management, error handling, and logging.
    
    Attributes:
        db (Session): SQLAlchemy database session for database operations
    """
    
    def __init__(self, db: Session):
        """
        Initialize the TranscriptionService with a database session.
        
        Args:
            db (Session): SQLAlchemy database session
        """
        self.db = db
    
    def create_transcription(
        self,
        audio_path: str,
        text: str,
        language: Optional[str] = None,
        duration: Optional[float] = None,
        status: str = "completed"
    ) -> Transcription:
        """
        Create a new transcription record in the database.
        
        Args:
            audio_path (str): File path to the audio file
            text (str): Transcribed text content
            language (Optional[str]): Language of the transcription (e.g., "en", "es")
            duration (Optional[float]): Duration of the audio in seconds
            status (str): Status of the transcription (default: "completed")
            
        Returns:
            Transcription: The created transcription object
            
        Raises:
            DatabaseOperationError: If the database operation fails
            
        Example:
            ```python
            service = TranscriptionService(db)
            transcription = service.create_transcription(
                audio_path="/uploads/audio123.mp3",
                text="Hello world",
                language="en",
                duration=5.2,
                status="completed"
            )
            ```
        """
        try:
            # Create new transcription object
            transcription = Transcription(
                audio_path=audio_path,
                text=text,
                language=language,
                duration=duration,
                status=status
            )
            
            # Add to session and commit
            self.db.add(transcription)
            self.db.commit()
            self.db.refresh(transcription)
            
            logger.info(
                f"Successfully created transcription with ID {transcription.id} "
                f"for audio file: {audio_path}"
            )
            
            return transcription
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Integrity error creating transcription: {str(e)}")
            raise DatabaseOperationError(
                "Failed to create transcription due to constraint violation",
                original_error=e
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error creating transcription: {str(e)}")
            raise DatabaseOperationError(
                "Failed to create transcription due to database error",
                original_error=e
            )
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error creating transcription: {str(e)}")
            raise DatabaseOperationError(
                "Failed to create transcription due to unexpected error",
                original_error=e
            )
    
    def get_transcription_by_id(self, transcription_id: int) -> Optional[Transcription]:
        """
        Retrieve a transcription by its ID.
        
        Args:
            transcription_id (int): The ID of the transcription to retrieve
            
        Returns:
            Optional[Transcription]: The transcription object if found, None otherwise
            
        Example:
            ```python
            service = TranscriptionService(db)
            transcription = service.get_transcription_by_id(123)
            if transcription:
                print(f"Found: {transcription.text}")
            else:
                print("Not found")
            ```
        """
        try:
            transcription = self.db.query(Transcription).filter(
                Transcription.id == transcription_id
            ).first()
            
            if transcription:
                logger.info(f"Retrieved transcription with ID {transcription_id}")
            else:
                logger.info(f"Transcription with ID {transcription_id} not found")
            
            return transcription
            
        except SQLAlchemyError as e:
            logger.error(f"Database error retrieving transcription {transcription_id}: {str(e)}")
            raise DatabaseOperationError(
                f"Failed to retrieve transcription with ID {transcription_id}",
                original_error=e
            )
    
    def update_transcription(
        self,
        transcription_id: int,
        **updates: Any
    ) -> Transcription:
        """
        Update a transcription with partial updates.
        
        This method supports partial updates, meaning only the fields provided
        in the updates dictionary will be changed. All other fields remain unchanged.
        
        Args:
            transcription_id (int): The ID of the transcription to update
            **updates: Keyword arguments representing fields to update
                      Valid fields: audio_path, text, language, duration, status
            
        Returns:
            Transcription: The updated transcription object
            
        Raises:
            TranscriptionNotFoundError: If transcription with given ID doesn't exist
            DatabaseOperationError: If the database operation fails
            
        Example:
            ```python
            service = TranscriptionService(db)
            updated = service.update_transcription(
                123,
                text="Updated transcription text",
                status="reviewed"
            )
            ```
        """
        try:
            # Get existing transcription
            transcription = self.db.query(Transcription).filter(
                Transcription.id == transcription_id
            ).first()
            
            if not transcription:
                logger.warning(f"Attempted to update non-existent transcription {transcription_id}")
                raise TranscriptionNotFoundError(transcription_id)
            
            # Apply updates to valid fields only
            valid_fields = {'audio_path', 'text', 'language', 'duration', 'status'}
            updated_fields = []
            
            for key, value in updates.items():
                if key in valid_fields:
                    setattr(transcription, key, value)
                    updated_fields.append(key)
            
            # Update the updated_at timestamp
            transcription.updated_at = datetime.utcnow()
            
            # Commit changes
            self.db.commit()
            self.db.refresh(transcription)
            
            logger.info(
                f"Successfully updated transcription {transcription_id}. "
                f"Updated fields: {', '.join(updated_fields)}"
            )
            
            return transcription
            
        except TranscriptionNotFoundError:
            # Re-raise without rollback (no changes made)
            raise
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Integrity error updating transcription {transcription_id}: {str(e)}")
            raise DatabaseOperationError(
                f"Failed to update transcription {transcription_id} due to constraint violation",
                original_error=e
            )
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error updating transcription {transcription_id}: {str(e)}")
            raise DatabaseOperationError(
                f"Failed to update transcription {transcription_id}",
                original_error=e
            )
    
    def delete_transcription(self, transcription_id: int) -> bool:
        """
        Delete a transcription from the database.
        
        Note: This method only deletes the database record. The caller is responsible
        for handling any associated file deletion (e.g., audio files) if needed.
        
        Args:
            transcription_id (int): The ID of the transcription to delete
            
        Returns:
            bool: True if deletion was successful, False if transcription not found
            
        Raises:
            DatabaseOperationError: If the database operation fails
            
        Example:
            ```python
            service = TranscriptionService(db)
            success = service.delete_transcription(123)
            if success:
                print("Deleted successfully")
            else:
                print("Transcription not found")
            ```
        """
        try:
            # Get existing transcription
            transcription = self.db.query(Transcription).filter(
                Transcription.id == transcription_id
            ).first()
            
            if not transcription:
                logger.info(f"Attempted to delete non-existent transcription {transcription_id}")
                return False
            
            # Delete the transcription
            self.db.delete(transcription)
            self.db.commit()
            
            logger.info(f"Successfully deleted transcription {transcription_id}")
            return True
            
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error deleting transcription {transcription_id}: {str(e)}")
            raise DatabaseOperationError(
                f"Failed to delete transcription {transcription_id}",
                original_error=e
            )
    
    def list_transcriptions(
        self,
        offset: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Transcription]:
        """
        List transcriptions with pagination and optional filtering.
        
        Args:
            offset (int): Number of records to skip (default: 0)
            limit (int): Maximum number of records to return (default: 100)
            filters (Optional[Dict[str, Any]]): Optional filters to apply
                Supported filters:
                - status: Filter by transcription status
                - language: Filter by language
                - audio_path: Filter by audio file path (partial match)
                
        Returns:
            List[Transcription]: List of transcription objects
            
        Raises:
            DatabaseOperationError: If the database operation fails
            
        Example:
            ```python
            service = TranscriptionService(db)
            
            # Get first 50 transcriptions
            transcriptions = service.list_transcriptions(offset=0, limit=50)
            
            # Get completed transcriptions in English
            transcriptions = service.list_transcriptions(
                filters={"status": "completed", "language": "en"}
            )
            ```
        """
        try:
            # Start with base query
            query = self.db.query(Transcription)
            
            # Apply filters if provided
            if filters:
                if 'status' in filters and filters['status']:
                    query = query.filter(Transcription.status == filters['status'])
                
                if 'language' in filters and filters['language']:
                    query = query.filter(Transcription.language == filters['language'])
                
                if 'audio_path' in filters and filters['audio_path']:
                    query = query.filter(
                        Transcription.audio_path.ilike(f"%{filters['audio_path']}%")
                    )
            
            # Apply ordering (most recent first)
            query = query.order_by(Transcription.created_at.desc())
            
            # Apply pagination
            transcriptions = query.offset(offset).limit(limit).all()
            
            logger.info(
                f"Retrieved {len(transcriptions)} transcriptions "
                f"(offset={offset}, limit={limit}, filters={filters})"
            )
            
            return transcriptions
            
        except SQLAlchemyError as e:
            logger.error(f"Database error listing transcriptions: {str(e)}")
            raise DatabaseOperationError(
                "Failed to list transcriptions",
                original_error=e
            )
