"""
Reasoning generator for ClarityLab.
Constructs a plan with specific prompts for multimodal assets.
"""

import logging
import json
from typing import Dict, Any, Optional
from config.logger import setup_logger
from ai_engine.gemini_client import get_gemini_client
from ai_engine.response_parser import ResponseParser
from ai_engine.prompt_builder import DIFFICULTY_INSTRUCTIONS

logger = setup_logger(__name__)

REASONING_SYSTEM_PROMPT = """You are the Lead Orchestrator for ClarityLab, a premium multimodal AI learning agent.
Your goal is to analyze a user's question and create a detailed "Execution Plan" for generating a rich, textbook-style explanation.

You will decide which multimodal assets (diagrams, images, videos) are appropriate for the topic and difficulty level.
You will then generate specific, high-quality prompts for EACH asset that our specialized generators will use.

For the explanation text, you will generate a prompt that includes all constraints (narrative style, markdown, specific vocabulary).

THE PRODUCT:
- A seamless "textbook" page.
- Beautiful, high-quality educational content.

DIFFICULTY CONTEXT:
{difficulty_instruction}

OUTPUT FORMAT (JSON):
{{
    "topic": "Clear title",
    "difficulty": "beginner|intermediate|advanced|expert",
    "explanation_prompt": "Highly detailed prompt for the text generator. Include narrative style, hook requirements, and specific concepts to cover.",
    "diagram_prompt": "Prompt for a Mermaid or SVG diagram. Must be 'null' if not needed.",
    "image_prompt": "Detailed prompt for Imagen 3. Must be 'null' if not needed.",
    "video_prompt": "Detailed prompt for Veo 3.1 animated explainer. Must be 'null' if not needed.",
    "narration_prompt": "Prompt for a short summary script. Must be 'null' if not needed.",
    "followup_prompt": "Prompt to generate target follow-up questions."
}}

CONSTRAINTS:
1. ONLY return the plan JSON.
2. Prompts should be self-contained and descriptive.
3. If user toggles are OFF for an asset, that prompt MUST be 'null'.
"""

class ReasoningGenerator:
    """Generates an initial plan for complex multimodal responses."""

    def __init__(self):
        self.client = get_gemini_client()
        self.parser = ResponseParser()

    async def generate_plan(
        self,
        question: str,
        difficulty: str = "auto",
        generate_diagram: bool = True,
        generate_image: bool = True,
        generate_video: bool = True,
        generate_audio: bool = True,
        model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate the multimodal execution plan."""
        
        diff_inst = DIFFICULTY_INSTRUCTIONS.get(difficulty, DIFFICULTY_INSTRUCTIONS["auto"])
        
        system_prompt = REASONING_SYSTEM_PROMPT.format(difficulty_instruction=diff_inst)
        
        user_prompt = f"""Create a multimodal execution plan for the following:
Question: {question}

User Preference Toggles:
- Diagrams: {"ENABLED" if generate_diagram else "DISABLED"}
- Images: {"ENABLED" if generate_image else "DISABLED"}
- Video: {"ENABLED" if generate_video else "DISABLED"}
- Narration: {"ENABLED" if generate_audio else "DISABLED"}

Generate the plan JSON:"""

        logger.info(f"Generating reasoning plan for: {question[:50]}")
        
        try:
            # Combine for a single call if model supports it, or use system instruction
            # Vertex AI models support system_instruction, but our client abstraction 
            # might need adjustment. For now, we'll prepend it.
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            response_data = await self.client.generate_content(full_prompt, model_name=model_name)
            raw_text = response_data.get("text", "")
            
            plan = self.parser.parse_json_response(raw_text)
            
            # Clean up 'null' strings that should be None
            for key in ["diagram_prompt", "image_prompt", "video_prompt", "narration_prompt"]:
                if isinstance(plan.get(key), str) and plan[key].lower() == "null":
                    plan[key] = None
            
            return {
                "status": "success",
                "plan": plan,
                "usage": response_data.get("usage", {})
            }
            
        except Exception as e:
            logger.error(f"Reasoning failed: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
