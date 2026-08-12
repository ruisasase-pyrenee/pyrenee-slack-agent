"""
PE Fund Simulation Runner.

Runs a complete fund operation cycle without Slack/external MCPs.
Uses local file I/O to simulate Drive/Notion/HubSpot.

Outputs everything to simulation/outputs/ as markdown files.
"""

import os
import sys
import json
import asyncio
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import anthropic
from simulation.state import (
    DEALS, MA_TARGET, LPS, PORTFOLIO, LEGAL_STATUS, FUND_METRICS
)
from config.fund_config import FUND_CONFIG, DEAL_SCREENING_CRITERIA, VALUE_CREATION_PLAYBOOK

OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

CLIENT = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# Use sonnet-4-6 for most tasks, opus-4-7 only for deep IC analysis
MODEL_FAST = "claude-sonnet-4-6"
MODEL_DEEP = "claude-opus-4-7"

SEPARATOR = "─" * 70


def save(filename: str, content: str) -> Path:
    path = OUTPUT_DIR / filename
    path.write_text(content, encoding="utf-8")
    return path


def ask(prompt: str, system: str = "", model: str = MODEL_FAST, max_tokens: int = 4096) -> str:
    msgs = [{"role": "user", "content": prompt}]
    kwargs = dict(model=model, max_tokens=max_tokens, messages=msgs)
    if system:
        kwargs["system"] = system
    r = CLIENT.messages.create(**kwargs)
    return r.content[0].text


def section(title: str):
    print(f"\n{SEPARATOR}")
    print(f"  {title}")
    print(SEPARATOR)


def step(msg: str):
    print(f"  ▶ {msg}")


def done(msg: str, path: Path = None):
    loc = f" → {path.name}" if path else ""
    print(f"  ✅ {msg}{loc}")


CEO_SYSTEM = f"""あなたはPyrenee Capital I（日本の5B JPYグロースエクイティファンド）の
自律型最高投資責任者（CIO）です。

ファンドテーゼ: {FUND_CONFIG['thesis']}
チェックサイズ: {FUND_CONFIG['focus']['check_size_min_mn_jpy']}〜{FUND_CONFIG['focus']['check_size_max_mn_jpy']}百万円
ターゲットIRR: {FUND_CONFIG['focus']['target_irr']}

判断は明確に。結論を先に。数字に基づいて話す。"""


# ═══════════════════════════════════════════════════════════════════════════════
# CYCLE 1: MORNING BRIEFING
# ═══════════════════════════════════════════════════════════════════════════════

def run_morning_briefing() -> str:
    section("🌅  CYCLE 1 / 朝次ブリーフィング")
    step("パイプライン・LP・法務を統合してブリーフィング生成中...")

    legal_summary = _legal_summary()
    deal_summary = _deal_pipeline_summary()
    lp_summary = _lp_pipeline_summary()
    portfolio_summary = _portfolio_summary()

    prompt = f"""今日（2026年5月27日 水曜日）のPyrenee Capital朝次ブリーフィングを作成してください。

## 投資パイプライン
{deal_summary}

## LPパイプライン
{lp_summary}

## ポートフォリオ
{portfolio_summary}

## 法務・コンプライアンス
{legal_summary}

---

以下の形式で朝次ブリーフィングを作成してください。
Ruiが朝一番で読む。「今日何をすべきか」が30秒でわかる内容に。

# 🌅 Pyrenee Capital 朝次ブリーフ
**2026年5月27日（水曜日）**

## ⚡ 今日の最優先3タスク
[「〜を検討」は不可。「誰に・何を・いつまでに」まで落とす]

## 🚨 見逃せないアラート
[緊急度高いもの。放置するとダメなやつだけ]

## 📊 ファンドスナップショット
[数字で見せる。5行以内]

## 🎯 投資パイプライン
[各案件の現状と今日やること]

## 🤝 LP進捗
[コミット済み額・ファーストクローズ達成率・今週のアクション]

## ⚖️ 法務
[今週期限のタスクと誰が動くべきか]

## 💼 ポートフォリオ
[要注意事項のみ]

---
*Good morning, Rui. 今日も前に進もう。*
"""
    result = ask(prompt, CEO_SYSTEM)
    path = save("01_morning_briefing.md", result)
    done("朝次ブリーフィング生成完了", path)
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# CYCLE 2: DEAL SCREENING × 3
# ═══════════════════════════════════════════════════════════════════════════════

def run_deal_screening() -> list[dict]:
    section("🔍  CYCLE 2 / ディールスクリーニング × 3社")

    criteria = DEAL_SCREENING_CRITERIA
    quant = criteria["quantitative"]
    must = "\n".join(f"- {c}" for c in criteria["must_have"])
    flags = "\n".join(f"- {c}" for c in criteria["red_flags"])

    results = []
    for deal in DEALS:
        step(f"スクリーニング中: {deal['company']}...")

        prompt = f"""以下の会社を投資基準に照らしてスクリーニングし、詳細メモと採点を出してください。

## Pyrenee Capital 投資基準
定量: ARR {quant['arr_min_mn_jpy']}M+、成長率 {quant['growth_yoy_min_pct']}%+YoY、粗利 {quant['gross_margin_min_pct']}%+、NRR {quant['nrr_min_pct']}%+
必須条件:
{must}
レッドフラグ:
{flags}

## 対象会社
{deal['description']}

---

以下の形式でスクリーニングメモを作成してください:

# スクリーニングメモ: {deal['company']}
**作成日**: 2026年5月27日 ｜ **作成者**: Pyrenee Capital ｜ **機密**

## 📌 一言判断
[1〜2行。投資するかどうか。根拠付き。迷わず書く]

## 会社概要
[表形式で主要項目]

## ビジネスモデルとプロダクト
[コアバリュー、競合との違い]

## 財務ハイライト
[表形式。ARR、成長率、粗利、NRR、ランウェイ]

## 投資基準 適合チェック
[各必須条件を ✅/⚠️/❌ で評価し根拠を書く]

## レッドフラグ確認
[各レッドフラグを ✅クリア/⚠️要確認/❌ヒット で評価]

## リスク上位3点と対応策

## 投資ストラクチャー案
[投資額、持株比率、バリュエーション根拠]

## 判断と次のアクション
**判断**: DD進行 / ウォッチリスト / Pass（どれか）
**スコア**: X/10
**次のアクション**: [具体的に3つ]
"""
        memo = ask(prompt, CEO_SYSTEM, model=MODEL_FAST, max_tokens=3000)

        # Score extraction prompt
        score_prompt = f"""以下のスクリーニングメモから投資スコアと判断を抽出して、JSONのみを返してください（他のテキスト不要）:

{memo}

形式:
{{"company": "会社名", "score": 数値, "verdict": "dd_proceed|watchlist|pass", "rationale": "1文"}}"""
        score_raw = ask(score_prompt, model=MODEL_FAST, max_tokens=200)

        try:
            import re
            j = re.search(r'\{.*\}', score_raw, re.DOTALL)
            score_data = json.loads(j.group()) if j else {}
        except Exception:
            score_data = {}

        filename = f"02_screening_{deal['company'].replace(' ', '_')}.md"
        path = save(filename, memo)

        verdict = score_data.get("verdict", "?")
        score = score_data.get("score", "?")
        emoji = {"dd_proceed": "✅", "watchlist": "⚠️", "pass": "❌"}.get(verdict, "❓")
        done(f"{deal['company']}: {score}/10 {emoji} {verdict}", path)

        results.append({
            "deal": deal,
            "memo": memo,
            "score": score_data,
            "path": path,
        })

    return results


# ═══════════════════════════════════════════════════════════════════════════════
# CYCLE 3: IC MEMO (Top deal from screening)
# ═══════════════════════════════════════════════════════════════════════════════

def run_ic_memo(screening_results: list[dict]) -> str:
    section("📄  CYCLE 3 / IC メモ作成（最高スコア案件）")

    # Pick the highest score
    best = max(
        screening_results,
        key=lambda r: r["score"].get("score", 0) if isinstance(r["score"].get("score"), (int, float)) else 0
    )
    company = best["deal"]["company"]
    step(f"ICメモ作成: {company}（スクリーニングスコア: {best['score'].get('score', '?')}/10）")

    prompt = f"""以下のスクリーニングリサーチをもとに、投資委員会（IC）向けの詳細投資メモを作成してください。
機関投資家（LP）が読んでも納得する水準で。

## スクリーニングメモ（既存調査）
{best['memo']}

## 会社詳細情報
{best['deal']['description']}

---

# 投資委員会メモ: {company}
**日付**: 2026年5月27日 ｜ **機密 - 投資委員会限り**

## 投資推奨サマリー
| 項目 | 内容 |
|------|------|
| 推奨 | 投資実行 / 見送り |
| 投資額 | X百万円 |
| 持株比率（投資後） | XX% |
| Pre-money | X億円 |
| 期待IRR (Base) | XX% |
| 期待MOIC (Base) | Xx |

## 1. 投資テーゼ（なぜ今、なぜこの会社か）

## 2. 市場分析
### TAM/SAM（根拠付き）
### 競合マップと差別化

## 3. ビジネスモデル深掘り
### 収益構造とユニットエコノミクス
### NRRのドライバー

## 4. チーム評価

## 5. 財務分析
### 過去実績と成長トレンド
### 3ヶ年シナリオ（Bull/Base/Bear）

## 6. バリュエーション
### 類似上場企業マルチプル比較（3社以上）
### バリュエーション結論

## 7. リターンシナリオ
| シナリオ | 前提 | IRR | MOIC |
|---------|------|-----|------|
| Bull | | | |
| Base | | | |
| Bear | | | |

## 8. リスクと対応策
（重要度・確率・ミティゲーションを表で）

## 9. バリューアッドプラン
### 投資後100日計画
### 中期価値創造施策

## 10. エグジット戦略

## 11. 投資条件（主要Term Sheet条件）

---
*本メモはPyrenee Capital投資委員会用資料です*
"""
    memo = ask(prompt, CEO_SYSTEM, model=MODEL_DEEP, max_tokens=6000)
    path = save(f"03_ic_memo_{company.replace(' ', '_')}.md", memo)
    done(f"ICメモ完成: {company}", path)
    return memo


# ═══════════════════════════════════════════════════════════════════════════════
# CYCLE 4: M&A TARGET ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

def run_ma_analysis() -> str:
    section("🏭  CYCLE 4 / M&A 事業承継ターゲット分析")
    step(f"分析中: {MA_TARGET['company']}...")

    prompt = f"""以下の事業承継型M&A候補について、詳細な投資・買収戦略メモを作成してください。

## 対象会社
{MA_TARGET['description']}

## Pyrenee Capitalの Buy-and-Build テーゼ
既存の優良ソフトウェア会社を買収し、AI機能追加 + クラウドSaaS化 + 隣接領域展開で価値を3〜5倍にする。

---

# M&A 投資メモ: {MA_TARGET['company']}
**作成日**: 2026年5月27日 ｜ **機密**

## なぜこの会社か（Investment Thesis）

## 企業概要と現状分析
### 収益構造と顧客基盤の強み
### 経営課題（後継者問題含む）

## 買収後の価値創造シナリオ
### Phase 1（0〜12ヶ月）: 安定化と関係構築
### Phase 2（12〜36ヶ月）: AI機能追加・SaaS化
### Phase 3（36〜60ヶ月）: 拡張とエグジット準備

## 財務モデル
### 現状: 売上・EBITDA・バリュエーション
### 買収後シナリオ（ARR転換後）
### リターン試算（IRR/MOIC）

## バリュエーション
### 現状評価（EV/Revenue、EV/EBITDA）
### 希望売値の根拠と交渉余地

## アプローチ戦略
### 菊池社長へのメッセージング（後継者問題に寄り添う）
### 初回コンタクト方法
### タイムライン（6ヶ月でクローズ目標）

## リスクと対応
### エンジニア・顧客関係の維持
### PMI（統合後経営）のポイント

## 結論とネクストアクション
"""
    result = ask(prompt, CEO_SYSTEM, model=MODEL_FAST, max_tokens=4000)
    path = save("04_ma_analysis_菊池建設システム.md", result)
    done(f"M&A分析完了: {MA_TARGET['company']}", path)
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# CYCLE 5: LP RELATIONSHIP MANAGEMENT
# ═══════════════════════════════════════════════════════════════════════════════

def run_lp_management() -> dict[str, str]:
    section("🤝  CYCLE 5 / LP 関係管理（5社全件処理）")

    outputs = {}
    for lp in LPS:
        step(f"処理中: {lp['org']} ({lp['status']})")

        if lp["status"] == "meeting_scheduled":
            # Pre-meeting prep brief
            prompt = f"""来週のLP面談に向けたプレップブリーフを作成してください。

LP情報:
- 機関名: {lp['org']}
- 担当者: {lp['contact']}
- 面談日: {lp['meeting_date']}
- 背景: {lp['notes']}

以下を含む面談準備メモ（1ページ）:
1. この面談で達成したいゴール（具体的な1つのアクション）
2. 相手の関心事とPyrenee Capitalとの接点
3. 想定Q&Aトップ5（難しい質問ほど想定する）
4. 絶対に触れてはいけないNG事項
5. 面談後のネクストステップ案"""

        elif lp["status"] == "met":
            # Follow-up email draft
            days_since = 12 if lp["org"] == "Sequoia Heritage（アジア枠）" else 12
            prompt = f"""LP面談後のフォローアップメールを起草してください。

LP: {lp['org']} / {lp['contact']}
面談日: {lp['meeting_date']}
背景: {lp['notes']}

要件:
- 面談から{days_since}日経過している（少し遅れたが自然な謝罪を添える）
- 件名は具体的で開封率が高いもの
- 本文は3段落以内（長いメールは読まれない）
- 具体的なネクストアクションを1つ提案して終わる
- プロフェッショナルだが温かいトーン

件名:
本文:"""

        elif lp["status"] == "intro_sent":
            # Follow-up for no-reply
            prompt = f"""返信がないLPへのフォローアップメールを起草してください。

LP: {lp['org']} / {lp['contact']}
最初のメール送付: 3日前
背景: {lp['notes']}

要件:
- 押しつけがましくない、自然なフォローアップ
- 相手に「読んでみよう」と思わせる新しい情報や視点を1つ加える
- 3行以内でコンパクトに
- 返信しやすい一言で締める"""

        elif lp["status"] == "prospect":
            # First outreach
            prompt = f"""まだコンタクトしていないLP候補への最初のアウトリーチメールを起草してください。

LP: {lp['org']} / {lp['contact']}
属性: {lp['type']}
チケット想定: {lp['ticket_mn_jpy']}百万円
背景: {lp['notes']}

Pyrenee Capital概要:
- ファンド名: {FUND_CONFIG['name']}
- テーゼ: {FUND_CONFIG['thesis']}
- ターゲットサイズ: {FUND_CONFIG['target_size_bn_jpy']}B JPY
- ターゲットIRR: {FUND_CONFIG['focus']['target_irr']}

要件:
- 件名: 相手の関心に刺さるもの（汎用的な「ご挨拶」は不可）
- 段落1: なぜこのLPに今連絡したか（相手の最近の動きを踏まえる）
- 段落2: なぜPyrenee Capitalが他のファンドと違うか
- 段落3: 具体的なネクストアクション（30分のzoomを提案）
- 全体: 3段落・300字以内

件名:
本文:"""

        result = ask(prompt, CEO_SYSTEM, model=MODEL_FAST, max_tokens=1500)
        key = lp["org"]
        outputs[key] = result

        # Determine action type for display
        action_map = {
            "meeting_scheduled": "面談プレップメモ",
            "met": "フォローアップメール下書き",
            "intro_sent": "リマインダーメール下書き",
            "prospect": "初回アウトリーチメール下書き",
        }
        action = action_map.get(lp["status"], "ドキュメント")

        filename = f"05_lp_{lp['org'].replace(' ', '_').replace('（', '_').replace('）', '')}.md"
        content = f"# LP: {lp['org']}\nステータス: {lp['status']}\n\n{result}"
        path = save(filename, content)
        done(f"{lp['org']}: {action}", path)

    return outputs


# ═══════════════════════════════════════════════════════════════════════════════
# CYCLE 6: PORTFOLIO ALERT SCAN
# ═══════════════════════════════════════════════════════════════════════════════

def run_portfolio_scan() -> str:
    section("📊  CYCLE 6 / ポートフォリオ早期警戒スキャン")
    step("2社の最新データを分析中...")

    portfolio_text = ""
    for co in PORTFOLIO:
        portfolio_text += f"""
## {co['company']} ({co['sector']})
投資日: {co['invested_date']} / 投資額: {co['investment_mn_jpy']}百万円 / 持株: {co['ownership_pct']}%
ARR: {co['last_arr_mn_jpy']}億円 / 成長率: {co['last_arr_growth_yoy']}%YoY / NRR: {co['last_nrr']}%
ランウェイ: {co['cash_runway_months']}ヶ月
最新状況:
{co['recent_updates']}
"""

    prompt = f"""ポートフォリオの早期警戒スキャンを実行してください。
投資先2社の最新データを分析し、Ruiが今日動くべきアクションを特定してください。

{portfolio_text}

---

# ポートフォリオ早期警戒スキャン
**2026年5月27日 ｜ 機密**

## 総合判断

各社のアラートレベル（🔴緊急/🟠要注意/🟡ウォッチ/✅正常）と理由を明示する。

## MedRoute株式会社
### アラートレベル & 根拠
### 検出したリスクシグナル
### 推奨アクション（誰が/何を/いつまでに）

## LogiPath AI株式会社
### アラートレベル & 根拠
### 成長機会のシグナル
### 推奨アクション

## 統合ビュー
### ポートフォリオKPIサマリー
### 次のBoard会議までにやること
### 今後6ヶ月の重要マイルストーン
"""
    result = ask(prompt, CEO_SYSTEM, model=MODEL_FAST, max_tokens=3000)
    path = save("06_portfolio_alert_scan.md", result)
    done("ポートフォリオスキャン完了", path)
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# CYCLE 7: LEGAL COMPLIANCE REVIEW
# ═══════════════════════════════════════════════════════════════════════════════

def run_legal_review() -> str:
    section("⚖️  CYCLE 7 / 法務・コンプライアンスレビュー")
    step("全25タスクを優先度分析中...")

    status_icon = {"pending": "⬜", "in_progress": "🔄", "completed": "✅", "blocked": "🚫"}
    priority_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡"}

    checklist_text = ""
    phase_labels = {
        "fund_formation": "フェーズ1: ファンド設立",
        "fundraising": "フェーズ2: ファンドレイズ",
        "investment_ops": "フェーズ3: 投資オペレーション",
    }
    for phase, tasks in LEGAL_STATUS.items():
        done_count = sum(1 for t in tasks if t["status"] == "completed")
        checklist_text += f"\n### {phase_labels[phase]} ({done_count}/{len(tasks)}完了)\n"
        for t in tasks:
            s = status_icon.get(t["status"], "❓")
            p = priority_icon.get(t["priority"], "")
            note = f"（{t.get('note', '')}）" if t.get("note") else ""
            checklist_text += f"{s} {p} {t['task']}{note}\n"

    prompt = f"""以下のファンド法務チェックリストを確認し、今週・今月の優先アクションプランを作成してください。

{checklist_text}

---

# 法務・コンプライアンス レビュー
**2026年5月27日 ｜ 機密**

## 全体進捗サマリー
[フェーズ別の完了率と達成見込み]

## 🔴 今週必ず動かすべきタスク（3つまで）
[タスク名・担当・期限・具体的アクション]

## 🟠 今月中のタスク

## ⚠️ ブロッカー & リスク
[このまま放置するとどうなるか]

## 📅 マイルストーン
[LPSファンド設立・第二種金商業登録・ファーストクローズの見込み日]

## アドバイス
[優先度付けの根拠と、Ruiが今日1つだけやるとしたら何か]
"""
    result = ask(prompt, CEO_SYSTEM, model=MODEL_FAST, max_tokens=2500)
    path = save("07_legal_review.md", result)
    done("法務レビュー完了", path)
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# CYCLE 8: WEEKLY CEO REPORT
# ═══════════════════════════════════════════════════════════════════════════════

def run_weekly_report(
    briefing: str,
    screening_results: list[dict],
    lp_outputs: dict,
    portfolio_scan: str,
    legal_review: str,
) -> str:
    section("📋  CYCLE 8 / 週次CEOレポート（全サイクル統合）")
    step("全サイクルの結果を統合してレポート生成中...")

    screening_summary = "\n".join([
        f"- {r['deal']['company']}: {r['score'].get('score', '?')}/10 → {r['score'].get('verdict', '?')}"
        for r in screening_results
    ])
    lp_summary = "\n".join([f"- {org}: アクション完了" for org in lp_outputs])

    prompt = f"""今週（2026年5月27日週）のPyrenee Capital週次CEOレポートを作成してください。
Ruiが週末に読んで「今週何が起きたか、来週何をすべきか」を把握できるもの。

## 今週の活動サマリー
スクリーニング完了:
{screening_summary}

LP管理:
{lp_summary}

ポートフォリオスキャン: 完了（2社）
法務レビュー: 完了（25タスク）

---

# Pyrenee Capital 週次CEOレポート
**2026年5月27日週 ｜ 機密**

## 今週のハイライト（3点）

## 投資パイプライン進捗
### 今週スクリーニングした案件と判断
### パイプライン全体の健全性

## LP進捗
### コミット状況（目標: 2B JPY）
### 来週のキーアクション

## ポートフォリオ
### 今週の重要動向
### 要対応アクション

## 法務・コンプライアンス
### 今週の進捗
### 来週の優先タスク

## 来週の最優先アクション TOP3
1.
2.
3.

## 数字で見る今週
| KPI | 値 | 目標 | 評価 |
|-----|-----|------|------|
| コミット資本 | 550M JPY | 2,000M JPY | 28% |
| スクリーニング案件数（累計） | | | |
| LP面談数（今月） | | | |
| 法務タスク完了率 | | | |

---
*Weekly report generated by Pyrenee Capital Autonomous Fund Agent*
"""
    result = ask(prompt, CEO_SYSTEM, model=MODEL_FAST, max_tokens=3000)
    path = save("08_weekly_ceo_report.md", result)
    done("週次CEOレポート完成", path)
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _legal_summary() -> str:
    total = sum(len(v) for v in LEGAL_STATUS.values())
    done_count = sum(1 for v in LEGAL_STATUS.values() for t in v if t["status"] == "completed")
    in_prog = sum(1 for v in LEGAL_STATUS.values() for t in v if t["status"] == "in_progress")
    pending = sum(1 for v in LEGAL_STATUS.values() for t in v if t["status"] == "pending")
    critical_pending = [
        t["task"] for v in LEGAL_STATUS.values()
        for t in v if t["status"] in ("pending", "in_progress") and t["priority"] == "critical"
    ]
    return (
        f"全{total}タスク中 完了:{done_count} 進行中:{in_prog} 未着手:{pending}\n"
        f"Critical未完了: {', '.join(critical_pending[:4])}"
    )


def _deal_pipeline_summary() -> str:
    stages = {}
    for d in DEALS:
        stages.setdefault(d["stage"], []).append(d["company"])
    return "\n".join(f"- {s}: {', '.join(cos)}" for s, cos in stages.items())


def _lp_pipeline_summary() -> str:
    committed = sum(lp["ticket_mn_jpy"] for lp in LPS if lp["status"] in ("committed",))
    target = FUND_METRICS["first_close_target_mn_jpy"]
    lines = [f"コミット済: {committed}M / 目標: {target}M JPY ({committed/target*100:.0f}%)"]
    for lp in LPS:
        lines.append(f"- {lp['org']} ({lp['status']}, ~{lp['ticket_mn_jpy']}M JPY)")
    return "\n".join(lines)


def _portfolio_summary() -> str:
    lines = []
    for co in PORTFOLIO:
        lines.append(
            f"- {co['company']}: ARR {co['last_arr_mn_jpy']}億 / {co['last_arr_growth_yoy']}%YoY / NRR {co['last_nrr']}% / ランウェイ {co['cash_runway_months']}ヶ月"
        )
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def run_simulation():
    print(f"\n{'═'*70}")
    print(f"  🏦 PYRENEE CAPITAL - FULL FUND SIMULATION")
    print(f"  2026年5月27日 ｜ シミュレーション開始")
    print(f"{'═'*70}")

    # Run all 8 cycles
    briefing = run_morning_briefing()
    screening = run_deal_screening()
    ic_memo = run_ic_memo(screening)
    ma = run_ma_analysis()
    lp_outputs = run_lp_management()
    portfolio = run_portfolio_scan()
    legal = run_legal_review()
    weekly = run_weekly_report(briefing, screening, lp_outputs, portfolio, legal)

    # Final summary
    section("🎯  シミュレーション完了")
    print(f"\n  生成されたファイル ({OUTPUT_DIR}):\n")
    for f in sorted(OUTPUT_DIR.glob("*.md")):
        size_kb = f.stat().st_size / 1024
        print(f"    📄 {f.name:<55} {size_kb:>5.1f} KB")

    total_size = sum(f.stat().st_size for f in OUTPUT_DIR.glob("*.md")) / 1024
    print(f"\n  合計: {len(list(OUTPUT_DIR.glob('*.md')))}ファイル / {total_size:.1f} KB")
    print(f"\n{'═'*70}")
    print(f"  Pyrenee Capital is operational. 🚀")
    print(f"{'═'*70}\n")


if __name__ == "__main__":
    run_simulation()
