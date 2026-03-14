## Deploying ClarityLab Backend to Cloud Run

This guide deploys the **Python FastAPI backend** (`ai_engine`) to **Google Cloud Run** using the root `Dockerfile`.

The Next.js frontend can be run locally (or deployed separately, e.g. to Vercel) and will talk to the Cloud Run URL via `BACKEND_URL`.

---

### 1. Prerequisites

- A Google Cloud project (Target: `glachackathon2026`)
- `gcloud` CLI installed and authenticated
- Billing enabled in your project

```bash
gcloud auth login
gcloud config set project glachackathon2026
```

---

### 2. Backend Deployment

Build and push the backend container:

```bash
gcloud builds submit --tag gcr.io/glachackathon2026/claritylab-backend --dockerfile Dockerfile.backend .
```

Deploy to Cloud Run:

```bash
gcloud run deploy claritylab-backend \
  --image gcr.io/glachackathon2026/claritylab-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000
```

### 3. Environment Variables

In the Cloud Run **Service > Edit & Deploy** screen, or via CLI, set:

- `GEMINI_API_KEY`
- `GCP_PROJECT_ID`
- `GCP_LOCATION`
- `DEBUG_MODE` (`false`)
- `LOG_LEVEL` (`INFO`)

---

### 4. CI/CD with GitHub Actions

Automated deployments are configured in `.github/workflows/deploy-backend.yml`. 
See [GITHUB_ACTIONS.md](./GITHUB_ACTIONS.md) for setup instructions.

