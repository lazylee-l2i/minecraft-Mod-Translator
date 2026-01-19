"""Data models for translation workflow."""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict


@dataclass
class LanguageFile:
    """
    Represents an extracted language file from a mod.
    
    Attributes:
        mod_id: Mod identifier from assets path
        content: Original JSON content (en_us.json)
        original_path: Path within the JAR file
    """
    mod_id: str
    content: Dict[str, Any]
    original_path: Path


@dataclass
class TranslationResult:
    """
    Represents a completed translation.
    
    Attributes:
        mod_id: Mod identifier
        mod_version: Mod version string
        original_content: Original en_us.json content
        translated_content: Translated ko_kr.json content
        from_cache: Whether this was loaded from cache
    """
    mod_id: str
    mod_version: str
    original_content: Dict[str, Any]
    translated_content: Dict[str, Any]
    from_cache: bool = False
    
    @property
    def lang_path(self) -> str:
        """
        Get the resource pack path for this translation.
        
        Returns:
            Path string like "assets/{mod_id}/lang/ko_kr.json"
        """
        return f"assets/{self.mod_id}/lang/ko_kr.json"
    
    @property
    def entry_count(self) -> int:
        """Get the number of translated entries."""
        return len(self.translated_content)


@dataclass
class TranslationProgress:
    """
    Tracks translation progress for UI updates.
    
    Attributes:
        total_mods: Total number of mods to process
        current_mod_index: Current mod being processed (0-based)
        current_mod_name: Name of the current mod
        status: Current status message
        is_complete: Whether translation is complete
        error: Error message if any
    """
    total_mods: int = 0
    current_mod_index: int = 0
    current_mod_name: str = ""
    status: str = "대기 중..."
    is_complete: bool = False
    error: str = ""
    
    @property
    def progress_percent(self) -> float:
        """Calculate progress percentage."""
        if self.total_mods == 0:
            return 0.0
        return (self.current_mod_index / self.total_mods) * 100
