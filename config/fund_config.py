"""
Pyrenee Capital I - Fund Configuration
My opinionated choices for the optimal 2026 Japan growth equity fund.
"""

FUND_CONFIG = {
    "name": "Pyrenee Capital I",
    "vintage": 2026,
    "strategy": "growth_equity",
    "thesis": "日本の3.5M中小企業に刺さるAI-native縦型SaaS。AIが既存SaaSを陳腐化させる第二波の破壊者を早期に捕捉する。",

    # Size: 5B JPY = 15-20社に分散投資できる最小限のクリティカルマス
    "target_size_bn_jpy": 5,
    "first_close_target_bn_jpy": 2,

    "focus": {
        # 確信度順。セクターが絞れていることが「なぜあなたのファンドか」への答えになる
        "sectors_ranked": [
            "医療・介護AI",           # 人手不足の緊急度が最高、規制モートあり
            "建設・不動産テック",      # 20兆円産業、デジタル化率最低水準
            "SMB向け金融インフラ",     # embedded finance、AIクレジット
            "サプライチェーン・物流AI", # 製造業のOT/IT統合
            "法務・バックオフィス自動化", # LegalON以降の第二層
        ],
        "geographies": ["Japan"],  # まずJapan one-country deep dive。SE Asiaはファンド2
        "stages": ["Series A", "Series B", "Pre-IPO"],

        # Check size: 200-500M JPYが俺のsweet spot
        # - 種は小さすぎてVC領域
        # - 1B+は既存PEとバッティング
        "check_size_min_mn_jpy": 200,
        "check_size_max_mn_jpy": 500,
        "follow_on_reserve_pct": 40,  # 40%をフォローオン用に確保
        "target_ownership": "15-25%",
        "hold_period_years": "4-6",
        "target_irr": "30%+",        # グロースエクイティとして野心的だが達成可能
        "target_moic": "3-5x",
        "portfolio_cos": "12-15",    # 集中投資。分散は収益の希薄化
    },

    "team": {
        "gp_name": "Pyrenee Capital GP合同会社",
        "key_person": "Rui Sasase",
        "fee_structure": "2/20",     # 管理報酬2%、キャリー20%（業界標準）
        "hurdle_rate": "8%",
    },

    # ターゲットLPプロファイル（優先度順）
    # 地銀が最短経路: 代替投資ニーズが高く、日本語でコミュニケーションできる
    "lp_targets": {
        "tier1": [
            {"type": "地方銀行", "rationale": "代替投資リターン需要、日本語コミュ、100-500M JPYチケット"},
            {"type": "事業法人CVC", "rationale": "戦略的価値+財務リターン、ポートフォリオ企業との相乗効果"},
        ],
        "tier2": [
            {"type": "ファミリーオフィス（創業家系）", "rationale": "意思決定速い、長期コミット"},
            {"type": "大学・財団", "rationale": "長期資金、IRRより安定重視"},
        ],
        "tier3": [
            {"type": "外資機関投資家", "rationale": "Japan露出を求める米系エンダウメント"},
            {"type": "政府系ファンド（SMRJ等）", "rationale": "LP-of-LP経由のバリデーション"},
        ],
    },

    "legal_status": "formation",
}

# ────────────────────────────────────────────
# Deal Screening Criteria (俺のフィルター)
# ────────────────────────────────────────────
DEAL_SCREENING_CRITERIA = {
    "quantitative": {
        "arr_min_mn_jpy": 200,
        "growth_yoy_min_pct": 80,       # 最低でも80%成長
        "gross_margin_min_pct": 70,
        "nrr_min_pct": 110,             # Net Revenue Retention 110%以上
        "runway_min_months": 12,
    },
    "must_have": [
        "AI-native または AI-first アーキテクチャ（後付けAIは不可）",
        "特定縦型セクターへの深い業界知識・参入障壁",
        "NRR 110%以上 または明確な達成ロードマップ",
        "創業者が業界課題を自ら経験した当事者",
        "TAM 1,000億円以上 (日本のみで)",
    ],
    "nice_to_have": [
        "ネットワーク効果またはデータ蓄積モート",
        "SMB→Enterprise拡張の実績または計画",
        "日本→東南アジア展開の青写真",
        "既存大手との提携・OEM実績",
    ],
    "red_flags": [
        "トップ顧客集中度30%超（チャーンリスク）",
        "創業者間の持分格差または関係悪化の兆候",
        "ARR成長率の鈍化傾向（QoQで3Q連続以上）",
        "競合に対する明確な差別化の欠如",
        "過去ラウンドでのdownround歴（要確認）",
        "CAC回収期間24ヶ月超（SMBとしては長すぎ）",
    ],
}

# ────────────────────────────────────────────
# Deal Signal Sources (これを監視する)
# ────────────────────────────────────────────
DEAL_SIGNAL_SOURCES = {
    "funding_news": [
        "PR TIMES (プレスリリース)",
        "TechCrunch Japan",
        "THE BRIDGE",
        "INITIAL (旧entrepedia)",
        "スタートアップデータベース",
    ],
    "hiring_signals": [
        "Wantedly 採用急増",
        "LinkedIn Headcount growth",
        "Green / doda スタートアップ採用",
    ],
    "ma_signals": [
        "M&A Online",
        "RECOF DATA",
        "日経バリュー検索",
        "後継者不足企業 (事業承継)",
    ],
    "early_signals": [
        "YC/500 Japan batch卒業生",
        "Coral Capital / DNX / WiL / Incubate Fund ポートフォリオ（シリーズA既投）",
        "IPA未踏スーパークリエイター出身",
        "大手企業スピンアウト",
    ],
    # これらのシグナルが重なる企業は最優先で当たる
    "conviction_multipliers": [
        "採用数50%+ QoQ成長 + 資金調達なし = キャッシュフロー黒字化の可能性",
        "既存VC未投資 + ARR成長高速 = アンダーレーダーの宝",
        "業界カンファレンス登壇多数 = ドメイン権威性あり",
    ],
}

# ────────────────────────────────────────────
# M&A / Buy-and-Build Target Profiles
# ────────────────────────────────────────────
MA_TARGET_PROFILES = {
    "description": "事業承継型M&A：後継者不在の優良SMBソフトウェア企業を買収してAI化",
    "rationale": "日本には後継者問題で売却検討中の優良ソフト会社が多数。これをプラットフォーム化する",
    "profiles": [
        {
            "sector": "建設業向けERPベンダー",
            "target_revenue_mn_jpy": "100-500",
            "signal": "創業20年以上、社長60代以上、後継者不在",
            "thesis": "レガシーシステムをAI-nativeに刷新 + クラウド化でARRに転換",
        },
        {
            "sector": "医療・介護向けシステムベンダー",
            "target_revenue_mn_jpy": "50-300",
            "signal": "地域密着型、顧客ロイヤルティ高い、IT投資滞り気味",
            "thesis": "AI診断支援・ケアプランAIをアドオンして単価3倍",
        },
        {
            "sector": "製造業向けMES/QMS系ソフト",
            "target_revenue_mn_jpy": "100-800",
            "signal": "細かい業界特化、競合少ない、SaaSに移行できていない",
            "thesis": "クラウドSaaS化 + AI品質管理機能追加でグローバル展開",
        },
    ],
}

# ────────────────────────────────────────────
# Legal Checklist（俺の優先順位付き）
# ────────────────────────────────────────────
LEGAL_CHECKLIST = {
    "fund_formation": [
        # Week 1-2: これなしでは何も始まらない
        {"task": "GP合同会社設立（資本金100万円）", "status": "pending", "priority": "critical", "week": 1},
        {"task": "弁護士選定（ファンド法務専門・3社見積）", "status": "pending", "priority": "critical", "week": 1},
        {"task": "会計士・監査法人選定", "status": "pending", "priority": "critical", "week": 1},
        # Week 3-4: 法的枠組み
        {"task": "投資事業有限責任組合（LPS）設立", "status": "pending", "priority": "critical", "week": 3},
        {"task": "第二種金融商品取引業者登録（or 適用除外確認）", "status": "pending", "priority": "critical", "week": 3},
        {"task": "適格機関投資家等特例業務届出（要件確認）", "status": "pending", "priority": "high", "week": 3},
        # Week 5-8: ドキュメント
        {"task": "LPA（有限責任組合契約書）起草", "status": "pending", "priority": "critical", "week": 5},
        {"task": "PPM（私募募集要項）起草", "status": "pending", "priority": "critical", "week": 5},
        {"task": "管理報酬・キャリー・ハードル条件確定（2/20/8%）", "status": "pending", "priority": "critical", "week": 5},
        {"task": "サイドレター雛形（MFN条項含む）", "status": "pending", "priority": "high", "week": 6},
        {"task": "KYC/AMLポリシー策定", "status": "pending", "priority": "critical", "week": 6},
        {"task": "税務ストラクチャリング（GP/LP課税確認）", "status": "pending", "priority": "high", "week": 7},
        {"task": "ファンド銀行口座開設", "status": "pending", "priority": "critical", "week": 8},
    ],
    "fundraising": [
        {"task": "LPターゲットリスト作成（Tier1: 20社、Tier2: 30社）", "status": "pending", "priority": "critical", "week": 2},
        {"task": "ピッチデック作成（15-20スライド）", "status": "pending", "priority": "critical", "week": 2},
        {"task": "トラックレコード整備（過去投資実績の数字）", "status": "pending", "priority": "critical", "week": 2},
        {"task": "Google Driveデータルーム構築", "status": "pending", "priority": "high", "week": 3},
        {"task": "ファーストクローズ目標設定（2B JPY）", "status": "pending", "priority": "high", "week": 4},
        {"task": "アンカーLP確保（総額の20-30%）", "status": "pending", "priority": "critical", "week": 6},
        {"task": "LP DDへの対応準備（Q&Aドキュメント）", "status": "pending", "priority": "high", "week": 8},
    ],
    "investment_ops": [
        {"task": "IC（投資委員会）プロセス・権限規程策定", "status": "pending", "priority": "high", "week": 4},
        {"task": "標準タームシート雛形（SHA/SPA）", "status": "pending", "priority": "high", "week": 6},
        {"task": "バリュエーション基準書策定", "status": "pending", "priority": "medium", "week": 8},
        {"task": "ポートフォリオ管理システム構築（Drive+Notion）", "status": "pending", "priority": "medium", "week": 8},
        {"task": "LP定期報告フォーマット確定（四半期）", "status": "pending", "priority": "medium", "week": 10},
    ],
}

# ────────────────────────────────────────────
# Portfolio Value Creation Playbook
# ────────────────────────────────────────────
VALUE_CREATION_PLAYBOOK = {
    "100_day_priorities": [
        "CFO/COO採用支援（創業者はプロダクトに集中させる）",
        "エンタープライズ営業チーム構築（SMBからアップセル）",
        "データ基盤整備（AIフィーチャー開発の前提）",
        "既存顧客NPS調査とチャーン予防施策",
    ],
    "value_creation_levers": [
        "価格改定（AI機能追加でtier pricing導入、ARPU 2倍）",
        "M&Aによる隣接領域展開（buy-and-build）",
        "SE Asia展開（シンガポール拠点設立支援）",
        "大手SIer/コンサルとのOEM・アライアンス締結",
        "IPO準備（監査法人変更、社外取締役招聘）",
    ],
    "exit_routes": [
        "IPO（東証グロース → スタンダード）: 最大リターン",
        "Strategic M&A: 大手IT・コンサル・総合商社へ売却",
        "Secondary sale to large PE: ファンドサイズ拡大期",
    ],
}
