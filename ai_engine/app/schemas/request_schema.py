"""
Request schema definitions for API endpoints.
"""

from pydantic import BaseModel, field_validator, Field
from typing import Optional


class ExplanationRequest(BaseModel):
    """Request schema for explanation endpoint."""

    question: str = Field(
        ..., min_length=5, max_length=1000, description="Question or concept to explain"
    )
    model_name: Optional[str] = Field(None, description="Model to use for generation")
    difficulty: Optional[str] = Field(
        "auto",
        description="Difficulty level: auto, beginner, intermediate, advanced, expert",
    )
    generate_diagram: bool = Field(
        True, description="Whether to allow diagram generation"
    )
    generate_image: bool = Field(True, description="Whether to allow image generation")
    generate_audio: bool = Field(
        True, description="Whether to allow audio narration generation"
    )
    generate_video: bool = Field(True, description="Whether to allow video generation")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {"question": "Explain quantum tunneling and its applications"}
        }


class ImageGenerationRequest(BaseModel):
    """Request schema for image generation endpoint."""

    prompt: str = Field(
        ..., min_length=5, max_length=1000, description="Prompt to generate image from"
    )
    model_name: Optional[str] = Field(
        "imagen-3.0-generate-001", description="Model to use for generation"
    )

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "prompt": "A simple red apple on a white background, low detail"
            }
        }


class ImageAnalysisRequest(BaseModel):
    """Request schema for image analysis endpoint."""

    question: str = Field(
        ..., min_length=5, max_length=500, description="Question about the image"
    )
    context: Optional[str] = Field(
        None, max_length=500, description="Additional context"
    )
    model_name: Optional[str] = Field(
        None, description="Model to use for image analysis"
    )
    difficulty: Optional[str] = Field(
        "auto",
        description="Difficulty level: auto, beginner, intermediate, advanced, expert",
    )
    generate_diagram: bool = Field(
        True, description="Whether to allow diagram generation"
    )
    generate_image: bool = Field(True, description="Whether to allow image generation")
    generate_audio: bool = Field(
        True, description="Whether to allow audio narration generation"
    )
    generate_video: bool = Field(True, description="Whether to allow video generation")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "question": "Explain the concepts shown in this diagram",
                "context": "This is from Chapter 5",
            }
        }


class BulkExplanationRequest(BaseModel):
    """Request schema for bulk explanation endpoint."""

    questions: list[str] = Field(..., max_length=10, description="List of questions")

    @field_validator("questions")
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
                    "Explain gravitational force",
                ]
            }
        }


class AssetGenerationRequest(BaseModel):
    """Request schema for granular asset generation (from plan prompts)."""

    prompt: str = Field(..., description="Prompt for the specific asset")
    model_name: Optional[str] = Field(None, description="Model override")

    class Config:
        """Pydantic config."""

        json_schema_extra = {
            "example": {
                "prompt": "Explain the concept of neural networks in simple terms"
            }
        }
