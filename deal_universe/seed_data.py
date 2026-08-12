"""
Deal universe — initial seed of 60 companies across 5 sectors.
All profiles are fictional archetypes based on real market patterns.
Replace/augment with real data from INITIAL, PR TIMES, etc.

Sectors:
  1. 医療・介護AI        (12 companies)
  2. 建設・不動産テック   (12 companies)
  3. SMB向け金融インフラ  (12 companies)
  4. サプライチェーン・物流AI (12 companies)
  5. 法務・バックオフィス  (12 companies)
"""

UNIVERSE: list[dict] = [

    # ══════════════════════════════════════════════════════════════
    # SECTOR 1: 医療・介護AI  ← 最高確信度
    # ══════════════════════════════════════════════════════════════

    {
        "id": "med_001", "name": "CareLink AI", "sector": "医療・介護AI",
        "stage": "Series B", "hq": "東京", "founded": 2021,
        "description": "介護施設向けAIケアプランニング＆スタッフ最適化SaaS。厚労省認定取得。",
        "website": "carelinkj.example.com", "source": "simulation",
        "metrics": {"arr_mn_jpy": 420, "growth_yoy_pct": 165, "gross_margin": 78,
                    "nrr_pct": 118, "cac_months": 11, "runway_months": 18,
                    "employees": 52, "tam_bn_jpy": 200},
    },
    {
        "id": "med_002", "name": "MediPath AI", "sector": "医療・介護AI",
        "stage": "Series A", "hq": "大阪", "founded": 2020,
        "description": "病院向けAI診断支援 + 電子カルテ自動入力。放射線科特化。",
        "website": "", "source": "pr_times",
        "metrics": {"arr_mn_jpy": 180, "growth_yoy_pct": 210, "gross_margin": 80,
                    "nrr_pct": 122, "cac_months": 14, "runway_months": 15,
                    "employees": 28, "tam_bn_jpy": 300},
    },
    {
        "id": "med_003", "name": "PharmaSense", "sector": "医療・介護AI",
        "stage": "Series B", "hq": "東京", "founded": 2019,
        "description": "製薬企業向けAI創薬候補探索 + 副作用予測プラットフォーム。",
        "website": "", "source": "bridge",
        "metrics": {"arr_mn_jpy": 650, "growth_yoy_pct": 88, "gross_margin": 85,
                    "nrr_pct": 130, "cac_months": 18, "runway_months": 24,
                    "employees": 90, "tam_bn_jpy": 1200},
    },
    {
        "id": "med_004", "name": "NurseFlow", "sector": "医療・介護AI",
        "stage": "Series A", "hq": "福岡", "founded": 2022,
        "description": "看護師の業務記録をAI自動化。夜勤ストレス軽減。病院チェーン特化。",
        "website": "", "source": "wantedly",
        "metrics": {"arr_mn_jpy": 95, "growth_yoy_pct": 290, "gross_margin": 75,
                    "nrr_pct": 115, "cac_months": 9, "runway_months": 14,
                    "employees": 18, "tam_bn_jpy": 80},
    },
    {
        "id": "med_005", "name": "CognitiveCare", "sector": "医療・介護AI",
        "stage": "Seed", "hq": "東京", "founded": 2023,
        "description": "認知症早期検知AIアプリ。MCI（軽度認知障害）をスマホで検知。",
        "website": "", "source": "initial",
        "metrics": {"arr_mn_jpy": 25, "growth_yoy_pct": 400, "gross_margin": 82,
                    "nrr_pct": 108, "cac_months": 6, "runway_months": 18,
                    "employees": 12, "tam_bn_jpy": 150},
    },
    {
        "id": "med_006", "name": "RehabAI", "sector": "医療・介護AI",
        "stage": "Series A", "hq": "名古屋", "founded": 2021,
        "description": "リハビリ施設向けAI回復予測＆プログラム最適化。保険適用データ連携。",
        "website": "", "source": "pr_times",
        "metrics": {"arr_mn_jpy": 140, "growth_yoy_pct": 175, "gross_margin": 76,
                    "nrr_pct": 119, "cac_months": 12, "runway_months": 16,
                    "employees": 24, "tam_bn_jpy": 120},
    },
    {
        "id": "med_007", "name": "ClinicBot", "sector": "医療・介護AI",
        "stage": "Series A", "hq": "東京", "founded": 2020,
        "description": "クリニック向けAI予約・問診・会計自動化。OpenAPI対応。",
        "website": "", "source": "initial",
        "metrics": {"arr_mn_jpy": 310, "growth_yoy_pct": 120, "gross_margin": 71,
                    "nrr_pct": 112, "cac_months": 8, "runway_months": 20,
                    "employees": 45, "tam_bn_jpy": 180},
    },
    {
        "id": "med_008", "name": "SeniorLink", "sector": "医療・介護AI",
        "stage": "Series B", "hq": "東京", "founded": 2019,
        "description": "在宅介護家族向けプラットフォーム。AI見守りセンサー＋家族アプリ。",
        "website": "", "source": "bridge",
        "metrics": {"arr_mn_jpy": 520, "growth_yoy_pct": 95, "gross_margin": 68,
                    "nrr_pct": 114, "cac_months": 15, "runway_months": 22,
                    "employees": 75, "tam_bn_jpy": 250},
    },
    {
        "id": "med_009", "name": "MentalScope", "sector": "医療・介護AI",
        "stage": "Series A", "hq": "東京", "founded": 2022,
        "description": "企業向けメンタルヘルスAI早期発見プラットフォーム。EAP連携。",
        "website": "", "source": "wantedly",
        "metrics": {"arr_mn_jpy": 160, "growth_yoy_pct": 220, "gross_margin": 80,
                    "nrr_pct": 125, "cac_months": 10, "runway_months": 18,
                    "employees": 30, "tam_bn_jpy": 90},
    },
    {
        "id": "med_010", "name": "PathologyAI", "sector": "医療・介護AI",
        "stage": "Series B", "hq": "京都", "founded": 2018,
        "description": "病理画像AIスキャン。がん検診の精度を向上。大学病院と共同開発。",
        "website": "", "source": "bridge",
        "metrics": {"arr_mn_jpy": 890, "growth_yoy_pct": 72, "gross_margin": 88,
                    "nrr_pct": 135, "cac_months": 20, "runway_months": 30,
                    "employees": 120, "tam_bn_jpy": 800},
    },
    {
        "id": "med_011", "name": "PharmaConnect", "sector": "医療・介護AI",
        "stage": "Series A", "hq": "大阪", "founded": 2021,
        "description": "薬局向けAI在庫管理＋患者フォローアップ自動化。調剤チェーン特化。",
        "website": "", "source": "pr_times",
        "metrics": {"arr_mn_jpy": 220, "growth_yoy_pct": 145, "gross_margin": 74,
                    "nrr_pct": 116, "cac_months": 11, "runway_months": 17,
                    "employees": 38, "tam_bn_jpy": 130},
    },
    {
        "id": "med_012", "name": "CareMetrics", "sector": "医療・介護AI",
        "stage": "Series A", "hq": "東京", "founded": 2022,
        "description": "介護施設経営者向けKPIダッシュボード＋AI経営アドバイザリー。",
        "website": "", "source": "initial",
        "metrics": {"arr_mn_jpy": 75, "growth_yoy_pct": 310, "gross_margin": 83,
                    "nrr_pct": 121, "cac_months": 7, "runway_months": 16,
                    "employees": 15, "tam_bn_jpy": 60},
    },

    # ══════════════════════════════════════════════════════════════
    # SECTOR 2: 建設・不動産テック
    # ══════════════════════════════════════════════════════════════

    {
        "id": "con_001", "name": "BuildSense", "sector": "建設・不動産テック",
        "stage": "Series A", "hq": "大阪", "founded": 2020,
        "description": "建設現場向けAI安全管理＆工程最適化SaaS。BIMネイティブ。",
        "website": "", "source": "simulation",
        "metrics": {"arr_mn_jpy": 210, "growth_yoy_pct": 210, "gross_margin": 72,
                    "nrr_pct": 124, "cac_months": 8, "runway_months": 12,
                    "employees": 35, "tam_bn_jpy": 500},
    },
    {
        "id": "con_002", "name": "EstimAI", "sector": "建設・不動産テック",
        "stage": "Series A", "hq": "東京", "founded": 2021,
        "description": "中小ゼネコン向けAI工事積算自動化。見積もり工数▲80%。",
        "website": "", "source": "pr_times",
        "metrics": {"arr_mn_jpy": 155, "growth_yoy_pct": 195, "gross_margin": 76,
                    "nrr_pct": 120, "cac_months": 10, "runway_months": 14,
                    "employees": 22, "tam_bn_jpy": 200},
    },
    {
        "id": "con_003", "name": "SiteWatch", "sector": "建設・不動産テック",
        "stage": "Series B", "hq": "東京", "founded": 2019,
        "description": "ドローン＋AIによる建設現場進捗管理。写真測量と工程比較。",
        "website": "", "source": "bridge",
        "metrics": {"arr_mn_jpy": 480, "growth_yoy_pct": 102, "gross_margin": 70,
                    "nrr_pct": 118, "cac_months": 13, "runway_months": 20,
                    "employees": 68, "tam_bn_jpy": 350},
    },
    {
        "id": "con_004", "name": "PropertyAI", "sector": "建設・不動産テック",
        "stage": "Series A", "hq": "東京", "founded": 2020,
        "description": "不動産売買AIマッチング＆価格査定。仲介会社向けSaaS。",
        "website": "", "source": "initial",
        "metrics": {"arr_mn_jpy": 280, "growth_yoy_pct": 130, "gross_margin": 78,
                    "nrr_pct": 113, "cac_months": 12, "runway_months": 18,
                    "employees": 42, "tam_bn_jpy": 400},
    },
    {
        "id": "con_005", "name": "FacilityBot", "sector": "建設・不動産テック",
        "stage": "Series A", "hq": "名古屋", "founded": 2021,
        "description": "ビルオーナー向けAI設備管理＆予知保全。IoTセンサー統合。",
        "website": "", "source": "wantedly",
        "metrics": {"arr_mn_jpy": 190, "growth_yoy_pct": 165, "gross_margin": 73,
                    "nrr_pct": 117, "cac_months": 11, "runway_months": 15,
                    "employees": 31, "tam_bn_jpy": 280},
    },
    {
        "id": "con_006", "name": "CivicMap", "sector": "建設・不動産テック",
        "stage": "Series B", "hq": "東京", "founded": 2018,
        "description": "自治体向けインフラ点検AIシステム。橋梁・トンネルの亀裂検知。",
        "website": "", "source": "bridge",
        "metrics": {"arr_mn_jpy": 720, "growth_yoy_pct": 78, "gross_margin": 82,
                    "nrr_pct": 125, "cac_months": 22, "runway_months": 28,
                    "employees": 95, "tam_bn_jpy": 600},
    },
    {
        "id": "con_007", "name": "RenovAI", "sector": "建設・不動産テック",
        "stage": "Series A", "hq": "東京", "founded": 2022,
        "description": "リノベーション施工会社向けAI見積＆工程管理。B2B SaaS。",
        "website": "", "source": "pr_times",
        "metrics": {"arr_mn_jpy": 85, "growth_yoy_pct": 340, "gross_margin": 74,
                    "nrr_pct": 116, "cac_months": 7, "runway_months": 16,
                    "employees": 16, "tam_bn_jpy": 150},
    },
    {
        "id": "con_008", "name": "SmartZone", "sector": "建設・不動産テック",
        "stage": "Series B", "hq": "東京", "founded": 2019,
        "description": "商業施設テナント管理AI。賃料最適化＋空室予測。REIT運用向け。",
        "website": "", "source": "initial",
        "metrics": {"arr_mn_jpy": 560, "growth_yoy_pct": 88, "gross_margin": 79,
                    "nrr_pct": 121, "cac_months": 16, "runway_months": 22,
                    "employees": 74, "tam_bn_jpy": 450},
    },
    {
        "id": "con_009", "name": "HousingFlow", "sector": "建設・不動産テック",
        "stage": "Series A", "hq": "福岡", "founded": 2021,
        "description": "住宅建設会社向けAI顧客管理＆契約自動化。地場工務店特化。",
        "website": "", "source": "wantedly",
        "metrics": {"arr_mn_jpy": 120, "growth_yoy_pct": 220, "gross_margin": 75,
                    "nrr_pct": 114, "cac_months": 9, "runway_months": 13,
                    "employees": 20, "tam_bn_jpy": 100},
    },
    {
        "id": "con_010", "name": "WorkerTrack", "sector": "建設・不動産テック",
        "stage": "Series A", "hq": "大阪", "founded": 2020,
        "description": "建設作業員の入退場管理＆資格証書類AI管理。コンプライアンス自動化。",
        "website": "", "source": "pr_times",
        "metrics": {"arr_mn_jpy": 170, "growth_yoy_pct": 155, "gross_margin": 71,
                    "nrr_pct": 115, "cac_months": 10, "runway_months": 17,
                    "employees": 28, "tam_bn_jpy": 180},
    },
    {
        "id": "con_011", "name": "EnergyBIM", "sector": "建設・不動産テック",
        "stage": "Series B", "hq": "東京", "founded": 2018,
        "description": "建物エネルギー消費AI最適化。ZEB（ゼロエネルギービル）認証支援。",
        "website": "", "source": "bridge",
        "metrics": {"arr_mn_jpy": 390, "growth_yoy_pct": 98, "gross_margin": 77,
                    "nrr_pct": 119, "cac_months": 15, "runway_months": 24,
                    "employees": 55, "tam_bn_jpy": 320},
    },
    {
        "id": "con_012", "name": "ConstructDesk", "sector": "建設・不動産テック",
        "stage": "Seed", "hq": "東京", "founded": 2023,
        "description": "建設会社バックオフィスAI自動化（請求書・日報・労務管理）。",
        "website": "", "source": "initial",
        "metrics": {"arr_mn_jpy": 30, "growth_yoy_pct": 500, "gross_margin": 80,
                    "nrr_pct": 112, "cac_months": 5, "runway_months": 20,
                    "employees": 10, "tam_bn_jpy": 80},
    },

    # ══════════════════════════════════════════════════════════════
    # SECTOR 3: SMB向け金融インフラ
    # ══════════════════════════════════════════════════════════════

    {
        "id": "fin_001", "name": "LoanForge", "sector": "SMB向け金融インフラ",
        "stage": "Series A", "hq": "東京", "founded": 2023,
        "description": "中小企業向けAI融資審査プラットフォーム（銀行・信金向けSaaS）。",
        "website": "", "source": "simulation",
        "metrics": {"arr_mn_jpy": 85, "growth_yoy_pct": 280, "gross_margin": 81,
                    "nrr_pct": 131, "cac_months": 18, "runway_months": 22,
                    "employees": 32, "tam_bn_jpy": 1500},
    },
    {
        "id": "fin_002", "name": "InvoiceFlow", "sector": "SMB向け金融インフラ",
        "stage": "Series B", "hq": "東京", "founded": 2020,
        "description": "中小企業向けAI請求書ファクタリング＆早期資金化。即日審査。",
        "website": "", "source": "bridge",
        "metrics": {"arr_mn_jpy": 430, "growth_yoy_pct": 118, "gross_margin": 65,
                    "nrr_pct": 128, "cac_months": 6, "runway_months": 18,
                    "employees": 58, "tam_bn_jpy": 2000},
    },
    {
        "id": "fin_003", "name": "TaxSense", "sector": "SMB向け金融インフラ",
        "stage": "Series A", "hq": "東京", "founded": 2021,
        "description": "中小企業向けAI税務自動化（インボイス対応）。税理士補助ツール。",
        "website": "", "source": "pr_times",
        "metrics": {"arr_mn_jpy": 260, "growth_yoy_pct": 148, "gross_margin": 78,
                    "nrr_pct": 116, "cac_months": 8, "runway_months": 16,
                    "employees": 40, "tam_bn_jpy": 300},
    },
    {
        "id": "fin_004", "name": "PayrollAI", "sector": "SMB向け金融インフラ",
        "stage": "Series A", "hq": "大阪", "founded": 2021,
        "description": "中小企業向けAI給与計算＋人事・労務管理。社労士API連携。",
        "website": "", "source": "initial",
        "metrics": {"arr_mn_jpy": 195, "growth_yoy_pct": 168, "gross_margin": 76,
                    "nrr_pct": 114, "cac_months": 9, "runway_months": 15,
                    "employees": 35, "tam_bn_jpy": 220},
    },
    {
        "id": "fin_005", "name": "CreditScope", "sector": "SMB向け金融インフラ",
        "stage": "Series B", "hq": "東京", "founded": 2019,
        "description": "小売・飲食業向けAI売掛金管理＆与信スコアリング。POS連携。",
        "website": "", "source": "bridge",
        "metrics": {"arr_mn_jpy": 580, "growth_yoy_pct": 90, "gross_margin": 72,
                    "nrr_pct": 122, "cac_months": 11, "runway_months": 24,
                    "employees": 80, "tam_bn_jpy": 800},
    },
    {
        "id": "fin_006", "name": "BankBridge", "sector": "SMB向け金融インフラ",
        "stage": "Series A", "hq": "東京", "founded": 2022,
        "description": "地銀向けオープンバンキングAPI基盤。SMBのデータをFinTechに開放。",
        "website": "", "source": "pr_times",
        "metrics": {"arr_mn_jpy": 110, "growth_yoy_pct": 240, "gross_margin": 83,
                    "nrr_pct": 127, "cac_months": 16, "runway_months": 20,
                    "employees": 22, "tam_bn_jpy": 600},
    },
    {
        "id": "fin_007", "name": "ExpenseBot", "sector": "SMB向け金融インフラ",
        "stage": "Series A", "hq": "東京", "founded": 2021,
        "description": "中小企業向けAI経費精算自動化。レシートOCR＋承認ワークフロー。",
        "website": "", "source": "wantedly",
        "metrics": {"arr_mn_jpy": 145, "growth_yoy_pct": 185, "gross_margin": 79,
                    "nrr_pct": 115, "cac_months": 7, "runway_months": 17,
                    "employees": 25, "tam_bn_jpy": 180},
    },
    {
        "id": "fin_008", "name": "CashFlow AI", "sector": "SMB向け金融インフラ",
        "stage": "Series A", "hq": "名古屋", "founded": 2022,
        "description": "中小製造業向けAI資金繰り予測＆自動借入申請。3ヶ月先を可視化。",
        "website": "", "source": "initial",
        "metrics": {"arr_mn_jpy": 70, "growth_yoy_pct": 320, "gross_margin": 81,
                    "nrr_pct": 118, "cac_months": 8, "runway_months": 14,
                    "employees": 14, "tam_bn_jpy": 400},
    },
    {
        "id": "fin_009", "name": "AgriFinance", "sector": "SMB向け金融インフラ",
        "stage": "Series A", "hq": "北海道", "founded": 2021,
        "description": "農業法人向けAI農業融資審査＆収益管理。JAとの連携。",
        "website": "", "source": "pr_times",
        "metrics": {"arr_mn_jpy": 90, "growth_yoy_pct": 260, "gross_margin": 74,
                    "nrr_pct": 120, "cac_months": 13, "runway_months": 18,
                    "employees": 18, "tam_bn_jpy": 200},
    },
    {
        "id": "fin_010", "name": "InsureTech Japan", "sector": "SMB向け金融インフラ",
        "stage": "Series B", "hq": "東京", "founded": 2019,
        "description": "中小企業向けオンデマンド型ビジネス保険AI。リスクに応じた動的プライシング。",
        "website": "", "source": "bridge",
        "metrics": {"arr_mn_jpy": 340, "growth_yoy_pct": 105, "gross_margin": 68,
                    "nrr_pct": 119, "cac_months": 10, "runway_months": 22,
                    "employees": 48, "tam_bn_jpy": 700},
    },
    {
        "id": "fin_011", "name": "GrantAI", "sector": "SMB向け金融インフラ",
        "stage": "Series A", "hq": "東京", "founded": 2022,
        "description": "中小企業の補助金・助成金申請をAIが自動マッチング＆書類作成。",
        "website": "", "source": "wantedly",
        "metrics": {"arr_mn_jpy": 55, "growth_yoy_pct": 380, "gross_margin": 85,
                    "nrr_pct": 123, "cac_months": 5, "runway_months": 19,
                    "employees": 11, "tam_bn_jpy": 120},
    },
    {
        "id": "fin_012", "name": "TradeDesk AI", "sector": "SMB向け金融インフラ",
        "stage": "Series B", "hq": "東京", "founded": 2018,
        "description": "中小輸出企業向け貿易金融AI。信用状・為替リスク管理を自動化。",
        "website": "", "source": "bridge",
        "metrics": {"arr_mn_jpy": 510, "growth_yoy_pct": 82, "gross_margin": 71,
                    "nrr_pct": 117, "cac_months": 17, "runway_months": 26,
                    "employees": 65, "tam_bn_jpy": 900},
    },

    # ══════════════════════════════════════════════════════════════
    # SECTOR 4: サプライチェーン・物流AI
    # ══════════════════════════════════════════════════════════════

    {
        "id": "logi_001", "name": "LogiPath AI", "sector": "サプライチェーン・物流AI",
        "stage": "Series A", "hq": "東京", "founded": 2022,
        "description": "物流・サプライチェーンAI最適化SaaS。（既投資先）",
        "website": "", "source": "portfolio",
        "metrics": {"arr_mn_jpy": 230, "growth_yoy_pct": 188, "gross_margin": 76,
                    "nrr_pct": 121, "cac_months": 10, "runway_months": 14,
                    "employees": 42, "tam_bn_jpy": 600},
    },
    {
        "id": "logi_002", "name": "InventAI", "sector": "サプライチェーン・物流AI",
        "stage": "Series B", "hq": "東京", "founded": 2019,
        "description": "製造業向けAI需要予測＆在庫最適化。ERP連携。過剰在庫▲35%実績。",
        "website": "", "source": "bridge",
        "metrics": {"arr_mn_jpy": 490, "growth_yoy_pct": 95, "gross_margin": 73,
                    "nrr_pct": 120, "cac_months": 14, "runway_months": 22,
                    "employees": 70, "tam_bn_jpy": 800},
    },
    {
        "id": "logi_003", "name": "LastMileAI", "sector": "サプライチェーン・物流AI",
        "stage": "Series A", "hq": "大阪", "founded": 2021,
        "description": "宅配ラストマイルAIルート最適化。配達員の生産性+30%。",
        "website": "", "source": "pr_times",
        "metrics": {"arr_mn_jpy": 200, "growth_yoy_pct": 155, "gross_margin": 69,
                    "nrr_pct": 115, "cac_months": 11, "runway_months": 15,
                    "employees": 32, "tam_bn_jpy": 400},
    },
    {
        "id": "logi_004", "name": "WareBot", "sector": "サプライチェーン・物流AI",
        "stage": "Series B", "hq": "愛知", "founded": 2018,
        "description": "倉庫内ロボット制御AIソフト。既存フォークリフト＋AI制御で自動化。",
        "website": "", "source": "bridge",
        "metrics": {"arr_mn_jpy": 680, "growth_yoy_pct": 88, "gross_margin": 72,
                    "nrr_pct": 122, "cac_months": 16, "runway_months": 24,
                    "employees": 88, "tam_bn_jpy": 700},
    },
    {
        "id": "logi_005", "name": "ColdChainAI", "sector": "サプライチェーン・物流AI",
        "stage": "Series A", "hq": "東京", "founded": 2020,
        "description": "食品・医薬品コールドチェーン温度管理AI。異常予知とコンプライアンス自動記録。",
        "website": "", "source": "wantedly",
        "metrics": {"arr_mn_jpy": 165, "growth_yoy_pct": 175, "gross_margin": 77,
                    "nrr_pct": 119, "cac_months": 12, "runway_months": 16,
                    "employees": 28, "tam_bn_jpy": 300},
    },
    {
        "id": "logi_006", "name": "PortAI", "sector": "サプライチェーン・物流AI",
        "stage": "Series B", "hq": "横浜", "founded": 2019,
        "description": "港湾コンテナ物流AIシステム。荷役スケジュール最適化＆遅延予測。",
        "website": "", "source": "initial",
        "metrics": {"arr_mn_jpy": 380, "growth_yoy_pct": 110, "gross_margin": 70,
                    "nrr_pct": 118, "cac_months": 18, "runway_months": 20,
                    "employees": 52, "tam_bn_jpy": 500},
    },
    {
        "id": "logi_007", "name": "ProcureAI", "sector": "サプライチェーン・物流AI",
        "stage": "Series A", "hq": "東京", "founded": 2021,
        "description": "製造業向けAI調達最適化。サプライヤー評価＋価格交渉支援自動化。",
        "website": "", "source": "pr_times",
        "metrics": {"arr_mn_jpy": 130, "growth_yoy_pct": 200, "gross_margin": 78,
                    "nrr_pct": 117, "cac_months": 13, "runway_months": 17,
                    "employees": 22, "tam_bn_jpy": 350},
    },
    {
        "id": "logi_008", "name": "TransparAI", "sector": "サプライチェーン・物流AI",
        "stage": "Series A", "hq": "東京", "founded": 2022,
        "description": "サプライチェーン可視化AI。ESG・CO2排出量の自動トレーサビリティ。",
        "website": "", "source": "initial",
        "metrics": {"arr_mn_jpy": 95, "growth_yoy_pct": 290, "gross_margin": 80,
                    "nrr_pct": 123, "cac_months": 9, "runway_months": 18,
                    "employees": 18, "tam_bn_jpy": 250},
    },
    {
        "id": "logi_009", "name": "AgriChain", "sector": "サプライチェーン・物流AI",
        "stage": "Series A", "hq": "宮崎", "founded": 2021,
        "description": "農産物流通AIプラットフォーム。産地→スーパーの直接マッチング＆物流最適化。",
        "website": "", "source": "wantedly",
        "metrics": {"arr_mn_jpy": 110, "growth_yoy_pct": 235, "gross_margin": 68,
                    "nrr_pct": 114, "cac_months": 10, "runway_months": 14,
                    "employees": 20, "tam_bn_jpy": 200},
    },
    {
        "id": "logi_010", "name": "FreightFlow", "sector": "サプライチェーン・物流AI",
        "stage": "Series B", "hq": "大阪", "founded": 2019,
        "description": "中小運送会社向けAI配車管理＆ドライバー労務管理。2024年問題対応。",
        "website": "", "source": "bridge",
        "metrics": {"arr_mn_jpy": 410, "growth_yoy_pct": 105, "gross_margin": 71,
                    "nrr_pct": 116, "cac_months": 12, "runway_months": 20,
                    "employees": 58, "tam_bn_jpy": 450},
    },
    {
        "id": "logi_011", "name": "QualityAI", "sector": "サプライチェーン・物流AI",
        "stage": "Series A", "hq": "愛知", "founded": 2020,
        "description": "製造業品質検査AI。ライン上の目視検査を画像AIで自動化。不良品▲90%。",
        "website": "", "source": "pr_times",
        "metrics": {"arr_mn_jpy": 175, "growth_yoy_pct": 168, "gross_margin": 75,
                    "nrr_pct": 120, "cac_months": 11, "runway_months": 16,
                    "employees": 30, "tam_bn_jpy": 300},
    },
    {
        "id": "logi_012", "name": "RetailOps", "sector": "サプライチェーン・物流AI",
        "stage": "Series A", "hq": "東京", "founded": 2022,
        "description": "小売チェーン向けAI発注最適化＆ロス削減。POSデータ × 気象API連携。",
        "website": "", "source": "initial",
        "metrics": {"arr_mn_jpy": 140, "growth_yoy_pct": 195, "gross_margin": 76,
                    "nrr_pct": 118, "cac_months": 8, "runway_months": 17,
                    "employees": 24, "tam_bn_jpy": 280},
    },

    # ══════════════════════════════════════════════════════════════
    # SECTOR 5: 法務・バックオフィス自動化
    # ══════════════════════════════════════════════════════════════

    {
        "id": "leg_001", "name": "ContractAI", "sector": "法務・バックオフィス自動化",
        "stage": "Series B", "hq": "東京", "founded": 2019,
        "description": "企業向けAI契約書レビュー＆管理SaaS。弁護士事務所API連携。",
        "website": "", "source": "bridge",
        "metrics": {"arr_mn_jpy": 550, "growth_yoy_pct": 112, "gross_margin": 82,
                    "nrr_pct": 126, "cac_months": 13, "runway_months": 24,
                    "employees": 78, "tam_bn_jpy": 400},
    },
    {
        "id": "leg_002", "name": "CompliAI", "sector": "法務・バックオフィス自動化",
        "stage": "Series A", "hq": "東京", "founded": 2021,
        "description": "金融機関向けAIコンプライアンス監視。取引監視＆規制報告自動化。",
        "website": "", "source": "pr_times",
        "metrics": {"arr_mn_jpy": 230, "growth_yoy_pct": 158, "gross_margin": 80,
                    "nrr_pct": 128, "cac_months": 16, "runway_months": 20,
                    "employees": 38, "tam_bn_jpy": 350},
    },
    {
        "id": "leg_003", "name": "HRAutomate", "sector": "法務・バックオフィス自動化",
        "stage": "Series A", "hq": "東京", "founded": 2021,
        "description": "中堅企業向けAI人事労務自動化（採用〜退職まで）。電子署名連携。",
        "website": "", "source": "initial",
        "metrics": {"arr_mn_jpy": 185, "growth_yoy_pct": 172, "gross_margin": 78,
                    "nrr_pct": 116, "cac_months": 10, "runway_months": 16,
                    "employees": 32, "tam_bn_jpy": 250},
    },
    {
        "id": "leg_004", "name": "PatentAI", "sector": "法務・バックオフィス自動化",
        "stage": "Series A", "hq": "東京", "founded": 2020,
        "description": "特許事務所向けAI明細書作成支援＆先行技術調査自動化。",
        "website": "", "source": "wantedly",
        "metrics": {"arr_mn_jpy": 145, "growth_yoy_pct": 190, "gross_margin": 83,
                    "nrr_pct": 122, "cac_months": 12, "runway_months": 18,
                    "employees": 24, "tam_bn_jpy": 180},
    },
    {
        "id": "leg_005", "name": "DocuFlow", "sector": "法務・バックオフィス自動化",
        "stage": "Series B", "hq": "東京", "founded": 2018,
        "description": "企業向けAIドキュメント管理＆承認ワークフロー。電子帳簿保存法対応。",
        "website": "", "source": "bridge",
        "metrics": {"arr_mn_jpy": 620, "growth_yoy_pct": 92, "gross_margin": 79,
                    "nrr_pct": 120, "cac_months": 11, "runway_months": 26,
                    "employees": 85, "tam_bn_jpy": 500},
    },
    {
        "id": "leg_006", "name": "AuditBot", "sector": "法務・バックオフィス自動化",
        "stage": "Series A", "hq": "大阪", "founded": 2021,
        "description": "中堅企業向けAI内部監査自動化。リスク評価＆監査証跡の自動生成。",
        "website": "", "source": "pr_times",
        "metrics": {"arr_mn_jpy": 105, "growth_yoy_pct": 250, "gross_margin": 81,
                    "nrr_pct": 125, "cac_months": 14, "runway_months": 17,
                    "employees": 19, "tam_bn_jpy": 200},
    },
    {
        "id": "leg_007", "name": "PrivacyGuard", "sector": "法務・バックオフィス自動化",
        "stage": "Series A", "hq": "東京", "founded": 2022,
        "description": "企業向けAI個人情報管理（改正個人情報保護法対応）。自動マスキング。",
        "website": "", "source": "initial",
        "metrics": {"arr_mn_jpy": 80, "growth_yoy_pct": 340, "gross_margin": 84,
                    "nrr_pct": 121, "cac_months": 8, "runway_months": 19,
                    "employees": 15, "tam_bn_jpy": 150},
    },
    {
        "id": "leg_008", "name": "DisputeAI", "sector": "法務・バックオフィス自動化",
        "stage": "Series A", "hq": "東京", "founded": 2021,
        "description": "法律事務所向けAI訴訟戦略支援＆判例検索。弁護士の初期調査▲70%。",
        "website": "", "source": "wantedly",
        "metrics": {"arr_mn_jpy": 120, "growth_yoy_pct": 210, "gross_margin": 82,
                    "nrr_pct": 119, "cac_months": 11, "runway_months": 15,
                    "employees": 21, "tam_bn_jpy": 160},
    },
    {
        "id": "leg_009", "name": "RegTrack", "sector": "法務・バックオフィス自動化",
        "stage": "Series B", "hq": "東京", "founded": 2019,
        "description": "製薬・食品・金融向けAI規制変更モニタリング＆対応タスク管理。",
        "website": "", "source": "bridge",
        "metrics": {"arr_mn_jpy": 370, "growth_yoy_pct": 118, "gross_margin": 81,
                    "nrr_pct": 124, "cac_months": 15, "runway_months": 22,
                    "employees": 50, "tam_bn_jpy": 300},
    },
    {
        "id": "leg_010", "name": "CorpSec AI", "sector": "法務・バックオフィス自動化",
        "stage": "Series A", "hq": "東京", "founded": 2022,
        "description": "上場企業向けAI株主総会準備＆開示書類自動化。IR部門の工数▲60%。",
        "website": "", "source": "pr_times",
        "metrics": {"arr_mn_jpy": 90, "growth_yoy_pct": 300, "gross_margin": 83,
                    "nrr_pct": 122, "cac_months": 10, "runway_months": 17,
                    "employees": 16, "tam_bn_jpy": 120},
    },
    {
        "id": "leg_011", "name": "SourcingCheck", "sector": "法務・バックオフィス自動化",
        "stage": "Series A", "hq": "東京", "founded": 2021,
        "description": "企業向けサプライヤーコンプライアンスAI（人権DD・ESG）。欧州規制対応。",
        "website": "", "source": "initial",
        "metrics": {"arr_mn_jpy": 160, "growth_yoy_pct": 185, "gross_margin": 79,
                    "nrr_pct": 118, "cac_months": 13, "runway_months": 16,
                    "employees": 27, "tam_bn_jpy": 220},
    },
    {
        "id": "leg_012", "name": "MeetingMind", "sector": "法務・バックオフィス自動化",
        "stage": "Series A", "hq": "東京", "founded": 2022,
        "description": "企業向けAI議事録自動生成＆アクション管理。Zoom/Teams統合。",
        "website": "", "source": "wantedly",
        "metrics": {"arr_mn_jpy": 65, "growth_yoy_pct": 420, "gross_margin": 85,
                    "nrr_pct": 113, "cac_months": 4, "runway_months": 21,
                    "employees": 12, "tam_bn_jpy": 100},
    },
]



# ── LP seed data ──────────────────────────────────────────────────────────────
#
# 2026-08-09 の調査（research/FINDINGS_lp_universe.md）で実在が確認できた主体のみ。
# それ以前のシードは全件フィクションだったため削除した。
#
# confidence の意味:
#   中     — 複数の独立ソース（公式リリース・日経等）が一致。ただし原文は未読
#   低     — 単一の検索スニペットのみ。再検索で未再現
#   未調査 — ソース取得に失敗し、クレームを1件も抽出できなかった
#
# ⚠️ 本調査ではネットワークegress制限により一次ソースを1件も直接読めていない。
#    confidence「高」は存在しない。数値を外部資料へ転記する前に §7 の検証を通すこと。

_SRC_COALIS   = "https://www.mizuhobank.co.jp/release/pdf/20251009release_jp.pdf"
_SRC_FIDUCIA  = "https://prtimes.jp/main/html/rd/p/000000001.000096346.html"
_SRC_SMRJ     = "https://www.smrj.go.jp/supporter/fund_investment/index.html"

LP_SEED: list[dict] = [

    # ── Tier 1: 政府系・準政府系 ────────────────────────────────────────────
    {
        "org_name": "独立行政法人 中小企業基盤整備機構", "tier": "tier1",
        "lp_type": "政府系", "status": "prospect",
        "first_time_fund_ok": "実績あり", "access_route": "公募",
        "track_record_req": "不明（要件PDF未入手）",
        "recent_activity": "SCCM1号に30億円出資決定・2025/10/01組成（要検証）／One Capital 1号の追加募集に参画（要検証）",
        "notes": "現在アクティブな公募3件を確認: 中小企業経営力強化支援出資事業／同 第2回サーチファンド型／再生支援出資事業。"
                 "ファンド出資事業は起業支援・中小企業成長支援・事業承継型の3類型。"
                 "出資比率上限・最低ファンド総額・GP要件・中小企業限定の目的制限はいずれも未取得。"
                 "『中小企業経営力強化支援ファンド出資事業の主な要件』PDFの入手が最優先。",
        "source_url": _SRC_SMRJ, "as_of": "2026-08-09", "confidence": "中",
    },
    {
        "org_name": "株式会社産業革新投資機構（JIC）", "tier": "tier1",
        "lp_type": "政府系", "status": "prospect",
        "first_time_fund_ok": "不明", "access_route": "不明",
        "notes": "今回ソース取得に失敗（claimCount 0）。まったく手つかず。次回調査の最優先。",
        "source_url": "https://www.j-ic.co.jp/", "as_of": "2026-08-09", "confidence": "未調査",
    },
    {
        "org_name": "株式会社日本政策投資銀行（DBJ）", "tier": "tier1",
        "lp_type": "政府系", "status": "prospect",
        "first_time_fund_ok": "不明", "access_route": "不明",
        "notes": "今回ソース取得に失敗（claimCount 0）。未調査。",
        "source_url": "https://www.dbj.jp/", "as_of": "2026-08-09", "confidence": "未調査",
    },
    {
        "org_name": "株式会社地域経済活性化支援機構（REVIC）", "tier": "tier1",
        "lp_type": "政府系", "status": "prospect",
        "first_time_fund_ok": "不明", "access_route": "不明",
        "notes": "今回ソース取得に失敗（claimCount 0）。未調査。",
        "source_url": "https://www.revic.co.jp/business/lp/index.html",
        "as_of": "2026-08-09", "confidence": "未調査",
    },

    # ── Tier 2: ゲートキーパー / FoF ───────────────────────────────────────
    {
        "org_name": "AI Capital株式会社", "tier": "tier2",
        "lp_type": "独立系FoF", "status": "prospect",
        "first_time_fund_ok": "実績あり", "access_route": "不明",
        "recent_activity": "Fiducia GrowthTech 1号（FC 32.6億円）にLP参加（要検証）",
        "notes": "Pyreneeに最も規模が近いFiducia 1号のLPとして名前が挙がった主体。"
                 "ただし単一スニペットのみで再検索では未再現。最優先の要検証先。",
        "source_url": _SRC_FIDUCIA, "as_of": "2026-08-09", "confidence": "低",
    },
    {
        "org_name": "ニッセイアセットマネジメント株式会社", "tier": "tier2",
        "lp_type": "FoF（生保系）", "status": "prospect",
        "first_time_fund_ok": "可", "access_route": "不明",
        "recent_activity": "NISSAY Startup Support Fund I を2024/02/22新設（300億円・期間20年）",
        "notes": "EMP（新興運用者への資金供給プログラム）に資する取組と位置づけ、"
                 "『優良な新興運用者』を投資対象に明記。ただし投資対象は『国内ベンチャーキャピタルが"
                 "運用するファンド』と限定されており、グロースエクイティPEのPyreneeは対象外の可能性。"
                 "資金源は日本生命の自己勘定であり企業年金マネーではない。要確認。",
        "source_url": "https://www.nam.co.jp/news/info/240222.html",
        "as_of": "2026-08-09", "confidence": "低",
    },

    # ── Tier 3: 地域金融機関・大学系 ───────────────────────────────────────
    {
        "org_name": "株式会社南都銀行", "tier": "tier3",
        "lp_type": "地方銀行", "status": "prospect",
        "first_time_fund_ok": "実績あり", "access_route": "不明",
        "recent_activity": "Fiducia GrowthTech 1号（FC 32.6億円）にLP参加（要検証）",
        "notes": "奈良県の地銀。運用実績のない1号ファンドに実名でLP参加したとされる事例。"
                 "事実なら『地銀は実績要件で門前払い』という前提への反証になる。単一スニペットのため要検証。",
        "source_url": _SRC_FIDUCIA, "as_of": "2026-08-09", "confidence": "低",
    },
    {
        "org_name": "東京理科大学インベストメント・マネジメント株式会社", "tier": "tier3",
        "lp_type": "大学系運用法人", "status": "prospect",
        "first_time_fund_ok": "実績あり", "access_route": "不明",
        "recent_activity": "Fiducia GrowthTech 1号にLP参加（要検証）",
        "notes": "大学系運用法人が1号ファンドのLPになった事例。単一スニペットのため要検証。",
        "source_url": _SRC_FIDUCIA, "as_of": "2026-08-09", "confidence": "低",
    },

    # ── Tier 4: 事業会社・CVC・金融機関 ────────────────────────────────────
    {
        "org_name": "株式会社みずほ銀行", "tier": "tier4",
        "lp_type": "メガバンク", "status": "prospect",
        "first_time_fund_ok": "実績あり", "access_route": "不明",
        "recent_activity": "Coalis1号に最大65億円を出資（2025/10/09 FC）",
        "notes": "総額200億円予定のファンドに対し約32.5%相当。単一LPが『総額の10〜20%以内』という"
                 "一般則を超えて1号ファンドに出資した実例。ただし対象は200億円ファンドであり、"
                 "50億円ファンドに同水準が出る根拠にはならない。同社公式PDF・日経・PR TIMESの3経路で一致。",
        "source_url": _SRC_COALIS, "as_of": "2026-08-09", "confidence": "中",
    },
    {
        "org_name": "住友商事株式会社", "tier": "tier4",
        "lp_type": "総合商社", "status": "prospect",
        "first_time_fund_ok": "実績あり", "access_route": "不明",
        "recent_activity": "Coalis1号に最大50億円を出資（2025/10/09 FC）",
        "notes": "自社公式リリースあり（sumitomocorp.com/ja/jp/news/release/2025/group/20430）。"
                 "『国内初、グロース期のスタートアップにマジョリティ投資する専門ファンドに参画』。",
        "source_url": "https://www.sumitomocorp.com/ja/jp/news/release/2025/group/20430",
        "as_of": "2026-08-09", "confidence": "中",
    },
    {
        "org_name": "SOMPO Growth Partners株式会社", "tier": "tier4",
        "lp_type": "CVC", "status": "prospect",
        "first_time_fund_ok": "実績あり", "access_route": "不明",
        "recent_activity": "Coalis1号にLP参加（2025/10/09 FC）。出資額は非公表",
        "notes": "SOMPOグループのCVC。CVCが1号ファンドの外部LPになった事例。",
        "source_url": _SRC_COALIS, "as_of": "2026-08-09", "confidence": "中",
    },
    {
        "org_name": "三井住友信託銀行株式会社", "tier": "tier4",
        "lp_type": "信託銀行", "status": "prospect",
        "first_time_fund_ok": "実績あり", "access_route": "不明",
        "recent_activity": "Coalis1号にLP参加（2025/10/09 FC）。出資額は非公表",
        "notes": "信託銀行が1号ファンドのLPになった事例。企業年金の運用受託機関でもあるため、"
                 "Tier 5（企業年金）への導線としても意味を持つ可能性。",
        "source_url": _SRC_COALIS, "as_of": "2026-08-09", "confidence": "中",
    },
]


# ── 1号ファンドの前例（設問1の回答の実体） ────────────────────────────────
#
# Pyrenee Capital I（目標50億円 / FC 20億円）が、過去の1号ファンドと比べて
# どの規模帯に位置するかを示すための実例集。

PRECEDENT_SEED: list[dict] = [
    {
        "fund_name": "Coalis1号投資事業有限責任組合", "manager": "株式会社Coalis Capital",
        "fund_number": "1号", "target_mn_jpy": 20000, "first_close_mn_jpy": None,
        "close_date": "2025-10-09", "strategy": "スタートアップ特化グロースバイアウト（マジョリティ取得）",
        "lps": "みずほ銀行(最大65億)／住友商事(最大50億)／SOMPO Growth Partners／三井住友信託銀行",
        "source_url": _SRC_COALIS, "confidence": "中",
        "notes": "運用会社は2024年設立。中小機構の関与は再検索で確認できず、"
                 "調査中に出た『中小機構30億円』はSCCM1号との混同の可能性が高い。",
    },
    {
        "fund_name": "ALPHA-1投資事業有限責任組合", "manager": "株式会社alpha",
        "fund_number": "1号", "target_mn_jpy": 15000, "first_close_mn_jpy": 10000,
        "close_date": "2025-07", "strategy": "VC",
        "lps": "機関投資家が約85%（実名は取得できず）",
        "source_url": "https://alphavc.jp/posts/ALPHA1_firstclose", "confidence": "低",
        "notes": "GP3名の個人としての投資実績（90社超投資・イグジット40社超・IPO25社）が"
                 "ファンド実績の代替として評価されたとされる。目標150億円・最大200億円。",
    },
    {
        "fund_name": "One Capital 1号ファンド", "manager": "One Capital株式会社",
        "fund_number": "1号", "target_mn_jpy": 16000, "first_close_mn_jpy": None,
        "close_date": "2021-05", "strategy": "VC（SaaS/クラウド）",
        "lps": "中小機構が追加募集に参画（要検証）",
        "source_url": "https://thebridge.jp/2021/05/one-capital-1st-fund-final-close",
        "confidence": "低",
        "notes": "当初目標50億円 = Pyreneeと同額。最終160億円で目標の3倍超に着地。",
    },
    {
        "fund_name": "SCCM1号投資事業有限責任組合", "manager": "SynClover Capital Management",
        "fund_number": "1号", "target_mn_jpy": None, "first_close_mn_jpy": None,
        "close_date": "2025-10-01", "strategy": "不明",
        "lps": "中小機構(30億円・出資決定)",
        "source_url": "https://www.smrj.go.jp/sme/funding/fund/news/fbrion0000001zma-att/hkj3i800000069x3.pdf",
        "confidence": "低",
        "notes": "PDF原本がegress遮断で未読。中小機構が1号ファンドへ単独30億円を出した事例として重要だが要検証。",
    },
    {
        "fund_name": "Fiducia GrowthTech有限責任投資事業組合", "manager": "Fiducia株式会社",
        "fund_number": "1号", "target_mn_jpy": None, "first_close_mn_jpy": 3260,
        "close_date": "2024", "strategy": "テクノロジー／社会課題解決",
        "lps": "AI Capital／東京理科大学インベストメント・マネジメント／南都銀行／Pavilion Capital（いずれも要検証）",
        "source_url": _SRC_FIDUCIA, "confidence": "低",
        "notes": "★Pyrenee Capital I（FC 20億円）に最も規模が近い前例。FC 32.6億円。"
                 "LP構成が『独立系FoF＋大学系＋地銀＋海外FoF』であれば、Pyreneeの現実的なテンプレートになる。",
    },
    {
        "fund_name": "Pyrenee Capital I（自社・参考）", "manager": "Pyrenee Capital",
        "fund_number": "1号", "target_mn_jpy": 5000, "first_close_mn_jpy": 2000,
        "close_date": "2026（予定）", "strategy": "国内グロースエクイティ（AI-native縦型SaaS）",
        "lps": "—", "source_url": "", "confidence": "—",
        "notes": "比較用。前例のうちFiducia以外はすべて100億円超であり、本ファンドは最小規模帯にあたる。",
    },
]
