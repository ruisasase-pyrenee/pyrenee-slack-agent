#!/usr/bin/env python3
"""
保有銘柄の日次チェック。

portfolio.json に書いてあるルール（-8%損切り / 1銘柄10%上限）を
実際の時価で照合し、違反している行だけを赤旗として報告する。

broker.risk_check() は order_cap_usd が null だと無条件で OK を返すため、
現状どのルールも実質機能していない。こちらは時価総額を自前で計算し、
注文前ではなく保有中の状態を毎日見張る役割を持つ。

    python daily_check.py            # 人間向けレポート
    python daily_check.py --slack    # Slack 投稿用の短い形
    python daily_check.py --json     # 機械処理用

アラートが1件でもあれば終了コード 1 を返すので、cron から
`python daily_check.py || notify` のように繋げられる。
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

PORTFOLIO = Path("portfolio.json")


def load_portfolio() -> dict:
    if not PORTFOLIO.exists():
        sys.exit("portfolio.json が見つかりません。リポジトリルートで実行してください。")
    return json.loads(PORTFOLIO.read_text(encoding="utf-8"))


def merge_lots(holdings: list[dict]) -> dict[str, dict]:
    """同一銘柄の複数ロットを加重平均でまとめる。"""
    merged: dict[str, dict] = {}
    for h in holdings:
        t = h["ticker"]
        qty = float(h["quantity"])
        price = float(h["avg_price"])
        if t not in merged:
            merged[t] = {"quantity": 0.0, "cost": 0.0, "lots": 0}
        merged[t]["quantity"] += qty
        merged[t]["cost"] += qty * price
        merged[t]["lots"] += 1
    for t, m in merged.items():
        m["avg_price"] = m["cost"] / m["quantity"] if m["quantity"] else 0.0
    return merged


def fetch_prices(tickers: list[str]) -> dict[str, float | None]:
    """現在値をまとめて取得。取れなかった銘柄は None。"""
    try:
        import yfinance as yf
    except ImportError:
        sys.exit("yfinance が必要です: pip install -r requirements.txt")

    prices: dict[str, float | None] = {}
    for t in tickers:
        try:
            p = yf.Ticker(t).fast_info.last_price
            prices[t] = float(p) if p else None
        except Exception:
            prices[t] = None
    return prices


def evaluate(portfolio: dict, prices: dict[str, float | None]) -> dict:
    stop_pct = float(portfolio.get("stop_loss_pct", 0.08))
    max_pct = float(portfolio.get("max_position_pct", 0.10))
    merged = merge_lots(portfolio.get("holdings", []))

    rows = []
    total_value = 0.0
    total_cost = 0.0

    for ticker, m in merged.items():
        price = prices.get(ticker)
        value = (price or m["avg_price"]) * m["quantity"]
        total_value += value
        total_cost += m["cost"]
        rows.append({
            "ticker": ticker,
            "quantity": m["quantity"],
            "lots": m["lots"],
            "avg_price": round(m["avg_price"], 4),
            "price": round(price, 2) if price else None,
            "stop_price": round(m["avg_price"] * (1 - stop_pct), 2),
            "value": round(value, 2),
            "pnl": round(value - m["cost"], 2),
            "pnl_pct": round((value - m["cost"]) / m["cost"] * 100, 2) if m["cost"] else 0.0,
            "stale": price is None,
        })

    alerts = []
    for r in rows:
        r["weight_pct"] = round(r["value"] / total_value * 100, 1) if total_value else 0.0

        if r["stale"]:
            alerts.append({"level": "warn", "ticker": r["ticker"],
                           "msg": "現在値を取得できず（簿価で代用）。判定は信用しないこと"})
            continue

        if r["pnl_pct"] <= -stop_pct * 100:
            alerts.append({
                "level": "stop", "ticker": r["ticker"],
                "msg": (f"損切りライン割れ {r['pnl_pct']:+.1f}% "
                        f"(現在 ${r['price']:,.2f} / ライン ${r['stop_price']:,.2f})"),
            })
        elif r["pnl_pct"] <= -stop_pct * 100 * 0.75:
            alerts.append({
                "level": "warn", "ticker": r["ticker"],
                "msg": f"損切りラインまで残り {abs(r['pnl_pct']) - stop_pct*100:.1f}pt ({r['pnl_pct']:+.1f}%)",
            })

        if r["weight_pct"] > max_pct * 100:
            alerts.append({
                "level": "size", "ticker": r["ticker"],
                "msg": f"1銘柄上限 {max_pct*100:.0f}% 超過 → 現在 {r['weight_pct']:.1f}%",
            })

    rows.sort(key=lambda r: r["pnl_pct"])
    order = {"stop": 0, "size": 1, "warn": 2}
    alerts.sort(key=lambda a: order.get(a["level"], 9))

    return {
        "as_of": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "total_value": round(total_value, 2),
        "total_cost": round(total_cost, 2),
        "total_pnl": round(total_value - total_cost, 2),
        "total_pnl_pct": round((total_value - total_cost) / total_cost * 100, 2) if total_cost else 0.0,
        "rules": {"stop_loss_pct": stop_pct, "max_position_pct": max_pct},
        "holdings": rows,
        "alerts": alerts,
    }


ICON = {"stop": "🔴", "size": "🟠", "warn": "🟡"}


def render_text(rep: dict) -> str:
    out = [f"📋 保有チェック  {rep['as_of']}", ""]
    out.append(f"評価額 ${rep['total_value']:,.2f}  /  "
               f"損益 {rep['total_pnl']:+,.2f} ({rep['total_pnl_pct']:+.2f}%)")
    out.append("")
    out.append(f"{'銘柄':<6}{'株数':>5}{'取得':>10}{'現在':>10}{'損益%':>9}{'比率':>7}")
    out.append("-" * 50)
    for r in rep["holdings"]:
        price = f"{r['price']:,.2f}" if r["price"] else "取得失敗"
        out.append(f"{r['ticker']:<6}{r['quantity']:>5.0f}{r['avg_price']:>10,.2f}"
                   f"{price:>10}{r['pnl_pct']:>8.1f}%{r['weight_pct']:>6.1f}%")

    out.append("")
    if rep["alerts"]:
        out.append(f"⚠️  アラート {len(rep['alerts'])}件")
        for a in rep["alerts"]:
            out.append(f"  {ICON.get(a['level'], '•')} {a['ticker']}: {a['msg']}")
    else:
        out.append("✅ ルール違反なし")
    return "\n".join(out)


def render_slack(rep: dict) -> str:
    head = (f"*📋 保有チェック* ({rep['as_of']})\n"
            f"評価額 ${rep['total_value']:,.0f} / "
            f"損益 *{rep['total_pnl']:+,.2f}* ({rep['total_pnl_pct']:+.2f}%)")
    if not rep["alerts"]:
        return head + "\n✅ ルール違反なし"
    lines = [head, f"\n*⚠️ アラート {len(rep['alerts'])}件*"]
    for a in rep["alerts"]:
        lines.append(f"{ICON.get(a['level'], '•')} *{a['ticker']}* — {a['msg']}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="保有銘柄の日次ルールチェック")
    ap.add_argument("--slack", action="store_true", help="Slack 投稿用に短く出す")
    ap.add_argument("--json", action="store_true", help="JSON で出す")
    args = ap.parse_args()

    portfolio = load_portfolio()
    merged = merge_lots(portfolio.get("holdings", []))
    if not merged:
        print("保有銘柄がありません。")
        return 0

    prices = fetch_prices(sorted(merged))
    report = evaluate(portfolio, prices)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.slack:
        print(render_slack(report))
    else:
        print(render_text(report))

    # 損切り割れ・上限超過があれば非ゼロで終了（cron から通知に繋げられる）
    return 1 if any(a["level"] in ("stop", "size") for a in report["alerts"]) else 0


if __name__ == "__main__":
    sys.exit(main())
