"""Quick test script to verify system works"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Test 1: Settings Loading
print("\n" + "="*60)
print("TEST 1: Configuration Loading")
print("="*60)
try:
    from config.settings import get_settings
    settings = get_settings()
    print("✅ Settings loaded successfully")
    print(f"   - API Key: {('*' * 20) if settings.gemini_api_key else 'NOT SET'}")
    print(f"   - Model: {settings.model_name}")
    print(f"   - Debug Mode: {settings.debug_mode}")
except Exception as e:
    print(f"❌ Error loading settings: {e}")
    sys.exit(1)

# Test 2: Gemini Client
print("\n" + "="*60)
print("TEST 2: Gemini Client Initialization")
print("="*60)
try:
    from ai_engine.gemini_client import get_gemini_client
    client = get_gemini_client()
    print("✅ Gemini client initialized")
    print(f"   - Model: {client.model_name}")
except Exception as e:
    print(f"❌ Error initializing Gemini client: {e}")
    sys.exit(1)

# Test 3: Prompt Builder
print("\n" + "="*60)
print("TEST 3: Prompt Builder")
print("="*60)
try:
    from ai_engine.prompt_builder import build_physics_prompt
    prompt = build_physics_prompt("What is gravity?", "beginner")
    print("✅ Prompt built successfully")
    print(f"   - Prompt length: {len(prompt)} characters")
    print(f"   - Contains JSON format: {'Yes' if 'JSON format' in prompt else 'No'}")
except Exception as e:
    print(f"❌ Error building prompt: {e}")
    sys.exit(1)

# Test 4: API Routes
print("\n" + "="*60)
print("TEST 4: API Routes")
print("="*60)
try:
    from api.api_routes import router
    print("✅ API routes loaded successfully")
    print(f"   - Router class: {type(router).__name__}")
except Exception as e:
    print(f"❌ Error loading API routes: {e}")
    sys.exit(1)

# Test 5: FastAPI Application
print("\n" + "="*60)
print("TEST 5: FastAPI Application")
print("="*60)
try:
    from main import app
    print("✅ FastAPI app initialized successfully")
    print(f"   - App title: {app.title}")
    print(f"   - App version: {app.version}")
except Exception as e:
    print(f"❌ Error initializing FastAPI app: {e}")
    sys.exit(1)

# Test 6: Validation
print("\n" + "="*60)
print("TEST 6: Input Validation")
print("="*60)
try:
    from schemas.request_schema import ExplanationRequest
    req = ExplanationRequest(question="Explain photosynthesis", difficulty="beginner")
    print("✅ Request validation works")
    print(f"   - Question: {req.question}")
    print(f"   - Difficulty: {req.difficulty}")
except Exception as e:
    print(f"❌ Error in request validation: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✅ ALL TESTS PASSED - System is Ready!")
print("="*60)
print("\nNext steps:")
print("1. Run: python main.py")
print("2. Visit: http://localhost:8000/docs")
print("3. Try the /api/explain endpoint")
print("\n")
