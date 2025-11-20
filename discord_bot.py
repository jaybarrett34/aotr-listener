#!/usr/bin/env python3
"""
AOTR Discord Webhook Bot
Listens for webhook notifications from AOTR script and pings Discord user when serum/mythic is gained.
"""

import discord
from discord.ext import commands
from flask import Flask, request, jsonify
import threading
import json
import os
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load configuration
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    logger.error("config.json not found! Please create it from config.example.json")
    exit(1)

DISCORD_TOKEN = config.get('discord_token')
CHANNEL_ID = config.get('channel_id')
USER_ID = config.get('user_id')  # User to ping
WEBHOOK_PORT = config.get('webhook_port', 8080)
WEBHOOK_SECRET = config.get('webhook_secret', '')

# Initialize Discord bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize Flask app for webhook
app = Flask(__name__)

# Store bot instance for webhook to use
discord_channel = None


@bot.event
async def on_ready():
    """Called when the bot successfully connects to Discord."""
    global discord_channel
    logger.info(f'Bot connected as {bot.user}')

    # Get the channel to send messages to
    discord_channel = bot.get_channel(int(CHANNEL_ID))
    if discord_channel:
        logger.info(f'Found channel: {discord_channel.name}')
    else:
        logger.error(f'Could not find channel with ID: {CHANNEL_ID}')


@bot.command(name='test')
async def test_command(ctx):
    """Test command to verify bot is working."""
    await ctx.send(f'Bot is online! Ready to receive AOTR notifications.')


@bot.command(name='ping')
async def ping_test(ctx):
    """Test ping functionality."""
    user = await bot.fetch_user(int(USER_ID))
    await ctx.send(f'Pinging {user.mention} - this is a test!')


@app.route('/webhook', methods=['POST'])
def webhook_handler():
    """Handle incoming webhooks from AOTR script."""
    try:
        # Verify secret if configured
        if WEBHOOK_SECRET:
            provided_secret = request.headers.get('X-Webhook-Secret', '')
            if provided_secret != WEBHOOK_SECRET:
                logger.warning('Invalid webhook secret provided')
                return jsonify({'error': 'Unauthorized'}), 401

        data = request.json
        logger.info(f'Received webhook: {data}')

        # Extract event type and details
        event_type = data.get('event_type', 'unknown')
        item_name = data.get('item_name', 'Unknown Item')
        item_type = data.get('item_type', 'item')
        timestamp = data.get('timestamp', datetime.now().isoformat())
        additional_info = data.get('info', '')

        # Send Discord notification
        if discord_channel and bot.is_ready():
            # Create the message
            message = _create_notification_message(event_type, item_name, item_type, additional_info)

            # Send asynchronously
            asyncio.run_coroutine_threadsafe(
                _send_discord_notification(message),
                bot.loop
            )

            return jsonify({'status': 'success', 'message': 'Notification sent'}), 200
        else:
            logger.error('Discord bot not ready or channel not found')
            return jsonify({'error': 'Bot not ready'}), 503

    except Exception as e:
        logger.error(f'Error handling webhook: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'bot_ready': bot.is_ready(),
        'channel_connected': discord_channel is not None
    }), 200


def _create_notification_message(event_type, item_name, item_type, additional_info):
    """Create a formatted notification message."""
    emoji_map = {
        'serum': '💉',
        'mythic': '⭐',
        'legendary': '🔥',
        'epic': '💜',
        'rare': '💙'
    }

    emoji = emoji_map.get(item_type.lower(), '🎁')

    message = f"{emoji} **{event_type.upper()}** {emoji}\n"
    message += f"**Item:** {item_name}\n"
    message += f"**Type:** {item_type.title()}\n"

    if additional_info:
        message += f"**Info:** {additional_info}\n"

    message += f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

    return message


async def _send_discord_notification(message):
    """Send notification to Discord channel."""
    if discord_channel:
        # Get user to ping
        user = await bot.fetch_user(int(USER_ID))
        full_message = f"{user.mention}\n\n{message}"

        # Create embed for better formatting
        embed = discord.Embed(
            title="🎮 AOTR Notification",
            description=message,
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )

        await discord_channel.send(content=user.mention, embed=embed)
        logger.info('Discord notification sent successfully')


def run_flask():
    """Run Flask webhook server."""
    logger.info(f'Starting webhook server on port {WEBHOOK_PORT}')
    app.run(host='0.0.0.0', port=WEBHOOK_PORT, debug=False, use_reloader=False)


def run_discord_bot():
    """Run Discord bot."""
    logger.info('Starting Discord bot...')
    bot.run(DISCORD_TOKEN)


if __name__ == '__main__':
    import asyncio

    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Run Discord bot in main thread
    try:
        run_discord_bot()
    except KeyboardInterrupt:
        logger.info('Shutting down bot...')
