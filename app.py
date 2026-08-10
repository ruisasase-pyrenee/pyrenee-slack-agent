import os
import re
import base64
import requests
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

INVOICE_SYSTEM_PROMPT = """あなたはRuiのビジネスアシスタントとして、注文リストの画像からお見積もり（Invoice）を作成します。

ルール:
- 画像内で赤い枠線・赤い囲みで囲まれた商品のみを「注文された商品」として扱います。赤枠が付いていない商品は無視してください。
- 各商品について、商品名・単価・数量を画像から読み取ります。数量が読み取れない場合は1として計算し、その旨を明記してください。
- 出力はSlackのmrkdwn形式で、以下の構成にしてください:
  1. タイトル「📋 お見積もり」
  2. 商品ごとの明細（商品名 / 単価 / 数量 / 小計）
  3. 小計合計
  4. 消費税（10%）
  5. 合計金額（税込）
- 金額は日本円（¥記号、カンマ区切り）で表記してください。
- 赤枠で囲まれた商品が画像内に見つからない場合は、その旨を明確に伝え、金額の計算は行わないでください。
- 価格や数量の読み取りに自信が持てない箇所は、必ず「要確認」と明記してください。"""

# Slack mimetypes Claude's vision API can read directly.
IMAGE_MIME_TO_MEDIA_TYPE = {
    "image/png": "image/png",
    "image/jpeg": "image/jpeg",
    "image/jpg": "image/jpeg",
    "image/gif": "image/gif",
    "image/webp": "image/webp",
}


def download_slack_file(file_info: dict) -> tuple[bytes, str]:
    """Download a file uploaded to Slack using the bot token."""
    resp = requests.get(
        file_info["url_private"],
        headers={"Authorization": f"Bearer {os.environ['SLACK_BOT_TOKEN']}"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.content, file_info.get("mimetype", "image/png")


def generate_invoice_from_image(image_bytes: bytes, media_type: str) -> str:
    """Ask Claude to read the red-framed order items from an image and build a quotation."""
    b64_image = base64.standard_b64encode(image_bytes).decode("utf-8")
    response = claude.messages.create(
        model="claude-opus-4-5",
        max_tokens=2048,
        system=INVOICE_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": b64_image,
                    },
                },
                {
                    "type": "text",
                    "text": "この画像で赤い枠で囲まれている商品が注文です。価格を解析して、日本語でお見積もりを作成してください。",
                },
            ],
        }],
    )
    return response.content[0].text


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


def handle_image_orders(event, say) -> bool:
    """If the event carries an order-list image, post a generated quotation. Returns True if it handled the event."""
    image_files = [
        f for f in event.get("files", [])
        if f.get("mimetype") in IMAGE_MIME_TO_MEDIA_TYPE
    ]
    if not image_files:
        return False

    file_info = image_files[0]
    if len(image_files) > 1:
        say(f"複数の画像が添付されていますが、最初の1枚（{file_info.get('name', '画像')}）のみ解析します。")

    try:
        image_bytes, mimetype = download_slack_file(file_info)
        media_type = IMAGE_MIME_TO_MEDIA_TYPE.get(mimetype, "image/png")
        invoice_text = generate_invoice_from_image(image_bytes, media_type)
    except Exception as exc:
        say(f"画像の解析中にエラーが発生しました: {exc}")
        return True

    say(invoice_text)
    return True


@app.event("app_mention")
def handle_mention(event, say):
    """Handle @mentions in channels."""
    user_id = event["user"]
    # Remove the bot mention from the text
    text = re.sub(r"<@[A-Z0-9]+>", "", event["text"]).strip()

    if handle_image_orders(event, say):
        return

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
    # Ignore bot messages / edits / deletions, but allow plain image uploads (file_share)
    if event.get("subtype") not in (None, "file_share"):
        return

    user_id = event["user"]
    text = event.get("text", "").strip()

    if handle_image_orders(event, say):
        return

    if not text:
        return

    response = get_claude_response(user_id, text)
    say(response)


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
