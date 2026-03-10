"""
Response schema definitions for API endpoints.
Defines the structure of responses returned by the API.
"""

from pydantic import BaseModel, Field
from typing import List


class ExplanationResponse(BaseModel):
    """Response schema for physics explanation endpoint.
    
    Represents a complete structured physics explanation with all components.
    """
    
    topic: str = Field(..., description="The physics topic or concept explained")
    difficulty: str = Field(..., description="Difficulty level: beginner, intermediate, advanced, or expert")
    explanation: str = Field(..., description="The main explanation text")
    key_points: List[str] = Field(..., description="List of important concepts and learning points")
    diagram_prompt: str = Field(..., description="Prompt for generating visual diagrams")
    animation_prompt: str = Field(..., description="Prompt for creating animations")
    simulation_prompt: str = Field(..., description="Prompt for interactive simulations")
    narration_script: str = Field(..., description="Script for narration or voiceover")
    follow_up_questions: List[str] = Field(..., description="Questions to deepen understanding")
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "topic": "Newton's Laws of Motion",
                "difficulty": "beginner",
                "explanation": "Newton's first law states that an object at rest stays at rest...",
                "key_points": ["Inertia", "Force", "Acceleration"],
                "diagram_prompt": "Create a diagram showing...",
                "animation_prompt": "Animate an object moving...",
                "simulation_prompt": "Create a simulation where users can adjust...",
                "narration_script": "In this explanation, we'll explore...",
                "follow_up_questions": ["What if there were no friction?"]
            }
        }