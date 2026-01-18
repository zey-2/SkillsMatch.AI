"""
API Blueprint - RESTful API endpoints

Provides:
- Unified API for all services
- AI-powered endpoints
- Batch operations
- Advanced search
"""

from flask import Blueprint, request, jsonify
import logging
from web.services import (
    ProfileService,
    JobService,
    MatchingService,
    AIService,
    ValidationError,
    NotFoundError,
)
from web.storage import storage  # Assuming global storage instance

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__, url_prefix="/api")
profile_service = ProfileService(storage=storage)
job_service = JobService(storage=storage)
matching_service = MatchingService()
ai_service = AIService()


@api_bp.route("/profiles", methods=["GET"])
def api_list_profiles():
    """API: List profiles"""
    try:
        skip = max(0, int(request.args.get("skip", 0)))
        limit = min(100, max(1, int(request.args.get("limit", 20))))

        profiles, total = profile_service.list_profiles(skip=skip, limit=limit)

        return jsonify(
            {
                "success": True,
                "data": [p.__dict__ if hasattr(p, "__dict__") else p for p in profiles],
                "pagination": {
                    "total": total,
                    "skip": skip,
                    "limit": limit,
                },
            }
        ), 200

    except ValidationError as e:
        return jsonify({"success": False, "error": str(e), "code": e.code}), 422
    except Exception as e:
        logger.error(f"Error in API list profiles: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@api_bp.route("/profiles", methods=["POST"])
def api_create_profile():
    """API: Create profile"""
    try:
        profile_data = request.get_json()
        profile = profile_service.create_profile(profile_data)

        return jsonify(
            {
                "success": True,
                "data": profile.__dict__ if hasattr(profile, "__dict__") else profile,
            }
        ), 201

    except ValidationError as e:
        return jsonify({"success": False, "error": str(e), "code": e.code}), 422
    except Exception as e:
        logger.error(f"Error in API create profile: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@api_bp.route("/jobs", methods=["GET"])
def api_list_jobs():
    """API: List jobs"""
    try:
        skip = max(0, int(request.args.get("skip", 0)))
        limit = min(100, max(1, int(request.args.get("limit", 20))))

        jobs, total = job_service.list_jobs(skip=skip, limit=limit)

        return jsonify(
            {
                "success": True,
                "data": [j.to_dict() for j in jobs],
                "pagination": {
                    "total": total,
                    "skip": skip,
                    "limit": limit,
                },
            }
        ), 200

    except ValidationError as e:
        return jsonify({"success": False, "error": str(e), "code": e.code}), 422
    except Exception as e:
        logger.error(f"Error in API list jobs: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@api_bp.route("/search/profiles", methods=["GET"])
def api_search_profiles():
    """API: Search profiles"""
    try:
        query = request.args.get("q", "").strip()
        limit = min(50, max(1, int(request.args.get("limit", 20))))

        if not query:
            return jsonify({"success": False, "error": "Search query required"}), 400

        results = profile_service.search_profiles(query=query, limit=limit)

        return jsonify(
            {
                "success": True,
                "query": query,
                "data": [r.__dict__ if hasattr(r, "__dict__") else r for r in results],
                "count": len(results),
            }
        ), 200

    except ValidationError as e:
        return jsonify({"success": False, "error": str(e), "code": e.code}), 422
    except Exception as e:
        logger.error(f"Error in API search profiles: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@api_bp.route("/search/jobs", methods=["GET"])
def api_search_jobs():
    """API: Search jobs"""
    try:
        query = request.args.get("q", "").strip()
        limit = min(50, max(1, int(request.args.get("limit", 20))))

        if not query:
            return jsonify({"success": False, "error": "Search query required"}), 400

        results = job_service.search_jobs(query=query, limit=limit)

        return jsonify(
            {
                "success": True,
                "query": query,
                "data": [j.to_dict() for j in results],
                "count": len(results),
            }
        ), 200

    except ValidationError as e:
        return jsonify({"success": False, "error": str(e), "code": e.code}), 422
    except Exception as e:
        logger.error(f"Error in API search jobs: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@api_bp.route("/matching/<profile_id>", methods=["GET"])
def api_match_profile(profile_id):
    """API: Match profile to all jobs"""
    try:
        profile = profile_service.get_profile(profile_id)
        jobs, _ = job_service.list_jobs(skip=0, limit=500)
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
                        "reasons": r.reasons,
                    }
                    for r in results[:50]
                ],
            }
        ), 200

    except NotFoundError as e:
        return jsonify({"success": False, "error": str(e), "code": "NOT_FOUND"}), 404
    except Exception as e:
        logger.error(f"Error in API match profile: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@api_bp.route("/ai/skill-explanation", methods=["GET"])
def api_skill_explanation():
    """API: Get AI skill explanation"""
    try:
        skill = request.args.get("skill", "").strip()
        if not skill:
            return jsonify({"success": False, "error": "skill parameter required"}), 400

        if not ai_service.is_available():
            return jsonify({"success": False, "error": "AI service not available"}), 503

        explanation = ai_service.generate_skill_explanation(skill)

        return jsonify(
            {"success": True, "skill": skill, "explanation": explanation}
        ), 200

    except ValidationError as e:
        return jsonify({"success": False, "error": str(e), "code": e.code}), 422
    except Exception as e:
        logger.error(f"Error in API skill explanation: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@api_bp.route("/ai/profile-summary", methods=["POST"])
def api_profile_summary():
    """API: Get AI profile summary"""
    try:
        profile_data = request.get_json()

        if not ai_service.is_available():
            return jsonify({"success": False, "error": "AI service not available"}), 503

        summary = ai_service.analyze_profile_summary(profile_data)

        return jsonify({"success": True, "summary": summary}), 200

    except ValidationError as e:
        return jsonify({"success": False, "error": str(e), "code": e.code}), 422
    except Exception as e:
        logger.error(f"Error in API profile summary: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@api_bp.route("/ai/skill-gaps", methods=["POST"])
def api_skill_gaps():
    """API: Get AI skill gap analysis"""
    try:
        data = request.get_json()
        profile_skills = data.get("profile_skills", [])
        job_title = data.get("job_title", "")
        required_skills = data.get("required_skills", [])

        if not ai_service.is_available():
            return jsonify({"success": False, "error": "AI service not available"}), 503

        analysis = ai_service.generate_skill_gap_analysis(
            profile_skills=profile_skills,
            job_title=job_title,
            required_skills=required_skills,
        )

        return jsonify({"success": True, "analysis": analysis}), 200

    except ValidationError as e:
        return jsonify({"success": False, "error": str(e), "code": e.code}), 422
    except Exception as e:
        logger.error(f"Error in API skill gaps: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@api_bp.route("/ai/interview-tips", methods=["POST"])
def api_interview_tips():
    """API: Get AI interview tips"""
    try:
        data = request.get_json()
        job_title = data.get("job_title", "")
        job_description = data.get("job_description", "")
        profile_skills = data.get("profile_skills", [])

        if not ai_service.is_available():
            return jsonify({"success": False, "error": "AI service not available"}), 503

        tips = ai_service.generate_interview_tips(
            job_title=job_title,
            job_description=job_description,
            profile_skills=profile_skills,
        )

        return jsonify({"success": True, "tips": tips}), 200

    except ValidationError as e:
        return jsonify({"success": False, "error": str(e), "code": e.code}), 422
    except Exception as e:
        logger.error(f"Error in API interview tips: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@api_bp.route("/ai/career-suggestions", methods=["POST"])
def api_career_suggestions():
    """API: Get AI career suggestions"""
    try:
        data = request.get_json()
        current_skills = data.get("current_skills", [])
        experience_years = int(data.get("experience_years", 0))
        industry = data.get("industry", "")

        if not ai_service.is_available():
            return jsonify({"success": False, "error": "AI service not available"}), 503

        suggestions = ai_service.generate_career_suggestions(
            current_skills=current_skills,
            experience_years=experience_years,
            industry=industry,
        )

        return jsonify({"success": True, "suggestions": suggestions}), 200

    except ValidationError as e:
        return jsonify({"success": False, "error": str(e), "code": e.code}), 422
    except Exception as e:
        logger.error(f"Error in API career suggestions: {e}")
        return jsonify({"success": False, "error": "Internal server error"}), 500


@api_bp.route("/health", methods=["GET"])
def api_health():
    """API: Health check"""
    return jsonify(
        {
            "success": True,
            "status": "healthy",
            "services": {
                "profiles": "available",
                "jobs": "available",
                "matching": "available",
                "ai": "available" if ai_service.is_available() else "unavailable",
            },
        }
    ), 200
