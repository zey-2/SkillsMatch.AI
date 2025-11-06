"""
AI-Powered Professional Summary Generator for SkillsMatch.AI
Generates concise professional summaries from resume text using AI models
"""
import os
import logging
import json
from typing import Optional, Dict, Any
import openai
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIProfileSummarizer:
    """
    AI-powered service for generating professional summaries from resume text
    """
    
    def __init__(self):
        self.openai_client = None
        self.github_client = None
        self.max_summary_length = 500
        
        # Initialize AI clients
        self._setup_ai_clients()
    
    def _setup_ai_clients(self):
        """Setup OpenAI and GitHub AI clients"""
        try:
            # OpenAI setup
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                self.openai_client = OpenAI(api_key=openai_key)
                logger.info("✅ OpenAI client initialized")
            
            # GitHub Models setup
            github_token = os.getenv('GITHUB_TOKEN')
            if github_token:
                self.github_client = OpenAI(
                    base_url="https://models.inference.ai.azure.com",
                    api_key=github_token,
                )
                logger.info("✅ GitHub Models client initialized")
                
        except Exception as e:
            logger.warning(f"AI client setup warning: {e}")
    
    def generate_professional_summary(self, resume_text: str, profile_data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate a professional summary from resume text
        
        Args:
            resume_text: Extracted text from resume/CV
            profile_data: Optional existing profile data for context
            
        Returns:
            Dictionary with generated summary and metadata
        """
        
        if not resume_text or len(resume_text.strip()) < 50:
            return {
                'success': False,
                'error': 'Insufficient resume text for summary generation',
                'summary': '',
                'model_used': None,
                'word_count': 0
            }
        
        # Prepare context information
        context_info = self._prepare_context(resume_text, profile_data)
        
        # Try different AI models in order of preference (optimized for ChatGPT Pro)
        models_to_try = [
            ('openai', 'gpt-4o'),           # ChatGPT Pro - Best for comprehensive analysis
            ('openai', 'gpt-4o-mini'),     # ChatGPT Pro - Cost-effective variant
            ('openai', 'gpt-4-turbo'),     # ChatGPT Pro - Fast and reliable
            ('openai', 'gpt-3.5-turbo'),   # Standard fallback
            ('github', 'gpt-4o-mini'),     # GitHub fallback
        ]
        
        for provider, model_name in models_to_try:
            try:
                result = self._generate_with_model(context_info, provider, model_name)
                if result['success']:
                    return result
                    
            except Exception as e:
                logger.warning(f"Failed to generate summary with {provider}/{model_name}: {e}")
                continue
        
        # Fallback to rule-based summary if AI fails
        return self._generate_fallback_summary(resume_text, profile_data)
    
    def _prepare_context(self, resume_text: str, profile_data: Optional[Dict] = None) -> Dict[str, str]:
        """Prepare context information for AI prompt"""
        
        # Truncate resume text if too long (to fit within token limits)
        max_resume_length = 2000
        if len(resume_text) > max_resume_length:
            resume_text = resume_text[:max_resume_length] + "..."
        
        context = {
            'resume_text': resume_text,
            'existing_title': '',
            'existing_experience_level': '',
            'existing_skills': ''
        }
        
        if profile_data:
            context['existing_title'] = profile_data.get('title', '')
            context['existing_experience_level'] = profile_data.get('experience_level', '')
            
            # Extract skills if available
            skills = profile_data.get('skills', [])
            if skills:
                skill_names = [skill.get('skill_name', '') for skill in skills if skill.get('skill_name')]
                context['existing_skills'] = ', '.join(skill_names[:10])  # Limit to top 10 skills
        
        return context
    
    def _generate_with_model(self, context: Dict[str, str], provider: str, model_name: str) -> Dict[str, Any]:
        """Generate summary using specific AI model"""
        
        client = None
        if provider == 'openai' and self.openai_client:
            client = self.openai_client
        elif provider == 'github' and self.github_client:
            client = self.github_client
        
        if not client:
            return {
                'success': False,
                'error': f'{provider} client not available'
            }
        
        # Create the prompt
        prompt = self._create_summary_prompt(context)
        
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional career counselor and resume writer. Generate concise, impactful professional summaries."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=150,  # Limit response length
                temperature=0.7
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Ensure summary is within character limit
            if len(summary) > self.max_summary_length:
                summary = summary[:self.max_summary_length - 3] + "..."
            
            return {
                'success': True,
                'summary': summary,
                'model_used': f'{provider}/{model_name}',
                'word_count': len(summary.split()),
                'char_count': len(summary),
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'AI generation failed: {str(e)}'
            }
    
    def _create_summary_prompt(self, context: Dict[str, str]) -> str:
        """Create AI prompt for summary generation"""
        
        prompt = f"""
Based on the following resume/CV text, generate a professional summary in exactly 500 characters or less.

Resume Text:
{context['resume_text']}

Additional Context:
- Current Title: {context['existing_title']}
- Experience Level: {context['existing_experience_level']}
- Key Skills: {context['existing_skills']}

Requirements:
1. Maximum 500 characters (including spaces)
2. Focus on key strengths, experience, and value proposition
3. Use professional, confident language
4. Highlight most relevant skills and achievements
5. Make it compelling for recruiters
6. Do not use bullet points or special formatting
7. Write in third person (e.g., "Experienced software developer...")

Generate only the summary text, no additional explanation.
"""
        
        return prompt.strip()
    
    def _generate_fallback_summary(self, resume_text: str, profile_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Generate a rule-based summary if AI fails"""
        
        try:
            # Extract key information from resume text
            words = resume_text.lower().split()
            
            # Identify experience level
            experience_indicators = {
                'senior': ['senior', 'lead', 'principal', 'manager', 'director'],
                'mid': ['specialist', 'analyst', 'coordinator', 'associate'],
                'entry': ['junior', 'intern', 'assistant', 'trainee']
            }
            
            experience_level = 'professional'
            for level, indicators in experience_indicators.items():
                if any(indicator in words for indicator in indicators):
                    experience_level = level
                    break
            
            # Extract potential skills (common tech/business terms)
            common_skills = [
                'python', 'java', 'javascript', 'react', 'node', 'sql', 'aws', 'azure',
                'project management', 'leadership', 'communication', 'analysis', 'design',
                'marketing', 'sales', 'finance', 'operations', 'strategy'
            ]
            
            found_skills = [skill for skill in common_skills if skill in resume_text.lower()]
            skills_text = ', '.join(found_skills[:5]) if found_skills else 'various technical and business'
            
            # Generate template-based summary
            title = 'Professional'
            if profile_data and profile_data.get('title'):
                title = profile_data['title']
            
            title_lower = title.lower() if title else 'professional'
            
            summary_templates = [
                f"Experienced {title_lower} with expertise in {skills_text} skills. Proven track record of delivering results in dynamic environments. Strong analytical and problem-solving abilities with excellent communication skills.",
                f"{experience_level.title()} {title_lower} skilled in {skills_text}. Demonstrates strong leadership and technical capabilities. Committed to driving innovation and achieving organizational goals.",
                f"Results-driven {title_lower} with proficiency in {skills_text}. Excellent collaboration and project management skills. Passionate about continuous learning and professional development."
            ]
            
            # Choose template and ensure it fits within character limit
            import random
            summary = random.choice(summary_templates)
            
            if len(summary) > self.max_summary_length:
                summary = summary[:self.max_summary_length - 3] + "..."
            
            return {
                'success': True,
                'summary': summary,
                'model_used': 'fallback/rule-based',
                'word_count': len(summary.split()),
                'char_count': len(summary),
                'error': None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Fallback summary generation failed: {e}',
                'summary': '',
                'model_used': None,
                'word_count': 0
            }

# Global instance
ai_summarizer = AIProfileSummarizer()

def generate_profile_summary(resume_text: str, profile_data: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Convenience function to generate professional summary
    
    Args:
        resume_text: Text extracted from resume/CV
        profile_data: Optional existing profile data
        
    Returns:
        Dictionary with generated summary and metadata
    """
    return ai_summarizer.generate_professional_summary(resume_text, profile_data)

if __name__ == "__main__":
    # Test the summarizer
    test_resume_text = """
    John Doe
    Senior Software Engineer
    
    Experience:
    - 5 years of experience in full-stack development
    - Proficient in Python, JavaScript, React, Node.js
    - Led team of 4 developers on multiple projects
    - Expertise in AWS cloud services and database design
    
    Education:
    - Bachelor's degree in Computer Science
    - Certified AWS Solutions Architect
    
    Skills: Python, JavaScript, React, Node.js, AWS, SQL, MongoDB
    """
    
    print("Testing AI Professional Summary Generator")
    print("=" * 50)
    
    result = generate_profile_summary(test_resume_text)
    
    print(f"Success: {result['success']}")
    print(f"Model used: {result.get('model_used', 'N/A')}")
    print(f"Character count: {result.get('char_count', 0)}/500")
    print(f"Word count: {result.get('word_count', 0)}")
    
    if result['success']:
        print(f"\\nGenerated Summary:")
        print(f'"{result["summary"]}"')
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")