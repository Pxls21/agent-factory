#!/usr/bin/env bash
# sync-lane-skills.sh — materialize .agents/lane-skills/ (the curated subset lanes load) from
# harness-ports/lane-skills.txt + .agents/skills/. Copies (not symlinks: Hermes walks real dirs and
# git keeps it portable). --check: exit 1 on drift, list it, copy nothing.
#   0 in sync / synced · 1 drift found (--check) · 64 usage or missing source skill
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
LIST="$ROOT/harness-ports/lane-skills.txt"; SRC="$ROOT/.agents/skills"; DST="$ROOT/.agents/lane-skills"
CHECK=0; [ "${1:-}" = "--check" ] && CHECK=1
names="$(grep -vE '^\s*(#|$)' "$LIST")"
[ -n "$names" ] || { echo "sync-lane-skills: empty list" >&2; exit 64; }
drift=0
for n in $names; do
  [ -d "$SRC/$n" ] || { echo "sync-lane-skills: MISSING source skill: $n" >&2; exit 64; }
  if ! diff -rq "$SRC/$n" "$DST/$n" >/dev/null 2>&1; then
    drift=$((drift+1)); echo "DRIFT: $n"
    if [ "$CHECK" = 0 ]; then rm -rf "$DST/$n"; mkdir -p "$DST"; cp -a "$SRC/$n" "$DST/$n"; fi
  fi
done
# stale: in DST but not in the list
for d in "$DST"/*/; do
  [ -d "$d" ] || continue; b="$(basename "$d")"
  if ! grep -qxF "$b" <<<"$names"; then drift=$((drift+1)); echo "STALE: $b"; [ "$CHECK" = 0 ] && rm -rf "$d"; fi
done
total="$(echo "$names" | wc -l)"
if [ "$CHECK" = 1 ]; then
  [ "$drift" = 0 ] && { echo "sync-lane-skills: in sync ($total skills)"; exit 0; } || { echo "sync-lane-skills: $drift drift item(s) — run without --check"; exit 1; }
fi
echo "sync-lane-skills: synced $total skills into .agents/lane-skills ($drift changed)"
