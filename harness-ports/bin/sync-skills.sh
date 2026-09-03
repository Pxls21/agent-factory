#!/usr/bin/env bash
# sync-skills.sh — copy .claude/skills to .agents/skills, report drift.
#
# Runs from the repo root (or set AF_REPO). Copies every skill dir from
# .claude/skills/ to .agents/skills/, EXCEPT:
#   - the empty .claude/skills/gitnexus/ parent (the 6 gitnexus-* tool-managed
#     dirs live flat and are handled by GitNexus analyze, not by this script)
#   - PROVENANCE-UIUX.md (a provenance file, not a skill dir)
#
# After copying, reports:
#   - NEW    dirs that exist in .claude/skills but not in .agents/skills
#   - STALE  dirs that exist in .agents/skills but not in .claude/skills
#   - DRIFT  dirs where file content differs between the two trees
#
# With --check, reports drift without copying (for CI / tests).
#
# Exit codes:
#   0   in sync (or copy succeeded with no prior drift)
#   1   --check found drift
#   64  usage / missing directory
set -uo pipefail

die() { echo "sync-skills: $*" >&2; exit 64; }

: "${AF_REPO:=$(git rev-parse --show-toplevel 2>/dev/null || echo .)}"
SRC="$AF_REPO/.claude/skills"
DST="$AF_REPO/.agents/skills"
[ -d "$SRC" ] || die ".claude/skills not found at $SRC"
[ -d "$DST" ] || mkdir -p "$DST"

CHECK=false
[ "${1:-}" = "--check" ] && CHECK=true

# Skill dirs = immediate children of $SRC that contain at least one file.
# Excludes: the bare "gitnexus" parent dir (empty after the flattening) and
# any plain files at the top level (PROVENANCE-UIUX.md).
src_dirs() {
  for d in "$SRC"/*/; do
    [ -d "$d" ] || continue
    name="$(basename "$d")"
    [ "$name" = "gitnexus" ] && continue   # empty parent, not a skill
    echo "$name"
  done
}

dst_dirs() {
  for d in "$DST"/*/; do
    [ -d "$d" ] || continue
    name="$(basename "$d")"
    [ "$name" = "PROVENANCE-UIUX.md" ] && continue  # not a dir; safety
    echo "$name"
  done
}

SRC_LIST="$(src_dirs | sort)"
DST_LIST="$(dst_dirs | sort)"

new="$(comm -23 <(echo "$SRC_LIST") <(echo "$DST_LIST"))"
stale="$(comm -13 <(echo "$SRC_LIST") <(echo "$DST_LIST"))"

drift=""
for name in $(comm -12 <(echo "$SRC_LIST") <(echo "$DST_LIST")); do
  if ! diff -rq "$SRC/$name" "$DST/$name" >/dev/null 2>&1; then
    drift="$drift $name"
  fi
done
drift="${drift# }"

# Report
rc=0
[ -n "$new" ]   && { echo "NEW (in .claude/skills, not yet in .agents/skills):"; echo "$new" | sed 's/^/  /'; }
[ -n "$stale" ] && { echo "STALE (in .agents/skills, no source in .claude/skills):"; echo "$stale" | sed 's/^/  /'; }
[ -n "$drift" ] && { echo "DRIFT (content differs):"; echo "$drift" | tr ' ' '\n' | sed 's/^/  /'; }

if [ -z "$new" ] && [ -z "$drift" ]; then
  echo "sync-skills: .agents/skills is in sync with .claude/skills ($(echo "$SRC_LIST" | wc -l) skills)"
  # Stale dirs are informational — they do not indicate the copy is out of date
  exit 0
fi

if $CHECK; then
  echo "sync-skills: --check found differences. Run without --check to copy."
  exit 1
fi

# Copy: new + drifted dirs; stale dirs are reported but NOT deleted
# (they may be tool-managed or have local edits the owner wants to keep).
# Uses cp -a (rsync may not be installed on all targets).
count_new=0; count_drift=0
for name in $new; do
  [ -z "$name" ] && continue
  rm -rf "$DST/$name"
  cp -a "$SRC/$name" "$DST/$name"
  count_new=$((count_new+1))
done
for name in $drift; do
  [ -z "$name" ] && continue
  rm -rf "$DST/$name"
  cp -a "$SRC/$name" "$DST/$name"
  count_drift=$((count_drift+1))
done
echo "sync-skills: copied $count_new new + $count_drift drifted. $(echo "$SRC_LIST" | wc -l) skills total."
[ -n "$stale" ] && echo "sync-skills: stale dirs left in place — remove manually if unwanted."
exit 0
