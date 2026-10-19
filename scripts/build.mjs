// Builds dist/index.html: a complete, standalone web page from src/ripple-pond.html.
//
// The source file is a page fragment (title, styles, markup and script, with no
// <html>/<head>/<body> tags) so the same file can be published as a Claude artifact.
// This script wraps it in a full HTML document so it can be opened directly or
// hosted anywhere (GitHub Pages, Netlify, any static file host).
//
// Usage: node scripts/build.mjs

import { readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const srcPath = join(root, 'src', 'ripple-pond.html');
const outPath = join(root, 'dist', 'index.html');

const src = readFileSync(srcPath, 'utf8');

// Everything up to the end of the first </style> belongs in <head>; the rest is the body.
const styleEnd = src.indexOf('</style>');
if (!src.includes('<title>') || styleEnd === -1) {
  console.error('Build failed: src/ripple-pond.html must contain a <title> and a <style> block.');
  process.exit(1);
}
const headPart = src.slice(0, styleEnd + '</style>'.length).trim();
const bodyPart = src.slice(styleEnd + '</style>'.length).trim();

// A small ripple icon, so the browser tab has one without any extra files.
const favicon = 'data:image/svg+xml,' + encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">' +
  '<rect width="64" height="64" rx="14" fill="#0c3b46"/>' +
  '<circle cx="32" cy="32" r="7" fill="#eef3ef"/>' +
  '<circle cx="32" cy="32" r="15" fill="none" stroke="#eef3ef" stroke-opacity=".7" stroke-width="3"/>' +
  '<circle cx="32" cy="32" r="24" fill="none" stroke="#eef3ef" stroke-opacity=".35" stroke-width="3"/>' +
  '</svg>'
);

const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="A calm koi pond to relax in: tap for ripples and gentle notes, feed the koi, breathe with a lotus, let worries drift away, or fall asleep to it.">
<meta name="theme-color" content="#06121c">
<meta name="color-scheme" content="dark">
<link rel="icon" href="${favicon}">
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
</body>
</html>
`;

mkdirSync(dirname(outPath), { recursive: true });
writeFileSync(outPath, html);
console.log(`Built dist/index.html (${(Buffer.byteLength(html) / 1024).toFixed(1)} KB)`);
