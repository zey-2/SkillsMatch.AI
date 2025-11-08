"""
Services module for SkillsMatch.AI web application
Contains job matching and API integration services
"""

# Import services to make them available at module level
try:
    from .job_matching import job_matching_service
    from .ssg_wsg_api import SSGWSGAPIClient
except ImportError:
    # Fallback imports
    try:
        from job_matching import job_matching_service
        from ssg_wsg_api import SSGWSGAPIClient
    except ImportError:
        print("Warning: Could not import services modules")
        job_matching_service = None
        SSGWSGAPIClient = None

__all__ = ['job_matching_service', 'SSGWSGAPIClient']