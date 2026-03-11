"""
API routes for ClarityLab AI Learning Agent.
Handles HTTP endpoints for explanation generation and image analysis.
"""

from fastapi import APIRouter, HTTPException, status, Query, File, UploadFile
from typing import Optional, List
import logging
import tempfile
import base64
from pathlib import Path

from google import genai
from config.settings import get_settings

from ai_engine.explanation_generator import ExplanationGenerator
from ai_engine.multimodal_handler import MultiModalHandler
from ai_engine.gemini_client import get_gemini_client
from utils.exceptions import AIEngineException
from schemas.request_schema import ExplanationRequest
from utils.validators import validate_request_input, sanitize_question
from config.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(tags=["Explanations"])


# ─── Dynamic Model Listing ──────────────────────────────────────────────────

@router.get(
    "/models",
    summary="List Available Models",
    description="Fetch available Gemini text models, image models, and audio voices"
)
async def list_models() -> dict:
    """List available models from the Gemini API and supported voices."""
    try:
        text_models = []
        image_models = []
        
        settings = get_settings()
        client = genai.Client(api_key=settings.gemini_api_key)
        
        for m in client.models.list():
            info = {
                "name": m.name.replace("models/", ""),
                "display_name": m.display_name,
                "description": getattr(m, "description", ""),
            }
            methods = getattr(m, "supported_generation_methods", [])
            methods_str = [str(method) for method in methods]
            
            if "generateContent" in methods_str:
                text_models.append(info)
            if "generateImages" in methods_str or "imagen" in m.name.lower():
                image_models.append(info)
        
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
        
        return {
            "status": "success",
            "text_models": text_models,
            "image_models": image_models,
            "audio_voices": audio_voices,
        }
    except Exception as e:
        logger.error(f"Error listing models: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list models"
        )


# ─── Explain ─────────────────────────────────────────────────────────────────

@router.post(
    "/explain",
    response_model=dict,
    summary="Generate Explanation",
    description="Generate a comprehensive explanation for any concept or question"
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
                detail=f"Invalid input: {error_msg}"
            )

        question = sanitize_question(request.question)

        generator = ExplanationGenerator()
        result = generator.generate_explanation(
            question=question,
            model_name=request.model_name
        )

        if result.get("status") != "success":
            logger.error(f"Generation failed: {result.get('message')}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("message", "Failed to generate explanation")
            )

        logger.info("Explanation generated successfully")
        return {
            "status": "success",
            "data": result.get("data")
        }

    except HTTPException:
        raise
    except AIEngineException as e:
        logger.error(f"AI Engine error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process request"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


# ─── Bulk Explain ────────────────────────────────────────────────────────────

@router.post(
    "/explain/bulk",
    response_model=list,
    summary="Generate Multiple Explanations",
    description="Generate explanations for multiple concepts"
)
async def explain_multiple(
    questions: List[str] = Query(..., description="List of questions"),
    model_name: Optional[str] = Query(None, description="Model override")
) -> list:
    """Generate explanations for multiple questions."""
    try:
        if not questions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No questions provided"
            )

        if len(questions) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 questions allowed per request"
            )

        logger.info(f"Processing {len(questions)} explanation requests")

        results = []
        generator = ExplanationGenerator()
        for i, question in enumerate(questions, 1):
            logger.debug(f"Processing question {i}/{len(questions)}")

            is_valid, error_msg = validate_request_input(question)
            if not is_valid:
                logger.warning(f"Question {i} validation failed: {error_msg}")
                results.append({
                    "status": "error",
                    "error": error_msg
                })
                continue

            question = sanitize_question(question)
            result = generator.generate_explanation(question, model_name=model_name)
            results.append(result)

        logger.info(f"Processed {len(questions)} requests")
        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing multiple requests: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process requests"
        )


# ─── Image Analysis ──────────────────────────────────────────────────────────

@router.post(
    "/analyze-image",
    summary="Analyze Uploaded Image/Diagram",
    description="Analyze an image, diagram, or learning material with a specific question"
)
async def analyze_image(
    question: str = Query(..., description="Question about the image"),
    context: Optional[str] = Query(None, description="Additional context"),
    model_name: Optional[str] = Query(None, description="Model override"),
    file: UploadFile = File(...)
) -> dict:
    """Analyze an uploaded image or diagram."""
    try:
        is_valid, error_msg = validate_request_input(question)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid question: {error_msg}"
            )

        allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file.content_type}"
            )

        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            contents = await file.read()
            temp_file.write(contents)
            temp_path = temp_file.name

        try:
            logger.info(f"Analyzing image for question: {question[:50]}...")
            handler = MultiModalHandler()
            analysis_dict = handler.explain_image(question, temp_path, context, model_name=model_name)

            logger.info("Image analysis completed")
            return {
                "status": "success",
                "analysis": analysis_dict.get("analysis", ""),
                "usage": analysis_dict.get("usage", {})
            }

        finally:
            Path(temp_path).unlink(missing_ok=True)

    except HTTPException:
        raise
    except AIEngineException as e:
        logger.error(f"Image analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze image"
        )
    except Exception as e:
        logger.error(f"Unexpected error analyzing image: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


# ─── Image Generation ────────────────────────────────────────────────────────

@router.post(
    "/generate-image",
    summary="Generate Image",
    description="Generate an image using the requested descriptive prompt"
)
async def generate_image(
    prompt: str = Query(..., description="Prompt to generate an image from"),
    model_name: Optional[str] = Query("imagen-3.0-generate-001", description="Image generation model name")
) -> dict:
    """Generate an image from a prompt."""
    try:
        is_valid, error_msg = validate_request_input(prompt)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg or "Invalid prompt"
            )
            
        logger.info(f"Generating image with prompt: {prompt[:50]}...")
        
        client = get_gemini_client()
        image_bytes = client.generate_image(prompt, model_name=model_name)
        
        base64_encoded = base64.b64encode(image_bytes).decode("utf-8")
        
        logger.info("Image generation completed")
        return {
            "status": "success",
            "image_data": f"data:image/png;base64,{base64_encoded}"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error generating image: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during image generation"
        )


# ─── Endpoints Listing ───────────────────────────────────────────────────────

@router.get(
    "/endpoints",
    summary="List Available Endpoints",
    description="Get list of all available API endpoints"
)
async def list_endpoints() -> dict:
    """List all available endpoints."""
    return {
        "status": "success",
        "endpoints": {
            "GET /api/models": "List available AI models and voices",
            "POST /api/explain": "Generate a single explanation",
            "POST /api/explain/bulk": "Generate multiple explanations",
            "POST /api/analyze-image": "Analyze uploaded image/diagram",
            "POST /api/generate-image": "Generate an image from a textual prompt",
            "GET /health": "Health check",
            "GET /config": "Get configuration",
            "GET /api/endpoints": "List all endpoints"
        }
    }