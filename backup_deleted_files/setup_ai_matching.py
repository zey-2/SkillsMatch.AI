#!/usr/bin/env python3
"""
Setup script for SkillsMatch.AI Enhanced AI Matching
Configures GitHub token and OpenAI API key for advanced matching capabilities
"""
import os
import json
import getpass
from pathlib import Path

def main():
    print("🚀 SkillsMatch.AI Enhanced AI Matching Setup")
    print("=" * 50)
    
    # Get current config
    config_path = Path(__file__).parent / "config" / "config.json"
    config = {}
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        print("✅ Found existing configuration")
    else:
        print("📝 Creating new configuration")
    
    print("\nFor advanced AI-powered job matching, you can configure:")
    print("1. OpenAI API Key (for ChatGPT Pro models: GPT-4o, GPT-4 Turbo, O1)")
    print("2. GitHub Token (for GitHub Copilot Pro models: GPT-5, DeepSeek-R1)")
    print("3. Both (recommended for maximum model availability)")
    print("\n💡 If you have ChatGPT Pro, use option 1 with your OpenAI API key")
    
    # GitHub Token setup
    print("\n🔑 GitHub Token Configuration")
    print("Get your token from: https://github.com/settings/tokens")
    print("Make sure to enable 'model:inference' scope for Copilot Pro models")
    
    current_github = config.get('github_token', os.environ.get('GITHUB_TOKEN', ''))
    if current_github:
        print(f"Current GitHub token: {current_github[:10]}...{current_github[-4:] if len(current_github) > 14 else ''}")
        update_github = input("Update GitHub token? (y/N): ").lower().startswith('y')
    else:
        update_github = True
    
    if update_github:
        github_token = getpass.getpass("Enter GitHub token (or press Enter to skip): ").strip()
        if github_token:
            config['github_token'] = github_token
            print("✅ GitHub token configured")
        else:
            print("⏭️ Skipping GitHub token")
    
    # OpenAI API Key setup
    print("\n🤖 OpenAI API Key Configuration")
    print("Get your key from: https://platform.openai.com/api-keys")
    
    current_openai = config.get('openai_api_key', os.environ.get('OPENAI_API_KEY', ''))
    if current_openai:
        print(f"Current OpenAI key: {current_openai[:10]}...{current_openai[-4:] if len(current_openai) > 14 else ''}")
        update_openai = input("Update OpenAI API key? (y/N): ").lower().startswith('y')
    else:
        update_openai = True
    
    if update_openai:
        openai_key = getpass.getpass("Enter OpenAI API key (or press Enter to skip): ").strip()
        if openai_key:
            config['openai_api_key'] = openai_key
            print("✅ OpenAI API key configured")
        else:
            print("⏭️ Skipping OpenAI API key")
    
    # Save configuration
    config_path.parent.mkdir(exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n💾 Configuration saved to {config_path}")
    
    # Environment variables option
    print("\n🌍 Environment Variables (Alternative Setup)")
    print("You can also set these environment variables instead of config file:")
    print("export GITHUB_TOKEN='your_github_token'")
    print("export OPENAI_API_KEY='your_openai_api_key'")
    
    # Test the configuration
    print("\n🧪 Testing AI Configuration...")
    
    try:
        # Test GitHub API
        github_token = config.get('github_token') or os.environ.get('GITHUB_TOKEN')
        if github_token:
            from openai import OpenAI
            github_client = OpenAI(
                base_url="https://models.github.ai/inference",
                api_key=github_token,
            )
            # Test a simple request
            response = github_client.chat.completions.create(
                model="openai/gpt-4o",  # Use a fallback model for testing
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            print("✅ GitHub AI API connection successful")
        else:
            print("⚠️  GitHub token not configured - AI matching will use fallback")
            
    except Exception as e:
        print(f"⚠️  GitHub AI API test failed: {e}")
        print("   You can still use the application with basic matching")
    
    try:
        # Test OpenAI API
        openai_key = config.get('openai_api_key') or os.environ.get('OPENAI_API_KEY')
        if openai_key:
            from openai import OpenAI
            openai_client = OpenAI(api_key=openai_key)
            # Test a simple request
            response = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=5
            )
            print("✅ OpenAI API connection successful")
        else:
            print("⚠️  OpenAI API key not configured - profile summaries will use fallback")
            
    except Exception as e:
        print(f"⚠️  OpenAI API test failed: {e}")
        print("   You can still use the application with basic functionality")
    
    print("\n🎉 Setup complete!")
    print("\nNext steps:")
    print("1. Start the application: python web/app.py")
    print("2. Go to the Match page")
    print("3. Select a profile and click 'Start Matching'")
    print("4. Experience AI-powered job matching!")
    
    if github_token:
        print(f"\n🚀 With GitHub Copilot Pro, you'll get access to:")
        print("   • GPT-5 for advanced reasoning ($3.69/1M tokens)")
        print("   • O1 for complex analysis ($26.25/1M tokens)")
        print("   • DeepSeek-R1 for exceptional reasoning capabilities")
        print("   • Comprehensive career insights and match analysis")

if __name__ == "__main__":
    main()