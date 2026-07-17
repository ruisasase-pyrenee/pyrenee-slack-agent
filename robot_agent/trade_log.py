"""Append executed trades to logs/trades.md."""
from pathlib import Path
from datetime import datetime, timezone

LOG_PATH = Path("logs/trades.md")


def log_trade(order: dict, result: dict) -> None:
    score_data = order.get("score", {})
    total_score = score_data.get("total", "—")

    price = result.get("price") or order.get("limit_price") or 0
    qty = result.get("quantity") or order.get("quantity") or 0
    order_value = result.get("order_value") or round(qty * price, 2)

    now_et = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    mode = result.get("mode", "paper")
    stop_loss = order.get("stop_loss", "—")
    reasoning_oneliner = (order.get("reasoning") or "").replace("\n", " ").replace("|", "/")[:80]

    row = (
        f"| {now_et} ET "
        f"| {order['action']} "
        f"| {order['ticker']} "
        f"| {qty} "
        f"| ${price:,.2f} "
        f"| ${order_value:,.0f} "
        f"| {mode} "
        f"| {total_score}/40 "
        f"| ${stop_loss} "
        f"| {reasoning_oneliner} |"
    )

    LOG_PATH.parent.mkdir(exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(row + "\n")
