"""
Test script for Google Cloud Veo video generation via Vertex AI.

Evaluates the feasibility of using Veo for generating short animated
explanation videos in ClarityLab. Uses the google-genai SDK with
Vertex AI backend (same setup as the main application).

Usage:
    cd ai_engine
    python test_veo_video.py

Prerequisites:
    - GCP authentication configured (gcloud auth application-default login)
    - GCP_PROJECT_ID set in .env (or defaults to glachackathon2026)
    - Vertex AI API enabled on the GCP project
"""

import os
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

from google import genai
from google.genai import types

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "glachackathon2026")
GCP_LOCATION = os.getenv("GCP_LOCATION", "us-central1")

# Veo model options:
#   "veo-3.1-generate-preview"  - latest, highest quality, supports audio
#   "veo-3.1-fast-generate-preview" - faster, still high quality
#   "veo-2.0-generate-001"     - stable, no audio
VEO_MODEL = "veo-2.0-generate-001"

OUTPUT_DIR = Path(__file__).parent / "test_output"
OUTPUT_FILENAME = "veo_test_video.mp4"

POLL_INTERVAL_SECONDS = 10
MAX_WAIT_SECONDS = 360  # 6 minutes max

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("veo_test")

# ---------------------------------------------------------------------------
# Educational Prompt – crafted for ClarityLab's use-case
# ---------------------------------------------------------------------------

PROMPT = """
A smooth, cinematic educational animation explaining how photosynthesis works
inside a plant leaf.

The camera begins with a wide aerial shot of a sunlit green meadow, then
slowly zooms into the surface of a single leaf until we see a cross-section
of the leaf tissue. The microscopic world comes alive as we enter a
chloroplast cell.

Inside the chloroplast, vibrant green thylakoid stacks glow softly. Golden
beams of sunlight stream through the cell membrane and strike the
chlorophyll molecules, which light up with a bright emerald pulse. Water
molecules (shown as small blue spheres) flow in from the roots through
translucent xylem channels and split apart at the thylakoid membrane,
releasing tiny oxygen bubbles that float upward.

Meanwhile, carbon dioxide molecules (shown as grey and red clusters) drift
in through the stomata pores on the leaf surface and enter the Calvin cycle,
visualized as a gentle, rotating molecular assembly line in the stroma.
Glucose molecules (glowing amber hexagons) emerge and travel outward through
the phloem.

The camera pulls back out through the leaf surface into the sunlit meadow.
Soft, warm natural lighting throughout. Studio-quality scientific animation
style with clean labels and a calm, educational atmosphere.
""".strip()

# ---------------------------------------------------------------------------
# Main test
# ---------------------------------------------------------------------------


def run_video_generation_test() -> None:
    """Run a single Veo video generation request and save the result."""

    logger.info("=" * 60)
    logger.info("  Veo Video Generation Test")
    logger.info("=" * 60)
    logger.info(f"Project   : {GCP_PROJECT_ID}")
    logger.info(f"Location  : {GCP_LOCATION}")
    logger.info(f"Model     : {VEO_MODEL}")
    logger.info(f"Prompt    : {PROMPT[:100]}...")
    logger.info("-" * 60)

    # ---- 1. Initialize client ----
    logger.info("Initializing Vertex AI genai client...")
    try:
        client = genai.Client(
            vertexai=True,
            project=GCP_PROJECT_ID,
            location=GCP_LOCATION,
        )
        logger.info("Client initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize client: {e}")
        sys.exit(1)

    # ---- 2. Submit video generation request ----
    logger.info("Submitting video generation request...")
    start_time = time.time()

    try:
        operation = client.models.generate_videos(
            model=VEO_MODEL,
            prompt=PROMPT,
            config=types.GenerateVideosConfig(
                aspect_ratio="16:9",
                number_of_videos=1,
                duration_seconds=8,
                person_generation="dont_allow",
            ),
        )
        logger.info(f"Request submitted. Operation: {operation.name}")
    except Exception as e:
        logger.error(f"Video generation request failed: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        elapsed = time.time() - start_time
        logger.info(f"Time elapsed: {elapsed:.1f}s")
        sys.exit(1)

    # ---- 3. Poll until complete ----
    logger.info(f"Polling every {POLL_INTERVAL_SECONDS}s (max {MAX_WAIT_SECONDS}s)...")
    poll_count = 0

    while not operation.done:
        elapsed = time.time() - start_time
        if elapsed > MAX_WAIT_SECONDS:
            logger.error(f"Timed out after {MAX_WAIT_SECONDS}s")
            sys.exit(1)

        poll_count += 1
        logger.info(
            f"  Poll #{poll_count} — {elapsed:.0f}s elapsed — still generating..."
        )
        time.sleep(POLL_INTERVAL_SECONDS)

        try:
            operation = client.operations.get(operation)
        except Exception as e:
            logger.error(f"Failed to poll operation: {e}")
            sys.exit(1)

    elapsed = time.time() - start_time
    logger.info(f"Generation complete! Total time: {elapsed:.1f}s")

    # ---- 4. Download and save ----
    try:
        response = operation.response
        if not response or not response.generated_videos:
            logger.error("No videos in the response.")
            logger.info(f"Full response: {response}")
            sys.exit(1)

        generated_video = response.generated_videos[0]
        video_obj = generated_video.video
        logger.info(f"Video response received.")

        # Save locally
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = OUTPUT_DIR / OUTPUT_FILENAME

        if hasattr(video_obj, 'video_bytes') and video_obj.video_bytes:
            logger.info("Saving video from video_bytes...")
            with open(output_path, "wb") as f:
                f.write(video_obj.video_bytes)
        elif hasattr(video_obj, 'uri') and video_obj.uri:
            logger.info(f"Video is at GCS URI: {video_obj.uri}")
            logger.info("Please download it manually or use GCS client.")
            # We don't have GCS client set up here, so we just log it
            return
        else:
            logger.error("Neither video_bytes nor uri found in the video object.")
            logger.info(f"Video object structure: {video_obj}")
            sys.exit(1)

        file_size = output_path.stat().st_size
        logger.info(f"Video saved to: {output_path}")
        logger.info(f"File size: {file_size / 1024:.1f} KB")

    except Exception as e:
        logger.error(f"Failed to save video: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        sys.exit(1)

    # ---- 5. Summary ----
    logger.info("")
    logger.info("=" * 60)
    logger.info("  TEST RESULTS")
    logger.info("=" * 60)
    logger.info(f"  Status        : SUCCESS")
    logger.info(f"  Model         : {VEO_MODEL}")
    logger.info(f"  Generation    : {elapsed:.1f}s")
    logger.info(f"  File size     : {file_size / 1024:.1f} KB")
    logger.info(f"  Output        : {output_path.resolve()}")
    logger.info(f"  Aspect ratio  : 16:9")
    logger.info(f"  Duration      : 8s")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Next steps:")
    logger.info("  1. Review the generated video for quality")
    logger.info("  2. Check if the educational content is accurate")
    logger.info("  3. Evaluate generation time vs. user experience")
    logger.info("  4. Compare cost with alternative approaches")
    logger.info("")


if __name__ == "__main__":
    run_video_generation_test()
