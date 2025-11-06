#!/bin/bash
# Web Application Startup Script with conda activation
# Usage: ./start_web.sh

echo "🚀 Starting SkillsMatch.AI Web Application..."

# Kill any existing processes on port 5003
lsof -ti:5003 | xargs kill -9 2>/dev/null || echo "Port 5003 is clear"

# Navigate to web directory
cd "$(dirname "$0")"

# Initialize conda
source ~/miniconda3/etc/profile.d/conda.sh 2>/dev/null || source ~/anaconda3/etc/profile.d/conda.sh 2>/dev/null || true

# Check if smai environment exists
if ! conda env list | grep -q "smai"; then
    echo "❌ Error: 'smai' conda environment not found!"
    echo "📝 Please create it first with: conda create -n smai python=3.11"
    echo "📦 Then install dependencies: conda activate smai && pip install -r requirements.txt"
    exit 1
fi

# Activate smai environment
conda activate smai

# Verify activation and start app
if [ "$CONDA_DEFAULT_ENV" = "smai" ]; then
    echo "✅ smai environment activated"
    echo "🌐 Starting Flask app on http://localhost:5003"
    echo "Press Ctrl+C to stop"
    echo ""
    python app.py
else
    echo "⚠️ Using conda run as fallback..."
    conda run -n smai python app.py
fi