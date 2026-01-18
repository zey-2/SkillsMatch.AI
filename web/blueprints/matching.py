"""
Matching Blueprint - Routes for job matching

Handles:
- Match profile to jobs
- Get match details
- Get skill gaps
- Get recommendations
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
import logging
from web.services import (
    MatchingService,
    ProfileService,
    JobService,
    ValidationError,
    NotFoundError,
)
from web.storage import storage  # Assuming global storage instance

logger = logging.getLogger(__name__)

matching_bp = Blueprint("matching", __name__, url_prefix="/match")
matching_service = MatchingService()
profile_service = ProfileService(storage=storage)
job_service = JobService(storage=storage)


@matching_bp.route("", methods=["GET"])
def match_page():
    """Render match page"""
    try:
        profiles, _ = profile_service.list_profiles(skip=0, limit=100)
        return render_template(
            "match.html",
            profiles=[p.__dict__ if hasattr(p, "__dict__") else p for p in profiles],
        )
    except Exception as e:
        logger.error(f"Error rendering match page: {e}")
        flash("Error loading match page", "error")
        return render_template("match.html", profiles=[])


@matching_bp.route("/profile/<profile_id>", methods=["GET"])
def match_profile(profile_id):
    """Match a profile to all available jobs"""
    try:
        # Get profile
        profile = profile_service.get_profile(profile_id)

        # Get jobs
        jobs, _ = job_service.list_jobs(skip=0, limit=500)

        # Perform matching
        min_score = max(0, min(100, int(request.args.get("min_score", 0))))
        results = matching_service.match_profile_to_jobs(
            profile, jobs, min_score=min_score
        )

        return jsonify(
            {
                "success": True,
                "profile_id": profile_id,
                "total_matches": len(results),
                "matches": [
                    {
                        "job_id": r.job_id,
                        "job_title": r.job_title,
                        "company": r.company,
                        "match_score": r.match_score,
                        "skill_match_percentage": r.skill_match_percentage,
                        "experience_match": r.experience_match,
                        "salary_match": r.salary_match,
                        "location_match": r.location_match,
                        "reasons": r.reasons,
                        "skill_gaps": r.skill_gaps,
                        "missing_skills": r.missing_skills,
                    }
                    for r in results[:50]  # Limit to top 50
                ],
            }
        ), 200

    except NotFoundError as e:
        return jsonify({"success": False, "error": str(e), "code": "NOT_FOUND"}), 404
    except Exception as e:
        logger.error(f"Error matching profile: {e}")
        return jsonify({"success": False, "error": "Failed to match profile"}), 500


@matching_bp.route("/profile/<profile_id>/job/<job_id>", methods=["GET"])
def match_profile_to_job(profile_id, job_id):
    """Match a specific profile to a specific job"""
    try:
        # Get profile and job
        profile = profile_service.get_profile(profile_id)
        job = job_service.get_job(job_id)

        # Perform matching
        result = matching_service.match_profile_to_job(profile, job)

        return jsonify(
            {
                "success": True,
                "profile_id": profile_id,
                "job_id": job_id,
                "match_score": result.match_score,
                "skill_match_percentage": result.skill_match_percentage,
                "experience_match": result.experience_match,
                "salary_match": result.salary_match,
                "location_match": result.location_match,
                "reasons": result.reasons,
                "skill_gaps": result.skill_gaps,
                "missing_skills": result.missing_skills,
            }
        ), 200

    except NotFoundError as e:
        return jsonify({"success": False, "error": str(e), "code": "NOT_FOUND"}), 404
    except Exception as e:
        logger.error(f"Error matching profile to job: {e}")
        return jsonify(
            {"success": False, "error": "Failed to match profile to job"}
        ), 500


@matching_bp.route("/skill-gaps/<profile_id>/<job_id>", methods=["GET"])
def get_skill_gaps(profile_id, job_id):
    """Get skill gaps for a profile-job pair"""
    try:
        profile = profile_service.get_profile(profile_id)
        job = job_service.get_job(job_id)

        result = matching_service.match_profile_to_job(profile, job)

        return jsonify(
            {
                "success": True,
                "profile_id": profile_id,
                "job_id": job_id,
                "skill_gaps": result.skill_gaps,
                "missing_skills": result.missing_skills,
            }
        ), 200

    except NotFoundError as e:
        return jsonify({"success": False, "error": str(e), "code": "NOT_FOUND"}), 404
    except Exception as e:
        logger.error(f"Error getting skill gaps: {e}")
        return jsonify({"success": False, "error": "Failed to get skill gaps"}), 500


@matching_bp.route("/recommendations/<profile_id>", methods=["GET"])
def get_recommendations(profile_id):
    """Get top job recommendations for a profile"""
    try:
        profile = profile_service.get_profile(profile_id)
        jobs, _ = job_service.list_jobs(skip=0, limit=500)

        # Get top 10 recommendations
        results = matching_service.match_profile_to_jobs(profile, jobs, min_score=50)
        top_recommendations = results[:10]

        return jsonify(
            {
                "success": True,
                "profile_id": profile_id,
                "recommendations": [
                    {
                        "rank": i + 1,
                        "job_id": r.job_id,
                        "job_title": r.job_title,
                        "company": r.company,
                        "match_score": r.match_score,
                        "reasons": r.reasons,
                    }
                    for i, r in enumerate(top_recommendations)
                ],
            }
        ), 200

    except NotFoundError as e:
        return jsonify({"success": False, "error": str(e), "code": "NOT_FOUND"}), 404
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return jsonify(
            {"success": False, "error": "Failed to get recommendations"}
        ), 500


@matching_bp.route("/batch", methods=["POST"])
def batch_match():
    """Match multiple profiles to all jobs (batch operation)"""
    try:
        data = request.get_json()
        profile_ids = data.get("profile_ids", [])
        min_score = max(0, min(100, int(data.get("min_score", 0))))

        if not profile_ids:
            return jsonify(
                {"success": False, "error": "profile_ids list required"}
            ), 400

        # Get jobs
        jobs, _ = job_service.list_jobs(skip=0, limit=500)

        results = {}
        errors = {}

        for profile_id in profile_ids[:10]:  # Limit to 10 profiles for batch
            try:
                profile = profile_service.get_profile(profile_id)
                matches = matching_service.match_profile_to_jobs(
                    profile, jobs, min_score=min_score
                )
                results[profile_id] = [
                    {
                        "job_id": m.job_id,
                        "job_title": m.job_title,
                        "company": m.company,
                        "match_score": m.match_score,
                    }
                    for m in matches[:20]
                ]
            except Exception as e:
                errors[profile_id] = str(e)

        return jsonify(
            {
                "success": True,
                "total_profiles": len(profile_ids),
                "processed": len(results),
                "errors": len(errors),
                "results": results,
                "errors_detail": errors,
            }
        ), 200

    except Exception as e:
        logger.error(f"Error batch matching: {e}")
        return jsonify({"success": False, "error": "Failed to batch match"}), 500


@matching_bp.route("/stats", methods=["GET"])
def matching_stats():
    """Get matching statistics"""
    try:
        profiles, _ = profile_service.list_profiles(skip=0, limit=1)
        jobs, total_jobs = job_service.list_jobs(skip=0, limit=1)

        return jsonify(
            {
                "success": True,
                "stats": {
                    "total_profiles": profile_service.get_profile_stats().get(
                        "total", 0
                    ),
                    "total_jobs": total_jobs,
                },
            }
        ), 200

    except Exception as e:
        logger.error(f"Error getting matching stats: {e}")
        return jsonify(
            {"success": False, "error": "Failed to retrieve statistics"}
        ), 500
