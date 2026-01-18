"""
Profiles Blueprint - Routes for user profile management

Handles:
- Create profile
- View/edit profile
- List profiles
- Search profiles
- Profile deletion
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
import logging
from web.services import ProfileService, ValidationError, NotFoundError
from web.storage import storage  # Assuming global storage instance

logger = logging.getLogger(__name__)

profiles_bp = Blueprint("profiles", __name__, url_prefix="/profiles")
profile_service = ProfileService(storage=storage)


@profiles_bp.route("/create", methods=["GET", "POST"])
def create_profile():
    """Create a new profile"""
    if request.method == "GET":
        return render_template("create_profile.html")

    try:
        profile_data = request.get_json() or request.form.to_dict()
        profile = profile_service.create_profile(profile_data)

        return jsonify(
            {
                "success": True,
                "message": "Profile created successfully",
                "profile": profile.__dict__
                if hasattr(profile, "__dict__")
                else profile,
            }
        ), 201

    except ValidationError as e:
        return jsonify({"success": False, "error": str(e), "code": e.code}), 422
    except Exception as e:
        logger.error(f"Error creating profile: {e}")
        return jsonify({"success": False, "error": "Failed to create profile"}), 500


@profiles_bp.route("/<profile_id>", methods=["GET"])
def view_profile(profile_id):
    """View a specific profile"""
    try:
        profile = profile_service.get_profile(profile_id)
        return render_template("view_profile.html", profile=profile)

    except NotFoundError as e:
        flash(f"Profile not found: {profile_id}", "error")
        return redirect(url_for("profiles.list_profiles")), 404
    except Exception as e:
        logger.error(f"Error viewing profile: {e}")
        flash("Error loading profile", "error")
        return redirect(url_for("profiles.list_profiles"))


@profiles_bp.route("/<profile_id>/edit", methods=["GET", "POST"])
def edit_profile(profile_id):
    """Edit a profile"""
    if request.method == "GET":
        try:
            profile = profile_service.get_profile(profile_id)
            return render_template(
                "create_profile.html", profile=profile, edit_mode=True
            )
        except NotFoundError:
            flash("Profile not found", "error")
            return redirect(url_for("profiles.list_profiles"))

    try:
        profile_data = request.get_json() or request.form.to_dict()
        updated_profile = profile_service.update_profile(profile_id, profile_data)

        return jsonify(
            {
                "success": True,
                "message": "Profile updated successfully",
                "profile": updated_profile.__dict__
                if hasattr(updated_profile, "__dict__")
                else updated_profile,
            }
        ), 200

    except ValidationError as e:
        return jsonify({"success": False, "error": str(e), "code": e.code}), 422
    except NotFoundError as e:
        return jsonify({"success": False, "error": str(e), "code": "NOT_FOUND"}), 404
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        return jsonify({"success": False, "error": "Failed to update profile"}), 500


@profiles_bp.route("", methods=["GET"])
def list_profiles():
    """List all profiles with pagination"""
    try:
        skip = max(0, int(request.args.get("skip", 0)))
        limit = min(100, max(1, int(request.args.get("limit", 20))))

        profiles, total = profile_service.list_profiles(skip=skip, limit=limit)

        return jsonify(
            {
                "success": True,
                "profiles": [
                    p.__dict__ if hasattr(p, "__dict__") else p for p in profiles
                ],
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        ), 200

    except ValidationError as e:
        return jsonify({"success": False, "error": str(e), "code": e.code}), 422
    except Exception as e:
        logger.error(f"Error listing profiles: {e}")
        return jsonify({"success": False, "error": "Failed to list profiles"}), 500


@profiles_bp.route("/search", methods=["GET"])
def search_profiles():
    """Search profiles by name or email"""
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
                "results": [
                    r.__dict__ if hasattr(r, "__dict__") else r for r in results
                ],
                "count": len(results),
            }
        ), 200

    except ValidationError as e:
        return jsonify({"success": False, "error": str(e), "code": e.code}), 422
    except Exception as e:
        logger.error(f"Error searching profiles: {e}")
        return jsonify({"success": False, "error": "Failed to search profiles"}), 500


@profiles_bp.route("/<profile_id>", methods=["DELETE"])
def delete_profile(profile_id):
    """Delete a profile"""
    try:
        success = profile_service.delete_profile(profile_id)

        return jsonify(
            {"success": True, "message": "Profile deleted successfully"}
        ), 200

    except NotFoundError as e:
        return jsonify({"success": False, "error": str(e), "code": "NOT_FOUND"}), 404
    except Exception as e:
        logger.error(f"Error deleting profile: {e}")
        return jsonify({"success": False, "error": "Failed to delete profile"}), 500


@profiles_bp.route("/<profile_id>/skills", methods=["POST"])
def add_skill(profile_id):
    """Add a skill to a profile"""
    try:
        skill_data = request.get_json()
        profile_service.add_skill_to_profile(profile_id, skill_data)

        return jsonify({"success": True, "message": "Skill added successfully"}), 201

    except ValidationError as e:
        return jsonify({"success": False, "error": str(e), "code": e.code}), 422
    except NotFoundError as e:
        return jsonify({"success": False, "error": str(e), "code": "NOT_FOUND"}), 404
    except Exception as e:
        logger.error(f"Error adding skill: {e}")
        return jsonify({"success": False, "error": "Failed to add skill"}), 500


@profiles_bp.route("/<profile_id>/skills/<skill_id>", methods=["DELETE"])
def remove_skill(profile_id, skill_id):
    """Remove a skill from a profile"""
    try:
        profile_service.remove_skill_from_profile(profile_id, skill_id)

        return jsonify({"success": True, "message": "Skill removed successfully"}), 200

    except NotFoundError as e:
        return jsonify({"success": False, "error": str(e), "code": "NOT_FOUND"}), 404
    except Exception as e:
        logger.error(f"Error removing skill: {e}")
        return jsonify({"success": False, "error": "Failed to remove skill"}), 500


@profiles_bp.route("/stats", methods=["GET"])
def profile_stats():
    """Get profile statistics"""
    try:
        stats = profile_service.get_profile_stats()

        return jsonify({"success": True, "stats": stats}), 200

    except Exception as e:
        logger.error(f"Error getting profile stats: {e}")
        return jsonify(
            {"success": False, "error": "Failed to retrieve statistics"}
        ), 500
