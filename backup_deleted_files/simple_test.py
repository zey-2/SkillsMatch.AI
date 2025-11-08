#!/usr/bin/env python3
"""
Simple test for job matching functionality
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_job_matching():
    """Test the job matching service"""
    print("🧪 Testing Job Matching Service")
    print("=" * 40)
    
    try:
        from web.services.job_matching import job_matching_service
        from web.storage import profile_manager
        
        print("✅ Successfully imported job matching service")
        print("✅ Successfully imported profile manager")
        
        # Get profiles
        profiles = profile_manager.list_profiles()
        print(f"📋 Found {len(profiles)} profiles in database")
        
        if not profiles:
            print("❌ No profiles found - create a profile first!")
            return False
        
        # Use the first profile
        test_profile = profiles[0]
        print(f"📋 Testing with profile: {test_profile.get('name', 'Unknown')}")
        print(f"   Skills: {test_profile.get('skills', [])}")
        
        # Find job matches
        print("\n🔍 Finding job matches...")
        try:
            matches = job_matching_service.find_job_matches(
                profile_data=test_profile,
                limit=5,
                min_match_score=0.1
            )
        except Exception as e:
            print(f"❌ Error finding job matches: {e}")
            matches = []
        
        print(f"✅ Found {len(matches)} job matches!")
        
        if matches:
            print("\n📊 Top 3 Matches:")
            for i, match in enumerate(matches[:3], 1):
                print(f"{i}. {match['job_title']} - {match['match_percentage']}%")
                print(f"   Category: {match['job_category']}")
                print(f"   Skills Matched: {match['skills_matched_count']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_database():
    """Check database connection and data"""
    try:
        from web.database.models import Job
        from web.database.db_config import db_config
        
        # Get session
        session = db_config.get_session()
        
        # Count jobs
        job_count = session.query(Job).count()
        print(f"📊 Jobs in database: {job_count}")
        
        # Sample job
        sample_job = session.query(Job).first()
        if sample_job:
            print(f"📄 Sample job: {sample_job.job_title}")
            print(f"   Category: {sample_job.category}")
            skills = sample_job.job_skill_set or []
            print(f"   Skills: {len(skills)} skills")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False

def main():
    print("🚀 Simple Job Matching Test")
    print("=" * 30)
    
    # Check database first
    db_ok = check_database()
    
    if db_ok:
        # Test job matching
        success = test_job_matching()
        
        if success:
            print("\n🎉 Job matching is working!")
            print("\n📝 Test the web interface:")
            print("1. Go to http://localhost:5003/match")
            print("2. Select a profile")
            print("3. Click 'Find Matches'")
        else:
            print("\n❌ Job matching needs debugging")
    else:
        print("\n❌ Database connection issues")

if __name__ == '__main__':
    main()