#!/usr/bin/env python3
"""
AOTR Discord Webhook Listener (Minimal Version)
Receives webhooks from AOTR script and posts to Discord using incoming webhooks.
NO BOT REQUIRED - uses Discord's built-in webhook feature.

Dependencies: Only Python standard library + requests
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import logging
from datetime import datetime
from urllib import request, parse
from urllib.error import URLError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    logger.error("config.json not found! Please create it from config.example.json")
    exit(1)

DISCORD_WEBHOOK_URL = config.get('discord_webhook_url')
USER_ID = config.get('user_id')  # User to ping
WEBHOOK_PORT = config.get('webhook_port', 8080)
WEBHOOK_SECRET = config.get('webhook_secret', '')

if not DISCORD_WEBHOOK_URL:
    logger.error("discord_webhook_url not configured in config.json!")
    exit(1)


class WebhookHandler(BaseHTTPRequestHandler):
    """Handles incoming webhooks from AOTR script."""

    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info(f"{self.address_string()} - {format % args}")

    def _send_json_response(self, status_code, data):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):
        """Handle GET requests (health check)."""
        if self.path == '/health':
            self._send_json_response(200, {'status': 'healthy'})
        else:
            self._send_json_response(404, {'error': 'Not found'})

    def do_POST(self):
        """Handle POST requests (webhook)."""
        if self.path != '/webhook':
            self._send_json_response(404, {'error': 'Not found'})
            return

        try:
            # Verify secret if configured
            if WEBHOOK_SECRET:
                provided_secret = self.headers.get('X-Webhook-Secret', '')
                if provided_secret != WEBHOOK_SECRET:
                    logger.warning('Invalid webhook secret provided')
                    self._send_json_response(401, {'error': 'Unauthorized'})
                    return

            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode())

            logger.info(f'Received webhook: {data}')

            # Extract event details
            event_type = data.get('event_type', 'unknown')
            item_name = data.get('item_name', 'Unknown Item')
            item_type = data.get('item_type', 'item')
            additional_info = data.get('info', '')

            # Send to Discord
            success = send_discord_notification(event_type, item_name, item_type, additional_info)

            if success:
                self._send_json_response(200, {'status': 'success', 'message': 'Notification sent'})
            else:
                self._send_json_response(500, {'error': 'Failed to send Discord notification'})

        except json.JSONDecodeError:
            logger.error('Invalid JSON in request body')
            self._send_json_response(400, {'error': 'Invalid JSON'})
        except Exception as e:
            logger.error(f'Error handling webhook: {e}')
            self._send_json_response(500, {'error': str(e)})


def send_discord_notification(event_type, item_name, item_type, additional_info):
    """Send notification to Discord using incoming webhook."""
    try:
        # Emoji mapping
        emoji_map = {
            'serum': '💉',
            'mythic': '⭐',
            'legendary': '🔥',
            'epic': '💜',
            'rare': '💙'
        }

        emoji = emoji_map.get(item_type.lower(), '🎁')

        # Create Discord embed
        embed = {
            'title': f'{emoji} AOTR Notification',
            'color': 16766720,  # Gold color
            'fields': [
                {'name': 'Event', 'value': event_type.upper(), 'inline': True},
                {'name': 'Item', 'value': item_name, 'inline': True},
                {'name': 'Type', 'value': item_type.title(), 'inline': True},
            ],
            'timestamp': datetime.now().isoformat(),
            'footer': {'text': 'AOTR Listener'}
        }

        if additional_info:
            embed['fields'].append({'name': 'Info', 'value': additional_info, 'inline': False})

        # Prepare Discord webhook payload
        payload = {
            'embeds': [embed]
        }

        # Add user ping if configured
        if USER_ID:
            payload['content'] = f'<@{USER_ID}>'

        # Send to Discord
        data = json.dumps(payload).encode('utf-8')
        req = request.Request(
            DISCORD_WEBHOOK_URL,
            data=data,
            headers={'Content-Type': 'application/json'}
        )

        with request.urlopen(req, timeout=10) as response:
            if response.status == 204 or response.status == 200:
                logger.info('Discord notification sent successfully')
                return True
            else:
                logger.error(f'Discord API returned status {response.status}')
                return False

    except URLError as e:
        logger.error(f'Failed to send Discord notification: {e}')
        return False
    except Exception as e:
        logger.error(f'Error sending Discord notification: {e}')
        return False


def run_server():
    """Run the webhook listener server."""
    server_address = ('', WEBHOOK_PORT)
    httpd = HTTPServer(server_address, WebhookHandler)

    logger.info(f'AOTR Webhook Listener starting on port {WEBHOOK_PORT}')
    logger.info(f'Health check: http://localhost:{WEBHOOK_PORT}/health')
    logger.info(f'Webhook endpoint: http://localhost:{WEBHOOK_PORT}/webhook')
    logger.info('Press Ctrl+C to stop')

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info('\nShutting down server...')
        httpd.shutdown()


if __name__ == '__main__':
    run_server()
