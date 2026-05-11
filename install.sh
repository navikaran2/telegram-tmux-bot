#!/bin/bash
# ============================================================
#  install.sh  —  Auto Setup Script for Ubuntu VPS
#  Run karo: bash install.sh
# ============================================================

set -e
BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BOLD}${GREEN}
╔════════════════════════════════════════╗
║   Telegram tmux Bot — Setup Script     ║
╚════════════════════════════════════════╝
${NC}"

# ── 1. System packages ───────────────────────────────────────
echo -e "${YELLOW}[1/5] System packages install ho rahe hain...${NC}"
sudo apt-get update -qq
sudo apt-get install -y python3 python3-pip python3-venv tmux curl

# ── 2. Virtual Environment ───────────────────────────────────
echo -e "${YELLOW}[2/5] Python virtual environment bana raha hoon...${NC}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

python3 -m venv venv
source venv/bin/activate

# ── 3. Python Dependencies ───────────────────────────────────
echo -e "${YELLOW}[3/5] Python packages install ho rahe hain...${NC}"
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

# ── 4. Config check ──────────────────────────────────────────
echo -e "${YELLOW}[4/5] config.py check kar raha hoon...${NC}"
if grep -q "YOUR_BOT_TOKEN_HERE" config.py; then
    echo -e "${RED}⚠️  config.py mein apna BOT_TOKEN aur ALLOWED_CHAT_IDS daalo!${NC}"
    echo -e "   File: ${SCRIPT_DIR}/config.py"
fi

# ── 5. Systemd Service ───────────────────────────────────────
echo -e "${YELLOW}[5/5] systemd service install kar raha hoon...${NC}"

SERVICE_FILE="/etc/systemd/system/tmux-bot.service"
sudo bash -c "cat > $SERVICE_FILE" << EOF
[Unit]
Description=Telegram tmux Manager Bot
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=$SCRIPT_DIR/venv/bin/python3 $SCRIPT_DIR/bot.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable tmux-bot.service

echo -e "${GREEN}
╔════════════════════════════════════════╗
║   ✅  Setup Complete!                  ║
╚════════════════════════════════════════╝
${NC}"
echo -e "${BOLD}Agle steps:${NC}"
echo "  1. config.py mein BOT_TOKEN aur ALLOWED_CHAT_IDS update karo"
echo "  2. Bot start karo:   sudo systemctl start tmux-bot"
echo "  3. Status dekho:     sudo systemctl status tmux-bot"
echo "  4. Live logs dekho:  sudo journalctl -u tmux-bot -f"
echo ""
