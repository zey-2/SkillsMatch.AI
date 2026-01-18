"""
Blueprints module for SkillsMatch.AI web application.

Phase 2: Monolithic App Refactoring
Organized route handlers for different domains:
- profiles: User profile management
- jobs: Job listing and search
- matching: Job-to-profile matching
- dashboard: Analytics and statistics
- api: REST API endpoints
"""

from flask import Blueprint
import logging

logger = logging.getLogger(__name__)


def create_blueprints(app):
    """
    Register all blueprints with the Flask application.

    Args:
        app: Flask application instance
    """
    try:
        # Import blueprints (created in Phase 2)
        from web.blueprints.profiles import profiles_bp
        from web.blueprints.jobs import jobs_bp
        from web.blueprints.matching import matching_bp
        from web.blueprints.dashboard import dashboard_bp
        from web.blueprints.api import api_bp

        # Register blueprints
        app.register_blueprint(profiles_bp, url_prefix="/profiles")
        app.register_blueprint(jobs_bp, url_prefix="/jobs")
        app.register_blueprint(matching_bp, url_prefix="/match")
        app.register_blueprint(dashboard_bp)  # No prefix for dashboard/home
        app.register_blueprint(api_bp, url_prefix="/api")

        logger.info("✅ All blueprints registered successfully")
        logger.info("   - Dashboard: /, /dashboard, /api/stats")
        logger.info("   - Profiles: /profiles, /profiles/<id>, /profiles/search")
        logger.info("   - Jobs: /jobs, /jobs/<id>, /jobs/search, /jobs/fetch-from-api")
        logger.info("   - Matching: /match, /match/profile/<id>, /match/batch")
        logger.info("   - API: /api/profiles, /api/jobs, /api/search/*, /api/ai/*")

    except ImportError as e:
        logger.error(f"❌ Error importing blueprints: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Error registering blueprints: {e}")
        raise


__all__ = ["create_blueprints"]
