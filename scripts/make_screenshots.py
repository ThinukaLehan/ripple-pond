"""Captures the app store / install screenshots into assets/screenshots/.

Run after building whenever the look of the game changes, then build again so the
screenshots are copied into docs/:

    node scripts/build.mjs
    python scripts/make_screenshots.py
    node scripts/build.mjs

Phone shots are 1080x1920 and desktop shots 1920x1080, the sizes the app stores accept.
Needs Playwright with Chromium (see README).
"""
import asyncio
import functools
import http.server
import pathlib
import shutil
import tempfile
import threading

from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "screenshots"
PHONE = dict(viewport={"width": 360, "height": 640}, device_scale_factor=3)
WIDE = dict(viewport={"width": 1280, "height": 720}, device_scale_factor=1.5)


def serve(site):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map, ".woff2": "font/woff2"}

        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(site)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}/shot.html"


async def scene(browser, url, size, time_mode, steps, name):
    ctx = await browser.new_context(**size, service_workers="block")
    pg = await ctx.new_page()
    await pg.goto(url)
    await pg.evaluate("document.fonts.ready")
    await pg.click("#btnSettings")
    await pg.click(f"#tm-{time_mode}")
    await pg.click("#btnDone")
    await pg.wait_for_timeout(2500)  # let the sky settle into the chosen time of day
    vw = size["viewport"]["width"]
    vh = size["viewport"]["height"]
    await steps(pg, vw, vh)
    await pg.screenshot(path=str(OUT / name))
    await ctx.close()
    print("wrote", name)


async def tap_and_feed(pg, w, h):
    await pg.click("#btnFeed")
    await pg.mouse.click(w * 0.5, h * 0.5)
    await pg.wait_for_timeout(3600)  # koi gather and the feeding tip fades out
    await pg.mouse.click(w * 0.3, h * 0.33)
    await pg.wait_for_timeout(900)
    await pg.mouse.click(w * 0.7, h * 0.66)
    await pg.wait_for_timeout(600)


async def breathe(pg, w, h):
    await pg.click("#btnBreathe")
    await pg.click("#len-3")
    await pg.click("#btnBreatheStart")
    # capture while the lotus is fully open ("Hold"), with no koi crossing the guide text
    await pg.wait_for_function("document.querySelector('#breathWord').textContent === 'Hold'", timeout=15000)
    await pg.wait_for_timeout(250)


async def let_go(pg, w, h):
    await pg.click("#btnLetgo")
    await pg.fill("#letgoText", "The presentation on Friday")
    await pg.click("#btnLetgoGo")
    await pg.wait_for_timeout(4200)


async def night(pg, w, h):
    await pg.mouse.click(w * 0.5, h * 0.55)
    await pg.wait_for_timeout(2600)


async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        site = pathlib.Path(tmp) / "site"
        shutil.copytree(ROOT / "docs", site)
        html = (site / "index.html").read_text(encoding="utf-8")
        # keep the start hint out of the shots
        html = html.replace('<div class="hint" id="hint">', '<div class="hint gone" id="hint">', 1)
        (site / "shot.html").write_text(html, encoding="utf-8")
        server, url = serve(site)
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            await scene(browser, url, PHONE, "day", tap_and_feed, "narrow-1.png")
            await scene(browser, url, PHONE, "sunset", breathe, "narrow-2.png")
            await scene(browser, url, PHONE, "sunset", let_go, "narrow-3.png")
            await scene(browser, url, PHONE, "night", night, "narrow-4.png")
            await scene(browser, url, WIDE, "day", tap_and_feed, "wide-1.png")
            await scene(browser, url, WIDE, "night", breathe, "wide-2.png")
            await browser.close()
        server.shutdown()


asyncio.run(main())
