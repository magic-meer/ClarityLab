"""
Prompt building module for constructing optimized prompts for Gemini.
The AI decides difficulty level and which multimedia outputs are appropriate.
"""

import logging
from typing import Optional
from config.logger import setup_logger
from utils.exceptions import InvalidPromptError

logger = setup_logger(__name__)

DIFFICULTY_INSTRUCTIONS = {
    "auto": """
DIFFICULTY: AUTO (AI decides)
- Analyze the question to determine the appropriate difficulty
- Consider the complexity of the topic and likely prior knowledge
- Set difficulty to: beginner, intermediate, advanced, or expert based on your analysis
- The "difficulty" field in your output should reflect your analysis""",
    "beginner": """
DIFFICULTY: BEGINNER (USER REQUESTED)
- CRITICAL: You MUST set the "difficulty" field to "beginner" in your JSON output
- Use simple, everyday language
- Avoid jargon or explain any technical terms
- Use familiar analogies from daily life
- Keep sentences short and clear
- Focus on "what" and "why" basics
- No complex formulas or advanced concepts""",
    "intermediate": """
DIFFICULTY: INTERMEDIATE (USER REQUESTED)
- CRITICAL: You MUST set the "difficulty" field to "intermediate" in your JSON output
- Use some technical terms with brief explanations
- Include relevant formulas when helpful
- Use analogies that require some domain knowledge
- Balance depth with accessibility
- Explain "how" things work
- Can include moderate complexity""",
    "advanced": """
DIFFICULTY: ADVANCED (USER REQUESTED)
- CRITICAL: You MUST set the "difficulty" field to "advanced" in your JSON output
- Use technical terminology freely
- Include detailed formulas and derivations
- Assume some background knowledge
- Focus on deep understanding and nuances
- Explain edge cases and corner conditions
- Connect to broader theoretical frameworks""",
    "expert": """
DIFFICULTY: EXPERT (USER REQUESTED)
- CRITICAL: You MUST set the "difficulty" field to "expert" in your JSON output
- Use precise technical language without explanation
- Include full mathematical rigor
- Assume deep domain expertise
- Discuss latest research and frontiers
- Handle edge cases and exceptions
- Connect to related fields and advanced topics""",
}

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

STRUCTURED_OUTPUT_SPEC = """CRITICAL: Output ONLY raw JSON - NO markdown code blocks, NO ```json, NO ``` delimiters. Just plain JSON text.

JSON Schema:
{
  "topic": "string - A clear, concise title for the topic",
  "difficulty": "string - One of: beginner, intermediate, advanced, expert",
  "explanation": "string - Your main explanation (supports markdown formatting)",
  "key_points": ["string", "string", ...],
  "diagram_type": "string|null - 'mermaid' or 'svg' if a diagram would help",
  "diagram_code": "string|null - Raw Mermaid/SVG code (no markdown codeblocks)",
  "image_prompt": "string|null - Detailed prompt for image generation",
  "narration_script": "string|null - 2-3 sentence spoken summary",
  "follow_up_questions": ["string", "string", ...]
}

Markdown Support in explanation field:
- # Heading 1, ## Heading 2, ### Heading 3
- **bold** for emphasis, *italic* for subtle emphasis
- `code` for technical terms, ```language for code blocks
- $inline math$ and $$block math$$ for equations
- - bullet lists, 1. numbered lists
- > blockquotes for important callouts"""

MARKDOWN_GUIDE = """IMPORTANT: We render markdown in the explanation field:
- Use # for headings (## for subsections)
- Use **bold** for key terms and important concepts
- Use *italic* for examples, analogies, and subtle emphasis
- Use `code` formatting for technical terms, function names, variables
- Use ``` for multi-line code examples
- Use $equation$ for inline math, $$equation$$ for block math
- Use bullet points for lists, but keep them flowing in paragraphs
- Use > for important callouts or key takeaways

Write in a NARRATIVE STYLE - like a chapter in an educational book. 
Start with an engaging hook, develop ideas in a flowing manner, and conclude meaningfully.
Avoid dry bullet-point lists; weave information into coherent paragraphs."""


def build_explanation_prompt(
    question: str,
    difficulty: str = "auto",
    generate_diagram: bool = True,
    generate_image: bool = True,
    generate_audio: bool = True,
) -> str:
    """
    Build optimized prompt for generating an explanation on any topic.
    The AI decides the difficulty level and which multimedia outputs are useful.

    Args:
        question: Concept or question to explain
        difficulty: Difficulty level - auto, beginner, intermediate, advanced, or expert
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

    if difficulty not in DIFFICULTY_INSTRUCTIONS:
        difficulty = "auto"

    difficulty_instruction = DIFFICULTY_INSTRUCTIONS.get(difficulty, "")

    diagram_instruction = ""
    if generate_diagram:
        diagram_instruction = """
DIAGRAM GUIDELINES (IMPORTANT):
- Only include a diagram if visual representation would genuinely help understanding
- For Mermaid diagrams, use ONLY valid syntax:
  - Flowcharts: graph TD/LR, node shapes (A[Rectangle], B(Rounded), C(Diamond))
  - Use --> for arrows, --- for lines
  - Labels go in double quotes: A["Label"]
  - Subgraphs: subgraph name...endsubgraph
- Test your mermaid code mentally before outputting
- Common errors to avoid: missing quotes, invalid shapes, unclosed brackets
- If unsure about syntax, set diagram_type to null"""
    else:
        diagram_instruction = """
- diagram_type: MUST be null (user disabled)"""

    image_instruction = ""
    if generate_image:
        image_instruction = """
IMAGE PROMPT: If an illustrative image would help visualize the concept, provide a detailed prompt describing what the image should show. Make it educational and visually clear."""
    else:
        image_instruction = """
- image_prompt: MUST be null (user disabled)"""

    audio_instruction = ""
    if generate_audio:
        audio_instruction = """
NARRATION: If a spoken summary would help, write 2-3 sentences that could be read aloud to summarize the concept."""
    else:
        audio_instruction = """
- narration_script: MUST be null (user disabled)"""

    prompt = f"""You are writing an educational chapter for a book. Your task is to explain the following concept in an engaging, narrative style that draws the reader in, develops ideas naturally, and concludes meaningfully.

{difficulty_instruction}

{STRUCTURED_OUTPUT_SPEC}

{MARKDOWN_GUIDE}

{diagram_instruction}
{image_instruction}
{audio_instruction}

IMPORTANT RESTRICTIONS:
1. Output ONLY valid JSON - no markdown code blocks, no explanatory text
2. Any field you decide is NOT useful MUST be null (not an empty string)
3. Use proper JSON syntax (double quotes, no trailing commas)
4. The explanation field supports markdown - use it to create a beautiful, readable chapter

Now generate the response for:

Topic/Question: {question.strip()}

Generate the JSON response:"""

    logger.debug(
        f"Prompt built for question: {question[:50]}... with difficulty: {difficulty}"
    )
    return prompt


# Keep backward-compatible alias
build_physics_prompt = build_explanation_prompt


def build_image_analysis_prompt(
    question: str,
    context: Optional[str] = None,
    difficulty: str = "auto",
    generate_diagram: bool = True,
    generate_image: bool = True,
    generate_audio: bool = True,
) -> str:
    """
    Build prompt for analyzing uploaded images/diagrams.

    Args:
        question: Question about the image
        context: Additional context about the image
        difficulty: Difficulty level

    Returns:
        Prompt for image analysis

    Raises:
        InvalidPromptError: If inputs are invalid
    """
    if not question or not question.strip():
        raise InvalidPromptError("Question cannot be empty")

    if difficulty not in DIFFICULTY_INSTRUCTIONS:
        difficulty = "auto"

    difficulty_instruction = DIFFICULTY_INSTRUCTIONS.get(difficulty, "")
    context_str = f"\nAdditional context: {context}" if context else ""

    prompt = f"""You are analyzing an educational image/diagram and writing a chapter about it.

{difficulty_instruction}

You are writing an educational chapter. Explain what the image shows, identify key elements, and connect it to the underlying concepts.

{STRUCTURED_OUTPUT_SPEC}

{MARKDOWN_GUIDE}

{context_str}

Question about the image: {question.strip()}

Output ONLY valid JSON:"""

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
