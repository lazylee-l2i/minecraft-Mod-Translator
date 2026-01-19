"""Translation cache manager for reusing previous translations."""
import json
import shutil
from pathlib import Path
from typing import Any, Dict, Optional

from ..config.constants import TRANSLATE_CACHE_DIR
from ..utils.logger import get_logger
from ..utils.exceptions import CacheError

logger = get_logger(__name__)


class CacheManager:
    """
    Manages translation cache.
    
    Cache structure:
        translate_cache/
        └── {mod_id}/
            └── {mod_version}/
                └── ko_kr.json
    
    This allows reusing translations when the same mod version
    is encountered again, saving API costs and time.
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Custom cache directory (default: translate_cache/)
        """
        self._cache_dir = cache_dir or TRANSLATE_CACHE_DIR
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Cache directory: {self._cache_dir}")
    
    def get_cache_path(self, mod_id: str, mod_version: str) -> Path:
        """
        Get the cache file path for a mod.
        
        Args:
            mod_id: Mod identifier
            mod_version: Mod version string
            
        Returns:
            Path to the cache file
        """
        # Sanitize version string for filesystem
        safe_version = mod_version.replace("/", "_").replace("\\", "_")
        return self._cache_dir / mod_id / safe_version / "ko_kr.json"
    
    def get_cached_translation(
        self, 
        mod_id: str, 
        mod_version: str
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve cached translation if exists.
        
        Args:
            mod_id: Mod identifier
            mod_version: Mod version string
            
        Returns:
            Cached translation dict or None if not found
        """
        cache_path = self.get_cache_path(mod_id, mod_version)
        
        if cache_path.exists():
            try:
                with cache_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    logger.info(f"✓ Cache hit: {mod_id} v{mod_version}")
                    return data
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to read cache for {mod_id}: {e}")
                return None
        
        logger.info(f"✗ Cache miss: {mod_id} v{mod_version}")
        return None
    
    def save_translation(
        self,
        mod_id: str,
        mod_version: str,
        translation: Dict[str, Any]
    ) -> Path:
        """
        Save translation to cache.
        
        Args:
            mod_id: Mod identifier
            mod_version: Mod version string
            translation: Translated content
            
        Returns:
            Path to cached file
        """
        cache_path = self.get_cache_path(mod_id, mod_version)
        
        try:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            with cache_path.open("w", encoding="utf-8") as f:
                json.dump(translation, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Translation cached: {mod_id} v{mod_version}")
            return cache_path
            
        except IOError as e:
            logger.error(f"Failed to save cache for {mod_id}: {e}")
            raise CacheError(f"Failed to save cache: {e}")
    
    def has_cache(self, mod_id: str, mod_version: str) -> bool:
        """
        Check if cache exists for a mod.
        
        Args:
            mod_id: Mod identifier
            mod_version: Mod version string
            
        Returns:
            True if cache exists
        """
        return self.get_cache_path(mod_id, mod_version).exists()
    
    def get_cached_mods(self) -> list[tuple[str, str]]:
        """
        Get list of all cached mods.
        
        Returns:
            List of (mod_id, version) tuples
        """
        cached = []
        
        if not self._cache_dir.exists():
            return cached
        
        for mod_dir in self._cache_dir.iterdir():
            if mod_dir.is_dir():
                for version_dir in mod_dir.iterdir():
                    if version_dir.is_dir() and (version_dir / "ko_kr.json").exists():
                        cached.append((mod_dir.name, version_dir.name))
        
        return cached
    
    def clear_cache(self, mod_id: Optional[str] = None) -> int:
        """
        Clear cache for a specific mod or all mods.
        
        Args:
            mod_id: Specific mod to clear, or None for all
            
        Returns:
            Number of cache entries cleared
        """
        count = 0
        
        try:
            if mod_id:
                mod_cache = self._cache_dir / mod_id
                if mod_cache.exists():
                    # Count versions before deleting
                    count = sum(1 for _ in mod_cache.glob("*/ko_kr.json"))
                    shutil.rmtree(mod_cache)
                    logger.info(f"Cache cleared for {mod_id}: {count} version(s)")
            else:
                # Clear all
                for mod_dir in self._cache_dir.iterdir():
                    if mod_dir.is_dir():
                        count += sum(1 for _ in mod_dir.glob("*/ko_kr.json"))
                        shutil.rmtree(mod_dir)
                logger.info(f"All cache cleared: {count} entry(ies)")
            
            return count
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            raise CacheError(f"Failed to clear cache: {e}")
    
    def get_cache_size(self) -> int:
        """
        Get total size of cache in bytes.
        
        Returns:
            Total cache size in bytes
        """
        total = 0
        for cache_file in self._cache_dir.rglob("*.json"):
            total += cache_file.stat().st_size
        return total
