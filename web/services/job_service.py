"""
Job Service for managing job operations.

Handles job CRUD operations, job fetching, job searching, and job statistics.
Provides a clean separation between business logic and route handlers.
"""

import logging
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import requests

from web.services.base import BaseService, ValidationError, NotFoundError

logger = logging.getLogger(__name__)


@dataclass
class JobData:
    """Represents a job opportunity"""

    job_id: str
    title: str
    company: str
    location: str
    job_type: str  # e.g., "Full-time", "Part-time", "Contract"
    salary_min: Optional[float] = None
    salary_max: Optional[float] = None
    currency: str = "SGD"
    description: str = ""
    requirements: List[str] = field(default_factory=list)
    skills_required: List[str] = field(default_factory=list)
    experience_years_min: int = 0
    experience_years_max: Optional[int] = None
    industry: str = ""
    posted_date: Optional[datetime] = None
    url: str = ""
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "job_id": self.job_id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "job_type": self.job_type,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "currency": self.currency,
            "description": self.description,
            "requirements": self.requirements,
            "skills_required": self.skills_required,
            "experience_years_min": self.experience_years_min,
            "experience_years_max": self.experience_years_max,
            "industry": self.industry,
            "posted_date": self.posted_date.isoformat() if self.posted_date else None,
            "url": self.url,
            "is_active": self.is_active,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JobData":
        """Create from dictionary"""
        return cls(
            job_id=data.get("job_id", ""),
            title=data.get("title", ""),
            company=data.get("company", ""),
            location=data.get("location", ""),
            job_type=data.get("job_type", "Full-time"),
            salary_min=data.get("salary_min"),
            salary_max=data.get("salary_max"),
            currency=data.get("currency", "SGD"),
            description=data.get("description", ""),
            requirements=data.get("requirements", []),
            skills_required=data.get("skills_required", []),
            experience_years_min=data.get("experience_years_min", 0),
            experience_years_max=data.get("experience_years_max"),
            industry=data.get("industry", ""),
            posted_date=datetime.fromisoformat(data["posted_date"])
            if data.get("posted_date")
            else None,
            url=data.get("url", ""),
            is_active=data.get("is_active", True),
            metadata=data.get("metadata", {}),
        )


class JobService(BaseService):
    """Service for managing job operations"""

    # FindSGJobs API configuration
    FINDSGJOBS_API_URL = "https://www.findsgjobs.com/apis/job/searchable"
    JOBS_PER_PAGE = 20
    DEFAULT_PAGES_TO_FETCH = 5

    def __init__(self, storage=None):
        """
        Initialize JobService

        Args:
            storage: Storage backend for jobs (e.g., database session)
        """
        super().__init__()
        self.storage = storage

    def validate_job_data(self, job_data: Dict[str, Any]) -> None:
        """
        Validate job data

        Args:
            job_data: Job data to validate

        Raises:
            ValidationError: If validation fails
        """
        # Required fields
        self.validate_required_fields(
            job_data, ["job_id", "title", "company", "location", "job_type"]
        )

        # Field type validation
        self.validate_field_type(job_data, "title", str)
        self.validate_field_type(job_data, "company", str)
        self.validate_field_type(job_data, "location", str)
        self.validate_field_type(job_data, "job_type", str)
        self.validate_field_type(job_data, "description", str, allow_none=True)
        self.validate_field_type(job_data, "requirements", list, allow_none=True)
        self.validate_field_type(job_data, "skills_required", list, allow_none=True)
        self.validate_field_type(job_data, "salary_min", (int, float), allow_none=True)
        self.validate_field_type(job_data, "salary_max", (int, float), allow_none=True)
        self.validate_field_type(job_data, "experience_years_min", int, allow_none=True)
        self.validate_field_type(job_data, "experience_years_max", int, allow_none=True)

        # String length validation
        self.validate_string_length(job_data, "title", min_length=3, max_length=200)
        self.validate_string_length(job_data, "company", min_length=2, max_length=100)
        self.validate_string_length(job_data, "location", min_length=2, max_length=100)

        # Job type validation
        valid_job_types = [
            "Full-time",
            "Part-time",
            "Contract",
            "Temporary",
            "Freelance",
        ]
        self.validate_in_choices(job_data, "job_type", valid_job_types)

        # Salary validation
        if job_data.get("salary_min") and job_data.get("salary_max"):
            if job_data["salary_min"] > job_data["salary_max"]:
                raise ValidationError(
                    "salary_min must be less than or equal to salary_max",
                    code="INVALID_SALARY_RANGE",
                )

        # Experience validation
        if job_data.get("experience_years_min") and job_data.get(
            "experience_years_max"
        ):
            if job_data["experience_years_min"] > job_data["experience_years_max"]:
                raise ValidationError(
                    "experience_years_min must be less than or equal to experience_years_max",
                    code="INVALID_EXPERIENCE_RANGE",
                )

        self.log_info(f"Validated job data for: {job_data.get('title')}")

    def create_job(self, job_data: Dict[str, Any]) -> JobData:
        """
        Create a new job

        Args:
            job_data: Job data

        Returns:
            JobData: Created job

        Raises:
            ValidationError: If validation fails
        """
        self.validate_job_data(job_data)
        job = JobData.from_dict(job_data)
        self.log_info(f"Created job: {job.title} at {job.company}")
        return job

    def get_job(self, job_id: str) -> JobData:
        """
        Get a job by ID

        Args:
            job_id: Job ID

        Returns:
            JobData: Job data

        Raises:
            NotFoundError: If job not found
        """
        if not job_id:
            raise ValidationError("job_id is required", code="EMPTY_JOB_ID")

        # Try to fetch from storage
        if self.storage:
            try:
                job = self.storage.get_job(job_id)
                if job:
                    return job
            except Exception as e:
                self.log_warning(f"Error fetching job from storage: {e}")

        raise NotFoundError(f"Job not found: {job_id}", code="JOB_NOT_FOUND")

    def list_jobs(
        self,
        skip: int = 0,
        limit: int = 50,
        filter_by: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[JobData], int]:
        """
        List jobs with pagination

        Args:
            skip: Number of jobs to skip
            limit: Maximum number of jobs to return
            filter_by: Filter criteria (e.g., {"location": "Singapore"})

        Returns:
            Tuple of (jobs, total_count)
        """
        if skip < 0:
            raise ValidationError("skip must be >= 0", code="INVALID_SKIP")
        if limit < 1 or limit > 500:
            raise ValidationError(
                "limit must be between 1 and 500", code="INVALID_LIMIT"
            )

        filter_by = filter_by or {}

        self.log_info(f"Listing jobs: skip={skip}, limit={limit}, filters={filter_by}")

        # Return empty list if no storage
        if not self.storage:
            return [], 0

        try:
            jobs, total = self.storage.list_jobs(
                skip=skip, limit=limit, filter_by=filter_by
            )
            return jobs, total
        except Exception as e:
            self.log_error(f"Error listing jobs: {e}")
            raise

    def search_jobs(self, query: str, limit: int = 20) -> List[JobData]:
        """
        Search jobs by keyword

        Args:
            query: Search query (job title, company, location, skills)
            limit: Maximum results

        Returns:
            List of matching jobs
        """
        if not query or not query.strip():
            raise ValidationError("query cannot be empty", code="EMPTY_QUERY")

        query = query.strip().lower()
        limit = max(1, min(limit, 100))

        self.log_info(f"Searching jobs: query='{query}', limit={limit}")

        if not self.storage:
            return []

        try:
            jobs = self.storage.search_jobs(query=query, limit=limit)
            return jobs
        except Exception as e:
            self.log_error(f"Error searching jobs: {e}")
            raise

    def fetch_from_findsgjobs_api(self, pages: int = 5) -> Tuple[List[JobData], int]:
        """
        Fetch jobs from FindSGJobs API

        Args:
            pages: Number of pages to fetch (20 jobs per page)

        Returns:
            Tuple of (jobs_fetched, errors_count)

        Raises:
            ValidationError: If pages is invalid
        """
        if pages < 1 or pages > 10:
            raise ValidationError(
                "pages must be between 1 and 10", code="INVALID_PAGES"
            )

        self.log_info(f"Fetching jobs from FindSGJobs API ({pages} pages)...")

        all_jobs = []
        error_count = 0

        try:
            for page in range(1, pages + 1):
                try:
                    self.log_info(f"Fetching page {page}...")

                    params = {
                        "page": page,
                        "items per page": self.JOBS_PER_PAGE,
                    }

                    response = requests.get(
                        self.FINDSGJOBS_API_URL, params=params, timeout=30
                    )
                    response.raise_for_status()

                    api_data = response.json()

                    if api_data.get("data", {}).get("result"):
                        page_jobs = api_data["data"]["result"]

                        # Process each job
                        for job_data in page_jobs:
                            try:
                                job = self._parse_findsgjobs_job(job_data)
                                all_jobs.append(job)
                            except Exception as e:
                                self.log_warning(f"Error parsing job: {e}")
                                error_count += 1

                        self.log_info(f"Page {page}: Found {len(page_jobs)} jobs")
                    else:
                        self.log_info(f"Page {page}: No job data found")
                        break

                except requests.exceptions.RequestException as e:
                    self.log_error(f"Error fetching page {page}: {e}")
                    error_count += 1
                    break

            self.log_info(
                f"Fetched {len(all_jobs)} jobs from API (errors: {error_count})"
            )
            return all_jobs, error_count

        except Exception as e:
            self.log_error(f"Error fetching from FindSGJobs API: {e}")
            raise

    def _parse_findsgjobs_job(self, job_data: Dict[str, Any]) -> JobData:
        """
        Parse a job from FindSGJobs API format

        Args:
            job_data: Raw job data from API

        Returns:
            JobData object

        Raises:
            ValidationError: If parsing fails
        """
        try:
            # Extract required fields
            job_id = job_data.get("id", "")
            title = job_data.get("title", "")
            company = job_data.get("company", "")
            location = job_data.get("location", "")

            if not all([job_id, title, company, location]):
                raise ValueError("Missing required job fields")

            # Extract optional fields
            description = job_data.get("description", "")
            job_type = job_data.get("job_type", "Full-time")
            url = job_data.get("url", "")

            # Extract salary information
            salary_min = job_data.get("salary_min")
            salary_max = job_data.get("salary_max")

            # Extract experience requirement
            experience_years_min = job_data.get("experience_years_min", 0)
            experience_years_max = job_data.get("experience_years_max")

            # Extract skills and requirements
            skills_required = job_data.get("skills_required", [])
            if isinstance(skills_required, str):
                skills_required = [s.strip() for s in skills_required.split(",")]

            requirements = job_data.get("requirements", [])
            if isinstance(requirements, str):
                requirements = [r.strip() for r in requirements.split(",")]

            # Extract industry
            industry = job_data.get("industry", "")

            # Create JobData
            job = JobData(
                job_id=str(job_id),
                title=self.sanitize_string(title, max_length=200),
                company=self.sanitize_string(company, max_length=100),
                location=self.sanitize_string(location, max_length=100),
                job_type=job_type,
                salary_min=salary_min,
                salary_max=salary_max,
                description=self.sanitize_string(description, max_length=5000),
                requirements=requirements,
                skills_required=skills_required,
                experience_years_min=experience_years_min,
                experience_years_max=experience_years_max,
                industry=self.sanitize_string(industry, max_length=100),
                url=url,
                is_active=job_data.get("is_active", True),
            )

            return job

        except Exception as e:
            self.log_error(f"Error parsing FindSGJobs job: {e}")
            raise ValidationError(
                f"Failed to parse job data: {str(e)}", code="PARSE_ERROR"
            )

    def get_job_statistics(self) -> Dict[str, Any]:
        """
        Get job statistics

        Returns:
            Dictionary with statistics
        """
        self.log_info("Generating job statistics...")

        if not self.storage:
            return {}

        try:
            stats = self.storage.get_job_statistics()
            return stats
        except Exception as e:
            self.log_error(f"Error getting job statistics: {e}")
            return {}

    def update_job(self, job_id: str, job_data: Dict[str, Any]) -> JobData:
        """
        Update an existing job

        Args:
            job_id: Job ID
            job_data: Updated job data

        Returns:
            Updated JobData

        Raises:
            NotFoundError: If job not found
            ValidationError: If validation fails
        """
        # Validate input
        if not job_id:
            raise ValidationError("job_id is required", code="EMPTY_JOB_ID")

        self.validate_job_data(job_data)

        self.log_info(f"Updating job {job_id}")

        if not self.storage:
            raise NotFoundError("Storage not available", code="NO_STORAGE")

        try:
            job = self.storage.update_job(job_id, job_data)
            return job
        except Exception as e:
            self.log_error(f"Error updating job: {e}")
            raise

    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job (soft delete - mark as inactive)

        Args:
            job_id: Job ID

        Returns:
            True if deleted

        Raises:
            NotFoundError: If job not found
        """
        if not job_id:
            raise ValidationError("job_id is required", code="EMPTY_JOB_ID")

        self.log_info(f"Deleting job {job_id}")

        if not self.storage:
            raise NotFoundError("Storage not available", code="NO_STORAGE")

        try:
            result = self.storage.delete_job(job_id)
            return result
        except Exception as e:
            self.log_error(f"Error deleting job: {e}")
            raise
