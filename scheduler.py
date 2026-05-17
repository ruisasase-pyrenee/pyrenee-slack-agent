"""
Scheduled jobs for automated digest and pre-meeting briefings.

Triggers:
- 毎朝 8:30 AM PT (16:30 UTC) → 朝のダイジェスト
- 毎 30分ごと → 次のミーティングが30分以内なら事前ブリーフィング送信

Required env:
  RUI_SLACK_USER_ID   Rui の Slack ユーザーID（DM送信先）
  MORNING_DIGEST_HOUR 朝ダイジェストの時刻（PT、デフォルト 8）
  MORNING_DIGEST_MIN  (デフォルト 30)
"""

import os
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

RUI_SLACK_USER_ID = os.getenv("RUI_SLACK_USER_ID", "")
MORNING_HOUR = int(os.getenv("MORNING_DIGEST_HOUR", "8"))
MORNING_MIN = int(os.getenv("MORNING_DIGEST_MIN", "30"))


def _send_dm(app, text: str):
    """Rui の Slack DM チャンネルにメッセージを送る。"""
    if not RUI_SLACK_USER_ID:
        logger.warning("RUI_SLACK_USER_ID not set, skipping DM")
        return
    try:
        result = app.client.conversations_open(users=RUI_SLACK_USER_ID)
        channel_id = result["channel"]["id"]
        app.client.chat_postMessage(channel=channel_id, text=text)
    except Exception as e:
        logger.error(f"Failed to send DM: {e}")


def _job_morning_digest(app):
    """朝のダイジェスト: メールトリアージ + 今日の予定。"""
    logger.info("Running morning digest job")
    try:
        from claude_client import run_morning_digest
        result = run_morning_digest()
        _send_dm(app, result)
    except Exception as e:
        logger.error(f"Morning digest failed: {e}")


def _job_pre_meeting_check(app):
    """30分ごとに次のミーティングをチェックして事前ブリーフィングを送る。"""
    try:
        import google_client
        if not google_client.is_configured():
            return

        event = google_client.get_next_event(within_minutes=35)
        if not event:
            return

        from db import kv_get, kv_set
        last_briefed = kv_get(f"briefed:{event['id']}")
        if last_briefed:
            return

        logger.info(f"Pre-meeting briefing for: {event['title']}")
        from claude_client import run_briefing
        result = run_briefing(event["title"])
        _send_dm(app, f"*30分後にミーティングがあります*\n\n{result}")

        kv_set(f"briefed:{event['id']}", datetime.now(timezone.utc).isoformat())
    except Exception as e:
        logger.error(f"Pre-meeting check failed: {e}")


def start_scheduler(app):
    """APScheduler を起動してジョブを登録する。"""
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
        from apscheduler.triggers.interval import IntervalTrigger

        scheduler = BackgroundScheduler(timezone="America/Los_Angeles")

        # 毎朝ダイジェスト
        scheduler.add_job(
            _job_morning_digest,
            CronTrigger(hour=MORNING_HOUR, minute=MORNING_MIN),
            args=[app],
            id="morning_digest",
            replace_existing=True,
        )

        # 30分ごとにミーティングチェック
        scheduler.add_job(
            _job_pre_meeting_check,
            IntervalTrigger(minutes=30),
            args=[app],
            id="pre_meeting_check",
            replace_existing=True,
        )

        scheduler.start()
        logger.info(
            f"Scheduler started. Morning digest at {MORNING_HOUR:02d}:{MORNING_MIN:02d} PT"
        )
        return scheduler

    except ImportError:
        logger.warning("APScheduler not installed. Scheduled jobs disabled.")
        return None
