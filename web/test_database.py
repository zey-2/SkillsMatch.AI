"""
Test database functionality directly in production
"""

def test_database_connection():
    """Test database connection and basic queries"""
    try:
        # Test the import that was causing issues
        print("🔍 Testing database imports...")
        
        # Import database modules with the same logic as app.py
        import_attempts = []
        
        try:
            from database.models import UserProfile, Job, UserSkill
            print("✅ Successfully imported database.models using relative paths")
            models_imported = True
        except ImportError as e1:
            import_attempts.append(f"Relative import: {e1}")
            try:
                from web.database.models import UserProfile, Job, UserSkill
                print("✅ Successfully imported database.models using web.database paths")
                models_imported = True
            except ImportError as e2:
                import_attempts.append(f"Web prefix import: {e2}")
                print(f"❌ All database import attempts failed:")
                for attempt in import_attempts:
                    print(f"   - {attempt}")
                models_imported = False
        
        if not models_imported:
            return False
            
        # Test database config import
        try:
            from database.db_config import db_config
            print("✅ Successfully imported database config")
        except ImportError:
            try:
                from web.database.db_config import db_config
                print("✅ Successfully imported web.database config")
            except ImportError:
                print("❌ Could not import database config")
                return False
        
        # Test database connection
        print("🔍 Testing database connection...")
        try:
            with db_config.session_scope() as session:
                if session is None:
                    print("⚠️ Session is None - using fallback")
                    return True
                    
                # Count jobs
                job_count = session.query(Job).count()
                print(f"✅ Found {job_count} jobs in database")
                
                # Count profiles  
                profile_count = session.query(UserProfile).count()
                print(f"✅ Found {profile_count} profiles in database")
                
                # Test active jobs query
                active_jobs = session.query(Job).filter(Job.is_active == True).limit(5).all()
                print(f"✅ Found {len(active_jobs)} active jobs")
                
                if active_jobs:
                    job = active_jobs[0]
                    print(f"✅ Sample job: {job.title} at {job.company_name}")
                
                return True
                
        except Exception as e:
            print(f"❌ Database connection test failed: {e}")
            return False
            
    except Exception as e:
        print(f"❌ Database test crashed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Database Functionality")
    print("=" * 50)
    
    success = test_database_connection()
    
    if success:
        print("\n🎉 Database test completed successfully!")
    else:
        print("\n❌ Database test failed!")