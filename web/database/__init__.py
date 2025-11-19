"""
Database initialization and setup utilities for SQLite
"""
import os
from pathlib import Path
from .db_config import db_config, Base

def init_database():
    """Initialize database tables"""
    print("🗄️  Initializing SQLite database...")
    try:
        # Create all tables
        db_config.create_tables()
        print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False

def check_database_connection():
    """Check if database connection is working"""
    try:
        from sqlalchemy import text
        with db_config.session_scope() as db:
            # Simple query to test connection
            db.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def setup_database():
    """Complete database setup process"""
    print("🚀 Setting up SkillMatch.AI SQLite database...")
    
    # Check connection
    if not check_database_connection():
        print("❌ SQLite database setup failed")
        return False
    
    # Initialize tables
    if not init_database():
        return False
    
    print("🎉 SQLite database setup completed successfully!")
    return True

if __name__ == "__main__":
    setup_database()