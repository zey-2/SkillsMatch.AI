"""
Job Matching Service
Service for matching user profiles with job postings from the jobs table
"""

from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
import re
from datetime import datetime

import sys
import os

# Ensure proper path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
web_dir = os.path.dirname(current_dir)
sys.path.insert(0, web_dir)

try:
    from database.db_config import db_config
    from database.models import Job, Skill, UserProfile
    from sqlalchemy import func, or_, and_
    from sqlalchemy.orm import Session
except ImportError as e:
    print(f"Import error in job_matching.py: {e}")
    # Try absolute imports
    try:
        from web.database.db_config import db_config
        from web.database.models import Job, Skill, UserProfile
        from sqlalchemy import func, or_, and_
        from sqlalchemy.orm import Session
    except ImportError as e2:
        print(f"Absolute import also failed: {e2}")
        raise

class JobMatchingService:
    """Service for matching user profiles with job postings"""
    
    def __init__(self):
        self.db_config = db_config
    
    def find_job_matches(
        self, 
        profile_data: Dict[str, Any], 
        limit: int = 20,
        min_match_score: float = 0.1
    ) -> List[Dict[str, Any]]:
        """
        Find job matches for a user profile based on skills matching
        
        Args:
            profile_data: User profile data dictionary
            limit: Maximum number of matches to return
            min_match_score: Minimum match score (0-1) to include
        
        Returns:
            List of matched jobs with scores and details
        """
        try:
            with self.db_config.session_scope() as session:
                # Extract user profile information
                user_skills = self._extract_user_skills(profile_data)
                user_location = (profile_data.get('location') or '').lower()
                user_experience = (profile_data.get('experience_level') or 'entry').lower()
                user_category = self._infer_user_category(profile_data)
                
                print(f"🔍 Searching jobs for user with {len(user_skills)} skills")
                print(f"   User skills: {user_skills[:5]}...")  # Show first 5
                
                # Get all jobs from database
                jobs = session.query(Job).filter(Job.is_active == True).all()
                print(f"📊 Found {len(jobs)} active jobs in database")
                
                # Calculate matches
                matches = []
                for job in jobs:
                    match_result = self._calculate_job_match(
                        job, user_skills, user_location, user_experience, user_category
                    )
                    
                    if match_result['match_score'] >= min_match_score:
                        matches.append(match_result)
                
                # Sort by match score (highest first)
                matches.sort(key=lambda x: x['match_score'], reverse=True)
                
                print(f"✅ Found {len(matches)} job matches (min score: {min_match_score})")
                
                return matches[:limit]
                
        except Exception as e:
            print(f"❌ Error finding job matches: {e}")
            return []
    
    def _extract_user_skills(self, profile_data: Dict[str, Any]) -> List[str]:
        """Extract and normalize user skills from profile data"""
        user_skills = []
        
        # Extract skills from different possible formats
        skills_data = profile_data.get('skills', [])
        
        if isinstance(skills_data, list):
            for skill in skills_data:
                if isinstance(skill, dict):
                    skill_name = skill.get('skill_name', '')
                elif isinstance(skill, str):
                    skill_name = skill
                else:
                    continue
                
                if skill_name:
                    user_skills.append(skill_name.lower().strip())
        
        # Also check legacy skills format
        if 'skill_names' in profile_data:
            legacy_skills = profile_data['skill_names']
            if isinstance(legacy_skills, list):
                user_skills.extend([skill.lower().strip() for skill in legacy_skills if skill])
        
        # Remove duplicates and empty strings
        user_skills = list(set([skill for skill in user_skills if skill]))
        
        return user_skills
    
    def _infer_user_category(self, profile_data: Dict[str, Any]) -> str:
        """Infer user's job category from profile data"""
        title = (profile_data.get('title') or '').lower()
        experience = profile_data.get('work_experience', [])
        
        # Category keywords mapping
        category_keywords = {
            'hr': ['human resources', 'hr', 'talent', 'recruitment', 'recruiting'],
            'information-technology': ['developer', 'engineer', 'software', 'programming', 'it', 'tech', 'data'],
            'finance': ['finance', 'accounting', 'financial', 'analyst', 'controller', 'cfo'],
            'sales': ['sales', 'account manager', 'business development', 'marketing'],
            'business-development': ['business', 'strategy', 'consulting', 'operations']
        }
        
        # Check title and work experience
        text_to_check = title
        if isinstance(experience, list):
            for exp in experience:
                if isinstance(exp, dict):
                    text_to_check += ' ' + exp.get('position', '') + ' ' + exp.get('company', '')
        
        text_to_check = (text_to_check or '').lower()
        
        # Find best matching category
        best_category = 'general'
        max_matches = 0
        
        for category, keywords in category_keywords.items():
            matches = sum(1 for keyword in keywords if keyword in text_to_check)
            if matches > max_matches:
                max_matches = matches
                best_category = category
        
        return best_category
    
    def _calculate_job_match(
        self, 
        job: Job, 
        user_skills: List[str], 
        user_location: str, 
        user_experience: str,
        user_category: str
    ) -> Dict[str, Any]:
        """Calculate match score between user and job"""
        
        job_skills = job.job_skill_set or []
        job_skills_lower = [skill.lower().strip() for skill in job_skills if skill and isinstance(skill, str)]
        
        # 1. Skill matching (70% weight)
        skill_matches = 0
        matched_skills = []
        missing_skills = []
        
        for job_skill in job_skills_lower:
            # Exact match
            if job_skill in user_skills:
                skill_matches += 1
                matched_skills.append(job_skill)
            # Partial match (contains)
            elif any(job_skill in user_skill or user_skill in job_skill for user_skill in user_skills):
                skill_matches += 0.7  # Partial match gets 70% score
                matched_skills.append(job_skill)
            else:
                missing_skills.append(job_skill)
        
        # Calculate skill match percentage
        total_job_skills = len(job_skills_lower) if job_skills_lower else 1
        skill_match_score = min(skill_matches / total_job_skills, 1.0)
        
        # 2. Category matching (20% weight)
        category_match_score = 0.0
        if job.category and user_category:
            if job.category.lower().replace('-', '').replace('_', '') == user_category.lower().replace('-', '').replace('_', ''):
                category_match_score = 1.0
            elif any(word in job.category.lower() for word in user_category.lower().split('-')):
                category_match_score = 0.6
        
        # 3. Experience level matching (10% weight) - simplified for now
        experience_match_score = 0.5  # Default neutral score
        
        # Calculate overall match score (weighted average)
        overall_score = (
            skill_match_score * 0.7 +
            category_match_score * 0.2 +
            experience_match_score * 0.1
        )
        
        # Calculate match percentage for display
        user_skills_matched = len(matched_skills)
        total_user_skills = len(user_skills) if user_skills else 1
        user_skill_coverage = user_skills_matched / total_user_skills
        
        return {
            'job_id': job.job_id,
            'job_title': job.job_title,
            'job_category': job.category,
            'job_description': job.job_description,
            'required_skills': job_skills,
            'match_score': round(overall_score, 3),
            'skill_match_score': round(skill_match_score, 3),
            'category_match_score': round(category_match_score, 3),
            'experience_match_score': round(experience_match_score, 3),
            'matched_skills': matched_skills,
            'missing_skills': missing_skills[:10],  # Limit to top 10 missing skills
            'skills_matched_count': user_skills_matched,
            'total_job_skills': len(job_skills),
            'user_skill_coverage': round(user_skill_coverage, 3),
            'match_percentage': round(overall_score * 100, 1),
            'created_at': job.created_at.isoformat() if job.created_at else None,
            'recommendation_reason': self._generate_recommendation_reason(
                skill_match_score, category_match_score, len(matched_skills), len(missing_skills)
            )
        }
    
    def _generate_recommendation_reason(
        self, 
        skill_score: float, 
        category_score: float, 
        matched_count: int, 
        missing_count: int
    ) -> str:
        """Generate a human-readable reason for the job recommendation"""
        
        reasons = []
        
        if skill_score >= 0.8:
            reasons.append(f"Excellent skill match ({matched_count} skills match)")
        elif skill_score >= 0.6:
            reasons.append(f"Good skill match ({matched_count} skills match)")
        elif skill_score >= 0.4:
            reasons.append(f"Moderate skill match ({matched_count} skills match)")
        else:
            reasons.append(f"Some skill overlap ({matched_count} skills match)")
        
        if category_score >= 0.8:
            reasons.append("Perfect category fit")
        elif category_score >= 0.5:
            reasons.append("Good category match")
        
        if missing_count <= 2:
            reasons.append("Few skills to learn")
        elif missing_count <= 5:
            reasons.append("Some new skills to develop")
        else:
            reasons.append("Growth opportunity with new skills")
        
        return " • ".join(reasons) if reasons else "Potential career opportunity"
    
    def get_job_categories(self) -> List[Dict[str, Any]]:
        """Get job categories with counts"""
        try:
            with self.db_config.session_scope() as session:
                results = session.query(
                    Job.category,
                    func.count(Job.id).label('count')
                ).group_by(Job.category).order_by(func.count(Job.id).desc()).all()
                
                categories = []
                for category, count in results:
                    categories.append({
                        'category': category or 'Unknown',
                        'count': count
                    })
                
                return categories
                
        except Exception as e:
            print(f"❌ Error getting job categories: {e}")
            return []
    
    def get_top_job_skills(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get most common skills across all jobs"""
        try:
            with self.db_config.session_scope() as session:
                jobs = session.query(Job).filter(Job.is_active == True).all()
                
                # Count all skills
                skill_counter = Counter()
                for job in jobs:
                    if job.job_skill_set:
                        for skill in job.job_skill_set:
                            skill_counter[skill.strip()] += 1
                
                # Format results
                top_skills = []
                for skill, count in skill_counter.most_common(limit):
                    top_skills.append({
                        'skill': skill,
                        'job_count': count,
                        'percentage': round((count / len(jobs)) * 100, 1)
                    })
                
                return top_skills
                
        except Exception as e:
            print(f"❌ Error getting top job skills: {e}")
            return []

# Global service instance
job_matching_service = JobMatchingService()