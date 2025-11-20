/**
 * AOTR Discord Webhook Forwarder - Cloudflare Worker
 *
 * Deploy this to Cloudflare Workers for FREE hosting (100K requests/day)
 * Zero local hosting required!
 *
 * Setup:
 * 1. Install wrangler: npm install -g wrangler
 * 2. Login: wrangler login
 * 3. Deploy: wrangler deploy
 * 4. Set secrets in Cloudflare dashboard:
 *    - DISCORD_WEBHOOK_URL
 *    - USER_ID
 *    - WEBHOOK_SECRET (optional)
 */

export default {
  async fetch(request, env, ctx) {
    // CORS headers for browser requests
    const corsHeaders = {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, X-Webhook-Secret',
    };

    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: corsHeaders });
    }

    const url = new URL(request.url);

    // Health check endpoint
    if (url.pathname === '/health') {
      return new Response(
        JSON.stringify({
          status: 'healthy',
          timestamp: new Date().toISOString(),
          version: '1.0.0'
        }),
        {
          status: 200,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        }
      );
    }

    // Webhook endpoint
    if (url.pathname === '/webhook' && request.method === 'POST') {
      try {
        // Verify webhook secret if configured
        if (env.WEBHOOK_SECRET) {
          const providedSecret = request.headers.get('X-Webhook-Secret');
          if (providedSecret !== env.WEBHOOK_SECRET) {
            return new Response(
              JSON.stringify({ error: 'Unauthorized' }),
              {
                status: 401,
                headers: { ...corsHeaders, 'Content-Type': 'application/json' }
              }
            );
          }
        }

        // Parse request body
        const data = await request.json();
        const eventType = data.event_type || 'unknown';
        const itemName = data.item_name || 'Unknown Item';
        const itemType = data.item_type || 'item';
        const additionalInfo = data.info || '';

        // Create Discord message
        const discordPayload = createDiscordMessage(
          eventType,
          itemName,
          itemType,
          additionalInfo,
          env.USER_ID
        );

        // Forward to Discord
        const discordResponse = await fetch(env.DISCORD_WEBHOOK_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(discordPayload)
        });

        if (!discordResponse.ok) {
          throw new Error(`Discord API returned ${discordResponse.status}`);
        }

        return new Response(
          JSON.stringify({
            status: 'success',
            message: 'Notification sent to Discord'
          }),
          {
            status: 200,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          }
        );

      } catch (error) {
        return new Response(
          JSON.stringify({
            error: error.message || 'Internal server error'
          }),
          {
            status: 500,
            headers: { ...corsHeaders, 'Content-Type': 'application/json' }
          }
        );
      }
    }

    // 404 for unknown routes
    return new Response(
      JSON.stringify({ error: 'Not found' }),
      {
        status: 404,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      }
    );
  }
};

/**
 * Create a Discord embed message
 */
function createDiscordMessage(eventType, itemName, itemType, additionalInfo, userId) {
  // Emoji mapping
  const emojiMap = {
    'serum': '💉',
    'mythic': '⭐',
    'legendary': '🔥',
    'epic': '💜',
    'rare': '💙'
  };

  const emoji = emojiMap[itemType.toLowerCase()] || '🎁';

  // Build embed fields
  const fields = [
    { name: 'Event', value: eventType.toUpperCase(), inline: true },
    { name: 'Item', value: itemName, inline: true },
    { name: 'Type', value: itemType.charAt(0).toUpperCase() + itemType.slice(1), inline: true }
  ];

  if (additionalInfo) {
    fields.push({ name: 'Info', value: additionalInfo, inline: false });
  }

  const payload = {
    embeds: [{
      title: `${emoji} AOTR Notification`,
      color: 16766720, // Gold
      fields: fields,
      timestamp: new Date().toISOString(),
      footer: { text: 'AOTR Listener • Cloudflare Workers' }
    }]
  };

  // Add user ping if configured
  if (userId) {
    payload.content = `<@${userId}>`;
  }

  return payload;
}
