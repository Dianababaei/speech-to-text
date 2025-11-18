from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# Database connection URL - should be configured via environment variables
DATABASE_URL = "sqlite:///./transcriptions.db"  # Example SQLite URL

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI to get database session.
    
    Yields:
        Database session that will be closed after request completes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
