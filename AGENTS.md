# ClarityLab - Agent Guidelines

This file provides guidelines for AI agents working on the ClarityLab project.

## Project Overview

ClarityLab is a multimodal AI learning agent that provides rich, structured explanations with diagrams, animations, narration scripts, and follow-up questions. It consists of:
- **Frontend**: Next.js 16 with React 19 (in `/app`)
- **Backend**: Python FastAPI (in `/ai_engine/app`)

---

## Commands

### Frontend (Next.js)

```bash
# Install dependencies
pnpm install

# Development server (http://localhost:3000)
pnpm dev

# Production build
pnpm build

# Start production server
pnpm start
```

### Backend (Python)

```bash
# Navigate to backend directory
cd ai_engine/app

# Create virtual environment (if not exists)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r ../requirements.txt

# Run the FastAPI server (http://localhost:8000)
python main.py
```

### Testing

```bash
# Run Python tests
cd ai_engine/app
python -m pytest tests/           # With pytest (if installed)
python tests/test.py               # Direct test runner

# Run a specific test function
python -c "from tests.test import test_explanation; test_explanation()"
```

---

## Environment Configuration

### Frontend (.env.local)
```
BACKEND_URL=http://localhost:8000
```

### Backend (ai_engine/.env)
```
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini-1.5-pro
DEBUG_MODE=true
LOG_LEVEL=INFO
```

---

## Code Style Guidelines

### Python (Backend)

**Imports**
- Standard library first, then third-party, then local
- Use absolute imports from project root
```python
from config.settings import get_settings
from utils.exceptions import GeminiAPIError
```

**Types**
- Use type hints for all function signatures
- Use `Optional[T]` for nullable types
- Use `Dict[str, Any]` for flexible dictionaries

**Naming Conventions**
- `snake_case` for variables, functions, methods
- `PascalCase` for classes
- `UPPER_SNAKE_CASE` for constants

**Docstrings**
- Use triple quotes `"""..."""`
- Include Args, Returns sections for functions

**Error Handling**
- Use custom exception classes in `utils/exceptions.py`
- Raise specific exceptions with descriptive messages
- Log errors before raising

**Logging**
- Use the `logging` module with `__name__`
- Use structured logger: `logger = logging.getLogger(__name__)`

**Pydantic Models**
- Use `BaseModel` with `Field` for validation
- Include `json_schema_extra` examples
- Use `field_validator` for custom validation

### JavaScript/React (Frontend)

**Components**
- Use `"use client"` directive for client components
- Use functional components with hooks
- Keep components small and focused

**Naming**
- `camelCase` for variables and functions
- `PascalCase` for components and React components
- CSS modules use `kebab-case` for class names

**Hooks**
- Use `useState`, `useEffect`, `useRef`, `useCallback`
- Include dependency arrays in `useEffect`
- Handle cleanup in return function

**API Routes (Next.js)**
- Use `export async function POST(request)` for POST handlers
- Return `Response.json()` with proper status codes
- Validate input before processing

**Error Handling**
- Try/catch with descriptive error messages
- Return appropriate HTTP status codes (400, 500, etc.)
- Handle both expected and unexpected errors

**Styling**
- Use CSS modules (`*.module.css`)
- Use existing design tokens from `globals.css`

---

## Project Structure

```
clarity-lab/
├── app/                          # Next.js frontend
│   ├── api/                     # API routes
│   │   ├── explain/route.js
│   │   ├── analyze/route.js
│   │   └── ...
│   ├── globals.css              # Design system
│   ├── layout.js                # Root layout
│   └── page.js                  # Main chat page
│
├── ai_engine/                   # Python backend
│   ├── app/
│   │   ├── main.py             # FastAPI entry point
│   │   ├── ai_engine/          # Core AI logic
│   │   │   ├── gemini_client.py
│   │   │   ├── explanation_generator.py
│   │   │   └── ...
│   │   ├── api/                # REST API routes
│   │   ├── schemas/            # Pydantic models
│   │   ├── config/             # Settings & logger
│   │   ├── utils/              # Validators & exceptions
│   │   └── tests/              # Test files
│   └── requirements.txt
│
├── package.json
└── .env.local
```

---

## Key Patterns

### Backend API Pattern
```python
from fastapi import APIRouter, HTTPException
from schemas.request_schema import ExplanationRequest
from utils.exceptions import GeminiAPIError

router = APIRouter()

@router.post("/explain")
async def explain(request: ExplanationRequest):
    try:
        # Business logic here
        return {"status": "success", "data": {...}}
    except GeminiAPIError as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Frontend API Proxy Pattern
```javascript
export async function POST(request) {
  try {
    const body = await request.json();
    // Validate input
    if (!body.question) {
      return Response.json({ error: "Question required" }, { status: 400 });
    }
    // Call backend
    const res = await fetch(`${backendUrl}/api/explain`, {...});
    return Response.json(await res.json());
  } catch (error) {
    return Response.json({ error: "Proxy error" }, { status: 500 });
  }
}
```

---

## API Endpoints

### Backend (Python)
- `POST /api/explain` - Generate explanation
- `POST /api/explain/bulk` - Bulk explanations
- `POST /api/analyze-image` - Image analysis
- `GET /health` - Health check
- `GET /config` - Get configuration

### Frontend (Next.js)
- `POST /api/explain` - Proxy to backend
- `POST /api/analyze` - Proxy to backend for image analysis
- `GET /api/models` - Get available models

---

## Important Notes

1. **Two servers required**: Both frontend (port 3000) and backend (port 8000) must be running
2. **API Key required**: Set `GEMINI_API_KEY` in backend `.env`
3. **Use pnpm**: The project uses pnpm, not npm or yarn
4. **Python path**: Run Python from `ai_engine/app/` directory
5. **Frontend proxy**: Frontend routes `/api/*` proxy to backend
