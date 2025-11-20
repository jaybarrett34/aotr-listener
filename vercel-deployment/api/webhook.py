"""
AOTR Discord Webhook Forwarder - Vercel Serverless Function

Deploy to Vercel for FREE hosting - zero local hosting required!

Setup:
1. Install Vercel CLI: npm install -g vercel
2. Login: vercel login
3. Deploy: vercel deploy
4. Set environment variables in Vercel dashboard:
   - DISCORD_WEBHOOK_URL
   - USER_ID
   - WEBHOOK_SECRET (optional)
"""

from http.server import BaseHTTPRequestHandler
import json
import os
from datetime import datetime
from urllib import request as url_request
from urllib.error import URLError, HTTPError

# Get config from environment variables
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')
USER_ID = os.environ.get('USER_ID')
WEBHOOK_SECRET = os.environ.get('WEBHOOK_SECRET', '')


class handler(BaseHTTPRequestHandler):
    """Vercel serverless function handler."""

    def _send_json(self, status_code, data):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Webhook-Secret')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self._send_json(200, {})

    def do_GET(self):
        """Handle GET requests (health check)."""
        self._send_json(200, {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })

    def do_POST(self):
        """Handle POST requests (webhook)."""
        try:
            # Verify webhook secret if configured
            if WEBHOOK_SECRET:
                provided_secret = self.headers.get('X-Webhook-Secret', '')
                if provided_secret != WEBHOOK_SECRET:
                    self._send_json(401, {'error': 'Unauthorized'})
                    return

            # Verify Discord webhook is configured
            if not DISCORD_WEBHOOK_URL:
                self._send_json(500, {'error': 'DISCORD_WEBHOOK_URL not configured'})
                return

            # Parse request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode())

            # Extract event details
            event_type = data.get('event_type', 'unknown')
            item_name = data.get('item_name', 'Unknown Item')
            item_type = data.get('item_type', 'item')
            additional_info = data.get('info', '')

            # Send to Discord
            success = send_discord_notification(
                event_type, item_name, item_type, additional_info
            )

            if success:
                self._send_json(200, {
                    'status': 'success',
                    'message': 'Notification sent to Discord'
                })
            else:
                self._send_json(500, {
                    'error': 'Failed to send Discord notification'
                })

        except json.JSONDecodeError:
            self._send_json(400, {'error': 'Invalid JSON'})
        except Exception as e:
            self._send_json(500, {'error': str(e)})


def send_discord_notification(event_type, item_name, item_type, additional_info):
    """Send notification to Discord."""
    try:
        # Log webhook URL (masked for security)
        if DISCORD_WEBHOOK_URL:
            masked_url = DISCORD_WEBHOOK_URL[:50] + '...' if len(DISCORD_WEBHOOK_URL) > 50 else DISCORD_WEBHOOK_URL
            print(f'Discord webhook URL configured: {masked_url}')
        else:
            print('ERROR: DISCORD_WEBHOOK_URL is empty!')
            return False

        # Emoji mapping
        emoji_map = {
            'serum': '💉',
            'mythic': '⭐',
            'legendary': '🔥',
            'epic': '💜',
            'rare': '💙'
        }

        emoji = emoji_map.get(item_type.lower(), '🎁')

        # Build embed fields
        fields = [
            {'name': 'Event', 'value': event_type.upper(), 'inline': True},
            {'name': 'Item', 'value': item_name, 'inline': True},
            {'name': 'Type', 'value': item_type.title(), 'inline': True}
        ]

        if additional_info:
            fields.append({'name': 'Info', 'value': additional_info, 'inline': False})

        # Create Discord payload
        payload = {
            'embeds': [{
                'title': f'{emoji} AOTR Notification',
                'color': 16766720,  # Gold
                'fields': fields,
                'timestamp': datetime.now().isoformat(),
                'footer': {'text': 'AOTR Listener • Vercel'}
            }]
        }

        # Add user ping if configured
        if USER_ID:
            payload['content'] = f'<@{USER_ID}>'
            print(f'Pinging user: {USER_ID}')

        print(f'Sending to Discord: {item_name} ({item_type})')

        # Send to Discord
        data = json.dumps(payload).encode('utf-8')
        req = url_request.Request(
            DISCORD_WEBHOOK_URL,
            data=data,
            headers={'Content-Type': 'application/json'}
        )

        try:
            with url_request.urlopen(req, timeout=10) as response:
                status = response.status
                print(f'Discord response status: {status}')
                if status in (200, 204):
                    print('✅ Successfully sent to Discord')
                    return True
                else:
                    print(f'⚠️ Unexpected status code: {status}')
                    return False
        except HTTPError as e:
            # Discord returned an error - log details
            error_body = e.read().decode('utf-8') if e.fp else 'No error body'
            print(f'❌ Discord HTTPError {e.code}: {e.reason}')
            print(f'Discord error details: {error_body}')
            return False

    except URLError as e:
        print(f'❌ URLError sending to Discord: {e}')
        print(f'URLError reason: {e.reason if hasattr(e, "reason") else "unknown"}')
        return False
    except Exception as e:
        print(f'❌ Unexpected error: {type(e).__name__}: {e}')
        import traceback
        print(f'Traceback: {traceback.format_exc()}')
        return False
