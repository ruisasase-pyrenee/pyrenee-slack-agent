# Pyreneeのすべて（社内ナレッジ）

最終更新：2026-10-07
出典：Notion（WEBサイト構成案、採用ページ、Rui's America Plan、Rising Act Films管理ページ）、Google Drive（会社案内 / PitchDeck April 2025、Tech Ranch VRA エントリーフォーム、プロジェクト設定メモ 2026-06-05）、Slack、公開ニュース記事。
数値は資料ごとに表記ゆれがあるため、外部に出す前に必ず最新の一次資料で確認すること。

---

## 1. 会社概要

| 項目 | 日本法人 | 米国法人 |
|---|---|---|
| 社名 | 株式会社Pyrenee（ピレニー） | Pyrenee Inc. |
| 設立 | 2016年1月（1月7日） | 2016年4月 |
| 登記・所在地 | 東京都中央区晴海4-7-4 CROSS DOCK HARUMI 601 | 米国デラウェア州（Delaware C-Corp）／所在地 Palo Alto, CA |
| 代表 | 代表取締役CEO 三野 龍太（Ryuta Mino） | CEO Ryuta Mino |

- 資本構成：米国法人 Pyrenee Inc. が親会社。
- 従業員：約10名。
- Web：https://www.pyrenee.net ／ 英語 https://www.pyrenee.net/en
- 米国拠点：Japan Innovation Campus（JIC）, 212 Homer Ave, Palo Alto, CA 94301
- 事業内容：AIドライバーアシスタントの開発・生産・販売、交通データの収集と解析。

### ビジョン・ミッション
- **世界中から交通事故をなくす。**
- 人間の相棒（Buddy）になるAIを世界に広げる。「毎日をよりよくする人間の相棒をつくる」。

### 社名の由来
フランス・ピレニー山脈で、羊飼いの家族と羊たちをオオカミや熊から守る、強くてやさしい「ピレニー犬（グレート・ピレニーズ）」に由来。ピレニー犬のように人の相棒になるプロダクトをつくる、という意思を込めている。

### 製品構想（Personal AI Buddy）
- **Pyrenee AI Buddy**：ユーザーごとに1体ずつ個別に生成される、人間の相棒になるAI。
- **Body**：AI Buddyが入って活躍する器。Body for Driving（= Pyrenee Drive）、Body for Kids、Body for Home など（Ring / Home / Shape / Glass 等の構想あり）。
- 最初の製品が **Pyrenee Drive**。

---

## 2. プロダクト：Pyrenee Drive

### 一言で
既存の車に後付けできるAI運転アシスタント。シガーソケットに挿すだけ・工事不要で、ほぼすべての車に取り付けられる。ドライバーの「第2の目」かつ話し相手になる。

### 解決する課題
- 交通事故で毎年 **約135万人** が死亡、**約5,000万人** が負傷、経済損失は **約300兆円**。
- 子どもと29歳以下の若者にとっては、交通事故が最大の死因。
- 死亡事故の9割以上は「見落とし」と「判断ミス」が原因（科学警察研究所）。事故の4件に3件は見落としによるもの。
- 米国では年間42,000人以上が交通事故で死亡し、その大半はヒューマンエラーが原因。

### ポジショニング（事故の3段階）
| 段階 | 対策 | 既存手段 |
|---|---|---|
| 第1段階：原因発生（見落とし等） | **プリベンティブセーフティ（予防安全）** | **Pyrenee Drive**（ここに有効な対策が存在しなかった） |
| 第2段階：衝突に向かう | アクティブセーフティ | 衝突軽減ブレーキ（防げる事故は2〜3割） |
| 第3段階：事故発生 | パッシブセーフティ | エアバッグ、シートベルト |

### 主な機能
1. **事故防止**：ステレオカメラで前方を3Dで捉え、ディープラーニングで歩行者・車両・バイク・自転車を認識。すべての対象の動きを同時に追跡し、衝突コースに入ると「右に人がいる！」「左から車が来ている！」と音声と画面で即座に警告。
2. **学習し進化する危険予測**：全デバイスがクラウドでつながり、各車両が経験したシーンを追加学習して危険予測が進化し続ける。
3. **道案内（ナビ）**：カメラ映像から目印を見つけて案内。行き先の相談にも乗る。
4. **オンラインドライブレコーダー**：Full HD・夜間も明るく撮影。重要シーンはクラウドへ自動アップロードし、スマホで確認・共有できる。
5. **話し相手・エンタメ**：会話、クイズ、豆知識、おみくじ、子ども向けミニゲーム、音楽再生。1台1台が個別IDを持つ専属アシスタント。
6. **通話・家族や職場とのやりとり、テレマティクス**。法人車両向けの業務機能も提供予定。
7. **購入後もアップデート**：OTAで新機能を追加。
8. **ユーザー同士のつながり**：走行映像のシェア、災害時の情報共有など。
9. **データ収集と活用**：利用許諾を得た運転・交通・街のデータを研究開発、市街地情報、地図更新に活用。

### キャラクター
フレンドリーな音声で、敬語を使わない「ドラえもん」的な相棒。ブランドの比喩は **Iron Man**（人間の能力を拡張するAI）。

### 製品仕様（会社案内 2025年4月版＋最新メモ）
| 部品 | スペック |
|---|---|
| SoC | NVIDIA Jetson Orin NX（GPU/CPU） |
| フロントカメラ | Full HD ステレオカメラ（各約200万画素）、視野角 約100〜120° |
| ドライバーカメラ | Full HD シングルカメラ、視野角120° 広角 |
| ディスプレイ | 6.5インチ タッチパネル液晶（1,920×480） |
| 通信 | 4G/LTE、Wi-Fi、Bluetooth、GPS |
| センサー | 加速度、ジャイロ、温度、照度、気圧 |
| その他 | ステレオスピーカー、マイク |
| 電源 | シガーソケット 12V（全世界共通なので同じ仕様で世界展開できる） |

### 価格・発売
- 価格：本体10万円台前半（約$700〜900）＋月額使用料。
- 発売予定：**2027年1月（2027年初頭）**。日米での並行展開を想定。
- 実証実験：千葉で2026年5月末から実施中（ADAS・ステレオカメラの録画とIMUのデータ取得、遅延改善などを継続中）。
- 予約：**150台のプレオーダーを確保済み**。

### 実績・受賞
- NVIDIA Inception Partner
- グッドデザイン賞 2019
- Japan Innovation Campus（JIC, Palo Alto）採択
- 2019年7月：シャープと量産支援で契約
- 元ソニー会長の故・出井伸之氏がアドバイザー・投資家
- YC Summer 2026 に申請（締切 2026年5月4日）

### 競合
| 競合 | 弱点 | Pyreneeの違い |
|---|---|---|
| Mobileye | 業務的でパーソナライズがない。主に新車向け | Pyreneeはドライバーの「パートナー」。既存車に後付けできる |
| Comma.ai | ハッカー向け・DIY前提 | Pyreneeは全車種・全ユーザーが対象 |
| 既存の後付けADAS・ドラレコ | 事後の記録が中心。設置が複雑で長期契約に縛られる | 事故が起きる「前に」予測して警告する |
| ドライバーモニタリング | 監視・罰則的と受け取られて反発されやすい | 相棒として寄り添う体験 |

---

## 3. 市場

- 対象：乗用車、トラック、バス、タクシー、社有車などすべての車種。
- 国内 7,800万台（乗用車5,500万／トラック1,430万／社有車800万／バス・タクシー50万）。
- 世界 15.7億台（米国2億9,200万、中国2億9,400万、その他先進国4億2,500万、新興国4億8,500万）。
- 米国：自動運転に対応していない既存車が2億8,000万台以上（約2億8,900万台）。
- 販売チャネル候補：カーディーラー、運送会社、カーリース。

### 米国向けピッチ（SCR）
- **Situation**：米国には自動運転非対応の既存車が2億8,000万台以上ある。
- **Complication**：交通事故の約70%は「認知の欠落（見落とし）」が原因。一方でOEMの安全技術は新車にしか届かない。
- **Resolution**：Pyrenee Driveは、既存車に後付けでAI予防安全を届けられる唯一の選択肢。

---

## 4. 資金調達

- **累計調達：約12.8〜13億円**（資金はほぼ日本法人に投入済み。米国法人の手元資金はほぼゼロ）。
  - ※Tech Ranchのエントリーフォームの日本語欄に「約¥1.3億」とあるのは誤記。英語欄は ¥1.3 billion で、約13億円が正しい。
- フェーズ：プレシリーズA → シリーズA。
- 次回ラウンド（シリーズB）：**$100M（約100億円超）**。内訳案はデット50億円＋エクイティ50億円、バリュエーションは約300億円（CEOと協議中。長期的には500億円も視野）。
- 直近：個人投資家から2〜3億円の調達を目指す。
- IPO：未確定（NASDAQ と東証の比較中。米国法人が親会社なのでNASDAQが現実的）。

### 主要株主・投資家
| 投資家 | 種別 | 時期 |
|---|---|---|
| 豊田合成（トヨタグループ） | 戦略投資 | 2023年9月 |
| システム・ロケーション | 投資 | 2024年7月 |
| シモハナ物流 会長 | 個人投資家 | — |
| Future Venture Capital ／ 菊池製作所 ／ 出井伸之氏 | VC・事業会社・エンジェル | 2021年5月 |

### ターゲットVC（米国・CVC中心）
Toyota Ventures / WiL / Honda Innovations / Scrum Ventures / DNX Ventures / Geodesic Capital / Pegasus Tech Ventures / Presidio Ventures / NTT Docomo Ventures / Sony Innovation Fund / Panasonic Ventures / Global Brain / Marubeni Ventures / Eclipse Ventures / Lux Capital / BMW i Ventures / Autotech Ventures / Fontinalis Partners / DENSO NEXT / Liberty Mutual Strategic Ventures

### 非希薄化資金（EA系財団・グラント）
- Coefficient Giving / Survival and Flourishing Fund / Future of Life Institute / EA Funds（EAIF）
- 訴求ポイント：「$1でどれだけの命を救えるか」という費用対効果。
- AIM Incubator（Ambitious Impact）：最大$20万のシード資金。

### アクセラレーター・プログラム
- Tech Ranch VRA Program（JETRO、テキサス州Austin）：2026年5月にエントリー。評価KPIは資金調達、米国オフィス開設、米国人雇用、特許、PoC完了。
- 過去の活動：Aichi × UT Austin Accelerator（2025年2月）、Capital Factory、SXSW（2026年3月）。

---

## 5. 米国事業（US Go-To-Market）

- 担当：笹瀬 類（Rui Sasase）／ US Evangelist（Head of US Business Development）。Palo Altoを拠点に、米国市場の開拓と投資家集めを担う。
- 2026年度の目標：
  1. シリーズBに向けて米国の機関投資家と関係を築く。
  2. テキサス州のフリート・物流会社と最初の商取引関係をつくる。
  3. 2027年の本格的な米国事業開始に向けて、E-2ビザと法人体制を整える。
- GTMのフェーズ：
  - フェーズ1：Uber / Lyft のドライバー、医療・歯科の送迎サービス、商用フリート
  - フェーズ2：NVIDIAとの連携（ハードウェア組み込み＋出資）
  - 並行：保険会社（米国では特に有望）、D2C
- フリート向けの訴求：事故を25〜40%削減できる可能性、保険料の低減、ドライバーの満足度向上（ペルソナ：VP of Safety など）。
- 主要パートナー・接点：NVIDIA（VP Sales の Todd Miller 氏、Jetson Orin NX の価格交渉）、JETRO SF / Houston、Stanford EAコミュニティ、Nick 氏（コンサル、Pokémon GO 立ち上げ経験）、Vince 氏（PR戦略、Kintone の米国進出経験）。

### 映像・ブランド制作（Rising Act Films）
- パートナー：Tim Moore（Director、撮影・編集、映像業界25年）、Daniel Stine（Executive Director、受賞歴のある監督・脚本家）。拠点はAtlanta。Rising Act Films は 501(c)(3) の非営利団体。
- 選んだ理由：ミッションへの共鳴（交通事故ゼロ）、「MADE BY HAND AND HEART」とAIのあたたかみの一致、グリーンスクリーン×AI画面合成（モックアップで撮影でき、UI更新後に差し替え可能、日米で素材を流用できる）、コスト効率（月3本 $15,000）。
- 制作物：ショート動画シリーズ（Shorts Proposal A）。「Honesty」「Truck」「Pedestrian」編など。タグラインは "Pyrenee Drive. Keeps It Real." / "Voice of Reason." / "Problem Solved." など。2026年7月にデモ映像、9月に字幕付きの最終版を調整。
- 注意：商業契約は名義（Rising Act / Daniel個人 など）を確認し、W-9を取得すること。

---

## 6. チーム

| 氏名 | 役職 |
|---|---|
| 三野 龍太（Ryuta Mino） | 代表取締役CEO |
| 水野 剛（Tsuyoshi Mizuno） | CTO |
| 三野 真代（Mayo Mino） | CDO（デザイン） |
| 野口 隼冬 | 経営企画 |
| 年綱 真一 | ファイナンス |
| 小松 琢充（Takumitsu Komatsu） | 機械エンジニア |
| スガル チメデセンゲ（Sengee） | プロジェクトマネージャー |
| 宮定 浩 | AIエンジニア |
| 西山 佳克（Yoshikatsu Nishiyama） | AIエンジニア |
| 荷軽部 彩（Aya Nikarube） | GM |
| 笹瀬 類（Rui Sasase） | US Evangelist（米国事業立ち上げ・投資家集め） |

### カルチャー
- 上下関係や官僚的な慣習がなく、少人数でオープンに協力し合う。
- 「求む男子と女子。至難の旅。極難。暗黒の開発の日々。絶えざる失敗の危険。成功の保証なし。ただし、成功の暁には喜びと報酬と次のさらに大きい挑戦の機会を得る。」（シャクルトンの南極探検隊の募集広告になぞらえたもの）
- 向いている人：自社プロダクトに携わりたい人、チャレンジングな人、車や運転が好きな人、人を喜ばせたい人、ダジャレ好き。
- オフィス：晴海のCROSS DOCK。屋上にフットサルコート、社内に車（シートで昼寝ができる）、LOVOTがいる。

---

## 7. 主要タイムライン

| 時期 | 出来事 |
|---|---|
| 2016年1月 | 株式会社Pyrenee 設立 |
| 2016年4月 | Pyrenee Inc.（Delaware）設立 |
| 2019年 | グッドデザイン賞。7月にシャープと量産支援で契約 |
| 2021年5月 | Future Venture Capital、菊池製作所、出井伸之氏などから調達 |
| 2022年12月 | CyberAgent Capital の Monthly Pitch に登壇（THE BRIDGE 掲載） |
| 2023年9月 | 豊田合成（トヨタグループ）から戦略投資 |
| 2024年7月 | システム・ロケーションから投資 |
| 2025年2月 | Aichi × UT Austin Accelerator に参加 |
| 2026年3月 | SXSW に参加。米国での活動を本格化 |
| 2026年4月 | JIC（Palo Alto）を拠点に活動 |
| 2026年5月 | YC S26 に申請。Tech Ranch VRA にエントリー。千葉で実証実験を開始 |
| 2026年6〜9月 | Rising Act Films とショート動画を制作 |
| 2026年9月 | CEO三野がNASDAQ副会長と面会 |
| 2027年1月（予定） | Pyrenee Drive 発売・米国展開 |

---

## 8. よく使うフレーズ（英語）

- One-liner: *Pyrenee Drive is a retrofit AI driving assistant that prevents accidents by detecting hazards and alerting drivers in real time — for the 280M+ cars on US roads that will never get factory ADAS.*
- Mission: *Eliminate traffic accidents worldwide.*
- Company: *Pyrenee Inc. is a Japanese AI startup founded in 2016, backed by a Toyota Group company, with ~¥1.3B raised to date.*
