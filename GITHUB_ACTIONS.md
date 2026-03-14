# Setting up GitHub Secrets for Cloud Run Deployment

To allow GitHub Actions to deploy to your Google Cloud Project, you need to set up a Service Account and add its key to GitHub Secrets.

## 1. Create a Service Account in GCP
- Go to **IAM & Admin > Service Accounts**.
- Create a new account, e.g., `github-actions-deployer`.
- Grant the following roles:
  - **Cloud Run Admin**
  - **Artifact Registry Writer** (Essential for pushing images)
  - **Storage Admin** (for Artifact Registry/GCR)
  - **Service Account User**
  - **Cloud Build Editor**

## 2. Create and Download a JSON Key
- Select the Service Account > **Keys** tab.
- Click **Add Key > Create new key** (JSON).
- Save the file locally.

## 3. Add to GitHub Secrets
- In your GitHub repository, go to **Settings > Secrets and variables > Actions**.
- Click **New repository secret**.
- **Name**: `GCP_SA_KEY`
- **Value**: Paste the entire content of the JSON key file.

## 4. Trigger Deployment
Push any changes in the `ai_engine/` directory to `main` to trigger the `.github/workflows/deploy-backend.yml` workflow.
