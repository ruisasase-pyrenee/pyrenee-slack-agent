"""
PE Fund Orchestrator - Full-stack agentic loop.

This is the brain. It receives any request, decides which tools to use,
executes them in sequence, and returns a structured response.

Model selection:
- opus-4-7: Deep analysis (IC memos, complex screening, strategic decisions)
- sonnet-4-6: Fast tasks (status updates, simple questions, morning brief)
"""

import anthropic
from datetime import datetime
from typing import Literal

from config.fund_config import (
    FUND_CONFIG,
    DEAL_SCREENING_CRITERIA,
    DEAL_SIGNAL_SOURCES,
    MA_TARGET_PROFILES,
    LEGAL_CHECKLIST,
    VALUE_CREATION_PLAYBOOK,
)
from tools.registry import get_all_tools, execute
from templates.documents import (
    screening_memo_prompt,
    ic_memo_prompt,
    morning_briefing_prompt,
    deal_sourcing_prompt,
    ma_target_analysis_prompt,
    lp_pitch_email_prompt,
)

ModelType = Literal["opus", "sonnet"]

MODEL_MAP = {
    "opus": "claude-opus-4-7",
    "sonnet": "claude-sonnet-4-6",
}

SYSTEM_PROMPT = f"""あなたはPEファンド「{FUND_CONFIG['name']}」の専属AIエージェントです。
ファンドマネージャーのRui Sasaseを支援します。

## ファンドテーゼ
{FUND_CONFIG['thesis']}

## 投資基準
- フォーカスセクター: {', '.join(FUND_CONFIG['focus']['sectors_ranked'][:3])} など
- チェックサイズ: {FUND_CONFIG['focus']['check_size_min_mn_jpy']}〜{FUND_CONFIG['focus']['check_size_max_mn_jpy']}百万円
- ターゲットIRR: {FUND_CONFIG['focus']['target_irr']}

## あなたの仕事
1. **Deal Screening**: 案件を基準に照らし、スクリーニングメモをDriveに保存、HubSpotにパイプライン登録
2. **IC Memo作成**: 投資委員会向け詳細分析メモを作成
3. **法務管理**: ファンド設立に必要な法務タスクを追跡・優先度付け
4. **LP管理**: LP候補の追加、フォローアップドラフト、コミット追跡
5. **ポートフォリオ管理**: KPI追跡、LP報告書作成、バリューアッド施策管理
6. **市場調査**: セクター分析、M&Aターゲット発掘

## 行動原則
- ドキュメントは必ずDrive + Notionに保存する（両方）
- 新しい案件は必ずHubSpotに登録する
- 結論を先に言う。理由は後
- 不確実な情報は合理的仮定を明示した上で進む
- 「できない」より「こうすれば前に進める」を言う
- 日本語で答える。英語で聞かれたら英語で答える"""


class Orchestrator:
    def __init__(self, mcp_tools: dict | None = None):
        self.claude = anthropic.Anthropic()
        self.mcp = mcp_tools or {}
        self.tools = get_all_tools()
        self.history: dict[str, list] = {}

    # ── Public interface ────────────────────────────────────────────────────

    async def chat(self, user_id: str, message: str, model: ModelType = "sonnet") -> str:
        """General chat - routes to appropriate model."""
        self._push(user_id, "user", message)
        response = await self._loop(
            messages=self._tail(user_id, 20),
            model=model,
        )
        self._push(user_id, "assistant", response)
        return response

    async def screen_deal(self, user_id: str, company_info: str) -> str:
        """Full deal screening workflow. Saves to Drive + HubSpot."""
        prompt = screening_memo_prompt(company_info, FUND_CONFIG, DEAL_SCREENING_CRITERIA)
        prompt += "\n\n分析が完了したら:\n1. drive_saveでdeal_pipelineフォルダに保存\n2. notion_save_pageでdeal_researchデータベースに保存\n3. crm_add_dealでHubSpotに登録（stage: screening）"
        return await self.chat(user_id, prompt, model="opus")

    async def create_ic_memo(self, user_id: str, company_name: str) -> str:
        """IC memo - searches existing research first, then deep analysis."""
        prompt = f"""「{company_name}」のICメモを作成してください。

手順:
1. drive_searchで既存のスクリーニングメモを検索
2. notion_searchでも既存調査を検索
3. 見つかった情報 + 以下のテンプレートでICメモを作成
4. drive_saveでic_memosフォルダに保存
5. notion_save_pageでdeal_researchに保存

{ic_memo_prompt(company_name, '（検索した既存資料を参照）', FUND_CONFIG)}"""
        return await self.chat(user_id, prompt, model="opus")

    async def deal_sourcing_research(self, user_id: str, sector: str) -> str:
        """Deep sector research + M&A target identification."""
        prompt = deal_sourcing_prompt(sector, DEAL_SIGNAL_SOURCES)
        prompt += f"\n\n分析完了後:\n1. drive_saveでmarket_researchフォルダに「{sector}セクター調査_{datetime.now().strftime('%Y%m%d')}」として保存\n2. notion_save_pageでmarket_intelに保存"
        return await self.chat(user_id, prompt, model="opus")

    async def ma_strategy(self, user_id: str, profile_idx: int = 0) -> str:
        """M&A / buy-and-build target analysis."""
        profiles = MA_TARGET_PROFILES["profiles"]
        if profile_idx >= len(profiles):
            profile_idx = 0
        profile = profiles[profile_idx]
        prompt = ma_target_analysis_prompt(profile)
        prompt += f"\n\n分析後、drive_saveでmarket_researchに保存してください。"
        return await self.chat(user_id, prompt, model="opus")

    async def legal_status(self, user_id: str) -> str:
        """Legal checklist status + prioritized action plan."""
        checklist_text = _format_legal_checklist(LEGAL_CHECKLIST)
        prompt = f"""ファンドの法務タスクを確認し、今週優先すべきアクションをアドバイスしてください。

{checklist_text}

アドバイス後:
1. このチェックリストをdrive_saveでlegal_complianceに保存
2. notion_save_pageでlegal_tasksに保存"""
        return await self.chat(user_id, prompt, model="sonnet")

    async def lp_outreach_draft(self, user_id: str, lp_info: str) -> str:
        """Draft LP outreach email + add to HubSpot."""
        prompt = lp_pitch_email_prompt({"description": lp_info}, FUND_CONFIG)
        prompt += f"""

メール下書き後:
1. gmail_draftでメール下書きを作成
2. crm_add_lpでHubSpotにLP候補を登録（status: prospect）
3. drive_saveでlp_relationsに保存"""
        return await self.chat(user_id, prompt, model="sonnet")

    async def morning_briefing(self, user_id: str) -> str:
        """Generate daily proactive briefing. Called by scheduler."""
        today = datetime.now().strftime("%Y年%m月%d日")
        checklist_text = _format_legal_checklist(LEGAL_CHECKLIST)

        # Try to get live pipeline data from CRM
        deal_pipeline = "（HubSpot MCP接続後にリアルタイムデータ表示）"
        lp_pipeline = "（HubSpot MCP接続後にリアルタイムデータ表示）"
        calendar_events = "（Calendar MCP接続後に表示）"

        prompt = morning_briefing_prompt(
            today,
            deal_pipeline,
            lp_pipeline,
            checklist_text,
            calendar_events,
            FUND_CONFIG,
        )
        prompt += "\n\nブリーフィング完了後、drive_saveでlp_relationsフォルダに「朝次ブリーフ_{today}」として保存してください。"
        # Don't add to history - briefing is standalone
        return await self._loop([{"role": "user", "content": prompt}], model="sonnet")

    async def fund_overview(self, user_id: str) -> str:
        """Quick fund dashboard."""
        checklist_text = _format_legal_checklist(LEGAL_CHECKLIST)
        prompt = f"""ファンドの現状を簡潔にサマリーしてください:
1. 設立進捗（法務タスクから）
2. 投資パイプライン状況（CRM検索）
3. LP進捗（CRM検索）
4. 今日の優先アクション3点

{checklist_text}

サマリー前に crm_get_pipeline でdealsとlpsを確認してください。"""
        return await self.chat(user_id, prompt, model="sonnet")

    # ── Agentic loop ────────────────────────────────────────────────────────

    async def _loop(self, messages: list, model: ModelType = "sonnet") -> str:
        """Tool-use agentic loop. Runs until end_turn."""
        current = list(messages)

        while True:
            response = self.claude.messages.create(
                model=MODEL_MAP[model],
                max_tokens=8192 if model == "opus" else 4096,
                system=SYSTEM_PROMPT,
                tools=self.tools,
                messages=current,
            )

            if response.stop_reason == "end_turn":
                for block in response.content:
                    if hasattr(block, "text"):
                        return block.text
                return "（応答なし）"

            if response.stop_reason == "tool_use":
                current.append({"role": "assistant", "content": response.content})

                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = await execute(block.name, block.input, self.mcp)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })

                current.append({"role": "user", "content": tool_results})
                continue

            break

        return "エラー: 応答生成に失敗しました。"

    # ── History management ───────────────────────────────────────────────────

    def _push(self, uid: str, role: str, content: str) -> None:
        if uid not in self.history:
            self.history[uid] = []
        self.history[uid].append({"role": role, "content": content})

    def _tail(self, uid: str, n: int) -> list:
        return self.history.get(uid, [])[-n:]


# ── Helpers ─────────────────────────────────────────────────────────────────

def _format_legal_checklist(checklist: dict) -> str:
    status_icon = {"pending": "⬜", "in_progress": "🔄", "completed": "✅", "blocked": "🚫"}
    priority_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "⚪"}

    phase_labels = {
        "fund_formation": "フェーズ1: ファンド設立",
        "fundraising": "フェーズ2: ファンドレイズ",
        "investment_ops": "フェーズ3: 投資オペレーション",
    }

    lines = [f"# 法務チェックリスト ({datetime.now().strftime('%Y/%m/%d')})\n"]
    for phase, tasks in checklist.items():
        done = sum(1 for t in tasks if t["status"] == "completed")
        lines.append(f"\n## {phase_labels.get(phase, phase)} ({done}/{len(tasks)}完了)")
        for t in tasks:
            s = status_icon.get(t["status"], "❓")
            p = priority_icon.get(t["priority"], "")
            week = f" [W{t.get('week', '?')}]" if "week" in t else ""
            lines.append(f"{s} {p}{week} {t['task']}")

    return "\n".join(lines)
