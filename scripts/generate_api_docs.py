#!/usr/bin/env python
"""
Script to generate and validate API documentation for SkillsMatch.AI.

Usage:
    python scripts/generate_api_docs.py
"""

import os
import sys
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from web.utils.api_docs_generator import generate_api_docs


def main():
    """Generate API documentation."""
    print("🚀 Generating SkillsMatch.AI API Documentation...")

    try:
        # Create docs/api directory if it doesn't exist
        docs_dir = "docs/api"
        os.makedirs(docs_dir, exist_ok=True)

        # Generate API documentation
        spec = generate_api_docs(docs_dir)

        # Validate spec
        assert spec.get("openapi") == "3.0.0", "Invalid OpenAPI version"
        assert "paths" in spec, "Missing paths in specification"
        assert "components" in spec, "Missing components in specification"

        print(f"\n✅ API Documentation Generated Successfully!")
        print(f"   📄 JSON: {docs_dir}/openapi.json")
        print(f"   📄 YAML: {docs_dir}/openapi.yaml")

        # Print statistics
        num_paths = len(spec.get("paths", {}))
        num_schemas = len(spec.get("components", {}).get("schemas", {}))

        print(f"\n📊 Statistics:")
        print(f"   Endpoints: {num_paths}")
        print(f"   Schemas: {num_schemas}")

        # Print endpoints
        print(f"\n📍 Endpoints:")
        for path, methods in sorted(spec.get("paths", {}).items()):
            for method in methods.keys():
                print(f"   {method.upper():6} {path}")

        return 0

    except Exception as e:
        print(f"\n❌ Error generating documentation: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
