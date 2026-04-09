import os
import re
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import anthropic

# Initialize Slack app
app = App(token=os.environ["SLACK_BOT_TOKEN"])

# Initialize Anthropic client
claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# Store conversation history per user (in-memory, resets on restart)
conversation_history: dict[str, list] = {}

SYSTEM_PROMPT = """あなたはRuiの専属ビジネス壁打ち相手です。スタートアップ、事業戦略、マーケティング、意思決定など、ビジネス全般の相談に乗ります。
まず結論・答えをズバッと言い、その後に理由を簡潔に添えます。
共感より「前に進む思考」を優先し、甘い言葉より鋭い本音を言います。
必要なら反論や別視点を積極的に提示します。
相手が話しかけた言語（日本語・英語）で返します。"""


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
                system=SYSTEM_PROMPT,
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
                            return # Ignore bot messages and other subtypes

    user_id = event["user"]
    text = event.get("text", "").strip()

    if not text:
                return

    response = get_claude_response(user_id, text)
    say(response)


if __name__ == "__main__":
        handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
