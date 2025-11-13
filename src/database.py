"""
Database connection and session management for the transcription service.
"""
import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/transcription_db"
)

# Create engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=10,
    max_overflow=20,
    echo=False  # Set to True for SQL query debugging
)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function that provides a database session.
    
    This function is designed to be used with FastAPI's Depends() for dependency injection.
    It creates a new database session for each request and ensures proper cleanup.
    
    Yields:
        Session: SQLAlchemy database session
        
    Example:
        ```python
        @app.get("/transcriptions/{id}")
        def get_transcription(id: int, db: Session = Depends(get_db)):
            service = TranscriptionService(db)
            return service.get_transcription_by_id(id)
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Create all database tables defined in the models.
    
    This function should be called on application startup to ensure
    all tables exist before the service starts handling requests.
    """
    from src.models import Base
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Drop all database tables.
    
    WARNING: This will delete all data. Use only for testing or development.
    """
    from src.models import Base
    Base.metadata.drop_all(bind=engine)
