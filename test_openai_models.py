#!/usr/bin/env python3
"""
Test script to check available OpenAI models with ChatGPT Pro subscription
"""
import os
import json
from pathlib import Path

# Load config
def load_config():
    config_path = Path(__file__).parent / "config" / "config.json"
    if config_path.exists():
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

def test_openai_models():
    try:
        from openai import OpenAI
        
        # Get API key from config or environment
        config = load_config()
        api_key = config.get('openai_api_key') or os.environ.get('OPENAI_API_KEY')
        
        if not api_key:
            print("❌ No OpenAI API key found")
            print("Set OPENAI_API_KEY environment variable or run setup_ai_matching.py")
            return
        
        print("🔍 Testing OpenAI API access...")
        client = OpenAI(api_key=api_key)
        
        # List available models
        print("\n📋 Available Models:")
        try:
            models = client.models.list()
            available_models = []
            
            for model in models.data:
                if any(prefix in model.id.lower() for prefix in ['gpt-4', 'gpt-3.5', 'o1']):
                    available_models.append(model.id)
            
            # Sort and display
            available_models.sort(reverse=True)
            for model in available_models:
                print(f"  ✅ {model}")
            
            print(f"\nTotal models available: {len(available_models)}")
            
        except Exception as e:
            print(f"❌ Could not list models: {e}")
        
        # Test with different models
        test_models = [
            "gpt-4o",           # Latest GPT-4 Omni
            "gpt-4o-mini",      # Cost-effective
            "gpt-4-turbo",      # GPT-4 Turbo
            "gpt-4",            # Standard GPT-4
            "gpt-3.5-turbo",    # Fallback
            "o1-preview",       # Advanced reasoning (if available)
            "o1-mini",          # Reasoning mini (if available)
        ]
        
        print("\n🧪 Testing model access...")
        working_models = []
        
        for model in test_models:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "user", "content": "Hello! Just testing API access."}
                    ],
                    max_tokens=10
                )
                print(f"  ✅ {model} - Working")
                working_models.append(model)
                
            except Exception as e:
                error_msg = str(e)
                if "does not exist" in error_msg:
                    print(f"  ❌ {model} - Not available")
                elif "quota" in error_msg.lower() or "billing" in error_msg.lower():
                    print(f"  ⚠️  {model} - Quota/billing issue")
                else:
                    print(f"  ❌ {model} - Error: {error_msg[:50]}...")
        
        print(f"\n✅ Working models: {len(working_models)}")
        for model in working_models:
            print(f"   • {model}")
        
        if working_models:
            print(f"\n🎉 Great! Your OpenAI API key has access to {len(working_models)} models")
            print("   SkillsMatch.AI will use these for enhanced job matching")
            
            # Check for premium models
            premium_models = [m for m in working_models if any(p in m for p in ['gpt-4o', 'gpt-4-turbo', 'o1'])]
            if premium_models:
                print(f"🚀 Premium models available: {', '.join(premium_models)}")
        else:
            print("❌ No working models found. Check your API key and billing status.")
        
    except ImportError:
        print("❌ OpenAI package not installed. Run: pip install openai")
    except Exception as e:
        print(f"❌ Error testing OpenAI: {e}")

if __name__ == "__main__":
    print("🤖 OpenAI Model Availability Test")
    print("=" * 40)
    test_openai_models()