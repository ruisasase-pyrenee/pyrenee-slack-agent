import os
import re
from pathlib import Path

from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import anthropic

load_dotenv()

# Initialize Slack app
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# Initialize Anthropic client
claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# Store conversation history per user (in-memory, resets on restart)
conversation_history: dict[str, list] = {}

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"

# Slack user ID of the owner (Rui). Private context is only shown to this user.
OWNER_SLACK_USER_ID = os.environ.get("OWNER_SLACK_USER_ID", "")


def load_knowledge(directory: Path) -> str:
    """Concatenate all Markdown files in a directory (non-recursive)."""
    if not directory.is_dir():
        return ""
    return "\n\n".join(
        f"<document name=\"{path.name}\">\n{path.read_text(encoding='utf-8')}\n</document>"
        for path in sorted(directory.glob("*.md"))
    )


BASE_PROMPT = """あなたはRuiの専属ビジネス壁打ち相手です。スタートアップ、事業戦略、マーケティング、意思決定など、ビジネス全般の相談に乗ります。
Ruiは株式会社Pyrenee（Pyrenee Inc.）のUS Evangelistとして、アメリカ事業の立ち上げと投資家集めを担っています。
まず結論・答えをズバッと言い、その後に理由を簡潔に添えます。
共感より「前に進む思考」を優先し、甘い言葉より鋭い本音を言います。
必要なら反論や別視点を積極的に提示します。
相手が話しかけた言語（日本語・英語）で返します。

Pyreneeについての質問には、下の社内ナレッジに基づいて答えます。ナレッジにないことは推測で断定せず、「不明」「ナレッジにない」と明言します。
ナレッジ内の [提供] は Rui 本人が提供した最優先の情報です。[資料] と食い違う場合は [提供] を正とします。
work_rules.md のルールは常に守ります。"""

PUBLIC_KNOWLEDGE = load_knowledge(KNOWLEDGE_DIR)
PRIVATE_KNOWLEDGE = load_knowledge(KNOWLEDGE_DIR / "private")

SYSTEM_PROMPT = BASE_PROMPT
if PUBLIC_KNOWLEDGE:
    SYSTEM_PROMPT += f"\n\n<pyrenee_knowledge>\n{PUBLIC_KNOWLEDGE}\n</pyrenee_knowledge>"

OWNER_SYSTEM_PROMPT = SYSTEM_PROMPT
if PRIVATE_KNOWLEDGE:
    OWNER_SYSTEM_PROMPT += f"\n\n<owner_private_context>\n{PRIVATE_KNOWLEDGE}\n</owner_private_context>"


def system_prompt_for(user_id: str) -> str:
    """Owner gets private context; everyone else gets company knowledge only."""
    if OWNER_SLACK_USER_ID and user_id == OWNER_SLACK_USER_ID:
        return OWNER_SYSTEM_PROMPT
    return SYSTEM_PROMPT


def get_claude_response(user_id: str, user_message: str) -> str:
    """Get a response from Claude, maintaining conversation history."""
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    conversation_history[user_id].append({
        "role": "user",
        "content": user_message
    })

    # Keep last 20 messages to avoid token limits
    messages = conversation_history[user_id][-20:]

    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=2048,
        system=system_prompt_for(user_id),
        messages=messages
    )

    assistant_message = response.content[0].text

    conversation_history[user_id].append({
        "role": "assistant",
        "content": assistant_message
    })

    return assistant_message


@app.event("app_mention")
def handle_mention(event, say):
    """Handle @mentions in channels."""
    user_id = event["user"]
    # Remove the bot mention from the text
    text = re.sub(r"<@[A-Z0-9]+>", "", event["text"]).strip()

    if not text:
        say("How can I help you?")
        return

    response = get_claude_response(user_id, text)
    say(response)


@app.event("message")
def handle_dm(event, say):
    """Handle direct messages."""
    # Only respond to DMs (channel_type == "im"), not channel messages
    if event.get("channel_type") != "im":
        return
    if event.get("subtype") is not None:
        return  # Ignore bot messages and other subtypes

    user_id = event["user"]
    text = event.get("text", "").strip()

    if not text:
        return

    response = get_claude_response(user_id, text)
    say(response)


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
