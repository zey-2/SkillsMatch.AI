"""
Database Configuration and Management
Utilities for database setup and table creation
"""
import os
import logging
from contextlib import contextmanager
from typing import Optional

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base class for all models
Base = declarative_base()

class DatabaseConfig:
    """Database configuration and session management"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._setup_database()
    
    def _setup_database(self):
        """Setup database connection"""
        # Get database URL from environment or build from components
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            # Try to build from individual components
            db_host = os.getenv('DB_HOST')
            db_port = os.getenv('DB_PORT')
            db_name = os.getenv('DB_NAME')
            db_user = os.getenv('DB_USER')
            db_password = os.getenv('DB_PASSWORD')
            
            if all([db_host, db_port, db_name, db_user, db_password]):
                database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
                logger.info(f"Built DATABASE_URL from components: postgresql://{db_user}:***@{db_host}:{db_port}/{db_name}")
            else:
                # Fallback to SQLite for development
                db_path = os.path.join(os.path.dirname(__file__), '..', 'skillsmatch.db')
                database_url = f'sqlite:///{db_path}'
                logger.warning("No DATABASE_URL or DB components found, using SQLite fallback")
        
        # Create engine
        if database_url.startswith('sqlite'):
            self.engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
            )
        else:
            self.engine = create_engine(database_url)
        
        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        logger.info(f"Database configured: {database_url}")
    
    def create_tables(self):
        """Create all database tables"""
        try:
            # Import all models to ensure they're registered
            from .models import UserProfile, Course
            
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
            
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            raise
    
    def get_session(self):
        """Get a database session"""
        return self.SessionLocal()
    
    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

# Global database configuration instance
db_config = DatabaseConfig()

# Convenience functions
def get_db():
    """Get database session (for dependency injection)"""
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all database tables"""
    db_config.create_tables()

def get_engine():
    """Get database engine"""
    return db_config.engine