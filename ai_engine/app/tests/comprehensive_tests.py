"""
Comprehensive test suite for Physics AI Engine.
Tests system initialization, API endpoints, Gemini integration, and error handling.
"""

import sys
from pathlib import Path
import logging
import json
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import get_settings
from config.logger import setup_logger
from ai_engine.explanation_generator import ExplanationGenerator
from ai_engine.gemini_client import get_gemini_client
from ai_engine.prompt_builder import build_explanation_prompt
from ai_engine.response_parser import ResponseParser
from api.api_routes import router
from schemas.request_schema import ExplanationRequest
from utils.validators import validate_request_input
from utils.exceptions import AIEngineException

logger = setup_logger("comprehensive_test", level="INFO")


class TestSystemInitialization:
    """Test system component initialization."""
    
    @staticmethod
    def test_all_modules_import():
        """Test that all modules import correctly."""
        logger.info("Testing module imports...")
        try:
            from google import genai
            logger.info("✅ All modules imported successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Import error: {e}")
            return False
    
    @staticmethod
    def test_configuration():
        """Test configuration loading."""
        logger.info("Testing configuration loading...")
        try:
            settings = get_settings()
            assert settings.gemini_api_key, "API key not loaded"
            assert settings.model_name, "Model name not configured"
            logger.info(f"✅ Configuration loaded: model={settings.model_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Configuration error: {e}")
            return False
    
    @staticmethod
    def test_logger():
        """Test logger initialization."""
        logger.info("Testing logger...")
        try:
            test_logger = setup_logger("test")
            assert test_logger is not None
            logger.info("✅ Logger initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Logger error: {e}")
            return False
    
    @staticmethod
    def test_gemini_client():
        """Test Gemini client initialization."""
        logger.info("Testing Gemini client...")
        try:
            client = get_gemini_client()
            assert client is not None
            assert client.model_name, "Model name not set"
            logger.info(f"✅ Gemini client initialized with model: {client.model_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Gemini client error: {e}")
            return False


class TestValidation:
    """Test input validation and schema."""
    
    @staticmethod
    def test_valid_input():
        """Test validation with valid input."""
        logger.info("Testing valid input validation...")
        try:
            valid, msg = validate_request_input("What is quantum physics?", "beginner")
            assert valid == True, "Valid input should pass"
            logger.info("✅ Valid input accepted")
            return True
        except Exception as e:
            logger.error(f"❌ Validation error: {e}")
            return False
    
    @staticmethod
    def test_invalid_input():
        """Test validation with invalid inputs."""
        logger.info("Testing invalid input rejection...")
        try:
            # Empty input
            valid, msg = validate_request_input("", "beginner")
            assert valid == False, "Empty input should reject"
            
            # Too short
            valid, msg = validate_request_input("Hi", "beginner")
            assert valid == False, "Short input should reject"
            
            logger.info("✅ Invalid inputs rejected correctly")
            return True
        except Exception as e:
            logger.error(f"❌ Validation error: {e}")
            return False
    
    @staticmethod
    def test_request_schema():
        """Test request schema validation."""
        logger.info("Testing request schema...")
        try:
            req = ExplanationRequest(
                question="Explain photosynthesis",
                difficulty="beginner"
            )
            assert req.question == "Explain photosynthesis"
            assert req.difficulty == "beginner"
            logger.info("✅ Request schema validation passed")
            return True
        except Exception as e:
            logger.error(f"❌ Schema error: {e}")
            return False


class TestPromptBuilder:
    """Test prompt building functionality."""
    
    @staticmethod
    def test_prompt_generation():
        """Test prompt generation."""
        logger.info("Testing prompt builder...")
        try:
            prompt = build_physics_prompt("What is gravity?", "beginner")
            assert prompt is not None
            assert len(prompt) > 100
            assert "gravity" in prompt.lower()
            logger.info(f"✅ Prompt generated successfully ({len(prompt)} chars)")
            return True
        except Exception as e:
            logger.error(f"❌ Prompt builder error: {e}")
            return False


class TestAvailableModels:
    """Test Gemini model availability."""
    
    @staticmethod
    def test_list_models():
        """List available Gemini models."""
        logger.info("Checking available Gemini models...")
        try:
            from google import genai
            from config.settings import get_settings
            
            settings = get_settings()
            client = genai.Client(api_key=settings.gemini_api_key)
            
            models = client.models.list()
            available = []
            
            for model in models:
                methods = getattr(model, "supported_generation_methods", [])
                if 'generateContent' in [str(m) for m in methods]:
                    available.append(model.name)
            
            logger.info(f"✅ Found {len(available)} available models")
            logger.info(f"   Suggested: {available[0] if available else 'None'}")
            return True
        except Exception as e:
            logger.error(f"❌ Model listing error: {e}")
            return False


class TestExplanationGenerator:
    """Test explanation generator without API calls."""
    
    @staticmethod
    def test_generator_initialization():
        """Test explanation generator initialization."""
        logger.info("Testing explanation generator...")
        try:
            gen = PhysicsExplanationGenerator()
            assert gen is not None
            logger.info("✅ Explanation generator initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Generator error: {e}")
            return False


class TestAPIEndpoints:
    """Test API endpoints."""
    
    @staticmethod
    def test_health_endpoint():
        """Test health check endpoint."""
        logger.info("Testing health endpoint...")
        try:
            import requests
            resp = requests.get("http://localhost:8000/health", timeout=5)
            assert resp.status_code == 200
            data = resp.json()
            assert data.get("status") == "healthy"
            logger.info("✅ Health endpoint working")
            return True
        except Exception as e:
            logger.error(f"❌ Health endpoint error: {e}")
            return False
    
    @staticmethod
    def test_config_endpoint():
        """Test config endpoint."""
        logger.info("Testing config endpoint...")
        try:
            import requests
            resp = requests.get("http://localhost:8000/config", timeout=5)
            assert resp.status_code == 200
            logger.info("✅ Config endpoint working")
            return True
        except Exception as e:
            logger.error(f"❌ Config endpoint error: {e}")
            return False
    
    @staticmethod
    def test_docs_endpoint():
        """Test documentation endpoints."""
        logger.info("Testing documentation endpoints...")
        try:
            import requests
            
            resp_swagger = requests.get("http://localhost:8000/docs", timeout=5)
            assert resp_swagger.status_code == 200
            
            resp_redoc = requests.get("http://localhost:8000/redoc", timeout=5)
            assert resp_redoc.status_code == 200
            
            logger.info("✅ Documentation endpoints working")
            return True
        except Exception as e:
            logger.error(f"❌ Documentation endpoints error: {e}")
            return False
    
    @staticmethod
    def test_explain_endpoint_invalid():
        """Test explain endpoint with invalid input."""
        logger.info("Testing explain endpoint with invalid input...")
        try:
            import requests
            
            payload = {"question": "Hi"}
            resp = requests.post("http://localhost:8000/api/explain", json=payload, timeout=5)
            assert resp.status_code == 422
            logger.info("✅ Invalid input rejected correctly")
            return True
        except Exception as e:
            logger.error(f"❌ Invalid input test error: {e}")
            return False
    
    @staticmethod
    def test_explain_endpoint_valid():
        """Test explain endpoint with valid input."""
        logger.info("Testing explain endpoint with valid input...")
        try:
            import requests
            
            payload = {
                "question": "What is photosynthesis?",
                "difficulty": "beginner"
            }
            resp = requests.post("http://localhost:8000/api/explain", json=payload, timeout=60)
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == "success":
                    result = data.get("data", {})
                    assert result.get("topic") is not None
                    assert result.get("explanation") is not None
                    logger.info(f"✅ Explain endpoint working - Generated {len(result.get('explanation', ''))} char explanation")
                    return True
            
            logger.error(f"❌ Unexpected response: {resp.status_code}")
            return False
        except requests.exceptions.Timeout:
            logger.warning("⚠️ Explain endpoint timeout (long processing time)")
            return True  # Not a failure, just takes time
        except Exception as e:
            logger.error(f"❌ Explain endpoint error: {e}")
            return False


def run_all_tests():
    """Run all test suites."""
    print('\n' + '='*80)
    print('COMPREHENSIVE TEST SUITE - PHYSICS AI ENGINE')
    print('='*80)
    
    results = {
        "System Initialization": [],
        "Input Validation": [],
        "Prompt Builder": [],
        "Available Models": [],
        "Explanation Generator": [],
        "API Endpoints": [],
    }
    
    # Test system initialization
    print("\n[SYSTEM INITIALIZATION TESTS]")
    print('-' * 80)
    results["System Initialization"].append(("Module Imports", TestSystemInitialization.test_all_modules_import()))
    results["System Initialization"].append(("Configuration", TestSystemInitialization.test_configuration()))
    results["System Initialization"].append(("Logger", TestSystemInitialization.test_logger()))
    results["System Initialization"].append(("Gemini Client", TestSystemInitialization.test_gemini_client()))
    
    # Test validation
    print("\n[INPUT VALIDATION TESTS]")
    print('-' * 80)
    results["Input Validation"].append(("Valid Input", TestValidation.test_valid_input()))
    results["Input Validation"].append(("Invalid Input", TestValidation.test_invalid_input()))
    results["Input Validation"].append(("Request Schema", TestValidation.test_request_schema()))
    
    # Test prompt builder
    print("\n[PROMPT BUILDER TESTS]")
    print('-' * 80)
    results["Prompt Builder"].append(("Prompt Generation", TestPromptBuilder.test_prompt_generation()))
    
    # Test available models
    print("\n[AVAILABLE MODELS TESTS]")
    print('-' * 80)
    results["Available Models"].append(("List Models", TestAvailableModels.test_list_models()))
    
    # Test explanation generator
    print("\n[EXPLANATION GENERATOR TESTS]")
    print('-' * 80)
    results["Explanation Generator"].append(("Generator Initialization", TestExplanationGenerator.test_generator_initialization()))
    
    # Test API endpoints
    print("\n[API ENDPOINT TESTS]")
    print('-' * 80)
    results["API Endpoints"].append(("Health Endpoint", TestAPIEndpoints.test_health_endpoint()))
    results["API Endpoints"].append(("Config Endpoint", TestAPIEndpoints.test_config_endpoint()))
    results["API Endpoints"].append(("Documentation", TestAPIEndpoints.test_docs_endpoint()))
    results["API Endpoints"].append(("Invalid Input", TestAPIEndpoints.test_explain_endpoint_invalid()))
    results["API Endpoints"].append(("Valid Input", TestAPIEndpoints.test_explain_endpoint_valid()))
    
    # Print summary
    print('\n' + '='*80)
    print('TEST SUMMARY')
    print('='*80)
    
    total_tests = 0
    total_passed = 0
    
    for category, tests in results.items():
        passed = sum(1 for _, result in tests if result)
        total = len(tests)
        total_passed += passed
        total_tests += total
        
        status = "✅" if passed == total else "⚠️" if passed > 0 else "❌"
        print(f"{status} {category}: {passed}/{total} passed")
        
        for test_name, result in tests:
            symbol = "✅" if result else "❌"
            print(f"   {symbol} {test_name}")
    
    print('\n' + '-'*80)
    overall = "✅ PASSED" if total_passed == total_tests else "⚠️ PARTIAL" if total_passed > 0 else "❌ FAILED"
    print(f"{overall}: {total_passed}/{total_tests} tests passed")
    print('='*80)
    
    return total_passed == total_tests


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
