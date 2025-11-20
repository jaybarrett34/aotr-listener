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

            # Log raw body for debugging
            print('=' * 80)
            print('RAW WEBHOOK PAYLOAD RECEIVED:')
            print(body.decode())
            print('=' * 80)

            data = json.loads(body.decode())

            # Log parsed JSON with pretty formatting
            print('PARSED JSON PAYLOAD:')
            print(json.dumps(data, indent=2))
            print('=' * 80)

            # Send entire payload to Discord for analysis
            success = send_discord_notification(data)

            if success:
                self._send_json(200, {
                    'status': 'success',
                    'message': 'Notification sent to Discord',
                    'received_payload': data
                })
            else:
                self._send_json(500, {
                    'error': 'Failed to send Discord notification',
                    'received_payload': data
                })

        except json.JSONDecodeError as e:
            print(f'JSON Decode Error: {e}')
            print(f'Raw body: {body.decode() if body else "empty"}')
            self._send_json(400, {'error': 'Invalid JSON', 'details': str(e)})
        except Exception as e:
            print(f'Unexpected error: {type(e).__name__}: {e}')
            import traceback
            print(traceback.format_exc())
            self._send_json(500, {'error': str(e)})


def send_discord_notification(payload_data):
    """Send notification to Discord with raw payload data."""
    try:
        # Log webhook URL (masked for security)
        if DISCORD_WEBHOOK_URL:
            masked_url = DISCORD_WEBHOOK_URL[:50] + '...' if len(DISCORD_WEBHOOK_URL) > 50 else DISCORD_WEBHOOK_URL
            print(f'Discord webhook URL configured: {masked_url}')
        else:
            print('ERROR: DISCORD_WEBHOOK_URL is empty!')
            return False

        # Format the JSON payload for Discord (limit to 1024 chars per field)
        json_str = json.dumps(payload_data, indent=2)

        # Build description with payload preview
        description = "**Received AOTR Webhook - Analyzing Payload Structure**\n\n"
        description += f"*Total keys received:* `{len(payload_data) if isinstance(payload_data, dict) else 'N/A'}`\n"

        # List all top-level keys
        if isinstance(payload_data, dict):
            keys_list = ', '.join(f'`{k}`' for k in payload_data.keys())
            description += f"*Keys:* {keys_list}\n"

        # Build embed fields for each key-value pair
        fields = []
        if isinstance(payload_data, dict):
            for key, value in list(payload_data.items())[:10]:  # Limit to first 10 fields
                # Format value for display
                if isinstance(value, (dict, list)):
                    value_str = json.dumps(value, indent=2)
                else:
                    value_str = str(value)

                # Truncate if too long
                if len(value_str) > 1024:
                    value_str = value_str[:1021] + '...'

                fields.append({
                    'name': f'📋 {key}',
                    'value': f'```json\n{value_str}\n```',
                    'inline': False
                })

        # Create Discord payload
        embed = {
            'title': '🔍 AOTR Webhook Payload Received',
            'description': description,
            'color': 3447003,  # Blue color for debugging
            'fields': fields,
            'timestamp': datetime.now().isoformat(),
            'footer': {'text': 'AOTR Listener • Debug Mode • Vercel'}
        }

        # Add full JSON as separate field if not too large
        if len(json_str) <= 1024:
            embed['fields'].append({
                'name': '📦 Complete Payload',
                'value': f'```json\n{json_str}\n```',
                'inline': False
            })

        discord_payload = {'embeds': [embed]}

        # Add user ping if configured
        if USER_ID:
            discord_payload['content'] = f'<@{USER_ID}> New AOTR webhook received!'
            print(f'Pinging user: {USER_ID}')

        print(f'Sending payload analysis to Discord...')

        # Send to Discord
        data = json.dumps(discord_payload).encode('utf-8')
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
