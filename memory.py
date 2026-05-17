"""
長期記憶システム。SQLite FTS5で意味検索可能な記憶を管理する。

記憶の種類:
  person    人物情報（連絡先・関係性・最終接触）
  project   プロジェクト状況・決定事項
  decision  重要な意思決定・合意事項
  fact      ビジネスファクト・数字
  followup  フォローアップ事項

使い方:
  memory.store("project", "映像制作", "Rising Act Films: 5/13 MTG完了。7月納品目標。")
  results = memory.search("Tim Moore 映像")
"""

import sqlite3
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from db import DB_PATH

logger = logging.getLogger(__name__)


def init_memory_tables():
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE VIRTUAL TABLE IF NOT EXISTS memories USING fts5(
            category,
            subject,
            content,
            source,
            tokenize="unicode61"
        );

        CREATE TABLE IF NOT EXISTS memories_meta (
            rowid INTEGER PRIMARY KEY,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()
    _seed_initial_memories()


def store(category: str, subject: str, content: str, source: str = "manual") -> int:
    """記憶を保存する。同じsubjectが既存なら更新。"""
    conn = sqlite3.connect(DB_PATH)
    now = datetime.now(timezone.utc).isoformat()

    # 既存チェック
    row = conn.execute(
        "SELECT rowid FROM memories WHERE subject = ?", (subject,)
    ).fetchone()

    if row:
        conn.execute(
            "UPDATE memories SET category=?, content=?, source=? WHERE subject=?",
            (category, content, source, subject)
        )
        conn.execute(
            "UPDATE memories_meta SET updated_at=? WHERE rowid=?",
            (now, row[0])
        )
        rowid = row[0]
    else:
        conn.execute(
            "INSERT INTO memories (category, subject, content, source) VALUES (?,?,?,?)",
            (category, subject, content, source)
        )
        rowid = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.execute(
            "INSERT INTO memories_meta (rowid, created_at, updated_at) VALUES (?,?,?)",
            (rowid, now, now)
        )

    conn.commit()
    conn.close()
    return rowid


def search(query: str, limit: int = 5) -> list[dict]:
    """クエリに関連する記憶を検索して返す。"""
    if not query.strip():
        return []

    conn = sqlite3.connect(DB_PATH)
    try:
        rows = conn.execute(
            """SELECT m.category, m.subject, m.content, m.source, meta.updated_at
               FROM memories m
               JOIN memories_meta meta ON m.rowid = meta.rowid
               WHERE memories MATCH ?
               ORDER BY rank
               LIMIT ?""",
            (query, limit)
        ).fetchall()
    except Exception as e:
        logger.warning(f"Memory search failed: {e}")
        rows = []
    conn.close()

    return [
        {"category": r[0], "subject": r[1], "content": r[2],
         "source": r[3], "updated_at": r[4]}
        for r in rows
    ]


def get_all(category: str = None, limit: int = 20) -> list[dict]:
    """カテゴリ別に記憶を取得する。"""
    conn = sqlite3.connect(DB_PATH)
    if category:
        rows = conn.execute(
            """SELECT m.category, m.subject, m.content, meta.updated_at
               FROM memories m JOIN memories_meta meta ON m.rowid = meta.rowid
               WHERE m.category = ?
               ORDER BY meta.updated_at DESC LIMIT ?""",
            (category, limit)
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT m.category, m.subject, m.content, meta.updated_at
               FROM memories m JOIN memories_meta meta ON m.rowid = meta.rowid
               ORDER BY meta.updated_at DESC LIMIT ?""",
            (limit,)
        ).fetchall()
    conn.close()
    return [{"category": r[0], "subject": r[1], "content": r[2], "updated_at": r[3]} for r in rows]


def format_for_prompt(memories: list[dict]) -> str:
    """記憶をプロンプト注入用テキストに変換する。"""
    if not memories:
        return ""
    lines = ["【関連する記憶・コンテキスト】"]
    for m in memories:
        lines.append(f"[{m['category']}] {m['subject']}: {m['content']}")
    return "\n".join(lines)


def extract_and_store(conversation: str, response: str):
    """会話から重要な事実を抽出してメモリに保存する（非同期で実行）。"""
    try:
        import os
        import anthropic
        client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"""以下の会話から保存すべき重要な事実・決定事項を抽出してください。
JSON配列で返してください（空なら[]）:
[{{"category": "person|project|decision|fact|followup", "subject": "20字以内のタイトル", "content": "内容"}}]

会話:
{conversation[-500:]}

回答:
{response[-300:]}"""
            }]
        )

        text = resp.content[0].text.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]

        items = json.loads(text)
        for item in items:
            if item.get("subject") and item.get("content"):
                store(
                    item.get("category", "fact"),
                    item["subject"],
                    item["content"],
                    source="conversation"
                )
    except Exception as e:
        logger.debug(f"Memory extraction failed: {e}")


def _seed_initial_memories():
    """CLAUDE.mdの重要情報を初期記憶として登録する。"""
    initial = [
        ("person", "三野龍太 (CEO)", "PyreneeのCEO。ryuta.mino@pyrenee.net。重要度最高。"),
        ("person", "野口颯人", "Pyrenee管理職。hayato.noguchi@pyrenee.net。"),
        ("person", "Tim Moore", "映像ディレクター。tim@timmoore.work。Rising Act Films。Pyrenee Drive動画パートナー。"),
        ("person", "Daniel Stine", "Rising Act Films代表。stine@risingactfilms.org。"),
        ("person", "Jake (Matkins)", "Matkins Digital映像制作。matkinsdigital@gmail.com。"),
        ("person", "瀧弁護士", "瀧法律事務所。E-2ビザ担当。"),
        ("person", "Lauren Buchanan", "Anthropic Partnerships。LinkedIn DM推奨。"),
        ("project", "映像制作 Pyrenee Drive", "Rising Act Films vs Matkins Digital。5/20 MTG後に発注先決定。予算$5K-$10K/月。7月納品目標。コンセプト: ドラえもん。"),
        ("project", "E-2ビザ申請", "瀧法律事務所と協議中。新会社設立($200K-$300K投資、W-2 3名)が必要。次回MTGで確実性を判断。費用: 事業計画$4K+着手金$8.8K+申請$380。"),
        ("project", "Anthropic連携", "Startup Program($25K APIクレジット)申請予定。Lauren BuchananへのLinkedIn DM。"),
        ("fact", "ESTA期限", "2026年6月12日。入国2026年3月14日。残り約26日。次回入国7-8月予定。"),
        ("fact", "Pyrenee資金調達", "累計13億円（2026年2月に2億円追加）。トヨタKINTO提携予定（来年1月）。NASDAQ上場目標。"),
        ("fact", "Pyrenee製品", "Pyrenee Drive: AI事故防止・ドライビングパートナーデバイス。米国対象市場約2億8900万台。"),
        ("fact", "Zoom MTG リンク", "https://us06web.zoom.us/j/84008535320?pwd=lbPHWoc3WHja9mKlw3NDXoMkPO8T3x.1"),
    ]

    conn = sqlite3.connect(DB_PATH)
    # 既存データがあればスキップ
    count = conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
    conn.close()

    if count == 0:
        for category, subject, content in initial:
            store(category, subject, content, source="claude.md")
        logger.info(f"Seeded {len(initial)} initial memories")
