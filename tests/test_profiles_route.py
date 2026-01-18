#!/usr/bin/env python3
"""Quick test to verify profiles route functionality."""

import os
import sys


def _add_repo_root_to_path() -> None:
    """Ensure the repository root is on sys.path for imports."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


_add_repo_root_to_path()

from web.app import app  # noqa: E402
from web.storage import profile_manager  # noqa: E402


def test_profiles_route() -> None:
    """Test the /profiles route with a test client."""
    with app.test_client() as client:
        print("[TEST] Testing /profiles route...")

        response = client.get("/profiles")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print("[OK] Route accessible")
            response_text = response.get_data(as_text=True)

            if "profile.name" in response_text or "No profiles found" in response_text:
                print("[OK] Template rendered correctly")

                if "RUBY FERDIANTO" in response_text:
                    print("[OK] Ruby's profile found in HTML")
                elif "Comprehensive Test User" in response_text:
                    print("[OK] Test profile found in HTML")
                else:
                    print("[WARNING] Profiles exist but not showing in HTML")
                    print("First 500 chars of response:")
                    print(response_text[:500])
            else:
                print("[ERROR] Template not rendering profiles correctly")
                print("First 300 chars of response:")
                print(response_text[:300])
        else:
            print(f"[ERROR] Route failed with status {response.status_code}")
            print(response.get_data(as_text=True)[:300])


if __name__ == "__main__":
    print("[DEBUG] Direct profile manager test:")
    profiles = profile_manager.list_profiles()
    print(f"Found {len(profiles)} profiles directly")
    for profile in profiles:
        print(f"  - {profile.get('name')} ({profile.get('user_id')})")

    print("\n" + "=" * 50)
    test_profiles_route()
