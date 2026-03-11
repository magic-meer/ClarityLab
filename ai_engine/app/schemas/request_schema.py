"""
Request schema definitions for API endpoints.
"""

from pydantic import BaseModel, field_validator, Field
from typing import Optional


class ExplanationRequest(BaseModel):
    """Request schema for explanation endpoint."""

    question: str = Field(..., min_length=5, max_length=1000, description="Question or concept to explain")
    difficulty: Optional[str] = Field(
        default="beginner",
        description="Difficulty level: beginner, intermediate, advanced, or expert"
    )

    @field_validator('difficulty')
    @classmethod
    def validate_difficulty(cls, v: str) -> str:
        """Validate difficulty level."""
        valid_levels = {"beginner", "intermediate", "advanced", "expert"}
        level = v.lower().strip()

        if level not in valid_levels:
            raise ValueError(f"Difficulty must be one of: {', '.join(valid_levels)}")

        return level

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "question": "Explain quantum tunneling and its applications",
                "difficulty": "intermediate"
            }
        }


class ImageAnalysisRequest(BaseModel):
    """Request schema for image analysis endpoint."""

    question: str = Field(..., min_length=5, max_length=500, description="Question about the image")
    context: Optional[str] = Field(None, max_length=500, description="Additional context")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "question": "Explain the concepts shown in this diagram",
                "context": "This is from Chapter 5"
            }
        }


class BulkExplanationRequest(BaseModel):
    """Request schema for bulk explanation endpoint."""

    questions: list[str] = Field(..., max_length=10, description="List of questions")
    difficulty: Optional[str] = Field(default="beginner", description="Difficulty level")

    @field_validator('questions')
    @classmethod
    def validate_questions(cls, v: list[str]) -> list[str]:
        """Validate question list."""
        if not v:
            raise ValueError("At least one question required")

        if len(v) > 10:
            raise ValueError("Maximum 10 questions allowed")

        for q in v:
            if not q or len(q) < 5:
                raise ValueError("Each question must be at least 5 characters")

        return v

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "questions": [
                    "What is Newton's first law of motion?",
                    "Explain gravitational force"
                ],
                "difficulty": "beginner"
            }
        }