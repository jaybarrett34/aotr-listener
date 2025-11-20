"""
Stats Message Updater

Creates and updates the stats message in Discord with charts and statistics.
"""

import json
from urllib import request as url_request
from urllib.error import HTTPError, URLError
from datetime import datetime
from typing import Optional

from database import (
    get_drops_summary,
    get_special_rewards_summary,
    get_last_n_runs,
    get_stats_message_id,
    set_stats_message_id
)
from charts import (
    create_drops_bar_chart,
    create_special_rewards_bar_chart,
    create_time_line_chart,
    create_level_line_chart,
    create_gold_line_chart,
    create_gems_line_chart
)


def create_stats_embeds() -> list:
    """
    Create all embeds for the stats message.

    Returns:
        List of Discord embed objects
    """
    embeds = []

    # Get data
    drops = get_drops_summary()
    specials = get_special_rewards_summary()
    recent_runs = get_last_n_runs(50)

    # Embed 1: Drops Bar Chart
    drops_chart_url = create_drops_bar_chart(drops)
    embeds.append({
        'title': '📊 Drops Distribution (All-Time)',
        'image': {'url': drops_chart_url},
        'color': 3447003  # Blue
    })

    # Embed 2: Special Rewards Bar Chart
    special_chart_url = create_special_rewards_bar_chart(specials)
    embeds.append({
        'title': '⭐ Special Rewards (All-Time)',
        'image': {'url': special_chart_url},
        'color': 15844367  # Gold
    })

    # Embed 3: Completion Time Line Chart
    time_chart_url = create_time_line_chart(recent_runs)
    embeds.append({
        'title': '⏱️ Completion Time Trend',
        'image': {'url': time_chart_url},
        'color': 3447003  # Blue
    })

    # Embed 4: Level Progress Line Chart
    level_chart_url = create_level_line_chart(recent_runs)
    embeds.append({
        'title': '📈 Level Progress',
        'image': {'url': level_chart_url},
        'color': 3066993  # Green
    })

    # Embed 5: Gold Earned Line Chart
    gold_chart_url = create_gold_line_chart(recent_runs)
    embeds.append({
        'title': '💰 Gold Earned',
        'image': {'url': gold_chart_url},
        'color': 15844367  # Gold
    })

    # Embed 6: Gems Earned Line Chart
    gems_chart_url = create_gems_line_chart(recent_runs)
    embeds.append({
        'title': '💎 Gems Earned',
        'image': {'url': gems_chart_url},
        'color': 10181046  # Purple
    })

    # Add footer to last embed with update time
    embeds[-1]['footer'] = {
        'text': f'Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}'
    }

    return embeds


def send_or_update_stats_message(webhook_url: str) -> bool:
    """
    Send a new stats message or update the existing one.

    Args:
        webhook_url: Discord webhook URL for the stats channel

    Returns:
        True if successful, False otherwise
    """
    try:
        # Get existing message ID
        message_id = get_stats_message_id()

        # Generate embeds
        embeds = create_stats_embeds()

        payload = {
            'embeds': embeds,
            'content': '**AOTR Statistics Dashboard**'
        }

        if message_id:
            # Update existing message
            print(f'Updating existing stats message: {message_id}')
            return _update_message(webhook_url, message_id, payload)
        else:
            # Create new message
            print('Creating new stats message')
            return _create_message(webhook_url, payload)

    except Exception as e:
        print(f'Error in send_or_update_stats_message: {e}')
        import traceback
        print(traceback.format_exc())
        return False


def _create_message(webhook_url: str, payload: dict) -> bool:
    """Create a new stats message and store its ID."""
    try:
        # Add ?wait=true to get message ID back
        url = webhook_url if '?wait=true' in webhook_url else f'{webhook_url}?wait=true'

        data = json.dumps(payload).encode('utf-8')
        req = url_request.Request(
            url,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'AOTR-Listener/1.0 (Stats Dashboard)'
            }
        )

        with url_request.urlopen(req, timeout=30) as response:
            if response.status in (200, 204):
                # Parse response to get message ID
                response_data = json.loads(response.read().decode('utf-8'))
                message_id = response_data.get('id')

                if message_id:
                    # Store message ID for future updates
                    set_stats_message_id(message_id)
                    print(f'✅ Created stats message with ID: {message_id}')
                    return True
                else:
                    print('⚠️ No message ID in response')
                    return False
            else:
                print(f'⚠️ Unexpected status code: {response.status}')
                return False

    except HTTPError as e:
        error_body = e.read().decode('utf-8') if e.fp else 'No error body'
        print(f'❌ Discord HTTPError {e.code}: {e.reason}')
        print(f'Discord error details: {error_body}')
        return False
    except Exception as e:
        print(f'❌ Error creating stats message: {e}')
        import traceback
        print(traceback.format_exc())
        return False


def _update_message(webhook_url: str, message_id: str, payload: dict) -> bool:
    """Update an existing stats message."""
    try:
        # Extract webhook ID and token from URL
        # Format: https://discord.com/api/webhooks/{webhook_id}/{token}
        parts = webhook_url.split('/')
        webhook_id = parts[-2]
        webhook_token = parts[-1].split('?')[0]  # Remove query params if any

        # Build edit URL
        edit_url = f'https://discord.com/api/webhooks/{webhook_id}/{webhook_token}/messages/{message_id}'

        data = json.dumps(payload).encode('utf-8')
        req = url_request.Request(
            edit_url,
            data=data,
            headers={
                'Content-Type': 'application/json',
                'User-Agent': 'AOTR-Listener/1.0 (Stats Dashboard)'
            },
            method='PATCH'
        )

        with url_request.urlopen(req, timeout=30) as response:
            if response.status == 200:
                print('✅ Updated stats message successfully')
                return True
            else:
                print(f'⚠️ Unexpected status code: {response.status}')
                return False

    except HTTPError as e:
        if e.code == 404:
            # Message no longer exists, create a new one
            print('⚠️ Stats message not found (404), creating new one')
            return _create_message(webhook_url, payload)
        else:
            error_body = e.read().decode('utf-8') if e.fp else 'No error body'
            print(f'❌ Discord HTTPError {e.code}: {e.reason}')
            print(f'Discord error details: {error_body}')
            return False
    except Exception as e:
        print(f'❌ Error updating stats message: {e}')
        import traceback
        print(traceback.format_exc())
        return False
