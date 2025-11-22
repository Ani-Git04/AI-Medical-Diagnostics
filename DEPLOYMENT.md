# Deployment Guide - Render

This guide will help you deploy the AI Medical Diagnostics System on Render.

## Prerequisites

1. A GitHub account
2. A Render account (free tier available at https://render.com)
3. API keys:
   - Hugging Face token (FREE) - https://huggingface.co/settings/tokens
   - OR OpenAI API key (Paid) - https://platform.openai.com/api-keys

## Step-by-Step Deployment

### Step 1: Prepare Your Repository

1. **Push your code to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit - Medical Diagnostics System"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```

2. **Ensure these files exist**:
   - ✅ `app.py` (Streamlit app)
   - ✅ `requirements.txt` (dependencies)
   - ✅ `render.yaml` (Render configuration)
   - ✅ `.gitignore` (excludes sensitive files)

### Step 2: Create Render Account

1. Go to https://render.com
2. Sign up with your GitHub account (recommended)
3. Connect your GitHub account to Render

### Step 3: Deploy on Render

#### Option A: Using render.yaml (Recommended)

1. **In Render Dashboard**:
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will automatically detect `render.yaml`
   - Click "Apply"

2. **Configure Environment Variables**:
   - Go to your service → "Environment" tab
   - Add your API keys:
     - `HUGGINGFACEHUB_API_TOKEN` = your_huggingface_token
     - OR `OPENAI_API_KEY` = your_openai_key
   - Click "Save Changes"

3. **Deploy**:
   - Render will automatically build and deploy
   - Wait for deployment to complete (5-10 minutes)
   - Your app will be live at: `https://your-app-name.onrender.com`

#### Option B: Manual Setup

1. **Create New Web Service**:
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository

2. **Configure Service**:
   - **Name**: `medical-diagnostics-system` (or your choice)
   - **Region**: Choose closest to you
   - **Branch**: `main`
   - **Root Directory**: Leave empty (or `./` if needed)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

3. **Add Environment Variables**:
   - Go to "Environment" tab
   - Add:
     - Key: `HUGGINGFACEHUB_API_TOKEN`
       Value: `your_huggingface_token_here`
     - OR
     - Key: `OPENAI_API_KEY`
       Value: `your_openai_key_here`

4. **Deploy**:
   - Click "Create Web Service"
   - Wait for build and deployment

### Step 4: Verify Deployment

1. Once deployed, click on your service URL
2. You should see the Streamlit app
3. Test with a sample medical report

## Important Notes

### Free Tier Limitations

- **Spins down after 15 minutes** of inactivity
- First request after spin-down takes ~30-60 seconds (cold start)
- **512 MB RAM** limit
- **0.1 CPU** share

### Upgrading (Optional)

For better performance:
- Upgrade to "Starter" plan ($7/month):
  - Always on (no spin-down)
  - 512 MB RAM
  - 0.5 CPU
- Or "Standard" plan ($25/month):
  - Always on
  - 2 GB RAM
  - 1 CPU

### Troubleshooting

#### Build Fails

1. **Check logs** in Render dashboard
2. **Common issues**:
   - Missing dependencies in `requirements.txt`
   - Python version mismatch
   - Build timeout (free tier has limits)

#### App Crashes

1. **Check logs** for error messages
2. **Common issues**:
   - Missing environment variables
   - Memory limits (free tier)
   - API key errors

#### Slow Performance

- Free tier has limited resources
- First request after spin-down is slow (cold start)
- Consider upgrading for better performance

### Environment Variables

Make sure these are set in Render:

```env
HUGGINGFACEHUB_API_TOKEN=your_token_here
# OR
OPENAI_API_KEY=your_key_here
```

**Note**: Never commit API keys to GitHub! Use Render's environment variables.

### File Structure for Deployment

```
Agent/
├── app.py                 # Main Streamlit app
├── requirements.txt       # Python dependencies
├── render.yaml           # Render configuration
├── config.py             # Configuration
├── Main.py               # CLI script (not needed for web)
├── Utils/                # Agent modules
│   ├── __init__.py
│   ├── Agents.py
│   ├── constants.py
│   └── logger.py
└── Medical Reports/      # Sample reports (optional)
```

### Updating Your App

1. **Make changes** to your code
2. **Commit and push** to GitHub:
   ```bash
   git add .
   git commit -m "Update description"
   git push
   ```
3. **Render auto-deploys** (if auto-deploy is enabled)
4. Or manually trigger deployment in Render dashboard

## Alternative: Using Streamlit Cloud (Easier)

If Render doesn't work, consider **Streamlit Cloud** (free):

1. Go to https://streamlit.io/cloud
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file: `app.py`
6. Add secrets (API keys) in "Secrets" tab
7. Deploy!

Streamlit Cloud is specifically designed for Streamlit apps and is easier to set up.

## Security Best Practices

1. ✅ Never commit `.env` files
2. ✅ Use Render's environment variables
3. ✅ Keep API keys secret
4. ✅ Use `.gitignore` to exclude sensitive files
5. ✅ Regularly rotate API keys

## Support

- **Render Docs**: https://render.com/docs
- **Streamlit Docs**: https://docs.streamlit.io
- **Check logs**: Render dashboard → Your service → Logs

---

**Ready to deploy?** Follow the steps above and your app will be live in minutes! 🚀

