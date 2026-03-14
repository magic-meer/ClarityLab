"""
Multi-step explanation generator.
Processes explanations in steps for better reliability and user feedback.
"""

import logging
from typing import Dict, Any, Optional
from config.logger import setup_logger
from utils.exceptions import AIEngineException, InvalidPromptError
from ai_engine.prompt_builder import (
    build_step_explanation_prompt,
    build_step_keypoints_prompt,
    build_step_diagram_prompt,
    build_step_image_prompt,
    build_step_narration_prompt,
    build_step_followup_prompt,
)
from ai_engine.gemini_client import get_gemini_client

logger = setup_logger(__name__)


class StepExplanationGenerator:
    """Generate explanations in steps for reliability and progress tracking."""

    def __init__(self):
        self.client = get_gemini_client()
        logger.debug("StepExplanationGenerator initialized")

    def generate_step(self, prompt: str, step_name: str) -> Dict[str, Any]:
        """Execute a single step and return the result."""
        try:
            logger.info(f"Executing step: {step_name}")
            response = self.client.generate_content(prompt)
            text = response.get("text", "").strip()

            usage = {
                "prompt_tokens": response.get("usage", {}).get("prompt_tokens", 0),
                "completion_tokens": response.get("usage", {}).get(
                    "completion_tokens", 0
                ),
                "total_tokens": response.get("usage", {}).get("total_tokens", 0),
            }

            return {"status": "success", "text": text, "usage": usage}
        except Exception as e:
            logger.error(f"Step {step_name} failed: {e}")
            return {"status": "error", "error": str(e)}

    def generate_full_explanation(
        self,
        question: str,
        difficulty: str = "auto",
        generate_diagram: bool = True,
        generate_image: bool = True,
        generate_audio: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate a complete explanation using multi-step process.

        Steps:
        1. Generate main explanation (markdown)
        2. Extract key points
        3. Generate diagram (if enabled)
        4. Generate image prompt + image (if enabled)
        5. Generate narration (if enabled)
        6. Generate follow-up questions
        """
        result = {
            "topic": question.strip(),
            "difficulty": difficulty if difficulty != "auto" else "intermediate",
            "explanation": "",
            "key_points": [],
            "diagram_type": None,
            "diagram_code": None,
            "image_base64": None,
            "image_mime_type": None,
            "narration_script": None,
            "follow_up_questions": [],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        }

        total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

        # Step 1: Generate main explanation
        step1 = self.generate_step(
            build_step_explanation_prompt(question, difficulty), "explanation"
        )
        if step1["status"] == "success":
            result["explanation"] = step1["text"]
            total_usage["prompt_tokens"] += step1["usage"]["prompt_tokens"]
            total_usage["completion_tokens"] += step1["usage"]["completion_tokens"]
            total_usage["total_tokens"] += step1["usage"]["total_tokens"]
        else:
            logger.error("Step 1 (explanation) failed")
            return {"status": "error", "error": "Failed to generate explanation"}

        # Step 2: Extract key points
        step2 = self.generate_step(
            build_step_keypoints_prompt(question, result["explanation"], difficulty),
            "key_points",
        )
        if step2["status"] == "success":
            try:
                import json

                points = json.loads(step2["text"])
                if isinstance(points, list):
                    result["key_points"] = points
            except:
                # If parsing fails, try to extract lines
                lines = [l.strip() for l in step2["text"].split("\n") if l.strip()]
                result["key_points"] = [l for l in lines if l and not l.startswith("[")]
            total_usage["prompt_tokens"] += step2["usage"]["prompt_tokens"]
            total_usage["completion_tokens"] += step2["usage"]["completion_tokens"]
            total_usage["total_tokens"] += step2["usage"]["total_tokens"]

        # Step 3: Generate diagram
        if generate_diagram:
            step3 = self.generate_step(
                build_step_diagram_prompt(question, result["explanation"]), "diagram"
            )
            if step3["status"] == "success" and step3["text"].lower() != "null":
                result["diagram_type"] = "mermaid"
                result["diagram_code"] = step3["text"]
                total_usage["prompt_tokens"] += step3["usage"]["prompt_tokens"]
                total_usage["completion_tokens"] += step3["usage"]["completion_tokens"]
                total_usage["total_tokens"] += step3["usage"]["total_tokens"]

        # Step 4: Generate image
        if generate_image:
            step4 = self.generate_step(
                build_step_image_prompt(question, result["explanation"]), "image_prompt"
            )
            if step4["status"] == "success" and step4["text"].lower() != "null":
                image_prompt = step4["text"]
                try:
                    image_result = self.client.generate_image(prompt=image_prompt)
                    result["image_base64"] = image_result.get("image_base64")
                    result["image_mime_type"] = image_result.get("mime_type")
                except Exception as e:
                    logger.error(f"Image generation failed: {e}")
                total_usage["prompt_tokens"] += step4["usage"]["prompt_tokens"]
                total_usage["completion_tokens"] += step4["usage"]["completion_tokens"]
                total_usage["total_tokens"] += step4["usage"]["total_tokens"]

        # Step 5: Generate narration
        if generate_audio:
            step5 = self.generate_step(
                build_step_narration_prompt(
                    question, result["explanation"], difficulty
                ),
                "narration",
            )
            if step5["status"] == "success":
                result["narration_script"] = step5["text"]
                total_usage["prompt_tokens"] += step5["usage"]["prompt_tokens"]
                total_usage["completion_tokens"] += step5["usage"]["completion_tokens"]
                total_usage["total_tokens"] += step5["usage"]["total_tokens"]

        # Step 6: Generate follow-up questions
        step6 = self.generate_step(
            build_step_followup_prompt(question, result["explanation"]), "follow_up"
        )
        if step6["status"] == "success":
            try:
                import json

                questions = json.loads(step6["text"])
                if isinstance(questions, list):
                    result["follow_up_questions"] = questions
            except:
                lines = [l.strip() for l in step6["text"].split("\n") if l.strip()]
                result["follow_up_questions"] = [
                    l for l in lines if l and not l.startswith("[")
                ]
            total_usage["prompt_tokens"] += step6["usage"]["prompt_tokens"]
            total_usage["completion_tokens"] += step6["usage"]["completion_tokens"]
            total_usage["total_tokens"] += step6["usage"]["total_tokens"]

        result["usage"] = total_usage
        return {"status": "success", "data": result}


def generate_explanation_step(
    question: str,
    difficulty: str = "auto",
    generate_diagram: bool = True,
    generate_image: bool = True,
    generate_audio: bool = True,
) -> Dict[str, Any]:
    """Convenience function for step-based explanation."""
    generator = StepExplanationGenerator()
    return generator.generate_full_explanation(
        question=question,
        difficulty=difficulty,
        generate_diagram=generate_diagram,
        generate_image=generate_image,
        generate_audio=generate_audio,
    )
