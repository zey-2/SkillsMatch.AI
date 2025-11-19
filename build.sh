#!/bin/bash
# Render.com build script for SQLite deployment
set -e

echo "🚀 Starting SkillsMatch.AI build for Render.com with SQLite..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements-render.txt

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data
mkdir -p uploads/resumes
mkdir -p profiles
mkdir -p web/data

# Initialize SQLite database
echo "🗃️ Initializing SQLite database..."
export USE_SQLITE=true
export RENDER=true
python init_sqlite.py

echo "✅ Build completed successfully with SQLite!"
echo "🌐 Ready for deployment on Render.com"
echo "📊 Database: SQLite (bundled, no external dependencies)"