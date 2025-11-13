"""create_transcription_and_lexicon_tables

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create transcription_status enum type
    transcription_status_enum = postgresql.ENUM(
        'pending', 'completed', 'failed',
        name='transcription_status',
        create_type=True
    )
    transcription_status_enum.create(op.get_bind(), checkfirst=True)
    
    # Create transcriptions table
    op.create_table(
        'transcriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('audio_file_path', sa.String(length=500), nullable=False),
        sa.Column('transcription_text', sa.Text(), nullable=True),
        sa.Column('language_detected', sa.String(length=10), nullable=True),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column('status', transcription_status_enum, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('id')
    )
    
    # Create indexes for transcriptions table
    op.create_index('idx_transcription_status', 'transcriptions', ['status'], unique=False)
    op.create_index('idx_transcription_created_at', 'transcriptions', ['created_at'], unique=False)
    
    # Create GIN index for full-text search on transcription_text (requires pg_trgm extension)
    # Note: This requires the pg_trgm extension to be enabled in PostgreSQL
    # Run: CREATE EXTENSION IF NOT EXISTS pg_trgm;
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm;')
    op.create_index(
        'idx_transcription_text',
        'transcriptions',
        ['transcription_text'],
        unique=False,
        postgresql_using='gin',
        postgresql_ops={'transcription_text': 'gin_trgm_ops'}
    )
    
    # Create lexicon table
    op.create_table(
        'lexicon',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('term', sa.String(length=255), nullable=False),
        sa.Column('correction', sa.String(length=255), nullable=False),
        sa.Column('frequency', sa.Integer(), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('term', 'source', name='uq_lexicon_term_source')
    )
    
    # Create index for lexicon table
    op.create_index('idx_lexicon_term', 'lexicon', ['term'], unique=False)


def downgrade() -> None:
    # Drop lexicon table and its indexes
    op.drop_index('idx_lexicon_term', table_name='lexicon')
    op.drop_table('lexicon')
    
    # Drop transcriptions table and its indexes
    op.drop_index('idx_transcription_text', table_name='transcriptions', postgresql_using='gin')
    op.drop_index('idx_transcription_created_at', table_name='transcriptions')
    op.drop_index('idx_transcription_status', table_name='transcriptions')
    op.drop_table('transcriptions')
    
    # Drop enum type
    transcription_status_enum = postgresql.ENUM(
        'pending', 'completed', 'failed',
        name='transcription_status'
    )
    transcription_status_enum.drop(op.get_bind(), checkfirst=True)
