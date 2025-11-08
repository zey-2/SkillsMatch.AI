"""
Database configuration and models for SkillMatch.AI PostgreSQL implementation
"""
import os
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSON, UUID
from datetime import datetime
import uuid

try:
    from .db_config import Base
except ImportError:
    # Fallback for direct module usage
    from sqlalchemy.ext.declarative import declarative_base
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

class Course(Base):
    """SSG-WSG Courses from Developer Portal API"""
    __tablename__ = 'courses'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(String, unique=True, nullable=False)  # External course ID
    course_reference_number = Column(String, unique=True)  # Course reference number
    title = Column(String, nullable=False)
    description = Column(Text)
    provider = Column(String)  # Training provider
    provider_code = Column(String)
    
    # Course details
    duration = Column(String)  # Course duration
    duration_hours = Column(Float)  # Duration in hours
    course_type = Column(String)  # Online, Classroom, Blended
    delivery_mode = Column(String)  # Full-time, Part-time, etc.
    
    # Skills and categories
    skills_taught = Column(JSON)  # List of skills covered
    skills_framework = Column(JSON)  # Skills framework mapping
    categories = Column(JSON)  # Course categories
    sectors = Column(JSON)  # Industry sectors
    
    # Eligibility and requirements
    eligibility_criteria = Column(Text)
    prerequisites = Column(Text)
    target_audience = Column(String)
    
    # Pricing and funding
    course_fee = Column(Float)
    nett_fee_citizen = Column(Float)  # Fee for citizens after subsidies
    nett_fee_pr = Column(Float)  # Fee for PRs after subsidies
    funding_available = Column(JSON)  # Available funding schemes
    
    # Schedule and location
    schedule = Column(JSON)  # Course schedule information
    locations = Column(JSON)  # Course locations
    next_intake = Column(DateTime)  # Next course intake date
    
    # Quality and accreditation
    rating = Column(Float)
    accreditation = Column(String)
    certification = Column(String)
    
    # API metadata
    api_source = Column(String, default='SSG-WSG')
    external_url = Column(String)  # Link to course details
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Job(Base):
    """Job postings from CSV import"""
    __tablename__ = 'jobs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, unique=True, nullable=False)  # From CSV job_id column
    category = Column(String)  # From CSV category column
    job_title = Column(String, nullable=False)  # From CSV job_title column
    job_description = Column(Text)  # From CSV job_description column
    job_skill_set = Column(JSON)  # From CSV job_skill_set column (parsed as JSON list)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

# Database configuration is now in db_config.py