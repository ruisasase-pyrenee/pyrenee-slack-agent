"""
週次レポート自動生成。

毎週月曜 8:00 AM PT に:
1. 先週のメール（重要なもの）を集計
2. 先週の会議を振り返り
3. 今週の予定を確認
4. Claude が「先週の成果 / 今週のフォーカス」をまとめる
5. Slack DM で送信 + Notion に保存（設定時）
"""

import os
import json
import logging
from datetime import datetime, timezone, timedelta
import anthropic
import google_client

logger = logging.getLogger(__name__)


def _get_claude():
    return anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


WEEKLY_PROMPT = """あなたはRui Sasaseの専属アシスタントです。
以下のデータを元に、週次レポートを作成してください。

フォーマット:
---
*週次レポート {date_range}*

*先週の振り返り*
• 主要な会議・連絡（箇条書き3〜5）
• 進んだプロジェクト

*今週のフォーカス*
• 最重要タスク（3つまで）
• 注意すべき締め切り

*未処理の懸念事項*
• フォローアップが必要なもの
---

データ:
{data}
"""


def generate_weekly_report() -> str:
    """先週のデータを集めてClaudeに週次レポートを生成させる。"""
    now = datetime.now(timezone.utc)
    week_ago = now - timedelta(days=7)

    data = {}

    # 先週のメール（重要そうなもの）
    if google_client.is_configured():
        week_ago_str = week_ago.strftime("%Y/%m/%d")
        emails = google_client.get_emails(
            query=f"after:{week_ago_str} -is:sent label:Claude/URGENT OR label:Claude/REPLY_NEED",
            max_results=20,
        )
        data["emails"] = [
            {"from": e["from"], "subject": e["subject"], "date": e["date"]}
            for e in emails
        ]

        # 先週の会議
        past_events = google_client.get_upcoming_events(days_ahead=0, max_results=0)
        # 過去7日のイベントはget_upcoming_eventsでは取れないので別途
        # 代替: 今週の予定（今後7日）を取得
        upcoming = google_client.get_upcoming_events(days_ahead=7, max_results=15)
        data["upcoming_events"] = [
            {"title": e["title"], "start": e["start"], "attendees": e["attendees"]}
            for e in upcoming
        ]
    else:
        data["emails"] = []
        data["upcoming_events"] = []

    # 日付範囲
    date_range = (
        f"{week_ago.strftime('%m/%d')} - {now.strftime('%m/%d')}"
    )

    client = _get_claude()
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=1500,
        messages=[
            {
                "role": "user",
                "content": WEEKLY_PROMPT.format(
                    date_range=date_range,
                    data=json.dumps(data, ensure_ascii=False, indent=2),
                ),
            }
        ],
    )

    return response.content[0].text


def run_weekly_report(app=None, rui_user_id: str = "") -> str:
    """週次レポートを生成してSlack DMで送る。"""
    try:
        report = generate_weekly_report()

        if app and rui_user_id:
            result = app.client.conversations_open(users=rui_user_id)
            channel_id = result["channel"]["id"]
            app.client.chat_postMessage(channel=channel_id, text=report)

            # Notionにも保存
            try:
                from notion_sync import is_configured, _get_client
                # 日次レポートDBに週次レポートとして保存
                REPORTS_DB_ID = "9d1e0e96-fdd5-44de-baf1-41d8269f35df"
                if is_configured():
                    notion = _get_client()
                    title = f"週次レポート {datetime.now().strftime('%Y-%m-%d')}"
                    notion.pages.create(
                        parent={"database_id": REPORTS_DB_ID},
                        properties={
                            "タイトル": {"title": [{"text": {"content": title}}]},
                            "日付": {"date": {"start": datetime.now().strftime("%Y-%m-%d")}},
                            "カテゴリ": {"select": {"name": "週次レポート"}},
                            "ステータス": {"select": {"name": "生成済み"}},
                        },
                        children=[
                            {
                                "object": "block",
                                "type": "paragraph",
                                "paragraph": {
                                    "rich_text": [{"type": "text", "text": {"content": report}}]
                                },
                            }
                        ],
                    )
            except Exception as e:
                logger.warning(f"Notion save failed: {e}")

        return report

    except Exception as e:
        logger.error(f"Weekly report failed: {e}")
        return f"週次レポート生成エラー: {e}"
