"""
AI Configuration for SkillsMatch.AI

Centralized configuration for AI models and services used in the application.
"""

import os
from typing import Dict, Optional


class AIConfig:
    """Configuration class for AI services"""

    def __init__(self):
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.azure_api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        self.azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")

        # Model preferences (in order of preference)
        self.model_preferences = [
            {
                "name": "OpenAI",
                "base_url": "https://api.openai.com/v1",
                "api_key": self.openai_api_key,
                "models": {
                    "fast": "gpt-5-mini",
                    "balanced": "gpt-5-mini",
                    "premium": "gpt-5-mini",
                    "reasoning": "gpt-5-mini",
                },
                "available": bool(self.openai_api_key),
            },
        ]

    def get_best_provider(self) -> Optional[Dict]:
        """Get the best available AI provider"""
        for provider in self.model_preferences:
            if provider["available"]:
                return provider
        return None

    def get_model_for_task(self, task_type: str = "balanced") -> tuple:
        """
        Get the best model for a specific task type

        Args:
            task_type: Type of task ('fast', 'balanced', 'premium', 'reasoning')

        Returns:
            tuple: (provider_info, model_id) or (None, None) if no provider available
        """
        provider = self.get_best_provider()
        if not provider:
            return None, None

        model_id = provider["models"].get(task_type, provider["models"]["balanced"])
        return provider, model_id

    def get_environment_info(self) -> Dict:
        """Get information about available AI services"""
        return {
            "github_token_available": bool(self.github_token),
            "openai_key_available": bool(self.openai_api_key),
            "azure_key_available": bool(self.azure_api_key),
            "best_provider": self.get_best_provider()["name"]
            if self.get_best_provider()
            else None,
            "total_providers": sum(1 for p in self.model_preferences if p["available"]),
        }


# Global configuration instance
ai_config = AIConfig()


# Convenience functions
def get_ai_provider():
    """Get the best available AI provider"""
    return ai_config.get_best_provider()


def get_ai_model(task_type: str = "balanced"):
    """Get the best AI model for a task"""
    return ai_config.get_model_for_task(task_type)


def is_ai_available():
    """Check if any AI provider is available"""
    return ai_config.get_best_provider() is not None


def get_ai_info():
    """Get AI environment information"""
    return ai_config.get_environment_info()
