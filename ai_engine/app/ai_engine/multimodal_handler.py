"""
Multi-modal handler for processing images and text with Gemini.
Uses the official google-genai SDK via the GeminiClient.
"""

import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from PIL import Image

from config.logger import setup_logger
from ai_engine.gemini_client import get_gemini_client
from ai_engine.prompt_builder import build_image_analysis_prompt, validate_prompt
from utils.exceptions import InvalidImageError, AIEngineException

logger = setup_logger(__name__)


class MultiModalHandler:
    """Handle multi-modal content (images + text) with Gemini."""
    
    def __init__(self):
        """Initialize multi-modal handler."""
        self.client = get_gemini_client()
        logger.debug("MultiModalHandler initialized")
    
    async def explain_image(
        self,
        question: str,
        image_path: str,
        context: Optional[str] = None,
        model_name: Optional[str] = None,
        generate_diagram: bool = True,
        generate_image: bool = True,
        generate_audio: bool = True,
        generate_video: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze an image or diagram.
        """
        try:
            # Build prompt
            prompt = build_image_analysis_prompt(
                question=question,
                context=context,
                generate_diagram=generate_diagram,
                generate_image=generate_image,
                generate_audio=generate_audio,
                generate_video=generate_video
            )
            validate_prompt(prompt)
            
            # Generate explanation using the migrated GeminiClient
            logger.debug(f"Generating image analysis for question: {question[:50]}...")
            response_data = await self.client.generate_content_with_image(
                prompt=prompt, 
                image_path=image_path,
                model_name=model_name
            )
            
            logger.info("Image explained successfully")
            return {
                "analysis": response_data["text"],
                "usage": response_data.get("usage", {})
            }
        
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise AIEngineException(f"Image processing failed: {str(e)}")
    
    def compare_images(
        self,
        question: str,
        image_paths: List[str],
        model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare multiple diagrams/images.
        
        Args:
            question: Question about images
            image_paths: List of image file paths
            model_name: Optional override for the model to use
        
        Returns:
            Dictionary with comparison analysis and usage stats
        
        Raises:
            InvalidImageError: If images are invalid
            AIEngineException: If API call fails
        """
        if not image_paths or len(image_paths) < 2:
            raise ValueError("At least 2 images required for comparison")
        
        try:
            images = []
            for path in image_paths:
                image_path_obj = Path(path)
                if not image_path_obj.exists():
                    raise InvalidImageError(f"Image not found: {path}")
                
                logger.debug(f"Loading image: {path}")
                images.append(Image.open(image_path_obj))
            
            # Build comparison prompt
            prompt = f"""You are an expert educator. Compare these {len(images)} diagrams/images and answer:

{question}

Provide a detailed analysis that:
1. Identifies key elements in each image
2. Highlights similarities and differences
3. Explains the concepts shown
4. Discusses implications of the differences
5. Suggests learning insights"""
            
            # The new SDK is clean. We use our client's underlying sdk client for flexibility
            # or we could extend the client to handle parts. Let's use the underlying client.
            logger.debug(f"Generating comparison for {len(images)} images")
            
            sdk_client = self.client.client
            model = model_name or self.client.default_model
            
            response = sdk_client.models.generate_content(
                model=model,
                contents=images + [prompt]
            )
            
            if not response or not response.text:
                raise AIEngineException("Empty response from API")
                
            usage = {
                "prompt_tokens": response.usage_metadata.prompt_token_count if response.usage_metadata else 0,
                "completion_tokens": response.usage_metadata.candidates_token_count if response.usage_metadata else 0,
                "total_tokens": response.usage_metadata.total_token_count if response.usage_metadata else 0
            }
            
            logger.info("Image comparison completed")
            return {
                "analysis": response.text,
                "usage": usage
            }
        
        except Exception as e:
            logger.error(f"Error comparing images: {e}")
            raise AIEngineException(f"Image comparison failed: {str(e)}")
    
    @staticmethod
    def validate_image_file(image_path: str) -> bool:
        """Validate if path exists and can be opened as image."""
        try:
            path = Path(image_path)
            if not path.exists():
                return False
            Image.open(path)
            return True
        except Exception:
            return False