"""Model list fetching utilities for each LLM provider."""
from typing import List, Optional
import requests

from ..utils.logger import get_logger

logger = get_logger(__name__)


def fetch_ollama_models(server_url: str = "http://localhost:11434") -> List[str]:
    """
    Fetch available models from Ollama server.
    
    Args:
        server_url: Ollama server URL
        
    Returns:
        List of model names, empty list if failed
    """
    try:
        response = requests.get(
            f"{server_url.rstrip('/')}/api/tags",
            timeout=5
        )
        response.raise_for_status()
        
        models = response.json().get("models", [])
        model_names = [m.get("name", "") for m in models if m.get("name")]
        
        logger.info(f"Found {len(model_names)} Ollama models")
        return model_names
        
    except requests.exceptions.ConnectionError:
        logger.warning("Cannot connect to Ollama server")
        return []
    except Exception as e:
        logger.warning(f"Failed to fetch Ollama models: {e}")
        return []


def fetch_openai_models(api_key: str) -> List[str]:
    """
    Fetch available models from OpenAI API.
    
    Args:
        api_key: OpenAI API key
        
    Returns:
        List of model names suitable for chat, empty list if failed
    """
    if not api_key:
        return []
    
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        models = client.models.list()
        
        # Filter for GPT models suitable for chat
        chat_models = [
            m.id for m in models.data
            if m.id.startswith(("gpt-4", "gpt-3.5", "o1", "o3"))
            and "instruct" not in m.id.lower()
        ]
        
        # Sort by name
        chat_models.sort(reverse=True)
        
        logger.info(f"Found {len(chat_models)} OpenAI chat models")
        return chat_models
        
    except Exception as e:
        logger.warning(f"Failed to fetch OpenAI models: {e}")
        return []


def fetch_openrouter_models(api_key: str) -> List[str]:
    """
    Fetch available models from OpenRouter API.
    
    Args:
        api_key: OpenRouter API key
        
    Returns:
        List of model IDs, empty list if failed
    """
    if not api_key:
        return []
    
    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        response.raise_for_status()
        
        models = response.json().get("data", [])
        
        # Extract model IDs and sort by popularity/name
        model_ids = [m.get("id", "") for m in models if m.get("id")]
        
        # Prioritize popular models
        priority_prefixes = [
            "openai/gpt-4",
            "anthropic/claude",
            "google/gemini",
            "meta-llama/",
            "mistralai/",
        ]
        
        def model_sort_key(model_id: str) -> tuple:
            for i, prefix in enumerate(priority_prefixes):
                if model_id.startswith(prefix):
                    return (i, model_id)
            return (len(priority_prefixes), model_id)
        
        model_ids.sort(key=model_sort_key)
        
        logger.info(f"Found {len(model_ids)} OpenRouter models")
        return model_ids
        
    except Exception as e:
        logger.warning(f"Failed to fetch OpenRouter models: {e}")
        return []


# Common/recommended models as fallback
DEFAULT_MODELS = {
    "OpenAI GPT": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
    ],
    "OpenRouter": [
        "openai/gpt-4o",
        "openai/gpt-4o-mini",
        "anthropic/claude-3.5-sonnet",
        "anthropic/claude-3-opus",
        "google/gemini-pro-1.5",
        "meta-llama/llama-3.1-70b-instruct",
        "mistralai/mistral-large",
    ],
    "Ollama (Local)": [
        "llama3.2",
        "llama3.1",
        "qwen2.5",
        "mistral",
        "gemma2",
    ],
}


def get_default_models(provider: str) -> List[str]:
    """
    Get default/recommended models for a provider.
    
    Args:
        provider: Provider name
        
    Returns:
        List of recommended model names
    """
    return DEFAULT_MODELS.get(provider, [])
