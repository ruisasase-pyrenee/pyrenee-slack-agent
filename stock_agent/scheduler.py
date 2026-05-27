"""
APScheduler-based periodic investment analysis.
Sends results to a designated Slack channel.
"""
import logging
import os
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

log = logging.getLogger(__name__)

# US Eastern time zone (NYSE trading hours)
ET = pytz.timezone("America/New_York")

_scheduler: BackgroundScheduler | None = None


def _run_and_notify(slack_client):
    from stock_agent.agent import run_investment_analysis

    channel = os.environ.get("INVESTMENT_CHANNEL_ID")
    if not channel:
        log.warning("INVESTMENT_CHANNEL_ID not set; skipping scheduled analysis")
        return

    log.info("Running scheduled investment analysis...")
    try:
        report = run_investment_analysis()
        now = datetime.now(ET).strftime("%Y-%m-%d %H:%M ET")
        slack_client.chat_postMessage(
            channel=channel,
            text=f"*📊 定期投資レポート ({now})*\n\n{report}",
        )
        log.info("Investment report sent to Slack")
    except Exception:
        log.exception("Scheduled investment analysis failed")


def start_scheduler(slack_client):
    global _scheduler
    if _scheduler and _scheduler.running:
        return

    _scheduler = BackgroundScheduler(timezone=ET)

    # Weekdays at 09:40 ET (just after NYSE open)
    _scheduler.add_job(
        lambda: _run_and_notify(slack_client),
        CronTrigger(day_of_week="mon-fri", hour=9, minute=40, timezone=ET),
        id="morning_analysis",
        name="Morning investment analysis",
        replace_existing=True,
    )

    # Weekdays at 15:45 ET (15 min before NYSE close)
    _scheduler.add_job(
        lambda: _run_and_notify(slack_client),
        CronTrigger(day_of_week="mon-fri", hour=15, minute=45, timezone=ET),
        id="closing_analysis",
        name="Closing investment analysis",
        replace_existing=True,
    )

    _scheduler.start()
    log.info("Investment scheduler started (09:40 ET open + 15:45 ET close, weekdays)")


def stop_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        log.info("Investment scheduler stopped")
