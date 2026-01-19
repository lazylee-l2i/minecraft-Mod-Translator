"""Tests for translator factory."""
import pytest

from src.core.translator import (
    create_translator,
    LLMProvider,
    OpenAITranslator,
    OpenRouterTranslator,
    OllamaTranslator,
)


class TestLLMProvider:
    """Tests for LLMProvider class."""
    
    def test_provider_constants(self):
        """Test provider constant values."""
        assert LLMProvider.OPENAI == "OpenAI GPT"
        assert LLMProvider.OPENROUTER == "OpenRouter"
        assert LLMProvider.OLLAMA == "Ollama (Local)"
    
    def test_all_providers(self):
        """Test all() returns all providers."""
        providers = LLMProvider.all()
        
        assert len(providers) == 3
        assert LLMProvider.OPENAI in providers
        assert LLMProvider.OPENROUTER in providers
        assert LLMProvider.OLLAMA in providers


class TestCreateTranslator:
    """Tests for create_translator factory function."""
    
    def test_create_openai_translator(self):
        """Test creating OpenAI translator."""
        translator = create_translator(
            provider=LLMProvider.OPENAI,
            api_key="test_key",
            model="gpt-4o"
        )
        
        assert isinstance(translator, OpenAITranslator)
        assert translator.model_name == "gpt-4o"
    
    def test_create_openrouter_translator(self):
        """Test creating OpenRouter translator."""
        translator = create_translator(
            provider=LLMProvider.OPENROUTER,
            api_key="test_key",
            model="openai/gpt-4o"
        )
        
        assert isinstance(translator, OpenRouterTranslator)
        assert translator.model_name == "openai/gpt-4o"
    
    def test_create_ollama_translator(self):
        """Test creating Ollama translator."""
        translator = create_translator(
            provider=LLMProvider.OLLAMA,
            model="llama3.2",
            server_url="http://localhost:11434"
        )
        
        assert isinstance(translator, OllamaTranslator)
        assert translator.model_name == "llama3.2"
    
    def test_default_models(self):
        """Test that default models are applied."""
        openai = create_translator(LLMProvider.OPENAI, api_key="key")
        assert openai.model_name == "gpt-4o"
        
        openrouter = create_translator(LLMProvider.OPENROUTER, api_key="key")
        assert openrouter.model_name == "openai/gpt-4o"
        
        ollama = create_translator(LLMProvider.OLLAMA)
        assert ollama.model_name == "llama3.2"
    
    def test_invalid_provider(self):
        """Test that invalid provider raises ValueError."""
        with pytest.raises(ValueError):
            create_translator("Invalid Provider")
