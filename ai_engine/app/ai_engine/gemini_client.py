"""
Gemini API client implementation supporting multimodal inputs.
Uses the official google-genai SDK formatted for Vertex AI.
"""

from google import genai
from google.genai import types
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from config.settings import get_settings
from utils.exceptions import GeminiAPIError

logger = logging.getLogger(__name__)


class GeminiClient:
    """Wrapper for the Gemini API using google-genai SDK (Vertex AI backend)."""

    def __init__(self):
        """Initialize the Gemini client with settings."""
        self.settings = get_settings()
        try:
            # Configure specifically for Vertex AI
            self.client = genai.Client(
                vertexai=True,
                project=self.settings.gcp_project_id,
                location=self.settings.gcp_location,
            )
            self.default_model = self.settings.model_name
            logger.info(
                f"Gemini client initialized for Vertex AI with model: {self.default_model}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise GeminiAPIError(f"Initialization failed: {str(e)}")

    def generate_content(
        self, prompt: str, model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate text content from a prompt.

        Args:
            prompt: User prompt
            model_name: Optional model override

        Returns:
            Dictionary containing 'text' and 'usage' metadata
        """
        try:
            model = model_name or self.default_model
            if "/" in model:
                model = model.split("/")[-1]

            logger.debug(f"Sending text generation request using model: {model}")

            # Check if we should force JSON or use plain text
            config = types.GenerateContentConfig(
                temperature=0.7,
            )

            response = self.client.models.generate_content(
                model=model, contents=prompt, config=config
            )

            result = {
                "text": response.text,
                "usage": {
                    "prompt_tokens": response.usage_metadata.prompt_token_count
                    if response.usage_metadata
                    else 0,
                    "completion_tokens": response.usage_metadata.candidates_token_count
                    if response.usage_metadata
                    else 0,
                    "total_tokens": response.usage_metadata.total_token_count
                    if response.usage_metadata
                    else 0,
                },
            }
            return result

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise GeminiAPIError(f"Content generation failed: {str(e)}")

    def generate_content_with_image(
        self, prompt: str, image_path: str, model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate text content based on an image and a pr)ompt.

        Args:
            prompt: Question or instruction about the image
            image_path: Path to the local image file
            model_name: Optional model override

        Returns:
            Dictionary containing 'text' and 'usage' metadata
        """
        try:
            model = model_name or self.default_model
            if "/" in model:
                model = model.split("/")[-1]

            path = Path(image_path)
            if not path.exists():
                raise FileNotFoundError(f"Image not found at {image_path}")

            # The new SDK accepts PIL Images or UploadedFiles
            from PIL import Image

            img = Image.open(path)

            logger.debug(f"Sending image analyze request using model: {model}")

            response = self.client.models.generate_content(
                model=model,
                contents=[img, prompt],
                config=types.GenerateContentConfig(
                    temperature=0.2,
                ),
            )

            result = {
                "text": response.text,
                "usage": {
                    "prompt_tokens": response.usage_metadata.prompt_token_count
                    if response.usage_metadata
                    else 0,
                    "completion_tokens": response.usage_metadata.candidates_token_count
                    if response.usage_metadata
                    else 0,
                    "total_tokens": response.usage_metadata.total_token_count
                    if response.usage_metadata
                    else 0,
                },
            }
            return result

        except Exception as e:
            logger.error(f"Gemini API multimodal error: {e}")
            raise GeminiAPIError(f"Multimodal generation failed: {str(e)}")

    def generate_image(
        self, prompt: str, model_name: Optional[str] = "imagen-3.0-generate-001"
    ) -> Dict[str, Any]:
        """
        Generate an image from a text prompt.

        Args:
            prompt: Text prompt for the image.
            model_name: Optional model override (defaults to imagen-3.0-generate-001).

        Returns:
            Dictionary containing 'image_base64' and 'mime_type'.
        """
        try:
            logger.debug(f"Sending image generation request using model: {model_name}")
            import base64

            result = self.client.models.generate_images(
                model=model_name,
                prompt=prompt,
                config=types.GenerateImagesConfig(
                    number_of_images=1,
                    output_mime_type="image/jpeg",
                    aspect_ratio="1:1",
                ),
            )

            if not result.generated_images:
                raise GeminiAPIError("No images were generated.")

            generated_image = result.generated_images[0]

            # Convert bytes to base64
            image_b64 = base64.b64encode(generated_image.image.image_bytes).decode(
                "utf-8"
            )

            return {"image_base64": image_b64, "mime_type": "image/jpeg"}

        except Exception as e:
            logger.error(f"Gemini API image generation error: {e}")
            raise GeminiAPIError(f"Image generation failed: {str(e)}")

    def generate_video(
        self, prompt: str, model_name: Optional[str] = "veo-3.1-generate-preview"
    ) -> Dict[str, Any]:
        """
        Generate a video from a text prompt using Veo on Vertex AI.

        Args:
            prompt: Text prompt for the video.
            model_name: Optional model override (defaults to veo-3.1-generate-preview).

        Returns:
            Dictionary containing 'video_base64' and 'mime_type'.
        """
        try:
            logger.info(f"Sending video generation request using model: {model_name}")
            import base64
            import time

            # Start the long-running operation
            operation = self.client.models.generate_videos(
                model=model_name,
                prompt=prompt,
                config=types.GenerateVideosConfig(
                    aspect_ratio="16:9",
                    number_of_videos=1,
                    duration_seconds=8,  # 8s is standard for Veo
                ),
            )

            # Poll until complete
            logger.info(f"Waiting for video generation (Operation: {operation.name})...")
            while not operation.done:
                time.sleep(10)
                operation = self.client.operations.get(operation)

            response = operation.response
            if not response or not response.generated_videos:
                raise GeminiAPIError("No videos were generated.")

            generated_video = response.generated_videos[0]
            video_obj = generated_video.video

            if hasattr(video_obj, "video_bytes") and video_obj.video_bytes:
                # Convert bytes to base64 for frontend consumption
                video_b64 = base64.b64encode(video_obj.video_bytes).decode("utf-8")
                return {"video_base64": video_b64, "mime_type": "video/mp4"}
            elif hasattr(video_obj, "uri") and video_obj.uri:
                # Handle GCS URI if provided (though we expect bytes in Vertex AI mode)
                return {"video_uri": video_obj.uri, "mime_type": "video/mp4"}
            else:
                raise GeminiAPIError("No video data found in response.")

        except Exception as e:
            logger.error(f"Gemini API video generation error: {e}")
            raise GeminiAPIError(f"Video generation failed: {str(e)}")


# Singleton instance
_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Get or create the Gemini client singleton."""
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client
