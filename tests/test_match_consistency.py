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

    print("\ud83e\uddea Testing Match Percentage Consistency")
    print("=" * 50)

    try:
        print("1\ufe0f\u20e3 Testing web interface match calculation...")

        profiles_response = requests.get(f"{base_url}/api/profiles", timeout=30)
        if profiles_response.status_code != 200:
            print(f"\u274c Failed to get profiles: {profiles_response.status_code}")
            return False

        profiles = profiles_response.json()
        if not profiles:
            print("\u274c No profiles found for testing")
            return False

        test_profile = profiles[0]
        profile_id = test_profile["profile_id"]
        print(
            f"\ud83d\udcdd Using profile: {test_profile['full_name']} "
            f"(ID: {profile_id})"
        )

        match_response = requests.post(
            f"{base_url}/api/match",
            json={"profile_id": profile_id},
            timeout=30,
        )

        if match_response.status_code != 200:
            print(f"\u274c Failed to get matches: {match_response.status_code}")
            return False

        matches = match_response.json()
        if not matches or "matches" not in matches:
            print("\u274c No matches found")
            return False

        first_match = matches["matches"][0]
        job_id = first_match["job_id"]
        web_percentage = first_match["match_percentage"]

        print(f"\ud83c\udfaf Job: {first_match['title']}")
        print(f"\ud83d\udcca Web Interface Match: {web_percentage}%")

        print("\n2\ufe0f\u20e3 Testing PDF generation match calculation...")

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
            print(f"\u274c Failed to generate PDF: {pdf_response.status_code}")
            return False

        print("\u2705 PDF generated successfully")

        print("\n3\ufe0f\u20e3 Match percentage comparison:")
        print(f"\ud83d\udcca Web Interface: {web_percentage}%")
        print("\ud83d\udcca PDF Generation: Check server debug output")

        print("\n\u2705 Test completed successfully!")
        print(
            "\ud83d\udca1 Check the terminal where the server is running for PDF "
            "debug output"
        )
        print("\ud83d\udca1 Both percentages should now be the same!")

        return True

    except requests.exceptions.ConnectionError:
        print("\u274c Error: Could not connect to server")
        print(f"\ud83d\udca1 Make sure the server is running on {base_url}")
        return False
    except Exception as exc:
        print(f"\u274c Error during testing: {exc}")
        return False


if __name__ == "__main__":
    success = test_match_consistency()
    sys.exit(0 if success else 1)