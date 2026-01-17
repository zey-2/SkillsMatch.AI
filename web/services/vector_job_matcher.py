"""
Efficient Vector-Based Job Matching Service
Uses pre-computed job embeddings for fast, single-AI-call matching.
"""

import os
import json
import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from openai import OpenAI
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class VectorJobMatcher:
    def __init__(self):
        self.openai_client = None
        self.jobs_data = []
        self.job_embeddings = {}
        self.initialize_openai()
        self.load_job_vectors()
    
    def initialize_openai(self):
        """Initialize OpenAI client"""
        openai_key = os.environ.get('OPENAI_API_KEY')
        if openai_key:
            self.openai_client = OpenAI(api_key=openai_key)
            logger.info("✅ Vector matcher initialized with OpenAI")
        else:
            logger.warning("⚠️ No OpenAI key - using fallback vector matching")
    
    def load_job_vectors(self):
        """Load pre-computed job vectors"""
        try:
            data_dir = Path(__file__).parent.parent / "data"
            
            # Load job data
            jobs_file = data_dir / "jobs_vector_data.json"
            if jobs_file.exists():
                with open(jobs_file, 'r') as f:
                    self.jobs_data = json.load(f)
                logger.info(f"📊 Loaded {len(self.jobs_data)} jobs")
            else:
                logger.warning(
                    "⚠️ Job vector data not found - run scripts/generate_job_vectors.py first"
                )
            
            # Load embeddings
            embeddings_file = data_dir / "job_embeddings.pkl"
            if embeddings_file.exists():
                with open(embeddings_file, 'rb') as f:
                    self.job_embeddings = pickle.load(f)
                logger.info(f"🎯 Loaded {len(self.job_embeddings)} job embeddings")
            else:
                logger.warning(
                    "⚠️ Job embeddings not found - run scripts/generate_job_vectors.py first"
                )
                
        except Exception as e:
            logger.error(f"❌ Error loading job vectors: {e}")
    
    def create_user_profile_text(self, profile_data: Dict) -> str:
        """Create comprehensive user profile text for embedding"""
        profile_parts = []
        
        # Basic info - EXCLUDE name to avoid name-based matching bias
        # Names like "TIM COOKING" should not influence job matching
        if profile_data.get('title'):
            profile_parts.append(f"Current Title: {profile_data['title']}")
        
        # Summary
        if profile_data.get('summary'):
            profile_parts.append(f"Summary: {profile_data['summary']}")
        
        # Skills
        skills = []
        if profile_data.get('skills'):
            for skill in profile_data['skills']:
                if isinstance(skill, dict):
                    skill_name = skill.get('skill_name', '')
                    level = skill.get('level', '')
                    if skill_name:
                        if level:
                            skills.append(f"{skill_name} ({level})")
                        else:
                            skills.append(skill_name)
                elif isinstance(skill, str):
                    skills.append(skill)
        
        if skills:
            profile_parts.append(f"Skills: {', '.join(skills)}")
        
        # Experience
        if profile_data.get('experience_level'):
            profile_parts.append(f"Experience Level: {profile_data['experience_level']}")
        
        # Location and preferences
        if profile_data.get('location'):
            profile_parts.append(f"Location: {profile_data['location']}")
        
        if profile_data.get('goals'):
            profile_parts.append(f"Career Goals: {profile_data['goals']}")
        
        return " | ".join(profile_parts)
    
    def get_user_embedding(self, profile_text: str) -> Optional[List[float]]:
        """Get embedding for user profile"""
        if not self.openai_client:
            return None
        
        try:
            response = self.openai_client.embeddings.create(
                model="text-embedding-3-small",
                input=[profile_text]
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"❌ Error getting user embedding: {e}")
            return None
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Calculate cosine similarity between embeddings"""
        try:
            # Convert to numpy arrays
            vec1 = np.array(embedding1)
            vec2 = np.array(embedding2)
            
            # Calculate cosine similarity
            dot_product = np.dot(vec1, vec2)
            norm1 = np.linalg.norm(vec1)
            norm2 = np.linalg.norm(vec2)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            similarity = dot_product / (norm1 * norm2)
            return float(similarity)
        except Exception as e:
            logger.error(f"❌ Error calculating similarity: {e}")
            return 0.0
    
    def find_top_matches_vector(self, profile_data: Dict, top_n: int = 15) -> List[Dict]:
        """Find top job matches using vector similarity"""
        if not self.jobs_data or not self.job_embeddings:
            logger.warning("⚠️ No job vectors available - using fallback")
            return []
        
        # Create user profile embedding
        profile_text = self.create_user_profile_text(profile_data)
        user_embedding = self.get_user_embedding(profile_text)
        
        if not user_embedding:
            logger.warning("⚠️ Could not create user embedding - using enhanced skill matching")
            return self.text_based_fallback(profile_data, top_n)
        
        # Calculate similarities
        job_similarities = []
        
        for job in self.jobs_data:
            job_id = job['job_id']
            
            if job_id in self.job_embeddings:
                job_embedding = self.job_embeddings[job_id]
                similarity = self.calculate_similarity(user_embedding, job_embedding)
                
                job_similarities.append({
                    'job': job,
                    'similarity': similarity
                })
        
        # Sort by similarity and return top matches
        job_similarities.sort(key=lambda x: x['similarity'], reverse=True)
        top_matches = job_similarities[:top_n]
        
        logger.info(f"🎯 Found {len(top_matches)} vector-based matches")
        return [match['job'] for match in top_matches]
    
    def text_based_fallback(self, profile_data: Dict, top_n: int = 15) -> List[Dict]:
        """Enhanced skill-based matching as fallback"""
        user_skills = set()
        if profile_data.get('skills'):
            for skill in profile_data['skills']:
                if isinstance(skill, dict):
                    skill_name = skill.get('skill_name', '').lower()
                    if skill_name:
                        user_skills.add(skill_name)
                elif isinstance(skill, str):
                    user_skills.add(skill.lower())
        
        # Enhanced skill synonyms and related terms
        skill_synonyms = {
            'nurse': ['nurse', 'nursing', 'healthcare', 'medical', 'patient care', 'clinical', 'ward', 'hospital', 'health'],
            'nursing': ['nurse', 'nursing', 'healthcare', 'medical', 'patient care', 'clinical', 'ward', 'hospital', 'health'],
            'healthcare': ['healthcare', 'medical', 'health', 'clinical', 'patient', 'hospital', 'nursing', 'nurse'],
            'medical': ['medical', 'healthcare', 'health', 'clinical', 'patient', 'hospital', 'nursing', 'nurse'],
            'python': ['python', 'django', 'flask', 'pandas', 'numpy', 'programming', 'developer'],
            'java': ['java', 'spring', 'programming', 'developer', 'software'],
            'javascript': ['javascript', 'js', 'node', 'react', 'vue', 'angular', 'web development'],
            'sql': ['sql', 'database', 'mysql', 'postgresql', 'data'],
            'marketing': ['marketing', 'digital marketing', 'social media', 'advertising', 'promotion'],
            'sales': ['sales', 'selling', 'business development', 'account management', 'customer'],
            'hr': ['hr', 'human resources', 'recruitment', 'hiring', 'people'],
            'finance': ['finance', 'accounting', 'financial', 'budget', 'money'],
            'engineering': ['engineering', 'engineer', 'technical', 'design', 'development'],
            'management': ['management', 'manager', 'leadership', 'team lead', 'supervisor']
        }
        
        # Expand user skills with synonyms
        expanded_skills = set(user_skills)
        for skill in user_skills:
            if skill in skill_synonyms:
                expanded_skills.update(skill_synonyms[skill])
        
        job_scores = []
        for job in self.jobs_data:
            job_text = f"{job.get('title', '')} {job.get('description', '')} {job.get('company_name', '')}".lower()
            
            # Calculate skill match score
            direct_matches = sum(1 for skill in user_skills if skill in job_text)
            synonym_matches = sum(1 for skill in expanded_skills if skill in job_text and skill not in user_skills)
            
            # Weight direct matches higher than synonym matches
            total_score = (direct_matches * 2.0) + (synonym_matches * 0.5)
            match_ratio = total_score / len(user_skills) if user_skills else 0
            
            # Bonus for exact title matches
            job_title = job.get('title', '').lower()
            for skill in user_skills:
                if skill in job_title:
                    match_ratio += 2.0  # Big bonus for title matches
            
            # Special healthcare relevance bonus
            healthcare_indicators = ['patient', 'ward', 'medical', 'clinical', 'health', 'care', 'hospital']
            healthcare_bonus = sum(1 for indicator in healthcare_indicators if indicator in job_text)
            if 'nurse' in user_skills or 'nursing' in user_skills:
                match_ratio += healthcare_bonus * 0.5  # Bonus for healthcare-related content
            
            # Strong penalty for completely unrelated jobs  
            unrelated_keywords = ['lift', 'elevator', 'mechanical', 'despatch', 'warehouse', 'logistics', 'barista', 'tea', 'beverage']
            unrelated_count = sum(1 for keyword in job_text if keyword in unrelated_keywords)
            if unrelated_count > 0 and not any(skill in job_text for skill in expanded_skills):
                match_ratio *= (0.1 ** unrelated_count)  # Heavy penalty scales with unrelated terms
            
            job_scores.append({
                'job': job,
                'score': match_ratio,
                'direct_matches': direct_matches,
                'synonym_matches': synonym_matches
            })
        
        # Sort by score and filter out zero-score matches if we have good matches
        job_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # If we have good matches (score > 0.5), filter out poor matches
        if job_scores and job_scores[0]['score'] > 0.5:
            filtered_scores = [job for job in job_scores if job['score'] > 0.1]
            if len(filtered_scores) >= 5:  # Ensure we have enough matches
                job_scores = filtered_scores
        
        logger.info(f"🎯 Text fallback: Top match score {job_scores[0]['score']:.2f} for {job_scores[0]['job']['title']}")
        return [match['job'] for match in job_scores[:top_n]]
    
    def analyze_matches_with_ai(self, profile_data: Dict, top_jobs: List[Dict]) -> Dict:
        """Single AI call to analyze top matches"""
        if not self.openai_client or not top_jobs:
            return self.generate_fallback_analysis(profile_data, top_jobs)
        
        try:
            # Create analysis prompt
            profile_summary = self.create_user_profile_text(profile_data)
            
            jobs_summary = []
            for i, job in enumerate(top_jobs[:10], 1):  # Analyze top 10
                job_summary = f"{i}. {job.get('title', 'Unknown')} at {job.get('company_name', 'Unknown')}"
                if job.get('description'):
                    job_summary += f" - {job['description'][:200]}..."
                jobs_summary.append(job_summary)
            
            prompt = f"""Analyze job matches for this candidate:

CANDIDATE PROFILE:
{profile_summary}

TOP JOB MATCHES:
{chr(10).join(jobs_summary)}

Provide a JSON response with:
1. "top_3_jobs": Array of job numbers (1-10) that are the best matches
2. "match_reasoning": Brief explanation for each top 3 job
3. "skill_gaps": Skills the candidate should develop
4. "overall_assessment": Brief overall matching assessment

Keep response concise and practical."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.3
            )
            
            # Parse AI response
            ai_content = response.choices[0].message.content
            logger.info("✅ AI match analysis completed")
            
            return {
                'ai_analysis': ai_content,
                'analysis_method': 'ai_powered',
                'jobs_analyzed': len(top_jobs)
            }
            
        except Exception as e:
            logger.error(f"❌ AI analysis failed: {e}")
            return self.generate_fallback_analysis(profile_data, top_jobs)
    
    def generate_fallback_analysis(self, profile_data: Dict, top_jobs: List[Dict]) -> Dict:
        """Generate analysis without AI"""
        analysis = {
            'ai_analysis': f"Found {len(top_jobs)} potential matches based on skill and profile similarity. Top jobs are ranked by relevance to your background.",
            'analysis_method': 'vector_similarity',
            'jobs_analyzed': len(top_jobs)
        }
        
        return analysis
    
    def match_jobs_efficiently(self, profile_data: Dict, limit: int = 10) -> Dict:
        """Main efficient matching method - single AI call approach"""
        try:
            logger.info(f"🚀 Starting efficient vector-based job matching")
            
            # Step 1: Find top matches using vectors (fast)
            top_jobs = self.find_top_matches_vector(profile_data, top_n=20)
            
            if not top_jobs:
                return {
                    'matches': [],
                    'analysis': 'No suitable jobs found',
                    'method': 'no_matches'
                }
            
            # Step 2: Single AI call to analyze top matches
            ai_analysis = self.analyze_matches_with_ai(profile_data, top_jobs)
            
            # Step 3: Format final results
            final_matches = []
            for i, job in enumerate(top_jobs[:limit]):
                match_result = {
                    'job_id': job.get('job_id'),
                    'title': job.get('title'),
                    'company_name': job.get('company_name'),
                    'location': job.get('location'),
                    'description': job.get('description', '')[:300] + '...',
                    'match_rank': i + 1,
                    'match_method': 'vector_similarity'
                }
                final_matches.append(match_result)
            
            result = {
                'matches': final_matches,
                'analysis': ai_analysis,
                'total_jobs_considered': len(self.jobs_data),
                'method': 'efficient_vector_matching',
                'ai_calls_used': 1 if ai_analysis.get('analysis_method') == 'ai_powered' else 0
            }
            
            logger.info(f"✅ Efficient matching complete: {len(final_matches)} matches, {result['ai_calls_used']} AI calls")
            return result
            
        except Exception as e:
            logger.error(f"❌ Efficient matching failed: {e}")
            return {
                'matches': [],
                'analysis': f'Matching failed: {str(e)}',
                'method': 'error'
            }

# Global instance
vector_job_matcher = VectorJobMatcher()