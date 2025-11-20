#!/usr/bin/env python3
"""
Local Runner for AOTR Webhook Listener
Runs the Vercel webhook.py locally with proper Python path setup for database support.
"""

import sys
import os
from pathlib import Path

# Add the vercel-deployment/api directory to Python path so imports work
api_dir = Path(__file__).parent / 'vercel-deployment' / 'api'
sys.path.insert(0, str(api_dir))

# Load environment from config.json
import json
config_path = Path(__file__).parent / 'config.json'
if config_path.exists():
    with open(config_path, 'r') as f:
        config = json.load(f)

    # Set environment variables from config
    os.environ['DISCORD_WEBHOOK_URL'] = config.get('discord_webhook_url', '')
    os.environ['DISCORD_STATS_WEBHOOK_URL'] = config.get('discord_stats_webhook_url', '')
    os.environ['USER_ID'] = config.get('user_id', '')
    os.environ['WEBHOOK_SECRET'] = config.get('webhook_secret', '')

    print('✅ Loaded configuration from config.json')
else:
    print('⚠️ config.json not found, using environment variables')

# Import and run the webhook handler
from http.server import HTTPServer
from webhook import handler

WEBHOOK_PORT = config.get('webhook_port', 8080) if config_path.exists() else 8080

def run_server():
    """Run the webhook listener server."""
    server_address = ('', WEBHOOK_PORT)
    httpd = HTTPServer(server_address, handler)

    print('=' * 80)
    print('🚀 AOTR Webhook Listener with Database Support')
    print('=' * 80)
    print(f'📡 Server running on port {WEBHOOK_PORT}')
    print(f'🏥 Health check: http://localhost:{WEBHOOK_PORT}/')
    print(f'🪝 Webhook endpoint: http://localhost:{WEBHOOK_PORT}/')
    print(f'💾 Database: SQLite at /tmp/aotr_stats.db')

    # Check if stats webhook is configured
    if os.environ.get('DISCORD_STATS_WEBHOOK_URL'):
        print(f'📊 Stats updates: ENABLED')
    else:
        print(f'📊 Stats updates: DISABLED (set discord_stats_webhook_url in config.json)')

    print('=' * 80)
    print('Press Ctrl+C to stop')
    print('=' * 80)

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n🛑 Shutting down server...')
        httpd.shutdown()


if __name__ == '__main__':
    run_server()
