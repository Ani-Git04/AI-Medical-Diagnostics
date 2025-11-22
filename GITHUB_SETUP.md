# GitHub Authentication Setup

## Option 1: Personal Access Token (Easiest)

### Step 1: Create a Personal Access Token

1. Go to GitHub: https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: `medical-diagnostics-app`
4. Select expiration: **90 days** (or your preference)
5. **Select scopes** (check these boxes):
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (if you plan to use GitHub Actions)
6. Click **"Generate token"**
7. **COPY THE TOKEN IMMEDIATELY** (you won't see it again!)

### Step 2: Use the Token

When you push, use the token as your password:

```bash
git push origin main
```

**Username**: `Ani-Git04`  
**Password**: `paste_your_token_here` (not your GitHub password!)

---

## Option 2: Switch to SSH (More Secure)

### Step 1: Check if you have SSH key

```bash
ls -al ~/.ssh
```

### Step 2: Generate SSH key (if you don't have one)

```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

Press Enter to accept default location, then set a passphrase (optional).

### Step 3: Add SSH key to GitHub

1. Copy your public key:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```

2. Go to GitHub: https://github.com/settings/keys
3. Click **"New SSH key"**
4. Title: `My Computer` (or any name)
5. Paste the key
6. Click **"Add SSH key"**

### Step 4: Change remote to SSH

```bash
git remote set-url origin git@github.com:Ani-Git04/AI-Medical-Diagnostics.git
```

### Step 5: Test connection

```bash
ssh -T git@github.com
```

You should see: `Hi Ani-Git04! You've successfully authenticated...`

### Step 6: Push

```bash
git push origin main
```

---

## Option 3: Use GitHub CLI (gh)

### Install GitHub CLI

```bash
# macOS
brew install gh

# Or download from: https://cli.github.com
```

### Authenticate

```bash
gh auth login
```

Follow the prompts, then:

```bash
git push origin main
```

---

## Quick Fix (If you just want to push now)

1. **Get a token**: https://github.com/settings/tokens → Generate new token (classic) → Check `repo` → Generate
2. **Push with token**:
   ```bash
   git push origin main
   ```
   - Username: `Ani-Git04`
   - Password: `paste_token_here`

---

## Troubleshooting

**"Permission denied"**
- Make sure you copied the full token
- Check token hasn't expired
- Verify `repo` scope is selected

**"Repository not found"**
- Check repository name is correct
- Verify you have access to the repo

**Still having issues?**
- Try SSH method (Option 2)
- Or use GitHub Desktop app

