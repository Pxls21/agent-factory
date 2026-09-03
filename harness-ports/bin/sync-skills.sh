#!/usr/bin/env bash
# sync-skills.sh — copy .claude/skills to .agents/skills, report drift.
#
# Runs from the repo root (or set AF_REPO). Copies every skill dir from
# .claude/skills/ to .agents/skills/, EXCEPT:
#   - the empty .claude/skills/gitnexus/ parent (the 6 gitnexus-* tool-managed
#     dirs live flat and are handled by GitNexus analyze, not by this script)
#   - PROVENANCE-UIUX.md (a provenance file, not a skill dir)
#   - hand-ported skills listed in harness-ports/hand-ported.txt (intentional
#     drift — those carry HARNESS PORT rewordings for Codex/Hermes)
#
# After copying, reports:
#   - NEW    dirs that exist in .claude/skills but not in .agents/skills
#   - STALE  dirs that exist in .agents/skills but not in .claude/skills
#   - DRIFT  dirs where file content differs between the two trees
#   - INTENTIONAL  hand-ported dirs whose .claude twin still matches the
#                  recorded base hash (expected drift, not an error)
#   - STALE-BASE   hand-ported dirs whose .claude twin changed since the
#                  port — the hand-port needs refreshing
#
# With --check, reports drift without copying (for CI / tests).
# With --record, refreshes the base hash file for hand-ported skills.
#
# Exit codes:
#   0   in sync (or copy succeeded with no prior drift)
#   1   --check found drift (DRIFT, NEW, or STALE-BASE)
#   64  usage / missing directory
#   65  comm comparison failed (fail-closed — /dev/fd absent or comm error)
set -uo pipefail

die() { echo "sync-skills: $*" >&2; exit 64; }

: "${AF_REPO:=$(git rev-parse --show-toplevel 2>/dev/null || echo .)}"
SRC="$AF_REPO/.claude/skills"
DST="$AF_REPO/.agents/skills"
HP_LIST="$AF_REPO/harness-ports/hand-ported.txt"
HP_HASH="$AF_REPO/harness-ports/hand-ported.sha256"
[ -d "$SRC" ] || die ".claude/skills not found at $SRC"
[ -d "$DST" ] || mkdir -p "$DST"

CHECK=false
RECORD=false
case "${1:-}" in
  --check)  CHECK=true ;;
  --record) RECORD=true ;;
esac

# Load hand-ported allowlist (one name per line; empty if file absent).
declare -A HP_NAMES
if [ -f "$HP_LIST" ]; then
  while IFS= read -r name || [ -n "$name" ]; do
    [ -z "$name" ] && continue
    HP_NAMES["$name"]=1
  done < "$HP_LIST"
fi

# Load recorded base hashes (sha256 of .claude twin at port time).
declare -A HP_HASHES
if [ -f "$HP_HASH" ]; then
  while read -r hash name rest; do
    [ -z "$hash" ] && continue
    HP_HASHES["$name"]="$hash"
  done < "$HP_HASH"
fi

# --record: refresh the hash file and exit.
if $RECORD; then
  if [ ${#HP_NAMES[@]} -eq 0 ]; then
    die "--record: no hand-ported.txt found at $HP_LIST"
  fi
  > "$HP_HASH"
  for name in $(printf '%s\n' "${!HP_NAMES[@]}" | sort); do
    if [ -f "$SRC/$name/SKILL.md" ]; then
      sha=$(sha256sum "$SRC/$name/SKILL.md" | cut -d' ' -f1)
      printf '%s  %s\n' "$sha" "$name" >> "$HP_HASH"
    fi
  done
  echo "sync-skills: recorded base hashes for ${#HP_NAMES[@]} hand-ported skills in $HP_HASH"
  exit 0
fi

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

SRC_LIST="$(src_dirs | sort)" || { echo "sync-skills: src skill-list generation failed" >&2; exit 65; }
DST_LIST="$(dst_dirs | sort)" || { echo "sync-skills: dst skill-list generation failed" >&2; exit 65; }

_SYNC_TMP_SRC="$(mktemp)" || die "cannot create temp file"
_SYNC_TMP_DST="$(mktemp)" || die "cannot create temp file"
trap 'rm -f "$_SYNC_TMP_SRC" "$_SYNC_TMP_DST"' EXIT
echo "$SRC_LIST" > "$_SYNC_TMP_SRC"
echo "$DST_LIST" > "$_SYNC_TMP_DST"

new="$(comm -23 "$_SYNC_TMP_SRC" "$_SYNC_TMP_DST")"; _rc=$?
[ $_rc -ne 0 ] && { echo "sync-skills: new-list comparison failed (comm rc=$_rc)" >&2; exit 65; }
stale="$(comm -13 "$_SYNC_TMP_SRC" "$_SYNC_TMP_DST")"; _rc=$?
[ $_rc -ne 0 ] && { echo "sync-skills: stale-list comparison failed (comm rc=$_rc)" >&2; exit 65; }

drift=""
intentional=""
stale_base=""
_common="$(comm -12 "$_SYNC_TMP_SRC" "$_SYNC_TMP_DST")"; _rc=$?
[ $_rc -ne 0 ] && { echo "sync-skills: common-list comparison failed (comm rc=$_rc)" >&2; exit 65; }
for name in $_common; do
  if ! diff -rq "$SRC/$name" "$DST/$name" >/dev/null 2>&1; then
    if [ -n "${HP_NAMES[$name]+x}" ]; then
      # Hand-ported skill — check whether .claude twin still matches recorded hash
      cur_hash=$(sha256sum "$SRC/$name/SKILL.md" | cut -d' ' -f1)
      rec_hash="${HP_HASHES[$name]:-}"
      if [ "$cur_hash" = "$rec_hash" ]; then
        intentional="$intentional $name"
      else
        stale_base="$stale_base $name"
      fi
    else
      drift="$drift $name"
    fi
  fi
done
drift="${drift# }"
intentional="${intentional# }"
stale_base="${stale_base# }"

# Report
[ -n "$new" ]   && { echo "NEW (in .claude/skills, not yet in .agents/skills):"; echo "$new" | sed 's/^/  /'; }
[ -n "$stale" ] && { echo "STALE (in .agents/skills, no source in .claude/skills):"; echo "$stale" | sed 's/^/  /'; }
[ -n "$drift" ] && { echo "DRIFT (content differs):"; echo "$drift" | tr ' ' '\n' | sed 's/^/  /'; }
for name in $intentional; do
  echo "INTENTIONAL: $name"
done
for name in $stale_base; do
  echo "STALE-BASE: $name (.claude twin changed since the port — re-port and --record)"
done

if [ -z "$new" ] && [ -z "$drift" ] && [ -z "$stale_base" ]; then
  echo "sync-skills: .agents/skills is in sync with .claude/skills ($(echo "$SRC_LIST" | wc -l) skills)"
  # Stale dirs are informational — they do not indicate the copy is out of date
  # Intentional dirs are expected drift from hand-ported skills
  exit 0
fi

if $CHECK; then
  echo "sync-skills: --check found differences. Run without --check to copy."
  exit 1
fi

# Copy: new + drifted dirs (NON-allowlisted only); stale dirs are reported but
# NOT deleted (they may be tool-managed or have local edits the owner wants to
# keep). Hand-ported (allowlisted) dirs are NEVER overwritten by a plain run.
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
[ -n "$stale_base" ] && echo "sync-skills: STALE-BASE hand-ported skills need re-porting — run the 3-way merge, then --record."
exit 0
