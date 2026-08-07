"""
Deal pipeline database - SQLite-backed persistent storage.
Tracks companies, interactions, scores, and decisions.
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "pipeline.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables on first run."""
    with get_conn() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS companies (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            sector      TEXT,
            stage       TEXT,
            hq          TEXT,
            founded     INTEGER,
            description TEXT,
            website     TEXT,
            source      TEXT,
            added_at    TEXT DEFAULT (datetime('now')),
            updated_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS metrics (
            company_id      TEXT PRIMARY KEY REFERENCES companies(id),
            arr_mn_jpy      REAL,
            growth_yoy_pct  REAL,
            gross_margin    REAL,
            nrr_pct         REAL,
            cac_months      REAL,
            runway_months   INTEGER,
            employees       INTEGER,
            tam_bn_jpy      REAL,
            updated_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS pipeline (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id      TEXT REFERENCES companies(id),
            status          TEXT DEFAULT 'universe',
            score           REAL,
            verdict         TEXT,
            rationale       TEXT,
            check_size_mn   REAL,
            assigned_to     TEXT DEFAULT 'Rui',
            next_action     TEXT,
            next_action_by  TEXT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS interactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id  TEXT REFERENCES companies(id),
            type        TEXT,
            note        TEXT,
            actor       TEXT DEFAULT 'agent',
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS lps (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            org_name        TEXT NOT NULL,
            contact_name    TEXT,
            contact_email   TEXT,
            tier            TEXT,
            lp_type         TEXT,
            ticket_mn_jpy   REAL,
            status          TEXT DEFAULT 'prospect',
            notes           TEXT,
            created_at      TEXT DEFAULT (datetime('now')),
            updated_at      TEXT DEFAULT (datetime('now'))
        );

        CREATE INDEX IF NOT EXISTS idx_pipeline_status ON pipeline(status);
        CREATE INDEX IF NOT EXISTS idx_pipeline_score  ON pipeline(score DESC);
        CREATE INDEX IF NOT EXISTS idx_companies_sector ON companies(sector);
        """)
        # Migration: add pension-specific columns if not present
        cols = {r[1] for r in conn.execute("PRAGMA table_info(lps)").fetchall()}
        if "aum_bn_jpy" not in cols:
            conn.execute("ALTER TABLE lps ADD COLUMN aum_bn_jpy REAL")
        if "pe_alloc_pct" not in cols:
            conn.execute("ALTER TABLE lps ADD COLUMN pe_alloc_pct REAL")
        if "pe_target_pct" not in cols:
            conn.execute("ALTER TABLE lps ADD COLUMN pe_target_pct REAL")


# ── Company CRUD ──────────────────────────────────────────────────────────────

def upsert_company(c: dict) -> str:
    """Insert or update a company. Returns company_id."""
    cid = c["id"]
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO companies (id,name,sector,stage,hq,founded,description,website,source)
            VALUES (:id,:name,:sector,:stage,:hq,:founded,:description,:website,:source)
            ON CONFLICT(id) DO UPDATE SET
              name=excluded.name, sector=excluded.sector, stage=excluded.stage,
              description=excluded.description, updated_at=datetime('now')
        """, c)
        if "metrics" in c:
            m = dict(c["metrics"], company_id=cid)
            conn.execute("""
                INSERT INTO metrics (company_id,arr_mn_jpy,growth_yoy_pct,gross_margin,
                  nrr_pct,cac_months,runway_months,employees,tam_bn_jpy)
                VALUES (:company_id,:arr_mn_jpy,:growth_yoy_pct,:gross_margin,
                  :nrr_pct,:cac_months,:runway_months,:employees,:tam_bn_jpy)
                ON CONFLICT(company_id) DO UPDATE SET
                  arr_mn_jpy=excluded.arr_mn_jpy,
                  growth_yoy_pct=excluded.growth_yoy_pct,
                  gross_margin=excluded.gross_margin,
                  nrr_pct=excluded.nrr_pct,
                  cac_months=excluded.cac_months,
                  runway_months=excluded.runway_months,
                  employees=excluded.employees,
                  updated_at=datetime('now')
            """, m)
    return cid


def upsert_pipeline(company_id: str, status: str = "universe",
                    score: float = None, verdict: str = None,
                    rationale: str = None, next_action: str = None,
                    check_size_mn: float = None) -> None:
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id FROM pipeline WHERE company_id=?", (company_id,)
        ).fetchone()
        if existing:
            conn.execute("""
                UPDATE pipeline SET status=?, score=COALESCE(?,score),
                  verdict=COALESCE(?,verdict), rationale=COALESCE(?,rationale),
                  next_action=COALESCE(?,next_action),
                  check_size_mn=COALESCE(?,check_size_mn),
                  updated_at=datetime('now')
                WHERE company_id=?
            """, (status, score, verdict, rationale, next_action, check_size_mn, company_id))
        else:
            conn.execute("""
                INSERT INTO pipeline (company_id,status,score,verdict,rationale,
                  next_action,check_size_mn)
                VALUES (?,?,?,?,?,?,?)
            """, (company_id, status, score, verdict, rationale, next_action, check_size_mn))


def log_interaction(company_id: str, itype: str, note: str, actor: str = "agent"):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO interactions (company_id,type,note,actor) VALUES (?,?,?,?)",
            (company_id, itype, note, actor)
        )


def upsert_lp(lp: dict) -> int:
    with get_conn() as conn:
        existing = conn.execute(
            "SELECT id FROM lps WHERE org_name=?", (lp["org_name"],)
        ).fetchone()
        if existing:
            conn.execute("""
                UPDATE lps SET status=COALESCE(:status,status),
                  notes=COALESCE(:notes,notes),
                  ticket_mn_jpy=COALESCE(:ticket_mn_jpy,ticket_mn_jpy),
                  aum_bn_jpy=COALESCE(:aum_bn_jpy,aum_bn_jpy),
                  pe_alloc_pct=COALESCE(:pe_alloc_pct,pe_alloc_pct),
                  pe_target_pct=COALESCE(:pe_target_pct,pe_target_pct),
                  updated_at=datetime('now')
                WHERE org_name=:org_name
            """, {**{"aum_bn_jpy": None, "pe_alloc_pct": None, "pe_target_pct": None}, **lp})
            return existing["id"]
        else:
            cur = conn.execute("""
                INSERT INTO lps (org_name,contact_name,contact_email,tier,lp_type,
                  ticket_mn_jpy,status,notes,aum_bn_jpy,pe_alloc_pct,pe_target_pct)
                VALUES (:org_name,:contact_name,:contact_email,:tier,:lp_type,
                  :ticket_mn_jpy,:status,:notes,:aum_bn_jpy,:pe_alloc_pct,:pe_target_pct)
            """, {**{"aum_bn_jpy": None, "pe_alloc_pct": None, "pe_target_pct": None}, **lp})
            return cur.lastrowid


# ── Query helpers ─────────────────────────────────────────────────────────────

def get_pipeline_summary() -> dict:
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT p.status, COUNT(*) as cnt,
                   AVG(p.score) as avg_score,
                   SUM(m.arr_mn_jpy) as total_arr
            FROM pipeline p
            JOIN companies c ON c.id = p.company_id
            LEFT JOIN metrics m ON m.company_id = p.company_id
            GROUP BY p.status
            ORDER BY CASE p.status
              WHEN 'term_sheet' THEN 1 WHEN 'ic_review' THEN 2
              WHEN 'dd' THEN 3 WHEN 'screening' THEN 4
              WHEN 'watchlist' THEN 5 WHEN 'universe' THEN 6
              ELSE 7 END
        """).fetchall()
        return {r["status"]: dict(r) for r in rows}


def get_top_targets(limit: int = 20) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT c.id, c.name, c.sector, c.stage, p.status, p.score, p.verdict,
                   p.next_action, m.arr_mn_jpy, m.growth_yoy_pct, m.nrr_pct,
                   m.runway_months
            FROM pipeline p
            JOIN companies c ON c.id = p.company_id
            LEFT JOIN metrics m ON m.company_id = p.company_id
            WHERE p.status NOT IN ('closed_won','closed_lost')
            ORDER BY p.score DESC NULLS LAST
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]


def get_universe_stats() -> dict:
    with get_conn() as conn:
        total = conn.execute("SELECT COUNT(*) FROM companies").fetchone()[0]
        scored = conn.execute(
            "SELECT COUNT(*) FROM pipeline WHERE score IS NOT NULL"
        ).fetchone()[0]
        dd_plus = conn.execute(
            "SELECT COUNT(*) FROM pipeline WHERE status IN ('dd','ic_review','term_sheet','closed_won')"
        ).fetchone()[0]
        by_sector = conn.execute("""
            SELECT c.sector, COUNT(*) as cnt
            FROM companies c GROUP BY c.sector ORDER BY cnt DESC
        """).fetchall()
        lp_total = conn.execute("SELECT COUNT(*) FROM lps").fetchone()[0]
        lp_committed = conn.execute("""
            SELECT COALESCE(SUM(ticket_mn_jpy),0) FROM lps
            WHERE status IN ('committed','closed')
        """).fetchone()[0]
        return {
            "total_companies": total,
            "scored": scored,
            "dd_plus": dd_plus,
            "by_sector": [dict(r) for r in by_sector],
            "lp_total": lp_total,
            "lp_committed_mn": lp_committed,
        }


def get_lp_pipeline() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM lps ORDER BY tier, status"
        ).fetchall()
        return [dict(r) for r in rows]


def get_pension_lps() -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT * FROM lps
            WHERE lp_type IN ('企業年金','公的年金','共済組合','確定給付企業年金','基金型企業年金')
            ORDER BY COALESCE(aum_bn_jpy,0) DESC
        """).fetchall()
        return [dict(r) for r in rows]


def search_companies(query: str) -> list[dict]:
    q = f"%{query}%"
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT c.*, m.arr_mn_jpy, m.growth_yoy_pct, p.status, p.score
            FROM companies c
            LEFT JOIN metrics m ON m.company_id=c.id
            LEFT JOIN pipeline p ON p.company_id=c.id
            WHERE c.name LIKE ? OR c.sector LIKE ? OR c.description LIKE ?
            LIMIT 20
        """, (q, q, q)).fetchall()
        return [dict(r) for r in rows]
