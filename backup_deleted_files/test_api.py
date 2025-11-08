#!/usr/bin/env python3
"""
Test the job matching API endpoint directly
"""

import json
import urllib.request
import urllib.parse

def test_api():
    """Test the job matching API"""
    print("🌐 Testing Job Matching API")
    print("=" * 30)
    
    try:
        # Get profiles first
        profiles_url = "http://localhost:5004/profiles"
        with urllib.request.urlopen(profiles_url) as response:
            profiles_html = response.read().decode()
            print("✅ Profiles page accessible")
        
        # Test API with a sample profile
        api_url = "http://localhost:5004/api/match"
        
        # Sample data (using the John Developer profile)
        data = {
            "profile_id": "john_dev",
            "include_database_jobs": True
        }
        
        # Make POST request
        json_data = json.dumps(data).encode('utf-8')
        req = urllib.request.Request(
            api_url, 
            data=json_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"🔍 Making API call to {api_url}")
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            
            print(f"✅ API Response:")
            print(f"   Status: {result.get('status')}")
            print(f"   Total matches: {result.get('total_matches', 0)}")
            print(f"   Database matches: {result.get('database_matches', 0)}")
            
            if result.get('matches'):
                print(f"\n📋 Top 3 matches:")
                for i, match in enumerate(result['matches'][:3], 1):
                    title = match.get('title', 'Unknown')
                    score = match.get('match_percentage', 0)
                    print(f"   {i}. {title} - {score}%")
            
            return True
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    print("🚀 Job Matching API Test")
    print("=" * 25)
    
    success = test_api()
    
    if success:
        print("\n🎉 Job matching API is working!")
        print("\n📝 Web interface available at:")
        print("   http://localhost:5004/match")
    else:
        print("\n❌ API needs debugging")

if __name__ == '__main__':
    main()