# 証券口座乗っ取り（2025-2026）の攻撃手口と多要素認証の防御力

調査日: 2026-11-10。
調査方法の注意: この環境では rakuten-sec.co.jp / jsda.or.jp / watch.impress.co.jp への直接フェッチが DNS 失敗（ネットワーク制限）で不可だった。以下はすべて WebSearch の結果本文（検索エンジンの要約を含む）に基づく。一次ソース（金融庁・日証協・各社公式）のURLを挙げていても、**本文を直接読んで確認したものではない**ため、本文で「（未確認）」と書いたものは特に要検証。
用語: AitM = Adversary-in-the-Middle（リアルタイムフィッシング）。

---

## Q1. 2025-2026年の攻撃で実際に使われた手口と、主要だった手口

### Takeaway
当局・報道・ベンダーが一致して主要経路としたのは「証券会社を装ったメール/SMSで偽ログインサイトへ誘導 → ID・パスワード（＋OTP）を詐取」というフィッシング（2025年中盤以降はOTPを中継するリアルタイムフィッシングが中心）で、補助的にインフォスティーラー（情報窃取マルウェア）が指摘された。2026年にはSIMスワップ、Google/Appleアカウント乗っ取り経由（クラウド保存パスキー/パスワードの悪用疑い）という新しい経路が各社から注意喚起された。検索広告経由の偽サイト・偽アプリ・パスワード使い回し（リスト型攻撃）が主要経路だったことを示す資料は見つからなかった。

### Cited Findings
**被害規模（金融庁集計、日付つき）**
- 2025年通年: 不正アクセス17,559件、うち不正取引9,752件。不正取引件数のピークは2025年4月の3,014件、12月は103件まで減少（金融庁 2026-01-14 発表として報道）— [ニッキン](https://www.nikkinonline.com/article/358303)
- 2025年4月の不正取引件数は、5月時点の速報では2,746件（3月は687件）と発表され、のち改定。ピーク値は3,014件とする報道と3,033件とする報道があり食い違う — [ScanNetSecurity 2025-05-21](https://scan.netsecurity.ne.jp/article/2025/05/21/52882.html); [ニッキン](https://www.nikkinonline.com/article/358303); 3,033件説は [LIMO](https://limo.media/articles/-/143032)、[Yahoo!ニュース(LIMO)](https://news.yahoo.co.jp/articles/c16367d8ce7d55fb0f67fe42f9936775b7ee2883)
- 2025年2月1日〜4月16日: 不正取引1,454件・約954億円、被害は楽天証券・SBI証券など大手6社に集中 — [nippon.com](https://www.nippon.com/ja/in-depth/d01153/); [日経クロステック](https://xtech.nikkei.com/atcl/nxt/column/18/00001/10532/)
- 2025年1〜5月: 不正アクセス10,422件、不正取引5,958件、不正売買額約5,240億円 — [Impress Watch](https://www.watch.impress.co.jp/docs/news/2020317.html); [トレンドマイクロ 2025-06](https://www.trendmicro.com/ja_jp/research/25/f/mfa-securities-hacks.html)
- 2025年1〜7月末累計の不正売買額6,205億円 — [Bloomberg 2025-08-07](https://www.bloomberg.com/jp/news/articles/2025-08-07/T0M118GOT0JO00)
- 2025年8月: 不正アクセス1,248件（7月1,055件から増加）、不正取引562件（7月894件）— [日経クロステック](https://xtech.nikkei.com/atcl/nxt/news/24/02812/)
- 2025年10月: 不正アクセス693件、不正取引333件 — [ScanNetSecurity 2025-11-27](https://scan.netsecurity.ne.jp/article/2025/11/27/54109.html)
- 2025年1〜11月で売買あわせて約7,191億円の不正取引（フィッシング対策協議会 2025年11月月次報告での引用）— [フィッシング対策協議会 202511](https://www.antiphishing.jp/report/monthly/202511.html)
- 2025年1月〜2026年2月累計: 不正アクセス18,193件、不正取引10,112件、売却約4,060億円・買付約3,557億円（金融庁 2026-03-09 発表として引用）— [McAfeeブログ](https://www.mcafee.com/blogs/ja-jp/internet-security/why-account-takeovers-of-brokerage-accounts-are-increasing/)
- 2026年1月の不正売買額45億円（2025年12月比で増加）— [日経 2026-02](https://www.nikkei.com/article/DGXZQOUB095SY0Z00C26A2000000/)（見出しのみ確認）
- 2026年7月の不正取引は「1件」と報道 — [日経 2026-08](https://www.nikkei.com/article/DGXZQOUB104E10Q6A810C2000000/)（見出しのみ確認）
- 2026年8月: 4社で不正アクセス39件（のち43件に修正）、不正取引25件（暫定）— [ScanNetSecurity 2026-09-28](https://scan.netsecurity.ne.jp/article/2026/09/28/56308.html)
- 2026年9月: 不正アクセス37件、不正取引2件（表面化以降最少）、9月の不正売買額は約2億円 — [LIMO](https://limo.media/articles/-/143032); [株探 2026-10-14](https://s.kabutan.jp/news/n202610141023/)
- 2025年1月〜2026年9月累計: 不正アクセス19,252件、不正取引10,642件（ただし他集計と微妙に不一致）— [LIMO](https://limo.media/articles/-/143032)

**手口（当局）**
- 2025-05-02、警察庁・金融庁・日本証券業協会が連名で、偽サイトにID・パスワードを入力させる手口への注意文書を公表 — [日経](https://www.nikkei.com/article/DGXZQOUD022JP0S5A500C2000000/)
- 警察庁は金融機関の公式サイトのブックマーク利用を推奨 — [日経](https://www.nikkei.com/article/DGXZQOUD022JP0S5A500C2000000/)（検索要約経由）

**手口（フィッシング対策協議会 = JPCERT/CC事務局）**
- 2025年4月、SBI証券をかたるフィッシングが報告全体の約11.3%に急増。5月は約23.3%、6月約11.3%、7月約16.1%、8月約12.3% — [協議会 202504](https://www.antiphishing.jp/report/monthly/202504.html); [202505](https://www.antiphishing.jp/report/monthly/202505.html); [202506](https://www.antiphishing.jp/report/monthly/202506.html); [202507](https://www.antiphishing.jp/report/monthly/202507.html); [202508](https://www.antiphishing.jp/report/monthly/202508.html)
- 証券系ブランドは2025年5月時点で11ブランド、7月時点で12ブランド — [協議会 202505](https://www.antiphishing.jp/report/monthly/202505.html); [202507](https://www.antiphishing.jp/report/monthly/202507.html)
- 2025年3月以降、協議会が情報掲載した証券会社は10社10ブランド（2025-11-05 協議会事務局資料）— [JPAAWG 平塚資料](https://meetings.jpaawg.org/wp-content/uploads/2025/11/A2-5-hiratsuka-JPAAWG8-%E5%85%AC%E9%96%8B%E7%94%A8.pdf)
- 2025年11月は証券会社をかたるフィッシングの報告が減少 — [協議会 202511](https://www.antiphishing.jp/report/monthly/202511.html)

**手口（報道・ベンダー）**
- 流入経路はSMSかフィッシングメール。SMSでは「このままだとロスカットに」など不安を煽る文面 — [Yahoo!ニュース(スマホライフPLUS)](https://news.yahoo.co.jp/articles/0cbeec9114706e032789f2acf2388a40a19ad7ae)
- SMS等で送られた認証パスコードまで偽サイトで入力させて突破する「リアルタイムフィッシング」が横行（2025年5月）— [日経](https://www.nikkei.com/article/DGXZQOUB139SY0T10C25A5000000/)
- 「ワンタイムパスワードで防げず」（2025年7月）— [日経](https://www.nikkei.com/article/DGXZQOUB087ME0Y5A700C2000000/)
- トレンドマイクロ（2025年6月）: 多要素認証必須化後も被害は減っていない。銀行向けに使われてきたキット、日本の証券口座向け大規模キャンペーン用キット、感染端末を不正SMSの送信元にするキットなど、複数のフィッシングキットが日本の証券口座を狙っていると分析 — [トレンドマイクロ](https://www.trendmicro.com/ja_jp/research/25/f/mfa-securities-hacks.html)
- トレンドマイクロ（2025年7月）: 盗んだセッションCookieを別端末に取り込む「パス・ザ・クッキー」で、MFA有効な口座でも追加コードなしでログインされうる — [トレンドマイクロ](https://www.trendmicro.com/ja_jp/research/25/g/proactive-security-against-account-takeover.html)
- インフォスティーラー: 証券口座情報の盗難手口にコンピューターウイルスも（2025年4月）— [日経](https://www.nikkei.com/article/DGXZQOUB291YK0Z20C25A4000000/); 「暗躍するインフォスティーラー」— [日経クロステック](https://xtech.nikkei.com/atcl/nxt/column/18/00001/10532/)
- 偽CAPTCHA（「私はロボットではありません」）を悪用したインフォスティーラー感染が増加、マクニカの調査で闇市場に証券口座の認証情報約10万5千件 — 検索要約が日経・マクニカ解説として紹介（**一次未確認**）[マイナビニュース](https://news.mynavi.jp/article/20250902-3429267/); [日経クロステック](https://xtech.nikkei.com/atcl/nxt/column/18/00001/10532/)
- 楽天・SBI・野村・マネックス・SMBC日興など9社で不正売買を確認（2025年5月頃）、最終的に不正取引発生は17社とする報道あり — [Yahoo!ニュース](https://news.yahoo.co.jp/articles/0cbeec9114706e032789f2acf2388a40a19ad7ae); [ザイ・オンライン](https://diamond.jp/zai/articles/-/1053757)

**2026年の新手口**
- SIMスワップ: 楽天証券 2026-04-06「SIMスワップ詐欺に関する注意喚起」— 第三者が携帯番号を不正に乗っ取る手口とみられる、身に覚えのないログイン・取引・各種申込みの事例を確認 — [楽天証券](https://www.rakuten-sec.co.jp/web/info/info20260406-01.html)
- 国内のSIMスワップ逮捕事例（偽造免許証でSIM再発行、銀行アプリから約600万円送金、愛知県警「日本初」）— 検索要約経由、日付不明 — [iPhone Mania](https://iphone-mania.jp/news-525622/); 参考 [福岡県警資料](https://www.police.pref.fukuoka.jp/data/open/cnt/3/22941/1/HP_SIM.pdf)
- Google/Appleアカウント乗っ取り経由: 2026-09-24 日経が報道、犯罪集団がApple・Googleアカウントに保存された証券口座のパスキーやパスワードを使って取引したとみられる。日証協が加盟社に注意喚起を要請 — [セキュリティ対策Lab](https://rocket-boys.co.jp/security-measures-lab/sbi-securities-google-apple-account-passkey/); [innovatopia](https://innovatopia.jp/cyber-security/cyber-security-news/118722/)
- SBI証券 2026-10-02 注意喚起（クラウド保存のパスキーやパスワードのメモが悪用されたとみられる、自社システムからの漏えいではない）、10-08 に「自社口座での被害は確認されていない」と追記。SMBC日興 2026-10-06 同種注意喚起 — [Kotori Life](https://www.kotori-life.com/2026/10/09/passkey-security-google-apple-securities-account/); [セキュリティ対策Lab](https://rocket-boys.co.jp/security-measures-lab/sbi-securities-google-apple-account-passkey/)（ブログ・二次情報）
- 楽天証券 2026-10-14: 他社でGoogle/Appleアカウントのログイン情報が不正取得され、証券口座への不正ログイン・不正取引が行われた疑いのある事案を確認として注意喚起 — [楽天証券](https://www.rakuten-sec.co.jp/web/info/info20261014-01.html); [LIMO](https://limo.media/articles/-/144977)

### Inferences
- 主要経路の順位（推定）: ①メール/SMSフィッシング→偽サイト（2025年前半はID/PW、MFA必須化後はOTP中継型AitM）＞②インフォスティーラー/Cookie窃取（ベンダー・報道が指摘、件数比率は不明）＞③2026年のSIMスワップ・クラウドアカウント乗っ取り（件数は小さいとみられる。2026年8〜9月の不正取引は月25件→2件）。
- 2025年5〜6月の各社MFA必須化後も不正取引が数百件規模で続き、2025年10〜11月のパスキー導入以降に急減、2026年6月の必須化期限後は一桁〜数十件、という時系列はパスキーの効果と整合する（ただし因果は当局が明示したものではない）。

### Gaps
- 金融庁・警察庁による「手口別の件数比率」（フィッシング何%、マルウェア何%等）は見つからず: **不明**。
- 検索広告（リスティング広告）経由の偽サイトが証券口座乗っ取りで使われたとする当局・協議会の資料は見つからず: **不明**。
- 偽アプリ（偽の証券アプリ）による被害事例: **不明**。
- パスワード使い回しによるリスト型攻撃の寄与: 各社がパスワード使い回し回避を呼びかけてはいるが、主要因とする統計は見つからず: **不明**。
- JPCERT/CC・IPA独自の分析文書は取得できず。

---

## Q2. 侵入後に攻撃者は何をしたか／なぜ直接出金しなかったか

### Takeaway
攻撃者は口座内の保有株を売却し、その資金で中国株・小型株など流動性の低い特定銘柄を大量に買い付けて株価をつり上げ、事前に自分たちが仕込んでいた同銘柄を高値で売り抜ける「相場操縦」型だった。出金は本人名義の登録銀行口座にしかできないため、現金を直接抜くより株価操作で利益を得る方式が選ばれたと解説されている。

### Cited Findings
- 他人の口座のID/PWで不正ログインし、保有株を勝手に売却、その資金で中国株などを買い付け、株価が上がったところで売り抜けて利益を得る — [ザイ・オンライン](https://diamond.jp/zai/articles/-/1053757)
- 日本の証券口座の出金先は本人名義の銀行口座に限られるため、攻撃者は現金化せず乗っ取り口座で特定銘柄を大量に買い付け、先に保有していた同銘柄を高値で売る — [nippon.com](https://www.nippon.com/ja/in-depth/d01153/)（検索要約経由）
- 2025年3月、中国籍の男2人が他人名義口座を使った株価つり上げで金商法違反（相場操縦）容疑で逮捕（警視庁）— 検索要約経由、[nippon.com](https://www.nippon.com/ja/in-depth/d01153/)
- 2025-12-18、証券取引等監視委員会が不正アクセスを手段とした相場操縦事件で法人1社・個人1名を東京地検に告発 — [証券取引等監視委員会](https://www.fsa.go.jp/sesc/news/c_2025/2025/20251218-1.html)（検索要約経由）
- 2026年7月、奈良県警が不正入手口座で相場操縦に関与したとみられる中国籍の姉妹を詐欺容疑で逮捕 — [熊本日日新聞](https://kumanichi.com/articles/2013609)
- 対策として各社は出金先口座変更時の認証強化・「裏口」対策も実施（楽天 2025年6月）— [ITmedia 2025-05-07](https://www.itmedia.co.jp/news/articles/2505/07/news138.html)
- 日証協ガイドラインは出金時・出金先口座変更時にもフィッシング耐性MFAを要求（Q5参照）— [Impress Watch](https://www.watch.impress.co.jp/docs/news/2031496.html)
- 野村證券は2026-06-27以降、オンラインサービスからの出金にパスキー認証を必須化（パスキー未設定ではオンライン出金不可）— [野村證券](https://www.nomura.co.jp/introduc/news/2026/20260513_1.html)

### Inferences
- 被害者側の損失は「現金が消える」より「優良株を売られ、値崩れしやすい銘柄を高値で掴まされる」形で発生する。直接出金の障壁は出金先の本人名義制約だが、出金先口座の変更が突破されれば直接出金も理論上ありうるため、各社とガイドラインは出金先変更にも強い認証を求めている。

### Gaps
- 不正買付の対象銘柄リスト・中国株と国内小型株の比率: **不明**（ここでは調査せず）。
- 2025-2026年に実際に出金先変更→出金まで至った事例があったか: **不明**。

---

## Q3. 各MFA方式の強さ（上記手口別）

### Takeaway
OTP系（SMS・メール・TOTP・画像/絵文字選択）は「利用者が偽サイトに入力/選択した結果を攻撃者がその場で本物サイトに中継する」AitMに構造的に弱く、日証協も一般的なOTPはフィッシング耐性要件を満たさない可能性が高いとした。パスキー（FIDO2）は鍵が正規ドメイン（オリジン）に紐付き、偽サイトでは署名自体が生成されないため中継が成立しない。ただしパスキーもインフォスティーラーによるログイン後Cookie窃取や、パスキーを同期するGoogle/Appleアカウント自体の乗っ取りには別途対策が必要。

### Cited Findings
- ワンタイムパスワードはリスト型攻撃には有効だが、偽サイトが入力を本物へリアルタイム中継するとそのコードがその場で使われてしまう — [issoh.co.jp](https://www.issoh.co.jp/tech/details/1440/)
- SMSのワンタイムコードやマジックリンクは、利用者がフィッシングページに入力させられれば傍受される — [Corbado](https://www.corbado.com/ja/blog/passkeys-passwordless-phishing-resistant-mfa.md)
- 偽サイトはID・パスワード・OTPを即座に中継する仕組みを持つため、OTPを設定していても突破されうる — [K2 College](https://media.k2-assurance.com/archives/30038); [日経 2025-07](https://www.nikkei.com/article/DGXZQOUB087ME0Y5A700C2000000/)
- パスキーは公開鍵暗号ベースで、秘密鍵は端末内にとどまり署名だけが送られる。鍵は登録先ドメインに結び付けられ、偽サイトでは署名が成立しない — [issoh.co.jp](https://www.issoh.co.jp/tech/details/1440/)
- FIDO2系は認証を正規オリジンに紐付けるため偽サイトへの転送・再利用ができず、攻撃者は秘密鍵も再利用可能な秘密コードも入手できない — [Corbado](https://www.corbado.com/ja/blog/passkeys-passwordless-phishing-resistant-mfa.md)
- FIDO Allianceは、パスキーはフィッシング等に耐性がありSMSのOTPより安全とする一方、サービス側がアカウント回復プロセスも強化しないと完全な防止にはならないと指摘 — [FIDO Alliance ホワイトペーパー](https://fidoalliance.org/white-paper-passkeys-the-journey-to-prevent-phishing-attacks/?lang=ja)
- パスキーはパスワードがネットワークを流れないためリアルタイムフィッシングを防げる（トレンドマイクロ 2025年6月）— [トレンドマイクロ](https://www.trendmicro.com/ja_jp/research/25/f/mfa-securities-hacks.html)
- 盗まれたセッションCookieの持ち込み（パス・ザ・クッキー）はMFA有効でもログインを許しうる — [トレンドマイクロ](https://www.trendmicro.com/ja_jp/research/25/g/proactive-security-against-account-takeover.html)
- 日証協改正ガイドラインに関し「一般的なワンタイムパスワードを組み合わせる多要素認証ではフィッシング耐性という要件を満たせない可能性が高い」「ワンタイムパスワードは原則禁止へ」— [日経クロステック](https://xtech.nikkei.com/atcl/nxt/column/18/00001/10906/); [PC-Webzine](https://www.pc-webzine.com/article/3095)
- 「生体認証で防ぐ」（日経 2025年8月、リアルタイムフィッシング被害拡大を受けて）— [日経](https://www.nikkei.com/article/DGXZQOUB227NM0S5A820C2000000/)（見出しのみ）
- パスキー導入後の新リスク: クラウド（Google/Apple）に同期されたパスキーやパスワードメモの悪用疑い（2026年9〜10月）。日証協はクラウドにパスキーをバックアップする場合はApple/Googleアカウント側にもMFAを設定するよう求める。端末ローカル保存という選択肢も紹介されている — [Kotori Life](https://www.kotori-life.com/2026/10/09/passkey-security-google-apple-securities-account/); [セキュリティ対策Lab](https://rocket-boys.co.jp/security-measures-lab/sbi-securities-google-apple-account-passkey/)（二次情報）
- 2026年10月、楽天証券とSMBC日興証券が「パスキーを設定していても（Google/Apple等の）2段階認証の確認を」と呼びかけ — [LIMO](https://limo.media/articles/-/144977)

### 手口 × 方式の防御力（上記ソースからの整理。表中の評価は推論）

| 方式 | 偽サイト(ID/PW詐取のみ) | リアルタイムフィッシング(AitM) | インフォスティーラー(Cookie窃取) | SIMスワップ | パスワード使い回し |
|---|---|---|---|---|---|
| SMS OTP | 有効 | **無効**（中継される） | 無効 | **無効**（番号を奪われる） | 有効 |
| メールOTP | 有効 | **無効** | 無効（メールも盗まれれば無効） | 有効（メールが別管理なら） | 有効 |
| 画像/絵文字選択認証（楽天のログイン追加認証） | 有効 | **原則無効**（偽サイトが同じ選択画面を中継しうる。下記推論） | 無効 | 有効 | 有効 |
| 認証アプリTOTP | 有効 | **無効** | 無効 | 有効 | 有効 |
| プッシュ承認 | 有効 | 弱い（攻撃者のログインを利用者が承認してしまう） | 無効 | 有効 | 有効 |
| 端末紐付け認証（旧デバイス認証・アプリFIDO認証等） | 有効 | 方式次第 | 無効 | 有効 | 有効 |
| パスキー(FIDO2) | 有効 | **有効**（オリジン不一致で署名不成立） | 無効（ログイン後のセッションは守らない） | 有効 | 有効（パスワード不要） |
| パスキー(端末ローカル保存/物理キー) | 同上 | **有効** | 無効 | 有効 | 有効＋クラウドアカウント乗っ取り耐性 |

### Inferences
- 画像/絵文字選択認証は、メールに届いた絵文字を利用者が偽サイト上で選ばせれば、攻撃者は同じ選択を本物サイトに即時入力できるため、構造的にはOTPと同じ「人が値を転記する」方式で、AitM耐性はない（楽天自身が2025年11月末目途に「セキュリティ強化」を予告していたことと整合）。ただし、これが実際に突破された事例の一次確認はできていない。
- プッシュ承認・TOTPの国内証券での突破事例は見つからなかった（そもそも主要3社が提供しているか不明）ため、評価は一般論からの推論。
- パスキーでもインフォスティーラー感染端末からのCookie窃取は防げないため、端末のマルウェア対策と、取引・出金時の再認証（野村のように取引・出金時もパスキー必須）が補完になる。
- 個人投資家にとってのおすすめ順（推論）: ①パスキー（端末ローカル保存 or 物理セキュリティキー）＞②パスキー（Google/Apple同期。同期元アカウント自体にパスキー/強いMFA必須）＞③端末紐付けのアプリ生体認証＞④TOTP/プッシュ＞⑤メールOTP・絵文字認証＞⑥SMS OTP（SIMスワップにも弱い）。

### Gaps
- 楽天の絵文字認証がAitMで実際に突破されたかどうか: **不明**。
- 国内証券口座で同期パスキー経由の被害が確定した件数: **不明**（2026年10月時点で「疑い」まで）。

---

## Q4. 楽天証券（およびSBI証券・野村證券）が提供する認証方式と最強設定

### Takeaway
楽天証券は2026年11月時点で、メールで届く絵文字を選ぶ「ログイン追加認証」と、生体認証等で行う「パスキー認証（FIDO2）」の2本立て。パスキーは2025-10-26に全チャネル導入、2026年6月から顧客ごとに順次ログイン時必須化、2026-05-31からPCへの直接保存にも対応。最強設定はパスキー（できれば端末ローカル保存）を登録し、Google/Appleアカウント側のMFAも固めること。SBI証券は2026-06-30からパスキー原則必須（ただしPWログインも当面可）、野村證券は2026-06-27からログイン・取引・出金でパスキー必須。

### Cited Findings
**楽天証券**
- 2025年6月1日から、マーケットスピード・iSPEEDなど全チャネルで画像選択方式（絵文字）の「ログイン追加認証（多要素認証）」を必須化。出金先変更など“裏口”の対策も — [ITmedia 2025-05-07](https://www.itmedia.co.jp/news/articles/2505/07/news138.html)
- 認証3回失敗で口座ロックと仕様を厳格化 — [ITmedia 2025-05-13](https://www.itmedia.co.jp/news/articles/2505/13/news125.html)
- 絵文字は登録メールアドレスに届き、有効期限30分（解説記事）— [otokurashi.jp](https://otokurashi.jp/rakuten-sec-mfa-guide-2025/)（二次情報）
- 2025-09-29プレスリリース「国内主要証券初！FIDO2『パスキー認証』全チャネルログインに導入」: 2025-10-26からパスキー認証・注文通知導入・セキュリティ設定画面リニューアル。絵文字ログイン追加認証のセキュリティ強化は2025年11月末目途 — [楽天証券 PDF](https://www.rakuten-sec.co.jp/web/company/newsrelease/pdf/press20250929.pdf); [PR TIMES](https://prtimes.jp/main/html/rd/p/000000669.000011088.html)
- 2026-05-29のお知らせ: 2026年6月より順次ログイン時のパスキー認証を必須化、時期は顧客ごとに個別案内。2026-05-31からPCへのパスキー直接保存に対応（端末ごとに最大10個）、スマホがなくてもパスキー利用可 — [楽天証券 パスキーページ](https://www.rakuten-sec.co.jp/web/security/passkey/); [Impress Watch](https://www.watch.impress.co.jp/docs/news/2113043.html)（いずれも検索要約経由、本文未確認）
- 操作ガイド — [楽天証券 パスキー操作ガイド](https://www.rakuten-sec.co.jp/web/security/passkey/guide/)
- 2026-11-01時点の解説: 楽天の多要素認証は「ログイン追加認証（メール絵文字）」と「パスキー認証（指紋・顔）」の2つ。メール絵文字認証は廃止されておらず併存 — [atsoho.com](https://atsoho.com/blog/rakuten-securities-multi-factor-authentication)（二次情報）
- パスキーが使えない場合はID・パスワード＋絵文字認証での代替ログインが残る — [soico.jp](https://www.soico.jp/no1/news/securities/4737)（二次情報）
- 必須化の案内前でもログイン後の設定画面から先にパスキー設定可能 — [リベシティ](https://library.libecity.com/articles/01KTGCXCR3036WKN5B4P1SMH9R)（二次情報）
- 楽天の取り組み全般 — [楽天証券 不正ログイン・不正出金防止の取り組み](https://www.rakuten-sec.co.jp/web/security/measures/information.html)

**SBI証券**
- 2025-05-31からログイン時の多要素認証とメールアドレス登録を必須化。未設定の場合は電話番号認証が自動適用（解説）— [soico.jp](https://www.soico.jp/no1/news/securities/5096); [choboraku](https://choboraku.com/sbisec-secrity-setting/)（二次情報）
- 2025-10-25にWebでパスキー認証導入（報道）— [soico.jp](https://www.soico.jp/no1/news/securities/5096); [日経クロステック](https://xtech.nikkei.com/atcl/nxt/column/18/00001/11141/)
- 公式FAQ: パスキー認証は2026-06-30（火）より原則必須化。ただしユーザーネーム/パスワードでのログインも引き続き可能で、設定するまで設定を促す案内が表示・配信される — [SBI証券 FAQ](https://faq.sbisec.co.jp/answer/6937e6e3b14749ed0cd6062a/)
- 従来の「デバイス認証」は2026-06-13に終了したとする解説（公式未確認）— [リベシティ](https://library.libecity.com/articles/01KV78BRQGFEXKC0840VJSDAKT); [yt-lifequest](https://yt-lifequest.com/sbi-shoken-passkey/)
- アプリ側の「FIDO認証」（パスワード＋顔認証等）はパスキーとは別の仕組みとして説明されている — [soico.jp](https://www.soico.jp/no1/news/securities/4434)（二次情報）
- YubiKey等の物理キー利用の解説 — [城咲子ブログ](https://infomation-sytem-security.hatenablog.com/entry/sbi-passkey-setup-guide)（二次情報）

**野村證券**
- 2025-10-18からオンラインサービス・NOMURAアプリのログイン時にパスキー認証を導入 — [野村證券](https://www.nomura.co.jp/onlineservice/news/trading/2025/change_security_1018.html?sc_cvid=top_bltn_link_02)
- 2025-11-29からパスキー認証を必須化（取引時。ログインはID/PWでも可能）— [野村證券](https://www.nomura.co.jp/onlineservice/news/trading/2025/change_security_1129.html); [Business Insider](https://www.businessinsider.jp/article/2511-what-is-passkey-security/)
- 2026-06-27（土）6時からログイン・取引・出金時にパスキー認証を必須化。オンラインからの出金はパスキーなしでは不可 — [野村證券 2026-05-13告知](https://www.nomura.co.jp/introduc/news/2026/20260513_1.html)
- 野村はメールのリンクからログインさせOTP入力やパスキー登録を求めることはないと案内 — [野村證券 セキュリティ](https://www.nomura.co.jp/lp/security/)
- パスキー登録は1口座最大5件、FIDO2ハードウェアキー可、2026-03-28からパスキー新規/再登録時にマイナンバーカード認証を要求とする記述（いずれも二次情報、公式未確認）— 検索要約 [城咲子ブログ](https://infomation-sytem-security.hatenablog.com/entry/sbi-rakuten-securities-passkey-2026)

### Inferences（楽天証券で最強にする手順・推論）
1. 公式アプリ/ブックマークから楽天証券にログイン →「セキュリティ設定」画面でパスキーを登録（個別案内を待たず先に設定可）。
2. 可能ならPC/スマホの端末ローカル保存（2026-05-31以降PCも可）や物理セキュリティキーを使い、クラウド同期に依存しない。同期する場合はGoogle/Appleアカウントにパスキーや強いMFAを設定。
3. 絵文字認証（メール）は代替経路として残るため、登録メールアカウント自体のMFAを強化し、注文通知・ログイン通知を有効化（楽天 2025-10-26 導入の注文通知）。
4. メール/SMSのリンクからログインしない（警察庁・各社の共通推奨）。

### Gaps
- 楽天で、パスキー登録後に絵文字認証による代替ログインを利用者自ら無効化できるか: **不明**。
- 楽天で物理セキュリティキー（YubiKey）が公式サポートされるか: **不明**。
- 楽天のパスキー必須化が2026年11月時点で全顧客に完了したか: **不明**。
- 楽天がTOTP・プッシュ承認を提供しているか: 見つかった資料に記載なし → 提供していないとみられるが **不明**。
- 2025年11月末予定の「絵文字認証のセキュリティ強化」の具体内容: **不明**。

---

## Q5. 業界のパスキー/フィッシング耐性MFA必須化の動き（2026年）

### Takeaway
日本証券業協会は「インターネット取引における不正アクセス等防止に向けたガイドライン」を2025-10-15に改正し、ログイン・出金・出金先変更などの重要操作でパスキー等フィッシング耐性MFAをデフォルト必須化、原則2026年6月末を期限とした。楽天・SBI・野村はいずれも2026年6月前後に必須化を実施（ただしSBI・楽天は当面PW＋代替認証のログインも残る）。

### Cited Findings
- 改正案は2025-07-15に公表、改正ガイドラインは2025-10-15付 — [日証協 改正案PDF](https://www.jsda.or.jp/about/public/bosyu/files/20250715_guideline_public.pdf); [日証協 ガイドラインPDF](https://www.jsda.or.jp/about/hatten/inv_alerts/alearts04/files/20251015_internetgl.pdf); [日証協 報道資料](https://www.jsda.or.jp/houdou/2025/20251015fuseiaccess-guideline.pdf)（いずれも本文未確認、検索要約経由）
- ログイン時・出金時・出金先口座変更時などの重要操作でフィッシング耐性MFA（パスキー、PKIベース認証等）を実装し、デフォルトで必須化 — [Impress Watch](https://www.watch.impress.co.jp/docs/news/2031496.html); [digital FIT](https://fit.nikkin.co.jp/post/detail/hl1489)
- 原則2026年6月末までの対応を求める。暫定的に代替MFAを使う場合は移行スケジュールを顧客に周知 — [東洋経済(Yahoo!ニュース)](https://news.yahoo.co.jp/articles/72d186c37f5843736cba35e76a57d98fc1c724ee?page=2); [日経クロステック](https://xtech.nikkei.com/atcl/nxt/column/18/00001/10906/)
- 取引時のフィッシング耐性MFAは「望ましい」（ベストプラクティス）扱い。ログイン・取引時の顧客通知、認証失敗時のアカウントロックも必須化 — 検索要約（[Impress Watch](https://www.watch.impress.co.jp/docs/news/2031496.html) ほか）
- 「パスキーに課題も」（東洋経済、本命のパスキーの普及課題）— [東洋経済(Yahoo!ニュース)](https://news.yahoo.co.jp/articles/72d186c37f5843736cba35e76a57d98fc1c724ee?page=2)
- 2026年の各社実施: 楽天 2026年6月〜順次ログイン必須化、SBI 2026-06-30原則必須、野村 2026-06-27 ログイン・取引・出金必須（Q4参照）
- 2026年9〜10月、日証協がクラウド保存パスキーのリスクについて加盟社に注意喚起を要請（報道）— [セキュリティ対策Lab](https://rocket-boys.co.jp/security-measures-lab/sbi-securities-google-apple-account-passkey/)

### Inferences
- 「必須化」と言っても、SBI・楽天はパスキー未設定者にPW＋代替認証のログインを残している（SBI公式FAQで明記）。野村は出金にパスキー必須とする点でより厳格。攻撃者は「残された弱い入口」（代替ログイン、アカウント回復、同期元クラウドアカウント）に移行していると読める（2026年のSIMスワップ・Google/Apple経由事案）。
- 2026年7〜9月の不正取引が月1〜25件まで減ったことは、ガイドライン期限前後の一斉必須化と時期が一致。

### Gaps
- 金融庁自身が監督指針等でパスキー/フィッシング耐性MFAを義務付けたか: 見つからず **不明**。
- 日証協ガイドライン期限（2026年6月末）時点の業界全体の対応率: **不明**。
- 銀行業界（全銀協等）の同様の動き: 本調査の範囲外・未調査。
