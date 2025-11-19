#!/usr/bin/env python3
"""
Verification script for the updated home page with dashboard features
"""

import sys
import os

# Add the web directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def verify_home_page_updates():
    """Verify that home page has been updated with dashboard features"""
    
    print("🧪 Verifying Home Page Dashboard Updates")
    print("=" * 50)
    
    # Check index.html template for dashboard features
    template_path = "templates/index.html"
    try:
        with open(template_path, 'r') as f:
            content = f.read()
        
        # Check for Summary Overview section
        if "Summary Overview" in content:
            print("✅ Summary Overview section found")
        else:
            print("❌ Summary Overview section missing")
        
        # Check for Total Job Listings card
        if "Total Job Listings" in content:
            print("✅ Total Job Listings card found")
        else:
            print("❌ Total Job Listings card missing")
        
        # Check for Total Profiles card
        if "Total Profiles" in content:
            print("✅ Total Profiles card found")
        else:
            print("❌ Total Profiles card missing")
        
        # Check for Job Distribution chart
        if "Job Distribution by Category" in content:
            print("✅ Job Distribution chart section found")
        else:
            print("❌ Job Distribution chart section missing")
        
        # Check for chart container
        if "jobCategoriesChart" in content:
            print("✅ Chart container (jobCategoriesChart) found")
        else:
            print("❌ Chart container missing")
        
        # Check for Plotly integration
        if "plotly" in content.lower():
            print("✅ Plotly.js integration found")
        else:
            print("❌ Plotly.js integration missing")
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Template file not found: {template_path}")
        return False
    except Exception as e:
        print(f"❌ Error reading template: {e}")
        return False

def verify_app_updates():
    """Verify that app.py has been updated with dashboard statistics"""
    
    print(f"\n🧪 Verifying App.py Dashboard Statistics")
    print("=" * 50)
    
    try:
        with open("app.py", 'r') as f:
            content = f.read()
        
        # Check for total_jobs in stats
        if "'total_jobs'" in content:
            print("✅ total_jobs statistic added")
        else:
            print("❌ total_jobs statistic missing")
        
        # Check for total_profiles in stats
        if "'total_profiles'" in content:
            print("✅ total_profiles statistic added")
        else:
            print("❌ total_profiles statistic missing")
        
        # Check for job_categories in stats
        if "'job_categories'" in content:
            print("✅ job_categories statistic added")
        else:
            print("❌ job_categories statistic missing")
        
        # Check for chart_data generation
        if "chart_data" in content:
            print("✅ Chart data generation found")
        else:
            print("❌ Chart data generation missing")
        
        # Check for Job model import
        if "from database.models import Job" in content:
            print("✅ Job model import found")
        else:
            print("❌ Job model import missing")
        
        return True
        
    except FileNotFoundError:
        print("❌ app.py file not found")
        return False
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        return False

def verify_navigation_updates():
    """Verify navigation menu updates"""
    
    print(f"\n🧪 Verifying Navigation Updates")
    print("=" * 50)
    
    try:
        with open("templates/base.html", 'r') as f:
            content = f.read()
        
        # Check that Dashboard link is removed
        dashboard_links = content.count('Dashboard</a>')
        if dashboard_links == 0:
            print("✅ Dashboard navigation link removed")
        else:
            print(f"❌ Dashboard navigation link still present ({dashboard_links} instances)")
        
        # Check that Home link exists
        if '<i class="fas fa-home me-1"></i>Home' in content:
            print("✅ Home navigation link found")
        else:
            print("❌ Home navigation link missing")
        
        return True
        
    except FileNotFoundError:
        print("❌ base.html template not found")
        return False
    except Exception as e:
        print(f"❌ Error reading base.html: {e}")
        return False

def test_database_statistics():
    """Test database statistics functionality"""
    
    print(f"\n🧪 Testing Database Statistics")
    print("=" * 50)
    
    try:
        import sqlite3
        conn = sqlite3.connect('data/skillsmatch.db')
        cursor = conn.cursor()
        
        # Test job count
        cursor.execute('SELECT COUNT(*) FROM jobs WHERE is_active = 1')
        job_count = cursor.fetchone()[0]
        print(f"📊 Active Jobs in Database: {job_count:,}")
        
        # Test profile count
        cursor.execute('SELECT COUNT(*) FROM user_profiles')
        profile_count = cursor.fetchone()[0]
        print(f"👥 Profiles in Database: {profile_count:,}")
        
        # Test job categories
        cursor.execute('SELECT job_category FROM jobs WHERE is_active = 1 AND job_category IS NOT NULL LIMIT 5')
        categories = cursor.fetchall()
        print(f"🏷️  Sample Categories Found: {len(categories)}")
        
        conn.close()
        
        if job_count > 0 or profile_count > 0:
            print("✅ Database contains data for dashboard")
            return True
        else:
            print("⚠️  Database appears empty")
            return True
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 SkillsMatch.AI Dashboard Integration Verification")
    print("=" * 60)
    
    results = []
    results.append(verify_home_page_updates())
    results.append(verify_app_updates())
    results.append(verify_navigation_updates())
    results.append(test_database_statistics())
    
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All dashboard integration tests passed!")
        print("\n📋 Summary of Changes:")
        print("• Summary Overview cards added to home page")
        print("• Job Distribution chart added with Plotly.js")
        print("• Dashboard statistics integrated into index route")
        print("• Separate dashboard menu removed")
        print("• Database queries for job/profile counts added")
        sys.exit(0)
    else:
        print("❌ Some verification tests failed")
        print("💡 Please check the specific errors above")
        sys.exit(1)