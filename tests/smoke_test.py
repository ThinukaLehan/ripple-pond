"""Smoke test for Ripple Pond.

Plays through every feature in headless Chromium at phone and desktop sizes and
fails if anything breaks or the page logs an error. Screenshots are saved to
tests/output/ so you can look at the results.

Setup (once):
    pip install playwright
    python -m playwright install chromium

Run (after `node scripts/build.mjs`):
    python tests/smoke_test.py

The test works on a copy of dist/index.html with two test-only changes:
the sleep timer runs fast (1 "minute" = 0.2 s) and the pond's state is exposed
on window.__t so the test can find the frog and check the koi and food.
"""
import asyncio
import pathlib
import sys

from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "tests" / "output"
FAILURES = []


def check(label, ok, detail=""):
    print(f"  {'PASS' if ok else 'FAIL'}  {label}{(' (' + str(detail) + ')') if detail != '' else ''}")
    if not ok:
        FAILURES.append(label)


def make_test_page():
    html = (ROOT / "dist" / "index.html").read_text(encoding="utf-8")
    for needle in ("const SLEEP_SECS_PER_MIN = 60;", "initFrog();\n"):
        if needle not in html:
            sys.exit(f"Test setup failed: '{needle.strip()}' not found in dist/index.html. Run the build first.")
    html = html.replace("const SLEEP_SECS_PER_MIN = 60;", "const SLEEP_SECS_PER_MIN = 0.2;")
    html = html.replace(
        "initFrog();\n",
        "initFrog();\nwindow.__t = { frog, dfly, food, sleep, koi, pads, breath, boats };\n",
        1,
    )
    OUT.mkdir(parents=True, exist_ok=True)
    page = OUT / "test-page.html"
    page.write_text(html, encoding="utf-8")
    return page


async def main():
    page_file = make_test_page()
    errors = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])

        async def open_page(name, viewport):
            pg = await browser.new_page(viewport=viewport)
            # Font downloads may fail in offline test environments; that is not a game error.
            pg.on("console", lambda m: errors.append((name, m.text))
                  if m.type == "error" and "Failed to load resource" not in m.text else None)
            pg.on("pageerror", lambda e: errors.append((name, str(e))))
            await pg.goto(page_file.as_uri())
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

        await browser.close()

    check("No errors in the browser console", not errors, errors)
    print()
    if FAILURES:
        print(f"{len(FAILURES)} check(s) failed: {', '.join(FAILURES)}")
        sys.exit(1)
    print(f"All checks passed. Screenshots are in {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    asyncio.run(main())
