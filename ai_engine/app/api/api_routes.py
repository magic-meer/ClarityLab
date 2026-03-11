"""
API routes for ClarityLab AI Learning Agent.
Handles HTTP endpoints for explanation generation and image analysis.
"""

from fastapi import APIRouter, HTTPException, status, Query, File, UploadFile
from typing import Optional, List
import logging
import tempfile
from pathlib import Path

from ai_engine.explanation_generator import ExplanationGenerator
from ai_engine.multimodal_handler import MultiModalHandler
from utils.exceptions import AIEngineException
from schemas.request_schema import ExplanationRequest
from schemas.response_schema import ExplanationResponse
from utils.validators import validate_request_input, sanitize_question
from config.logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter(tags=["Explanations"])


@router.post(
    "/explain",
    response_model=dict,
    summary="Generate Explanation",
    description="Generate a comprehensive explanation for any concept or question"
)
async def explain_concept(request: ExplanationRequest) -> dict:
    """
    Generate an explanation.

    Args:
        request: ExplanationRequest with question and difficulty

    Returns:
        Explanation response with structured content
    """
    try:
        logger.info(f"Processing explanation request: {request.question[:50]}...")

        # Validate input
        is_valid, error_msg = validate_request_input(request.question, request.difficulty)
        if not is_valid:
            logger.warning(f"Validation failed: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input: {error_msg}"
            )

        # Sanitize input
        question = sanitize_question(request.question)

        # Generate explanation
        generator = ExplanationGenerator()
        result = generator.generate_explanation(
            question=question,
            difficulty=request.difficulty
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


@router.post(
    "/explain/bulk",
    response_model=list,
    summary="Generate Multiple Explanations",
    description="Generate explanations for multiple concepts"
)
async def explain_multiple(
    questions: List[str] = Query(..., description="List of questions"),
    difficulty: str = Query("beginner", description="Difficulty level")
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

            is_valid, error_msg = validate_request_input(question, difficulty)
            if not is_valid:
                logger.warning(f"Question {i} validation failed: {error_msg}")
                results.append({
                    "status": "error",
                    "error": error_msg
                })
                continue

            question = sanitize_question(question)
            result = generator.generate_explanation(question, difficulty)
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


@router.post(
    "/analyze-image",
    summary="Analyze Uploaded Image/Diagram",
    description="Analyze an image, diagram, or learning material with a specific question"
)
async def analyze_image(
    question: str = Query(..., description="Question about the image"),
    context: Optional[str] = Query(None, description="Additional context"),
    file: UploadFile = File(...)
) -> dict:
    """Analyze an uploaded image or diagram."""
    try:
        # Validate input
        is_valid, error_msg = validate_request_input(question)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid question: {error_msg}"
            )

        # Validate file
        allowed_types = {"image/jpeg", "image/png", "image/gif", "image/webp"}
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type: {file.content_type}"
            )

        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
            contents = await file.read()
            temp_file.write(contents)
            temp_path = temp_file.name

        try:
            # Analyze image
            logger.info(f"Analyzing image for question: {question[:50]}...")
            handler = MultiModalHandler()
            analysis = handler.explain_image(question, temp_path, context)

            logger.info("Image analysis completed")
            return {
                "status": "success",
                "analysis": analysis
            }

        finally:
            # Clean up temp file
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
            "POST /api/explain": "Generate a single explanation",
            "POST /api/explain/bulk": "Generate multiple explanations",
            "POST /api/analyze-image": "Analyze uploaded image/diagram",
            "GET /health": "Health check",
            "GET /config": "Get configuration",
            "GET /api/endpoints": "List all endpoints"
        }
    }