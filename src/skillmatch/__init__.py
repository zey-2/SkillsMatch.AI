"""
SkillMatch.AI - Intelligent Career and Skill Matching System

A comprehensive AI-powered platform for matching users with jobs, projects, 
and learning opportunities based on their skills, experience, and preferences.
"""

__version__ = "0.1.0"
__author__ = "SkillMatch.AI Team"
__email__ = "team@skillmatch.ai"

from .models import *
from .agents.skill_match_agent import SkillMatchAgent
from .utils import DataLoader, SkillMatcher

__all__ = [
    "SkillMatchAgent",
    "DataLoader", 
    "SkillMatcher",
    # Re-export models
    "UserProfile",
    "SkillItem",
    "WorkExperience", 
    "Education",
    "UserPreferences",
    "Opportunity",
    "JobOpportunity",
    "ProjectOpportunity",
    "LearningOpportunity",
    "OpportunityDatabase",
    "MatchScore",
    "SkillGap",
    "ExperienceLevel",
    "PreferenceType",
    "OpportunityType"
]