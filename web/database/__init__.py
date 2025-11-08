"""
Database initialization and setup utilities
"""
import os
from pathlib import Path
from .db_config import db_config, Base
from .services import JSONToPostgreSQLMigrator

def init_database():
    """Initialize database tables"""
    print("🗄️  Initializing PostgreSQL database...")
    try:
        # Create all tables
        db_config.create_tables()
        print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        return False

def migrate_json_profiles():
    """Migrate existing JSON profiles to PostgreSQL"""
    print("📁 Migrating JSON profiles to PostgreSQL...")
    
    # Get profiles directory
    profiles_dir = Path(__file__).parent.parent.parent / "profiles"
    
    if not profiles_dir.exists():
        print("❌ Profiles directory not found")
        return False
    
    try:
        # Get database session
        with db_config.get_session() as db:
            migrator = JSONToPostgreSQLMigrator(db)
            stats = migrator.migrate_all_profiles(str(profiles_dir))
            
            print(f"✅ Migration completed!")
            print(f"   Success: {stats['success']} profiles")
            print(f"   Failed: {stats['failed']} profiles")
            
            return stats['failed'] == 0
            
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

def check_database_connection():
    """Check if database connection is working"""
    try:
        with db_config.get_session() as db:
            # Simple query to test connection
            db.execute("SELECT 1")
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def setup_database():
    """Complete database setup process"""
    print("🚀 Setting up SkillMatch.AI PostgreSQL database...")
    
    # Check connection
    if not check_database_connection():
        print("💡 Make sure PostgreSQL is running and environment variables are set:")
        print("   - DATABASE_URL or DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD")
        return False
    
    # Initialize tables
    if not init_database():
        return False
    
    # Migrate existing data
    if not migrate_json_profiles():
        print("⚠️  Migration had issues, but database is ready for new profiles")
    
    print("🎉 Database setup completed successfully!")
    return True

if __name__ == "__main__":
    setup_database()