"""
Claude API wrapper with tool use support.

Claudeがツールを呼び出してGmail/Calendarにアクセスし、
自律的にトリアージ・ブリーフィング・フォローアップを実行する。
"""

import os
import json
import logging
from pathlib import Path
import anthropic
import google_client
import memory
from db import get_history, append_message

logger = logging.getLogger(__name__)

claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
MODEL = "claude-opus-4-7"

# ── System prompt ──────────────────────────────────────────────────────────────

_CLAUDE_MD = (Path(__file__).parent / "CLAUDE.md").read_text(encoding="utf-8")

SYSTEM_PROMPT = f"""あなたは笹瀬 類（Rui Sasase）の専属AIビジネスパートナーです。

【行動原則】
- 結論から言う。理由・背景は後。
- 甘い言葉より鋭い本音。前に進む思考を優先する。
- 日本語で来たら日本語、英語で来たら英語で返す。
- ツールが使えるなら積極的に使い、実際のデータに基づいて答える。

【コンテキスト（CLAUDE.md）】
{_CLAUDE_MD}
"""

# ── Tool definitions ───────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "get_emails",
        "description": "Gmailからメールを検索・取得する。未読メールのトリアージ、特定の相手からのメール確認などに使う。",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Gmail検索クエリ。例: 'is:unread', 'from:tim@timmoore.work', 'subject:E-2'",
                },
                "max_results": {
                    "type": "integer",
                    "description": "取得件数（デフォルト10）",
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_email_body",
        "description": "特定メールの本文を取得する。get_emails で得た message_id を使う。",
        "input_schema": {
            "type": "object",
            "properties": {
                "message_id": {"type": "string", "description": "メールのID"},
            },
            "required": ["message_id"],
        },
    },
    {
        "name": "create_email_draft",
        "description": "Gmailに下書きを作成する。送信は行わない。",
        "input_schema": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "宛先メールアドレス"},
                "subject": {"type": "string", "description": "件名"},
                "body": {"type": "string", "description": "本文"},
            },
            "required": ["to", "subject", "body"],
        },
    },
    {
        "name": "get_upcoming_events",
        "description": "Googleカレンダーから今後の予定を取得する。",
        "input_schema": {
            "type": "object",
            "properties": {
                "days_ahead": {
                    "type": "integer",
                    "description": "何日先まで取得するか（デフォルト7）",
                    "default": 7,
                },
                "max_results": {
                    "type": "integer",
                    "description": "最大取得件数（デフォルト10）",
                    "default": 10,
                },
            },
        },
    },
]


# ── Tool execution ─────────────────────────────────────────────────────────────

def _run_tool(name: str, inputs: dict) -> str:
    try:
        if name == "get_emails":
            results = google_client.get_emails(
                query=inputs["query"],
                max_results=inputs.get("max_results", 10),
            )
            if not results:
                return "メールが見つかりませんでした。"
            return json.dumps(results, ensure_ascii=False, indent=2)

        elif name == "get_email_body":
            body = google_client.get_email_body(inputs["message_id"])
            return body or "（本文を取得できませんでした）"

        elif name == "create_email_draft":
            result = google_client.create_draft(
                to=inputs["to"],
                subject=inputs["subject"],
                body=inputs["body"],
            )
            return json.dumps(result, ensure_ascii=False)

        elif name == "get_upcoming_events":
            events = google_client.get_upcoming_events(
                days_ahead=inputs.get("days_ahead", 7),
                max_results=inputs.get("max_results", 10),
            )
            if not events:
                return "予定が見つかりませんでした。"
            return json.dumps(events, ensure_ascii=False, indent=2)

        else:
            return f"不明なツール: {name}"

    except Exception as e:
        logger.error(f"Tool {name} error: {e}")
        return f"エラー: {e}"


# ── Agentic loop ───────────────────────────────────────────────────────────────

def _run_with_tools(messages: list[dict], system: str = None) -> str:
    """ツール使用のアジェンティックループを実行する。"""
    sys_prompt = system or SYSTEM_PROMPT
    tools = TOOLS if google_client.is_configured() else []

    while True:
        response = claude.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=sys_prompt,
            tools=tools,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            text_blocks = [b.text for b in response.content if hasattr(b, "text")]
            return "\n".join(text_blocks)

        if response.stop_reason == "tool_use":
            # ツール呼び出しを実行
            assistant_msg = {"role": "assistant", "content": response.content}
            messages.append(assistant_msg)

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    logger.info(f"Tool call: {block.name}({block.input})")
                    result = _run_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            messages.append({"role": "user", "content": tool_results})
            continue

        # 予期しない stop_reason
        text_blocks = [b.text for b in response.content if hasattr(b, "text")]
        return "\n".join(text_blocks)


# ── Public API ─────────────────────────────────────────────────────────────────

def get_claude_response(user_id: str, user_message: str, channel_id: str = None) -> str:
    """通常の会話: 履歴＋長期記憶付きでClaudeに返答させる。"""
    # 関連する記憶を検索して注入
    relevant_memories = memory.search(user_message, limit=5)
    memory_context = memory.format_for_prompt(relevant_memories)

    system = SYSTEM_PROMPT
    if memory_context:
        system = f"{SYSTEM_PROMPT}\n\n{memory_context}"

    history = get_history(user_id)
    history.append({"role": "user", "content": user_message})

    response = _run_with_tools(history, system=system)

    append_message(user_id, "user", user_message, channel_id)
    append_message(user_id, "assistant", response, channel_id)

    # 会話から重要な事実を非同期で記憶に保存
    import threading
    threading.Thread(
        target=memory.extract_and_store,
        args=(user_message, response),
        daemon=True
    ).start()

    return response


def run_triage() -> str:
    """A: 未読メールのトリアージを実行する。"""
    prompt = """未読メールをチェックして、Ruiのために以下の形式でまとめてください：

**今日のメールトリアージ**

【要返信（優先度順）】
- 件名 / 送信者 / 一言サマリー → 推奨アクション

【FYI（確認のみ）】
- 件名 / 送信者 / 内容一行

【スキップ可】
- 件数のみ

まずis:unreadでメールを検索してください。"""

    messages = [{"role": "user", "content": prompt}]
    return _run_with_tools(messages)


def run_briefing(meeting_name: str = "") -> str:
    """B: 次のミーティングのブリーフィングを実行する。"""
    context = f"ミーティング名: {meeting_name}" if meeting_name else "次の予定"
    prompt = f"""カレンダーを確認して、{context}のブリーフィングを作成してください：

**ミーティングブリーフィング**

【概要】タイトル / 時間 / 参加者

【参加者について】
- 各参加者の役割・関係性（CLAUDE.mdの情報を活用）

【前回からの流れ】
- 直近のメールやコンテキスト（get_emailsで相手からのメールを検索）

【確認すべき点・議題候補】
- 箇条書き3〜5項目

【おすすめ冒頭トーク】
- 一言"""

    messages = [{"role": "user", "content": prompt}]
    return _run_with_tools(messages)


def run_followup(context: str = "") -> str:
    """C: ミーティング後のフォローアップドラフトを作成する。"""
    prompt = f"""直近のミーティングに基づいて、フォローアップメールの下書きを作成してください。

{'ミーティングメモ: ' + context if context else 'カレンダーで直近の予定を確認してください。'}

以下の形式で出力:
1. 送信すべき相手と件名の提案
2. メール本文案（英語 or 日本語、相手に合わせて）
3. 「create_email_draft でGmail下書きに保存しますか？」と確認

必要に応じてメールや予定を検索して文脈を補完してください。"""

    messages = [{"role": "user", "content": prompt}]
    return _run_with_tools(messages)


def run_morning_digest() -> str:
    """A+B: 朝の自動ダイジェスト（トリアージ + 今日の予定）。"""
    prompt = """おはようございます。Ruiのために今日のスタートダッシュ情報をまとめてください。

**ステップ1**: is:unread でメールをチェック
**ステップ2**: カレンダーで今日と明日の予定を確認

出力フォーマット:
---
**おはようございます**

**今日の予定** (日付)
- 時間 / ミーティング名 / 参加者

**未読メール（要対応）**
- 件名 / 送信者 → アクション

**今日のフォーカス**
- 最重要タスク1〜3個（メール・カレンダーから判断）
---"""

    messages = [{"role": "user", "content": prompt}]
    return _run_with_tools(messages)
