"""
Job, project, and learning opportunity models for SkillMatch.AI
"""
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from .user_profile import ExperienceLevel, PreferenceType


class OpportunityType(str, Enum):
    """Types of opportunities"""
    JOB = "job"
    PROJECT = "project"
    INTERNSHIP = "internship"
    LEARNING = "learning"
    VOLUNTEER = "volunteer"
    FREELANCE = "freelance"


class RequiredSkill(BaseModel):
    """Required skill for an opportunity"""
    skill_id: str = Field(..., description="Skill identifier")
    skill_name: str = Field(..., description="Human-readable skill name")
    category: str = Field(..., description="Skill category")
    required_level: ExperienceLevel = Field(..., description="Minimum required proficiency")
    importance: float = Field(..., ge=0.0, le=1.0, description="Importance weight 0-1")
    is_mandatory: bool = Field(True, description="Whether this skill is mandatory or preferred")


class CompanyInfo(BaseModel):
    """Company or organization information"""
    name: str = Field(..., description="Company name")
    industry: str = Field(..., description="Industry sector")
    size: Optional[str] = Field(None, description="Company size category")
    location: Optional[str] = Field(None, description="Company location")
    website: Optional[str] = Field(None, description="Company website")
    description: Optional[str] = Field(None, description="Company description")


class SalaryInfo(BaseModel):
    """Salary and compensation information"""
    min_salary: Optional[float] = Field(None, description="Minimum salary")
    max_salary: Optional[float] = Field(None, description="Maximum salary")
    currency: str = Field("USD", description="Currency code")
    equity: Optional[bool] = Field(None, description="Equity offered")
    benefits: List[str] = Field(default_factory=list, description="Benefits offered")


class LearningPath(BaseModel):
    """Learning path or course information"""
    title: str = Field(..., description="Course or learning path title")
    provider: str = Field(..., description="Educational provider")
    duration: Optional[str] = Field(None, description="Expected duration")
    difficulty: Optional[str] = Field(None, description="Difficulty level")
    certification: Optional[bool] = Field(None, description="Offers certification")
    cost: Optional[float] = Field(None, description="Cost of the course")
    prerequisites: List[str] = Field(default_factory=list, description="Required prerequisites")


class Opportunity(BaseModel):
    """Base opportunity model for jobs, projects, and learning"""
    opportunity_id: str = Field(..., description="Unique opportunity identifier")
    title: str = Field(..., description="Opportunity title")
    description: str = Field(..., description="Detailed description")
    opportunity_type: OpportunityType = Field(..., description="Type of opportunity")
    
    # Skills and requirements
    required_skills: List[RequiredSkill] = Field(default_factory=list, description="Required skills")
    preferred_skills: List[RequiredSkill] = Field(default_factory=list, description="Preferred skills")
    min_experience_years: Optional[float] = Field(None, description="Minimum years of experience")
    
    # Organization details
    company: Optional[CompanyInfo] = Field(None, description="Company information")
    location: Optional[str] = Field(None, description="Job location")
    work_type: List[PreferenceType] = Field(default_factory=list, description="Work arrangement options")
    
    # Compensation (for jobs/freelance)
    salary_info: Optional[SalaryInfo] = Field(None, description="Salary information")
    
    # Learning specific (for courses/training)
    learning_info: Optional[LearningPath] = Field(None, description="Learning details")
    
    # Timeline
    posted_date: datetime = Field(default_factory=datetime.now, description="When posted")
    application_deadline: Optional[datetime] = Field(None, description="Application deadline")
    start_date: Optional[datetime] = Field(None, description="Expected start date")
    duration: Optional[str] = Field(None, description="Expected duration")
    
    # Metadata
    is_active: bool = Field(True, description="Whether opportunity is active")
    urgency: float = Field(0.5, ge=0.0, le=1.0, description="Urgency level 0-1")
    tags: List[str] = Field(default_factory=list, description="Additional tags")
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
    
    def get_all_skills(self) -> List[RequiredSkill]:
        """Get all required and preferred skills combined"""
        return self.required_skills + self.preferred_skills
    
    def get_skills_by_category(self, category: str) -> List[RequiredSkill]:
        """Get skills filtered by category"""
        all_skills = self.get_all_skills()
        return [skill for skill in all_skills if skill.category == category]
    
    def get_mandatory_skills(self) -> List[RequiredSkill]:
        """Get only mandatory skills"""
        return [skill for skill in self.required_skills if skill.is_mandatory]
    
    def calculate_skill_importance_sum(self) -> float:
        """Calculate total importance weight of all skills"""
        return sum(skill.importance for skill in self.get_all_skills())


class JobOpportunity(Opportunity):
    """Specialized model for job opportunities"""
    opportunity_type: OpportunityType = Field(default=OpportunityType.JOB, description="Always 'job'")
    job_level: Optional[str] = Field(None, description="Job level (entry, mid, senior)")
    team_size: Optional[int] = Field(None, description="Size of the team")
    reports_to: Optional[str] = Field(None, description="Reporting structure")
    growth_opportunities: List[str] = Field(default_factory=list, description="Career growth opportunities")


class ProjectOpportunity(Opportunity):
    """Specialized model for project opportunities"""
    opportunity_type: OpportunityType = Field(default=OpportunityType.PROJECT, description="Always 'project'")
    project_budget: Optional[float] = Field(None, description="Project budget")
    team_members: Optional[int] = Field(None, description="Expected team size")
    collaboration_style: Optional[str] = Field(None, description="Collaboration approach")
    deliverables: List[str] = Field(default_factory=list, description="Expected deliverables")


class LearningOpportunity(Opportunity):
    """Specialized model for learning opportunities"""
    opportunity_type: OpportunityType = Field(default=OpportunityType.LEARNING, description="Always 'learning'")
    skill_outcomes: List[str] = Field(default_factory=list, description="Skills you'll gain")
    career_paths: List[str] = Field(default_factory=list, description="Relevant career paths")
    completion_rate: Optional[float] = Field(None, description="Course completion rate")
    rating: Optional[float] = Field(None, description="Course rating")


class OpportunityDatabase(BaseModel):
    """Container for multiple opportunities"""
    opportunities: List[Opportunity] = Field(default_factory=list, description="List of all opportunities")
    last_updated: datetime = Field(default_factory=datetime.now, description="Last database update")
    
    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
    
    def add_opportunity(self, opportunity: Opportunity) -> None:
        """Add a new opportunity to the database"""
        # Remove existing opportunity with same ID if present
        self.opportunities = [op for op in self.opportunities if op.opportunity_id != opportunity.opportunity_id]
        self.opportunities.append(opportunity)
        self.last_updated = datetime.now()
    
    def get_opportunity_by_id(self, opportunity_id: str) -> Optional[Opportunity]:
        """Get opportunity by ID"""
        for opportunity in self.opportunities:
            if opportunity.opportunity_id == opportunity_id:
                return opportunity
        return None
    
    def get_opportunities_by_type(self, opportunity_type: OpportunityType) -> List[Opportunity]:
        """Get opportunities filtered by type"""
        return [op for op in self.opportunities if op.opportunity_type == opportunity_type]
    
    def get_active_opportunities(self) -> List[Opportunity]:
        """Get only active opportunities"""
        return [op for op in self.opportunities if op.is_active]
    
    def search_by_skills(self, skill_ids: List[str]) -> List[Opportunity]:
        """Find opportunities that require any of the given skills"""
        matching_opportunities = []
        for opportunity in self.get_active_opportunities():
            opportunity_skill_ids = [skill.skill_id for skill in opportunity.get_all_skills()]
            if any(skill_id in opportunity_skill_ids for skill_id in skill_ids):
                matching_opportunities.append(opportunity)
        return matching_opportunities
    
    def search_by_location(self, location: str) -> List[Opportunity]:
        """Find opportunities in a specific location"""
        return [op for op in self.get_active_opportunities() 
                if op.location and location.lower() in op.location.lower()]