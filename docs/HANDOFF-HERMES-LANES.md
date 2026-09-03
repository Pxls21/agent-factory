# HANDOFF PROMPT — adopt the PC Hermes build/verify lanes in trading-system (paste to that repo's agent)

Written 2026-09-03 in `pxls21/agent-factory`. Everything below is proven in that repo unless marked
PROVISIONAL. Source of truth for the mechanics: `agent-factory` at the commit named in §1;
`docs/WORKFLOW-OFFLOAD-MAP.md` there is the end-to-end map, `PC-BRIDGE.md` §Hermes BUILD lanes is the
runbook, `docs/INCIDENT-LOG.md` (2026-09-03 bring-up entry) lists the eight things that broke and
their fixes. The owner's ruling that this implements: all token-heavy work (build, fix, debug, run,
first-pass verification) runs on the owner's Hermes CLI on the PC through OmniRoute; the coordinator
keeps seeds, briefs, contracts, the final validation and every push.

---

## PROMPT (copy from here)

You are the coordinator of `trading-system` (branch `claude/clean-build`). Port the PC Hermes lane
kit from `pxls21/agent-factory` so that build, fix, debug and first-pass verification lanes run on
the owner's Hermes CLI on the PC through OmniRoute, while you keep seeds, briefs, contracts, final
validation and every push. Go through your own build loop for this port (it is tooling: one
increment = files + deterministic test + commit; no seed needed). Do not touch the owner's running
services on the PC; nothing needs sudo. The owner's default Hermes profile is never modified — a
dedicated profile is cloned from it.

### 1. Fetch the kit (read it before copying; the brief is a hypothesis, the tree wins)
`git clone --depth 1 https://github.com/pxls21/agent-factory /tmp/af && git -C /tmp/af log -1`
(any commit at or after `c93b46b` on `claude/soundbox-kit-migration-iz1jwf`). Copy these paths,
then adapt as in §2:
- `harness-ports/bin/{pc-lane.sh,pc-setup.sh,hermes-config-merge.py,hermes-session-export.py,hook-shim.sh,hermes-hook-adapter.py,sync-skills.sh,build-roles.py}`
- `harness-ports/roles/*.md`, `harness-ports/briefs/*.md`, `harness-ports/hermes/config-snippet.yaml`, `harness-ports/hand-ported.txt`
- `harness-ports/tests/{run-all.sh,test_pc_lane.sh,test_pc_bridge_exec.py,test_bridge_token_handling.py,test_hermes_session_export.py,test_hermes_hook_adapter.py,test_hermes_spool.py,test_sync_skills.sh}`
- `scripts/{pc.sh,pc_bridge_exec.py,pc_lane.sh,transcript_export.py}`, `tests/{test_transcript_export.py,test_hooks_worktree.py,test_shell_syntax.py}`
- the post-push transcript-sync block at the end of `scripts/push_clean.sh`, the `transcripts/`
  ledger-plane exemption in `scripts/hooks/post-commit`, and the worktree-safe sentinel paths in
  `.claude/hooks/turn-retro-gate.sh` + `scripts/hooks/{post-commit,pre-push}` (`git rev-parse
  --absolute-git-dir` / `--git-common-dir` instead of `$REPO_ROOT/.git/...`).
- `PC-BRIDGE.md` §"Hermes BUILD lanes on the PC" and `docs/WORKFLOW-OFFLOAD-MAP.md` as the runbook/map
  to adapt into your own docs.

### 2. Adapt (mechanical substitutions; grep each one to zero)
`agent-factory` → `trading-system`; `AF_REPO`/`AF_VENV` env names may stay (they are generic) but the
defaults `$HOME/agent-factory` / `$HOME/venv-agent-factory` → your PC clone `$HOME/trading-system`
and its venv; `LANE_BRANCH` default → `claude/clean-build`; the Hermes profile name `agentfactory` →
`tradingsystem` (lowercase alphanumeric only); the `X-Agent-Token` + `{"cmd"}` + `/exec` bridge
contract is the owner's bridge, keep it; `.pc-bridge.env` stays untracked. Keep the role→route
defaults in `pc-lane.sh` as they are (owner ruling: build = `codex/gpt-5.6-sol-ultra`, reasoning
ultra); the other roles' routes are PROVISIONAL.

### 3. Bring-up on the PC (over the bridge; the owner pastes the BRIDGE READY banner into `.pc-bridge.env`)
1. Clone your repo on the PC at `$HOME/trading-system` (designated branch), `git config core.hooksPath scripts/hooks`.
2. `nohup bash harness-ports/bin/pc-setup.sh > .lanes/pc-setup.log 2>&1 &` (user-level: venv, gitnexus 1.6.10, graft, codebase-memory, code-review-graph, ouroboros, detached indexes). Poll the log; never a foreground call over the bridge longer than ~100 s.
3. `hermes profile create --clone --description "trading-system BUILD lanes" tradingsystem`, then
   `python3 harness-ports/bin/hermes-config-merge.py --config ~/.hermes/profiles/tradingsystem/config.yaml --snippet harness-ports/hermes/config-snippet.yaml --set AF_REPO=$HOME/trading-system --set AF_VENV=$HOME/venv-trading-system --set CODEBASE_MEMORY_BIN=$HOME/.local/bin/codebase-memory-mcp --skip mcp_servers.codebase-memory` (the owner's default already runs `codebase-memory-mcp`). The snippet already disables the Ouroboros MCP server for lanes and carries the hard denies (`git push*`, `gh pr *` …). Never `--yolo` a lane yourself; Hermes one-shot already runs with `HERMES_YOLO_MODE=1`, which is exactly why the denies and the git/gh shims exist.
4. Run the TWO diagnostic lanes before any real brief (60–90 s each; templates in `agent-factory` `spikes/hermes-lane-trial/README.md` and the diag briefs described in `docs/INCIDENT-LOG.md`): (a) placement — `pwd` = the pinned linked worktree, `.git` is a `gitdir:` file, HEAD = PIN, `TERMINAL_CWD` set; (b) guards — `git push origin HEAD` and `gh pr list` are BLOCKED (exit -1, deny message). Then (c) one lane that writes ONE new file and returns it through the patch path (`patch-<lane>.diff` next to the report; apply with `git apply --index`).
5. First real brief: your next pending increment, with a pre-registered contract (`contract-gate` step 1) and the evidence demands the templates show. Dispatch: `scripts/pc_lane.sh <brief-with-PIN.md> hermes code-implementer`; poll; harvest the patch; run your gates; dispatch the verifier (lane template `verify-contract.md` on the PC, plus your sandbox Opus 5 verifier for spine work); commit with the reasoning record; push through your `push_clean.sh`.

### 4. The eight pitfalls already paid for (do not rediscover them)
1. A known-broken optional MCP server (Ouroboros `mcp serve`) crash-loops and stalls the lane before its first model call → disabled in the lane profile.
2. The bridge answers with a JSON envelope; unwrap it (`pc_bridge_exec.py`) or polling matches by substring luck and the report fetch base64-decodes JSON.
3. Hermes restores its last recorded cwd; `--in DIR --no-restore-cwd` moves the PROCESS only — the terminal tool reads `TERMINAL_CWD`; export it per lane and prove placement with `pwd` from the lane's own output.
4. Hook sentinels under `$REPO_ROOT/.git/...` are unwritable in a linked worktree (`.git` is a file) → a turn gate fires every turn and a lane loops (20 model calls, 1.8M tokens) → use `git rev-parse --absolute-git-dir` / `--git-common-dir`.
5. A coordinator turn-end hook (retro gate, Stop-style) wired into a one-shot lane replaces the final DATA report with the gate's answer → never wire `pre_verify` for lanes.
6. A pre-commit hook that hardcodes the sandbox venv path and exits 0 when pyflakes is missing skips every later gate on the PC → honour `AF_VENV`, degrade one gate only.
7. A brief must quote artifact shapes and identifiers read from the file in the same sitting; a lane will (correctly) halt on an invented rule id or a misdescribed shape.
8. The lane's patch must diff the index against the PIN, not HEAD, or a lane that commits its increments ships an empty patch.

### 5. Operating rules that travel with the kit
Briefs are files with a `PIN:` line; reports are DATA (files:lines, verbatim outputs, discrepancies, NOT-done); lanes never push, open PRs, comment, install system packages or issue gate verdicts; the coordinator never self-accepts spine work; every gate is deterministic and LLM-free; transcripts are scrubbed before they reach the repo (`scripts/transcript_export.py`'s SECRET_PATTERNS, tested per class) — extend the scrubber test before exporting anything new; the wiki curator, echo-sweeper and researcher lanes are PROVISIONAL routes until your own probe table pins them.

Report back: the commit that lands the port, the three diagnostic lane outputs verbatim, and the first real increment's contract + verdict.

## (end of prompt)

---

**Maturity note for the owner (2026-09-03):** proven here — build lane round trip, worktree placement,
hard limits under yolo, patch path, transcript export with per-class scrubbing tests, lane transcript
export. PROVISIONAL — the non-build routes (verifier/researcher/curator), the curator lane (never run),
the probe table (empty). Sending this before the probe table has rows is fine as long as the receiving
agent treats §2's routes as defaults to measure, not facts.
