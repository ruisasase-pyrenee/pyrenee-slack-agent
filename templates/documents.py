"""
Document templates for all PE fund workflows.
"""

from datetime import datetime


def screening_memo_prompt(company_info: str, fund_config: dict, criteria: dict) -> str:
    sectors = ", ".join(fund_config["focus"]["sectors_ranked"])
    must_have = "\n".join(f"- {c}" for c in criteria["must_have"])
    red_flags = "\n".join(f"- {c}" for c in criteria["red_flags"])
    quant = criteria["quantitative"]

    return f"""以下の会社について、プロのPEファンド投資家として詳細なスクリーニングメモを作成してください。

## Pyrenee Capital 投資基準
- フォーカス: {sectors}
- 定量基準: ARR {quant['arr_min_mn_jpy']}M+ / 成長率 {quant['growth_yoy_min_pct']}%+YoY / 粗利 {quant['gross_margin_min_pct']}%+ / NRR {quant['nrr_min_pct']}%+
- 必須条件:
{must_have}
- レッドフラグ:
{red_flags}

## 分析対象
{company_info}

---
以下の構成でスクリーニングメモを作成してください:

# スクリーニングメモ: [会社名]
**作成日**: {datetime.now().strftime('%Y年%m月%d日')}  **作成**: Pyrenee Capital  **機密**

## 📌 一言判断
[1-2行で投資するかどうか。理由付きで。迷わず書く]

## 会社概要
| 項目 | 内容 |
|------|------|
| 会社名 | |
| 設立年 | |
| 事業内容 | |
| ステージ | |
| 最終調達 | 金額 / ラウンド / 投資家 |
| バリュエーション | |
| 本社 | |

## ビジネスモデル
[収益モデル・顧客セグメント・主要KPI。プロダクトのコアバリューを1段落で]

## 市場機会
- **TAM**: X,000億円（根拠付き）
- **競合**: [競合マップ。誰と戦っているか]
- **差別化**: [なぜこの会社が勝つか]

## 財務ハイライト
| 指標 | 実績/予測 | YoY成長率 |
|------|---------|---------|
| ARR | | |
| 売上成長率 | | |
| 粗利率 | | |
| NRR | | |
| 営業損益 | | |
| キャッシュ残高/ランウェイ | | |

## 投資基準適合チェック
| 基準 | 評価 | 根拠 |
|------|------|------|
| AI-nativeアーキテクチャ | ✅/⚠️/❌ | |
| NRR 110%+ | ✅/⚠️/❌ | |
| 成長率 80%+ | ✅/⚠️/❌ | |
| TAM 1,000億+ | ✅/⚠️/❌ | |
| 創業者当事者性 | ✅/⚠️/❌ | |
| レッドフラグなし | ✅/⚠️/❌ | |

## リスク上位3点
1. [最重要リスク + ミティゲーション案]
2. [リスク2 + 対応]
3. [リスク3 + 対応]

## 投資ストラクチャー案
- 投資額: XXX百万円
- Pre-money: X億円（根拠: XX社比較）
- 持株比率: XX%
- ラウンド: Series X

## 判断 & アクション
**判断**: ✅ DD進行 / ⚠️ ウォッチリスト / ❌ Pass

**理由**: [3行以内で鋭く]

**ネクストアクション**:
- [ ] [具体的アクション 1 - 担当/期限]
- [ ] [具体的アクション 2 - 担当/期限]

**優先度スコア**: X/10
"""


def ic_memo_prompt(company_name: str, existing_research: str, fund_config: dict) -> str:
    return f"""以下の情報をもとに、投資委員会（IC）向けの詳細投資メモを作成してください。
プロのPEファンドが機関投資家に提出する水準で作成すること。

## ファンド: {fund_config['name']}
## テーゼ: {fund_config['thesis']}

## 既存調査・情報
{existing_research}

---

# 投資委員会メモ: {company_name}
**日付**: {datetime.now().strftime('%Y年%m月%d日')}
**機密 - 社外秘 - 投資委員会限り**

---

## 投資推奨サマリー
| 項目 | 内容 |
|------|------|
| **推奨** | 投資実行 / 見送り |
| **投資額** | X億円 |
| **持株比率（投資後）** | XX% |
| **Pre-money** | X億円 |
| **期待IRR (Base)** | XX% |
| **期待MOIC (Base)** | Xx |

---

## 1. 投資テーゼ（なぜ今、なぜこの会社か）
[3-5段落。ファンドテーゼとの整合性、タイミングの論拠、この会社が勝つ理由を明確に]

## 2. 事業詳細
### 2.1 プロダクト & テクノロジー
### 2.2 収益モデル & 単価構造
### 2.3 顧客プロファイル & 主要顧客事例
### 2.4 GTM戦略

## 3. 市場分析
### 3.1 TAM/SAM/SOM（根拠付き）
### 3.2 競合マップ（2x2マトリクス）
### 3.3 競争優位性の持続可能性

## 4. チーム評価
### 4.1 経営陣プロフィール
### 4.2 強み・ギャップ・採用計画
### 4.3 過去の修羅場・実績

## 5. 財務分析
### 5.1 過去3期財務（P/L・BS・CF）
### 5.2 ユニットエコノミクス（LTV / CAC / CAC回収期間）
### 5.3 コーホート分析（NRR / チャーン）
### 5.4 3ヶ年事業計画 & 前提

## 6. バリュエーション
### 6.1 類似上場企業マルチプル比較
| 会社 | ARR Multiple | NTM Revenue Multiple | 備考 |
|------|------------|---------------------|------|

### 6.2 類似取引事例
### 6.3 DCF感応度分析
### 6.4 バリュエーション結論

## 7. リターンシナリオ
| シナリオ | 前提 | Exit倍率 | IRR | MOIC |
|---------|------|---------|-----|------|
| Bull | 市場No.1、SE Asia展開 | | | |
| Base | 現状トレジェクトリ継続 | | | |
| Bear | 成長鈍化、競合激化 | | | |
| Downside | 大手参入、チャーン悪化 | | | |

## 8. DD サマリー & 残課題
### 完了済み
- [ ] ビジネスDD
- [ ] 財務DD（3期分）
- [ ] 法務DD
- [ ] 技術DD（アーキテクチャレビュー）

### 残課題（クローズ前に解消必須）
| 課題 | 重要度 | 対応方針 |
|------|-------|---------|

## 9. リスク & ミティゲーション
| リスク | 確率 | 影響度 | ミティゲーション |
|-------|------|-------|----------------|

## 10. 投資条件
### 10.1 主要Term Sheet条件
- 優先分配: 1x non-participating preferred
- アンチダイリューション: Broad-based weighted average
- 情報提供権 / 取締役会オブザーバー
- 先買権 / 共同売却権

### 10.2 CP条件

## 11. バリューアッドプラン
### 100日計画
### 価値創造施策（3-5年）

## 12. エグジット戦略
[想定エグジットルート・バイヤー候補・タイムライン]

---
*本メモはPyrenee Capitalの投資委員会審議用資料です。*
"""


def morning_briefing_prompt(
    date: str,
    deal_pipeline: str,
    lp_pipeline: str,
    legal_tasks: str,
    calendar_events: str,
    fund_config: dict,
) -> str:
    return f"""今日（{date}）のPyrenee Capital朝次ブリーフィングを作成してください。
Rui Sasaseが最初に見るもので、「今日何をすべきか」が即座にわかる内容にしてください。

## 入力データ

### 投資パイプライン
{deal_pipeline}

### LPパイプライン
{lp_pipeline}

### 法務タスク
{legal_tasks}

### 今週のカレンダー
{calendar_events}

---

以下の形式で朝次ブリーフィングを作成してください:

# 🌅 Pyrenee Capital 朝次ブリーフ
**{date}（{_get_weekday(date)}）**

---

## ⚡ 今日の最優先3タスク
1. 🔴 [最重要タスク - 誰に/何を/なぜ今日か]
2. 🟠 [重要タスク2]
3. 🟡 [重要タスク3]

---

## 📊 ファンド状況スナップショット
| カテゴリ | 状況 |
|---------|------|
| 投資パイプライン | X社スクリーニング中 / X社DD中 |
| LP進捗 | コミット済X億円 / 目標Y億円（Z%） |
| 法務タスク | X/Y完了 |
| 今週の面談 | X件 |

---

## 🎯 投資パイプライン更新
[各ステージにいる案件と必要アクション]

## 🤝 LP更新
[フォローアップが必要なLPと推奨アクション]

## ⚖️ 法務 & コンプライアンス
[今週期限のタスク・ブロッカー]

## 📅 今週のスケジュール
[重要イベントと準備事項]

---
*Good morning. 今日も前に進もう。*
"""


def lp_pitch_email_prompt(lp_info: dict, fund_config: dict) -> str:
    return f"""以下のLP候補に送る最初のアウトリーチメールを起草してください。
プロフェッショナルかつ具体的で、相手の関心を引く内容にしてください。

## LP情報
{lp_info}

## ファンド情報
- ファンド名: {fund_config['name']}
- テーゼ: {fund_config['thesis']}
- ターゲットサイズ: {fund_config['target_size_bn_jpy']}億円
- ターゲットIRR: {fund_config['focus']['target_irr']}

## メール要件
- 件名：LP候補の関心を引く、具体的な件名
- 本文：3段落以内（長いと読まれない）
- 段落1: なぜこのLPに連絡したか（相手研究を示す）
- 段落2: なぜPyrenee Capitalが他と違うか（テーゼの独自性）
- 段落3: 具体的なネクストアクション（30分のzoom）
- トーン: 丁寧だが自信がある。過剰な敬語不要

件名と本文を出力してください。
"""


def deal_sourcing_prompt(sector: str, signals: dict) -> str:
    signal_list = "\n".join(f"- {s}" for s in signals.get("early_signals", []))
    return f"""「{sector}」セクターにおける投資機会を分析してください。

## 注目すべきシグナル
{signal_list}

## 分析してほしいこと
1. このセクターの日本市場における現状と課題
2. AI導入によって破壊・創造される価値
3. 理想的な投資ターゲット企業のプロファイル（3種類）
4. 見落とされがちなニッチ機会（アンダーレーダーの宝）
5. 次の30日でやるべき具体的なソーシングアクション5点

セクターレポートとして構造化してまとめてください。
"""


def ma_target_analysis_prompt(profile: dict) -> str:
    return f"""以下のM&A/事業承継ターゲットプロファイルに合う企業を日本市場で探す戦略を立ててください。

## ターゲットプロファイル
{profile}

## 分析してほしいこと
1. このプロファイルに合う企業を探すための具体的な手法・データソース
2. アプローチ前に確認すべき情報（公開情報から取れるもの）
3. 初回コンタクトの最適な切り口（後継者問題 vs 成長支援 etc）
4. バリュエーション考え方（EV/Revenue, EV/EBITDA のベンチマーク）
5. この種のM&Aで失敗する典型パターンとその回避法

M&A戦略メモとしてまとめてください。
"""


def _get_weekday(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y年%m月%d日")
        days = ["月", "火", "水", "木", "金", "土", "日"]
        return f"{days[dt.weekday()]}曜日"
    except Exception:
        return ""
