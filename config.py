# ============================================================
#  config.py  —  Telegram tmux Bot Configuration
#  Yahan apna Bot Token aur Chat ID daalo
# ============================================================

# ── Telegram Credentials ────────────────────────────────────
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"       # @BotFather se mila token
ALLOWED_CHAT_IDS = [123456789]          # Tumhara Telegram Chat ID (integer)

# ── Bot Settings ────────────────────────────────────────────
BOT_NAME = "🖥️ VPS tmux Manager"
MAX_LOG_LINES = 30                      # /logs command mein kitni lines dikhani hain
LOG_FILE = "bot_activity.log"           # Bot ki apni activity log
COMMAND_TIMEOUT = 10                    # Shell commands ka max timeout (seconds)
