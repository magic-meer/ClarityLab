"""
Response parsing and validation module.
Handles parsing and validating Gemini API responses.
"""

import json
import re
import logging
from typing import Dict, Any, Optional
from utils.exceptions import ResponseParsingError
from config.logger import setup_logger

logger = setup_logger(__name__)


class ResponseParser:
    """Parse and validate API responses."""

    # Fields that must be plain strings (not objects/dicts)
    STRING_FIELDS = {
        "topic",
        "difficulty",
        "explanation",
        "diagram_type",
        "diagram_code",
        "image_prompt",
        "narration_script",
    }

    @staticmethod
    def _obj_to_str(value: Any) -> str:
        """Convert a non-string value to a readable string."""
        if isinstance(value, dict):
            for key in ("description", "text", "content", "summary", "body", "value"):
                if key in value and isinstance(value[key], str):
                    return value[key]
            return json.dumps(value)
        if isinstance(value, list):
            return " ".join(ResponseParser._obj_to_str(v) for v in value)
        return str(value)

    @classmethod
    def normalize_string_fields(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all fields that should be strings ARE strings."""
        for field in cls.STRING_FIELDS:
            if field in data and data[field] is not None:
                if not isinstance(data[field], str):
                    original = data[field]
                    data[field] = cls._obj_to_str(original)
                    logger.warning(
                        f"Field '{field}' was {type(original).__name__}, "
                        f"converted to string: {data[field][:80]}..."
                    )
        return data

    @staticmethod
    def parse_json_response(response_text: str) -> Dict[str, Any]:
        """
        Extract and parse JSON from response text.
        Handles markdown code blocks and malformed JSON.
        """
        if not response_text or not response_text.strip():
            raise ResponseParsingError("Empty response text")

        logger.debug(f"Response text sample: {response_text[:300]}...")

        # Strategy 1: Try direct JSON parsing
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass

        # Strategy 2: Extract from markdown code blocks
        # Match ```json ... ``` or ``` ... ```
        json_block_match = re.search(
            r"```json\s*\n?(.*?)\n?```", response_text, re.DOTALL
        )
        if not json_block_match:
            json_block_match = re.search(
                r"```\s*\n?(.*?)\n?```", response_text, re.DOTALL
            )

        if json_block_match:
            json_str = json_block_match.group(1).strip()
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                logger.debug(f"JSON block parse failed: {e}")
                # Try to fix common issues
                json_str = ResponseParser._fix_json_string(json_str)
                try:
                    return json.loads(json_str)
                except:
                    pass

        # Strategy 3: Find JSON between first { and last }
        first_brace = response_text.find("{")
        last_brace = response_text.rfind("}")

        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            json_candidate = response_text[first_brace : last_brace + 1]
            json_candidate = ResponseParser._fix_json_string(json_candidate)
            try:
                return json.loads(json_candidate)
            except json.JSONDecodeError as e:
                logger.debug(f"Brace extraction failed: {e}")

        # Strategy 4: Try ast.literal_eval as last resort
        try:
            import ast

            result = ast.literal_eval(response_text)
            if isinstance(result, dict):
                return result
        except Exception as e:
            logger.debug(f"literal_eval failed: {e}")

        logger.error(
            f"All parsing strategies failed. Response: {response_text[:1000]}..."
        )
        raise ResponseParsingError("Could not extract valid JSON from response")

    @staticmethod
    def _fix_json_string(json_str: str) -> str:
        """Attempt to fix common JSON formatting issues."""
        # Remove trailing commas
        json_str = re.sub(r",(\s*[}\]])", r"\1", json_str)

        # Remove single-line comments
        json_str = re.sub(r"//.*$", "", json_str, flags=re.MULTILINE)

        # Remove multi-line comments
        json_str = re.sub(r"/\*.*?\*/", "", json_str, flags=re.DOTALL)

        return json_str

    def validate_explanation_response(
        self, data: Dict[str, Any], required_fields: Optional[list] = None
    ) -> bool:
        """Validate explanation response structure."""
        if required_fields is None:
            required_fields = [
                "topic",
                "explanation",
                "key_points",
                "follow_up_questions",
            ]

        if not isinstance(data, dict):
            raise ResponseParsingError("Response must be a dictionary")

        self.normalize_string_fields(data)

        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            raise ResponseParsingError(f"Missing required fields: {missing_fields}")

        if not isinstance(data.get("key_points"), list):
            raise ResponseParsingError("key_points must be a list")

        if not isinstance(data.get("follow_up_questions"), list):
            raise ResponseParsingError("follow_up_questions must be a list")

        return True

    validate_physics_response = validate_explanation_response
