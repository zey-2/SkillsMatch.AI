"""
Advanced AI-Powered Job Matching System for SkillsMatch.AI
Uses GitHub Copilot Pro models for comprehensive skill analysis and job matching
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from openai import OpenAI
import asyncio
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MatchInsight:
    """Structured insights from AI analysis"""
    strength_score: float
    growth_areas: List[str]
    career_trajectory: str
    salary_estimate: Optional[Dict[str, int]]
    recommendations: List[str]

@dataclass
class EnhancedMatch:
    """Enhanced match result with AI insights"""
    opportunity_id: str
    title: str
    company: str
    overall_score: float
    skill_match: float
    experience_fit: float
    cultural_fit: float
    growth_potential: float
    ai_insights: MatchInsight
    match_explanation: str
    next_steps: List[str]

class AIJobMatcher:
    """
    Advanced AI-powered job matching using GitHub Copilot Pro models
    """
    
    def __init__(self):
        self.github_client = None
        self.openai_client = None
        
        # OpenAI API models (including latest ChatGPT models)
        self.openai_models = [
            "gpt-4o",                # Latest GPT-4 Omni
            "gpt-4o-mini",          # Cost-effective GPT-4 variant
            "gpt-4-turbo",          # GPT-4 Turbo
            "gpt-4",                # Standard GPT-4
            "gpt-3.5-turbo",        # Fallback
        ]
        
        # GitHub Copilot Pro models (for users with GitHub subscription)
        self.github_models = [
            "openai/gpt-5",           # Most advanced reasoning
            "openai/gpt-4.1",        # Excellent for analysis  
            "openai/o1",             # Advanced reasoning
            "deepseek/deepseek-r1",  # Strong analytical capabilities
            "openai/gpt-4o",         # Multimodal fallback
        ]
        
        self.current_model = None
        self.current_provider = None
        self._setup_ai_clients()
    
    def _setup_ai_clients(self):
        """Setup both OpenAI and GitHub AI clients"""
        
        # Setup OpenAI client (for ChatGPT Pro users)
        try:
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                self.openai_client = OpenAI(api_key=openai_key)
                self.current_model = self.openai_models[0]  # Start with latest GPT-4o
                self.current_provider = "openai"
                logger.info(f"✅ OpenAI client initialized with {self.current_model}")
            else:
                logger.info("ℹ️ No OpenAI API key found")
        except Exception as e:
            logger.error(f"Failed to setup OpenAI client: {e}")
        
        # Setup GitHub AI client (for GitHub Copilot Pro users)
        try:
            github_token = os.getenv('GITHUB_TOKEN')
            if github_token:
                self.github_client = OpenAI(
                    base_url="https://models.github.ai/inference",
                    api_key=github_token,
                )
                
                # If no OpenAI client, use GitHub as primary
                if not self.openai_client:
                    self.current_model = self.github_models[0]
                    self.current_provider = "github"
                    logger.info(f"✅ GitHub AI client initialized as primary with {self.current_model}")
                else:
                    logger.info("✅ GitHub AI client initialized as fallback")
            else:
                logger.info("ℹ️ No GitHub token found")
        except Exception as e:
            logger.error(f"Failed to setup GitHub AI client: {e}")
        
        if not self.openai_client and not self.github_client:
            logger.warning("❌ No AI clients available - will use fallback matching")
    
    async def analyze_profile_comprehensive(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive AI analysis of user profile
        """
        if not self.github_client:
            return self._fallback_profile_analysis(profile_data)
        
        try:
            # Build comprehensive profile context
            profile_context = self._build_profile_context(profile_data)
            
            analysis_prompt = f"""
            As an expert career advisor and talent analyst, provide a comprehensive analysis of this professional profile:

            {profile_context}

            Provide a detailed JSON analysis with:
            1. "strength_score": Overall professional strength (0-100)
            2. "key_strengths": List of top 5 professional strengths
            3. "growth_areas": List of 3-5 areas for skill development
            4. "career_trajectory": Predicted career path and potential
            5. "market_value": Estimated salary range in Singapore market
            6. "competitive_advantages": Unique selling points
            7. "industry_fit": Best matching industries
            8. "skill_gaps": Common skill gaps in their field
            9. "career_recommendations": Actionable career advice

            Return only valid JSON format.
            """
            
            response = await self._call_ai_model(analysis_prompt)
            return json.loads(response)
            
        except Exception as e:
            logger.error(f"AI profile analysis failed: {e}")
            return self._fallback_profile_analysis(profile_data)
    
    async def intelligent_job_matching(
        self, 
        profile_data: Dict[str, Any], 
        opportunities: List[Dict[str, Any]]
    ) -> List[EnhancedMatch]:
        """
        Advanced AI-powered job matching with detailed insights
        """
        if not self.github_client:
            return self._fallback_matching(profile_data, opportunities)
        
        try:
            # Get profile analysis first
            profile_analysis = await self.analyze_profile_comprehensive(profile_data)
            
            enhanced_matches = []
            
            # Analyze each opportunity in batches for efficiency
            for i in range(0, len(opportunities), 5):  # Process 5 at a time
                batch = opportunities[i:i+5]
                batch_results = await self._analyze_opportunity_batch(
                    profile_data, profile_analysis, batch
                )
                enhanced_matches.extend(batch_results)
            
            # Sort by overall score
            enhanced_matches.sort(key=lambda x: x.overall_score, reverse=True)
            
            return enhanced_matches[:20]  # Top 20 matches
            
        except Exception as e:
            logger.error(f"AI job matching failed: {e}")
            return self._fallback_matching(profile_data, opportunities)
    
    async def _analyze_opportunity_batch(
        self, 
        profile_data: Dict[str, Any], 
        profile_analysis: Dict[str, Any],
        opportunities: List[Dict[str, Any]]
    ) -> List[EnhancedMatch]:
        """Analyze a batch of opportunities"""
        
        # Build context for batch analysis
        profile_summary = self._build_profile_summary(profile_data, profile_analysis)
        opportunities_context = self._build_opportunities_context(opportunities)
        
        matching_prompt = f"""
        As an expert talent matcher and career advisor, analyze how well these job opportunities match this candidate:

        CANDIDATE PROFILE:
        {profile_summary}

        JOB OPPORTUNITIES:
        {opportunities_context}

        For each opportunity, provide detailed matching analysis in JSON format:
        {{
            "matches": [
                {{
                    "opportunity_id": "job_id",
                    "overall_score": 85,
                    "skill_match": 90,
                    "experience_fit": 80,
                    "cultural_fit": 85,
                    "growth_potential": 90,
                    "match_explanation": "Detailed explanation of why this is a good match...",
                    "strengths_alignment": ["strength1", "strength2"],
                    "skill_gaps": ["gap1", "gap2"],
                    "growth_opportunities": ["opportunity1", "opportunity2"],
                    "salary_fit": "Excellent/Good/Fair/Poor",
                    "next_steps": ["step1", "step2", "step3"],
                    "interview_prep_tips": ["tip1", "tip2"]
                }}
            ]
        }}

        Consider:
        - Skill alignment and transferability
        - Career progression potential
        - Cultural and values fit
        - Growth and learning opportunities
        - Compensation alignment
        - Long-term career impact

        Return only valid JSON.
        """
        
        try:
            response = await self._call_ai_model(matching_prompt)
            analysis_result = json.loads(response)
            
            enhanced_matches = []
            for match_data in analysis_result.get('matches', []):
                # Find the corresponding opportunity
                opp = next((o for o in opportunities if o.get('opportunity_id') == match_data.get('opportunity_id')), None)
                if opp:
                    insights = MatchInsight(
                        strength_score=match_data.get('overall_score', 0),
                        growth_areas=match_data.get('skill_gaps', []),
                        career_trajectory=match_data.get('growth_opportunities', ['Unknown'])[0],
                        salary_estimate=None,  # Could be enhanced with salary data
                        recommendations=match_data.get('interview_prep_tips', [])
                    )
                    
                    enhanced_match = EnhancedMatch(
                        opportunity_id=opp.get('opportunity_id', ''),
                        title=opp.get('title', ''),
                        company=opp.get('company', {}).get('name', 'Unknown') if isinstance(opp.get('company'), dict) else str(opp.get('company', 'Unknown')),
                        overall_score=match_data.get('overall_score', 0),
                        skill_match=match_data.get('skill_match', 0),
                        experience_fit=match_data.get('experience_fit', 0),
                        cultural_fit=match_data.get('cultural_fit', 0),
                        growth_potential=match_data.get('growth_potential', 0),
                        ai_insights=insights,
                        match_explanation=match_data.get('match_explanation', ''),
                        next_steps=match_data.get('next_steps', [])
                    )
                    enhanced_matches.append(enhanced_match)
            
            return enhanced_matches
            
        except Exception as e:
            logger.error(f"Batch analysis failed: {e}")
            return []
    
    async def _call_ai_model(self, prompt: str, max_retries: int = 3) -> str:
        """Call AI model with fallback logic - tries OpenAI first, then GitHub"""
        
        messages = [
            {
                "role": "system",
                "content": "You are an expert career advisor and talent analyst with deep knowledge of the Singapore job market. Provide accurate, actionable insights in the requested format."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        
        for attempt in range(max_retries):
            # Try OpenAI models first (including latest ChatGPT models)
            if self.openai_client:
                for model in self.openai_models:
                    try:
                        logger.info(f"Trying OpenAI model: {model}")
                        response = self.openai_client.chat.completions.create(
                            model=model,
                            messages=messages,
                            max_tokens=2000,
                            temperature=0.3
                        )
                        
                        self.current_model = model
                        self.current_provider = "openai"
                        logger.info(f"✅ Success with OpenAI {model}")
                        return response.choices[0].message.content.strip()
                        
                    except Exception as e:
                        logger.warning(f"OpenAI model {model} failed (attempt {attempt + 1}): {e}")
                        continue
            
            # Fallback to GitHub models
            if self.github_client:
                for model in self.github_models:
                    try:
                        logger.info(f"Trying GitHub model: {model}")
                        response = self.github_client.chat.completions.create(
                            model=model,
                            messages=messages,
                            max_tokens=2000,
                            temperature=0.3
                        )
                        
                        self.current_model = model
                        self.current_provider = "github"
                        logger.info(f"✅ Success with GitHub {model}")
                        return response.choices[0].message.content.strip()
                        
                    except Exception as e:
                        logger.warning(f"GitHub model {model} failed (attempt {attempt + 1}): {e}")
                        continue
        
        raise Exception("All AI models failed")
    
    def _build_profile_context(self, profile_data: Dict[str, Any]) -> str:
        """Build comprehensive profile context for AI analysis"""
        
        # Basic info
        name = profile_data.get('name', 'Professional')
        title = profile_data.get('title', 'Not specified')
        location = profile_data.get('location', 'Singapore')
        experience_level = profile_data.get('experience_level', 'entry')
        
        # Skills
        skills = profile_data.get('skills', [])
        skill_list = []
        for skill in skills:
            if isinstance(skill, dict):
                skill_name = skill.get('skill_name', '')
                skill_level = skill.get('level', 'intermediate')
                years = skill.get('years_experience', 0)
                skill_list.append(f"{skill_name} ({skill_level}, {years} years)")
            else:
                skill_list.append(str(skill))
        
        # Work experience
        work_exp = profile_data.get('work_experience', [])
        experience_text = ""
        total_years = 0
        for exp in work_exp:
            position = exp.get('position', '')
            company = exp.get('company', '')
            years = exp.get('years', 0)
            description = exp.get('description', '')
            total_years += years
            experience_text += f"\n- {position} at {company} ({years} years): {description}"
        
        # Education
        education = profile_data.get('education', [])
        education_text = ""
        for edu in education:
            degree = edu.get('degree', '')
            field = edu.get('field_of_study', '')
            institution = edu.get('institution', '')
            year = edu.get('graduation_year', '')
            education_text += f"\n- {degree} in {field} from {institution} ({year})"
        
        # Goals and summary
        goals = profile_data.get('goals', '')
        summary = profile_data.get('summary', '')
        
        context = f"""
        Name: {name}
        Current Title: {title}  
        Location: {location}
        Experience Level: {experience_level}
        Total Experience: {total_years} years
        
        Skills: {', '.join(skill_list[:10])}
        
        Work Experience:{experience_text}
        
        Education:{education_text}
        
        Career Goals: {goals}
        Professional Summary: {summary}
        """
        
        return context.strip()
    
    def _build_profile_summary(self, profile_data: Dict[str, Any], profile_analysis: Dict[str, Any]) -> str:
        """Build concise profile summary for matching"""
        
        strengths = profile_analysis.get('key_strengths', [])
        trajectory = profile_analysis.get('career_trajectory', 'Not analyzed')
        industries = profile_analysis.get('industry_fit', [])
        
        return f"""
        Professional: {profile_data.get('name', 'Candidate')}
        Title: {profile_data.get('title', 'Not specified')}
        Experience: {profile_data.get('experience_level', 'entry')} level
        Location: {profile_data.get('location', 'Singapore')}
        
        Key Strengths: {', '.join(strengths[:5])}
        Career Trajectory: {trajectory}
        Industry Fit: {', '.join(industries[:3])}
        
        Top Skills: {', '.join([s.get('skill_name', '') for s in profile_data.get('skills', [])[:8]])}
        """
    
    def _build_opportunities_context(self, opportunities: List[Dict[str, Any]]) -> str:
        """Build opportunities context for AI analysis"""
        
        context = ""
        for opp in opportunities:
            opp_id = opp.get('opportunity_id', '')
            title = opp.get('title', '')
            company = opp.get('company', {})
            company_name = company.get('name', 'Unknown') if isinstance(company, dict) else str(company)
            location = opp.get('location', '')
            description = opp.get('description', '')[:200] + "..." if len(opp.get('description', '')) > 200 else opp.get('description', '')
            
            # Required skills
            required_skills = opp.get('required_skills', [])
            req_skill_names = [skill.get('skill_name', '') for skill in required_skills[:5]]
            
            context += f"""
            Job ID: {opp_id}
            Title: {title}
            Company: {company_name}
            Location: {location}
            Required Skills: {', '.join(req_skill_names)}
            Description: {description}
            ---
            """
        
        return context.strip()
    
    def _fallback_profile_analysis(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback profile analysis when AI is unavailable"""
        
        skills = profile_data.get('skills', [])
        experience_level = profile_data.get('experience_level', 'entry')
        
        # Simple rule-based analysis
        strength_score = min(100, len(skills) * 10 + (40 if experience_level == 'senior' else 20 if experience_level == 'intermediate' else 10))
        
        return {
            'strength_score': strength_score,
            'key_strengths': [skill.get('skill_name', '') for skill in skills[:5]],
            'growth_areas': ['Communication', 'Leadership', 'Technical Skills'],
            'career_trajectory': f'{experience_level.title()} professional with growth potential',
            'market_value': {'min': 50000, 'max': 100000},
            'competitive_advantages': ['Diverse skill set', 'Local market knowledge'],
            'industry_fit': ['Technology', 'Business Services'],
            'career_recommendations': ['Continue skill development', 'Build professional network']
        }
    
    def _fallback_matching(self, profile_data: Dict[str, Any], opportunities: List[Dict[str, Any]]) -> List[EnhancedMatch]:
        """Fallback matching when AI is unavailable"""
        
        matches = []
        user_skills = [skill.get('skill_name', '').lower() for skill in profile_data.get('skills', [])]
        
        for opp in opportunities[:10]:  # Limit to top 10 for fallback
            # Simple skill matching
            required_skills = opp.get('required_skills', [])
            skill_matches = sum(1 for req_skill in required_skills 
                              if any(req_skill.get('skill_name', '').lower() in user_skill for user_skill in user_skills))
            
            skill_score = (skill_matches / max(len(required_skills), 1)) * 100
            overall_score = min(100, skill_score + 20)  # Add base score
            
            insights = MatchInsight(
                strength_score=overall_score,
                growth_areas=['Communication', 'Technical Skills'],
                career_trajectory='Growth potential',
                salary_estimate=None,
                recommendations=['Research company', 'Prepare for interview']
            )
            
            match = EnhancedMatch(
                opportunity_id=opp.get('opportunity_id', ''),
                title=opp.get('title', ''),
                company=str(opp.get('company', 'Unknown')),
                overall_score=overall_score,
                skill_match=skill_score,
                experience_fit=60,
                cultural_fit=50,
                growth_potential=70,
                ai_insights=insights,
                match_explanation=f"Basic skill match analysis shows {skill_matches} matching skills.",
                next_steps=['Review job description', 'Update resume', 'Apply directly']
            )
            matches.append(match)
        
        return sorted(matches, key=lambda x: x.overall_score, reverse=True)

# Global instance
ai_job_matcher = AIJobMatcher()

async def get_ai_job_matches(profile_data: Dict[str, Any], opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convenience function for AI-powered job matching
    
    Args:
        profile_data: User profile data
        opportunities: List of job opportunities
        
    Returns:
        List of enhanced match results
    """
    try:
        enhanced_matches = await ai_job_matcher.intelligent_job_matching(profile_data, opportunities)
        
        # Convert to dictionary format for API response
        results = []
        for match in enhanced_matches:
            results.append({
                'opportunity_id': match.opportunity_id,
                'title': match.title,
                'company': match.company,
                'overall_score': match.overall_score,
                'skill_score': match.skill_match,
                'experience_score': match.experience_fit,
                'cultural_fit': match.cultural_fit,
                'growth_potential': match.growth_potential,
                'match_explanation': match.match_explanation,
                'ai_insights': {
                    'strength_score': match.ai_insights.strength_score,
                    'growth_areas': match.ai_insights.growth_areas,
                    'career_trajectory': match.ai_insights.career_trajectory,
                    'recommendations': match.ai_insights.recommendations
                },
                'next_steps': match.next_steps,
                'model_used': ai_job_matcher.current_model or 'fallback'
            })
        
        return results
        
    except Exception as e:
        logger.error(f"AI job matching failed: {e}")
        return []

if __name__ == "__main__":
    # Test the AI matcher
    import asyncio
    
    async def test_ai_matcher():
        test_profile = {
            'name': 'Test User',
            'title': 'Software Developer',
            'location': 'Singapore',
            'experience_level': 'intermediate',
            'skills': [
                {'skill_name': 'Python', 'level': 'advanced', 'years_experience': 3},
                {'skill_name': 'JavaScript', 'level': 'intermediate', 'years_experience': 2}
            ],
            'work_experience': [
                {'position': 'Developer', 'company': 'Tech Corp', 'years': 2, 'description': 'Built web applications'}
            ]
        }
        
        test_opportunities = [
            {
                'opportunity_id': 'test_001',
                'title': 'Senior Python Developer',
                'company': {'name': 'AI Startup'},
                'location': 'Singapore',
                'required_skills': [
                    {'skill_name': 'Python', 'required_level': 'advanced'},
                    {'skill_name': 'Machine Learning', 'required_level': 'intermediate'}
                ]
            }
        ]
        
        print("Testing AI Job Matcher...")
        results = await get_ai_job_matches(test_profile, test_opportunities)
        print(f"Found {len(results)} matches")
        for result in results:
            print(f"- {result['title']} at {result['company']}: {result['overall_score']}% match")
    
    asyncio.run(test_ai_matcher())