#!/usr/bin/env python3
"""Production test script for SkillsMatch.AI."""

import sys
from datetime import datetime

import requests


def test_production_deployment() -> bool:
    """Test the production deployment on Render."""
    base_url = "https://skillsmatch-ai.onrender.com"

    print("\ud83d\ude80 Testing SkillsMatch.AI Production Deployment")
    print(f"\ud83c\udf10 Base URL: {base_url}")
    print(f"\u23f0 Test started at: {datetime.now():%Y-%m-%d %H:%M:%S}")
    print("-" * 60)

    tests = [
        ("Home Page", "/"),
        ("Jobs Listing", "/jobs"),
        ("Profiles", "/profiles"),
        ("Dashboard", "/dashboard"),
        ("Health Check", "/health"),
    ]

    results = []

    for test_name, endpoint in tests:
        try:
            print(f"\ud83d\udd0d Testing {test_name}...")
            response = requests.get(f"{base_url}{endpoint}", timeout=30)

            if response.status_code == 200:
                print(f"\u2705 {test_name}: SUCCESS ({response.status_code})")
                results.append((test_name, "SUCCESS", response.status_code, None))
            else:
                print(f"\u274c {test_name}: FAILED ({response.status_code})")
                results.append((test_name, "FAILED", response.status_code, None))

        except requests.exceptions.Timeout:
            print(f"\u23f0 {test_name}: TIMEOUT")
            results.append((test_name, "TIMEOUT", None, "Request timeout"))

        except requests.exceptions.ConnectionError as exc:
            print(f"\ud83d\udd0c {test_name}: CONNECTION ERROR")
            results.append((test_name, "CONNECTION_ERROR", None, str(exc)))

        except Exception as exc:
            print(f"\ud83d\udca5 {test_name}: ERROR - {exc}")
            results.append((test_name, "ERROR", None, str(exc)))

    print("\n" + "=" * 60)
    print("\ud83d\udcca TEST SUMMARY")
    print("=" * 60)

    success_count = sum(1 for _, status, _, _ in results if status == "SUCCESS")
    total_tests = len(results)

    for test_name, status, code, error in results:
        status_icon = "\u2705" if status == "SUCCESS" else "\u274c"
        code_info = f" ({code})" if code else ""
        error_info = f" - {error}" if error else ""
        print(f"{status_icon} {test_name}{code_info}{error_info}")

    print(f"\n\ud83c\udfaf Results: {success_count}/{total_tests} tests passed")

    if success_count == total_tests:
        print("\ud83c\udf89 All tests passed! Production is working correctly.")
        return True

    print("\u26a0\ufe0f Some tests failed. Check the deployment logs.")
    return False


if __name__ == "__main__":
    success = test_production_deployment()
    sys.exit(0 if success else 1)