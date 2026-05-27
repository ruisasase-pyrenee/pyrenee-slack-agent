"""
yfinance-backed tool implementations + Claude tool schema definitions.
"""
import json
from datetime import datetime, timezone
from typing import Any

import yfinance as yf

# ── Claude tool schema definitions ──────────────────────────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "get_stock_quote",
        "description": (
            "指定銘柄の現在値・前日比・出来高などリアルタイムに近い株価スナップショットを返す。"
            "複数銘柄を一括取得できる。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "tickers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "ティッカーシンボルのリスト (例: [\"NVDA\", \"GOOGL\"])",
                }
            },
            "required": ["tickers"],
        },
    },
    {
        "name": "get_stock_info",
        "description": "企業の基本情報（セクター・業種・時価総額・PER・説明など）を返す。",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "ティッカーシンボル"}
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "get_price_history",
        "description": "指定期間の終値履歴を返す。トレンド・モメンタム分析に使う。",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"},
                "period": {
                    "type": "string",
                    "description": "取得期間: '5d'|'1mo'|'3mo'|'6mo'|'1y'",
                    "enum": ["5d", "1mo", "3mo", "6mo", "1y"],
                },
            },
            "required": ["ticker", "period"],
        },
    },
    {
        "name": "get_stock_news",
        "description": "指定銘柄の最新ニュースヘッドラインを最大10件返す。",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string"}
            },
            "required": ["ticker"],
        },
    },
    {
        "name": "screen_momentum_stocks",
        "description": (
            "指定テーマ（space/ai/simulator）のウォッチリスト銘柄を一括スクリーニングし、"
            "1ヶ月モメンタムが高い順にソートして返す。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "theme": {
                    "type": "string",
                    "enum": ["spacex", "anthropic", "simulator", "all"],
                    "description": "スクリーニングするテーマ",
                },
                "top_n": {
                    "type": "integer",
                    "description": "上位何銘柄を返すか (デフォルト5)",
                    "default": 5,
                },
            },
            "required": ["theme"],
        },
    },
]

# ── Tool implementations ────────────────────────────────────────────────────

def get_stock_quote(tickers: list[str]) -> dict[str, Any]:
    results = {}
    for t in tickers:
        try:
            tk = yf.Ticker(t)
            info = tk.fast_info
            results[t] = {
                "price": round(float(info.last_price), 2) if info.last_price else None,
                "prev_close": round(float(info.previous_close), 2) if info.previous_close else None,
                "change_pct": (
                    round((info.last_price - info.previous_close) / info.previous_close * 100, 2)
                    if info.last_price and info.previous_close
                    else None
                ),
                "volume": int(info.last_volume) if info.last_volume else None,
                "market_cap": int(info.market_cap) if info.market_cap else None,
            }
        except Exception as e:
            results[t] = {"error": str(e)}
    return results


def get_stock_info(ticker: str) -> dict[str, Any]:
    try:
        info = yf.Ticker(ticker).info
        return {
            "name": info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
            "summary": (info.get("longBusinessSummary") or "")[:400],
        }
    except Exception as e:
        return {"error": str(e)}


def get_price_history(ticker: str, period: str = "1mo") -> dict[str, Any]:
    try:
        hist = yf.Ticker(ticker).history(period=period)
        if hist.empty:
            return {"error": "no data"}
        closes = hist["Close"].round(2).tolist()
        dates = [str(d.date()) for d in hist.index]
        start, end = closes[0], closes[-1]
        momentum_pct = round((end - start) / start * 100, 2) if start else None
        return {
            "period": period,
            "start_price": start,
            "end_price": end,
            "momentum_pct": momentum_pct,
            "dates": dates[-5:],
            "closes": closes[-5:],
        }
    except Exception as e:
        return {"error": str(e)}


def get_stock_news(ticker: str) -> list[dict]:
    try:
        news = yf.Ticker(ticker).news or []
        return [
            {
                "title": n.get("content", {}).get("title", ""),
                "published": n.get("content", {}).get("pubDate", ""),
                "url": n.get("content", {}).get("canonicalUrl", {}).get("url", ""),
            }
            for n in news[:10]
        ]
    except Exception as e:
        return [{"error": str(e)}]


def screen_momentum_stocks(theme: str, top_n: int = 5) -> list[dict]:
    from stock_agent.watchlist import ALL_WATCHLIST, get_all_tickers

    if theme == "all":
        tickers_with_desc = []
        seen = set()
        for items in ALL_WATCHLIST.values():
            for t, d in items:
                if t not in seen:
                    seen.add(t)
                    tickers_with_desc.append((t, d))
    else:
        tickers_with_desc = ALL_WATCHLIST.get(theme, [])

    results = []
    for ticker, description in tickers_with_desc:
        hist = get_price_history(ticker, "1mo")
        quote = get_stock_quote([ticker]).get(ticker, {})
        if "error" not in hist and hist.get("momentum_pct") is not None:
            results.append({
                "ticker": ticker,
                "description": description,
                "momentum_1mo_pct": hist["momentum_pct"],
                "current_price": quote.get("price"),
                "change_today_pct": quote.get("change_pct"),
                "market_cap": quote.get("market_cap"),
            })

    results.sort(key=lambda x: x["momentum_1mo_pct"], reverse=True)
    return results[:top_n]


# ── Tool dispatcher ─────────────────────────────────────────────────────────

def dispatch_tool(name: str, inputs: dict) -> str:
    if name == "get_stock_quote":
        result = get_stock_quote(inputs["tickers"])
    elif name == "get_stock_info":
        result = get_stock_info(inputs["ticker"])
    elif name == "get_price_history":
        result = get_price_history(inputs["ticker"], inputs.get("period", "1mo"))
    elif name == "get_stock_news":
        result = get_stock_news(inputs["ticker"])
    elif name == "screen_momentum_stocks":
        result = screen_momentum_stocks(inputs["theme"], inputs.get("top_n", 5))
    else:
        result = {"error": f"unknown tool: {name}"}
    return json.dumps(result, ensure_ascii=False)
