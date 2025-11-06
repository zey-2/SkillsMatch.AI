#!/usr/bin/env python3
"""
PostgreSQL Database Setup Script for SkillMatch.AI

This script helps you set up PostgreSQL database for SkillMatch.AI profiles.
"""
import os
import sys
import subprocess
from pathlib import Path

def install_requirements():
    """Install PostgreSQL requirements"""
    print("📦 Installing PostgreSQL requirements...")
    
    try:
        # Install requirements
        subprocess.run([
            sys.executable, "-m", "pip", "install",
            "sqlalchemy>=2.0.23",
            "psycopg2-binary>=2.9.7", 
            "alembic>=1.12.0"
        ], check=True)
        
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def check_postgresql():
    """Check if PostgreSQL is running"""
    print("🔍 Checking PostgreSQL connection...")
    
    try:
        # Try to connect to PostgreSQL
        import psycopg2
        
        # Try to connect with default settings
        conn_params = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': 'postgres',  # Connect to default database first
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }
        
        conn = psycopg2.connect(**conn_params)
        conn.close()
        print("✅ PostgreSQL is running and accessible!")
        return True
        
    except ImportError:
        print("❌ psycopg2 not installed. Run this script to install it.")
        return False
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        print("💡 Make sure PostgreSQL is running and credentials are correct")
        return False

def create_database():
    """Create SkillMatch database"""
    print("🗄️  Creating SkillMatch database...")
    
    try:
        import psycopg2
        from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
        
        # Connect to PostgreSQL server
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', '5432'),
            database='postgres',
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', '')
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create database
        db_name = os.getenv('DB_NAME', 'skillmatch')
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        
        if cursor.fetchone() is None:
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"✅ Database '{db_name}' created successfully!")
        else:
            print(f"✅ Database '{db_name}' already exists!")
        
        # Create user if specified
        db_user = os.getenv('DB_USER', 'skillmatch_user')
        if db_user != 'postgres':
            cursor.execute(f"SELECT 1 FROM pg_user WHERE usename = '{db_user}'")
            if cursor.fetchone() is None:
                db_password = os.getenv('DB_PASSWORD', 'secure_password')
                cursor.execute(f"CREATE USER {db_user} WITH PASSWORD '{db_password}'")
                cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user}")
                print(f"✅ User '{db_user}' created and granted permissions!")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error creating database: {e}")
        return False

def setup_database_schema():
    """Set up database tables"""
    print("🏗️  Setting up database schema...")
    
    try:
        # Add web directory to path to import database modules
        web_dir = Path(__file__).parent / "web"
        sys.path.insert(0, str(web_dir))
        
        from database.models import db_config
        db_config.create_tables()
        print("✅ Database schema created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up database schema: {e}")
        return False

def print_configuration():
    """Print current configuration"""
    print("\n📋 Current Configuration:")
    print(f"   Database Host: {os.getenv('DB_HOST', 'localhost')}")
    print(f"   Database Port: {os.getenv('DB_PORT', '5432')}")
    print(f"   Database Name: {os.getenv('DB_NAME', 'skillmatch')}")
    print(f"   Database User: {os.getenv('DB_USER', 'skillmatch_user')}")
    print(f"   Storage Type: {os.getenv('STORAGE_TYPE', 'json')}")

def main():
    """Main setup function"""
    print("🚀 SkillMatch.AI PostgreSQL Setup")
    print("=" * 40)
    
    # Load environment variables
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        from dotenv import load_dotenv
        load_dotenv(env_file)
        print(f"✅ Loaded configuration from {env_file}")
    else:
        print(f"⚠️  No .env file found at {env_file}")
        print("   Using default/system environment variables")
    
    print_configuration()
    
    # Step 1: Install requirements
    if not install_requirements():
        return False
    
    # Step 2: Check PostgreSQL
    if not check_postgresql():
        print("\n💡 PostgreSQL Setup Instructions:")
        print("   1. Install PostgreSQL: https://postgresql.org/download/")
        print("   2. Start PostgreSQL service")
        print("   3. Set environment variables in .env.postgresql")
        return False
    
    # Step 3: Create database
    if not create_database():
        return False
    
    # Step 4: Setup schema
    if not setup_database_schema():
        return False
    
    print("\n🎉 PostgreSQL setup completed successfully!")
    print("\n📝 Next Steps:")
    print("   1. Set STORAGE_TYPE=postgresql in your .env file")
    print("   2. Restart your Flask application")
    print("   3. Your JSON profiles have been migrated to PostgreSQL")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)