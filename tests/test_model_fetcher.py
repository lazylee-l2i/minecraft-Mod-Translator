"""Tests for model fetcher functionality."""
import pytest

from src.core.model_fetcher import get_default_models, DEFAULT_MODELS


class TestModelFetcher:
    """Tests for model fetcher module."""
    
    def test_get_default_models_openai(self):
        """Test getting default OpenAI models."""
        models = get_default_models("OpenAI GPT")
        
        assert isinstance(models, list)
        assert len(models) > 0
        assert "gpt-4o" in models
    
    def test_get_default_models_openrouter(self):
        """Test getting default OpenRouter models."""
        models = get_default_models("OpenRouter")
        
        assert isinstance(models, list)
        assert len(models) > 0
        assert "openai/gpt-4o" in models
    
    def test_get_default_models_ollama(self):
        """Test getting default Ollama models."""
        models = get_default_models("Ollama (Local)")
        
        assert isinstance(models, list)
        assert len(models) > 0
        assert "llama3.2" in models
    
    def test_get_default_models_unknown_provider(self):
        """Test getting models for unknown provider returns empty list."""
        models = get_default_models("Unknown Provider")
        
        assert isinstance(models, list)
        assert len(models) == 0
    
    def test_default_models_structure(self):
        """Test DEFAULT_MODELS dictionary structure."""
        assert "OpenAI GPT" in DEFAULT_MODELS
        assert "OpenRouter" in DEFAULT_MODELS
        assert "Ollama (Local)" in DEFAULT_MODELS
        
        for provider, models in DEFAULT_MODELS.items():
            assert isinstance(models, list)
            assert len(models) > 0
            for model in models:
                assert isinstance(model, str)
                assert len(model) > 0
