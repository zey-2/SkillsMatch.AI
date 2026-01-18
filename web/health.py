#!/usr/bin/env python3
"""
Health check script for SkillsMatch.AI deployment
"""

import sys
import os
from pathlib import Path


def check_imports():
    """Check if all critical imports work"""
    print("🔍 Checking critical imports...")

    try:
        # Add paths
        app_dir = Path(__file__).parent
        project_root = app_dir.parent
        sys.path.insert(0, str(project_root))
        sys.path.insert(0, str(app_dir))

        # Initialize centralized import manager
        from web.core import initialize_imports

        import_manager = initialize_imports(is_production=False)

        # Test database models using manager
        try:
            user_profile, job, user_skill = import_manager.resolve_database_models()
            print("✅ Database models resolved via import manager")
        except Exception as e:
            print(f"❌ Database models resolution failed: {e}")
            return False

        # Test services imports
        try:
            from services.simple_vector_service import get_vector_service

            print("✅ Direct services imports working")
        except ImportError:
            try:
                from web.services.simple_vector_service import get_vector_service

                print("✅ Web services imports working")
            except ImportError:
                print("⚠️ Vector services not available (optional)")

        # Test storage imports
        try:
            from web.storage import profile_manager

            print("✅ Web storage imports working")
        except ImportError:
            try:
                from storage import profile_manager

                print("✅ Direct storage imports working")
            except ImportError:
                print("⚠️ Storage imports failed (fallback will be used)")

        return True

    except Exception as e:
        print(f"❌ Import check failed: {e}")
        return False


def check_environment():
    """Check environment variables"""
    print("\n🔍 Checking environment...")

    # Check production indicators
    is_production = (
        os.environ.get("RENDER")
        or os.environ.get("RAILWAY")
        or os.environ.get("HEROKU")
    )
    if is_production:
        print(
            f"✅ Running in production: {os.environ.get('RENDER_SERVICE_NAME', 'Cloud Platform')}"
        )
    else:
        print("🔧 Running in development")

    # Check API keys
    if os.environ.get("OPENAI_API_KEY"):
        print("✅ OpenAI API key available")
    else:
        print("⚠️ OpenAI API key not found")

    if os.environ.get("GITHUB_TOKEN"):
        print("✅ GitHub token available")
    else:
        print("⚠️ GitHub token not found")

    return True


def main():
    """Run health checks"""
    print("🏥 SkillsMatch.AI Health Check")
    print("=" * 40)

    checks_passed = 0
    total_checks = 2

    if check_imports():
        checks_passed += 1

    if check_environment():
        checks_passed += 1

    print("\n" + "=" * 40)
    print(f"📊 Health Check Results: {checks_passed}/{total_checks} passed")

    if checks_passed == total_checks:
        print("🎉 All health checks passed!")
        return 0
    else:
        print("⚠️ Some health checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
