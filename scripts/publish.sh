#!/usr/bin/env bash
# Publish a draft: move drafts/<name>/ to talks/<name>/, list it in the README, commit and push main, where the
# Pages workflow builds it (.github/workflows/pages.yml, about a minute).
#   bash scripts/publish.sh drafts/2026-11-12-weekly-gilles "Weekly meeting with Gilles Louppe"
# The talk's paths (../../media/..., figures/...) are the same in drafts/ and talks/: nothing changes inside it.
set -euo pipefail
cd "$(dirname "$0")/.."
draft="${1%/}"; name="$2"
slug=$(basename "$draft"); date=${slug:0:10}
[ -f "$draft/talk.md" ] || { echo "no $draft/talk.md" >&2; exit 1; }
[[ "$date" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] || { echo "the folder must be drafts/YYYY-MM-DD-name" >&2; exit 1; }
[ "$(git branch --show-current)" = main ] || { echo "run it on main" >&2; exit 1; }
[ -e "talks/$slug" ] && { echo "talks/$slug exists already" >&2; exit 1; }
if grep -qE 'class="rule|class="guides|<!-- *RULE' "$draft/talk.md"; then
  echo "remove the rule boxes, guides and RULE comments first" >&2; exit 1
fi
for ref in $(grep -oE '\.\./\.\./[^"'"'"' )>]+' "$draft/talk.md" | sort -u); do
  [ -f "${ref#../../}" ] || { echo "missing shared file: ${ref#../../}" >&2; exit 1; }
done

git pull -q --ff-only origin main
mkdir -p talks
mv "$draft" "talks/$slug"
rm -f "talks/$slug"/*.html "talks/$slug"/*.pdf "talks/$slug"/*.pdf-src.md   # built files are rebuilt by Pages

page="https://vikvador.github.io/Talks/talks/$slug/talk.html"
line="- $date: [$name]($page)"
if ! grep -qF "($page)" README.md; then
  # Newest first: right under the "## Talks" heading and its blank line
  awk -v l="$line" '{ print } /^## Talks$/ && !done { getline; print; print l; done = 1 }' README.md > README.tmp
  mv README.tmp README.md
fi

git add README.md "talks/$slug"
git commit -q -m "📝 Talks - $name ($date)"
git push -q origin main
echo "published: $page (online once the Pages workflow ends, about a minute)"
