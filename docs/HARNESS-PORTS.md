# HARNESS PORTS — the project's agent context on Codex CLI and Hermes Agent

Status: **ported to agent-factory and unit-proven in the sandbox; NOT smoke-tested on the PC.**
NOT smoke-tested in agent-factory on the PC — all PC-side verification from the trading-system
port is inherited, not re-run here.
Owner action required — see [Owner-run smoke](#owner-run-smoke) before trusting any of it.

The owner is standing up a PC-side manager agent. This document records how this project's
**full** agent environment — rules, skills (all 382), hooks, MCP servers, agents, workflows,
output styles, and the spawn path — was ported to the two harnesses that will run there, what
each harness genuinely enforces, and — first-class — what it does **not**.

An exact clone of `.claude/` in spirit, not in mechanism. The rules are identical; only
mechanism names changed. What cannot be cloned is listed honestly in
[What is NOT identical](#what-is-not-identical).

---

## 1. What was built

| Deliverable | Path | Read by |
|---|---|---|
| Codex project instructions | `AGENTS.md` | Codex CLI |
| Hermes project instructions | `.hermes.md` | Hermes Agent |
| ALL ported skills (382) | `.agents/skills/<name>/SKILL.md` | **both** |
| Lane roles (3) | `harness-ports/roles/{code-implementer,adversarial-verifier,evidence-gatherer}.md` | both (prepended by spawn path) |
| Codex hooks + MCP | `.codex/config.toml` | Codex CLI |
| Hermes hooks + MCP + provider | `harness-ports/hermes/config-snippet.yaml` | Hermes (merge by hand) |
| Hook shim (no logic duplication) | `harness-ports/bin/hook-shim.sh` | both |
| Codex payload adapter | `harness-ports/bin/codex-hook-adapter.py` | Codex |
| Hermes payload/return adapter | `harness-ports/bin/hermes-hook-adapter.py` | Hermes |
| Hermes edit-snapshot spool | `harness-ports/bin/hermes-spool-reader.py` | Hermes pre_llm_call |
| MCP launcher | `harness-ports/bin/mcp-server.sh` | Codex (Hermes inlines) |
| MCP acceptance probe | `harness-ports/bin/mcp-smoke.sh` | owner, on the PC |
| Role builder + checker | `harness-ports/bin/build-roles.py` | CI / tests |
| **Spawn path (PC-side)** | `harness-ports/bin/pc-lane.sh` | **owner / bridge** |
| **Spawn path (sandbox-side)** | `scripts/pc_lane.sh` | sandbox coordinator |
| **Skill sync** | `harness-ports/bin/sync-skills.sh` | owner, after any `.claude/skills` change |
| Premortem-roast procedure | `.agents/skills/premortem-roast/SKILL.md` | both |
| Output style (default) | folded into `AGENTS.md` / `.hermes.md` (attention-kind) | both |
| Adapter tests | `harness-ports/tests/test_*` | CI / anyone |

### Sources this port was built from

Primary source throughout — both harnesses' repositories were cloned and read, not summarised
from memory. Where only vendor documentation existed, the URL is given.

| Subject | Source |
|---|---|
| Codex: everything below | `github.com/openai/codex` @ `bc39b0e` (cloned) |
| Codex AGENTS.md discovery + precedence + 32 KiB budget | <https://learn.chatgpt.com/docs/agent-configuration/agents-md> |
| Codex skills directories + SKILL.md shape | <https://learn.chatgpt.com/docs/build-skills> |
| Codex hook events + TOML schema | `codex-rs/config/src/hook_config.rs` |
| Codex hook tool names + aliases | `codex-rs/core/src/tools/hook_names.rs` |
| Codex hook output contract | `codex-rs/hooks/src/engine/output_parser.rs`, `events/{session_start,user_prompt_submit,stop}.rs` |
| Codex MCP TOML schema | `codex-rs/config/src/mcp_types.rs` |
| Codex project config layer path | `codex-rs/config/src/config_layer_source.rs`, `config/src/loader/mod.rs:1136` |
| Codex `exec` flags + headless defaults | `codex-rs/exec/src/lib.rs:413` (approval `never`), `codex-rs/exec/tests/suite/hooks.rs` |
| Codex session transcripts | `codex-rs/rollout/src/lib.rs:68` (`SESSIONS_SUBDIR`) |
| Hermes: everything below | `github.com/NousResearch/hermes-agent` @ `f6c9cb7` (cloned) |
| Hermes context-file chain | `website/docs/user-guide/which-file-does-what.md` |
| Hermes skills + `external_dirs` | `website/docs/user-guide/features/skills.md` |
| Hermes shell hooks + per-event returns | `website/docs/user-guide/features/hooks.md` |
| Hermes MCP config keys | `website/docs/reference/mcp-config-reference.md` |
| Hermes session storage (SQLite) | `website/docs/user-guide/sessions.md` |
| Hermes providers / base URL | `website/docs/user-guide/configuring-models.md` |
| Hermes tool names | `website/docs/reference/tools-reference.md` |
| Hermes headless one-shot (`-z`) | `website/docs/reference/cli-reference.md` |
| GitNexus banner rewriter | `gitnexus@1.6.10`, `dist/cli/ai-context.js:250-254` |
| OmniRoute gateway | `github.com/pitbaden/omniroute` |

---

## 2. What is NOT identical

An honest list. Each gap is structural — it cannot be closed by editing a config file.

| Gap | Why it exists | Mitigation |
|---|---|---|
| **No Workflow runtime** | Claude Code's `Workflow` API (`agent()/parallel()/pipeline()`) has no equivalent on Codex or Hermes. `premortem-roast.js` was the only workflow. | Ported as a skill-shaped PROCEDURE (`.agents/skills/premortem-roast/SKILL.md`) — same stages, run as sequential `codex exec` or `hermes -z` calls via the spawn path. |
| **Model routing collapses** | Claude Code routes by tier (Fable/Opus/Sonnet/Haiku). Neither PC harness has multi-tier routing. | All roles run on a single model. The routing table in CLAUDE.md is removed from AGENTS.md/.hermes.md and replaced by a note: "one model; hand verification back to the sandbox." |
| **Hook gaps on Hermes** | See [§4 NO-HOOK list](#no-hook-list--rules-that-ride-on-the-agent-not-the-harness). `post_tool_call` and `on_session_start` are observers (return discarded); `pre_tool_call` is block-only (no advisory). | Standing instructions in `.hermes.md` replace the missing hooks. The edit-snapshot gap is partially closed by a spool mechanism (J). |
| **Permission model differs** | Claude Code: `settings.json` allow-lists + prompt. Codex: `config.toml` `sandbox` + `approval_policy`. Hermes: `--yolo` / per-tool. | Mapped where possible (Codex sandbox=workspace-write, approval=auto-edit in interactive / never in exec). No-equivalents listed in [§9](#no-equivalent-list). |
| **No SubagentStart hook** | Neither harness has a dispatch-time injection point. Honey mode injection does not apply. | Honey mode is a prose style, not a mechanism — the role body carries it. |
| **No task DB** | The in-session task database (TaskCreate/TaskUpdate) does not exist. | The ledger (`todo/BUILD-TASKLIST.md` + `tasks/*.md`) is the tracker, edited by hand. |
| **Transcript format differs** | Codex: `~/.codex/sessions/*.jsonl`. Hermes: SQLite `~/.hermes/state.db`. Neither matches Claude Code's `.jsonl`. | Session-continuity skill reworded per harness. |

---

## 3. Instructions files — placement and why

### Codex reads `AGENTS.md`

Codex concatenates `AGENTS.md` from the git root down to the cwd, joining with blank lines;
files closer to the cwd override earlier guidance because they appear later. `AGENTS.override.md`
beats `AGENTS.md` at any level. The budget is **32 KiB** (`project_doc_max_bytes`), and Codex
stops adding files once combined size reaches it.

`AGENTS.md` is **~24.5 KiB** with the port — comfortably inside the budget, but the headroom is
finite, and the GitNexus banner grows it a little on each reindex. If it approaches 32 KiB, move
detail into a skill rather than into this file. Check with `wc -c AGENTS.md`.

**The GitNexus banner co-exists safely.** `AGENTS.md` already carried a machine-regenerated
GitNexus block between `gitnexus:start` / `gitnexus:end` markers. The rewriter
(`ai-context.js:250-254`) computes `before = content[0..startIdx]` and
`after = content[endIdx+len..]` and writes `before + newBlock + after` — everything outside the
marked span is re-emitted verbatim. The port is written **above** the block.

Confirmed empirically: the post-commit hook ran `gitnexus analyze` during this work, the banner's
symbol counts were rewritten, and the ported content above it survived untouched.

### Hermes reads `.hermes.md`

Hermes loads **exactly one** project context file per session, first match wins:

    .hermes.md  ->  AGENTS.md  ->  CLAUDE.md  ->  .cursorrules

Had we shipped only `AGENTS.md`, Hermes would have loaded the **Codex-worded** file and been told
about `apply_patch`, `spawn_agent`, and Codex hook events — none of which exist for it. Writing
`.hermes.md` gives each harness a file written for the tools it actually has.

### Rewording in the instructions files

| File | Reworded | Why |
|---|---|---|
| `AGENTS.md`, `.hermes.md` | the source repo's "ignore an injected branch directive" sentence → DROPPED | Here the development branch IS the session's designated branch, so a directive to push elsewhere is the owner's next session, not an attack; the rule that survives is "never another branch without the owner's say-so". |
| both | MANAGER CHARTER: the source repo's proposal ids (`#23`, `#25`) → removed; PC environment facts block ADDED (OmniRoute `:20128` sole egress, never stop the owner's services, sudo, untracked bridge env) | A PC-side manager needs the safety facts the Environment section carries in `CLAUDE.md`. |
| both | model-routing table → removed; replaced by "one model, hand verification back" | Neither harness can route to a tier. |
| both | `TaskCreate` → "the task ledger (`todo/BUILD-TASKLIST.md` + `tasks/*.md`)" | No task DB on either harness. |
| both | output styles → a prose-style rule stated inline | No output-style mechanism on either harness. |
| both | `AskUserQuestion` → "ask in plain text and wait" | No interactive question tool. |
| both | `SubagentStart` honey injection → dropped | No subagent dispatch to inject into. |
| `AGENTS.md` | tool names → `apply_patch` / `Bash` / `spawn_agent` | Codex's actual names. |
| `.hermes.md` | tool names → `patch` / `write_file` / `search_files` / `terminal` | Hermes's actual names. |

**Kept verbatim and machine-checked byte-for-byte:** the 15 **STANDING PROJECT RULES** (the planning
repo's own agent rules, originally this file's whole content). The numbered lines under that heading
hash identically in `CLAUDE.md`, `AGENTS.md` and `.hermes.md` (`sed -n '/^### STANDING PROJECT RULES/,/^###\|^## /{ /^[0-9]\+\. /p }' <file> | md5sum`).
They are not paraphrased or summarised anywhere in this port.

Also kept intact: the **NO STUBS** block, the **GROUND TRUTH** reading order, the project
description.

**Added to both:** the MANAGER CHARTER — duties and the five hard limits: never in the gate
spine, never a verdict on a gate, all code through `contract-gate` plus the sandbox adversarial
verify lane, only `claude/soundbox-kit-migration-iz1jwf` via `scripts/push_clean.sh`, no outward-facing actions.

---

## 4. Skills — one copy, both harnesses

**Location: `.agents/skills/<name>/SKILL.md`.** 382 skills total (49 MB, 2986 files).

- **Codex** discovers: `$CWD/.agents/skills`, parent folders, `$REPO_ROOT/.agents/skills`,
  `$HOME/.agents/skills`, `/etc/codex/skills`, then bundled skills.
  Source: <https://learn.chatgpt.com/docs/build-skills>.
- **Hermes** reads `~/.hermes/skills/` as primary, plus any directory under
  `skills.external_dirs` in `~/.hermes/config.yaml`.
  Source: `website/docs/user-guide/features/skills.md`.

Both consume the same `SKILL.md` with `name` / `description` YAML frontmatter, so **one ported
copy serves both** — placed once, at `.agents/skills/`.

### Scope — 14 hand-ported, 6 tool-managed, 362 vendored verbatim (THIS repo)

**14 project-authored skills** carry HARNESS PORT rewordings in `.agents/skills/` — each has a
`> **HARNESS PORT.**` note and mechanism-name substitutions for Codex/Hermes. The 14 names
(listed in `harness-ports/hand-ported.txt`, base hashes in `harness-ports/hand-ported.sha256`):

`adversarial-review` · `anti-hollow-green` · `bug-echo` · `build-loop` · `code-intel-trio` ·
`contract-gate` · `deep-work` · `empirical-validation` · `luck` · `orchestration` ·
`root-cause-debugging` · `session-continuity` · `thermo-nuclear-review` · `trace-the-chain`

The sync script (`harness-ports/bin/sync-skills.sh`) recognizes these as intentional drift and
never overwrites them on a plain run; `--check` reports them as `INTENTIONAL` (exit 0) when the
`.claude` twin's hash matches the recorded base, or `STALE-BASE` (exit 1) when it has changed
since the port.

**Tool-managed (6)** — `gitnexus-cli` · `gitnexus-debugging` · `gitnexus-exploring` ·
`gitnexus-guide` · `gitnexus-impact-analysis` · `gitnexus-refactoring`

GitNexus mirrors these into `.agents/skills/` whenever an `.agents/` directory exists
(`gitnexus@1.6.10`, `dist/cli/ai-context.js:309-332`). It **overwrites on every `analyze`**.
Never hand-edit them — any edit is lost at the next reindex.

**Vendored (362)** — the third-party skill library, copied VERBATIM. Lines inside vendored
skills that name Claude-Code-only mechanisms (Task/Agent tool, /slash commands, hooks) are left
as-is and mapped through the mechanism table in `AGENTS.md` — one table, not 362 edits.

### Skill invocation mapping

Both harnesses invoke skills by name. Codex uses `@skill-name` in the prompt; Hermes uses
`#skill-name` or loads skills automatically by keyword match. Slash-command-shaped skills
(`/council`, `/wiki-*`, `/bug-echo`, `/contract-gate`, `/luck`, etc.) are reachable on both
harnesses by their skill name without the leading `/`.

### Rewording in the hand-ported skills

42 body reword sites across the 14 hand-ported skills. Two carry semantic changes beyond
mechanism renaming: `contract-gate` — builder and evaluator in separate contexts, a single-model
harness hands step 3 back to the sandbox lane; `orchestration` SUCCESSION — reframed as the
operating mode. Trading-system-specific live paths/branches/env names were re-pointed to this
repo during the port (war stories referencing the source repo by name are left as evidence).

---

## 5. Hooks

Both harnesses have a real hook surface, so **all five project hooks are ported** — but Hermes
cannot carry all five with full effect.

**No hook logic is duplicated.** Both harnesses invoke the same `.claude/hooks/*` scripts
through `harness-ports/bin/`.

### Mapping

| Project hook | Codex event | Hermes event | Effect on Hermes |
|---|---|---|---|
| `session-start.sh` | `SessionStart` | `on_session_start` | **Side effects only** — observer, return discarded |
| `wiki-context.py` | `UserPromptSubmit` | `pre_llm_call` | Full equivalent |
| `edit-snapshot.py` | `PostToolUse` (matcher `Write\|Edit`) | `post_tool_call` | Spool mechanism (see below) |
| `turn-retro-gate.sh` | `Stop` | `pre_verify` | **Partial** — edited-code verify gate only |
| `graft-first-nag.py` | `PreToolUse` (matcher `Bash`) | `pre_tool_call` | **NOT WIRED** — would become a hard block |

### Hermes edit-snapshot spool (deliverable J)

Hermes's `post_tool_call` discards the return, so the blast radius and anti-pattern screen from
`edit-snapshot.py` would never reach the model. The spool mechanism writes each snapshot to
`$AF_REPO/.hermes-spool/` and a `pre_llm_call` reader (`hermes-spool-reader.py`) drains
the spool into the next `{"context": ...}` injection, delivering the output one turn late. This
is an honest gap: the snapshot arrives AFTER the edit, not during it; a Claude Code hook delivers
it immediately.

### NO-HOOK list — rules that ride on the agent, not the harness

Restated inside `.hermes.md` so the agent sees them even without this document.

1. **`edit-snapshot.py` on Hermes — SPOOL (one turn late).** The spool mechanism delivers the
   output, but delayed. **Standing instruction:** run `scripts/why.sh <file> [function]` and
   GitNexus `impact` before editing a symbol.
2. **`graft-first-nag.py` on Hermes — NO HOOK by default.** A commented-out config line exists;
   enabling it converts the advisory warning into a hard block. Owner's call.
3. **`turn-retro-gate.sh` on Hermes — PARTIAL.** `pre_verify` fires only at the edited-code
   verify gate, not on every turn end.
4. **`session-start.sh` context injection on Hermes — NO HOOK.** Observer event; live-state
   injected through `pre_llm_call` instead.
5. **`SubagentStart` honey injection — no equivalent on either harness.**
6. **No task-DB sync hook on either harness.** Edit the ledger by hand.

### Adapter details

Both harnesses match Claude Code's hook wire protocol (JSON on stdin, non-JSON stdout = injected
context, exit 2 + stderr = block). But payloads and return contracts differ:

- **`codex-hook-adapter.py`** — splits Codex's `apply_patch` envelope into per-file
  `edit-snapshot.py` calls. Parses `rg`/`grep` shell commands back to Grep-shaped payloads for
  the graft nag.
- **`hermes-hook-adapter.py`** — maps Hermes's per-event return contracts (`pre_llm_call` →
  `{"context": ...}`, `pre_verify` → `{"decision":"block","reason":...}`). On observer events
  it emits nothing and logs to stderr.

Tests: `test_codex_hook_adapter.py` (7), `test_hermes_hook_adapter.py` (6),
`test_hermes_spool.py` (9). Every positive paired with a negative control.

### Git hooks are harness-independent

`scripts/hooks/post-commit` and `scripts/hooks/pre-push` run under git, not any harness. They
need `core.hooksPath` set:

    git config core.hooksPath scripts/hooks

`scripts/setup.sh` does this in the sandbox. **The PC clone needs it set once, by hand.**

---

## 6. MCP servers

All seven are ported (vectorbtpro removed -- not applicable to agent-factory).
**No PC path is committed.** The two harnesses differ:

- **Codex** launches through `harness-ports/bin/mcp-server.sh`, which resolves `AF_REPO`,
  `AF_VENV`, and per-server binary overrides with non-root defaults.
- **Hermes** expands `${VAR}` inline in its config snippet.

The launcher **fails loud**: unknown name or missing binary = non-zero exit with a message.

### aleph and the mcp version pin

aleph IS installed in the sandbox venv by `scripts/setup.sh` (editable from `sandbox-kit/aleph[mcp]`,
MCP server connected at user scope, verified 2026-09-03). aleph's MCP server imports `mcp.server.fastmcp`, which `mcp>=2.0` removed (the module was renamed to
`mcp.server.lowlevel`). The project venv pins `mcp==1.29.1` and installs aleph editable from
`sandbox-kit/aleph[mcp]`.

**The PC venv must do the same:**

```bash
cd $AF_REPO
pip install "mcp==1.29.1"                    # pin BEFORE installing aleph
pip install -e "sandbox-kit/aleph[mcp]"      # editable so updates land instantly
```

If the PC venv already has `mcp>=2`, installing aleph's `[mcp]` extra will pull `mcp>=1.0.0`
which pip may resolve to 2.x — pin first.

### MCP smoke procedure

Run the acceptance probe on the PC:

    bash harness-ports/bin/mcp-smoke.sh              # every server
    bash harness-ports/bin/mcp-smoke.sh gitnexus     # just one

It speaks raw MCP over stdio (`initialize`, then `tools/list`) with no harness involved.

---

## 7. The spawn path

The point of the whole port. Two scripts:

### PC-side: `harness-ports/bin/pc-lane.sh`

    harness-ports/bin/pc-lane.sh <brief-file> [codex|hermes] [role]

Runs ONE build/verify lane on the PC. Takes a brief, runs the harness non-interactively in its
own git worktree, and leaves the final message in `report.md`.

**How it works:**

1. **SHA pin.** The brief must contain a line like `PIN: <sha>`. No pin = refused. A lane on an
   unpinned tree produces confident wrong work.
2. **Worktree.** `git worktree add` under `$AF_REPO/.lanes/<lane-id>` (disjoint per lane,
   same pattern as the sandbox's agent worktrees).
3. **Role prepend.** If a role is named, `harness-ports/roles/<role>.md` is prepended to the
   brief before the harness sees it.
4. **Non-interactive run.**
   - **Codex:** `codex exec --cd <tree> --output-last-message report.md --skip-git-repo-check --dangerously-bypass-hook-trust --sandbox workspace-write - < prompt.md`
     Approval defaults to `never` in headless mode (`exec/src/lib.rs:413`).
     `--dangerously-bypass-hook-trust` is REQUIRED for ported hooks to run without interactive
     trust granting (proven by `codex-rs/exec/tests/suite/hooks.rs`).
   - **Hermes:** `hermes -z "<prompt>" --usage-file usage.json > report.md`
     `-z` is the purest one-shot: single prompt in, final response out.
5. **Report capture.** The harness's final message → `.lanes/<lane-id>/report.md`.
6. **Exit code passthrough.** The lane exits with the harness's exit code.

**Hard limits, enforced not just documented:**

- **Never pushes.** A `git` shim on PATH refuses `push`, `remote add`, `remote set-url`.
- **Never opens PRs or posts comments.** A `gh` shim refuses `pr`, `release`, `issue`, `api`.
- **Never issues a gate verdict.** Rule lives in the role bodies and project instructions.

**Replay safety** (per `docs/PC-BRIDGE-RUNBOOK.md`): if `report.md` already exists, the lane
re-prints it without re-running. If the pidfile names a live process, the lane exits without
starting a second one. Keyed on the STATE it intends to create, not on mutual exclusion.

**Environment variables (all overridable):**

| Variable | Default | Purpose |
|---|---|---|
| `AF_REPO` | `$HOME/agent-factory` | repo clone |
| `AF_VENV` | `$HOME/venv-agent-factory` | python venv root |
| `CODEX_BIN` | `codex` (from PATH) | codex binary |
| `HERMES_BIN` | `hermes` (from PATH) | hermes binary |
| `LANE_BRANCH` | `claude/soundbox-kit-migration-iz1jwf` | branch to fetch |
| `LANE_ID` | derived from the brief | lane directory name |

### Sandbox-side: `scripts/pc_lane.sh`

    scripts/pc_lane.sh <brief-file> [codex|hermes] [role]

Ships the brief to the PC over the bridge, launches the PC-side run **detached** (setsid +
pidfile), and polls for the report with short bridge probes.

**Bridge rules obeyed** (all from `docs/PC-BRIDGE-RUNBOOK.md`):

- Calls cap at ~120s — the PC run is detached, and this script polls locally.
- Replay-idempotent — a timed-out bridge call replayed is a no-op, not a second lane.
- Token via `curl --config stdin`, never in argv or on disk.

**Environment:** `PC_BRIDGE_URL`, `PC_BRIDGE_TOKEN` (from env ONLY), `POLL_SECONDS` (default
15), `MAX_POLLS` (default 240 = 60 min).

### Owner-run smoke (one real brief per harness)

Before relying on either harness, run one read-only task on the PC:

**Task (identical for both):**

> Summarize `wiki/topics/live-state.md` and list the pending tasks in the ledger. Do not change
> any file.
>
> PIN: <current tip of claude/soundbox-kit-migration-iz1jwf>

Run it as:

    # Codex
    harness-ports/bin/pc-lane.sh /path/to/smoke-brief.md codex

    # Hermes
    harness-ports/bin/pc-lane.sh /path/to/smoke-brief.md hermes

**Check the report for all four:**

| # | Check | Pass looks like |
|---|---|---|
| 1 | **Skills loaded** | Ask "which skills do you have?" — the ported names appear (`build-loop`, `deep-work`, `contract-gate`, etc.). |
| 2 | **Branch rule** | Ask "which branch may you push to, and how?" — must answer `claude/soundbox-kit-migration-iz1jwf` only, via `scripts/push_clean.sh`. |
| 3 | **No-stub rule** | Ask "the ledger file is missing — what do you do?" — must surface the blocker and refuse to invent content. |
| 4 | **Never-gate-spine** | Ask "can you tell me whether the PBO gate passed?" — must decline to issue a gate verdict. |

Also confirm, once, on the PC clone:

    git config core.hooksPath        # must print: scripts/hooks
    bash harness-ports/bin/mcp-smoke.sh

---

## 8. UNVERIFIED

Everything here is either unconfirmable from primary sources or unrunnable from the sandbox.
Nothing in this list should be treated as working until checked on the PC.

**Not run at all**
1. **Neither harness has been run against this repo.** No session, no smoke, no verification that
   `AGENTS.md` or `.hermes.md` is actually loaded. Section 7's owner-run smoke is the missing proof.
2. **No MCP server was smoked on the PC.** The sandbox probe proves the probe works; it says
   nothing about the PC's servers.
3. **The Hermes config snippet has never been loaded by a running Hermes.** It parses as YAML and
   every repo script it references exists — that is all.
4. **Codex hook execution was never observed.** The adapters were tested by invoking them
   directly with shaped payloads; Codex itself never ran them.
5. **The spawn path (`pc-lane.sh`) was tested against a fake harness only.** The plumbing
   (worktree, SHA pin, role prepend, report capture, replay guard, push refusal) is proven. Whether
   `codex exec` or `hermes -z` actually produces a useful lane is UNVERIFIED. The test is labeled
   as a test double and is the one permitted stand-in.
6. **Codex `exec` hook firing in non-interactive mode.** The
   `--dangerously-bypass-hook-trust` flag should enable hooks without interactive trust granting
   (upstream test `codex-rs/exec/tests/suite/hooks.rs` uses it). Unconfirmed on this repo.

**Could not be confirmed from primary source**
7. **Codex nested skill directories.** The filesystem walk sits behind a trait whose
   implementation is not in the public crate. Moot in practice: all ported skills are flat.
8. **Codex `config.toml` full reference.** `developers.openai.com/codex/config-reference` was
   unreachable (404). The schema was read from the Rust structs.
9. ~~What is actually listening on the OmniRoute port~~ — RESOLVED 2026-09-03: OmniRoute is on
   `:20128` (spike #0, `spikes/pc-bridge/result.json`, probed live over the bridge); `:8317` was
   the source repo's Hermes port and does not apply here.

**Product identification — RESOLVED**
10. **The gateway is OmniRoute** (`github.com/pitbaden/omniroute`). Owner correction 2026-09-01.
    The Hermes provider block is commented out — the owner supplies live values on the PC.
11. **Hermes identification is solid.** NousResearch hermes-agent, corroborated three ways.

---

## 9. No-equivalent list

Settings from `.claude/settings.json` that have no mapping on either harness:

| Setting | Codex | Hermes |
|---|---|---|
| `hooks[].matcher` regex | Codex matchers are glob-based (`tool_name`), not regex | Hermes has per-event hooks, not per-tool |
| `allow` tool allowlists (per-project) | `approval_policy` in `config.toml` (coarser) | `--yolo` or per-tool config (coarser) |
| `deny` tool blocklists | Not supported | Not supported |
| Output style switching | Not supported | Not supported |
| SubagentStart hook injection | No subagent dispatch mechanism | No subagent dispatch mechanism |
| TaskCreate / TaskUpdate API | No task DB | No task DB |

---

## 10. Keeping the ports in sync

The rules now live in three places: `CLAUDE.md`, `AGENTS.md`, `.hermes.md`. That is a drift risk
and there is **no mechanical check** for it.

When a rule changes:
1. Change `CLAUDE.md` (the source of truth).
2. Mirror it into `AGENTS.md` and `.hermes.md`, keeping each harness's mechanism names.
3. If it touched a skill, edit `.claude/skills/` and re-run `bash harness-ports/bin/sync-skills.sh`
   (the pre-commit SKILL-SYNC GATE blocks a `.claude/skills/` commit whose `.agents/skills/` twin
   is stale). If it touched a `gitnexus-*` skill, **stop**: those 6 are tool-managed and
   regenerated by `analyze`.
4. If the STANDING PROJECT RULES ever change, re-run the md5 check in section 3 — the three
   files must hash identically.

### Skill sync — 382 skills (14 hand-ported, 362 verbatim, 6 tool-managed)

After any change to `.claude/skills/` (new skill, vendored update, skill removal):

    bash harness-ports/bin/sync-skills.sh              # copy + report (never overwrites allowlisted dirs)
    bash harness-ports/bin/sync-skills.sh --check      # report only, exit 1 on drift/stale-base
    bash harness-ports/bin/sync-skills.sh --record     # refresh base hashes for hand-ported skills

The script copies every non-allowlisted skill dir from `.claude/skills/` to `.agents/skills/`,
excluding the empty `gitnexus` parent dir. Hand-ported skills listed in
`harness-ports/hand-ported.txt` are NEVER overwritten by a plain run; their drift is classified
by comparing the `.claude` twin's sha256 against the recorded base hash in
`harness-ports/hand-ported.sha256`. Reports:

- **NEW** — dirs in source but not destination (copied on run, reported on --check)
- **STALE** — dirs in destination but not source (reported, NOT deleted)
- **DRIFT** — non-allowlisted dirs where content differs (copied on run, exit 1 on --check)
- **INTENTIONAL** — hand-ported dirs whose `.claude` twin matches the recorded base hash
  (expected drift, exit 0 on --check)
- **STALE-BASE** — hand-ported dirs whose `.claude` twin changed since the port (exit 1 on
  --check; re-port via 3-way merge, then `--record` to update the base hash)

The pre-commit SKILL-SYNC GATE (`scripts/hooks/pre-commit`) calls `sync-skills.sh --check` and
blocks on exit 1. A clean check reports 14 INTENTIONAL lines and exit 0.

Test: `harness-ports/tests/test_sync_skills.sh` (19 checks).

### Instructions-file drift check

    diff <(sed -n '/^## /,$p' AGENTS.md) <(sed -n '/^## /,$p' .hermes.md)

The differences should only be mechanism names.

---

## 11. PC install steps

### Prerequisites

- Codex CLI installed (`codex` on PATH)
- Hermes Agent installed (`hermes` on PATH)
- OmniRoute running on `:20128` (verified live 2026-09-03 — the model egress for Hermes; the
  routed model id is whatever OmniRoute exposes, no vLLM dependency)
- Python 3.11+ with a venv at `$HOME/venv-agent-factory` (or set `AF_VENV`)

### First-time setup

```bash
# 1. Clone and configure
cd $HOME/agent-factory                      # or wherever the clone lives
git config core.hooksPath scripts/hooks      # enable post-commit + pre-push hooks

# 2. Python dependencies — the mcp pin is load-bearing
$HOME/venv-agent-factory/bin/pip install "mcp==1.29.1"
$HOME/venv-agent-factory/bin/pip install -e "sandbox-kit/aleph[mcp]"

# 3. Skills sync (49 MB, 2986 files under .agents/skills/)
bash harness-ports/bin/sync-skills.sh

# 4. Roles (already committed, but verify)
python3 harness-ports/bin/build-roles.py --check

# 5. MCP servers — smoke every one
bash harness-ports/bin/mcp-smoke.sh

# 6. Hermes config — merge the snippet into ~/.hermes/config.yaml
#    Set skills.external_dirs to include $AF_REPO/.agents/skills
#    Set the OmniRoute provider block (uncomment, fill in live values)

# 7. Codex config — .codex/config.toml is committed; verify hooks fire
#    codex exec --dangerously-bypass-hook-trust --sandbox workspace-write \
#      "echo hello" 2>&1 | grep -i hook
```

### Environment variables for pc-lane.sh

Export these (or set in a shell profile):

```bash
export AF_REPO="$HOME/agent-factory"
export AF_VENV="$HOME/venv-agent-factory"
export CODEX_BIN="codex"                      # or full path
export HERMES_BIN="hermes"                    # or full path
```

### Size budget

| Item | Size |
|---|---|
| `.agents/skills/` | 49 MB, 2986 files, 382 dirs |
| `harness-ports/roles/` | 3 files, ~2 KB each |
| `harness-ports/bin/` | 8 scripts |
| `.codex/config.toml` | ~3 KB |
| `AGENTS.md` | ~24.5 KB (under 32 KB budget) |
| `.hermes.md` | ~22.7 KB |
