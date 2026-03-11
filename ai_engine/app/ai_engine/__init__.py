"""
AI Engine module for ClarityLab Learning Agent.
Provides interfaces for generating explanations and analyzing uploaded materials.
"""

from ai_engine.explanation_generator import (
    ExplanationGenerator,
    PhysicsExplanationGenerator,
    generate_explanation,
    generate_physics_explanation
)
from ai_engine.gemini_client import get_gemini_client, GeminiClient
from ai_engine.multimodal_handler import MultiModalHandler
from ai_engine.prompt_builder import build_explanation_prompt, build_physics_prompt
from ai_engine.response_parser import ResponseParser
from utils.exceptions import (
    AIEngineException,
    GeminiAPIError,
    InvalidPromptError,
    ResponseParsingError,
    InvalidImageError
)

__all__ = [
    "ExplanationGenerator",
    "PhysicsExplanationGenerator",
    "generate_explanation",
    "generate_physics_explanation",
    "get_gemini_client",
    "GeminiClient",
    "MultiModalHandler",
    "build_explanation_prompt",
    "build_physics_prompt",
    "ResponseParser",
    "AIEngineException",
    "GeminiAPIError",
    "InvalidPromptError",
    "ResponseParsingError",
    "InvalidImageError",
]
