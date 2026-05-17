"""
自動メールトリアージエンジン。

2時間ごとに未読メールをバッチ処理:
  URGENT     → Slack即時通知 + Gmail下書き自動作成
  REPLY_NEED → Slackにまとめて通知（1日2回）
  FYI        → Gmailに「FYI」ラベルのみ
  SKIP       → 何もしない（ニュースレター等）

Required env: (google_client.py の設定に依存)
Optional env:
  TRIAGE_INTERVAL_HOURS  (default: 2)
"""

import json
import logging
from datetime import datetime, timezone, timedelta
import anthropic
import google_client
from db import kv_get, kv_set, append_message

logger = logging.getLogger(__name__)

_claude = None


def _get_claude():
    global _claude
    if not _claude:
        import os
        _claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return _claude


CLASSIFY_PROMPT = """あなたはRui Sasase（Pyrenee Inc. US Evangelist）のメールを分類するAIです。

以下のメール一覧を分析して、各メールを次の4カテゴリに分類してください:

URGENT    : 今日中に返信が必要。ビジネス上の緊急事項、重要な意思決定、CEO/投資家からの連絡
REPLY_NEED: 数日以内に返信が必要だが急ぎではない
FYI       : 情報共有のみ、返信不要
SKIP      : ニュースレター、自動通知、スパム等

重要な関係者:
- 三野龍太(ryuta.mino@pyrenee.net): CEO — URGENT扱い
- 野口颯人(hayato.noguchi@pyrenee.net): 管理職 — URGENT扱い
- Tim Moore(tim@timmoore.work): 映像制作パートナー — REPLY_NEED
- Jake/Vin(matkinsdigital@gmail.com, vin.garc@gmail.com): 映像制作 — REPLY_NEED
- 瀧弁護士: E-2ビザ — URGENT
- Lauren Buchanan: Anthropic — URGENT

以下のJSON形式のみで返してください（説明文不要）:
{
  "results": [
    {
      "id": "メールID",
      "category": "URGENT|REPLY_NEED|FYI|SKIP",
      "reason": "15字以内の理由",
      "suggested_reply": "URGENTのみ: 返信の要点を2〜3行で（日本語か英語、送信者に合わせて）"
    }
  ]
}
"""


def _classify_emails(emails: list[dict]) -> list[dict]:
    """Claudeでメールを一括分類する。"""
    if not emails:
        return []

    email_summary = json.dumps(
        [
            {
                "id": e["id"],
                "from": e["from"],
                "subject": e["subject"],
                "snippet": e["snippet"][:200],
                "date": e["date"],
            }
            for e in emails
        ],
        ensure_ascii=False,
        indent=2,
    )

    client = _get_claude()
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=2048,
        system=CLASSIFY_PROMPT,
        messages=[{"role": "user", "content": f"メール一覧:\n{email_summary}"}],
    )

    text = response.content[0].text.strip()
    # JSONブロックの抽出
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]

    data = json.loads(text)
    return data.get("results", [])


def _apply_gmail_label(message_id: str, label: str):
    """Gmailにラベルを付ける（ラベルが存在しなければ作成）。"""
    try:
        svc = google_client._gmail()
        if not svc:
            return

        # ラベル一覧を取得
        labels_result = svc.users().labels().list(userId="me").execute()
        existing = {l["name"]: l["id"] for l in labels_result.get("labels", [])}

        label_name = f"Claude/{label}"
        if label_name not in existing:
            created = svc.users().labels().create(
                userId="me",
                body={
                    "name": label_name,
                    "labelListVisibility": "labelShow",
                    "messageListVisibility": "show",
                },
            ).execute()
            label_id = created["id"]
        else:
            label_id = existing[label_name]

        svc.users().messages().modify(
            userId="me",
            id=message_id,
            body={"addLabelIds": [label_id]},
        ).execute()
    except Exception as e:
        logger.warning(f"Label apply failed: {e}")


def run_auto_triage(app=None, rui_user_id: str = "") -> str:
    """
    未読メールを取得して自動分類する。
    app + rui_user_id が渡された場合はSlack DM通知も送る。
    戻り値: Slackに送るサマリーテキスト
    """
    if not google_client.is_configured():
        return "Google API未設定のためトリアージをスキップ"

    # 最終チェック時刻を取得（なければ3時間前から）
    last_check = kv_get("triage_last_check")
    if last_check:
        since = datetime.fromisoformat(last_check)
    else:
        since = datetime.now(timezone.utc) - timedelta(hours=3)

    # 未読かつ一定時間以内のメールを取得
    since_str = since.strftime("%Y/%m/%d")
    emails = google_client.get_emails(
        query=f"is:unread after:{since_str}", max_results=20
    )

    kv_set("triage_last_check", datetime.now(timezone.utc).isoformat())

    if not emails:
        return ""

    # Claude で分類
    try:
        results = _classify_emails(emails)
    except Exception as e:
        logger.error(f"Classification failed: {e}")
        return f"分類エラー: {e}"

    email_map = {e["id"]: e for e in emails}
    urgent_lines = []
    reply_lines = []

    for r in results:
        email = email_map.get(r["id"], {})
        category = r.get("category", "SKIP")
        reason = r.get("reason", "")

        # Gmailラベル付け
        if category in ("URGENT", "REPLY_NEED", "FYI"):
            _apply_gmail_label(r["id"], category)

        if category == "URGENT":
            # HubSpot自動同期
            try:
                import hubspot_client
                hubspot_client.sync_email_to_hubspot(
                    email,
                    f"[URGENT] {email.get('subject', '')} — {reason}"
                )
            except Exception:
                pass

            # 下書き自動作成
            suggested = r.get("suggested_reply", "")
            if suggested and email.get("from"):
                try:
                    google_client.create_draft(
                        to=email["from"],
                        subject=f"Re: {email.get('subject', '')}",
                        body=suggested,
                    )
                    draft_note = " ✓下書き作成済み"
                except Exception:
                    draft_note = ""
            else:
                draft_note = ""

            urgent_lines.append(
                f"• *{email.get('subject', '（件名なし）')}*\n"
                f"  From: {email.get('from', '')}\n"
                f"  → {reason}{draft_note}"
            )

        elif category == "REPLY_NEED":
            reply_lines.append(
                f"• {email.get('subject', '（件名なし）')} — {email.get('from', '')}  _{reason}_"
            )

    # Slack通知メッセージ構築
    if not urgent_lines and not reply_lines:
        return ""

    parts = []
    now_str = datetime.now().strftime("%m/%d %H:%M")

    if urgent_lines:
        parts.append(f"*【緊急】要返信 ({now_str})*")
        parts.extend(urgent_lines)

    if reply_lines:
        parts.append(f"\n*【要返信】数日以内*")
        parts.extend(reply_lines)

    message = "\n".join(parts)

    # Slack DM 送信
    if app and rui_user_id:
        try:
            result = app.client.conversations_open(users=rui_user_id)
            channel_id = result["channel"]["id"]
            app.client.chat_postMessage(channel=channel_id, text=message)
        except Exception as e:
            logger.error(f"Slack notify failed: {e}")

    return message
