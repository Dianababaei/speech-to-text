# Database Setup Guide

This document describes the database integration setup for the speech-to-text FastAPI application.

## Overview

The application uses:
- **PostgreSQL** with UTF-8 encoding for multi-language support (especially Persian/Farsi)
- **SQLAlchemy** as the ORM with connection pooling
- **Alembic** for database migrations

## Configuration

### Environment Variables

Set the `DATABASE_URL` environment variable with your PostgreSQL connection string:

```bash
export DATABASE_URL="postgresql://username:password@localhost:5432/dbname"
```

Example with UTF-8 encoding explicitly specified:
```bash
export DATABASE_URL="postgresql://user:pass@localhost:5432/speech_db?client_encoding=utf8"
```

## Database Components

### 1. `src/database.py`

Contains:
- **SQLAlchemy engine** with UTF-8 encoding and connection pooling
- **Connection pooling** configuration (pool_size=5, max_overflow=10, pool_pre_ping=True)
- **`get_db()` dependency** for FastAPI route injection
- **`Base` declarative class** for all models to inherit from
- **`test_connection()` function** to verify database connectivity and UTF-8 support

#### Connection Pooling

The engine is configured with:
- `pool_size=5`: Maintains 5 persistent connections
- `max_overflow=10`: Allows up to 10 additional connections under load
- `pool_pre_ping=True`: Verifies connections before use (prevents stale connection errors)

#### UTF-8 Encoding

Critical for Persian/Farsi text support:
- `client_encoding='UTF8'` set in connection arguments
- Event listener ensures encoding is set on every connection
- Test function verifies Persian text can be stored and retrieved

### 2. Alembic Migration System

#### Directory Structure

```
alembic/
├── env.py                  # Migration environment configuration
├── script.py.mako         # Template for new migrations
├── README                 # Alembic documentation
└── versions/              # Migration files
    ├── .gitkeep
    └── 001_initial_setup.py
```

#### Configuration Files

- `alembic.ini`: Main Alembic configuration (loads DATABASE_URL from environment)
- `alembic/env.py`: Imports Base from `src.database` for auto-migration detection

## Usage

### Testing Database Connection

Run the database module directly to test connectivity:

```bash
python -m src.database
```

Expected output:
```
✓ Database connection successful
✓ UTF-8 encoding verified (Persian text: سلام دنیا)
```

### Running Migrations

#### Apply all pending migrations:
```bash
alembic upgrade head
```

#### Check current migration version:
```bash
alembic current
```

#### View migration history:
```bash
alembic history
```

#### Create a new migration (after adding/modifying models):
```bash
alembic revision --autogenerate -m "description of changes"
```

#### Rollback one migration:
```bash
alembic downgrade -1
```

### Using in FastAPI Routes

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from src.database import get_db

@app.get("/items")
def get_items(db: Session = Depends(get_db)):
    # db is automatically provided and managed
    items = db.query(Item).all()
    return items
```

The `get_db()` dependency:
- Creates a new session for each request
- Automatically commits on success
- Rolls back on errors
- Always closes the session when done

## Creating Models

Create model classes by inheriting from `Base`:

```python
from sqlalchemy import Column, Integer, String, Text
from src.database import Base

class Transcription(Base):
    __tablename__ = "transcriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    audio_filename = Column(String(255), nullable=False)
    transcript_text = Column(Text, nullable=False)  # Supports Persian/Farsi
    language = Column(String(50))
```

After creating or modifying models:
1. Generate a migration: `alembic revision --autogenerate -m "add transcription model"`
2. Review the generated migration in `alembic/versions/`
3. Apply the migration: `alembic upgrade head`

## Troubleshooting

### Connection Issues

If you see connection errors:
1. Verify DATABASE_URL is set correctly
2. Ensure PostgreSQL is running
3. Check network connectivity and firewall rules
4. Verify credentials and database name

### UTF-8 Encoding Issues

If Persian/Farsi text appears corrupted:
1. Verify database was created with UTF-8 encoding:
   ```sql
   CREATE DATABASE dbname ENCODING 'UTF8';
   ```
2. Run the test function: `python -m src.database`
3. Check PostgreSQL client_encoding: `SHOW client_encoding;`

### Migration Issues

If migrations fail:
1. Check `alembic current` to see current state
2. Review the migration file in `alembic/versions/`
3. Check database logs for detailed errors
4. Use `alembic downgrade` to rollback if needed

## Success Criteria Checklist

- [x] Database connection established with UTF-8 encoding
- [x] Connection pooling configured (pool_size=5, max_overflow=10, pool_pre_ping=True)
- [x] Persian/Farsi text support verified
- [x] Alembic initialized and configured
- [x] `get_db()` dependency function provides auto-managed sessions
- [x] Initial migration created and ready to run
- [x] Graceful error handling implemented

## Next Steps

1. Set your DATABASE_URL environment variable
2. Ensure PostgreSQL is running
3. Test the connection: `python -m src.database`
4. Apply migrations: `alembic upgrade head`
5. Start creating your models in the `src/models/` directory
