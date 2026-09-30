# 顧客提出用シート・請求書（PDF）

対外的にそのまま出せる資料の保管場所。生成用のHTML/スクリプトも同梱してあるので、価格やレートが変わったら作り直せる。

## 価格シート

| ファイル | 内容 | 宛先/用途 | 通貨基準 |
|---|---|---|---|
| `FirstAgri_FA25_2026-08.pdf` | **FA2.5 単品**（Kyoto/Ceremonial/1st・在庫4,000kg・FA003↔FA002のラダー付き） | 中間価格帯を求める先・US遠征（★最新） | AUD = USD × 1.428 ⚠️**価格未確定** |
| `FirstAgri_Hojicha_Organic_2026-08.pdf` | **有機ほうじ茶2種**（AEg $90.00／Ij $55.60） | 汎用（Tea Drop・OSOI・Tori's 等ほうじ茶実需のある先） | AUD = USD × 1.428 |
| `FirstAgri_Samples_OnHand_2026-08.pdf` | **今手元にある非FA 9SKU**（AFb/De/AFa/Dg/AEa/Cf＋ほうじ茶Ii/AEg/Ij） | 汎用・訪問時の手渡し（★最新） | AUD = USD × 1.428 |
| `FirstAgri_Sample_Lineup_2026-08.pdf` | 豪州手持ちサンプル（非FA 9SKU） | 汎用・訪問時の手渡し | AUD = USD × 1.428 |
| `FirstAgri_Hojicha_PriceSheet_O3.pdf` | ほうじ茶（AEh／AEg） | O3（Rachel）向け・2026-08-03発行 | AUD = USD × 1.428 |
| `FirstAgri_Matcha_PriceSheet_O3_2026-08-03.pdf` | 抹茶 | O3（Rachel）向け | |
| `FirstAgri_Matcha_PriceSheet_Volume_Culinary.pdf` | 量販・製菓グレード | 汎用 | |
| `FirstAgri_Cf_PriceSheet.pdf` | Cf 単品 | 汎用（製菓提案） | |
| `FirstAgri_Cf_Premium_Kagoshima.pdf` | Cf 商品資料 | 汎用 | |
| `FirstAgri_ALg_Wazuka_Organic.pdf` | ALg（有機・京都/和束） | Hello Matcha 等の有機宇治ライン向け | |

## 社内資料

| ファイル | 内容 |
|---|---|
| `FirstAgri_AU_TripReport_2026-08.pdf` | **オーストラリア出張報告 2026-07-21〜08-18**（A4 8ページ・社内セールス向け）。6月出張報告と同じ構成。確定¥13,225,000／粗利¥4,525,000、⚠️見込み粗利¥80,035,000。ソース＝`../reports/豪州出張報告_2026-07-21_08-18.md` |
| `FirstAgri_AU_Handover_ByCompany_2026-08.pdf` | **豪州出張ハンドオーバー 会社別**（A4 30ページ・67社）。**会社名／担当者／オーナー／連絡先4種（WhatsApp・E-mail・Instagram・その他）** を先頭に置いた形式。ソース＝`../豪州出張ハンドオーバー_会社別.md`（生成＝`../build/handover_v2.py`） |
| `FirstAgri_AU_Handover_2026-08.pdf` | **豪州出張ハンドオーバー**（A4 36ページ・65社/95名を人単位で棚卸し）。🔴**社内限定・対外配布不可**（顧客名・担当者名・価格・粗利を含む）。ソース＝`../豪州出張ハンドオーバー.md` |

## 請求書

| ファイル | 内容 |
|---|---|
| `Commercial_Invoice_Purematcha_66kg.pdf` | Purematcha 66kg＋送料（FA003） |
| `請求書_2026年7月分_笹瀬類.pdf` | Rui 業務委託 2026年7月分（¥385,071） |

## 作り直し方

```bash
# FA2.5 単品シート
python3 render_fa25.py  # fa25_src.html → FirstAgri_FA25_2026-08.pdf

# 手持ちサンプル一覧
python3 render_oh.py    # onhand_src.html → FirstAgri_Samples_OnHand_2026-08.pdf

# 有機ほうじ茶シート
python3 render_hj.py        # hojicha_src.html → FirstAgri_Hojicha_Organic_2026-08.pdf

# サンプルラインナップ
python3 render_sl.py        # samplelist.html → FirstAgri_Sample_Lineup_2026-08.pdf

# 豪州出張ハンドオーバー（Markdown → A4複数ページPDF）
python3 render_handover.py     # ../豪州出張ハンドオーバー.md → FirstAgri_AU_Handover_2026-08.pdf

# 豪州出張ハンドオーバー 会社別（★最新の形式）
python3 ../build/handover_v2.py   # → ../豪州出張ハンドオーバー_会社別.md
python3 render_handover_bc.py     # → FirstAgri_AU_Handover_ByCompany_2026-08.pdf

# 出張報告
python3 render_report.py          # ../reports/豪州出張報告_2026-07-21_08-18.md → FirstAgri_AU_TripReport_2026-08.pdf
```

`render_handover.py` は Markdown をそのままA4の冊子体にする。表紙・フッターのページ番号・表のヘッダー行の繰り返しまで入っているので、**内容を直すときは .md 側だけ編集して再レンダリングする**。

Playwright + Chromium（`/opt/pw-browsers/chromium`）でA4 1枚に自動フィットさせている。価格を直すときは HTML 側の該当セルを編集してから再レンダリングする。

## ⚠️ 注意

- 🔴**`FirstAgri_Sample_Lineup_2026-08.pdf` は 2026-08-15 の値下げ前の価格**（AFb $300／AEa $102／Cf $58.90／AEg $77.10＝MM個別価格）。**顧客に渡すなら `FirstAgri_Samples_OnHand_2026-08.pdf` の方を使うこと**
- **AUD換算は 1 USD = 1.428 で全シート統一**。⚠️過去に 1.451 で作った版があり、混在すると同一SKUで2つの金額が出るので、必ず既存シートに合わせる
- **価格の一次ソースは `../supplier-master-2026-08.md`**。Matcha Mate個別シートの数字（標準の0.857倍）を転記しないこと
- `Ij` はグレード・焙煎・品種が **TBC**。鈴木専務（かねはち茶園）への照会待ち
- 🔴 **FA2.5 の価格は未確定**。シートは US遠征の設定値 **¥25,000／$166.7／A$238.05** で作ってあるが、仕入マスターは **⚠️未定（¥24,000〜26,000）**。⚠️**社内で確定してから客に渡すこと**（¥24,000なら $160.0／A$228.48）
- PDFは配布した相手と日付を CLAUDE.md 側に必ず記録する
