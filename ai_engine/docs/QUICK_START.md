"""
QUICK START GUIDE - Physics AI Explainer
========================================

PROJECT: Physics AI Explainer v1.0
PURPOSE: Advanced AI system for explaining physics concepts with diagrams and animations
TECH STACK: FastAPI, Pydantic, Google Gemini AI

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SETUP (3 STEPS)
===============

1. CREATE .env FILE
   $ cp .env.example .env
   $ # Edit .env and add your GEMINI_API_KEY

2. INSTALL DEPENDENCIES
   $ pip install -r requirements.txt

3. START THE SERVER
   $ python main.py
   # Server runs on http://localhost:8000

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

QUICK API EXAMPLES
==================

1️⃣  GENERATE EXPLANATION
   
   curl -X POST "http://localhost:8000/api/explain" \\
     -H "Content-Type: application/json" \\
     -d '{
       "question": "Explain quantum tunneling",
       "difficulty": "intermediate"
     }'

2️⃣  ANALYZE IMAGE
   
   curl -X POST "http://localhost:8000/api/analyze-image" \\
     -F "file=@diagram.png" \\
     -F "question=Explain the physics in this diagram" \\
     "http://localhost:8000/api/analyze-image"

3️⃣  BULK EXPLANATIONS
   
   curl -X POST "http://localhost:8000/api/explain/bulk" \\
     -H "Content-Type: application/json" \\
     -d '{
       "questions": [
         "What is photosynthesis?",
         "Explain gravity"
       ],
       "difficulty": "beginner"
     }'

4️⃣  CHECK HEALTH
   
   curl "http://localhost:8000/health"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PYTHON USAGE
============

from ai_engine import generate_physics_explanation

result = generate_physics_explanation(
    question="Explain photoelectric effect",
    difficulty="intermediate"
)

if result["status"] == "success":
    data = result["data"]
    print(f"Topic: {data['topic']}")
    print(f"Explanation: {data['explanation']}")
    print(f"Key Points: {data['key_points']}")
    print(f"Diagram Prompt: {data['diagram_prompt']}")
    for q in data['follow_up_questions']:
        print(f"- {q}")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DIFFICULTY LEVELS
=================

"beginner"      → High school level explanations
"intermediate"  → Early undergraduate level
"advanced"      → Upper-level undergraduate or graduate
"expert"        → Expert audience

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

RESPONSE FORMAT
===============

All responses follow this structure:

{
  "status": "success" | "error",
  "data": {...},           # For success responses
  "error": "error_type",   # For error responses
  "message": "details"     # For error responses
}

Success response includes:
- topic: The physics topic
- difficulty: Level used
- explanation: Full explanation
- key_points: Important concepts (list)
- diagram_prompt: Prompt for creating diagram
- animation_prompt: Prompt for animated visualization
- simulation_prompt: Interactive simulation idea
- narration_script: Audio narration
- follow_up_questions: Learning questions (list)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DOCUMENTATION
==============

📚 Main README: README.md
📚 API Docs: http://localhost:8000/docs
📚 Refactoring Details: REFACTORING_SUMMARY.md
📚 Code Docstrings: All source files

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

KEY FEATURES
============

✅ Type-safe code with full type hints
✅ Comprehensive error handling
✅ Input validation and sanitization
✅ Custom exception hierarchy
✅ Structured logging
✅ Singleton API client
✅ Multi-modal image support
✅ Bulk processing support
✅ CORS middleware
✅ Health checks
✅ Production-ready

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TROUBLESHOOTING
===============

❌ "GEMINI_API_KEY not configured"
   → Add GEMINI_API_KEY to .env file

❌ "Empty response from Gemini API"
   → Check API key quota and permissions

❌ "Invalid image format"
   → Use JPG, PNG, GIF, or WebP

❌ "Port 8000 already in use"
   → Run: uvicorn main:app --port 8001

❌ Import errors
   → Ensure you're in the correct directory and dependencies are installed

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ENDPOINTS SUMMARY
=================

POST   /api/explain           Generate single explanation
POST   /api/explain/bulk      Generate multiple explanations
POST   /api/analyze-image     Analyze physics diagram
GET    /health               Health check
GET    /config               Get configuration
GET    /api/endpoints        List all endpoints
GET    /docs                 Interactive API documentation
GET    /redoc                Alternative API documentation

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PROJECT STRUCTURE
=================

e:\\Hackathon\\
├── main.py                 # FastAPI app entry point
├── requirements.txt        # Dependencies
├── .env.example           # Env configuration template
├── README.md              # Full documentation
├── QUICK_START.md         # This file
│
├── ai_engine/             # Core AI logic
│   ├── gemini_client.py   # API client (singleton)
│   ├── explanation_generator.py
│   ├── prompt_builder.py
│   ├── response_parser.py
│   ├── multimodel_handler.py
│   ├── exceptions.py
│   ├── logger.py
│   └── test.py
│
├── api/                   # REST API
│   └── api_routes.py
│
├── schemas/              # Data models
│   ├── request_schema.py
│   └── response_schema.py
│
├── config/              # Settings
│   └── settings.py
│
└── utils/              # Utilities
    └── validators.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ADVANCED FEATURES
=================

🔍 Response Parsing
   - Extracts JSON from markdown code blocks
   - Validates response structure
   - Handles multiple formats

🛡️ Error Handling
   - Custom exception hierarchy
   - Specific error types
   - User-friendly messages

📝 Validation
   - Pydantic field validators
   - Input sanitization
   - Length constraints

🎯 Logging
   - Configurable levels
   - File and console output
   - Structured logging

🔄 Singleton Pattern
   - Single API instance
   - Reduced overhead
   - Consistent state

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

SECURITY
========

✅ Input validation and sanitization
✅ Environment variable protection
✅ Type safety
✅ CORS configuration
✅ Generic error messages
✅ Temporary file cleanup

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PERFORMANCE
===========

✅ Singleton API client
✅ LRU cache for settings
✅ Async request handling
✅ Efficient error handling
✅ No unnecessary retries

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For detailed information, see README.md or visit http://localhost:8000/docs
"""
