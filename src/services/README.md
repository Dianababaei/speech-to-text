# OpenAI Service with Retry Logic

## Overview

The OpenAI service provides audio transcription using the Whisper API with built-in retry logic and exponential backoff for handling transient errors.

## Features

### Automatic Retry with Exponential Backoff

- **Maximum Attempts**: 3 total attempts (initial + 2 retries)
- **Backoff Delays**: 1s, 2s, 4s between retries
- **Smart Error Detection**: Automatically distinguishes between transient and permanent errors

### Error Handling

#### Retryable Errors (Transient)
The following errors will be automatically retried:
- **RateLimitError (429)**: API rate limit exceeded
- **Timeout**: Request timeout
- **APIError**: General API errors
- **APIConnectionError**: Network/connection failures
- **ServiceUnavailableError**: Service temporarily unavailable
- **InternalServerError**: Server-side errors

#### Non-Retryable Errors (Permanent)
The following errors will fail immediately without retries:
- **AuthenticationError (401)**: Invalid API key
- **InvalidRequestError (400)**: Invalid request parameters
- **PermissionDeniedError (403)**: Insufficient permissions
- **NotFoundError (404)**: Resource not found

### Logging

Each retry attempt is logged with:
- Attempt number (e.g., "Retry attempt 1/3")
- Error type and message
- File being processed (if available)
- Wait time before next retry

## Usage

### Using the Service Class

```python
from src.services.openai_service import OpenAIService

# Initialize the service
service = OpenAIService(api_key="your-api-key")

# Transcribe audio (with automatic retry)
try:
    transcript = service.transcribe_audio(
        audio_file="path/to/audio.mp3",
        language="en",
        prompt="Medical transcription"
    )
    print(transcript)
except Exception as e:
    print(f"Transcription failed after all retries: {e}")
```

### Using the Convenience Function

```python
from src.services.openai_service import transcribe_audio

# Direct transcription (with automatic retry)
try:
    transcript = transcribe_audio(
        audio_file="path/to/audio.mp3",
        api_key="your-api-key",
        language="en"
    )
    print(transcript)
except Exception as e:
    print(f"Transcription failed: {e}")
```

## Retry Behavior Examples

### Example 1: Rate Limit Error (429)
```
[WARNING] Retry attempt 1/3 for transcribe_audio: RateLimitError - Rate limit exceeded (file: audio.mp3). Waiting 1s before retry...
[WARNING] Retry attempt 2/3 for transcribe_audio: RateLimitError - Rate limit exceeded (file: audio.mp3). Waiting 2s before retry...
[INFO] Successfully executed transcribe_audio on attempt 3/3
```

### Example 2: Authentication Error (401)
```
[ERROR] Permanent error in transcribe_audio: AuthenticationError - Invalid API key. Not retrying.
```

### Example 3: Successful First Attempt
```
[INFO] Starting transcription for file: audio.mp3
[INFO] Successfully transcribed file: audio.mp3 (1523 characters)
```

## Architecture

The retry logic is implemented as a decorator (`@retry_with_exponential_backoff`) that can be applied to any function. This makes it:
- **Reusable**: Can be applied to other API calls
- **Maintainable**: Retry logic is centralized in one place
- **Testable**: Easy to test retry behavior independently

## Configuration

The retry decorator can be customized:

```python
from src.utils.retry import retry_with_exponential_backoff

@retry_with_exponential_backoff(
    max_attempts=5,           # Override default of 3
    backoff_delays=[2, 4, 8, 16]  # Override default delays
)
def my_function():
    # Your code here
    pass
```

## Dependencies

- `openai` - OpenAI Python SDK
- Python standard library: `time`, `logging`, `functools`, `pathlib`, `typing`
