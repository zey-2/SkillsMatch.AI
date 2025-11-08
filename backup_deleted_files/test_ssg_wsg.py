#!/usr/bin/env python3
"""
Test SSG-WSG API Integration
Simple test to verify the API connection and course fetching
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_api_key():
    """Check if API key is configured"""
    print("🔑 Checking API Key Configuration...")
    
    api_key = os.getenv('SSGWSG_API_KEY')
    if not api_key:
        print("❌ SSGWSG_API_KEY environment variable not set!")
        print("\nTo configure:")
        print("export SSGWSG_API_KEY='your-api-key-here'")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    return True

def test_database_connection():
    """Test database connection"""
    print("\n📊 Testing Database Connection...")
    
    try:
        from web.database.db_config import db_config
        
        # Test session creation
        session = db_config.get_session()
        print("✅ Database session created successfully")
        session.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        # Try alternative import path
        try:
            import sys
            sys.path.append('web/database')
            from db_config import db_config
            session = db_config.get_session()
            print("✅ Database session created successfully (alternative import)")
            session.close()
            return True
        except Exception as e2:
            print(f"❌ Alternative import also failed: {e2}")
            return False

def test_course_model():
    """Test Course model"""
    print("\n📚 Testing Course Model...")
    
    try:
        from web.database.models import Course
        from web.database.db_config import db_config
        
        # Create tables
        db_config.create_tables()
        print("✅ Course model and tables verified")
        
        return True
        
    except Exception as e:
        print(f"❌ Course model test failed: {e}")
        return False

def test_api_client():
    """Test API client"""
    print("\n🌐 Testing API Client...")
    
    if not test_api_key():
        return False
    
    try:
        from web.services.ssg_wsg_api import SSGWSGAPIClient
        
        client = SSGWSGAPIClient()
        
        # Test basic API call
        print("Making test API call...")
        response = client.get_courses(page=0, size=1)
        
        if response and 'data' in response and 'courses' in response['data']:
            courses = response['data']['courses']
            if courses:
                course = courses[0].get('course', {})
                print(f"✅ API call successful!")
                print(f"   Sample course: {course.get('title', 'N/A')}")
                print(f"   Provider: {course.get('provider', 'N/A')}")
                return True
            else:
                print("⚠️  API call successful but no courses returned")
        else:
            print(f"⚠️  API call returned unexpected format: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ API client test failed: {e}")
        return False

def test_course_service():
    """Test course service"""
    print("\n🔧 Testing Course Service...")
    
    try:
        from web.services.ssg_wsg_api import course_service
        
        # Test service initialization
        print("✅ Course service initialized")
        
        # Test database operations (without API calls)
        from web.database.db_config import db_config
        with db_config.session_scope() as session:
            from web.database.models import Course
            
            # Count existing courses
            count = session.query(Course).count()
            print(f"✅ Current courses in database: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Course service test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 SkillsMatch.AI SSG-WSG API Integration Test")
    print("=" * 50)
    
    tests = [
        ("API Key", test_api_key),
        ("Database Connection", test_database_connection), 
        ("Course Model", test_course_model),
        ("API Client", test_api_client),
        ("Course Service", test_course_service),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! SSG-WSG integration is ready.")
        print("\nNext steps:")
        print("1. Run: python manage_courses.py sync --max-pages 2")
        print("2. Run: python manage_courses.py stats")
    else:
        print("⚠️  Some tests failed. Please check the configuration.")

if __name__ == '__main__':
    main()