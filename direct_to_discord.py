#!/usr/bin/env python3
"""
Direct to Discord - No Hosting Required!

This is the SIMPLEST option - your AOTR script sends directly to Discord.
Discord hosts everything, you host nothing!

Usage:
1. Get your Discord webhook URL (see QUICKSTART.md)
2. Get your Discord user ID (see QUICKSTART.md)
3. Copy the notify_discord() function into your AOTR script
4. Call it when you find serum/mythic!
"""

import json
from urllib import request
from datetime import datetime

# ===== CONFIGURATION =====
# Get these from Discord (see QUICKSTART.md)
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN"
USER_ID = "YOUR_USER_ID"
# =========================


def notify_discord(item_name, item_type, info=""):
    """
    Send notification directly to Discord - no hosting needed!

    Args:
        item_name: Name of the item (e.g., "Serum of Power")
        item_type: Type of item ("serum", "mythic", "legendary", etc.)
        info: Optional additional info about the item

    Example:
        notify_discord("Serum of Agility", "serum")
        notify_discord("Mythic Blade", "mythic", "Dropped from Dragon Boss")
    """

    # Emoji mapping for different item types
    emoji_map = {
        'serum': '💉',
        'mythic': '⭐',
        'legendary': '🔥',
        'epic': '💜',
        'rare': '💙',
        'uncommon': '💚',
        'common': '⚪'
    }

    emoji = emoji_map.get(item_type.lower(), '🎁')

    # Build embed fields
    fields = [
        {'name': 'Item', 'value': item_name, 'inline': True},
        {'name': 'Type', 'value': item_type.title(), 'inline': True}
    ]

    if info:
        fields.append({'name': 'Info', 'value': info, 'inline': False})

    # Create Discord webhook payload
    payload = {
        'content': f'<@{USER_ID}>',  # This pings you in Discord
        'embeds': [{
            'title': f'{emoji} AOTR Notification',
            'description': f'**{item_name}** acquired!',
            'color': 16766720,  # Gold color
            'fields': fields,
            'timestamp': datetime.now().isoformat(),
            'footer': {'text': 'AOTR • Direct to Discord'}
        }]
    }

    try:
        # Send to Discord
        data = json.dumps(payload).encode('utf-8')
        req = request.Request(
            DISCORD_WEBHOOK_URL,
            data=data,
            headers={'Content-Type': 'application/json'}
        )

        with request.urlopen(req, timeout=5) as response:
            if response.status in (200, 204):
                print(f'✅ Discord notification sent: {item_name}')
                return True
            else:
                print(f'⚠️ Discord returned status {response.status}')
                return False

    except Exception as e:
        print(f'❌ Failed to send Discord notification: {e}')
        return False


# ===== EXAMPLE USAGE =====
if __name__ == '__main__':
    """
    Test the notification system.
    Run this script to test: python3 direct_to_discord.py
    """

    print("🧪 Testing Direct to Discord Notifications\n")

    # Test 1: Serum notification
    print("Test 1: Serum notification")
    notify_discord(
        item_name="Serum of Power",
        item_type="serum",
        info="Found in ancient treasure chest"
    )
    print()

    # Test 2: Mythic notification
    print("Test 2: Mythic notification")
    notify_discord(
        item_name="Mythic Blade of Eternity",
        item_type="mythic",
        info="Dropped from Dragon King Boss"
    )
    print()

    # Test 3: Legendary notification
    print("Test 3: Legendary notification")
    notify_discord(
        item_name="Legendary Armor of the Ancients",
        item_type="legendary"
    )
    print()

    print("✨ All tests completed! Check Discord for notifications.")


# ===== INTEGRATION EXAMPLES =====
"""
Example 1: Basic integration in your AOTR script
------------------------------------------------

from direct_to_discord import notify_discord

# When you detect a serum:
notify_discord("Serum of Agility", "serum")

# When you detect a mythic:
notify_discord("Mythic Sword", "mythic", "Boss drop")


Example 2: Inline integration (copy function into your script)
--------------------------------------------------------------

import json
from urllib import request
from datetime import datetime

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN"
USER_ID = "YOUR_USER_ID"

def notify_discord(item_name, item_type, info=""):
    emoji_map = {'serum': '💉', 'mythic': '⭐', 'legendary': '🔥'}
    emoji = emoji_map.get(item_type.lower(), '🎁')

    payload = {
        'content': f'<@{USER_ID}>',
        'embeds': [{
            'title': f'{emoji} {item_name}',
            'color': 16766720,
            'fields': [
                {'name': 'Type', 'value': item_type.title(), 'inline': True}
            ],
            'timestamp': datetime.now().isoformat()
        }]
    }

    if info:
        payload['embeds'][0]['fields'].append({'name': 'Info', 'value': info})

    req = request.Request(
        DISCORD_WEBHOOK_URL,
        data=json.dumps(payload).encode(),
        headers={'Content-Type': 'application/json'}
    )
    request.urlopen(req)

# Use it:
notify_discord("Serum of Power", "serum")


Example 3: Error handling for unreliable networks
-------------------------------------------------

def notify_discord_safe(item_name, item_type, info=""):
    '''Notification with retry logic'''
    max_retries = 3

    for attempt in range(max_retries):
        try:
            notify_discord(item_name, item_type, info)
            return True
        except Exception as e:
            if attempt < max_retries - 1:
                print(f'Retry {attempt + 1}/{max_retries}...')
                time.sleep(1)
            else:
                print(f'Failed after {max_retries} attempts: {e}')
                return False

# Use with retry:
notify_discord_safe("Mythic Armor", "mythic")
"""
