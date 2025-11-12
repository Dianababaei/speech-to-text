"""
Database configuration and session management for the FastAPI application.

This module provides:
- SQLAlchemy engine with UTF-8 encoding for multi-language support (especially Persian/Farsi)
- Connection pooling for efficient database access
- Session management with FastAPI dependency injection
- Base declarative class for all models
"""

import os
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session


# Get database URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/dbname")

# Configure SQLAlchemy engine with UTF-8 encoding and connection pooling
engine = create_engine(
    DATABASE_URL,
    # Connection pooling configuration
    pool_size=5,  # Number of connections to maintain in the pool
    max_overflow=10,  # Maximum number of connections that can be created beyond pool_size
    pool_pre_ping=True,  # Verify connections before using them (prevents stale connections)
    # UTF-8 encoding configuration for multi-language support
    connect_args={
        "client_encoding": "UTF8",
        "options": "-c timezone=utc"
    },
    # Echo SQL statements for debugging (set to False in production)
    echo=False,
)


# Event listener to ensure UTF-8 encoding on every connection
@event.listens_for(Engine, "connect")
def set_client_encoding(dbapi_conn, connection_record):
    """
    Ensure UTF-8 encoding is set for every database connection.
    This is critical for Persian/Farsi text support.
    """
    cursor = dbapi_conn.cursor()
    cursor.execute("SET CLIENT_ENCODING TO 'UTF8'")
    cursor.close()


# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create Base class for all models to inherit from
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency function that provides a database session.
    
    This function:
    - Creates a new database session for each request
    - Yields the session for use in route handlers
    - Automatically commits changes on success
    - Rolls back changes on error
    - Always closes the session when done
    
    Usage in FastAPI routes:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def test_connection() -> bool:
    """
    Test the database connection and UTF-8 encoding support.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        with engine.connect() as connection:
            # Test basic connection
            result = connection.execute("SELECT 1")
            result.fetchone()
            
            # Test UTF-8 encoding with Persian text
            persian_test = "سلام دنیا"  # "Hello World" in Persian/Farsi
            result = connection.execute(
                "SELECT :text::text as test_text",
                {"text": persian_test}
            )
            retrieved_text = result.fetchone()[0]
            
            # Verify the text was stored and retrieved correctly
            if retrieved_text != persian_test:
                print(f"UTF-8 encoding test failed: expected '{persian_test}', got '{retrieved_text}'")
                return False
            
            print("✓ Database connection successful")
            print(f"✓ UTF-8 encoding verified (Persian text: {retrieved_text})")
            return True
            
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test the database connection when running this module directly
    test_connection()
