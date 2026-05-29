"""
Batch screener - auto-scores all universe companies against investment criteria.
No API calls: pure rule-based scoring for initial triage.
High scorers get queued for deep Claude analysis.
"""

from config.fund_config import DEAL_SCREENING_CRITERIA
from db.pipeline import upsert_company, upsert_pipeline, log_interaction, get_conn


def score_company(metrics: dict) -> tuple[float, str, str]:
    """
    Rule-based pre-score (0-10). Returns (score, verdict, rationale).
    This runs before Claude to filter the universe efficiently.
    """
    if not metrics:
        return 0.0, "insufficient_data", "財務データなし"

    crit = DEAL_SCREENING_CRITERIA
    q    = crit["quantitative"]
    score = 0.0
    flags = []
    positives = []

    arr       = metrics.get("arr_mn_jpy", 0) or 0
    growth    = metrics.get("growth_yoy_pct", 0) or 0
    gm        = metrics.get("gross_margin", 0) or 0
    nrr       = metrics.get("nrr_pct", 0) or 0
    cac_mo    = metrics.get("cac_months", 99) or 99
    runway    = metrics.get("runway_months", 0) or 0

    # ── Quantitative scoring (10 pts total) ──────────────────────
    # ARR (0-2)
    if arr >= 500:       score += 2.0; positives.append(f"ARR {arr}M 基準5倍超")
    elif arr >= 300:     score += 1.7; positives.append(f"ARR {arr}M 基準超え")
    elif arr >= 200:     score += 1.4; positives.append(f"ARR {arr}M 基準超え")
    elif arr >= 100:     score += 1.0
    elif arr >= 50:      score += 0.5
    else:                flags.append(f"ARR {arr}M — 基準未達")

    # Growth (0-3)
    if growth >= 250:    score += 3.0; positives.append(f"成長率{growth:.0f}% — 爆速")
    elif growth >= 200:  score += 2.7; positives.append(f"成長率{growth:.0f}%")
    elif growth >= 150:  score += 2.3; positives.append(f"成長率{growth:.0f}%")
    elif growth >= q["growth_yoy_min_pct"]:
                         score += 1.7
    elif growth >= 50:   score += 0.8; flags.append(f"成長率{growth:.0f}% — 低め")
    else:                flags.append(f"成長率{growth:.0f}% — 基準未達")

    # Gross margin (0-2)
    if gm >= 82:         score += 2.0; positives.append(f"粗利{gm:.0f}% — 最高水準")
    elif gm >= 78:       score += 1.7; positives.append(f"粗利{gm:.0f}%")
    elif gm >= q["gross_margin_min_pct"]:
                         score += 1.3
    elif gm >= 60:       score += 0.6; flags.append(f"粗利{gm:.0f}% — 低め")
    else:                flags.append(f"粗利{gm:.0f}% — 基準未達")

    # NRR (0-3)
    if nrr >= 128:       score += 3.0; positives.append(f"NRR{nrr:.0f}% — 最高水準")
    elif nrr >= 120:     score += 2.5; positives.append(f"NRR{nrr:.0f}%")
    elif nrr >= 115:     score += 2.0; positives.append(f"NRR{nrr:.0f}%")
    elif nrr >= q["nrr_min_pct"]:
                         score += 1.4
    elif nrr >= 100:     score += 0.5; flags.append(f"NRR{nrr:.0f}% — 基準ギリギリ")
    else:                flags.append(f"NRR{nrr:.0f}% — 基準未達")

    # ── Red flags (-points) ───────────────────────────────────────
    if runway < 12:      score -= 1.0; flags.append(f"ランウェイ{runway}ヶ月 — 緊急")
    elif runway < 6:     score -= 2.0; flags.append(f"ランウェイ{runway}ヶ月 — 危機的")

    if cac_mo > 24:      score -= 0.5; flags.append(f"CAC回収{cac_mo}ヶ月 — 長い")

    score = max(0.0, min(10.0, score))

    # ── Verdict ───────────────────────────────────────────────────
    if score >= 7.5:
        verdict = "priority_screen"  # → Claude deep analysis immediately
    elif score >= 5.5:
        verdict = "screen"           # → Claude screening within 1 week
    elif score >= 3.5:
        verdict = "watchlist"        # → monitor, re-screen in 3 months
    else:
        verdict = "pass"             # → insufficient for now

    pos_str  = " / ".join(positives[:3]) if positives else "—"
    flag_str = " / ".join(flags[:2])     if flags     else "なし"
    rationale = f"強み: {pos_str} | リスク: {flag_str}"

    return round(score, 1), verdict, rationale


def run_batch_screen(companies: list[dict] | None = None) -> dict:
    """
    Screen all companies in the universe.
    If companies is None, loads from DB.
    Returns summary stats.
    """
    from deal_universe.seed_data import UNIVERSE

    targets = companies or UNIVERSE
    results = {"total": 0, "priority": 0, "screen": 0, "watchlist": 0, "pass": 0}

    for co in targets:
        cid = upsert_company(co)
        metrics = co.get("metrics", {})
        score, verdict, rationale = score_company(metrics)

        # Map verdict to pipeline status
        status_map = {
            "priority_screen": "screening",
            "screen":          "universe",
            "watchlist":       "watchlist",
            "pass":            "universe",
        }
        upsert_pipeline(
            company_id=cid,
            status=status_map[verdict],
            score=score,
            verdict=verdict,
            rationale=rationale,
        )
        log_interaction(cid, "auto_screen", f"自動スコア: {score}/10 → {verdict}")

        results["total"] += 1
        key = verdict.replace("priority_screen", "priority").replace("screen", "screen")
        # simplify key
        if verdict == "priority_screen": results["priority"] += 1
        elif verdict == "screen":        results["screen"] += 1
        elif verdict == "watchlist":     results["watchlist"] += 1
        else:                            results["pass"] += 1

    return results


def get_priority_targets(limit: int = 10) -> list[dict]:
    """Return top-scored companies that need Claude deep-screening."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT c.id, c.name, c.sector, c.stage, p.score, p.verdict,
                   m.arr_mn_jpy, m.growth_yoy_pct, m.nrr_pct, m.runway_months
            FROM pipeline p
            JOIN companies c ON c.id = p.company_id
            LEFT JOIN metrics m ON m.company_id = p.company_id
            WHERE p.verdict = 'priority_screen'
              AND p.status = 'screening'
            ORDER BY p.score DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]
