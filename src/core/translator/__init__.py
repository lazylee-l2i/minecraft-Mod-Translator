"""Translation engine factory and exports."""
from typing import Optional

from .base import BaseTranslator
from .openai_translator import OpenAITranslator
from .openrouter_translator import OpenRouterTranslator
from .ollama_translator import OllamaTranslator

__all__ = [
    "BaseTranslator",
    "OpenAITranslator",
    "OpenRouterTranslator",
    "OllamaTranslator",
    "create_translator",
    "LLMProvider",
]


class LLMProvider:
    """LLM Provider constants."""
    OPENAI = "OpenAI GPT"
    OPENROUTER = "OpenRouter"
    OLLAMA = "Ollama (Local)"
    
    @classmethod
    def all(cls) -> list[str]:
        """Get all provider names."""
        return [cls.OPENAI, cls.OPENROUTER, cls.OLLAMA]


def create_translator(
    provider: str,
    api_key: str = "",
    model: str = "",
    server_url: str = "",
) -> BaseTranslator:
    """
    Factory function to create appropriate translator.
    
    Args:
        provider: Provider name (OpenAI GPT, OpenRouter, Ollama (Local))
        api_key: API key for cloud providers (memory only)
        model: Model name
        server_url: Server URL for Ollama
        
    Returns:
        Configured translator instance
        
    Raises:
        ValueError: If unknown provider is specified
    """
    if provider == LLMProvider.OPENAI:
        return OpenAITranslator(
            api_key=api_key,
            model=model or "gpt-4o"
        )
    elif provider == LLMProvider.OPENROUTER:
        return OpenRouterTranslator(
            api_key=api_key,
            model=model or "openai/gpt-4o"
        )
    elif provider == LLMProvider.OLLAMA:
        return OllamaTranslator(
            model=model or "llama3.2",
            server_url=server_url
        )
    else:
        raise ValueError(f"Unknown provider: {provider}")
