"""
SkillsMatch.AI Services Module

Provides high-level business logic services:
- ProfileService: User profile management
- MatchingService: Job matching logic
- JobService: Job listing operations
- AIService: AI-powered features

Phase 2: Service Layer Abstraction
Extracts business logic from routes for better testability and maintainability.
"""

# Import base service classes
from web.services.base import (
    BaseService,
    ServiceError,
    ValidationError,
    NotFoundError,
    AuthorizationError,
)

# Import specific services
from web.services.profile_service import ProfileService
from web.services.matching_service import MatchingService, MatchResult
from web.services.job_service import JobService, JobData
from web.services.ai_service import AIService

# Keep legacy imports for backward compatibility
try:
    from web.services.job_matching import job_matching_service
except ImportError:
    try:
        from .job_matching import job_matching_service
    except ImportError:
        job_matching_service = None

__all__ = [
    # Base classes
    "BaseService",
    "ServiceError",
    "ValidationError",
    "NotFoundError",
    "AuthorizationError",
    # Services
    "ProfileService",
    "MatchingService",
    "MatchResult",
    "JobService",
    "JobData",
    "AIService",
    # Legacy
    "job_matching_service",
]
