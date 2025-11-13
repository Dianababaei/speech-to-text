# Database Models and Migrations

This document provides information about the database models and how to run migrations.

## Database Schema

### Transcription Table

Stores audio transcription data with multi-language support (including Persian/Farsi).

**Columns:**
- `id`: UUID primary key
- `audio_file_path`: VARCHAR(500) - relative path to audio file
- `transcription_text`: TEXT - transcribed content (UTF-8, supports all languages)
- `language_detected`: VARCHAR(10) - ISO language code (e.g., 'en', 'fa', 'multi')
- `duration`: FLOAT - audio duration in seconds
- `status`: ENUM('pending', 'completed', 'failed')
- `created_at`: TIMESTAMP WITH TIME ZONE
- `updated_at`: TIMESTAMP WITH TIME ZONE

**Indexes:**
- `idx_transcription_status` on `status`
- `idx_transcription_created_at` on `created_at`
- `idx_transcription_text` (GIN index with pg_trgm) for full-text search

### Lexicon Table

Stores domain-specific terms and their corrections for post-processing.

**Columns:**
- `id`: INTEGER primary key (auto-increment)
- `term`: VARCHAR(255) - medical/domain-specific term
- `correction`: VARCHAR(255) - corrected spelling
- `frequency`: INTEGER - usage count (default: 0)
- `source`: VARCHAR(50) - origin: 'fda', 'rxnorm', 'who', 'user_feedback'

**Constraints:**
- Unique constraint on `(term, source)` to prevent duplicates

**Indexes:**
- `idx_lexicon_term` on `term` for fast lookups

## Setup

### Prerequisites

1. Install required packages:
```bash
pip install sqlalchemy psycopg2-binary alembic
```

2. Set up PostgreSQL database with UTF-8 encoding:
```sql
CREATE DATABASE transcription_db WITH ENCODING 'UTF8';
```

3. Enable the pg_trgm extension for full-text search:
```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

### Configuration

Edit the database URL in `alembic.ini` or set the `DATABASE_URL` environment variable:

```bash
export DATABASE_URL="postgresql://username:password@localhost/transcription_db?client_encoding=utf8"
```

Or modify `src/database.py` to set the default connection string.

## Running Migrations

### Apply Migrations (Upgrade)

To create the tables and indexes:

```bash
alembic upgrade head
```

This will:
- Create the `transcriptions` table with all columns and indexes
- Create the `lexicon` table with all columns and indexes
- Create the `transcription_status` enum type
- Enable the `pg_trgm` extension for full-text search

### Rollback Migrations (Downgrade)

To remove all tables:

```bash
alembic downgrade base
```

### Check Migration Status

```bash
alembic current
```

### View Migration History

```bash
alembic history
```

## Testing UTF-8 Support

After running migrations, you can test Persian/multi-language support:

```python
from src.database import SessionLocal, engine
from src.models import Transcription, Lexicon
from src.models.transcription import TranscriptionStatus
import uuid

# Create a session
db = SessionLocal()

# Test Persian text in transcription
transcription = Transcription(
    id=uuid.uuid4(),
    audio_file_path="test/audio_fa.mp3",
    transcription_text="این یک متن فارسی است برای تست",  # Persian text
    language_detected="fa",
    duration=15.5,
    status=TranscriptionStatus.completed
)
db.add(transcription)
db.commit()

# Test Persian term in lexicon
lexicon = Lexicon(
    term="اسپرین",  # Persian: Aspirin
    correction="آسپرین",
    frequency=1,
    source="user_feedback"
)
db.add(lexicon)
db.commit()

print("UTF-8 test successful!")
db.close()
```

## Model Usage Examples

### Creating a Transcription

```python
from src.models import Transcription, TranscriptionStatus
from src.database import SessionLocal
import uuid

db = SessionLocal()

transcription = Transcription(
    id=uuid.uuid4(),
    audio_file_path="uploads/audio_20240101_123456.mp3",
    transcription_text="This is a test transcription",
    language_detected="en",
    duration=120.5,
    status=TranscriptionStatus.completed
)

db.add(transcription)
db.commit()
db.close()
```

### Adding Lexicon Terms

```python
from src.models import Lexicon
from src.database import SessionLocal

db = SessionLocal()

# Add medical term
lexicon = Lexicon(
    term="acetaminophen",
    correction="acetaminophen",
    frequency=0,
    source="fda"
)

db.add(lexicon)
db.commit()
db.close()
```

### Querying Transcriptions

```python
from src.models import Transcription, TranscriptionStatus
from src.database import SessionLocal

db = SessionLocal()

# Get all completed transcriptions
completed = db.query(Transcription).filter(
    Transcription.status == TranscriptionStatus.completed
).all()

# Get transcriptions by language
persian_transcriptions = db.query(Transcription).filter(
    Transcription.language_detected == "fa"
).all()

db.close()
```

## Directory Structure

```
.
├── alembic/
│   ├── versions/
│   │   ├── __init__.py
│   │   └── 001_create_transcription_and_lexicon_tables.py
│   ├── __init__.py
│   ├── env.py
│   └── script.py.mako
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── transcription.py
│   │   └── lexicon.py
│   ├── __init__.py
│   └── database.py
├── alembic.ini
└── README_MIGRATIONS.md
```

## Notes

- The database uses UTF-8 encoding to support Persian and other Unicode characters
- All timestamp fields use `TIMESTAMP WITH TIME ZONE` for proper timezone handling
- The `created_at` field is automatically set on record creation
- The `updated_at` field is automatically updated on record modification
- The GIN index on `transcription_text` requires the `pg_trgm` extension for efficient full-text search
- The migration script automatically enables `pg_trgm` if not already enabled
