#!/usr/bin/env python3
"""
Demo: GPT-4 Analysis of SQLite Data in SkillsMatch.AI

This script demonstrates how GPT-4 can analyze data from SQLite database
to provide intelligent insights about job matching, skill trends, and career recommendations.
"""

import sys
import os
import json
import sqlite3
from typing import Dict, List, Any, Optional

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("⚠️ OpenAI not available, showing data analysis concepts only")

def get_database_path():
    """Get the SQLite database path"""
    return "web/data/skillsmatch.db"

class SQLiteGPTAnalyzer:
    """Demonstrates GPT-4 analysis of SQLite data"""
    
    def __init__(self):
        self.db_path = get_database_path()
        self.client = None
        
        if HAS_OPENAI:
            # Try different API key sources
            api_key = (
                os.environ.get('OPENAI_API_KEY') or
                os.environ.get('GITHUB_TOKEN')  # For GitHub Models
            )
            
            if api_key and api_key.startswith('ghp_'):
                # GitHub Models
                self.client = OpenAI(
                    base_url="https://models.github.ai/inference",
                    api_key=api_key
                )
                self.model = "openai/gpt-4.1-mini"
                print("✅ Using GitHub Models for AI analysis")
            elif api_key:
                # OpenAI
                self.client = OpenAI(api_key=api_key)
                self.model = "gpt-4o-mini"
                print("✅ Using OpenAI for AI analysis")
            else:
                print("⚠️ No API keys found, showing data extraction only")
    
    def get_database_summary(self) -> Dict[str, Any]:
        """Extract summary data from SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get table statistics
            tables_info = {}
            
            # Jobs data
            cursor.execute("SELECT COUNT(*) as count FROM jobs")
            jobs_count = cursor.fetchone()['count']
            
            cursor.execute("""
                SELECT category, COUNT(*) as count 
                FROM jobs 
                WHERE category IS NOT NULL 
                GROUP BY category 
                ORDER BY count DESC 
                LIMIT 10
            """)
            job_categories = [dict(row) for row in cursor.fetchall()]
            
            # User profiles data
            cursor.execute("SELECT COUNT(*) as count FROM user_profiles WHERE is_active = 1")
            profiles_count = cursor.fetchone()['count']
            
            cursor.execute("""
                SELECT experience_level, COUNT(*) as count 
                FROM user_profiles 
                WHERE experience_level IS NOT NULL AND is_active = 1
                GROUP BY experience_level
            """)
            experience_levels = [dict(row) for row in cursor.fetchall()]
            
            # Skills data
            cursor.execute("SELECT COUNT(*) as count FROM skills")
            skills_count = cursor.fetchone()['count']
            
            cursor.execute("""
                SELECT s.skill_name, COUNT(us.user_id) as user_count
                FROM skills s
                LEFT JOIN user_skills_detail us ON s.skill_id = us.skill_id
                GROUP BY s.skill_id, s.skill_name
                HAVING user_count > 0
                ORDER BY user_count DESC
                LIMIT 15
            """)
            popular_skills = [dict(row) for row in cursor.fetchall()]
            
            return {
                'database_path': self.db_path,
                'tables': {
                    'jobs': {
                        'count': jobs_count,
                        'categories': job_categories
                    },
                    'user_profiles': {
                        'count': profiles_count,
                        'experience_levels': experience_levels
                    },
                    'skills': {
                        'count': skills_count,
                        'popular_skills': popular_skills
                    }
                }
            }
    
    def get_specific_profile_data(self, user_name: str = "TIM COOKING") -> Optional[Dict]:
        """Get specific user profile data for AI analysis"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get user profile
            cursor.execute("""
                SELECT * FROM user_profiles 
                WHERE name LIKE ? AND is_active = 1
            """, (f"%{user_name}%",))
            
            profile = cursor.fetchone()
            if not profile:
                return None
            
            profile_dict = dict(profile)
            
            # Get user skills
            cursor.execute("""
                SELECT s.skill_name, us.level, us.years_experience
                FROM user_skills_detail us
                JOIN skills s ON us.skill_id = s.skill_id
                WHERE us.user_id = ?
            """, (profile['user_id'],))
            
            profile_dict['skills'] = [dict(row) for row in cursor.fetchall()]
            
            # Get work experience
            cursor.execute("""
                SELECT company, position, years, description
                FROM work_experience
                WHERE user_id = ?
                ORDER BY start_date DESC
            """, (profile['user_id'],))
            
            profile_dict['work_experience'] = [dict(row) for row in cursor.fetchall()]
            
            return profile_dict
    
    def get_matching_jobs_data(self, user_skills: List[str], limit: int = 10) -> List[Dict]:
        """Get potential matching jobs from database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Create skill search pattern
            skill_pattern = '|'.join(user_skills)
            
            cursor.execute("""
                SELECT 
                    id, title, company_name, location, category,
                    job_description, employment_type, experience_level,
                    salary_range, keywords
                FROM jobs
                WHERE job_description LIKE ? 
                   OR keywords LIKE ?
                   OR title LIKE ?
                   OR category LIKE ?
                ORDER BY 
                    CASE 
                        WHEN category LIKE '%healthcare%' OR category LIKE '%medical%' THEN 1
                        WHEN job_description LIKE '%nurse%' OR job_description LIKE '%patient%' THEN 2
                        ELSE 3
                    END
                LIMIT ?
            """, (f"%{skill_pattern}%", f"%{skill_pattern}%", f"%{skill_pattern}%", f"%{skill_pattern}%", limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    async def analyze_with_gpt4(self, data: Dict[str, Any], analysis_type: str = "job_matching") -> str:
        """Use GPT-4 to analyze the database data"""
        if not self.client:
            return "GPT-4 analysis not available (no API key configured)"
        
        if analysis_type == "job_matching":
            prompt = f"""
            You are an expert career counselor analyzing job matching data from a SQLite database.
            
            Database Summary:
            {json.dumps(data.get('database_summary', {}), indent=2)}
            
            User Profile:
            {json.dumps(data.get('user_profile', {}), indent=2)}
            
            Potential Matching Jobs:
            {json.dumps(data.get('matching_jobs', []), indent=2)}
            
            Please provide a comprehensive analysis including:
            
            1. **Profile Assessment**: Analyze the user's skills, experience, and career background
            2. **Job Market Analysis**: What the database reveals about available opportunities
            3. **Matching Strategy**: How to improve job matching for this profile
            4. **Skill Gap Analysis**: What skills might be missing for better matches
            5. **Career Recommendations**: Specific advice based on the data
            
            Focus on actionable insights and data-driven recommendations.
            """
        
        elif analysis_type == "database_insights":
            prompt = f"""
            You are a data analyst examining a job matching platform's SQLite database.
            
            Database Analysis Data:
            {json.dumps(data, indent=2)}
            
            Please provide insights on:
            
            1. **Market Trends**: What industries and skills are most in demand?
            2. **User Demographics**: Profile distribution and experience levels
            3. **Skill Demand**: Most popular skills vs. market needs
            4. **Platform Health**: Database metrics and potential improvements
            5. **Business Intelligence**: Key findings for platform optimization
            
            Provide specific numbers and percentages where possible.
            """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"GPT-4 analysis failed: {e}"
    
    def demonstrate_analysis(self):
        """Demonstrate complete GPT-4 analysis of SQLite data"""
        print("🔍 SQLite + GPT-4 Analysis Demo for SkillsMatch.AI")
        print("=" * 60)
        
        # 1. Extract database summary
        print("\n📊 Step 1: Extracting data from SQLite database...")
        db_summary = self.get_database_summary()
        print(f"✅ Found {db_summary['tables']['jobs']['count']} jobs, {db_summary['tables']['user_profiles']['count']} profiles")
        
        # 2. Get specific user data
        print("\n👤 Step 2: Analyzing specific user profile...")
        profile_data = self.get_specific_profile_data("TIM COOKING")
        if profile_data:
            print(f"✅ Found profile: {profile_data['name']}")
            print(f"📋 Skills: {[skill['skill_name'] for skill in profile_data['skills']]}")
            
            # 3. Get matching jobs
            print("\n🎯 Step 3: Finding potential job matches...")
            user_skills = [skill['skill_name'] for skill in profile_data['skills']]
            matching_jobs = self.get_matching_jobs_data(user_skills, 5)
            print(f"✅ Found {len(matching_jobs)} potential matches")
            
            # 4. GPT-4 Analysis
            if self.client:
                print("\n🤖 Step 4: GPT-4 Analysis of the data...")
                analysis_data = {
                    'database_summary': db_summary,
                    'user_profile': profile_data,
                    'matching_jobs': matching_jobs
                }
                
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                gpt_analysis = loop.run_until_complete(
                    self.analyze_with_gpt4(analysis_data, "job_matching")
                )
                
                print("🎯 GPT-4 Career Analysis Results:")
                print("-" * 40)
                print(gpt_analysis)
            else:
                print("\n⚠️ GPT-4 analysis skipped (no API key)")
                print("📋 Raw data would be sent to GPT-4 for analysis:")
                print(f"- User: {profile_data['name']}")
                print(f"- Skills: {user_skills}")
                print(f"- Potential jobs: {len(matching_jobs)}")
        else:
            print("❌ TIM COOKING profile not found")
        
        # 5. Database insights
        print("\n📈 Step 5: Overall database insights...")
        print(f"📊 Popular skills: {db_summary['tables']['skills']['popular_skills'][:5]}")
        print(f"🏢 Job categories: {db_summary['tables']['jobs']['categories'][:5]}")

def main():
    """Main demonstration function"""
    analyzer = SQLiteGPTAnalyzer()
    analyzer.demonstrate_analysis()

if __name__ == "__main__":
    main()