# AOTR Discord Webhook Listener

A lightweight webhook listener that sends Discord notifications when you gain serum or mythic items in your AOTR script.

**🔒 Security First:** Uses ONLY Python's standard library - zero external dependencies, zero supply chain risk.

**⚡ Quick Start:** See [QUICKSTART.md](QUICKSTART.md) for 5-minute setup guide.

**☁️ Zero Hosting Required:** See [DEPLOY.md](DEPLOY.md) for cloud deployment options (no local hosting!)

## Deployment Options

### ⭐ Option 1: Direct to Discord (SIMPLEST - No Hosting!)
- ✅ **Zero hosting required** - Discord hosts everything!
- ✅ **30-second setup** - Just copy/paste code
- ✅ **Most secure** - Fewest moving parts
- 📄 See [direct_to_discord.py](direct_to_discord.py) or [DEPLOY.md](DEPLOY.md)

### ☁️ Option 2: Cloudflare Workers (FREE Cloud Hosting)
- ✅ **Free hosting** - 100K requests/day
- ✅ **Global CDN** - Super fast worldwide
- ✅ **Better security** - Webhook URL stays hidden
- 📄 See [cloudflare-worker/](cloudflare-worker/) or [DEPLOY.md](DEPLOY.md)

### 🔷 Option 3: Vercel (FREE Cloud Hosting)
- ✅ **Free hosting** with GitHub auto-deploy
- ✅ **Nice dashboard** for monitoring
- ✅ **Zero local hosting**
- 📄 See [vercel-deployment/](vercel-deployment/) or [DEPLOY.md](DEPLOY.md)

### 💻 Option 4: Local Hosting (Advanced)
- Requires running webhook_listener.py on your Mac
- More control but requires local process
- 📄 See setup below

**👉 For most users: Start with Option 1 (Direct to Discord)**

See [DEPLOY.md](DEPLOY.md) for detailed comparison and setup guides!

## Features

- 🎮 Real-time Discord notifications
- 💉 Serum detection alerts
- ⭐ Mythic item alerts
- 🔔 Automatic user pinging
- 🌐 Simple HTTP webhook endpoint
- 🔒 Zero dependencies (no supply chain attacks)
- 🔐 Optional webhook security with secrets

## Prerequisites

- Python 3.8 or higher (comes with macOS)
- A Discord account
- A Discord server where you can create webhooks

**That's it!** No external packages needed for the minimal version.

## Installation (MacBook Pro M4)

### Quick Check

Python 3 comes with macOS:
```bash
python3 --version
```

Should show Python 3.8 or higher.

### Navigate to Repository

```bash
cd /path/to/aotr-listener
```

**That's it!** No dependencies to install for the minimal version.

## Setup (Minimal Version - RECOMMENDED)

### 1. Create Discord Incoming Webhook

**Much simpler than creating a bot!**

1. Open Discord and go to your server
2. Right-click the channel where you want notifications → **Edit Channel**
3. Go to **Integrations** → **Webhooks** → **New Webhook**
4. Name it "AOTR Listener" (or anything you like)
5. **Copy the Webhook URL** (it looks like: `https://discord.com/api/webhooks/123456789/abcdefg...`)
6. Click **Save**

### 2. Get Your User ID (for pinging)

1. In Discord: **Settings** → **Advanced** → Enable **Developer Mode**
2. Right-click your username anywhere in Discord → **Copy ID**

### 3. Create Configuration File

```bash
cp config.example.json config.json
```

Edit `config.json`:

```json
{
  "discord_webhook_url": "https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN",
  "user_id": "YOUR_USER_ID",
  "webhook_port": 8080,
  "webhook_secret": ""
}
```

**Configuration Options:**
- `discord_webhook_url`: Your Discord webhook URL from step 1 (required)
- `user_id`: Your Discord user ID to ping (required)
- `webhook_port`: Port for webhook listener (default: 8080)
- `webhook_secret`: Optional secret for webhook security (leave empty for now)

## Running the Listener

### 1. Start the Listener

```bash
python3 webhook_listener.py
```

You should see:
```
AOTR Webhook Listener starting on port 8080
Health check: http://localhost:8080/health
Webhook endpoint: http://localhost:8080/webhook
Press Ctrl+C to stop
```

### 2. Test It

Open a **new terminal window** and run:

```bash
python3 test_webhook.py
```

Check Discord - you should see 3 test notifications with a ping!

## Webhook Listener

The bot runs a webhook listener on `http://localhost:8080/webhook`

### Webhook Format

Your AOTR script should send POST requests to `http://localhost:8080/webhook` with JSON:

```json
{
  "event_type": "LOOT_GAINED",
  "item_name": "Serum of Strength",
  "item_type": "serum",
  "timestamp": "2025-11-20T10:30:00",
  "info": "Additional details here (optional)"
}
```

**Supported item_type values:**
- `serum` - Shows 💉
- `mythic` - Shows ⭐
- `legendary` - Shows 🔥
- `epic` - Shows 💜
- `rare` - Shows 💙

### Security (Optional)

If you set a `webhook_secret` in config.json, include it in requests:

```bash
curl -X POST http://localhost:8080/webhook \
  -H "Content-Type: application/json" \
  -H "X-Webhook-Secret: my_secret_key_123" \
  -d '{"event_type": "LOOT_GAINED", "item_name": "Serum of Strength", "item_type": "serum"}'
```

## Testing the Webhook

Use the included test script:

```bash
python3 test_webhook.py
```

Or test manually with curl:

```bash
curl -X POST http://localhost:8080/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "LOOT_GAINED",
    "item_name": "Mythic Sword of Destiny",
    "item_type": "mythic",
    "info": "Dropped from boss"
  }'
```

## Integration with Your AOTR Script

### Python Example (No External Libraries)

```python
import json
from urllib import request
from datetime import datetime

def notify_discord(item_name, item_type, info=""):
    """Send notification to AOTR listener."""
    payload = {
        "event_type": "LOOT_GAINED",
        "item_name": item_name,
        "item_type": item_type,
        "timestamp": datetime.now().isoformat(),
        "info": info
    }

    headers = {
        "Content-Type": "application/json",
        # "X-Webhook-Secret": "your_secret"  # If using secrets
    }

    data = json.dumps(payload).encode('utf-8')
    req = request.Request(
        "http://localhost:8080/webhook",
        data=data,
        headers=headers
    )

    try:
        with request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                print(f"✅ Notified Discord: {item_name}")
    except Exception as e:
        print(f"❌ Notification failed: {e}")

# Usage
notify_discord("Serum of Agility", "serum")
notify_discord("Mythic Armor", "mythic", "Dropped from Dragon Boss")
```

### JavaScript Example

```javascript
async function notifyDiscord(itemName, itemType) {
  const response = await fetch('http://localhost:8080/webhook', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      // 'X-Webhook-Secret': 'my_secret_key_123'  // If using secrets
    },
    body: JSON.stringify({
      event_type: 'LOOT_GAINED',
      item_name: itemName,
      item_type: itemType,
      timestamp: new Date().toISOString()
    })
  });

  return response.json();
}

// Usage
notifyDiscord('Serum of Power', 'serum');
```

## Running as a Background Service (macOS)

### Option 1: Using `nohup`

```bash
nohup python3 discord_bot.py > bot.log 2>&1 &
```

Stop with:
```bash
pkill -f discord_bot.py
```

### Option 2: Using `screen`

```bash
screen -S aotr-bot
python3 discord_bot.py
# Press Ctrl+A then D to detach
```

Reattach:
```bash
screen -r aotr-bot
```

### Option 3: Create a Launch Agent (Persistent)

Create `~/Library/LaunchAgents/com.aotr.discordbot.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.aotr.discordbot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/venv/bin/python3</string>
        <string>/path/to/aotr-listener/discord_bot.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/path/to/aotr-listener</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardErrorPath</key>
    <string>/path/to/aotr-listener/error.log</string>
    <key>StandardOutPath</key>
    <string>/path/to/aotr-listener/output.log</string>
</dict>
</plist>
```

Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.aotr.discordbot.plist
```

## Troubleshooting

### Bot doesn't connect:
- Check your Discord token in config.json
- Ensure the bot is invited to your server
- Check internet connection

### Not receiving pings:
- Verify channel_id and user_id are correct
- Ensure bot has "Mention Everyone" permission
- Check bot has permission to send messages in the channel

### Webhook not working:
- Ensure bot is running (`python3 discord_bot.py`)
- Check firewall settings for port 8080
- Verify webhook URL is `http://localhost:8080/webhook`
- Check webhook secret matches (if configured)

### Check bot status:
```bash
curl http://localhost:8080/health
```

Should return:
```json
{
  "status": "healthy",
  "bot_ready": true,
  "channel_connected": true
}
```

## Health Check

The bot provides a health check endpoint:

```bash
curl http://localhost:8080/health
```

## Commands

- `!test` - Test if bot is online
- `!ping` - Test ping functionality

## Port Configuration

If port 8080 is in use, change `webhook_port` in config.json to another port (e.g., 8081, 9000).

## Security Notes

1. Never share your `config.json` file (it contains your bot token)
2. The bot token gives full control of your bot - keep it secret
3. Use `webhook_secret` for production use
4. By default, the webhook listens on all interfaces (0.0.0.0) - consider firewall rules

## License

MIT
