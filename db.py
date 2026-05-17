import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "agent.db"


def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            channel_id TEXT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_conv_user ON conversations(user_id, id);

        CREATE TABLE IF NOT EXISTS kv_store (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()


def get_history(user_id: str, limit: int = 20) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT role, content FROM conversations WHERE user_id = ? ORDER BY id DESC LIMIT ?",
        (user_id, limit),
    ).fetchall()
    conn.close()
    return [{"role": r, "content": c} for r, c in reversed(rows)]


def append_message(user_id: str, role: str, content: str, channel_id: str = None):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO conversations (user_id, channel_id, role, content, created_at) VALUES (?, ?, ?, ?, ?)",
        (user_id, channel_id, role, content, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def kv_set(key: str, value: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR REPLACE INTO kv_store (key, value, updated_at) VALUES (?, ?, ?)",
        (key, value, datetime.now().isoformat()),
    )
    conn.commit()
    conn.close()


def kv_get(key: str) -> str | None:
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute("SELECT value FROM kv_store WHERE key = ?", (key,)).fetchone()
    conn.close()
    return row[0] if row else None
