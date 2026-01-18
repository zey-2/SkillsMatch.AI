#!/usr/bin/env python3
"""Test script for dashboard statistics functionality."""

import os
import sys


def _add_web_root_to_path() -> None:
    """Ensure the web root is on sys.path for imports."""
    web_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if web_root not in sys.path:
        sys.path.insert(0, web_root)


_add_web_root_to_path()


def test_dashboard_stats() -> bool:
    """Test dashboard statistics gathering."""
    print("[TEST] Testing Dashboard Statistics...")

    try:
        from database.db_config import db_config
        from database.models import Job, UserProfile

        with db_config.session_scope() as session:
            total_jobs = session.query(Job).filter(Job.is_active == True).count()
            print(f"[INFO] Total Active Jobs: {total_jobs:,}")

            total_profiles = session.query(UserProfile).count()
            print(f"[INFO] Total User Profiles: {total_profiles:,}")

            jobs_with_categories = (
                session.query(Job)
                .filter(Job.is_active == True, Job.job_category.isnot(None))
                .all()
            )

            print(f"[INFO] Jobs with Categories: {len(jobs_with_categories):,}")

            category_counts = {}
            for job in jobs_with_categories:
                if job.job_category:
                    if isinstance(job.job_category, list):
                        for category in job.job_category:
                            if category and isinstance(category, (str, dict)):
                                if isinstance(category, str):
                                    cat_name = category
                                else:
                                    cat_name = category.get("name", str(category))
                                if cat_name:
                                    category_counts[cat_name] = (
                                        category_counts.get(cat_name, 0) + 1
                                    )
                    elif isinstance(job.job_category, str):
                        category_counts[job.job_category] = (
                            category_counts.get(job.job_category, 0) + 1
                        )

            top_categories = sorted(
                category_counts.items(), key=lambda item: item[1], reverse=True
            )[:10]

            print("\n[INFO] Top Job Categories:")
            print("=" * 50)
            for index, (category, count) in enumerate(top_categories, 1):
                print(f"{index:2d}. {category:<30} {count:>4,} jobs")

            print("\n[INFO] Dashboard Statistics Summary:")
            print("=" * 50)
            print(f"Total Jobs: {total_jobs:,}")
            print(f"Total Profiles: {total_profiles:,}")
            print(f"Unique Categories: {len(category_counts):,}")
            if top_categories:
                top_category = top_categories[0]
                print(f"Top Category: {top_category[0]} ({top_category[1]} jobs)")
            else:
                print("Top Category: None (0 jobs)")

            if top_categories:
                chart_data = {
                    "categories": [cat[0] for cat in top_categories],
                    "counts": [cat[1] for cat in top_categories],
                    "total_categories": len(category_counts),
                }

                print("\n[INFO] Chart Data Ready:")
                print(f"Categories for chart: {len(chart_data['categories'])}")
                print(f"Total job count in chart: {sum(chart_data['counts']):,}")
                return True

                print("[WARN] No category data available for chart")
            return True

    except ImportError as exc:
        print(f"[ERROR] Database modules not available: {exc}")
        print("[HINT] This is expected outside the proper environment")
        return False
    except Exception as exc:
        print(f"[ERROR] Error testing dashboard stats: {exc}")
        return False


def test_dashboard_route() -> bool:
    """Test the dashboard route with a test client."""
    print("\n[TEST] Testing Dashboard Route...")

    try:
        from app import app

        with app.test_client() as client:
            response = client.get("/dashboard")

            print(f"[INFO] Dashboard Route Status: {response.status_code}")

            if response.status_code == 200:
                print("[OK] Dashboard route accessible")
                data = response.get_data(as_text=True)
                if "Summary Overview" in data:
                    print("[OK] Summary Overview section found")
                if "Total Job Listings" in data:
                    print("[OK] Total Job Listings card found")
                if "Total Profiles" in data:
                    print("[OK] Total Profiles card found")
                if "jobCategoriesChart" in data:
                    print("[OK] Job Categories Chart container found")
                return True

            print(f"[ERROR] Dashboard route returned {response.status_code}")
            return False

    except Exception as exc:
        print(f"[ERROR] Error testing dashboard route: {exc}")
        return False


if __name__ == "__main__":
    print("[TEST] Dashboard Functionality Test")
    print("=" * 50)

    db_success = test_dashboard_stats()
    route_success = test_dashboard_route()

    print("\n" + "=" * 50)
    if db_success and route_success:
        print("[OK] All dashboard tests passed!")
        sys.exit(0)

    print("[ERROR] Some dashboard tests failed")
    sys.exit(1)
