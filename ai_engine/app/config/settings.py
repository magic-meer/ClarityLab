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
        self.gcp_project_id: str = os.getenv("GCP_PROJECT_ID", "")
        self.gcp_location: str = os.getenv("GCP_LOCATION", "us-central1")
        self.model_name: str = os.getenv("MODEL_NAME", "gemini-1.5-pro")
        self.debug_mode: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        
        self._validate_settings()
    
    def _validate_settings(self) -> None:
        """Validate that all required settings are present."""
        if not self.gcp_project_id:
            logger.warning("GCP_PROJECT_ID not set in environment variables. Vertex AI calls may fail.")
    
    def to_dict(self) -> dict:
        """Convert settings to dictionary."""
        return {
            "gcp_project_id": self.gcp_project_id,
            "gcp_location": self.gcp_location,
            "model_name": self.model_name,
            "debug_mode": self.debug_mode,
            "log_level": self.log_level,
        }


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
