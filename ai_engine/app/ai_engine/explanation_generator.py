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

    async def generate_explanation(
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
        """
        import asyncio
        try:
            # Validate input
            if not question or not question.strip():
                raise InvalidPromptError("Question cannot be empty")

            logger.info(f"Generating explanation for: {question[:50]}...")

            # Build optimized prompt
            prompt = build_explanation_prompt(
                question=question,
                difficulty=difficulty,
                generate_diagram=generate_diagram,
                generate_image=generate_image,
                generate_audio=generate_audio,
                generate_video=generate_video,
            )
            validate_prompt(prompt)

            # Get response from Gemini (Async)
            logger.debug("Sending request to Gemini API")
            response_data = await self.client.generate_content(prompt, model_name=model_name)

            # Log raw response for debugging
            raw_text = response_data.get("text", "")
            logger.info(f"Raw model response (first 500 chars): {raw_text[:500]}")

            # Parse and validate response
            logger.debug("Parsing response")
            parsed_response = self.parser.parse_json_response(raw_text)
            self.parser.validate_explanation_response(parsed_response)

            # Attach usage
            parsed_response["usage"] = response_data.get("usage", {})

            # Prepare async tasks for image/video generation to run in parallel
            tasks = []
            task_keys = []
            
            image_prompt = parsed_response.get("image_prompt")
            if (
                image_prompt
                and str(image_prompt).strip()
                and str(image_prompt).strip().lower() != "null"
                and generate_image
            ):
                logger.debug(f"Queuing image generation: {image_prompt[:50]}")
                tasks.append(self.client.generate_image(prompt=image_prompt))
                task_keys.append("image")
            
            video_prompt = parsed_response.get("video_prompt")
            if (
                video_prompt
                and str(video_prompt).strip()
                and str(video_prompt).strip().lower() != "null"
                and generate_video
            ):
                logger.debug(f"Queuing video generation: {video_prompt[:50]}")
                tasks.append(self.client.generate_video(prompt=video_prompt))
                task_keys.append("video")

            if tasks:
                logger.info(f"Executing {len(tasks)} parallel generation tasks")
                task_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for key, res in zip(task_keys, task_results):
                    if isinstance(res, Exception):
                        logger.error(f"Parallel task {key} failed: {res}")
                        parsed_response[f"{key}_error"] = str(res)
                    elif res:
                        if key == "image":
                            parsed_response["image_base64"] = res.get("image_base64")
                            parsed_response["image_mime_type"] = res.get("mime_type")
                        elif key == "video":
                            parsed_response["video_base64"] = res.get("video_base64")
                            parsed_response["video_mime_type"] = res.get("mime_type")

            logger.info("Explanation generated successfully")
            return {"status": "success", "data": parsed_response}

        except Exception as e:
            logger.error(f"Unexpected error in generate_explanation: {e}", exc_info=True)
            return {
                "status": "error",
                "error": type(e).__name__,
                "message": str(e),
            }

    async def generate_bulk_explanations(
        self,
        questions: list[str],
        model_name: Optional[str] = None,
        generate_diagram: bool = True,
        generate_image: bool = True,
        generate_audio: bool = True,
        generate_video: bool = True,
    ) -> list[Dict[str, Any]]:
        """
        Generate explanations for multiple questions sequentially.
        """
        results = []
        for i, question in enumerate(questions, 1):
            logger.debug(f"Processing question {i}/{len(questions)}")
            result = await self.generate_explanation(
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
async def generate_explanation(
    question: str,
    model_name: Optional[str] = None,
    generate_diagram: bool = True,
    generate_image: bool = True,
    generate_audio: bool = True,
    generate_video: bool = True,
) -> Dict[str, Any]:
    """
    Generate an explanation (convenience function).
    """
    generator = ExplanationGenerator()
    return await generator.generate_explanation(
        question,
        model_name=model_name,
        generate_diagram=generate_diagram,
        generate_image=generate_image,
        generate_audio=generate_audio,
        generate_video=generate_video,
    )


# Backward-compatible alias
generate_physics_explanation = generate_explanation
