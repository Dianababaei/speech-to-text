#!/usr/bin/env python3
"""
Database initialization script.

This script:
1. Tests the database connection
2. Verifies UTF-8 encoding support
3. Runs Alembic migrations to set up the database schema

Usage:
    python init_database.py
"""

import os
import sys
import subprocess


def check_database_url():
    """Check if DATABASE_URL is set."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable is not set")
        print("\nPlease set it using:")
        print('  export DATABASE_URL="postgresql://username:password@localhost:5432/dbname"')
        return False
    
    print(f"✓ DATABASE_URL is set: {database_url[:20]}...")
    return True


def test_connection():
    """Test database connection and UTF-8 encoding."""
    print("\n" + "="*60)
    print("Testing Database Connection")
    print("="*60)
    
    try:
        from src.database import test_connection
        result = test_connection()
        if not result:
            print("\n❌ Database connection test failed")
            return False
        return True
    except Exception as e:
        print(f"\n❌ Error testing connection: {e}")
        return False


def run_migrations():
    """Run Alembic migrations."""
    print("\n" + "="*60)
    print("Running Database Migrations")
    print("="*60)
    
    try:
        # Run alembic upgrade head
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        print("✓ Migrations completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running migrations: {e}")
        print(e.stdout)
        print(e.stderr)
        return False
    except FileNotFoundError:
        print("❌ Alembic is not installed or not in PATH")
        print("Please install it: pip install alembic")
        return False


def show_migration_status():
    """Show current migration status."""
    print("\n" + "="*60)
    print("Migration Status")
    print("="*60)
    
    try:
        result = subprocess.run(
            ["alembic", "current"],
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    except Exception as e:
        print(f"Warning: Could not get migration status: {e}")


def main():
    """Main initialization routine."""
    print("\n" + "="*60)
    print("Database Initialization Script")
    print("="*60)
    
    # Step 1: Check DATABASE_URL
    if not check_database_url():
        sys.exit(1)
    
    # Step 2: Test connection
    if not test_connection():
        print("\n⚠️  Database connection failed. Please check:")
        print("  1. PostgreSQL is running")
        print("  2. DATABASE_URL is correct")
        print("  3. Database exists and credentials are valid")
        sys.exit(1)
    
    # Step 3: Run migrations
    if not run_migrations():
        print("\n⚠️  Migrations failed. Please check the error messages above.")
        sys.exit(1)
    
    # Step 4: Show status
    show_migration_status()
    
    print("\n" + "="*60)
    print("✅ Database Initialization Complete!")
    print("="*60)
    print("\nYour database is ready to use.")
    print("\nNext steps:")
    print("  1. Create your models in src/models/")
    print("  2. Generate migrations: alembic revision --autogenerate -m 'description'")
    print("  3. Apply migrations: alembic upgrade head")
    print("  4. Start your FastAPI application")


if __name__ == "__main__":
    main()
