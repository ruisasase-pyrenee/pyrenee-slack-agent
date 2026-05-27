"""
PE Fund Launch Agent - Slack interface + daily scheduler.

Commands:
  スクリーニング [会社情報]      → Deal screening + Drive/HubSpot自動保存
  ICメモ [会社名]               → IC memo（Deep analysis with opus）
  ソーシング [セクター名]        → セクター調査 + アンダーレーダー案件発掘
  MA戦略                       → 事業承継M&A戦略分析
  LP追加 [LP情報]              → LPアウトリーチメール下書き + HubSpot登録
  法務チェック                  → 法務タスク優先度付きレビュー
  ファンド状況                  → ダッシュボード（パイプライン + LP + 法務）
  朝報                         → 今日の優先アクション（手動トリガー）
  [その他]                     → PE全般の壁打ち相手
"""

import os
import re
import asyncio
import threading
import time
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from agents.orchestrator import Orchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = App(token=os.environ["SLACK_BOT_TOKEN"])
agent = Orchestrator()  # MCP接続は本番環境で mcp_tools={...} を渡す


# ── Async runner ─────────────────────────────────────────────────────────────

def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ── Command router ────────────────────────────────────────────────────────────

COMMANDS = {
    r"^スクリーニング\s*(.+)": "screening",
    r"^ICメモ\s*(.+)": "ic_memo",
    r"^ソーシング\s*(.+)": "sourcing",
    r"^MA戦略$": "ma_strategy",
    r"^LP追加\s*(.+)": "lp_add",
    r"^(法務チェック|法務|コンプライアンス)$": "legal",
    r"^(ファンド状況|状況|サマリー|overview)$": "overview",
    r"^(朝報|morning|briefing)$": "morning",
}


def route(text: str) -> tuple[str, str]:
    """Returns (command_name, args)."""
    for pattern, cmd in COMMANDS.items():
        m = re.match(pattern, text.strip(), re.IGNORECASE)
        if m:
            args = m.group(1).strip() if m.lastindex and m.lastindex >= 1 else ""
            return cmd, args
    return "chat", text.strip()


def dispatch(user_id: str, text: str) -> str:
    cmd, args = route(text)

    if cmd == "screening":
        if not args:
            return "会社情報を入力してください。\n例: `スクリーニング 会社名: XX社、業種: B2B SaaS、ARR: 1億円、YoY成長: 120%`"
        return run_async(agent.screen_deal(user_id, args))

    elif cmd == "ic_memo":
        if not args:
            return "会社名を入力してください。\n例: `ICメモ XX社`"
        return run_async(agent.create_ic_memo(user_id, args))

    elif cmd == "sourcing":
        if not args:
            return "セクター名を入力してください。\n例: `ソーシング 医療AI`"
        return run_async(agent.deal_sourcing_research(user_id, args))

    elif cmd == "ma_strategy":
        return run_async(agent.ma_strategy(user_id))

    elif cmd == "lp_add":
        if not args:
            return "LP情報を入力してください。\n例: `LP追加 XX地方銀行、担当: 田中様、チケット想定: 300M JPY`"
        return run_async(agent.lp_outreach_draft(user_id, args))

    elif cmd == "legal":
        return run_async(agent.legal_status(user_id))

    elif cmd == "overview":
        return run_async(agent.fund_overview(user_id))

    elif cmd == "morning":
        return run_async(agent.morning_briefing(user_id))

    else:
        return run_async(agent.chat(user_id, text))


# ── Slack event handlers ──────────────────────────────────────────────────────

@app.event("app_mention")
def handle_mention(event, say):
    user_id = event["user"]
    text = re.sub(r"<@[A-Z0-9]+>", "", event["text"]).strip()
    if not text:
        say(_help_text())
        return
    say(dispatch(user_id, text))


@app.event("message")
def handle_dm(event, say):
    if event.get("channel_type") != "im":
        return
    if event.get("subtype") is not None:
        return
    user_id = event["user"]
    text = event.get("text", "").strip()
    if not text:
        return
    say(dispatch(user_id, text))


# ── Daily morning briefing scheduler ────────────────────────────────────────
# 毎朝8:00 JSTに自動でブリーフィングを送信

def _morning_briefing_job():
    """Send morning briefing to configured channel."""
    channel = os.environ.get("BRIEFING_CHANNEL_ID", "")
    if not channel:
        logger.info("BRIEFING_CHANNEL_ID not set, skipping morning briefing")
        return

    try:
        briefing = run_async(agent.morning_briefing("scheduler"))
        app.client.chat_postMessage(channel=channel, text=briefing)
        logger.info("Morning briefing sent to %s", channel)
    except Exception as e:
        logger.error("Morning briefing failed: %s", e)


def _scheduler():
    """Simple scheduler: fires at JST 08:00 daily."""
    import datetime
    while True:
        now = datetime.datetime.utcnow()
        jst_hour = (now.hour + 9) % 24
        if jst_hour == 8 and now.minute == 0:
            _morning_briefing_job()
            time.sleep(61)  # prevent double-fire within the same minute
        else:
            time.sleep(30)


def _help_text() -> str:
    return """*🏦 Pyrenee Capital PE Fund Agent*

*投資案件*
• `スクリーニング [会社情報]` — スクリーニングメモ作成 → Drive + HubSpot自動保存
• `ICメモ [会社名]` — 投資委員会メモ作成（Deep analysis）
• `ソーシング [セクター]` — セクター調査 + アンダーレーダー案件発掘
• `MA戦略` — 事業承継型M&A戦略分析

*LP管理*
• `LP追加 [LP情報]` — アウトリーチメール下書き + HubSpot登録

*ファンド運営*
• `法務チェック` — 法務タスク優先度レビュー
• `ファンド状況` — パイプライン + LP + 法務ダッシュボード
• `朝報` — 今日の優先アクション（毎朝8時に自動送信）

その他はPE全般の壁打ち相手として使えます。"""


if __name__ == "__main__":
    # Start scheduler in background thread
    briefing_thread = threading.Thread(target=_scheduler, daemon=True)
    briefing_thread.start()
    logger.info("Morning briefing scheduler started")

    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
