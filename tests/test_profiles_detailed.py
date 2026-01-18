#!/usr/bin/env python3
"""Test the actual profiles route with minimal template."""

import os
import sys


def _add_repo_root_to_path() -> None:
    """Ensure the repository root is on sys.path for imports."""
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)


_add_repo_root_to_path()

from web.app import app  # noqa: E402


def test_profiles_route_detailed() -> None:
    """Run a detailed inspection of the /profiles route."""
    with app.test_client() as client:
        print("[TEST] Testing actual /profiles route...")

        response = client.get("/profiles")
        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            response_text = response.get_data(as_text=True)

            checks = {
                "Template loaded": "<!DOCTYPE html>" in response_text,
                "Title correct": "Profiles - SkillsMatch.AI" in response_text,
                "Bootstrap loaded": "bootstrap" in response_text,
                "Main content": "Career Profiles" in response_text,
                "Profile name - Ruby": "RUBY FERDIANTO" in response_text,
                "Profile name - Test": "Comprehensive Test User" in response_text,
                "Profile cards": "profile-card" in response_text,
                "Empty state": "No Profiles Yet" in response_text,
                "Create button": "New Profile" in response_text,
            }

            print("[DEBUG] Content Analysis:")
            for check, result in checks.items():
                status = "[OK]" if result else "[FAIL]"
                print(f"   {status} {check}")

            if not checks["Profile name - Ruby"] and not checks["Profile name - Test"]:
                if checks["Empty state"]:
                    print(
                        "\n[WARNING] ISSUE FOUND: Template is showing empty "
                        "state despite having profiles!"
                    )
                    print("   This suggests the {% if profiles %} condition is failing")
                else:
                    print(
                        "\n[ERROR] UNKNOWN ISSUE: Neither profiles nor empty "
                        "state showing"
                    )

                if "DEBUG: About to render template with" in response_text:
                    print("   [OK] Debug output found - profiles processed")
                else:
                    print("   [ERROR] Debug output missing - route may be failing")

            print("\n[DEBUG] HTML snippet around profiles section:")
            lines = response_text.split("\n")
            for i, line in enumerate(lines):
                if "Profiles Grid" in line or "No Profiles Yet" in line:
                    start = max(0, i - 2)
                    end = min(len(lines), i + 10)
                    for j in range(start, end):
                        prefix = ">>> " if j == i else "    "
                        print(f"{prefix}{lines[j]}")
                    break
        else:
            print(f"[ERROR] Route failed with status {response.status_code}")


if __name__ == "__main__":
    test_profiles_route_detailed()
