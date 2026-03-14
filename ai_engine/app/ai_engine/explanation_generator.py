"""
Main module for generating explanations on any topic.
Orchestrates prompt building, API calls, and response parsing.
"""

import logging
from typing import Dict, Any, Optional
from config.logger import setup_logger
from utils.exceptions import AIEngineException, InvalidPromptError, ResponseParsingError
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
        model_name: Optional[str] = None,
        difficulty: str = "auto",
        generate_diagram: bool = True,
        generate_image: bool = True,
        generate_audio: bool = True,
        generate_video: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate a complete explanation.

        Args:
            question: Concept or question
            model_name: Optional override for the model to use
            difficulty: Difficulty level
            generate_diagram: Allow diagram generation
            generate_image: Allow image generation
            generate_audio: Allow audio generation
            generate_video: Allow video generation

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

            # Build optimized prompt (AI decides difficulty and outputs)
            prompt = build_explanation_prompt(
                question=question,
                difficulty=difficulty,
                generate_diagram=generate_diagram,
                generate_image=generate_image,
                generate_audio=generate_audio,
                generate_video=generate_video,
            )
            validate_prompt(prompt)

            # Get response from Gemini
            logger.debug("Sending request to Gemini API")
            response_data = self.client.generate_content(prompt, model_name=model_name)

            # Log raw response for debugging
            raw_text = response_data.get("text", "")
            logger.info(f"Raw model response (first 500 chars): {raw_text[:500]}")

            # Parse and validate response
            logger.debug("Parsing response")
            parsed_response = self.parser.parse_json_response(raw_text)
            self.parser.validate_explanation_response(parsed_response)

            # Attach usage
            parsed_response["usage"] = response_data.get("usage", {})

            # If an image_prompt was provided and is not empty, generate the image
            image_prompt = parsed_response.get("image_prompt")
            if (
                image_prompt
                and str(image_prompt).strip()
                and str(image_prompt).strip().lower() != "null"
            ):
                logger.debug(
                    f"Image prompt detected, generating image: {image_prompt[:50]}..."
                )
                try:
                    # You can pass a specific model_name if needed, or rely on default
                    image_result = self.client.generate_image(prompt=image_prompt)
                    parsed_response["image_base64"] = image_result.get("image_base64")
                    parsed_response["image_mime_type"] = image_result.get("mime_type")
                    logger.info("Image generated and attached to response")
                except Exception as img_err:
                    logger.error(f"Failed to generate accompanying image: {img_err}")
                    parsed_response["image_base64"] = None
                    parsed_response["image_error"] = str(img_err)

            # If a video_prompt was provided, generate the video
            video_prompt = parsed_response.get("video_prompt")
            if (
                video_prompt
                and str(video_prompt).strip()
                and str(video_prompt).strip().lower() != "null"
                and generate_video
            ):
                logger.debug(
                    f"Video prompt detected, generating video: {video_prompt[:50]}..."
                )
                try:
                    video_result = self.client.generate_video(prompt=video_prompt)
                    parsed_response["video_base64"] = video_result.get("video_base64")
                    parsed_response["video_mime_type"] = video_result.get("mime_type")
                    logger.info("Video generated and attached to response")
                except Exception as vid_err:
                    logger.error(f"Failed to generate accompanying video: {vid_err}")
                    parsed_response["video_base64"] = None
                    parsed_response["video_error"] = str(vid_err)

            logger.info("Explanation generated successfully")
            return {"status": "success", "data": parsed_response}

        except InvalidPromptError as e:
            logger.error(f"Invalid prompt: {e}")
            return {"status": "error", "error": "Invalid input", "message": str(e)}

        except ResponseParsingError as e:
            logger.error(f"Response parsing failed: {e}")
            return {
                "status": "error",
                "error": "Response parsing failed",
                "message": str(e),
            }

        except AIEngineException as e:
            logger.error(f"AI engine error: {e}")
            return {
                "status": "error",
                "error": "AI processing error",
                "message": str(e),
            }

        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            return {
                "status": "error",
                "error": "Unexpected error",
                "message": "An unexpected error occurred",
            }

    def generate_bulk_explanations(
        self,
        questions: list[str],
        model_name: Optional[str] = None,
        generate_diagram: bool = True,
        generate_image: bool = True,
        generate_audio: bool = True,
        generate_video: bool = True,
    ) -> list[Dict[str, Any]]:
        """
        Generate explanations for multiple questions.

        Args:
            questions: List of questions
            model_name: Optional override for the model to use
            generate_diagram: Allow diagram generation
            generate_image: Allow image generation
            generate_audio: Allow audio generation
            generate_video: Allow video generation

        Returns:
            List of explanations
        """
        results = []
        for i, question in enumerate(questions, 1):
            logger.debug(f"Processing question {i}/{len(questions)}")
            result = self.generate_explanation(
                question,
                model_name=model_name,
                generate_diagram=generate_diagram,
                generate_image=generate_image,
                generate_audio=generate_audio,
                generate_video=generate_video,
            )
            results.append(result)

        return results


# Backward-compatible alias
PhysicsExplanationGenerator = ExplanationGenerator


# Convenience function
def generate_explanation(
    question: str,
    model_name: Optional[str] = None,
    generate_diagram: bool = True,
    generate_image: bool = True,
    generate_audio: bool = True,
    generate_video: bool = True,
) -> Dict[str, Any]:
    """
    Generate an explanation (convenience function).

    Args:
        question: Question
        model_name: Output model override
        generate_diagram: Allow diagram generation
        generate_image: Allow image generation
        generate_audio: Allow audio generation
        generate_video: Allow video generation

    Returns:
        Explanation result dictionary
    """
    generator = ExplanationGenerator()
    return generator.generate_explanation(
        question,
        model_name=model_name,
        generate_diagram=generate_diagram,
        generate_image=generate_image,
        generate_audio=generate_audio,
        generate_video=generate_video,
    )


# Backward-compatible alias
generate_physics_explanation = generate_explanation
