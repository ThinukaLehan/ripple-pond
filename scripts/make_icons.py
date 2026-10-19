"""Renders assets/icon.svg into the PNG app icons in assets/icons/.

Run this only when the icon artwork changes; the PNGs are committed.

    python scripts/make_icons.py

Needs Playwright with Chromium (see README).
"""
import asyncio
import pathlib

from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SVG = (ROOT / "assets" / "icon.svg").read_text(encoding="utf-8")
OUT = ROOT / "assets" / "icons"

# (file name, size in px, corner radius as a fraction of the size)
# "icon-*" are rounded for desktops and browsers; "maskable-*" and the Apple icon are
# full-bleed squares because Android and iOS cut their own shape.
ICONS = [
    ("icon-512.png", 512, 0.22),
    ("icon-192.png", 192, 0.22),
    ("maskable-512.png", 512, 0),
    ("maskable-192.png", 192, 0),
    ("apple-touch-icon.png", 180, 0),
    ("favicon-32.png", 32, 0.22),
]


async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        for name, size, radius in ICONS:
            page = await browser.new_page(viewport={"width": size, "height": size})
            html = (
                "<html><body style='margin:0;background:transparent'>"
                f"<div style='width:{size}px;height:{size}px;border-radius:{radius * size}px;overflow:hidden'>"
                f"{SVG.replace('<svg ', f'<svg width=\"{size}\" height=\"{size}\" ', 1)}"
                "</div></body></html>"
            )
            await page.set_content(html)
            await page.screenshot(path=str(OUT / name), omit_background=True)
            await page.close()
            print("wrote", name)
        await browser.close()


asyncio.run(main())
