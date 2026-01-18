"""
Jobs Blueprint - Routes for job management

Handles:
- Fetch jobs from API
- List jobs
- View job details
- Search jobs
- Job statistics
"""

from flask import Blueprint, render_template, request, jsonify, flash
import logging
from web.services import JobService, ValidationError, NotFoundError
from web.storage import storage  # Assuming global storage instance

logger = logging.getLogger(__name__)

jobs_bp = Blueprint("jobs", __name__, url_prefix="/jobs")
job_service = JobService(storage=storage)


@jobs_bp.route("", methods=["GET"])
def list_jobs():
    """List all jobs with pagination"""
    try:
        skip = max(0, int(request.args.get("skip", 0)))
        limit = min(100, max(1, int(request.args.get("limit", 20))))

        # Optional filters
        filters = {}
        if request.args.get("location"):
            filters["location"] = request.args.get("location")
        if request.args.get("job_type"):
            filters["job_type"] = request.args.get("job_type")
        if request.args.get("company"):
            filters["company"] = request.args.get("company")

        jobs, total = job_service.list_jobs(skip=skip, limit=limit, filter_by=filters)

        return jsonify(
            {
                "success": True,
                "jobs": [j.to_dict() for j in jobs],
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        ), 200

    except ValidationError as e:
        return jsonify({"success": False, "error": str(e), "code": e.code}), 422
    except Exception as e:
        logger.error(f"Error listing jobs: {e}")
        return jsonify({"success": False, "error": "Failed to list jobs"}), 500


@jobs_bp.route("/<job_id>", methods=["GET"])
def get_job(job_id):
    """Get a specific job"""
    try:
        job = job_service.get_job(job_id)

        return jsonify({"success": True, "job": job.to_dict()}), 200

    except NotFoundError as e:
        return jsonify({"success": False, "error": str(e), "code": "NOT_FOUND"}), 404
    except Exception as e:
        logger.error(f"Error getting job: {e}")
        return jsonify({"success": False, "error": "Failed to retrieve job"}), 500


@jobs_bp.route("/search", methods=["GET"])
def search_jobs():
    """Search jobs by keyword"""
    try:
        query = request.args.get("q", "").strip()
        limit = min(100, max(1, int(request.args.get("limit", 20))))

        if not query:
            return jsonify({"success": False, "error": "Search query required"}), 400

        results = job_service.search_jobs(query=query, limit=limit)

        return jsonify(
            {
                "success": True,
                "query": query,
                "results": [j.to_dict() for j in results],
                "count": len(results),
            }
        ), 200

    except ValidationError as e:
        return jsonify({"success": False, "error": str(e), "code": e.code}), 422
    except Exception as e:
        logger.error(f"Error searching jobs: {e}")
        return jsonify({"success": False, "error": "Failed to search jobs"}), 500


@jobs_bp.route("/fetch-from-api", methods=["POST"])
def fetch_from_api():
    """Fetch jobs from FindSGJobs API and update database"""
    try:
        pages = int(request.json.get("pages", 5)) if request.is_json else 5

        if pages < 1 or pages > 10:
            return jsonify(
                {"success": False, "error": "pages must be between 1 and 10"}
            ), 400

        jobs_fetched, errors = job_service.fetch_from_findsgjobs_api(pages=pages)

        return jsonify(
            {
                "success": True,
                "message": f"Fetched {len(jobs_fetched)} jobs",
                "jobs_fetched": len(jobs_fetched),
                "errors": errors,
            }
        ), 200

    except ValidationError as e:
        return jsonify({"success": False, "error": str(e), "code": e.code}), 422
    except Exception as e:
        logger.error(f"Error fetching jobs from API: {e}")
        return jsonify({"success": False, "error": "Failed to fetch jobs"}), 500


@jobs_bp.route("/stats", methods=["GET"])
def job_stats():
    """Get job statistics"""
    try:
        stats = job_service.get_job_statistics()

        return jsonify({"success": True, "stats": stats}), 200

    except Exception as e:
        logger.error(f"Error getting job stats: {e}")
        return jsonify(
            {"success": False, "error": "Failed to retrieve statistics"}
        ), 500


@jobs_bp.route("/listing")
def jobs_listing_html():
    """Render jobs listing page"""
    try:
        jobs, total = job_service.list_jobs(skip=0, limit=50)
        return render_template(
            "jobs_listing.html", jobs=[j.to_dict() for j in jobs], total_jobs=total
        )
    except Exception as e:
        logger.error(f"Error rendering jobs listing: {e}")
        flash("Error loading jobs", "error")
        return render_template("jobs_listing.html", jobs=[], total_jobs=0)


@jobs_bp.route("", methods=["POST"])
def create_job():
    """Create a new job"""
    try:
        job_data = request.get_json()
        job = job_service.create_job(job_data)

        return jsonify(
            {
                "success": True,
                "message": "Job created successfully",
                "job": job.to_dict(),
            }
        ), 201

    except ValidationError as e:
        return jsonify({"success": False, "error": str(e), "code": e.code}), 422
    except Exception as e:
        logger.error(f"Error creating job: {e}")
        return jsonify({"success": False, "error": "Failed to create job"}), 500


@jobs_bp.route("/<job_id>", methods=["PUT"])
def update_job(job_id):
    """Update a job"""
    try:
        job_data = request.get_json()
        updated_job = job_service.update_job(job_id, job_data)

        return jsonify(
            {
                "success": True,
                "message": "Job updated successfully",
                "job": updated_job.to_dict(),
            }
        ), 200

    except ValidationError as e:
        return jsonify({"success": False, "error": str(e), "code": e.code}), 422
    except NotFoundError as e:
        return jsonify({"success": False, "error": str(e), "code": "NOT_FOUND"}), 404
    except Exception as e:
        logger.error(f"Error updating job: {e}")
        return jsonify({"success": False, "error": "Failed to update job"}), 500


@jobs_bp.route("/<job_id>", methods=["DELETE"])
def delete_job(job_id):
    """Delete a job"""
    try:
        job_service.delete_job(job_id)

        return jsonify({"success": True, "message": "Job deleted successfully"}), 200

    except NotFoundError as e:
        return jsonify({"success": False, "error": str(e), "code": "NOT_FOUND"}), 404
    except Exception as e:
        logger.error(f"Error deleting job: {e}")
        return jsonify({"success": False, "error": "Failed to delete job"}), 500
