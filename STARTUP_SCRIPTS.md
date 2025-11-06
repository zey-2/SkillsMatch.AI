# SkillsMatch.AI Startup Scripts

This directory contains multiple startup scripts that ensure the `smai` conda environment is always activated before running the application.

## Available Startup Scripts

### 1. `./start_skillmatch.sh` (Recommended)
- **Universal startup script** that works from any directory
- Automatically detects conda installation location
- Ensures `smai` environment is activated
- Includes comprehensive error checking
- **Usage**: `./start_skillmatch.sh`

### 2. `./start_smai.sh`
- Main project startup script
- Enhanced with better conda activation
- **Usage**: `./start_smai.sh`

### 3. `./run.sh`
- Simple launcher for local development
- Updated with conda activation
- **Usage**: `./run.sh`

### 4. `./web/start_web.sh`
- Web-specific startup script
- Run from within the web directory
- **Usage**: `cd web && ./start_web.sh`

## Environment Requirements

All scripts ensure the following:
- ✅ `smai` conda environment is activated
- ✅ Port 5003 is cleared of any existing processes
- ✅ Proper error messages if environment is missing
- ✅ Fallback to `conda run` if direct activation fails

## Creating the smai Environment

If you don't have the `smai` conda environment yet:

```bash
# Create the environment
conda create -n smai python=3.11

# Activate it
conda activate smai

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

1. **From project root directory**:
   ```bash
   ./start_skillmatch.sh
   ```

2. **From web directory**:
   ```bash
   cd web
   ./start_web.sh
   ```

## Features

- 🚀 Automatic conda environment activation
- 🧹 Port cleanup before starting
- ✅ Environment validation
- 🔧 Fallback mechanisms
- 💡 Helpful error messages
- 🌐 Application available at http://localhost:5003

## Troubleshooting

If you get environment activation errors:
1. Ensure conda is installed and in PATH
2. Create the `smai` environment as shown above
3. Try the fallback method: `conda run -n smai python web/app.py`

All startup scripts have been updated to ensure consistent conda environment activation!