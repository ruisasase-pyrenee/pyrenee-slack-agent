"""
Fund configuration - edit this to define your fund's investment thesis.
The agent uses this to screen deals and track compliance.
"""

FUND_CONFIG = {
    "name": "Pyrenee Capital I",
    "vintage": 2026,
    "target_size_bn_jpy": 10,  # 10億円
    "strategy": "growth_equity",  # growth_equity | buyout | venture | real_estate
    "focus": {
        "sectors": ["B2B SaaS", "DeepTech", "FinTech", "HealthTech"],
        "geographies": ["Japan", "Southeast Asia"],
        "stages": ["Series A", "Series B", "Growth"],
        "check_size_min_mn_jpy": 100,
        "check_size_max_mn_jpy": 500,
        "target_ownership": "10-30%",
        "hold_period_years": "5-7",
        "target_irr": "25%+",
        "target_moic": "3x+",
    },
    "team": {
        "gp_name": "Pyrenee Capital GP LLC",
        "key_person": "Rui Sasase",
    },
    "legal_status": "formation",  # formation | fundraising | investment | harvesting
}

DEAL_SCREENING_CRITERIA = {
    "must_have": [
        "Recurring revenue or clear path to it",
        "Defensible market position or proprietary technology",
        "Strong founding team with relevant domain expertise",
        "Total addressable market > 100B JPY",
    ],
    "nice_to_have": [
        "Network effects or platform dynamics",
        "Strong unit economics (LTV/CAC > 3x)",
        "International expansion potential",
    ],
    "red_flags": [
        "Single customer concentration > 30%",
        "Regulatory risk without mitigation plan",
        "Founder conflicts or cap table issues",
        "Revenue decline or negative growth",
    ],
}

LEGAL_CHECKLIST = {
    "fund_formation": [
        {"task": "GP LLC設立 (合同会社)", "status": "pending", "priority": "high"},
        {"task": "ファンド有限責任組合 (LPS) 設立", "status": "pending", "priority": "high"},
        {"task": "金融商品取引業者登録 (第二種)", "status": "pending", "priority": "high"},
        {"task": "投資事業有限責任組合法 (LPS法) 適格確認", "status": "pending", "priority": "high"},
        {"task": "LPA (組合契約書) 起草", "status": "pending", "priority": "high"},
        {"task": "PPM (私募募集要項) 起草", "status": "pending", "priority": "high"},
        {"task": "管理報酬・キャリー条件確定 (2/20など)", "status": "pending", "priority": "high"},
        {"task": "サイドレター雛形作成", "status": "pending", "priority": "medium"},
        {"task": "KYC/AML体制整備", "status": "pending", "priority": "high"},
        {"task": "税務ストラクチャリング確認", "status": "pending", "priority": "medium"},
    ],
    "fundraising": [
        {"task": "ターゲットLPリスト作成 (50社以上)", "status": "pending", "priority": "high"},
        {"task": "ピッチデック作成", "status": "pending", "priority": "high"},
        {"task": "データルーム構築 (Google Drive)", "status": "pending", "priority": "high"},
        {"task": "ファーストクローズ目標設定", "status": "pending", "priority": "medium"},
        {"task": "LP向けトラック記録整備", "status": "pending", "priority": "high"},
    ],
    "investment": [
        {"task": "投資基準・IC決議プロセス確立", "status": "pending", "priority": "high"},
        {"task": "標準投資契約書類作成 (SHA/SPA/Term Sheet)", "status": "pending", "priority": "high"},
        {"task": "バリュエーション基準策定", "status": "pending", "priority": "medium"},
        {"task": "ポートフォリオ管理体制構築", "status": "pending", "priority": "medium"},
    ],
}
