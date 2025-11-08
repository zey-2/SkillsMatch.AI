#!/usr/bin/env python3
"""
Simple Vector Database Initialization for SkillsMatch.AI
Initialize vector search with existing resumes and jobs
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    """Initialize vector database"""
    print("Simple Vector Database Initialization for SkillsMatch.AI")
    print("=" * 55)
    
    try:
        print("🚀 Initializing Simple Vector Search for SkillsMatch.AI")
        print("=" * 55)
        
        # Import the vector service
        from web.services.simple_vector_service import get_vector_service
        
        # Get vector service instance
        vector_service = get_vector_service()
        
        # Initialize with existing jobs from database
        print("\n💼 Loading jobs from database...")
        try:
            from web.services.job_matching import JobMatchingService
            job_service = JobMatchingService()
            
            # Get database session
            with job_service.db_config.get_db() as db:
                from web.database.models import Job
                
                # Query all jobs
                jobs_query = db.query(Job).all()
                jobs = []
                
                for job_obj in jobs_query:
                    job_dict = {
                        'id': job_obj.id,
                        'title': job_obj.title or '',
                        'description': job_obj.description or '',
                        'company': job_obj.company or 'Various Companies',
                        'location': job_obj.location or 'Multiple Locations',
                        'category': job_obj.category or 'General',
                        'requirements': job_obj.requirements or [],
                        'skills': job_obj.skills or []
                    }
                    jobs.append(job_dict)
                
                print(f"📊 Found {len(jobs)} jobs in database")
                
                # Add jobs to vector database
                for i, job in enumerate(jobs, 1):
                    job_id = str(job['id'])
                    success = vector_service.add_job_to_vector_db(job_id, job)
                    if success and i % 100 == 0:  # Progress indicator
                        print(f"   📈 Processed {i}/{len(jobs)} jobs...")
                        
                print(f"✅ Successfully processed {len(jobs)} jobs")
            
        except Exception as job_error:
            print(f"⚠️ Could not load jobs from database: {job_error}")
            print("   This is normal if database is not set up")
        
        # Summary
        print(f"\n🎉 Vector Database Initialization Complete!")
        print(f"   📄 Resumes in vector DB: {len(vector_service.resume_data)}")
        print(f"   💼 Jobs in vector DB: {len(vector_service.job_data)}")
        
        # Test vector search if we have data
        if len(vector_service.resume_data) > 0 and len(vector_service.job_data) > 0:
            print(f"\n🧪 Testing vector search...")
            test_resume = vector_service.resume_data[0]
            test_results = vector_service.search_similar_jobs(
                test_resume['text_content'][:500],  # First 500 chars
                n_results=3
            )
            print(f"   🔍 Test search returned {len(test_results)} results")
            for result in test_results[:2]:
                print(f"      - {result['title']} (similarity: {result['similarity_score']:.3f})")
        
        print(f"\n✨ Vector database is ready for semantic job matching!")
        
    except Exception as e:
        print(f"❌ Vector database initialization failed: {e}")
        import traceback
        traceback.print_exc()
        print(f"\n❌ Initialization failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()