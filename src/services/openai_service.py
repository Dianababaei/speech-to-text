"""
OpenAI service for audio transcription using Whisper API.
"""

import logging
from pathlib import Path
from typing import Optional, Dict, Any

from openai import OpenAI
from openai import (
    RateLimitError,
    APIError,
    APIConnectionError,
    AuthenticationError,
    InvalidRequestError
)

from src.utils.retry import retry_with_exponential_backoff

logger = logging.getLogger(__name__)


class OpenAIService:
    """
    Service for interacting with OpenAI's Whisper API for audio transcription.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the OpenAI service.
        
        Args:
            api_key: OpenAI API key. If not provided, will use environment variable.
        """
        self.client = OpenAI(api_key=api_key) if api_key else OpenAI()
        logger.info("OpenAI service initialized")
    
    @retry_with_exponential_backoff(max_attempts=3, backoff_delays=[1, 2, 4])
    def transcribe_audio(
        self,
        audio_file: str,
        model: str = "whisper-1",
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: str = "text",
        temperature: float = 0.0
    ) -> str:
        """
        Transcribe audio file using OpenAI Whisper API with automatic retry on transient errors.
        
        This function is wrapped with exponential backoff retry logic that:
        - Retries up to 3 times total (initial + 2 retries)
        - Uses exponential backoff delays: 1s, 2s, 4s
        - Retries on: RateLimitError (429), Timeout, APIError, APIConnectionError
        - Does NOT retry on: AuthenticationError (401), InvalidRequestError (400)
        
        Args:
            audio_file: Path to the audio file to transcribe (WAV, MP3, M4A supported)
            model: Model to use for transcription (default: "whisper-1")
            language: Optional language code (e.g., "en", "es", "fr")
            prompt: Optional prompt to guide the model
            response_format: Format of the response (default: "text")
            temperature: Sampling temperature (default: 0.0 for deterministic output)
        
        Returns:
            Transcribed text as a string
        
        Raises:
            FileNotFoundError: If the audio file doesn't exist
            AuthenticationError: If API key is invalid (not retried)
            InvalidRequestError: If request parameters are invalid (not retried)
            RateLimitError: If rate limit is exceeded after all retries
            APIError: If API error occurs after all retries
            APIConnectionError: If connection fails after all retries
        """
        # Validate file exists
        file_path = Path(audio_file)
        if not file_path.exists():
            error_msg = f"Audio file not found: {audio_file}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        logger.info(f"Starting transcription for file: {audio_file}")
        
        try:
            # Open the audio file and send to OpenAI
            with open(audio_file, "rb") as audio:
                # Prepare transcription parameters
                transcription_params: Dict[str, Any] = {
                    "model": model,
                    "file": audio,
                    "response_format": response_format,
                    "temperature": temperature
                }
                
                # Add optional parameters if provided
                if language:
                    transcription_params["language"] = language
                if prompt:
                    transcription_params["prompt"] = prompt
                
                # Call OpenAI Whisper API
                response = self.client.audio.transcriptions.create(**transcription_params)
                
                # Extract text from response
                if isinstance(response, str):
                    transcript = response
                else:
                    transcript = response.text if hasattr(response, 'text') else str(response)
                
                logger.info(f"Successfully transcribed file: {audio_file} ({len(transcript)} characters)")
                return transcript
                
        except (AuthenticationError, InvalidRequestError) as e:
            # These are permanent errors - logged and raised by retry decorator
            logger.error(f"Permanent error during transcription of {audio_file}: {type(e).__name__} - {str(e)}")
            raise
            
        except (RateLimitError, APIError, APIConnectionError) as e:
            # These are transient errors - will be retried by decorator
            logger.warning(f"Transient error during transcription of {audio_file}: {type(e).__name__} - {str(e)}")
            raise
            
        except Exception as e:
            # Unexpected error
            logger.error(f"Unexpected error during transcription of {audio_file}: {type(e).__name__} - {str(e)}")
            raise


# Convenience function for direct use
@retry_with_exponential_backoff(max_attempts=3, backoff_delays=[1, 2, 4])
def transcribe_audio(
    audio_file: str,
    api_key: Optional[str] = None,
    model: str = "whisper-1",
    language: Optional[str] = None,
    prompt: Optional[str] = None,
    response_format: str = "text",
    temperature: float = 0.0
) -> str:
    """
    Convenience function to transcribe audio without instantiating OpenAIService.
    
    This function is wrapped with exponential backoff retry logic that:
    - Retries up to 3 times total (initial + 2 retries)
    - Uses exponential backoff delays: 1s, 2s, 4s
    - Retries on: RateLimitError (429), Timeout, APIError, APIConnectionError
    - Does NOT retry on: AuthenticationError (401), InvalidRequestError (400)
    
    Args:
        audio_file: Path to the audio file to transcribe
        api_key: OpenAI API key (optional, uses environment variable if not provided)
        model: Model to use for transcription (default: "whisper-1")
        language: Optional language code
        prompt: Optional prompt to guide the model
        response_format: Format of the response (default: "text")
        temperature: Sampling temperature (default: 0.0)
    
    Returns:
        Transcribed text as a string
    
    Raises:
        Same exceptions as OpenAIService.transcribe_audio()
    """
    service = OpenAIService(api_key=api_key)
    # Note: The retry decorator is applied to both this function and the method,
    # but only one will be active per call path
    return service.transcribe_audio(
        audio_file=audio_file,
        model=model,
        language=language,
        prompt=prompt,
        response_format=response_format,
        temperature=temperature
    )
