"""
Database configuration and SQLAlchemy setup
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL - can be overridden by environment variable
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://localhost/transcription_db?client_encoding=utf8"
)

# Create engine with UTF-8 encoding
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to False in production
    pool_pre_ping=True,  # Verify connections before using
    connect_args={
        "client_encoding": "utf8"
    }
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
