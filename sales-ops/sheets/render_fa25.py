import asyncio, pathlib
from playwright.async_api import async_playwright
SCR = pathlib.Path(".").resolve()
A4W, A4H = 794.0, 1123.0
SHELL = """<!doctype html><html><head><meta charset="utf-8"><style>
*,*::before,*::after{box-sizing:border-box}html,body{margin:0;padding:0}
@page{size:A4;margin:0}.sheet{max-width:none!important}
</style></head><body>__C__</body></html>"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = await b.new_page()
        await pg.emulate_media(color_scheme="light", media="screen")
        html = (SCR/"fa25_src.html").read_text()
        s = 1.0
        for _ in range(6):
            await pg.set_viewport_size({"width": round(A4W/s), "height": round(A4H/s)})
            await pg.set_content(SHELL.replace("__C__", html), wait_until="load")
            await pg.wait_for_timeout(300)
            h = await pg.evaluate("document.querySelector('.sheet').getBoundingClientRect().height")
            if h <= (A4H/s) - 4: break
            s = max(.4, round((A4H/h)*.99, 3))
        await pg.pdf(path=str(SCR/"FirstAgri_FA25_2026-08.pdf"), format="A4",
                     print_background=True, scale=s, margin={"top":"0","bottom":"0","left":"0","right":"0"})
        await pg.screenshot(path=str(SCR/"fa25_pv.png"), full_page=True)
        print("scale", s, "h", round(h))
        await b.close()
asyncio.run(main())
