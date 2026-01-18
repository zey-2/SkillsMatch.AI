# 🔒 API Security Guide for SkillsMatch.AI

## ⚠️ **CRITICAL: API Key Security**

Your API keys are **valuable credentials** that must be protected. Follow this guide to ensure security when pushing to Git.

## 🚨 **Current Status Check**

✅ **GOOD**: `.env` file is in `.gitignore` - won't be committed  
✅ **GOOD**: Application uses secure loading methods  
⚠️  **ACTION NEEDED**: Remove API keys before any Git commits  

## 🛡️ **Secure API Key Storage Methods**

### **Method 1: Environment Variables (MOST SECURE)**
```bash
# In your terminal/shell profile (.zshrc, .bashrc)
export OPENAI_API_KEY="your_actual_key_here"
export GITHUB_TOKEN="your_actual_token_here"

# Then start the app
conda activate smai
python web/app.py
```

### **Method 2: Local Config File (DEVELOPMENT)**
```json
// config/config.json (also gitignored)
{
  "openai_api_key": "your_actual_key_here",
  "github_token": "your_actual_token_here"
}
```

### **Method 3: .env File (CURRENT - SECURE IF GITIGNORED)**
```bash
# .env file (must be in .gitignore)
OPENAI_API_KEY=your_actual_key_here
GITHUB_TOKEN=your_actual_token_here
```

## 🚫 **NEVER DO THIS:**

❌ **DON'T** commit `.env` with real keys  
❌ **DON'T** put keys directly in Python files  
❌ **DON'T** put keys in any file that gets committed  
❌ **DON'T** share keys in chat/email/screenshots  

## ✅ **SAFE FOR GIT COMMITS:**

✅ **DO** commit `.env.example` with placeholder values  
✅ **DO** commit `.env.example` with templates  
✅ **DO** ensure `.gitignore` includes `.env` and `config/config.json`  
✅ **DO** use placeholder values in documentation  

## 🔧 **Pre-Commit Security Checklist**

Before pushing to Git, run this check:

```bash
# Check what will be committed
git status
git diff --staged

# Verify no API keys in staged files
grep -r "sk-proj" . --exclude-dir=.git
grep -r "github_pat" . --exclude-dir=.git

# If found, remove them before committing!
```

## 🚀 **Production Deployment Security**

For production environments:

1. **Use Environment Variables**
   ```bash
   export OPENAI_API_KEY="production_key"
   export GITHUB_TOKEN="production_token"
   ```

2. **Use Secret Management Services**
   - AWS Secrets Manager
   - Azure Key Vault
   - Google Secret Manager
   - Docker secrets

3. **Use CI/CD Secret Variables**
   - GitHub Actions secrets
   - GitLab CI variables
   - Jenkins credentials

## 🔄 **Current Application Security Features**

The SkillsMatch.AI app already implements secure key loading:

```python
# Priority order (most secure first):
openai_key = (
    os.getenv('OPENAI_API_KEY') or          # 1. Environment variable
    config.get('openai_api_key') or         # 2. Config file  
    load_from_env_file('OPENAI_API_KEY')    # 3. .env file
)
```

## 🆘 **If API Keys Are Accidentally Committed**

**IMMEDIATE ACTIONS:**

1. **Revoke the keys immediately**
   - OpenAI: https://platform.openai.com/api-keys
   - GitHub: https://github.com/settings/tokens

2. **Generate new keys**

3. **Remove from Git history**
   ```bash
   # Remove sensitive file from all commits
   git filter-branch --force --index-filter \
   'git rm --cached --ignore-unmatch .env' \
   --prune-empty --tag-name-filter cat -- --all
   
   # Force push (WARNING: destructive)
   git push origin --force --all
   ```

4. **Update your local keys**

## 📋 **Best Practices Summary**

- ✅ Keep API keys in environment variables or local config files
- ✅ Always use `.env.example` templates for documentation  
- ✅ Add security checks to your git workflow
- ✅ Regularly rotate API keys
- ✅ Monitor API usage for unusual activity
- ✅ Use different keys for development/production

## 🔍 **Quick Security Verification**

Run this to verify your current setup:

```bash
cd "/Applications/RF/NTU/SCTP in DSAI/SkillsMatch.AI"

# Check gitignore
echo "=== GITIGNORE CHECK ==="
grep -E "\\.env|config\\.json" .gitignore

# Check for staged secrets
echo "=== STAGED FILES CHECK ==="
git diff --staged --name-only

# Verify app can load keys securely
echo "=== API KEY LOADING TEST ==="
conda activate smai
python -c "
import os
from pathlib import Path
import json

# Check environment variables
env_key = bool(os.getenv('OPENAI_API_KEY'))
print(f'Environment variable: {env_key}')

# Check config file
config_path = Path('config/config.json')
config_key = False
if config_path.exists():
    with open(config_path) as f:
        config = json.load(f)
        config_key = bool(config.get('openai_api_key'))
print(f'Config file: {config_key}')

# Check .env file  
env_file = Path('.env').exists()
print(f'.env file exists: {env_file}')

print(f'API key available: {env_key or config_key or env_file}')
"
```

Your current setup is **already secure** as long as you don't accidentally commit the `.env` file! 🛡️