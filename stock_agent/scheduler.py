"""
APScheduler-based scheduler for all investment jobs:
  - SpaceX/Anthropic/Simulator analysis report (twice daily)
  - Robotics/SpaceX/AI auto-trade scan (twice daily, market hours)
  - Stop-loss monitor (every 30 min during market hours)
"""
import logging
import os
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

log = logging.getLogger(__name__)
ET = pytz.timezone("America/New_York")

_scheduler: BackgroundScheduler | None = None


def _run_investment_report(slack_client):
    from stock_agent.agent import run_investment_analysis

    channel = os.environ.get("INVESTMENT_CHANNEL_ID")
    if not channel:
        return

    try:
        report = run_investment_analysis()
        now = datetime.now(ET).strftime("%Y-%m-%d %H:%M ET")
        slack_client.chat_postMessage(
            channel=channel,
            text=f"*📊 定期投資レポート ({now})*\n\n{report}",
        )
    except Exception:
        log.exception("Investment report failed")


def _run_auto_trade_scan(slack_client):
    from robot_agent.auto_trader import run_auto_scan

    try:
        results = run_auto_scan(slack_client=slack_client)
        log.info("Auto-trade scan complete: %d signals", len(results))
    except Exception:
        log.exception("Auto-trade scan failed")


def _run_stop_loss_check(slack_client):
    from robot_agent.auto_trader import check_stop_losses

    try:
        triggered = check_stop_losses(slack_client=slack_client)
        if triggered:
            log.info("Stop-loss check: %d triggered", len(triggered))
    except Exception:
        log.exception("Stop-loss check failed")


def start_scheduler(slack_client):
    global _scheduler
    if _scheduler and _scheduler.running:
        return

    _scheduler = BackgroundScheduler(timezone=ET)

    # ── SpaceX/AI/Simulator analysis report ───────────────────────────────
    _scheduler.add_job(
        lambda: _run_investment_report(slack_client),
        CronTrigger(day_of_week="mon-fri", hour=9, minute=40, timezone=ET),
        id="morning_report", name="Morning investment report", replace_existing=True,
    )
    _scheduler.add_job(
        lambda: _run_investment_report(slack_client),
        CronTrigger(day_of_week="mon-fri", hour=15, minute=45, timezone=ET),
        id="closing_report", name="Closing investment report", replace_existing=True,
    )

    # ── Auto-trade scan (robotics + SpaceX + AI watchlist) ────────────────
    _scheduler.add_job(
        lambda: _run_auto_trade_scan(slack_client),
        CronTrigger(day_of_week="mon-fri", hour=9, minute=45, timezone=ET),
        id="morning_autotrade", name="Morning auto-trade scan", replace_existing=True,
    )
    _scheduler.add_job(
        lambda: _run_auto_trade_scan(slack_client),
        CronTrigger(day_of_week="mon-fri", hour=15, minute=45, timezone=ET),
        id="closing_autotrade", name="Closing auto-trade scan", replace_existing=True,
    )

    # ── Stop-loss monitor every 30 min (10:00–16:00 ET) ───────────────────
    _scheduler.add_job(
        lambda: _run_stop_loss_check(slack_client),
        CronTrigger(
            day_of_week="mon-fri",
            hour="10-15",
            minute="0,30",
            timezone=ET,
        ),
        id="stop_loss_monitor", name="Stop-loss monitor", replace_existing=True,
    )

    _scheduler.start()
    log.info(
        "Scheduler started: report(09:40/15:45 ET) + "
        "auto-trade(09:45/15:45 ET) + stop-loss(30min 10-16 ET)"
    )


def stop_scheduler():
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        log.info("Scheduler stopped")
