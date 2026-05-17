"""
Notion自動同期。

- カレンダーのミーティング前にNotionページを自動作成
- 会議ページテンプレート: 参加者 / アジェンダ / メモ欄 / アクションアイテム

Required env:
  NOTION_API_KEY         Notion Integration Token
  NOTION_MEETINGS_DB_ID  ミーティングを記録するNotionデータベースのID
"""

import os
import logging
from datetime import datetime, timezone
import sqlite3
from db import DB_PATH

logger = logging.getLogger(__name__)

NOTION_API_KEY = os.getenv("NOTION_API_KEY", "")
MEETINGS_DB_ID = os.getenv("NOTION_MEETINGS_DB_ID", "")


def is_configured() -> bool:
    return bool(NOTION_API_KEY and MEETINGS_DB_ID)


def _get_client():
    from notion_client import Client
    return Client(auth=NOTION_API_KEY)


def _init_notion_tracking():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS notion_pages (
            calendar_event_id TEXT PRIMARY KEY,
            notion_page_id TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def _already_created(event_id: str) -> bool:
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT notion_page_id FROM notion_pages WHERE calendar_event_id=?", (event_id,)
    ).fetchone()
    conn.close()
    return row is not None


def _save_page(event_id: str, page_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT OR REPLACE INTO notion_pages (calendar_event_id, notion_page_id, created_at) VALUES (?,?,?)",
        (event_id, page_id, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    conn.close()


def create_meeting_page(event: dict) -> str | None:
    """
    カレンダーイベントからNotionミーティングページを作成する。
    作成したページのURLを返す。
    """
    if not is_configured():
        logger.warning("Notion not configured")
        return None

    _init_notion_tracking()

    if _already_created(event["id"]):
        return None

    notion = _get_client()

    title = event.get("title", "ミーティング")
    start = event.get("start", "")
    attendees = event.get("attendees", [])
    location = event.get("location", "")
    meet_link = event.get("meet_link", "")

    # 参加者テキスト
    attendees_text = "\n".join(f"• {a}" for a in attendees) if attendees else "（未設定）"

    # Notion ページ作成
    try:
        page = notion.pages.create(
            parent={"database_id": MEETINGS_DB_ID},
            properties={
                "Name": {
                    "title": [{"text": {"content": title}}]
                },
                "Date": {
                    "date": {"start": start[:10] if start else datetime.now().strftime("%Y-%m-%d")}
                },
            },
            children=[
                _heading("ミーティング情報"),
                _bullet(f"日時: {start}"),
                _bullet(f"場所: {location or meet_link or '未設定'}"),
                _bullet(f"参加者:\n{attendees_text}"),
                _divider(),
                _heading("アジェンダ"),
                _bullet("（記入してください）"),
                _divider(),
                _heading("メモ"),
                _paragraph(""),
                _divider(),
                _heading("アクションアイテム"),
                _todo(""),
            ],
        )
        page_url = page.get("url", "")
        _save_page(event["id"], page["id"])
        logger.info(f"Notion page created: {title} → {page_url}")
        return page_url
    except Exception as e:
        logger.error(f"Notion page creation failed: {e}")
        return None


def sync_upcoming_meetings(app=None, rui_user_id: str = ""):
    """
    今後2日のミーティングのNotionページを作成し、Slackで通知する。
    """
    if not is_configured():
        return

    import google_client
    if not google_client.is_configured():
        return

    events = google_client.get_upcoming_events(days_ahead=2, max_results=10)
    for event in events:
        page_url = create_meeting_page(event)
        if page_url and app and rui_user_id:
            try:
                result = app.client.conversations_open(users=rui_user_id)
                channel_id = result["channel"]["id"]
                app.client.chat_postMessage(
                    channel=channel_id,
                    text=(
                        f"*Notionページを作成しました*\n"
                        f"📅 {event['title']} ({event['start']})\n"
                        f"{page_url}"
                    ),
                )
            except Exception as e:
                logger.error(f"Slack notify failed: {e}")


# ── Notion ブロックヘルパー ────────────────────────────────────────────────────

def _heading(text: str) -> dict:
    return {
        "object": "block",
        "type": "heading_2",
        "heading_2": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def _bullet(text: str) -> dict:
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def _paragraph(text: str) -> dict:
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {"rich_text": [{"type": "text", "text": {"content": text}}]},
    }


def _todo(text: str) -> dict:
    return {
        "object": "block",
        "type": "to_do",
        "to_do": {
            "rich_text": [{"type": "text", "text": {"content": text or "　"}}],
            "checked": False,
        },
    }


def _divider() -> dict:
    return {"object": "block", "type": "divider", "divider": {}}
