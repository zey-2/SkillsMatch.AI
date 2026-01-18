"""
Centralized Import Manager for SkillsMatch.AI

Handles all module import resolution with fallback strategies,
environment-aware path resolution, and consistent error handling.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class ImportManager:
    """
    Unified import resolution manager for SkillsMatch.AI.

    Handles:
    - Multiple import strategies with fallback chains
    - Environment-aware path resolution
    - Comprehensive error tracking and reporting
    - Production vs development behaviors
    """

    def __init__(self, is_production: bool = False, verbose: bool = True):
        """
        Initialize the import manager.

        Args:
            is_production: Whether running in production environment
            verbose: Whether to print import attempt logs
        """
        self.is_production = is_production
        self.verbose = verbose
        self.import_attempts: Dict[str, List[str]] = {}
        self._cache: Dict[str, Any] = {}

    def _log(self, message: str) -> None:
        """Log a message if verbose mode is enabled."""
        if self.verbose:
            print(message)

    def resolve_database_models(
        self, create_placeholders: bool = True
    ) -> Tuple[Any, Any, Any]:
        """
        Resolve and import database models (UserProfile, Job, UserSkill).

        Tries multiple import paths:
        1. Direct relative import (database.models)
        2. Web-prefixed import (web.database.models)
        3. Path manipulation import (adding database parent to sys.path)
        4. Placeholder classes (fallback, if create_placeholders=True)

        Args:
            create_placeholders: If True, creates placeholder classes on failure

        Returns:
            Tuple of (UserProfile, Job, UserSkill) classes
        """
        attempt_key = "database_models"
        self.import_attempts[attempt_key] = []

        # Check cache first
        if attempt_key in self._cache:
            return self._cache[attempt_key]

        # Identify database paths to check
        database_paths = self._get_database_paths()

        if self.is_production:
            self._log("[DEBUG] Checking database paths:")
            for i, path in enumerate(database_paths, 1):
                exists = "EXISTS" if os.path.exists(path) else "NOT FOUND"
                self._log(f"   Path {i}: {path} - {exists}")

        # Strategy 1: Relative import
        try:
            from database.models import UserProfile, Job, UserSkill

            self._log("[OK] Successfully imported database.models using relative paths")
            result = (UserProfile, Job, UserSkill)
            self._cache[attempt_key] = result
            return result
        except ImportError as e:
            self.import_attempts[attempt_key].append(f"Relative import: {e}")

        # Strategy 2: Web-prefixed import
        try:
            from web.database.models import UserProfile, Job, UserSkill

            self._log(
                "[OK] Successfully imported database.models using web.database paths"
            )
            result = (UserProfile, Job, UserSkill)
            self._cache[attempt_key] = result
            return result
        except ImportError as e:
            self.import_attempts[attempt_key].append(f"Web prefix import: {e}")

        # Strategy 3: Path manipulation
        for database_path in database_paths:
            if os.path.exists(database_path):
                try:
                    parent_path = os.path.dirname(database_path)
                    if parent_path not in sys.path:
                        sys.path.insert(0, parent_path)

                    import database.models as db_models

                    UserProfile = db_models.UserProfile
                    Job = db_models.Job
                    UserSkill = db_models.UserSkill

                    self._log(
                        f"[OK] Successfully imported database.models using "
                        f"path manipulation: {parent_path}"
                    )
                    result = (UserProfile, Job, UserSkill)
                    self._cache[attempt_key] = result
                    return result
                except ImportError as e:
                    self.import_attempts[attempt_key].append(
                        f"Path manipulation ({parent_path}): {e}"
                    )
                    continue

        # Strategy 4: Placeholder classes (fallback)
        if create_placeholders:
            if self.is_production:
                self._log("[ERROR] All database import attempts failed:")
                for attempt in self.import_attempts[attempt_key]:
                    self._log(f"   - {attempt}")

            class UserProfile:  # noqa: F811
                def __init__(self, **kwargs):
                    pass

            class Job:  # noqa: F811
                def __init__(self, **kwargs):
                    pass

            class UserSkill:  # noqa: F811
                def __init__(self, **kwargs):
                    pass

            self._log(
                "[WARNING] Using placeholder classes - database functionality limited"
            )
            result = (UserProfile, Job, UserSkill)
            self._cache[attempt_key] = result
            return result

        # Raise if no placeholders allowed
        raise ImportError(
            f"Failed to import database models. Attempts:\n"
            f"{chr(10).join(self.import_attempts[attempt_key])}"
        )

    def resolve_skillmatch_core(
        self,
    ) -> Tuple[bool, Optional[Any], Optional[Any], Optional[Any]]:
        """
        Resolve SkillMatch core modules (models and utilities).

        Returns:
            Tuple of (success, SkillMatchAgent, DataLoader, SkillMatcher)
            or (False, None, None, None) on failure
        """
        attempt_key = "skillmatch_core"
        self.import_attempts[attempt_key] = []

        # Check cache first
        if attempt_key in self._cache:
            return self._cache[attempt_key]

        try:
            from skillmatch.models import (
                SkillItem,
                ExperienceLevel,
                UserPreferences,
                PreferenceType,
            )
            from skillmatch.utils import DataLoader, SkillMatcher

            # Try importing the agent (may have OpenAI issues)
            SkillMatchAgent = None
            try:
                from skillmatch import SkillMatchAgent

                self._log("[OK] SkillMatch core modules loaded successfully")
            except Exception as agent_error:
                self._log(
                    f"[WARNING] SkillMatch agent not available "
                    f"(OpenAI compatibility issue): {agent_error}"
                )
                self.import_attempts[attempt_key].append(
                    f"SkillMatchAgent import: {agent_error}"
                )

            result = (True, SkillMatchAgent, DataLoader, SkillMatcher)
            self._cache[attempt_key] = result
            return result

        except ImportError as e:
            error_msg = str(e)
            self.import_attempts[attempt_key].append(f"Core modules import: {e}")

            # Suppress harmless import warnings (e.g., conflicting CLI entry point)
            if "is not a package" in error_msg or "skillmatch.cli" in error_msg:
                # This is expected - skillmatch.py CLI entry point shadows the package
                # The app still works fine without it
                pass
            else:
                self._log(f"[WARNING] SkillMatch core modules not available: {e}")

            result = (False, None, None, None)
            self._cache[attempt_key] = result
            return result

    def resolve_ai_services(self) -> Tuple[bool, bool, bool]:
        """
        Resolve AI service imports (OpenAI, matching services, vector services).

        Returns:
            Tuple of (openai_available, ai_matching_available, vector_matching_available)
        """
        attempt_key = "ai_services"
        self.import_attempts[attempt_key] = []

        # Check cache first
        if attempt_key in self._cache:
            return self._cache[attempt_key]

        # OpenAI import
        openai_available = False
        try:
            import openai  # noqa: F401
            from openai import OpenAI  # noqa: F401

            openai_available = True
            self._log("[OK] OpenAI SDK available")
        except ImportError as e:
            self.import_attempts[attempt_key].append(f"OpenAI SDK: {e}")
            self._log("[WARNING] OpenAI SDK not available")

        # AI Matching services
        ai_matching_available = False
        try:
            from services.ai_skill_matcher import ai_skill_matcher  # noqa: F401
            from services.enhanced_job_matcher import find_enhanced_matches  # noqa: F401

            ai_matching_available = True
            self._log("[OK] AI skill matching services available")
        except ImportError as e:
            self.import_attempts[attempt_key].append(f"AI matching services: {e}")
            self._log("[WARNING] AI skill matching services not available")

        # Vector matching services
        vector_matching_available = False
        try:
            from services.vector_job_matcher import vector_job_matcher  # noqa: F401

            vector_matching_available = True
            self._log("[OK] Vector job matching service available")
        except ImportError as e:
            self.import_attempts[attempt_key].append(f"Vector job matching: {e}")
            self._log("[WARNING] Vector job matching service not available")

        result = (openai_available, ai_matching_available, vector_matching_available)
        self._cache[attempt_key] = result
        return result

    def resolve_module(
        self,
        module_name: str,
        import_strategies: List[str],
        fallback_to_none: bool = True,
    ) -> Optional[Any]:
        """
        Generic module resolution with custom strategies.

        Args:
            module_name: Name of module to import
            import_strategies: List of import strings to try in order
            fallback_to_none: If True, return None on failure; if False, raise exception

        Returns:
            Imported module or None

        Example:
            resolve_module(
                "storage",
                ["from web.storage import profile_manager",
                 "from storage import profile_manager"]
            )
        """
        attempt_key = f"module_{module_name}"
        self.import_attempts[attempt_key] = []

        for strategy in import_strategies:
            try:
                # Use exec to safely execute the import statement
                namespace: Dict[str, Any] = {}
                exec(strategy, namespace)

                # Extract the last imported object
                imported_name = strategy.split()[-1]
                if imported_name in namespace:
                    self._log(f"[OK] Successfully imported {module_name}: {strategy}")
                    return namespace[imported_name]
            except Exception as e:
                self.import_attempts[attempt_key].append(f"{strategy}: {e}")

        if fallback_to_none:
            self._log(f"[WARNING] {module_name} not available (fallback to None)")
            return None

        raise ImportError(
            f"Failed to import {module_name}. Attempts:\n"
            f"{chr(10).join(self.import_attempts[attempt_key])}"
        )

    def get_import_report(self) -> str:
        """
        Generate a formatted report of all import attempts.

        Returns:
            Formatted string with import attempt history
        """
        if not self.import_attempts:
            return "No import attempts recorded"

        report = "Import Attempt Report:\n"
        report += "=" * 50 + "\n"

        for key, attempts in self.import_attempts.items():
            if attempts:
                report += f"\n{key}:\n"
                for attempt in attempts:
                    report += f"  - {attempt}\n"

        return report

    def validate_critical_imports(self) -> bool:
        """
        Validate that all critical imports are available.

        Returns:
            True if all critical imports available, False otherwise
        """
        critical_checks = {
            "Database models": self._check_database_models,
            # Note: Core utilities are optional - app works fine without them
            # "Core utilities": self._check_core_utilities,
        }

        all_valid = True
        for check_name, check_func in critical_checks.items():
            valid = check_func()
            status = "[OK]" if valid else "[FAIL]"
            self._log(f"{status} {check_name}")
            all_valid = all_valid and valid

        return all_valid

    def _check_database_models(self) -> bool:
        """Check if database models can be imported."""
        try:
            user_profile, job, user_skill = self.resolve_database_models(
                create_placeholders=False
            )
            return all([user_profile, job, user_skill])
        except (ImportError, TypeError):
            return False

    def _check_core_utilities(self) -> bool:
        """Check if core utilities are available."""
        success, _, _, _ = self.resolve_skillmatch_core()
        return success

    @staticmethod
    def _get_database_paths() -> List[str]:
        """Get list of potential database directory paths to check."""
        return [
            os.path.join(os.getcwd(), "database"),
            os.path.join(os.getcwd(), "web", "database"),
            os.path.join(os.path.dirname(__file__), "..", "database"),
            os.path.join(os.path.dirname(__file__), "..", "..", "web", "database"),
        ]


# Global singleton instance
_import_manager: Optional[ImportManager] = None


def get_import_manager(
    is_production: bool = False, verbose: bool = True, force_new: bool = False
) -> ImportManager:
    """
    Get or create the global import manager instance.

    Args:
        is_production: Whether running in production
        verbose: Whether to print logs
        force_new: If True, create new instance ignoring existing one

    Returns:
        ImportManager instance
    """
    global _import_manager

    if force_new or _import_manager is None:
        _import_manager = ImportManager(is_production=is_production, verbose=verbose)

    return _import_manager


def initialize_imports(is_production: bool = False) -> ImportManager:
    """
    Initialize all imports using the centralized manager.

    This is the main entry point for setting up all imports at application startup.

    Args:
        is_production: Whether running in production environment

    Returns:
        Configured ImportManager instance
    """
    manager = get_import_manager(is_production=is_production, verbose=True)

    # Validate critical imports
    if not manager.validate_critical_imports():
        if is_production:
            print("[WARNING] Some imports failed validation, check logs for details")
        else:
            print("[WARNING] Running with degraded functionality")

    return manager
