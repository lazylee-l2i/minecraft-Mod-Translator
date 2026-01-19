"""OpenAI GPT translation engine."""
import json
from typing import Any, Dict

from .base import BaseTranslator
from ...utils.exceptions import TranslationError
from ...utils.logger import get_logger

logger = get_logger(__name__)


class OpenAITranslator(BaseTranslator):
    """
    Translator using OpenAI GPT API.
    
    Supports GPT-4o and other OpenAI models.
    """
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        """
        Initialize OpenAI translator.
        
        Args:
            api_key: OpenAI API key (memory only, not stored)
            model: Model name (default: gpt-4o)
        """
        super().__init__(api_key=api_key, model=model)
        
        try:
            import openai
            self._client = openai.OpenAI(api_key=api_key)
        except ImportError:
            raise TranslationError("openai package not installed. Run: pip install openai")
    
    def translate(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate using OpenAI GPT.
        
        Args:
            content: Dictionary containing en_us.json content
            
        Returns:
            Translated dictionary for ko_kr.json
        """
        logger.info(f"Translating with OpenAI {self._model}...")
        logger.debug(f"Content has {len(content)} entries")
        
        try:
            messages = self._build_system_messages()
            messages.append({
                "role": "user",
                "content": json.dumps(content, ensure_ascii=False, indent=2)
            })
            
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                temperature=0.3,  # 낮은 temperature로 일관된 번역
            )
            
            result = response.choices[0].message.content
            logger.debug(f"Received response of length {len(result)}")
            
            translated = self._parse_json_response(result)
            logger.info(f"Successfully translated {len(translated)} entries")
            
            return translated
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse translation response: {e}")
            raise TranslationError(f"Invalid JSON in response: {e}")
        except Exception as e:
            logger.error(f"OpenAI translation failed: {e}")
            raise TranslationError(f"OpenAI translation failed: {e}")
