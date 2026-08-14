# 顧客提出用シート・請求書（PDF）

対外的にそのまま出せる資料の保管場所。生成用のHTML/スクリプトも同梱してあるので、価格やレートが変わったら作り直せる。

## 価格シート

| ファイル | 内容 | 宛先/用途 | 通貨基準 |
|---|---|---|---|
| `FirstAgri_Hojicha_Organic_2026-08.pdf` | **有機ほうじ茶2種**（AEg $90.00／Ij $55.60） | 汎用（Tea Drop・OSOI・Tori's 等ほうじ茶実需のある先） | AUD = USD × 1.428 |
| `FirstAgri_Samples_OnHand_2026-08.pdf` | **今手元にある非FA 9SKU**（AFb/De/AFa/Dg/AEa/Cf＋ほうじ茶Ii/AEg/Ij） | 汎用・訪問時の手渡し（★最新） | AUD = USD × 1.428 |
| `FirstAgri_Sample_Lineup_2026-08.pdf` | 豪州手持ちサンプル（非FA 9SKU） | 汎用・訪問時の手渡し | AUD = USD × 1.428 |
| `FirstAgri_Hojicha_PriceSheet_O3.pdf` | ほうじ茶（AEh／AEg） | O3（Rachel）向け・2026-08-03発行 | AUD = USD × 1.428 |
| `FirstAgri_Matcha_PriceSheet_O3_2026-08-03.pdf` | 抹茶 | O3（Rachel）向け | |
| `FirstAgri_Matcha_PriceSheet_Volume_Culinary.pdf` | 量販・製菓グレード | 汎用 | |
| `FirstAgri_Cf_PriceSheet.pdf` | Cf 単品 | 汎用（製菓提案） | |
| `FirstAgri_Cf_Premium_Kagoshima.pdf` | Cf 商品資料 | 汎用 | |
| `FirstAgri_ALg_Wazuka_Organic.pdf` | ALg（有機・京都/和束） | Hello Matcha 等の有機宇治ライン向け | |

## 請求書

| ファイル | 内容 |
|---|---|
| `Commercial_Invoice_Purematcha_66kg.pdf` | Purematcha 66kg＋送料（FA003） |
| `請求書_2026年7月分_笹瀬類.pdf` | Rui 業務委託 2026年7月分（¥385,071） |

## 作り直し方

```bash
# 手持ちサンプル一覧
python3 render_oh.py    # onhand_src.html → FirstAgri_Samples_OnHand_2026-08.pdf

# 有機ほうじ茶シート
python3 render_hj.py        # hojicha_src.html → FirstAgri_Hojicha_Organic_2026-08.pdf

# サンプルラインナップ
python3 render_sl.py        # samplelist.html → FirstAgri_Sample_Lineup_2026-08.pdf
```

Playwright + Chromium（`/opt/pw-browsers/chromium`）でA4 1枚に自動フィットさせている。価格を直すときは HTML 側の該当セルを編集してから再レンダリングする。

## ⚠️ 注意

- **AUD換算は 1 USD = 1.428 で全シート統一**。⚠️過去に 1.451 で作った版があり、混在すると同一SKUで2つの金額が出るので、必ず既存シートに合わせる
- **価格の一次ソースは `../supplier-master-2026-08.md`**。Matcha Mate個別シートの数字（標準の0.857倍）を転記しないこと
- `Ij` はグレード・焙煎・品種が **TBC**。鈴木専務（かねはち茶園）への照会待ち
- PDFは配布した相手と日付を CLAUDE.md 側に必ず記録する
