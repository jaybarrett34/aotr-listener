# Vercel Deployment

Deploy your AOTR listener to Vercel - **100% FREE** with auto-deploy from GitHub!

## Benefits

- ✅ **FREE** hosting
- ✅ **Auto-deploy** from GitHub
- ✅ **Zero local hosting** required
- ✅ **HTTPS** by default
- ✅ **Nice dashboard** for monitoring

## Quick Deploy

### Option 1: Deploy from GitHub (Recommended)

1. **Push to GitHub** (if not already)
   ```bash
   git push origin claude/discord-aotr-webhook-bot-01BZyiWvSNSS5nZuhKKUXamF
   ```

2. **Go to [vercel.com](https://vercel.com)**
   - Sign in with GitHub

3. **Import Project**
   - Click "Add New" → "Project"
   - Select your `aotr-listener` repository
   - Select `vercel-deployment` as root directory
   - Click "Deploy"

4. **Set Environment Variables**
   - In Vercel dashboard → Settings → Environment Variables
   - Add:
     - `DISCORD_WEBHOOK_URL`: Your Discord webhook URL
     - `USER_ID`: Your Discord user ID
     - `WEBHOOK_SECRET`: (optional) Your secret password

5. **Redeploy** (after adding env vars)
   - Go to Deployments tab
   - Click "..." → Redeploy

You'll get: `https://aotr-listener.vercel.app/webhook`

### Option 2: Deploy with CLI

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Login**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   cd vercel-deployment
   vercel deploy --prod
   ```

4. **Set Environment Variables**
   ```bash
   vercel env add DISCORD_WEBHOOK_URL
   vercel env add USER_ID
   vercel env add WEBHOOK_SECRET
   ```

## Test It

### Health Check

```bash
curl https://aotr-listener.vercel.app/health
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-20T...",
  "version": "1.0.0"
}
```

### Send Test Notification

```bash
curl -X POST https://aotr-listener.vercel.app/webhook \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: YOUR_SECRET" \
  -d '{
    "event_type": "LOOT_GAINED",
    "item_name": "Test Mythic",
    "item_type": "mythic"
  }'
```

Check Discord!

## Use from Your AOTR Script

```python
import json
from urllib import request

VERCEL_URL = "https://aotr-listener.vercel.app/webhook"
WEBHOOK_SECRET = "your_secret"  # If you set one

def notify_discord(item_name, item_type, info=""):
    payload = {
        "event_type": "LOOT_GAINED",
        "item_name": item_name,
        "item_type": item_type,
        "info": info
    }

    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Secret": WEBHOOK_SECRET  # Remove if not using
    }

    req = request.Request(
        VERCEL_URL,
        data=json.dumps(payload).encode(),
        headers=headers
    )

    try:
        request.urlopen(req, timeout=5)
    except Exception as e:
        print(f"Failed to notify: {e}")

# Usage
notify_discord("Serum of Strength", "serum")
```

## Auto-Deploy from GitHub

Once connected to GitHub:

1. Make changes to `vercel-deployment/api/webhook.py`
2. Commit and push to GitHub
3. Vercel automatically deploys!

## View Logs

1. Go to [vercel.com](https://vercel.com)
2. Select your project
3. Click "Deployments"
4. Click on a deployment → "Function Logs"

## Costs

**FREE tier includes:**
- Unlimited deployments
- 100 GB bandwidth/month
- Serverless function executions
- More than enough for AOTR!

## Troubleshooting

**"DISCORD_WEBHOOK_URL not configured"**
- Add environment variable in Vercel dashboard
- Redeploy after adding

**"Unauthorized"**
- Check `WEBHOOK_SECRET` matches

**Deployment failed**
- Check `vercel.json` is in `vercel-deployment/` directory
- Ensure `api/webhook.py` exists

## Security

- Environment variables encrypted by Vercel
- Functions run in isolated containers
- HTTPS only
- Optional webhook secret
