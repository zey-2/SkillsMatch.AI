#!/bin/bash
# SkillsMatch.AI Startup Script using smai conda environment
# Usage: ./start_smai.sh

echo "🚀 Starting SkillsMatch.AI with smai environment..."

# Kill any existing Flask processes
echo "🧹 Cleaning up existing processes..."
lsof -ti:5003 | xargs kill -9 2>/dev/null || echo "Port 5003 is clear"
pkill -f "python.*app.py" 2>/dev/null || true
sleep 2

# Navigate to project directory
cd "$(dirname "$0")"

# Initialize conda in this shell
source ~/miniconda3/etc/profile.d/conda.sh 2>/dev/null || source ~/anaconda3/etc/profile.d/conda.sh 2>/dev/null || true

# Check if smai conda environment exists
if ! conda env list | grep -q "smai"; then
    echo "❌ Error: 'smai' conda environment not found!"
    echo "📝 Please create it first with: conda create -n smai python=3.11"
    echo "📦 Then install dependencies: conda activate smai && pip install -r requirements.txt"
    exit 1
fi

# Activate smai conda environment
echo "🔧 Activating smai environment..."
conda activate smai

# Check if activation was successful
if [ "$CONDA_DEFAULT_ENV" != "smai" ]; then
    echo "⚠️ Warning: Could not activate smai environment. Trying conda run instead..."
    cd web
    conda run -n smai python app.py
else
    echo "✅ smai environment activated successfully!"
    echo "🌐 App will be available at: http://localhost:5003"
    echo "🔧 Direct API access configured for data integration"
    echo "💡 Features: Profile Matching, AI Chat, Database Management"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    # Navigate to web directory and start Flask app
    cd web
    python app.py
fi