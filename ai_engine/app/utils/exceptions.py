"""
Custom exceptions for AI engine module.
"""


class AIEngineException(Exception):
    """Base exception for AI engine errors."""
    pass


class GeminiAPIError(AIEngineException):
    """Raised when Gemini API call fails."""
    pass


class InvalidPromptError(AIEngineException):
    """Raised when prompt generation fails."""
    pass


class ResponseParsingError(AIEngineException):
    """Raised when response parsing fails."""
    pass


class InvalidImageError(AIEngineException):
    """Raised when image processing fails."""
    pass
