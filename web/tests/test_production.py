#!/usr/bin/env python3
"""Production test script for SkillsMatch.AI."""

import sys
from datetime import datetime

import requests


def test_production_deployment() -> bool:
    """Test the production deployment on Render."""
    base_url = "https://skillsmatch-ai.onrender.com"

    print("[TEST] Testing SkillsMatch.AI Production Deployment")
    print(f"[INFO] Base URL: {base_url}")
    print(f"[INFO] Test started at: {datetime.now():%Y-%m-%d %H:%M:%S}")
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
            print(f"[INFO] Testing {test_name}...")
            response = requests.get(f"{base_url}{endpoint}", timeout=30)

            if response.status_code == 200:
                print(f"[OK] {test_name}: SUCCESS ({response.status_code})")
                results.append((test_name, "SUCCESS", response.status_code, None))
            else:
                print(f"[ERROR] {test_name}: FAILED ({response.status_code})")
                results.append((test_name, "FAILED", response.status_code, None))

        except requests.exceptions.Timeout:
            print(f"[WARN] {test_name}: TIMEOUT")
            results.append((test_name, "TIMEOUT", None, "Request timeout"))

        except requests.exceptions.ConnectionError as exc:
            print(f"[WARN] {test_name}: CONNECTION ERROR")
            results.append((test_name, "CONNECTION_ERROR", None, str(exc)))

        except Exception as exc:
            print(f"[ERROR] {test_name}: ERROR - {exc}")
            results.append((test_name, "ERROR", None, str(exc)))

    print("\n" + "=" * 60)
    print("[INFO] TEST SUMMARY")
    print("=" * 60)

    success_count = sum(1 for _, status, _, _ in results if status == "SUCCESS")
    total_tests = len(results)

    for test_name, status, code, error in results:
        status_icon = "[OK]" if status == "SUCCESS" else "[FAIL]"
        code_info = f" ({code})" if code else ""
        error_info = f" - {error}" if error else ""
        print(f"{status_icon} {test_name}{code_info}{error_info}")

    print(f"\n[INFO] Results: {success_count}/{total_tests} tests passed")

    if success_count == total_tests:
        print("[OK] All tests passed! Production is working correctly.")
        return True

    print("[WARN] Some tests failed. Check the deployment logs.")
    return False


if __name__ == "__main__":
    success = test_production_deployment()
    sys.exit(0 if success else 1)