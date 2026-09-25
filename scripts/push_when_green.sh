#!/usr/bin/env bash
# push_when_green.sh — wait for the branch's stage0-ci verdict, then push through push_clean.sh (task #269).
# Three times on 2026-09-25 a push stopped at the CI gate's WAIT (rc 75), and the coordinator chained `ci_gate.py --wait`
# and push_clean.sh by hand, as one long background command. This script is that command:
#
#   scripts/push_when_green.sh [--wait SECONDS] [--lanes-live | --no-delegates-live]
#
# 1. python3 scripts/ci_gate.py --branch B --wait SECONDS. B is $PUSH_BRANCH, else the current branch (a detached HEAD
#    with no PUSH_BRANCH is a usage error); SECONDS defaults to 3000 (CI runs took 32-37 min on 2026-09-25; 1700 gave up
#    twice with the run still going). rc 0 goes on. Any other rc (1 red, 2 cannot
#    decide, 75 still unknown at the deadline, 64 usage, ...) is this script's rc, and nothing is fetched or pushed.
# 2. The banner guard. AGENTS.md or CLAUDE.md whose working copy differs from HEAD only between its one
#    `<!-- gitnexus:start -->` line and its one `<!-- gitnexus:end -->` line (the GitNexus re-index churn) is restored
#    with `git checkout -- FILE`. A difference anywhere else (a marker line, a byte outside the block, a missing or a
#    second marker, a deleted file) refuses with rc 65 and one line naming the file. Both files are judged before
#    either is restored, so a refusal restores nothing: an unsaved edit is never discarded.
# 3. The mode. A mode flag wins. With none: --lanes-live when .lanes-live declares at least one path (push_clean's
#    reading: a line that is not empty and does not start with #) AND the tracked tree has changes; else
#    --no-delegates-live (push_clean refuses --lanes-live on a clean tree).
# 4. git fetch -q origin B, then PUSH_BRANCH=B bash scripts/push_clean.sh MODE; its rc is this script's rc. push_clean
#    stays the authority: it fetches and runs the gate again, and refuses what it refuses.
# One log line per step, with its reason (`push_when_green: [N/4] ...`; refusals on stderr). This script sets none of
# CI_FIX, CI_WAIT_SKIP or CI_GATE_OFFLINE: the waiter ignores them, and a caller's own values reach push_clean as given.
# Exit codes: step 1's (ci_gate), 64 usage, 65 the banner guard, git fetch's, push_clean's.
#
# RUN IT IN THE BACKGROUND: the wait alone can take SECONDS (about 28 minutes at the default).
#   Claude Code: the Bash tool with run_in_background: true (the tool reports the exit code when the run ends).
#   A shell: setsid nohup bash scripts/push_when_green.sh > /tmp/push_when_green.log 2>&1 < /dev/null &
#   (setsid: the run outlives the shell or the monitor that started it). The log's [4/4] line carries the outcome.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
USAGE="usage: push_when_green.sh [--wait SECONDS] [--lanes-live | --no-delegates-live]"
say() { echo "push_when_green: $*"; }
die() { local rc="$1"; shift; echo "push_when_green: $*" >&2; exit "$rc"; }

WAIT=3000; MODE=""
while [ $# -gt 0 ]; do
  case "$1" in
    --wait)
      [ $# -ge 2 ] && [[ "$2" =~ ^[0-9]+$ ]] || die 64 "--wait takes a whole number of seconds; $USAGE"
      WAIT="$2"; shift 2 ;;
    --lanes-live|--no-delegates-live)
      [ -z "$MODE" ] || die 64 "give one mode flag; $USAGE"
      MODE="$1"; shift ;;
    *) die 64 "unknown argument '$1'; $USAGE" ;;
  esac
done
cd "$(git rev-parse --show-toplevel)"   # push_clean reads .lanes-live and its sibling scripts from the top of the tree
B="${PUSH_BRANCH:-$(git rev-parse --abbrev-ref HEAD)}"
[ "$B" != HEAD ] || die 64 "HEAD is detached: set PUSH_BRANCH=<branch>"

# 1. the verdict
rc=0
python3 "$HERE/ci_gate.py" --branch "$B" --wait "$WAIT" || rc=$?
case "$rc" in
  0)  say "[1/4] ci_gate.py --wait allows the push of $B (rc 0)" ;;
  1)  die 1 "[1/4] ci_gate.py rc 1: the verdict run of $B is red; nothing fetched or pushed" ;;
  2)  die 2 "[1/4] ci_gate.py rc 2: it cannot decide; nothing fetched or pushed" ;;
  75) die 75 "[1/4] ci_gate.py rc 75: the verdict of $B is still unknown after $WAIT s; nothing fetched or pushed" ;;
  *)  die "$rc" "[1/4] ci_gate.py rc $rc: no verdict; nothing fetched or pushed" ;;
esac

# 2. the banner guard. BANNER_PY exits 0 only when HEAD's copy (stdin) and the working copy (argv[1]) each hold exactly
# one start line before exactly one end line, and their texts OUTSIDE the block (every line up to and including the
# start line, every line from the end line on) are equal byte for byte: bytes, never a shell string, because a
# command substitution drops trailing newlines and an edit at the end of the file would read as no difference.
BANNER_PY='
import sys
START, END = b"<!-- gitnexus:start -->", b"<!-- gitnexus:end -->"
def outside(data):
    lines = data.split(b"\n")
    s = [i for i, line in enumerate(lines) if line == START]
    e = [i for i, line in enumerate(lines) if line == END]
    if len(s) != 1 or len(e) != 1 or s[0] > e[0]:
        return None
    return lines[:s[0] + 1] + lines[e[0]:]
try:
    with open(sys.argv[1], "rb") as fh:
        work = outside(fh.read())
except OSError:
    work = None
head = outside(sys.stdin.buffer.read())
sys.exit(0 if head is not None and head == work else 1)
'
H=$(git rev-parse --verify 'HEAD^{commit}')   # one snapshot for every read below: a commit may land mid-run (AF-AP-175)
restore=(); refuse=()
for f in AGENTS.md CLAUDE.md; do
  git diff --quiet "$H" -- "$f" && continue
  if git show "$H:$f" 2>/dev/null | python3 -c "$BANNER_PY" "$f"; then restore+=("$f"); else refuse+=("$f"); fi
done
if [ ${#refuse[@]} -gt 0 ]; then
  for f in "${refuse[@]}"; do
    echo "push_when_green: [2/4] REFUSED: $f differs from HEAD outside its gitnexus block; left untouched, nothing restored or pushed" >&2
  done
  exit 65
fi
if [ ${#restore[@]} -gt 0 ]; then
  git checkout -- "${restore[@]}"
  say "[2/4] banner guard: restored ${restore[*]} (a difference from HEAD inside the gitnexus block only)"
else
  say "[2/4] banner guard: AGENTS.md and CLAUDE.md match HEAD"
fi

# 3. the mode (after the guard: banner churn alone must not count as a tracked change)
if [ -n "$MODE" ]; then
  say "[3/4] mode $MODE (given)"
else
  declared=0
  [ ! -f .lanes-live ] || declared=$(awk '!/^#/ && !/^$/ { n++ } END { print n + 0 }' .lanes-live)
  if [ "$declared" -gt 0 ] && [ -n "$(git status --porcelain --untracked-files=no)" ]; then
    MODE=--lanes-live
    say "[3/4] mode --lanes-live (auto: .lanes-live declares $declared path(s) and the tracked tree has changes)"
  else
    MODE=--no-delegates-live
    if [ ! -f .lanes-live ]; then why="no .lanes-live"
    elif [ "$declared" -eq 0 ]; then why=".lanes-live declares no path"
    else why="the tracked tree has no changes"; fi
    say "[3/4] mode --no-delegates-live (auto: $why)"
  fi
fi

# 4. the push
rc=0
git fetch -q origin "$B" || rc=$?
[ "$rc" -eq 0 ] || die "$rc" "[4/4] git fetch -q origin $B failed (rc $rc); nothing pushed"
rc=0
PUSH_BRANCH="$B" bash "$HERE/push_clean.sh" "$MODE" || rc=$?
if [ "$rc" -eq 0 ]; then
  say "[4/4] fetched origin/$B; push_clean.sh $MODE exited rc 0"
else
  echo "push_when_green: [4/4] fetched origin/$B; push_clean.sh $MODE exited rc $rc" >&2
fi
exit "$rc"
