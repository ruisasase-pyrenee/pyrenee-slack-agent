"""
Simulated fund state - realistic Japanese PE fund data for 2026.
This is what Pyrenee Capital looks like on Day 1 of operations.
"""

from datetime import datetime, timedelta

TODAY = datetime(2026, 5, 27)


# ── Deal Pipeline ──────────────────────────────────────────────────────────────
# 3 deals at different stages. All real enough to generate actual analysis.

DEALS = [
    {
        "id": "deal_001",
        "company": "CareLink AI",
        "stage": "screening",
        "sector": "医療・介護AI",
        "description": """
会社名: CareLink AI株式会社
設立: 2021年4月
本社: 東京都渋谷区
事業: 介護施設向けAIケアプランニング＆スタッフ最適配置SaaS
ターゲット顧客: 特別養護老人ホーム、有料老人ホーム（従業員50名以上の施設）
導入実績: 280施設（うち大手法人チェーン15社）

【財務】
ARR: 4.2億円
YoY成長率: 165%
粗利率: 78%
NRR: 118%
月次チャーン: 0.8%
CAC回収期間: 11ヶ月
営業損益: ▲8,000万円（積極投資期）
キャッシュ残高: 6.8億円（ランウェイ18ヶ月）

【プロダクト】
- AIがケアプランを自動生成（行政への提出書類含む）
- スタッフシフト最適化（残業30%削減実績）
- 家族向けアプリ（介護状況のリアルタイム共有）
- 2023年にMHLW（厚生労働省）認定取得済み

【チーム】
- CEO: 山田健太（元ニチイ学館 介護部門責任者、慶應義塾大学医学部）
- CTO: 李文博（元Google DeepMind、AI/ML博士）
- COO: 中村美咲（元マッキンゼー、ヘルスケアプラクティス）

【資金調達履歴】
- Seed: 5,000万円（Coral Capital、2021年）
- Series A: 2.5億円（DNX Ventures、2022年）
- Series B: 7.5億円（Incubate Fund + 医療法人SHD、2024年）

【競合】
- カナミックネットワーク（上場、ケアマネ向けシステム）
- ワイズマン（レガシーシステム、AI機能なし）
- CarePoint（米国発、日本参入失敗済み）

【リスク】
- 介護報酬改定リスク（2026年4月改定、プラス影響）
- 施設の IT リテラシー格差
- 大手レコードベンダーの AI 機能追加
""",
    },
    {
        "id": "deal_002",
        "company": "BuildSense",
        "stage": "sourced",
        "sector": "建設・不動産テック",
        "description": """
会社名: BuildSense株式会社
設立: 2020年9月
本社: 大阪府大阪市
事業: 建設現場向けAI安全管理＆工程最適化SaaS（BIMネイティブ）
ターゲット顧客: 中堅ゼネコン（売上100〜5,000億円）

【財務】
ARR: 2.1億円
YoY成長率: 210%
粗利率: 72%
NRR: 124%
月次チャーン: 0.3%（解約ほぼなし、現場定着率高）
CAC回収期間: 8ヶ月
営業損益: ▲1.2億円
キャッシュ残高: 3.2億円（ランウェイ12ヶ月 → 要調達）

【プロダクト】
- カメラ＋AIによるリアルタイム安全確認（ヘルメット未着用・危険行動検知）
- BIMデータとの統合による工程シミュレーション
- 現場日報の自動生成（工数▲60%実績）
- 重機・作業員の動線分析 → 生産性可視化

【チーム】
- CEO: 鈴木剛（元鹿島建設 現場監督→DX推進室、東京大学工学部）
- CTO: 田中翔（元NTTデータ、コンピュータビジョン専門）
- VP Sales: 佐藤隆（元竹中工務店 営業部長）

【資金調達履歴】
- Seed: 3,000万円（ANRI、2020年）
- Series A: 1.5億円（WiL + SMBC VC、2022年）
- 今回: Series B 調達検討中（ランウェイ逼迫）

【競合】
- 安藤ハザマ社内開発ツール（クローズド）
- Autodesk Construction Cloud（グローバル大手、日本語対応弱）
- SpiderPlus（上場、図面管理特化）

【リスク】
- 建設業の2024年問題（残業規制）が追い風だが営業サイクル長い
- ランウェイ12ヶ月 → シリーズB調達スピードが鍵
- 競合がBIM+AIを強化中
""",
    },
    {
        "id": "deal_003",
        "company": "LoanForge",
        "stage": "sourced",
        "sector": "SMB向け金融インフラ",
        "description": """
会社名: LoanForge株式会社
設立: 2023年1月
本社: 東京都千代田区
事業: 中小企業向けAI融資審査プラットフォーム（銀行・信金向けSaaS）
ターゲット顧客: 地方銀行・信用金庫（Pyrenee CapitalのLPターゲットと重複）

【財務】
ARR: 8,500万円
YoY成長率: 280%（ただし基数小）
粗利率: 81%
NRR: 131%
月次チャーン: 0%（解約ゼロ、金融機関は一度入れたら動かない）
CAC回収期間: 18ヶ月（金融機関の営業サイクルが長い）
営業損益: ▲2.1億円
キャッシュ残高: 4.5億円

【プロダクト】
- 中小企業の会計データ・POS・EC・税務申告を統合して信用スコア自動計算
- 審査担当者の意思決定支援（説明可能AIで金融庁対応）
- 融資実行後の早期警戒（デフォルト予測）
- API提供でコアバンキングと統合

【チーム】
- CEO: 小林誠（元日本政策金融公庫 融資審査部長、東京大学法学部）
- CTO: 山口博（元Stripe Japan、フィンテックエンジニア10年）
- CSO: 高橋純（元みずほFG フィンテック戦略室）

【資金調達履歴】
- Seed: 1億円（East Ventures + 個人エンジェル3名、2023年）
- Series A: 5億円（DBJ（日本政策投資銀行）+ SBI Investment、2024年）

【競合】
- クレジットエンジン（類似サービス、数年先行）
- 全銀システム系ベンダー（TIS、NTTデータ）の新機能
- 米国Kabbage系の日本参入

【リスク】
- LPターゲット（地銀）との利益相反リスク要確認
- 金融庁規制対応コスト高い
- 顧客獲得サイクルが18ヶ月と長い
- ARRが基数小（1億円未満）のため成長率が歪んで見える
""",
    },
]

# ── M&A Target ────────────────────────────────────────────────────────────────

MA_TARGET = {
    "company": "菊池建設システム株式会社",
    "sector": "建設業向けERPベンダー（事業承継型M&A候補）",
    "description": """
会社名: 菊池建設システム株式会社
設立: 1987年
本社: 埼玉県さいたま市
事業: 中小ゼネコン向け工事原価管理・積算システムの開発・販売
代表: 菊池正雄（創業者、72歳。後継者不在、売却を検討）

【財務】
売上: 3.2億円（うちSaaS系サポート収益: 1.4億円）
営業利益率: 28%
顧客数: 340社（創業以来の関係、チャーンほぼゼロ）
エンジニア: 15名（平均勤続12年）
時価総額相場: 売上0.8〜1.2x → 2.5〜3.8億円

【なぜこれが面白いか】
- 既存顧客340社はAI機能に飢えているが、同社は開発力なし
- CareLink AIやBuildSenseとの連携でエコシステム化できる
- Pyrenee買収後: クラウドSaaS化 + AI積算機能追加 → ARR3倍シナリオ
- 菊池社長は「技術と社員を守ってくれる買い手」を探している
""",
}

# ── LP Pipeline ────────────────────────────────────────────────────────────────

LPS = [
    {
        "org": "東北みらい銀行",
        "contact": "佐々木部長（経営企画部 代替投資担当）",
        "email": "sasaki@tohoku-mirai-bank.co.jp",
        "tier": "tier1",
        "type": "地方銀行",
        "ticket_mn_jpy": 300,
        "status": "meeting_scheduled",
        "meeting_date": "2026-05-30",
        "notes": "来週木曜10時にzoom。日本政策投資銀行経由の紹介。地銀のALMで代替投資枠30億円を新設したばかり。初めてのPEファンド投資になる可能性。",
    },
    {
        "org": "Sony Innovation Fund",
        "contact": "田村VP（Ventures部門）",
        "email": "tamura@sony-if.com",
        "tier": "tier1",
        "type": "事業法人CVC",
        "ticket_mn_jpy": 500,
        "status": "met",
        "meeting_date": "2026-05-15",
        "notes": "先週初回ミーティング済。医療・介護AIへの戦略的関心あり（Sony自身もヘルスケア強化中）。CareLink AIへの共同投資に興味示す。次のステップはDD資料送付。",
    },
    {
        "org": "田中ファミリーオフィス",
        "contact": "田中太郎（創業家3代目、CFO）",
        "email": "tanaka@tanaka-fo.com",
        "tier": "tier2",
        "type": "ファミリーオフィス",
        "ticket_mn_jpy": 200,
        "status": "intro_sent",
        "meeting_date": None,
        "notes": "3日前にメール送付済み。返信なし。元は製造業（部品メーカー）の創業家。相続税対策でオルタナティブ投資を探している。共通の知人（X氏）経由の紹介。",
    },
    {
        "org": "関西電力企業年金基金",
        "contact": "松本理事（運用委員会）",
        "email": "matsumoto@kepf.or.jp",
        "tier": "tier2",
        "type": "企業年金",
        "ticket_mn_jpy": 500,
        "status": "prospect",
        "meeting_date": None,
        "notes": "まだコンタクトしていない。運用委員会が代替投資比率を5%→8%に引き上げる方針を発表（業界誌ソース）。アプローチタイミングとして最適。",
    },
    {
        "org": "Sequoia Heritage（アジア枠）",
        "contact": "James Chen（MD）",
        "email": "jchen@sequoiaheritage.com",
        "tier": "tier3",
        "type": "外資機関投資家",
        "ticket_mn_jpy": 1000,
        "status": "met",
        "meeting_date": "2026-04-20",
        "notes": "4月に初回面談。Japan露出を増やしたいとのこと。ただし『まずは実績を見せてくれ』スタンス。ファーストクローズ後に再アプローチが現実的。フォローアップメールを送っていない（3週間放置してしまっている）。",
    },
]

# ── Portfolio Companies ────────────────────────────────────────────────────────
# Already invested (simulated)

PORTFOLIO = [
    {
        "company": "MedRoute株式会社",
        "sector": "医療DX",
        "invested_date": "2025-09-01",
        "investment_mn_jpy": 300,
        "ownership_pct": 18,
        "last_arr_mn_jpy": 5.8,
        "last_arr_growth_yoy": 142,
        "last_nrr": 112,
        "cash_runway_months": 20,
        "recent_updates": """
- Q1: ARR 5.8億円（前QoQ +18%）。目標達成。
- 主要顧客: 病院チェーン3社で売上の38%。集中リスクあり。
- CTO退職の噂（LinkedInでポジション更新を確認）。要確認。
- 競合: Medical Note社が3月に30億円調達。機能強化中。
- 次回Board: 6月3日
""",
    },
    {
        "company": "LogiPath AI株式会社",
        "sector": "物流・サプライチェーンAI",
        "invested_date": "2025-12-15",
        "investment_mn_jpy": 250,
        "ownership_pct": 21,
        "last_arr_mn_jpy": 2.3,
        "last_arr_growth_yoy": 188,
        "last_nrr": 121,
        "cash_runway_months": 14,
        "recent_updates": """
- Q1: ARR 2.3億円（前QoQ +22%）。計画超え。
- 佐川急便との大型PoC合意（MRR 800万円、3ヶ月PoC）。本採用になれば一気にARR1億円追加。
- 採用加速: エンジニア5名採用中（現在12名）。
- ランウェイ14ヶ月。Series B調達を来Q末に開始予定。
- CEO: 「Pyreneeのネットワークで佐川のPoC成功を手伝ってほしい」
""",
    },
]

# ── Legal Tasks Status ────────────────────────────────────────────────────────

LEGAL_STATUS = {
    "fund_formation": [
        {"task": "GP合同会社設立", "status": "completed", "priority": "critical", "week": 1, "note": "2026年3月完了"},
        {"task": "弁護士選定（田辺総合法律事務所）", "status": "completed", "priority": "critical", "week": 1},
        {"task": "会計士・監査法人選定（EY新日本）", "status": "completed", "priority": "critical", "week": 1},
        {"task": "投資事業有限責任組合（LPS）設立", "status": "in_progress", "priority": "critical", "week": 3, "note": "書類準備中、6月末設立予定"},
        {"task": "第二種金融商品取引業者登録", "status": "in_progress", "priority": "critical", "week": 3, "note": "弁護士と申請書類作成中。審査3〜4ヶ月"},
        {"task": "適格機関投資家等特例業務届出", "status": "pending", "priority": "high", "week": 3},
        {"task": "LPA（有限責任組合契約書）起草", "status": "in_progress", "priority": "critical", "week": 5, "note": "田辺法律事務所にて初稿作成中"},
        {"task": "PPM（私募募集要項）起草", "status": "pending", "priority": "critical", "week": 5},
        {"task": "管理報酬・キャリー条件確定（2/20/8%）", "status": "completed", "priority": "critical", "week": 5},
        {"task": "KYC/AMLポリシー策定", "status": "pending", "priority": "critical", "week": 6},
        {"task": "税務ストラクチャリング確認", "status": "in_progress", "priority": "high", "week": 7},
        {"task": "ファンド銀行口座開設", "status": "pending", "priority": "critical", "week": 8},
    ],
    "fundraising": [
        {"task": "LPターゲットリスト作成（Tier1: 20社）", "status": "in_progress", "priority": "critical", "week": 2, "note": "現在Tier1: 8社、Tier2: 12社"},
        {"task": "ピッチデック作成", "status": "completed", "priority": "critical", "week": 2},
        {"task": "トラックレコード整備", "status": "completed", "priority": "critical", "week": 2},
        {"task": "Google Driveデータルーム構築", "status": "in_progress", "priority": "high", "week": 3},
        {"task": "ファーストクローズ目標設定（2B JPY）", "status": "completed", "priority": "high", "week": 4},
        {"task": "アンカーLP確保（総額の20-30%）", "status": "pending", "priority": "critical", "week": 6},
        {"task": "LP DDへの対応準備（Q&Aドキュメント）", "status": "pending", "priority": "high", "week": 8},
    ],
    "investment_ops": [
        {"task": "IC（投資委員会）プロセス策定", "status": "completed", "priority": "high", "week": 4},
        {"task": "標準タームシート雛形作成", "status": "pending", "priority": "high", "week": 6},
        {"task": "バリュエーション基準書策定", "status": "pending", "priority": "medium", "week": 8},
        {"task": "ポートフォリオ管理システム構築", "status": "in_progress", "priority": "medium", "week": 8},
        {"task": "LP定期報告フォーマット確定", "status": "pending", "priority": "medium", "week": 10},
    ],
}

# ── Fund Metrics ──────────────────────────────────────────────────────────────

FUND_METRICS = {
    "committed_capital_mn_jpy": 550,  # 東北みらい銀行口頭コミット300M、その他検討中
    "first_close_target_mn_jpy": 2000,
    "invested_capital_mn_jpy": 550,   # MedRoute 300M + LogiPath 250M
    "portfolio_companies": 2,
    "active_screening": 3,
    "lp_prospects": 5,
    "fund_inception": "2026-03-01",
}
