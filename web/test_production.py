#!/usr/bin/env python3
"""
Production Test Script for SkillsMatch.AI

Tests database imports and basic functionality in production environment.
"""

import os
import sys
import requests
import json
from datetime import datetime

def test_production_deployment():
    """Test the production deployment on Render"""
    base_url = "https://skillsmatch-ai.onrender.com"
    
    print("🚀 Testing SkillsMatch.AI Production Deployment")
    print(f"🌐 Base URL: {base_url}")
    print(f"⏰ Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    tests = [
        ("Home Page", "/"),
        ("Jobs Listing", "/jobs"),
        ("Profiles", "/profiles"), 
        ("Dashboard", "/dashboard"),
        ("Health Check", "/health")
    ]
    
    results = []
    
    for test_name, endpoint in tests:
        try:
            print(f"🔍 Testing {test_name}...")
            response = requests.get(f"{base_url}{endpoint}", timeout=30)
            
            if response.status_code == 200:
                print(f"✅ {test_name}: SUCCESS ({response.status_code})")
                results.append((test_name, "SUCCESS", response.status_code, None))
            else:
                print(f"❌ {test_name}: FAILED ({response.status_code})")
                results.append((test_name, "FAILED", response.status_code, None))
                
        except requests.exceptions.Timeout:
            print(f"⏰ {test_name}: TIMEOUT")
            results.append((test_name, "TIMEOUT", None, "Request timeout"))
            
        except requests.exceptions.ConnectionError as e:
            print(f"🔌 {test_name}: CONNECTION ERROR")
            results.append((test_name, "CONNECTION_ERROR", None, str(e)))
            
        except Exception as e:
            print(f"💥 {test_name}: ERROR - {str(e)}")
            results.append((test_name, "ERROR", None, str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    success_count = sum(1 for _, status, _, _ in results if status == "SUCCESS")
    total_tests = len(results)
    
    for test_name, status, code, error in results:
        status_icon = "✅" if status == "SUCCESS" else "❌"
        code_info = f" ({code})" if code else ""
        error_info = f" - {error}" if error else ""
        print(f"{status_icon} {test_name}{code_info}{error_info}")
    
    print(f"\n🎯 Results: {success_count}/{total_tests} tests passed")
    
    if success_count == total_tests:
        print("🎉 All tests passed! Production deployment is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Check the deployment logs.")
        return False

if __name__ == "__main__":
    success = test_production_deployment()
    sys.exit(0 if success else 1)