"""
Database Configuration and Management
SQLite-only configuration for SkillMatch.AI
"""
import os
import logging
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base class for all models
Base = declarative_base()

class DatabaseConfig:
    """SQLite database configuration and session management"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._setup_database()
    
    def _setup_database(self):
        """Setup SQLite database connection"""
        # Create data directory
        db_dir = Path(__file__).parent.parent / 'data'
        db_dir.mkdir(exist_ok=True)
        
        # SQLite database path
        db_path = db_dir / 'skillsmatch.db'
        database_url = f'sqlite:///{db_path}'
        
        # Create SQLite engine
        self.engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        logger.info(f"SQLite database configured: {database_url}")
    
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