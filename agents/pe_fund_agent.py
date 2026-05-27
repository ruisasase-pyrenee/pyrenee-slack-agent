"""
PE Fund Launch Agent - Core orchestrator.

Uses Claude tool-use to autonomously:
1. Screen deals against investment thesis
2. Track legal/compliance checklist
3. Manage portfolio companies
4. Generate IC memos and LP reports
"""

import json
import anthropic
from datetime import datetime

from config.fund_config import FUND_CONFIG, DEAL_SCREENING_CRITERIA, LEGAL_CHECKLIST
from tools.drive_tools import get_tool_definitions, execute_tool
from templates.documents import (
    screening_memo_prompt,
    ic_memo_prompt,
    lp_report_prompt,
    legal_checklist_report,
)

MODEL = "claude-opus-4-7"

SYSTEM_PROMPT = f"""あなたはPEファンド「Pyrenee Capital」の専属AIエージェントです。
ファンドマネージャーのRui Sasaseを支援し、以下の業務を自律的に実行します:

1. **Deal Screening**: 案件を投資基準に照らしてスクリーニングし、詳細メモをGoogle Driveに保存
2. **法務コンプライアンス**: ファンド設立・運営に必要な法務タスクを追跡・管理
3. **ポートフォリオ管理**: 投資先のKPI追跡、LP報告書作成
4. **IC メモ作成**: 投資委員会向けの詳細分析メモを作成

## ファンド基本情報
- ファンド名: {FUND_CONFIG['name']}
- 戦略: {FUND_CONFIG['strategy']}
- フォーカスセクター: {', '.join(FUND_CONFIG['focus']['sectors'])}
- チェックサイズ: {FUND_CONFIG['focus']['check_size_min_mn_jpy']}M〜{FUND_CONFIG['focus']['check_size_max_mn_jpy']}M JPY
- ターゲットIRR: {FUND_CONFIG['focus']['target_irr']}

## 行動原則
- 情報が不足している場合は、合理的な仮定を明示した上で分析を進める
- 重要な意思決定には必ずリスクと根拠を示す
- ドキュメントは自動的にGoogle Driveの適切なフォルダに保存する
- 日本語で回答する（英語で聞かれた場合は英語で回答）
- 結論を先に述べ、詳細は後から説明する

## 利用可能なツール
- search_drive: 既存ドキュメント検索
- save_to_drive: ドキュメント保存（メモ、レポート、チェックリスト）
- update_deal_status: ディールパイプライン更新
- update_legal_task: 法務タスクステータス更新
- list_portfolio: ポートフォリオ一覧取得

判断に迷った場合は積極的に確認を求める。"""


class PEFundAgent:
    def __init__(self, mcp_client=None):
        self.claude = anthropic.Anthropic()
        self.mcp_client = mcp_client
        self.tools = get_tool_definitions()
        self.conversation_history: dict[str, list] = {}

    def _get_history(self, user_id: str) -> list:
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = []
        return self.conversation_history[user_id]

    def _add_message(self, user_id: str, role: str, content) -> None:
        self._get_history(user_id).append({"role": role, "content": content})

    async def process_message(self, user_id: str, message: str) -> str:
        """Process a user message through the agentic loop."""
        self._add_message(user_id, "user", message)
        messages = self._get_history(user_id)[-20:]

        response_text = await self._agentic_loop(messages)

        self._add_message(user_id, "assistant", response_text)
        return response_text

    async def _agentic_loop(self, messages: list) -> str:
        """Run the tool-use agentic loop until a final response."""
        current_messages = list(messages)

        while True:
            response = self.claude.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=SYSTEM_PROMPT,
                tools=self.tools,
                messages=current_messages,
            )

            if response.stop_reason == "end_turn":
                # Extract text from response
                for block in response.content:
                    if hasattr(block, "text"):
                        return block.text
                return "（応答なし）"

            if response.stop_reason == "tool_use":
                # Add assistant's response (with tool calls) to messages
                current_messages.append({
                    "role": "assistant",
                    "content": response.content
                })

                # Execute all tool calls
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = await execute_tool(
                            block.name,
                            block.input,
                            self.mcp_client
                        )
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })

                current_messages.append({
                    "role": "user",
                    "content": tool_results
                })
                continue

            # Unexpected stop reason
            break

        return "エラー: 応答の生成に失敗しました。"

    # ── Structured workflow triggers ──────────────────────────────────────

    async def screen_deal(self, user_id: str, company_info: str) -> str:
        """Trigger deal screening workflow."""
        prompt = f"""以下の会社をスクリーニングしてください。
分析後、必ずsave_to_driveツールを使ってdeal_pipelineフォルダにスクリーニングメモを保存し、
その後update_deal_statusツールでステータスを'screening'に更新してください。

{screening_memo_prompt(company_info, FUND_CONFIG, DEAL_SCREENING_CRITERIA)}
"""
        return await self.process_message(user_id, prompt)

    async def create_ic_memo(self, user_id: str, company_info: str) -> str:
        """Trigger IC memo creation workflow."""
        # First search for existing screening memo
        search_prompt = f"""「{company_info}」のICメモを作成してください。
まずsearch_driveで既存のスクリーニングメモを検索し、見つかれば内容を読み込んでください。
その後、詳細なICメモを作成し、ic_memosフォルダに保存してください。

{ic_memo_prompt(company_info, '（Drive内のスクリーニングメモを参照）', FUND_CONFIG)}
"""
        return await self.process_message(user_id, search_prompt)

    async def show_legal_checklist(self, user_id: str) -> str:
        """Show current legal/compliance status."""
        checklist_text = legal_checklist_report(LEGAL_CHECKLIST)
        prompt = f"""現在のファンド法務チェックリストを確認し、優先度の高い未完了タスクについてアドバイスしてください。
また、このチェックリストをsave_to_driveでlegal_complianceフォルダに保存してください。

{checklist_text}
"""
        return await self.process_message(user_id, prompt)

    async def generate_lp_report(self, user_id: str, period: str = None) -> str:
        """Generate LP report."""
        if period is None:
            period = datetime.now().strftime("%Y年%m月")

        prompt = f"""LP報告書を作成してください。
まずlist_portfolioでポートフォリオ情報を取得し、
{lp_report_prompt('（Drive内のポートフォリオデータを参照）', period, FUND_CONFIG)}
作成後、lp_relationsフォルダに保存してください。
"""
        return await self.process_message(user_id, prompt)

    async def fund_overview(self, user_id: str) -> str:
        """Provide a quick fund status overview."""
        checklist_text = legal_checklist_report(LEGAL_CHECKLIST)
        prompt = f"""ファンドの現状サマリーを提供してください。
以下を含めてください:
1. ファンド設立進捗（法務チェックリストから）
2. ディールパイプライン状況（Drive検索で確認）
3. 本日優先すべきアクション3点

現在のチェックリスト:
{checklist_text}
"""
        return await self.process_message(user_id, prompt)
