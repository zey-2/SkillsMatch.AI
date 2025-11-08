#!/usr/bin/env python3
"""
Test Job Matching Functionality
Test the new job matching service with sample profile data
"""

import os
import sys
import json
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_job_matching():
    """Test the job matching service"""
    print("🧪 Testing Job Matching Service")
    print("=" * 40)
    
    try:
        from web.services.job_matching import job_matching_service
        from web.storage import profile_manager
        
        # Get a sample profile from the database
        profiles = profile_manager.list_profiles()
        if not profiles:
            print("❌ No profiles found in database")
            return
        
        # Use the first profile
        test_profile = profiles[0]
        print(f"📋 Testing with profile: {test_profile.get('name', 'Unknown')}")
        print(f"   Skills: {len(test_profile.get('skills', []))} skills")
        print(f"   Title: {test_profile.get('title', 'N/A')}")
        print(f"   Experience: {test_profile.get('experience_level', 'N/A')}")
        
        # Find job matches
        print("\n🔍 Finding job matches...")
        matches = job_matching_service.find_job_matches(
            profile_data=test_profile,
            limit=10,
            min_match_score=0.1
        )
        
        if not matches:
            print("❌ No job matches found")
            return
        
        print(f"\n✅ Found {len(matches)} job matches!")
        print("\n📊 Top 5 Matches:")
        print("-" * 50)
        
        for i, match in enumerate(matches[:5], 1):
            print(f"\n{i}. {match['job_title']} ({match['job_category']})")
            print(f"   Job ID: {match['job_id']}")
            print(f"   Match Score: {match['match_percentage']}%")
            print(f"   Skills Matched: {match['skills_matched_count']}/{match['total_job_skills']}")
            print(f"   Matched Skills: {match['matched_skills'][:3]}...")
            print(f"   Missing Skills: {match['missing_skills'][:3]}...")
            print(f"   Reason: {match['recommendation_reason']}")
        
        # Show statistics
        print(f"\n📈 Match Statistics:")
        print(f"   Best Match: {matches[0]['match_percentage']}%")
        print(f"   Average Match: {sum(m['match_percentage'] for m in matches) / len(matches):.1f}%")
        print(f"   Categories: {set(m['job_category'] for m in matches)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_call():
    """Test the API call directly"""
    print("\n🌐 Testing API Call")
    print("-" * 25)
    
    try:
        import requests
        from web.storage import profile_manager
        
        # Get a profile
        profiles = profile_manager.list_profiles()
        if not profiles:
            print("❌ No profiles found")
            return
        
        profile_id = profiles[0]['user_id']
        
        # Make API call
        response = requests.post('http://localhost:5003/api/match', json={
            'profile_id': profile_id,
            'include_database_jobs': True
        })
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API call successful!")
            print(f"   Status: {result['status']}")
            print(f"   Total matches: {result['total_matches']}")
            print(f"   Sources used: {result.get('sources_used', [])}")
            print(f"   Database matches: {result.get('database_matches', 0)}")
            
            if result['matches']:
                print(f"\n🎯 Top match: {result['matches'][0]['title']} ({result['matches'][0]['match_percentage']}%)")
            
        else:
            print(f"❌ API call failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ API test failed: {e}")

def main():
    """Run tests"""
    print("🚀 Job Matching Test Suite")
    print("=" * 50)
    
    # Test 1: Direct service call
    success1 = test_job_matching()
    
    # Test 2: API call (only if service test passed)
    if success1:
        test_api_call()
    
    print("\n" + "=" * 50)
    if success1:
        print("🎉 Job matching functionality is working!")
        print("\n📝 Next steps:")
        print("1. Go to http://localhost:5003/match")
        print("2. Select a profile and click 'Find Matches'")
        print("3. You should see job matches from the database!")
    else:
        print("❌ Job matching needs debugging")

if __name__ == '__main__':
    main()