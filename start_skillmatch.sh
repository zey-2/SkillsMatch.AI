#!/bin/bash
# Universal SkillsMatch.AI Startup Script with automatic conda activation
# Can be run from any directory
# Usage: ./start_skillmatch.sh

echo "🚀 SkillsMatch.AI Universal Startup Script"
echo "📍 This script ensures 'base' conda environment is always activated"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR"
WEB_DIR="$PROJECT_DIR/web"

# Kill any existing processes on port 5004
echo "🧹 Cleaning up port 5004..."
lsof -ti:5004 | xargs kill -9 2>/dev/null || echo "Port 5004 is clear"

# Initialize conda in this shell (try multiple locations)
if [ -f ~/miniconda3/etc/profile.d/conda.sh ]; then
    source ~/miniconda3/etc/profile.d/conda.sh
    echo "🐍 Using miniconda3"
elif [ -f ~/anaconda3/etc/profile.d/conda.sh ]; then
    source ~/anaconda3/etc/profile.d/conda.sh
    echo "🐍 Using anaconda3"
elif [ -f /opt/conda/etc/profile.d/conda.sh ]; then
    source /opt/conda/etc/profile.d/conda.sh
    echo "🐍 Using system conda"
else
    echo "❌ Error: Could not find conda installation!"
    echo "💡 Please ensure conda is installed and available in PATH"
    exit 1
fi

# Check if base environment exists
if ! conda env list | grep -q "base"; then
    echo "❌ Error: 'base' conda environment not found!"
    echo "📝 Please create it first:"
    echo "   conda create -n base python=3.11"
    echo "   conda activate base"
    echo "   pip install -r requirements.txt"
    echo ""
    echo "📋 Available environments:"
    conda env list
    exit 1
fi

echo "🔧 Activating base environment..."

# Change to web directory
cd "$WEB_DIR" || {
    echo "❌ Error: Could not find web directory at $WEB_DIR"
    exit 1
}

# FORCE activate environment with multiple attempts
echo "🔧 Forcing conda activation..."

# Method 1: Standard conda activate
conda activate base 2>/dev/null

# Method 2: Force activation if first attempt failed
if [ "$CONDA_DEFAULT_ENV" != "base" ]; then
    echo "🔄 First activation attempt failed, trying alternative methods..."
    eval "$(conda shell.bash hook)"
    conda activate base
fi

# Method 3: Use conda run if activation still failed
if [ "$CONDA_DEFAULT_ENV" != "base" ]; then
    echo "⚠️  Direct activation failed. Using conda run as primary method..."
    echo "🔧 Running: conda run -n base python app.py"
    echo "✅ Running in correct conda environment: base"
    echo "📂 Working directory: $(pwd)"
    echo "🌐 Starting Flask app on http://localhost:5004"
    echo "💡 App features: Profile Matching, AI Chat, Database Management"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo "========================================"
    echo ""
    
    # Use conda run to ensure correct environment
    conda run -n base python app.py
else
    echo "✅ base environment activated successfully!"
    
    # Verify Python environment
    echo "🐍 Using Python: $(which python)"
    echo "📦 Conda environment: $CONDA_DEFAULT_ENV"
    echo "� Working directory: $(pwd)"
    echo "🌐 Starting Flask app on http://localhost:5004"
    echo "💡 App features: Profile Matching, AI Chat, Database Management"
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo "========================================"
    echo ""
    
    # Start the Flask application in activated environment
    python app.py
fi