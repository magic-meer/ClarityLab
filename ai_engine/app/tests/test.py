"""
Test script for Physics AI Explainer.
Usage: python tests/test.py
"""

import sys
from pathlib import Path
import logging

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_engine.explanation_generator import PhysicsExplanationGenerator
from config.logger import setup_logger

# Setup logging
logger = setup_logger("test", level="DEBUG")


def test_explanation():
    """Test basic explanation generation."""
    logger.info("Testing physics explanation generation")
    
    generator = PhysicsExplanationGenerator()
    
    test_questions = [
        "Explain quantum tunneling",
        "What is the photoelectric effect?",
        "Describe how photosynthesis works"
    ]
    
    for question in test_questions:
        logger.info(f"Processing: {question}")
        try:
            result = generator.generate_explanation(question, difficulty="intermediate")
            
            if result.get("status") == "success":
                data = result.get("data", {})
                logger.info(f"Success! Topic: {data.get('topic', 'N/A')}")
                logger.debug(f"Explanation length: {len(data.get('explanation', ''))}")
            else:
                logger.error(f"Failed: {result.get('message', 'Unknown error')}")
        
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)


def test_error_handling():
    """Test error handling."""
    logger.info("Testing error handling")
    
    generator = PhysicsExplanationGenerator()
    
    test_cases = [
        ("", "Empty question"),
        ("123", "Too short question"),
        ("a" * 2000, "Too long question"),
    ]
    
    for question, description in test_cases:
        logger.info(f"Testing: {description}")
        try:
            result = generator.generate_explanation(question)
            logger.info(f"Result: {result.get('status')}")
        except Exception as e:
            logger.debug(f"Expected error: {type(e).__name__}")


if __name__ == "__main__":
    logger.info("Starting tests")
    
    # test_explanation()  # Uncomment to test with actual API
    test_error_handling()
    
    logger.info("Tests completed")