"""
Services module for SkillsMatch.AI web application
Contains job matching and API integration services
"""

# Import services to make them available at module level
try:
    from .job_matching import job_matching_service
except ImportError:
    # Fallback imports
    try:
        from job_matching import job_matching_service
    except ImportError:
        print("Warning: Could not import job_matching service")
        job_matching_service = None

__all__ = ['job_matching_service']