"""
Configuration management for Physics AI Explainer.
Handles environment variables and application settings.
"""

import os
from dotenv import load_dotenv
from functools import lru_cache
from typing import Optional
import logging

logger = logging.getLogger(__name__)

load_dotenv()


class Settings:
    """Application settings with validation."""
    
    def __init__(self):
        self.gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
        self.model_name: str = os.getenv("MODEL_NAME", "gemini-1.5-pro")
        self.debug_mode: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        
        self._validate_settings()
    
    def _validate_settings(self) -> None:
        """Validate that all required settings are present."""
        if not self.gemini_api_key:
            logger.warning("GEMINI_API_KEY not set in environment variables")
    
    def to_dict(self) -> dict:
        """Convert settings to dictionary."""
        return {
            "gemini_api_key": "***" if self.gemini_api_key else "NOT_SET",
            "model_name": self.model_name,
            "debug_mode": self.debug_mode,
            "log_level": self.log_level,
        }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
