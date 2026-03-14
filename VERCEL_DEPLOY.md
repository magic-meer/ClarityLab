# Deploying ClarityLab Frontend to Vercel

Vercel is the recommended way to deploy Next.js applications. It's fast, free (for hobby projects), and handles SSL and deployments automatically.

## Steps to Deploy

### 1. Connect to GitHub
- Push your code to a GitHub repository.
- Log in to [Vercel](https://vercel.com).
- Click **"New Project"** and select your `ClarityLab` repository.

### 2. Configure Project Settings
- **Framework Preset**: Next.js (should be auto-detected).
- **Root Directory**: `.` (Project root).
- **Build Command**: `pnpm build` (Ensure `pnpm` is selected or use the default build command).

### 3. Set Environment Variables
In the **Environment Variables** section, add the following:

- `BACKEND_URL`: Your Google Cloud Run backend URL (e.g., `https://claritylab-backend-xyz.a.run.app`).

### 4. Deploy
- Click **"Deploy"**.
- Vercel will build and host your frontend. You'll get a URL like `https://clarity-lab.vercel.app`.

## Automatic Deployments
Every time you push to the `main` branch, Vercel will automatically trigger a new build and deploy the changes.
