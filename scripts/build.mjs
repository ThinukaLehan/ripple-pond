// Builds the publishable website into docs/ (served by GitHub Pages from main /docs).
//
//   docs/index.html            the game, as a complete page
//   docs/privacy.html          privacy policy
//   docs/manifest.webmanifest  makes the game installable (Add to Home Screen, app stores)
//   docs/sw.js                 service worker: the game works offline after the first visit
//   docs/fonts/, icons/, screenshots/
//
// src/ripple-pond.html is a page fragment (no <html>/<head>/<body>) that loads Google
// Fonts, so the same file can be published as a Claude artifact. For the website, this
// script swaps Google Fonts for the bundled copies in assets/fonts so nothing is loaded
// from other sites and the game works fully offline.
//
// Usage: node scripts/build.mjs        (Node 18+, no packages needed)

import { readFileSync, writeFileSync, mkdirSync, rmSync, readdirSync, copyFileSync, existsSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const out = join(root, 'docs');
const SITE_URL = 'https://thinukalehan.github.io/ripple-pond/';
const NAME = 'Ripple Pond';
const DESCRIPTION = 'A calm koi pond to relax in: tap for ripples and gentle notes, feed the koi, breathe with a lotus, let worries drift away, or fall asleep to it.';
const BG = '#06121c';

const fail = msg => { console.error('Build failed: ' + msg); process.exit(1); };

// ---------- fonts ----------
const FONTS = [
  ['Figtree', 400, 'figtree-latin-400-normal.woff2'],
  ['Figtree', 500, 'figtree-latin-500-normal.woff2'],
  ['Figtree', 600, 'figtree-latin-600-normal.woff2'],
  ['Shippori Mincho', 500, 'shippori-mincho-latin-500-normal.woff2'],
  ['Shippori Mincho', 600, 'shippori-mincho-latin-600-normal.woff2'],
];
const LATIN_RANGE = 'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD';
const fontCss = '<style>\n/* Bundled fonts (SIL Open Font License, see fonts/OFL-*.txt) */\n' +
  FONTS.map(([family, weight, file]) =>
    `@font-face{font-family:'${family}';font-style:normal;font-weight:${weight};font-display:swap;src:url(fonts/${file}) format('woff2');unicode-range:${LATIN_RANGE}}`
  ).join('\n') + '\n</style>';
const fontPreload = '<link rel="preload" href="fonts/shippori-mincho-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin>';

// ---------- game page ----------
let game = readFileSync(join(root, 'src', 'ripple-pond.html'), 'utf8');
const googleFontLines = /^<link[^>]+fonts\.(googleapis|gstatic)\.com[^>]*>\r?\n/gm;
if ((game.match(googleFontLines) || []).length !== 3) fail('expected 3 Google Fonts <link> lines in src/ripple-pond.html.');
game = game.replace(googleFontLines, '');
// the privacy link points at the live site in the artifact; on the website keep it local so it works offline
game = game.split(SITE_URL + 'privacy.html').join('privacy.html');

const styleEnd = game.indexOf('</style>');
if (!game.includes('<title>') || styleEnd === -1) fail('src/ripple-pond.html must contain a <title> and a <style> block.');
const headPart = game.slice(0, styleEnd + '</style>'.length).trim();
const bodyPart = game.slice(styleEnd + '</style>'.length).trim();

const swRegister = `<script>
// Offline support: cache the game after the first visit (website and installed app only).
if ('serviceWorker' in navigator && (location.protocol === 'https:' || ['localhost', '127.0.0.1'].includes(location.hostname))) {
  addEventListener('load', () => { navigator.serviceWorker.register('sw.js').catch(() => {}); });
}
</script>`;

const indexHtml = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="${DESCRIPTION}">
<meta name="theme-color" content="${BG}">
<meta name="color-scheme" content="dark">
<link rel="canonical" href="${SITE_URL}">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" sizes="32x32" href="icons/favicon-32.png">
<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="${NAME}">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta property="og:type" content="website">
<meta property="og:title" content="${NAME}">
<meta property="og:description" content="${DESCRIPTION}">
<meta property="og:url" content="${SITE_URL}">
<meta property="og:image" content="${SITE_URL}screenshots/wide-1.png">
<meta name="twitter:card" content="summary_large_image">
${fontPreload}
${fontCss}
<style>
/* Base reset (matches the artifact host's page skeleton) */
:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}
body{margin:0;font:14px/1.4 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
img{max-width:100%}
[hidden]{display:none!important}
</style>
${headPart}
</head>
<body>
${bodyPart}
${swRegister}
</body>
</html>
`;

// ---------- privacy page ----------
let privacy = readFileSync(join(root, 'src', 'privacy.html'), 'utf8');
if (!privacy.includes('<!--FONTS-->')) fail('src/privacy.html must contain <!--FONTS-->.');
privacy = privacy.replace('<!--FONTS-->', fontCss);

// ---------- copy assets ----------
rmSync(out, { recursive: true, force: true });
mkdirSync(out, { recursive: true });
const copyDir = (from, to, filter = () => true) => {
  mkdirSync(join(out, to), { recursive: true });
  const files = readdirSync(join(root, from)).filter(filter).sort();
  for (const f of files) copyFileSync(join(root, from, f), join(out, to, f));
  return files.map(f => `${to}/${f}`);
};
const fontFiles = copyDir('assets/fonts', 'fonts');
const iconFiles = copyDir('assets/icons', 'icons', f => f.endsWith('.png'));
const shotFiles = existsSync(join(root, 'assets', 'screenshots'))
  ? copyDir('assets/screenshots', 'screenshots', f => f.endsWith('.png')) : [];
for (const [, , file] of FONTS) if (!fontFiles.includes(`fonts/${file}`)) fail(`missing assets/fonts/${file}`);
for (const f of ['icon-192.png', 'icon-512.png', 'maskable-192.png', 'maskable-512.png', 'apple-touch-icon.png', 'favicon-32.png'])
  if (!iconFiles.includes(`icons/${f}`)) fail(`missing assets/icons/${f} (run: python scripts/make_icons.py)`);

writeFileSync(join(out, 'index.html'), indexHtml);
writeFileSync(join(out, 'privacy.html'), privacy);
writeFileSync(join(out, '.nojekyll'), ''); // serve files as-is on GitHub Pages

// ---------- manifest ----------
const SHOTS = [
  ['narrow-1.png', '1080x1920', 'narrow', 'Tap the water: ripples spread and the koi gather'],
  ['narrow-2.png', '1080x1920', 'narrow', 'Breathe with the Pond: follow the lotus as it opens and closes'],
  ['narrow-3.png', '1080x1920', 'narrow', 'Let go: a paper boat carries your worry away'],
  ['narrow-4.png', '1080x1920', 'narrow', 'Night pond with moonlight, fireflies and the frog'],
  ['wide-1.png', '1920x1080', 'wide', 'Feeding the koi on a sunny afternoon'],
  ['wide-2.png', '1920x1080', 'wide', 'Breathe with the Pond under the night sky'],
];
const manifest = {
  id: './',
  name: NAME,
  short_name: NAME,
  description: DESCRIPTION,
  lang: 'en',
  dir: 'ltr',
  start_url: './',
  scope: './',
  display: 'standalone',
  orientation: 'any',
  background_color: BG,
  theme_color: BG,
  categories: ['games', 'health', 'lifestyle'],
  icons: [
    { src: 'icons/icon-192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
    { src: 'icons/icon-512.png', sizes: '512x512', type: 'image/png', purpose: 'any' },
    { src: 'icons/maskable-192.png', sizes: '192x192', type: 'image/png', purpose: 'maskable' },
    { src: 'icons/maskable-512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
  ],
  screenshots: SHOTS.filter(([f]) => shotFiles.includes(`screenshots/${f}`)).map(([f, sizes, form_factor, label]) =>
    ({ src: `screenshots/${f}`, sizes, type: 'image/png', form_factor, label })),
};
writeFileSync(join(out, 'manifest.webmanifest'), JSON.stringify(manifest, null, 2) + '\n');

// ---------- service worker ----------
// Everything the game needs to run offline. Screenshots are only for app stores, so they are not cached.
const precache = ['./', 'index.html', 'privacy.html', 'manifest.webmanifest', ...fontFiles.filter(f => f.endsWith('.woff2')), ...iconFiles];
const hash = createHash('sha256');
for (const f of precache) if (f !== './') hash.update(f).update(readFileSync(join(out, f)));
const version = hash.digest('hex').slice(0, 12);
const sw = `// Ripple Pond service worker (generated by scripts/build.mjs, do not edit by hand).
// The version changes whenever any cached file changes, so players get updates automatically.
const VERSION = '${version}';
const CACHE = 'ripple-pond-' + VERSION;
const PRECACHE = ${JSON.stringify(precache, null, 2)};

self.addEventListener('install', event => {
  event.waitUntil(caches.open(CACHE).then(cache => cache.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k.startsWith('ripple-pond-') && k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

const timeout = ms => new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), ms));

self.addEventListener('fetch', event => {
  const req = event.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== self.location.origin) return;

  // Pages: try the network first so updates show up, fall back to the cached copy offline.
  if (req.mode === 'navigate') {
    event.respondWith((async () => {
      try {
        const res = await Promise.race([fetch(req), timeout(4000)]);
        if (res && res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
        return res;
      } catch (e) {
        return (await caches.match(req, { ignoreSearch: true })) || (await caches.match('index.html')) || Response.error();
      }
    })());
    return;
  }

  // Fonts, icons and other files: use the cache first, then the network.
  event.respondWith(
    caches.match(req).then(hit => hit || fetch(req).then(res => {
      if (res && res.ok && res.type === 'basic') { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
      return res;
    }))
  );
});
`;
writeFileSync(join(out, 'sw.js'), sw);

const kb = f => (Buffer.byteLength(readFileSync(join(out, f))) / 1024).toFixed(1);
console.log(`Built docs/ (version ${version})`);
console.log(`  index.html ${kb('index.html')} KB, privacy.html ${kb('privacy.html')} KB, ${fontFiles.length} font files, ${iconFiles.length} icons, ${shotFiles.length} screenshots`);
