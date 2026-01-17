"""Shared initialization and helper utilities for the web app."""

import contextlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

openai = None
OpenAI = None
AI_MATCHING_AVAILABLE = False
VECTOR_MATCHING_AVAILABLE = False
VECTOR_SEARCH_AVAILABLE = False
vector_job_matcher = None
profile_manager = None
get_vector_service = None
openai_key = None
github_token = None
UserProfile = None
Job = None
UserSkill = None
SKILLMATCH_AVAILABLE = False
SkillMatchAgent = None
DataLoader = None
SkillMatcher = None
SCRAPER_AVAILABLE = False
is_production = False


def check_conda_environment() -> None:
    """Check if we're running in the correct conda environment."""
    conda_env = os.environ.get("CONDA_DEFAULT_ENV")
    production = bool(
        os.environ.get("RENDER")
        or os.environ.get("RAILWAY")
        or os.environ.get("HEROKU")
        or os.environ.get("VERCEL")
    )

    if production:
        print(
            "🚀 Running in production environment: "
            f"{os.environ.get('RENDER_SERVICE_NAME', 'Cloud Platform')}"
        )
        print(f"🐍 Python environment: {conda_env or 'system'}")
    elif conda_env != "base":
        print("⚠️  WARNING: Not running in 'base' conda environment!")
        print(f"📍 Current environment: {conda_env or 'base'}")
        print("🔧 To fix this, activate the environment first:")
        print("   conda activate base")
        print("   python app.py")
        print("")
    else:
        print(f"✅ Running in correct conda environment: {conda_env}")


def initialize_environment() -> None:
    """Initialize environment, paths, and shared services."""
    global openai, OpenAI, AI_MATCHING_AVAILABLE, VECTOR_MATCHING_AVAILABLE
    global VECTOR_SEARCH_AVAILABLE, vector_job_matcher, profile_manager
    global get_vector_service, openai_key, github_token, UserProfile, Job
    global UserSkill, SKILLMATCH_AVAILABLE, SkillMatchAgent, DataLoader
    global SkillMatcher, SCRAPER_AVAILABLE, is_production

    is_production = bool(
        os.environ.get("RENDER")
        or os.environ.get("RAILWAY")
        or os.environ.get("HEROKU")
    )

    if not os.environ.get("RENDER"):
        check_conda_environment()

    from dotenv import load_dotenv

    env_path = Path(__file__).parent.parent / ".env"
    load_dotenv(env_path)

    app_dir = Path(__file__).parent
    project_root = app_dir.parent

    if is_production:
        print(f"📍 App directory: {app_dir}")
        print(f"📍 Project root: {project_root}")
        print(f"📍 Current working directory: {os.getcwd()}")
        print(f"📍 Python path before: {sys.path[:3]}")

    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(app_dir))
    sys.path.insert(0, os.getcwd())

    if is_production:
        print(f"📍 Python path after: {sys.path[:5]}")

    try:
        import openai as openai_module
        from openai import OpenAI as OpenAIClient

        openai = openai_module
        OpenAI = OpenAIClient
    except ImportError:
        openai = None
        OpenAI = None

    try:
        from services.ai_skill_matcher import (
            ai_skill_matcher,
            categorize_skills_ai,
            find_skill_matches_ai,
        )
        from services.enhanced_job_matcher import (
            enhanced_job_matcher,
            find_enhanced_matches,
        )

        AI_MATCHING_AVAILABLE = True
    except ImportError:
        AI_MATCHING_AVAILABLE = False
        print("⚠️  AI skill matching services not available, using fallback matching")
        OpenAI = None

    try:
        from services.vector_job_matcher import vector_job_matcher as job_matcher

        vector_job_matcher = job_matcher
        VECTOR_MATCHING_AVAILABLE = True
        print("✅ Vector job matching service available")
    except ImportError as error:
        VECTOR_MATCHING_AVAILABLE = False
        vector_job_matcher = None
        print(f"⚠️ Vector job matching service not available: {error}")

    try:
        try:
            from services.simple_vector_service import get_vector_service as getter
        except ImportError:
            from web.services.simple_vector_service import get_vector_service as getter

        get_vector_service = getter
        VECTOR_SEARCH_AVAILABLE = True
        print("✅ Vector search service available")
    except ImportError as error:
        print(f"⚠️ Vector search service not available: {error}")
        VECTOR_SEARCH_AVAILABLE = False

    try:
        from web.storage import profile_manager as manager

        profile_manager = manager
    except ImportError:
        try:
            from storage import profile_manager as manager

            profile_manager = manager
        except ImportError:
            class MinimalProfileManager:
                def list_profiles(self):
                    return []

                def load_profile(self, profile_id):
                    return None

            profile_manager = MinimalProfileManager()

    openai_key = os.environ.get("OPENAI_API_KEY")
    github_token = os.environ.get("GITHUB_TOKEN")

    if openai_key:
        print(
            "✅ OpenAI API key loaded from .env "
            f"(length: {len(openai_key)} characters)"
        )
        print(
            "🚀 Using latest OpenAI models: GPT-4o, GPT-4 Turbo "
            "(including ChatGPT Pro models)"
        )
        if github_token:
            print("🔄 GitHub token also available as fallback")
    elif github_token:
        print(
            "✅ GitHub token loaded from .env "
            f"(length: {len(github_token)} characters)"
        )
        print("🚀 Using GitHub Copilot Pro models: GPT-5, O1, DeepSeek-R1")
    else:
        print("❌ No AI API keys found - will use enhanced basic matching")

    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

    UserProfile, Job, UserSkill = import_database_modules(is_production=is_production)

    try:
        from skillmatch.models import (
            UserProfile as CoreUserProfile,
            SkillItem,
            ExperienceLevel,
            UserPreferences,
            PreferenceType,
        )
        from skillmatch.utils import DataLoader as CoreDataLoader, SkillMatcher as CoreSkillMatcher

        try:
            from skillmatch import SkillMatchAgent as CoreSkillMatchAgent

            SkillMatchAgent = CoreSkillMatchAgent
            print("✅ SkillMatch core modules loaded successfully")
        except Exception as agent_error:
            print(
                "⚠️  SkillMatch agent not available "
                f"(OpenAI compatibility issue): {agent_error}"
            )
            SkillMatchAgent = None

        DataLoader = CoreDataLoader
        SkillMatcher = CoreSkillMatcher
        SKILLMATCH_AVAILABLE = True
    except ImportError as error:
        print(f"Warning: SkillMatch core modules not available: {error}")
        SkillMatchAgent = None
        DataLoader = None
        SkillMatcher = None
        SKILLMATCH_AVAILABLE = False

    SCRAPER_AVAILABLE = False


def import_database_modules(is_production: bool) -> tuple:
    """Import database modules with fallback handling."""
    import_attempts = []
    database_paths = [
        os.path.join(os.getcwd(), "database"),
        os.path.join(os.getcwd(), "web", "database"),
        os.path.join(os.path.dirname(__file__), "database"),
        os.path.join(os.path.dirname(__file__), "..", "web", "database"),
    ]

    if is_production:
        print("🔍 Checking database paths:")
        for index, path in enumerate(database_paths, 1):
            exists = os.path.exists(path)
            print(f"   Path {index}: {path} - {'EXISTS' if exists else 'NOT FOUND'}")

    try:
        from database.models import UserProfile as DbUserProfile
        from database.models import Job as DbJob
        from database.models import UserSkill as DbUserSkill

        print("✅ Successfully imported database.models using relative paths")
        return DbUserProfile, DbJob, DbUserSkill
    except ImportError as error:
        import_attempts.append(f"Relative import: {error}")

    try:
        from web.database.models import UserProfile as DbUserProfile
        from web.database.models import Job as DbJob
        from web.database.models import UserSkill as DbUserSkill

        print("✅ Successfully imported database.models using web.database paths")
        return DbUserProfile, DbJob, DbUserSkill
    except ImportError as error:
        import_attempts.append(f"Web prefix import: {error}")

    for database_path in database_paths:
        if os.path.exists(database_path):
            try:
                parent_path = os.path.dirname(database_path)
                if parent_path not in sys.path:
                    sys.path.insert(0, parent_path)

                import database.models as db_models

                print(
                    "✅ Successfully imported database.models using path manipulation: "
                    f"{parent_path}"
                )
                return db_models.UserProfile, db_models.Job, db_models.UserSkill
            except ImportError as error:
                import_attempts.append(f"Path manipulation ({parent_path}): {error}")

    if is_production:
        print("❌ All database import attempts failed:")
        for attempt in import_attempts:
            print(f"   - {attempt}")

    class DbUserProfile:
        def __init__(self, **kwargs):
            pass

    class DbJob:
        def __init__(self, **kwargs):
            pass

    class DbUserSkill:
        def __init__(self, **kwargs):
            pass

    print("⚠️ Using placeholder classes - database functionality limited")
    return DbUserProfile, DbJob, DbUserSkill


def parse_datetime(date_str):
    """Parse datetime string from database into datetime object."""
    if not date_str:
        return None
    if isinstance(date_str, datetime):
        return date_str
    try:
        return datetime.fromisoformat(date_str.replace("T", " ").split(".")[0])
    except (ValueError, AttributeError):
        return None


def quick_skill_filter(profile_data, jobs_list, top_n=20):
    """Quickly filter jobs using basic skill matching before AI analysis."""
    try:
        user_skills = set()
        if profile_data.get("skills"):
            for skill in profile_data["skills"]:
                if isinstance(skill, dict):
                    skill_name = skill.get("skill_name", "").lower()
                    if skill_name:
                        user_skills.add(skill_name)
                elif isinstance(skill, str):
                    user_skills.add(skill.lower())

        if not user_skills:
            return jobs_list[:top_n]

        job_scores = []
        for job in jobs_list:
            job_text = f"{job.get('job_title', '')} {job.get('job_description', '')}".lower()
            matches = sum(1 for skill in user_skills if skill in job_text)
            match_ratio = matches / len(user_skills) if user_skills else 0
            job_scores.append((match_ratio, job))

        job_scores.sort(key=lambda x: x[0], reverse=True)
        return [job for score, job in job_scores[:top_n]]

    except Exception as error:
        print(f"⚠️ Quick filter error: {error}")
        return jobs_list[:top_n]


def ai_enhanced_job_matching(profile_data, jobs_list, vector_resume_text=None):
    """Use AI to analyze user profile and match with jobs."""
    print(f"🔍 AI Debug - openai module: {openai is not None}")
    print(f"🔍 AI Debug - OpenAI class: {OpenAI is not None}")
    print(f"🔍 AI Debug - API key available: {openai_key is not None}")
    print(
        f"🔍 AI Debug - API key length: {len(openai_key) if openai_key else 0}"
    )

    if not openai or not OpenAI:
        print("⚠️ AI modules not available - falling back to basic matching")
        return None

    if not openai_key and not github_token:
        print("⚠️ No AI API keys available - falling back to basic matching")
        return None

    try:
        use_github_first = False
        if github_token and openai_key:
            use_github_first = True

        if use_github_first and github_token:
            print("🚀 Using GitHub Models (free tier) for AI analysis")
            client = OpenAI(
                base_url="https://models.inference.ai.azure.com",
                api_key=github_token,
            )
            model_to_use = "gpt-4o-mini"
        else:
            client = OpenAI(api_key=openai_key)
            model_to_use = "gpt-4o-mini"

        profile_context = {
            "name": profile_data.get("name", "Professional"),
            "title": profile_data.get("title", ""),
            "location": profile_data.get("location", ""),
            "experience_level": profile_data.get("experience_level", "entry"),
            "summary": profile_data.get("summary", ""),
            "skills": [],
            "work_experience": profile_data.get("work_experience", []),
            "education": profile_data.get("education", []),
            "preferences": profile_data.get("preferences", {}),
            "goals": profile_data.get("goals", ""),
        }

        if profile_data.get("skills"):
            for skill in profile_data["skills"]:
                if isinstance(skill, dict):
                    skill_name = skill.get("skill_name", "")
                    if skill_name:
                        profile_context["skills"].append(skill_name)
                elif isinstance(skill, str):
                    profile_context["skills"].append(skill)

        resume_context = ""
        if vector_resume_text:
            resume_context = f"\n\nResume Content Analysis:\n{vector_resume_text[:1000]}..."

        job_summaries = []
        for job in jobs_list[:15]:
            job_summaries.append(
                {
                    "job_id": job.get("job_id", "unknown"),
                    "title": job.get("job_title", job.get("title", "Unknown")),
                    "category": job.get("category", job.get("job_category", "General")),
                    "description": job.get(
                        "job_description", job.get("description", "")
                    )[:300],
                    "required_skills": job.get(
                        "job_skill_set", job.get("required_skills", [])
                    )[:10],
                }
            )

        prompt = f"""You are an elite career matching AI with deep expertise in talent acquisition and career development. Conduct a comprehensive analysis of this professional's profile and identify the TOP 5 most strategically aligned opportunities.

You will analyze each opportunity based on these sophisticated criteria:

🎯 ADVANCED MATCHING METHODOLOGY:
═══════════════════════════════════════════
1. SKILLS ALIGNMENT (45%): 
   - Technical Skills Match: Direct overlap between candidate skills and job requirements
   - Transferable Skills: Adjacent skills that indicate capability to learn required skills
   - Skill Depth Analysis: Level of expertise vs. role requirements
   - Emerging Technology Alignment: Future-oriented skill matching

2. INDUSTRY & DOMAIN FIT (30%):
   - Industry Experience: Previous work in similar domains
   - Business Context Understanding: Knowledge of industry challenges/opportunities
   - Regulatory/Compliance Familiarity: Industry-specific knowledge requirements
   - Market Trends Alignment: Understanding of current industry direction

3. CAREER PROGRESSION LOGIC (15%):
   - Role Seniority Match: Appropriate level for candidate's experience
   - Responsibility Scope: Leadership/management requirements alignment
   - Career Growth Path: Logical next step in professional development
   - Promotion Readiness: Candidate's readiness for increased responsibility

4. CULTURAL & WORK STYLE FIT (5%):
   - Work Environment Preferences: Office culture, team dynamics
   - Communication Style: Collaborative vs. independent work preferences
   - Values Alignment: Company mission alignment with candidate values

5. STRATEGIC CAREER IMPACT (5%):
   - Learning Opportunities: Skill development potential
   - Network Expansion: Professional network growth opportunities
   - Industry Positioning: Role's impact on candidate's market position
   - Long-term Career Value: 3-5 year career trajectory enhancement

USER PROFILE:
{json.dumps(profile_context, indent=2)}

AVAILABLE OPPORTUNITIES:
{json.dumps(job_summaries, indent=2)}

RESUME CONTEXT (if provided):
{resume_context}

Return a JSON array of the TOP 5 matches with fields: job_id, match_percentage, skills_only_percentage, matched_skills, missing_skills, explanation.
"""

        response = client.chat.completions.create(
            model=model_to_use,
            messages=[
                {"role": "system", "content": "You are a strict JSON API."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1200,
            temperature=0.2,
        )

        raw_response = response.choices[0].message.content.strip()
        return json.loads(raw_response)

    except Exception as error:
        print(f"❌ AI matching error: {error}")
        return None
