"""
議事録自動取込・NA抽出エンジン。

監視対象メール送信元:
  notifications@circleback.ai   (Circleback AI)
  gemini-notes@google.com       (Google Gemini Meeting Notes)

処理フロー:
  1. 15分ごとに新着議事録メールをチェック
  2. Claude で議事録全文を解析 → NA・決定事項・参加者を抽出
  3. Slack #議事録チャンネル に構造化サマリーを投稿
  4. 抽出したNAをDBに登録 → 期限チェックで毎朝リマインド

Required env:
  ANTHROPIC_API_KEY
Optional env:
  MINUTES_CHANNEL  Slack チャンネル名またはID (default: #議事録)
"""

import json
import logging
import os
import sqlite3
from datetime import datetime, timezone

import anthropic
import google_client
from db import DB_PATH

logger = logging.getLogger(__name__)

MINUTES_CHANNEL = os.getenv("MINUTES_CHANNEL", "#議事録")

MEETING_NOTES_SENDERS = [
    "notifications@circleback.ai",
    "gemini-notes@google.com",
]

_claude = None


def _get_claude():
    global _claude
    if not _claude:
        _claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _claude


# ── DB 初期化 ──────────────────────────────────────────────────────────────────

def init_meetings_table():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS processed_meetings (
            email_id   TEXT PRIMARY KEY,
            meeting_title TEXT,
            meeting_date  TEXT,
            processed_at  TEXT,
            slack_ts      TEXT
        );

        CREATE TABLE IF NOT EXISTS meeting_nas (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            email_id      TEXT,
            meeting_title TEXT,
            meeting_date  TEXT,
            action        TEXT,
            owner         TEXT,
            deadline      TEXT,
            priority      TEXT DEFAULT 'MEDIUM',
            completed     INTEGER DEFAULT 0,
            created_at    TEXT
        );
    """)
    conn.commit()
    conn.close()


def _is_processed(email_id: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT 1 FROM processed_meetings WHERE email_id=?", (email_id,)
    ).fetchone()
    conn.close()
    return row is not None


def _mark_processed(email_id: str, title: str, date: str, slack_ts: str = ""):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """INSERT OR REPLACE INTO processed_meetings
           (email_id, meeting_title, meeting_date, processed_at, slack_ts)
           VALUES (?, ?, ?, ?, ?)""",
        (email_id, title, date, datetime.now(timezone.utc).isoformat(), slack_ts),
    )
    conn.commit()
    conn.close()


def _save_nas(email_id: str, title: str, date: str, nas: list[dict]):
    if not nas:
        return
    conn = sqlite3.connect(DB_PATH)
    now = datetime.now(timezone.utc).isoformat()
    for na in nas:
        conn.execute(
            """INSERT INTO meeting_nas
               (email_id, meeting_title, meeting_date, action, owner, deadline, priority, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                email_id, title, date,
                na.get("action", ""),
                na.get("owner", "Rui"),
                na.get("deadline", ""),
                na.get("priority", "MEDIUM"),
                now,
            ),
        )
    conn.commit()
    conn.close()


# ── Claude 解析 ────────────────────────────────────────────────────────────────

EXTRACT_PROMPT = """あなたはRui Sasase（Pyrenee Inc. US Evangelist）の議事録解析AIです。

以下の議事録テキストを解析して、JSONのみ返してください。

抽出項目:
- meeting_title: ミーティング名（件名から推定可）
- meeting_date: 開催日 YYYY-MM-DD（不明なら""）
- participants: 参加者リスト（名前 or メール、最大10名）
- decisions: 決定事項リスト（各15〜40字、最大8件）
- next_actions: NAリスト
    action   : 具体的なアクション（日本語または英語）
    owner    : 担当者名（不明なら"Rui"）
    deadline : 期限 YYYY-MM-DD（不明なら""）
    priority : "HIGH" | "MEDIUM" | "LOW"
- key_topics: 主要トピックの要約（3〜5行、日本語）

JSONのみ返すこと（```や説明文は不要）:
{
  "meeting_title": "",
  "meeting_date": "",
  "participants": [],
  "decisions": [],
  "next_actions": [{"action":"","owner":"","deadline":"","priority":"MEDIUM"}],
  "key_topics": ""
}"""


def _extract_meeting_data(body: str, subject: str) -> dict:
    client = _get_claude()
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2048,
        system=EXTRACT_PROMPT,
        messages=[{
            "role": "user",
            "content": f"件名: {subject}\n\n議事録本文:\n{body[:8000]}",
        }],
    )
    text = response.content[0].text.strip()
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    return json.loads(text)


# ── Slack メッセージ整形 ────────────────────────────────────────────────────────

_PRIORITY_EMOJI = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢"}


def _format_slack_message(data: dict, sender: str) -> str:
    title = data.get("meeting_title", "ミーティング")
    date = data.get("meeting_date", "")
    participants = data.get("participants", [])
    decisions = data.get("decisions", [])
    nas = data.get("next_actions", [])
    topics = data.get("key_topics", "")

    source = "Circleback" if "circleback" in sender else "Gemini"

    lines = [
        f"📋 *議事録自動取込* [{source}]",
        f"*{title}*  {date}",
        "",
    ]

    if participants:
        lines.append(f"👥 {' / '.join(participants[:8])}")
        lines.append("")

    if topics:
        lines.append("*📝 主要トピック*")
        lines.append(topics)
        lines.append("")

    if decisions:
        lines.append("*✅ 決定事項*")
        for d in decisions:
            lines.append(f"• {d}")
        lines.append("")

    if nas:
        lines.append("*🎯 Next Actions*")
        for na in nas:
            emoji = _PRIORITY_EMOJI.get(na.get("priority", "MEDIUM"), "🟡")
            owner = na.get("owner", "Rui")
            deadline = f"  ⏰ {na['deadline']}" if na.get("deadline") else ""
            lines.append(f"{emoji} *{owner}*: {na.get('action', '')}{deadline}")
        lines.append("")

    lines.append("_NAは自動でフォローアップ追跡に登録済み_")
    return "\n".join(lines)


# ── メイン処理 ─────────────────────────────────────────────────────────────────

def run_meeting_notes_watcher(app=None, rui_user_id: str = "") -> int:
    """
    新着議事録メールを検索・処理してSlackに投稿する。
    戻り値: 処理した議事録数
    """
    if not google_client.is_configured():
        return 0

    processed_count = 0

    for sender in MEETING_NOTES_SENDERS:
        try:
            emails = google_client.get_emails(
                query=f"from:{sender} newer_than:2d",
                max_results=10,
            )

            for email in emails:
                email_id = email["id"]
                if _is_processed(email_id):
                    continue

                body = google_client.get_email_body(email_id)
                if not body or len(body) < 100:
                    continue

                try:
                    data = _extract_meeting_data(body, email.get("subject", ""))
                except Exception as e:
                    logger.error(f"Extract failed {email_id}: {e}")
                    continue

                message = _format_slack_message(data, email.get("from", ""))

                # #議事録 チャンネルに投稿、失敗時はDMにフォールバック
                slack_ts = ""
                if app:
                    try:
                        result = app.client.chat_postMessage(
                            channel=MINUTES_CHANNEL,
                            text=message,
                        )
                        slack_ts = result.get("ts", "")
                    except Exception as e:
                        logger.warning(f"Channel post failed, falling back to DM: {e}")
                        if rui_user_id:
                            try:
                                dm = app.client.conversations_open(users=rui_user_id)
                                app.client.chat_postMessage(
                                    channel=dm["channel"]["id"],
                                    text=message,
                                )
                            except Exception as e2:
                                logger.error(f"DM fallback failed: {e2}")

                title = data.get("meeting_title", email.get("subject", ""))
                date = data.get("meeting_date", "")
                _save_nas(email_id, title, date, data.get("next_actions", []))
                _mark_processed(email_id, title, date, slack_ts)
                processed_count += 1
                logger.info(f"Meeting notes processed: {title}")

        except Exception as e:
            logger.error(f"Watcher error [{sender}]: {e}")

    return processed_count


# ── NA リマインダー ────────────────────────────────────────────────────────────

def check_na_reminders(app=None, rui_user_id: str = "") -> list[str]:
    """期限切れ・期限間近のNAをSlack DM でリマインドする。"""
    now = datetime.now(timezone.utc)
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """SELECT id, meeting_title, action, owner, deadline, priority
           FROM meeting_nas
           WHERE completed=0 AND deadline != ''
           ORDER BY deadline ASC"""
    ).fetchall()
    conn.close()

    overdue, due_soon = [], []

    for row in rows:
        na_id, title, action, owner, deadline, priority = row
        try:
            dl_dt = datetime.fromisoformat(f"{deadline}T00:00:00+00:00")
            days_left = (dl_dt - now).days
            emoji = _PRIORITY_EMOJI.get(priority, "🟡")
            line = f"{emoji} *{owner}*: {action}\n  　_[{title}]_"
            if days_left < 0:
                overdue.append(f"• ⚠️ 期限切れ({abs(days_left)}日超過) {line}")
            elif days_left <= 2:
                due_soon.append(f"• 🔔 あと{days_left}日 {line}")
        except Exception:
            continue

    if not overdue and not due_soon:
        return []

    parts = ["*📌 NA リマインダー*", ""]
    if overdue:
        parts += ["*【期限切れ】*"] + overdue + [""]
    if due_soon:
        parts += ["*【期限間近】*"] + due_soon

    message = "\n".join(parts)

    if app and rui_user_id:
        try:
            dm = app.client.conversations_open(users=rui_user_id)
            app.client.chat_postMessage(channel=dm["channel"]["id"], text=message)
        except Exception as e:
            logger.error(f"NA reminder DM failed: {e}")

    return [message]


# ── 手動実行サポート ───────────────────────────────────────────────────────────

def get_pending_nas() -> list[dict]:
    """未完了NAの一覧を返す（/minutes コマンド等から参照用）。"""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        """SELECT id, meeting_title, meeting_date, action, owner, deadline, priority
           FROM meeting_nas WHERE completed=0
           ORDER BY deadline ASC, priority DESC"""
    ).fetchall()
    conn.close()
    return [
        {
            "id": r[0], "meeting": r[1], "date": r[2],
            "action": r[3], "owner": r[4], "deadline": r[5], "priority": r[6],
        }
        for r in rows
    ]


def mark_na_done(na_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE meeting_nas SET completed=1 WHERE id=?", (na_id,))
    conn.commit()
    conn.close()
