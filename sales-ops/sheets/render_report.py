import asyncio, pathlib, re, markdown
from playwright.async_api import async_playwright

SRC = pathlib.Path("../reports/豪州出張報告_2026-07-21_08-18.md")
OUT = pathlib.Path("FirstAgri_AU_TripReport_2026-08.pdf")

md = SRC.read_text()
title = md.split("\n",1)[0].lstrip("# ").strip()
body = markdown.markdown(md, extensions=["tables","sane_lists","attr_list"])
# H1 は表紙に使うので本文からは落とす
body = re.sub(r"<h1>.*?</h1>", "", body, count=1, flags=re.S)

CSS = """
@page{size:A4;margin:14mm 12mm 16mm;}
:root{--ground:#fff;--panel:#F2F6F0;--ink:#16251A;--soft:#5A6B58;--faint:#8B968A;
 --brand:#2E5E3A;--rule:#D5DED1;--warn:#8A5A1E;--crit:#9B3B2E;
 --disp:"Zen Old Mincho",Georgia,serif;
 --body:"Zen Kaku Gothic New","Hiragino Sans","Noto Sans JP",system-ui,sans-serif;
 --mono:"IBM Plex Mono",ui-monospace,Menlo,monospace;}
*{box-sizing:border-box}
body{margin:0;background:#fff;color:var(--ink);font-family:var(--body);
 font-size:8.4pt;line-height:1.58;-webkit-print-color-adjust:exact;print-color-adjust:exact}

/* 表紙 */
.cover{height:262mm;display:flex;flex-direction:column;justify-content:center;
 page-break-after:always;border-top:3px solid var(--brand);border-bottom:3px solid var(--brand)}
.cover .eyebrow{font-family:var(--mono);font-size:7pt;letter-spacing:.24em;
 text-transform:uppercase;color:var(--soft);margin-bottom:1.2rem}
.cover h1{font-family:var(--disp);font-weight:600;font-size:30pt;line-height:1.25;margin:0 0 1.4rem;
 color:var(--ink);border:0;padding:0;page-break-before:avoid;page-break-after:auto}
.cover .rule{width:64px;height:2px;background:var(--brand);margin-bottom:1.4rem}
.cover .meta{font-size:9pt;color:var(--soft);line-height:2}
.cover .meta b{color:var(--ink)}
.cover .warn{margin-top:2.4rem;border-left:3px solid var(--crit);padding:.4rem 0 .4rem .9rem;
 font-size:8.4pt;color:var(--ink);max-width:150mm}

/* 見出し */
h1{font-family:var(--disp);font-weight:600;font-size:17pt;color:var(--brand);
 margin:0 0 .5rem;padding:.45rem 0 .45rem 0;border-top:2.5px solid var(--brand);
 border-bottom:1px solid var(--rule);page-break-before:always;page-break-after:avoid}
h2{font-family:var(--disp);font-weight:600;font-size:11.5pt;margin:1.5rem 0 .45rem;
 padding-bottom:.22rem;border-bottom:1px solid var(--rule);page-break-after:avoid}
h3{font-family:var(--body);font-weight:700;font-size:9.4pt;color:var(--brand);
 margin:1.15rem 0 .35rem;page-break-after:avoid}
h1+h2,h1+p{page-break-before:avoid}

p{margin:.3rem 0;orphans:2;widows:2}
strong{font-weight:700}
hr{border:0;border-top:1px solid var(--rule);margin:1.1rem 0}

/* リスト */
ul,ol{margin:.3rem 0;padding-left:1.1rem}
li{margin:.16rem 0}
li>strong:first-child{color:var(--ink)}

/* テーブル */
table{width:100%;border-collapse:collapse;margin:.45rem 0 .7rem;font-size:7.6pt;
 page-break-inside:auto}
thead{display:table-header-group}
tr{page-break-inside:avoid}
th{background:var(--brand);color:#fff;font-family:var(--mono);font-size:6.4pt;
 letter-spacing:.07em;text-transform:uppercase;font-weight:600;
 padding:.28rem .34rem;text-align:left;border:0}
td{padding:.28rem .34rem;border-bottom:.5px solid var(--rule);vertical-align:top;line-height:1.45}
tbody tr:nth-child(even) td{background:var(--panel)}
td:first-child{white-space:nowrap}
table table td{font-size:7.2pt}

blockquote{margin:.4rem 0;padding-left:.8rem;border-left:2px solid var(--brand);color:var(--soft)}
code{font-family:var(--mono);font-size:7.2pt;background:var(--panel);padding:.03rem .18rem}
"""

SHELL = """<!doctype html><html lang="ja"><head><meta charset="utf-8">
<title>__T__</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Zen+Kaku+Gothic+New:wght@400;500;700&family=Zen+Old+Mincho:wght@400;600&family=IBM+Plex+Mono:wght@400;600&display=swap">
<style>__CSS__</style></head><body>
<section class="cover">
  <div class="eyebrow">First Agri Inc.　Sales Operations</div>
  <h1>オーストラリア<br>出張報告</h1>
  <div class="rule"></div>
  <div class="meta">
    <b>宛先</b>　社内セールス向け<br>
    <b>担当</b>　笹瀬 類（Global Sales Manager &amp; Founding Member）<br>
    <b>期間</b>　2026-07-21 〜 08-18（29日間）<br>
    <b>最終更新</b>　2026-08-19
  </div>
  <div class="warn"><b>取り扱い注意</b>　顧客名・価格・粗利を含む社内資料です。対外配布はしないでください。<br>✅確定と⚠️見込みをラベルで分けています。<b>見込みを受注として扱わないこと。</b></div>
</section>
__BODY__
</body></html>"""

async def main():
    html = SHELL.replace("__CSS__",CSS).replace("__BODY__",body).replace("__T__",title)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = await b.new_page()
        await pg.emulate_media(color_scheme="light", media="print")
        await pg.set_content(html, wait_until="load")
        await pg.wait_for_timeout(1200)
        await pg.pdf(path=str(OUT), format="A4", print_background=True,
            display_header_footer=True,
            header_template='<div></div>',
            footer_template='<div style="width:100%;font-size:7px;font-family:sans-serif;'
              'color:#8B968A;padding:0 12mm;display:flex;justify-content:space-between">'
              '<span>First Agri Inc.　オーストラリア出張報告　2026-07-21〜08-18　社内資料</span>'
              '<span><span class="pageNumber"></span>&nbsp;/&nbsp;<span class="totalPages"></span></span></div>',
            margin={"top":"12mm","bottom":"14mm","left":"12mm","right":"12mm"})
        await b.close()
    print("done")
asyncio.run(main())
