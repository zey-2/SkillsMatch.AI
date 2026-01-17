#!/usr/bin/env python3
"""
Simple AI Configuration Checker for SkillsMatch.AI
"""

import os

def main():
    print("🔍 SkillsMatch.AI - AI Configuration Checker")
    print("=" * 50)
    
    # Check environment variables
    print("\n📋 Environment Variables:")
    
    github_token = os.environ.get('GITHUB_TOKEN')
    openai_key = os.environ.get('OPENAI_API_KEY')
    
    if github_token:
        if github_token.startswith('ghp_') and len(github_token) > 20:
            print(f"   GITHUB_TOKEN: ✅ Valid ({len(github_token)} chars)")
        else:
            print(f"   GITHUB_TOKEN: ⚠️ Invalid format ({len(github_token)} chars)")
    else:
        print("   GITHUB_TOKEN: ❌ Missing")
    
    if openai_key:
        if openai_key.startswith('sk-') and len(openai_key) > 40:
            print(f"   OPENAI_API_KEY: ✅ Valid ({len(openai_key)} chars)")
        else:
            print(f"   OPENAI_API_KEY: ⚠️ Invalid format ({len(openai_key)} chars)")
    else:
        print("   OPENAI_API_KEY: ❌ Missing")
    
    # Check OpenAI library
    try:
        import openai
        print(f"\n📦 OpenAI library: ✅ Installed (v{openai.__version__})")
    except ImportError:
        print("\n📦 OpenAI library: ❌ Not installed")
        print("   💡 Run: pip install openai")
        return
    
    # Status summary
    github_ok = github_token and github_token.startswith('ghp_') and len(github_token) > 20
    openai_ok = openai_key and openai_key.startswith('sk-') and len(openai_key) > 40
    
    print("\n💡 Current Status:")
    if github_ok:
        print("   ✅ GitHub Models ready - Free AI matching available")
    if openai_ok:
        print("   ✅ OpenAI ready - Premium AI matching available")
    
    if not (github_ok or openai_ok):
        print("   ⚠️  No valid AI keys found")
        print("   🔄 Will use enhanced fallback matching")
        print("\n🔧 To enable AI features:")
        print("   1. Get GitHub token: https://github.com/settings/tokens")
        print("   2. Or get OpenAI key: https://platform.openai.com/account/api-keys")
        print("   3. Set environment variable:")
        print("      export GITHUB_TOKEN='ghp_your_token'")
        print("      export OPENAI_API_KEY='sk-your_key'")
        print("   4. Restart terminal and try again")
    else:
        print("   🚀 AI-enhanced matching enabled!")
    
    print("\n🎯 Next Steps:")
    print("   1. Start app: ./start_skillmatch.sh")
    print("   2. Check startup logs for: '✅ Initialized AI Skill Matcher'")
    print("   3. Test at: http://localhost:5004")

if __name__ == "__main__":
    main()