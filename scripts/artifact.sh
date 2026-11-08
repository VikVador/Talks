#!/usr/bin/env bash
# Stage a deck as a self-contained folder, ready to publish as a Claude artifact (the draft we iterate on).
#   bash scripts/artifact.sh drafts/2026-11-12-weekly-gilles/talk.md OUTDIR
# OUTDIR gets index.html plus every local file the deck uses, at paths without "../":
#   shared assets keep their path from the repo root (media/..., team/..., theme/fonts/...),
#   the talk's own files keep their path from the talk folder (figures/...).
# Publish OUTDIR/index.html as the artifact page and every other file of OUTDIR as a supporting file.
# The staged deck embeds Arimo (SIL Open Font License, theme/fonts/Arimo-OFL.txt).
set -euo pipefail
cd "$(dirname "$0")/.."
md="$1"; outdir="$2"
case "$outdir" in /*) ;; *) echo "OUTDIR must be an absolute path (it is emptied first)" >&2; exit 1;; esac
bash scripts/build.sh "$md" >/dev/null
html="${md%.md}.html"
rm -rf "$outdir"; mkdir -p "$outdir"
node -e '
  const fs = require("fs"), path = require("path");
  const [html, outdir] = process.argv.slice(1);
  const root = process.cwd(), talk = path.dirname(path.resolve(html));
  let page = fs.readFileSync(html, "utf8");
  const files = new Map();
  const publish = (ref) => {
    if (/^([a-z]+:|#|\/\/)/i.test(ref)) return ref;            // URL, anchor, data URI
    const abs = path.resolve(talk, ref);
    if (!fs.existsSync(abs) || !fs.statSync(abs).isFile()) return ref;
    const rel = abs.startsWith(talk + path.sep) ? path.relative(talk, abs) : path.relative(root, abs);
    files.set(rel, abs);
    return rel.split(path.sep).join("/");
  };
  page = page.replace(/\b(src|poster|href)="([^"]+)"/g, (m, a, ref) => `${a}="${publish(ref)}"`);
  page = page.replace(/url\(\x27([^\x27]+)\x27\)/g, (m, ref) => `url(\x27${publish(ref)}\x27)`);
  fs.writeFileSync(path.join(outdir, "index.html"), page);
  for (const [rel, abs] of files) {
    fs.mkdirSync(path.join(outdir, path.dirname(rel)), { recursive: true });
    fs.copyFileSync(abs, path.join(outdir, rel));
  }
  console.log(`staged ${outdir}/index.html + ${files.size} files:`);
  for (const rel of [...files.keys()].sort()) console.log("  " + rel);
' "$html" "$outdir"
