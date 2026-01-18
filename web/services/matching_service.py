"""
Matching service for job-to-profile matching operations.

Handles all matching-related business logic:
- Matching profiles to job listings
- Calculating match scores
- Generating match explanations
- Filtering and ranking matches
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import math

from web.services.base import BaseService, ValidationError


@dataclass
class MatchResult:
    """Result of matching a profile to a job."""

    job_id: str
    job_title: str
    company: str
    match_score: float  # 0-100
    skill_match_percentage: float
    experience_match: bool
    salary_match: bool
    location_match: bool
    reasons: List[str]
    skill_gaps: List[str]
    missing_skills: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "job_id": self.job_id,
            "job_title": self.job_title,
            "company": self.company,
            "match_score": round(self.match_score, 2),
            "skill_match_percentage": round(self.skill_match_percentage, 2),
            "experience_match": self.experience_match,
            "salary_match": self.salary_match,
            "location_match": self.location_match,
            "reasons": self.reasons,
            "skill_gaps": self.skill_gaps,
            "missing_skills": self.missing_skills,
        }


class MatchingService(BaseService):
    """Service for job-to-profile matching operations."""

    # Default matching weights
    DEFAULT_WEIGHTS = {
        "skill_match": 0.40,  # 40% weight
        "experience": 0.25,  # 25% weight
        "location": 0.15,  # 15% weight
        "salary": 0.10,  # 10% weight
        "industry": 0.10,  # 10% weight
    }

    def __init__(self):
        """Initialize matching service."""
        super().__init__()
        self.weights = self.DEFAULT_WEIGHTS.copy()

    def match_profile_to_jobs(
        self,
        profile: Dict[str, Any],
        jobs: List[Dict[str, Any]],
        min_score: float = 0.3,
    ) -> List[MatchResult]:
        """
        Match a profile against multiple jobs.

        Args:
            profile: User profile data
            jobs: List of job postings
            min_score: Minimum match score threshold (0-1)

        Returns:
            List of MatchResult sorted by score (highest first)
        """
        if min_score < 0 or min_score > 1:
            raise ValidationError("min_score must be between 0 and 1")

        matches = []

        for job in jobs:
            try:
                result = self.match_profile_to_job(profile, job)

                # Only include matches meeting threshold
                if result.match_score / 100 >= min_score:
                    matches.append(result)
            except Exception as e:
                self.log_error(f"Error matching job {job.get('job_id')}: {e}")
                continue

        # Sort by match score (highest first)
        matches.sort(key=lambda m: m.match_score, reverse=True)

        self.log_info(f"Matched profile to {len(matches)} of {len(jobs)} jobs")
        return matches

    def match_profile_to_job(
        self, profile: Dict[str, Any], job: Dict[str, Any]
    ) -> MatchResult:
        """
        Match a single profile to a single job.

        Args:
            profile: User profile
            job: Job posting

        Returns:
            MatchResult with detailed matching information
        """
        job_id = job.get("job_id", "unknown")
        job_title = job.get("title", "Unknown Position")
        company = job.get("company", "Unknown Company")

        try:
            # Calculate individual match components
            skill_score = self._calculate_skill_match(profile, job)
            experience_match = self._check_experience_match(profile, job)
            location_match = self._check_location_match(profile, job)
            salary_match = self._check_salary_match(profile, job)
            industry_match = self._check_industry_match(profile, job)

            # Calculate weighted overall score
            overall_score = self._calculate_overall_score(
                skill_score,
                experience_match,
                location_match,
                salary_match,
                industry_match,
            )

            # Generate explanation
            reasons = self._generate_match_reasons(
                profile,
                job,
                skill_score,
                experience_match,
                location_match,
                salary_match,
                industry_match,
                overall_score,
            )

            # Identify skill gaps
            skill_gaps = self._identify_skill_gaps(profile, job)
            missing_skills = self._get_missing_skills(profile, job)

            return MatchResult(
                job_id=job_id,
                job_title=job_title,
                company=company,
                match_score=overall_score,
                skill_match_percentage=skill_score * 100,
                experience_match=experience_match,
                salary_match=salary_match,
                location_match=location_match,
                reasons=reasons,
                skill_gaps=skill_gaps,
                missing_skills=missing_skills,
            )

        except Exception as e:
            self.log_error(f"Error calculating match for job {job_id}: {e}")
            raise

    def _calculate_skill_match(
        self, profile: Dict[str, Any], job: Dict[str, Any]
    ) -> float:
        """
        Calculate skill match percentage (0-1).

        Args:
            profile: User profile
            job: Job posting

        Returns:
            Skill match score 0-1
        """
        profile_skills = {s.get("skill_id") for s in profile.get("skills", [])}
        required_skills = {s.get("skill_id") for s in job.get("required_skills", [])}

        if not required_skills:
            return 1.0  # No requirements = perfect match

        matched_skills = len(profile_skills & required_skills)
        match_percentage = matched_skills / len(required_skills)

        return min(match_percentage, 1.0)

    def _check_experience_match(
        self, profile: Dict[str, Any], job: Dict[str, Any]
    ) -> bool:
        """
        Check if profile experience matches job requirements.

        Args:
            profile: User profile
            job: Job posting

        Returns:
            True if experience is acceptable
        """
        profile_years = profile.get("total_years_experience", 0)
        min_years = job.get("min_years_experience", 0)
        max_years = job.get("max_years_experience", 100)

        return min_years <= profile_years <= max_years

    def _check_location_match(
        self, profile: Dict[str, Any], job: Dict[str, Any]
    ) -> bool:
        """
        Check if profile location matches job location.

        Args:
            profile: User profile
            job: Job posting

        Returns:
            True if location matches
        """
        # If job is remote, it matches any location
        if job.get("remote_type") == "remote":
            return True

        # If job allows hybrid/remote, consider it a match if profile open to remote
        if job.get("remote_type") in ["hybrid", "remote"]:
            profile_remote = profile.get("open_to_remote", True)
            if profile_remote:
                return True

        # Check location match
        profile_location = profile.get("location", "").lower()
        job_location = job.get("location", "").lower()

        return profile_location == job_location

    def _check_salary_match(self, profile: Dict[str, Any], job: Dict[str, Any]) -> bool:
        """
        Check if salary ranges overlap.

        Args:
            profile: User profile
            job: Job posting

        Returns:
            True if salary ranges overlap or job is above profile minimum
        """
        profile_min = profile.get("salary_range", {}).get("min", 0)
        job_min = job.get("salary_range", {}).get("min", 0)
        job_max = job.get("salary_range", {}).get("max", job_min)

        # Job must overlap or exceed minimum acceptable
        return job_max >= profile_min

    def _check_industry_match(
        self, profile: Dict[str, Any], job: Dict[str, Any]
    ) -> bool:
        """
        Check if profile and job industries overlap.

        Args:
            profile: User profile
            job: Job posting

        Returns:
            True if industries overlap or no preference stated
        """
        profile_industries = set(profile.get("preferred_industries", []))
        job_industries = set(job.get("industries", []))

        if not profile_industries or not job_industries:
            return True  # No preference = match

        return bool(profile_industries & job_industries)

    def _calculate_overall_score(
        self,
        skill_score: float,
        experience_match: bool,
        location_match: bool,
        salary_match: bool,
        industry_match: bool,
    ) -> float:
        """
        Calculate weighted overall match score (0-100).

        Args:
            skill_score: Skill match percentage (0-1)
            experience_match: Whether experience matches
            location_match: Whether location matches
            salary_match: Whether salary matches
            industry_match: Whether industry matches

        Returns:
            Overall match score 0-100
        """
        score = 0.0

        # Skill component (40%)
        score += skill_score * self.weights["skill_match"] * 100

        # Experience component (25%)
        score += (1.0 if experience_match else 0.5) * self.weights["experience"] * 100

        # Location component (15%)
        score += (1.0 if location_match else 0.5) * self.weights["location"] * 100

        # Salary component (10%)
        score += (1.0 if salary_match else 0.5) * self.weights["salary"] * 100

        # Industry component (10%)
        score += (1.0 if industry_match else 0.5) * self.weights["industry"] * 100

        return min(score, 100.0)

    def _identify_skill_gaps(
        self, profile: Dict[str, Any], job: Dict[str, Any]
    ) -> List[str]:
        """Identify high-priority missing skills."""
        profile_skills = {s.get("skill_id") for s in profile.get("skills", [])}
        required_mandatory = [
            s for s in job.get("required_skills", []) if s.get("is_mandatory", False)
        ]

        gaps = []
        for skill in required_mandatory:
            if skill.get("skill_id") not in profile_skills:
                gaps.append(skill.get("skill_id", "unknown"))

        return gaps

    def _get_missing_skills(
        self, profile: Dict[str, Any], job: Dict[str, Any]
    ) -> List[str]:
        """Get all missing skills."""
        profile_skills = {s.get("skill_id") for s in profile.get("skills", [])}
        all_required = [s.get("skill_id") for s in job.get("required_skills", [])]

        return [skill for skill in all_required if skill not in profile_skills]

    def _generate_match_reasons(
        self,
        profile: Dict[str, Any],
        job: Dict[str, Any],
        skill_score: float,
        experience_match: bool,
        location_match: bool,
        salary_match: bool,
        industry_match: bool,
        overall_score: float,
    ) -> List[str]:
        """Generate human-readable match reasons."""
        reasons = []

        if overall_score >= 80:
            reasons.append(f"Excellent match ({overall_score:.0f}%)")
        elif overall_score >= 60:
            reasons.append(f"Good match ({overall_score:.0f}%)")
        elif overall_score >= 40:
            reasons.append(f"Fair match ({overall_score:.0f}%)")
        else:
            reasons.append(f"Potential match ({overall_score:.0f}%)")

        if skill_score >= 0.8:
            reasons.append("Strong skill alignment")
        elif skill_score >= 0.5:
            reasons.append("Partial skill match")
        else:
            reasons.append("Different skill set - growth opportunity")

        if experience_match:
            years = profile.get("total_years_experience", 0)
            min_years = job.get("min_years_experience", 0)
            if years >= min_years + 5:
                reasons.append(f"Well-qualified experience ({years} years)")
            else:
                reasons.append(f"Matching experience level ({years} years)")

        if location_match:
            if job.get("remote_type") == "remote":
                reasons.append("Remote work available")
            else:
                reasons.append(f"Location match: {job.get('location')}")

        if salary_match:
            reasons.append("Within expected salary range")

        if industry_match:
            reasons.append("Preferred industry match")

        return reasons
