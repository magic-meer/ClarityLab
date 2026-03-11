"""
Request schema definitions for API endpoints.
"""

from pydantic import BaseModel, field_validator, Field
from typing import Optional


class ExplanationRequest(BaseModel):
    """Request schema for explanation endpoint."""

    question: str = Field(..., min_length=5, max_length=1000, description="Question or concept to explain")
    model_name: Optional[str] = Field(None, description="Model to use for generation")

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "question": "Explain quantum tunneling and its applications"
            }
        }


class ImageAnalysisRequest(BaseModel):
    """Request schema for image analysis endpoint."""

    question: str = Field(..., min_length=5, max_length=500, description="Question about the image")
    context: Optional[str] = Field(None, max_length=500, description="Additional context")
    model_name: Optional[str] = Field(None, description="Model to use for image analysis")

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
                ]
            }
        }