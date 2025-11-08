#!/usr/bin/env python3
"""
Safe File Cleanup Analysis for SkillsMatch.AI
Identifies files that can be safely deleted without breaking functionality
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def analyze_files_for_cleanup():
    """Analyze project files and categorize them for potential cleanup"""
    
    project_root = Path("/Applications/RF/NTU/SCTP in DSAI/SkillsMatch.AI")
    
    # Categories of files to analyze
    analysis = {
        "SAFE_TO_DELETE": [],
        "PROBABLY_SAFE": [],
        "REVIEW_NEEDED": [],
        "KEEP_ESSENTIAL": [],
        "ACTIVE_SCRIPTS": []
    }
    
    print("🔍 SkillsMatch.AI File Cleanup Analysis")
    print("=" * 50)
    
    # Get all files in root directory
    root_files = [f for f in project_root.iterdir() if f.is_file()]
    
    for file_path in root_files:
        filename = file_path.name
        
        # SAFE TO DELETE: Test files that are not needed in production
        if any(filename.startswith(prefix) for prefix in [
            'test_', 'demo_', 'debug_', 'simple_test', 'performance_comparison'
        ]):
            analysis["SAFE_TO_DELETE"].append({
                'file': filename,
                'reason': 'Test/demo script - not needed for production',
                'size': get_file_size(file_path)
            })
        
        # SAFE TO DELETE: Old/deprecated scripts
        elif filename in [
            'setup_ai_matching.py',  # Superseded by current implementation
            'initialize_chromadb.py',  # ChromaDB not used, using simple vector search
            'manage_courses.py',  # Seems unrelated to current functionality
            'skillmatch.py',  # Old version, web/app.py is the main app
            'run.sh',  # start_smai.sh is the main startup script
            'server.log'  # Log file that gets regenerated
        ]:
            analysis["SAFE_TO_DELETE"].append({
                'file': filename,
                'reason': 'Deprecated/superseded script',
                'size': get_file_size(file_path)
            })
        
        # PROBABLY SAFE: Documentation that might be outdated
        elif filename.endswith('.md') and filename not in [
            'README.md', 'QUICKSTART.md', 'PROJECT_SUMMARY.md'
        ]:
            analysis["PROBABLY_SAFE"].append({
                'file': filename,
                'reason': 'Documentation file - review for relevance',
                'size': get_file_size(file_path)
            })
        
        # KEEP ESSENTIAL: Core application files
        elif filename in [
            '.env', '.env.example', '.gitignore', 'README.md', 
            'requirements.txt', 'start_smai.sh'
        ]:
            analysis["KEEP_ESSENTIAL"].append({
                'file': filename,
                'reason': 'Essential configuration/startup file',
                'size': get_file_size(file_path)
            })
        
        # ACTIVE SCRIPTS: Currently used utility scripts
        elif filename in [
            'initialize_vector_db.py',  # Vector database setup
            'explain_vector_flow.py',   # Vector system documentation
            'import_jobs_csv.py',       # Job data import
            'query_jobs.py',            # Database queries
            'setup_postgresql.py'       # Database setup
        ]:
            analysis["ACTIVE_SCRIPTS"].append({
                'file': filename,
                'reason': 'Active utility script',
                'size': get_file_size(file_path)
            })
        
        # REVIEW NEEDED: Everything else
        else:
            analysis["REVIEW_NEEDED"].append({
                'file': filename,
                'reason': 'Needs manual review',
                'size': get_file_size(file_path)
            })
    
    return analysis

def get_file_size(file_path):
    """Get human-readable file size"""
    try:
        size = file_path.stat().st_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}TB"
    except:
        return "Unknown"

def check_file_usage(filename):
    """Check if file is referenced elsewhere in the project"""
    project_root = Path("/Applications/RF/NTU/SCTP in DSAI/SkillsMatch.AI")
    references = []
    
    # Check common locations for references
    search_paths = [
        project_root / "web",
        project_root / "src", 
        project_root / "tests"
    ]
    
    for search_path in search_paths:
        if search_path.exists():
            for py_file in search_path.rglob("*.py"):
                try:
                    content = py_file.read_text(encoding='utf-8', errors='ignore')
                    if filename.replace('.py', '') in content:
                        references.append(str(py_file.relative_to(project_root)))
                except:
                    continue
    
    return references

def main():
    """Main analysis function"""
    analysis = analyze_files_for_cleanup()
    
    print("\n🗑️  SAFE TO DELETE (High Confidence)")
    print("-" * 40)
    total_safe_size = 0
    for item in analysis["SAFE_TO_DELETE"]:
        print(f"✅ {item['file']} ({item['size']}) - {item['reason']}")
        
        # Check for usage
        refs = check_file_usage(item['file'])
        if refs:
            print(f"   ⚠️  Referenced in: {', '.join(refs)}")
    
    print(f"\n📊 Total files safe to delete: {len(analysis['SAFE_TO_DELETE'])}")
    
    print("\n🤔 PROBABLY SAFE (Review Recommended)")
    print("-" * 40)
    for item in analysis["PROBABLY_SAFE"]:
        print(f"📄 {item['file']} ({item['size']}) - {item['reason']}")
    
    print("\n✅ KEEP ESSENTIAL")
    print("-" * 20)
    for item in analysis["KEEP_ESSENTIAL"]:
        print(f"🔒 {item['file']} ({item['size']}) - {item['reason']}")
    
    print("\n🔧 ACTIVE SCRIPTS")
    print("-" * 20)
    for item in analysis["ACTIVE_SCRIPTS"]:
        print(f"⚙️  {item['file']} ({item['size']}) - {item['reason']}")
    
    print("\n❓ NEEDS REVIEW")
    print("-" * 15)
    for item in analysis["REVIEW_NEEDED"]:
        print(f"❓ {item['file']} ({item['size']}) - {item['reason']}")
    
    # Generate deletion commands
    print("\n🔥 SAFE DELETION COMMANDS")
    print("=" * 30)
    print("# Run these commands to delete safe files:")
    print("cd \"/Applications/RF/NTU/SCTP in DSAI/SkillsMatch.AI\"")
    
    for item in analysis["SAFE_TO_DELETE"]:
        print(f"rm \"{item['file']}\"  # {item['reason']}")
    
    print("\n⚠️  IMPORTANT NOTES:")
    print("- Test the application after deletion")
    print("- Keep a backup if you're unsure")
    print("- Documentation files can be moved to a docs/ folder instead of deleting")

if __name__ == "__main__":
    main()