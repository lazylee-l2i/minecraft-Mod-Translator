"""Tests for CacheManager."""
import json
import tempfile
from pathlib import Path

import pytest

from src.core.cache_manager import CacheManager


class TestCacheManager:
    """Tests for CacheManager class."""
    
    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def cache_manager(self, temp_cache_dir):
        """Create CacheManager with temp directory."""
        return CacheManager(cache_dir=temp_cache_dir)
    
    def test_get_cache_path(self, cache_manager, temp_cache_dir):
        """Test cache path generation."""
        path = cache_manager.get_cache_path("test_mod", "1.0.0")
        
        expected = temp_cache_dir / "test_mod" / "1.0.0" / "ko_kr.json"
        assert path == expected
    
    def test_save_and_get_translation(self, cache_manager):
        """Test saving and retrieving translation."""
        mod_id = "test_mod"
        version = "1.0.0"
        translation = {"test.key": "테스트 값"}
        
        # Save
        cache_manager.save_translation(mod_id, version, translation)
        
        # Retrieve
        result = cache_manager.get_cached_translation(mod_id, version)
        
        assert result == translation
    
    def test_cache_miss(self, cache_manager):
        """Test that cache miss returns None."""
        result = cache_manager.get_cached_translation("nonexistent", "1.0.0")
        assert result is None
    
    def test_has_cache(self, cache_manager):
        """Test has_cache method."""
        mod_id = "test_mod"
        version = "1.0.0"
        
        # Initially no cache
        assert not cache_manager.has_cache(mod_id, version)
        
        # After saving
        cache_manager.save_translation(mod_id, version, {"key": "value"})
        assert cache_manager.has_cache(mod_id, version)
    
    def test_clear_cache_specific_mod(self, cache_manager):
        """Test clearing cache for specific mod."""
        # Save translations for two mods
        cache_manager.save_translation("mod_a", "1.0", {"a": "A"})
        cache_manager.save_translation("mod_b", "1.0", {"b": "B"})
        
        # Clear only mod_a
        cache_manager.clear_cache("mod_a")
        
        # mod_a should be gone, mod_b should remain
        assert not cache_manager.has_cache("mod_a", "1.0")
        assert cache_manager.has_cache("mod_b", "1.0")
    
    def test_clear_all_cache(self, cache_manager):
        """Test clearing all cache."""
        # Save multiple translations
        cache_manager.save_translation("mod_a", "1.0", {"a": "A"})
        cache_manager.save_translation("mod_b", "1.0", {"b": "B"})
        
        # Clear all
        cache_manager.clear_cache()
        
        # Both should be gone
        assert not cache_manager.has_cache("mod_a", "1.0")
        assert not cache_manager.has_cache("mod_b", "1.0")
    
    def test_get_cached_mods(self, cache_manager):
        """Test get_cached_mods returns correct list."""
        cache_manager.save_translation("mod_a", "1.0", {"a": "A"})
        cache_manager.save_translation("mod_a", "2.0", {"a": "A2"})
        cache_manager.save_translation("mod_b", "1.0", {"b": "B"})
        
        cached = cache_manager.get_cached_mods()
        
        assert len(cached) == 3
        assert ("mod_a", "1.0") in cached
        assert ("mod_a", "2.0") in cached
        assert ("mod_b", "1.0") in cached
