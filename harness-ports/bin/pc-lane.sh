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
#   HERMES_MODEL   OmniRoute route id    default: by ROLE (see role_model below); owner ruling
#                  2026-09-03: BUILD = codex/gpt-5.6-sol-ultra; cheaper routes for consistent
#                  low-judgment roles; Gemini for search/research. PROVISIONAL until probed.
#   HERMES_REASONING  Hermes effort      default: by ROLE (ultra for build/verify, high otherwise)
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
cleanup() { rm -f "$PIDFILE"; }
trap cleanup EXIT

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
# Standing lane rule (2026-09-03): the report must survive a mid-run death.
printf '\n\n---\nINCREMENTAL REPORT (standing lane rule): append each FINISHED section of your report to the file %s as you go (shell: `cat >> "$LANE_REPORT_DRAFT"`); the final message is still your full report. Never commit that file.\n' "$LANE_DIR/report-draft.md" >> "$PROMPT_FILE"

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
CAPACITY_RX='^API call failed after [0-9]+ retries: HTTP 503'
# INCREMENTAL REPORT (2026-09-03): a 167-call verify lane died mid-stream with report.md EMPTY —
# the report was all-or-nothing, so 66 minutes of grading came home only via state.db forensics.
# Every lane now gets LANE_REPORT_DRAFT in its environment and a standing prompt line telling it
# to append each finished section there; if the final report is empty, the draft is promoted.
LANE_REPORT_DRAFT="$LANE_DIR/report-draft.md"; export LANE_REPORT_DRAFT
attempt=0
while :; do
attempt=$((attempt + 1))

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
  "$PC_LANE_FAKE_HARNESS" < "$PROMPT_FILE" > "$REPORT" 2> "$LOG"
  rc=$?

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
      - < "$PROMPT_FILE" > "$LOG" 2>&1
  rc=$?

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
  # (priority failover chains defined in OmniRoute's `combos` table, smoke-tested 200 each):
  #   agentfactory-build    sol-ultra -> sol-xhigh -> terra-ultra -> gpt-5.5-xhigh -> free-coding
  #   agentfactory-verify   terra-xhigh -> agy/gemini-3.1-pro-low -> antigravity pro-low -> gpt-5.5-xhigh -> free-reasoning
  #   agentfactory-research gemini-3.1-pro-preview -> agy pro-low -> antigravity pro-low -> gemini flash -> free-chat
  #   agentfactory-sweep    gemini-3-flash-preview -> agy flash-agent -> antigravity flash-agent -> free-fast
  # A combo answers even when its first route refuses (the 503 capacity class, a 429 quota);
  # the served model is whatever the chain reached — the lane report's usage.json names it.
  case "${ROLE:-}" in
    code-implementer)     DEF_MODEL="agentfactory-build";    DEF_EFFORT="ultra";;
    adversarial-verifier) DEF_MODEL="agentfactory-verify";   DEF_EFFORT="xhigh";;
    evidence-gatherer|researcher) DEF_MODEL="agentfactory-research"; DEF_EFFORT="high";;
    curator|echo-sweeper|contract-runner) DEF_MODEL="agentfactory-sweep"; DEF_EFFORT="medium";;
    *)                    DEF_MODEL="agentfactory-build";    DEF_EFFORT="ultra";;
  esac
  TERMINAL_CWD="$TREE" \
  "$HERMES_BIN" -p "${HERMES_PROFILE:-agentfactory}" --in "$TREE" --no-restore-cwd -z "$(cat "$PROMPT_FILE")" \
      -m "${HERMES_MODEL:-$DEF_MODEL}" \
      --reasoning "${HERMES_REASONING:-$DEF_EFFORT}" \
      --accept-hooks \
      --usage-file "$LANE_DIR/usage.json" > "$REPORT" 2> "$LOG"
  rc=$?
fi

if [ "$attempt" -le "$LANE_CAPACITY_RETRIES" ] && grep -Eq "$CAPACITY_RX" "$REPORT" 2>/dev/null; then
  wait_s=$((LANE_CAPACITY_BACKOFF * (1 << (attempt - 1))))
  cp "$REPORT" "$LANE_DIR/report.attempt$attempt.md"
  echo "pc-lane: attempt $attempt refused by route capacity (HTTP 503) — retrying in ${wait_s}s ($LANE_CAPACITY_RETRIES retries max)" >&2
  sleep "$wait_s"
  continue
fi
[ "$attempt" -gt 1 ] && echo "pc-lane: attempt $attempt ended rc=$rc" >&2
break
done

if [ ! -s "$REPORT" ] && [ -s "$LANE_REPORT_DRAFT" ]; then
  { echo "DRAFT REPORT — the lane ended (harness rc=$rc) before writing its final report; this is the incremental draft it kept. Grade it as PARTIAL evidence, never as a verdict."; echo; cat "$LANE_REPORT_DRAFT"; } > "$REPORT"
  echo "pc-lane: final report empty — promoted report-draft.md (PARTIAL)" >&2
fi

# LANE TRANSCRIPT HOME (owner 2026-09-03): export the Hermes session (scrubbed) INTO the worktree
# so it travels with the patch; the curator lane reads transcripts/pc/*.md later.
if [ "$HARNESS" = "hermes" ] && [ -s "$LANE_DIR/usage.json" ]; then
  SID="$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('session_id',''))" "$LANE_DIR/usage.json" 2>/dev/null)"
  HDB="${HERMES_STATE_DB:-$HOME/.hermes/profiles/${HERMES_PROFILE:-agentfactory}/state.db}"
  if [ -n "$SID" ] && [ -f "$HDB" ]; then
    python3 "$AF_REPO/harness-ports/bin/hermes-session-export.py" --db "$HDB" --session "$SID" \
      --out "$TREE/transcripts/pc/$LANE_ID.md" >/dev/null 2>>"$LOG" \
      && { printf '\n---\nusage.json:\n\n```json\n' >> "$TREE/transcripts/pc/$LANE_ID.md"; cat "$LANE_DIR/usage.json" >> "$TREE/transcripts/pc/$LANE_ID.md"; printf '\n```\n' >> "$TREE/transcripts/pc/$LANE_ID.md"; echo "pc-lane: transcript -> transcripts/pc/$LANE_ID.md (in the lane tree)" >&2; } \
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
