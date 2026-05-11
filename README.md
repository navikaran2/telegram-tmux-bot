<div align="center">

# 🖥️ Telegram tmux Bot

### Ubuntu VPS ke tmux sessions ko Telegram se control karo!

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?style=for-the-badge&logo=telegram)
![Ubuntu](https://img.shields.io/badge/Ubuntu-VPS-orange?style=for-the-badge&logo=ubuntu)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

</div>

---

## 📖 Yeh Kya Hai?

Yeh ek **Python Telegram Bot** hai jo tumhare **Ubuntu VPS** par **24/7** chalta hai.  
Iske zariye tum apne **tmux sessions** ko **Telegram se control** kar sakte ho — bina SSH kiye!

### ✨ Features
- 📋 **Sabhi tmux sessions dekho** — ek click mein
- 💀 **Session kill karo** — confirmation dialog ke saath
- 🔁 **Session restart karo** — ek button se
- ➕ **Nayi session banao** — command ke saath
- 📄 **Session logs dekho** — live output
- ⌨️ **Session mein command bhejo** — remotely
- 📊 **VPS status dekho** — CPU, RAM, Disk
- 🖱️ **Bottom Menu Buttons** — commands type karne ki zaroorat nahi
- 🔒 **Security** — sirf authorized Chat ID use kar sakta hai
- ♻️ **Auto Restart** — crash hone par khud restart
- 🚀 **Auto Start on Boot** — VPS restart par bot khud chalu

---

## 📁 File Structure

```
telegram-tmux-bot/
├── bot.py              ← Main bot (commands + inline buttons + menu)
├── config.py           ← 🔑 Bot Token & Chat ID (YAHAN DAALO)
├── tmux_manager.py     ← tmux commands ka wrapper
├── system_monitor.py   ← CPU/RAM/Disk stats
├── requirements.txt    ← Python dependencies
├── install.sh          ← Auto setup script
└── tmux-bot.service    ← systemd service template
```

---

## ⚙️ Setup — Step by Step

### Zaroorat Kya Hai?
- Ubuntu VPS (18.04 / 20.04 / 22.04)
- Python 3.10+
- Telegram Bot Token (`@BotFather` se banao)
- Apna Telegram Chat ID (`@userinfobot` se pata karo)

---

### Step 1 — Files VPS Par Copy Karo

**Option A — Git Clone (Recommended)**
```bash
cd ~
git clone https://github.com/tumhara-username/telegram-tmux-bot.git
cd telegram-tmux-bot
```

**Option B — SCP se Local PC se Upload**
```bash
# Local PC par yeh command chalao
scp -r telegram-tmux-bot/ user@VPS_IP:~/
```

---

### Step 2 — config.py Edit Karo ⚠️

```bash
nano config.py
```

Yeh do cheezein apni daalo:

```python
BOT_TOKEN        = "1234567890:ABCdefGHI..."   # @BotFather se mila token
ALLOWED_CHAT_IDS = [987654321]                 # Tumhara Chat ID (integer)
```

**Chat ID kaise pata kare?**  
Telegram mein `@userinfobot` search karo → `/start` bhejo → Chat ID dikhega

`Ctrl+X` → `Y` → `Enter` (save karo)

---

### Step 3 — Install Script Chalao

```bash
bash install.sh
```

Yeh script automatically karti hai:
- ✅ `python3`, `pip`, `venv`, `tmux` install
- ✅ Python virtual environment banati hai
- ✅ `requirements.txt` ke sare packages install
- ✅ systemd service install aur enable karti hai

---

### Step 4 — Bot Start Karo

```bash
sudo systemctl start tmux-bot
```

**Status check karo:**
```bash
sudo systemctl status tmux-bot
```
> `active (running)` dikhega → ✅ Bot live hai!

---

### Step 5 — Telegram Par Test Karo

Bot ko `/start` bhejo → Menu dikhega → Test karo! 🎉

---

## 📱 Bot Commands

| Command | Kaam |
|---------|------|
| `/start` | Welcome message + Bottom menu dikhao |
| `/help` | Sabhi commands ki list |
| `/sessions` | Sabhi tmux sessions + Inline Buttons |
| `/status` | VPS CPU / RAM / Disk stats |
| `/new <name> <cmd>` | Nayi tmux session banao |
| `/kill <name>` | Ek session kill karo |
| `/killall` | Sabhi sessions kill karo |
| `/restart <name>` | Session restart karo |
| `/logs <name>` | Session ka output dekho |
| `/send <name> <cmd>` | Session mein command bhejo |

### Examples:
```
/new trading python3 bot.py
/new monitor htop
/new myapp bash start.sh
/kill trading
/restart monitor
/logs trading
/send trading ls -la
```

---

## 🖱️ Bottom Menu Buttons

`/start` karne ke baad chat ke **neeche yeh buttons hamesha dikhenge:**

```
┌──────────────────┬───────────────────┐
│  📋 Sessions     │  📊 System Status │
├──────────────────┼───────────────────┤
│  ➕ New Session  │  💣 Kill All      │
├──────────────────┴───────────────────┤
│            ❓ Help                    │
└───────────────────────────────────────┘
```

**Commands type karne ki zaroorat nahi — bas buttons tap karo!**

---

## 🖱️ Inline Buttons (Sessions List Mein)

`/sessions` ya `📋 Sessions` button tap karne par:

```
🔵 trading  (W:1)
  [📋 Logs]  [🔁 Restart]  [💀 Kill]

🟢 monitor  (W:2)
  [📋 Logs]  [🔁 Restart]  [💀 Kill]

[🔄 Refresh]  [💣 Kill All]
[📊 System Status]
```

> 🟢 = Session attached hai  
> 🔵 = Session detached hai (background mein chal rahi)

**Kill/KillAll se pehle confirmation dialog aata hai — galti se band nahi hogi!**

---

## 🔧 systemd Commands (Daily Use)

```bash
# Bot start karo
sudo systemctl start tmux-bot

# Bot band karo (sirf abhi ke liye)
sudo systemctl stop tmux-bot

# Bot restart karo
sudo systemctl restart tmux-bot

# Status dekho
sudo systemctl status tmux-bot

# Live logs dekho
sudo journalctl -u tmux-bot -f

# Auto-start band karo (VPS restart par nahi chalega)
sudo systemctl disable tmux-bot

# Auto-start on karo
sudo systemctl enable tmux-bot
```

---

## 🔒 Security

- **Chat ID Whitelist:** `config.py` mein sirf listed Chat IDs hi bot use kar sakte hain
- **Confirmation Dialog:** Kill aur KillAll commands se pehle confirm karna padta hai
- **Safe Commands:** `shlex.quote()` se command injection se protection
- **Unauthorized Log:** Koi aur try kare toh `bot_activity.log` mein record hota hai

---

## 📊 VPS Status Example

```
🖥️ System Status
──────────────────────────────
⏱️ Uptime:    2d 5h 30m
🔥 CPU:       12.5%  (2 cores)
📊 Load Avg:  0.15 | 0.20 | 0.18
💾 RAM:       1.2 / 4.0 GB  (30%)
💿 Disk:      15.1 / 50.0 GB  (30%)
🌐 Net ↑:     250.5 MB
🌐 Net ↓:     1024.3 MB
```

---

## 🐛 Troubleshooting

| Samasya | Hal |
|---------|-----|
| Bot respond nahi kar raha | `sudo journalctl -u tmux-bot -f` se error dekho |
| "Unauthorized" message aa raha | `config.py` mein sahi Chat ID daalo |
| `tmux: command not found` | `sudo apt install tmux` |
| Sessions list khaali hai | VPS par koi tmux session nahi chal rahi |
| `Conflict` error | Bot 2 jagah chal raha — ek band karo |
| Bot start nahi ho raha | `config.py` mein sahi Bot Token daalo |

**Error log dekhne ka tarika:**
```bash
sudo journalctl -u tmux-bot -f
# Ya
tail -f bot_activity.log
```

---

## 📦 Dependencies

```
python-telegram-bot==20.7
psutil==5.9.8
```

---

## 🔄 Bot Update Kaise Karo

```bash
# 1. Nayi files upload karo / git pull karo
git pull

# 2. Bot restart karo
sudo systemctl restart tmux-bot

# 3. Status check karo
sudo systemctl status tmux-bot
```

---

## 📜 License

MIT License — Free to use, modify and distribute.

---

<div align="center">

**Banaya gaya ❤️ ke saath — Ubuntu VPS users ke liye**

⭐ Agar kaam aaya toh GitHub par Star zaroor do!

</div>
