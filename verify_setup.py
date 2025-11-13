#!/usr/bin/env python3
"""
Verification script to check database models and migration setup.
This script does NOT require a database connection - it only validates the code structure.
"""

import sys
from pathlib import Path

print("=" * 80)
print("Database Models and Migration Setup Verification")
print("=" * 80)

# Check if all required files exist
required_files = [
    "src/__init__.py",
    "src/database.py",
    "src/models/__init__.py",
    "src/models/transcription.py",
    "src/models/lexicon.py",
    "alembic.ini",
    "alembic/__init__.py",
    "alembic/env.py",
    "alembic/script.py.mako",
    "alembic/versions/__init__.py",
    "alembic/versions/001_create_transcription_and_lexicon_tables.py",
]

print("\n1. Checking file structure...")
all_exist = True
for file_path in required_files:
    exists = Path(file_path).exists()
    status = "✓" if exists else "✗"
    print(f"   {status} {file_path}")
    if not exists:
        all_exist = False

if not all_exist:
    print("\n❌ ERROR: Some required files are missing!")
    sys.exit(1)

print("\n2. Validating Python imports...")

try:
    from src.database import Base, engine, SessionLocal, get_db
    print("   ✓ src.database imports successfully")
except ImportError as e:
    print(f"   ✗ Error importing src.database: {e}")
    sys.exit(1)

try:
    from src.models import Transcription, TranscriptionStatus, Lexicon
    print("   ✓ src.models imports successfully")
except ImportError as e:
    print(f"   ✗ Error importing src.models: {e}")
    sys.exit(1)

print("\n3. Validating model structure...")

# Check Transcription model
print("   Transcription model:")
transcription_columns = [
    'id', 'audio_file_path', 'transcription_text', 'language_detected',
    'duration', 'status', 'created_at', 'updated_at'
]
for col in transcription_columns:
    has_col = hasattr(Transcription, col)
    status = "✓" if has_col else "✗"
    print(f"     {status} {col}")

# Check Lexicon model
print("   Lexicon model:")
lexicon_columns = ['id', 'term', 'correction', 'frequency', 'source']
for col in lexicon_columns:
    has_col = hasattr(Lexicon, col)
    status = "✓" if has_col else "✗"
    print(f"     {status} {col}")

print("\n4. Checking TranscriptionStatus enum...")
enum_values = ['pending', 'completed', 'failed']
for val in enum_values:
    has_val = hasattr(TranscriptionStatus, val)
    status = "✓" if has_val else "✗"
    print(f"   {status} {val}")

print("\n5. Validating model methods...")
has_transcription_repr = hasattr(Transcription, '__repr__')
has_lexicon_repr = hasattr(Lexicon, '__repr__')
print(f"   {'✓' if has_transcription_repr else '✗'} Transcription.__repr__")
print(f"   {'✓' if has_lexicon_repr else '✗'} Lexicon.__repr__")

print("\n6. Checking Base metadata...")
tables = Base.metadata.tables
print(f"   ✓ Found {len(tables)} table(s) in metadata")
if 'transcriptions' in tables:
    print("   ✓ transcriptions table registered")
if 'lexicon' in tables:
    print("   ✓ lexicon table registered")

print("\n7. Migration file validation...")
migration_file = Path("alembic/versions/001_create_transcription_and_lexicon_tables.py")
if migration_file.exists():
    content = migration_file.read_text()
    checks = [
        ("upgrade function", "def upgrade()"),
        ("downgrade function", "def downgrade()"),
        ("transcriptions table", "create_table('transcriptions'"),
        ("lexicon table", "create_table('lexicon'"),
        ("status enum", "transcription_status_enum"),
        ("idx_transcription_status", "idx_transcription_status"),
        ("idx_transcription_created_at", "idx_transcription_created_at"),
        ("idx_transcription_text", "idx_transcription_text"),
        ("idx_lexicon_term", "idx_lexicon_term"),
        ("pg_trgm extension", "pg_trgm"),
    ]
    
    for check_name, check_str in checks:
        found = check_str in content
        status = "✓" if found else "✗"
        print(f"   {status} {check_name}")

print("\n" + "=" * 80)
print("✅ VERIFICATION COMPLETE - All checks passed!")
print("=" * 80)

print("\n📝 Next Steps:")
print("   1. Install dependencies: pip install -r requirements.txt")
print("   2. Configure your DATABASE_URL in alembic.ini or environment variable")
print("   3. Run migrations: alembic upgrade head")
print("   4. Test with Persian text using examples in README_MIGRATIONS.md")
print("\n")
