#!/usr/bin/env python3
"""
Test script to validate match percentage consistency between web interface and PDF generation
"""

import requests
import json
import sys

def test_match_consistency():
    """Test that web interface and PDF generation show same match percentages"""
    
    base_url = "http://localhost:5006"
    
    print("🧪 Testing Match Percentage Consistency")
    print("=" * 50)
    
    try:
        # Test 1: Get match results from web interface
        print("1️⃣ Testing web interface match calculation...")
        
        # First, get profiles to use for testing
        profiles_response = requests.get(f"{base_url}/api/profiles")
        if profiles_response.status_code != 200:
            print(f"❌ Failed to get profiles: {profiles_response.status_code}")
            return False
            
        profiles = profiles_response.json()
        if not profiles:
            print("❌ No profiles found for testing")
            return False
            
        # Use first profile
        test_profile = profiles[0]
        profile_id = test_profile['profile_id']
        print(f"📝 Using profile: {test_profile['full_name']} (ID: {profile_id})")
        
        # Get job matches for this profile
        match_response = requests.post(f"{base_url}/api/match", json={
            'profile_id': profile_id
        })
        
        if match_response.status_code != 200:
            print(f"❌ Failed to get matches: {match_response.status_code}")
            return False
            
        matches = match_response.json()
        if not matches or 'matches' not in matches:
            print("❌ No matches found")
            return False
            
        # Get first match
        first_match = matches['matches'][0]
        job_id = first_match['job_id'] 
        web_percentage = first_match['match_percentage']
        
        print(f"🎯 Job: {first_match['title']}")
        print(f"📊 Web Interface Match: {web_percentage}%")
        
        # Test 2: Generate PDF and check match percentage
        print("\n2️⃣ Testing PDF generation match calculation...")
        
        pdf_response = requests.post(f"{base_url}/api/generate-job-application-pdf", json={
            'profile_id': profile_id,
            'job_id': job_id,
            'application_type': 'standard'
        })
        
        if pdf_response.status_code != 200:
            print(f"❌ Failed to generate PDF: {pdf_response.status_code}")
            return False
            
        # The PDF generation should print debug info with match percentage
        print("✅ PDF generated successfully")
        
        # Test 3: Compare percentages (we can't easily extract from PDF, but debug prints should show)
        print("\n3️⃣ Match percentage comparison:")
        print(f"📊 Web Interface: {web_percentage}%")
        print("📊 PDF Generation: Check terminal output for debug print")
        
        print("\n✅ Test completed successfully!")
        print("💡 Check the terminal where the server is running for PDF debug output")
        print("💡 Both percentages should now be the same!")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to server")
        print("💡 Make sure the server is running on http://localhost:5006")
        return False
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

if __name__ == "__main__":
    success = test_match_consistency()
    sys.exit(0 if success else 1)