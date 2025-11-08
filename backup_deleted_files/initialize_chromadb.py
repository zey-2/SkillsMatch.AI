#!/usr/bin/env python3
"""
ChromaDB Initialization Script for SkillsMatch.AI
Populates ChromaDB with existing job data and resumes
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'web'))

def initialize_chromadb():
    """Initialize ChromaDB with existing data"""
    try:
        print("🚀 Initializing ChromaDB for SkillsMatch.AI")
        print("=" * 50)
        
        # Import ChromaDB service
        from web.services.chroma_service import get_chroma_service
        chroma_service = get_chroma_service()
        
        print("✅ ChromaDB service initialized")
        
        # 1. Initialize with existing resume files
        print("\n📄 Processing existing resume files...")
        chroma_service.initialize_existing_resumes("uploads/resumes")
        
        # 2. Initialize with database jobs
        print("\n💼 Processing database jobs...")
        try:
            from web.database.db_config import db_config
            from web.database.models import Job
            
            with db_config.session_scope() as session:
                jobs = session.query(Job).filter(Job.is_active == True).limit(1000).all()
                print(f"📊 Found {len(jobs)} active jobs in database")
                
                success_count = 0
                for job in jobs:
                    job_data = {
                        'title': job.job_title,
                        'description': job.job_description or '',
                        'requirements': job.job_requirements or '',
                        'skills': job.job_skill_set or [],
                        'company': 'Various Companies',
                        'location': 'Multiple Locations',
                        'category': job.category or 'General'
                    }
                    
                    success = chroma_service.add_job_to_vector_db(
                        job_id=str(job.job_id),
                        job_data=job_data
                    )
                    
                    if success:
                        success_count += 1
                    
                    # Progress indicator
                    if success_count % 100 == 0:
                        print(f"   Processed {success_count} jobs...")
                
                print(f"✅ Successfully added {success_count} jobs to vector database")
                
        except Exception as db_error:
            print(f"⚠️ Database job initialization failed: {db_error}")
            print("   Continuing with resume initialization only...")
        
        print("\n🎉 ChromaDB initialization complete!")
        print("=" * 50)
        print("📊 Vector Database Status:")
        
        # Get status information
        try:
            resume_count = len(chroma_service.resume_collection.get()['ids'])
            job_count = len(chroma_service.job_collection.get()['ids'])
            
            print(f"   📄 Resume documents: {resume_count}")
            print(f"   💼 Job documents: {job_count}")
        except Exception as e:
            print(f"   ⚠️ Could not get collection stats: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB initialization failed: {e}")
        return False

def test_vector_search():
    """Test the vector search functionality"""
    try:
        print("\n🔍 Testing vector search functionality...")
        
        from web.services.chroma_service import get_chroma_service
        chroma_service = get_chroma_service()
        
        # Test search with sample resume text
        test_resume = """
        Software Engineer with 5 years experience in Python, JavaScript, and React.
        Experienced in machine learning, data analysis, and web development.
        Strong background in computer science and artificial intelligence.
        """
        
        results = chroma_service.search_similar_jobs(test_resume, n_results=5)
        
        print(f"✅ Vector search test successful!")
        print(f"   Found {len(results)} similar jobs")
        
        for i, result in enumerate(results[:3], 1):
            print(f"   {i}. {result.get('title', 'N/A')} (similarity: {result.get('similarity_score', 0):.2f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector search test failed: {e}")
        return False

if __name__ == "__main__":
    print("ChromaDB Initialization for SkillsMatch.AI")
    print("=========================================")
    
    # Initialize ChromaDB
    success = initialize_chromadb()
    
    if success:
        # Test vector search
        test_vector_search()
        
        print("\n🚀 Ready to use ChromaDB-powered semantic job matching!")
        print("   Start the web application with: python web/app.py")
    else:
        print("\n❌ Initialization failed. Please check the error messages above.")
        sys.exit(1)