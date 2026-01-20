"""Abstract base class for translation engines."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Callable, Iterator

from ...utils.logger import get_logger

logger = get_logger(__name__)


class BaseTranslator(ABC):
    """
    Abstract base class for all translation engines.
    
    All LLM-based translators should inherit from this class
    and implement the translate() method.
    
    Supports batch processing for large JSON files to optimize
    memory usage for local LLMs with limited VRAM.
    """
    
    # Detailed system prompt for cloud APIs (OpenAI, OpenRouter)
    SYSTEM_PROMPT = """You are a professional game translator specializing in Minecraft.

TASK: Translate the JSON values into Korean. Keep all JSON keys unchanged.

RULES:
1. Translate ONLY the values, never modify the keys.
2. Translate ALL values into Korean, regardless of the source language (English, Portuguese, etc.).
3. Even if the text looks simple or is a proper noun, translate it to Korean if possible (e.g., "Iron Sword" -> "철 검").
4. Keep special formatting: %s, %d, %1$s, %2$d, etc.
5. Keep Minecraft formatting codes: §a, §b, §l, §r, etc.
6. Keep HTML-like tags: <b>, </b>, <i>, etc.
7. Keep placeholders in curly braces: {item}, {player}, etc.
8. Use appropriate Korean gaming terminology.

EXAMPLE INPUT:
{"item.sword": "Iron Sword", "tooltip.durability": "%d/%d Durability", "message.error": "Erro no sistema"}

EXAMPLE OUTPUT:
{"item.sword": "철 검", "tooltip.durability": "%d/%d 내구도", "message.error": "시스템 오류"}

RESPOND WITH ONLY THE TRANSLATED JSON. No explanations, no markdown code blocks."""
    
    # Simple system prompt for local LLMs (Ollama) - optimized for smaller models
    SIMPLE_SYSTEM_PROMPT = """Translate JSON values to Korean. Keep keys unchanged.

Rules:
- Translate values only, keep keys as-is
- Keep: %s, %d, §a, §b, {item}, <b> etc.

Input: {"item.sword": "Iron Sword"}
Output: {"item.sword": "철 검"}

Return JSON only."""
    
    # Default batch size (number of entries per batch)
    DEFAULT_BATCH_SIZE = 50
    
    def __init__(self, api_key: str = "", model: str = "", batch_size: int = 0, **kwargs):
        """
        Initialize translator.
        
        Args:
            api_key: API key (not stored to disk, memory only)
            model: Model name to use
            batch_size: Number of entries per batch (0 = auto, -1 = no batching)
            **kwargs: Additional provider-specific options
        """
        self._api_key = api_key  # 메모리에만 저장, 파일에 저장하지 않음
        self._model = model
        self._batch_size = batch_size if batch_size != 0 else self.DEFAULT_BATCH_SIZE
    
    @abstractmethod
    def translate(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate JSON content from English to Korean.
        
        Args:
            content: Dictionary containing en_us.json content
            
        Returns:
            Translated dictionary for ko_kr.json
            
        Raises:
            TranslationError: If translation fails
        """
        pass
    
    @property
    def provider_name(self) -> str:
        """Return the provider name for logging."""
        return self.__class__.__name__
    
    @property
    def model_name(self) -> str:
        """Return the model name being used."""
        return self._model
    
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for translation.
        
        Subclasses can override this to use a different prompt.
        Local LLMs should override to return SIMPLE_SYSTEM_PROMPT.
        
        Returns:
            System prompt string
        """
        return self.SYSTEM_PROMPT
    
    def _build_system_messages(self) -> list[dict]:
        """Build system message list for API calls."""
        return [{"role": "system", "content": self.get_system_prompt()}]
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """
        Parse JSON from LLM response, handling markdown code blocks.
        
        Args:
            response: Raw response string from LLM
            
        Returns:
            Parsed JSON dictionary
        """
        import json
        
        text = response.strip()
        
        # Remove markdown code block if present
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first line (```json or ```)
            lines = lines[1:]
            # Remove last line (```)
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)
        
        return json.loads(text.strip())
    
    def translate_batched(
        self,
        content: Dict[str, Any],
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, Any]:
        """
        Translate large JSON content in batches.
        
        Splits the content into smaller chunks to reduce memory usage
        and prevent timeout issues with large language files.
        
        Args:
            content: Dictionary containing en_us.json content
            progress_callback: Optional callback(current_batch, total_batches)
            
        Returns:
            Merged translated dictionary for ko_kr.json
        """
        total_entries = len(content)
        
        # If content is small enough or batching is disabled, translate directly
        if self._batch_size < 0 or total_entries <= self._batch_size:
            logger.debug(f"Translating directly ({total_entries} entries)")
            return self.translate(content)
        
        logger.info(
            f"Batched translation: {total_entries} entries in "
            f"~{(total_entries + self._batch_size - 1) // self._batch_size} batches"
        )
        
        # Split into batches and translate
        result: Dict[str, Any] = {}
        batches = list(self._split_dict(content, self._batch_size))
        total_batches = len(batches)
        
        for i, batch in enumerate(batches):
            batch_num = i + 1
            logger.info(f"Processing batch {batch_num}/{total_batches} ({len(batch)} entries)")
            
            if progress_callback:
                progress_callback(batch_num, total_batches)
            
            try:
                translated_batch = self.translate(batch)
                result.update(translated_batch)
            except Exception as e:
                logger.error(f"Batch {batch_num} failed: {e}")
                # Continue with remaining batches, use original for failed ones
                logger.warning(f"Using original text for {len(batch)} failed entries")
                result.update(batch)
        
        logger.info(f"Batched translation complete: {len(result)} entries")
        return result
    
    @staticmethod
    def _split_dict(d: Dict[str, Any], chunk_size: int) -> Iterator[Dict[str, Any]]:
        """
        Split a dictionary into chunks of specified size.
        
        Args:
            d: Dictionary to split
            chunk_size: Maximum entries per chunk
            
        Yields:
            Dictionary chunks
        """
        items = list(d.items())
        for i in range(0, len(items), chunk_size):
            yield dict(items[i:i + chunk_size])
    
    @property
    def batch_size(self) -> int:
        """Get current batch size."""
        return self._batch_size
    
    @batch_size.setter
    def batch_size(self, value: int) -> None:
        """Set batch size. Use -1 to disable batching."""
        self._batch_size = value if value != 0 else self.DEFAULT_BATCH_SIZE
