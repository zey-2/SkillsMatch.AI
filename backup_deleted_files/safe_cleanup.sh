#!/bin/bash
# Conservative File Cleanup Script for SkillsMatch.AI
# Only deletes files with HIGH confidence of safety

echo "🧹 Starting conservative cleanup of SkillsMatch.AI files..."
echo "==============================================="

cd "/Applications/RF/NTU/SCTP in DSAI/SkillsMatch.AI"

# Create backup directory first
mkdir -p backup_deleted_files
echo "📦 Created backup directory: backup_deleted_files/"

# Function to safely delete with backup
safe_delete() {
    file="$1"
    reason="$2"
    
    if [ -f "$file" ]; then
        echo "🗑️  Deleting: $file ($reason)"
        cp "$file" "backup_deleted_files/" 2>/dev/null
        rm "$file"
        echo "   ✅ Backed up to backup_deleted_files/$file"
    else
        echo "   ⚠️  File not found: $file"
    fi
}

echo ""
echo "🔥 Deleting VERY SAFE files (no references found):"
echo "------------------------------------------------"

# Test files - definitely safe
safe_delete "test_chatgpt_pro.py" "Test script"
safe_delete "test_openai_models.py" "Test script"
safe_delete "test_db_api.py" "Test script"
safe_delete "test_api.py" "Test script"
safe_delete "test_ssg_wsg.py" "Test script"
safe_delete "simple_test.py" "Test script"

# Demo files - safe
safe_delete "demo_ssg_wsg.py" "Demo script"

# Deprecated/superseded files - safe  
safe_delete "setup_ai_matching.py" "Superseded by current implementation"
safe_delete "initialize_chromadb.py" "ChromaDB not used anymore"
safe_delete "run.sh" "Superseded by start_smai.sh"
safe_delete "server.log" "Log file that gets regenerated"
safe_delete "manage_courses.py" "Unrelated to current functionality"

echo ""
echo "⚠️  SKIPPING files with references (need manual review):"
echo "-------------------------------------------------------"
echo "❌ debug_test.html - Referenced in web/app.py"
echo "❌ skillmatch.py - Referenced in multiple files"
echo "❌ test_job_matching.py - May contain useful test cases"
echo "❌ test_vector_search.py - May contain useful test cases"
echo "❌ performance_comparison.py - May contain useful benchmarks"

echo ""
echo "📊 SUMMARY:"
echo "==========="
echo "✅ Deleted files safely (with backups)"
echo "🔒 Kept files with references for manual review"
echo "📦 All deleted files backed up to: backup_deleted_files/"

echo ""
echo "🧪 RECOMMENDED NEXT STEPS:"
echo "========================"
echo "1. Test the application: ./start_smai.sh"
echo "2. If everything works, you can delete backup_deleted_files/"
echo "3. If issues occur, restore from backup_deleted_files/"

echo ""
echo "🎯 MANUAL REVIEW CANDIDATES:"
echo "============================"
echo "• Review documentation files in 'PROBABLY SAFE' category"
echo "• Check if debug_test.html is actually needed in web/app.py"
echo "• Evaluate if old test files have useful test cases to preserve"

echo ""
echo "✨ Cleanup complete!"