# 🚀 Quick Start: Deploy to Render

## Fastest Way (5 minutes)

### 1. Push to GitHub
```bash
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

### 2. Deploy on Render

1. Go to https://render.com → Sign up/Login
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repo
4. Render will auto-detect `render.yaml`
5. Click **"Apply"**

### 3. Add API Key

1. Go to your service → **"Environment"** tab
2. Add: `HUGGINGFACEHUB_API_TOKEN` = `your_token_here`
3. Click **"Save Changes"**

### 4. Wait & Done! ✅

- Build takes 5-10 minutes
- Your app: `https://your-app-name.onrender.com`

---

## Manual Setup (Alternative)

If Blueprint doesn't work:

1. **New +** → **Web Service**
2. Connect GitHub repo
3. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
4. Add environment variable: `HUGGINGFACEHUB_API_TOKEN`
5. Deploy!

---

## Get Your Hugging Face Token (FREE)

1. Go to https://huggingface.co/settings/tokens
2. Click **"New token"**
3. Name: `medical-app`
4. Permission: **Read**
5. Copy token → Paste in Render

---

## ⚠️ Important Notes

- **Free tier spins down** after 15 min inactivity
- First load after spin-down: ~30-60 seconds
- For always-on: Upgrade to Starter ($7/month)

---

## Troubleshooting

**Build fails?**
- Check Render logs
- Ensure `requirements.txt` is correct

**App crashes?**
- Check environment variables are set
- Review logs for errors

**Need help?**
- See full guide: `DEPLOYMENT.md`

---

**That's it! Your app will be live soon! 🎉**

