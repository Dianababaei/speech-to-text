"""
Configuration module for loading environment variables and application settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""
    
    # Audio storage configuration
    AUDIO_STORAGE_PATH: str = os.getenv(
        'AUDIO_STORAGE_PATH',
        './storage/audio/'
    )
    
    @classmethod
    def get_audio_storage_path(cls) -> Path:
        """
        Get the audio storage path as a Path object.
        
        Returns:
            Path: The base path for audio file storage
        """
        return Path(cls.AUDIO_STORAGE_PATH)


# Create singleton instance for easy import
config = Config()
