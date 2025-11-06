#!/bin/bash
# Simple launcher for SkillsMatch.AI local development

echo "🚀 Starting SkillsMatch.AI..."
echo ""

# Kill any existing processes on port 5003
lsof -ti:5003 | xargs kill -9 2>/dev/null || echo "Port 5003 is clear"

# Navigate to project directory
cd "/Applications/RF/NTU/SCTP in DSAI/SkillsMatch.AI"

# Initialize conda in this shell
source ~/miniconda3/etc/profile.d/conda.sh 2>/dev/null || source ~/anaconda3/etc/profile.d/conda.sh 2>/dev/null || true

# Activate smai environment and run
conda activate smai

# Verify activation
if [ "$CONDA_DEFAULT_ENV" = "smai" ]; then
    echo "✅ Environment: smai activated successfully"
    echo "🌐 Starting web application..."
    echo ""
    python web/app.py
else
    echo "⚠️ Warning: smai environment not activated. Using conda run instead..."
    conda run -n smai python web/app.py
fi