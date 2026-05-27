"""
Document templates for PE fund workflows.
"""

from datetime import datetime


def screening_memo_prompt(company_info: str, fund_config: dict, criteria: dict) -> str:
    sectors = ", ".join(fund_config["focus"]["sectors"])
    must_have = "\n".join(f"- {c}" for c in criteria["must_have"])
    red_flags = "\n".join(f"- {c}" for c in criteria["red_flags"])
    check_min = fund_config["focus"]["check_size_min_mn_jpy"]
    check_max = fund_config["focus"]["check_size_max_mn_jpy"]
    target_irr = fund_config["focus"]["target_irr"]

    return f"""以下の会社について、PE/グロースエクイティ投資家として詳細なスクリーニングメモを作成してください。

## ファンド投資基準
- フォーカスセクター: {sectors}
- チェックサイズ: {check_min}M〜{check_max}M JPY
- ターゲットIRR: {target_irr}
- 必須条件:
{must_have}
- レッドフラグ:
{red_flags}

## 会社情報
{company_info}

## 出力形式（以下の構成でメモを作成）

# スクリーニングメモ: [会社名]
作成日: {datetime.now().strftime('%Y年%m月%d日')}
作成者: Pyrenee Capital

## 1. Executive Summary
[2-3行で投資判断の結論]

## 2. 会社概要
- 会社名:
- 設立:
- 本社:
- 事業内容:
- ステージ:
- 最新資金調達:
- バリュエーション:

## 3. ビジネスモデル
[収益モデル、顧客セグメント、主要KPI]

## 4. 市場機会
- TAM (全体市場):
- SAM (獲得可能市場):
- 市場成長率:
- 競合環境:

## 5. 競争優位性
[プロダクト、技術、ネットワーク効果、参入障壁]

## 6. 財務サマリー
| 指標 | 数値 |
|------|------|
| ARR/売上 | |
| YoY成長率 | |
| 粗利率 | |
| 営業赤字/黒字 | |
| キャッシュランウェイ | |

## 7. 投資基準適合性
| 基準 | 評価 | コメント |
|------|------|---------|
| 必須条件1 | ✅/⚠️/❌ | |
| 必須条件2 | ✅/⚠️/❌ | |
| レッドフラグ確認 | ✅/⚠️/❌ | |

## 8. リスク要因
1. [最重要リスク]
2. [リスク2]
3. [リスク3]

## 9. 投資ストラクチャー案
- 投資額: M JPY
- 持株比率:
- バリュエーション前提:
- ラウンド種類:

## 10. 判断 & ネクストアクション
**判断**: [Pass / DD進行 / ウォッチリスト]
**理由**: [1-2行]
**ネクスト**: [具体的アクション & 担当 & 期限]

スコア: /10 (投資優先度)
"""


def ic_memo_prompt(company_info: str, screening_memo: str, fund_config: dict) -> str:
    return f"""以下の情報をもとに、投資委員会（IC）向けの詳細投資メモを作成してください。
プロフェッショナルなPEファンドのICメモ形式で、意思決定に必要な全情報を含めてください。

## ファンド基本情報
{fund_config}

## スクリーニングメモ（既存調査）
{screening_memo}

## 追加会社情報
{company_info}

## IC メモ出力形式

# 投資委員会メモ: [会社名]
機密 - 社外秘
作成日: {datetime.now().strftime('%Y年%m月%d日')}

## 投資推奨
**推奨**: [投資実行 / 見送り]
**投資額**: X億円
**投資後持株比率**: X%
**Pre-moneyバリュエーション**: X億円

---

## 1. 投資テーゼ（1ページサマリー）

## 2. 会社・事業詳細
### 2.1 事業概要
### 2.2 プロダクト
### 2.3 顧客・収益構造
### 2.4 GTM戦略

## 3. 市場分析
### 3.1 市場規模・成長性
### 3.2 競合マップ
### 3.3 差別化要因

## 4. チーム評価
### 4.1 経営陣プロフィール
### 4.2 チームの強み・ギャップ
### 4.3 採用計画

## 5. 財務分析
### 5.1 過去財務（P/L、B/S、CF）
### 5.2 財務モデル前提
### 5.3 3ヶ年予測
### 5.4 ユニットエコノミクス

## 6. バリュエーション
### 6.1 類似上場企業比較 (Comps)
### 6.2 類似取引事例 (Precedent Transactions)
### 6.3 DCF分析
### 6.4 バリュエーションサマリー

## 7. リターン分析
| シナリオ | Exit倍率 | IRR | MOIC |
|---------|---------|-----|------|
| Base | | | |
| Bull | | | |
| Bear | | | |

## 8. デューデリジェンス サマリー
### 8.1 ビジネスDD
### 8.2 財務DD
### 8.3 法務DD
### 8.4 残課題

## 9. リスク & ミティゲーション
| リスク | 重大度 | 確率 | ミティゲーション |
|-------|-------|------|----------------|

## 10. 投資条件
### 10.1 ストラクチャー
### 10.2 Term Sheet主要条件
### 10.3 CP条件

## 11. バリューアッドプラン
[投資後100日計画、価値創造施策]

## 12. エグジット戦略
[想定エグジットルート、バイヤー候補、タイムライン]

## 付録
"""


def lp_report_prompt(portfolio_data: str, period: str, fund_config: dict) -> str:
    return f"""以下のポートフォリオデータをもとに、LP（出資者）向けの定期報告書を作成してください。
プロフェッショナルかつ透明性の高いLP報告書を作成してください。

## ファンド: {fund_config['name']}
## 報告期間: {period}

## ポートフォリオデータ
{portfolio_data}

## LP報告書 出力形式

# {fund_config['name']} - LP Report
{period}
機密 - 出資者限り

## ファンドハイライト
[3-5点の主要トピック]

## 1. ファンドサマリー
| 指標 | 数値 |
|------|------|
| コミット総額 | |
| 投資実行額 | |
| 残余コミット | |
| ポートフォリオ社数 | |
| NAV (時価純資産) | |
| TVPI | |
| IRR (実現+未実現) | |

## 2. ポートフォリオ概況
[各社の進捗・KPI・ハイライト]

## 3. バリュエーション
[バリュエーション方法論と各社評価額]

## 4. 新規投資・フォローオン
[期間中の新規投資・追加投資]

## 5. エグジット・実現収益
[期間中のエグジット実績]

## 6. マーケット環境
[投資テーマ関連の市場動向]

## 7. ファンド運営
[チーム・組織・ファンドレイズ状況]

## 8. 次期の見通し
[投資パイプライン・重点施策]

## 付録: 財務諸表
"""


def legal_checklist_report(checklist: dict) -> str:
    """Generate a formatted legal compliance checklist report."""
    lines = ["# ファンド法務・コンプライアンス チェックリスト\n"]
    lines.append(f"最終更新: {datetime.now().strftime('%Y年%m月%d日')}\n")

    status_emoji = {
        "pending": "⬜",
        "in_progress": "🔄",
        "completed": "✅",
        "blocked": "🚫",
    }

    for phase, tasks in checklist.items():
        phase_labels = {
            "fund_formation": "## フェーズ1: ファンド設立",
            "fundraising": "## フェーズ2: ファンドレイズ",
            "investment": "## フェーズ3: 投資実行",
        }
        lines.append(f"\n{phase_labels.get(phase, phase)}\n")

        completed = sum(1 for t in tasks if t["status"] == "completed")
        lines.append(f"進捗: {completed}/{len(tasks)} 完了\n")

        for task in tasks:
            emoji = status_emoji.get(task["status"], "❓")
            priority = "🔴" if task["priority"] == "high" else "🟡"
            lines.append(f"{emoji} {priority} {task['task']}")

    return "\n".join(lines)
