"""
AI Engine module for Physics Explanation System.
Provides interfaces for generating physics explanations and analyzing diagrams.
"""

from ai_engine.explanation_generator import PhysicsExplanationGenerator
from ai_engine.gemini_client import get_gemini_client, GeminiClient
from ai_engine.multimodal_handler import MultiModalHandler
from ai_engine.prompt_builder import build_physics_prompt
from ai_engine.response_parser import ResponseParser
from utils.exceptions import (
    AIEngineException,
    GeminiAPIError,
    InvalidPromptError,
    ResponseParsingError,
    InvalidImageError
)

__all__ = [
    "PhysicsExplanationGenerator",
    "get_gemini_client",
    "GeminiClient",
    "MultiModalHandler",
    "build_physics_prompt",
    "ResponseParser",
    "AIEngineException",
    "GeminiAPIError",
    "InvalidPromptError",
    "ResponseParsingError",
    "InvalidImageError",
]
