# Project Context: Multimodal AI Learning Agent (Clarity Lab)

## 1. Original Project Vision vs. Current State

The original vision was to build a general-purpose AI-powered multimodal learning agent that provides interleaved multimedia explanations (text, visuals, audio, interactive elements) based on user questions and uploaded materials (images, notes, screenshots).

**Current State summary**: The project has been effectively started, but there is a clear separation between an advanced Python/FastAPI backend API (currently styled specifically as a "Physics AI Explainer") and a mostly uninitialized Next.js frontend user interface. The core pieces to support the Google Cloud tech stack (Firestore, Storage, Text-to-Speech) and Gemini AI are present.

---

## 2. Technical Stack Realization

**Proposed Stack:**
- **AI Model:** Gemini Model (via Google GenAI SDK) → **IMPLEMENTED** (Python backend `GeminiClient` and Node.js SDK added)
- **Backend Hosting:** Cloud Run → **PENDING** (Currently runs locally with Uvicorn/FastAPI)
- **Session/Conversation Management:** Firestore → **PENDING** (SDK installed in Next.js `package.json`, but no DB code exists yet)
- **Storage for Generated Media:** Cloud Storage → **PENDING** (SDK installed in Next.js `package.json`, but no storage pipeline exists)
- **Frontend UI:** Web or Mobile App → **IN PROGRESS** (Next.js web app setup started)

---

## 3. Backend (Python via `ai_engine/`)

The core AI engine logic is housed in the `ai_engine/` directory and served via a FastAPI application (`main.py`). The backend seems to have been highly refactored into a production-ready application.

**Key Features (Currently Implemented):**
- **Domain:** Currently focused on Physics (`Physics AI Explainer`). Explanations are structured with JSON out-of-the-box (topics, key points, diagram/animation simulation prompts, and narration scripts).
- **Core Endpoints:**
  - `POST /api/explain`: Generates a single detailed explanation based on question & difficulty (beginner, intermediate, advanced, expert).
  - `POST /api/explain/bulk`: Processes multiple questions.
  - `POST /api/analyze-image`: Multimodal capability to analyze user-uploaded physics diagrams/images.
- **Architecture Highlights:** Uses Singleton pattern for the `GeminiClient`, Pydantic for input/output validation, custom exception classes, structured logging, and asynchronous request handling.

---

## 4. Frontend (Next.js via `app/` and root)

The frontend is a Next.js 15 application (with React 19) located at the root of `clarity-lab`.

**Current Status:**
- **Mostly Starter Code:** Uses the default Next.js `app/` router layout (`page.js`, `layout.js`, `globals.css`). The main UI has not yet been implemented to connect the backend APIs.
- **Dependencies Setup:** The `package.json` includes required Google Cloud SDKs (`@google-cloud/firestore`, `@google-cloud/storage`, `@google-cloud/text-to-speech`) and Google GenAI SDK (`@google/generative-ai`) indicating that the frontend will integrate directly with Google Cloud services alongside the Python AI Engine.
- **Component Drafting:** A file named `Question input.js` exists at the root, which appears to be an early, mislocated draft of a user input component (`<QuestionInput onSubmit={handleQuestionSubmit} />`).

---

## 5. Next Steps / Gap Analysis

To bring the project closer to the original proposal, the following gaps need to be addressed:

1. **Frontend Integration:**
   - The Next.js frontend needs to be built out with components for chatting, uploading documents, viewing interleaved content, and displaying audio/animations.
   - Connect the Next.js API/Frontend to the FastAPI Python backend endpoints (`/api/explain`, `/api/analyze-image`).
   - Relocate `Question input.js` and other stray components into a proper Next.js structure (e.g., `components/` directory).

2. **Multimodal Output (Audio & Interleaving):**
   - The backend currently generates narration *scripts* and prompts, but does not actually orchestrate TTS (Text-to-Speech) generation entirely on the backend.
   - Interleaving engine must be built either on the Next.js layer or backend to stitch generated text, diagrams, and TTS into one coherent flow for the user.

3. **Generalize Domain:**
   - The backend is currently branded and tuned as a "Physics Explainer". To meet the "Multimodal AI Learning Agent" goal, the domain boundaries and system prompts need to be generalized to support ANY topic (or explicitly allow switching subjects).

4. **Persistence & Storage Implementation:**
   - Write code using the `@google-cloud/firestore` SDK to manage user sessions, chat histories, and learner profiles (which allows adaptive learning difficulty).
   - Write code using the `@google-cloud/storage` SDK to save the generated diagrams/audio files.
