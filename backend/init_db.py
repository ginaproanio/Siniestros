#!/usr/bin/env python3
"""
Database initialization script that completely resets the database
and creates all tables from scratch.
"""
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from app.database import engine, Base
import sqlalchemy as sa

def reset_database():
    """Completely reset the database by dropping all tables and recreating them"""
    try:
        print("🔥 RESETTING DATABASE COMPLETELY...", flush=True)

        # Drop all existing tables
        print("🗑️ Dropping all existing tables...", flush=True)
        with engine.connect() as conn:
            # Get all table names
            result = conn.execute(sa.text("""
                SELECT tablename FROM pg_tables
                WHERE schemaname = 'public'
            """))
            tables = [row[0] for row in result]

            if tables:
                # Drop tables with CASCADE to handle foreign keys
                for table in tables:
                    try:
                        conn.execute(sa.text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                        print(f"  ✅ Dropped table: {table}", flush=True)
                    except Exception as e:
                        print(f"  ⚠️ Could not drop {table}: {e}", flush=True)

                conn.commit()
                print(f"✅ Dropped {len(tables)} tables", flush=True)
            else:
                print("ℹ️ No tables to drop", flush=True)

        # Create all tables from SQLAlchemy models
        print("🏗️ Creating all tables from models...", flush=True)
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully", flush=True)

        print("🎉 DATABASE RESET COMPLETE!", flush=True)
        return True

    except Exception as e:
        print(f"❌ DATABASE RESET FAILED: {e}", flush=True)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = reset_database()
    sys.exit(0 if success else 1)
