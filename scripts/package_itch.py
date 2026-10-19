"""Packages the built website into release/ripple-pond-itch.zip for itch.io.

    node scripts/build.mjs
    python scripts/package_itch.py

itch.io needs index.html at the root of the zip. Store screenshots are left out
because the game does not use them.
"""
import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
OUT = ROOT / "release" / "ripple-pond-itch.zip"

if not (DOCS / "index.html").exists():
    raise SystemExit("docs/index.html not found. Run: node scripts/build.mjs")

OUT.parent.mkdir(parents=True, exist_ok=True)
count = 0
with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(DOCS.rglob("*")):
        rel = f.relative_to(DOCS).as_posix()
        if f.is_file() and not rel.startswith("screenshots/"):
            z.write(f, rel)
            count += 1
print(f"Wrote {OUT.relative_to(ROOT)} ({count} files, {OUT.stat().st_size / 1024:.0f} KB)")
