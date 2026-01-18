"""
Profile service for managing user profiles.

Handles all profile-related business logic:
- Creating new profiles
- Retrieving profile information
- Updating existing profiles
- Deleting profiles
- Listing and filtering profiles
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from web.services.base import BaseService, ValidationError, NotFoundError, ServiceError


class ProfileService(BaseService):
    """Service for profile management operations."""

    def __init__(self, storage_service=None):
        """
        Initialize profile service.

        Args:
            storage_service: Service for profile storage (database or file)
        """
        super().__init__()
        self.storage = storage_service

    def validate_profile_data(self, profile_data: Dict[str, Any]) -> None:
        """
        Validate profile data structure.

        Args:
            profile_data: Profile data to validate

        Raises:
            ValidationError: If validation fails
        """
        # Required fields
        required_fields = ["name", "email"]
        self.validate_required_fields(profile_data, required_fields)

        # Field types
        self.validate_field_type(profile_data, "name", str)
        self.validate_field_type(profile_data, "email", str)
        self.validate_field_type(profile_data, "skills", list, allow_none=True)

        # Field lengths
        self.validate_string_length(profile_data, "name", min_length=2, max_length=200)
        self.validate_string_length(profile_data, "email", min_length=5, max_length=255)

        # Experience level validation
        if "experience_level" in profile_data:
            self.validate_in_choices(
                profile_data,
                "experience_level",
                ["entry", "junior", "mid", "senior", "expert"],
            )

        # Total years experience
        if "total_years_experience" in profile_data:
            years = profile_data["total_years_experience"]
            if not isinstance(years, (int, float)):
                raise ValidationError("total_years_experience must be a number")
            if years < 0 or years > 70:
                raise ValidationError("total_years_experience must be between 0 and 70")

        # Validate skills if present
        if profile_data.get("skills"):
            self._validate_skills(profile_data["skills"])

    def _validate_skills(self, skills: List[Dict[str, Any]]) -> None:
        """
        Validate skill data structure.

        Args:
            skills: List of skills to validate

        Raises:
            ValidationError: If skill validation fails
        """
        if not isinstance(skills, list):
            raise ValidationError("Skills must be a list")

        for i, skill in enumerate(skills):
            if not isinstance(skill, dict):
                raise ValidationError(f"Skill {i} must be a dictionary")

            # Required fields
            if "skill_id" not in skill or "level" not in skill:
                raise ValidationError(
                    f"Skill {i} missing required fields: skill_id, level"
                )

            # Validate skill level
            valid_levels = ["beginner", "intermediate", "advanced", "expert"]
            if skill["level"] not in valid_levels:
                raise ValidationError(
                    f"Skill {i} level must be one of: {', '.join(valid_levels)}"
                )

    def create_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new profile.

        Args:
            profile_data: Profile data (name, email, skills, experience, etc.)

        Returns:
            Created profile with ID

        Raises:
            ValidationError: If profile data is invalid
        """
        # Sanitize and validate
        profile_data["name"] = self.sanitize_string(
            profile_data.get("name", ""), max_length=200
        )
        profile_data["email"] = self.sanitize_string(
            profile_data.get("email", ""), max_length=255
        )

        self.validate_profile_data(profile_data)

        # Add metadata
        now = datetime.now().isoformat()
        profile = {
            **profile_data,
            "created_at": now,
            "updated_at": now,
        }

        # Persist profile
        if self.storage:
            saved_profile = self.storage.save_profile(profile)
            self.log_info(
                f"Profile created: {saved_profile.get('profile_id', 'unknown')}"
            )
            return saved_profile

        return profile

    def get_profile(self, profile_id: str) -> Dict[str, Any]:
        """
        Get profile by ID.

        Args:
            profile_id: Profile identifier

        Returns:
            Profile data

        Raises:
            NotFoundError: If profile not found
        """
        if not self.storage:
            raise ServiceError("Storage service not configured")

        profile = self.storage.get_profile(profile_id)
        if not profile:
            raise NotFoundError("Profile", profile_id)

        self.log_info(f"Profile retrieved: {profile_id}")
        return profile

    def update_profile(
        self, profile_id: str, profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update existing profile.

        Args:
            profile_id: Profile identifier
            profile_data: Fields to update

        Returns:
            Updated profile

        Raises:
            NotFoundError: If profile not found
            ValidationError: If update data is invalid
        """
        # Get existing profile
        existing = self.get_profile(profile_id)

        # Merge and validate
        updated = {**existing, **profile_data}
        self.validate_profile_data(updated)

        # Update timestamp
        updated["updated_at"] = datetime.now().isoformat()

        # Persist changes
        if self.storage:
            saved_profile = self.storage.update_profile(profile_id, updated)
            self.log_info(f"Profile updated: {profile_id}")
            return saved_profile

        return updated

    def delete_profile(self, profile_id: str) -> bool:
        """
        Delete profile.

        Args:
            profile_id: Profile identifier

        Returns:
            True if deleted successfully

        Raises:
            NotFoundError: If profile not found
        """
        # Verify exists
        self.get_profile(profile_id)

        # Delete
        if self.storage:
            self.storage.delete_profile(profile_id)
            self.log_info(f"Profile deleted: {profile_id}")
            return True

        return False

    def list_profiles(
        self, skip: int = 0, limit: int = 20, filter_by: Optional[Dict[str, Any]] = None
    ) -> tuple[List[Dict[str, Any]], int]:
        """
        List profiles with pagination and filtering.

        Args:
            skip: Number of profiles to skip
            limit: Number of profiles to return
            filter_by: Filter criteria (experience_level, total_years_experience, etc.)

        Returns:
            Tuple of (profiles list, total count)
        """
        if not self.storage:
            return [], 0

        profiles, total = self.storage.list_profiles(
            skip=skip, limit=limit, filter_by=filter_by
        )

        self.log_info(f"Listed {len(profiles)} profiles (total: {total})")
        return profiles, total

    def search_profiles(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search profiles by name or email.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching profiles
        """
        if not self.storage:
            return []

        self.validate_string_length(
            {"query": query}, "query", min_length=1, max_length=100
        )

        profiles = self.storage.search_profiles(query, limit=limit)
        self.log_info(f"Search completed: '{query}' found {len(profiles)} results")
        return profiles

    def get_profile_stats(self) -> Dict[str, Any]:
        """
        Get profile statistics.

        Returns:
            Dictionary with profile statistics
        """
        if not self.storage:
            return {
                "total_profiles": 0,
                "avg_experience": 0,
                "experience_distribution": {},
            }

        stats = self.storage.get_profile_stats()
        return stats

    def add_skill_to_profile(
        self, profile_id: str, skill_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Add a skill to profile.

        Args:
            profile_id: Profile identifier
            skill_data: Skill information (skill_id, level, etc.)

        Returns:
            Updated profile

        Raises:
            NotFoundError: If profile not found
            ValidationError: If skill data invalid
        """
        profile = self.get_profile(profile_id)

        # Validate skill
        self._validate_skills([skill_data])

        # Add skill (avoid duplicates)
        skills = profile.get("skills", [])
        skill_ids = {s.get("skill_id") for s in skills}

        if skill_data.get("skill_id") not in skill_ids:
            skills.append(skill_data)
            profile["skills"] = skills

            return self.update_profile(profile_id, profile)

        return profile

    def remove_skill_from_profile(
        self, profile_id: str, skill_id: str
    ) -> Dict[str, Any]:
        """
        Remove a skill from profile.

        Args:
            profile_id: Profile identifier
            skill_id: Skill identifier

        Returns:
            Updated profile

        Raises:
            NotFoundError: If profile not found
        """
        profile = self.get_profile(profile_id)

        # Remove skill
        skills = profile.get("skills", [])
        profile["skills"] = [s for s in skills if s.get("skill_id") != skill_id]

        return self.update_profile(profile_id, profile)
