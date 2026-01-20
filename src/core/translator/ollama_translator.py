"""Ollama (Local LLM) translation engine."""
import json
from typing import Any, Dict

import requests

from .base import BaseTranslator
from ...utils.exceptions import TranslationError
from ...utils.logger import get_logger

logger = get_logger(__name__)


class OllamaTranslator(BaseTranslator):
    """
    Translator using Ollama local LLM.
    
    Ollama runs LLMs locally, requiring no API key or internet connection.
    """
    
    DEFAULT_SERVER_URL = "http://localhost:11434"
    REQUEST_TIMEOUT = 600  # 10 minutes for large translations
    
    def __init__(
        self, 
        model: str = "llama3.2", 
        server_url: str = "",
        **kwargs
    ):
        """
        Initialize Ollama translator.
        
        Args:
            model: Model name (e.g., "llama3.2", "mistral", "qwen2.5")
            server_url: Ollama server URL (default: http://localhost:11434)
        """
        super().__init__(api_key="", model=model)
        self._server_url = (server_url or self.DEFAULT_SERVER_URL).rstrip("/")
    
    def get_system_prompt(self) -> str:
        """
        Get simplified system prompt for local LLMs.
        
        Local LLMs have limited capacity, so we use a simpler prompt
        that's easier to understand and follow.
        
        Returns:
            Simple system prompt string
        """
        return self.SIMPLE_SYSTEM_PROMPT
    
    def translate(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate using Ollama.
        
        Args:
            content: Dictionary containing en_us.json content
            
        Returns:
            Translated dictionary for ko_kr.json
        """
        logger.info(f"Translating with Ollama {self._model}...")
        logger.debug(f"Content has {len(content)} entries")
        logger.debug(f"Server URL: {self._server_url}")
        
        try:
            # Check if Ollama server is running
            self._check_server_connection()
            
            # Build prompt - use simplified prompt for local LLMs
            system_prompt = self.get_system_prompt()
            user_content = json.dumps(content, ensure_ascii=False, indent=2)
            
            # Make request
            response = requests.post(
                f"{self._server_url}/api/generate",
                json={
                    "model": self._model,
                    "prompt": f"{system_prompt}\n\n입력:\n{user_content}",
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.3,
                    }
                },
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            result = response.json().get("response", "")
            logger.debug(f"Received response of length {len(result)}")
            
            translated = self._parse_json_response(result)
            logger.info(f"Successfully translated {len(translated)} entries")
            
            return translated
            
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama server")
            raise TranslationError(
                f"Cannot connect to Ollama server at {self._server_url}. "
                "Make sure Ollama is running."
            )
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            raise TranslationError("Translation request timed out")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse translation response: {e}")
            raise TranslationError(f"Invalid JSON in response: {e}")
        except Exception as e:
            logger.error(f"Ollama translation failed: {e}")
            raise TranslationError(f"Ollama translation failed: {e}")
    
    def _check_server_connection(self) -> None:
        """Check if Ollama server is accessible."""
        try:
            response = requests.get(
                f"{self._server_url}/api/tags",
                timeout=5
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise TranslationError(
                f"Cannot connect to Ollama server: {e}"
            )
    
    def get_available_models(self) -> list[str]:
        """
        Get list of available models on the Ollama server.
        
        Returns:
            List of model names
        """
        try:
            response = requests.get(
                f"{self._server_url}/api/tags",
                timeout=10
            )
            response.raise_for_status()
            
            models = response.json().get("models", [])
            return [m.get("name", "") for m in models if m.get("name")]
            
        except Exception as e:
            logger.warning(f"Failed to get Ollama models: {e}")
            return []
