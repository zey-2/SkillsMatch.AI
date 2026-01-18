"""Database index initialization and management script.

This script creates database indexes for performance optimization.
Run this after updating models to ensure indexes are created.
"""

import logging
from pathlib import Path
from sqlalchemy import create_engine, inspect, Index, MetaData
from sqlalchemy.orm import sessionmaker

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_db_path() -> Path:
    """Get the database path."""
    db_path = Path(__file__).parent.parent.parent / "web" / "data" / "skillsmatch.db"
    if not db_path.exists():
        db_path = Path(__file__).parent / "skillsmatch.db"
    return db_path


def create_indexes(db_url: str = None) -> None:
    """Create all indexes defined in models.

    Args:
        db_url: Database URL (defaults to SQLite in web/data/)
    """
    if db_url is None:
        db_path = get_db_path()
        db_url = f"sqlite:///{db_path}"

    logger.info(f"Creating indexes in: {db_url}")

    # Create engine
    engine = create_engine(db_url, echo=False)

    # Create all indexes
    try:
        # Get all models metadata
        from web.database.models import (
            Base,
            UserProfile,
            Skill,
            Job,
            UserSkill,
            WorkExperience,
            Education,
            UserPreferences,
            CareerGoal,
            Course,
        )

        # Create tables (if they don't exist)
        Base.metadata.create_all(engine)
        logger.info("✅ All tables created or already exist")

        # Get inspector
        inspector = inspect(engine)

        # Check for and report existing indexes
        logger.info("\nExisting indexes:")
        for table_name in inspector.get_table_names():
            indexes = inspector.get_indexes(table_name)
            if indexes:
                logger.info(f"  {table_name}:")
                for idx in indexes:
                    logger.info(f"    - {idx['name']}: {idx['column_names']}")
            else:
                logger.info(f"  {table_name}: (no indexes)")

        # Report created indexes from models
        logger.info("\nIndexes from models:")
        _report_model_indexes()

        logger.info("\n✅ Index creation completed successfully")

    except Exception as e:
        logger.error(f"❌ Error creating indexes: {e}")
        raise


def _report_model_indexes() -> None:
    """Report all indexes defined in models."""
    from web.database.models import (
        UserProfile,
        Skill,
        Job,
        UserSkill,
        WorkExperience,
        Education,
        UserPreferences,
        CareerGoal,
        Course,
    )

    models = [
        UserProfile,
        Skill,
        Job,
        UserSkill,
        WorkExperience,
        Education,
        UserPreferences,
        CareerGoal,
        Course,
    ]

    for model in models:
        if hasattr(model, "__table_args__") and model.__table_args__:
            table_args = model.__table_args__
            indexes = [arg for arg in table_args if isinstance(arg, Index)]
            if indexes:
                logger.info(f"  {model.__tablename__}:")
                for idx in indexes:
                    logger.info(f"    - {idx.name}: {idx.expressions}")


def verify_indexes(db_url: str = None) -> bool:
    """Verify all expected indexes exist.

    Args:
        db_url: Database URL

    Returns:
        True if all indexes exist, False otherwise
    """
    if db_url is None:
        db_path = get_db_path()
        db_url = f"sqlite:///{db_path}"

    engine = create_engine(db_url, echo=False)
    inspector = inspect(engine)

    expected_indexes = {
        "user_profiles": [
            "idx_user_profiles_created_at",
            "idx_user_profiles_experience_level",
            "idx_user_profiles_location",
            "idx_user_profiles_is_active",
            "idx_user_profiles_email",
        ],
        "skills": [
            "idx_skills_name",
            "idx_skills_category",
        ],
        "jobs": [
            "idx_jobs_created_at",
            "idx_jobs_position_level",
            "idx_jobs_is_active",
            "idx_jobs_company_name",
            "idx_jobs_keywords",
        ],
    }

    all_exist = True
    for table_name, expected_idx_names in expected_indexes.items():
        if table_name not in inspector.get_table_names():
            logger.warning(f"Table {table_name} does not exist")
            continue

        indexes = inspector.get_indexes(table_name)
        existing_idx_names = {idx["name"] for idx in indexes}

        for expected_name in expected_idx_names:
            if expected_name not in existing_idx_names:
                logger.warning(f"Index {expected_name} missing on {table_name}")
                all_exist = False
            else:
                logger.info(f"✅ Index {expected_name} exists on {table_name}")

    return all_exist


def drop_indexes(db_url: str = None) -> None:
    """Drop all custom indexes (for cleanup/rebuild).

    Args:
        db_url: Database URL
    """
    if db_url is None:
        db_path = get_db_path()
        db_url = f"sqlite:///{db_path}"

    logger.info(f"Dropping indexes from: {db_url}")

    engine = create_engine(db_url, echo=False)
    inspector = inspect(engine)

    # Get all indexes to drop
    indexes_to_drop = [
        "idx_user_profiles_created_at",
        "idx_user_profiles_experience_level",
        "idx_user_profiles_location",
        "idx_user_profiles_is_active",
        "idx_user_profiles_email",
        "idx_skills_name",
        "idx_skills_category",
        "idx_jobs_created_at",
        "idx_jobs_position_level",
        "idx_jobs_is_active",
        "idx_jobs_company_name",
        "idx_jobs_keywords",
    ]

    with engine.connect() as conn:
        for idx_name in indexes_to_drop:
            try:
                conn.execute(f"DROP INDEX IF EXISTS {idx_name}")
                logger.info(f"Dropped index: {idx_name}")
            except Exception as e:
                logger.debug(f"Could not drop {idx_name}: {e}")

        conn.commit()

    logger.info("✅ Index cleanup completed")


def analyze_queries(db_url: str = None) -> None:
    """Analyze query performance (SQLite ANALYZE).

    Args:
        db_url: Database URL
    """
    if db_url is None:
        db_path = get_db_path()
        db_url = f"sqlite:///{db_path}"

    logger.info(f"Analyzing queries in: {db_url}")

    engine = create_engine(db_url, echo=False)

    with engine.connect() as conn:
        try:
            # Run SQLite ANALYZE to gather statistics
            conn.execute("ANALYZE")
            conn.commit()
            logger.info("✅ Query analysis completed")
        except Exception as e:
            logger.error(f"❌ Error during analysis: {e}")


if __name__ == "__main__":
    import sys

    # Parse command line arguments
    action = sys.argv[1] if len(sys.argv) > 1 else "create"

    if action == "create":
        create_indexes()
        verify_indexes()
    elif action == "verify":
        if verify_indexes():
            logger.info("✅ All indexes verified")
            sys.exit(0)
        else:
            logger.error("❌ Some indexes missing")
            sys.exit(1)
    elif action == "drop":
        drop_indexes()
    elif action == "analyze":
        analyze_queries()
    elif action == "rebuild":
        drop_indexes()
        create_indexes()
        analyze_queries()
        verify_indexes()
    else:
        print(f"Unknown action: {action}")
        print("Available actions: create, verify, drop, analyze, rebuild")
        sys.exit(1)
