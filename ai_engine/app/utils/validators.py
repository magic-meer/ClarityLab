"""
Input validation utilities for request/response handling.
"""

import logging
from typing import Optional
from pydantic import ValidationError, field_validator, BaseModel

from config.logger import setup_logger

logger = setup_logger(__name__)


class QuestionValidator(BaseModel):
    """Validator for questions."""
    
    question: str
    max_length: int = 5000
    
    @field_validator('question')
    @classmethod
    def validate_question(cls, v: str) -> str:
        """Validate question format and length."""
        if not v or not v.strip():
            raise ValueError("Question cannot be empty")
        
        if len(v) > 5000:
            raise ValueError(f"Question too long (max 5000 characters, got {len(v)})")
        
        if len(v) < 5:
            raise ValueError("Question too short (min 5 characters)")
        
        return v.strip()


def validate_request_input(
    question: str,
    **kwargs
) -> tuple[bool, Optional[str]]:
    """
    Validate request input parameters.
    
    Args:
        question: Question to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        QuestionValidator(question=question)
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
