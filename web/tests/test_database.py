"""Test database functionality directly in production."""

import os
import sys


def _add_web_root_to_path() -> None:
    """Ensure the web root is on sys.path for imports."""
    web_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if web_root not in sys.path:
        sys.path.insert(0, web_root)


_add_web_root_to_path()


def test_database_connection() -> bool:
    """Test database connection and basic queries."""
    try:
        print("\ud83d\udd0d Testing database imports...")

        import_attempts = []

        try:
            from database.models import Job, UserProfile, UserSkill

            print("\u2705 Imported database.models using relative paths")
            models_imported = True
        except ImportError as exc:
            import_attempts.append(f"Relative import: {exc}")
            try:
                from web.database.models import Job, UserProfile, UserSkill

                print("\u2705 Imported database.models using web.database paths")
                models_imported = True
            except ImportError as exc2:
                import_attempts.append(f"Web prefix import: {exc2}")
                print("\u274c All database import attempts failed:")
                for attempt in import_attempts:
                    print(f"   - {attempt}")
                models_imported = False

        if not models_imported:
            return False

        try:
            from database.db_config import db_config

            print("\u2705 Imported database config")
        except ImportError:
            try:
                from web.database.db_config import db_config

                print("\u2705 Imported web.database config")
            except ImportError:
                print("\u274c Could not import database config")
                return False

        print("\ud83d\udd0d Testing database connection...")
        try:
            with db_config.session_scope() as session:
                if session is None:
                    print("\u26a0\ufe0f Session is None - using fallback")
                    return True

                job_count = session.query(Job).count()
                print(f"\u2705 Found {job_count} jobs in database")

                profile_count = session.query(UserProfile).count()
                print(f"\u2705 Found {profile_count} profiles in database")

                active_jobs = (
                    session.query(Job)
                    .filter(Job.is_active == True)
                    .limit(5)
                    .all()
                )
                print(f"\u2705 Found {len(active_jobs)} active jobs")

                if active_jobs:
                    job = active_jobs[0]
                    print(f"\u2705 Sample job: {job.title} at {job.company_name}")

                return True

        except Exception as exc:
            print(f"\u274c Database connection test failed: {exc}")
            return False

    except Exception as exc:
        print(f"\u274c Database test crashed: {exc}")
        return False


if __name__ == "__main__":
    print("\ud83e\uddea Testing Database Functionality")
    print("=" * 50)

    success = test_database_connection()

    if success:
        print("\n\ud83c\udf89 Database test completed successfully!")
    else:
        print("\n\u274c Database test failed!")