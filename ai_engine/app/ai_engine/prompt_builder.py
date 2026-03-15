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
  "video_prompt": null,
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
  "diagram_code": "string|null - Raw Mermaid flowchart code. Use ONLY ID[\"Label\"] format with square brackets and double quotes. No markdown fences. Only generate if diagram_type is 'mermaid'.",
  "image_prompt": "string|null - Detailed prompt for image generation",
  "video_prompt": "string|null - Detailed prompt for a short (8s) animated educational video",
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
    generate_video: bool = True,
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
        generate_video: Allow video generation

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
DIAGRAM GUIDELINES (TECHNICAL):
- THIS IS AN AUTOMATED APP. Your output will be directly parsed and rendered by Mermaid.js.
- CRITICAL: Generate ONLY Mermaid flowchart code (graph TD or graph LR). 
- COMPATIBILITY RULES:
  1. Use ONLY square bracket nodes: ID["Label Text"]. Avoid ( ) or { }.
  2. EVERY label MUST be enclosed in exactly one pair of double quotes: A["Text"].
  3. No labels on arrows (e.g., A --> B). Do not use |Label|.
  4. No comments (%%) or extra quotes anywhere.
  5. OUTPUT ONLY THE RAW CODE. No markdown fences, no text.
- If a diagram is not helpful, set diagram_type to null.
"""
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

    video_instruction = ""
    if generate_video:
        video_instruction = """
VEO VIDEO PROMPT — 8 SECONDS HARD LIMIT:
You are writing a prompt for an 8-second animated educational video. This is an absolute time constraint.

PLANNING RULE — ONE IDEA ONLY:
8 seconds can communicate exactly ONE visual idea. Do not try to show a full explanation. Instead, identify the single most visually compelling moment or mechanism of this concept — the "aha moment" — and build the entire 8 seconds around it.

THREE-ACT STRUCTURE (stick to this timing):
- Seconds 0–2 (Setup): Establish the scene. A clean, minimal environment appears. The subject or system is introduced at rest.
- Seconds 2–6 (Core Action): The key mechanism, transformation, or interaction plays out. This is the main event — animate it with motion, flow, and labeled arrows.
- Seconds 6–8 (Payoff): The result or insight lands. A key label or equation fades in. The animation holds on the final state.

VISUAL STYLE:
- Flat design, 2D or simple 3D. Clean white or soft-gradient background.
- Primary colors for key elements. Animated arrows and labels to show flow or causality.
- No photorealism. No cinematic lighting. No busy backgrounds.
- Think: premium Khan Academy or 3Blue1Brown aesthetic.

AUDIO CUES (include all three):
- Narrator line: A single sentence of 12–18 words spoken during seconds 2–7. Write the exact line.
- Sound effect: One or two subtle ambient or action sounds (e.g., "a soft electric hum as current flows", "a gentle whoosh as the arrow traces the path").
- Musical tone: One adjective for the background music (e.g., "minimal and curious", "calm and precise").

FORMAT YOUR PROMPT AS A SINGLE PARAGRAPH describing the full 8 seconds in continuous prose, including all timing cues, visual actions, the narrator's exact line, and sound design."""
    else:
        video_instruction = """
- video_prompt: MUST be null (user disabled)"""

    prompt = f"""You are writing an educational chapter for a book. Your task is to explain the following concept in an engaging, narrative style that draws the reader in, develops ideas naturally, and concludes meaningfully.

{difficulty_instruction}

{STRUCTURED_OUTPUT_SPEC}

{MARKDOWN_GUIDE}

{diagram_instruction}
{image_instruction}
{audio_instruction}
{video_instruction}

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
    generate_video: bool = True,
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
    context_str = f"\\nAdditional context: {context}" if context else ""

    diagram_instruction = ""
    if generate_diagram:
        diagram_instruction = """
DIAGRAM GUIDELINES: Only include a diagram if visual representation of the image elements would help. Use Mermaid flowchart/graph syntax."""
    else:
        diagram_instruction = "- diagram_type: MUST be null"

    image_instruction = ""
    if generate_image:
        image_instruction = "IMAGE PROMPT: Provide an illustrative prompt for a clarifying image if needed."
    else:
        image_instruction = "- image_prompt: MUST be null"

    audio_instruction = ""
    if generate_audio:
        audio_instruction = "NARRATION: Provide a 2-3 sentence spoken summary of the analysis."
    else:
        audio_instruction = "- narration_script: MUST be null"

    video_instruction = ""
    if generate_video:
        video_instruction = """
VEO VIDEO PROMPT — 8 SECONDS HARD LIMIT:
You are writing a prompt for an 8-second animated educational video that brings the key element of this image to life.

PLANNING RULE — ONE INTERACTION ONLY:
Look at the image and identify the single most important relationship, flow, or mechanism it depicts. The entire 8 seconds will animate only that one thing. Do not attempt to recreate the full image — animate its core insight.

THREE-ACT STRUCTURE (stick to this timing):
- Seconds 0–2 (Setup): A simplified, flat-design version of the image's key element appears on a clean background. Labels fade in to name the components.
- Seconds 2–6 (Core Action): The relationship or mechanism animates — arrows flow, elements interact, a transformation occurs. Motion makes the concept tangible.
- Seconds 6–8 (Payoff): The animation settles. A short text overlay or equation reinforces the takeaway.

VISUAL STYLE:
- Flat 2D animation. Soft gradient or white background.
- Match the color palette of the original image loosely for visual continuity.
- Clean, labeled arrows. No photorealism or cinematic effects.

AUDIO CUES (include all three):
- Narrator line: A single sentence of 12–18 words, spoken during seconds 2–7. Write the exact line.
- Sound effect: One subtle ambient or interaction sound.
- Musical tone: One adjective for the background music.

FORMAT YOUR PROMPT AS A SINGLE PARAGRAPH describing the full 8 seconds in continuous prose, including all timing cues, visual actions, the narrator's exact line, and sound design."""
    else:
        video_instruction = "- video_prompt: MUST be null"

    prompt = f"""You are analyzing an educational image/diagram and writing a chapter about it.

{difficulty_instruction}

You are writing an educational chapter. Explain what the image shows, identify key elements, and connect it to the underlying concepts.

{STRUCTURED_OUTPUT_SPEC}

{MARKDOWN_GUIDE}

{context_str}

{diagram_instruction}
{image_instruction}
{audio_instruction}
{video_instruction}

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


# ===== Step-based prompts for multi-step processing =====


def build_step_explanation_prompt(question: str, difficulty: str = "auto") -> str:
    """Step 1: Generate the main explanation in markdown format."""
    if difficulty not in DIFFICULTY_INSTRUCTIONS:
        difficulty = "auto"

    diff_instruction = DIFFICULTY_INSTRUCTIONS.get(
        difficulty, DIFFICULTY_INSTRUCTIONS["auto"]
    )

    return f"""Write an educational explanation for the following topic.

{diff_instruction}

Topic: {question.strip()}

Write in a narrative, book-like style:
- Start with an engaging hook or introduction
- Develop ideas in flowing paragraphs
- Use headings (# ## ###) to organize sections
- Use **bold** for key terms
- Use *italic* for examples and emphasis
- Use `code` for technical terms
- Use $math$ for inline math, $$math$$ for block equations
- Use bullet points sparingly, prefer flowing prose
- End with a meaningful conclusion

CRITICAL: Output plain text with markdown formatting. Do NOT output JSON. Do NOT use code blocks (no ```). Start your response directly with the explanation text."""


def build_step_keypoints_prompt(
    question: str, explanation: str, difficulty: str = "auto"
) -> str:
    """Step 2: Extract key learning points from the explanation."""
    return f"""Extract 3-5 key learning points from the following explanation about "{question.strip()}".

Explanation:
{explanation}

Output ONLY a JSON array of strings like: ["point 1", "point 2", "point 3"]
No other text, no code blocks, just the JSON array."""


def build_step_diagram_prompt(question: str, explanation: str) -> str:
    """Step 3: Generate mermaid diagram code."""
    return f"""This is part of an AUTOMATED app. Generate a raw Mermaid flowchart for: "{question.strip()}".
    
    SYSTEM LOGIC:
    - We use Mermaid.js flowchart (graph TD/LR).
    - Parsing is strict: Nodes MUST be formatted as ID["Label"] (square brackets + double quotes).
    - PARSING RULE: Do NOT use |label| on arrows. Do NOT use quotes or brackets inside labels.
    - OUTPUT: Raw Mermaid code ONLY. No backticks, no markdown, no conversational filler.
    
    Explanation context:
    {explanation[:500]}...
    
    Generate raw Mermaid code (or output 'null' if a diagram is not appropriate):"""


def build_step_image_prompt(question: str, explanation: str) -> str:
    """Step 4: Generate image generation prompt."""
    return f"""Create a detailed, educational image prompt for the concept: "{question.strip()}".

The image should help visualize and understand this concept:
{explanation[:500]}...

Output ONLY a detailed image prompt description.
No JSON, no code blocks. Just the prompt text.
If an image would not help, output: null"""


def build_step_narration_prompt(
    question: str, explanation: str, difficulty: str = "auto"
) -> str:
    """Step 5: Generate narration script."""
    length_guide = {
        "beginner": "2-3 sentences, very simple language",
        "intermediate": "2-4 sentences, moderate complexity",
        "advanced": "3-5 sentences, technical but clear",
        "expert": "4-6 sentences, assume expertise",
    }
    guide = length_guide.get(difficulty, "3-4 sentences")

    return f"""Write a spoken narration script summarizing: "{question.strip()}".

Guidelines:
- Length: {guide}
- Write for text-to-speech (speak naturally when read aloud)
- Focus on the core concept
- No markdown, no formatting, just plain text

Output ONLY the narration script. No JSON, no code blocks."""


def build_step_followup_prompt(question: str, explanation: str) -> str:
    """Step 6: Generate follow-up questions."""
    return f"""Suggest 2-3 thought-provoking follow-up questions to deepen understanding of: "{question.strip()}".
 
 Based on this explanation:
 {explanation[:500]}...
 
 Output ONLY a JSON array of question strings like: ["question 1?", "question 2?"]
 No code blocks, no explanations, just the JSON array."""


def build_step_video_prompt(question: str, explanation: str) -> str:
    """Step 7: Generate video generation prompt."""
    return f"""You are writing a prompt for an 8-second animated educational video about: "{question.strip()}".

This is an absolute hard limit — 8 seconds. Your prompt must be engineered for this constraint.

STEP 1 — IDENTIFY THE ONE VISUAL MOMENT:
Read the explanation below and extract the single most visually compelling insight — the mechanism, transformation, or relationship that, if animated, would make the concept immediately click. Ignore everything else. The entire 8 seconds is devoted to this one moment.

Explanation context:
{explanation[:600]}...

STEP 2 — APPLY THIS EXACT STRUCTURE:

THREE-ACT TIMING:
- Seconds 0–2 (Setup): A minimal, flat-design scene appears on a clean background. The key subject or system is introduced at rest. One or two labels fade in to name the components.
- Seconds 2–6 (Core Action): The central mechanism animates. Arrows flow, elements transform, forces act, data moves — whatever is most true to the concept. This is the "aha moment". Animated labels or values reinforce what is happening in real time.
- Seconds 6–8 (Payoff): Motion slows. The final state holds on screen. A short text overlay (one phrase or a key equation) fades in to crystallize the takeaway.

VISUAL STYLE (non-negotiable):
- Flat 2D animation with optional simple 3D shapes. Soft white or subtle gradient background.
- Bold, primary accent colors for key elements. Clean sans-serif labels.
- Smooth easing on all motion (ease-in-out). No abrupt cuts.
- Absolutely NO photorealism, NO cinematic lighting, NO stock footage aesthetic.
- Reference aesthetic: 3Blue1Brown, Kurzgesagt (minimal version), or Khan Academy explainer.

AUDIO (include all three, be specific):
- Narrator: Write the EXACT sentence (12–18 words) spoken aloud during seconds 2–7. It must complete the thought the animation is showing.
- SFX: One or two specific ambient or interaction sounds that reinforce the visual action (e.g., "a soft electric hum that rises as voltage increases", "a crisp click each time a node connects").
- Music: One phrase describing the background tone (e.g., "quiet and curious, single piano notes", "minimal electronic, calm and precise").

OUTPUT FORMAT:
Write a single, continuous paragraph in present tense that describes the full 8 seconds — what appears, what moves, what is heard, and what the narrator says. Do not use bullet points or section headers in your output. Do not include any JSON, code blocks, or meta-commentary. Output ONLY the video prompt paragraph.

If this concept is entirely abstract and cannot be meaningfully visualized in 8 seconds, output: null"""