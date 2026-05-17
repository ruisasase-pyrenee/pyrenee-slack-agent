"""
送信済みメールのフォローアップ追跡。

- 送信後3日で返信なし → Slackで「まだ返ってきてないよ」通知
- 送信後7日で返信なし → Slackで最終通知
- 返信が来たら追跡を終了

SQLite テーブル: followup_tracking
  thread_id TEXT PRIMARY KEY
  subject TEXT
  to_addr TEXT
  sent_at TEXT
  reminded_3d INTEGER DEFAULT 0
  reminded_7d INTEGER DEFAULT 0
  resolved INTEGER DEFAULT 0
"""

import logging
from datetime import datetime, timezone, timedelta
import sqlite3
from db import DB_PATH
import google_client

logger = logging.getLogger(__name__)


def init_followup_table():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS followup_tracking (
            thread_id TEXT PRIMARY KEY,
            subject TEXT,
            to_addr TEXT,
            sent_at TEXT,
            reminded_3d INTEGER DEFAULT 0,
            reminded_7d INTEGER DEFAULT 0,
            resolved INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def _upsert_sent(thread_id: str, subject: str, to_addr: str, sent_at: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """INSERT OR IGNORE INTO followup_tracking
           (thread_id, subject, to_addr, sent_at)
           VALUES (?, ?, ?, ?)""",
        (thread_id, subject, to_addr, sent_at),
    )
    conn.commit()
    conn.close()


def _mark_reminded(thread_id: str, days: int):
    col = "reminded_3d" if days == 3 else "reminded_7d"
    conn = sqlite3.connect(DB_PATH)
    conn.execute(f"UPDATE followup_tracking SET {col}=1 WHERE thread_id=?", (thread_id,))
    conn.commit()
    conn.close()


def _mark_resolved(thread_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "UPDATE followup_tracking SET resolved=1 WHERE thread_id=?", (thread_id,)
    )
    conn.commit()
    conn.close()


def _get_pending() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """SELECT thread_id, subject, to_addr, sent_at, reminded_3d, reminded_7d
           FROM followup_tracking WHERE resolved=0"""
    ).fetchall()
    conn.close()
    return [
        {
            "thread_id": r[0],
            "subject": r[1],
            "to_addr": r[2],
            "sent_at": r[3],
            "reminded_3d": r[4],
            "reminded_7d": r[5],
        }
        for r in rows
    ]


def _has_reply(thread_id: str) -> bool:
    """スレッドに自分以外からの返信があるか確認する。"""
    try:
        svc = google_client._gmail()
        if not svc:
            return False
        thread = svc.users().threads().get(userId="me", id=thread_id).execute()
        messages = thread.get("messages", [])
        if len(messages) <= 1:
            return False
        # 2通目以降に "SENT" でないメッセージがあれば返信あり
        for msg in messages[1:]:
            labels = msg.get("labelIds", [])
            if "SENT" not in labels:
                return True
        return False
    except Exception as e:
        logger.warning(f"Thread check failed {thread_id}: {e}")
        return False


def sync_sent_emails():
    """Sentフォルダから最近7日の送信メールをDBに登録する。"""
    if not google_client.is_configured():
        return

    emails = google_client.get_emails(
        query="in:sent newer_than:7d -from:noreply -from:no-reply",
        max_results=30,
    )

    for e in emails:
        _upsert_sent(
            thread_id=e["thread_id"],
            subject=e["subject"],
            to_addr=e["to"],
            sent_at=e["date"],
        )


def check_followups(app=None, rui_user_id: str = "") -> list[str]:
    """
    追跡中のスレッドをチェックして、必要なリマインドをSlackで送る。
    戻り値: 送ったリマインドメッセージのリスト
    """
    if not google_client.is_configured():
        return []

    sync_sent_emails()
    pending = _get_pending()
    now = datetime.now(timezone.utc)
    reminders = []

    for item in pending:
        try:
            sent_dt = datetime.fromisoformat(
                item["sent_at"].replace("Z", "+00:00").replace(" +0000", "+00:00")
            )
        except Exception:
            continue

        days_elapsed = (now - sent_dt).days

        # 返信チェック
        if _has_reply(item["thread_id"]):
            _mark_resolved(item["thread_id"])
            continue

        msg = None

        if days_elapsed >= 7 and not item["reminded_7d"]:
            msg = (
                f"*フォローアップ【最終】*\n"
                f"件名: _{item['subject']}_\n"
                f"宛先: {item['to_addr']}\n"
                f"送信から *7日* 経過。まだ返信なし。"
            )
            _mark_reminded(item["thread_id"], 7)

        elif days_elapsed >= 3 and not item["reminded_3d"]:
            msg = (
                f"*フォローアップ確認*\n"
                f"件名: _{item['subject']}_\n"
                f"宛先: {item['to_addr']}\n"
                f"送信から *3日* 経過。返信を待っています。"
            )
            _mark_reminded(item["thread_id"], 3)

        if msg:
            reminders.append(msg)
            if app and rui_user_id:
                try:
                    result = app.client.conversations_open(users=rui_user_id)
                    channel_id = result["channel"]["id"]
                    app.client.chat_postMessage(channel=channel_id, text=msg)
                except Exception as e:
                    logger.error(f"Slack reminder failed: {e}")

    return reminders
