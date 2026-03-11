"""
Main module for generating explanations on any topic.
Orchestrates prompt building, API calls, and response parsing.
"""

import logging
from typing import Dict, Any, Optional
from config.logger import setup_logger
from utils.exceptions import (
    AIEngineException,
    InvalidPromptError,
    ResponseParsingError
)
from ai_engine.prompt_builder import build_explanation_prompt, validate_prompt
from ai_engine.gemini_client import get_gemini_client
from ai_engine.response_parser import ResponseParser

logger = setup_logger(__name__)


class ExplanationGenerator:
    """Generate structured explanations using AI."""

    def __init__(self):
        """Initialize the explanation generator."""
        self.client = get_gemini_client()
        self.parser = ResponseParser()
        logger.debug("ExplanationGenerator initialized")

    def generate_explanation(
        self,
        question: str,
        difficulty: str = "beginner",
        include_diagram: bool = True,
        include_animation: bool = True,
        include_simulation: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a complete explanation.

        Args:
            question: Concept or question
            difficulty: Explanation difficulty level
            include_diagram: Include diagram prompt
            include_animation: Include animation prompt
            include_simulation: Include simulation prompt

        Returns:
            Dictionary with structured explanation

        Raises:
            InvalidPromptError: If input is invalid
            ResponseParsingError: If response parsing fails
            AIEngineException: For other errors
        """
        try:
            # Validate input
            if not question or not question.strip():
                raise InvalidPromptError("Question cannot be empty")

            logger.info(f"Generating explanation for: {question[:50]}...")

            # Build optimized prompt
            prompt = build_explanation_prompt(
                question=question,
                difficulty=difficulty,
                include_diagram=include_diagram,
                include_animation=include_animation,
                include_simulation=include_simulation
            )
            validate_prompt(prompt)

            # Get response from Gemini
            logger.debug("Sending request to Gemini API")
            response_text = self.client.generate_content(prompt)

            # Parse and validate response
            logger.debug("Parsing response")
            parsed_response = self.parser.parse_json_response(response_text)
            self.parser.validate_explanation_response(parsed_response)

            logger.info("Explanation generated successfully")
            return {
                "status": "success",
                "data": parsed_response
            }

        except InvalidPromptError as e:
            logger.error(f"Invalid prompt: {e}")
            return {
                "status": "error",
                "error": "Invalid input",
                "message": str(e)
            }

        except ResponseParsingError as e:
            logger.error(f"Response parsing failed: {e}")
            return {
                "status": "error",
                "error": "Response parsing failed",
                "message": str(e)
            }

        except AIEngineException as e:
            logger.error(f"AI engine error: {e}")
            return {
                "status": "error",
                "error": "AI processing error",
                "message": str(e)
            }

        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return {
                "status": "error",
                "error": "Unexpected error",
                "message": "An unexpected error occurred"
            }

    def generate_bulk_explanations(
        self,
        questions: list[str],
        difficulty: str = "beginner"
    ) -> list[Dict[str, Any]]:
        """
        Generate explanations for multiple questions.

        Args:
            questions: List of questions
            difficulty: Explanation difficulty level

        Returns:
            List of explanations
        """
        results = []
        for i, question in enumerate(questions, 1):
            logger.debug(f"Processing question {i}/{len(questions)}")
            result = self.generate_explanation(question, difficulty)
            results.append(result)

        return results


# Backward-compatible alias
PhysicsExplanationGenerator = ExplanationGenerator


# Convenience function
def generate_explanation(
    question: str,
    difficulty: str = "beginner"
) -> Dict[str, Any]:
    """
    Generate an explanation (convenience function).

    Args:
        question: Question
        difficulty: Explanation difficulty

    Returns:
        Explanation result dictionary
    """
    generator = ExplanationGenerator()
    return generator.generate_explanation(question, difficulty)


# Backward-compatible alias
generate_physics_explanation = generate_explanation