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

DEFAULT_IMAGE_MODEL = "publishers/google/models/imagen-3.0-generate-002"
DEFAULT_DIAGRAM_IMAGE_MODEL = "publishers/google/models/imagen-4.0-ultra-generate-001"
DEFAULT_VIDEO_MODEL = "publishers/google/models/veo-3.1-generate-001"


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
            # Sync client for long-running operations that might have buggy aio support
            self.sync_client = genai.Client(
                vertexai=True,
                project=self.settings.gcp_project_id,
                location=self.settings.gcp_location,
            )
            self.default_model = self.settings.model_name
            logger.info(
                f"Gemini client initialized for Vertex AI with project: {self.settings.gcp_project_id}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            raise GeminiAPIError(f"Initialization failed: {str(e)}")

    async def generate_content(
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

            # Use await for the async call via the .aio property
            response = await self.client.aio.models.generate_content(
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

    async def generate_content_with_image(
        self, prompt: str, image_path: str, model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate text content based on an image and a prompt.

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

            response = await self.client.aio.models.generate_content(
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

    async def generate_image(
        self, prompt: str, model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate an image from a text prompt.
        """
        model = model_name or DEFAULT_IMAGE_MODEL
        try:
            prompt_preview = str(prompt)[:50]
            logger.info(f"Generating image (model: {model}) for: {prompt_preview}...")
            import base64

            result = await self.client.aio.models.generate_images(
                model=model,
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

    async def generate_video(
        self, prompt: str, model_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a video from a text prompt using Veo on Vertex AI.
        Uses synchronous operation in a thread to bypass suspected .aio endpoint issues.
        """
        model = model_name or DEFAULT_VIDEO_MODEL
        try:
            logger.info(f"Submitting video generation (Sync-Threaded) using model: {model}")
            import base64
            import asyncio
            import time

            def _generate():
                # This uses the same logic as the working test script
                operation = self.sync_client.models.generate_videos(
                    model=model,
                    prompt=prompt,
                    config=types.GenerateVideosConfig(
                        aspect_ratio="16:9",
                        number_of_videos=1,
                        duration_seconds=8,
                        person_generation="dont_allow",
                    ),
                )
                
                logger.info(f"Video operation started: {operation.name}")
                
                # Poll synchronously within the thread
                start_time = time.time()
                while not operation.done:
                    if time.time() - start_time > 600: # 10 min timeout
                        raise TimeoutError("Video generation timed out")
                    time.sleep(10)
                    operation = self.sync_client.operations.get(operation)
                
                return operation.response

            # Run the synchronous polling in a separate thread
            response = await asyncio.to_thread(_generate)

            if not response or not response.generated_videos:
                raise GeminiAPIError("No videos were generated.")

            generated_video = response.generated_videos[0]
            video_obj = generated_video.video

            if hasattr(video_obj, "video_bytes") and video_obj.video_bytes:
                video_b64 = base64.b64encode(video_obj.video_bytes).decode("utf-8")
                return {"video_base64": video_b64, "mime_type": "video/mp4"}
            elif hasattr(video_obj, "uri") and video_obj.uri:
                return {"video_uri": video_obj.uri, "mime_type": "video/mp4"}
            else:
                raise GeminiAPIError("No video data found in response.")

        except Exception as e:
            logger.error(f"Gemini API video generation error: {e}", exc_info=True)
            raise GeminiAPIError(f"Video generation failed: {str(e)}")


# Singleton instance
_client: Optional[GeminiClient] = None


def get_gemini_client() -> GeminiClient:
    """Get or create the Gemini client singleton."""
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client
