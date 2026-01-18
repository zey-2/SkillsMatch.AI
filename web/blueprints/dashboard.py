"""
Dashboard Blueprint - Routes for dashboard and home page

Handles:
- Dashboard home page
- Statistics and metrics
- Recent activity
"""

from flask import Blueprint, render_template, jsonify
import logging
from web.services import ProfileService, JobService
from web.storage import storage  # Assuming global storage instance

logger = logging.getLogger(__name__)

dashboard_bp = Blueprint("dashboard", __name__)
profile_service = ProfileService(storage=storage)
job_service = JobService(storage=storage)


@dashboard_bp.route("/")
def index():
    """Dashboard home page"""
    try:
        # Get statistics
        profile_stats = profile_service.get_profile_stats()
        job_stats = job_service.get_job_statistics()

        context = {
            "profile_stats": profile_stats,
            "job_stats": job_stats,
        }

        return render_template("index.html", **context)

    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}")
        return render_template("index.html", profile_stats={}, job_stats={})


@dashboard_bp.route("/dashboard")
def dashboard():
    """Dashboard view with detailed statistics"""
    try:
        # Get lists for display
        recent_profiles, _ = profile_service.list_profiles(skip=0, limit=5)
        recent_jobs, total_jobs = job_service.list_jobs(skip=0, limit=10)

        profile_stats = profile_service.get_profile_stats()
        job_stats = job_service.get_job_statistics()

        context = {
            "recent_profiles": [
                p.__dict__ if hasattr(p, "__dict__") else p for p in recent_profiles
            ],
            "recent_jobs": [j.to_dict() for j in recent_jobs],
            "total_jobs": total_jobs,
            "profile_stats": profile_stats,
            "job_stats": job_stats,
        }

        return render_template("dashboard.html", **context)

    except Exception as e:
        logger.error(f"Error rendering detailed dashboard: {e}")
        return render_template(
            "dashboard.html",
            recent_profiles=[],
            recent_jobs=[],
            total_jobs=0,
            profile_stats={},
            job_stats={},
        )


@dashboard_bp.route("/api/stats")
def get_stats():
    """Get dashboard statistics as JSON"""
    try:
        profile_stats = profile_service.get_profile_stats()
        job_stats = job_service.get_job_statistics()

        return jsonify(
            {
                "success": True,
                "profiles": profile_stats,
                "jobs": job_stats,
            }
        ), 200

    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify(
            {"success": False, "error": "Failed to retrieve statistics"}
        ), 500


@dashboard_bp.route("/api/recent-activity")
def get_recent_activity():
    """Get recent activity (profiles, jobs, matches)"""
    try:
        recent_profiles, _ = profile_service.list_profiles(skip=0, limit=5)
        recent_jobs, _ = job_service.list_jobs(skip=0, limit=5)

        return jsonify(
            {
                "success": True,
                "recent_profiles": [
                    p.__dict__ if hasattr(p, "__dict__") else p for p in recent_profiles
                ],
                "recent_jobs": [j.to_dict() for j in recent_jobs],
            }
        ), 200

    except Exception as e:
        logger.error(f"Error getting recent activity: {e}")
        return jsonify(
            {"success": False, "error": "Failed to retrieve recent activity"}
        ), 500


@dashboard_bp.route("/api/system-health")
def system_health():
    """Get system health status"""
    try:
        # Check profile service
        profile_stats = profile_service.get_profile_stats()
        profile_ok = profile_stats is not None

        # Check job service
        job_stats = job_service.get_job_statistics()
        job_ok = job_stats is not None

        health_status = "healthy" if (profile_ok and job_ok) else "degraded"

        return jsonify(
            {
                "success": True,
                "status": health_status,
                "services": {
                    "profiles": "up" if profile_ok else "down",
                    "jobs": "up" if job_ok else "down",
                },
            }
        ), 200

    except Exception as e:
        logger.error(f"Error checking system health: {e}")
        return jsonify({"success": False, "status": "error", "error": str(e)}), 500


@dashboard_bp.route("/health")
def health_check():
    """Health check endpoint"""
    return jsonify(
        {"status": "healthy", "message": "Dashboard service is running"}
    ), 200
