"""
Auto-trading engine.
Runs on a schedule, screens watchlist for signals, and:
  - Paper mode  → auto-executes if score >= min_score (no approval needed)
  - Live mode   → always sends a Slack proposal requiring "承認"

Signal criteria (ALL must pass):
  1. 1-month momentum >= momentum_threshold_pct
  2. Claude 4-axis score >= min_score_to_trade
  3. Not already holding the ticker
  4. Daily order cap not yet hit
"""
import json
import logging
from datetime import date
from pathlib import Path

log = logging.getLogger(__name__)

PORTFOLIO_PATH = Path("portfolio.json")
WATCHLIST_PATH = Path("watchlist.json")

# Track per-run order count so we don't exceed max_daily_orders
_daily_order_count: dict[str, int] = {}  # date-str -> count


def _load_portfolio() -> dict:
    return json.loads(PORTFOLIO_PATH.read_text())


def _load_watchlist() -> list[dict]:
    return json.loads(WATCHLIST_PATH.read_text())["universe"]


def _today_str() -> str:
    return str(date.today())


def _daily_count() -> int:
    return _daily_order_count.get(_today_str(), 0)


def _increment_daily_count() -> None:
    key = _today_str()
    _daily_order_count[key] = _daily_order_count.get(key, 0) + 1


def _already_holding(ticker: str, portfolio: dict) -> bool:
    return any(h["ticker"] == ticker for h in portfolio.get("holdings", []))


def _theme_filter(ticker_entry: dict, themes: list[str]) -> bool:
    cat = ticker_entry.get("category", "")
    return any(t in cat for t in themes)


def _get_momentum(ticker: str) -> float | None:
    try:
        import yfinance as yf
        hist = yf.Ticker(ticker).history(period="1mo")
        if hist.empty or len(hist) < 2:
            return None
        closes = hist["Close"]
        start, end = float(closes.iloc[0]), float(closes.iloc[-1])
        return round((end - start) / start * 100, 2)
    except Exception:
        return None


def _auto_score_and_propose(ticker: str, description: str) -> dict | None:
    """Run Claude agent for a single ticker. Returns proposal dict or None."""
    try:
        from robot_agent.agent import run_robot_agent
        prompt = (
            f"ロボティクス・SpaceX・AI関連ウォッチリストの中から {ticker}（{description}）を"
            f"詳しく分析してください。ファンダメンタルズ・モメンタム・ニュースカタリスト・"
            f"バリュエーションの4軸でスコアリングし、買いシグナルが出ていれば"
            f"propose_tradeツールで売買提案を作成してください。"
        )
        _, proposal = run_robot_agent(prompt)
        return proposal
    except Exception as e:
        log.exception("Auto-score failed for %s: %s", ticker, e)
        return None


def run_auto_scan(slack_client=None) -> list[dict]:
    """
    Main entry point called by the scheduler.
    Returns list of executed/proposed orders.
    """
    portfolio = _load_portfolio()
    auto_cfg = portfolio.get("auto_trade", {})

    if not auto_cfg.get("enabled"):
        log.info("Auto-trade disabled; skipping scan")
        return []

    max_daily = int(auto_cfg.get("max_daily_orders", 3))
    if _daily_count() >= max_daily:
        log.info("Daily order limit (%d) reached; skipping scan", max_daily)
        return []

    min_score = int(auto_cfg.get("min_score_to_trade", 30))
    momentum_threshold = float(auto_cfg.get("momentum_threshold_pct", 10.0))
    themes = list(auto_cfg.get("themes", ["robotics", "spacex", "ai"]))
    notify_channel = auto_cfg.get("notify_channel")
    paper_auto_execute = bool(auto_cfg.get("paper_auto_execute", True))
    live_requires_approval = bool(auto_cfg.get("live_requires_approval", True))

    from robot_agent.broker import is_paper_enforced, risk_check, execute_trade
    from robot_agent.trade_log import log_trade

    watchlist = _load_watchlist()
    candidates = [e for e in watchlist if _theme_filter(e, themes)]

    results = []
    for entry in candidates:
        if _daily_count() >= max_daily:
            break

        ticker = entry["ticker"]

        if _already_holding(ticker, _load_portfolio()):
            continue

        # Quick momentum pre-filter (avoids full Claude call for cold stocks)
        mom = _get_momentum(ticker)
        if mom is None or mom < momentum_threshold:
            log.debug("%s momentum %.1f%% < threshold %.1f%%", ticker, mom or 0, momentum_threshold)
            continue

        log.info("Momentum signal %s (%.1f%%) — running Claude analysis", ticker, mom)
        proposal = _auto_score_and_propose(ticker, entry.get("notes", ""))
        if not proposal:
            continue

        score_total = proposal.get("score", {}).get("total", 0)
        if score_total < min_score:
            log.info("%s score %d < min %d; skip", ticker, score_total, min_score)
            continue

        is_paper = is_paper_enforced()

        if is_paper and paper_auto_execute:
            # Auto-execute in paper mode
            ok, reason = risk_check(proposal)
            if not ok:
                log.warning("Risk check failed for %s: %s", ticker, reason)
                _notify(slack_client, notify_channel,
                        f"⚠️ 自動売買リスクチェック失敗 {ticker}: {reason}")
                continue

            result = execute_trade(proposal)
            log_trade(proposal, result)
            _increment_daily_count()

            msg = (
                f"🤖 *自動売買執行* (ペーパー)\n"
                f"  {proposal['action']} {ticker} {proposal['quantity']}株 "
                f"@ ${proposal.get('limit_price') or 0:,.2f}\n"
                f"  スコア: {score_total}/40  |  モメンタム: {mom:+.1f}%\n"
                f"  根拠: {proposal.get('reasoning', '')}"
            )
            _notify(slack_client, notify_channel, msg)
            results.append({"ticker": ticker, "mode": "auto_paper", "result": result})

        elif not is_paper and live_requires_approval:
            # Live mode: notify and wait for approval
            msg = (
                f"🔔 *自動売買シグナル（承認待ち）*\n"
                f"  {ticker} — モメンタム: {mom:+.1f}%  |  スコア: {score_total}/40\n"
                f"  ↩️ DMで `承認` と返信すると執行します"
            )
            _notify(slack_client, notify_channel, msg)
            results.append({"ticker": ticker, "mode": "pending_approval", "proposal": proposal})

        else:
            log.info("Auto-trade conditions not met for %s", ticker)

    return results


def _notify(slack_client, channel: str | None, message: str) -> None:
    if slack_client and channel:
        try:
            slack_client.chat_postMessage(channel=channel, text=message)
        except Exception as e:
            log.warning("Slack notify failed: %s", e)
    else:
        log.info("[auto_trade notify] %s", message)


def check_stop_losses(slack_client=None) -> list[dict]:
    """
    Check all holdings for -8% stop-loss triggers and auto-sell in paper mode.
    """
    portfolio = _load_portfolio()
    stop_pct = float(portfolio.get("stop_loss_pct", 0.08))
    notify_channel = portfolio.get("auto_trade", {}).get("notify_channel")
    holdings = portfolio.get("holdings", [])

    from robot_agent.broker import is_paper_enforced, execute_trade
    from robot_agent.trade_log import log_trade

    triggered = []
    for holding in holdings:
        ticker = holding["ticker"]
        avg_price = float(holding["avg_price"])
        qty = int(holding["quantity"])
        stop_price = round(avg_price * (1 - stop_pct), 2)

        try:
            import yfinance as yf
            current = yf.Ticker(ticker).fast_info.last_price
            if current is None:
                continue
            current = float(current)
        except Exception:
            continue

        if current <= stop_price:
            loss_pct = round((current - avg_price) / avg_price * 100, 2)
            log.warning("Stop-loss triggered: %s @ $%.2f (avg $%.2f, %+.1f%%)",
                        ticker, current, avg_price, loss_pct)

            if is_paper_enforced():
                sell_order = {
                    "ticker": ticker,
                    "action": "SELL",
                    "quantity": qty,
                    "limit_price": None,
                    "stop_loss": stop_price,
                    "reasoning": f"損切りライン到達 ({loss_pct:+.1f}%)",
                    "main_risk": "自動損切り",
                    "score": {"total": 0},
                }
                result = execute_trade(sell_order)
                log_trade(sell_order, result)
                triggered.append({"ticker": ticker, "result": result})

                _notify(
                    slack_client, notify_channel,
                    f"🔴 *損切り自動執行* {ticker}\n"
                    f"  現在値 ${current:,.2f}  |  損失 {loss_pct:+.1f}%  |  売却完了（ペーパー）"
                )
            else:
                _notify(
                    slack_client, notify_channel,
                    f"⚠️ *損切りシグナル* {ticker}\n"
                    f"  現在値 ${current:,.2f}  |  損失 {loss_pct:+.1f}%\n"
                    f"  ↩️ `承認` で成行売り執行"
                )
                triggered.append({"ticker": ticker, "mode": "stop_loss_alert"})

    return triggered
