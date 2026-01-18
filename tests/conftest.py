"""
Pytest configuration and shared fixtures for SkillsMatch.AI tests.

Provides:
- User profile fixtures (junior, senior, with various skill combinations)
- Job opportunity fixtures
- Mock AI/OpenAI responses
- Database session fixtures
- Sample data for testing
"""

import pytest
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, List, Any

# Add parent directory to path to allow importing from 'web' package
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configure pytest
pytest_plugins = []


# ============================================================================
# Profile Fixtures
# ============================================================================


@pytest.fixture
def junior_developer_profile() -> Dict[str, Any]:
    """Junior developer profile with Python and basic skills."""
    return {
        "profile_id": "junior_dev_001",
        "name": "Alex Junior",
        "email": "alex@example.com",
        "created_at": datetime.now().isoformat(),
        "experience_level": "junior",
        "total_years_experience": 2,
        "skills": [
            {
                "skill_id": "python",
                "skill_name": "Python",
                "category": "programming_languages",
                "level": "intermediate",
                "years_experience": 2,
                "verified": False,
            },
            {
                "skill_id": "javascript",
                "skill_name": "JavaScript",
                "category": "programming_languages",
                "level": "beginner",
                "years_experience": 1,
                "verified": False,
            },
            {
                "skill_id": "django",
                "skill_name": "Django",
                "category": "web_development",
                "level": "intermediate",
                "years_experience": 1,
                "verified": False,
            },
        ],
        "work_experience": [
            {
                "company": "StartupXYZ",
                "position": "Junior Python Developer",
                "start_date": "2023-01-01",
                "end_date": "2024-12-31",
                "description": "Built REST APIs with Django and FastAPI",
            }
        ],
        "education": [
            {
                "institution": "University of Technology",
                "degree": "Bachelor of Computer Science",
                "field": "Software Engineering",
                "graduation_year": 2022,
            }
        ],
        "industries": ["technology", "startups"],
        "location": "San Francisco, CA",
        "remote_preference": "hybrid",
        "salary_expectation": {"min": 80000, "max": 120000},
        "resume_file": None,
    }


@pytest.fixture
def senior_developer_profile() -> Dict[str, Any]:
    """Senior developer profile with extensive experience."""
    return {
        "profile_id": "senior_dev_001",
        "name": "Jordan Senior",
        "email": "jordan@example.com",
        "created_at": datetime.now().isoformat(),
        "experience_level": "senior",
        "total_years_experience": 8,
        "skills": [
            {
                "skill_id": "python",
                "skill_name": "Python",
                "category": "programming_languages",
                "level": "expert",
                "years_experience": 8,
                "verified": True,
            },
            {
                "skill_id": "django",
                "skill_name": "Django",
                "category": "web_development",
                "level": "expert",
                "years_experience": 6,
                "verified": True,
            },
            {
                "skill_id": "kubernetes",
                "skill_name": "Kubernetes",
                "category": "cloud_devops",
                "level": "advanced",
                "years_experience": 4,
                "verified": True,
            },
            {
                "skill_id": "aws",
                "skill_name": "AWS",
                "category": "cloud_devops",
                "level": "advanced",
                "years_experience": 5,
                "verified": True,
            },
            {
                "skill_id": "system_design",
                "skill_name": "System Design",
                "category": "soft_skills",
                "level": "expert",
                "years_experience": 7,
                "verified": False,
            },
        ],
        "work_experience": [
            {
                "company": "TechGiant Corp",
                "position": "Senior Software Engineer",
                "start_date": "2019-01-01",
                "end_date": None,
                "description": "Led team of 5 engineers, designed microservices architecture",
            },
            {
                "company": "MidSize Tech",
                "position": "Python Developer",
                "start_date": "2016-06-01",
                "end_date": "2018-12-31",
                "description": "Built data processing pipelines and REST APIs",
            },
        ],
        "education": [
            {
                "institution": "Top University",
                "degree": "Master of Computer Science",
                "field": "Distributed Systems",
                "graduation_year": 2016,
            },
            {
                "institution": "University of Technology",
                "degree": "Bachelor of Computer Science",
                "field": "Software Engineering",
                "graduation_year": 2014,
            },
        ],
        "industries": ["technology", "fintech", "healthcare"],
        "location": "New York, NY",
        "remote_preference": "full_remote",
        "salary_expectation": {"min": 200000, "max": 300000},
        "resume_file": None,
    }


@pytest.fixture
def data_scientist_profile() -> Dict[str, Any]:
    """Data scientist profile with ML/data skills."""
    return {
        "profile_id": "data_sci_001",
        "name": "Casey DataScientist",
        "email": "casey@example.com",
        "created_at": datetime.now().isoformat(),
        "experience_level": "mid",
        "total_years_experience": 5,
        "skills": [
            {
                "skill_id": "python",
                "skill_name": "Python",
                "category": "programming_languages",
                "level": "expert",
                "years_experience": 5,
                "verified": True,
            },
            {
                "skill_id": "machine_learning",
                "skill_name": "Machine Learning",
                "category": "data_science_ml",
                "level": "advanced",
                "years_experience": 4,
                "verified": True,
            },
            {
                "skill_id": "pandas",
                "skill_name": "Pandas",
                "category": "data_science_ml",
                "level": "expert",
                "years_experience": 5,
                "verified": False,
            },
            {
                "skill_id": "sql",
                "skill_name": "SQL",
                "category": "databases",
                "level": "advanced",
                "years_experience": 5,
                "verified": True,
            },
            {
                "skill_id": "tensorflow",
                "skill_name": "TensorFlow",
                "category": "data_science_ml",
                "level": "intermediate",
                "years_experience": 2,
                "verified": False,
            },
        ],
        "work_experience": [
            {
                "company": "DataAnalytics Inc",
                "position": "Senior Data Scientist",
                "start_date": "2021-01-01",
                "end_date": None,
                "description": "Built ML models for customer prediction",
            }
        ],
        "education": [
            {
                "institution": "Tech University",
                "degree": "Master of Data Science",
                "field": "Machine Learning",
                "graduation_year": 2019,
            }
        ],
        "industries": ["finance", "tech", "healthcare"],
        "location": "Boston, MA",
        "remote_preference": "hybrid",
        "salary_expectation": {"min": 150000, "max": 200000},
        "resume_file": None,
    }


# ============================================================================
# Job Opportunity Fixtures
# ============================================================================


@pytest.fixture
def junior_python_job() -> Dict[str, Any]:
    """Junior Python developer job posting."""
    return {
        "job_id": "job_junior_python_001",
        "title": "Junior Python Developer",
        "company": "StartupXYZ",
        "description": "We're looking for a junior Python developer to join our growing team.",
        "required_skills": [
            {
                "skill_id": "python",
                "skill_name": "Python",
                "level": "intermediate",
                "is_mandatory": True,
            },
            {
                "skill_id": "django",
                "skill_name": "Django",
                "level": "intermediate",
                "is_mandatory": False,
            },
        ],
        "experience_level": "junior",
        "min_years_experience": 1,
        "max_years_experience": 3,
        "location": "San Francisco, CA",
        "remote_type": "hybrid",
        "salary_range": {"min": 80000, "max": 120000},
        "industries": ["technology", "startups"],
        "posted_date": datetime.now().isoformat(),
        "deadline": None,
        "status": "active",
    }


@pytest.fixture
def senior_architect_job() -> Dict[str, Any]:
    """Senior architect job posting."""
    return {
        "job_id": "job_senior_arch_001",
        "title": "Senior Software Architect",
        "company": "TechGiant Corp",
        "description": "Lead our architecture team and design scalable systems.",
        "required_skills": [
            {
                "skill_id": "system_design",
                "skill_name": "System Design",
                "level": "expert",
                "is_mandatory": True,
            },
            {
                "skill_id": "kubernetes",
                "skill_name": "Kubernetes",
                "level": "advanced",
                "is_mandatory": True,
            },
            {
                "skill_id": "aws",
                "skill_name": "AWS",
                "level": "advanced",
                "is_mandatory": True,
            },
        ],
        "experience_level": "senior",
        "min_years_experience": 7,
        "max_years_experience": None,
        "location": "New York, NY",
        "remote_type": "full_remote",
        "salary_range": {"min": 200000, "max": 300000},
        "industries": ["technology", "fintech"],
        "posted_date": datetime.now().isoformat(),
        "deadline": None,
        "status": "active",
    }


@pytest.fixture
def ml_engineer_job() -> Dict[str, Any]:
    """ML engineer job posting."""
    return {
        "job_id": "job_ml_engineer_001",
        "title": "Machine Learning Engineer",
        "company": "AI Startup",
        "description": "Build ML models at scale.",
        "required_skills": [
            {
                "skill_id": "machine_learning",
                "skill_name": "Machine Learning",
                "level": "advanced",
                "is_mandatory": True,
            },
            {
                "skill_id": "python",
                "skill_name": "Python",
                "level": "expert",
                "is_mandatory": True,
            },
            {
                "skill_id": "tensorflow",
                "skill_name": "TensorFlow",
                "level": "intermediate",
                "is_mandatory": False,
            },
            {
                "skill_id": "scikit-learn",
                "skill_name": "Scikit-learn",
                "level": "intermediate",
                "is_mandatory": False,
            },
            {
                "skill_id": "keras",
                "skill_name": "Keras",
                "level": "intermediate",
                "is_mandatory": False,
            },
        ],
        "experience_level": "mid",
        "min_years_experience": 3,
        "max_years_experience": 7,
        "location": "Boston, MA",
        "remote_type": "hybrid",
        "salary_range": {"min": 150000, "max": 200000},
        "industries": ["technology", "healthcare"],
        "posted_date": datetime.now().isoformat(),
        "deadline": None,
        "status": "active",
    }


# ============================================================================
# Collection Fixtures (Multiple items)
# ============================================================================


@pytest.fixture
def job_listings(
    junior_python_job, senior_architect_job, ml_engineer_job
) -> List[Dict[str, Any]]:
    """Collection of various job listings for testing."""
    return [junior_python_job, senior_architect_job, ml_engineer_job]


@pytest.fixture
def developer_profiles(
    junior_developer_profile, senior_developer_profile, data_scientist_profile
) -> List[Dict[str, Any]]:
    """Collection of various developer profiles for testing."""
    return [junior_developer_profile, senior_developer_profile, data_scientist_profile]


# ============================================================================
# Mock AI Response Fixtures
# ============================================================================


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = MagicMock()

    # Mock successful chat completion response
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content="This is a mock AI response."))
    ]
    mock_client.chat.completions.create.return_value = mock_response

    return mock_client


@pytest.fixture
def mock_ai_match_response() -> Dict[str, Any]:
    """Mock AI matching response."""
    return {
        "match_score": 85,
        "match_percentage": "85%",
        "matched_skills": ["Python", "Django", "REST APIs"],
        "missing_skills": ["Kubernetes"],
        "reasoning": "Strong Python and Django background matches job requirements",
        "growth_opportunities": ["Learn Kubernetes", "Expand to DevOps"],
        "confidence": 0.92,
    }


@pytest.fixture
def mock_ai_summary() -> str:
    """Mock AI-generated summary."""
    return """
    Alex is a Junior Python Developer with 2 years of experience in building REST APIs with Django. 
    Strong foundation in Python and web development. Best fit for junior to mid-level Python positions 
    in startups or growing tech companies.
    """


# ============================================================================
# Database Fixtures
# ============================================================================


@pytest.fixture
def mock_database_session():
    """Mock SQLAlchemy database session."""
    session = MagicMock()
    session.query = MagicMock()
    session.add = MagicMock()
    session.commit = MagicMock()
    session.rollback = MagicMock()
    session.close = MagicMock()
    return session


@pytest.fixture
def mock_db_config():
    """Mock database configuration."""
    config = MagicMock()
    config.get_db = MagicMock()
    config.session_scope = MagicMock()
    return config


# ============================================================================
# Flask App Fixtures
# ============================================================================


@pytest.fixture
def app():
    """Create Flask app for testing."""
    # Import here to avoid issues with app initialization
    try:
        from web.app import app as flask_app

        flask_app.config["TESTING"] = True
        flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        return flask_app
    except ImportError:
        pytest.skip("Flask app not available in test environment")


@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create Flask CLI runner."""
    return app.test_cli_runner()


# ============================================================================
# Matching Logic Fixtures
# ============================================================================


@pytest.fixture
def skill_mapping() -> Dict[str, List[str]]:
    """Mapping of skills to related skills for similarity matching."""
    return {
        "python": ["django", "flask", "fastapi", "pandas", "numpy", "programming"],
        "javascript": ["react", "vue", "angular", "nodejs", "typescript", "web"],
        "django": ["python", "rest_api", "web_development", "backend"],
        "kubernetes": ["docker", "devops", "containers", "orchestration", "cloud"],
        "aws": ["cloud", "devops", "infrastructure", "deployment", "scaling"],
        "machine_learning": ["python", "tensorflow", "data_science", "ai", "analytics"],
    }


@pytest.fixture
def scoring_weights() -> Dict[str, float]:
    """Scoring weights for matching algorithm."""
    return {
        "skill_match": 0.45,
        "experience_level": 0.25,
        "industry_preference": 0.15,
        "location_preference": 0.10,
        "salary_range": 0.05,
    }


# ============================================================================
# Utility Fixtures
# ============================================================================


@pytest.fixture
def temp_resume_file(tmp_path) -> Path:
    """Create a temporary resume file for testing."""
    resume_path = tmp_path / "test_resume.txt"
    resume_content = """
    John Doe
    john@example.com | 555-1234
    
    EXPERIENCE
    Senior Python Developer at TechCorp (2020-2024)
    - Built REST APIs with Django
    - Managed cloud infrastructure on AWS
    - Led team of 3 engineers
    
    SKILLS
    - Python (Expert)
    - Django (Advanced)
    - AWS (Advanced)
    - Kubernetes (Intermediate)
    
    EDUCATION
    Master of Computer Science, University of Tech (2020)
    """
    resume_path.write_text(resume_content)
    return resume_path


@pytest.fixture
def sample_vector_data() -> Dict[str, Any]:
    """Sample vector data for testing vector operations."""
    return {
        "job_vectors": {
            "job_1": [0.1, 0.2, 0.3, 0.4],
            "job_2": [0.15, 0.25, 0.35, 0.45],
            "job_3": [0.05, 0.1, 0.15, 0.2],
        },
        "profile_vectors": {
            "profile_1": [0.12, 0.22, 0.32, 0.42],
            "profile_2": [0.02, 0.05, 0.08, 0.1],
        },
    }


# ============================================================================
# Parametrized Test Data
# ============================================================================


@pytest.fixture(params=[1, 2, 3, 5, 8])
def years_of_experience(request):
    """Parametrized fixture for various years of experience."""
    return request.param


@pytest.fixture(params=["beginner", "intermediate", "advanced", "expert"])
def skill_level(request):
    """Parametrized fixture for skill levels."""
    return request.param


@pytest.fixture(params=["junior", "mid", "senior"])
def experience_level(request):
    """Parametrized fixture for experience levels."""
    return request.param


# ============================================================================
# Cleanup & Teardown
# ============================================================================


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically cleanup test files after each test."""
    yield
    # Cleanup code here if needed


# ============================================================================
# Test Configuration
# ============================================================================


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "unit: mark test as a unit test")
    config.addinivalue_line("markers", "integration: mark test as an integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "requires_db: mark test as requiring database")
