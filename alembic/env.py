"""
Alembic migration environment configuration.

This module configures Alembic to:
- Load database URL from environment variables
- Import Base from src.database for auto-migration detection
- Support both online and offline migration modes
- Handle UTF-8 encoding for multi-language support
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Add the project root to the Python path so we can import from src
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import Base from src.database to enable auto-migration detection
# This allows Alembic to automatically detect model changes
try:
    from src.database import Base
    target_metadata = Base.metadata
except ImportError as e:
    print(f"Warning: Could not import Base from src.database: {e}")
    print("Auto-generation will not work properly.")
    target_metadata = None

# Get database URL from environment variable
# This overrides any value in alembic.ini for security
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
else:
    print("Warning: DATABASE_URL environment variable not set.")
    print("Please set DATABASE_URL to your PostgreSQL connection string.")

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well. By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        # Ensure UTF-8 encoding for migrations
        render_as_batch=False,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    
    # Get the configuration section
    configuration = config.get_section(config.config_ini_section)
    if configuration is None:
        configuration = {}
    
    # Override with DATABASE_URL from environment if available
    if DATABASE_URL:
        configuration["sqlalchemy.url"] = DATABASE_URL
    
    # Create engine with UTF-8 encoding support
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args={
            "client_encoding": "UTF8",
            "options": "-c timezone=utc"
        },
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # Enable detailed comparison for auto-generation
            compare_type=True,
            compare_server_default=True,
            # Render item_attach_map=... in inline form
            render_item=None,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
