"""
Autonomous Fund Manager - Claude as CEO.

This agent runs on a schedule WITHOUT human input.
It makes decisions, takes actions, and reports results.

Philosophy:
- Remove human bias from investment decisions
- Consistent application of criteria, every time
- 24/7 attention (no "I missed that email")
- Every decision logged with explicit rationale
- Speed as a competitive advantage (8-week deal cycle)

Scheduled runs:
  08:00 JST daily  → morning_cycle()  - priorities + pipeline review
  18:00 JST daily  → evening_cycle()  - deal signals + LP touches
  Monday 09:00     → weekly_cycle()   - full pipeline review + IC prep
"""

import anthropic
import json
from datetime import datetime, timedelta
from typing import Any

from config.fund_config import (
    FUND_CONFIG,
    DEAL_SCREENING_CRITERIA,
    DEAL_SIGNAL_SOURCES,
    MA_TARGET_PROFILES,
    LEGAL_CHECKLIST,
    VALUE_CREATION_PLAYBOOK,
)
from tools.registry import get_all_tools, execute
from agents.orchestrator import _format_legal_checklist

CLIENT = anthropic.Anthropic()
TOOLS = get_all_tools()

# ── CEO System Prompt ────────────────────────────────────────────────────────

CEO_PROMPT = f"""あなたはPyrenee Capitalの自律型最高投資責任者（CIO）です。
誰かに聞かれるのを待たず、自分で判断し、自分でアクションを取ります。

## 経営原則
1. **速度が武器**: ファーストミーティングから8週間でterm sheet。競合より速く動く
2. **基準の一貫性**: チャーミングな創業者でも基準を外れたらPassと書く。例外を作らない
3. **透明な意思決定**: 全ての判断にスコアと根拠を記録する
4. **プロアクティブ**: 聞かれる前にやる。LPフォローアップは3営業日以内
5. **ポートフォリオファースト**: 既存投資先を守ることが新規投資より常に優先

## 毎日必ずやること
- パイプラインの各案件に具体的なネクストアクションを1つ割り当てる
- 3営業日以上触れていないLPをフラグする
- 法務タスクのうち今週期限のものを確認する
- 不審なシグナル（ポートフォリオのチャーン急増、競合の資金調達）を察知する

## ファンドKPI（これを常に頭に置く）
- ターゲットIRR: {FUND_CONFIG['focus']['target_irr']}
- ファーストクローズ: {FUND_CONFIG['first_close_target_bn_jpy']}B JPY
- 投資ペース: 年3-4件（焦らない、が止まらない）
- LP数: 最大20（小さく保つことで情報流出を防ぐ）

全てのドキュメントはDrive + Notionの両方に保存すること。
全ての新規案件はHubSpotに登録すること。
重要な判断はslack_send_alertでRuiに通知すること。"""


# ── Main scheduled cycles ─────────────────────────────────────────────────────

async def morning_cycle(mcp: dict | None = None) -> dict[str, str]:
    """
    Daily 08:00 JST. Returns {briefing, actions_taken}.

    1. Review legal tasks → flag overdue
    2. Review deal pipeline → assign next actions
    3. Review LP pipeline → flag stale relationships
    4. Generate briefing + send to Slack
    """
    today = datetime.now().strftime("%Y年%m月%d日（%A）")
    legal_text = _format_legal_checklist(LEGAL_CHECKLIST)

    prompt = f"""今日（{today}）の朝次マネジメントサイクルを実行してください。

## 今日の法務状況
{legal_text}

## 実行手順（全て自律的に実行する）:

1. crm_get_pipeline で deals パイプラインを確認
2. crm_get_pipeline で lps パイプラインを確認
3. calendar_get_week で今週のカレンダーを確認
4. 以下のブリーフィングを作成:

# 🌅 朝次ブリーフ {today}

## ⚡ 今日の最優先3タスク
[具体的なアクション。「〜を検討する」は不可。「〜に電話する」「〜のメールを送る」まで落とす]

## 📊 パイプラインスナップショット
[各ステージの案件数と動き]

## 🚨 フラグ
[3営業日以上動いていないLP・案件、今週期限の法務タスク]

## 📅 今週の重要イベント
[面談・締切・IC予定]

---
*Pyrenee Capital Autonomous Morning Report*

5. ブリーフィングを drive_save で lp_relations/朝次ブリーフ_{today}.md として保存
6. slack_send_alert で #general チャンネルに送信（urgency: high）
"""
    result = await _run(prompt, "sonnet", mcp)
    return {"briefing": result, "timestamp": datetime.now().isoformat()}


async def evening_cycle(mcp: dict | None = None) -> dict[str, str]:
    """
    Daily 18:00 JST. Deal signal scan + LP follow-up drafts.

    1. Check for new deal signals
    2. Draft overdue LP follow-ups
    3. Update deal scores
    """
    today = datetime.now().strftime("%Y年%m月%d日")

    prompt = f"""夕次サイクルを実行してください（{today} 18:00）。

## タスク

### 1. ディールシグナル確認
drive_search で「シグナル {today}」を検索し、新規案件フラグがないか確認。
notion_search で「新規案件」を検索。
見つかった案件があれば crm_add_deal で stage: sourced で登録。

### 2. LPフォローアップ確認
crm_get_pipeline で lps を確認。
status が met または meeting_scheduled で3営業日以上変化なしのLPを特定。
各LPについて gmail_draft でフォローアップメールを下書き作成。

### 3. 明日の準備
calendar_get_week で明日の予定を確認。
LP面談がある場合: notion_search でそのLPの情報を検索し、簡単なプレップメモを作成して drive_save。

完了後、実行したアクションのサマリーを返してください。"""
    result = await _run(prompt, "sonnet", mcp)
    return {"summary": result, "timestamp": datetime.now().isoformat()}


async def weekly_cycle(mcp: dict | None = None) -> dict[str, str]:
    """
    Monday 09:00 JST. Full pipeline review + IC prep + LP status.
    Uses opus for deeper analysis.
    """
    week_start = datetime.now().strftime("%Y年%m月%d日")

    prompt = f"""週次マネジメントレビューを実行してください（週始め: {week_start}）。

## 完全パイプラインレビュー

### 投資パイプライン
1. crm_get_pipeline deals を取得
2. 各ステージの案件を評価:
   - screening: 1週間以上止まっている → DD判断を下す（進める/Passする）
   - dd: 2週間以上止まっている → IC memo完成の目処を立てる
   - ic_review: IC開催日程を決める
   - term_sheet: 1週間以上止まっている → 弁護士を動かす

### LPパイプライン
3. crm_get_pipeline lps を取得
4. コミット向けの具体的アクションを1社ずつ割り当てる
5. ファーストクローズ達成率を計算して報告（目標: {FUND_CONFIG['first_close_target_bn_jpy']}B JPY）

### 法務・コンプライアンス
6. 今週期限タスクに担当と締切日を割り当てる

### IC準備
7. 今週IC提出予定の案件があれば notion_search で既存メモを確認
8. 不足情報があれば具体的なDD質問リストを作成

## 週次レポート作成
全項目完了後、週次レポートを作成して:
- drive_save → portfolio/週次レビュー_{week_start}.md
- notion_save_page → portfolio データベースに保存
- slack_send_alert → #general に「週次レビュー完了」を通知（urgency: medium）

判断基準: データが不足していても「確認待ち」で止めない。合理的仮定を置いて推奨アクションを出す。"""
    result = await _run(prompt, "opus", mcp)
    return {"weekly_report": result, "timestamp": datetime.now().isoformat()}


# ── Investment Decision Engine ────────────────────────────────────────────────

async def score_deal(
    company_info: str,
    mcp: dict | None = None,
) -> dict[str, Any]:
    """
    Autonomously score a deal against criteria.
    Returns structured decision: {score, verdict, rationale, next_action}.

    This is the heart of the bias-free investment process.
    """
    criteria = DEAL_SCREENING_CRITERIA
    quant = criteria["quantitative"]

    prompt = f"""以下の会社を投資基準に照らして採点し、明確な判断を出してください。

## 評価対象
{company_info}

## 定量基準
- ARR: {quant['arr_min_mn_jpy']}M JPY以上
- 成長率: {quant['growth_yoy_min_pct']}%+YoY
- 粗利率: {quant['gross_margin_min_pct']}%+
- NRR: {quant['nrr_min_pct']}%+

## 必須条件
{chr(10).join(f'- {c}' for c in criteria['must_have'])}

## レッドフラグ
{chr(10).join(f'- {c}' for c in criteria['red_flags'])}

## 評価 & アクション

以下のJSON形式で回答してください（テキストなし、JSONのみ）:

{{
  "company": "会社名",
  "score": 0-10の数値,
  "verdict": "dd_proceed" | "watchlist" | "pass",
  "criteria_scores": {{
    "arr_growth": 0-3,
    "business_model": 0-3,
    "team": 0-2,
    "market": 0-2
  }},
  "top_positives": ["強み1", "強み2"],
  "top_risks": ["リスク1", "リスク2"],
  "red_flags_triggered": ["該当するレッドフラグ"],
  "rationale": "判断理由を2-3文で",
  "next_action": "具体的なネクストアクション（誰が/何を/いつまでに）",
  "check_size_mn_jpy": 想定投資額の数値
}}"""

    result = await _run(prompt, "sonnet", mcp)

    # Parse JSON decision
    try:
        # Extract JSON from response
        import re
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            decision = json.loads(json_match.group())
        else:
            decision = {"raw": result, "parse_error": True}
    except json.JSONDecodeError:
        decision = {"raw": result, "parse_error": True}

    # Auto-save decision and register in CRM
    verdict = decision.get("verdict", "unknown")
    company = decision.get("company", "Unknown")
    score = decision.get("score", 0)

    save_content = f"""# 投資スコアリング: {company}
スコア: {score}/10
判断: {verdict}
作成: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}

## 詳細
{json.dumps(decision, ensure_ascii=False, indent=2)}
"""
    await execute("drive_save", {
        "title": f"[Score] {company} - {score}点 {verdict}",
        "content": save_content,
        "folder": "deal_pipeline",
    }, mcp)

    stage_map = {"dd_proceed": "dd", "watchlist": "watchlist", "pass": "closed_lost"}
    await execute("crm_add_deal", {
        "company_name": company,
        "stage": stage_map.get(verdict, "screening"),
        "notes": decision.get("rationale", ""),
    }, mcp)

    return decision


async def portfolio_alert_scan(
    portfolio_data: str,
    mcp: dict | None = None,
) -> str:
    """
    Scan portfolio for early warning signals.
    Called weekly. Flags issues before they become crises.
    """
    prompt = f"""ポートフォリオの早期警戒スキャンを実行してください。

## ポートフォリオデータ
{portfolio_data}

## 監視すべきシグナル（これを見る）
- NRRが前四半期比5pt以上悪化
- 主要顧客の解約・縮小
- エンジニア・営業の主要メンバー退職
- 競合の大型資金調達（3ヶ月以内）
- ARR成長率の2Q連続鈍化
- 資金残高18ヶ月割れ（要ブリッジ）
- 創業者間の不和の兆候

## 出力
各社のアラートレベル（🔴緊急/🟠要注意/🟡ウォッチ/✅正常）と推奨アクション。
緊急・要注意の案件は slack_send_alert で #portfolio-alerts チャンネルに送信。"""

    return await _run(prompt, "sonnet", mcp)


# ── LP Relationship Engine ────────────────────────────────────────────────────

async def lp_relationship_cycle(
    lp_list: list[dict],
    mcp: dict | None = None,
) -> str:
    """
    Manages the full LP relationship lifecycle autonomously.
    Drafts touchpoints, flags stale relationships, tracks to close.
    """
    lp_text = json.dumps(lp_list, ensure_ascii=False, indent=2)
    today = datetime.now().strftime("%Y年%m月%d日")

    prompt = f"""LP関係管理サイクルを実行してください（{today}）。

## LPリスト
{lp_text}

## 実行手順

1. **ステータス別仕分け**:
   - prospect: まだコンタクトしていない → アウトリーチメール下書き作成
   - intro_sent: 返信なし3営業日+ → フォローアップメール下書き
   - meeting_scheduled: 面談3営業日以内 → プレップメモ作成
   - met: フォローアップ未送信 → サンキューメール + 資料送付
   - dd: 質問への回答が必要 → 回答ドキュメント整備

2. **各LPアクション**:
   - gmail_draft でメール下書き作成
   - crm_add_lp でステータス更新

3. **LP進捗サマリー**:
   - コミット済み: X億円
   - 目標: {FUND_CONFIG['first_close_target_bn_jpy']}B JPY
   - 達成率: X%
   - ファーストクローズ達成見込み: X週間後

サマリーを drive_save で lp_relations/LP進捗_{today}.md として保存。"""

    return await _run(prompt, "sonnet", mcp)


# ── Internal runner ──────────────────────────────────────────────────────────

async def _run(prompt: str, model: str, mcp: dict | None) -> str:
    """Single-purpose agentic loop for fund manager tasks."""
    from agents.orchestrator import MODEL_MAP
    mcp = mcp or {}
    messages = [{"role": "user", "content": prompt}]

    while True:
        response = CLIENT.messages.create(
            model=MODEL_MAP.get(model, MODEL_MAP["sonnet"]),
            max_tokens=8192 if model == "opus" else 4096,
            system=CEO_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return ""

        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = await execute(block.name, block.input, mcp)
                    results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })
            messages.append({"role": "user", "content": results})
            continue

        break

    return "実行エラー"
