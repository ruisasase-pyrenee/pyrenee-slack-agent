# -*- coding: utf-8 -*-
"""
Render the SpaceX report Markdown to a typeset PDF.

Handles the subset the report actually uses: ATX headings, GFM tables,
blockquotes, fenced code, bullet/ordered lists, --- rules, and inline
**bold** / `code`. Japanese text is set in IPA Gothic.
"""
import re
import sys
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable, KeepTogether,
)

SRC, OUT, TITLE = sys.argv[1], sys.argv[2], sys.argv[3]

pdfmetrics.registerFont(TTFont("JP", "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf"))
pdfmetrics.registerFont(TTFont("JPM", "/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf"))

NAVY   = colors.HexColor("#12203C")
ACCENT = colors.HexColor("#C8562A")
GREEN  = colors.HexColor("#1F7A4D")
RED    = colors.HexColor("#B03A3A")
GRAY   = colors.HexColor("#5A6070")
LIGHT  = colors.HexColor("#F2F0EA")
LINE   = colors.HexColor("#D8D2C4")

def st(name, **kw):
    base = dict(fontName="JP", fontSize=9.5, leading=14.5, textColor=colors.HexColor("#1C1C1C"),
                alignment=TA_LEFT, spaceAfter=4)
    base.update(kw)
    return ParagraphStyle(name, **base)

S = {
    "h1":   st("h1", fontSize=18, leading=24, textColor=colors.white, spaceBefore=6, spaceAfter=8),
    "h2":   st("h2", fontSize=14, leading=19, textColor=NAVY, spaceBefore=12, spaceAfter=6),
    "h3":   st("h3", fontSize=11.5, leading=16, textColor=ACCENT, spaceBefore=9, spaceAfter=4),
    "p":    st("p"),
    "li":   st("li", leftIndent=7*mm, firstLineIndent=-3.5*mm, spaceAfter=2.5),
    "quote":st("quote", leftIndent=5*mm, rightIndent=3*mm, textColor=NAVY, fontSize=10, leading=15),
    "code": st("code", fontName="JPM", fontSize=8.5, leading=12.5, leftIndent=3*mm),
    "cell": st("cell", fontSize=8.2, leading=11.6, spaceAfter=0),
    "hdr":  st("hdr", fontSize=8.2, leading=11.6, textColor=colors.white, spaceAfter=0),
    "meta": st("meta", fontSize=9, leading=13, textColor=GRAY),
}

def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def inline(t):
    """Markdown inline -> reportlab markup, with semantic colouring."""
    t = esc(t)
    t = re.sub(r"`([^`]+)`", r'<font name="JPM" color="#7A3E9D">\1</font>', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<font color="#1A5FA8">\1</font>', t)
    # cues that carry meaning here; IPA Gothic lacks the dingbats, so map
    # them onto JIS symbols it does ship
    for src, glyph, col in (
        ("\u2705", "\u25cf", "#1F7A4D"),   # check  -> filled circle
        ("\u2714", "\u25cf", "#1F7A4D"),
        ("\u2611\ufe0f", "\u25cf", "#1F7A4D"),
        ("\u2611", "\u25cf", "#1F7A4D"),
        ("\u2717", "\u00d7", "#B03A3A"),   # ballot X -> multiplication sign
        ("\u2718", "\u00d7", "#B03A3A"),
        ("\u2716", "\u00d7", "#B03A3A"),
        ("\u26a0\ufe0f", "\u25b2", "#C8562A"),  # warning -> triangle
        ("\u26a0", "\u25b2", "#C8562A"),
        ("\u25b3", "\u25b3", "#C8562A"),
        ("\u2610", "\u25a1", "#5A6070"),
        ("\u2605", "\u2605", "#C8562A"),
    ):
        t = t.replace(src, f'<font color="{col}">{glyph}</font>')
    for tag, col in (("L1", "#1F7A4D"), ("L2", "#C8562A"), ("L3", "#B03A3A")):
        t = re.sub(rf"(?<![A-Za-z]){tag}(?![A-Za-z0-9])", f'<font color="{col}"><b>{tag}</b></font>', t)
    return t

def band(text):
    """Full-width dark heading band for H1."""
    tbl = Table([[Paragraph(inline(text), S["h1"])]], colWidths=[170*mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), NAVY),
        ("LEFTPADDING", (0,0), (-1,-1), 9), ("RIGHTPADDING", (0,0), (-1,-1), 9),
        ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    return tbl

def make_table(rows):
    head, body = rows[0], rows[1:]
    ncol = len(head)
    avail = 170*mm
    # weight columns by content length so number columns stay narrow
    weights = []
    for i in range(ncol):
        L = max([len(head[i])] + [len(r[i]) for r in body if i < len(r)] or [1])
        weights.append(max(L, 4) ** 0.65)
    total = sum(weights)
    widths = [avail * w / total for w in weights]

    data = [[Paragraph(inline(c), S["hdr"]) for c in head]]
    for r in body:
        r = (r + [""] * ncol)[:ncol]
        data.append([Paragraph(inline(c), S["cell"]) for c in r])

    t = Table(data, colWidths=widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("GRID", (0,0), (-1,-1), 0.4, LINE),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4),
        ("TOPPADDING", (0,0), (-1,-1), 3.5), ("BOTTOMPADDING", (0,0), (-1,-1), 3.5),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0,i), (-1,i), LIGHT))
    t.setStyle(TableStyle(style))
    return t

def parse(md):
    flow = []
    lines = md.split("\n")
    i = 0
    while i < len(lines):
        ln = lines[i]

        if ln.startswith("```"):
            buf = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            box = Table([[Paragraph("<br/>".join(esc(b) or "&nbsp;" for b in buf), S["code"])]],
                        colWidths=[170*mm])
            box.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#F6F5F1")),
                ("BOX", (0,0), (-1,-1), 0.5, LINE),
                ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8),
                ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ]))
            flow += [Spacer(1, 3), box, Spacer(1, 5)]
            continue

        if ln.strip().startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i+1]):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                if not re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i]):
                    cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                    rows.append(cells)
                i += 1
            flow += [Spacer(1, 3), make_table(rows), Spacer(1, 7)]
            continue

        if re.match(r"^---+\s*$", ln):
            flow += [Spacer(1, 4), HRFlowable(width="100%", thickness=0.7, color=LINE), Spacer(1, 6)]
            i += 1; continue

        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            lvl, txt = len(m.group(1)), m.group(2)
            if lvl == 1:
                flow += [Spacer(1, 6), band(txt), Spacer(1, 6)]
            else:
                flow.append(Paragraph(inline(txt), S["h2" if lvl == 2 else "h3"]))
            i += 1; continue

        if ln.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i].lstrip(">").strip()); i += 1
            q = Table([[Paragraph(inline(" ".join(buf)), S["quote"])]], colWidths=[170*mm])
            q.setStyle(TableStyle([
                ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#EEF1F7")),
                ("LEFTPADDING", (0,0), (-1,-1), 10), ("RIGHTPADDING", (0,0), (-1,-1), 8),
                ("TOPPADDING", (0,0), (-1,-1), 6), ("BOTTOMPADDING", (0,0), (-1,-1), 6),
            ]))
            flow += [Spacer(1, 3), q, Spacer(1, 6)]
            continue

        m = re.match(r"^(\s*)[-*]\s+(.*)$", ln)
        if m:
            ind = len(m.group(1)) // 2
            flow.append(Paragraph(
                f'<font color="#C8562A">•</font>&nbsp;&nbsp;{inline(m.group(2))}',
                ParagraphStyle(f"li{ind}", parent=S["li"], leftIndent=(7 + ind*5)*mm)))
            i += 1; continue

        m = re.match(r"^(\s*)(\d+)\.\s+(.*)$", ln)
        if m:
            ind = len(m.group(1)) // 2
            flow.append(Paragraph(
                f'<font color="#C8562A"><b>{m.group(2)}.</b></font>&nbsp;&nbsp;{inline(m.group(3))}',
                ParagraphStyle(f"ol{ind}", parent=S["li"], leftIndent=(7 + ind*5)*mm)))
            i += 1; continue

        if ln.strip():
            flow.append(Paragraph(inline(ln.strip()), S["p"]))
        else:
            flow.append(Spacer(1, 3))
        i += 1
    return flow

def deco(canvas, doc):
    canvas.saveState()
    canvas.setFont("JP", 7.6)
    canvas.setFillColor(GRAY)
    canvas.drawString(20*mm, 11*mm, TITLE)
    canvas.drawRightString(190*mm, 11*mm, str(doc.page))
    canvas.setStrokeColor(LINE); canvas.setLineWidth(0.4)
    canvas.line(20*mm, 14*mm, 190*mm, 14*mm)
    canvas.restoreState()

doc = BaseDocTemplate(OUT, pagesize=A4,
                      leftMargin=20*mm, rightMargin=20*mm,
                      topMargin=16*mm, bottomMargin=18*mm,
                      title=TITLE, author="Rui / Pyrenee")
doc.addPageTemplates([PageTemplate(
    id="body",
    frames=[Frame(20*mm, 18*mm, 170*mm, A4[1]-34*mm, id="f", leftPadding=0,
                  rightPadding=0, topPadding=0, bottomPadding=0)],
    onPage=deco)])

doc.build(parse(open(SRC, encoding="utf-8").read()))
print("wrote", OUT)
