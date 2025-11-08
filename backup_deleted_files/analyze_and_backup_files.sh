#!/bin/bash
# Safe File Analysis and Backup Script
# Analyzes specific files and moves non-essential ones to backup

echo "🔍 Analyzing files for backup or retention..."
echo "============================================"

cd "/Applications/RF/NTU/SCTP in DSAI/SkillsMatch.AI"

# Ensure backup directory exists
mkdir -p backup_deleted_files/analysis_files
echo "📦 Created backup directory: backup_deleted_files/analysis_files/"

# Function to move file to backup
move_to_backup() {
    file="$1"
    reason="$2"
    
    if [ -f "$file" ]; then
        echo "📦 Moving to backup: $file ($reason)"
        mv "$file" "backup_deleted_files/analysis_files/"
        echo "   ✅ Moved to backup_deleted_files/analysis_files/"
    else
        echo "   ⚠️  File not found: $file"
    fi
}

# Function to keep file
keep_file() {
    file="$1"
    reason="$2"
    
    if [ -f "$file" ]; then
        echo "✅ KEEPING: $file ($reason)"
    else
        echo "   ⚠️  File not found: $file"
    fi
}

echo ""
echo "🔍 ANALYSIS RESULTS:"
echo "==================="

echo ""
echo "📦 MOVING TO BACKUP (Safe to archive):"
echo "-------------------------------------"

# Documentation/explanation files - safe to backup
move_to_backup "explain_vector_flow.py" "Documentation script - explains system flow"
move_to_backup "pdf_download_fix.md" "Bug fix documentation - issue already resolved"

# Demo files - safe to backup (not critical for production)
move_to_backup "demo.py" "Demo script - not needed for production operation"

# Test files - safe to backup (functionality already working)
move_to_backup "test_job_matching.py" "Test script - job matching already working"
move_to_backup "test_vector_search.py" "Test script - vector search already working"

# Check if test_vector_matching.py exists (it might not)
if [ -f "test_vector_matching.py" ]; then
    move_to_backup "test_vector_matching.py" "Test script - vector matching already working"
else
    echo "   ℹ️  test_vector_matching.py - File does not exist (already cleaned up)"
fi

echo ""
echo "⚠️  KEEPING (Has active references):"
echo "-----------------------------------"

# Files with active references - keep them
keep_file "debug_test.html" "Referenced in web/app.py - debug endpoint still active"

# Data import script - might be needed for future data updates
keep_file "import_jobs_csv.py" "Data import utility - may be needed for database updates"

echo ""
echo "📊 SUMMARY:"
echo "==========="
echo "📦 Moved to backup: 5-6 files (documentation, demo, test scripts)"
echo "✅ Kept essential: 2 files (debug tool, data import utility)"
echo "📁 All files safely backed up to: backup_deleted_files/analysis_files/"

echo ""
echo "💡 RATIONALE:"
echo "============"
echo "• Demo/test files moved to backup - functionality already proven working"
echo "• Documentation files archived - information preserved but not cluttering workspace"
echo "• Debug tool kept - still referenced in web application"
echo "• Import script kept - may be needed for future database operations"

echo ""
echo "🔄 NEXT STEPS:"
echo "============="
echo "1. Test the application to ensure nothing is broken"
echo "2. If you need any backed-up file, it's in backup_deleted_files/analysis_files/"
echo "3. Consider reviewing debug_test.html usage in web/app.py if not needed"

echo ""
echo "✨ File analysis and backup complete!"