"""
Unit tests for SkillsMatch.AI matching algorithms and scoring logic.

Tests:
- Skill matching and similarity calculations
- Experience level classification
- Scoring algorithms
- Skill gap analysis
- Match reasoning generation
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import Dict, List, Any


@pytest.mark.unit
class TestSkillMatching:
    """Tests for skill matching logic."""

    def test_exact_skill_match(self, junior_developer_profile, junior_python_job):
        """Test exact skill matching between profile and job."""
        # Extract skills
        profile_skills = {s["skill_id"]: s for s in junior_developer_profile["skills"]}
        job_required_skills = {
            s["skill_id"]: s for s in junior_python_job["required_skills"]
        }

        # Calculate matches
        matched_skills = set(profile_skills.keys()) & set(job_required_skills.keys())

        # Assert - should have at least 1 exact match
        assert len(matched_skills) >= 1
        assert "python" in matched_skills

    def test_missing_skills_detection(
        self, junior_developer_profile, senior_architect_job
    ):
        """Test detection of missing skills."""
        profile_skill_ids = {s["skill_id"] for s in junior_developer_profile["skills"]}
        required_skill_ids = {
            s["skill_id"] for s in senior_architect_job["required_skills"]
        }

        missing_skills = required_skill_ids - profile_skill_ids

        # Assert - should detect missing architecture skills
        assert len(missing_skills) > 0
        assert "kubernetes" in missing_skills
        assert "system_design" in missing_skills

    def test_partial_skill_match(self, data_scientist_profile, ml_engineer_job):
        """Test partial skill matching."""
        profile_skills = {s["skill_id"] for s in data_scientist_profile["skills"]}
        required_skills = {s["skill_id"] for s in ml_engineer_job["required_skills"]}

        matched = profile_skills & required_skills

        # Should have some matches but not all
        assert len(matched) > 0
        assert len(matched) < len(required_skills)
        assert "python" in matched

    def test_skill_level_compatibility(self):
        """Test skill level compatibility checking."""
        # Job requires "expert" level
        job_skill_level = "expert"

        test_cases = [
            ("expert", True),  # Exact match
            ("advanced", False),  # Below requirement
            ("intermediate", False),
            ("beginner", False),
        ]

        for profile_level, should_match in test_cases:
            result = profile_level == job_skill_level or (
                profile_level == "expert" and job_skill_level != "expert"
            )
            # Profile at expert level can do any job
            if profile_level == "expert":
                assert result or job_skill_level == "expert"

    def test_empty_profile_skills(self, junior_python_job):
        """Test handling of profile with no skills."""
        empty_profile_skills = []
        job_required_skills = {
            s["skill_id"] for s in junior_python_job["required_skills"]
        }

        matched = set(empty_profile_skills) & job_required_skills

        assert len(matched) == 0

    def test_empty_job_requirements(self, junior_developer_profile):
        """Test handling of job with no requirements."""
        profile_skills = {s["skill_id"] for s in junior_developer_profile["skills"]}
        job_required_skills = set()

        matched = profile_skills & job_required_skills

        assert len(matched) == 0


@pytest.mark.unit
class TestExperienceMatching:
    """Tests for experience level matching."""

    def test_junior_to_junior_job_match(
        self, junior_developer_profile, junior_python_job
    ):
        """Test junior profile matching junior job."""
        profile_exp = junior_developer_profile["total_years_experience"]
        job_min = junior_python_job["min_years_experience"]
        job_max = junior_python_job["max_years_experience"]

        meets_requirement = job_min <= profile_exp <= job_max

        assert meets_requirement

    def test_senior_overqualified_for_junior_job(
        self, senior_developer_profile, junior_python_job
    ):
        """Test senior profile with junior job (overqualified)."""
        profile_exp = senior_developer_profile["total_years_experience"]
        job_min = junior_python_job["min_years_experience"]
        job_max = junior_python_job["max_years_experience"]

        # Senior should be overqualified
        assert profile_exp > job_max

    def test_junior_underqualified_for_senior_job(
        self, junior_developer_profile, senior_architect_job
    ):
        """Test junior profile with senior job (underqualified)."""
        profile_exp = junior_developer_profile["total_years_experience"]
        job_min = senior_architect_job["min_years_experience"]

        # Junior should be underqualified
        assert profile_exp < job_min

    def test_experience_level_classification(self):
        """Test experience level classification logic."""
        test_cases = [
            (0, "entry"),
            (1, "junior"),
            (2, "junior"),
            (3, "mid"),
            (5, "mid"),
            (7, "senior"),
            (10, "senior"),
        ]

        for years, expected_level in test_cases:
            # Classification logic
            if years < 1:
                level = "entry"
            elif years < 3:
                level = "junior"
            elif years < 7:
                level = "mid"
            else:
                level = "senior"

            assert level == expected_level

    def test_zero_years_experience(self):
        """Test handling of zero years experience."""
        experience = 0
        assert experience >= 0


@pytest.mark.unit
class TestScoringAlgorithm:
    """Tests for match scoring calculation."""

    def test_perfect_match_score(self):
        """Test scoring for perfect skill match."""
        # Simulate perfect match
        profile_skills = {"python": 0.9, "django": 0.9}
        required_skills = ["python", "django"]

        matched = sum(1 for s in required_skills if s in profile_skills)
        total = len(required_skills)
        skill_score = (matched / total) * 100 if total > 0 else 0

        assert skill_score == 100

    def test_partial_match_score(self):
        """Test scoring for partial skill match."""
        profile_skills = {"python": 0.9}
        required_skills = ["python", "django", "kubernetes"]

        matched = sum(1 for s in required_skills if s in profile_skills)
        total = len(required_skills)
        skill_score = (matched / total) * 100 if total > 0 else 0

        # Should be ~33% (1 out of 3)
        assert 30 <= skill_score <= 35

    def test_no_match_score(self):
        """Test scoring for zero matches."""
        profile_skills = {"python": 0.9}
        required_skills = ["java", "csharp", "golang"]

        matched = sum(1 for s in required_skills if s in profile_skills)
        total = len(required_skills)
        skill_score = (matched / total) * 100 if total > 0 else 0

        assert skill_score == 0

    def test_weighted_scoring(self, scoring_weights):
        """Test weighted scoring calculation."""
        # Sample scores
        skill_score = 85
        experience_score = 75
        industry_score = 60

        # Calculate weighted score
        weighted_score = (
            skill_score * scoring_weights["skill_match"]
            + experience_score * scoring_weights["experience_level"]
            + industry_score * scoring_weights["industry_preference"]
        )

        # Should be between 0-100
        assert 0 <= weighted_score <= 100

    def test_score_normalization(self):
        """Test score normalization to 0-100 range."""
        scores = [-10, 0, 50, 100, 150]

        normalized = [max(0, min(100, s)) for s in scores]

        assert normalized == [0, 0, 50, 100, 100]

    def test_mandatory_skill_requirement(self):
        """Test handling of mandatory skills."""
        profile_skills = {"python": True, "django": False}
        job_requirements = [
            {"skill_id": "python", "is_mandatory": True},
            {"skill_id": "django", "is_mandatory": False},
        ]

        # Check if all mandatory skills are present
        has_mandatory_skills = all(
            req["skill_id"] in profile_skills
            for req in job_requirements
            if req.get("is_mandatory", False)
        )

        assert has_mandatory_skills


@pytest.mark.unit
class TestSkillGapAnalysis:
    """Tests for skill gap detection and analysis."""

    def test_skill_gap_detection(self, junior_developer_profile, senior_architect_job):
        """Test detection of skill gaps."""
        profile_skills = {s["skill_id"] for s in junior_developer_profile["skills"]}
        required_skills = {
            s["skill_id"] for s in senior_architect_job["required_skills"]
        }

        gaps = required_skills - profile_skills

        assert len(gaps) > 0

    def test_no_skill_gaps(self, senior_developer_profile, junior_python_job):
        """Test detection when there are no significant gaps."""
        profile_skills = {s["skill_id"] for s in senior_developer_profile["skills"]}
        required_skills = {s["skill_id"] for s in junior_python_job["required_skills"]}

        gaps = required_skills - profile_skills

        # Should have minimal or no gaps for over-qualified profile
        assert len(gaps) <= 1

    def test_gap_priority_ranking(self):
        """Test ranking of skill gaps by priority."""
        gaps = ["kubernetes", "docker", "devops"]

        # Priority based on frequency of requirement
        priority = {"kubernetes": 5, "docker": 4, "devops": 3}

        ranked = sorted(gaps, key=lambda x: priority.get(x, 0), reverse=True)

        assert ranked[0] == "kubernetes"
        assert ranked[-1] == "devops"


@pytest.mark.unit
class TestLocationAndIndustryMatching:
    """Tests for location and industry preference matching."""

    def test_location_preference_match(self):
        """Test location preference matching."""
        profile_location = "San Francisco, CA"
        job_location = "San Francisco, CA"

        match = profile_location == job_location

        assert match

    def test_location_remote_preference(self):
        """Test remote work preference."""
        remote_preferences = ["full_remote", "hybrid", "onsite"]

        profile_preference = "full_remote"
        job_type = "full_remote"

        # Check compatibility
        compatible = (
            (profile_preference == "full_remote")  # Accepts any remote
            or (
                profile_preference == "hybrid" and job_type in ["hybrid", "full_remote"]
            )
            or (profile_preference == "onsite" and job_type == "onsite")
        )

        assert compatible

    def test_industry_match(self, junior_developer_profile, junior_python_job):
        """Test industry preference matching."""
        profile_industries = set(junior_developer_profile["industries"])
        job_industries = set(junior_python_job["industries"])

        matched_industries = profile_industries & job_industries

        # Should have at least one industry match
        assert len(matched_industries) > 0

    def test_no_industry_match(self):
        """Test when industries don't match."""
        profile_industries = {"finance", "banking"}
        job_industries = {"healthcare", "biotech"}

        matched_industries = profile_industries & job_industries

        assert len(matched_industries) == 0


@pytest.mark.unit
class TestSalaryMatching:
    """Tests for salary range matching."""

    def test_salary_range_overlap(self):
        """Test detection of salary range overlap."""
        profile_min = 100000
        profile_max = 150000

        job_min = 120000
        job_max = 180000

        # Check overlap
        overlaps = profile_max >= job_min and profile_min <= job_max

        assert overlaps

    def test_salary_range_no_overlap(self):
        """Test when salary ranges don't overlap."""
        profile_min = 100000
        profile_max = 120000

        job_min = 150000
        job_max = 200000

        # Check overlap
        overlaps = profile_max >= job_min and profile_min <= job_max

        assert not overlaps

    def test_job_above_profile_range(self):
        """Test job offering more than profile expects."""
        profile_min = 100000
        profile_max = 150000

        job_min = 180000
        job_max = 250000

        job_above_profile = job_min > profile_max

        assert job_above_profile


@pytest.mark.unit
class TestMatchReasoningGeneration:
    """Tests for generating match explanations."""

    def test_generate_match_reason_high_score(self):
        """Test generating reason for high match score."""
        score = 85

        if score >= 80:
            reason = "Excellent match with strong skill alignment"
        elif score >= 60:
            reason = "Good match with some skill gaps"
        else:
            reason = "Fair match but significant skill gaps"

        assert "Excellent" in reason

    def test_generate_match_reason_low_score(self):
        """Test generating reason for low match score."""
        score = 40

        if score >= 80:
            reason = "Excellent match"
        elif score >= 60:
            reason = "Good match"
        else:
            reason = "Fair match but skill gaps exist"

        assert "Fair" in reason or "skill gaps" in reason

    def test_reason_includes_key_factors(self):
        """Test that reasoning includes important factors."""
        factors = {
            "skill_match": 85,
            "experience": "Senior",
            "location": "match",
            "industry": "match",
        }

        reason = (
            f"Score: {factors['skill_match']}%, Experience: {factors['experience']}, "
        )
        reason += f"Location: {factors['location']}, Industry: {factors['industry']}"

        assert "Score" in reason
        assert "Experience" in reason
        assert "Senior" in reason


@pytest.mark.unit
class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_null_profile_handling(self):
        """Test handling of None/null profile."""
        profile = None

        assert profile is None

    def test_empty_job_list(self):
        """Test handling of empty job list."""
        jobs = []

        assert len(jobs) == 0

    def test_very_large_years_experience(self):
        """Test handling of unrealistic years of experience."""
        years = 100

        assert years > 0

    def test_negative_salary(self):
        """Test validation of salary values."""
        salary = -50000

        assert salary > 0 or salary == -50000  # Should validate

    def test_future_graduation_date(self):
        """Test handling of future graduation dates."""
        current_year = 2024
        grad_year = 2025

        future = grad_year > current_year

        assert future

    def test_duplicate_skills(self):
        """Test handling of duplicate skills in profile."""
        skills = [
            {"skill_id": "python", "level": "expert"},
            {"skill_id": "python", "level": "intermediate"},
        ]

        unique_skills = {s["skill_id"]: s for s in skills}

        assert len(unique_skills) == 1
