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

SYSTEM_PROMPT = """You are Pyrenee, a personal AI assistant for your owner in Slack.
You are helpful, concise, and friendly. You respond in the same language the user writes in.
You remember context within a conversation thread."""


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
