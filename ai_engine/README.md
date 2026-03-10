# Physics AI Explainer

An advanced AI-powered system for generating comprehensive physics explanations with diagrams, animations, and interactive simulations using Google's Gemini AI.

## Features

- 🧠 **AI-Powered Explanations**: Generate structured, accurate physics explanations for any concept
- 🎓 **Multiple Difficulty Levels**: Beginner, Intermediate, Advanced, and Expert modes
- 📊 **Structured Output**: JSON-formatted responses with diagrams, animations, and narration scripts
- 🖼️ **Image Analysis**: Analyze physics diagrams and explain concepts from images
- 🔄 **Bulk Processing**: Generate explanations for multiple questions in one request
- 📝 **Validation & Error Handling**: Comprehensive input validation and error management
- 🔍 **Advanced Architecture**: Type hints, logging, custom exceptions, and singleton patterns
- 📱 **REST API**: FastAPI-based REST API for easy integration

## Quick Start

### Prerequisites

- Python 3.11+
- Google Gemini API key

### Installation

1. Clone or download the project
2. Create a virtual environment:
```bash
conda create -p env python==3.10
source conda activate .\env  # On Windows: env\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### Running the Application

Start the FastAPI server:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`
- Interactive API docs: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

## API Endpoints

### 1. Generate Physics Explanation
**POST** `/api/explain`

Generate a comprehensive physics explanation.

**Request:**
```json
{
  "question": "Explain quantum tunneling and its applications",
  "difficulty": "intermediate"
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "topic": "Quantum Tunneling",
    "difficulty": "intermediate",
    "explanation": "...",
    "key_points": [...],
    "diagram_prompt": "...",
    "animation_prompt": "...",
    "simulation_prompt": "...",
    "narration_script": "...",
    "follow_up_questions": [...]
  }
}
```

### 2. Generate Multiple Explanations
**POST** `/api/explain/bulk`

Generate explanations for multiple questions.

**Query Parameters:**
- `questions`: List of physics questions (max 10)
- `difficulty`: Difficulty level (default: beginner)

**Example:**
```
POST /api/explain/bulk?questions=What%20is%20photosynthesis&questions=Explain%20gravity&difficulty=beginner
```

### 3. Analyze Physics Diagram
**POST** `/api/analyze-image`

Analyze a physics diagram or image.

**Query Parameters:**
- `question`: Question about the image (required)
- `context`: Additional context (optional)
- `file`: Image file (required)

**Response:**
```json
{
  "status": "success",
  "analysis": "Detailed analysis of the image..."
}
```

### 4. Health Check
**GET** `/health`

Check if the service is running.

### 5. Get Configuration
**GET** `/config`

Get non-sensitive configuration details.

### 6. List Endpoints
**GET** `/api/endpoints`

Get a list of all available API endpoints.

## Project Structure

```
├── main.py                          # FastAPI application entry point
├── requirements.txt                 # Python dependencies
├── .env.example                    # Environment variables template
│
├── ai_engine/                      # Core AI logic
│   ├── __init__.py
│   ├── gemini_client.py           # Gemini API client (singleton)
│   ├── explanation_generator.py   # Main explanation generation logic
│   ├── prompt_builder.py          # Prompt construction and templates
│   ├── response_parser.py         # Response parsing and validation
│   ├── multimodel_handler.py      # Multi-modal (image) handling
│   ├── exceptions.py              # Custom exceptions
│   ├── logger.py                  # Logging configuration
│   └── test.py                    # Testing script
│
├── api/                           # API layer
│   ├── __init__.py
│   └── api_routes.py             # FastAPI route definitions
│
├── schemas/                       # Data validation schemas
│   ├── __init__.py
│   ├── request_schema.py         # Request validation
│   └── response_schema.py        # Response data models
│
├── config/                        # Configuration
│   ├── __init__.py
│   └── settings.py               # Application settings
│
└── utils/                         # Utility functions
    └── validators.py             # Input validation utilities
```

## Architecture & Advanced Features

### 1. **Singleton Pattern**
The `GeminiClient` uses the singleton pattern to ensure only one API client instance exists.

### 2. **Exception Handling**
Custom exception hierarchy for better error management:
- `AIEngineException` (base)
  - `GeminiAPIError`
  - `InvalidPromptError`
  - `ResponseParsingError`
  - `InvalidImageError`

### 3. **Type Hints**
Comprehensive type hints throughout for better IDE support and type checking.

### 4. **Logging**
Structured logging with configurable levels for debugging and monitoring.

### 5. **Input Validation**
- Pydantic models for request validation
- Custom validators for difficulty levels
- Input sanitization to prevent injection attacks

### 6. **Error Recovery**
Graceful error handling with meaningful error messages.

### 7. **Async Support**
FastAPI endpoints support asynchronous processing.

## Usage Examples

### Python Client Example

```python
from ai_engine import generate_physics_explanation

# Generate explanation
result = generate_physics_explanation(
    question="Explain the photoelectric effect",
    difficulty="intermediate"
)

if result["status"] == "success":
    data = result["data"]
    print(f"Topic: {data['topic']}")
    print(f"Explanation: {data['explanation']}")
    print(f"Key Points: {data['key_points']}")
```

### cURL Example

```bash
curl -X POST "http://localhost:8000/api/explain" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Explain Newton'\''s laws of motion",
    "difficulty": "beginner"
  }'
```

### JavaScript/Fetch Example

```javascript
const response = await fetch('http://localhost:8000/api/explain', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    question: 'Explain relativity',
    difficulty: 'advanced'
  })
});

const data = await response.json();
console.log(data);
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
GEMINI_API_KEY=your_api_key_here
MODEL_NAME=gemini-1.5-pro
DEBUG_MODE=false
LOG_LEVEL=INFO
```

### Settings

Application settings are managed by the `config/settings.py` module with validation and caching.

## Error Handling

The system provides comprehensive error handling:

| Error | Status | Description |
|-------|--------|-------------|
| Invalid input | 400 | Question is too short/long or invalid |
| Invalid difficulty | 400 | Difficulty level not recognized |
| API error | 500 | Gemini API call failed |
| Invalid image | 400 | Image file is invalid or unsupported |
| Response parsing error | 500 | Failed to parse API response |

## Performance Considerations

- **Caching**: Settings are cached using `@lru_cache()`
- **Singleton Pattern**: Single Gemini client instance reduces initialization overhead
- **Connection Pooling**: FastAPI with Uvicorn handles connection pooling automatically
- **Async Processing**: Endpoints support async operations for better concurrency

## Security Features

- **Input Validation**: All inputs are validated using Pydantic
- **Input Sanitization**: Questions are sanitized to prevent injection attacks
- **CORS Configuration**: CORS middleware for secure cross-origin requests
- **Environment Variables**: Sensitive data stored in environment variables
- **Error Messages**: Generic error messages hide internal implementation details

## Testing

Run the test script:

```bash
python -m ai_engine.test
```

## Troubleshooting

### "GEMINI_API_KEY not configured"
**Solution**: Make sure your `.env` file has the `GEMINI_API_KEY` set correctly.

### "Empty response from Gemini API"
**Solution**: Check if your API key has appropriate quotas and permissions.

### "Invalid image format"
**Solution**: Supported formats are: JPG, PNG, GIF, WebP

### Port 8000 already in use
**Solution**: Use a different port:
```bash
uvicorn main:app --port 8001
```

## Best Practices

1. **Use Appropriate Difficulty Levels**: Choose the right difficulty for your audience
2. **Validate Responses**: Always check the response status
3. **Cache Results**: Cache explanations for frequently asked questions
4. **Rate Limiting**: Implement rate limiting in production
5. **Monitoring**: Enable comprehensive logging for production deployments

## Future Enhancements

- [ ] Database persistence for generated explanations
- [ ] Caching layer (Redis) for frequently asked questions
- [ ] Multiple language support
- [ ] User authentication and authorization
- [ ] Advanced analytics and usage tracking
- [ ] Streaming responses for long explanations
- [ ] Custom model configuration
- [ ] Batch processing with job queues

## License

MIT License - Feel free to use this project for educational and commercial purposes.

## Support

For issues or questions, please refer to the comprehensive error messages and logging output.

## Contributing

Contributions are welcome! Please ensure:
- Code follows the existing style and architecture
- All functions have type hints and docstrings
- Error handling is comprehensive
- Tests are included for new features
