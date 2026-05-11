# ============================================================
#  system_monitor.py  —  CPU / RAM / Disk Stats
# ============================================================

import psutil
import platform
import os
from datetime import datetime, timedelta


def get_uptime() -> str:
    """System uptime return karo."""
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time
    days    = uptime.days
    hours, remainder = divmod(uptime.seconds, 3600)
    minutes = remainder // 60
    return f"{days}d {hours}h {minutes}m"


def get_system_stats() -> str:
    """Ek formatted system status string return karo."""
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_count   = psutil.cpu_count()

    # RAM
    ram         = psutil.virtual_memory()
    ram_used    = ram.used  / (1024 ** 3)
    ram_total   = ram.total / (1024 ** 3)
    ram_percent = ram.percent

    # Disk (root partition)
    disk        = psutil.disk_usage("/")
    disk_used   = disk.used  / (1024 ** 3)
    disk_total  = disk.total / (1024 ** 3)
    disk_percent= disk.percent

    # Network (bytes sent/recv since boot)
    net         = psutil.net_io_counters()
    net_sent    = net.bytes_sent / (1024 ** 2)
    net_recv    = net.bytes_recv / (1024 ** 2)

    # Load average (Linux only)
    try:
        load1, load5, load15 = os.getloadavg()
        load_str = f"{load1:.2f} | {load5:.2f} | {load15:.2f}"
    except AttributeError:
        load_str = "N/A"

    uptime = get_uptime()

    msg = (
        f"🖥️ *System Status*\n"
        f"{'─'*30}\n"
        f"⏱️ *Uptime:*    `{uptime}`\n"
        f"🔥 *CPU:*       `{cpu_percent:.1f}%`  ({cpu_count} cores)\n"
        f"📊 *Load Avg:*  `{load_str}`\n"
        f"💾 *RAM:*       `{ram_used:.1f} / {ram_total:.1f} GB  ({ram_percent}%)`\n"
        f"💿 *Disk:*      `{disk_used:.1f} / {disk_total:.1f} GB  ({disk_percent}%)`\n"
        f"🌐 *Net ↑:*     `{net_sent:.1f} MB`\n"
        f"🌐 *Net ↓:*     `{net_recv:.1f} MB`\n"
    )
    return msg
