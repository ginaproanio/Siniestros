#!/usr/bin/env python3
"""
Script to set up database migrations properly by clearing old migration history
and running fresh migrations.
"""
import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

from app.database import engine
import sqlalchemy as sa

def setup_migrations():
    """Clear old migration history and prepare for fresh migration"""
    try:
        print("🧹 Clearing old alembic version table...", flush=True)
        with engine.connect() as conn:
            # Drop the alembic version table if it exists
            conn.execute(sa.text("DROP TABLE IF EXISTS alembic_version CASCADE"))
            conn.commit()
        print("✅ Alembic version table cleared successfully", flush=True)
        return True
    except Exception as e:
        print(f"❌ Error clearing alembic version table: {e}", flush=True)
        return False

if __name__ == "__main__":
    success = setup_migrations()
    sys.exit(0 if success else 1)
