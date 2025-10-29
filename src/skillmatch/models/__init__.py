"""
SkillMatch.AI models package
"""
from .user_profile import (
    UserProfile,
    SkillItem,
    WorkExperience,
    Education,
    UserPreferences,
    ExperienceLevel,
    PreferenceType,
    SkillGap,
    MatchScore
)

from .opportunities import (
    Opportunity,
    JobOpportunity,
    ProjectOpportunity,
    LearningOpportunity,
    OpportunityDatabase,
    RequiredSkill,
    CompanyInfo,
    SalaryInfo,
    LearningPath,
    OpportunityType
)

__all__ = [
    # User profile models
    "UserProfile",
    "SkillItem", 
    "WorkExperience",
    "Education",
    "UserPreferences",
    "ExperienceLevel",
    "PreferenceType",
    "SkillGap",
    "MatchScore",
    
    # Opportunity models
    "Opportunity",
    "JobOpportunity",
    "ProjectOpportunity", 
    "LearningOpportunity",
    "OpportunityDatabase",
    "RequiredSkill",
    "CompanyInfo",
    "SalaryInfo",
    "LearningPath",
    "OpportunityType"
]