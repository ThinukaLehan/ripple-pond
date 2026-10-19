"""Smoke test for Ripple Pond.

Serves the built website (docs/) from a local web server, plays through every
feature in headless Chromium at phone and desktop sizes, and checks that the game
installs as an app and works offline. Fails if anything breaks or the page logs
an error. Screenshots are saved to tests/output/ so you can look at the results.

Setup (once):
    pip install playwright
    python -m playwright install chromium

Run (after `node scripts/build.mjs`):
    python tests/smoke_test.py

The feature test uses test-page.html, a copy of index.html with two test-only
changes: the sleep timer runs fast (1 "minute" = 0.2 s) and the pond's state is
exposed on window.__t so the test can find the frog and check the koi and food.
The install/offline test uses the real index.html.
"""
import asyncio
import functools
import http.server
import json
import pathlib
import shutil
import sys
import threading

from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tests" / "output"
SITE = OUT / "site"
FAILURES = []


def check(label, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {label}{(' (' + str(detail) + ')') if detail != '' else ''}")
    if not ok:
        FAILURES.append(label)


def make_site():
    """Copy docs/ to tests/output/site/ and add test-page.html next to index.html."""
    docs = ROOT / "docs"
    if not (docs / "index.html").exists():
        sys.exit("Test setup failed: docs/index.html not found. Run: node scripts/build.mjs")
    html = (docs / "index.html").read_text(encoding="utf-8")
    for needle in ("const SLEEP_SECS_PER_MIN = 60;", "initFrog();\n"):
        if needle not in html:
            sys.exit(f"Test setup failed: '{needle.strip()}' not found in docs/index.html.")
    html = html.replace("const SLEEP_SECS_PER_MIN = 60;", "const SLEEP_SECS_PER_MIN = 0.2;")
    html = html.replace(
        "initFrog();\n",
        "initFrog();\nwindow.__t = { frog, dfly, food, sleep, koi, pads, breath, boats };\n",
        1,
    )
    shutil.rmtree(SITE, ignore_errors=True)
    shutil.copytree(docs, SITE)
    (SITE / "test-page.html").write_text(html, encoding="utf-8")


def start_server():
    """Serve tests/output/site on a free localhost port (localhost allows service workers)."""
    class Quiet(http.server.SimpleHTTPRequestHandler):
        extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                          ".webmanifest": "application/manifest+json", ".woff2": "font/woff2", ".js": "text/javascript"}

        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(SITE)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}/"


async def main():
    make_site()
    server, base = start_server()
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])

        def watch(pg, name):
            pg.on("console", lambda m: errors.append((name, m.text)) if m.type == "error" else None)
            pg.on("pageerror", lambda e: errors.append((name, str(e))))

        async def open_page(name, viewport):
            ctx = await browser.new_context(viewport=viewport, service_workers="block")
            pg = await ctx.new_page()
            watch(pg, name)
            await pg.goto(base + "test-page.html")
            await pg.wait_for_timeout(600)
            return pg

        js = lambda pg, s: pg.evaluate(s)
        text = lambda pg, sel: pg.evaluate(f"document.querySelector('{sel}').textContent")

        # ---------- Desktop, daytime ----------
        print("Desktop (1280x800), daytime")
        dk = await open_page("desktop", {"width": 1280, "height": 800})
        await dk.click("#btnSettings"); await dk.click("#tm-day"); await dk.click("#btnDone")
        await dk.wait_for_timeout(2500)

        await dk.mouse.click(640, 400)
        await dk.wait_for_timeout(300)
        check("Tapping the water hides the start hint", await js(dk, "document.querySelector('#hint').classList.contains('gone')"))

        frog = await js(dk, "({x: __t.frog.x, y: __t.frog.y, pad: __t.frog.pad})")
        check("Frog sits on a lily pad", frog["pad"] >= 0, frog["pad"])
        await dk.mouse.click(frog["x"], frog["y"])
        await dk.wait_for_timeout(150)
        check("Tapping the frog makes it hop", await js(dk, "!!__t.frog.hop"))
        await dk.wait_for_timeout(1600)
        check("Frog lands on a different pad",
              await js(dk, "!__t.frog.hop") and await js(dk, "__t.frog.pad") != frog["pad"])

        await dk.click("#btnFeed")
        check("Feed button arms feeding", await js(dk, "document.querySelector('#btnFeed').classList.contains('on')"))
        # Scatter away from where the koi gathered after the first tap, and count straight
        # away: hungry koi nearby can eat a pellet within a fraction of a second.
        await dk.mouse.click(1150, 640)
        await dk.wait_for_timeout(30)
        pellets = await js(dk, "__t.food.length")
        check("Tapping the water scatters a pinch of food", 10 <= pellets <= 12, f"{pellets} of 12")
        await dk.wait_for_timeout(2500)
        await dk.screenshot(path=str(OUT / "desktop-feeding.png"))
        await dk.wait_for_timeout(10000)
        check("Koi eat the food", await js(dk, "__t.food.length") < 12, f"{await js(dk, '__t.food.length')} left")

        await js(dk, "__t.dfly.spawnT = 0")
        await dk.wait_for_timeout(2500)
        check("Dragonfly visits in daytime", await js(dk, "__t.dfly.active"))
        await dk.screenshot(path=str(OUT / "desktop-dragonfly.png"))

        await js(dk, "__t.frog.croakT = 0")
        await dk.wait_for_timeout(200)
        check("Frog croaks", await js(dk, "__t.frog.croak > 0"))

        await dk.click("#btnBreathe"); await dk.click("#len-1"); await dk.click("#btnBreatheStart")
        await dk.wait_for_timeout(500)
        check("Breathing session starts", await text(dk, "#breathWord") == "Breathe in")
        await dk.wait_for_timeout(4500)
        word = await text(dk, "#breathWord")
        check("Breathing moves to the next phase on time", word in ("Hold", "Breathe out"), word)
        await dk.screenshot(path=str(OUT / "desktop-breathing.png"))
        await dk.click("#btnBreathEnd")
        check("Ending the session hides the guide", await js(dk, "document.querySelector('#breath').hidden"))

        # ---------- Phone, night ----------
        print("Phone (390x844), night")
        ph = await open_page("phone", {"width": 390, "height": 844})
        await ph.click("#btnSettings"); await ph.click("#tm-night"); await ph.click("#btnDone")
        await ph.wait_for_timeout(2500)

        bar_w = await js(ph, "document.querySelector('.bar').getBoundingClientRect().width")
        check("Bottom bar fits on a phone screen", bar_w <= 358, f"{bar_w:.0f}px")

        await ph.click("#btnLetgo")
        check("Let go button is disabled while empty", await js(ph, "document.querySelector('#btnLetgoGo').disabled"))
        await ph.fill("#letgoText", "The presentation on Friday")
        await ph.click("#btnLetgoGo")
        await ph.wait_for_timeout(2500)
        check("Paper boat sets off", await js(ph, "__t.boats.length") == 1)
        check("Nothing typed is kept in the box", await js(ph, "document.querySelector('#letgoText').value") == "")
        await ph.screenshot(path=str(OUT / "phone-boat.png"))

        await js(ph, "__t.frog.tongueT = 0")
        await ph.wait_for_timeout(1000)
        check("Frog tries to catch a firefly at night", await js(ph, "__t.frog.tongueT > 0"))

        await ph.click("#btnSettings"); await ph.click("#sl-15"); await ph.click("#btnSleepStart")
        await ph.wait_for_timeout(500)
        check("Sleep mode hides the controls", await js(ph, "document.body.classList.contains('sleeping')"))
        await ph.wait_for_timeout(4500)
        check("Sleep timer finishes", await js(ph, "__t.sleep.ended"))
        food_before = await js(ph, "__t.food.length")
        await ph.mouse.click(195, 300)
        await ph.wait_for_timeout(300)
        check("Tapping while asleep shows the timer instead of a pebble",
              await text(ph, "#sleepText") == "Sleep timer finished" and await js(ph, "__t.food.length") == food_before)
        await ph.screenshot(path=str(OUT / "phone-sleep.png"))
        await ph.click("#btnWake")
        await ph.wait_for_timeout(300)
        check("Wake up brings the controls back", not await js(ph, "document.body.classList.contains('sleeping')"))

        # ---------- Installable app and offline play ----------
        print("Installable app and offline play")
        ctx = await browser.new_context(viewport={"width": 390, "height": 844})
        app = await ctx.new_page()
        watch(app, "app")
        await app.goto(base)
        await app.wait_for_timeout(500)

        manifest_href = await js(app, "document.querySelector('link[rel=manifest]')?.getAttribute('href')")
        check("Page links a web app manifest", manifest_href == "manifest.webmanifest", manifest_href)
        manifest = json.loads((SITE / "manifest.webmanifest").read_text(encoding="utf-8"))
        check("Manifest has the name, start page and standalone display",
              manifest.get("name") == "Ripple Pond" and manifest.get("start_url") == "./" and manifest.get("display") == "standalone")
        sizes = {(i["sizes"], i.get("purpose", "any")) for i in manifest.get("icons", [])}
        check("Manifest has 192 and 512 icons, normal and maskable",
              {("192x192", "any"), ("512x512", "any"), ("192x192", "maskable"), ("512x512", "maskable")} <= sizes)
        files = [i["src"] for i in manifest["icons"]] + [s["src"] for s in manifest.get("screenshots", [])]
        missing = [f for f in files if not (SITE / f).exists()]
        check("Every icon and screenshot in the manifest exists", not missing, missing)

        scope = await js(app, "navigator.serviceWorker.ready.then(r => r.scope)")
        check("Offline service worker installs", scope == base, scope)
        await app.reload()
        await app.wait_for_timeout(500)
        check("Service worker controls the page", await js(app, "!!navigator.serviceWorker.controller"))
        await js(app, "document.fonts.ready")
        check("Bundled fonts load (no Google Fonts needed)",
              await js(app, "document.fonts.check('600 20px \"Shippori Mincho\"') && document.fonts.check('500 14px Figtree')"))
        google = await js(app, "performance.getEntriesByType('resource').filter(e => /fonts\\.(googleapis|gstatic)/.test(e.name)).length")
        check("Nothing is loaded from other websites", google == 0, google)

        await ctx.set_offline(True)
        await app.reload()
        await app.wait_for_timeout(800)
        check("Game opens with no internet connection",
              await js(app, "document.title") == "Ripple Pond" and await js(app, "!!document.querySelector('#pond')"))
        await app.mouse.click(195, 400)
        await app.wait_for_timeout(300)
        check("Game is playable offline", await js(app, "document.querySelector('#hint').classList.contains('gone')"))
        await app.screenshot(path=str(OUT / "phone-offline.png"))
        await app.goto(base + "privacy.html")
        check("Privacy page opens offline", "Privacy Policy" in (await js(app, "document.title")))
        await ctx.set_offline(False)
        await ctx.close()

        await browser.close()
    server.shutdown()

    check("No errors in the browser console", not errors, errors)
    print()
    if FAILURES:
        print(f"{len(FAILURES)} check(s) failed: {', '.join(FAILURES)}")
        sys.exit(1)
    print(f"All checks passed. Screenshots are in {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    asyncio.run(main())
