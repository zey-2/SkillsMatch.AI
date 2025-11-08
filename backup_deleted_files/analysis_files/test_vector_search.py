#!/usr/bin/env python3
"""
Test Vector Search Integration
Quick test to verify vector search is working in the web app
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_vector_search():
    """Test vector search functionality"""
    print("🧪 Testing Vector Search Integration")
    print("=" * 40)
    
    try:
        # Import and test vector service
        from web.services.simple_vector_service import get_vector_service
        
        vector_service = get_vector_service()
        
        print(f"📊 Vector service status:")
        print(f"   📄 Resumes: {len(vector_service.resume_data)}")
        print(f"   💼 Jobs: {len(vector_service.job_data)}")
        
        # Test with sample resume text
        if len(vector_service.resume_data) > 0:
            sample_resume = vector_service.resume_data[0]
            print(f"\n🔍 Testing search with resume: {sample_resume['profile_id']}")
            
            # Create some sample jobs for testing
            sample_jobs = [
                {
                    'id': 'test_job_1',
                    'title': 'Software Engineer',
                    'description': 'Python developer position with Flask and AI experience',
                    'company': 'Tech Corp',
                    'location': 'Singapore',
                    'category': 'Technology',
                    'skills': ['Python', 'Flask', 'AI', 'Machine Learning']
                },
                {
                    'id': 'test_job_2', 
                    'title': 'Data Scientist',
                    'description': 'Data analysis and machine learning specialist role',
                    'company': 'Data Inc',
                    'location': 'Singapore',
                    'category': 'Data Science',
                    'skills': ['Python', 'Machine Learning', 'Data Analysis', 'SQL']
                },
                {
                    'id': 'test_job_3',
                    'title': 'Frontend Developer',
                    'description': 'React and JavaScript web development position',
                    'company': 'Web Solutions',
                    'location': 'Singapore', 
                    'category': 'Web Development',
                    'skills': ['JavaScript', 'React', 'HTML', 'CSS']
                }
            ]
            
            # Add sample jobs to vector database
            print(f"\n➕ Adding {len(sample_jobs)} sample jobs...")
            for job in sample_jobs:
                success = vector_service.add_job_to_vector_db(job['id'], job)
                if success:
                    print(f"   ✅ Added: {job['title']}")
            
            # Test vector search
            resume_text = sample_resume['text_content'][:1000]  # First 1000 chars
            print(f"\n🔍 Performing vector search...")
            
            results = vector_service.search_similar_jobs(resume_text, n_results=5)
            
            print(f"\n📊 Search Results ({len(results)} found):")
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result['title']} at {result['company']}")
                print(f"      📈 Similarity: {result['similarity_score']:.3f}")
                print(f"      📝 Match: {result['matched_text'][:100]}...")
                print()
            
            if len(results) > 0:
                print("✅ Vector search is working correctly!")
            else:
                print("⚠️ Vector search returned no results")
        
        else:
            print("⚠️ No resumes found for testing")
        
        print(f"\n🎉 Vector search test completed!")
        
    except Exception as e:
        print(f"❌ Vector search test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vector_search()