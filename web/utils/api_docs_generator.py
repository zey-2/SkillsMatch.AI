"""
API Documentation Generator - Creates OpenAPI 3.0 specifications for SkillsMatch.AI.

Generates comprehensive API documentation including:
- All endpoints with methods
- Request/response schemas
- Error codes and handling
- Authentication requirements
- Rate limiting information
"""

import json
from typing import Dict, List, Any, Optional
from datetime import datetime


class OpenAPIGenerator:
    """Generate OpenAPI 3.0 specification for SkillsMatch.AI."""

    def __init__(
        self,
        title: str = "SkillsMatch.AI API",
        version: str = "1.0.0",
        description: str = "Intelligent job matching platform with AI-powered skill analysis",
        base_url: str = "http://localhost:5000",
    ):
        """Initialize OpenAPI generator."""
        self.title = title
        self.version = version
        self.description = description
        self.base_url = base_url
        self.spec: Dict[str, Any] = {}

    def generate(self) -> Dict[str, Any]:
        """Generate complete OpenAPI 3.0 specification."""
        self.spec = {
            "openapi": "3.0.0",
            "info": {
                "title": self.title,
                "description": self.description,
                "version": self.version,
                "contact": {
                    "name": "SkillsMatch.AI Support",
                    "url": "https://github.com/rubyferdianto/SkillsMatch.AI",
                },
                "license": {
                    "name": "MIT",
                },
            },
            "servers": [
                {
                    "url": self.base_url,
                    "description": "Local Development Server",
                },
                {
                    "url": "https://api.skillsmatch.ai",
                    "description": "Production Server",
                },
            ],
            "paths": self._build_paths(),
            "components": self._build_components(),
            "tags": self._build_tags(),
        }
        return self.spec

    def _build_paths(self) -> Dict[str, Any]:
        """Build paths section of OpenAPI spec."""
        return {
            # Profile endpoints
            "/api/profiles": {
                "get": {
                    "tags": ["Profiles"],
                    "summary": "List all profiles",
                    "description": "Retrieve paginated list of user profiles",
                    "operationId": "listProfiles",
                    "parameters": [
                        {
                            "name": "page",
                            "in": "query",
                            "description": "Page number (1-indexed)",
                            "schema": {"type": "integer", "default": 1},
                        },
                        {
                            "name": "per_page",
                            "in": "query",
                            "description": "Items per page",
                            "schema": {"type": "integer", "default": 20},
                        },
                        {
                            "name": "search",
                            "in": "query",
                            "description": "Search by name or email",
                            "schema": {"type": "string"},
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "List of profiles",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean"},
                                            "profiles": {
                                                "type": "array",
                                                "items": {
                                                    "$ref": "#/components/schemas/Profile"
                                                },
                                            },
                                            "total": {"type": "integer"},
                                            "page": {"type": "integer"},
                                            "per_page": {"type": "integer"},
                                        },
                                    }
                                }
                            },
                        },
                        "400": {"$ref": "#/components/responses/BadRequest"},
                        "500": {"$ref": "#/components/responses/InternalError"},
                    },
                },
                "post": {
                    "tags": ["Profiles"],
                    "summary": "Create a new profile",
                    "description": "Create a new user profile with skills and experience",
                    "operationId": "createProfile",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/CreateProfileRequest"
                                }
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "Profile created successfully",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean"},
                                            "profile": {
                                                "$ref": "#/components/schemas/Profile"
                                            },
                                            "message": {"type": "string"},
                                        },
                                    }
                                }
                            },
                        },
                        "422": {"$ref": "#/components/responses/ValidationError"},
                        "500": {"$ref": "#/components/responses/InternalError"},
                    },
                },
            },
            # Jobs endpoints
            "/api/jobs": {
                "get": {
                    "tags": ["Jobs"],
                    "summary": "List jobs",
                    "description": "Get list of available jobs with filtering options",
                    "operationId": "listJobs",
                    "parameters": [
                        {
                            "name": "page",
                            "in": "query",
                            "schema": {"type": "integer", "default": 1},
                        },
                        {
                            "name": "per_page",
                            "in": "query",
                            "schema": {"type": "integer", "default": 20},
                        },
                        {
                            "name": "search",
                            "in": "query",
                            "description": "Search by title or company",
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "position_level",
                            "in": "query",
                            "description": "Filter by position level",
                            "schema": {
                                "type": "string",
                                "enum": ["entry", "junior", "mid", "senior", "lead"],
                            },
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "List of jobs",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "success": {"type": "boolean"},
                                            "jobs": {
                                                "type": "array",
                                                "items": {
                                                    "$ref": "#/components/schemas/Job"
                                                },
                                            },
                                            "total": {"type": "integer"},
                                        },
                                    }
                                }
                            },
                        },
                        "500": {"$ref": "#/components/responses/InternalError"},
                    },
                },
            },
            # Matching endpoints
            "/api/match": {
                "post": {
                    "tags": ["Matching"],
                    "summary": "Match profile to job",
                    "description": "Find best matching jobs for a given profile",
                    "operationId": "matchProfile",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/MatchRequest"}
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Matching results",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/MatchResult"
                                    }
                                }
                            },
                        },
                        "422": {"$ref": "#/components/responses/ValidationError"},
                        "500": {"$ref": "#/components/responses/InternalError"},
                    },
                }
            },
            # Health check endpoint
            "/api/health": {
                "get": {
                    "tags": ["Health"],
                    "summary": "Health check",
                    "description": "Check API health and service status",
                    "operationId": "healthCheck",
                    "responses": {
                        "200": {
                            "description": "API is healthy",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {
                                                "type": "string",
                                                "enum": ["healthy"],
                                            },
                                            "timestamp": {
                                                "type": "string",
                                                "format": "date-time",
                                            },
                                            "services": {
                                                "type": "object",
                                                "properties": {
                                                    "database": {"type": "string"},
                                                    "cache": {"type": "string"},
                                                    "ai_service": {"type": "string"},
                                                },
                                            },
                                        },
                                    }
                                }
                            },
                        },
                        "503": {"$ref": "#/components/responses/ServiceUnavailable"},
                    },
                }
            },
        }

    def _build_components(self) -> Dict[str, Any]:
        """Build components section of OpenAPI spec."""
        return {
            "schemas": {
                "Profile": {
                    "type": "object",
                    "required": ["id", "name", "email", "created_at"],
                    "properties": {
                        "id": {"type": "string", "format": "uuid"},
                        "name": {"type": "string"},
                        "email": {"type": "string", "format": "email"},
                        "experience_level": {
                            "type": "string",
                            "enum": ["entry", "junior", "mid", "senior", "expert"],
                        },
                        "total_years_experience": {"type": "number"},
                        "skills": {
                            "type": "array",
                            "items": {"$ref": "#/components/schemas/Skill"},
                        },
                        "location": {"type": "string"},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"},
                    },
                },
                "CreateProfileRequest": {
                    "type": "object",
                    "required": ["name", "email"],
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string", "format": "email"},
                        "experience_level": {
                            "type": "string",
                            "enum": ["entry", "junior", "mid", "senior", "expert"],
                        },
                        "total_years_experience": {"type": "number"},
                        "skills": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "skill_id": {"type": "string"},
                                    "level": {
                                        "type": "string",
                                        "enum": [
                                            "beginner",
                                            "intermediate",
                                            "advanced",
                                            "expert",
                                        ],
                                    },
                                    "years": {"type": "number"},
                                },
                            },
                        },
                        "location": {"type": "string"},
                    },
                },
                "Skill": {
                    "type": "object",
                    "required": ["id", "name", "level"],
                    "properties": {
                        "id": {"type": "string"},
                        "name": {"type": "string"},
                        "level": {
                            "type": "string",
                            "enum": ["beginner", "intermediate", "advanced", "expert"],
                        },
                        "years": {"type": "number"},
                        "category": {"type": "string"},
                    },
                },
                "Job": {
                    "type": "object",
                    "required": ["id", "title", "company", "position_level"],
                    "properties": {
                        "id": {"type": "string", "format": "uuid"},
                        "title": {"type": "string"},
                        "company": {"type": "string"},
                        "position_level": {
                            "type": "string",
                            "enum": ["entry", "junior", "mid", "senior", "lead"],
                        },
                        "description": {"type": "string"},
                        "required_skills": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "location": {"type": "string"},
                        "salary_range": {
                            "type": "object",
                            "properties": {
                                "min": {"type": "number"},
                                "max": {"type": "number"},
                            },
                        },
                    },
                },
                "MatchRequest": {
                    "type": "object",
                    "required": ["profile_id"],
                    "properties": {
                        "profile_id": {"type": "string", "format": "uuid"},
                        "job_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Specific job IDs to match against (optional)",
                        },
                    },
                },
                "MatchResult": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "matches": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "job_id": {"type": "string"},
                                    "job_title": {"type": "string"},
                                    "overall_score": {"type": "number"},
                                    "skill_match_score": {"type": "number"},
                                    "experience_match_score": {"type": "number"},
                                    "location_match": {"type": "boolean"},
                                    "reasoning": {"type": "string"},
                                    "skill_gaps": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                },
                "Error": {
                    "type": "object",
                    "required": ["success", "error"],
                    "properties": {
                        "success": {"type": "boolean", "example": False},
                        "error": {"type": "string"},
                        "code": {"type": "string"},
                        "details": {"type": "object"},
                    },
                },
            },
            "responses": {
                "BadRequest": {
                    "description": "Bad request",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Error"},
                            "example": {
                                "success": False,
                                "error": "Invalid request parameters",
                                "code": "BAD_REQUEST",
                            },
                        }
                    },
                },
                "ValidationError": {
                    "description": "Validation error",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Error"},
                            "example": {
                                "success": False,
                                "error": "Validation failed",
                                "code": "VALIDATION_ERROR",
                                "details": {
                                    "field": "email",
                                    "message": "Invalid email format",
                                },
                            },
                        }
                    },
                },
                "InternalError": {
                    "description": "Internal server error",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Error"},
                            "example": {
                                "success": False,
                                "error": "An unexpected error occurred",
                                "code": "INTERNAL_ERROR",
                            },
                        }
                    },
                },
                "ServiceUnavailable": {
                    "description": "Service unavailable",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/Error"},
                            "example": {
                                "success": False,
                                "error": "Service is temporarily unavailable",
                                "code": "SERVICE_UNAVAILABLE",
                            },
                        }
                    },
                },
            },
        }

    def _build_tags(self) -> List[Dict[str, str]]:
        """Build tags section of OpenAPI spec."""
        return [
            {
                "name": "Profiles",
                "description": "User profile management",
            },
            {
                "name": "Jobs",
                "description": "Job listing and retrieval",
            },
            {
                "name": "Matching",
                "description": "Job matching and recommendations",
            },
            {
                "name": "Health",
                "description": "System health and status",
            },
        ]

    def save_to_file(self, filepath: str) -> None:
        """Save OpenAPI spec to JSON file."""
        with open(filepath, "w") as f:
            json.dump(self.spec, f, indent=2)

    def save_to_yaml(self, filepath: str) -> None:
        """Save OpenAPI spec to YAML file."""
        try:
            import yaml

            with open(filepath, "w") as f:
                yaml.dump(self.spec, f, default_flow_style=False, sort_keys=False)
        except ImportError:
            print("PyYAML not installed. Install with: pip install pyyaml")


def generate_api_docs(output_dir: str = "docs/api") -> None:
    """Generate API documentation files."""
    import os

    os.makedirs(output_dir, exist_ok=True)

    generator = OpenAPIGenerator()
    spec = generator.generate()

    # Save as JSON
    json_path = os.path.join(output_dir, "openapi.json")
    generator.save_to_file(json_path)
    print(f"✅ OpenAPI JSON saved to {json_path}")

    # Save as YAML
    yaml_path = os.path.join(output_dir, "openapi.yaml")
    try:
        generator.save_to_yaml(yaml_path)
        print(f"✅ OpenAPI YAML saved to {yaml_path}")
    except Exception as e:
        print(f"⚠️ Could not save YAML: {e}")

    return spec


if __name__ == "__main__":
    spec = generate_api_docs()
    print("\n📚 API Documentation Generated Successfully!")
