"""initial setup

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Initial setup migration.
    
    This is a placeholder migration that ensures the Alembic versioning system
    is initialized. As models are added to the application, subsequent migrations
    will be auto-generated using:
        alembic revision --autogenerate -m "description"
    
    The database is configured with UTF-8 encoding to support multi-language
    content, especially Persian/Farsi text.
    """
    # Set client encoding to UTF-8 for this migration
    op.execute("SET CLIENT_ENCODING TO 'UTF8'")
    
    # Verify PostgreSQL version and UTF-8 support
    # This doesn't create any tables yet, but ensures the database is properly configured
    pass


def downgrade() -> None:
    """
    Downgrade from initial setup.
    
    Since this is the initial migration with no schema changes,
    there's nothing to downgrade.
    """
    pass
