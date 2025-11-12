"""
Medical Transcription API - FastAPI Application Entry Point

This module initializes the FastAPI application for the medical transcription service.

Architecture Decisions:
-----------------------
1. **Versioned API Pattern**: All routes are prefixed with `/v1/` to support future API
   versions without breaking existing clients. This allows for smooth API evolution.

2. **CORS Configuration**: Permissive CORS settings are used for development to allow
   cross-origin requests from any domain. In production, this should be restricted to
   specific trusted origins (e.g., your frontend domain).

3. **Router Organization**: The application uses FastAPI's APIRouter pattern to organize
   endpoints into logical modules under `src/routers/`. This keeps the codebase modular
   and maintainable as the API grows.

4. **Health Check Endpoint**: Provides a simple way to verify service availability and
   monitor application status. Returns version information and timestamp for debugging.

Usage:
------
To run the application in development mode with auto-reload:
    uvicorn src.main:app --reload

To run in production:
    uvicorn src.main:app --host 0.0.0.0 --port 8000

API Documentation:
------------------
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json
"""

from datetime import datetime
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware


# Initialize FastAPI application with metadata
app = FastAPI(
    title="Medical Transcription API",
    description=(
        "A speech-to-text API for medical transcription using OpenAI's Whisper model. "
        "Supports multi-language audio transcription with code-switching, custom lexicons, "
        "and post-processing for medical terminology."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)


# CORS Configuration
# NOTE: In production, replace allow_origins=["*"] with specific domains
# Example: allow_origins=["https://your-frontend-domain.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)


# Create versioned API router with /v1 prefix
# All endpoints registered to this router will automatically have /v1/ prefix
v1_router = APIRouter(prefix="/v1")


@v1_router.get("/health")
async def health_check():
    """
    Health Check Endpoint
    
    Verifies that the API service is running and responsive.
    Returns the service status, current timestamp, and API version.
    
    Returns:
        dict: Service health status with timestamp and version information
    
    Example Response:
        {
            "status": "healthy",
            "timestamp": "2025-01-18T10:30:00.123456Z",
            "version": "1.0.0"
        }
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": app.version
    }


# Include the versioned router in the main application
app.include_router(v1_router)


# Root endpoint (optional, for quick verification)
@app.get("/")
async def root():
    """
    Root endpoint - redirects users to API documentation
    """
    return {
        "message": "Medical Transcription API",
        "version": app.version,
        "documentation": "/docs",
        "health_check": "/v1/health"
    }
