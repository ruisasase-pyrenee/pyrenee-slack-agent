"""
締め切り・リスク自動監視システム。

登録された重要事項を毎日チェックし、
期限が近づいたらSlackで自動通知する。

アラートタイミング: 30日前、14日前、7日前、3日前、1日前、当日
"""

import sqlite3
import logging
from datetime import datetime, timezone, date, timedelta
from db import DB_PATH

logger = logging.getLogger(__name__)


def init_watchlist_table():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            deadline TEXT,
            category TEXT NOT NULL,
            description TEXT,
            alert_days TEXT DEFAULT '30,14,7,3,1,0',
            alerted_days TEXT DEFAULT '',
            resolved INTEGER DEFAULT 0,
            created_at TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()
    _seed_initial_watchlist()


def add(title: str, deadline: str, category: str, description: str = "",
        alert_days: str = "30,14,7,3,1,0") -> int:
    """監視アイテムを追加する。deadline は YYYY-MM-DD 形式。"""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """INSERT INTO watchlist (title, deadline, category, description, alert_days, created_at)
           VALUES (?,?,?,?,?,?)""",
        (title, deadline, category, description, alert_days,
         datetime.now(timezone.utc).isoformat())
    )
    rowid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.commit()
    conn.close()
    return rowid


def resolve(item_id: int):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE watchlist SET resolved=1 WHERE id=?", (item_id,))
    conn.commit()
    conn.close()


def get_active() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT id, title, deadline, category, description, alert_days, alerted_days "
        "FROM watchlist WHERE resolved=0 ORDER BY deadline ASC"
    ).fetchall()
    conn.close()
    return [
        {"id": r[0], "title": r[1], "deadline": r[2], "category": r[3],
         "description": r[4], "alert_days": r[5], "alerted_days": r[6]}
        for r in rows
    ]


def _mark_alerted(item_id: int, days: int):
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT alerted_days FROM watchlist WHERE id=?", (item_id,)
    ).fetchone()
    existing = row[0] if row and row[0] else ""
    days_list = [d for d in existing.split(",") if d]
    if str(days) not in days_list:
        days_list.append(str(days))
    conn.execute(
        "UPDATE watchlist SET alerted_days=? WHERE id=?",
        (",".join(days_list), item_id)
    )
    conn.commit()
    conn.close()


def check_and_alert(app=None, rui_user_id: str = "") -> list[str]:
    """
    全アイテムをチェックして、アラートが必要なものをSlack通知する。
    戻り値: 送ったアラートのリスト
    """
    today = date.today()
    items = get_active()
    alerts = []

    for item in items:
        if not item["deadline"]:
            continue

        try:
            dl = date.fromisoformat(item["deadline"])
        except ValueError:
            continue

        days_left = (dl - today).days
        alert_days = [int(d) for d in item["alert_days"].split(",") if d.strip().isdigit()]
        alerted = [d.strip() for d in item["alerted_days"].split(",") if d.strip()]

        # このタイミングで通知すべきか判断
        trigger = None
        for ad in sorted(alert_days, reverse=True):
            if days_left <= ad and str(ad) not in alerted:
                trigger = ad
                break

        if trigger is None:
            continue

        # アラートメッセージ
        emoji_map = {"visa": "🛂", "project": "🎬", "finance": "💰", "followup": "📧"}
        cat_emoji = emoji_map.get(item["category"], "⚠️")

        if days_left < 0:
            urgency = f"*{abs(days_left)}日超過*"
        elif days_left == 0:
            urgency = "*今日が期限*"
        elif days_left <= 3:
            urgency = f"*残り{days_left}日*"
        else:
            urgency = f"残り{days_left}日"

        msg = (
            f"{cat_emoji} *{item['title']}* — {urgency}\n"
            f"期限: {item['deadline']}\n"
            f"{item['description']}"
        ).strip()

        alerts.append(msg)
        _mark_alerted(item["id"], trigger)

        if app and rui_user_id:
            try:
                result = app.client.conversations_open(users=rui_user_id)
                channel_id = result["channel"]["id"]
                app.client.chat_postMessage(channel=channel_id, text=msg)
            except Exception as e:
                logger.error(f"Watchlist alert send failed: {e}")

    return alerts


def get_summary() -> str:
    """朝のダイジェストに追加する締め切りサマリーを生成する。"""
    today = date.today()
    items = get_active()
    if not items:
        return ""

    urgent = []
    upcoming = []

    for item in items:
        if not item["deadline"]:
            continue
        try:
            dl = date.fromisoformat(item["deadline"])
            days_left = (dl - today).days
            if days_left <= 7:
                urgent.append(f"• *{item['title']}* — 残り{days_left}日 ({item['deadline']})")
            elif days_left <= 30:
                upcoming.append(f"• {item['title']} — 残り{days_left}日")
        except ValueError:
            continue

    parts = []
    if urgent:
        parts.append("*【要注意】締め切り7日以内*\n" + "\n".join(urgent))
    if upcoming:
        parts.append("*【今月の締め切り】*\n" + "\n".join(upcoming))

    return "\n\n".join(parts)


def _seed_initial_watchlist():
    """既知の重要な締め切りを初期データとして登録する。"""
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute("SELECT COUNT(*) FROM watchlist").fetchone()[0]
    conn.close()

    if count > 0:
        return

    initial = [
        ("ESTA期限", "2026-06-12", "visa",
         "出国必要。次回入国は7-8月にE-2またはB-1で正規に準備。",
         "30,14,7,3,1,0"),
        ("Matkins MTG", "2026-05-20", "project",
         "US時間火曜日。見積り受領済み。Rising Act Films vs Matkins Digital の発注先決定。",
         "3,1,0"),
        ("E-2ビザ 最終判断MTG", "2026-06-01", "visa",
         "瀧法律事務所との次回MTGで「確実に通るか」最終判断。新会社設立$200K-$300K必要。",
         "14,7,3,1,0"),
        ("Anthropic Startup Program申請", "2026-06-30", "project",
         "Lauren BuchananへのLinkedIn DM。最大$25K APIクレジット。",
         "30,14,7"),
    ]

    for title, deadline, category, description, alert_days in initial:
        add(title, deadline, category, description, alert_days)

    logger.info(f"Seeded {len(initial)} watchlist items")
