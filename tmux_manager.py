# ============================================================
#  tmux_manager.py  —  tmux Commands Wrapper
# ============================================================

import subprocess
import shlex
from config import COMMAND_TIMEOUT


def _run(cmd: str) -> tuple[bool, str]:
    """Shell command run karo aur (success, output) return karo."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True,
            text=True, timeout=COMMAND_TIMEOUT
        )
        output = (result.stdout + result.stderr).strip()
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "❌ Command timeout ho gaya."
    except Exception as e:
        return False, f"❌ Error: {e}"


# ── Session List ─────────────────────────────────────────────
def list_sessions() -> list[dict]:
    """
    Sabhi tmux sessions ki list return karo.
    Har item: {"name": str, "windows": str, "created": str, "attached": bool}
    """
    ok, out = _run(
        "tmux list-sessions -F "
        "'#{session_name}|#{session_windows}|#{session_created_string}|#{session_attached}'"
    )
    if not ok or not out:
        return []

    sessions = []
    for line in out.splitlines():
        parts = line.strip().split("|")
        if len(parts) >= 4:
            sessions.append({
                "name":     parts[0],
                "windows":  parts[1],
                "created":  parts[2],
                "attached": parts[3] == "1",
            })
    return sessions


# ── Kill Session ──────────────────────────────────────────────
def kill_session(name: str) -> tuple[bool, str]:
    """Ek specific session kill karo."""
    safe_name = shlex.quote(name)
    ok, out = _run(f"tmux kill-session -t {safe_name}")
    if ok:
        return True, f"✅ Session `{name}` kill kar diya."
    return False, f"❌ Session kill nahi hua: {out}"


# ── Kill All Sessions ─────────────────────────────────────────
def kill_all_sessions() -> tuple[bool, str]:
    """Sabhi sessions kill karo."""
    ok, out = _run("tmux kill-server")
    if ok:
        return True, "✅ Sabhi tmux sessions kill kar diye."
    return False, f"❌ Kill nahi hua: {out}"


# ── New Session ───────────────────────────────────────────────
def new_session(name: str, command: str = "") -> tuple[bool, str]:
    """Nayi detached tmux session banao."""
    safe_name = shlex.quote(name)
    if command:
        safe_cmd = shlex.quote(command)
        ok, out = _run(f"tmux new-session -d -s {safe_name} {safe_cmd}")
    else:
        ok, out = _run(f"tmux new-session -d -s {safe_name}")
    if ok:
        return True, f"✅ Session `{name}` shuru ho gayi."
    return False, f"❌ Session nahi bani: {out}"


# ── Restart Session ───────────────────────────────────────────
def restart_session(name: str) -> tuple[bool, str]:
    """Session kill karke wahi command se dobara start karo."""
    # Pehle command fetch karo
    safe_name = shlex.quote(name)
    ok_env, env_out = _run(
        f"tmux display-message -p -t {safe_name} '#{{pane_current_command}}'"
    )
    kill_ok, kill_msg = kill_session(name)
    if not kill_ok:
        return False, kill_msg

    command = env_out.strip() if ok_env and env_out.strip() else ""
    return new_session(name, command)


# ── Session Logs ──────────────────────────────────────────────
def get_logs(name: str, lines: int = 30) -> tuple[bool, str]:
    """Session ka pane output capture karo."""
    safe_name = shlex.quote(name)
    ok, out = _run(
        f"tmux capture-pane -p -t {safe_name} -S -{lines}"
    )
    if ok:
        return True, out if out.strip() else "(Koi output nahi mila)"
    return False, f"❌ Logs nahi mile: {out}"


# ── Send Keys ─────────────────────────────────────────────────
def send_keys(name: str, keys: str) -> tuple[bool, str]:
    """Session mein keystrokes bhejo (command run karne ke liye)."""
    safe_name = shlex.quote(name)
    safe_keys = shlex.quote(keys)
    ok, out = _run(f"tmux send-keys -t {safe_name} {safe_keys} Enter")
    if ok:
        return True, f"✅ Command bhej diya: `{keys}`"
    return False, f"❌ Nahi bheja: {out}"
