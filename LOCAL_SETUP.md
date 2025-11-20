# Local Setup with Database Support

Your AOTR listener can now run locally with **full database support** for statistics tracking!

## 🔧 Quick Setup

### 1. Create config.json

Copy the example config and fill in your values:

```bash
cp config.example.json config.json
```

Edit `config.json` with your Discord webhooks:

```json
{
  "discord_webhook_url": "https://discord.com/api/webhooks/YOUR_WEBHOOK_ID/TOKEN",
  "discord_stats_webhook_url": "https://discord.com/api/webhooks/STATS_WEBHOOK_ID/TOKEN",
  "user_id": "YOUR_DISCORD_USER_ID",
  "webhook_port": 8080,
  "webhook_secret": "optional_secret"
}
```

**Important:**
- `discord_webhook_url` - Main channel for run-by-run notifications
- `discord_stats_webhook_url` - Stats channel for the auto-updating dashboard with charts

### 2. Run the Server

```bash
python3 run_local.py
```

You should see:

```
🚀 AOTR Webhook Listener with Database Support
📡 Server running on port 8080
💾 Database: SQLite at /tmp/aotr_stats.db
📊 Stats updates: ENABLED
```

### 3. Update Your AOTR Script

Point your AOTR script to the local server:

```python
WEBHOOK_URL = "http://localhost:8080/"
```

## 📊 What's New?

### Database Storage
Every run is now stored in a SQLite database with:
- User, level, gold, gems
- Time taken, damage dealt, titan kills, critical hits
- Rewards (gold, XP, gems)
- Drops (by rarity)
- Special rewards

### Stats Dashboard
The stats channel automatically updates with:
- 📊 **Drops Distribution** (all-time bar chart)
- ⭐ **Special Rewards** (all-time bar chart)
- ⏱️ **Completion Time Trend** (last 50 runs)
- 📈 **Level Progress** (last 50 runs)
- 💰 **Gold Earned** (last 50 runs)
- 💎 **Gems Earned** (last 50 runs)

The dashboard updates automatically after each run!

## 🆚 Old vs New

### Before (webhook_listener.py)
```bash
# Simple forwarding only
python3 webhook_listener.py
```
- ❌ No database
- ❌ No stats tracking
- ❌ No charts
- ✅ Simple forwarding

### After (run_local.py)
```bash
# Full-featured with database
python3 run_local.py
```
- ✅ SQLite database storage
- ✅ Stats tracking
- ✅ Auto-updating charts
- ✅ Special reward detection
- ✅ Smart backtick cleanup

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8080/
```

Should return:
```json
{
  "status": "healthy",
  "timestamp": "...",
  "version": "1.0.0"
}
```

### Test Webhook
```bash
python3 test_webhook.py
```

This will send a test payload and verify:
- Notification appears in main channel
- Stats dashboard is created/updated in stats channel

## 📁 Database Location

The database is stored at `/tmp/aotr_stats.db`

To view your stats:
```bash
sqlite3 /tmp/aotr_stats.db
```

```sql
-- View all runs
SELECT * FROM runs ORDER BY timestamp DESC LIMIT 10;

-- View drops summary
SELECT drop_type, COUNT(*) as count FROM drops GROUP BY drop_type;

-- View special rewards
SELECT reward_name, COUNT(*) as count FROM special_rewards GROUP BY reward_name;
```

## 🔍 Troubleshooting

### "Database modules not available"
- ✅ **FIXED!** Use `python3 run_local.py` instead of old scripts
- The new launcher properly sets up Python paths

### Stats channel not updating
- Check that `discord_stats_webhook_url` is set in config.json
- Verify the webhook URL is correct
- Check logs for "Updating stats dashboard..."

### Database is empty
- Database starts fresh each run (stored in /tmp)
- For persistent storage, change `DB_PATH` in `vercel-deployment/api/database.py`
- Example: `DB_PATH = '/home/user/aotr-listener/aotr_stats.db'`

## 🚀 Deploy to Production

When ready to deploy, follow [vercel-deployment/README.md](vercel-deployment/README.md) for FREE cloud hosting!

The Vercel deployment includes all the same features:
- Database storage (serverless)
- Auto-updating stats dashboard
- HTTPS by default
- Zero maintenance
