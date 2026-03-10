"""
Gemini API client for handling AI requests.
Provides safe, typed interface to Google's Generative AI.
"""

import google.generativeai as genai
from typing import Optional
import logging
from config.settings import get_settings
from utils.exceptions import GeminiAPIError
from config.logger import setup_logger

logger = setup_logger(__name__)


class GeminiClient:
    """Client for interacting with Gemini API."""
    
    _instance: Optional['GeminiClient'] = None
    
    def __new__(cls) -> 'GeminiClient':
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize Gemini client with API key."""
        if self._initialized:
            return
        
        settings = get_settings()
        if not settings.gemini_api_key:
            raise GeminiAPIError("GEMINI_API_KEY not configured in environment")
        
        try:
            genai.configure(api_key=settings.gemini_api_key)
            self.model_name = settings.model_name
            self.model = genai.GenerativeModel(self.model_name)
            self._initialized = True
            logger.info(f"Gemini client initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise GeminiAPIError(f"Initialization failed: {str(e)}")
    
    def generate_content(self, prompt: str) -> str:
        """
        Generate content from prompt using Gemini.
        
        Args:
            prompt: The prompt text to send to Gemini
        
        Returns:
            Generated content as string
        
        Raises:
            GeminiAPIError: If API call fails
            ValueError: If prompt is empty
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        try:
            logger.debug(f"Generating content with prompt length: {len(prompt)}")
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                raise GeminiAPIError("Empty response from Gemini API")
            
            logger.debug(f"Content generated successfully, length: {len(response.text)}")
            return response.text
        
        except Exception as e:
            if "blocked" in str(e).lower():
                logger.error(f"Prompt blocked by API: {e}")
                raise GeminiAPIError(f"Prompt blocked: {str(e)}")
            logger.error(f"Gemini API error: {e}")
            raise GeminiAPIError(f"API call failed: {str(e)}")
    
    def generate_content_with_image(self, prompt: str, image_data) -> str:
        """
        Generate content from prompt and image using Gemini.
        
        Args:
            prompt: The prompt text
            image_data: Image data (PIL Image, file path, or bytes)
        
        Returns:
            Generated content as string
        
        Raises:
            GeminiAPIError: If API call fails
        """
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        try:
            logger.debug("Generating content with image")
            response = self.model.generate_content([prompt, image_data])
            
            if not response or not response.text:
                raise GeminiAPIError("Empty response from Gemini API")
            
            logger.debug("Content with image generated successfully")
            return response.text
        
        except Exception as e:
            logger.error(f"Gemini API error with image: {e}")
            raise GeminiAPIError(f"API call with image failed: {str(e)}")


# Singleton instance
_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Get or create Gemini client singleton."""
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client