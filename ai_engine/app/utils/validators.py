"""
Input validation utilities for request/response handling.
"""

import logging
from typing import Optional
from pydantic import ValidationError, field_validator, BaseModel

from config.logger import setup_logger

logger = setup_logger(__name__)


class QuestionValidator(BaseModel):
    """Validator for physics questions."""
    
    question: str
    max_length: int = 1000
    
    @field_validator('question')
    @classmethod
    def validate_question(cls, v: str) -> str:
        """Validate question format and length."""
        if not v or not v.strip():
            raise ValueError("Question cannot be empty")
        
        if len(v) > 1000:
            raise ValueError(f"Question too long (max 1000 characters, got {len(v)})")
        
        if len(v) < 5:
            raise ValueError("Question too short (min 5 characters)")
        
        return v.strip()


class DifficultyValidator(BaseModel):
    """Validator for difficulty levels."""
    
    difficulty: str
    
    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        """Validate difficulty level."""
        valid_levels = {"beginner", "intermediate", "advanced", "expert"}
        level = v.lower().strip()
        
        if level not in valid_levels:
            raise ValueError(f"Invalid difficulty level. Must be one of: {valid_levels}")
        
        return level


def validate_request_input(
    question: str,
    difficulty: Optional[str] = "beginner"
) -> tuple[bool, Optional[str]]:
    """
    Validate request input parameters.
    
    Args:
        question: Physics question
        difficulty: Explanation difficulty
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        QuestionValidator(question=question)
        DifficultyValidator(difficulty=difficulty)
        return True, None
    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return False, str(e)


def sanitize_question(question: str) -> str:
    """
    Sanitize question input.
    
    Args:
        question: Raw question input
    
    Returns:
        Sanitized question
    """
    if not question:
        return ""
    
    # Remove extra whitespace
    question = " ".join(question.split())
    
    # Remove special characters that might cause issues
    # but keep alphanumeric, spaces, and basic punctuation
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 .,?!:;()[]{}-")
    
    question = "".join(c for c in question if c in allowed_chars or ord(c) > 127)
    
    return question.strip()
