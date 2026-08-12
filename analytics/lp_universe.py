"""
LP universe analytics — shapes the researched LP list and the first-time-fund
precedents for the dashboard.

Nothing here invents a number. Where the research came back empty the field
stays None and the view renders it as 不明 / 未調査, because on this dataset the
absence of a figure is itself the finding.
"""

from config.fund_config import FUND_CONFIG
from db.pipeline import get_lp_pipeline, get_precedents

TIERS: list[dict] = [
    {"key": "tier1", "label": "Tier 1 政府系",        "desc": "制度として1号ファンドに出資しうる"},
    {"key": "tier2", "label": "Tier 2 FoF",           "desc": "ゲートキーパー／FoF運用会社"},
    {"key": "tier3", "label": "Tier 3 地銀・大学",     "desc": "地域金融機関・大学系運用法人"},
    {"key": "tier4", "label": "Tier 4 事業会社・CVC",  "desc": "メガバンク・商社・CVC・信託"},
    {"key": "tier5", "label": "Tier 5 企業年金",       "desc": "企業年金・共済・公的年金"},
]

# Ordered weakest → strongest. 「高（一次ソース原文確認）」は本調査には存在しない。
CONFIDENCE_ORDER = ["未調査", "低", "中", "高"]


def _conf_rank(c: str | None) -> int:
    try:
        return CONFIDENCE_ORDER.index(c or "未調査")
    except ValueError:
        return 0


def tier_rollup(lps: list[dict]) -> list[dict]:
    """Per-tier counts, split by confidence — the data-quality view."""
    rollup = []
    for t in TIERS:
        members = [lp for lp in lps if lp.get("tier") == t["key"]]
        rollup.append({
            **t,
            "count": len(members),
            "by_confidence": {
                c: sum(1 for lp in members if (lp.get("confidence") or "未調査") == c)
                for c in CONFIDENCE_ORDER
            },
            "with_precedent": sum(
                1 for lp in members if lp.get("first_time_fund_ok") == "実績あり"),
        })
    return rollup


def lp_dashboard_data() -> dict:
    lps = sorted(
        get_lp_pipeline(),
        key=lambda lp: (lp.get("tier") or "z", -_conf_rank(lp.get("confidence"))),
    )
    precedents = get_precedents()

    # Plot scale: a fund's headline size is its target, falling back to the
    # first close when no target was published.
    for p in precedents:
        p["plot_mn_jpy"] = p.get("target_mn_jpy") or p.get("first_close_mn_jpy")
        p["is_self"] = p["fund_name"].startswith("Pyrenee")

    own_target_mn = FUND_CONFIG["target_size_bn_jpy"] * 1000
    peers = [p for p in precedents if not p["is_self"] and p["plot_mn_jpy"]]
    smaller = [p for p in peers if p["plot_mn_jpy"] < own_target_mn]

    return {
        "lps": lps,
        "precedents": precedents,
        "tiers": tier_rollup(lps),
        "own_target_mn": own_target_mn,
        "own_first_close_mn": FUND_CONFIG["first_close_target_bn_jpy"] * 1000,
        "peer_count": len(peers),
        "smaller_peer_count": len(smaller),
        "with_precedent": sum(1 for lp in lps if lp.get("first_time_fund_ok") == "実績あり"),
        "unresearched": sum(1 for lp in lps if (lp.get("confidence") or "未調査") == "未調査"),
        "primary_source_count": sum(1 for lp in lps if lp.get("confidence") == "高"),
        "by_confidence": {
            c: sum(1 for lp in lps if (lp.get("confidence") or "未調査") == c)
            for c in CONFIDENCE_ORDER
        },
    }
