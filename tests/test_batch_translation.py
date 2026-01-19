"""Tests for batch translation functionality."""
import pytest

from src.core.translator.base import BaseTranslator


class MockTranslator(BaseTranslator):
    """Mock translator for testing batch functionality."""
    
    def __init__(self, batch_size: int = 50):
        super().__init__(api_key="test", model="test", batch_size=batch_size)
        self.translate_calls = []
    
    def translate(self, content: dict) -> dict:
        """Mock translate that returns content with '[번역됨]' suffix."""
        self.translate_calls.append(content)
        return {k: f"{v} [번역됨]" for k, v in content.items()}


class TestBatchTranslation:
    """Tests for batched translation functionality."""
    
    def test_small_content_no_batching(self):
        """Test that small content is not batched."""
        translator = MockTranslator(batch_size=50)
        content = {f"key{i}": f"value{i}" for i in range(10)}
        
        result = translator.translate_batched(content)
        
        # Should be a single translate call
        assert len(translator.translate_calls) == 1
        assert len(result) == 10
    
    def test_large_content_is_batched(self):
        """Test that large content is split into batches."""
        translator = MockTranslator(batch_size=20)
        content = {f"key{i}": f"value{i}" for i in range(50)}
        
        result = translator.translate_batched(content)
        
        # Should be 3 batches: 20 + 20 + 10
        assert len(translator.translate_calls) == 3
        assert len(result) == 50
        
        # Verify batch sizes
        assert len(translator.translate_calls[0]) == 20
        assert len(translator.translate_calls[1]) == 20
        assert len(translator.translate_calls[2]) == 10
    
    def test_batching_preserves_all_content(self):
        """Test that all content is preserved after batching."""
        translator = MockTranslator(batch_size=10)
        content = {f"key{i}": f"value{i}" for i in range(25)}
        
        result = translator.translate_batched(content)
        
        # All keys should be present
        assert set(result.keys()) == set(content.keys())
        
        # All values should be translated
        for key in content:
            assert result[key] == f"{content[key]} [번역됨]"
    
    def test_batching_disabled(self):
        """Test that batching can be disabled with -1."""
        translator = MockTranslator(batch_size=-1)
        content = {f"key{i}": f"value{i}" for i in range(100)}
        
        result = translator.translate_batched(content)
        
        # Should be a single translate call even for large content
        assert len(translator.translate_calls) == 1
        assert len(result) == 100
    
    def test_batch_size_property(self):
        """Test batch_size getter and setter."""
        translator = MockTranslator(batch_size=50)
        
        assert translator.batch_size == 50
        
        translator.batch_size = 100
        assert translator.batch_size == 100
        
        # 0 should use default
        translator.batch_size = 0
        assert translator.batch_size == translator.DEFAULT_BATCH_SIZE
    
    def test_progress_callback(self):
        """Test that progress callback is called correctly."""
        translator = MockTranslator(batch_size=10)
        content = {f"key{i}": f"value{i}" for i in range(25)}
        
        callbacks = []
        def progress_cb(current, total):
            callbacks.append((current, total))
        
        translator.translate_batched(content, progress_callback=progress_cb)
        
        # Should have 3 callbacks for 3 batches
        assert len(callbacks) == 3
        assert callbacks == [(1, 3), (2, 3), (3, 3)]
    
    def test_split_dict_helper(self):
        """Test _split_dict helper method."""
        d = {f"key{i}": f"value{i}" for i in range(10)}
        
        chunks = list(BaseTranslator._split_dict(d, 3))
        
        assert len(chunks) == 4  # 3 + 3 + 3 + 1
        assert len(chunks[0]) == 3
        assert len(chunks[1]) == 3
        assert len(chunks[2]) == 3
        assert len(chunks[3]) == 1
        
        # All keys should be present across chunks
        all_keys = set()
        for chunk in chunks:
            all_keys.update(chunk.keys())
        assert all_keys == set(d.keys())
