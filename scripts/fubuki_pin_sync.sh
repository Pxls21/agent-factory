#!/usr/bin/env bash
# fubuki_pin_sync.sh — the pinned fubuki-os checkout as a DECLARED test input on every venue (GOV1's landing,
# 2026-09-15: twelve governance tests were green on the PC only through the lane shell's PYTHONPATH; the sandbox
# static-copy gate, bare, read `12 failed, 17 passed` — AF-AP-81, the hidden test input).
#
#   scripts/fubuki_pin_sync.sh [DEST] [SOURCE]
#     DEST    the directory holding the two checkouts (default ${FUBUKI_PIN_DIR:-$HOME/fubuki-pin}):
#               DEST/fubuki-os        the lock's commit, clean, on a local branch `pinned`      -> FUBUKI_OS_ROOT
#               DEST/fubuki-os-other  ONE empty commit on top of the pin (the identical tree) -> FUBUKI_OTHER_ROOT,
#                                     the negative control verify_pinned_fubuki refuses by name (commit mismatch)
#     SOURCE  the repository to clone from (default: the lock's repository URL; a local checkout for offline use)
#
# Idempotent: an existing checkout is VERIFIED (HEAD = the lock's commit, clean, the other's parent = the pin, the
# other's tree = the pin's tree), never reset — a drifted or dirty pinned checkout is a FINDING, rc 3 with the reason
# (remove the directory by hand to re-provision). Prints the two roots as KEY=VALUE lines on success (rc 0); CI
# appends them to $GITHUB_ENV, scripts/test_summary.sh and scripts/pc_suite.sh export each venue's defaults.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOCK="$ROOT/upstream.lock.yaml"
DEST="${1:-${FUBUKI_PIN_DIR:-$HOME/fubuki-pin}}"
# The lock is read with awk (no PyYAML on a venue's bare python3): the `fubuki-os:` block's `commit:` / `repository:`.
read_lock() { awk -v key="$1" '
  /^[[:space:]]*fubuki-os:[[:space:]]*$/ { inblock = 1; next }
  inblock && /^[[:space:]]*[A-Za-z0-9_-]+:[[:space:]]*$/ { inblock = 0 }
  inblock && $1 == key ":" { sub(/^[[:space:]]*[A-Za-z_-]+:[[:space:]]*/, ""); gsub(/["'"'"']/, ""); print; exit }
' "$LOCK"; }
die() { echo "fubuki_pin_sync: $2" >&2; exit "$1"; }
COMMIT="$(read_lock commit)"
SOURCE="${2:-$(read_lock repository)}"
case "$COMMIT" in
  *[!0-9a-f]*|"") die 2 "the lock's fubuki-os commit is not lowercase hex: '$COMMIT'" ;;
esac
[ "${#COMMIT}" -eq 40 ] || die 2 "the lock's fubuki-os commit is not 40 characters: '$COMMIT'"
PIN="$DEST/fubuki-os"; OTHER="$DEST/fubuki-os-other"
head_of() { git -C "$1" rev-parse HEAD; }
tree_of() { git -C "$1" rev-parse 'HEAD^{tree}'; }
clean() { [ -z "$(git -C "$1" status --porcelain)" ]; }
# Clone quietly, dropping git's benign "source repository is shallow" note from stderr, but keeping every other
# line and the exit code. A tempfile in the already-created $DEST does this on EVERY venue; the process
# substitution it replaces needs /dev/fd, which the header promises but not every venue mounts (review
# 2026-09-15: four tests failed where /dev/fd was absent — the claim was broader than the impl).
git_clone_quiet() { # $1=source $2=dest
  local err="$DEST/.fubuki-clone-stderr.$$" rc
  git clone -q "$1" "$2" 2> "$err" && rc=0 || rc=$?
  grep -v 'shallow' "$err" >&2 || true
  rm -f "$err"
  return "$rc"
}

mkdir -p "$DEST"
if [ ! -d "$PIN/.git" ]; then
  git_clone_quiet "$SOURCE" "$PIN"
  git -C "$PIN" checkout -q -B pinned "$COMMIT" 2>/dev/null || { rm -rf "$PIN"; die 3 "commit-absent: $COMMIT is not in $SOURCE"; }
fi
[ "$(head_of "$PIN")" = "$COMMIT" ] || die 3 "commit-mismatch: $PIN is at $(head_of "$PIN"), the lock pins $COMMIT (a drifted checkout is a finding; remove it by hand to re-provision)"
clean "$PIN" || die 3 "dirty: $PIN has local changes (a dirty pinned checkout is a finding; never reset here)"
[ -d "$PIN/src/fubuki_os" ] || die 3 "source-missing: $PIN/src/fubuki_os"

if [ ! -d "$OTHER/.git" ]; then
  git_clone_quiet "$PIN" "$OTHER"
  git -C "$OTHER" checkout -q -B pinned "$COMMIT"
  git -C "$OTHER" -c user.name=fubuki-pin-sync -c user.email=fubuki-pin-sync@agent-factory.invalid \
    commit -q --allow-empty -m "negative control: one empty commit on top of the pinned $COMMIT (identical tree)"
fi
[ "$(head_of "$OTHER")" != "$COMMIT" ] || die 3 "other-is-the-pin: $OTHER sits at the pinned commit itself"
[ "$(git -C "$OTHER" rev-parse 'HEAD^')" = "$COMMIT" ] || die 3 "other-parent: $OTHER must sit exactly one commit above the pin"
[ "$(tree_of "$OTHER")" = "$(tree_of "$PIN")" ] || die 3 "other-tree-differs: $OTHER must carry the pinned tree"
clean "$OTHER" || die 3 "dirty: $OTHER has local changes"
echo "FUBUKI_OS_ROOT=$PIN"
echo "FUBUKI_OTHER_ROOT=$OTHER"
