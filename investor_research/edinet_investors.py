"""EDINETの有価証券報告書を全件取得し、Pyreneeに1口5,000万円以上を出資できる事業会社候補をスコアリングする。

使い方:
    export EDINET_API_KEY=xxxxxxxx   # https://api.edinet-fsa.go.jp で無料登録して発行
    python investor_research/edinet_investors.py --days 400 --out investor_research/out

必要な通信先: api.edinet-fsa.go.jp, disclosure2dl.edinet-fsa.go.jp
途中で止まっても --out 配下のキャッシュから再開できる。
"""

import argparse
import csv
import datetime as dt
import io
import json
import os
import re
import sys
import time
import zipfile
from pathlib import Path

import requests

API = "https://api.edinet-fsa.go.jp/api/v2"
CODELIST_URL = "https://disclosure2dl.edinet-fsa.go.jp/searchdocument/codelist/Edinetcode.zip"

TICKET_YEN = 50_000_000

# 戦略適合度: 業種 → 点数（Pyrenee Drive = AI運転アシスタント × 交通データ）
INDUSTRY_FIT = {
    "陸運業": 30,
    "倉庫・運輸関連業": 25,
    "輸送用機器": 30,
    "ゴム製品": 20,
    "保険業": 25,
    "卸売業": 15,
    "その他金融業": 20,
    "石油・石炭製品": 15,
    "電気機器": 15,
    "情報・通信業": 10,
    "空運業": 10,
    "海運業": 10,
    "小売業": 5,
    "食料品": 5,
}

# 出資姿勢のシグナル（有報の全文から件数を数える）
INVEST_KEYWORDS = [
    "スタートアップ", "ベンチャー", "CVC", "コーポレート・ベンチャー", "コーポレートベンチャー",
    "オープンイノベーション", "資本業務提携", "投資事業有限責任組合", "少数株主持分",
]
THEME_KEYWORDS = [
    "交通安全", "安全運転", "事故削減", "ドライブレコーダー", "ドライバー不足", "自動運転",
    "モビリティ", "物流DX", "2024年問題", "テレマティクス", "AI", "人工知能",
]
# 既存株主（豊田合成・坂東化学）の系列は紹介ルートになる
RELATION_KEYWORDS = ["トヨタ自動車", "豊田合成", "豊田通商", "デンソー", "アイシン", "バンドー化学"]

# (列名, 要素IDの候補) — 先に見つかったものを採用
NUMERIC_ELEMENTS = {
    "現金及び預金": ["jppfs_cor:CashAndDeposits"],
    "現金同等物": [
        "jpcrp_cor:CashAndCashEquivalentsSummaryOfBusinessResults",
        "jpcrp_cor:CashAndCashEquivalentsIFRSSummaryOfBusinessResults",
        "jpcrp_cor:CashAndCashEquivalentsUSGAAPSummaryOfBusinessResults",
    ],
    "投資有価証券": ["jppfs_cor:InvestmentSecurities"],
    "純資産": [
        "jpcrp_cor:NetAssetsSummaryOfBusinessResults",
        "jpcrp_cor:EquityAttributableToOwnersOfParentIFRSSummaryOfBusinessResults",
        "jpcrp_cor:EquityIncludingPortionAttributableToNonControllingInterestUSGAAPSummaryOfBusinessResults",
        "jppfs_cor:NetAssets",
    ],
    "売上高": [
        "jpcrp_cor:NetSalesSummaryOfBusinessResults",
        "jpcrp_cor:OperatingRevenue1SummaryOfBusinessResults",
        "jpcrp_cor:RevenueIFRSSummaryOfBusinessResults",
        "jpcrp_cor:RevenuesUSGAAPSummaryOfBusinessResults",
        "jppfs_cor:NetSales",
    ],
    "親会社株主に帰属する当期純利益": [
        "jpcrp_cor:ProfitLossAttributableToOwnersOfParentSummaryOfBusinessResults",
        "jpcrp_cor:ProfitLossAttributableToOwnersOfParentIFRSSummaryOfBusinessResults",
        "jpcrp_cor:NetIncomeLossAttributableToOwnersOfParentUSGAAPSummaryOfBusinessResults",
        "jpcrp_cor:NetIncomeLossSummaryOfBusinessResults",
    ],
    "従業員数": ["jpcrp_cor:NumberOfEmployees"],
}
TEXT_ELEMENTS = {
    "代表者": "jpcrp_cor:TitleAndNameOfRepresentativeCoverPage",
    "本店所在地": "jpcrp_cor:AddressOfRegisteredHeadquarterCoverPage",
    "電話番号": "jpcrp_cor:TelephoneNumberAddressOfRegisteredHeadquarterCoverPage",
    "関係会社の状況": "jpcrp_cor:OverviewOfAffiliatedEntitiesTextBlock",
    "大株主の状況": "jpcrp_cor:MajorShareholdersTextBlock",
    "役員の状況": "jpcrp_cor:InformationAboutOfficersTextBlock",
}
TEXT_SNIPPET_LEN = 1500


def get(session, url, params=None, retries=4):
    for i in range(retries):
        try:
            r = session.get(url, params=params, timeout=60)
            if r.status_code == 200:
                return r
            if r.status_code in (429, 500, 502, 503, 504):
                time.sleep(2 ** (i + 1))
                continue
            r.raise_for_status()
        except requests.RequestException:
            if i == retries - 1:
                raise
            time.sleep(2 ** (i + 1))
    raise RuntimeError(f"failed: {url}")


def load_codelist(session, cache: Path):
    """EDINETコード → 業種・上場区分などの辞書。"""
    if not cache.exists():
        r = get(session, CODELIST_URL)
        with zipfile.ZipFile(io.BytesIO(r.content)) as z:
            name = next(n for n in z.namelist() if n.endswith(".csv"))
            cache.write_bytes(z.read(name))
    text = cache.read_bytes().decode("cp932")
    rows = list(csv.reader(io.StringIO(text)))
    header = rows[1]  # 1行目はダウンロード日などのメタ情報
    out = {}
    for row in rows[2:]:
        rec = dict(zip(header, row))
        out[rec["ＥＤＩＮＥＴコード"]] = rec
    return out


def list_annual_reports(session, key, days, cache: Path):
    """直近days日分の提出書類一覧から有価証券報告書（訂正を除く）を集める。企業ごとに最新1件。"""
    cache.mkdir(parents=True, exist_ok=True)
    latest = {}
    today = dt.date.today()
    for d in range(days):
        day = today - dt.timedelta(days=d)
        f = cache / f"{day.isoformat()}.json"
        if f.exists():
            results = json.loads(f.read_text())
        else:
            r = get(session, f"{API}/documents.json",
                    {"date": day.isoformat(), "type": 2, "Subscription-Key": key})
            results = r.json().get("results") or []
            if day < today:  # 当日分は追加提出があり得るのでキャッシュしない
                f.write_text(json.dumps(results, ensure_ascii=False))
            time.sleep(0.5)
        for doc in results:
            if (doc.get("docTypeCode") == "120" and doc.get("ordinanceCode") == "010"
                    and doc.get("csvFlag") == "1" and doc.get("withdrawalStatus") == "0"):
                code = doc["edinetCode"]
                if code not in latest or doc["submitDateTime"] > latest[code]["submitDateTime"]:
                    latest[code] = doc
        if d % 50 == 0:
            print(f"[list] {day} まで確認 / 有報 {len(latest)} 社", file=sys.stderr)
    return list(latest.values())


def read_xbrl_csv(content: bytes):
    """type=5 のZIPから本体（jpcrp）のCSV行を返す。UTF-16・タブ区切り。"""
    rows = []
    with zipfile.ZipFile(io.BytesIO(content)) as z:
        for name in z.namelist():
            if not name.endswith(".csv") or "jpcrp" not in os.path.basename(name):
                continue
            text = z.read(name).decode("utf-16")
            reader = csv.reader(io.StringIO(text), delimiter="\t")
            next(reader, None)
            rows.extend(reader)
    return rows


def pick(rows, element_ids, numeric=True):
    """連結の当期値を優先し、なければ個別の当期値。"""
    contexts = [c + suffix
                for suffix in ("", "_NonConsolidatedMember")
                for c in ("CurrentYearInstant", "CurrentYearDuration", "FilingDateInstant")]
    for eid in element_ids:
        by_ctx = {r[2]: r[8] for r in rows if len(r) > 8 and r[0] == eid}
        for ctx in contexts:
            if ctx not in by_ctx:
                continue
            if not numeric:
                return by_ctx[ctx]
            try:
                return float(by_ctx[ctx])
            except ValueError:
                continue
    return None


def count_keywords(text, keywords):
    return {k: text.count(k) for k in keywords if text.count(k)}


def clean(s):
    return re.sub(r"\s+", " ", s or "").strip()


def analyze(doc, rows, codeinfo):
    full_text = "\n".join(r[8] for r in rows if len(r) > 8)
    rec = {
        "提出者名": doc["filerName"],
        "EDINETコード": doc["edinetCode"],
        "証券コード": (doc.get("secCode") or "")[:4],
        "法人番号": doc.get("JCN") or "",
        "業種": codeinfo.get("提出者業種", ""),
        "上場区分": codeinfo.get("上場区分", ""),
        "決算期末": doc.get("periodEnd") or "",
        "有報docID": doc["docID"],
        "有報URL": f"https://disclosure2.edinet-fsa.go.jp/WZEK0040.aspx?{doc['docID']}",
    }
    for col, eids in NUMERIC_ELEMENTS.items():
        rec[col] = pick(rows, eids)
    for col, eid in TEXT_ELEMENTS.items():
        v = clean(pick(rows, [eid], numeric=False))
        rec[col] = v[:TEXT_SNIPPET_LEN] if col.endswith("状況") else v

    invest_hits = count_keywords(full_text, INVEST_KEYWORDS)
    theme_hits = count_keywords(full_text, THEME_KEYWORDS)
    relation_hits = count_keywords((rec["大株主の状況"] or "") + (rec["関係会社の状況"] or ""),
                                   RELATION_KEYWORDS)
    rec["出資シグナル"] = json.dumps(invest_hits, ensure_ascii=False)
    rec["テーマシグナル"] = json.dumps(theme_hits, ensure_ascii=False)
    rec["既存株主系列"] = ", ".join(relation_hits)

    # --- スコア（100点満点目安）---
    cash = rec["現金及び預金"] or rec["現金同等物"] or 0
    # 体力: 1口5,000万が手元資金の1%以下なら満点
    ratio = cash / TICKET_YEN if cash else 0
    capacity = 30 if ratio >= 100 else 20 if ratio >= 20 else 10 if ratio >= 5 else 0
    fit = INDUSTRY_FIT.get(rec["業種"], 0)
    invest = min(25, 5 * len(invest_hits) + (5 if "投資事業有限責任組合" in invest_hits else 0))
    theme = min(15, 3 * len(theme_hits))
    relation = 10 if relation_hits else 0
    rec["体力点"] = capacity
    rec["業種適合点"] = fit
    rec["出資姿勢点"] = invest
    rec["テーマ点"] = theme
    rec["系列点"] = relation
    rec["スコア"] = capacity + fit + invest + theme + relation
    rec["1口5000万可"] = "◯" if ratio >= 5 else ""
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=400, help="遡る日数（有報は年1回なので400日で全社をカバー）")
    ap.add_argument("--out", default="investor_research/out")
    ap.add_argument("--limit", type=int, default=0, help="試験用に取得社数を制限")
    ap.add_argument("--industries", default="", help="カンマ区切りで業種を絞る（空なら全業種）")
    args = ap.parse_args()

    key = os.environ.get("EDINET_API_KEY")
    if not key:
        sys.exit("EDINET_API_KEY が未設定です")

    out = Path(args.out)
    (out / "parsed").mkdir(parents=True, exist_ok=True)
    session = requests.Session()

    codelist = load_codelist(session, out / "EdinetcodeDlInfo.csv")
    docs = list_annual_reports(session, key, args.days, out / "doclists")
    if args.industries:
        wanted = set(args.industries.split(","))
        docs = [d for d in docs if codelist.get(d["edinetCode"], {}).get("提出者業種") in wanted]
    docs.sort(key=lambda d: d["edinetCode"])
    if args.limit:
        docs = docs[: args.limit]
    print(f"[fetch] 対象 {len(docs)} 社", file=sys.stderr)

    records = []
    for i, doc in enumerate(docs, 1):
        cache = out / "parsed" / f"{doc['docID']}.json"
        if cache.exists():
            records.append(json.loads(cache.read_text()))
            continue
        try:
            r = get(session, f"{API}/documents/{doc['docID']}",
                    {"type": 5, "Subscription-Key": key})
            rows = read_xbrl_csv(r.content)
            rec = analyze(doc, rows, codelist.get(doc["edinetCode"], {}))
        except Exception as e:  # 1社の失敗で全体を止めない
            print(f"[skip] {doc['filerName']} {doc['docID']}: {e}", file=sys.stderr)
            continue
        cache.write_text(json.dumps(rec, ensure_ascii=False))
        records.append(rec)
        if i % 100 == 0:
            print(f"[fetch] {i}/{len(docs)}", file=sys.stderr)
        time.sleep(0.5)

    records.sort(key=lambda r: r["スコア"], reverse=True)
    path = out / "investor_candidates.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        w.writeheader()
        w.writerows(records)
    print(f"[done] {len(records)} 社 → {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
