#!/usr/bin/env python3
"""
Main entry point for SkillMatch.AI CLI
"""
import sys
import os

# Add src directory to path so we can import skillmatch
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from skillmatch.cli import main

if __name__ == '__main__':
    main()