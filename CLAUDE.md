# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A personal Slack bot (Socket Mode) that routes messages to one of three Claude-backed
behaviours: a business advisor, a read-only stock analyst, and a robotics/space/AI
trading assistant that can propose and execute trades. Conversation language is Japanese.

## Commands

```bash
pip install -r requirements.txt
python app.py          # MUST be run from the repo root — see "Working directory" below
```

There is no test suite, linter config, or build step. Verify changes by importing the
module and calling the function directly, e.g.:

```bash
python -c "from robot_agent.tools import get_price_momentum; print(get_price_momentum('RKLB'))"
python -c "import ast; ast.parse(open('app.py').read())"   # syntax check
```

Market data comes from `yfinance` (no API key). Sandboxes without outbound network
access will fail every `yfinance` call with a proxy/403 error — that is an environment
limitation, not a code bug.

## Required environment

`SLACK_BOT_TOKEN`, `SLACK_APP_TOKEN`, `ANTHROPIC_API_KEY` are read at import time and
will `KeyError` on startup if missing. `INVESTMENT_CHANNEL_ID` (scheduled reports) and
`ALPACA_KEY` / `ALPACA_SECRET` (live broker) are optional. See `.env.example`.

## Architecture

### Message routing

`app.py::_dispatch()` is the single entry point for both DMs and `@mentions`. It is an
ordered chain of regex guards, and **order is load-bearing**:

1. `承認` / `キャンセル` — must match before anything else, or a bare approval would be
   swallowed by a keyword route
2. auto-trade on/off/status
3. portfolio status
4. `ROBOT_KEYWORDS` → `robot_agent` (robotics + SpaceX + AI tickers, can propose trades)
5. `STOCK_KEYWORDS` → `stock_agent` (read-only thematic analysis)
6. fallback → business advisor chat

Adding a keyword to `ROBOT_KEYWORDS` silently steals traffic from the routes below it.

### Two agent packages, same shape

`stock_agent/` and `robot_agent/` each contain `tools.py` (yfinance functions +
Claude tool-use JSON schemas + a `dispatch_tool` switch) and `agent.py` (a bounded
`while` loop calling `claude.messages.create` and feeding `tool_result` blocks back).
The loop pattern is duplicated rather than shared — changing one does not change the other.

The difference that matters: `robot_agent` exposes a `propose_trade` tool. When Claude
calls it, `run_robot_agent` captures the result and returns `(narrative, proposal)`.
`stock_agent` returns text only and can never trade.

Model ID is set per-call in `robot_agent/agent.py`, `stock_agent/agent.py`, and
`app.py::get_claude_response`.

### Trade execution path (human-in-the-loop)

```
Claude calls propose_trade
  → app.py stores it in pending_orders[user_id]  (in-memory)
  → user replies 承認
  → broker.risk_check()  → broker.execute_trade()  → trade_log.log_trade()
```

`broker.execute_trade` picks its destination in this order: paper simulation if
`is_paper_enforced()` (mode is `paper` AND within `live_enabled_after_weeks` of
`paper_start_date`), then Alpaca live if mode is `live` and keys exist, then Alpaca
paper if keys exist, else local paper simulation.

`robot_agent/auto_trader.py` bypasses the approval step **in paper mode only**: it
pre-filters the watchlist on 1-month momentum, runs the full Claude analysis on
survivors, and auto-executes anything scoring above `min_score_to_trade`. In live mode
it only posts a Slack alert. Driven by `stock_agent/scheduler.py` (APScheduler, US/Eastern).

### State

| File | Holds |
|---|---|
| `watchlist.json` | ticker universe, `category` prefix (`robotics_*`/`spacex_*`/`ai_*`/`etf_*`) drives theme filtering |
| `portfolio.json` | mode, risk limits, `auto_trade` config, holdings — **written at runtime** |
| `logs/trades.md` | append-only markdown table of every execution |

In-memory and lost on restart: `conversation_history`, `pending_orders`, and
`auto_trader._daily_order_count` (so `max_daily_orders` resets on restart).

### Working directory

Every state file is opened via a bare relative `Path("portfolio.json")` etc. from
`app.py`, `broker.py`, `auto_trader.py`, `tools.py`, and `trade_log.py`. Running the app
from anywhere other than the repo root will create or read the wrong files.

## Known gaps in the risk layer

The owner's stated rules are: max 10% of portfolio per position, a per-order USD cap,
and −8% stop-loss. The code does not fully enforce them:

- `order_cap_usd` is `null` in `portfolio.json`, and `broker.risk_check()` returns `OK`
  unconditionally when it is unset — no limit is applied today.
- The `max_position_pct` branch in `risk_check()` reduces algebraically to the same
  comparison as the `order_cap_usd` check, so it never rejects anything the first check
  accepted. Real position sizing would need account equity (e.g. from Alpaca).
- Stop-loss is advisory: `propose_trade` computes the −8% line and
  `auto_trader.check_stop_losses()` acts on it only for holdings recorded in
  `portfolio.json`, and only auto-sells in paper mode.

Treat tightening these as intentional work, not incidental cleanup — the owner relies on
these rules and has asked that they hold even against their own in-the-moment instructions.

## Notes

- Agent modules are imported lazily inside handler functions so the bot still boots when
  `yfinance` / `alpaca-py` are absent or slow.
- `docs/spacex-research-prompt.md` is a research artifact, not code.
