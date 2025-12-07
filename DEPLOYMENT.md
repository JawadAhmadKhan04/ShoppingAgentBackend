# Deployment Guide for Render

## Prerequisites
1. A Render account (sign up at https://render.com)
2. Your code pushed to a Git repository (GitHub, GitLab, or Bitbucket)

## Deployment Steps

### 1. Push Your Code to Git
Make sure all your files are committed and pushed to your repository:
```bash
git add .
git commit -m "Prepare for Render deployment"
git push
```

### 2. Create a New Web Service on Render

1. Go to your Render dashboard: https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your Git repository (GitHub/GitLab/Bitbucket)
4. Select your repository

### 3. Configure the Service

**Basic Settings:**
- **Name**: `shopping-agent-backend` (or your preferred name)
- **Environment**: `Docker`
- **Region**: Choose closest to your users (e.g., `Oregon`)
- **Branch**: `main` (or your default branch)
- **Root Directory**: Leave empty (or `.` if needed)

**Docker Settings:**
- Render will automatically detect your `Dockerfile`
- The `render.yaml` file will be used if present, or configure manually

### 4. Set Environment Variables

In the Render dashboard, go to **Environment** section and add:

- `GEMINI_API_KEY` - Your Gemini API key
- `CLIENT_ID` - Your client ID (if needed)
- `CLIENT_SECRET` - Your client secret (if needed)

**Note**: Render automatically sets the `PORT` environment variable - you don't need to set it manually.

### 5. Deploy

1. Click **"Create Web Service"**
2. Render will build and deploy your Docker image
3. Wait for the build to complete (usually 5-10 minutes)
4. Your service will be available at: `https://your-service-name.onrender.com`

### 6. Verify Deployment

Once deployed, test your endpoints:
- Health check: `https://your-service-name.onrender.com/health`
- API docs: `https://your-service-name.onrender.com/docs`
- Search endpoint: `https://your-service-name.onrender.com/search`

## Important Notes

- **Free Tier**: Render's free tier spins down after 15 minutes of inactivity. First request after spin-down may take 30-60 seconds.
- **Environment Variables**: Never commit `.env` files. Always set secrets in Render dashboard.
- **Logs**: View logs in the Render dashboard under your service's "Logs" tab.
- **Auto-Deploy**: Render automatically deploys on every push to your main branch (if enabled).

## Troubleshooting

- **Build fails**: Check the build logs in Render dashboard
- **Service won't start**: Verify all environment variables are set
- **Port errors**: The Dockerfile now uses `PORT` env var automatically
- **Health check fails**: Ensure `/health` endpoint is accessible

