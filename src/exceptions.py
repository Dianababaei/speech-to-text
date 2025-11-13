"""
Custom exception classes for the transcription service.
"""


class TranscriptionNotFoundError(Exception):
    """
    Raised when a transcription with the specified ID is not found in the database.
    """
    def __init__(self, transcription_id: int):
        self.transcription_id = transcription_id
        super().__init__(f"Transcription with ID {transcription_id} not found")


class DatabaseOperationError(Exception):
    """
    Raised when a database operation fails due to constraint violations or other database errors.
    """
    def __init__(self, message: str, original_error: Exception = None):
        self.original_error = original_error
        super().__init__(message)
