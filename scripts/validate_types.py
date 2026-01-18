#!/usr/bin/env python
"""
Script to validate type hints using mypy.

Usage:
    python scripts/validate_types.py          # Check all files
    python scripts/validate_types.py --fix    # Auto-fix if possible (not supported by mypy)
"""

import subprocess
import sys
import os


def run_mypy():
    """Run mypy type checking."""
    print("🔍 Running mypy type checker...")
    print("-" * 60)

    cmd = [
        "mypy",
        "web/services/",
        "web/blueprints/",
        "src/skillmatch/",
        "--config-file=mypy.ini",
        "--show-error-codes",
        "--pretty",
    ]

    result = subprocess.run(cmd)

    print("-" * 60)

    if result.returncode == 0:
        print("✅ All type checks passed!")
        return True
    else:
        print("❌ Type check failed!")
        print("\n💡 Tips:")
        print("   - Add type hints to function arguments and return values")
        print("   - Use Optional[Type] for nullable values")
        print("   - Import types from typing module")
        print("   - Use Union[Type1, Type2] for multiple possible types")
        return False


def check_coverage():
    """Check type hint coverage in key files."""
    print("\n📊 Type Hint Coverage Analysis")
    print("-" * 60)

    import ast
    from pathlib import Path

    def has_type_hints(func_def):
        """Check if function has type hints."""
        # Check return type
        if func_def.returns is None and func_def.name != "__init__":
            return False
        # Check argument types (skip 'self')
        args = func_def.args
        for arg in args.args:
            if arg.arg != "self" and arg.annotation is None:
                return False
        return True

    total_functions = 0
    typed_functions = 0

    for py_file in Path("web/services/").glob("**/*.py"):
        if py_file.name.startswith("_"):
            continue

        try:
            with open(py_file) as f:
                tree = ast.parse(f.read())

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Skip private methods
                    if node.name.startswith("_") and node.name != "__init__":
                        continue

                    total_functions += 1
                    if has_type_hints(node):
                        typed_functions += 1
        except Exception as e:
            print(f"⚠️  Could not parse {py_file}: {e}")

    if total_functions > 0:
        coverage = (typed_functions / total_functions) * 100
        print(
            f"Services Type Coverage: {typed_functions}/{total_functions} ({coverage:.1f}%)"
        )

        if coverage >= 90:
            print("✅ Excellent type coverage!")
        elif coverage >= 70:
            print("✓ Good type coverage")
        else:
            print("⚠️  Consider adding more type hints")

    print("-" * 60)


def main():
    """Run type validation."""
    print("=" * 60)
    print("SkillsMatch.AI Type Hint Validation")
    print("=" * 60)

    # Check if mypy is installed
    try:
        subprocess.run(["mypy", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ mypy is not installed!")
        print("   Install with: pip install mypy")
        return 1

    # Run mypy
    success = run_mypy()

    # Check coverage
    check_coverage()

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
