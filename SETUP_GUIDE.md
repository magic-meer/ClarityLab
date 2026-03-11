# ClarityLab — Setup & Run Guide

## Prerequisites

| Tool        | Version   | Check command         |
|-------------|-----------|-----------------------|
| **Node.js** | ≥ 18      | `node -v`             |
| **pnpm**    | ≥ 8       | `pnpm -v`             |
| **Python**  | ≥ 3.10    | `python --version`    |
| **pip**     | latest    | `pip --version`       |

---

## 1. Clone & Enter the Project

```bash
cd ~/clarity-lab
```

---

## 2. Set Up the Python Backend

### 2a. Create a virtual environment

```bash
cd ai_engine
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate
```

### 2b. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2c. Configure the environment

Create or edit `ai_engine/.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
MODEL_NAME=gemini-1.5-pro
DEBUG_MODE=true
LOG_LEVEL=INFO
```

> **How to get a Gemini API key:**  
> Go to [Google AI Studio](https://aistudio.google.com/apikey) and create a free API key.

### 2d. Start the backend

```bash
cd app
python main.py
```

The FastAPI server will start at **http://localhost:8000**.  
Swagger docs available at **http://localhost:8000/docs**.

---

## 3. Set Up the Next.js Frontend

Open a **new terminal**.

### 3a. Install Node.js dependencies

```bash
cd ~/clarity-lab
pnpm install
```

### 3b. Configure the frontend environment

Create or edit `.env.local` at the project root:

```env
BACKEND_URL=http://localhost:8000
```

### 3c. Start the development server

```bash
pnpm dev
```

The frontend will start at **http://localhost:3000**.

---

## 4. Using the App

1. Open **http://localhost:3000** in your browser.
2. Select a **difficulty level** from the sidebar (Beginner / Intermediate / Advanced / Expert).
3. Type any question in the input bar — e.g. *"Explain quantum entanglement"* or *"How does photosynthesis work?"*
4. Press **Enter** or click the **Send** button.
5. The AI will return a structured response with:
   - **Explanation** — clear text explanation
   - **Key Points** — important concepts
   - **Diagram Concept** — prompt for generating a visual diagram
   - **Animation Concept** — prompt for creating an animation
   - **Simulation Idea** — concept for an interactive simulation
   - **Narration Script** — voiceover script
   - **Follow-up Questions** — questions to deepen understanding

---

## 5. Project Structure

```
clarity-lab/
├── app/                          # Next.js frontend
│   ├── api/
│   │   ├── explain/route.js      # Proxies to Python backend
│   │   └── analyze/route.js      # Image analysis proxy
│   ├── globals.css               # Design system
│   ├── layout.js                 # Root layout
│   ├── page.js                   # Main chat page
│   └── page.module.css           # Page styles
│
├── ai_engine/                    # Python backend
│   ├── app/
│   │   ├── main.py               # FastAPI entry point
│   │   ├── ai_engine/            # Core AI logic
│   │   │   ├── gemini_client.py  # Gemini API client
│   │   │   ├── explanation_generator.py
│   │   │   ├── prompt_builder.py
│   │   │   ├── response_parser.py
│   │   │   └── multimodal_handler.py
│   │   ├── api/api_routes.py     # REST API routes
│   │   ├── config/               # Settings & logger
│   │   ├── schemas/              # Pydantic models
│   │   └── utils/                # Validators & exceptions
│   ├── requirements.txt
│   └── .env                      # Backend env vars
│
├── package.json
├── next.config.mjs
└── project_context.md
```

---

## 6. Troubleshooting

| Issue | Solution |
|-------|----------|
| `GEMINI_API_KEY not configured` | Set your key in `ai_engine/.env` |
| Frontend shows "Could not reach the server" | Ensure the Python backend is running on port 8000 |
| Port 8000 already in use | Change port in `main.py`: `uvicorn.run(app, port=8001)` and update `BACKEND_URL` in `.env.local` |
| `ModuleNotFoundError` in Python | Ensure you're in the `ai_engine/app/` directory when running `python main.py` |
| `pnpm: command not found` | Install pnpm: `npm install -g pnpm` |

---

## Quick Start (TL;DR)

```bash
# Terminal 1 — Backend
cd ~/clarity-lab/ai_engine
source .venv/bin/activate
cd app
python main.py

# Terminal 2 — Frontend
cd ~/clarity-lab
pnpm install
pnpm dev
```

Open **http://localhost:3000** and start asking questions!
