# HubSpot インポート用CSV（担当者ベース）

豪州出張（2026-07/08）の全接触先を HubSpot に落とすための3ファイル。
一次ソース＝`../豪州出張ハンドオーバー.md`／`../sample-ledger-2026-08.md`。

| ファイル | 件数 | オブジェクト |
|---|---:|---|
| `hubspot-companies.csv` | 65 | 会社 |
| `hubspot-contacts.csv` | 62 | コンタクト（人） |
| `hubspot-deals.csv` | 20 | 取引 |

---

## 🔴 インポートの順番（この順でないと関連付けが壊れる）

1. **会社** → 2. **コンタクト** → 3. **取引**

HubSpot の「複数ファイルをインポート」を使い、**`Company name` 列で会社とコンタクト／取引を関連付ける**。
（1ファイルずつ入れる場合は、会社を先に入れてから、コンタクト側の `Company name` で紐づける）

---

## ⚠️ 先に作っておくカスタムプロパティ

`FA_` で始まる列は標準プロパティに無いので、**インポート前に HubSpot 側で作成**する。作らない場合はマッピング画面で「インポートしない」を選べば飛ばせる。

| プロパティ名 | オブジェクト | 種類 |
|---|---|---|
| `FA_決裁権` | コンタクト | 1行テキスト（決裁者／取次ぎ／情報提供者のみ／要確認） |
| `FA_対応言語` | コンタクト | 1行テキスト（Japanese／English／空＝未確認） |
| `FA_豪州出張メモ` | コンタクト・会社 | 複数行テキスト |
| `FA_配布サンプル` | 会社 | 1行テキスト |
| `FA_連絡チャネル` | 会社 | 1行テキスト |
| `FA_確度メモ` | 取引 | 複数行テキスト |

---

## 値の対応表

**Lifecycle Stage**（会社・コンタクト）
| 本CSVの値 | 意味 |
|---|---|
| `customer` | ✅受注（Itteki／Cosecha／Groove／Elle Collective／Purematcha） |
| `opportunity` | クロージング圏＝数量・価格まで議論済 |
| `salesqualifiedlead` | サンプルを渡して評価待ち |
| `lead` | 接触したが未連絡・情報が薄い |
| `other` | ❌失注 |

**Lead Status**（コンタクト）
`OPEN_DEAL`＝案件が動いている／`IN_PROGRESS`＝やりとり中／`ATTEMPTED_TO_CONTACT`＝連絡したが返事待ち／`NEW`＝未連絡／`UNQUALIFIED`＝失注・見送り／`BAD_TIMING`＝時期が来たら再開（Chatime＝2027年1月）

**Deal Stage**（取引・デフォルトパイプライン）
`closedwon`＝受注／`contractsent`＝契約書・見積もり提出済／`decisionmakerboughtin`＝決裁者が承認プロセスに入った／`qualifiedtobuy`＝条件を詰めている／`appointmentscheduled`＝次回の約束がある

**Amount** は **JPY**。⚠️**受注済み以外はすべて見込み**（`closedwon` 以外の金額を売上として扱わないこと）。
金額が空欄なのは、数量または単価が未確定で算出できないもの。

---

## ⚠️ インポート前に知っておくこと

- **氏名が未記録の先は会社レコードだけ作られる。**23件ある（The Tea Centre／Issho Cafe／JIBBI／A3／T Totler ほか）。人が埋まったら後から追加する
- **メール・電話が空のコンタクトが多い。**HubSpot は Email が無くても「姓名」で作成できるが、**重複判定が効かない**ので二重登録に注意
- **Ken が2人いる**（Matcha Mate の CFO兼CMO ／ Little Rogue の窓口）。**別人**なのでマージしないこと
- **ゆうかさんが2人いる可能性**（BALIBOLA ／ Bench Coffee）。同一人物かは未確認
- **`FA_連絡チャネル` は連絡『手段』であって、連絡済みという意味ではない。**連絡したかどうかは `Lead Status` を見る
- **Karomi Cafe は Itteki Matcha 経由で仕入れている。**直接の営業をかけない先なので `other` にしてある
- **Hello Matcha は US 側で扱う**（2026-08-18 Rui指示）。豪州のパイプラインとして追わない

## 更新するとき
`../豪州出張ハンドオーバー.md` を直してから、このCSVを作り直す。生成スクリプトは会話ログ側にあるので、
継続的に使うなら `sales-ops/hubspot/build.py` として切り出すこと。
