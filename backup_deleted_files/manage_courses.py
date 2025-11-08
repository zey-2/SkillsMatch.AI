#!/usr/bin/env python3
"""
SSG-WSG Course Sync Management Script
Utility script to sync courses from SSG-WSG Developer Portal API
"""
import os
import sys
import argparse
from datetime import datetime

# Add parent directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.services.ssg_wsg_api import course_service
from web.database.models import db_config

def sync_courses(max_pages: int = 10, force: bool = False):
    """Sync courses from SSG-WSG API"""
    print(f"🚀 Starting SSG-WSG Course Sync")
    print(f"📊 Max pages to fetch: {max_pages}")
    print(f"🔄 Force sync: {force}")
    print(f"⏰ Started at: {datetime.now()}")
    print("-" * 50)
    
    try:
        # Create tables if they don't exist
        db_config.create_tables()
        print("✅ Database tables verified/created")
        
        # Sync courses
        stats = course_service.sync_courses_from_api(max_pages=max_pages)
        
        print("\n📈 Sync Results:")
        print(f"   Total Fetched: {stats['total_fetched']}")
        print(f"   New Courses: {stats['new_courses']}")
        print(f"   Updated Courses: {stats['updated_courses']}")
        print(f"   Errors: {stats['errors']}")
        
        if stats['errors'] > 0:
            print(f"⚠️  {stats['errors']} errors occurred during sync. Check logs for details.")
        else:
            print("✅ Sync completed successfully!")
            
    except Exception as e:
        print(f"❌ Error during sync: {e}")
        sys.exit(1)
    
    print(f"⏰ Completed at: {datetime.now()}")

def search_courses(query: str, limit: int = 10):
    """Search courses in database"""
    print(f"🔍 Searching courses for: '{query}'")
    print("-" * 50)
    
    try:
        courses = course_service.search_courses(query)
        
        if not courses:
            print("No courses found matching your search.")
            return
        
        print(f"Found {len(courses)} courses:")
        print()
        
        for i, course in enumerate(courses[:limit], 1):
            print(f"{i}. {course.title}")
            print(f"   Provider: {course.provider}")
            print(f"   Type: {course.course_type}")
            print(f"   Reference: {course.course_reference_number}")
            if course.course_fee:
                print(f"   Fee: ${course.course_fee:.2f}")
            print(f"   Skills: {len(course.skills_taught or [])} skills covered")
            print()
            
    except Exception as e:
        print(f"❌ Error searching courses: {e}")
        sys.exit(1)

def get_course_stats():
    """Get statistics about courses in database"""
    print("📊 Course Database Statistics")
    print("-" * 50)
    
    try:
        db = db_config.get_session()
        
        from web.database.models import Course
        
        total_courses = db.query(Course).count()
        active_courses = db.query(Course).filter(Course.is_active == True).count()
        
        # Get unique providers
        providers = db.query(Course.provider).distinct().count()
        
        # Get course types
        course_types = db.query(Course.course_type).distinct().all()
        
        print(f"Total Courses: {total_courses}")
        print(f"Active Courses: {active_courses}")
        print(f"Unique Providers: {providers}")
        print(f"Course Types: {len([ct[0] for ct in course_types if ct[0]])}")
        
        print("\nCourse Types:")
        for course_type in course_types:
            if course_type[0]:
                count = db.query(Course).filter(Course.course_type == course_type[0]).count()
                print(f"  - {course_type[0]}: {count} courses")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error getting statistics: {e}")
        sys.exit(1)

def test_api_connection():
    """Test connection to SSG-WSG API"""
    print("🔗 Testing SSG-WSG API Connection")
    print("-" * 50)
    
    try:
        api_client = course_service.api_client
        
        if not api_client.api_key:
            print("❌ API Key not configured!")
            print("Set SSGWSG_API_KEY environment variable")
            return
        
        print("✅ API Key found")
        
        # Test API call
        response = api_client.get_courses(page=0, size=1)
        
        if response.get('data', {}).get('courses'):
            print("✅ API connection successful!")
            print(f"Sample course: {response['data']['courses'][0].get('course', {}).get('title', 'N/A')}")
        else:
            print("⚠️  API connection established but no courses returned")
            
    except Exception as e:
        print(f"❌ API connection failed: {e}")

def main():
    parser = argparse.ArgumentParser(description='SSG-WSG Course Management')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Sync command
    sync_parser = subparsers.add_parser('sync', help='Sync courses from API')
    sync_parser.add_argument('--max-pages', type=int, default=10, 
                           help='Maximum pages to fetch (default: 10)')
    sync_parser.add_argument('--force', action='store_true', 
                           help='Force sync even if recent data exists')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search courses')
    search_parser.add_argument('query', help='Search query')
    search_parser.add_argument('--limit', type=int, default=10, 
                             help='Maximum results to show (default: 10)')
    
    # Stats command
    subparsers.add_parser('stats', help='Show course statistics')
    
    # Test command
    subparsers.add_parser('test', help='Test API connection')
    
    args = parser.parse_args()
    
    if args.command == 'sync':
        sync_courses(max_pages=args.max_pages, force=args.force)
    elif args.command == 'search':
        search_courses(args.query, limit=args.limit)
    elif args.command == 'stats':
        get_course_stats()
    elif args.command == 'test':
        test_api_connection()
    else:
        parser.print_help()

if __name__ == '__main__':
    main()