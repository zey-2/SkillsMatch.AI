"""
User profile and skill management models for SkillMatch.AI
"""
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class ExperienceLevel(str, Enum):
    """Experience levels for skills"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    DEVELOPING = "developing"
    COMPETENT = "competent"
    PROFICIENT = "proficient"


class PreferenceType(str, Enum):
    """Types of job/project preferences"""
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    CONTRACT = "contract"
    FULLTIME = "fulltime"
    PARTTIME = "parttime"
    INTERNSHIP = "internship"


class SkillItem(BaseModel):
    """Individual skill with proficiency level"""
    skill_id: str = Field(..., description="Unique identifier for the skill")
    skill_name: str = Field(..., description="Human-readable skill name")
    category: str = Field(..., description="Skill category")
    level: ExperienceLevel = Field(..., description="Proficiency level")
    years_experience: Optional[float] = Field(None, description="Years of experience with this skill")
    last_used: Optional[datetime] = Field(None, description="When this skill was last used")
    verified: bool = Field(False, description="Whether the skill has been verified")
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class WorkExperience(BaseModel):
    """Work experience entry"""
    company: str = Field(..., description="Company name")
    position: str = Field(..., description="Job title/position")
    start_date: datetime = Field(..., description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date (None if current)")
    description: Optional[str] = Field(None, description="Job description")
    key_skills: List[str] = Field(default_factory=list, description="Key skills used in this role")
    achievements: List[str] = Field(default_factory=list, description="Notable achievements")
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class Education(BaseModel):
    """Education entry"""
    institution: str = Field(..., description="Educational institution")
    degree: str = Field(..., description="Degree or certification")
    field_of_study: Optional[str] = Field(None, description="Major or field of study")
    start_date: Optional[datetime] = Field(None, description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date")
    gpa: Optional[float] = Field(None, description="GPA or grade")
    relevant_coursework: List[str] = Field(default_factory=list, description="Relevant courses")
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }


class UserPreferences(BaseModel):
    """User preferences for job matching"""
    work_type: List[PreferenceType] = Field(default_factory=list, description="Preferred work arrangements")
    desired_roles: List[str] = Field(default_factory=list, description="Desired job titles/roles")
    salary_min: Optional[float] = Field(None, description="Minimum salary expectation")
    salary_max: Optional[float] = Field(None, description="Maximum salary expectation")
    locations: List[str] = Field(default_factory=list, description="Preferred locations")
    company_size: List[str] = Field(default_factory=list, description="Preferred company sizes")
    industries: List[str] = Field(default_factory=list, description="Preferred industries")
    growth_areas: List[str] = Field(default_factory=list, description="Skills they want to develop")
    availability: Optional[str] = Field(None, description="When they can start")


class UserProfile(BaseModel):
    """Complete user profile for skill matching"""
    user_id: str = Field(..., description="Unique user identifier")
    name: str = Field(..., description="User's full name")
    email: str = Field(..., description="User's email address")
    location: Optional[str] = Field(None, description="Current location")
    summary: Optional[str] = Field(None, description="Professional summary")
    
    # Skills and experience
    skills: List[SkillItem] = Field(default_factory=list, description="User's skills")
    work_experience: List[WorkExperience] = Field(default_factory=list, description="Work history")
    education: List[Education] = Field(default_factory=list, description="Educational background")
    
    # Preferences and goals
    preferences: UserPreferences = Field(default_factory=UserPreferences, description="Job preferences")
    career_goals: List[str] = Field(default_factory=list, description="Career aspirations")
    
    # Profile metadata
    created_at: datetime = Field(default_factory=datetime.now, description="Profile creation date")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update date")
    is_active: bool = Field(True, description="Whether profile is active")
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
    
    def get_skill_by_id(self, skill_id: str) -> Optional[SkillItem]:
        """Get a specific skill by ID"""
        for skill in self.skills:
            if skill.skill_id == skill_id:
                return skill
        return None
    
    def get_skills_by_category(self, category: str) -> List[SkillItem]:
        """Get all skills in a specific category"""
        return [skill for skill in self.skills if skill.category == category]
    
    def get_total_experience_years(self) -> float:
        """Calculate total years of professional experience"""
        total_years = 0.0
        for exp in self.work_experience:
            if exp.end_date:
                years = (exp.end_date - exp.start_date).days / 365.25
            else:
                years = (datetime.now() - exp.start_date).days / 365.25
            total_years += years
        return round(total_years, 1)
    
    def update_skill_level(self, skill_id: str, new_level: ExperienceLevel) -> bool:
        """Update the proficiency level of a skill"""
        skill = self.get_skill_by_id(skill_id)
        if skill:
            skill.level = new_level
            self.updated_at = datetime.now()
            return True
        return False
    
    def add_skill(self, skill: SkillItem) -> None:
        """Add a new skill to the profile"""
        # Remove existing skill with same ID if present
        self.skills = [s for s in self.skills if s.skill_id != skill.skill_id]
        self.skills.append(skill)
        self.updated_at = datetime.now()
    
    def remove_skill(self, skill_id: str) -> bool:
        """Remove a skill from the profile"""
        original_count = len(self.skills)
        self.skills = [s for s in self.skills if s.skill_id != skill_id]
        if len(self.skills) < original_count:
            self.updated_at = datetime.now()
            return True
        return False


class SkillGap(BaseModel):
    """Represents a skill gap for learning recommendations"""
    skill_id: str
    skill_name: str
    category: str
    current_level: Optional[ExperienceLevel] = None
    required_level: ExperienceLevel
    importance: float = Field(..., ge=0.0, le=1.0, description="Importance score 0-1")
    learning_resources: List[str] = Field(default_factory=list)


class MatchScore(BaseModel):
    """Represents a matching score for jobs/opportunities"""
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall match score 0-1")
    skill_match_score: float = Field(..., ge=0.0, le=1.0, description="Skill compatibility score")
    experience_score: float = Field(..., ge=0.0, le=1.0, description="Experience level score")
    preference_score: float = Field(..., ge=0.0, le=1.0, description="Preference alignment score")
    skill_gaps: List[SkillGap] = Field(default_factory=list, description="Missing or insufficient skills")
    strengths: List[str] = Field(default_factory=list, description="Strong matching areas")
    explanation: str = Field(..., description="Human-readable explanation of the match")