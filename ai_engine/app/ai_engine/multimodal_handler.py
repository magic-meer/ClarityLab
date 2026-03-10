"""
Multi-modal handler for processing images and text with Gemini.
"""

import logging
from pathlib import Path
from typing import Optional, Union
from PIL import Image
import google.generativeai as genai

from config.logger import setup_logger
from ai_engine.gemini_client import get_gemini_client
from ai_engine.prompt_builder import build_image_analysis_prompt
from utils.exceptions import InvalidImageError, AIEngineException

logger = setup_logger(__name__)


class MultiModalHandler:
    """Handle multi-modal content (images + text) with Gemini."""
    
    def __init__(self):
        """Initialize multi-modal handler."""
        self.client = get_gemini_client()
        logger.debug("MultiModalHandler initialized")
    
    def explain_image(
        self,
        question: str,
        image_path: str,
        context: Optional[str] = None
    ) -> str:
        """
        Explain a physics diagram or image.
        
        Args:
            question: Question about the image
            image_path: Path to image file
            context: Additional context
        
        Returns:
            Explanation text
        
        Raises:
            InvalidImageError: If image is invalid
            AIEngineException: If API call fails
        """
        try:
            # Validate and load image
            image_path_obj = Path(image_path)
            if not image_path_obj.exists():
                raise InvalidImageError(f"Image file not found: {image_path}")
            
            if image_path_obj.suffix.lower() not in {'.jpg', '.jpeg', '.png', '.gif', '.webp'}:
                raise InvalidImageError(f"Unsupported image format: {image_path_obj.suffix}")
            
            logger.debug(f"Loading image: {image_path}")
            image = Image.open(image_path)
            
            # Build prompt
            prompt = build_image_analysis_prompt(question, context)
            
            # Generate explanation
            logger.debug("Generating image explanation")
            explanation = self.client.generate_content_with_image(prompt, image)
            
            logger.info("Image explained successfully")
            return explanation
        
        except InvalidImageError:
            raise
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise AIEngineException(f"Image processing failed: {str(e)}")
    
    def compare_images(
        self,
        question: str,
        image_paths: list[str]
    ) -> str:
        """
        Compare multiple physics diagrams/images.
        
        Args:
            question: Question about images
            image_paths: List of image file paths
        
        Returns:
            Comparison analysis
        
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
            prompt = f"""You are an expert physics educator. Compare these {len(images)} physics diagrams/images and answer:

{question}

Provide a detailed analysis that:
1. Identifies key elements in each image
2. Highlights similarities and differences
3. Explains physics concepts shown
4. Discusses implications of the differences
5. Suggests learning insights"""
            
            # Create content array with images
            content = [prompt] + images
            
            logger.debug(f"Generating comparison for {len(images)} images")
            response_text = self.client.model.generate_content(content)
            
            if not response_text or not response_text.text:
                raise AIEngineException("Empty response from API")
            
            logger.info("Image comparison completed")
            return response_text.text
        
        except Exception as e:
            logger.error(f"Error comparing images: {e}")
            raise AIEngineException(f"Image comparison failed: {str(e)}")
    
    @staticmethod
    def validate_image_file(image_path: str) -> bool:
        """
        Validate that an image file exists and is valid.
        
        Args:
            image_path: Path to image
        
        Returns:
            True if valid
        
        Raises:
            InvalidImageError: If validation fails
        """
        try:
            path = Path(image_path)
            if not path.exists():
                raise InvalidImageError(f"File not found: {image_path}")
            
            if path.suffix.lower() not in {'.jpg', '.jpeg', '.png', '.gif', '.webp'}:
                raise InvalidImageError(f"Unsupported format: {path.suffix}")
            
            # Try to open image
            Image.open(path)
            return True
        
        except InvalidImageError:
            raise
        except Exception as e:
            raise InvalidImageError(f"Invalid image: {str(e)}")