"""
File storage service for managing audio file operations.

Handles saving, retrieving, and deleting audio files with organized
date-based directory structure (YYYY/MM/DD) and UUID-based filenames.
"""

import os
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import BinaryIO, Optional, Set
from shutil import copyfileobj

from ..config import config

# Configure logging
logger = logging.getLogger(__name__)


class StorageError(Exception):
    """Base exception for storage-related errors."""
    pass


class DiskFullError(StorageError):
    """Raised when disk is full."""
    pass


class PermissionError(StorageError):
    """Raised when permission is denied."""
    pass


class InvalidPathError(StorageError):
    """Raised when an invalid path is provided."""
    pass


class StorageService:
    """
    Service for managing audio file storage operations.
    
    Organizes files in a date-based directory structure (YYYY/MM/DD)
    with UUID v4 filenames to prevent collisions.
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize the storage service.
        
        Args:
            base_path: Base directory for storage. If None, uses config value.
        """
        self.base_path = base_path or config.get_audio_storage_path()
        self._ensure_base_directory()
        logger.info(f"StorageService initialized with base path: {self.base_path}")
    
    def _ensure_base_directory(self) -> None:
        """
        Ensure the base storage directory exists with proper permissions.
        
        Raises:
            PermissionError: If directory cannot be created due to permissions.
            StorageError: If directory creation fails for other reasons.
        """
        try:
            self.base_path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Base directory ensured: {self.base_path}")
        except PermissionError as e:
            logger.error(f"Permission denied creating base directory: {self.base_path}")
            raise PermissionError(f"Cannot create storage directory: {e}")
        except Exception as e:
            logger.error(f"Failed to create base directory: {e}")
            raise StorageError(f"Failed to create storage directory: {e}")
    
    def _get_date_path(self, date: Optional[datetime] = None) -> Path:
        """
        Generate date-based directory path (YYYY/MM/DD).
        
        Args:
            date: Date to use for path. If None, uses current date.
            
        Returns:
            Path: Date-based subdirectory path relative to base
        """
        if date is None:
            date = datetime.now()
        
        year = date.strftime("%Y")
        month = date.strftime("%m")
        day = date.strftime("%d")
        
        return Path(year) / month / day
    
    def _ensure_directory(self, directory: Path) -> None:
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            directory: Directory path to ensure exists
            
        Raises:
            PermissionError: If directory cannot be created due to permissions.
            StorageError: If directory creation fails for other reasons.
        """
        try:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Directory ensured: {directory}")
        except PermissionError as e:
            logger.error(f"Permission denied creating directory: {directory}")
            raise PermissionError(f"Cannot create directory: {e}")
        except Exception as e:
            logger.error(f"Failed to create directory: {e}")
            raise StorageError(f"Failed to create directory: {e}")
    
    def _normalize_extension(self, extension: str) -> str:
        """
        Normalize file extension to lowercase, ensuring leading dot.
        
        Args:
            extension: File extension (with or without leading dot)
            
        Returns:
            str: Normalized extension with leading dot (e.g., '.mp3')
        """
        ext = extension.lower().strip()
        if not ext.startswith('.'):
            ext = f'.{ext}'
        return ext
    
    def save_audio_file(
        self,
        file: BinaryIO,
        extension: str,
        date: Optional[datetime] = None
    ) -> str:
        """
        Save an audio file to the storage system.
        
        Creates a date-based directory structure (YYYY/MM/DD) and saves
        the file with a UUID v4 filename to prevent collisions.
        
        Args:
            file: File-like object to save (must be opened in binary mode)
            extension: File extension (e.g., 'wav', 'mp3', 'm4a')
            date: Optional date for directory structure. Uses current date if None.
            
        Returns:
            str: Relative path to saved file (e.g., '2024/01/15/abc-123-def.mp3')
            
        Raises:
            InvalidPathError: If extension is invalid
            PermissionError: If file cannot be written due to permissions
            DiskFullError: If disk is full
            StorageError: If save fails for other reasons
        """
        # Validate and normalize extension
        ext = self._normalize_extension(extension)
        if ext not in ['.wav', '.mp3', '.m4a']:
            logger.warning(f"Unusual file extension: {ext}")
        
        # Generate UUID filename
        filename = f"{uuid.uuid4()}{ext}"
        
        # Get date-based subdirectory
        date_path = self._get_date_path(date)
        
        # Full directory path
        full_dir = self.base_path / date_path
        
        # Ensure directory exists
        self._ensure_directory(full_dir)
        
        # Full file path
        full_path = full_dir / filename
        
        # Relative path for database storage
        relative_path = str(date_path / filename)
        
        # Save the file
        try:
            with open(full_path, 'wb') as dest:
                # Use copyfileobj for efficient copying
                copyfileobj(file, dest)
            
            logger.info(f"Audio file saved: {relative_path}")
            return relative_path
            
        except PermissionError as e:
            logger.error(f"Permission denied writing file: {full_path}")
            raise PermissionError(f"Cannot write file: {e}")
        except OSError as e:
            # Check for disk full error (errno 28 on Linux, errno 112 on some systems)
            if e.errno in (28, 112):
                logger.error(f"Disk full while writing file: {full_path}")
                raise DiskFullError(f"Disk full: {e}")
            else:
                logger.error(f"OS error writing file: {e}")
                raise StorageError(f"Failed to write file: {e}")
        except Exception as e:
            logger.error(f"Unexpected error saving file: {e}")
            raise StorageError(f"Failed to save file: {e}")
    
    def get_audio_file_path(self, relative_path: str) -> Path:
        """
        Resolve a relative path to an absolute filesystem path.
        
        Args:
            relative_path: Relative path as stored in database
                          (e.g., '2024/01/15/abc-123-def.mp3')
            
        Returns:
            Path: Absolute path to the file
            
        Raises:
            InvalidPathError: If the path is invalid or attempts directory traversal
        """
        # Validate path - prevent directory traversal
        if '..' in relative_path or relative_path.startswith('/'):
            logger.error(f"Invalid path detected: {relative_path}")
            raise InvalidPathError(f"Invalid path: {relative_path}")
        
        # Convert to Path and resolve
        try:
            rel_path = Path(relative_path)
            full_path = self.base_path / rel_path
            
            # Ensure resolved path is still under base_path (prevent traversal)
            resolved = full_path.resolve()
            base_resolved = self.base_path.resolve()
            
            if not str(resolved).startswith(str(base_resolved)):
                logger.error(f"Path traversal attempt detected: {relative_path}")
                raise InvalidPathError(f"Path outside storage directory: {relative_path}")
            
            return resolved
            
        except Exception as e:
            logger.error(f"Error resolving path: {e}")
            raise InvalidPathError(f"Invalid path: {relative_path}")
    
    def delete_audio_file(self, relative_path: str) -> bool:
        """
        Delete an audio file from the storage system.
        
        Args:
            relative_path: Relative path to file (e.g., '2024/01/15/abc-123-def.mp3')
            
        Returns:
            bool: True if file was deleted, False if file didn't exist
            
        Raises:
            InvalidPathError: If the path is invalid
            PermissionError: If file cannot be deleted due to permissions
            StorageError: If deletion fails for other reasons
        """
        full_path = self.get_audio_file_path(relative_path)
        
        try:
            if not full_path.exists():
                logger.warning(f"File not found for deletion: {relative_path}")
                return False
            
            full_path.unlink()
            logger.info(f"Audio file deleted: {relative_path}")
            
            # Optionally clean up empty parent directories
            self._cleanup_empty_directories(full_path.parent)
            
            return True
            
        except PermissionError as e:
            logger.error(f"Permission denied deleting file: {relative_path}")
            raise PermissionError(f"Cannot delete file: {e}")
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            raise StorageError(f"Failed to delete file: {e}")
    
    def _cleanup_empty_directories(self, directory: Path) -> None:
        """
        Remove empty parent directories up to base_path.
        
        Args:
            directory: Directory to start cleanup from
        """
        try:
            current = directory
            base_resolved = self.base_path.resolve()
            
            while current != base_resolved and current > base_resolved:
                if current.exists() and not any(current.iterdir()):
                    current.rmdir()
                    logger.debug(f"Removed empty directory: {current}")
                    current = current.parent
                else:
                    break
        except Exception as e:
            # Don't fail if cleanup fails - this is a courtesy operation
            logger.debug(f"Could not clean up empty directories: {e}")
    
    def get_all_stored_files(self) -> Set[str]:
        """
        Get all audio files currently in storage.
        
        Returns:
            Set[str]: Set of relative paths for all stored files
        """
        stored_files = set()
        
        try:
            if not self.base_path.exists():
                return stored_files
            
            # Walk through the directory structure
            for file_path in self.base_path.rglob('*'):
                if file_path.is_file():
                    # Get relative path from base
                    relative = file_path.relative_to(self.base_path)
                    stored_files.add(str(relative))
            
            logger.debug(f"Found {len(stored_files)} files in storage")
            return stored_files
            
        except Exception as e:
            logger.error(f"Error scanning storage directory: {e}")
            raise StorageError(f"Failed to scan storage: {e}")
    
    def cleanup_orphaned_files(self, database_files: Set[str]) -> int:
        """
        Remove files from storage that are not referenced in the database.
        
        Args:
            database_files: Set of relative paths that should exist
                           (from Transcription.audio_path records)
            
        Returns:
            int: Number of orphaned files deleted
            
        Raises:
            StorageError: If cleanup fails
        """
        logger.info("Starting orphaned files cleanup")
        
        try:
            stored_files = self.get_all_stored_files()
            orphaned_files = stored_files - database_files
            
            deleted_count = 0
            for relative_path in orphaned_files:
                try:
                    if self.delete_audio_file(relative_path):
                        deleted_count += 1
                        logger.info(f"Deleted orphaned file: {relative_path}")
                except Exception as e:
                    logger.error(f"Failed to delete orphaned file {relative_path}: {e}")
                    # Continue with other files
            
            logger.info(f"Cleanup complete. Deleted {deleted_count} orphaned files")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Orphaned file cleanup failed: {e}")
            raise StorageError(f"Cleanup failed: {e}")


# Create singleton instance for easy import
storage_service = StorageService()
