# Cloudflare Workers Deployment

Deploy your AOTR listener to Cloudflare's global network - **100% FREE**!

## Benefits

- ✅ **FREE** - 100,000 requests/day on free tier
- ✅ **Global CDN** - Fast from anywhere
- ✅ **Zero local hosting** - Runs on Cloudflare's servers
- ✅ **HTTPS** - Secure by default
- ✅ **Logging** - View requests in dashboard

## Quick Deploy

### 1. Install Wrangler CLI

```bash
npm install -g wrangler
# or
brew install cloudflare-wrangler2
```

### 2. Login to Cloudflare

```bash
wrangler login
```

This opens your browser to authorize.

### 3. Deploy

```bash
cd cloudflare-worker
wrangler deploy
```

You'll get a URL like: `https://aotr-listener.YOUR-SUBDOMAIN.workers.dev`

### 4. Set Secrets

**Required:**

```bash
wrangler secret put DISCORD_WEBHOOK_URL
# Paste your Discord webhook URL when prompted

wrangler secret put USER_ID
# Paste your Discord user ID when prompted
```

**Optional (for security):**

```bash
wrangler secret put WEBHOOK_SECRET
# Enter a secret password
```

## Test It

### Health Check

```bash
curl https://aotr-listener.YOUR-SUBDOMAIN.workers.dev/health
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
curl -X POST https://aotr-listener.YOUR-SUBDOMAIN.workers.dev/webhook \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: YOUR_SECRET" \
  -d '{
    "event_type": "LOOT_GAINED",
    "item_name": "Test Serum",
    "item_type": "serum"
  }'
```

Check Discord - you should get pinged!

## Use from Your AOTR Script

```python
import json
from urllib import request

WORKER_URL = "https://aotr-listener.YOUR-SUBDOMAIN.workers.dev/webhook"
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
        WORKER_URL,
        data=json.dumps(payload).encode(),
        headers=headers
    )

    try:
        request.urlopen(req, timeout=5)
    except Exception as e:
        print(f"Failed to notify: {e}")

# Usage
notify_discord("Serum of Power", "serum")
notify_discord("Mythic Blade", "mythic", "Boss drop")
```

## Update Worker

After making changes to `worker.js`:

```bash
wrangler deploy
```

Changes are live instantly!

## View Logs

```bash
wrangler tail
```

Or view in Cloudflare dashboard.

## Costs

**FREE tier includes:**
- 100,000 requests per day
- 10ms CPU time per request
- More than enough for AOTR notifications!

## Troubleshooting

**"No route found"**
- Make sure you deployed: `wrangler deploy`

**"Unauthorized"**
- Check webhook secret matches

**"Discord API error"**
- Verify `DISCORD_WEBHOOK_URL` is correct
- Check it in Cloudflare dashboard → Workers → aotr-listener → Settings → Variables

## Security

- Secrets are encrypted in Cloudflare
- Worker runs in isolated environment
- HTTPS only
- Optional webhook secret for extra security
