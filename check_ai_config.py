#!/usr/bin/env python3
"""
AI Configuration Checker and Setup Helper for SkillsMatch.AI

This script helps diagnose AI configuration issues and provides setup instructions.
"""

import os
import sys
from typing import Dict, List, Tuple

def check_environment_variables() -> Dict[str, any]:
    """Check for AI-related environment variables"""
    
    env_vars = {
        'GITHUB_TOKEN': os.environ.get('GITHUB_TOKEN'),
        'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY'),
        'AZURE_OPENAI_API_KEY': os.environ.get('AZURE_OPENAI_API_KEY'),
        'AZURE_OPENAI_ENDPOINT': os.environ.get('AZURE_OPENAI_ENDPOINT')
    }
    
    results = {}
    
    for key, value in env_vars.items():
        if value:
            if key == 'GITHUB_TOKEN':
                valid = value.startswith('ghp_') and len(value) > 20
                results[key] = {
                    'present': True,
                    'valid_format': valid,
                    'length': len(value),
                    'status': '✅ Valid' if valid else '⚠️ Invalid format'
                }
            elif key == 'OPENAI_API_KEY':
                valid = value.startswith('sk-') and len(value) > 40
                results[key] = {
                    'present': True,
                    'valid_format': valid,
                    'length': len(value),
                    'status': '✅ Valid' if valid else '⚠️ Invalid format'
                }
            else:
                results[key] = {
                    'present': True,
                    'valid_format': True,
                    'length': len(value),
                    'status': '✅ Present'
                }
        else:
            results[key] = {
                'present': False,
                'valid_format': False,
                'length': 0,
                'status': '❌ Missing'
            }
    
    return results

def print_setup_instructions():\n    \"\"\"Test AI service connectivity\"\"\"\n    \n    results = {}\n    \n    # Test GitHub Models\n    github_token = os.environ.get('GITHUB_TOKEN')\n    if github_token and github_token.startswith('ghp_'):\n        try:\n            from openai import OpenAI\n            client = OpenAI(\n                base_url=\"https://models.github.ai/inference\",\n                api_key=github_token,\n                timeout=10.0\n            )\n            \n            # Simple test request\n            response = client.chat.completions.create(\n                model=\"openai/gpt-4.1-mini\",\n                messages=[{\"role\": \"user\", \"content\": \"Hello\"}],\n                max_tokens=5\n            )\n            \n            results['github_models'] = {\n                'status': '✅ Working',\n                'model': 'openai/gpt-4.1-mini',\n                'response_length': len(response.choices[0].message.content)\n            }\n            \n        except Exception as e:\n            error_msg = str(e).lower()\n            if 'unauthorized' in error_msg or '401' in error_msg:\n                status = '❌ Unauthorized - Check token'\n            elif 'too many requests' in error_msg or '429' in error_msg:\n                status = '⚠️ Rate limited - Try later'\n            else:\n                status = f'❌ Error: {str(e)[:50]}'\n            \n            results['github_models'] = {\n                'status': status,\n                'error': str(e)\n            }\n    else:\n        results['github_models'] = {\n            'status': '⚪ Not configured',\n            'note': 'No valid GitHub token found'\n        }\n    \n    # Test OpenAI\n    openai_key = os.environ.get('OPENAI_API_KEY')\n    if openai_key and openai_key.startswith('sk-'):\n        try:\n            from openai import OpenAI\n            client = OpenAI(api_key=openai_key, timeout=10.0)\n            \n            response = client.chat.completions.create(\n                model=\"gpt-4o-mini\",\n                messages=[{\"role\": \"user\", \"content\": \"Hello\"}],\n                max_tokens=5\n            )\n            \n            results['openai'] = {\n                'status': '✅ Working',\n                'model': 'gpt-4o-mini',\n                'response_length': len(response.choices[0].message.content)\n            }\n            \n        except Exception as e:\n            error_msg = str(e).lower()\n            if 'unauthorized' in error_msg or '401' in error_msg:\n                status = '❌ Unauthorized - Check API key'\n            elif 'too many requests' in error_msg or '429' in error_msg:\n                status = '⚠️ Rate limited - Try later'\n            else:\n                status = f'❌ Error: {str(e)[:50]}'\n            \n            results['openai'] = {\n                'status': status,\n                'error': str(e)\n            }\n    else:\n        results['openai'] = {\n            'status': '⚪ Not configured',\n            'note': 'No valid OpenAI API key found'\n        }\n    \n    return results\n\ndef print_setup_instructions():\n    \"\"\"Print detailed setup instructions\"\"\"\n    \n    print(\"\"\"\n🔧 AI SETUP INSTRUCTIONS FOR SKILLSMATCH.AI\n=============================================\n\n1. GITHUB MODELS (RECOMMENDED - FREE TIER)\n   ----------------------------------------\n   • Go to: https://github.com/settings/tokens\n   • Click \"Generate new token (classic)\"\n   • Select scopes: repo, read:user\n   • Copy the token (starts with ghp_)\n   • Set environment variable:\n     \n     export GITHUB_TOKEN=\"ghp_your_token_here\"\n     \n   • Add to your shell profile (~/.zshrc or ~/.bashrc):\n     echo 'export GITHUB_TOKEN=\"ghp_your_token_here\"' >> ~/.zshrc\n     source ~/.zshrc\n\n2. OPENAI API (PREMIUM OPTION)\n   ----------------------------\n   • Go to: https://platform.openai.com/account/api-keys\n   • Click \"Create new secret key\"\n   • Copy the key (starts with sk-)\n   • Set environment variable:\n     \n     export OPENAI_API_KEY=\"sk-your_key_here\"\n     \n   • Add to shell profile:\n     echo 'export OPENAI_API_KEY=\"sk-your_key_here\"' >> ~/.zshrc\n     source ~/.zshrc\n\n3. VERIFY SETUP\n   -------------\n   • Restart your terminal\n   • Run this script again: python check_ai_config.py\n   • Start SkillsMatch.AI: ./start_skillmatch.sh\n   • Look for \"✅ Initialized AI Skill Matcher\" in the logs\n\n4. TROUBLESHOOTING\n   ---------------\n   • 401 Unauthorized: Invalid API key format or expired token\n   • 429 Too Many Requests: Rate limit exceeded, wait a few minutes\n   • Import errors: Run 'pip install openai' in smai environment\n   \n   If AI fails, the system will use enhanced fallback matching.\n\"\"\")\n\ndef main():\n    \"\"\"Main diagnostic function\"\"\"\n    \n    print(\"🔍 SkillsMatch.AI - AI Configuration Checker\")\n    print(\"=\" * 50)\n    \n    # Check environment variables\n    print(\"\\n📋 Environment Variables:\")\n    env_results = check_environment_variables()\n    \n    for key, result in env_results.items():\n        print(f\"   {key}: {result['status']}\")\n        if result['present']:\n            print(f\"      Length: {result['length']} characters\")\n    \n    # Check if any AI service is configured\n    github_ok = env_results['GITHUB_TOKEN']['valid_format']\n    openai_ok = env_results['OPENAI_API_KEY']['valid_format']\n    \n    if not (github_ok or openai_ok):\n        print(\"\\n⚠️  No valid AI services configured!\")\n        print(\"   SkillsMatch.AI will use enhanced fallback matching.\")\n        print_setup_instructions()\n        return\n    \n    # Test AI services\n    print(\"\\n🤖 AI Service Connectivity:\")\n    try:\n        ai_results = test_ai_services()\n        \n        for service, result in ai_results.items():\n            print(f\"   {service.title()}: {result['status']}\")\n            if 'model' in result:\n                print(f\"      Model: {result['model']}\")\n            if 'error' in result:\n                print(f\"      Error: {result['error'][:100]}\")\n                \n    except ImportError:\n        print(\"   ❌ OpenAI library not installed\")\n        print(\"   💡 Run: pip install openai\")\n    except Exception as e:\n        print(f\"   ❌ Test failed: {e}\")\n    \n    # Summary and recommendations\n    print(\"\\n💡 Recommendations:\")\n    \n    if github_ok:\n        print(\"   ✅ GitHub Models configured - Free tier AI matching available\")\n    elif openai_ok:\n        print(\"   ✅ OpenAI configured - Premium AI matching available\")\n    \n    working_services = 0\n    try:\n        ai_results = test_ai_services()\n        working_services = sum(1 for result in ai_results.values() if '✅' in result['status'])\n    except:\n        pass\n    \n    if working_services == 0:\n        print(\"   ⚠️  No AI services working - check API keys and network\")\n        print(\"   🔄 Enhanced fallback matching will be used\")\n    else:\n        print(f\"   🚀 {working_services} AI service(s) working - Enhanced matching enabled!\")\n    \n    print(\"\\n🎯 Next Steps:\")\n    print(\"   1. Fix any issues shown above\")\n    print(\"   2. Restart terminal to load new environment variables\")\n    print(\"   3. Run: ./start_skillmatch.sh\")\n    print(\"   4. Test job matching at: http://localhost:5004\")\n    \nif __name__ == \"__main__\":\n    main()