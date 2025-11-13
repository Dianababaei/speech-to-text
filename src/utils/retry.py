"""
Retry decorator with exponential backoff for handling transient API errors.
"""

import time
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)


def retry_with_exponential_backoff(
    max_attempts: int = 3,
    backoff_delays: list = None
):
    """
    Decorator that retries a function with exponential backoff on transient errors.
    
    Args:
        max_attempts: Maximum number of attempts (initial + retries). Default is 3.
        backoff_delays: List of delays in seconds between retries. Default is [1, 2, 4].
    
    Returns:
        Decorated function that automatically retries on transient errors.
    
    Retries on:
        - RateLimitError (429)
        - Timeout errors
        - APIError
        - APIConnectionError
    
    Does NOT retry on:
        - AuthenticationError (401)
        - InvalidRequestError (400)
    """
    if backoff_delays is None:
        backoff_delays = [1, 2, 4]
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    # Attempt to execute the function
                    result = func(*args, **kwargs)
                    
                    # Log successful retry if this wasn't the first attempt
                    if attempt > 0:
                        logger.info(
                            f"Successfully executed {func.__name__} on attempt {attempt + 1}/{max_attempts}"
                        )
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    error_type = type(e).__name__
                    
                    # Check if this is a permanent error that should not be retried
                    if _is_permanent_error(e):
                        logger.error(
                            f"Permanent error in {func.__name__}: {error_type} - {str(e)}. "
                            f"Not retrying."
                        )
                        raise
                    
                    # Check if this is a retryable error
                    if not _is_retryable_error(e):
                        logger.error(
                            f"Non-retryable error in {func.__name__}: {error_type} - {str(e)}"
                        )
                        raise
                    
                    # Calculate if we have more attempts left
                    attempts_remaining = max_attempts - attempt - 1
                    
                    if attempts_remaining > 0:
                        # Get the delay for this retry (use the last delay if we exceed the list)
                        delay_index = min(attempt, len(backoff_delays) - 1)
                        delay = backoff_delays[delay_index]
                        
                        # Extract file information from kwargs if available
                        file_info = ""
                        if 'file_path' in kwargs:
                            file_info = f" (file: {kwargs['file_path']})"
                        elif 'audio_file' in kwargs:
                            file_info = f" (file: {kwargs['audio_file']})"
                        
                        logger.warning(
                            f"Retry attempt {attempt + 1}/{max_attempts} for {func.__name__}: "
                            f"{error_type} - {str(e)}{file_info}. "
                            f"Waiting {delay}s before retry..."
                        )
                        
                        time.sleep(delay)
                    else:
                        # No more attempts left
                        logger.error(
                            f"All {max_attempts} attempts exhausted for {func.__name__}. "
                            f"Final error: {error_type} - {str(e)}"
                        )
                        raise
            
            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
                
        return wrapper
    return decorator


def _is_retryable_error(error: Exception) -> bool:
    """
    Check if an error is retryable (transient errors).
    
    Returns:
        True if the error should be retried, False otherwise.
    """
    error_type = type(error).__name__
    error_message = str(error).lower()
    
    # Check for specific OpenAI error types
    retryable_errors = [
        'RateLimitError',
        'Timeout',
        'APIError',
        'APIConnectionError',
        'ServiceUnavailableError',
        'InternalServerError'
    ]
    
    if error_type in retryable_errors:
        return True
    
    # Check for timeout-related errors by message
    if 'timeout' in error_message or 'timed out' in error_message:
        return True
    
    # Check for rate limit by status code in message
    if '429' in error_message or 'rate limit' in error_message:
        return True
    
    # Check for connection errors
    if 'connection' in error_message and ('failed' in error_message or 'error' in error_message):
        return True
    
    return False


def _is_permanent_error(error: Exception) -> bool:
    """
    Check if an error is permanent (should not be retried).
    
    Returns:
        True if the error is permanent, False otherwise.
    """
    error_type = type(error).__name__
    error_message = str(error).lower()
    
    # Check for specific OpenAI error types that should not be retried
    permanent_errors = [
        'AuthenticationError',
        'InvalidRequestError',
        'PermissionDeniedError',
        'NotFoundError'
    ]
    
    if error_type in permanent_errors:
        return True
    
    # Check for authentication errors by status code in message
    if '401' in error_message or 'unauthorized' in error_message or 'authentication' in error_message:
        return True
    
    # Check for bad request errors by status code in message
    if '400' in error_message or 'bad request' in error_message or 'invalid request' in error_message:
        return True
    
    # Check for permission errors
    if '403' in error_message or 'forbidden' in error_message or 'permission denied' in error_message:
        return True
    
    return False
