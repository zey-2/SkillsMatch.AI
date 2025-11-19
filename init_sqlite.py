#!/usr/bin/env python3
"""
SQLite Database Initialization for SkillsMatch.AI
Creates tables and loads sample data for deployment
"""
import os
import sys
import json
from pathlib import Path

# Add project paths
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / 'web'))

def initialize_sqlite_database():
    """Initialize SQLite database with tables and sample data"""
    try:
        # Set environment to use SQLite
        os.environ['USE_SQLITE'] = 'true'
        os.environ['RENDER'] = 'true'  # Simulate production environment
        
        from web.database.db_config import db_config
        from web.database.models import Base, Job
        
        print("🗃️ Initializing SQLite database...")
        
        # Create all tables
        Base.metadata.create_all(db_config.engine)
        print("✅ Database tables created successfully")
        
        # Add sample jobs if database is empty
        with db_config.session_scope() as session:
            existing_jobs = session.query(Job).count()
            
            if existing_jobs == 0:
                print("📊 Adding sample job data...")
                
                # Sample jobs for testing
                sample_jobs = [
                    {
                        'job_id': 'SM001',
                        'job_title': 'Python Developer',
                        'category': 'Technology',
                        'job_description': 'We are looking for a skilled Python developer to join our team. Experience with Flask, Django, and data analysis required.',
                        'job_skill_set': ['Python', 'Flask', 'Django', 'SQL', 'Git', 'REST API']
                    },
                    {
                        'job_id': 'SM002', 
                        'job_title': 'Data Scientist',
                        'category': 'Data Science',
                        'job_description': 'Seeking a data scientist with expertise in machine learning, statistical analysis, and Python programming.',
                        'job_skill_set': ['Python', 'Machine Learning', 'Pandas', 'NumPy', 'SQL', 'Statistics', 'Jupyter']
                    },
                    {
                        'job_id': 'SM003',
                        'job_title': 'Full Stack Developer',
                        'category': 'Technology', 
                        'job_description': 'Full stack developer needed for web application development using modern frameworks and technologies.',
                        'job_skill_set': ['JavaScript', 'React', 'Node.js', 'Python', 'SQL', 'MongoDB', 'Git']
                    },
                    {
                        'job_id': 'SM004',
                        'job_title': 'DevOps Engineer',
                        'category': 'Technology',
                        'job_description': 'DevOps engineer to manage cloud infrastructure, CI/CD pipelines, and deployment automation.',
                        'job_skill_set': ['AWS', 'Docker', 'Kubernetes', 'Python', 'Linux', 'Git', 'CI/CD']
                    },
                    {
                        'job_id': 'SM005',
                        'job_title': 'Business Analyst',
                        'category': 'Business',
                        'job_description': 'Business analyst to work with stakeholders and translate requirements into technical specifications.',
                        'job_skill_set': ['SQL', 'Excel', 'Power BI', 'Business Analysis', 'Communication', 'Project Management']
                    }
                ]
                
                for job_data in sample_jobs:
                    job = Job(
                        job_id=job_data['job_id'],
                        job_title=job_data['job_title'],
                        category=job_data['category'],
                        job_description=job_data['job_description'],
                        job_skill_set=job_data['job_skill_set'],
                        is_active=True
                    )
                    session.add(job)
                
                session.commit()
                print(f"✅ Added {len(sample_jobs)} sample jobs to database")
            else:
                print(f"📊 Database already contains {existing_jobs} jobs")
        
        print("🎉 SQLite database initialization complete!")
        print("📂 Database location: web/data/skillsmatch.db")
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = initialize_sqlite_database()
    sys.exit(0 if success else 1)