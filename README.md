<div align="center">
  <img src="app/icon.svg" alt="ClarityLab Logo" width="120" />
  <h1>ClarityLab</h1>
  <p><em>An intelligent, multimodal AI learning agent that explains complex topics through text, dynamic diagrams, images, and video.</em></p>
  <p><b>Created for the Gemini Live Agent Challenge 2026</b></p>
</div>

---

## Overview

**ClarityLab** is an advanced AI-powered educational platform designed to break down extremely complex subjects into digestible, multimodal explanations. By leveraging the power of **Google Cloud Vertex AI** and the latest **Gemini** multimodal ecosystem (including Gemini 2.5 Flash/Pro, Imagen 3 & Imagen 4 Ultra, and Veo 3.1), ClarityLab generates a rich, textbook-like learning experience completely on the fly. 

When you ask a question, ClarityLab acts as an intelligent agent. It dynamically assesses the query's complexity, devises an execution plan, and natively orchestrates:
- **Textual Explanations:** Tailored to your learning level (Beginner to Expert).
- **Visual Diagrams:** AI-generated professional diagram images using Imagen 4 Ultra.
- **Images:** High-fidelity conceptual illustrations natively synthesized using Google Imagen 3.
- **Educational Videos:** Synthetic learning visual sequences powered by Veo 3.1 on Vertex AI.
- **Narration:** Read-aloud Native Text-to-Speech integration for auditory learners.

## System Architecture

ClarityLab consists of a **Next.js 15 frontend** that communicates with a **FastAPI backend (AI Engine)**. The backend acts as an orchestrator, securely interacting with Google Cloud Vertex AI to generate parallel multimodal responses.

### High-Level Architecture Diagram
![System Architecture](./resources/diagram/claritylab.architecture.drawio.svg)

## Tech Stack

**Frontend:**
- **Framework:** [Next.js 15](https://nextjs.org/) (App Router)
- **UI & Styling:** React 19, Vanilla CSS Modules
- **Rendering Elements:** `react-markdown`, `katex`
- **Audio:** Web SpeechSynthesis API

**Backend (AI Engine):**
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/) w/ Uvicorn
- **AI SDK:** `google-genai` (Configured for Vertex AI backend)
- **Language:** Python 3.11+

**Google Cloud Services & Infrastructure:**
- **Vertex AI:** Core machine learning platform powering Gemini 2.5, Imagen 3, Imagen 4 Ultra, and Veo 3.1 models.
- **Cloud Run:** Serverless container hosting for the FastAPI backend.
- **Artifact Registry:** Docker image storage for CI/CD deployments.
- **Cloud Text-to-Speech:** High-quality Journey/Standard voices for narration.
- **Frontend Hosting:** Vercel (with automated GitHub deployments).

## Directory Structure

```text
clarity-lab/
├── .github/                  # GitHub Actions CI/CD Workflows
│   └── workflows/
│       └── deploy-backend.yml
├── app/                      # Next.js Frontend Application
│   ├── api/                  # Frontend API Proxies
│   ├── components/           # Reusable UI Components (MarkdownRenderer, etc.)
│   ├── page.js               # Main Chat UI & State Management
│   └── globals.css           # Global Styles
├── ai_engine/                # Python FastAPI Backend
│   ├── app/
│   │   ├── ai_engine/        # Core AI Generation Logic (Gemini Client, Planners)
│   │   ├── api/              # FastAPI Routes & Endpoints
│   │   ├── config/           # App Configuration (Settings, Loggers)
│   │   └── main.py           # FastAPI Entry point
│   └── requirements.txt      # Python Dependencies
├── public/                   # Static Frontend Assets (Logos, Icons)
└── package.json              # Node.js Dependencies & Scripts
```

## Running Locally

### Prerequisites
- [Node.js](https://nodejs.org/) (v18+) and `npm` or `pnpm`
- Python 3.11+
- A Google Cloud Project with the **Vertex AI API** enabled.
- Make sure to authenticate your Google Cloud CLI locally: `gcloud auth application-default login`

### 1. Start the Backend AI Engine
Open a terminal and navigate to the backend directory:
```bash
cd clarity-lab/ai_engine
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in the `ai_engine` folder:
```env
GCP_PROJECT_ID=your-google-cloud-project-id
GCP_LOCATION=us-central1
```

Run the FastAPI server:
```bash
cd app
uvicorn main:app --reload --port 8080
```
*The backend will be running at http://localhost:8080*

### 2. Start the Frontend
In a separate terminal, run the Next.js app:
```bash
cd clarity-lab
npm install
npm run dev
```
*The frontend will be running at http://localhost:3000*

## Deployment & CI/CD

ClarityLab features a fully automated CI/CD pipeline triggered by pushing to the `main` branch.

### Live Application
- **Frontend URL:** [https://clarity-lab-gamma.vercel.app/](https://clarity-lab-gamma.vercel.app/)

### Frontend (Vercel)
The Next.js frontend is deployed via [Vercel](https://vercel.com/new). Through its GitHub integration, any commits pushed to the `main` branch automatically trigger a new production build and deployment. The frontend interacts directly with the Google Cloud Run-hosted backend via environment variables.

### Backend (Google Cloud Run)
The AI Engine is containerized using `Dockerfile.backend` and hosted on Google Cloud Run. The deployment is entirely automated via GitHub Actions:
1. When code is pushed to `main` (specifically inside the `ai_engine/` directory), the `.github/workflows/deploy-backend.yml` pipeline triggers.
2. It builds the Docker image and pushes it to **Google Artifact Registry**.
3. It deploys the latest image to **Google Cloud Run**, ensuring the Service Account used has permissions for Vertex AI.

## Contributing

We welcome contributions from the community! If you're inspired by the **Gemini Live Agent Challenge 2026** and want to enhance ClarityLab:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
5. Open a Pull Request

## Contributors

A huge thank you to the following individuals who helped build ClarityLab:
- **[Anees Ahmed](https://github.com/IaM-AnEeS)** (Backend prototype & Docker)
- **[Maryam Naqvi](https://github.com/maryam-naqvi)** (Documentation, blog & demo video)

See [CONTRIBUTORS.md](./CONTRIBUTORS.md) for more details.
