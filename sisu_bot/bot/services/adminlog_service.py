import json
import os
import datetime

ADMINLOG_FILE = os.path.join(os.path.dirname(__file__), '../../data/adminlog.json')


def log_admin_action(user_id, username, command, params=None, result=None):
    log = {
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user_id": user_id,
        "username": username,
        "command": command,
        "params": params,
        "result": result
    }
    logs = []
    if os.path.exists(ADMINLOG_FILE):
        try:
            with open(ADMINLOG_FILE, 'r', encoding='utf-8') as f:
                logs = json.load(f)
        except Exception:
            logs = []
    logs.append(log)
    # Ограничиваем размер лога (например, 1000 записей)
    logs = logs[-1000:]
    with open(ADMINLOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)


def get_admin_logs(limit=20):
    if not os.path.exists(ADMINLOG_FILE):
        return []
    with open(ADMINLOG_FILE, 'r', encoding='utf-8') as f:
        try:
            logs = json.load(f)
        except Exception:
            return []
    return logs[-limit:][::-1]  # последние N, в обратном порядке (свежие сверху) 