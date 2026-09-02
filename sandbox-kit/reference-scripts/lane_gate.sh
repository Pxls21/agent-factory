#!/usr/bin/env bash
# lane_gate.sh — the ONE exit gate for every build/repair lane and every verify lane.
#
# Why (owner mandate 2026-09-02, after RP-30b needed seven verify rounds): each
# round re-derived by hand what this script computes — "is this red pre-existing",
# "did the repair orphan an import", "does the OFF path still hash the same", "do
# the mutants die" — and each hand derivation was wrong at least once (a red was
# called pre-existing against a mid-stack SHA instead of the push base; orphaned
# imports rode through two rounds). The builder pastes this script's VERDICT block
# verbatim; the verifier re-runs the same script. Prose is not a gate result.
#
# Usage:
#   scripts/lane_gate.sh <push-base> <gate-files.txt> [--mutants MANIFEST.py]
#                        [--digest SCRIPT.py] [--out DIR] [--skip-base] [--allow-dirty]
#
#   push-base      the SHA origin/<branch> pointed at when the lane started —
#                  "pre-existing" means red THERE, nowhere else.
#   gate-files.txt one pytest target per line (the lane's literal file set).
#   --mutants      scripts/mutants/<lane>.py (MUTANTS list) — every mutant must die.
#   --digest       a script that prints `digest <hex>` for the byte-identical
#                  surface (knob-OFF path etc.); run on base and HEAD, must match.
#   --skip-base    skip the push-base run (only when it already exists in --out).
#   --allow-dirty  measure a dirty tree anyway (verify lanes probing a worktree).
#                  The VERDICT then says DIRTY and names the SHA it does NOT vouch for.
#
# A gate of record vouches for ONE SHA. Without --allow-dirty the script refuses a
# tree with tracked modifications or untracked .py files (exit 2), and it goes RED
# if HEAD moves or the tree gets dirtied while it runs (TN3-F3: a VERDICT citing
# 302c5982 was measured on a worktree carrying an uncommitted 14-mutant manifest).
# A pytest run that crashed, could not collect, or ran zero tests is RED, never a
# quiet GREEN (TN3-F2: run_pytest's rc used to be discarded, so `no tests ran`
# and a collection error both produced VERDICT GREEN).
#
# Stages (each writes to --out, each has a line in the VERDICT block):
#   0. mutation_run --check-anchors (optional) drifted anchor → RED in seconds,
#      BEFORE the two ~26-min passes (AP-67: 2/11 anchors were stale at 302c5982
#      and only stage 4 would have said so)
#   1. lint_delta --base <push-base>            NEW pyflakes hits → RED
#   2. gate set on the worktree, TWICE          run1 != run2 bitwise → RED
#   3. same set on a `git archive <push-base>`  reds at HEAD not red at base → RED
#      (pre-existing = red on both; fixed = red at base only; both are REPORTED)
#   4. mutants (optional)                       any survivor / anchor fail → RED
#   5. digest (optional)                        base digest != HEAD digest → RED
#
# Runs are long (an RP-30b gate set is ~2h per pass in the sandbox). Launch as
# ONE detached invocation and poll $OUT/DONE:
#   setsid nohup scripts/lane_gate.sh 1cd26f99 $S/gate_files.txt --out $S/lg > $S/lg.log 2>&1 &
set -u
REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT" || exit 2
PY=/root/venv-trading/bin/python
[ -x "$PY" ] || PY=python3

BASE="${1:?push-base SHA required}"; shift
FILES="${1:?gate-files.txt required}"; shift
MUTANTS=""; DIGEST=""; OUT=""; SKIP_BASE=0; ALLOW_DIRTY=0
while [ $# -gt 0 ]; do
  case "$1" in
    --mutants) MUTANTS="$2"; shift 2 ;;
    --digest) DIGEST="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    --skip-base) SKIP_BASE=1; shift ;;
    --allow-dirty) ALLOW_DIRTY=1; shift ;;
    *) echo "unknown arg $1" >&2; exit 2 ;;
  esac
done
BASE_FULL="$(git rev-parse --verify "$BASE^{commit}")" || { echo "bad push-base $BASE" >&2; exit 2; }
HEAD_FULL="$(git rev-parse HEAD)"
[ -n "$OUT" ] || OUT="${TMPDIR:-/tmp}/lane_gate_${HEAD_FULL:0:8}_$(date -u +%H%M%S)"
mkdir -p "$OUT"
rm -f "$OUT/DONE"

# ---- tree state: the VERDICT vouches for HEAD_FULL, so the tree must BE HEAD_FULL ----
# Tracked modifications + untracked .py (an untracked test file runs here and is absent
# at the SHA; an untracked manifest is exactly the TN3-F3 case). Ignored paths are exempt.
OUT_ABS="$(realpath -m "$OUT")"
dirty_list() {
  git status --porcelain --untracked-files=no
  # the gate's own --out (archives, logs) is not dirt when it sits inside the repo
  git ls-files --others --exclude-standard -- '*.py' | while IFS= read -r f; do
    case "$(realpath -m "$f")" in "$OUT_ABS"/*) ;; *) echo "?? $f" ;; esac
  done
}
dirty_list > "$OUT/dirty_start.txt"
N_DIRTY=$(wc -l < "$OUT/dirty_start.txt")
if [ "$N_DIRTY" != "0" ] && [ "$ALLOW_DIRTY" = "0" ]; then
  echo "lane_gate: tree is DIRTY ($N_DIRTY path(s)) — a gate of record must measure exactly $HEAD_FULL." >&2
  echo "Commit first, or pass --allow-dirty for a worktree probe (the VERDICT will say so)." >&2
  cat "$OUT/dirty_start.txt" >&2
  exit 2
fi
TREE_LINE="tree      clean at start"
[ "$N_DIRTY" = "0" ] || TREE_LINE="tree      DIRTY($N_DIRTY) at start — --allow-dirty; this VERDICT does NOT vouch for $HEAD_FULL (see $OUT/dirty_start.txt)"
mapfile -t TARGETS < <(grep -v '^\s*$' "$FILES" | grep -v '^#' | sort -u)
[ "${#TARGETS[@]}" -gt 0 ] || { echo "empty gate set" >&2; exit 2; }
RED=()
note() { echo "[lane_gate $(date -u +%H:%M:%S)] $*"; }

# ---- helpers -----------------------------------------------------------------
run_pytest() {  # cwd log targets...  → pytest rc
  local cwd="$1" log="$2"; shift 2
  ( cd "$cwd" && PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 "$PY" -m pytest -p no:randomly -q --tb=no -rfE "$@" ) > "$log" 2>&1
  return $?
}
summary_line() {  # strip the wall-clock so two runs can be compared bitwise
  grep -E '^[0-9]+ (passed|failed|error|skipped)|^no tests ran' "$1" | tail -1 | sed -E 's/ in [0-9.]+s.*$//'
}
red_ids() { grep -E '^(FAILED|ERROR) ' "$1" | sed -E 's/ - .*$//' | sort -u; }
pytest_usable() {  # label rc log — a run the gate may reason about, or a RED
  # rc 0/1 = ran and reported. 2 interrupted, 3 internal error, 4 usage error, 5 no tests
  # collected, anything else = crash. A run with no `passed` in its summary exercised
  # nothing the gate claims to cover (collection error, empty set), so it is RED too.
  local label="$1" rc="$2" log="$3" s
  s="$(summary_line "$log")"
  if [ "$rc" != "0" ] && [ "$rc" != "1" ]; then
    RED+=("$label: pytest rc $rc (crash/interrupt/no-tests) [${s:-<no summary>}] see $log"); return 1
  fi
  if ! grep -qE '(^| )[0-9]+ passed' <<< "$s"; then
    RED+=("$label: zero passed tests [${s:-<no summary>}] see $log"); return 1
  fi
  return 0
}
archive_tree() {  # sha dir — a runnable copy of <sha>, not just its bytes
  rm -rf "$2"; mkdir -p "$2"
  git archive "$1" | tar -x -C "$2"
  # the editable vectorbtpro install resolves to <repo>/vectorbtpro-new; the archived copy is
  # a different path, so verify_vbt_install() would red every vbt-touching test as a "shadow".
  # Point the copy at the real install (the guard resolves symlinks) — 2 phantom reds otherwise.
  if [ -d "$REPO_ROOT/vectorbtpro-new" ]; then
    rm -rf "$2/vectorbtpro-new"; ln -s "$REPO_ROOT/vectorbtpro-new" "$2/vectorbtpro-new"
  fi
}

# ---- 0. anchor pre-flight ----------------------------------------------------
ANCHOR_LINE="anchors: not requested"
if [ -n "$MUTANTS" ]; then
  note "stage 0: mutation_run --check-anchors $MUTANTS"
  "$PY" scripts/mutation_run.py --manifest "$MUTANTS" --tests "${TARGETS[*]}" --workdir "$OUT/mut" --check-anchors > "$OUT/anchors.txt" 2>&1
  ANCHOR_RC=$?
  ANCHOR_LINE="$(grep '^mutation_run' "$OUT/anchors.txt" | tail -1)"
  [ "$ANCHOR_RC" = "0" ] || RED+=("anchors: drifted manifest anchor (see $OUT/anchors.txt)")
fi

# ---- 1. lint delta -----------------------------------------------------------
note "stage 1: lint_delta --base $BASE"
"$PY" scripts/lint_delta.py --base "$BASE_FULL" > "$OUT/lint_delta.txt" 2>&1
LINT_RC=$?
[ "$LINT_RC" = "0" ] || RED+=("lint_delta: NEW pyflakes hits (see $OUT/lint_delta.txt)")

# ---- 2. worktree gate, twice -------------------------------------------------
INVOCATION="PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 $PY -m pytest -p no:randomly -q --tb=no -rfE ${TARGETS[*]}"
note "stage 2: gate set (${#TARGETS[@]} targets) on worktree, run 1"
run_pytest "$REPO_ROOT" "$OUT/head_run1.log" "${TARGETS[@]}"; RC1=$?
note "stage 2: run 2"
run_pytest "$REPO_ROOT" "$OUT/head_run2.log" "${TARGETS[@]}"; RC2=$?
pytest_usable run1 "$RC1" "$OUT/head_run1.log"
pytest_usable run2 "$RC2" "$OUT/head_run2.log"
S1="$(summary_line "$OUT/head_run1.log")"; S2="$(summary_line "$OUT/head_run2.log")"
red_ids "$OUT/head_run1.log" > "$OUT/head_reds1.txt"; red_ids "$OUT/head_run2.log" > "$OUT/head_reds2.txt"
if [ "$S1" != "$S2" ] || ! cmp -s "$OUT/head_reds1.txt" "$OUT/head_reds2.txt"; then
  RED+=("nondeterministic: run1 [$S1] != run2 [$S2] or failing ids differ")
fi

# ---- 3. push-base run → pre-existing / new / fixed ---------------------------
BASE_TREE="$OUT/base_tree"
if [ "$SKIP_BASE" = "0" ] || [ ! -f "$OUT/base_run.log" ]; then
  note "stage 3: archive $BASE and run the gate set there"
  archive_tree "$BASE_FULL" "$BASE_TREE"
  BASE_TARGETS=()
  : > "$OUT/base_absent.txt"   # appended below; a rerun into the same OUT must not accumulate
  for t in "${TARGETS[@]}"; do
    f="${t%%::*}"
    if [ -e "$BASE_TREE/$f" ]; then BASE_TARGETS+=("$t"); else echo "$t" >> "$OUT/base_absent.txt"; fi
  done
  if [ "${#BASE_TARGETS[@]}" -gt 0 ]; then
    run_pytest "$BASE_TREE" "$OUT/base_run.log" "${BASE_TARGETS[@]}"; RCB=$?
    # an unusable base run makes every HEAD red look NEW (or every fixed red look real)
    pytest_usable base "$RCB" "$OUT/base_run.log"
  else
    : > "$OUT/base_run.log"
  fi
fi
red_ids "$OUT/base_run.log" > "$OUT/base_reds.txt"
SB="$(summary_line "$OUT/base_run.log")"
comm -23 "$OUT/head_reds1.txt" "$OUT/base_reds.txt" > "$OUT/reds_new.txt"
comm -12 "$OUT/head_reds1.txt" "$OUT/base_reds.txt" > "$OUT/reds_preexisting.txt"
comm -13 "$OUT/head_reds1.txt" "$OUT/base_reds.txt" > "$OUT/reds_fixed.txt"
N_NEW=$(wc -l < "$OUT/reds_new.txt"); N_PRE=$(wc -l < "$OUT/reds_preexisting.txt"); N_FIX=$(wc -l < "$OUT/reds_fixed.txt")
[ "$N_NEW" = "0" ] || RED+=("$N_NEW NEW red(s) vs push base $BASE (see $OUT/reds_new.txt)")

# ---- 4. mutants --------------------------------------------------------------
MUT_LINE="mutants: not requested"
if [ -n "$MUTANTS" ]; then
  note "stage 4: mutation manifest $MUTANTS"
  "$PY" scripts/mutation_run.py --manifest "$MUTANTS" --tests "${TARGETS[*]}" --workdir "$OUT/mut" > "$OUT/mutants.txt" 2>&1
  MUT_RC=$?
  MUT_LINE="$(grep '^mutation_run' "$OUT/mutants.txt" | tail -1)"
  [ "$MUT_RC" = "0" ] || RED+=("mutants: survivor/anchor-fail (see $OUT/mutants.txt)")
fi

# ---- 5. digest ---------------------------------------------------------------
DIG_LINE="digest: not requested"
if [ -n "$DIGEST" ]; then
  note "stage 5: digest $DIGEST on base and HEAD"
  [ -d "$BASE_TREE" ] || archive_tree "$BASE_FULL" "$BASE_TREE"
  cp "$DIGEST" "$OUT/digest_script.py"
  DB="$(cd "$BASE_TREE" && PYTHONPATH=. "$PY" "$OUT/digest_script.py" "$OUT/digest_base.json" 2>&1 | grep '^digest ' | awk '{print $2}')"
  DH="$(PYTHONPATH=. "$PY" "$OUT/digest_script.py" "$OUT/digest_head.json" 2>&1 | grep '^digest ' | awk '{print $2}')"
  DIG_LINE="digest: base ${DB:-<none>} head ${DH:-<none>}"
  if [ -z "$DB" ] || [ -z "$DH" ] || [ "$DB" != "$DH" ]; then RED+=("digest mismatch or missing: $DIG_LINE"); fi
fi

# ---- tree state at the end: HEAD moved or tree dirtied mid-run → the runs above
# measured something other than HEAD_FULL (a live delegate committing/editing in the
# shared tree during a ~2h gate is the realistic case)
HEAD_END="$(git rev-parse HEAD)"
dirty_list > "$OUT/dirty_end.txt"
N_DIRTY_END=$(wc -l < "$OUT/dirty_end.txt")
[ "$HEAD_END" = "$HEAD_FULL" ] || RED+=("HEAD moved during the gate: started $HEAD_FULL, ended $HEAD_END")
if [ "$ALLOW_DIRTY" = "0" ] && [ "$N_DIRTY_END" != "0" ]; then
  RED+=("tree dirtied during the gate ($N_DIRTY_END path(s), see $OUT/dirty_end.txt)")
fi

# ---- VERDICT -----------------------------------------------------------------
{
  echo "===== lane_gate VERDICT ====="
  echo "head      $HEAD_FULL"
  echo "push-base $BASE_FULL"
  echo "$TREE_LINE"
  echo "tree-end  head=$HEAD_END dirty=$N_DIRTY_END"
  echo "invocation $INVOCATION"
  echo "run1      $S1"
  echo "run2      $S2"
  echo "base      ${SB:-<no base run>}"
  # gate files that do not exist at the push base run only on HEAD — say so, or the base
  # count looks like a regression next to run1
  [ -s "$OUT/base_absent.txt" ] && echo "base-absent $(wc -l < "$OUT/base_absent.txt") gate file(s) new since $BASE (see $OUT/base_absent.txt)"
  echo "$ANCHOR_LINE"
  echo "lint      $(head -1 "$OUT/lint_delta.txt")"
  echo "reds      new=$N_NEW pre-existing=$N_PRE fixed=$N_FIX"
  [ "$N_NEW" = "0" ] || sed 's/^/  NEW  /' "$OUT/reds_new.txt"
  [ "$N_PRE" = "0" ] || sed 's/^/  PRE  /' "$OUT/reds_preexisting.txt"
  [ "$N_FIX" = "0" ] || sed 's/^/  FIX  /' "$OUT/reds_fixed.txt"
  echo "$MUT_LINE"
  echo "$DIG_LINE"
  if [ "${#RED[@]}" = "0" ]; then
    echo "VERDICT   GREEN"
  else
    echo "VERDICT   RED"
    printf '  - %s\n' "${RED[@]}"
  fi
  echo "artifacts $OUT"
} | tee "$OUT/VERDICT.txt"
touch "$OUT/DONE"
[ "${#RED[@]}" = "0" ]
