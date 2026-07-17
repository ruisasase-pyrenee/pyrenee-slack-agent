"""
Claude-powered robotics trading analyst.
Returns (analysis_text, trade_proposal | None).
"""
import json
import os

import anthropic

from robot_agent.tools import ROBOT_TOOLS, dispatch_tool

claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

ROBOT_SYSTEM = """あなたは私専属のテック株リサーチ&トレードアシスタントです。
最終判断は必ず私が下します。あなたの仕事は「提案」のみです。

## 対象ユニバース（3テーマ）

🤖 ロボティクス:
ヒューマノイド / 産業用・協働ロボット / 手術ロボット / 倉庫自動化 /
ロボット部品（アクチュエータ・センサー・減速機・触覚）/ Physical AI関連。

🚀 SpaceX関連（SpaceX自体は非上場）:
小型ロケット / 衛星通信 / 月面探査 / 防衛宇宙 / 宇宙インフラ /
SpaceXのETF・競合上場株。

🤖 AI/Anthropic関連（Anthropic自体は非上場）:
LLM競合・投資家 / AIインフラ（GPU・サーバー） / エッジAI /
量子コンピュータ / エンタープライズAI。

## 必須ワークフロー
1. 起動時に必ず read_watchlist と read_portfolio を呼ぶ
2. 各銘柄のデータを get_stock_quote / get_financial_data / get_price_momentum / get_stock_news で取得
3. 以下4軸でスコアリング（各1-10点、合計40点満点）:
   - ファンダメンタルズ: 売上成長率・粗利率・FCF
   - モメンタム: 1ヶ月・3ヶ月リターン、移動平均乖離
   - ニュースカタリスト: 決算beat・新規契約・製品発表
   - バリュエーション: PSR・EV/Revenue vs セクター平均（割安ほど高スコア）
4. 売買提案をする場合は必ず propose_trade ツールを呼んで確定させる

## 売買提案フォーマット（propose_trade呼び出し前に必ずテキストで表示）
```
📊 売買提案
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
銘柄: [TICKER] — [会社名]
売買: BUY / SELL
数量: X株
指値: $XXX.XX（成行の場合は「成行」）
注文額: $X,XXX

スコアリング:
  ファンダメンタルズ: X/10
  モメンタム:         X/10
  ニュースカタリスト: X/10
  バリュエーション:   X/10
  ━━━━━━━━━━━━
  合計:               XX/40

根拠:
  [3行以内]

主要リスク: [1行]
損切りライン: $XXX.XX（取得価格 -8%）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

## 禁止事項
- 「確実に上がる」等の断定表現
- propose_trade を呼ばずに「注文します」等の発言
- 日付未検証の古いニュースによる提案
- ※投資は自己責任である旨を必ず末尾に一言添える"""


def run_robot_agent(user_prompt: str) -> tuple[str, dict | None]:
    """
    Run the robotics investment agent.
    Returns (narrative_text, trade_proposal_dict | None).
    trade_proposal_dict is set only if the agent called propose_trade.
    """
    messages = [{"role": "user", "content": user_prompt}]
    trade_proposal: dict | None = None

    for _ in range(12):  # safety cap on tool rounds
        response = claude.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=ROBOT_SYSTEM,
            tools=ROBOT_TOOLS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            break

        if response.stop_reason != "tool_use":
            break

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result_str = dispatch_tool(block.name, block.input)

                # Capture the trade proposal if agent called propose_trade
                if block.name == "propose_trade":
                    trade_proposal = json.loads(result_str)

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result_str,
                })

        if tool_results:
            messages.append({"role": "user", "content": tool_results})

    # Extract final narrative text
    final_text = ""
    for block in reversed(response.content):
        if hasattr(block, "text"):
            final_text = block.text
            break

    return final_text, trade_proposal
