import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

router = APIRouter()

# Configuration
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB in bytes
ALLOWED_MIME_TYPES = {
    "audio/wav",
    "audio/mpeg",
    "audio/mp4",
    "audio/x-m4a"
}
ALLOWED_EXTENSIONS = {".wav", ".mp3", ".m4a"}
TEMP_STORAGE_DIR = Path("/tmp/transcriptions")

# Ensure temporary storage directory exists
TEMP_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def validate_file_extension(filename: str) -> Optional[str]:
    """
    Validate file extension and return it in lowercase.
    
    Args:
        filename: Name of the uploaded file
        
    Returns:
        Lowercase extension with dot (e.g., '.mp3') or None if invalid
    """
    if not filename:
        return None
    
    ext = Path(filename).suffix.lower()
    if ext in ALLOWED_EXTENSIONS:
        return ext
    return None


def validate_mime_type(content_type: str) -> bool:
    """
    Validate MIME type of uploaded file.
    
    Args:
        content_type: MIME type from uploaded file
        
    Returns:
        True if valid, False otherwise
    """
    return content_type in ALLOWED_MIME_TYPES


async def validate_file_size(file: UploadFile) -> int:
    """
    Validate file size by reading it.
    
    Args:
        file: Uploaded file object
        
    Returns:
        File size in bytes
        
    Raises:
        HTTPException: If file exceeds maximum size
    """
    # Read file in chunks to check size
    size = 0
    chunk_size = 1024 * 1024  # 1MB chunks
    
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        size += len(chunk)
        if size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File size exceeds 50MB limit"
            )
    
    # Reset file pointer to beginning for later processing
    await file.seek(0)
    return size


@router.post("/transcribe")
async def transcribe_audio(
    audio: Optional[UploadFile] = File(None),
    file: Optional[UploadFile] = File(None)
):
    """
    Upload an audio file for transcription.
    
    Accepts audio files in WAV, MP3, or M4A format up to 50MB.
    Returns a job ID for tracking the transcription.
    
    Args:
        audio: Audio file uploaded with field name "audio"
        file: Audio file uploaded with field name "file"
        
    Returns:
        JSON response with job_id, status, and created_at timestamp
        
    Raises:
        HTTPException: For missing file, invalid format, or size exceeded
    """
    # Check if file was provided (accept either "audio" or "file" field name)
    upload_file = audio or file
    
    if not upload_file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided. Please upload a file using 'audio' or 'file' field name."
        )
    
    # Validate file has a filename
    if not upload_file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must have a filename"
        )
    
    # Validate file extension
    file_ext = validate_file_extension(upload_file.filename)
    if not file_ext:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed extensions: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validate MIME type
    if not validate_mime_type(upload_file.content_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid MIME type '{upload_file.content_type}'. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}"
        )
    
    # Validate file size
    try:
        await validate_file_size(upload_file)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading file: {str(e)}"
        )
    
    # Generate unique job ID
    job_id = str(uuid.uuid4())
    
    # Save file to temporary storage with unique filename
    temp_file_path = TEMP_STORAGE_DIR / f"{job_id}{file_ext}"
    
    try:
        # Write file to disk
        with open(temp_file_path, "wb") as f:
            # Read and write in chunks to handle large files
            while True:
                chunk = await upload_file.read(1024 * 1024)  # 1MB chunks
                if not chunk:
                    break
                f.write(chunk)
    except Exception as e:
        # Clean up partial file if write failed
        if temp_file_path.exists():
            temp_file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # Generate timestamp
    created_at = datetime.utcnow().isoformat() + "Z"
    
    # Return response
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "job_id": job_id,
            "status": "processing",
            "created_at": created_at
        }
    )
