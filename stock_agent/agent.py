"""
Claude-powered stock investment agent.
Uses tool_use to fetch live data, then produces a Slack-ready analysis report.
"""
import os
import anthropic

from stock_agent.tools import TOOL_DEFINITIONS, dispatch_tool

claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

AGENT_SYSTEM = """あなたは株式投資アドバイザーエージェントです。
ユーザーはSpaceX関連株・Anthropic関連株・シミュレーター関連株に強い関心を持っています。
（SpaceX・Anthropicは非上場のため、関連する上場株・ETFをモニタリングします）

あなたのミッション:
1. ウォッチリストのモメンタム上位銘柄を特定する
2. 注目ニュースと価格動向を組み合わせて投資機会を評価する
3. 「今すぐ注目すべき銘柄」と「理由」をSlack通知向けに日本語で簡潔にまとめる

レポート形式:
- 先頭に🚀(宇宙系) 🤖(AI系) 🎮(シミュレーター系) の絵文字でカテゴリを示す
- 銘柄名・ティッカー・現在値・1ヶ月モメンタム・一言理由を記載
- 最後に「今週のアクション候補」として3銘柄以内に絞って提示する
- 投資は自己責任である旨を末尾に一言添える"""


def run_investment_analysis(user_prompt: str = None) -> str:
    """
    Run a full agentic investment analysis loop with tool use.
    Returns a Slack-ready markdown string.
    """
    if user_prompt is None:
        user_prompt = (
            "SpaceX関連・Anthropic関連・シミュレーター関連の全ウォッチリストを分析して、"
            "今週最も注目すべき投資機会トップ5をSlack通知用にまとめてください。"
            "各テーマのモメンタム上位銘柄を確認し、直近ニュースも参照した上で判断してください。"
        )

    messages = [{"role": "user", "content": user_prompt}]

    # Agentic loop: keep calling Claude until no more tool_use
    for _ in range(10):  # safety cap
        response = claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=AGENT_SYSTEM,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        # Collect assistant turn
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            break

        if response.stop_reason != "tool_use":
            break

        # Execute all tool calls and build tool_result turn
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result_text = dispatch_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result_text,
                })

        if tool_results:
            messages.append({"role": "user", "content": tool_results})

    # Extract final text from last assistant message
    for block in reversed(response.content):
        if hasattr(block, "text"):
            return block.text

    return "分析結果を取得できませんでした。"
