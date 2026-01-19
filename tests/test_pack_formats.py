"""Tests for pack_formats module."""
import pytest

from src.config.pack_formats import get_pack_format, get_supported_versions


class TestGetPackFormat:
    """Tests for get_pack_format function."""
    
    def test_valid_versions(self):
        """Test that known versions return correct pack_format."""
        assert get_pack_format("1.21.4") == 46
        assert get_pack_format("1.21") == 34
        assert get_pack_format("1.20.1") == 15
        assert get_pack_format("1.19.4") == 13
        assert get_pack_format("1.18.2") == 8
    
    def test_invalid_version(self):
        """Test that unknown versions return None."""
        assert get_pack_format("1.0.0") is None
        assert get_pack_format("invalid") is None
        assert get_pack_format("") is None
    
    def test_minor_versions(self):
        """Test minor version variations."""
        # Same pack_format for related versions
        assert get_pack_format("1.21") == get_pack_format("1.21.1")
        assert get_pack_format("1.20") == get_pack_format("1.20.1")


class TestGetSupportedVersions:
    """Tests for get_supported_versions function."""
    
    def test_returns_list(self):
        """Test that function returns a list."""
        versions = get_supported_versions()
        assert isinstance(versions, list)
        assert len(versions) > 0
    
    def test_sorted_descending(self):
        """Test that versions are sorted newest first."""
        versions = get_supported_versions()
        # First version should be newer than last
        first = versions[0]
        last = versions[-1]
        
        first_parts = tuple(int(x) for x in first.split("."))
        last_parts = tuple(int(x) for x in last.split("."))
        
        assert first_parts > last_parts
    
    def test_all_versions_have_format(self):
        """Test that all returned versions have a pack_format."""
        versions = get_supported_versions()
        for version in versions:
            assert get_pack_format(version) is not None
