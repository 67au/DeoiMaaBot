#!/bin/bash
echo "[pyrogram]
api_id=${API_ID}
api_hash=${API_HASH}
bot_token=${BOT_TOKEN}

[opts]
admin=${ADMIN}" > config.ini
exec "$@"