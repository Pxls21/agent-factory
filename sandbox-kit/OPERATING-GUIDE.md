# Sandbox operating guide — how to work in this environment

The cross-cutting, learned-the-hard-way rules for operating a project inside the **Claude Code on the
web** ephemeral container. Topic-specific setup lives alongside this file in the kit
(`OUROBOROS-SETUP.md`, `PC-BRIDGE.md`) and in the host repo (`scripts/setup.sh`); this is the
day-to-day operating playbook. **If a step here contradicts another doc, this file is the operational
source.** Repo-specific values below (branch names, the test subset) are examples — adapt per project.

Last updated 2026-06-25.

## 0. The one rule: nothing local survives

The container is reclaimed after inactivity and re-cloned fresh. Global installs, MCP registrations,
caches, and uncommitted edits are **all lost**. So: **commit and push anything worth keeping**, and
prefer *committed repo config* (e.g. `.mcp.json`) over per-session setup commands. `scripts/setup.sh`
is the source of truth for the toolchain and re-runs each session.

**The toolchain is rebuilt automatically by a SessionStart hook** (`.claude/hooks/session-start.sh`,
registered in `.claude/settings.json`) that runs `scripts/setup.sh` on every web session. It is
**synchronous** (the session waits — cold ~2-4 min, cached <30s) and prints a start banner + an
elapsed-time completion line, so you can see how long setup took and that it finished. If you ever hit
a missing dep mid-session, the hook either hasn't been merged to the default branch yet or you can
re-run `bash scripts/setup.sh` by hand.

## 1. Branch — verify before you commit

The task-designated branch can be a **stale bare base**. As of 2026-06-20 all real work is on
**`claude/project-setup-review-urlfik`**; `claude/project-setup-access-rjmun7` is a 3-commit skeleton
with none of the code. Always confirm first:

```bash
git branch --show-current        # expect claude/project-setup-review-urlfik
```

If wrong: `git fetch origin && git checkout claude/project-setup-review-urlfik`. Commit and push
frequently — unpushed work dies with the container.

## 2. Running tests

- **Use the project venv** — `pytest` is NOT on the system python:
  ```bash
  .venv/bin/python -m pytest tests/test_foo.py -q
  ```
  If `.venv` is missing, `bash scripts/setup.sh` rebuilds it (deps live only in `.venv`).
- **Do NOT run the full suite blind — it HANGS.** Some tests reach for a live model / network (the
  bridge, embedder, `claude -p`) and block indefinitely. Run a **targeted subset** scoped to your
  change instead. Example, for gate-synthesis work:
  ```bash
  .venv/bin/python -m pytest tests/test_propose_assertions.py tests/test_proposer_acceptance.py \
    tests/test_derive_gate_from_trace.py tests/test_outcome_gate.py tests/test_solve_loop.py \
    tests/test_solve_spine.py tests/test_workflow_store.py -q
  ```
  To approximate a full run, exclude the model/network tests:
  `-k "not real_tier and not fully_auto and not e2e_setup"` (and expect `test_phase3_semantic` to
  error if the `wordllama` model isn't installed — a known env gap, not a regression).

## 3. GitNexus (code intelligence — required by CLAUDE.md) — three tiers, in order

**Actually use GitNexus** — the recurring failure mode is not leveraging it at all. Prefer the richest
interface that works right now:

1. **Native MCP tools** (`impact`, `detect_changes`, `query`, `context`, `explain`, …) when the session
   has them connected.
2. **stdio fallback** when the native MCP is disconnected (common — it loads only at session start and
   often doesn't reconnect after a reclaim). The *server* is still fine; drive it directly:
   ```bash
   python scripts/gn_mcp.py --list
   python scripts/gn_mcp.py impact '{"target":"<symbol>","direction":"upstream","summaryOnly":true}'
   python scripts/gn_mcp.py detect_changes '{"scope":"compare","base_ref":"<pre-change-commit>"}'
   ```
   (`gn_mcp.py` keeps stdin open across the async tool call — a one-shot `subprocess.run` closes stdin,
   the server reads EOF as a disconnect, and you get no response. This is the gotcha that makes naive
   stdio MCP probes "silently" fail.)
3. **CLI last resort** — same operations as subcommands:
   ```bash
   node .gitnexus/run.cjs impact <symbol> --summary-only            # BEFORE editing
   node .gitnexus/run.cjs detect-changes -s compare -b <pre-change-commit>   # BEFORE pushing
   ```

**Keep the index fresh.** `node .gitnexus/run.cjs status` reports freshness; `analyze` rebuilds it. A
**stale index silently breaks `impact` on newly-added symbols** (it hangs / returns empty) — re-analyze
after adding modules before trusting the blast radius. `analyze` auto-edits the index-count line in
`CLAUDE.md`/`AGENTS.md` (commit as a chore; don't hand-edit inside the `gitnexus:start` blocks). Full
command reference + diff-scope semantics + a worked example: **`GITNEXUS-CLI.md`**. If everything is
missing, fall back to a manual blast-radius check (grep importers + run the affected tests) and say so.

## 3b. Council of High Intelligence (`/council`) — debate BEFORE the research prompt

Vendored at `sandbox-kit/council-of-high-intelligence/` (MIT, file-copy install only); `scripts/setup.sh`
re-installs it to `~/.claude` each session (the install does NOT survive container reclaim — that's why it's
in setup). It is the **first stage of the feature workflow** (CLAUDE.md step 1.5): an 18-persona
structured-disagreement engine that frames the *questions* before the research prompt is written, so we never
research/execute a badly-posed question (the Granite-swap failure mode).

- **Invoke:** `/council <problem>` (full 18), `/council --quick <problem>` (2-round), `/council --duo` (one
  polarity pair), or `/council --members a,b,c` / `--triad <domain>` to bound cost. `--dry-route` previews
  routing without running.
- **Protocol:** blind Round 1 → **anonymized** Round 2 cross-examination (kills conformity bias) → 100-word
  final positions → a separate audited **Chairman** verdict that *leads with what's unresolved*. Dissent
  quotas + novelty gates + anti-recursion are enforced between rounds.
- **One backbone here:** the sandbox has only the Claude provider, so it runs Claude-only (`--no-auto-route`
  effectively). Still valuable for orthogonal perspectives; for genuine multi-model diversity run it on the
  **PC** with Gemini/Ollama/NIM CLIs installed (auto-routing splits polarity pairs across providers).
- **When:** mandatory before any change that could trade away security/accuracy/robustness for speed; skip
  for small/obvious work. Feed the verdict's unresolved-questions + dissents into `RESEARCH-PROMPT-N.md` as
  the entropy the brief must SETTLE.
- **Portable:** to add it elsewhere, run `sandbox-kit/council-of-high-intelligence/install.sh`
  (`--codex` / `--gemini` for those CLIs).

## 4. Ouroboros MCP — flapping and session recovery

The interview/seed MCP can **disconnect and reconnect repeatedly ("flapping")**. Root cause: a
tool-approval prompt is sent to the user's phone with a ~10–20 min window; if it isn't approved in
time the session restarts, dropping the in-flight call. Mitigations:

- **Interview state persists on disk** at `~/.ouroboros/data/interview_*.json`. After a context loss,
  read the latest file to recover the `session_id` and the current question.
- **Resume with `session_id`, not `interview_id`** — `interview_id` is only valid for *new*
  interviews (passing it to resume errors).
- Keep `last_question` **free of shell metacharacters** (`;`, etc.) — they're rejected.
- The Ouroboros MCP is **pre-approved** in `.claude/settings.json` (`permissions.allow: ["mcp__ouroboros"]`)
  so its tool calls don't trigger a phone approval each time — keep that entry to reduce the flapping.
- Persist seeds to `seeds/seed-<name>-vN.yaml` and commit immediately; the seed is the spec.

## 5. The PC bridge (heavy / live-model jobs)

Run heavy, long, or live-model work **on the PC, not in the sandbox** (the sandbox is ephemeral and
CPU-only). The bridge works over an **HTTP/HTTPS tunnel** — Tailscale/SSH do *not* work from the
sandbox (egress is 80/443 only via the Egress Gateway). Procedure + token-gated shell bridge:
`PC-BRIDGE.md`. The live LLM proposer and the empirical lift run (see
`../docs/INCREMENT-2-PROPOSER-HANDOFF.md`) go through this bridge.

**The current session's live bridge URLs are in `ACTIVE-LINKS.md` — check there first** (and record
fresh links the human pastes); they are ephemeral quick-tunnel URLs that change every launch.

**Critical: tunnel the TurboQuant `llama-server` (port 11435), NOT Ollama (11434).** Ollama can't
bound the 27B thinking model's reasoning, so a structured / think-then-emit call hangs 30+ min.
Verify with `curl <url>/props` — a `model_path` ⇒ llama-server (good). **Do NOT use `/api/tags`** to
tell them apart: llama-server answers it too. Absence of `model_path` ⇒ wrong/stale endpoint. Full
detail in `PC-BRIDGE.md`'s ⚠️ box.

## 5a. Observability human plane (see the pipeline on your phone)

When the pipeline is a black box, bring up the **human plane**: `bash scripts/phoenix-up.sh` ON THE
PC starts a self-hosted Phoenix UI + OTLP collector on :6006 and a Cloudflare tunnel, printing a
phone-clickable `trycloudflare.com` URL (record it in `ACTIVE-LINKS.md`). Opt the pipeline in with
`PHOENIX_OTLP_ENDPOINT=<endpoint>/v1/traces` — unset = OFF, committed substrate byte-identical. The
human plane is best-effort and can never perturb the committed trace. Full how-to + guarantees:
`HUMAN-PLANE.md`.

## 6. Tool / shell gotchas (agent-specific)

- **`pytest` INTERNALERROR: `ValueError: no option named 'htmlpath'`** — a globally-installed
  `seleniumbase` pytest plugin auto-registers and crashes `pytest_configure` on containers with no
  `.venv` yet (system python's site-packages has it, unrelated to this project's deps). Fix: add
  `-p no:seleniumbase` to the invocation. Confirm first whether `.venv` exists (`ls .venv/bin/python`)
  — if it's missing and your change doesn't need the heavy deps (hmmlearn/pymoo/stumpy/ta-lib), a
  targeted subset against system python + this flag is enough; don't run `scripts/setup.sh` just to
  silence this.
- **No broad `pkill` / `kill %1`.** `pkill -f pytest` and job-spec kills can terminate the agent's own
  shell (seen as exit 144). Target an explicit PID, or just let a background task finish.
- **The Bash tool blocks chained `sleep`.** To wait on a condition use the **Monitor** tool or
  `run_in_background: true` with an `until <check>; do sleep 2; done` loop — not `sleep N && cmd`.
- **Avoid `cd` in compound commands** (triggers permission prompts); use absolute paths.
- **Headless screenshots (HTML render checks):** `npm i playwright-core --no-save` in the
  SCRATCHPAD (no repo-tree node_modules has it; the valuecell path drops it on reinstall), then
  `chromium.launch({executablePath: '/opt/pw-browsers/chromium'})` — never `playwright install`.
  Verify layout with `document.documentElement.scrollWidth` at the target viewport; old-headless
  clipping artifacts come from the SHOT tool, not the page (measure before "fixing" the page).
- Make independent tool calls **in parallel** (one message, multiple calls); only serialize when a
  call depends on a prior result.
