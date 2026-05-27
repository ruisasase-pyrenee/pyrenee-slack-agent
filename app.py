"""
PE Fund Launch Agent - Slack interface.

Commands:
  スクリーニング [会社情報]  → Deal screening memo
  ICメモ [会社名]           → Investment Committee memo
  法務チェック              → Legal/compliance checklist
  LPレポート               → LP report generation
  ファンド状況              → Fund overview dashboard
  (その他)                 → General PE advisor chat
"""

import os
import re
import asyncio
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from agents.pe_fund_agent import PEFundAgent

app = App(token=os.environ["SLACK_BOT_TOKEN"])
agent = PEFundAgent()  # mcp_client=None until Drive MCP is wired in


def run_async(coro):
    """Run async coroutine from sync Slack handler."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def parse_command(text: str) -> tuple[str, str]:
    """
    Parse message into (command, args).
    Returns ('chat', text) if no specific command is matched.
    """
    text = text.strip()

    # Deal screening
    if re.match(r'^スクリーニング\s*', text):
        args = re.sub(r'^スクリーニング\s*', '', text).strip()
        return "screening", args

    # IC memo
    if re.match(r'^ICメモ\s*', text):
        args = re.sub(r'^ICメモ\s*', '', text).strip()
        return "ic_memo", args

    # Legal checklist
    if text in ["法務チェック", "法務", "コンプライアンス", "チェックリスト"]:
        return "legal", ""

    # LP report
    if re.match(r'^LPレポート', text):
        period = re.sub(r'^LPレポート\s*', '', text).strip() or None
        return "lp_report", period

    # Fund overview
    if text in ["ファンド状況", "状況", "サマリー", "overview"]:
        return "overview", ""

    return "chat", text


def handle_message(user_id: str, text: str) -> str:
    command, args = parse_command(text)

    if command == "screening":
        if not args:
            return "スクリーニングする会社の情報を入力してください。\n例: `スクリーニング 会社名: XX社、事業内容: B2B SaaS、ARR: 1億円`"
        return run_async(agent.screen_deal(user_id, args))

    elif command == "ic_memo":
        if not args:
            return "ICメモを作成する会社名を入力してください。\n例: `ICメモ XX社`"
        return run_async(agent.create_ic_memo(user_id, args))

    elif command == "legal":
        return run_async(agent.show_legal_checklist(user_id))

    elif command == "lp_report":
        return run_async(agent.generate_lp_report(user_id, args or None))

    elif command == "overview":
        return run_async(agent.fund_overview(user_id))

    else:
        return run_async(agent.process_message(user_id, text))


@app.event("app_mention")
def handle_mention(event, say):
    user_id = event["user"]
    text = re.sub(r"<@[A-Z0-9]+>", "", event["text"]).strip()
    if not text:
        say(_help_text())
        return
    response = handle_message(user_id, text)
    say(response)


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

    response = handle_message(user_id, text)
    say(response)


def _help_text() -> str:
    return """*🏦 Pyrenee Capital PE Fund Agent*

使えるコマンド:
• `スクリーニング [会社情報]` — ディールスクリーニングメモ作成 & Drive保存
• `ICメモ [会社名]` — 投資委員会メモ作成 & Drive保存
• `法務チェック` — 法務・コンプライアンスチェックリスト確認
• `LPレポート [期間]` — LP報告書生成 & Drive保存
• `ファンド状況` — ファンド全体のダッシュボード

その他は壁打ち相手としてPE/ファンド運営の質問に答えます。"""


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
