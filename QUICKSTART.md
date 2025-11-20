# AOTR Listener - Quick Start (MacBook Pro)

Get Discord notifications when you gain serum/mythic items in 5 minutes!

## 🚀 Quick Setup

### 1. Create Discord Webhook (2 minutes)

1. Open Discord and go to your server
2. Right-click the channel where you want notifications → **Edit Channel**
3. Go to **Integrations** → **Webhooks** → **New Webhook**
4. Name it "AOTR Listener"
5. Copy the **Webhook URL** (looks like: `https://discord.com/api/webhooks/123456789/abcdefg...`)
6. Click **Save**

### 2. Get Your Discord User ID (30 seconds)

1. In Discord: **Settings** → **Advanced** → Enable **Developer Mode**
2. Right-click your username anywhere → **Copy ID**
3. Save this number

### 3. Configure the Listener (1 minute)

```bash
cd /path/to/aotr-listener
cp config.example.json config.json
```

Edit `config.json`:
```json
{
  "discord_webhook_url": "PASTE_YOUR_WEBHOOK_URL_HERE",
  "user_id": "PASTE_YOUR_USER_ID_HERE",
  "webhook_port": 8080,
  "webhook_secret": ""
}
```

### 4. Run the Listener (30 seconds)

```bash
python3 webhook_listener.py
```

You should see:
```
AOTR Webhook Listener starting on port 8080
Webhook endpoint: http://localhost:8080/webhook
```

### 5. Test It (30 seconds)

Open a **new terminal** and run:
```bash
python3 test_webhook.py
```

Check Discord - you should see 3 test notifications with a ping!

## ✅ You're Done!

Now integrate with your AOTR script:

```python
import json
from urllib import request

def notify_discord(item_name, item_type):
    data = json.dumps({
        "event_type": "LOOT_GAINED",
        "item_name": item_name,
        "item_type": item_type
    }).encode()

    req = request.Request(
        "http://localhost:8080/webhook",
        data=data,
        headers={"Content-Type": "application/json"}
    )

    request.urlopen(req)

# Use it:
notify_discord("Serum of Power", "serum")
notify_discord("Mythic Blade", "mythic")
```

## 🔒 Security Features

- **Zero external dependencies** - Uses only Python standard library
- **Optional webhook secret** - Add to `webhook_secret` in config.json
- **No bot token** - Uses Discord's incoming webhooks (simpler & safer)
- **Open source** - Review all code yourself

## 📱 Keep It Running

**Option 1: Simple background process**
```bash
nohup python3 webhook_listener.py > listener.log 2>&1 &
```

**Option 2: Using screen** (recommended)
```bash
screen -S aotr
python3 webhook_listener.py
# Press Ctrl+A then D to detach
```

To check if running:
```bash
curl http://localhost:8080/health
```

## 🎨 Item Types

- `serum` → 💉
- `mythic` → ⭐
- `legendary` → 🔥
- `epic` → 💜
- `rare` → 💙

## 🆘 Troubleshooting

**Not receiving notifications?**
```bash
curl http://localhost:8080/health
```

**Port 8080 in use?**
Change `webhook_port` to `8081` in config.json

**Discord webhook not working?**
Make sure you copied the full URL including the token

## 📚 Full Documentation

See [README.md](README.md) for complete documentation.
