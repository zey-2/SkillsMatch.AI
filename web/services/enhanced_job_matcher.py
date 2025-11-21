"""
Enhanced Job Matching Service with AI-Powered Skill Analysis

This service combines traditional keyword matching with AI-powered semantic analysis
for more accurate and intelligent job matching.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime

from .ai_skill_matcher import ai_skill_matcher, SkillMatch, SkillCategory

logger = logging.getLogger(__name__)

@dataclass
class JobMatchResult:
    """Enhanced job match result with AI insights"""
    job_id: int
    match_score: float
    skill_matches: List[SkillMatch]
    industry_match: bool
    location_match: bool
    experience_match: bool
    ai_reasoning: str
    match_breakdown: Dict[str, float]
    recommended_skills: List[str]

class EnhancedJobMatcher:
    """AI-enhanced job matching service"""
    
    def __init__(self):
        self.skill_matcher = ai_skill_matcher
        self.match_cache = {}
    
    async def find_matches(self, user_profile: Dict, jobs_list: List[Dict], limit: int = 10) -> List[JobMatchResult]:
        """
        Find job matches using AI-enhanced analysis
        
        Args:
            user_profile: User profile data with skills, experience, etc.
            jobs_list: List of job opportunities
            limit: Maximum number of matches to return
            
        Returns:
            List of JobMatchResult objects sorted by match score
        """
        try:
            # Extract user data
            user_skills = self._extract_user_skills(user_profile)
            user_location = (user_profile.get('location') or '').lower()
            user_experience = (user_profile.get('experience_level') or 'entry').lower()
            user_title = (user_profile.get('title') or '').lower()
            
            logger.info(f"🔍 AI-enhanced matching for {len(user_skills)} skills across {len(jobs_list)} jobs")
            
            # Process jobs in parallel for better performance
            match_tasks = []
            for job in jobs_list[:100]:  # Limit to first 100 jobs for performance
                task = self._analyze_job_match(user_skills, user_location, user_experience, user_title, job)
                match_tasks.append(task)
            
            # Execute AI analysis in batches to avoid rate limits
            batch_size = 10
            all_matches = []
            
            for i in range(0, len(match_tasks), batch_size):
                batch = match_tasks[i:i + batch_size]
                batch_results = await asyncio.gather(*batch, return_exceptions=True)
                
                for result in batch_results:
                    if isinstance(result, JobMatchResult):
                        all_matches.append(result)
                    elif isinstance(result, Exception):
                        logger.error(f"❌ Job matching error: {result}")
                
                # Small delay between batches to respect rate limits
                if i + batch_size < len(match_tasks):
                    await asyncio.sleep(0.1)
            
            # Sort by match score and return top matches
            all_matches.sort(key=lambda x: x.match_score, reverse=True)
            top_matches = all_matches[:limit]
            
            logger.info(f"✅ Found {len(top_matches)} top matches with AI analysis")
            return top_matches
            
        except Exception as e:
            logger.error(f"❌ Enhanced job matching failed: {e}")
            return self._fallback_matching(user_profile, jobs_list, limit)
    
    async def _analyze_job_match(self, user_skills: List[str], user_location: str, 
                                user_experience: str, user_title: str, job: Dict) -> JobMatchResult:
        """Analyze a single job match using AI"""
        try:
            job_id = job.get('id', 0)
            job_title = job.get('title', '')
            job_description = job.get('description', '')
            job_location = (job.get('location') or '').lower()
            job_experience = (job.get('experience_level') or '').lower()
            company_name = job.get('company_name', '')
            
            # Use AI to find skill matches
            skill_matches = self.skill_matcher.find_skill_matches(
                user_skills, job_description, job_title
            )
            
            # Calculate various match factors
            skill_score = self._calculate_skill_score(skill_matches)
            location_match = self._check_location_match(user_location, job_location)
            experience_match = self._check_experience_match(user_experience, job_experience)
            industry_match = await self._check_industry_match(user_title, job_title, job_description)
            
            # Calculate overall match score with weighted factors
            weights = {
                'skills': 0.5,
                'location': 0.2,
                'experience': 0.2,
                'industry': 0.1
            }
            
            match_score = (
                skill_score * weights['skills'] +
                (1.0 if location_match else 0.3) * weights['location'] +
                (1.0 if experience_match else 0.5) * weights['experience'] +
                (1.0 if industry_match else 0.4) * weights['industry']
            )
            
            # Generate AI reasoning
            ai_reasoning = self._generate_match_reasoning(
                skill_matches, location_match, experience_match, industry_match, job_title
            )
            
            # Extract recommended skills for improvement
            recommended_skills = await self._get_recommended_skills(
                user_skills, job_description, job_title
            )
            
            match_breakdown = {
                'skills': skill_score,
                'location': 1.0 if location_match else 0.3,
                'experience': 1.0 if experience_match else 0.5,
                'industry': 1.0 if industry_match else 0.4
            }
            
            return JobMatchResult(
                job_id=job_id,
                match_score=match_score,
                skill_matches=skill_matches,
                industry_match=industry_match,
                location_match=location_match,
                experience_match=experience_match,
                ai_reasoning=ai_reasoning,
                match_breakdown=match_breakdown,
                recommended_skills=recommended_skills
            )
            
        except Exception as e:
            logger.error(f"❌ Job analysis failed for job {job.get('id', 'unknown')}: {e}")
            # Return basic match result as fallback
            return JobMatchResult(
                job_id=job.get('id', 0),
                match_score=0.3,
                skill_matches=[],
                industry_match=False,
                location_match=False,
                experience_match=False,
                ai_reasoning="Basic matching used due to AI analysis error",
                match_breakdown={'skills': 0.3, 'location': 0.3, 'experience': 0.3, 'industry': 0.3},
                recommended_skills=[]
            )
    
    def _extract_user_skills(self, user_profile: Dict) -> List[str]:
        """Extract and normalize user skills"""
        skills = []
        
        if user_profile.get('skills'):
            for skill in user_profile['skills']:
                if isinstance(skill, dict):
                    skill_name = skill.get('skill_name', '')
                else:
                    skill_name = str(skill)
                if skill_name:
                    skills.append(skill_name.lower().strip())
        
        return list(set([skill for skill in skills if skill]))
    
    def _calculate_skill_score(self, skill_matches: List[SkillMatch]) -> float:
        """Calculate skill match score from AI-generated matches"""
        if not skill_matches:
            return 0.0
        
        # Weight matches by confidence and calculate average
        total_confidence = sum(match.confidence for match in skill_matches)
        return min(total_confidence / len(skill_matches), 1.0)
    
    def _check_location_match(self, user_location: str, job_location: str) -> bool:
        """Check if locations match (including remote options)"""
        if not user_location or not job_location:
            return True  # No location preference
        
        if 'remote' in job_location or 'remote' in user_location:
            return True
        
        # Check for city/state matches
        location_keywords = user_location.split()
        return any(keyword in job_location for keyword in location_keywords if len(keyword) > 2)
    
    def _check_experience_match(self, user_experience: str, job_experience: str) -> bool:
        """Check if experience levels match"""
        if not job_experience:
            return True
        
        experience_mapping = {
            'entry': ['entry', 'junior', 'beginner', '0-1', '0-2'],
            'junior': ['entry', 'junior', '1-3', '2-4'],
            'mid': ['mid', 'intermediate', '3-5', '4-6', '2-5'],
            'senior': ['senior', '5+', '7+', '5-10'],
            'lead': ['lead', 'principal', 'senior', '8+', '10+']
        }
        
        user_exp_keywords = experience_mapping.get(user_experience, [user_experience])
        return any(keyword in job_experience.lower() for keyword in user_exp_keywords)
    
    async def _check_industry_match(self, user_title: str, job_title: str, job_description: str) -> bool:
        """Use AI to check industry/role compatibility"""
        try:
            if not user_title:
                return True
            
            # Simple keyword matching as fallback
            user_keywords = user_title.lower().split()
            job_text = f"{job_title} {job_description}".lower()
            
            return any(keyword in job_text for keyword in user_keywords if len(keyword) > 3)
            
        except Exception:
            return False
    
    def _generate_match_reasoning(self, skill_matches: List[SkillMatch], location_match: bool,
                                 experience_match: bool, industry_match: bool, job_title: str) -> str:
        """Generate human-readable match reasoning"""
        reasons = []
        
        if skill_matches:
            high_confidence_matches = [m for m in skill_matches if m.confidence > 0.7]
            if high_confidence_matches:
                reasons.append(f"Strong skill alignment with {len(high_confidence_matches)} key matches")
            else:
                reasons.append(f"Moderate skill compatibility with {len(skill_matches)} potential matches")
        
        if location_match:
            reasons.append("Location compatible")
        
        if experience_match:
            reasons.append("Experience level aligned")
        
        if industry_match:
            reasons.append("Industry background relevant")
        
        if not reasons:
            reasons.append("Basic qualification match")
        
        return f"Match for {job_title}: " + ", ".join(reasons)
    
    async def _get_recommended_skills(self, user_skills: List[str], job_description: str, job_title: str) -> List[str]:
        """Get AI-recommended skills for better matching"""
        try:
            # Extract job skills and find gaps
            job_skills = await self.skill_matcher.extract_job_skills(job_title, job_description)
            
            # Find skills mentioned in job but not in user profile
            user_skills_lower = [skill.lower() for skill in user_skills]
            recommended = []
            
            for job_skill in job_skills:
                if job_skill.lower() not in user_skills_lower:
                    recommended.append(job_skill)
            
            return recommended[:5]  # Return top 5 recommendations
            
        except Exception:
            return []
    
    def _fallback_matching(self, user_profile: Dict, jobs_list: List[Dict], limit: int) -> List[JobMatchResult]:
        """Fallback matching using traditional methods"""
        logger.warning("🔄 Using fallback matching due to AI service unavailability")
        
        user_skills = self._extract_user_skills(user_profile)
        matches = []
        
        for job in jobs_list[:limit]:
            job_text = f"{job.get('title', '')} {job.get('description', '')}".lower()
            
            # Simple keyword matching
            skill_count = sum(1 for skill in user_skills if skill in job_text)
            match_score = min(skill_count / max(len(user_skills), 1) * 0.8, 0.8)
            
            matches.append(JobMatchResult(
                job_id=job.get('id', 0),
                match_score=match_score,
                skill_matches=[],
                industry_match=False,
                location_match=True,
                experience_match=True,
                ai_reasoning=f"Fallback matching: {skill_count} skill keywords found",
                match_breakdown={'skills': match_score, 'location': 0.8, 'experience': 0.8, 'industry': 0.5},
                recommended_skills=[]
            ))
        
        matches.sort(key=lambda x: x.match_score, reverse=True)
        return matches

# Global instance
enhanced_job_matcher = EnhancedJobMatcher()

# Async wrapper function
async def find_enhanced_matches(user_profile: Dict, jobs_list: List[Dict], limit: int = 10) -> List[JobMatchResult]:
    """Find enhanced job matches using AI analysis"""
    return await enhanced_job_matcher.find_matches(user_profile, jobs_list, limit)