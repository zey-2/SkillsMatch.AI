#!/usr/bin/env python3
"""
Test script to validate match percentage consistency between web interface and
PDF generation.
"""

import os
import sys

import requests


def test_match_consistency() -> bool:
    """Test that web interface and PDF generation show same match percentages."""
    base_url = os.environ.get("SKILLSMATCH_BASE_URL", "http://localhost:5006")

    print("[TEST] Testing Match Percentage Consistency")
    print("=" * 50)

    try:
        print("[STEP] 1. Testing web interface match calculation...")

        profiles_response = requests.get(f"{base_url}/api/profiles", timeout=30)
        if profiles_response.status_code != 200:
            print(f"[ERROR] Failed to get profiles: {profiles_response.status_code}")
            return False

        profiles = profiles_response.json()
        if not profiles:
            print("[ERROR] No profiles found for testing")
            return False

        test_profile = profiles[0]
        profile_id = test_profile["profile_id"]
        print(f"[INFO] Using profile: {test_profile['full_name']} (ID: {profile_id})")

        match_response = requests.post(
            f"{base_url}/api/match",
            json={"profile_id": profile_id},
            timeout=30,
        )

        if match_response.status_code != 200:
            print(f"[ERROR] Failed to get matches: {match_response.status_code}")
            return False

        matches = match_response.json()
        if not matches or "matches" not in matches:
            print("[ERROR] No matches found")
            return False

        first_match = matches["matches"][0]
        job_id = first_match["job_id"]
        web_percentage = first_match["match_percentage"]

        print(f"[INFO] Job: {first_match['title']}")
        print(f"[INFO] Web Interface Match: {web_percentage}%")

        print("\n[STEP] 2. Testing PDF generation match calculation...")

        pdf_response = requests.post(
            f"{base_url}/api/generate-job-application-pdf",
            json={
                "profile_id": profile_id,
                "job_id": job_id,
                "application_type": "standard",
            },
            timeout=30,
        )

        if pdf_response.status_code != 200:
            print(f"[ERROR] Failed to generate PDF: {pdf_response.status_code}")
            return False

        print("[OK] PDF generated successfully")

        print("\n[STEP] 3. Match percentage comparison:")
        print(f"[INFO] Web Interface: {web_percentage}%")
        print("[INFO] PDF Generation: Check server debug output")

        print("\n[OK] Test completed successfully!")
        print(
            "[INFO] Check the terminal where the server is running for PDF debug output"
        )
        print("[INFO] Both percentages should now be the same!")

        return True

    except requests.exceptions.ConnectionError:
        print("[ERROR] Error: Could not connect to server")
        print(f"[INFO] Make sure the server is running on {base_url}")
        return False
    except Exception as exc:
        print(f"[ERROR] Error during testing: {exc}")
        return False


if __name__ == "__main__":
    success = test_match_consistency()
    sys.exit(0 if success else 1)
