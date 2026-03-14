## Deploying ClarityLab Backend to Cloud Run

This guide deploys the **Python FastAPI backend** (`ai_engine`) to **Google Cloud Run** using the root `Dockerfile`.

The Next.js frontend can be run locally (or deployed separately, e.g. to Vercel) and will talk to the Cloud Run URL via `BACKEND_URL`.

---

### 1. Prerequisites

- A Google Cloud project
- `gcloud` CLI installed and authenticated
- Billing enabled in your project

```bash
gcloud auth login
gcloud config set project YOUR_GCP_PROJECT_ID
```

---

### 2. Build and Push the Container

From the project root (`ClarityLab/`):

```bash
gcloud builds submit --tag gcr.io/YOUR_GCP_PROJECT_ID/claritylab-backend
```

---

### 3. Deploy to Cloud Run

```bash
gcloud run deploy claritylab-backend \
  --image gcr.io/YOUR_GCP_PROJECT_ID/claritylab-backend \
  --platform managed \
  --region YOUR_REGION \
  --allow-unauthenticated \
  --port 8000
```

Note the **Cloud Run URL** from the output, e.g.:

`https://claritylab-backend-xyz-uc.a.run.app`

---

### 4. Configure Environment Variables

In the Cloud Run **Service > Edit & Deploy** screen, set env vars:

- `GEMINI_API_KEY`
- `MODEL_NAME` (e.g. `gemini-2.5-flash`)
- `DEBUG_MODE` (`false` in production)
- `LOG_LEVEL` (`INFO`)

Save and redeploy.

---

### 5. Point the Frontend at Cloud Run

Update the frontend `.env.local`:

```env
BACKEND_URL=https://claritylab-backend-xyz-uc.a.run.app
```

Restart the Next.js dev server:

```bash
pnpm dev
```

Your local frontend will now proxy API calls (e.g. `/api/explain`, `/api/models`) to the Cloud Run backend.

