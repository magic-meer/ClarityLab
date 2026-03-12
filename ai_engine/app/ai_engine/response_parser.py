"""
Response parsing and validation module.
Handles parsing and validating Gemini API responses.
"""

import json
import logging
from typing import Dict, Any, Optional
from utils.exceptions import ResponseParsingError
from config.logger import setup_logger

logger = setup_logger(__name__)


class ResponseParser:
    """Parse and validate API responses."""

    # Fields that must be plain strings (not objects/dicts)
    STRING_FIELDS = {
        "topic", "difficulty", "explanation",
        "diagram_type", "diagram_code",
        "image_prompt",
        "narration_script",
    }

    @staticmethod
    def _obj_to_str(value: Any) -> str:
        """Convert a non-string value to a readable string."""
        if isinstance(value, dict):
            # Prefer common prose keys; fall back to JSON dump
            for key in ("description", "text", "content", "summary", "body", "value"):
                if key in value and isinstance(value[key], str):
                    return value[key]
            return json.dumps(value)
        if isinstance(value, list):
            return " ".join(ResponseParser._obj_to_str(v) for v in value)
        return str(value)

    @classmethod
    def normalize_string_fields(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure all fields that should be strings ARE strings.
        The model occasionally returns objects or lists for these fields.
        """
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

        Args:
            response_text: Raw response text from API

        Returns:
            Parsed JSON as dictionary

        Raises:
            ResponseParsingError: If parsing fails
        """
        if not response_text or not response_text.strip():
            raise ResponseParsingError("Empty response text")

        try:
            # Try direct JSON parsing first
            return json.loads(response_text)
        except json.JSONDecodeError:
            logger.debug("Direct JSON parsing failed, attempting extraction")

        try:
            # Try extracting JSON from markdown code blocks
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                if json_end != -1:
                    json_str = response_text[json_start:json_end].strip()
                    return json.loads(json_str)

            # Try extracting from regular code blocks
            if "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                if json_end != -1:
                    json_str = response_text[json_start:json_end].strip()
                    return json.loads(json_str)

        except json.JSONDecodeError as e:
            logger.error(f"JSON extraction failed: {e}")

        raise ResponseParsingError("Could not extract valid JSON from response")

    def validate_explanation_response(
        self,
        data: Dict[str, Any],
        required_fields: Optional[list] = None
    ) -> bool:
        """
        Validate explanation response structure.

        Args:
            data: Response data to validate
            required_fields: List of required field names

        Returns:
            True if valid

        Raises:
            ResponseParsingError: If validation fails
        """
        if required_fields is None:
            required_fields = [
                "topic",
                "explanation",
                "key_points",
                "follow_up_questions"
            ]

        if not isinstance(data, dict):
            raise ResponseParsingError("Response must be a dictionary")

        # Normalize string fields BEFORE validation so type checks pass
        self.normalize_string_fields(data)

        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            raise ResponseParsingError(f"Missing required fields: {missing_fields}")

        # Type validation
        if not isinstance(data.get("key_points"), list):
            raise ResponseParsingError("key_points must be a list")

        if not isinstance(data.get("follow_up_questions"), list):
            raise ResponseParsingError("follow_up_questions must be a list")

        return True

    # Backward-compatible alias
    validate_physics_response = validate_explanation_response
