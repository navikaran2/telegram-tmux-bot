# ============================================================
#  bot.py  —  Main Telegram Bot  (python-telegram-bot v20+)
#  Features:
#    /start /help /sessions /status /new /kill /killall
#    /restart /logs /send  + Inline Buttons + Bottom Menu
# ============================================================

import logging
import html
from datetime import datetime

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, BotCommand
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from telegram.constants import ParseMode

import config
import tmux_manager as tmux
import system_monitor as sysmon

# ── Logging Setup ────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ╔══════════════════════════════════════════════════════════╗
#  SECURITY GUARD — Sirf authorized users ko allow karo
# ╚══════════════════════════════════════════════════════════╝
def authorized(update: Update) -> bool:
    uid = update.effective_chat.id
    if uid not in config.ALLOWED_CHAT_IDS:
        logger.warning(f"Unauthorized access attempt from chat_id={uid}")
        return False
    return True


# ╔══════════════════════════════════════════════════════════╗
#  PERSISTENT BOTTOM MENU KEYBOARD
# ╚══════════════════════════════════════════════════════════╝
def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Chat ke neeche hamesha dikhne wala menu."""
    buttons = [
        [KeyboardButton("📋 Sessions"),  KeyboardButton("📊 System Status")],
        [KeyboardButton("➕ New Session"), KeyboardButton("💣 Kill All")],
        [KeyboardButton("❓ Help")],
    ]
    return ReplyKeyboardMarkup(
        buttons,
        resize_keyboard=True,      # Keyboard compact rahega
        persistent=True,           # Hamesha dikhta rahega
        input_field_placeholder="Menu se select karo ya command type karo..."
    )


# ╔══════════════════════════════════════════════════════════╗
#  HELPER: Session List → Inline Keyboard banana
# ╚══════════════════════════════════════════════════════════╝
def build_sessions_keyboard(sessions: list[dict], action: str = "menu") -> InlineKeyboardMarkup:
    """
    Har session ke liye ek row banao jisme:
      [📋 Logs]  [🔁 Restart]  [💀 Kill]
    """
    buttons = []
    for s in sessions:
        name = s["name"]
        status = "🟢" if s["attached"] else "🔵"
        buttons.append([
            InlineKeyboardButton(
                f"{status} {name}  (W:{s['windows']})",
                callback_data=f"info|{name}"
            )
        ])
        buttons.append([
            InlineKeyboardButton("📋 Logs",    callback_data=f"logs|{name}"),
            InlineKeyboardButton("🔁 Restart", callback_data=f"restart_confirm|{name}"),
            InlineKeyboardButton("💀 Kill",    callback_data=f"kill_confirm|{name}"),
        ])

    # Footer buttons
    buttons.append([
        InlineKeyboardButton("🔄 Refresh",      callback_data="refresh_sessions"),
        InlineKeyboardButton("💣 Kill All",     callback_data="killall_confirm"),
    ])
    buttons.append([
        InlineKeyboardButton("📊 System Status", callback_data="status"),
    ])
    return InlineKeyboardMarkup(buttons)


def sessions_text(sessions: list[dict]) -> str:
    if not sessions:
        return "📭 Koi tmux session nahi chal rahi."
    now = datetime.now().strftime("%H:%M:%S")
    lines = [f"🖥️ *tmux Sessions*  `[{now}]`\n{'─'*28}"]
    for s in sessions:
        icon = "🟢 *Attached*" if s["attached"] else "🔵 Detached"
        lines.append(
            f"\n*{html.escape(s['name'])}*\n"
            f"  {icon} | Windows: {s['windows']}\n"
            f"  🕒 {s['created']}"
        )
    return "\n".join(lines)


# ╔══════════════════════════════════════════════════════════╗
#  COMMAND HANDLERS
# ╚══════════════════════════════════════════════════════════╝

async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    await update.message.reply_text(
        f"👋 *{config.BOT_NAME}*\n\n"
        "tmux sessions ko Telegram se control karo!\n\n"
        "📌 *Neeche menu buttons hain — bas tap karo!*\n"
        "Ya commands type karo: /help",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=main_menu_keyboard()
    )


async def cmd_help(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    text = (
        f"*{config.BOT_NAME} — Commands*\n"
        f"{'─'*30}\n\n"
        "📋 *Session Management*\n"
        "`/sessions`  — Sabhi sessions + inline buttons\n"
        "`/new <name> [cmd]`  — Nayi session banao\n"
        "`/kill <name>`  — Ek session kill karo\n"
        "`/killall`  — Sabhi sessions kill karo\n"
        "`/restart <name>`  — Session restart karo\n\n"
        "🔍 *Info & Logs*\n"
        "`/logs <name>`  — Session output dekho\n"
        "`/status`  — VPS CPU/RAM/Disk status\n\n"
        "⌨️ *Control*\n"
        "`/send <name> <command>`  — Session mein command bhejo\n\n"
        "ℹ️ *Bot*\n"
        "`/start`  — Welcome message\n"
        "`/help`  — Yeh list\n"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_sessions(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    sessions = tmux.list_sessions()
    text = sessions_text(sessions)
    keyboard = build_sessions_keyboard(sessions)
    await update.message.reply_text(
        text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN
    )


async def cmd_status(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    msg = await update.message.reply_text("⏳ System stats le raha hoon...")
    stats = sysmon.get_system_stats()
    await msg.edit_text(stats, parse_mode=ParseMode.MARKDOWN)


async def cmd_new(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    args = ctx.args
    if not args:
        await update.message.reply_text(
            "⚠️ Usage: `/new <name> [command]`\n"
            "Example: `/new trading python3 bot.py`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    name    = args[0]
    command = " ".join(args[1:]) if len(args) > 1 else ""
    ok, msg = tmux.new_session(name, command)
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


async def cmd_kill(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    if not ctx.args:
        await update.message.reply_text(
            "⚠️ Usage: `/kill <session_name>`", parse_mode=ParseMode.MARKDOWN
        )
        return
    name = ctx.args[0]
    # Confirmation buttons
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Haan, Kill Karo", callback_data=f"kill_do|{name}"),
        InlineKeyboardButton("❌ Nahi",            callback_data="cancel"),
    ]])
    await update.message.reply_text(
        f"⚠️ *Session `{name}` kill karna chahte ho?*",
        reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN
    )


async def cmd_killall(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("💣 Haan, Sabhi Kill Karo", callback_data="killall_do"),
        InlineKeyboardButton("❌ Nahi",                  callback_data="cancel"),
    ]])
    await update.message.reply_text(
        "⚠️ *Sabhi tmux sessions kill karna chahte ho?*\n"
        "Yeh action wapas nahi hoga!",
        reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN
    )


async def cmd_restart(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    if not ctx.args:
        await update.message.reply_text(
            "⚠️ Usage: `/restart <session_name>`", parse_mode=ParseMode.MARKDOWN
        )
        return
    name = ctx.args[0]
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton("🔁 Haan, Restart Karo", callback_data=f"restart_do|{name}"),
        InlineKeyboardButton("❌ Nahi",               callback_data="cancel"),
    ]])
    await update.message.reply_text(
        f"⚠️ *Session `{name}` restart karna chahte ho?*",
        reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN
    )


async def cmd_logs(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    if not ctx.args:
        await update.message.reply_text(
            "⚠️ Usage: `/logs <session_name>`", parse_mode=ParseMode.MARKDOWN
        )
        return
    name = ctx.args[0]
    ok, output = tmux.get_logs(name, config.MAX_LOG_LINES)
    header = f"📋 *Logs — `{name}`*\n{'─'*28}\n"
    # Telegram message limit 4096 chars
    content = output[-3500:] if len(output) > 3500 else output
    await update.message.reply_text(
        header + f"```\n{content}\n```",
        parse_mode=ParseMode.MARKDOWN
    )


async def cmd_send(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    args = ctx.args
    if len(args) < 2:
        await update.message.reply_text(
            "⚠️ Usage: `/send <name> <command>`\n"
            "Example: `/send trading ls -la`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    name    = args[0]
    command = " ".join(args[1:])
    ok, msg = tmux.send_keys(name, command)
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)


# ╔══════════════════════════════════════════════════════════╗
#  CALLBACK QUERY HANDLER  —  Inline Button Actions
# ╚══════════════════════════════════════════════════════════╝

async def button_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()           # Loading state hatao

    if not authorized(update): return

    data = query.data
    parts = data.split("|", 1)
    action = parts[0]
    name   = parts[1] if len(parts) > 1 else ""

    # ── Cancel ──────────────────────────────────────────────
    if action == "cancel":
        await query.edit_message_text("❎ Action cancel kar diya.")

    # ── Refresh Sessions ────────────────────────────────────
    elif action == "refresh_sessions":
        sessions = tmux.list_sessions()
        text     = sessions_text(sessions)
        keyboard = build_sessions_keyboard(sessions)
        await query.edit_message_text(
            text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN
        )

    # ── Session Info (header button click) ──────────────────
    elif action == "info":
        sessions = tmux.list_sessions()
        s = next((x for x in sessions if x["name"] == name), None)
        if s:
            msg = (
                f"ℹ️ *Session: `{name}`*\n"
                f"  Windows: `{s['windows']}`\n"
                f"  Created: `{s['created']}`\n"
                f"  Status:  {'🟢 Attached' if s['attached'] else '🔵 Detached'}"
            )
        else:
            msg = f"❌ Session `{name}` nahi mili."
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("📋 Logs",    callback_data=f"logs|{name}"),
            InlineKeyboardButton("🔁 Restart", callback_data=f"restart_confirm|{name}"),
            InlineKeyboardButton("💀 Kill",    callback_data=f"kill_confirm|{name}"),
        ], [
            InlineKeyboardButton("⬅️ Wapas",  callback_data="refresh_sessions"),
        ]])
        await query.edit_message_text(
            msg, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN
        )

    # ── System Status ────────────────────────────────────────
    elif action == "status":
        stats = sysmon.get_system_stats()
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("⬅️ Sessions", callback_data="refresh_sessions"),
        ]])
        await query.edit_message_text(
            stats, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN
        )

    # ── Logs ─────────────────────────────────────────────────
    elif action == "logs":
        ok, output = tmux.get_logs(name, config.MAX_LOG_LINES)
        content = output[-3200:] if len(output) > 3200 else output
        header  = f"📋 *Logs — `{name}`*\n{'─'*28}\n"
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔄 Refresh Logs", callback_data=f"logs|{name}"),
            InlineKeyboardButton("⬅️ Wapas",        callback_data="refresh_sessions"),
        ]])
        await query.edit_message_text(
            header + f"```\n{content}\n```",
            reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN
        )

    # ── Kill Confirm ─────────────────────────────────────────
    elif action == "kill_confirm":
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("✅ Haan, Kill Karo", callback_data=f"kill_do|{name}"),
            InlineKeyboardButton("❌ Nahi",            callback_data="refresh_sessions"),
        ]])
        await query.edit_message_text(
            f"⚠️ *Session `{name}` kill karna chahte ho?*",
            reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN
        )

    # ── Kill Do ──────────────────────────────────────────────
    elif action == "kill_do":
        ok, msg = tmux.kill_session(name)
        sessions = tmux.list_sessions()
        text     = msg + "\n\n" + sessions_text(sessions)
        keyboard = build_sessions_keyboard(sessions)
        await query.edit_message_text(
            text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN
        )

    # ── Kill All Confirm ──────────────────────────────────────
    elif action == "killall_confirm":
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("💣 Haan, Sabhi Kill", callback_data="killall_do"),
            InlineKeyboardButton("❌ Nahi",             callback_data="refresh_sessions"),
        ]])
        await query.edit_message_text(
            "⚠️ *Sabhi tmux sessions kill karna chahte ho?*",
            reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN
        )

    # ── Kill All Do ───────────────────────────────────────────
    elif action == "killall_do":
        ok, msg = tmux.kill_all_sessions()
        await query.edit_message_text(msg, parse_mode=ParseMode.MARKDOWN)

    # ── Restart Confirm ───────────────────────────────────────
    elif action == "restart_confirm":
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton("🔁 Haan, Restart", callback_data=f"restart_do|{name}"),
            InlineKeyboardButton("❌ Nahi",          callback_data=f"info|{name}"),
        ]])
        await query.edit_message_text(
            f"⚠️ *Session `{name}` restart karna chahte ho?*",
            reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN
        )

    # ── Restart Do ────────────────────────────────────────────
    elif action == "restart_do":
        ok, msg = tmux.restart_session(name)
        sessions = tmux.list_sessions()
        text     = msg + "\n\n" + sessions_text(sessions)
        keyboard = build_sessions_keyboard(sessions)
        await query.edit_message_text(
            text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN
        )


# ── Unknown command ───────────────────────────────────────────
async def unknown_cmd(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    if not authorized(update): return
    await update.message.reply_text(
        "❓ Yeh command nahi pehchana. `/help` try karo.",
        parse_mode=ParseMode.MARKDOWN
    )


# ── Menu Button Text Handler ──────────────────────────────────
MENU_MAP = {
    "📋 Sessions":     cmd_sessions,
    "📊 System Status": cmd_status,
    "❓ Help":          cmd_help,
}

async def menu_button_handler(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    """Bottom menu buttons ka text pakad kar sahi command chalao."""
    if not authorized(update): return
    text = update.message.text

    if text in MENU_MAP:
        await MENU_MAP[text](update, ctx)

    elif text == "➕ New Session":
        await update.message.reply_text(
            "➕ *Nayi Session Banao*\n\n"
            "Command bhejo:\n"
            "`/new <name> <command>`\n\n"
            "*Examples:*\n"
            "`/new trading python3 bot.py`\n"
            "`/new monitor htop`\n"
            "`/new myapp bash run.sh`",
            parse_mode=ParseMode.MARKDOWN
        )

    elif text == "💣 Kill All":
        await cmd_killall(update, ctx)


# ╔══════════════════════════════════════════════════════════╗
#  MAIN
# ╚══════════════════════════════════════════════════════════╝
async def post_init(app):
    """Bot start hone par BotCommand list register karo (/ menu ke liye)."""
    await app.bot.set_my_commands([
        BotCommand("start",    "👋 Welcome + Menu dikhao"),
        BotCommand("sessions", "📋 Sabhi tmux sessions"),
        BotCommand("status",   "📊 VPS CPU/RAM/Disk stats"),
        BotCommand("new",      "➕ Nayi session banao"),
        BotCommand("kill",     "💀 Ek session kill karo"),
        BotCommand("killall",  "💣 Sabhi sessions kill karo"),
        BotCommand("restart",  "🔁 Session restart karo"),
        BotCommand("logs",     "📄 Session output dekho"),
        BotCommand("send",     "⌨️ Session mein command bhejo"),
        BotCommand("help",     "❓ Sab commands ki list"),
    ])
    logger.info("✅ BotCommands register ho gaye.")


def main():
    logger.info("🚀 Telegram tmux Bot shuru ho raha hai...")

    app = (
        Application.builder()
        .token(config.BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # ── Slash Commands ────────────────────────────────────────
    app.add_handler(CommandHandler("start",    cmd_start))
    app.add_handler(CommandHandler("help",     cmd_help))
    app.add_handler(CommandHandler("sessions", cmd_sessions))
    app.add_handler(CommandHandler("status",   cmd_status))
    app.add_handler(CommandHandler("new",      cmd_new))
    app.add_handler(CommandHandler("kill",     cmd_kill))
    app.add_handler(CommandHandler("killall",  cmd_killall))
    app.add_handler(CommandHandler("restart",  cmd_restart))
    app.add_handler(CommandHandler("logs",     cmd_logs))
    app.add_handler(CommandHandler("send",     cmd_send))

    # ── Inline Button Callbacks ───────────────────────────────
    app.add_handler(CallbackQueryHandler(button_handler))

    # ── Bottom Menu Button Text Handler ──────────────────────
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        menu_button_handler
    ))

    # ── Unknown Commands ──────────────────────────────────────
    app.add_handler(MessageHandler(filters.COMMAND, unknown_cmd))

    logger.info("✅ Bot ready! Polling shuru...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
