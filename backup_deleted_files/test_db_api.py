#!/usr/bin/env python3
"""
Test the updated job matching API with database jobs
"""

import json

def test_api_curl():
    """Test using curl command"""
    import subprocess
    
    print("🌐 Testing Job Matching API with curl")
    print("=" * 40)
    
    # Test with a specific profile ID that exists
    payload = {
        "profile_id": "john_dev",
        "include_database_jobs": True,
        "use_ai": False
    }
    
    curl_cmd = [
        'curl', '-s', '-X', 'POST',
        'http://localhost:5003/api/match',
        '-H', 'Content-Type: application/json',
        '-d', json.dumps(payload)
    ]
    
    try:
        result = subprocess.run(curl_cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            response = json.loads(result.stdout)
            print(f"✅ API Response received!")
            print(f"   Status: {response.get('status')}")
            print(f"   Profile: {response.get('profile_name')}")
            print(f"   Total matches: {response.get('total_matches', 0)}")
            print(f"   Database matches: {response.get('database_matches', 0)}")
            
            if response.get('matches'):
                print(f"\n📋 Sample matches:")
                for i, match in enumerate(response['matches'][:3], 1):
                    title = match.get('title', 'Unknown')
                    score = match.get('match_percentage', 0)
                    source = match.get('source', 'unknown')
                    print(f"   {i}. {title} - {score}% (source: {source})")
            
            return True
        else:
            print(f"❌ Curl failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("🚀 Database Job Matching API Test")
    print("=" * 35)
    
    success = test_api_curl()
    
    print("\n" + "=" * 35)
    if success:
        print("🎉 Database job matching API is working!")
        print("\n📝 Frontend should now show:")
        print("   • Database job matches from PostgreSQL")
        print("   • Match percentages and skill analysis")
        print("   • No SSG-WSG API calls")
    else:
        print("❌ API needs debugging")

if __name__ == '__main__':
    main()