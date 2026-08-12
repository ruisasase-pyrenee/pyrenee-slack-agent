"""
PE Fund Agent - Slack interface + autonomous scheduler.

Claude runs as CEO. No human input required for daily operations.

Autonomous schedule (no Slack command needed):
  08:00 JST daily   → morning_cycle   (priorities + pipeline review)
  18:00 JST daily   → evening_cycle   (deal signals + LP follow-ups)
  Mon 09:00 JST     → weekly_cycle    (full review + IC prep)

Slack commands (for when Rui wants to dig in):
  スクリーニング [会社情報]   → Deal screening + auto-save
  ICメモ [会社名]            → IC memo (Deep analysis)
  採点 [会社情報]            → Instant deal score (JSON)
  ソーシング [セクター]       → Sector research
  MA戦略 [番号]             → M&A target strategy (1-3)
  LP追加 [LP情報]           → LP outreach draft + HubSpot
  法務チェック               → Legal checklist
  ファンド状況               → Dashboard
  朝報 / 夕報 / 週報         → Manual trigger of scheduled cycles
  [その他]                  → CEO advisor chat
"""

import os
import re
import asyncio
import threading
import time
import logging
from datetime import datetime
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from agents.orchestrator import Orchestrator
from agents.fund_manager import (
    morning_cycle,
    evening_cycle,
    weekly_cycle,
    score_deal,
    portfolio_alert_scan,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("pyrenee")

app = App(token=os.environ["SLACK_BOT_TOKEN"])
orchestrator = Orchestrator()

BRIEFING_CHANNEL = os.environ.get("BRIEFING_CHANNEL_ID", "")


# ── Async runner ──────────────────────────────────────────────────────────────

def run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# ── Command router ────────────────────────────────────────────────────────────

COMMANDS = {
    r"^スクリーニング\s+(.+)": "screening",
    r"^ICメモ\s+(.+)": "ic_memo",
    r"^採点\s+(.+)": "score",
    r"^ソーシング\s+(.+)": "sourcing",
    r"^MA戦略\s*(\d*)$": "ma_strategy",
    r"^LP追加\s+(.+)": "lp_add",
    r"^(法務チェック|法務)$": "legal",
    r"^(ファンド状況|状況|dashboard)$": "overview",
    r"^(朝報|morning)$": "morning",
    r"^(夕報|evening)$": "evening",
    r"^(週報|weekly)$": "weekly",
}


def route(text: str) -> tuple[str, str]:
    for pattern, cmd in COMMANDS.items():
        m = re.match(pattern, text.strip(), re.IGNORECASE | re.DOTALL)
        if m:
            args = m.group(1).strip() if m.lastindex and m.lastindex >= 1 else ""
            return cmd, args
    return "chat", text.strip()


def dispatch(user_id: str, text: str) -> str:
    cmd, args = route(text)

    if cmd == "screening":
        return run_async(orchestrator.screen_deal(user_id, args))

    elif cmd == "ic_memo":
        return run_async(orchestrator.create_ic_memo(user_id, args))

    elif cmd == "score":
        result = run_async(score_deal(args))
        verdict_emoji = {"dd_proceed": "✅", "watchlist": "⚠️", "pass": "❌"}
        v = result.get("verdict", "?")
        s = result.get("score", "?")
        rationale = result.get("rationale", "")
        next_action = result.get("next_action", "")
        return (
            f"*採点結果: {result.get('company', '?')}*\n"
            f"スコア: *{s}/10* {verdict_emoji.get(v, '?')} `{v}`\n\n"
            f"*判断根拠:* {rationale}\n\n"
            f"*ネクストアクション:* {next_action}"
        )

    elif cmd == "sourcing":
        return run_async(orchestrator.deal_sourcing_research(user_id, args))

    elif cmd == "ma_strategy":
        idx = int(args) - 1 if args.isdigit() else 0
        return run_async(orchestrator.ma_strategy(user_id, max(0, idx)))

    elif cmd == "lp_add":
        return run_async(orchestrator.lp_outreach_draft(user_id, args))

    elif cmd == "legal":
        return run_async(orchestrator.legal_status(user_id))

    elif cmd == "overview":
        return run_async(orchestrator.fund_overview(user_id))

    elif cmd == "morning":
        result = run_async(morning_cycle())
        return result.get("briefing", "朝報生成に失敗しました")

    elif cmd == "evening":
        result = run_async(evening_cycle())
        return result.get("summary", "夕報生成に失敗しました")

    elif cmd == "weekly":
        result = run_async(weekly_cycle())
        return result.get("weekly_report", "週報生成に失敗しました")

    else:
        return run_async(orchestrator.chat(user_id, text))


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


# ── Autonomous scheduler ──────────────────────────────────────────────────────

def _post(text: str) -> None:
    if not BRIEFING_CHANNEL:
        logger.info("No BRIEFING_CHANNEL_ID set")
        return
    try:
        app.client.chat_postMessage(channel=BRIEFING_CHANNEL, text=text)
    except Exception as e:
        logger.error("Slack post failed: %s", e)


def _scheduler():
    """
    Fires autonomous cycles on schedule.
    Runs in a background daemon thread.
    """
    logger.info("Autonomous scheduler started")
    last_fired: dict[str, str] = {}

    while True:
        now = datetime.utcnow()
        jst_hour = (now.hour + 9) % 24
        jst_minute = now.minute
        jst_weekday = (now.weekday() + (1 if now.hour + 9 >= 24 else 0)) % 7
        today_key = now.strftime("%Y-%m-%d")

        # 08:00 JST daily → morning cycle
        if jst_hour == 8 and jst_minute == 0:
            key = f"morning-{today_key}"
            if last_fired.get("morning") != today_key:
                last_fired["morning"] = today_key
                logger.info("Running morning_cycle")
                try:
                    result = run_async(morning_cycle())
                    _post(result.get("briefing", ""))
                except Exception as e:
                    logger.error("morning_cycle failed: %s", e)

        # 18:00 JST daily → evening cycle
        elif jst_hour == 18 and jst_minute == 0:
            if last_fired.get("evening") != today_key:
                last_fired["evening"] = today_key
                logger.info("Running evening_cycle")
                try:
                    result = run_async(evening_cycle())
                    _post(result.get("summary", ""))
                except Exception as e:
                    logger.error("evening_cycle failed: %s", e)

        # Monday 09:00 JST → weekly cycle
        elif jst_weekday == 0 and jst_hour == 9 and jst_minute == 0:
            week_key = now.strftime("%Y-W%W")
            if last_fired.get("weekly") != week_key:
                last_fired["weekly"] = week_key
                logger.info("Running weekly_cycle")
                try:
                    result = run_async(weekly_cycle())
                    _post(result.get("weekly_report", ""))
                except Exception as e:
                    logger.error("weekly_cycle failed: %s", e)

        time.sleep(30)


def _help_text() -> str:
    return """*🏦 Pyrenee Capital - Autonomous Fund Agent*
_毎朝8時・毎夕18時・月曜9時に自律実行中_

*投資判断*
• `スクリーニング [会社情報]` — 詳細スクリーニングメモ → Drive/Notion/HubSpot自動保存
• `ICメモ [会社名]` — 投資委員会メモ（Deep analysis）
• `採点 [会社情報]` — 即時スコアリング（0-10点・判断根拠）

*ソーシング*
• `ソーシング [医療AIなどセクター名]` — アンダーレーダー案件発掘
• `MA戦略 [1-3]` — 事業承継M&A戦略（1:建設ERP / 2:医療介護 / 3:製造MES）

*LP管理*
• `LP追加 [LP情報]` — アウトリーチメール下書き + HubSpot登録

*ファンド運営*
• `法務チェック` — 優先度付き法務タスクレビュー
• `ファンド状況` — 全体ダッシュボード
• `朝報 / 夕報 / 週報` — スケジュール済みサイクルを手動トリガー

その他はCEOアドバイザーとして何でも"""


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    scheduler_thread = threading.Thread(target=_scheduler, daemon=True)
    scheduler_thread.start()

    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
