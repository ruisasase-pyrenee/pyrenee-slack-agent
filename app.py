import os
import re
import logging
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from db import init_db
from claude_client import get_claude_response, run_triage, run_briefing, run_followup
from followup_tracker import init_followup_table

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = App(token=os.environ["SLACK_BOT_TOKEN"])


# ── Chat handlers ──────────────────────────────────────────────────────────────

@app.event("app_mention")
def handle_mention(event, say):
    text = re.sub(r"<@[A-Z0-9]+>", "", event["text"]).strip()
    if not text:
        say("はい、何でしょう？")
        return
    response = get_claude_response(event["user"], text, channel_id=event["channel"])
    say(response)


@app.event("message")
def handle_dm(event, say):
    if event.get("channel_type") != "im":
        return
    if event.get("subtype") is not None:
        return
    text = event.get("text", "").strip()
    if not text:
        return
    response = get_claude_response(event["user"], text, channel_id=event.get("channel"))
    say(response)


# ── Slash commands ─────────────────────────────────────────────────────────────

@app.command("/triage")
def handle_triage(ack, respond):
    """未読メールをトリアージして優先度付きでまとめる。"""
    ack()
    respond("メールをチェックしています... (少々お待ちください)")
    try:
        result = run_triage()
        respond(result)
    except Exception as e:
        logger.error(f"/triage error: {e}")
        respond(f"エラーが発生しました: {e}")


@app.command("/brief")
def handle_brief(ack, respond, command):
    """次のミーティングの事前ブリーフィングを作成する。
    使い方: /brief [ミーティング名]
    """
    ack()
    meeting_name = command.get("text", "").strip()
    respond("ミーティング情報を確認しています...")
    try:
        result = run_briefing(meeting_name)
        respond(result)
    except Exception as e:
        logger.error(f"/brief error: {e}")
        respond(f"エラーが発生しました: {e}")


@app.command("/followup")
def handle_followup(ack, respond, command):
    """ミーティング後のフォローアップメールを作成する。
    使い方: /followup [ミーティングのメモや文脈]
    """
    ack()
    context = command.get("text", "").strip()
    respond("フォローアップを準備しています...")
    try:
        result = run_followup(context)
        respond(result)
    except Exception as e:
        logger.error(f"/followup error: {e}")
        respond(f"エラーが発生しました: {e}")


@app.command("/digest")
def handle_digest(ack, respond):
    """朝のダイジェスト（メール + カレンダー）を手動で実行する。"""
    ack()
    respond("ダイジェストを生成しています...")
    try:
        from claude_client import run_morning_digest
        result = run_morning_digest()
        respond(result)
    except Exception as e:
        logger.error(f"/digest error: {e}")
        respond(f"エラーが発生しました: {e}")


@app.command("/weekly")
def handle_weekly(ack, respond):
    """週次レポートを手動で生成する。"""
    ack()
    respond("週次レポートを生成しています...")
    try:
        from weekly_report import run_weekly_report
        result = run_weekly_report()
        respond(result)
    except Exception as e:
        logger.error(f"/weekly error: {e}")
        respond(f"エラーが発生しました: {e}")


@app.command("/notion")
def handle_notion(ack, respond):
    """今後の会議のNotionページを作成する。"""
    ack()
    respond("Notionページを確認・作成しています...")
    try:
        from notion_sync import sync_upcoming_meetings
        sync_upcoming_meetings()
        respond("完了しました。")
    except Exception as e:
        logger.error(f"/notion error: {e}")
        respond(f"エラーが発生しました: {e}")


# ── Entry point ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    init_followup_table()

    from scheduler import start_scheduler
    start_scheduler(app)

    logger.info("Starting Pyrenee Slack Agent...")
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
