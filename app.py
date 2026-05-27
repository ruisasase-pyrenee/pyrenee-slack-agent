import os
import re
import logging

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import anthropic

from stock_agent.scheduler import start_scheduler

logging.basicConfig(level=logging.INFO)

app = App(token=os.environ["SLACK_BOT_TOKEN"])
claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

conversation_history: dict[str, list] = {}

SYSTEM_PROMPT = """あなたはRuiの専属ビジネス壁打ち相手です。スタートアップ、事業戦略、マーケティング、意思決定など、ビジネス全般の相談に乗ります。
まず結論・答えをズバッと言い、その後に理由を簡潔に添えます。
共感より「前に進む思考」を優先し、甘い言葉より鋭い本音を言います。
必要なら反論や別視点を積極的に提示します。
相手が話しかけた言語（日本語・英語）で返します。"""

# ── Stock command keywords ─────────────────────────────────────────────────
STOCK_KEYWORDS = re.compile(
    r"(株|stock|invest|銘柄|分析|ウォッチ|space.?x|anthropic|シミュレ|simulator|etf|ticker)",
    re.IGNORECASE,
)


def _run_stock_analysis(prompt: str | None = None) -> str:
    from stock_agent.agent import run_investment_analysis
    return run_investment_analysis(prompt)


# ── Claude chat helper ─────────────────────────────────────────────────────

def get_claude_response(user_id: str, user_message: str) -> str:
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    conversation_history[user_id].append({"role": "user", "content": user_message})
    messages = conversation_history[user_id][-20:]

    response = claude.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    assistant_message = response.content[0].text
    conversation_history[user_id].append({"role": "assistant", "content": assistant_message})
    return assistant_message


# ── Slack event handlers ───────────────────────────────────────────────────

@app.event("app_mention")
def handle_mention(event, say):
    user_id = event["user"]
    text = re.sub(r"<@[A-Z0-9]+>", "", event["text"]).strip()

    if not text:
        say("How can I help you?")
        return

    # Route stock-related requests to the investment agent
    if STOCK_KEYWORDS.search(text):
        say("📈 株式分析エージェントを起動中... 少々お待ちください")
        try:
            report = _run_stock_analysis(text)
            say(report)
        except Exception as e:
            say(f"エラーが発生しました: {e}")
        return

    say(get_claude_response(user_id, text))


@app.event("message")
def handle_dm(event, say):
    if event.get("channel_type") != "im":
        return
    if event.get("subtype") is not None:
        return

    user_id = event["user"]
    text = event.get("text", "").strip()

    if not text:
        return

    if STOCK_KEYWORDS.search(text):
        say("📈 株式分析エージェントを起動中... 少々お待ちください")
        try:
            report = _run_stock_analysis(text)
            say(report)
        except Exception as e:
            say(f"エラーが発生しました: {e}")
        return

    say(get_claude_response(user_id, text))


# ── Entry point ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Start background investment scheduler (sends to INVESTMENT_CHANNEL_ID)
    start_scheduler(app.client)

    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
