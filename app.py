import logging
import os
import re

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import anthropic

from stock_agent.scheduler import start_scheduler

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

app = App(token=os.environ["SLACK_BOT_TOKEN"])
claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# ── In-memory state ────────────────────────────────────────────────────────
conversation_history: dict[str, list] = {}

# Pending trade proposals waiting for "承認": user_id -> proposal dict
pending_orders: dict[str, dict] = {}

# ── System prompts ─────────────────────────────────────────────────────────
BUSINESS_SYSTEM = """あなたはRuiの専属ビジネス壁打ち相手です。スタートアップ、事業戦略、マーケティング、意思決定など、ビジネス全般の相談に乗ります。
まず結論・答えをズバッと言い、その後に理由を簡潔に添えます。
共感より「前に進む思考」を優先し、甘い言葉より鋭い本音を言います。
必要なら反論や別視点を積極的に提示します。
相手が話しかけた言語（日本語・英語）で返します。"""

# ── Routing patterns ───────────────────────────────────────────────────────
ROBOT_KEYWORDS = re.compile(
    r"(ロボ|robot|isrg|fanuc|ファナック|手術|surgical|倉庫|warehouse|ドローン|drone|"
    r"ヒューマノイド|humanoid|robo etf|botz|symbotic|sym\b|ter\b|rok\b|提案|スクリーニング|"
    r"spacex|space x|rklb|asts|lunr|lmt\b|noc\b|rtx\b|ktos|spce|arkx|宇宙|ロケット|"
    r"ai株|nvda|nvidia|googl|amzn|msft|meta\b|pltr|palantir|arm\b|smci|anet|"
    r"自動売買|auto.?trade|シグナル|signal)",
    re.IGNORECASE,
)
STOCK_KEYWORDS = re.compile(
    r"(株|stock|invest|銘柄|anthropic|シミュレ|simulator|etf|モメンタム)",
    re.IGNORECASE,
)
APPROVAL_RE = re.compile(r"^(承認|approve|yes|ok|はい)$", re.IGNORECASE)
CANCEL_RE = re.compile(r"^(キャンセル|取消|cancel|no|いいえ|やめる)$", re.IGNORECASE)
AUTO_TRADE_ON_RE = re.compile(r"自動売買(を?)?(オン|on|開始|スタート|有効)", re.IGNORECASE)
AUTO_TRADE_OFF_RE = re.compile(r"自動売買(を?)?(オフ|off|停止|無効)", re.IGNORECASE)
AUTO_TRADE_STATUS_RE = re.compile(r"自動売買.*(状態|ステータス|確認)|auto.?trade.*(status|on\?|off\?)", re.IGNORECASE)
PORTFOLIO_RE = re.compile(r"(ポートフォリオ|保有|holdings?|portfolio)", re.IGNORECASE)


# ── Helpers ────────────────────────────────────────────────────────────────

def _format_proposal(proposal: dict) -> str:
    s = proposal["score"]
    price_str = f"${proposal['limit_price']:,.2f}" if proposal.get("limit_price") else "成行"
    value_str = f"${proposal.get('order_value_usd', 0):,.0f}" if proposal.get("order_value_usd") else "—"
    stop_str = f"${proposal['stop_loss']:,.2f}" if proposal.get("stop_loss") else "—"
    return (
        f"*📊 売買提案*\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"銘柄: *{proposal['ticker']}*  |  売買: *{proposal['action']}*\n"
        f"数量: {proposal['quantity']}株  |  指値: {price_str}  |  注文額: {value_str}\n\n"
        f"*スコアリング*\n"
        f"  ファンダメンタルズ: {s['fundamentals']}/10\n"
        f"  モメンタム:         {s['momentum']}/10\n"
        f"  ニュースカタリスト: {s['catalyst']}/10\n"
        f"  バリュエーション:   {s['valuation']}/10\n"
        f"  ──────────────\n"
        f"  合計:               *{s['total']}/40*\n\n"
        f"*根拠:* {proposal['reasoning']}\n"
        f"*主要リスク:* {proposal['main_risk']}\n"
        f"*損切りライン:* {stop_str}（取得価格 −8%）\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"✅ 執行するには `承認` と返信  |  ❌ `キャンセル` で取消"
    )


def _execute_approved(user_id: str, say) -> None:
    from robot_agent.broker import risk_check, execute_trade
    from robot_agent.trade_log import log_trade

    order = pending_orders.pop(user_id)
    ok, reason = risk_check(order)
    if not ok:
        say(f"⛔ リスクチェック失敗: {reason}\n注文を執行しませんでした。")
        return

    price_str = f"${order['limit_price']:,.2f}" if order.get("limit_price") else "成行"
    say(
        f"🔄 *最終確認*\n"
        f"  {order['action']} {order['ticker']} {order['quantity']}株 @ {price_str}\n"
        f"  リスクチェック: ✅  →  執行します..."
    )

    result = execute_trade(order)
    log_trade(order, result)

    if result.get("status") in ("executed", "submitted"):
        mode_label = "📝 ペーパー" if "paper" in result.get("mode", "") else "🔴 ライブ"
        say(
            f"✅ *執行完了* ({mode_label})\n"
            f"  {result['action']} {result['ticker']} {result['quantity']}株 "
            f"@ ${result.get('price') or 0:,.2f}\n"
            f"  取引ログに記録しました。"
        )
    else:
        say(f"❌ 執行エラー: {result.get('error', '不明なエラー')}")


def get_claude_response(user_id: str, user_message: str) -> str:
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    conversation_history[user_id].append({"role": "user", "content": user_message})
    messages = conversation_history[user_id][-20:]
    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=BUSINESS_SYSTEM,
        messages=messages,
    )
    assistant_message = response.content[0].text
    conversation_history[user_id].append({"role": "assistant", "content": assistant_message})
    return assistant_message


# ── Core dispatcher ────────────────────────────────────────────────────────

def _auto_trade_toggle(enable: bool, say) -> None:
    import json
    from pathlib import Path
    p = Path("portfolio.json")
    data = json.loads(p.read_text())
    data.setdefault("auto_trade", {})["enabled"] = enable
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2))
    status = "✅ オン" if enable else "⛔ オフ"
    say(
        f"自動売買を *{status}* にしました。\n"
        + (
            "ペーパーモード中はスコア閾値を超えた銘柄を自動執行します。\n"
            "設定変更は `portfolio.json > auto_trade` で行えます。"
            if enable else
            "シグナルが出ても自動執行しません（手動提案は引き続き利用可）。"
        )
    )


def _portfolio_status(say) -> None:
    import json
    from pathlib import Path
    data = json.loads(Path("portfolio.json").read_text())
    mode = data.get("mode", "paper")
    auto_on = data.get("auto_trade", {}).get("enabled", False)
    holdings = data.get("holdings", [])

    lines = [
        f"*📂 ポートフォリオ状態*",
        f"モード: {'📝 ペーパー' if mode == 'paper' else '🔴 ライブ'}  |  "
        f"自動売買: {'✅ ON' if auto_on else '⛔ OFF'}",
        f"保有銘柄: {len(holdings)}件",
    ]
    if holdings:
        lines.append("")
        for h in holdings:
            lines.append(
                f"  • {h['ticker']}: {h['quantity']}株 "
                f"@ ${h.get('avg_price', 0):,.2f}"
            )
    say("\n".join(lines))


def _dispatch(user_id: str, text: str, say) -> None:
    if not text:
        return

    # 1. Approval / cancel (highest priority)
    if APPROVAL_RE.match(text):
        if user_id in pending_orders:
            _execute_approved(user_id, say)
        else:
            say("承認待ちの注文はありません。")
        return

    if CANCEL_RE.match(text):
        if user_id in pending_orders:
            order = pending_orders.pop(user_id)
            say(f"❌ {order['ticker']} の注文提案をキャンセルしました。")
        else:
            say("キャンセル待ちの注文はありません。")
        return

    # 2. Auto-trade control
    if AUTO_TRADE_ON_RE.search(text):
        _auto_trade_toggle(True, say)
        return
    if AUTO_TRADE_OFF_RE.search(text):
        _auto_trade_toggle(False, say)
        return
    if AUTO_TRADE_STATUS_RE.search(text):
        _portfolio_status(say)
        return

    # 3. Portfolio status
    if PORTFOLIO_RE.search(text):
        _portfolio_status(say)
        return

    # 4. Robotics / SpaceX / AI unified agent
    if ROBOT_KEYWORDS.search(text):
        say("🤖 分析中... しばらくお待ちください")
        try:
            from robot_agent.agent import run_robot_agent
            narrative, proposal = run_robot_agent(text)
            say(narrative)
            if proposal:
                pending_orders[user_id] = proposal
                say(_format_proposal(proposal))
        except Exception as e:
            log.exception("Robot agent error")
            say(f"エラーが発生しました: {e}")
        return

    # 5. General stock / Anthropic / Simulator agent
    if STOCK_KEYWORDS.search(text):
        say("📈 株式分析中... しばらくお待ちください")
        try:
            from stock_agent.agent import run_investment_analysis
            say(run_investment_analysis(text))
        except Exception as e:
            log.exception("Stock agent error")
            say(f"エラーが発生しました: {e}")
        return

    # 6. Default: business advisor
    say(get_claude_response(user_id, text))


# ── Slack event handlers ───────────────────────────────────────────────────

@app.event("app_mention")
def handle_mention(event, say):
    user_id = event["user"]
    text = re.sub(r"<@[A-Z0-9]+>", "", event["text"]).strip()
    if not text:
        say("How can I help you?")
        return
    _dispatch(user_id, text, say)


@app.event("message")
def handle_dm(event, say):
    if event.get("channel_type") != "im":
        return
    if event.get("subtype") is not None:
        return
    _dispatch(event["user"], event.get("text", "").strip(), say)


# ── Entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    start_scheduler(app.client)
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
