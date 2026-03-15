"""
API routes for ClarityLab AI Learning Agent.
Handles HTTP endpoints for explanation generation and image analysis.
"""

from fastapi import APIRouter, HTTPException, status, Query, File, UploadFile, Form
from typing import Optional, List
import logging
import tempfile
import base64
import asyncio
from pathlib import Path

from google import genai
from config.settings import get_settings

from ai_engine.explanation_generator import ExplanationGenerator
from ai_engine.step_explanation_generator import StepExplanationGenerator
from ai_engine.reasoning_generator import ReasoningGenerator
from ai_engine.multimodal_handler import MultiModalHandler
from ai_engine.gemini_client import get_gemini_client
from utils.exceptions import AIEngineException
from schemas.request_schema import ExplanationRequest, ImageGenerationRequest, AssetGenerationRequest
from utils.validators import validate_request_input, sanitize_question
from config.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(tags=["Explanations"])


# ─── Dynamic Model Listing ──────────────────────────────────────────────────

# Cache so we only hit the Gemini models.list() API once per server lifetime
_models_cache: dict | None = None


@router.get(
    "/models",
    summary="List Available Models",
    description="Fetch available Gemini text models, image models, and audio voices",
)
async def list_models() -> dict:
    """List available models — cached after first fetch to avoid slow startup."""
    global _models_cache
    if _models_cache is not None:
        return _models_cache

    try:
        text_models = []
        image_models = []

        settings = get_settings()

        # Configure specifically for Vertex AI
        client = genai.Client(
            vertexai=True,
            project=settings.gcp_project_id,
            location=settings.gcp_location,
        )

        for m in client.models.list():
            name_lower = m.name.lower()
            description = getattr(m, "description", "") or ""
            description_lower = description.lower()

            # Extract the actual model name for Vertex AI prediction.
            # Example: "publishers/google/models/gemini-2.5-flash" -> "gemini-2.5-flash"
            model_name_id = m.name.split("/")[-1]

            info = {
                "name": model_name_id,
                "display_name": m.display_name,
                "description": description,
            }

            # ── Text models ──────────────────────────────────────────────────
            # Use name-based matching: any Gemini model that isn't a pure
            # embedding / text-embedding / aqa / vision-only model.
            # The old methods_str approach broke because the SDK returns enum
            # objects whose str() is NOT the literal string "generateContent".
            is_gemini = "gemini" in name_lower
            is_not_embedding = "embedding" not in name_lower
            is_not_aqa = "aqa" not in name_lower
            is_not_tts = "tts" not in name_lower

            if is_gemini and is_not_embedding and is_not_aqa and is_not_tts:
                text_models.append(info)

            # ── Image models ─────────────────────────────────────────────────
            # Include imagen models BUT exclude "Vertex served" ones — those
            # require a Vertex AI / GCP project and are not accessible with a
            # standard Gemini API key.
            is_imagen = "imagen" in name_lower
            is_vertex_only = "vertex" in description_lower

            if is_imagen and not is_vertex_only:
                image_models.append(info)

        # ── Sort for good UX ──────────────────────────────────────────────────
        # Prefer newer/faster models first for text; maintain API list order
        # for images (newest first is fine).
        def _model_sort_key(m: dict) -> tuple:
            n = m["name"].lower()
            # Push experimental / preview to the bottom
            is_exp = any(x in n for x in ("exp", "preview", "latest", "thinking"))
            # Prefer gemini-2.x over gemini-1.x
            gen = 0
            if "2.5" in n:
                gen = -3
            elif "2.0" in n:
                gen = -2
            elif "1.5" in n:
                gen = -1
            return (int(is_exp), gen, n)

        text_models.sort(key=_model_sort_key)

        # Audio voices are from GCP TTS — not discoverable via genai SDK
        audio_voices = [
            {"name": "en-US-Journey-D", "display_name": "Journey (US Male)"},
            {"name": "en-US-Journey-F", "display_name": "Journey (US Female)"},
            {"name": "en-US-Standard-A", "display_name": "Standard (US Male)"},
            {"name": "en-US-Standard-C", "display_name": "Standard (US Female)"},
            {"name": "en-GB-Standard-A", "display_name": "Standard (UK Female)"},
            {"name": "en-GB-Standard-B", "display_name": "Standard (UK Male)"},
            {"name": "en-AU-Standard-A", "display_name": "Standard (AU Female)"},
        ]

        _models_cache = {
            "status": "success",
            "text_models": text_models,
            "image_models": image_models,
            "audio_voices": audio_voices,
        }
        logger.info(
            f"Models cached: {len(text_models)} text, {len(image_models)} image models"
        )
        return _models_cache

    except Exception as e:
        logger.error(f"Error listing models: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list models",
        )


@router.delete(
    "/models/cache",
    summary="Clear Model Cache",
    description="Force the model list to be re-fetched from the Gemini API on next request",
)
async def clear_models_cache() -> dict:
    """Clear cached model list so it's refreshed on the next /models call."""
    global _models_cache
    _models_cache = None
    logger.info("Model cache cleared")
    return {"status": "success", "message": "Model cache cleared"}


# ─── Explain ─────────────────────────────────────────────────────────────────


@router.post(
    "/explain",
    response_model=dict,
    summary="Generate Explanation",
    description="Generate a comprehensive explanation for any concept or question",
)
async def explain_concept(request: ExplanationRequest) -> dict:
    """Generate an explanation. AI decides difficulty and which outputs to produce."""
    try:
        logger.info(f"Processing explanation request: {request.question[:50]}...")

        is_valid, error_msg = validate_request_input(request.question)
        if not is_valid:
            logger.warning(f"Validation failed: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input: {error_msg}",
            )

        question = sanitize_question(request.question)

        # Use ExplanationGenerator to get structured response
        generator = ExplanationGenerator()

        result = await generator.generate_explanation(
            question=question,
            model_name=request.model_name,
            difficulty=request.difficulty or "auto",
            generate_diagram=request.generate_diagram,
            generate_image=request.generate_image,
            generate_audio=request.generate_audio,
            generate_video=request.generate_video,
        )

        if result.get("status") != "success":
            logger.error(f"Generation failed: {result.get('message') or result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("message") or result.get("error") or "Failed to generate explanation",
            )

        logger.info("Explanation generated successfully")
        return {"status": "success", "data": result.get("data")}

    except HTTPException:
        raise
    except AIEngineException as e:
        logger.error(f"AI Engine error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process request",
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


# ─── Step-by-Step Explain (Multi-Step) ────────────────────────────────────────


@router.post(
    "/explain/steps",
    response_model=dict,
    summary="Generate Explanation (Step-by-Step)",
    description="Generate explanation using multi-step process for better reliability",
)
async def explain_concept_steps(request: ExplanationRequest) -> dict:
    """Generate an explanation using step-by-step process for reliability."""
    try:
        logger.info(f"Processing step-by-step explanation: {request.question[:50]}...")

        is_valid, error_msg = validate_request_input(request.question)
        if not is_valid:
            logger.warning(f"Validation failed: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input: {error_msg}",
            )

        question = sanitize_question(request.question)

        # Use StepExplanationGenerator for multi-step processing
        generator = StepExplanationGenerator()

        result = await generator.generate_full_explanation(
            question=question,
            difficulty=request.difficulty or "auto",
            generate_diagram=request.generate_diagram,
            generate_image=request.generate_image,
            generate_audio=request.generate_audio,
            generate_video=request.generate_video,
        )

        if result.get("status") != "success":
            logger.error(f"Step-by-step generation failed: {result.get('error')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Failed to generate explanation"),
            )

        logger.info("Step-by-step explanation generated successfully")
        return {"status": "success", "data": result.get("data")}

    except HTTPException:
        raise
    except AIEngineException as e:
        logger.error(f"AI Engine error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process request",
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


# ─── Bulk Explain ────────────────────────────────────────────────────────────


@router.post(
    "/explain/bulk",
    response_model=list,
    summary="Generate Multiple Explanations",
    description="Generate explanations for multiple concepts",
)
async def explain_multiple(
    questions: List[str] = Query(..., description="List of questions"),
    model_name: Optional[str] = Query(None, description="Model override"),
) -> list:
    """Generate explanations for multiple questions."""
    try:
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No questions provided"
            )

        if len(questions) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 questions allowed per request",
            )

        logger.info(f"Processing {len(questions)} explanation requests in parallel")

        generator = ExplanationGenerator()
        tasks = []
        for question in questions:
            sanitized = sanitize_question(question)
            tasks.append(generator.generate_explanation(sanitized, model_name=model_name))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        final_results = []
        for res in results:
            if isinstance(res, Exception):
                final_results.append({"status": "error", "error": str(res)})
            else:
                final_results.append(res)

        logger.info(f"Processed {len(questions)} bulk requests")
        return final_results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing multiple requests: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process requests",
        )


# ─── Image Analysis ──────────────────────────────────────────────────────────


@router.post(
    "/analyze-image",
    summary="Analyze Uploaded Image/Diagram",
    description="Analyze an image, diagram, or learning material with a specific question",
)
async def analyze_image(
    question: str = Form(..., description="Question about the image"),
    context: Optional[str] = Form(None, description="Additional context"),
    model_name: Optional[str] = Form(None, description="Model override"),
    file: UploadFile = File(...),
    generate_diagram: bool = Form(True, description="Whether to generate diagrams"),
    generate_image: bool = Form(True, description="Whether to generate images"),
    generate_audio: bool = Form(True, description="Whether to generate audio"),
    generate_video: bool = Form(True, description="Whether to generate video"),
) -> dict:
    """
    Analyze an uploaded image or diagram.
    """
    try:
        is_valid, error_msg = validate_request_input(question)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid question: {error_msg}",
            )

        allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file.content_type}",
            )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png", mode="wb") as temp_file:
            contents = await file.read()
            temp_file.write(contents)
            temp_path = temp_file.name

        try:
            logger.info(f"Analyzing image for question: {question[:50]}...")
            handler = MultiModalHandler()
            analysis_dict = await handler.explain_image(
                question=question,
                image_path=temp_path,
                context=context,
                model_name=model_name,
                generate_video=generate_video
            )

            logger.info("Image analysis completed")
            return {
                "status": "success",
                "analysis": analysis_dict.get("analysis", ""),
                "usage": analysis_dict.get("usage", {}),
            }

        finally:
            Path(temp_path).unlink(missing_ok=True)

    except HTTPException:
        raise
    except AIEngineException as e:
        logger.error(f"Image analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze image",
        )
    except Exception as e:
        logger.error(f"Unexpected error analyzing image: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred",
        )


# ─── Image Generation ────────────────────────────────────────────────────────


@router.post(
    "/generate-image",
    summary="Generate Image",
    description="Generate an image using Vertex AI Imagen model based on a text prompt",
)
async def generate_image(request: AssetGenerationRequest) -> dict:
    """Generate image from a prompt."""
    try:
        prompt_preview = str(request.prompt)[:50]
        logger.info(f"Processing image generation request: {prompt_preview}...")

        is_valid, error_msg = validate_request_input(request.prompt)
        if not is_valid:
            logger.warning(f"Validation failed: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input: {error_msg}",
            )

        client = get_gemini_client()
        result = await client.generate_image(
            prompt=request.prompt, model_name=request.model_name
        )

        logger.info("Image generated successfully")
        return {"status": "success", "data": result}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating image: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate image",
        )


@router.post(
    "/plan",
    response_model=dict,
    summary="Generate Multimodal Plan",
    description="Initial reasoning step to plan the multimodal response",
)
async def generate_plan(request: ExplanationRequest) -> dict:
    """Generate a multimodal execution plan."""
    try:
        logger.info(f"Generating plan for: {request.question[:50]}...")
        generator = ReasoningGenerator()
        result = await generator.generate_plan(
            question=request.question,
            difficulty=request.difficulty or "auto",
            generate_diagram=request.generate_diagram,
            generate_image=request.generate_image,
            generate_video=request.generate_video,
            generate_audio=request.generate_audio,
            model_name=request.model_name
        )
        if result.get("status") != "success":
            raise HTTPException(status_code=500, detail=result.get("message"))
        return result
    except Exception as e:
        logger.error(f"Plan generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-video")
async def generate_video(request: AssetGenerationRequest) -> dict:
    """Generate a video from a prompt."""
    try:
        client = get_gemini_client()
        result = await client.generate_video(prompt=request.prompt, model_name=request.model_name)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Video generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-explanation")
async def generate_text_explanation(request: AssetGenerationRequest) -> dict:
    """Generate the main text explanation."""
    try:
        client = get_gemini_client()
        # For text, we expect JSON-ish or Markdown from the specialized prompt
        result = await client.generate_content(prompt=request.prompt, model_name=request.model_name)
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Text generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-diagram")
async def generate_diagram(request: AssetGenerationRequest) -> dict:
    """Generate a diagram (Mermaid/SVG)."""
    try:
        client = get_gemini_client()
        result = await client.generate_content(prompt=request.prompt, model_name=request.model_name)
        # We might need to parse the diagram code from the response or it might be raw
        return {"status": "success", "data": result}
    except Exception as e:
        logger.error(f"Diagram generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── Endpoints Listing ───────────────────────────────────────────────────────


@router.get(
    "/endpoints",
    summary="List Available Endpoints",
    description="Get list of all available API endpoints",
)
async def list_endpoints() -> dict:
    """List all available endpoints."""
    return {
        "status": "success",
        "endpoints": {
            "GET /api/models": "List available AI models and voices",
            "POST /api/plan": "Initial reasoning step to plan the multimodal response",
            "POST /api/explain": "Generate a single explanation (legacy)",
            "POST /api/generate-image": "Generate image from text prompt",
            "POST /api/generate-video": "Generate video from text prompt",
            "POST /api/generate-explanation": "Generate text explanation from prompt",
            "POST /api/generate-diagram": "Generate diagram from prompt",
            "GET /health": "Health check",
            "GET /api/endpoints": "List all endpoints",
        },
    }
