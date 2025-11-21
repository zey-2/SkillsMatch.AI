"""
AI-Powered Skill Categorization and Matching Service

This service uses AI models to dynamically categorize skills, understand semantic
relationships, and provide intelligent job matching that goes beyond hardcoded synonyms.
"""

import os
import json
import asyncio
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from openai import OpenAI
import logging

logger = logging.getLogger(__name__)

@dataclass
class SkillCategory:
    """Represents a dynamically discovered skill category"""
    name: str
    skills: List[str]
    confidence: float
    related_industries: List[str]
    synonyms: List[str]

@dataclass
class SkillMatch:
    """Represents a skill match with confidence and reasoning"""
    user_skill: str
    job_skill: str
    confidence: float
    reasoning: str
    category: str

class AISkillMatcher:
    """AI-powered skill categorization and matching system"""
    
    def __init__(self):
        """Initialize the AI skill matcher"""
        self.openai_client = None
        self.skill_cache = {}
        self.category_cache = {}
        self.initialize_openai()
    
    def initialize_openai(self):
        """Initialize OpenAI client - prioritize OpenAI over GitHub Models"""
        try:
            # Try OpenAI first (more reliable if available)
            openai_key = os.environ.get('OPENAI_API_KEY')
            if openai_key and openai_key.startswith('sk-'):
                self.openai_client = OpenAI(
                    api_key=openai_key,
                    timeout=30.0,
                    max_retries=2
                )
                self.model_id = "gpt-4o-mini"
                logger.info("✅ Initialized AI Skill Matcher with OpenAI")
            else:
                # Fallback to GitHub Models (free tier)
                github_token = os.environ.get('GITHUB_TOKEN')
                if github_token and (github_token.startswith('ghp_') or github_token.startswith('github_pat_')):
                    # Test GitHub token first before using it
                    test_client = OpenAI(
                        base_url="https://models.inference.ai.azure.com",
                        api_key=github_token,
                        timeout=10.0,
                        max_retries=1
                    )
                    
                    # Quick test to verify token works
                    try:
                        test_response = test_client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": "test"}],
                            max_tokens=1
                        )
                        # If we get here, token works
                        self.openai_client = test_client
                        self.model_id = "gpt-4o-mini"
                        logger.info("✅ Initialized AI Skill Matcher with GitHub Models")
                    except Exception as github_error:
                        logger.warning(f"⚠️ GitHub token test failed: {github_error}")
                        logger.warning("⚠️ No valid AI API keys found, using fallback matching")
                        logger.info("💡 To enable AI: Set OPENAI_API_KEY (sk-...) or update GITHUB_TOKEN")
                else:
                    logger.warning("⚠️ No valid AI API keys found, using fallback matching")
                    logger.info("💡 To enable AI: Set GITHUB_TOKEN (ghp_...) or OPENAI_API_KEY (sk-...)")
        except Exception as e:
            logger.error(f"❌ Failed to initialize AI client: {e}")
            self.openai_client = None
    
    def categorize_skills(self, skills: List[str]) -> List[SkillCategory]:
        """
        Use AI to dynamically categorize a list of skills
        
        Args:
            skills: List of skill names to categorize
            
        Returns:
            List of SkillCategory objects with AI-generated categorization
        """
        if not self.openai_client or not skills:
            return self._fallback_categorization(skills)
        
        try:
            # Create cache key
            cache_key = hash(tuple(sorted(skills)))
            if cache_key in self.category_cache:
                return self.category_cache[cache_key]
            
            prompt = f"""
            You are an expert HR and skills analyst. Analyze the following skills and group them into logical categories.
            
            Skills to categorize: {', '.join(skills)}
            
            Please provide a JSON response with the following structure:
            {{
                "categories": [
                    {{
                        "name": "category_name",
                        "skills": ["skill1", "skill2"],
                        "confidence": 0.95,
                        "related_industries": ["industry1", "industry2"],
                        "synonyms": ["synonym1", "synonym2"]
                    }}
                ]
            }}
            
            Rules:
            1. Group similar/related skills together
            2. Use descriptive category names (e.g., "Healthcare & Medical", "Software Development", "Data Analytics")
            3. Confidence should be 0.0-1.0 based on how certain you are about the categorization
            4. Include related industries where these skills are commonly used
            5. Add synonyms and related terms for each category
            6. Ensure all input skills are assigned to exactly one category
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,  # Low temperature for consistent categorization
                max_tokens=1500
            )
            
            try:
                content = response.choices[0].message.content.strip()
                if not content:
                    logger.warning("⚠️ Empty AI response for skill categorization")
                    return []
                
                # Try to clean common JSON issues
                if content.startswith('```json'):
                    content = content.replace('```json', '').replace('```', '').strip()
                
                result = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"❌ AI skill categorization failed: {e}")
                logger.debug(f"Raw response: {response.choices[0].message.content[:200]}...")
                return []
            
            categories = []
            
            for cat_data in result.get('categories', []):
                try:
                    category = SkillCategory(
                        name=cat_data['name'],
                        skills=cat_data['skills'],
                        confidence=cat_data.get('confidence', 0.8),
                        related_industries=cat_data.get('related_industries', []),
                        synonyms=cat_data.get('synonyms', [])
                    )
                    categories.append(category)
                except KeyError as e:
                    logger.warning(f"⚠️ Skipping invalid category data: {e}")
            
            # Cache the result
            self.category_cache[cache_key] = categories
            return categories
            
        except Exception as e:
            error_msg = str(e).lower()
            if 'unauthorized' in error_msg or '401' in error_msg:
                logger.error(f"❌ AI authorization failed: Invalid API key. Please check your GitHub token or OpenAI key.")
            elif 'too many requests' in error_msg or '429' in error_msg:
                logger.warning(f"⚠️ AI rate limit exceeded. Using fallback matching.")
            else:
                logger.error(f"❌ AI categorization failed: {e}")
            return self._fallback_categorization(skills)
    
    def find_skill_matches(self, user_skills: List[str], job_description: str, job_title: str) -> List[SkillMatch]:
        """
        Use AI to find semantic matches between user skills and job requirements
        
        Args:
            user_skills: List of user's skills
            job_description: Job description text
            job_title: Job title
            
        Returns:
            List of SkillMatch objects with AI-generated matching
        """
        if not self.openai_client or not user_skills:
            return self._fallback_matching(user_skills, job_description, job_title)
        
        try:
            prompt = f"""
            You are an expert career counselor and skills analyst. Analyze how well a candidate's skills match a job opportunity.
            
            Candidate Skills: {', '.join(user_skills)}
            Job Title: {job_title}
            Job Description: {job_description}
            
            Please provide a JSON response analyzing skill matches:
            {{
                "matches": [
                    {{
                        "user_skill": "user's skill name",
                        "job_skill": "relevant job requirement",
                        "confidence": 0.85,
                        "reasoning": "explanation of why this is a match",
                        "category": "skill category"
                    }}
                ]
            }}
            
            Rules:
            1. Find semantic matches, not just exact matches (e.g., "nursing" matches "patient care")
            2. Consider skill transferability (e.g., "python" for "data analysis" roles)
            3. Confidence 0.0-1.0 based on strength of match
            4. Provide clear reasoning for each match
            5. Include both direct and indirect skill applications
            6. Consider the job context and industry
            7. Only include matches with confidence > 0.3
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,  # Low temperature for consistent matching
                max_tokens=2000
            )
            
            try:
                content = response.choices[0].message.content.strip()
                if not content:
                    logger.warning("⚠️ Empty AI response for skill matching")
                    return []
                
                # Try to clean common JSON issues
                if content.startswith('```json'):
                    content = content.replace('```json', '').replace('```', '').strip()
                
                result = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"❌ AI skill matching failed: {e}")
                logger.debug(f"Raw response: {response.choices[0].message.content[:200]}...")
                return []
            
            matches = []
            
            for match_data in result.get('matches', []):
                try:
                    match = SkillMatch(
                        user_skill=match_data['user_skill'],
                        job_skill=match_data['job_skill'],
                        confidence=match_data.get('confidence', 0.5),
                        reasoning=match_data.get('reasoning', ''),
                        category=match_data.get('category', 'General')
                    )
                    matches.append(match)
                except KeyError as e:
                    logger.warning(f"⚠️ Skipping invalid match data: {e}")
            
            return matches
            
        except Exception as e:
            error_msg = str(e).lower()
            if 'unauthorized' in error_msg or '401' in error_msg:
                logger.error(f"❌ AI authorization failed: Invalid API key. Check GITHUB_TOKEN or OPENAI_API_KEY")
            elif 'too many requests' in error_msg or '429' in error_msg:
                logger.warning(f"⚠️ AI rate limit exceeded. Using enhanced fallback matching.")
            else:
                logger.error(f"❌ AI skill matching failed: {e}")
            return self._fallback_matching(user_skills, job_description, job_title)
    
    async def extract_job_skills(self, job_title: str, job_description: str) -> List[str]:
        """
        Use AI to extract required skills from job description
        
        Args:
            job_title: Job title
            job_description: Job description text
            
        Returns:
            List of extracted skills
        """
        if not self.openai_client:
            return self._fallback_skill_extraction(job_title, job_description)
        
        try:
            prompt = f"""
            Extract the required skills and qualifications from this job posting.
            
            Job Title: {job_title}
            Job Description: {job_description}
            
            Please provide a JSON response:
            {{
                "required_skills": ["skill1", "skill2"],
                "preferred_skills": ["skill3", "skill4"],
                "soft_skills": ["skill5", "skill6"],
                "technical_skills": ["skill7", "skill8"]
            }}
            
            Rules:
            1. Extract both explicitly mentioned and implied skills
            2. Normalize skill names (e.g., "Python programming" → "python")
            3. Include industry-specific skills and tools
            4. Consider soft skills and technical skills separately
            5. Focus on actionable, matchable skills
            """
            
            response = self.openai_client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=800
            )
            
            try:
                content = response.choices[0].message.content.strip()
                if not content:
                    logger.warning("⚠️ Empty AI response for skill extraction")
                    return self._fallback_skill_extraction(job_title, job_description)
                
                # Try to clean common JSON issues
                if content.startswith('```json'):
                    content = content.replace('```json', '').replace('```', '').strip()
                
                result = json.loads(content)
            except json.JSONDecodeError as e:
                logger.error(f"❌ AI skill extraction failed: {e}")
                logger.debug(f"Raw response: {response.choices[0].message.content[:200]}...")
                return self._fallback_skill_extraction(job_title, job_description)
            
            # Combine all skill types
            all_skills = []
            all_skills.extend(result.get('required_skills', []))
            all_skills.extend(result.get('preferred_skills', []))
            all_skills.extend(result.get('soft_skills', []))
            all_skills.extend(result.get('technical_skills', []))
            
            # Normalize and deduplicate
            normalized_skills = list(set([skill.lower().strip() for skill in all_skills if skill]))
            return normalized_skills
            
        except Exception as e:
            error_msg = str(e).lower()
            if 'unauthorized' in error_msg or '401' in error_msg:
                logger.error(f"❌ AI authorization failed: Please verify your API keys")
            elif 'too many requests' in error_msg or '429' in error_msg:
                logger.warning(f"⚠️ AI rate limit hit. Using enhanced skill extraction fallback.")
            else:
                logger.error(f"❌ AI skill extraction failed: {e}")
            return self._fallback_skill_extraction(job_title, job_description)
    
    def _fallback_categorization(self, skills: List[str]) -> List[SkillCategory]:
        """Fallback categorization using hardcoded rules"""
        tech_keywords = ['python', 'sql', 'javascript', 'java', 'programming', 'developer', 'software']
        healthcare_keywords = ['nurse', 'nursing', 'medical', 'healthcare', 'clinical', 'patient']
        data_keywords = ['data', 'analytics', 'analysis', 'scientist', 'ml', 'ai']
        
        categories = []
        
        # Technology category
        tech_skills = [skill for skill in skills if any(keyword in skill.lower() for keyword in tech_keywords)]
        if tech_skills:
            categories.append(SkillCategory(
                name="Technology & Software",
                skills=tech_skills,
                confidence=0.8,
                related_industries=["Technology", "Software", "IT"],
                synonyms=["tech", "it", "software development", "programming"]
            ))
        
        # Healthcare category
        health_skills = [skill for skill in skills if any(keyword in skill.lower() for keyword in healthcare_keywords)]
        if health_skills:
            categories.append(SkillCategory(
                name="Healthcare & Medical",
                skills=health_skills,
                confidence=0.8,
                related_industries=["Healthcare", "Medical", "Nursing"],
                synonyms=["medical", "clinical", "patient care", "health services"]
            ))
        
        # Data category
        data_skills = [skill for skill in skills if any(keyword in skill.lower() for keyword in data_keywords)]
        if data_skills:
            categories.append(SkillCategory(
                name="Data & Analytics",
                skills=data_skills,
                confidence=0.8,
                related_industries=["Data Science", "Analytics", "Business Intelligence"],
                synonyms=["data science", "analytics", "business intelligence", "statistics"]
            ))
        
        # General category for remaining skills
        assigned_skills = set()
        for cat in categories:
            assigned_skills.update(cat.skills)
        
        remaining_skills = [skill for skill in skills if skill not in assigned_skills]
        if remaining_skills:
            categories.append(SkillCategory(
                name="General Skills",
                skills=remaining_skills,
                confidence=0.6,
                related_industries=["General"],
                synonyms=[]
            ))
        
        return categories
    
    def _fallback_matching(self, user_skills: List[str], job_description: str, job_title: str) -> List[SkillMatch]:
        """Enhanced fallback matching using improved keyword and synonym matching"""
        matches = []
        job_text = f"{job_title} {job_description}".lower()
        
        # Enhanced synonym mapping for better fallback matching
        skill_synonyms = {
            'nurse': ['nursing', 'patient care', 'healthcare', 'medical', 'clinical', 'bedside', 'rn', 'registered nurse'],
            'healthcare': ['medical', 'health', 'clinical', 'hospital', 'clinic', 'patient', 'nursing'],
            'python': ['programming', 'coding', 'software', 'development', 'script', 'automation'],
            'data': ['analytics', 'analysis', 'statistics', 'insights', 'reporting', 'metrics'],
            'management': ['lead', 'supervise', 'coordinate', 'oversee', 'direct', 'manage'],
            'communication': ['interpersonal', 'verbal', 'written', 'presentation', 'liaison']
        }
        
        for skill in user_skills:
            skill_lower = skill.lower()
            
            # Direct match
            if skill_lower in job_text:
                matches.append(SkillMatch(
                    user_skill=skill,
                    job_skill=skill,
                    confidence=0.8,
                    reasoning=f"Direct skill match found in job requirements",
                    category="Direct Match"
                ))
                continue
            
            # Synonym matching
            synonyms = skill_synonyms.get(skill_lower, [])
            for synonym in synonyms:
                if synonym in job_text:
                    matches.append(SkillMatch(
                        user_skill=skill,
                        job_skill=synonym,
                        confidence=0.7,
                        reasoning=f"Skill '{skill}' matches '{synonym}' requirement in job",
                        category="Synonym Match"
                    ))
                    break
        
        return matches
    
    def _fallback_skill_extraction(self, job_title: str, job_description: str) -> List[str]:
        """Fallback skill extraction using keyword detection"""
        common_skills = [
            'python', 'sql', 'javascript', 'java', 'react', 'node.js', 'aws', 'docker',
            'machine learning', 'data analysis', 'excel', 'powerbi', 'tableau',
            'nursing', 'patient care', 'clinical', 'medical', 'healthcare',
            'project management', 'communication', 'leadership', 'teamwork'
        ]
        
        job_text = f"{job_title} {job_description}".lower()
        found_skills = []
        
        for skill in common_skills:
            if skill in job_text:
                found_skills.append(skill)
        
        return found_skills

# Global instance
ai_skill_matcher = AISkillMatcher()

# Async wrapper functions for easy integration
async def categorize_skills_ai(skills: List[str]) -> List[SkillCategory]:
    """Async wrapper for AI skill categorization"""
    return ai_skill_matcher.categorize_skills(skills)

async def find_skill_matches_ai(user_skills: List[str], job_description: str, job_title: str) -> List[SkillMatch]:
    """Async wrapper for AI skill matching"""
    return ai_skill_matcher.find_skill_matches(user_skills, job_description, job_title)

async def extract_job_skills_ai(job_title: str, job_description: str) -> List[str]:
    """Async wrapper for job skill extraction"""
    return await ai_skill_matcher.extract_job_skills(job_title, job_description)