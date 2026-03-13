"""
Prompt building module for constructing optimized prompts for Gemini.
The AI decides difficulty level and which output types are appropriate.
"""

import logging
from typing import Optional
from config.logger import setup_logger
from utils.exceptions import InvalidPromptError

logger = setup_logger(__name__)

JSON_FORMAT_TEMPLATE = """{
 "topic": "",
 "difficulty": "",
 "explanation": "",
 "key_points": [],
 "diagram_type": null,
 "diagram_code": null,
 "image_prompt": null,
 "narration_script": null,
 "follow_up_questions": []
}"""

def build_explanation_prompt(
    question: str,
    generate_diagram: bool = True,
    generate_image: bool = True,
    generate_audio: bool = True
) -> str:
    """
    Build optimized prompt for generating an explanation on any topic.
    The AI decides the difficulty level and which multimedia outputs are useful.

    Args:
        question: Concept or question to explain
        generate_diagram: Allow diagram generation
        generate_image: Allow image generation
        generate_audio: Allow audio generation

    Returns:
        Optimized prompt string

    Raises:
        InvalidPromptError: If inputs are invalid
    """
    if not question or not question.strip():
        raise InvalidPromptError("Question cannot be empty")

    prompt = f"""You are an expert tutor with exceptional ability to explain complex concepts clearly and accurately across any subject — science, mathematics, history, literature, computer science, and more.

Your task: Explain the following concept or answer the following question.

**Instructions:**

1. **Determine Difficulty**: Based on the question's complexity, decide the most appropriate difficulty level: "beginner", "intermediate", "advanced", or "expert". Set this in the "difficulty" field.

2. **Generate Explanation**: Provide a clear, comprehensive explanation using everyday language and analogies where appropriate.

3. **Key Learning Points**: List 3-5 important concepts the student should understand.

4. **Decide Which Outputs Are Useful**: Think carefully about which outputs would genuinely help explain THIS specific topic:
   - **diagram_type**: {"If a structural visual diagram would help, set this to 'mermaid' or 'svg'. If not useful, set to null." if generate_diagram else "Strictly set to null. User disabled diagram generation."}
   - **diagram_code**: {"If `diagram_type` is set, provide the RAW CODE for the diagram. Do NOT wrap it in markdown codeblocks (no ```). If not useful, set to null." if generate_diagram else "Strictly set to null. User disabled diagram generation."}
   - **image_prompt**: {"If an illustrative image would help explain the topic, provide a highly detailed, descriptive prompt. If not useful, set to null." if generate_image else "Strictly set to null. User disabled image generation."}
   - **narration_script**: {"If a spoken narration summarizing the concept would be helpful, provide a clear 2-3 sentence narration script. If not suitable, set to null." if generate_audio else "Strictly set to null. User disabled audio narration generation."}

5. **Follow-up Questions**: Suggest 2-3 thought-provoking questions to deepen understanding.

IMPORTANT: Return your response STRICTLY as valid JSON with no additional text or markdown.
Any output type you decide is NOT useful for this topic MUST be set to null (not an empty string).

Expected JSON format:
{JSON_FORMAT_TEMPLATE}

Concept/Question:
{question.strip()}

Generate the response now:"""

    logger.debug(f"Prompt built for question: {question[:50]}...")
    return prompt


# Keep backward-compatible alias
build_physics_prompt = build_explanation_prompt


def build_image_analysis_prompt(
    question: str,
    context: Optional[str] = None,
    generate_diagram: bool = True,
    generate_image: bool = True,
    generate_audio: bool = True
) -> str:
    """
    Build prompt for analyzing uploaded images/diagrams.

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

    prompt = f"""You are an expert educator analyzing a diagram, screenshot, or learning material.

Please analyze the image and answer the following question:

{question.strip()}{context_str}

Provide a detailed, educational explanation that:
1. Identifies key elements in the image
2. Explains the concepts shown
3. Answers the specific question
4. Identifies any misconceptions a student might have
5. Suggests follow-up learning topics

Also provide responses in structured JSON matching this format:
{JSON_FORMAT_TEMPLATE}

Follow the same rules for deciding outputs:
   - **diagram_type**: {"If a structural visual diagram would help, set this to 'mermaid' or 'svg'. If not useful, set to null." if generate_diagram else "Strictly set to null. User disabled diagram generation."}
   - **diagram_code**: {"If `diagram_type` is set, provide the RAW CODE for the diagram. If not useful, set to null." if generate_diagram else "Strictly set to null."}
   - **image_prompt**: {"If an illustrative image would help explain the topic, provide a highly detailed, descriptive prompt. If not useful, set to null." if generate_image else "Strictly set to null."}
   - **narration_script**: {"If a spoken narration summarizing the concept would be helpful, provide a 2-3 sentence narration script. If not suitable, set to null." if generate_audio else "Strictly set to null."}"""

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