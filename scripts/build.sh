#!/usr/bin/env bash
# Build a deck to HTML (default) or PDF.
#   bash scripts/build.sh talks/2026-11-12-weekly-gilles/talk.md        -> talk.html next to it
#   bash scripts/build.sh talks/2026-11-12-weekly-gilles/talk.md --pdf  -> talk.pdf
# Media paths in a talk are relative to the repo root (media/, team/), so talks
# reference them as ../../media/... ; the template and palettes decks sit at the root.
set -euo pipefail
cd "$(dirname "$0")/.."
md="${1:-template.md}"; fmt="${2:-}"
out="${md%.md}.html"; [ "$fmt" = "--pdf" ] && out="${md%.md}.pdf"
themes=theme
# PDF of a deck in a sub-folder: the relative font path would not resolve, so render with a
# temporary copy of the themes whose font URLs are absolute (the HTML is fixed after the build instead).
if [ "${out##*.}" = "pdf" ] && [ "$(dirname "$md")" != "." ]; then
  themes=$(mktemp -d)
  cp theme/*.css "$themes/"
  sed -i.bak "s#url('theme/fonts/#url('file://$PWD/theme/fonts/#g" "$themes"/*.css && rm -f "$themes"/*.bak
fi
# PDF: every recap video becomes its stills, one slide each, under one page number (scripts/video-stills.js).
src="$md"
if [ "${out##*.}" = "pdf" ]; then
  src="${md%.md}.pdf-src.md"; trap 'rm -f "$src"; [ "$themes" != theme ] && rm -rf "$themes"' EXIT
  node scripts/video-stills.js "$md" "$src"
fi
npx marp --no-stdin --html --allow-local-files -o "$out" --theme-set "$themes" -- "$src"
# The theme refers to its fonts as theme/fonts/... (relative to the repo root).
# For a deck in a sub-folder (talks/...), rewrite that path relative to the HTML file.
if [ "${out##*.}" = "html" ]; then
  up=$(dirname "$md" | awk -F/ '{ if ($0 == ".") print ""; else { s=""; for (i=1;i<=NF;i++) s=s "../"; print s } }')
  [ -n "$up" ] && sed -i.bak "s#url('theme/fonts/#url('${up}theme/fonts/#g" "$out" && rm -f "$out.bak"
  # Recap videos: inline theme/video-controls.js (autoplay on slide entry, play/pause button, seek bar).
  node -e '
    const fs = require("fs"), [out, js] = process.argv.slice(1);
    let html = fs.readFileSync(out, "utf8");
    const tag = "<script>\n" + fs.readFileSync(js, "utf8") + "\n</script>";
    const i = html.lastIndexOf("</body>");
    html = i >= 0 ? html.slice(0, i) + tag + html.slice(i) : html + tag;
    fs.writeFileSync(out, html);
  ' "$out" theme/video-controls.js
fi
echo "built $out"
