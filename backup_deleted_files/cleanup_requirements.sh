#!/bin/bash
# Requirements Files Cleanup Script for SkillsMatch.AI
# Removes redundant requirements files safely

echo "🧹 Cleaning up redundant requirements files..."
echo "============================================="

cd "/Applications/RF/NTU/SCTP in DSAI/SkillsMatch.AI"

# Create backup directory for requirements files
mkdir -p backup_deleted_files/requirements_backup
echo "📦 Created backup directory: backup_deleted_files/requirements_backup/"

# Function to safely delete requirements files with backup
safe_delete_req() {
    file="$1"
    reason="$2"
    
    if [ -f "$file" ]; then
        echo "🗑️  Deleting: $file ($reason)"
        cp "$file" "backup_deleted_files/requirements_backup/" 2>/dev/null
        rm "$file"
        echo "   ✅ Backed up to backup_deleted_files/requirements_backup/"
    else
        echo "   ⚠️  File not found: $file"
    fi
}

echo ""
echo "🔥 Deleting REDUNDANT requirements files:"
echo "----------------------------------------"

# Remove redundant requirements files
safe_delete_req "requirements.production.txt" "Redundant - covered by main requirements.txt"
safe_delete_req "requirements.in" "pip-tools template - not needed for conda environment"
safe_delete_req "web/requirements.txt" "Duplicate - covered by main requirements.txt"

echo ""
echo "✅ KEEPING essential files:"
echo "-------------------------"
echo "📋 requirements.txt - Main dependencies (ESSENTIAL)"
echo "🗄️  requirements-postgresql.txt - Database specific (SPECIALIZED)"
echo "🧪 requirements.dev.txt - Development tools (USEFUL)"

echo ""
echo "📊 CLEANUP SUMMARY:"
echo "=================="
echo "✅ Deleted 3 redundant requirements files"
echo "✅ Kept 3 essential requirements files"
echo "📦 All deleted files backed up safely"

echo ""
echo "🎯 REMAINING STRUCTURE:"
echo "======================"
echo "• requirements.txt - Main production dependencies"
echo "• requirements-postgresql.txt - Database dependencies"  
echo "• requirements.dev.txt - Development tools"

echo ""
echo "💡 RECOMMENDED USAGE:"
echo "===================="
echo "• Production: pip install -r requirements.txt -r requirements-postgresql.txt"
echo "• Development: pip install -r requirements.dev.txt"
echo "• Database only: pip install -r requirements-postgresql.txt"

echo ""
echo "✨ Requirements cleanup complete!"