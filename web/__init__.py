"""
SkillsMatch.AI Web Application Package

Phase 2: Monolithic App Refactoring
Refactors monolithic Flask app into modular Blueprint-based architecture with service layer.

Module Structure:
- blueprints/: Route handlers organized by domain
- services/: Business logic layer
- database/: Data access layer
- models/: Data models
- core/: Core utilities (imports, configuration)

Usage:
    from web.app import create_app
    app = create_app('development')
"""

__version__ = "2.0.0"
__author__ = "SkillsMatch.AI Team"

# Package level imports for convenience
from web.config import (
    get_config,
    Config,
    DevelopmentConfig,
    ProductionConfig,
    TestingConfig,
)
from web.services import (
    ProfileService,
    MatchingService,
    ValidationError,
    NotFoundError,
)

__all__ = [
    "get_config",
    "Config",
    "DevelopmentConfig",
    "ProductionConfig",
    "TestingConfig",
    "ProfileService",
    "MatchingService",
    "ValidationError",
    "NotFoundError",
]
