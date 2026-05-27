# SpaceX is private; these are publicly traded space/launch-sector proxies
SPACEX_RELATED = [
    ("RKLB", "Rocket Lab USA - 小型衛星打ち上げ直接競合"),
    ("SPCE", "Virgin Galactic - 宇宙旅行"),
    ("ASTS", "AST SpaceMobile - 衛星携帯通信"),
    ("LUNR", "Intuitive Machines - 月面ミッション"),
    ("LMT",  "Lockheed Martin - 防衛・宇宙"),
    ("BA",   "Boeing - 宇宙船・防衛"),
    ("NOC",  "Northrop Grumman - 宇宙・防衛"),
    ("RTX",  "Raytheon Technologies - 防衛・宇宙"),
    ("KTOS", "Kratos Defense - 宇宙・ドローン"),
    ("RDW",  "Redwire - 宇宙インフラ"),
    ("ASTR", "Astra Space - 小型ロケット"),
    ("UFO",  "Procure Space ETF - 宇宙セクターETF"),
    ("ARKX", "ARK Space Exploration ETF - 宇宙探索ETF"),
]

# Anthropic is private; these are publicly traded AI/LLM-sector proxies
ANTHROPIC_RELATED = [
    ("GOOGL", "Alphabet - Anthropic投資家・Gemini競合"),
    ("AMZN",  "Amazon - Anthropic主要投資家"),
    ("MSFT",  "Microsoft - OpenAI経由でLLM競合"),
    ("META",  "Meta - Llama OSS競合"),
    ("NVDA",  "NVIDIA - AI学習インフラ"),
    ("AI",    "C3.ai - 企業向けAI"),
    ("PLTR",  "Palantir - AI・データ分析"),
    ("SOUN",  "SoundHound AI - 音声AI"),
    ("BBAI",  "BigBear.ai - 意思決定AI"),
    ("IONQ",  "IonQ - 量子コンピュータ"),
    ("SMCI",  "Super Micro Computer - AIサーバー"),
    ("ARM",   "Arm Holdings - AIチップ設計"),
]

# Simulation / digital-twin / gaming engine companies
SIMULATOR_RELATED = [
    ("ANSS",  "Ansys - シミュレーションソフト最大手"),
    ("CDNS",  "Cadence Design Systems - 設計シミュレーション"),
    ("SNPS",  "Synopsys - 半導体シミュレーション"),
    ("U",     "Unity Technologies - ゲームエンジン・産業シミュレーション"),
    ("NVDA",  "NVIDIA Omniverse - 物理シミュレーション"),
    ("META",  "Meta - VR/ARシミュレーション"),
    ("CAE",   "CAE Inc. - フライトシミュレーター"),
    ("MSFT",  "Microsoft - Azure Digital Twins"),
    ("PTC",   "PTC Inc. - 産業デジタルツイン"),
    ("RBLX",  "Roblox - メタバース・シミュレーション"),
]

ALL_WATCHLIST = {
    "spacex": SPACEX_RELATED,
    "anthropic": ANTHROPIC_RELATED,
    "simulator": SIMULATOR_RELATED,
}

def get_all_tickers() -> list[str]:
    seen = set()
    result = []
    for items in ALL_WATCHLIST.values():
        for ticker, _ in items:
            if ticker not in seen:
                seen.add(ticker)
                result.append(ticker)
    return result
