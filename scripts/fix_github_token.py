#!/usr/bin/env python3
"""
GitHub Token Diagnostic and Fix Script for SkillsMatch.AI
This script helps diagnose and fix GitHub token authentication issues.
"""

import os
import requests
from pathlib import Path
from dotenv import load_dotenv

def check_github_token():
    """Check if GitHub token is valid and has correct permissions"""
    
    # Load environment
    env_path = Path(__file__).resolve().parents[1] / '.env'
    load_dotenv(env_path)
    
    github_token = os.environ.get('GITHUB_TOKEN')
    
    if not github_token:
        print("❌ No GITHUB_TOKEN found in .env file")
        return False
    
    print(f"🔍 GitHub token found (length: {len(github_token)})")
    print(f"🔍 Token prefix: {github_token[:20]}...")
    
    # Test GitHub API access
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        # Test basic GitHub API access
        response = requests.get('https://api.github.com/user', headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ GitHub API access successful")
            print(f"👤 Authenticated as: {user_data.get('login', 'Unknown')}")
            
            # Check token scopes
            scopes = response.headers.get('X-OAuth-Scopes', '').split(', ')
            print(f"🔑 Token scopes: {scopes}")
            
            # Test GitHub Models access
            return test_github_models(github_token)
            
        elif response.status_code == 401:
            print("❌ GitHub token is invalid or expired")
            print("💡 Generate a new token at: https://github.com/settings/tokens")
            return False
        else:
            print(f"❌ GitHub API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing GitHub token: {e}")
        return False

def test_github_models(github_token):
    """Test GitHub Models API access"""
    
    try:
        from openai import OpenAI
        
        client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=github_token
        )
        
        # Test with a simple request
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        
        print("✅ GitHub Models access successful")
        print(f"🤖 Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ GitHub Models access failed: {e}")
        print("💡 Possible solutions:")
        print("   1. Generate a new token with 'repo' or 'public_repo' scope")
        print("   2. Wait a few minutes for token activation")
        print("   3. Check if GitHub Models is available for your account")
        return False

def generate_new_token_instructions():
    """Provide instructions for generating a new GitHub token"""
    
    print("\n🔧 How to generate a new GitHub token:")
    print("1. Visit: https://github.com/settings/tokens")
    print("2. Click 'Generate new token (classic)'")
    print("3. Give it a name: 'SkillsMatch AI'")
    print("4. Select scopes:")
    print("   ✓ repo (Full control of private repositories)")
    print("   ✓ read:user (Read user profile)")
    print("5. Click 'Generate token'")
    print("6. Copy the token (starts with 'ghp_' or 'github_pat_')")
    print("7. Update your .env file:")
    print("   GITHUB_TOKEN=your_new_token_here")
    print("8. Restart the application")

def fix_env_file():
    """Help fix the .env file configuration"""
    
    env_path = Path(__file__).resolve().parents[1] / '.env'
    
    print(f"\n📝 Current .env file location: {env_path}")
    
    if env_path.exists():
        with open(env_path, 'r') as f:
            content = f.read()
        
        if 'GITHUB_TOKEN=' in content:
            print("✅ GITHUB_TOKEN found in .env file")
        else:
            print("❌ GITHUB_TOKEN not found in .env file")
            print("💡 Add this line to your .env file:")
            print("GITHUB_TOKEN=your_github_token_here")
    else:
        print("❌ .env file not found!")
        print("💡 Create a .env file with:")
        print("GITHUB_TOKEN=your_github_token_here")

if __name__ == "__main__":
    print("🔍 GitHub Token Diagnostic Tool")
    print("=" * 50)
    
    # Check current token
    token_valid = check_github_token()
    
    if not token_valid:
        print("\n" + "=" * 50)
        generate_new_token_instructions()
        fix_env_file()
    else:
        print("\n✅ GitHub token is working correctly!")
        print("🚀 You can now use GitHub Models in SkillsMatch.AI")