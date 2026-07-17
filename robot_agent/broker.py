"""
Trade execution broker.
- Paper mode: local simulation (portfolio.json)
- Live mode: Alpaca API (requires ALPACA_KEY + ALPACA_SECRET in .env)
Paper mode is enforced for the first `live_enabled_after_weeks` weeks from paper_start_date.
"""
import json
import os
from datetime import date, datetime, timezone
from pathlib import Path

PORTFOLIO_PATH = Path("portfolio.json")


def _load() -> dict:
    return json.loads(PORTFOLIO_PATH.read_text())


def _save(data: dict) -> None:
    PORTFOLIO_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def is_paper_enforced() -> bool:
    """Returns True if paper mode is still active (within the grace period)."""
    p = _load()
    if p.get("mode") != "paper":
        return False
    start = date.fromisoformat(p["paper_start_date"])
    weeks = int(p.get("live_enabled_after_weeks", 2))
    days_passed = (date.today() - start).days
    return days_passed < weeks * 7


def risk_check(order: dict) -> tuple[bool, str]:
    """
    Validate order against risk rules. Returns (ok, reason).
    Rules:
      - 1注文上限 (order_cap_usd)
      - 1銘柄 max_position_pct
    """
    p = _load()
    qty = order["quantity"]
    price = order.get("limit_price") or 0
    order_value = qty * price

    cap = p.get("order_cap_usd")
    if cap and order_value > cap:
        return False, f"注文上限 ${cap:,.0f} 超過（注文額 ${order_value:,.2f}）"

    # Position size check: simple proxy — if order_cap is set use it as denominator
    # For full impl, we'd pull Alpaca account equity here
    max_pct = p.get("max_position_pct", 0.10)
    if cap:
        implied_portfolio = cap / max_pct
        if order_value > implied_portfolio * max_pct:
            return False, f"1銘柄上限 {int(max_pct * 100)}% 超過"

    return True, "OK"


def execute_trade(order: dict) -> dict:
    """
    Execute a trade. Routes to paper or live broker based on current mode.
    order keys: ticker, action, quantity, limit_price, stop_loss, reasoning
    """
    if is_paper_enforced():
        return _execute_paper(order)

    alpaca_key = os.environ.get("ALPACA_KEY")
    alpaca_secret = os.environ.get("ALPACA_SECRET")
    portfolio_mode = _load().get("mode", "paper")

    if portfolio_mode == "live" and alpaca_key and alpaca_secret:
        return _execute_alpaca(order, alpaca_key, alpaca_secret, paper=False)
    elif alpaca_key and alpaca_secret:
        return _execute_alpaca(order, alpaca_key, alpaca_secret, paper=True)
    else:
        return _execute_paper(order)


def _execute_paper(order: dict) -> dict:
    p = _load()
    ticker = order["ticker"]
    action = order["action"]
    qty = order["quantity"]
    price = order.get("limit_price") or 0.0
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    holdings = p.setdefault("holdings", [])

    if action == "BUY":
        existing = next((h for h in holdings if h["ticker"] == ticker), None)
        if existing:
            total_qty = existing["quantity"] + qty
            existing["avg_price"] = round(
                (existing["avg_price"] * existing["quantity"] + price * qty) / total_qty, 4
            )
            existing["quantity"] = total_qty
        else:
            holdings.append({
                "ticker": ticker,
                "quantity": qty,
                "avg_price": price,
                "bought_at": now_str,
            })

    elif action == "SELL":
        for h in holdings:
            if h["ticker"] == ticker:
                h["quantity"] = max(0, h["quantity"] - qty)
        p["holdings"] = [h for h in holdings if h["quantity"] > 0]

    _save(p)
    return {
        "status": "executed",
        "mode": "paper",
        "ticker": ticker,
        "action": action,
        "quantity": qty,
        "price": price,
        "order_value": round(qty * price, 2),
        "executed_at": now_str,
    }


def _execute_alpaca(order: dict, key: str, secret: str, paper: bool) -> dict:
    try:
        from alpaca.trading.client import TradingClient
        from alpaca.trading.requests import LimitOrderRequest, MarketOrderRequest
        from alpaca.trading.enums import OrderSide, TimeInForce

        client = TradingClient(api_key=key, secret_key=secret, paper=paper)
        side = OrderSide.BUY if order["action"] == "BUY" else OrderSide.SELL

        if order.get("limit_price"):
            req = LimitOrderRequest(
                symbol=order["ticker"],
                qty=order["quantity"],
                side=side,
                time_in_force=TimeInForce.DAY,
                limit_price=order["limit_price"],
            )
        else:
            req = MarketOrderRequest(
                symbol=order["ticker"],
                qty=order["quantity"],
                side=side,
                time_in_force=TimeInForce.DAY,
            )

        submitted = client.submit_order(req)
        mode_label = "alpaca_paper" if paper else "alpaca_live"
        return {
            "status": "submitted",
            "mode": mode_label,
            "order_id": str(submitted.id),
            "ticker": order["ticker"],
            "action": order["action"],
            "quantity": order["quantity"],
            "price": order.get("limit_price"),
            "executed_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
