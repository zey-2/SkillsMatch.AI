"""
Core utilities for SkillsMatch.AI web application.

Provides centralized import management, configuration, and shared infrastructure.
"""

from .import_manager import (
    ImportManager,
    get_import_manager,
    initialize_imports,
)

__all__ = [
    "ImportManager",
    "get_import_manager",
    "initialize_imports",
]
