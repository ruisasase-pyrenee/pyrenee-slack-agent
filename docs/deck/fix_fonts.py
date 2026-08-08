# -*- coding: utf-8 -*-
"""
pptxgenjs copies the Latin typeface into the East-Asian slot
(<a:ea typeface="Cambria">). Cambria and Calibri carry no Japanese glyphs, so
PowerPoint renders every Japanese run as tofu. Rewrite the ea slot to a real
Japanese face and tag the runs as ja-JP.

Plain string edits on the XML text — round-tripping OOXML through ElementTree
rewrites namespace prefixes and corrupts the package.
"""
import re
import shutil
import sys
import zipfile
from pathlib import Path

SRC = Path(sys.argv[1])
JP = "Yu Gothic"          # ships with Office 2016+ on Windows and Mac
LATIN = ("Cambria", "Calibri")

tmp = SRC.with_suffix(".tmp.pptx")
changed = {"ea": 0, "lang": 0, "theme": 0}

with zipfile.ZipFile(SRC) as zin, zipfile.ZipFile(
    tmp, "w", zipfile.ZIP_DEFLATED
) as zout:
    for item in zin.infolist():
        data = zin.read(item.filename)

        if item.filename.endswith(".xml") and (
            "/slides/" in item.filename
            or "/notesSlides/" in item.filename
            or "/slideMasters/" in item.filename
            or "/slideLayouts/" in item.filename
            or "/charts/" in item.filename
        ):
            x = data.decode("utf-8")

            for face in LATIN:
                new, n = re.subn(
                    rf'<a:ea typeface="{face}"', f'<a:ea typeface="{JP}"', x
                )
                x, changed["ea"] = new, changed["ea"] + n

            # tag runs as Japanese so PowerPoint picks the ea face
            new, n = re.subn(
                r'lang="en-US"(?! altLang)', 'lang="ja-JP" altLang="en-US"', x
            )
            x, changed["lang"] = new, changed["lang"] + n

            data = x.encode("utf-8")

        elif item.filename.startswith("ppt/theme/"):
            x = data.decode("utf-8")
            new, n = re.subn(r'<a:ea typeface=""/>', f'<a:ea typeface="{JP}"/>', x)
            x, changed["theme"] = new, changed["theme"] + n
            data = x.encode("utf-8")

        zout.writestr(item, data)

shutil.move(str(tmp), str(SRC))
print(f"ea typeface -> {JP}: {changed['ea']} runs")
print(f"lang -> ja-JP: {changed['lang']} runs")
print(f"theme ea slots: {changed['theme']}")

# verify
with zipfile.ZipFile(SRC) as z:
    bad = 0
    for n in z.namelist():
        if n.endswith(".xml") and "/slides/" in n:
            t = z.read(n).decode("utf-8")
            for face in LATIN:
                bad += t.count(f'<a:ea typeface="{face}"')
print("remaining Latin-only ea slots:", bad)
sys.exit(1 if bad else 0)
