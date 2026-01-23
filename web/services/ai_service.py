"""
AI Service for AI-powered features.

Handles AI-based operations including skill explanations, job recommendations,
resume analysis, and match reasoning generation.
"""

import logging
import os
import json
from typing import Dict, List, Optional, Any, Tuple
from openai import OpenAI, AzureOpenAI
from web.services.base import BaseService, ValidationError

# Import centralized API key loader
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import get_openai_api_key

logger = logging.getLogger(__name__)


class AIService(BaseService):
    """Service for AI-powered features using GPT models"""

    def __init__(self, model: str = "gpt-5-mini"):
        """
        Initialize AIService

        Args:
            model: Model to use (default: gpt-5-mini)
        """
        super().__init__()
        self.model = model
        self.client = None
        self.provider = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize appropriate AI client based on available credentials"""
        try:
            # Use centralized API key loader
            openai_key = get_openai_api_key()
            if openai_key:
                self.client = OpenAI(api_key=openai_key)
                self.provider = "OpenAI"
                self.log_info(f"✅ AI Service initialized with {self.provider}")
                return

            # Try Azure OpenAI
            azure_key = os.environ.get("AZURE_OPENAI_API_KEY")
            azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
            if azure_key and azure_endpoint:
                self.client = AzureOpenAI(
                    api_key=azure_key,
                    azure_endpoint=azure_endpoint,
                    api_version="2024-02-15-preview",
                )
                self.provider = "Azure OpenAI"
                self.log_info(f"✅ AI Service initialized with {self.provider}")
                return

            self.log_warning("⚠️ No AI credentials found. AI features will be limited.")
            self.provider = None

        except Exception as e:
            self.log_error(f"❌ Error initializing AI client: {e}")
            self.provider = None

    def is_available(self) -> bool:
        """Check if AI service is available"""
        return self.client is not None and self.provider is not None

    def generate_skill_explanation(self, skill_name: str, context: str = "") -> str:
        """
        Generate an AI explanation for a skill

        Args:
            skill_name: Name of the skill
            context: Additional context (job title, industry, etc.)

        Returns:
            Explanation text

        Raises:
            ValidationError: If skill_name is empty
        """
        if not skill_name or not skill_name.strip():
            raise ValidationError("skill_name cannot be empty", code="EMPTY_SKILL")

        if not self.is_available():
            return f"Explanation for {skill_name} not available."

        try:
            prompt = f"""
Provide a brief, professional explanation (2-3 sentences) of the "{skill_name}" skill.
{f"Context: {context}" if context else ""}
Focus on practical applications and why it's valuable in a technical career.
Keep the tone informative and accessible.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200,
            )

            explanation = response.choices[0].message.content.strip()
            self.log_info(f"Generated explanation for skill: {skill_name}")
            return explanation

        except Exception as e:
            self.log_error(f"Error generating skill explanation: {e}")
            return f"Explanation for {skill_name} not available."

    def generate_job_recommendation_reason(
        self, profile_skills: List[str], job_title: str, job_skills: List[str]
    ) -> str:
        """
        Generate AI-powered reason for job recommendation

        Args:
            profile_skills: User's skills
            job_title: Job title
            job_skills: Skills required for the job

        Returns:
            Recommendation reason

        Raises:
            ValidationError: If inputs are invalid
        """
        if not job_title or not job_title.strip():
            raise ValidationError("job_title cannot be empty", code="EMPTY_JOB_TITLE")

        if not profile_skills:
            raise ValidationError("profile_skills cannot be empty", code="EMPTY_SKILLS")

        if not self.is_available():
            # Fallback to simple reason
            matched = len(set(profile_skills) & set(job_skills))
            return f"You have {matched} of the required skills for this {job_title} position."

        try:
            matching_skills = set(profile_skills) & set(job_skills)
            missing_skills = set(job_skills) - set(profile_skills)

            prompt = f"""
Generate a concise, encouraging recommendation reason (2-3 sentences) for why someone 
with these skills: {", ".join(profile_skills)}
would be a good fit for a {job_title} position.

Matching skills: {", ".join(matching_skills) if matching_skills else "None"}
Missing skills (can be learned): {", ".join(missing_skills) if missing_skills else "None"}

Focus on transferable knowledge and learning potential.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=200,
            )

            reason = response.choices[0].message.content.strip()
            self.log_info(f"Generated recommendation reason for {job_title}")
            return reason

        except Exception as e:
            self.log_error(f"Error generating recommendation reason: {e}")
            # Fallback
            matched = len(set(profile_skills) & set(job_skills))
            return f"You have {matched} of the required skills for this {job_title} position."

    def analyze_profile_summary(self, profile_data: Dict[str, Any]) -> str:
        """
        Generate AI summary of user profile

        Args:
            profile_data: User profile data

        Returns:
            Summary text

        Raises:
            ValidationError: If profile_data is invalid
        """
        if not profile_data:
            raise ValidationError("profile_data cannot be empty", code="EMPTY_PROFILE")

        if not self.is_available():
            return "Profile analysis not available."

        try:
            name = profile_data.get("name", "User")
            experience_level = profile_data.get("experience_level", "")
            years_experience = profile_data.get("years_experience", 0)
            skills = profile_data.get("skills", [])
            industry = profile_data.get("industry", "")

            prompt = f"""
Generate a brief, professional profile summary (3-4 sentences) for:
Name: {name}
Experience Level: {experience_level}
Years of Experience: {years_experience}
Key Skills: {", ".join(skills[:5]) if skills else "Not specified"}
Industry: {industry or "Not specified"}

The summary should highlight strengths and career positioning.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300,
            )

            summary = response.choices[0].message.content.strip()
            self.log_info(f"Generated profile summary for {name}")
            return summary

        except Exception as e:
            self.log_error(f"Error analyzing profile: {e}")
            return "Profile analysis not available."

    def generate_skill_gap_analysis(
        self,
        profile_skills: List[str],
        job_title: str,
        required_skills: List[str],
    ) -> str:
        """
        Generate AI analysis of skill gaps

        Args:
            profile_skills: User's skills
            job_title: Target job title
            required_skills: Skills required for the job

        Returns:
            Skill gap analysis

        Raises:
            ValidationError: If inputs are invalid
        """
        if not job_title or not job_title.strip():
            raise ValidationError("job_title cannot be empty", code="EMPTY_JOB_TITLE")

        if not required_skills:
            raise ValidationError(
                "required_skills cannot be empty", code="EMPTY_REQUIRED_SKILLS"
            )

        if not self.is_available():
            missing = set(required_skills) - set(profile_skills)
            if missing:
                return f"To qualify for this {job_title}, you should develop: {', '.join(list(missing)[:3])}"
            return f"You have all the key skills for this {job_title} position!"

        try:
            missing_skills = set(required_skills) - set(profile_skills)

            if not missing_skills:
                return f"Great news! You have all the key skills for this {job_title} position!"

            prompt = f"""
Generate a brief, actionable analysis (2-3 sentences) of skill gaps for:
Target Position: {job_title}
Missing Skills: {", ".join(missing_skills)}
Current Skills: {", ".join(profile_skills[:5]) if profile_skills else "Foundational"}

Include recommendations for addressing these gaps.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=250,
            )

            analysis = response.choices[0].message.content.strip()
            self.log_info(f"Generated skill gap analysis for {job_title}")
            return analysis

        except Exception as e:
            self.log_error(f"Error generating skill gap analysis: {e}")
            missing = set(required_skills) - set(profile_skills)
            if missing:
                return f"To qualify for this {job_title}, you should develop: {', '.join(list(missing)[:3])}"
            return f"You have the skills for this {job_title} position!"

    def generate_interview_tips(
        self, job_title: str, job_description: str, profile_skills: List[str]
    ) -> str:
        """
        Generate AI interview tips for a specific job

        Args:
            job_title: Job title
            job_description: Job description
            profile_skills: User's skills

        Returns:
            Interview tips

        Raises:
            ValidationError: If inputs are invalid
        """
        if not job_title or not job_title.strip():
            raise ValidationError("job_title cannot be empty", code="EMPTY_JOB_TITLE")

        if not self.is_available():
            return f"Research the {job_title} role and prepare examples of your relevant experience."

        try:
            prompt = f"""
Generate 3-4 concise interview tips (bullet points) for a {job_title} position:
Job Focus: {job_description[:200]}
Candidate Skills: {", ".join(profile_skills[:5]) if profile_skills else "General"}

Format: Each tip on a new line starting with •
Make tips specific, actionable, and encouraging.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300,
            )

            tips = response.choices[0].message.content.strip()
            self.log_info(f"Generated interview tips for {job_title}")
            return tips

        except Exception as e:
            self.log_error(f"Error generating interview tips: {e}")
            return f"Research the {job_title} role and prepare examples of your relevant experience."

    def generate_career_suggestions(
        self, current_skills: List[str], experience_years: int, industry: str
    ) -> List[str]:
        """
        Generate AI career path suggestions

        Args:
            current_skills: User's current skills
            experience_years: Years of experience
            industry: Current industry

        Returns:
            List of career suggestions

        Raises:
            ValidationError: If inputs are invalid
        """
        if not current_skills:
            raise ValidationError("current_skills cannot be empty", code="EMPTY_SKILLS")

        if not self.is_available():
            return [
                "Continue building expertise in your current skills",
                "Explore adjacent technical roles",
                "Consider leadership or mentorship opportunities",
            ]

        try:
            prompt = f"""
Generate 3-4 career path suggestions for someone with:
Skills: {", ".join(current_skills)}
Experience: {experience_years} years
Industry: {industry or "Tech"}

Return as a JSON array of strings, each suggestion being a short career path.
Example format: ["Senior Software Engineer", "Tech Lead"]
Make suggestions realistic and based on skill progression.
"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300,
            )

            response_text = response.choices[0].message.content.strip()

            # Try to parse JSON
            try:
                suggestions = json.loads(response_text)
                if isinstance(suggestions, list):
                    self.log_info(f"Generated {len(suggestions)} career suggestions")
                    return suggestions
            except json.JSONDecodeError:
                # Fallback: split by newlines
                suggestions = [
                    s.strip() for s in response_text.split("\n") if s.strip()
                ]
                return suggestions[:4]

        except Exception as e:
            self.log_error(f"Error generating career suggestions: {e}")
            return [
                "Continue building expertise in your current skills",
                "Explore adjacent technical roles",
                "Consider leadership opportunities",
            ]

    def batch_generate_explanations(self, skills: List[str]) -> Dict[str, str]:
        """
        Generate explanations for multiple skills (with batching for efficiency)

        Args:
            skills: List of skill names

        Returns:
            Dictionary mapping skill names to explanations
        """
        if not skills:
            raise ValidationError("skills list cannot be empty", code="EMPTY_SKILLS")

        explanations = {}

        for skill in skills[:10]:  # Limit to 10 to avoid API overload
            try:
                explanation = self.generate_skill_explanation(skill)
                explanations[skill] = explanation
            except Exception as e:
                self.log_warning(f"Error explaining skill '{skill}': {e}")
                explanations[skill] = f"Explanation for {skill} not available."

        self.log_info(f"Generated explanations for {len(explanations)} skills")
        return explanations
