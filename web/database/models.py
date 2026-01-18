"""
Database configuration and models for SkillMatch.AI SQLite implementation
"""

import os
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    DateTime,
    Text,
    ForeignKey,
    Table,
    JSON,
    Index,
)
from sqlalchemy.orm import relationship
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
    "user_skills",
    Base.metadata,
    Column("user_id", String, ForeignKey("user_profiles.user_id")),
    Column("skill_id", Integer, ForeignKey("skills.id")),
)

# Association table for user career goals
user_career_goals = Table(
    "user_career_goals",
    Base.metadata,
    Column("user_id", String, ForeignKey("user_profiles.user_id")),
    Column("goal_id", Integer, ForeignKey("career_goals.id")),
)


class UserProfile(Base):
    """User profile table"""

    __tablename__ = "user_profiles"

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
    skills = relationship(
        "UserSkill", back_populates="user", cascade="all, delete-orphan"
    )
    work_experience = relationship(
        "WorkExperience", back_populates="user", cascade="all, delete-orphan"
    )
    education = relationship(
        "Education", back_populates="user", cascade="all, delete-orphan"
    )
    preferences = relationship(
        "UserPreferences",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    career_goals = relationship(
        "CareerGoal", secondary=user_career_goals, back_populates="users"
    )

    # Indexes for performance optimization
    __table_args__ = (
        Index("idx_user_profiles_created_at", "created_at"),
        Index("idx_user_profiles_experience_level", "experience_level"),
        Index("idx_user_profiles_location", "location"),
        Index("idx_user_profiles_is_active", "is_active"),
        Index("idx_user_profiles_email", "email_address"),
    )


class Skill(Base):
    """Skills reference table"""

    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, autoincrement=True)
    skill_id = Column(String, unique=True, nullable=False)
    skill_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text)
    aliases = Column(JSON)  # Alternative names for the skill

    # Relationships
    user_skills = relationship("UserSkill", back_populates="skill")

    # Indexes for performance optimization
    __table_args__ = (
        Index("idx_skills_name", "skill_name"),
        Index("idx_skills_category", "category"),
    )


class UserSkill(Base):
    """User-skill association with proficiency details"""

    __tablename__ = "user_skills_detail"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("user_profiles.user_id"), nullable=False)
    skill_id = Column(Integer, ForeignKey("skills.id"), nullable=False)

    level = Column(String)  # beginner, intermediate, advanced, expert
    years_experience = Column(Float)
    last_used = Column(DateTime)
    verified = Column(Boolean, default=False)

    # Relationships
    user = relationship("UserProfile", back_populates="skills")
    skill = relationship("Skill", back_populates="user_skills")


class WorkExperience(Base):
    """Work experience entries"""

    __tablename__ = "work_experience"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("user_profiles.user_id"), nullable=False)

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

    __tablename__ = "education"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("user_profiles.user_id"), nullable=False)

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

    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        String, ForeignKey("user_profiles.user_id"), nullable=False, unique=True
    )

    work_types = Column(JSON)  # full_time, part_time, contract
    work_type = Column(JSON)  # hybrid, remote, onsite (legacy)
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

    __tablename__ = "career_goals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    goal_text = Column(String, nullable=False, unique=True)
    category = Column(String)  # technical, leadership, business
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    users = relationship(
        "UserProfile", secondary=user_career_goals, back_populates="career_goals"
    )


class Course(Base):
    """SSG-WSG Courses from Developer Portal API"""

    __tablename__ = "courses"

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
    api_source = Column(String, default="SSG-WSG")
    external_url = Column(String)  # Link to course details
    last_updated = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class Job(Base):
    """Job model for storing job opportunities from FindSGJobs API"""

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(
        String, nullable=False, unique=True
    )  # From API job.id or unique identifier
    title = Column(String, nullable=False)  # From API job.Title
    company_name = Column(String)  # From API company.CompanyName
    company_sid = Column(String)  # From API job.company_sid
    activation_date = Column(DateTime)  # From API job.activation_date
    expiration_date = Column(DateTime)  # From API job.expiration_date
    updated_at = Column(DateTime)  # From API job.updated_at
    keywords = Column(Text)  # From API job.keywords
    simple_keywords = Column(Text)  # From API job.simple_keywords
    job_description = Column(Text)  # From API job.JobDescription

    # Job details
    position_level = Column(String)  # From API job.id_Job_PositionLevel.caption
    min_years_experience = Column(
        String
    )  # From API job.MinimumYearsofExperience.caption
    min_education_level = Column(String)  # From API job.MinimumEducationLevel.caption
    no_of_vacancies = Column(Integer)  # From API job.id_Job_Noofvacancies
    min_salary = Column(Integer)  # From API job.id_Job_Salary
    max_salary = Column(Integer)  # From API job.id_Job_MaxSalary
    salary_interval = Column(String)  # From API job.id_Job_Interval.caption
    currency = Column(String)  # From API job.id_Job_Currency.caption
    employment_type = Column(JSON)  # From API job.EmploymentType (array)
    work_arrangement = Column(String)  # From API job.id_Job_WorkArrangement.caption
    nearest_mrt_station = Column(JSON)  # From API job.id_Job_NearestMRTStation (array)
    timing_shift = Column(JSON)  # From API job.id_Job_TimingShift (array)

    # Job categories
    job_category = Column(JSON)  # From API job.JobCategory (array)

    # Company details
    contact_name = Column(String)  # From API company.ContactName
    website = Column(String)  # From API company.Website
    company_description = Column(Text)  # From API company.CompanyDescription
    company_uen = Column(String)  # From API company.id__CompanyUEN
    company_country_code = Column(String)  # From API company.id__Companycountrycode

    # Location from GooglePlace
    latitude = Column(Float)  # From API company.GooglePlace.lat
    longitude = Column(Float)  # From API company.GooglePlace.lng
    postal_code = Column(String)  # From API company.GooglePlace.postal
    address = Column(Text)  # From API company.GooglePlace.address

    # API metadata
    job_source = Column(String)  # From API job.job_source
    api_fetched_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Local metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    # Indexes for performance optimization
    __table_args__ = (
        Index("idx_jobs_created_at", "created_at"),
        Index("idx_jobs_position_level", "position_level"),
        Index("idx_jobs_is_active", "is_active"),
        Index("idx_jobs_company_name", "company_name"),
        Index("idx_jobs_keywords", "keywords"),
    )

    def to_dict(self):
        """Convert job to dictionary for JSON serialization"""
        return {
            "id": self.id,
            "job_id": self.job_id,
            "title": self.title,
            "company_name": self.company_name,
            "company_sid": self.company_sid,
            "activation_date": self.activation_date.isoformat()
            if self.activation_date
            else None,
            "expiration_date": self.expiration_date.isoformat()
            if self.expiration_date
            else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "keywords": self.keywords,
            "simple_keywords": self.simple_keywords,
            "job_description": self.job_description,
            "position_level": self.position_level,
            "min_years_experience": self.min_years_experience,
            "min_education_level": self.min_education_level,
            "no_of_vacancies": self.no_of_vacancies,
            "min_salary": self.min_salary,
            "max_salary": self.max_salary,
            "salary_interval": self.salary_interval,
            "currency": self.currency,
            "employment_type": self.employment_type,
            "work_arrangement": self.work_arrangement,
            "nearest_mrt_station": self.nearest_mrt_station,
            "timing_shift": self.timing_shift,
            "job_category": self.job_category,
            "contact_name": self.contact_name,
            "website": self.website,
            "company_description": self.company_description,
            "company_uen": self.company_uen,
            "company_country_code": self.company_country_code,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "postal_code": self.postal_code,
            "address": self.address,
            "job_source": self.job_source,
            "api_fetched_at": self.api_fetched_at.isoformat()
            if self.api_fetched_at
            else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# Database configuration is now in db_config.py
