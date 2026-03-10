╔═══════════════════════════════════════════════════════════════════════════════╗
║                     PROJECT STRUCTURE & ARCHITECTURE                           ║
║                      Physics AI Explainer v1.0                                 ║
╚═══════════════════════════════════════════════════════════════════════════════╝


PROJECT DIRECTORY TREE
═══════════════════════════════════════════════════════════════════════════════

e:\Hackathon\
│
├── 📄 main.py                          ⭐ MAIN ENTRY POINT
│   └─ FastAPI application with middleware, logging, health checks
│   └─ Run with: python main.py
│   └─ Port: 8000 (configurable)
│
├── 📄 requirements.txt                 📦 DEPENDENCIES
│   └─ google-generativeai>=0.7.0
│   └─ fastapi>=0.104.0
│   └─ uvicorn>=0.24.0
│   └─ pydantic>=2.0.0
│   └─ python-dotenv>=1.0.0
│   └─ pillow>=10.0.0
│
├── 📄 .env.example                     ⚙️  CONFIG TEMPLATE
│   └─ Copy to .env and add GEMINI_API_KEY
│
├── 📄 .env                             🔐 ACTUAL CONFIG (optional)
│   └─ Create with your actual values
│
│
├── 📂 ai_engine/                       🧠 CORE AI LOGIC
│   │
│   ├── 📄 __init__.py                  Module exports
│   │
│   ├── 📄 gemini_client.py             🔌 Gemini API Client
│   │   ├─ Class: GeminiClient (Singleton pattern)
│   │   ├─ Methods:
│   │   │  ├─ __init__() - Initialize with API key
│   │   │  ├─ generate_content(prompt: str) -> str
│   │   │  └─ generate_content_with_image(prompt: str, image) -> str
│   │   └─ Uses custom exceptions for error handling
│   │
│   ├── 📄 explanation_generator.py     🎯 Main Generator
│   │   ├─ Class: PhysicsExplanationGenerator
│   │   ├─ Methods:
│   │   │  ├─ generate_explanation() - Generate single explanation
│   │   │  └─ generate_bulk_explanations() - Multiple explanations
│   │   └─ Function: generate_physics_explanation() - Convenience wrapper
│   │
│   ├── 📄 prompt_builder.py            📝 Prompt Construction
│   │   ├─ Function: build_physics_prompt() - Main builder
│   │   ├─ Function: build_image_analysis_prompt() - For images
│   │   ├─ Function: validate_prompt() - Validation
│   │   └─ Constants: DIFFICULTY_LEVELS, JSON_FORMAT_TEMPLATE
│   │
│   ├── 📄 multimodel_handler.py        🖼️  Image Processing
│   │   ├─ Class: MultiModalHandler
│   │   ├─ Methods:
│   │   │  ├─ explain_image() - Analyze single image
│   │   │  ├─ compare_images() - Compare multiple images
│   │   │  └─ validate_image_file() - Static validation method
│   │
│   ├── 📄 response_parser.py           📊 Response Handling
│   │   ├─ Class: ResponseParser
│   │   ├─ Methods:
│   │   │  ├─ parse_json_response() - Extract JSON from response
│   │   │  └─ validate_physics_response() - Validate structure
│   │   └─ Handles markdown code blocks and format variations
│   │
│   ├── 📄 exceptions.py                ⚠️ CUSTOM EXCEPTIONS
│   │   ├─ AIEngineException (base)
│   │   ├─ GeminiAPIError
│   │   ├─ InvalidPromptError
│   │   ├─ ResponseParsingError
│   │   └─ InvalidImageError
│   │
│   ├── 📄 logger.py                    📝 LOGGING SYSTEM
│   │   └─ Function: setup_logger() - Configure logging
│   │   └─ Features: Console & file output, configurable levels
│   │
│   └── 📄 test.py                      🧪 TEST MODULE
│       ├─ Function: test_explanation() - Test generation
│       └─ Function: test_error_handling() - Test error cases
│
│
├── 📂 api/                             🌐 REST API LAYER
│   │
│   ├── 📄 __init__.py                  Module marker
│   │
│   └── 📄 api_routes.py                🛣️ API ENDPOINTS
│       ├─ POST /api/explain
│       │  └─ Generate single explanation
│       ├─ POST /api/explain/bulk
│       │  └─ Generate multiple explanations
│       ├─ POST /api/analyze-image
│       │  └─ Analyze physics diagram
│       ├─ GET /api/endpoints
│       │  └─ List all endpoints
│       └─ All endpoints with comprehensive error handling
│
│
├── 📂 schemas/                        📋 DATA VALIDATION
│   │
│   ├── 📄 __init__.py                 Module exports
│   │
│   ├── 📄 request_schema.py            ✅ REQUEST MODELS
│   │   ├─ ExplanationRequest - Single explanation
│   │   ├─ ImageAnalysisRequest - Image analysis
│   │   └─ BulkExplanationRequest - Multiple explanations
│   │   └─ All with field validators and examples
│   │
│   ├── 📄 response_schema.py           📤 RESPONSE MODELS
│   │   └─ ExplanationResponse
│   │   └─ Structured with all output fields
│   │
│   └── 📄 response_schema.json         (JSON schema reference)
│
│
├── 📂 config/                         ⚙️ CONFIGURATION
│   │
│   ├── 📄 __init__.py                 Module exports
│   │
│   └── 📄 settings.py                 🔧 SETTINGS MANAGEMENT
│       ├─ Class: Settings
│       │  ├─ Attributes: gemini_api_key, model_name, debug_mode, log_level
│       │  ├─ Method: _validate_settings() - Validation
│       │  └─ Method: to_dict() - Export settings
│       └─ Function: get_settings() - Get cached singleton
│
│
├── 📂 utils/                          🛠️ UTILITIES
│   │
│   └── 📄 validators.py               ✔️ VALIDATION UTILITIES
│       ├─ Class: QuestionValidator - Question validation
│       ├─ Class: DifficultyValidator - Difficulty validation
│       ├─ Function: validate_request_input() - Combined validation
│       └─ Function: sanitize_question() - Input sanitization
│
│
├── 📂 prompts/                        📝 PROMPT TEMPLATES
│   └── 📄 pysics_prompts.txt (Reference, main prompts in code)
│
│
├── 📂 env/                            🐍 PYTHON ENVIRONMENT
│   └─ Conda/pip environment files
│   └─ Used for project isolation
│
│
├── 📄 README.md                       📚 FULL DOCUMENTATION
│   └─ Complete guide, API docs, examples, architecture
│
├── 📄 QUICK_START.md                  🚀 QUICK REFERENCE
│   └─ Setup, examples, troubleshooting, quick reference
│
├── 📄 REFACTORING_SUMMARY.md          📋 REFACTORING DETAILS
│   └─ Detailed list of all changes and improvements
│
├── 📄 COMPLETION_REPORT.md            ✅ COMPLETION REPORT
│   └─ Final verification and status report
│
└── 📄 STRUCTURE.md                    📂 THIS FILE
    └─ Project structure and navigation guide


MAIN ENTRY POINTS & API USAGE
═══════════════════════════════════════════════════════════════════════════════


1. RUNNING THE APPLICATION
─────────────────────────────────────────────────────────────────────────────

   # Setup
   $ cd e:\Hackathon
   $ python -m venv env
   $ env\Scripts\activate  # Windows
   $ pip install -r requirements.txt

   # Configure
   $ cp .env.example .env
   $ # Edit .env with your GEMINI_API_KEY

   # Run
   $ python main.py

   # Access
   - API: http://localhost:8000
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - Health: http://localhost:8000/health


2. USING THE PYTHON API
─────────────────────────────────────────────────────────────────────────────

   from ai_engine import generate_physics_explanation

   result = generate_physics_explanation(
       question="Explain quantum tunneling",
       difficulty="intermediate"
   )

   if result["status"] == "success":
       data = result["data"]
       print(f"Topic: {data['topic']}")
       print(f"Explanation: {data['explanation']}")


3. USING THE REST API
─────────────────────────────────────────────────────────────────────────────

   # Generate Explanation
   curl -X POST "http://localhost:8000/api/explain" \
     -H "Content-Type: application/json" \
     -d '{
       "question": "Explain photoelectric effect",
       "difficulty": "beginner"
     }'

   # Generate Multiple Explanations
   curl -X POST "http://localhost:8000/api/explain/bulk" \
     -H "Content-Type: application/json" \
     -d '{
       "questions": [
         "What is Newton first law?",
         "Explain gravity"
       ],
       "difficulty": "beginner"
     }'

   # Analyze Image
   curl -X POST "http://localhost:8000/api/analyze-image" \
     -F "file=@diagram.png" \
     -F "question=What physics is shown?"

   # Health Check
   curl "http://localhost:8000/health"


DIFFICULTY LEVELS
═════════════════════════════════════════════════════════════════════════════

   "beginner"      → High school level explanations
   "intermediate"  → Early undergraduate level
   "advanced"      → Upper-level undergraduate or graduate level
   "expert"        → Expert audience


CLASS HIERARCHY & RELATIONSHIPS
═════════════════════════════════════════════════════════════════════════════

   AIEngineException (base)
   ├── GeminiAPIError (API failures)
   ├── InvalidPromptError (Validation)
   ├── ResponseParsingError (Parsing)
   └── InvalidImageError (Image processing)

   Logger Configuration
   └── setup_logger() → logging.Logger

   Singleton Pattern
   ├── GeminiClient → get_gemini_client()
   └── Settings → get_settings()

   API
   ├── FastAPI (main app)
   ├── APIRouter (routes in api_routes.py)
   └── 6 Endpoints (explain, bulk, analyze-image, health, config, endpoints)


WORKFLOW DIAGRAM
═════════════════════════════════════════════════════════════════════════════

   User Request
        ↓
   API Endpoint (api_routes.py)
        ↓
   Input Validation (schemas + validators.py)
        ↓
   Generate/Analyze (explanation_generator.py or multimodel_handler.py)
        ↓
   Build Prompt (prompt_builder.py)
        ↓
   Call Gemini API (gemini_client.py)
        ↓
   Parse Response (response_parser.py)
        ↓
   Return Result to User
        ↓
   Logging & Monitoring (logger.py)


ERROR HANDLING FLOW
═════════════════════════════════════════════════════════════════════════════

   Exception Raised
        ↓
   Custom Exception Type Check
        ├─ GeminiAPIError → 500 Internal Server Error
        ├─ InvalidPromptError → 400 Bad Request
        ├─ ResponseParsingError → 500 Internal Server Error
        └─ InvalidImageError → 400 Bad Request
        ↓
   Log with Context (logger.py)
        ↓
   User-Friendly Error Response


PERFORMANCE OPTIMIZATIONS
═════════════════════════════════════════════════════════════════════════════

   [Singleton Pattern]
   GeminiClient → Single instance → Reduced connection overhead

   [LRU Cache]
   get_settings() → Cached after first call → Zero overhead retrieval

   [Async/Await]
   FastAPI endpoints → Handle multiple concurrent requests efficiently

   [Smart Logging]
   Configurable levels → Minimal overhead in production


KEY FILES TO UNDERSTAND
═════════════════════════════════════════════════════════════════════════════

   1. main.py
      ├─ Entry point
      ├─ FastAPI configuration
      ├─ Middleware setup (CORS)
      ├─ Event handlers (startup/shutdown)
      └─ Health/config endpoints

   2. ai_engine/explanation_generator.py
      ├─ Core logic for generating explanations
      ├─ Orchestrates other modules
      └─ Error handling and recovery

   3. ai_engine/gemini_client.py
      ├─ Singleton API client
      ├─ Direct Gemini interaction
      ├─ Error mapping to custom exceptions
      └─ Image handling

   4. api/api_routes.py
      ├─ REST API endpoints
      ├─ Request validation
      ├─ Response formatting
      ├─ HTTP status codes
      └─ Error details

   5. schemas/request_schema.py
      ├─ Input validation models
      ├─ Field validators
      ├─ Type checking
      └─ Example values


TESTING & VERIFICATION
═════════════════════════════════════════════════════════════════════════════

   Run Tests:
   $ python -m ai_engine.test

   Manual Testing:
   1. Open http://localhost:8000/docs
   2. Click "Try it out" on endpoints
   3. Fill in parameters
   4. Execute and view response


CONFIGURATION OPTIONS
═════════════════════════════════════════════════════════════════════════════

   Environment Variable          Default         Description
   ─────────────────────────────────────────────────────────────────
   GEMINI_API_KEY               (required)       Google Gemini API key
   MODEL_NAME                   gemini-1.5-pro   Model to use
   DEBUG_MODE                   false            Enable debug logging
   LOG_LEVEL                    INFO             Logging level


DIRECTORY ORGANIZATION RATIONALE
═════════════════════════════════════════════════════════════════════════════

   ai_engine/     → Self-contained AI logic module
   api/           → FastAPI REST API layer
   schemas/       → Data validation (Pydantic models)
   config/        → Application configuration
   utils/         → Shared utilities and helpers
   prompts/       → Prompt templates (reference)
   env/           → Python environment

   This structure ensures:
   - Clear separation of concerns
   - Easy testing (each module is independent)
   - Scalability (easy to add new features)
   - Maintainability (intuitive organization)
   - Reusability (modules can be used independently)


DEPENDENCY RELATIONSHIPS
═════════════════════════════════════════════════════════════════════════════

   main.py
   ├── config/settings.py ────────────────────── Load configuration
   ├── api/api_routes.py
   │   ├── ai_engine/explanation_generator.py
   │   │   ├── ai_engine/gemini_client.py ────── API client (singleton)
   │   │   ├── ai_engine/prompt_builder.py ──── Build prompts
   │   │   ├── ai_engine/response_parser.py ─── Parse responses
   │   │   └── ai_engine/exceptions.py ─────── Exception types
   │   ├── ai_engine/multimodel_handler.py
   │   │   └── ai_engine/gemini_client.py
   │   ├── schemas/request_schema.py ────────── Validate requests
   │   └── utils/validators.py ──────────────── Custom validators
   └── ai_engine/logger.py ──────────────────── Setup logging


NEXT STEPS
═════════════════════════════════════════════════════════════════════════════

   To extend or deploy:

   1. Add Database Support
      → Create models in new models/ directory
      → Add repository pattern for data access

   2. Add Caching
      → Redis integration
      → Cache explanations for common questions

   3. Add Authentication
      → JWT tokens in security.py
      → Update API routes with auth middleware

   4. Containerization
      → Create Dockerfile
      → Docker Compose for multi-service setup

   5. Deployment
      → Cloud provider setup (AWS, GCP, Azure)
      → Kubernetes manifest files
      → CI/CD pipeline

   6. Monitoring
      → Prometheus metrics
      → ELK stack for logging
      → Sentry for error tracking


═════════════════════════════════════════════════════════════════════════════
See README.md for full documentation and QUICK_START.md for quick reference
═════════════════════════════════════════════════════════════════════════════
