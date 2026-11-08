#!/usr/bin/env bash
# Publish a talk on main, where GitHub Pages builds it (.github/workflows/pages.yml on main).
#   bash scripts/publish.sh talks/2026-11-12-weekly-gilles "Weekly meeting with Gilles Louppe"
# Copies to main, at the same paths: the talk's talk.md and figures/, and every shared file it uses
# (../../media/..., ../../projects/..., ../../logos/...). Adds "- <date>: [<name>](<page>)" at the top of the
# README list (once), commits and pushes main. Run it from the template branch, with the talk approved.
set -euo pipefail
cd "$(dirname "$0")/.."
talk="${1%/}"; name="$2"
slug=$(basename "$talk"); date=${slug:0:10}
[ -f "$talk/talk.md" ] || { echo "no $talk/talk.md" >&2; exit 1; }
[[ "$date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] || { echo "the folder must be talks/YYYY-MM-DD-name" >&2; exit 1; }
if grep -qE 'class="rule|class="guides|<!-- *RULE' "$talk/talk.md"; then
  echo "remove the rule boxes, guides and RULE comments first" >&2; exit 1
fi

git fetch -q origin main
main=$(mktemp -d); trap 'git worktree remove --force "$main"; rm -rf "$main"' EXIT
git worktree add -q --detach "$main" origin/main

mkdir -p "$main/$talk"
cp "$talk/talk.md" "$main/$talk/"
if [ -d "$talk/figures" ]; then rsync -a --delete "$talk/figures/" "$main/$talk/figures/"; fi
# Shared files, referenced from the talk as ../../<path>: copied at <path> on main
grep -oE '\.\./\.\./[^"'"'"' )>]+' "$talk/talk.md" | sort -u | while read -r ref; do
  rel=${ref#../../}
  [ -f "$rel" ] || { echo "missing shared file: $rel" >&2; exit 1; }
  mkdir -p "$main/$(dirname "$rel")"; cp "$rel" "$main/$rel"
  poster="${rel%.mp4}.jpg"                                   # a recap video brings its poster
  if [ "$rel" != "$poster" ] && [ -f "$poster" ]; then cp "$poster" "$main/$poster"; fi
done

page="https://vikvador.github.io/Talks/$talk/talk.html"
line="- $date: [$name]($page)"
if ! grep -qF "($page)" "$main/README.md"; then
  # Newest first: right after the banner line
  awk -v l="$line" 'NR==1 { print; getline; print ""; print l; if ($0 != "") print; next } { print }' \
    "$main/README.md" > "$main/README.tmp" && mv "$main/README.tmp" "$main/README.md"
fi

git -C "$main" add -A
git -C "$main" commit -q -m "📝 Talks - $name ($date)"
git -C "$main" push -q origin HEAD:main
echo "published: $page (online once the Pages workflow ends, about a minute)"
