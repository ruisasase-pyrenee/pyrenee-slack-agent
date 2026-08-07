"""
Pension LP analytics — derives the fundraising metrics the dashboard charts.

The raw `lps` rows carry AUM and PE allocation; everything the charts plot
(allocation headroom, stage-weighted pipeline value, funnel rollup) is
computed here so the template stays presentational.
"""

from config.fund_config import FUND_CONFIG
from db.pipeline import get_pension_lps

# Engagement stages, earliest → latest. The weight is the probability we
# assign to an LP at that stage actually committing its target ticket.
STAGES: list[dict] = [
    {"key": "prospect",          "label": "見込み",   "weight": 0.05},
    {"key": "intro_sent",        "label": "資料送付", "weight": 0.15},
    {"key": "meeting_scheduled", "label": "面談設定", "weight": 0.25},
    {"key": "met",               "label": "面談済み", "weight": 0.40},
    {"key": "committed",         "label": "コミット", "weight": 1.00},
]

STAGE_BY_KEY = {s["key"]: s for s in STAGES}

# Suffixes stripped (in order) to get a chart-width-friendly label.
_NAME_SUFFIXES = [
    "企業年金連合会", "企業年金基金", "確定給付企業年金", "企業年金",
    "共済組合連合会", "職員共済組合", "共済組合連合", "共済組合",
    "年金基金", "連合会", "基金",
]


def short_name(org_name: str) -> str:
    """Trim the boilerplate suffix so long fund names fit a chart axis."""
    name = org_name
    for suffix in _NAME_SUFFIXES:
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    name = name.strip("　 ")
    return name or org_name


def pe_headroom_mn(lp: dict) -> float:
    """
    Room left under the LP's own PE allocation target, in M JPY.

    AUM is held in B JPY and the allocations in percent, so the ×1000
    converts the resulting B JPY figure to M JPY. Negative headroom (an LP
    already over its target) clamps to zero — it is not capacity we can sell into.
    """
    aum    = lp.get("aum_bn_jpy")
    current = lp.get("pe_alloc_pct")
    target  = lp.get("pe_target_pct")
    if aum is None or current is None or target is None:
        return 0.0
    return max(0.0, aum * (target - current) / 100 * 1000)


def weighted_value_mn(lp: dict) -> float:
    """Target ticket discounted by the LP's engagement stage."""
    weight = STAGE_BY_KEY.get(lp.get("status", ""), {}).get("weight", 0.0)
    return (lp.get("ticket_mn_jpy") or 0) * weight


def enrich(lp: dict) -> dict:
    """Add the derived fields the charts and table read."""
    stage = STAGE_BY_KEY.get(lp.get("status", ""), {})
    gap   = None
    if lp.get("pe_target_pct") is not None and lp.get("pe_alloc_pct") is not None:
        gap = lp["pe_target_pct"] - lp["pe_alloc_pct"]
    return {
        **lp,
        "short_name":     short_name(lp["org_name"]),
        "headroom_mn":    pe_headroom_mn(lp),
        "weighted_mn":    weighted_value_mn(lp),
        "stage_label":    stage.get("label", lp.get("status", "—")),
        "stage_weight":   stage.get("weight", 0.0),
        "pe_gap_pct":     gap,
    }


def funnel_rollup(lps: list[dict]) -> list[dict]:
    """Per-stage counts and money, ordered earliest → latest."""
    rollup = []
    for stage in STAGES:
        members = [lp for lp in lps if lp.get("status") == stage["key"]]
        if not members and stage["key"] == "committed":
            continue  # pre-first-close: don't plot an empty terminal stage
        rollup.append({
            "key":         stage["key"],
            "label":       stage["label"],
            "weight":      stage["weight"],
            "count":       len(members),
            "ticket_mn":   sum(lp.get("ticket_mn_jpy") or 0 for lp in members),
            "weighted_mn": sum(lp["weighted_mn"] for lp in members),
        })
    return rollup


def pension_dashboard_data() -> dict:
    """Everything the /pension view needs, charts included."""
    lps = [enrich(lp) for lp in get_pension_lps()]

    total_weighted = sum(lp["weighted_mn"] for lp in lps)
    fund_target_mn = FUND_CONFIG["target_size_bn_jpy"] * 1000

    return {
        "lps":            lps,
        "funnel":         funnel_rollup(lps),
        "total_aum_bn":   sum(lp.get("aum_bn_jpy") or 0 for lp in lps),
        "total_ticket_mn":   sum(lp.get("ticket_mn_jpy") or 0 for lp in lps),
        "total_headroom_mn": sum(lp["headroom_mn"] for lp in lps),
        "total_weighted_mn": total_weighted,
        "fund_target_mn":    fund_target_mn,
        "coverage_pct":      (total_weighted / fund_target_mn * 100) if fund_target_mn else 0,
        "active_count":   sum(1 for lp in lps
                              if lp.get("status") in ("intro_sent", "meeting_scheduled", "met")),
    }
