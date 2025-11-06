"""
Database configuration and models for SkillMatch.AI PostgreSQL implementation
"""
import os
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import JSON, UUID
from datetime import datetime
import uuid

Base = declarative_base()

# Association table for user skills
user_skills = Table(
    'user_skills',
    Base.metadata,
    Column('user_id', String, ForeignKey('user_profiles.user_id')),
    Column('skill_id', Integer, ForeignKey('skills.id'))
)

# Association table for user career goals
user_career_goals = Table(
    'user_career_goals', 
    Base.metadata,
    Column('user_id', String, ForeignKey('user_profiles.user_id')),
    Column('goal_id', Integer, ForeignKey('career_goals.id'))
)

class UserProfile(Base):
    """User profile table"""
    __tablename__ = 'user_profiles'
    
    user_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email_address = Column(String, unique=True)
    title = Column(String)
    location = Column(String)
    bio = Column(Text)
    goals = Column(Text)  # Simple text field for career goals
    summary = Column(Text)
    experience_level = Column(String)  # entry, mid, senior
    resume_file = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    skills = relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")
    work_experience = relationship("WorkExperience", back_populates="user", cascade="all, delete-orphan")
    education = relationship("Education", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    career_goals = relationship("CareerGoal", secondary=user_career_goals, back_populates="users")

class Skill(Base):
    """Skills reference table"""
    __tablename__ = 'skills'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    skill_id = Column(String, unique=True, nullable=False)
    skill_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text)
    aliases = Column(JSON)  # Alternative names for the skill
    
    # Relationships
    user_skills = relationship("UserSkill", back_populates="skill")

class UserSkill(Base):
    """User-skill association with proficiency details"""
    __tablename__ = 'user_skills_detail'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('user_profiles.user_id'), nullable=False)
    skill_id = Column(Integer, ForeignKey('skills.id'), nullable=False)
    
    level = Column(String)  # beginner, intermediate, advanced, expert
    years_experience = Column(Float)
    last_used = Column(DateTime)
    verified = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("UserProfile", back_populates="skills")
    skill = relationship("Skill", back_populates="user_skills")

class WorkExperience(Base):
    """Work experience entries"""
    __tablename__ = 'work_experience'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('user_profiles.user_id'), nullable=False)
    
    company = Column(String, nullable=False)
    position = Column(String, nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)  # NULL for current position
    years = Column(Integer)  # Legacy field for existing data
    description = Column(Text)
    employment_status = Column(String)  # employed, unemployed, contract
    key_skills = Column(JSON)  # List of skill names
    achievements = Column(JSON)  # List of achievements
    
    # Relationships
    user = relationship("UserProfile", back_populates="work_experience")

class Education(Base):
    """Education entries"""
    __tablename__ = 'education'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('user_profiles.user_id'), nullable=False)
    
    institution = Column(String, nullable=False)
    degree = Column(String, nullable=False)
    field_of_study = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    graduation_year = Column(Integer)  # Legacy field
    gpa = Column(Float)
    relevant_coursework = Column(JSON)  # List of courses
    
    # Relationships
    user = relationship("UserProfile", back_populates="education")

class UserPreferences(Base):
    """User job preferences"""
    __tablename__ = 'user_preferences'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('user_profiles.user_id'), nullable=False, unique=True)
    
    work_types = Column(JSON)  # full_time, part_time, contract
    work_type = Column(JSON)   # hybrid, remote, onsite (legacy)
    desired_roles = Column(JSON)  # List of desired job titles
    salary_min = Column(Integer)  # Changed from Float to Integer
    salary_max = Column(Integer)  # Changed from Float to Integer
    locations = Column(JSON)  # Preferred locations
    industries = Column(JSON)  # Preferred industries
    company_size = Column(JSON)  # Company size preferences
    remote_preference = Column(String)  # remote, hybrid, onsite
    growth_areas = Column(JSON)  # Skills to develop
    availability = Column(String)  # When can start
    
    # Relationships
    user = relationship("UserProfile", back_populates="preferences")

class CareerGoal(Base):
    """Career goals (can be shared across users)"""
    __tablename__ = 'career_goals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    goal_text = Column(String, nullable=False, unique=True)
    category = Column(String)  # technical, leadership, business
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    users = relationship("UserProfile", secondary=user_career_goals, back_populates="career_goals")

# Database configuration
class DatabaseConfig:
    """Database configuration class"""
    
    def __init__(self):
        self.database_url = self._get_database_url()
        self.engine = create_engine(
            self.database_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            echo=os.getenv('DATABASE_DEBUG', 'false').lower() == 'true'
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    def _get_database_url(self) -> str:
        """Get database URL from environment variables"""
        # Try to get full database URL first
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            return database_url
        
        # Build URL from individual components
        host = os.getenv('DB_HOST', 'localhost')
        port = os.getenv('DB_PORT', '5432')
        database = os.getenv('DB_NAME', 'skillmatch')
        username = os.getenv('DB_USER', 'skillmatch_user')
        password = os.getenv('DB_PASSWORD', 'password')
        
        return f"postgresql://{username}:{password}@{host}:{port}/{database}"
    
    def create_tables(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get database session"""
        session = self.SessionLocal()
        try:
            return session
        except Exception:
            session.close()
            raise

# Global database instance
db_config = DatabaseConfig()

def get_db():
    """Dependency for getting database session"""
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()