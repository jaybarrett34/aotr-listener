#!/usr/bin/env python3
"""
Test script to send sample webhooks to the listener.
This simulates what your AOTR script will send.
"""

import json
from urllib import request
from datetime import datetime

# Configuration
WEBHOOK_URL = "http://localhost:8080/webhook"
WEBHOOK_SECRET = "optional_secret_for_security"  # Must match config.json


def send_test_notification(item_name, item_type, event_type="LOOT_GAINED", info=""):
    """Send a test notification to the webhook listener."""
    payload = {
        "event_type": event_type,
        "item_name": item_name,
        "item_type": item_type,
        "timestamp": datetime.now().isoformat(),
        "info": info
    }

    headers = {
        "Content-Type": "application/json",
        "X-Webhook-Secret": WEBHOOK_SECRET  # Remove if not using secret
    }

    data = json.dumps(payload).encode('utf-8')
    req = request.Request(WEBHOOK_URL, data=data, headers=headers)

    try:
        with request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode())
            print(f"✅ Success: {result}")
            return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    print("🧪 Testing AOTR Webhook Listener\n")

    # Test 1: Serum notification
    print("Test 1: Serum notification")
    send_test_notification(
        item_name="Serum of Strength",
        item_type="serum",
        info="Found in treasure chest"
    )
    print()

    # Test 2: Mythic notification
    print("Test 2: Mythic notification")
    send_test_notification(
        item_name="Mythic Sword of Destiny",
        item_type="mythic",
        info="Dropped from boss battle"
    )
    print()

    # Test 3: Legendary notification
    print("Test 3: Legendary notification")
    send_test_notification(
        item_name="Legendary Armor",
        item_type="legendary"
    )
    print()

    print("✨ All tests completed!")
