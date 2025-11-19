#!/usr/bin/env python3
"""
Quick test to verify profiles route functionality
"""
import sys
import os
sys.path.insert(0, '/Applications/RF/NTU/SCTP in DSAI/SkillsMatch.AI')

from web.app import app
from web.storage import profile_manager

def test_profiles_route():
    with app.test_client() as client:
        print("🧪 Testing /profiles route...")
        
        # Test the profiles route
        response = client.get('/profiles')
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Route accessible")
            # Check if response contains profile data
            response_text = response.get_data(as_text=True)
            
            # Check for common profile elements
            if 'profile.name' in response_text or 'No profiles found' in response_text:
                print("✅ Template rendered correctly")
                
                # Check for specific profile names we know exist
                if 'RUBY FERDIANTO' in response_text:
                    print("✅ Ruby's profile found in HTML")
                elif 'Comprehensive Test User' in response_text:
                    print("✅ Test profile found in HTML")
                else:
                    print("⚠️  Profiles exist but not showing in HTML")
                    print("First 500 chars of response:")
                    print(response_text[:500])
            else:
                print("❌ Template not rendering profiles correctly")
                print("First 300 chars of response:")
                print(response_text[:300])
        else:
            print(f"❌ Route failed with status {response.status_code}")
            print(response.get_data(as_text=True)[:300])

if __name__ == "__main__":
    # First check profile manager directly
    print("🔍 Direct profile manager test:")
    profiles = profile_manager.list_profiles()
    print(f"Found {len(profiles)} profiles directly")
    for p in profiles:
        print(f"  - {p.get('name')} ({p.get('user_id')})")
    
    print("\n" + "="*50)
    test_profiles_route()