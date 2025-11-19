#!/usr/bin/env python3
"""
Test script for dashboard statistics functionality
"""

import sys
import os
import json

# Add the web directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_dashboard_stats():
    """Test dashboard statistics gathering"""
    
    print("🧪 Testing Dashboard Statistics...")
    
    try:
        # Test database connection and statistics
        from database.db_config import db_config
        from database.models import Job, UserProfile
        
        with db_config.session_scope() as session:
            # Count total jobs
            total_jobs = session.query(Job).filter(Job.is_active == True).count()
            print(f"📊 Total Active Jobs: {total_jobs:,}")
            
            # Count total profiles
            total_profiles = session.query(UserProfile).count()
            print(f"👥 Total User Profiles: {total_profiles:,}")
            
            # Get job categories distribution
            jobs_with_categories = session.query(Job).filter(
                Job.is_active == True,
                Job.job_category.isnot(None)
            ).all()
            
            print(f"🏷️  Jobs with Categories: {len(jobs_with_categories):,}")
            
            category_counts = {}
            for job in jobs_with_categories:
                if job.job_category:
                    if isinstance(job.job_category, list):
                        for category in job.job_category:
                            if category and isinstance(category, (str, dict)):
                                cat_name = str(category) if isinstance(category, str) else category.get('name', str(category))
                                if cat_name:
                                    category_counts[cat_name] = category_counts.get(cat_name, 0) + 1
                    elif isinstance(job.job_category, str):
                        if job.job_category:
                            category_counts[job.job_category] = category_counts.get(job.job_category, 0) + 1
            
            # Sort categories by count and show top 10
            top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            
            print(f"\n📈 Top Job Categories:")
            print("=" * 50)
            for i, (category, count) in enumerate(top_categories, 1):
                print(f"{i:2d}. {category:<30} {count:>4,} jobs")
            
            print(f"\n📊 Dashboard Statistics Summary:")
            print("=" * 50)
            print(f"Total Jobs: {total_jobs:,}")
            print(f"Total Profiles: {total_profiles:,}")
            print(f"Unique Categories: {len(category_counts):,}")
            print(f"Top Category: {top_categories[0][0] if top_categories else 'None'} ({top_categories[0][1] if top_categories else 0} jobs)")
            
            # Test chart data generation
            if top_categories:
                chart_data = {
                    'categories': [cat[0] for cat in top_categories],
                    'counts': [cat[1] for cat in top_categories],
                    'total_categories': len(category_counts)
                }
                
                print(f"\n📊 Chart Data Ready:")
                print(f"Categories for chart: {len(chart_data['categories'])}")
                print(f"Total job count in chart: {sum(chart_data['counts']):,}")
                
                return True
            else:
                print("⚠️ No category data available for chart")
                return True
                
    except ImportError as e:
        print(f"❌ Database modules not available: {e}")
        print("💡 This is expected if running outside proper environment")
        return False
    except Exception as e:
        print(f"❌ Error testing dashboard stats: {e}")
        return False

def test_dashboard_route():
    """Test the dashboard route with mock request"""
    print("\n🧪 Testing Dashboard Route...")
    
    try:
        # Import Flask app
        from app import app
        
        with app.test_client() as client:
            # Test dashboard route
            response = client.get('/dashboard')
            
            print(f"📍 Dashboard Route Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Dashboard route accessible")
                # Check if response contains expected elements
                data = response.get_data(as_text=True)
                if 'Summary Overview' in data:
                    print("✅ Summary Overview section found")
                if 'Total Job Listings' in data:
                    print("✅ Total Job Listings card found")
                if 'Total Profiles' in data:
                    print("✅ Total Profiles card found")
                if 'jobCategoriesChart' in data:
                    print("✅ Job Categories Chart container found")
                return True
            else:
                print(f"❌ Dashboard route returned {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Error testing dashboard route: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Dashboard Functionality Test")
    print("=" * 50)
    
    # Test database statistics
    db_success = test_dashboard_stats()
    
    # Test dashboard route
    route_success = test_dashboard_route()
    
    print("\n" + "=" * 50)
    if db_success and route_success:
        print("✅ All dashboard tests passed!")
        sys.exit(0)
    else:
        print("❌ Some dashboard tests failed")
        sys.exit(1)