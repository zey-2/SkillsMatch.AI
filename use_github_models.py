#!/usr/bin/env python3
"""
Quick script to switch SkillsMatch.AI to use GitHub Models (free tier) instead of OpenAI
This avoids quota/billing issues while maintaining AI functionality.
"""

import os
from pathlib import Path

def switch_to_github_models():
    """Switch the .env file to prioritize GitHub Models over OpenAI"""
    
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print("❌ .env file not found!")
        return
    
    # Read current .env
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Modify to comment out OpenAI key and prioritize GitHub
    new_lines = []
    for line in lines:
        if line.startswith('OPENAI_API_KEY='):
            # Comment out OpenAI key to force GitHub fallback
            new_lines.append(f"# {line}")
            new_lines.append("# OpenAI API key temporarily disabled due to quota limits\n")
        else:
            new_lines.append(line)
    
    # Add GitHub priority setting
    new_lines.append("\n# Force GitHub Models usage (free tier)\n")
    new_lines.append("USE_GITHUB_MODELS_FIRST=true\n")
    
    # Write back to .env
    with open(env_path, 'w') as f:
        f.writelines(new_lines)
    
    print("✅ Switched to GitHub Models (free tier)")
    print("🔄 Restart the application to apply changes")
    print("💡 This avoids OpenAI quota limits while keeping AI features")

def restore_openai():
    """Restore OpenAI as primary (when quota is reset)"""
    
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print("❌ .env file not found!")
        return
    
    # Read current .env
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Restore OpenAI key
    content = content.replace('# OPENAI_API_KEY=', 'OPENAI_API_KEY=')
    content = content.replace('USE_GITHUB_MODELS_FIRST=true', 'USE_GITHUB_MODELS_FIRST=false')
    
    # Write back
    with open(env_path, 'w') as f:
        f.write(content)
    
    print("✅ Restored OpenAI as primary AI provider")
    print("🔄 Restart the application to apply changes")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        restore_openai()
    else:
        switch_to_github_models()
        print("\n📋 Usage:")
        print("  python use_github_models.py        # Switch to GitHub Models (free)")
        print("  python use_github_models.py restore # Restore OpenAI (when quota reset)")