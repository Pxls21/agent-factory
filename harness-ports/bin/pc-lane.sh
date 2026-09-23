#!/usr/bin/env bash
# pc-lane.sh — run ONE build/verify lane on the PC, non-interactively.
#
#   pc-lane.sh <brief-file> [codex|hermes] [role]
#
# This is the thing the whole harness port exists for: give it a brief and it
# runs the same kind of lane the sandbox runs, on the PC, in its own git
# worktree, under a lane role, and leaves the final message in report.md.
#
# Runs SYNCHRONOUSLY and exits with the harness's exit code. To run it detached
# (which is what the bridge caller does, because a bridge call dies at ~120s),
# see scripts/pc_lane.sh — it wraps this in setsid + a pidfile and polls.
#
# ---------------------------------------------------------------------------
# Environment (all overridable; defaults are non-root and PC-shaped)
#   AF_REPO   repo clone            default: $HOME/agent-factory
#   AF_VENV   python venv root      default: $HOME/venv-agent-factory
#   CODEX_BIN      codex binary          default: codex (from PATH)
#   HERMES_BIN     hermes binary         default: hermes (from PATH)
#   HERMES_PROFILE lane profile          default: agentfactory (dedicated; never the owner default)
#   HERMES_MODEL   OmniRoute route id    default: by ROLE (see role_model below). Since 2026-09-14 (owner):
#                  BUILD = agentfactory-build-local and VERIFY = agentfactory-verify-local — the local
#                  Qwen3.8-27B on the PC's 3090 first, the cloud chain as fallback; they alternate on
#                  the one 262k slot. Cloud routes stay one env away (agentfactory-build / -verify).
#   HERMES_REASONING  Hermes effort      default: by ROLE (medium for build, xhigh for verify, high otherwise);
#                  on a local route ultra/max/high are CLAMPED to xhigh (the Qwen3.8 template's ceiling)
#   LANE_BRANCH    branch to fetch       default: claude/soundbox-kit-migration-iz1jwf
#   LANE_ID        override the lane id  default: derived from the brief
#   PC_LANE_FAKE_HARNESS
#                  test-double harness; see harness-ports/tests/test_pc_lane.sh.
#                  Set ONLY by the plumbing test. Refuses to run if the brief is
#                  not itself under a test directory, so it cannot be used to
#                  fake a real lane.
# ---------------------------------------------------------------------------
#
# HARD LIMITS, enforced not just documented:
#   - the lane NEVER pushes. A `git` shim earlier on PATH refuses push, remote
#     add/set-url, and the gh subcommands that publish. The sandbox side reviews
#     and pushes; a lane that could push could bypass that review.
#   - the lane NEVER opens PRs or posts comments (same shim).
#   - the lane NEVER issues a gate verdict — that rule lives in the role bodies
#     (harness-ports/roles/*.md) and in the project instructions, because it is a
#     judgement, not a command that can be blocked.
#
# REPLAY SAFETY (docs/PC-BRIDGE-RUNBOOK.md, "Bridge-launched background processes
# MUST self-guard"): a bridge call that times out may be REPLAYED, and a bare
# relaunch would spawn a second lane on the same worktree. The guard here is on
# the STATE THIS INTENDS TO CREATE, not mutual exclusion (rule 1b — a kill+
# relaunch defeats flock): if report.md already exists the lane is done and this
# re-prints it; if the pidfile names a live process the lane is running and this
# exits without starting a second one.
set -uo pipefail

die() { echo "pc-lane: $*" >&2; exit 64; }

# bash reads a script LAZILY: an edit to this file while a lane loop runs (a `git merge` of the main clone on the PC)
# corrupts the running loop at a byte offset — the sandbox-side twin (scripts/pc_lane.sh) learned it on 2026-09-08 and
# this side had eight loops alive when the fix was needed. Run from a private copy; the copy is removed by cleanup().
if [ -z "${PC_LANE_SELF_COPY:-}" ]; then
  _self="$(mktemp "${TMPDIR:-/tmp}/pc-lane.XXXXXX")" && cp "$0" "$_self" \
    && PC_LANE_SELF_COPY="$_self" exec bash "$_self" "$@"
fi
BRIEF="${1:-}"; HARNESS="${2:-codex}"; ROLE="${3:-}"
[ -n "$BRIEF" ] || die "usage: pc-lane.sh <brief-file> [codex|hermes] [role]"
[ -f "$BRIEF" ] || die "brief not found: $BRIEF"
case "$HARNESS" in codex|hermes) ;; *) die "harness must be codex or hermes, got '$HARNESS'";; esac

: "${AF_REPO:=$HOME/agent-factory}"
: "${AF_VENV:=$HOME/venv-agent-factory}"
: "${CODEX_BIN:=codex}"
: "${HERMES_BIN:=hermes}"
: "${LANE_BRANCH:=claude/soundbox-kit-migration-iz1jwf}"
[ -d "$AF_REPO/.git" ] || [ -f "$AF_REPO/.git" ] || die "not a git clone: $AF_REPO"

BRIEF="$(cd "$(dirname "$BRIEF")" && pwd)/$(basename "$BRIEF")"

# --- the pinned SHA ---------------------------------------------------------
# A lane must never run on "whatever HEAD happens to be" — the runbook records a
# live incident where a relaunch landed on the wrong tree. The brief pins it.
PIN="$(grep -oiE '^[[:space:]]*(PIN|SHA|BASE)[[:space:]:]+[0-9a-f]{7,40}' "$BRIEF" \
        | head -1 | grep -oiE '[0-9a-f]{7,40}$' || true)"
[ -n "$PIN" ] || die "brief pins no SHA. Add a line like 'PIN: <sha>' — refusing to
  guess a base commit (a lane on the wrong tree produces confident wrong work)."

LANE_ID="${LANE_ID:-$(basename "$BRIEF" | tr -c 'A-Za-z0-9_.-' '-' | cut -c1-40)-${PIN:0:8}}"
LANE_DIR="$AF_REPO/.lanes/$LANE_ID"
TREE="$LANE_DIR/tree"
REPORT="$LANE_DIR/report.md"
PIDFILE="$LANE_DIR/lane.pid"
LOG="$LANE_DIR/lane.log"
mkdir -p "$LANE_DIR" || die "cannot create $LANE_DIR"

# Lane worktrees must never enter the index. `.lanes/` is in the repo's
# .gitignore, but a lane may run in a clone that predates that entry, and a
# `git add -A` would then stage an embedded git repository ("adding embedded git
# repository: .lanes/…/tree" — seen live in the plumbing test). This
# self-contained ignore makes the guard travel with the lane rather than
# depending on the checkout.
[ -f "$AF_REPO/.lanes/.gitignore" ] || printf '*\n' > "$AF_REPO/.lanes/.gitignore"

# --- state guard (replay safety) --------------------------------------------
if [ -s "$REPORT" ]; then
  echo "pc-lane: lane '$LANE_ID' already produced a report — not re-running." >&2
  cat "$REPORT"; exit 0
fi
if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE" 2>/dev/null)" 2>/dev/null; then
  echo "pc-lane: lane '$LANE_ID' is already running (pid $(cat "$PIDFILE")) — not starting a second." >&2
  exit 0
fi
echo $$ > "$PIDFILE"
cleanup() { rm -f "$PIDFILE" "${PC_LANE_SELF_COPY:-}"; }
trap cleanup EXIT
# A coordinator's TERM must take the lane's WHOLE session with it — the harness, its terminal-tool shells, their probes and
# load loops — not one level of children. 2026-09-08 14:27Z: five lanes were stopped by pid (loop, then the Hermes child)
# for the WAL migration; VERIFY-B5j's six `while :; do :; done` race-margin workers were grandchildren, lost their parent's
# EXIT trap with it, and burned six cores for 90 minutes (AF-AP-68). scripts/pc_lane.sh starts this script under setsid, so
# the lane IS a session: everything in it is ours, nothing outside it is. Not the session leader (a test, a manual run) →
# never touch the session: it belongs to whoever started us.
stop_session() {
  local sid pids; sid="$(ps -o sid= -p $$ 2>/dev/null | tr -d ' ')"
  [ -n "$sid" ] && [ "$sid" = "$$" ] || return 0
  pids="$(ps -o pid= --sid "$sid" 2>/dev/null | tr -d ' ' | grep -vx "$$" | tr '\n' ' ')"
  [ -n "${pids// /}" ] || return 0
  kill -TERM $pids 2>/dev/null; sleep 1; kill -KILL $pids 2>/dev/null
  echo "pc-lane: stopped — $(echo $pids | wc -w) process(es) of the lane session terminated with it" >&2
}
trap 'stop_session; cleanup; trap - EXIT; exit 143' TERM INT

# --- a dead loop's FAILED is not this loop's verdict (AF-AP-140, task #167) ------------------------------------------------
# A relaunch reuses this directory, and FAILED is written by a loop right before it exits 70. On 2026-09-23 07:14Z the poller
# read VERIFY-T92's dead first loop's FAILED as the relaunched loop's verdict and printed LANE FAILED while the new loop ran.
# So the marker is renamed HERE, at loop start and before any slow step: kept as evidence (never deleted), named for the time
# the dead loop wrote it. A left-over marker would also hide a relaunched loop that succeeds (the poller tests FAILED before
# READY). The poller binds FAILED to its own dispatch too (scripts/pc_lane.sh), which covers the window before this line runs.
if [ -e "$LANE_DIR/FAILED" ]; then
  STALE_FAILED="$LANE_DIR/FAILED.stale-$(date -u -r "$LANE_DIR/FAILED" +%Y%m%dT%H%M%SZ 2>/dev/null || date -u +%Y%m%dT%H%M%SZ)"
  [ -e "$STALE_FAILED" ] && STALE_FAILED="$STALE_FAILED.$$"   # never overwrite an older stale marker
  mv "$LANE_DIR/FAILED" "$STALE_FAILED" \
    || die "cannot set aside the previous loop's FAILED marker ($LANE_DIR/FAILED) — refusing to run under a verdict that is not this loop's"
  echo "pc-lane: the previous loop's FAILED is not this loop's verdict — kept as $(basename "$STALE_FAILED") (AF-AP-140)" >&2
fi

# --- the no-push shim -------------------------------------------------------
# Earlier on PATH than the real binaries. This is the enforcement point for
# "a lane never pushes"; the prose in the role file is the explanation.
SHIM="$LANE_DIR/shim"
mkdir -p "$SHIM"
REAL_GIT="$(command -v git)" || die "git not found"
cat > "$SHIM/git" <<SHIMEOF
#!/usr/bin/env bash
# Lane guard: this lane may read and commit locally, but may not publish.
for a in "\$@"; do
  case "\$a" in
    push) echo "pc-lane: 'git push' is refused inside a lane. The sandbox side reviews and pushes." >&2; exit 13;;
  esac
done
case "\${1:-}" in
  remote) case "\${2:-}" in add|set-url) echo "pc-lane: 'git remote \$2' is refused inside a lane." >&2; exit 13;; esac;;
esac
exec "$REAL_GIT" "\$@"
SHIMEOF
cat > "$SHIM/gh" <<'SHIMEOF'
#!/usr/bin/env bash
case "${1:-}" in
  pr|release|issue|api|repo)
    echo "pc-lane: 'gh $1' is refused inside a lane — no outward-facing actions." >&2; exit 13;;
esac
exec "$(command -v -- gh 2>/dev/null | grep -v "$0" | head -1)" "$@"
SHIMEOF
chmod +x "$SHIM/git" "$SHIM/gh"
export PATH="$SHIM:$PATH"

# --- the lane's worktree ----------------------------------------------------
# Disjoint per lane, exactly like the sandbox's agent worktrees, so parallel
# lanes cannot collide on the tree.
if [ ! -d "$TREE/.git" ] && [ ! -f "$TREE/.git" ]; then
  "$REAL_GIT" -C "$AF_REPO" fetch origin "$LANE_BRANCH" --quiet \
    || echo "pc-lane: fetch failed — continuing with local objects" >&2
  "$REAL_GIT" -C "$AF_REPO" worktree add --detach "$TREE" "$PIN" --quiet \
    || die "worktree add failed at $PIN (is the SHA fetched?)"
fi
HAVE="$("$REAL_GIT" -C "$TREE" rev-parse HEAD 2>/dev/null || echo none)"
case "$HAVE" in
  "$PIN"*) ;;
  *) die "lane tree is at $HAVE but the brief pins $PIN — refusing to run on the wrong tree.";;
esac

# --- an optional lane patch on top of the PIN --------------------------------
# .lanes/<id>/lane.patch (shipped by scripts/pc_lane.sh from LANE_PATCH): a sandbox lane's uncommitted files,
# so the PC continues work that never reached a commit (2026-09-08). Applied ONCE — a clean tree means not yet
# applied; a replayed launch on a dirty tree leaves it alone. A patch that does not apply is a FAILED lane
# (the reason in FAILED, rc 70, no report.md to grade), never a lane on the wrong bytes.
LANE_PATCH_FILE="$LANE_DIR/lane.patch"
if [ -s "$LANE_PATCH_FILE" ]; then
  if [ -z "$("$REAL_GIT" -C "$TREE" status --porcelain 2>/dev/null)" ]; then
    if ! "$REAL_GIT" -C "$TREE" apply --index --binary --whitespace=nowarn "$LANE_PATCH_FILE" 2>"$LANE_DIR/patch.err"; then
      { echo "lane patch $(sha256sum "$LANE_PATCH_FILE" | cut -c1-12) does not apply on $PIN:"; cat "$LANE_DIR/patch.err"; } > "$LANE_DIR/FAILED"
      echo "pc-lane: lane patch failed to apply — FAILED lane (see $LANE_DIR/FAILED)" >&2
      exit 70
    fi
    echo "pc-lane: lane patch applied on $PIN ($(grep -c '^diff --git' "$LANE_PATCH_FILE") file(s), sha $(sha256sum "$LANE_PATCH_FILE" | cut -c1-12))" >&2
  else
    echo "pc-lane: lane tree already dirty — lane patch assumed applied (replay)" >&2
  fi
fi

# --- code intel in the lane tree (2026-09-15) ----------------------------------
# A lane tree is a fresh worktree of the PIN: no graft index, no GitNexus index — so `graft ask` and the pack
# script (scripts/lane_context.sh) could not run there, and no lane used them (arm A: graft x1; arm B v3: x0,
# 132 whole-file reads, 456 shell calls — the owner, 2026-09-15: "why isn't it using the quartet?").
# `graft build` in a worktree SEEDS from the clone's graph: 4 s measured on the v3 tree (2026-09-15 07:05Z), after
# which `graft ask` answers in 1 s and the whole pack in 4 s — so it runs at every launch. Fail-LOUD, never fatal:
# a lane without an index falls back to grep and says so. The coordinator's report tooling is not proof code:
# the CURRENT report_lint.py is overlaid so a lane never runs the PIN's older lint (v3 ran a lint without fix
# hints and looped on its report — the same class the hints were written to close).
if command -v graft >/dev/null 2>&1; then
  if ( cd "$TREE" && graft build > "$LANE_DIR/graft-build.log" 2>&1 ) && [ -f "$TREE/graft/INDEX.md" ]; then
    echo "pc-lane: graft index built in the lane tree ($TREE/graft/INDEX.md)" >&2
  else
    echo "pc-lane: graft build FAILED (see $LANE_DIR/graft-build.log) — the lane falls back to grep" >&2
  fi
else
  echo "pc-lane: graft not on PATH — no lane index (harness-ports/bin/pc-setup.sh installs it)" >&2
fi
for tool in scripts/report_lint.py; do
  if [ -f "$AF_REPO/$tool" ] && ! cmp -s "$AF_REPO/$tool" "$TREE/$tool" 2>/dev/null; then
    cp "$AF_REPO/$tool" "$TREE/$tool" && echo "pc-lane: overlaid the current $tool into the lane tree" >&2
  fi
done
# --- the prompt: role file, then brief --------------------------------------
PROMPT_FILE="$LANE_DIR/prompt.md"
: > "$PROMPT_FILE"
if [ -n "$ROLE" ]; then
  RF="$AF_REPO/harness-ports/roles/$ROLE.md"
  [ -f "$RF" ] || die "role '$ROLE' not found at $RF"
  cat "$RF" >> "$PROMPT_FILE"
  printf '\n\n---\n\n' >> "$PROMPT_FILE"
fi
cat "$BRIEF" >> "$PROMPT_FILE"
# Standing lane rule (2026-09-03): the context budget is the lane's life. A build lane loaded four
# skills (75 KB) on its first turn, compacted, was told by the compaction handoff to reload them,
# and looped: eight compactions, the brief itself compacted away, a stop-on-reversal halt.
printf '\n\n---\nCONTEXT BUDGET (standing lane rule): do NOT call skill_view or tool_describe unless this brief names a skill by name — your role text and this brief carry every rule you need, and after a compaction do NOT reload skills. Read files by line range (`sed -n`, `grep -n`), never whole large files; every large tool output is context you cannot get back.\n' >> "$PROMPT_FILE"
# Standing lane rule (2026-09-03): the report must survive a mid-run death.
printf '\n\n---\nINCREMENTAL REPORT (standing lane rule): append each FINISHED section of your report to the file %s as you go (shell: `cat >> "$LANE_REPORT_DRAFT"`); the final message is still your full report. Never commit that file.\n' "$LANE_DIR/report-draft.md" >> "$PROMPT_FILE"
# Standing lane rule (2026-09-14): a mechanical gate is BOUNDED. N5k (the first local-model lane) spent 47 minutes and
# 20 turns re-deriving report_lint's token rule and relocating references that were already right, because its brief
# demanded "MISS 0" on a heuristic lint with no fix procedure, no round cap and no escape hatch (AF-AP-76). The lint now
# prints a fix hint per MISS row; the round cap lives HERE so no brief carries it by hand and an old brief's bar is read
# through it.
printf '\n\n---\nMECHANICAL GATES ARE BOUNDED (standing lane rule): `scripts/report_lint.py` is a HEURISTIC check of the `alias:NN` references in your report — run it LAST with the `--map` aliases your brief names, read the `fix:` hint printed on every MISS row and do exactly that (add one backticked identifier copied from the cited line when the line is right; correct the number when it is wrong; write a line that existed only at the PIN as `alias@<PIN>:NN` or in words), for at most THREE rounds; then paste the final summary line into your DISCREPANCIES section and FINISH. Wherever the brief says "MISS 0", read it as this bounded rule: MISS 0 is the target, never a stop condition, and a MISS that survives three rounds is REPORTED, not chased. Never read the source of the lint to re-derive its rule — the hint IS the rule. The harvest grades the floor (`--min-refs`) plus your paste.\n' >> "$PROMPT_FILE"
# Standing lane rule (2026-09-14 23:0xZ): a premise conflict is BOUNDED too. The xhigh arm of the N5k A/B spent 60+
# minutes (45 tool calls, 130k output tokens, no code) re-deriving CPython's close-on-exec default because item 2
# stated a leak the coordinator had never measured at the real emitter; the medium arm flagged the same
# non-reproduction in DISCREPANCIES and built. The cap lives here; the brief-writer measures premises before writing.
printf '\n\n---\nPREMISE CONFLICTS ARE BOUNDED (standing lane rule): when a premise the brief states does not reproduce in your tree (a mutant that does not die, a count that differs, a mechanism that is not there), spend at most THREE experiments on it, then write ONE DISCREPANCIES entry with your measurement (the command and its output) and either build the item on the measured truth when its intent is still satisfiable, or STOP and report when it is not. Never read interpreter or library sources, write C programs or probe the kernel to re-derive a mechanism the brief did not ask you to build; never re-read a file region the harness has already returned (a BLOCKED read is a loop signal — move on). A brief premise is a claim to check once, not a research question.\n' >> "$PROMPT_FILE"
# Standing lane rule (2026-09-15): the instruments are IN the tree now (the block above) — say so, or the lane
# never looks (v3 never called graft; the profile's MCP servers were never searched under the context-budget rule).
printf '\n\n---\nCODE INTEL FIRST (standing lane rule): the dispatcher built a graft index in your tree at launch (`graft/INDEX.md`, seeded from the clone in seconds). Every semantic code question — who calls X, where is the seam for Y, which flags does Z pass, which tests exercise W — goes to the instruments BEFORE any grep or whole-file read: `graft ask "<question>" [--in <path>]` and `graft skeleton <file>` (symbols + line ranges at a twentieth of the tokens of the file); `bash scripts/ripwire_review.sh for|callers|impact|exercises <symbol>` (a second, independent instrument); `python3 scripts/ap_screen.py <file>` (the anti-pattern registry screen; `--tests` for a test file); the whole pack in ONE command: `bash scripts/lane_context.sh -q "<question>" -s <SYMBOL> -o pack.md <files>` (about 4 s). GitNexus blast radius reads the CLONE index: `node %s/.gitnexus/run.cjs impact "<symbol>" --direction upstream --repo %s` (its line numbers are the clone HEAD, not your PIN). Read files by line range from their answers, never whole. `scripts/report_lint.py` in your tree is the dispatcher CURRENT copy, overlaid at launch — not yours: never revert it, never list it in FILE IDENTITY.\n' "$AF_REPO" "$AF_REPO" >> "$PROMPT_FILE"

echo "pc-lane: lane=$LANE_ID harness=$HARNESS role=${ROLE:-none} pin=$PIN" >&2
echo "pc-lane: tree=$TREE" >&2

# --- run the harness --------------------------------------------------------
cd "$TREE" || die "cannot cd $TREE"
export AF_REPO AF_VENV
rc=0

# CAPACITY RETRY (2026-09-03): OmniRoute's Codex routes refuse a "structurally heavy" request
# (a lane prompt is ~47 KB of system prompt + tools) with `HTTP 503 ... capacity is busy`
# while a 24-token probe on the same route answers in 2 s. Hermes retries three times within
# seconds and gives up; the whole lane then costs a dispatch round for a transient. Retry the
# ATTEMPT on that exact signature only, with a doubling backoff, keeping every refused report.
: "${LANE_CAPACITY_RETRIES:=3}"     # extra attempts after a capacity refusal; 0 disables
: "${LANE_CAPACITY_BACKOFF:=60}"    # seconds before the first retry, doubling; tests pass 0
: "${LANE_CAPACITY_MAX_WAIT:=600}"  # cap on one backoff wait (2026-09-08: ten patient retries, never a 30-minute sleep)
# 2026-09-06: a 429 is the same transient class when it is a per-credential cooldown (Ollama Cloud rate limit under two
# concurrent Kimi lanes) or the tail of a fallback chain whose members are all cooling; the codex quota 429 ("exhausted their
# quota (reset after NNh") is NOT transient, so it is excluded — retrying it would burn the backoff for nothing.
# 2026-09-08: the upstream's own overload text (`Our servers are currently overloaded`) carried no HTTP code and slipped past
# this regex — O2 died un-retried eight minutes into an admitted session. Any `API call failed after N retries:` line is a
# transient unless QUOTA_RX says otherwise.
CAPACITY_RX='^API call failed after [0-9]+ retries: '
QUOTA_RX='exhausted their quota'
# 2026-09-08 22:2xZ: the codex quota 429 came back as `(reset after 5m)` — a ROLLING WINDOW, not the hours-long exhaustion
# the 2026-09-06 rule assumed — and three lanes (O3, D5n, B5k) died un-retried on their first refusal, drafts intact. A
# quota refusal whose stated reset carries NO hours field is transient: wait the stated reset plus a slack, then resume
# from the draft like any other refusal. A reset with an hours field, an unparsable one, or one beyond LANE_QUOTA_MAX_WAIT
# stays the FAILED class (retrying it would burn the backoff for nothing).
: "${LANE_QUOTA_SLACK:=30}"        # seconds added to a sub-hour quota reset before the retry; tests pass 0
: "${LANE_QUOTA_MAX_WAIT:=1800}"   # a sub-hour reset longer than this is treated like the hours class
quota_wait_s() {  # $1 = the refusal text; prints the wait for a sub-hour reset, returns 1 for the hours class / no parse
  local spec tok total=0 any=0
  spec=$(grep -Eo 'reset after [0-9hms ]+' "$1" 2>/dev/null | head -1 | sed 's/^reset after //; s/ *$//')
  [ -n "$spec" ] || return 1
  for tok in $spec; do
    case "$tok" in
      *h) return 1;;
      *m) total=$((total + ${tok%m} * 60)); any=1;;
      *s) total=$((total + ${tok%s})); any=1;;
      *) return 1;;
    esac
  done
  [ "$any" = 1 ] || return 1
  total=$((total + LANE_QUOTA_SLACK))
  [ "$total" -le "$LANE_QUOTA_MAX_WAIT" ] || return 1
  echo "$total"
}
# 2026-09-08 13:3xZ: Hermes ends a turn on `session_persistence_failed` with a `⚠️ No reply: the turn was stopped because
# session storage …` line as its ONLY output (the six lanes share the agentfactory profile's one state.db, kept in
# journal_mode=DELETE because the linked SQLite 3.49.1 has the WAL-reset bug — a contended write is classified `disk`);
# VERIFY-B5j died at item 5 that way and the line stood as report.md. Every `No reply:` line is the HARNESS failing, never
# a report: retry the attempt like a capacity refusal (the draft resumes it), and never let it stand as report.md.
# 2026-09-22: a model provider can refuse a lane before it runs with a safety-filter message. The same context is
# deterministic, so retrying only replays the refusal. Match only the first non-empty line: a real lane report may quote
# the specimen later without becoming a refusal. Hermes can render two, one, or zero spaces after the warning glyph, or no glyph.
# This matcher is passed to grep -E; `[[:space:]]*` preserves every glyph-spacing form while the whole glyph group is optional.
SAFETY_RX="^(⚠️[[:space:]]*)?The model provider's safety filter blocked"
PERSIST_RX='^(⚠️ )?No reply: '
# INCREMENTAL REPORT (2026-09-03): a 167-call verify lane died mid-stream with report.md EMPTY —
# the report was all-or-nothing, so 66 minutes of grading came home only via state.db forensics.
# Every lane now gets LANE_REPORT_DRAFT in its environment and a standing prompt line telling it
# to append each finished section there; if the final report is empty, the draft is promoted.
LANE_REPORT_DRAFT="$LANE_DIR/report-draft.md"; export LANE_REPORT_DRAFT
attempt=0
while :; do
attempt=$((attempt + 1))
# RESUME NOTE (2026-09-08): every attempt is a FRESH Hermes session — the route refusal that ended the previous one took its
# context with it (a B5j attempt read for an hour, left a 1.3 KB draft, and its successor started from zero). The successor is
# told what it inherits: the tree state and the incremental draft, to continue from — never to redo.
# A RELAUNCHED loop starts at attempt 1 with a draft already on disk (the coordinator stopped the previous loop by
# pid or it FAILED out of retries): the draft, not the counter, is the resume signal.
PROMPT_RUN="$PROMPT_FILE"
if [ "$attempt" -gt 1 ] || [ -s "$LANE_REPORT_DRAFT" ]; then
  PROMPT_RUN="$LANE_DIR/prompt.attempt$attempt.md"
  { printf 'RESUME (attempt %s of this lane): a previous attempt of THIS lane ended on a route refusal or was stopped by the coordinator, not on its own decision. Its edits are already in your worktree (`git status --porcelain` lists them beside the lane patch) and its incremental report draft is at %s — read that draft FIRST and continue from its last finished section; do not redo a finished section, but verify its claims by run before relying on them.\n\n---\n\n' "$attempt" "$LANE_REPORT_DRAFT"; cat "$PROMPT_FILE"; } > "$PROMPT_RUN"
fi

if [ -n "${PC_LANE_FAKE_HARNESS:-}" ]; then
  # TEST DOUBLE — the one stand-in this port permits, and only for plumbing.
  # It proves worktree/role/report wiring without a model. Refused unless the
  # brief lives under a tests/ directory, so it can never masquerade as a lane.
  # The brief must itself live under a tests/ directory or be named test-*.
  # Deliberately NOT "anything under /tmp": briefs are routinely staged in a
  # temp dir, so that would have let the double stand in for a real lane — which
  # the plumbing test caught.
  case "$BRIEF" in
    */tests/*|*/test-*) ;;
    *) die "PC_LANE_FAKE_HARNESS set for a non-test brief ($BRIEF) — refusing.";;
  esac
  echo "pc-lane: USING FAKE HARNESS (test double) — this is NOT a real lane run." >&2
  # Background + wait at EVERY harness site: bash defers a trapped TERM until a FOREGROUND child exits, so a stop signal
  # would sit unanswered for the whole harness run and stop_session would fire only after the harness finished on its
  # own (the session-stop test read exactly that: grandchild alive, no stderr line). `wait` is interruptible.
  "$PC_LANE_FAKE_HARNESS" < "$PROMPT_RUN" > "$REPORT" 2> "$LOG" &
  HARNESS_PID=$!; wait "$HARNESS_PID"; rc=$?

elif [ "$HARNESS" = "codex" ]; then
  # `codex exec` = non-interactive. Flags, and why each one:
  #   --cd            run in the lane worktree
  #   -o/--output-last-message  the agent's FINAL message -> report.md (this is
  #                   the built-in mechanism; do not scrape stdout for it)
  #   --skip-git-repo-check     the worktree is detached-HEAD; don't refuse it
  #   --dangerously-bypass-hook-trust
  #                   REQUIRED for the ported hooks to run: hooks need persisted
  #                   trust, and an unattended lane has no way to grant it
  #                   interactively. Proven by upstream's own exec hook test
  #                   (codex-rs/exec/tests/suite/hooks.rs). Without it the hooks
  #                   silently do not fire.
  #   --sandbox workspace-write  keep the sandbox ON. NOT
  #                   --dangerously-bypass-approvals-and-sandbox: that disables
  #                   the sandbox too, which is the opposite of what an
  #                   unattended lane should have.
  # Approvals need no flag: exec defaults approval_policy to `never` in headless
  # mode (exec/src/lib.rs:413), so a lane cannot stall on a prompt.
  "$CODEX_BIN" exec \
      --cd "$TREE" \
      --output-last-message "$REPORT" \
      --skip-git-repo-check \
      --dangerously-bypass-hook-trust \
      --sandbox workspace-write \
      - < "$PROMPT_RUN" > "$LOG" 2>&1 &
  HARNESS_PID=$!; wait "$HARNESS_PID"; rc=$?

else
  # `hermes -z` = the purest one-shot: single prompt in, final response text out,
  # nothing else on stdout or stderr. So stdout IS the report.
  # Same agent, same tools, same skills — only the interactive layers stripped.
  # cwd is the workspace, which is why we cd'd into the lane tree above. We do
  # NOT pass --worktree: this script already manages the worktree, and letting
  # Hermes make a second one would put the lane somewhere we are not watching.
  # Owner ruling 2026-09-03: the BUILD lane is Hermes on the PC through OmniRoute on the
  # owner's OpenAI route at the HIGHEST reasoning. -m pins the OmniRoute route id (the
  # persistent provider stays `custom` = OmniRoute in ~/.hermes/config.yaml), --reasoning
  # pins Hermes's own effort, --accept-hooks lets the ported shell hooks run without a
  # TTY prompt (an unattended lane cannot answer one). Both overridable per lane.
  # -p selects the DEDICATED lane profile (created with `hermes profile create --clone`): the
  # merged snippet (repo skills dir, MCP servers, hooks, lane approvals) lives there, so the
  # owner's own default profile is never touched by lane configuration.
  # --in "$TREE" --no-restore-cwd: Hermes restores the last session's recorded cwd by default;
  # the first real lane ran its shell in the main clone (branch tip) instead of the pinned
  # worktree and correctly STOPPED on the pin mismatch (2026-09-03). Pin the cwd explicitly.
  # TERMINAL_CWD is Hermes's runtime carrier for the terminal tool's working directory
  # (agent/runtime_cwd.py: terminal.cwd is bridged to TERMINAL_CWD; agent_init.py reads it).
  # --in moves the PROCESS cwd only — a diagnostic lane still started its shell in $HOME
  # (2026-09-03, 7th run). Pin the tool's cwd explicitly.
  # ROLE -> route defaults (owner 2026-09-03: offload every consistent low-judgment step to
  # the cheapest route that does it reliably; PROVISIONAL until the probe table in
  # docs/WORKFLOW-OFFLOAD-MAP.md pins them). Explicit HERMES_MODEL/HERMES_REASONING win.
  # 2026-09-03 (owner, via Codex): the routes are the four OmniRoute COMBOS `agentfactory-*`
  # (priority failover chains defined in OmniRoute's `combos` table). Chain orders as of
  # 2026-09-05 (K3 promoted, deepseek-v4-flash removed — docs/OMNIROUTE-HERMES-FEDORA-HANDOFF.md):
  #   agentfactory-build    sol-ultra -> ollama-cloud/kimi-k3 -> sol-xhigh -> terra-ultra -> gpt-5.5-xhigh -> glm-5.2 -> free-coding
  #   agentfactory-verify   terra-xhigh -> kimi-k3 -> glm-5.2 -> agy/gemini-3.1-pro-low -> antigravity pro-low -> gpt-5.5-xhigh -> free-reasoning
  #   agentfactory-research kimi-k3 -> gemini-3.1-pro-preview -> glm-5.2 -> agy pro-low -> antigravity pro-low -> gemini flash -> free-chat
  #   agentfactory-sweep    kimi-k3 -> gemini-3-flash-preview -> agy flash-agent -> antigravity flash-agent -> free-fast
  # A combo answers even when its first route refuses (the 503 capacity class, a 429 quota);
  # the served model is whatever the chain reached — the lane report's usage.json names it.
  # 2026-09-14 (owner: "let's get Qwen to do the heavy lifting" after 23 days lost to cloud quota):
  # the BUILD lane's default route is the LOCAL combo `agentfactory-build-local` = the Qwen3.8-27B
  # server on the PC's 3090 (harness-ports/bin/qwen-server.sh, behind OmniRoute as node `qwen-local`
  # via harness-ports/bin/omniroute_local_builder.py) FIRST, then the agentfactory-build chain as
  # fallback when the local server is down. Effort `medium` (measured: ~95 % of xhigh substance at
  # 1/2-1/7 of the thinking; FINDINGS-LOCAL-BUILDER-QWEN38 §6). The cloud route stays one env away:
  # HERMES_MODEL=agentfactory-build HERMES_REASONING=ultra.
  # 2026-09-14 (owner): the VERIFY lane runs on the local model too — build and verify alternate on the one
  # 262k slot. The Qwen3.8 chat template accepts ONLY xhigh (its default), medium and low (`high` maps to xhigh;
  # any other value raises "Unexpected reasoning effort" → the request fails and OmniRoute falls through to the
  # CLOUD chain silently), so on a local combo the effort is CLAMPED below: ultra/max/high → xhigh. The A/B of
  # 2026-09-14 (FINDINGS-LOCAL-BUILDER-QWEN38 §6 step 5) decides whether the build default moves to xhigh.
  case "${ROLE:-}" in
    code-implementer)     DEF_MODEL="agentfactory-build-local"; DEF_EFFORT="medium";;
    adversarial-verifier) DEF_MODEL="agentfactory-verify-local"; DEF_EFFORT="xhigh";;
    evidence-gatherer|researcher) DEF_MODEL="agentfactory-research"; DEF_EFFORT="high";;
    curator|echo-sweeper|contract-runner) DEF_MODEL="agentfactory-sweep"; DEF_EFFORT="medium";;
    *)                    DEF_MODEL="agentfactory-build";    DEF_EFFORT="ultra";;
  esac
  RUN_MODEL="${HERMES_MODEL:-$DEF_MODEL}"; RUN_EFFORT="${HERMES_REASONING:-$DEF_EFFORT}"
  case "$RUN_MODEL" in
    agentfactory-*-local|qwen-local/*)
      case "$RUN_EFFORT" in ultra|max|high) echo "pc-lane: effort '$RUN_EFFORT' clamped to xhigh on the local route ($RUN_MODEL)" >&2; RUN_EFFORT=xhigh;; esac;;
  esac
  # The default is a disposable per-lane clone of the interactive agentfactory profile:
  # it preserves the approved config/env while removing fallback_providers and adding the
  # lane id as OmniRoute's request correlation header. An explicit HERMES_PROFILE is the
  # operator escape hatch and is logged instead of cloned.
  LANE_PROFILE_HELPER="$AF_REPO/harness-ports/bin/lane-profile.sh"
  if [ -n "${HERMES_PROFILE:-}" ]; then
    LANE_PROFILE="$HERMES_PROFILE"
    echo "pc-lane: profile override $LANE_PROFILE" >&2
  else
    [ -x "$LANE_PROFILE_HELPER" ] || die "lane profile helper missing: $LANE_PROFILE_HELPER"
    LANE_PROFILE="$("$LANE_PROFILE_HELPER" create "$LANE_ID")" || die "lane profile create failed"
    "$LANE_PROFILE_HELPER" verify "$LANE_ID" || die "lane profile verify failed"
  fi
  printf '%s\n' "$LANE_PROFILE" > "$LANE_DIR/profile.txt" || die "cannot record lane profile"
  export HERMES_PROFILE="$LANE_PROFILE"

  TERMINAL_CWD="$TREE" \
  "$HERMES_BIN" -p "$LANE_PROFILE" --in "$TREE" --no-restore-cwd -z "$(cat "$PROMPT_RUN")" \
      -m "$RUN_MODEL" \
      --reasoning "$RUN_EFFORT" \
      --accept-hooks \
      --usage-file "$LANE_DIR/usage.json" > "$REPORT" 2> "$LOG" &
  HARNESS_PID=$!; wait "$HARNESS_PID"; rc=$?
fi

quota_wait=""
if grep -Eq "$QUOTA_RX" "$REPORT" 2>/dev/null; then quota_wait=$(quota_wait_s "$REPORT") || quota_wait=""; fi
# A provider safety refusal is terminal for this exact context. Classify it before the capacity retry branch so it can
# never create report.attemptN.md or sleep/back off. Preserve any incremental work under a non-READY filename.
first_nonempty="$(sed -n '/[^[:space:]]/{p;q;}' "$REPORT" 2>/dev/null)"
if printf '%s\n' "$first_nonempty" | grep -Eq "$SAFETY_RX"; then
  { printf 'safety-filter: '; cat "$REPORT"; } > "$LANE_DIR/FAILED"
  rm -f "$REPORT"
  if [ -s "$LANE_REPORT_DRAFT" ]; then
    { echo "PARTIAL REPORT — the model provider's safety filter refused the lane before it wrote its final report; this is the incremental draft it kept. Grade it as PARTIAL evidence, never as a verdict."; echo; cat "$LANE_REPORT_DRAFT"; } > "$LANE_DIR/report.partial.md"
    echo "pc-lane: safety-filter refusal — preserved report-draft.md as report.partial.md" >&2
  fi
  echo "pc-lane: FAILED — the model provider's safety filter refused the request; reason in $LANE_DIR/FAILED" >&2
  exit 70
fi
if [ "$attempt" -le "$LANE_CAPACITY_RETRIES" ] && grep -Eq "$CAPACITY_RX|$PERSIST_RX" "$REPORT" 2>/dev/null \
   && { ! grep -Eq "$QUOTA_RX" "$REPORT" 2>/dev/null || [ -n "$quota_wait" ]; }; then
  wait_s=$((LANE_CAPACITY_BACKOFF * (1 << (attempt - 1))))
  [ "$wait_s" -le "$LANE_CAPACITY_MAX_WAIT" ] || wait_s="$LANE_CAPACITY_MAX_WAIT"
  # a sub-hour quota window: the wait is the window itself (plus the slack), never shorter — a retry inside it is wasted
  if [ -n "$quota_wait" ] && [ "$quota_wait" -gt "$wait_s" ]; then wait_s="$quota_wait"; fi
  cp "$REPORT" "$LANE_DIR/report.attempt$attempt.md"
  : > "$REPORT"   # the refusal line must not STAND as report.md during the backoff: the sandbox poller read a non-empty
                  # report.md as READY and brought the refusal home as six lanes' final reports (2026-09-08 08:1xZ)
  if grep -Eq "$PERSIST_RX" "$LANE_DIR/report.attempt$attempt.md" 2>/dev/null; then
    echo "pc-lane: attempt $attempt ended on a Hermes session-storage failure (state.db write refused) — resuming from the draft in ${wait_s}s ($LANE_CAPACITY_RETRIES retries max)" >&2
  elif [ -n "$quota_wait" ]; then
    echo "pc-lane: attempt $attempt refused by a sub-hour codex quota window ($(grep -Eo 'reset after [0-9hms ]+' "$LANE_DIR/report.attempt$attempt.md" | head -1)) — resuming from the draft in ${wait_s}s ($LANE_CAPACITY_RETRIES retries max)" >&2
  else
    echo "pc-lane: attempt $attempt refused by route capacity / rate limit (HTTP 503 or 429) — retrying in ${wait_s}s ($LANE_CAPACITY_RETRIES retries max)" >&2
  fi
  sleep "$wait_s"
  continue
fi
[ "$attempt" -gt 1 ] && echo "pc-lane: attempt $attempt ended rc=$rc" >&2
break
done

# --- the RUNTIME's verdict decides first (2026-09-23, task #200; AF-AP-67, sixth family) ------------------------------------
# VERIFY-T92-T90R3-PCJ1 wrote its 55 KB report into the lane dir, then its final turn failed: Hermes printed `HTTP 400: [400]:
# No user query found in messages.` and wrote usage.json with "completed": false, "failed": true. The line matched none of the
# text screens below, so it stood as report.md and the poller brought 50 bytes home as the report. A denylist of failure texts
# grows one family per incident (rejected: add `^HTTP [0-9]{3}: `); the runtime's own flags are the structural signal. So,
# after the loop (its capacity and session-storage retries have run; the safety family has already exited 70) and BEFORE the
# text screens: a Hermes session whose usage.json says "failed": true or "completed": false produced no report, whatever its
# last output says. That output is kept in report.failed-output.md (never deleted). A non-empty draft is promoted under a
# FAILED-session header whose first line is the runner's DRAFT REPORT header (the poller's exemption keys on it; the 200 bytes
# go on ONE line, so no pasted `API call failed`/`No reply:` line can start a line the poller greps); no draft = FAILED, rc 70.
# Never retried here: the same context fails the same way. usage.json absent, unparsable or carrying neither flag: the text
# screens decide as before, and ONE warning line says the runtime's verdict was not read.
usage_verdict=""
if [ "$HARNESS" = "hermes" ]; then
  usage_verdict="$(python3 -c 'import json, sys
d = json.load(open(sys.argv[1]))
if not isinstance(d, dict) or not any(isinstance(d.get(k), bool) for k in ("failed", "completed")):
    sys.exit(4)
flag = lambda k: json.dumps(d[k]) if k in d else "absent"
bad = d.get("failed") is True or d.get("completed") is False
print(("failed" if bad else "ok") + " \"failed\": " + flag("failed") + ", \"completed\": " + flag("completed"))' "$LANE_DIR/usage.json" 2>/dev/null)" \
    || { usage_verdict=""; echo "pc-lane: WARNING usage-verdict-unread — $LANE_DIR/usage.json is absent, does not parse or carries neither flag; the runtime's own verdict was not read, so the text screens alone decide this lane (AF-AP-67)" >&2; }
fi
if [ "${usage_verdict%% *}" = failed ]; then
  usage_flags="${usage_verdict#failed }"
  cp -f "$REPORT" "$LANE_DIR/report.failed-output.md"
  failed_head="$(head -c 200 "$LANE_DIR/report.failed-output.md" | sed -z 's/\n/\\n/g')"
  if [ -s "$LANE_REPORT_DRAFT" ]; then
    { echo "DRAFT REPORT — the Hermes session FAILED (usage.json $usage_flags; harness rc=$rc) before writing its final report; its last output is not a report and is kept in report.failed-output.md. This is the incremental draft the lane kept. Grade it as PARTIAL evidence, never as a verdict."
      printf 'FAILED SESSION OUTPUT (first 200 bytes, newlines shown as \\n): %s\n' "$failed_head"
      echo; cat "$LANE_REPORT_DRAFT"; } > "$REPORT"
    echo "pc-lane: the Hermes session FAILED (usage.json $usage_flags) — its last output kept as report.failed-output.md; promoted report-draft.md (PARTIAL)" >&2
  else
    { echo "failed-session: the Hermes runtime reported this session failed (usage.json $usage_flags; harness rc=$rc) and the lane kept no draft to promote. Its last output (also kept in report.failed-output.md):"; cat "$LANE_DIR/report.failed-output.md"; } > "$LANE_DIR/FAILED"
    rm -f "$REPORT"
    echo "pc-lane: FAILED — the Hermes session failed (usage.json $usage_flags) and left no draft; reason in $LANE_DIR/FAILED: $failed_head" >&2
    exit 70
  fi
# 2026-09-07: with the retries exhausted (or disabled) the refusal line used to STAND as report.md — the sandbox
# poller printed "report -> …" and exited 0 for a lane that never ran (B5i, HTTP 503 on every call while the owner's
# own Hermes sessions held the route's admission slots). A refusal is a FAILED lane: the line goes to $LANE_DIR/FAILED,
# report.md is removed so nothing downstream can grade it, and the script exits 70. The poller reads FAILED.
elif grep -Eq "$CAPACITY_RX|$QUOTA_RX|$PERSIST_RX|^API call failed" "$REPORT" 2>/dev/null; then
  cp "$REPORT" "$LANE_DIR/FAILED"; rm -f "$REPORT"
  echo "pc-lane: FAILED — the route or the harness refused every attempt ($attempt); reason in $LANE_DIR/FAILED: $(head -c 200 "$LANE_DIR/FAILED")" >&2
  exit 70
fi

if [ ! -s "$REPORT" ] && [ -s "$LANE_REPORT_DRAFT" ]; then
  { echo "DRAFT REPORT — the lane ended (harness rc=$rc) before writing its final report; this is the incremental draft it kept. Grade it as PARTIAL evidence, never as a verdict."; echo; cat "$LANE_REPORT_DRAFT"; } > "$REPORT"
  echo "pc-lane: final report empty — promoted report-draft.md (PARTIAL)" >&2
fi

# LANE TRANSCRIPT HOME (owner 2026-09-03): export the Hermes session (scrubbed) INTO the worktree
# so it travels with the patch; the curator lane reads transcripts/pc/*.md later.
if [ "$HARNESS" = "hermes" ] && [ -s "$LANE_DIR/usage.json" ]; then
  SID="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('session_id',''))" "$LANE_DIR/usage.json" 2>/dev/null)"
  LANE_PROFILE="$(cat "$LANE_DIR/profile.txt" 2>/dev/null)"
  HDB="${HERMES_STATE_DB:-$HOME/.hermes/profiles/${LANE_PROFILE:-${HERMES_PROFILE:-agentfactory}}/state.db}"
  if [ -n "$SID" ] && [ -f "$HDB" ]; then
    python3 "$AF_REPO/harness-ports/bin/hermes-session-export.py" --db "$HDB" --session "$SID" \
      --out "$TREE/transcripts/pc/$LANE_ID.md" >/dev/null 2>>"$LOG" \
      && { printf '\n---\nprofile: %s\n\nusage.json:\n\n```json\n' "${LANE_PROFILE:-unknown}" >> "$TREE/transcripts/pc/$LANE_ID.md"; cat "$LANE_DIR/usage.json" >> "$TREE/transcripts/pc/$LANE_ID.md"; printf '\n```\n' >> "$TREE/transcripts/pc/$LANE_ID.md"; echo "pc-lane: transcript -> transcripts/pc/$LANE_ID.md (in the lane tree)" >&2; } \
      || echo "pc-lane: session export FAILED (see lane.log) — report still stands" >&2
  fi
fi

if [ ! -s "$REPORT" ]; then
  echo "pc-lane: harness exited $rc but produced NO report — see $LOG" >&2
  [ -s "$LOG" ] && tail -40 "$LOG" >&2
  [ "$rc" -eq 0 ] && rc=70
fi

echo "pc-lane: done lane=$LANE_ID rc=$rc report=$REPORT" >&2
[ -s "$REPORT" ] && cat "$REPORT"
exit "$rc"
