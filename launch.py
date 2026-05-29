"""
Pyrenee Capital - Launch script.
Initializes the database, seeds universe, runs batch screening,
and starts the dashboard + Slack bot.

Usage:
  python launch.py           # Full launch (dashboard + Slack bot)
  python launch.py --setup   # DB init + seed + screen only (no servers)
  python launch.py --screen  # Re-run batch screening
  python launch.py --stats   # Show pipeline stats
"""

import sys
import os
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from db.pipeline import init_db, upsert_lp, get_universe_stats, get_top_targets
from deal_universe.seed_data import UNIVERSE, LP_SEED
from deal_universe.screener import run_batch_screen, get_priority_targets


SEP = "─" * 60


def setup():
    """Initialize DB, seed universe, run batch screening."""
    print(f"\n{'═'*60}")
    print("  🏦  PYRENEE CAPITAL — INITIALIZING")
    print(f"{'═'*60}\n")

    print(f"{SEP}\n  Step 1/4: Database init")
    init_db()
    print("  ✅ pipeline.db created\n")

    print(f"{SEP}\n  Step 2/4: Seeding deal universe ({len(UNIVERSE)} companies)")
    results = run_batch_screen(UNIVERSE)
    print(f"  ✅ {results['total']} companies loaded")
    print(f"     Priority screen : {results['priority']} 社")
    print(f"     Screen queue    : {results['screen']} 社")
    print(f"     Watchlist       : {results['watchlist']} 社")
    print(f"     Pass (for now)  : {results['pass']} 社\n")

    print(f"{SEP}\n  Step 3/4: Seeding LP pipeline ({len(LP_SEED)} LPs)")
    for lp in LP_SEED:
        upsert_lp(lp)
    print(f"  ✅ {len(LP_SEED)} LPs loaded\n")

    print(f"{SEP}\n  Step 4/4: Top 10 priority targets")
    tops = get_priority_targets(10)
    for i, t in enumerate(tops, 1):
        arr = t.get("arr_mn_jpy", 0) or 0
        g   = t.get("growth_yoy_pct", 0) or 0
        nrr = t.get("nrr_pct", 0) or 0
        print(f"  {i:2}. {t['name']:<25} {t['score']}/10  "
              f"ARR:{arr:.0f}M  +{g:.0f}%  NRR:{nrr:.0f}%  [{t['sector'][:12]}]")

    stats = get_universe_stats()
    print(f"\n{SEP}")
    print(f"  UNIVERSE: {stats['total_companies']} 社  |  "
          f"Scored: {stats['scored']}  |  DD+: {stats['dd_plus']}")
    print(f"  LP: {stats['lp_total']} 社  |  Committed: {stats['lp_committed_mn']:.0f}M JPY")
    print(f"{SEP}\n")


def show_stats():
    stats = get_universe_stats()
    tops  = get_top_targets(10)
    print(f"\n{'═'*60}\n  PYRENEE CAPITAL — PIPELINE STATS\n{'═'*60}\n")
    print(f"  Universe: {stats['total_companies']} 社  Scored: {stats['scored']}  DD+: {stats['dd_plus']}")
    print(f"  LP: {stats['lp_total']} 社  Committed: {stats['lp_committed_mn']:.0f}M JPY\n")
    print("  Sector breakdown:")
    for s in stats["by_sector"]:
        print(f"    {s['sector']:<30} {s['cnt']} 社")
    print("\n  Top 10 targets:")
    for i, t in enumerate(tops, 1):
        arr = t.get("arr_mn_jpy", 0) or 0
        g   = t.get("growth_yoy_pct", 0) or 0
        print(f"  {i:2}. {t['name']:<25} {(t['score'] or 0):.1f}/10  "
              f"ARR:{arr:.0f}M  +{g:.0f}%  [{t['sector'][:14]}]")
    print()


def start_dashboard():
    """Start Flask dashboard on port 5000 in background thread."""
    from dashboard.app import app
    print("  🌐  Dashboard: http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)


def start_slack():
    """Start Slack bot (blocks main thread)."""
    from app import app as slack_app, _scheduler
    from slack_bolt.adapter.socket_mode import SocketModeHandler
    import threading

    sched = threading.Thread(target=_scheduler, daemon=True)
    sched.start()
    print("  💬  Slack bot: starting (socket mode)")
    handler = SocketModeHandler(slack_app, os.environ["SLACK_APP_TOKEN"])
    handler.start()


if __name__ == "__main__":
    args = sys.argv[1:]

    if "--stats" in args:
        show_stats()
        sys.exit(0)

    if "--screen" in args:
        print("Re-running batch screen...")
        from deal_universe.seed_data import UNIVERSE
        r = run_batch_screen(UNIVERSE)
        print(f"Done: {r}")
        sys.exit(0)

    # Always setup first
    setup()

    if "--setup" in args:
        print("Setup complete. Run without --setup to start servers.")
        sys.exit(0)

    # Start dashboard in background
    dash_thread = threading.Thread(target=start_dashboard, daemon=True)
    dash_thread.start()

    # Start Slack bot (blocks)
    try:
        start_slack()
    except KeyError as e:
        print(f"\n  ⚠️  Missing env var: {e}")
        print("  Set SLACK_BOT_TOKEN, SLACK_APP_TOKEN, ANTHROPIC_API_KEY")
        print("  Dashboard is running at http://localhost:5000")
        print("  Press Ctrl+C to exit.\n")
        try:
            while True:
                import time; time.sleep(60)
        except KeyboardInterrupt:
            pass
