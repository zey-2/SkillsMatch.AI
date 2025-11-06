# SkillsMatch.AI Quick Start Guide 🚀

## Environment Setup (CRITICAL!)

### ⚠️ ALWAYS USE THE `smai` CONDA ENVIRONMENT

This project **MUST** be run in the `smai` conda environment to ensure all dependencies work correctly.

### 🔴 Common Mistake: Using Base Environment

If you see `(base)` in your terminal instead of `(smai)`, you're using the wrong environment!

**How to Fix:**
1. Stop any running processes (Ctrl+C)
2. Activate the smai environment: `conda activate smai`
3. Verify you see `(smai)` in your prompt
4. Then run your commands

## Step-by-Step Setup

### 1. Create the smai Environment (First Time Only)

```bash
# Create the conda environment with Python 3.11
conda create -n smai python=3.11

# Activate the environment
conda activate smai
```

### 2. Verify Environment is Active

Before running ANY command, verify your terminal shows:
```
(smai) your-username@your-computer project-folder %
```

The `(smai)` prefix confirms the environment is active.

### 3. Install Dependencies

```bash
# Make sure smai is activated!
conda activate smai

# Install minimal Flask for web interface
pip install Flask

# OR install full requirements (if needed)
pip install -r requirements.txt
```

## Running the Web Application

### Run the Web Application

```bash
# 1. Activate environment
conda activate smai

# 2. Navigate to project directory
cd "/Applications/RF/NTU/SCTP in DSAI/SkillMatch.AI"

# 3. Install web dependencies (if not already installed)
pip install flask flask-cors flask-socketio eventlet beautifulsoup4 aiohttp requests

# 4. Run the application
python web/app.py
```

**Access at:** `http://localhost:5003` (or the port shown in the terminal)

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'flask'"

**Solution:**
```bash
# Check if smai environment is active
conda activate smai

# Install Flask
pip install Flask
```

### Issue: "SSL wrap_socket error" or "eventlet error"

**Solution:** Check your environment and dependencies:
```bash
conda activate smai
pip install flask flask-cors flask-socketio eventlet
python web/app.py
```

### Issue: Wrong Python Version

**Solution:**
```bash
# Deactivate current environment
conda deactivate

# Recreate smai with correct Python version
conda create -n smai python=3.11 -y
conda activate smai

# Reinstall dependencies
pip install Flask
```

### Issue: Terminal doesn't show (smai)

**Solution:**
```bash
# Activate the environment
conda activate smai

# If environment doesn't exist, create it first
conda create -n smai python=3.11
conda activate smai
```

## Daily Workflow

Every time you work on this project:

```bash
# 1. Open terminal
# 2. Navigate to project folder
cd "/Applications/RF/NTU/SCTP in DSAI/SkillMatch.AI"

# 3. ALWAYS activate smai environment FIRST
conda activate smai

# 4. Verify you see (smai) in your terminal prompt
# Your prompt should look like: (smai) username@computer folder %

# 5. Run your desired command
python web/app_minimal.py

# 6. When done, you can deactivate (optional)
conda deactivate
```

### ⚠️ IMPORTANT: Run Commands in Separate Steps

**DON'T DO THIS** (conda activate doesn't persist):
```bash
cd folder && conda activate smai && python app.py  # ❌ WRONG!
```

**DO THIS INSTEAD** (activate first, then run):
```bash
cd "/Applications/RF/NTU/SCTP in DSAI/SkillMatch.AI"
conda activate smai
python web/app_minimal.py  # ✅ CORRECT!
```

## Environment Management Commands

```bash
# List all conda environments
conda env list

# Check if smai exists
conda env list | grep smai

# Activate smai
conda activate smai

# Deactivate current environment
conda deactivate

# Remove smai environment (if needed to recreate)
conda env remove -n smai

# Export environment for others
conda env export > environment.yml

# Create environment from file
conda env create -f environment.yml
```

## Troubleshooting Checklist

Before asking for help, verify:

- [ ] `smai` environment is activated (check terminal prefix)
- [ ] You're in the correct project directory
- [ ] Flask is installed: `pip list | grep -i flask`
- [ ] Python version is correct: `python --version` (should be 3.11+)
- [ ] No other Python environments are interfering

## Quick Reference

| Command | Purpose |
|---------|---------|
| `conda activate smai` | Activate the project environment |
| `conda deactivate` | Exit current environment |
| `python web/app_minimal.py` | Run minimal web app (port 5002) |
| `python web/app_demo.py` | Run demo web app (port 5001) |
| `python web/app.py` | Run full web app (port 5000) |
| `pip install Flask` | Install Flask in current environment |
| `pip list` | Show all installed packages |
| `conda env list` | List all conda environments |

## Application Overview

| File | Port | Description |
|------|------|-------------|
| `app.py` | 5003 | Full SkillsMatch.AI application with real MySkillsFuture scraping |

**All demo/minimal versions have been removed to avoid confusion. Focus on the main application.**

---

**Remember:** 🔴 **ALWAYS USE `conda activate smai` BEFORE ANY COMMAND!** 🔴
