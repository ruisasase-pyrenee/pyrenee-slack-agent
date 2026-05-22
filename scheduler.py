"""
全自動化ジョブのスケジューラー。

ジョブ一覧:
  morning_digest      毎朝 8:30 PT  — メール + カレンダー朝ダイジェスト
  auto_triage         2時間ごと     — 未読メール自動分類 + Slack通知
  followup_check      毎朝 9:00 PT  — フォローアップリマインダー
  pre_meeting_brief   30分ごと      — 次のMTGが30分以内なら事前ブリーフィング
  notion_sync         毎朝 7:00 PT  — 今後2日のミーティングページをNotion作成
  weekly_report       毎週月曜 8:00 PT — 週次レポート生成 + Slack送信

Required env:
  RUI_SLACK_USER_ID
Optional env:
  MORNING_DIGEST_HOUR (default: 8)
  MORNING_DIGEST_MIN  (default: 30)
  TRIAGE_INTERVAL_HOURS (default: 2)
"""

import os
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

RUI_SLACK_USER_ID = os.getenv("RUI_SLACK_USER_ID", "")
MORNING_HOUR = int(os.getenv("MORNING_DIGEST_HOUR", "8"))
MORNING_MIN = int(os.getenv("MORNING_DIGEST_MIN", "30"))
TRIAGE_INTERVAL = int(os.getenv("TRIAGE_INTERVAL_HOURS", "2"))


def _send_dm(app, text: str):
    if not RUI_SLACK_USER_ID:
        logger.warning("RUI_SLACK_USER_ID not set")
        return
    try:
        result = app.client.conversations_open(users=RUI_SLACK_USER_ID)
        channel_id = result["channel"]["id"]
        app.client.chat_postMessage(channel=channel_id, text=text)
    except Exception as e:
        logger.error(f"DM send failed: {e}")


# ── ジョブ定義 ──────────────────────────────────────────────────────────────────

def _job_morning_digest(app):
    logger.info("Job: morning_digest")
    try:
        from claude_client import run_morning_digest
        result = run_morning_digest()
        _send_dm(app, result)
    except Exception as e:
        logger.error(f"morning_digest failed: {e}")


def _job_auto_triage(app):
    logger.info("Job: auto_triage")
    try:
        from auto_triage import run_auto_triage
        run_auto_triage(app=app, rui_user_id=RUI_SLACK_USER_ID)
    except Exception as e:
        logger.error(f"auto_triage failed: {e}")


def _job_followup_check(app):
    logger.info("Job: followup_check")
    try:
        from followup_tracker import check_followups
        check_followups(app=app, rui_user_id=RUI_SLACK_USER_ID)
    except Exception as e:
        logger.error(f"followup_check failed: {e}")


def _job_pre_meeting_check(app):
    logger.info("Job: pre_meeting_check")
    try:
        import google_client
        if not google_client.is_configured():
            return
        event = google_client.get_next_event(within_minutes=35)
        if not event:
            return
        from db import kv_get, kv_set
        if kv_get(f"briefed:{event['id']}"):
            return
        from claude_client import run_briefing
        result = run_briefing(event["title"])
        _send_dm(app, f"*30分後にミーティング開始です*\n\n{result}")
        kv_set(f"briefed:{event['id']}", datetime.now(timezone.utc).isoformat())
    except Exception as e:
        logger.error(f"pre_meeting_check failed: {e}")


def _job_notion_sync(app):
    logger.info("Job: notion_sync")
    try:
        from notion_sync import sync_upcoming_meetings
        sync_upcoming_meetings(app=app, rui_user_id=RUI_SLACK_USER_ID)
    except Exception as e:
        logger.error(f"notion_sync failed: {e}")


def _job_weekly_report(app):
    logger.info("Job: weekly_report")
    try:
        from weekly_report import run_weekly_report
        run_weekly_report(app=app, rui_user_id=RUI_SLACK_USER_ID)
    except Exception as e:
        logger.error(f"weekly_report failed: {e}")


def _job_watchlist_check(app):
    logger.info("Job: watchlist_check")
    try:
        from watchlist import check_and_alert
        check_and_alert(app=app, rui_user_id=RUI_SLACK_USER_ID)
    except Exception as e:
        logger.error(f"watchlist_check failed: {e}")


def _job_meeting_notes_watcher(app):
    logger.info("Job: meeting_notes_watcher")
    try:
        from meeting_notes_watcher import run_meeting_notes_watcher
        count = run_meeting_notes_watcher(app=app, rui_user_id=RUI_SLACK_USER_ID)
        if count:
            logger.info(f"meeting_notes_watcher: {count}件の議事録を処理")
    except Exception as e:
        logger.error(f"meeting_notes_watcher failed: {e}")


def _job_na_reminder(app):
    logger.info("Job: na_reminder")
    try:
        from meeting_notes_watcher import check_na_reminders
        check_na_reminders(app=app, rui_user_id=RUI_SLACK_USER_ID)
    except Exception as e:
        logger.error(f"na_reminder failed: {e}")


# ── スケジューラー起動 ──────────────────────────────────────────────────────────

def start_scheduler(app):
    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
        from apscheduler.triggers.interval import IntervalTrigger

        scheduler = BackgroundScheduler(timezone="America/Los_Angeles")

        # 朝ダイジェスト (8:30 PT)
        scheduler.add_job(
            _job_morning_digest,
            CronTrigger(hour=MORNING_HOUR, minute=MORNING_MIN),
            args=[app], id="morning_digest", replace_existing=True,
        )

        # 自動トリアージ (2時間ごと)
        scheduler.add_job(
            _job_auto_triage,
            IntervalTrigger(hours=TRIAGE_INTERVAL),
            args=[app], id="auto_triage", replace_existing=True,
        )

        # フォローアップチェック (毎朝 9:00 PT)
        scheduler.add_job(
            _job_followup_check,
            CronTrigger(hour=9, minute=0),
            args=[app], id="followup_check", replace_existing=True,
        )

        # 事前ブリーフィング (30分ごと)
        scheduler.add_job(
            _job_pre_meeting_check,
            IntervalTrigger(minutes=30),
            args=[app], id="pre_meeting_check", replace_existing=True,
        )

        # Notion ミーティングページ作成 (毎朝 7:00 PT)
        scheduler.add_job(
            _job_notion_sync,
            CronTrigger(hour=7, minute=0),
            args=[app], id="notion_sync", replace_existing=True,
        )

        # 週次レポート (毎週月曜 8:00 PT)
        scheduler.add_job(
            _job_weekly_report,
            CronTrigger(day_of_week="mon", hour=8, minute=0),
            args=[app], id="weekly_report", replace_existing=True,
        )

        # 締め切り・リスク監視 (毎朝 8:00 PT)
        scheduler.add_job(
            _job_watchlist_check,
            CronTrigger(hour=8, minute=0),
            args=[app], id="watchlist_check", replace_existing=True,
        )

        # 議事録自動取込 (15分ごと)
        scheduler.add_job(
            _job_meeting_notes_watcher,
            IntervalTrigger(minutes=15),
            args=[app], id="meeting_notes_watcher", replace_existing=True,
        )

        # NA リマインダー (毎朝 9:15 PT)
        scheduler.add_job(
            _job_na_reminder,
            CronTrigger(hour=9, minute=15),
            args=[app], id="na_reminder", replace_existing=True,
        )

        scheduler.start()
        logger.info(
            f"Scheduler started: "
            f"digest={MORNING_HOUR:02d}:{MORNING_MIN:02d}PT, "
            f"triage=every {TRIAGE_INTERVAL}h, "
            f"followup=09:00PT, "
            f"notion=07:00PT, "
            f"weekly=Mon 08:00PT, "
            f"meeting_notes=every 15min, "
            f"na_reminder=09:15PT"
        )
        return scheduler

    except ImportError:
        logger.warning("APScheduler not installed. Run: pip install apscheduler")
        return None
