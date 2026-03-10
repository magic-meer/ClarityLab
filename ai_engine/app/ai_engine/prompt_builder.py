"""
Prompt building module for constructing optimized prompts for Gemini.
"""

import logging
from typing import Optional
from config.logger import setup_logger
from utils.exceptions import InvalidPromptError

logger = setup_logger(__name__)

# Difficulty level templates
DIFFICULTY_LEVELS = {
    "beginner": "a beginner-level student (high school)",
    "intermediate": "an intermediate-level student (early undergraduate)",
    "advanced": "an advanced student (upper-level undergraduate or graduate)",
    "expert": "an expert-level audience"
}

JSON_FORMAT_TEMPLATE = """{
 "topic": "",
 "difficulty": "",
 "explanation": "",
 "key_points": [],
 "diagram_prompt": "",
 "animation_prompt": "",
 "simulation_prompt": "",
 "narration_script": "",
 "follow_up_questions": []
}"""


def build_physics_prompt(
    question: str,
    difficulty: str = "beginner",
    include_diagram: bool = True,
    include_animation: bool = True,
    include_simulation: bool = True
) -> str:
    """
    Build optimized prompt for physics explanation.
    
    Args:
        question: Physics concept or question to explain
        difficulty: Level of explanation (beginner, intermediate, advanced, expert)
        include_diagram: Whether to include diagram prompt
        include_animation: Whether to include animation prompt
        include_simulation: Whether to include simulation prompt
    
    Returns:
        Optimized prompt string
    
    Raises:
        InvalidPromptError: If inputs are invalid
    """
    if not question or not question.strip():
        raise InvalidPromptError("Question cannot be empty")
    
    if difficulty not in DIFFICULTY_LEVELS:
        logger.warning(f"Unknown difficulty level: {difficulty}, defaulting to beginner")
        difficulty = "beginner"
    
    difficulty_desc = DIFFICULTY_LEVELS[difficulty]
    
    prompt = f"""You are an expert physics tutor with exceptional ability to explain complex concepts clearly and accurately.

Your task: Explain the following physics concept for {difficulty_desc}.

Provide a comprehensive, well-structured explanation that includes:

1. **Simple Explanation**: A clear, concise explanation using everyday language and analogies
2. **Key Learning Points**: 3-5 important concepts the student should understand
3. **Diagram Description**: Detailed prompt for generating a visual diagram
4. **Animation Description**: Detailed prompt for an animated visualization
5. **Simulation Idea**: Concept for an interactive simulation to reinforce learning
6. **Narration Script**: A clear narration script (2-3 sentences) for the explanation
7. **Follow-up Questions**: 2-3 thought-provoking questions to deepen understanding

IMPORTANT: Return your response STRICTLY as valid JSON with no additional text or markdown.

Expected JSON format:
{JSON_FORMAT_TEMPLATE}

Physics Concept/Question:
{question.strip()}

Generate the response now:"""
    
    logger.debug(f"Prompt built for question: {question[:50]}... (difficulty: {difficulty})")
    return prompt


def build_image_analysis_prompt(
    question: str,
    context: Optional[str] = None
) -> str:
    """
    Build prompt for analyzing physics diagrams/images.
    
    Args:
        question: Question about the image
        context: Additional context about the image
    
    Returns:
        Prompt for image analysis
    
    Raises:
        InvalidPromptError: If inputs are invalid
    """
    if not question or not question.strip():
        raise InvalidPromptError("Question cannot be empty")
    
    context_str = f"\nAdditional context: {context}" if context else ""
    
    prompt = f"""You are an expert physics educator analyzing a physics diagram or concept image.

Please analyze the image and answer the following question:

{question.strip()}{context_str}

Provide a detailed, educational explanation that:
1. Identifies key elements in the image
2. Explains physics concepts shown
3. Answers the specific question
4. Identifies any misconceptions a student might have
5. Suggests follow-up learning topics

Format your response as a clear, structured explanation."""
    
    logger.debug(f"Image analysis prompt built for question: {question[:50]}...")
    return prompt


def validate_prompt(prompt: str, min_length: int = 10) -> bool:
    """
    Validate that a prompt meets minimum requirements.
    
    Args:
        prompt: Prompt to validate
        min_length: Minimum prompt length
    
    Returns:
        True if valid
    
    Raises:
        InvalidPromptError: If validation fails
    """
    if not prompt or not prompt.strip():
        raise InvalidPromptError("Prompt cannot be empty")
    
    if len(prompt) < min_length:
        raise InvalidPromptError(f"Prompt too short (min {min_length} characters)")
    
    return True