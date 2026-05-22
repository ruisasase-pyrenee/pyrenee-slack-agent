"""
Google Gmail + Calendar API client.

Setup:
1. Google Cloud Console でプロジェクト作成
2. Gmail API + Google Calendar API を有効化
3. OAuth 2.0 クライアントID を作成（デスクトップアプリ）
4. credentials.json をこのディレクトリに配置
5. 初回起動時に認証フローが走り token.json が生成される

Required env: (なし。credentials.json / token.json を使用)
Optional env:
  GOOGLE_CREDENTIALS_PATH  (default: credentials.json)
  GOOGLE_TOKEN_PATH        (default: token.json)
  GOOGLE_CALENDAR_ID       (default: primary)
"""

import os
import json
import base64
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

CREDENTIALS_PATH = Path(os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json"))
TOKEN_PATH = Path(os.getenv("GOOGLE_TOKEN_PATH", "token.json"))
CALENDAR_ID = os.getenv("GOOGLE_CALENDAR_ID", "primary")
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/calendar.readonly",
]

_gmail_service = None
_calendar_service = None


def _bootstrap_credentials_from_env():
    """環境変数 GOOGLE_TOKEN_JSON / GOOGLE_CREDENTIALS_JSON からファイルを生成する（Render等クラウド用）。"""
    token_env = os.getenv("GOOGLE_TOKEN_JSON")
    if token_env and not TOKEN_PATH.exists():
        try:
            TOKEN_PATH.write_text(base64.b64decode(token_env).decode())
            logger.info("token.json written from GOOGLE_TOKEN_JSON env var")
        except Exception as e:
            logger.warning(f"Failed to write token.json from env: {e}")

    creds_env = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if creds_env and not CREDENTIALS_PATH.exists():
        try:
            CREDENTIALS_PATH.write_text(base64.b64decode(creds_env).decode())
            logger.info("credentials.json written from GOOGLE_CREDENTIALS_JSON env var")
        except Exception as e:
            logger.warning(f"Failed to write credentials.json from env: {e}")


def _get_creds():
    _bootstrap_credentials_from_env()
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request
        from google_auth_oauthlib.flow import InstalledAppFlow

        creds = None
        if TOKEN_PATH.exists():
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                TOKEN_PATH.write_text(creds.to_json())
            else:
                if not CREDENTIALS_PATH.exists():
                    return None
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)
                TOKEN_PATH.write_text(creds.to_json())

        return creds
    except Exception as e:
        logger.warning(f"Google auth failed: {e}")
        return None


def _gmail():
    global _gmail_service
    if _gmail_service:
        return _gmail_service
    creds = _get_creds()
    if not creds:
        return None
    from googleapiclient.discovery import build
    _gmail_service = build("gmail", "v1", credentials=creds)
    return _gmail_service


def _calendar():
    global _calendar_service
    if _calendar_service:
        return _calendar_service
    creds = _get_creds()
    if not creds:
        return None
    from googleapiclient.discovery import build
    _calendar_service = build("calendar", "v3", credentials=creds)
    return _calendar_service


def is_configured() -> bool:
    return (
        CREDENTIALS_PATH.exists()
        or TOKEN_PATH.exists()
        or bool(os.getenv("GOOGLE_TOKEN_JSON"))
    )


# ── Gmail ─────────────────────────────────────────────────────────────────────

def get_emails(query: str = "is:unread", max_results: int = 10) -> list[dict]:
    """Gmailからメールを検索して返す。"""
    svc = _gmail()
    if not svc:
        return []

    result = svc.users().messages().list(
        userId="me", q=query, maxResults=max_results
    ).execute()

    messages = []
    for msg_meta in result.get("messages", []):
        msg = svc.users().messages().get(
            userId="me", id=msg_meta["id"], format="metadata",
            metadataHeaders=["From", "To", "Subject", "Date"]
        ).execute()

        headers = {h["name"]: h["value"] for h in msg["payload"].get("headers", [])}
        snippet = msg.get("snippet", "")
        messages.append({
            "id": msg["id"],
            "thread_id": msg["threadId"],
            "from": headers.get("From", ""),
            "to": headers.get("To", ""),
            "subject": headers.get("Subject", "（件名なし）"),
            "date": headers.get("Date", ""),
            "snippet": snippet,
            "labels": msg.get("labelIds", []),
        })

    return messages


def get_email_body(message_id: str) -> str:
    """メール本文を取得する。"""
    svc = _gmail()
    if not svc:
        return ""

    msg = svc.users().messages().get(userId="me", id=message_id, format="full").execute()
    payload = msg.get("payload", {})

    def extract_text(part):
        if part.get("mimeType") == "text/plain":
            data = part.get("body", {}).get("data", "")
            return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
        for sub in part.get("parts", []):
            text = extract_text(sub)
            if text:
                return text
        return ""

    return extract_text(payload)


def create_draft(to: str, subject: str, body: str) -> dict:
    """メールの下書きを作成する。"""
    svc = _gmail()
    if not svc:
        return {"error": "Google API未設定"}

    mime = MIMEText(body, "plain", "utf-8")
    mime["to"] = to
    mime["subject"] = subject
    raw = base64.urlsafe_b64encode(mime.as_bytes()).decode()

    draft = svc.users().drafts().create(
        userId="me", body={"message": {"raw": raw}}
    ).execute()
    return {"draft_id": draft["id"], "status": "作成完了"}


# ── Google Calendar ────────────────────────────────────────────────────────────

def get_upcoming_events(days_ahead: int = 7, max_results: int = 10) -> list[dict]:
    """今後の予定を取得する。"""
    svc = _calendar()
    if not svc:
        return []

    now = datetime.now(timezone.utc)
    end = now + timedelta(days=days_ahead)

    events_result = svc.events().list(
        calendarId=CALENDAR_ID,
        timeMin=now.isoformat(),
        timeMax=end.isoformat(),
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    events = []
    for e in events_result.get("items", []):
        start = e["start"].get("dateTime", e["start"].get("date", ""))
        end_time = e["end"].get("dateTime", e["end"].get("date", ""))
        attendees = [a.get("email", "") for a in e.get("attendees", [])]
        events.append({
            "id": e["id"],
            "title": e.get("summary", "（タイトルなし）"),
            "start": start,
            "end": end_time,
            "location": e.get("location", ""),
            "description": e.get("description", "")[:300],
            "attendees": attendees,
            "meet_link": e.get("hangoutLink", ""),
        })

    return events


def get_next_event(within_minutes: int = 60) -> dict | None:
    """次のミーティングを返す（within_minutes 以内に始まるもの）。"""
    svc = _calendar()
    if not svc:
        return None

    now = datetime.now(timezone.utc)
    cutoff = now + timedelta(minutes=within_minutes)

    events = get_upcoming_events(days_ahead=1, max_results=5)
    for e in events:
        start_str = e["start"]
        if "T" not in start_str:
            continue
        start_dt = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
        if now <= start_dt <= cutoff:
            return e

    return None
