"""Custom exceptions for the application."""


class ModTranslatorError(Exception):
    """Base exception for all application errors."""
    pass


class JarExtractionError(ModTranslatorError):
    """Raised when JAR extraction fails."""
    pass


class TranslationError(ModTranslatorError):
    """Raised when translation fails."""
    pass


class ResourcePackError(ModTranslatorError):
    """Raised when resource pack generation fails."""
    pass


class ConfigurationError(ModTranslatorError):
    """Raised when configuration is invalid."""
    pass


class CacheError(ModTranslatorError):
    """Raised when cache operation fails."""
    pass
