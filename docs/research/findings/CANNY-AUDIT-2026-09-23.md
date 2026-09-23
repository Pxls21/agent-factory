# CANNY AUDIT — grounded findings and plan (2026-09-23)

Owner ask (2026-09-22): "https://github.com/qkal/Canny I found this repo aswell that uses jev that we can intergrate" + "Some parrallel with what i requested before".
Sources: the read-only evidence report `docs/research/findings/jev-audit/canny-evidence.md` (qkal/canny at f2c5e53, package `canny-warden` 0.3.0, MIT; 204 cited rows; static reading only, nothing from the clone was run, built or installed), plus the coordinator's own measurements on 2026-09-23 named below. Row numbers such as "E3.24" point into the evidence report.
Status: findings and a recommendation. Nothing is built. The owner decides between the options in §5.

## 1. What Canny is

Canny is a hook layer for Claude Code and Codex CLI sessions (E1.1-E1.17). On every hook event it appends a fact to a per-session JSONL ledger under `~/.canny/sessions/`, and it makes five kinds of decision:

- **The done-gate (Stop):** block the end of a turn when a code file changed and no test, build, lint or type-check command has passed since that edit (E2.1-E2.14). "Passed" means a recognized check command with exit code 0 (E2.6-E2.9).
- **Pattern checks (PreToolUse):** deny a secret written into a file (E2.21-E2.23); ask (Claude) or deny (Codex) before a test is removed or skipped (E1.20); rewrite `check | tail` to run behind `set -o pipefail` so the pipe cannot hide a failure (E1.21, E2.10); deny the fourth run of a command that failed three times with the same output (E2.16-E2.19).
- **Jev judgments (advisory in Canny's own framing):** a per-edit question "does this change break a rule in CLAUDE.md or AGENTS.md" that can only add a note (E3.23), and a Stop question "does this message claim the work is done" that can only turn a done-gate block into an allow (E3.24).
- `canny replay` re-derives the Stop decisions from the ledger and compares the decision kind (E4.10-E4.16).

Its deterministic half is well tested (13 test files, a 90-97 % coverage gate, E8.1-E8.15). Its "Does it help?" numbers have no committed data behind them, and its README says the bench shows no change in outcome yet (E8.25-E8.27). The README and the code disagree in 13 places (evidence §Contradictions); the code is the truth.

## 2. How it meets our rules

| Canny part | Our rule | Finding |
|---|---|---|
| Stop `claims_done` relaxes the done-gate (E3.24) | KC-J1: a Laya value reachable from any gate predicate invalidates the layer (`docs/research/COUNCIL-VERDICT-JEV-LAYA-v1.md:45`) | **Forbidden here.** Pointed at our Laya endpoint, a Laya probability would decide whether a turn-end gate blocks. |
| Jev with the key unset | KC-J1 | "Jev off" is not proven by an unset key: cached answers are returned without a key (E3.9, pinned by its own test), and the cache key excludes the endpoint URL (E3.8, E3.22). Off means a fresh `CANNY_HOME` with an empty `jev/` directory AND no key. |
| Default endpoint `api.typesafe.ai` (E3.1) | Prior audit §7 rule 2: the hosted TypeSafe API is not a production dependency (`docs/research/findings/JEV-LAYA-AUDIT-2026-09-22.md:163-165`) | With a key set and no `CANNY_JEV_URL`, diffs, rules and the final message leave the machine (E7.1, E7.17). |
| Per-edit rule notes (E3.4-E3.5, E3.23) | Advisory use is allowed; D-046 (task #115) proposes the same shape | Latency blocks it on CPU: one request carries up to 24 questions against a ~2-3k-token state, with a 3,000 ms timeout (E3.5, E3.20). Our measured CPU cost is ~1.0-1.25 s per (state, question) pair with no batching gain (`docs/research/findings/JEV-LAYA-AUDIT-2026-09-22.md:133-136`), so such a request fails open. That is an extrapolation; Canny against our endpoint was NOT run (E3.21). |
| Runtime install: `init` writes `.claude/settings.json` hooks that run `node dist/cli.js` on every event (E5.13-E5.15) | The sandbox refuses self-modification of harness settings and the execution of external code without the owner | An install is owner-run. External code would then run on every hook call. |
| Repeat-failure deny (E2.18-E2.19) | Our lanes re-run the same pytest command after every fix | The failure count never resets within a session, so the exact command is denied forever after three identical failures, even after the code is fixed. A footgun for our loops. |
| Done-gate + our Stop hook | `.claude/hooks/turn-retro-gate.sh` already blocks turn-end once per landed batch (E10.8) | Two Stop gates would both fire on the same turn. |
| Deterministic done-gate and pattern checks | Anti-hollow-green: never read a piped rc; never skip a test; AF-AP-39: no secrets in files or argv | **Aligned.** These mechanize rules we hold only in prose and skills today. |

## 3. Measured on our side (2026-09-23)

- **Hermes records exit codes.** A read-only probe of the PC's Hermes `state.db` (the last 400 tool rows) found terminal results shaped `{error, exit_code, output}` in 143 rows and `{cwd, error, exit_code, output}` in 5; `exit_code` values: 0 ×146, 1 ×8, 2 ×2, 124, -1, 6. File edits come back as `{diff, files_modified, lint, resolved_path, success}` (21) and `{bytes_written, dirs_created, files_modified, lint, resolved_path, verified}` (8). The facts a done-gate needs (which files changed, which commands passed) are in Hermes's own tool results. Whether the `post_tool_call` hook payload carries the same fields was NOT checked against the Hermes source.
- **Our hook seams** (quoted from our adapter's docstring, not re-read against the pinned Hermes source, E5.18-E5.21): `pre_verify` fires only after code edits, and its block becomes a continue nudge bounded by `agent.max_verify_nudges` (3), never a hard block. `post_tool_call` is an observer whose return is ignored, and its `--spool` output reaches the model at the next `pre_llm_call`. `pre_tool_call` can block, modify or approve. Our `pre_verify` wiring is commented out for build lanes today (`harness-ports/hermes/config-snippet.yaml:166-178`).
- **Wire compatibility with our endpoint:** Canny's request `{state, model, questions}` with `noul` questions matches `scripts/laya_systemone_server.py`'s accepted shape; our server ignores the bearer token, and Canny sends nothing unless `TYPESAFE_API_KEY` is non-empty (E3.14-E3.19).

## 4. What is worth taking

1. **The verify-command classifier and its tables** (E2.6-E2.10): the rule that a command counts as a passing check only when its exit status cannot be hidden by a pipe, `||`, a background `&` or a non-check first word, plus a 78-pattern check list and its test tables (27 rows, 11 checks × 14 hiding forms, 11 × 13 keeping forms; E8.2). This is the part most likely to prevent a hollow green in our lanes.
2. **The done-gate predicate** (E2.1, E2.4): "code changed since the last passing check" as a pure function over a fact ledger, with a bounded escape (`stop_hook_active` turns the second block into a warning).
3. **The rule-check shape** as a reference design for D-046: rules extracted from the agent files (bullets with never/always/must/do not; E6.6), one question per rule per edit, notes only, fail-open.

Not worth taking: the repeat-failure deny (E2.19), the relax-only Jev branch (KC-J1), the runtime itself.

## 5. Options for the owner

1. **Port the deterministic core as first-party code (recommended).** Two increments, both LLM-free and test-gated, with Canny credited (MIT) in `sandbox-kit/docs/THIRD-PARTY-AGENT-TOOLS.md`:
   - C1 (sandbox tooling lane): `scripts/verify_command.py`, the check classifier, with Canny's tables ported as our tests.
   - C2 (a PC lane): a lane done-gate on Hermes `pre_verify`, fed by `post_tool_call` facts (edits and terminal exit codes) spooled per session, returning the bounded nudge "you changed X after your last passing check". The first step of C2 measures the real `post_tool_call` payload. Then an A/B on lane landings: how many lanes come home with a failing gate, with and without the nudge.
   No Jev anywhere in either.
2. **Install Canny yourself for your own Claude Code sessions, Jev off.** No code from us. External code runs on every hook call, and its Stop gate sits beside our retro gate. I would write the exact install and the Jev-off proof (a fresh `CANNY_HOME`, an empty `jev/`, no key).
3. **Park Canny.** Keep only its rule-check shape as design input for D-046.

Recommendation: option 1, and option 3's design input goes into D-046 either way. The deterministic half is the part that fits our rules, and a lane done-gate targets a failure we already see: lanes that report done while their last edit was never re-checked.

## 6. Not determined

- Canny's runtime behavior (nothing was run), its CI result at f2c5e53, the README's performance numbers (no committed data) (E8.22, E8.25-E8.28).
- The Hermes `post_tool_call` payload fields (the tool results in `state.db` carry `exit_code`; the hook payload was not read).
- Laya's answers and latency for Canny's multi-rule request shape against our endpoint (E3.21).
