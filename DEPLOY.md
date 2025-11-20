# Deployment Options - No Local Hosting Required!

You have **3 options** to avoid hosting on your computer:

## ⭐ Option 1: Direct to Discord (SIMPLEST - No Hosting At All!)

**Your AOTR script sends directly to Discord's webhook - Discord hosts everything!**

### Setup (30 seconds)

1. Get your Discord webhook URL from Discord (see QUICKSTART.md step 1)
2. In your AOTR script, send directly to Discord:

```python
import json
from urllib import request

DISCORD_WEBHOOK = "https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN"
USER_ID = "YOUR_USER_ID"

def notify_discord(item_name, item_type):
    """Send directly to Discord - no hosting needed!"""

    emoji_map = {'serum': '💉', 'mythic': '⭐', 'legendary': '🔥'}
    emoji = emoji_map.get(item_type, '🎁')

    payload = {
        'content': f'<@{USER_ID}>',  # Ping you
        'embeds': [{
            'title': f'{emoji} AOTR Notification',
            'color': 16766720,  # Gold
            'fields': [
                {'name': 'Item', 'value': item_name, 'inline': True},
                {'name': 'Type', 'value': item_type.title(), 'inline': True}
            ],
            'timestamp': datetime.now().isoformat()
        }]
    }

    req = request.Request(
        DISCORD_WEBHOOK,
        data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'}
    )

    request.urlopen(req)

# Usage
notify_discord("Serum of Power", "serum")
```

**Pros:**
- ✅ Zero hosting required
- ✅ Zero cost
- ✅ Simplest possible setup
- ✅ Discord handles everything
- ✅ Most secure (fewer moving parts)

**Cons:**
- ⚠️ Webhook URL is in your script (keep it private)
- ⚠️ No request logging/monitoring

---

## 🚀 Option 2: Cloudflare Workers (FREE - Hosted by Cloudflare)

**Host the forwarder on Cloudflare's global network - 100% free, zero local hosting!**

### Setup (5 minutes)

#### 1. Create Cloudflare Account
- Go to [cloudflare.com](https://cloudflare.com)
- Sign up (free tier includes 100,000 requests/day)

#### 2. Install Wrangler CLI
```bash
npm install -g wrangler
# or
brew install cloudflare-wrangler2
```

#### 3. Deploy the Worker

I've created a Cloudflare Worker for you - see `cloudflare-worker/worker.js`

```bash
cd cloudflare-worker
wrangler login
wrangler deploy
```

You'll get a URL like: `https://aotr-listener.YOUR-SUBDOMAIN.workers.dev`

#### 4. Configure the Worker

Edit the worker's environment variables in Cloudflare dashboard:
- `DISCORD_WEBHOOK_URL`: Your Discord webhook
- `USER_ID`: Your Discord user ID
- `WEBHOOK_SECRET`: Optional secret

#### 5. Use It from Your AOTR Script

```python
import json
from urllib import request

WORKER_URL = "https://aotr-listener.YOUR-SUBDOMAIN.workers.dev/webhook"
SECRET = "your_secret"

def notify_discord(item_name, item_type):
    payload = {
        "event_type": "LOOT_GAINED",
        "item_name": item_name,
        "item_type": item_type
    }

    req = request.Request(
        WORKER_URL,
        data=json.dumps(payload).encode(),
        headers={
            'Content-Type': 'application/json',
            'X-Webhook-Secret': SECRET
        }
    )

    request.urlopen(req)
```

**Pros:**
- ✅ FREE hosting (100K requests/day)
- ✅ Global CDN (super fast)
- ✅ No local hosting required
- ✅ Request logging & analytics
- ✅ Better security (webhook URL not in your script)
- ✅ Easy to update/modify

**Cons:**
- Requires initial setup
- Need to manage Cloudflare account

---

## 🔧 Option 3: Vercel (FREE - Alternative to Cloudflare)

**Similar to Cloudflare but uses Vercel's platform**

### Setup (5 minutes)

#### 1. Create Vercel Account
- Go to [vercel.com](https://vercel.com)
- Sign up with GitHub (free)

#### 2. Deploy

```bash
cd vercel-deployment
npm install -g vercel
vercel login
vercel deploy
```

You'll get: `https://aotr-listener.vercel.app/webhook`

#### 3. Configure Environment Variables

In Vercel dashboard:
- `DISCORD_WEBHOOK_URL`
- `USER_ID`
- `WEBHOOK_SECRET`

**Pros:**
- ✅ FREE hosting
- ✅ Easy GitHub integration
- ✅ Auto-deploys on git push
- ✅ Nice dashboard
- ✅ No local hosting

**Cons:**
- Requires GitHub account
- Initial setup needed

---

## 📊 Comparison

| Feature | Direct to Discord | Cloudflare Workers | Vercel |
|---------|------------------|-------------------|---------|
| **Cost** | Free | Free (100K req/day) | Free |
| **Setup Time** | 30 seconds | 5 minutes | 5 minutes |
| **Local Hosting** | None | None | None |
| **Security** | Good | Excellent | Excellent |
| **Logging** | None | Yes | Yes |
| **Speed** | Fast | Very Fast | Fast |
| **Complexity** | Simplest | Medium | Medium |

---

## 🎯 My Recommendation

**Start with Option 1 (Direct to Discord)** - it's the simplest and you don't need hosting at all!

**Upgrade to Option 2 (Cloudflare Workers)** later if you want:
- Request logging
- Better security (hide webhook URL)
- Rate limiting
- Custom logic

---

## 🔒 Security Notes

All three options are secure:

1. **Direct to Discord**: Discord webhook URL is like a password - keep it private
2. **Cloudflare Workers**: Webhook URL hidden in worker, only you know the worker URL
3. **Vercel**: Same as Cloudflare

**None require hosting on your Mac!** Your AOTR script just sends HTTPS requests to Discord or your cloud endpoint.

---

## 🆘 Questions?

**Q: Do I need to keep anything running on my Mac?**
A: Only your AOTR script itself (to detect items). Nothing else!

**Q: What about the webhook_listener.py file?**
A: That was for local hosting. You don't need it with these options!

**Q: Which is most secure?**
A: Cloudflare Workers or Vercel (webhook URL is hidden server-side)

**Q: Which is easiest?**
A: Direct to Discord (just copy/paste code into your AOTR script)
