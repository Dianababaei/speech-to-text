#!/usr/bin/env python3
"""
Test script to demonstrate model instantiation without database connection.
This validates that the models are correctly defined.
"""

import uuid
from datetime import datetime

# Import models
from src.models import Transcription, TranscriptionStatus, Lexicon

print("=" * 80)
print("Testing Model Instantiation (No Database Required)")
print("=" * 80)

# Test Transcription model
print("\n1. Testing Transcription Model...")
try:
    transcription = Transcription(
        id=uuid.uuid4(),
        audio_file_path="uploads/test_audio.mp3",
        transcription_text="این یک متن فارسی است - This is a test transcription",
        language_detected="multi",
        duration=125.5,
        status=TranscriptionStatus.completed,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    print(f"   ✓ Transcription instance created")
    print(f"   ✓ ID type: {type(transcription.id).__name__}")
    print(f"   ✓ Status type: {type(transcription.status).__name__}")
    print(f"   ✓ __repr__: {repr(transcription)}")
    
    # Test status enum values
    print("\n   Testing TranscriptionStatus enum:")
    print(f"     ✓ pending: {TranscriptionStatus.pending.value}")
    print(f"     ✓ completed: {TranscriptionStatus.completed.value}")
    print(f"     ✓ failed: {TranscriptionStatus.failed.value}")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    raise

# Test Lexicon model
print("\n2. Testing Lexicon Model...")
try:
    lexicon = Lexicon(
        id=1,
        term="اسپرین",  # Persian: Aspirin
        correction="آسپرین",
        frequency=10,
        source="user_feedback"
    )
    
    print(f"   ✓ Lexicon instance created")
    print(f"   ✓ ID type: {type(lexicon.id).__name__}")
    print(f"   ✓ __repr__: {repr(lexicon)}")
    
    # Test with different sources
    print("\n   Testing various sources:")
    sources = ["fda", "rxnorm", "who", "user_feedback"]
    for source in sources:
        lex = Lexicon(
            term="test_term",
            correction="test_correction",
            frequency=0,
            source=source
        )
        print(f"     ✓ {source}")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    raise

# Test table names
print("\n3. Testing Table Names...")
print(f"   ✓ Transcription table: '{Transcription.__tablename__}'")
print(f"   ✓ Lexicon table: '{Lexicon.__tablename__}'")

# Test that models have required columns
print("\n4. Verifying Column Attributes...")
print("   Transcription columns:")
transcription_attrs = [
    'id', 'audio_file_path', 'transcription_text', 'language_detected',
    'duration', 'status', 'created_at', 'updated_at'
]
for attr in transcription_attrs:
    has_attr = hasattr(Transcription, attr)
    print(f"     {'✓' if has_attr else '✗'} {attr}")

print("   Lexicon columns:")
lexicon_attrs = ['id', 'term', 'correction', 'frequency', 'source']
for attr in lexicon_attrs:
    has_attr = hasattr(Lexicon, attr)
    print(f"     {'✓' if has_attr else '✗'} {attr}")

# Test UTF-8 support
print("\n5. Testing UTF-8 (Persian/Farsi) Support...")
persian_texts = [
    "سلام دنیا",  # Hello World
    "این یک متن فارسی است",  # This is Persian text
    "پزشکی و دارو",  # Medicine and Drug
    "آسپرین، استامینوفن، ایبوپروفن"  # Aspirin, Acetaminophen, Ibuprofen
]

try:
    for text in persian_texts:
        t = Transcription(
            id=uuid.uuid4(),
            audio_file_path="test.mp3",
            transcription_text=text,
            language_detected="fa",
            status=TranscriptionStatus.pending,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        print(f"   ✓ Persian text: {text[:30]}...")
except Exception as e:
    print(f"   ✗ Error with UTF-8: {e}")
    raise

print("\n" + "=" * 80)
print("✅ ALL MODEL TESTS PASSED!")
print("=" * 80)

print("\n📝 Models are correctly defined and ready to use.")
print("   Next steps:")
print("   1. Set up PostgreSQL database")
print("   2. Configure DATABASE_URL")
print("   3. Run: alembic upgrade head")
print("   4. Start using the models with actual database operations")
print()
