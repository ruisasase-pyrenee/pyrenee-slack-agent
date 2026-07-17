"""
Tool implementations and Claude tool schemas for the robotics trading agent.
"""
import json
from pathlib import Path
from typing import Any

import yfinance as yf

# ── Claude tool schema definitions ──────────────────────────────────────────

ROBOT_TOOLS = [
    {
        "name": "read_watchlist",
        "description": "watchlist.jsonを読み込み、ロボティクスユニバースの全銘柄リストを返す。",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "read_portfolio",
        "description": "portfolio.jsonを読み込み、現在のポートフォリオ設定・保有銘柄・ペーパーモード状態を返す。",
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_stock_quote",
        "description": "指定銘柄の現在値・前日比・出来高・時価総額を返す。複数銘柄一括取得可能。",
        "input_schema": {
            "type": "object",
            "properties": {
                "tickers": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "ティッカーシンボルのリスト",
                }
            },
            "required": ["tickers"],
        },
    },
    {
        "name": "get_financial_data",
        "description": (
            "銘柄のファンダメンタルズ情報を返す: 売上高成長率・粗利益率・PER・PSR・"
            "EV/Sales・負債比率・FCF。4軸スコアリングのファンダメンタルズ・バリュエーション軸に使う。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {"ticker": {"type": "string"}},
            "required": ["ticker"],
        },
    },
    {
        "name": "get_price_momentum",
        "description": (
            "銘柄の価格モメンタムを計算: 1週・1ヶ月・3ヶ月・6ヶ月リターン、"
            "50日MA・200日MAとの乖離率。4軸スコアリングのモメンタム軸に使う。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {"ticker": {"type": "string"}},
            "required": ["ticker"],
        },
    },
    {
        "name": "get_stock_news",
        "description": "銘柄の最新ニュースヘッドライン（最大10件）を返す。ニュースカタリスト軸のスコアリングに使う。",
        "input_schema": {
            "type": "object",
            "properties": {"ticker": {"type": "string"}},
            "required": ["ticker"],
        },
    },
    {
        "name": "propose_trade",
        "description": (
            "売買提案を確定・フォーマットする。このツールを呼ぶと提案がSlackに送信され、"
            "ユーザーの承認を待つ状態になる。承認なしでは絶対に執行されない。"
            "損切りラインは自動計算（取得価格 - 8%）するが、明示的に指定も可能。"
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {"type": "string", "description": "ティッカーシンボル"},
                "action": {"type": "string", "enum": ["BUY", "SELL"], "description": "売買方向"},
                "quantity": {"type": "integer", "description": "注文数量（株数）"},
                "limit_price": {
                    "type": "number",
                    "description": "指値価格（USD）。nullの場合は成行注文",
                },
                "reasoning": {
                    "type": "string",
                    "description": "根拠（3行以内）",
                },
                "main_risk": {
                    "type": "string",
                    "description": "主要リスク（1行）",
                },
                "score_fundamentals": {"type": "integer", "description": "ファンダメンタルズスコア 1-10"},
                "score_momentum": {"type": "integer", "description": "モメンタムスコア 1-10"},
                "score_catalyst": {"type": "integer", "description": "ニュースカタリストスコア 1-10"},
                "score_valuation": {"type": "integer", "description": "バリュエーションスコア 1-10"},
            },
            "required": [
                "ticker", "action", "quantity", "limit_price",
                "reasoning", "main_risk",
                "score_fundamentals", "score_momentum",
                "score_catalyst", "score_valuation",
            ],
        },
    },
]

# ── Tool implementations ─────────────────────────────────────────────────────

def read_watchlist() -> dict:
    path = Path("watchlist.json")
    if path.exists():
        return json.loads(path.read_text())
    return {"error": "watchlist.json not found"}


def read_portfolio() -> dict:
    path = Path("portfolio.json")
    if path.exists():
        return json.loads(path.read_text())
    return {"error": "portfolio.json not found"}


def get_stock_quote(tickers: list[str]) -> dict[str, Any]:
    results = {}
    for t in tickers:
        try:
            info = yf.Ticker(t).fast_info
            prev = float(info.previous_close) if info.previous_close else None
            last = float(info.last_price) if info.last_price else None
            results[t] = {
                "price": round(last, 2) if last else None,
                "prev_close": round(prev, 2) if prev else None,
                "change_pct": round((last - prev) / prev * 100, 2) if last and prev else None,
                "volume": int(info.last_volume) if info.last_volume else None,
                "market_cap_b": round(float(info.market_cap) / 1e9, 2) if info.market_cap else None,
            }
        except Exception as e:
            results[t] = {"error": str(e)}
    return results


def get_financial_data(ticker: str) -> dict[str, Any]:
    try:
        info = yf.Ticker(ticker).info
        return {
            "name": info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "revenue_growth_yoy": info.get("revenueGrowth"),
            "gross_margin": info.get("grossMargins"),
            "operating_margin": info.get("operatingMargins"),
            "pe_trailing": info.get("trailingPE"),
            "pe_forward": info.get("forwardPE"),
            "ps_ratio": info.get("priceToSalesTrailing12Months"),
            "ev_to_revenue": info.get("enterpriseToRevenue"),
            "debt_to_equity": info.get("debtToEquity"),
            "free_cash_flow_b": (
                round(info["freeCashflow"] / 1e9, 2)
                if info.get("freeCashflow")
                else None
            ),
            "52w_high": info.get("fiftyTwoWeekHigh"),
            "52w_low": info.get("fiftyTwoWeekLow"),
        }
    except Exception as e:
        return {"error": str(e)}


def get_price_momentum(ticker: str) -> dict[str, Any]:
    try:
        hist = yf.Ticker(ticker).history(period="1y")
        if hist.empty:
            return {"error": "no data"}

        closes = hist["Close"]
        now = float(closes.iloc[-1])

        def ret(n_days: int) -> float | None:
            if len(closes) >= n_days:
                return round((now - float(closes.iloc[-n_days])) / float(closes.iloc[-n_days]) * 100, 2)
            return None

        ma50 = float(closes.rolling(50).mean().iloc[-1]) if len(closes) >= 50 else None
        ma200 = float(closes.rolling(200).mean().iloc[-1]) if len(closes) >= 200 else None

        return {
            "current_price": round(now, 2),
            "return_1w_pct": ret(5),
            "return_1mo_pct": ret(21),
            "return_3mo_pct": ret(63),
            "return_6mo_pct": ret(126),
            "above_50d_ma_pct": round((now - ma50) / ma50 * 100, 2) if ma50 else None,
            "above_200d_ma_pct": round((now - ma200) / ma200 * 100, 2) if ma200 else None,
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
            }
            for n in news[:10]
        ]
    except Exception as e:
        return [{"error": str(e)}]


def propose_trade(
    ticker: str,
    action: str,
    quantity: int,
    limit_price: float | None,
    reasoning: str,
    main_risk: str,
    score_fundamentals: int,
    score_momentum: int,
    score_catalyst: int,
    score_valuation: int,
) -> dict:
    total_score = score_fundamentals + score_momentum + score_catalyst + score_valuation
    entry = limit_price or 0.0
    stop_loss = round(entry * (1 - 0.08), 2) if entry else None
    order_value = round(quantity * entry, 2) if entry else None

    return {
        "ticker": ticker,
        "action": action,
        "quantity": quantity,
        "limit_price": limit_price,
        "order_value_usd": order_value,
        "stop_loss": stop_loss,
        "reasoning": reasoning,
        "main_risk": main_risk,
        "score": {
            "fundamentals": score_fundamentals,
            "momentum": score_momentum,
            "catalyst": score_catalyst,
            "valuation": score_valuation,
            "total": total_score,
        },
    }


# ── Tool dispatcher ──────────────────────────────────────────────────────────

def dispatch_tool(name: str, inputs: dict) -> str:
    if name == "read_watchlist":
        result = read_watchlist()
    elif name == "read_portfolio":
        result = read_portfolio()
    elif name == "get_stock_quote":
        result = get_stock_quote(inputs["tickers"])
    elif name == "get_financial_data":
        result = get_financial_data(inputs["ticker"])
    elif name == "get_price_momentum":
        result = get_price_momentum(inputs["ticker"])
    elif name == "get_stock_news":
        result = get_stock_news(inputs["ticker"])
    elif name == "propose_trade":
        result = propose_trade(
            ticker=inputs["ticker"],
            action=inputs["action"],
            quantity=inputs["quantity"],
            limit_price=inputs.get("limit_price"),
            reasoning=inputs["reasoning"],
            main_risk=inputs["main_risk"],
            score_fundamentals=inputs["score_fundamentals"],
            score_momentum=inputs["score_momentum"],
            score_catalyst=inputs["score_catalyst"],
            score_valuation=inputs["score_valuation"],
        )
    else:
        result = {"error": f"unknown tool: {name}"}

    return json.dumps(result, ensure_ascii=False)
