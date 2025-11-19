#!/usr/bin/env python3
"""
Test the actual profiles route with minimal template
"""
import sys
import os
sys.path.insert(0, '/Applications/RF/NTU/SCTP in DSAI/SkillsMatch.AI')

from web.app import app

def test_profiles_route_detailed():
    with app.test_client() as client:
        print("🧪 Testing actual /profiles route...")
        
        # Test the profiles route
        response = client.get('/profiles')
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_text = response.get_data(as_text=True)
            
            # Check for specific content
            checks = {
                'Template loaded': '<!DOCTYPE html>' in response_text,
                'Title correct': 'Profiles - SkillsMatch.AI' in response_text,
                'Bootstrap loaded': 'bootstrap' in response_text,
                'Main content': 'Career Profiles' in response_text,
                'Profile name - Ruby': 'RUBY FERDIANTO' in response_text,
                'Profile name - Test': 'Comprehensive Test User' in response_text,
                'Profile cards': 'profile-card' in response_text,
                'Empty state': 'No Profiles Yet' in response_text,
                'Create button': 'New Profile' in response_text
            }
            
            print("🔍 Content Analysis:")
            for check, result in checks.items():
                status = "✅" if result else "❌"
                print(f"   {status} {check}")
            
            # If profiles aren't showing, check for empty state
            if not checks['Profile name - Ruby'] and not checks['Profile name - Test']:
                if checks['Empty state']:
                    print("\n⚠️  ISSUE FOUND: Template is showing empty state despite having profiles!")
                    print("   This suggests the {% if profiles %} condition is failing")
                else:
                    print("\n❌ UNKNOWN ISSUE: Neither profiles nor empty state showing")
                
                # Look for debug output we added
                if 'DEBUG: About to render template with' in response_text:
                    print("   ✅ Debug output found - profiles are being processed")
                else:
                    print("   ❌ Debug output missing - route might be failing silently")
            
            # Show relevant snippet of HTML
            print(f"\n📋 HTML snippet around profiles section:")
            lines = response_text.split('\n')
            for i, line in enumerate(lines):
                if 'Profiles Grid' in line or 'No Profiles Yet' in line:
                    start = max(0, i-2)
                    end = min(len(lines), i+10)
                    for j in range(start, end):
                        prefix = ">>> " if j == i else "    "
                        print(f"{prefix}{lines[j]}")
                    break
        else:
            print(f"❌ Route failed with status {response.status_code}")

if __name__ == "__main__":
    test_profiles_route_detailed()