# Project incident log (`agent-factory`)

> Institutional memory: the incidents behind the rules in CLAUDE.md. **Log a one-line entry
> here the moment a CLAUDE.md rule bites for real** — which section/rule it confirms, the
> concrete trigger, the fix — don't defer it to a handoff doc; a lesson recorded only there
> WILL be re-learned the expensive way (deep-work retrospective rule). GENERAL rules distilled
> from an incident still get baked into the matching skill/CLAUDE.md section; this file carries
> the full incident detail. Ported structure from `trading-system/docs/INCIDENT-LOG.md`.

**2026-09-03 — planned against a sandbox-only world while the owner had a PC bridge all along (deep-work Phase-1 "inventory what is already built" bite, at the ENVIRONMENT level):** the findings, the council verdict and the seed classified S0-08/S0-03 as host- and credential-blocked because the sandbox lacks gVisor and a model credential. The owner's environment (`trading-system/docs/PC-BRIDGE-RUNBOOK.md`, left behind by the kit's manifest) already had the PC bridge, the Buzz relay stack, OmniRoute and observability RUNNING. Second form the same hour: vLLM was assumed as the model upstream when OmniRoute — the plan's own egress — was already up. Fix: `PC-BRIDGE.md` + `scripts/pc.sh` + spike #0; plan docs corrected to "OmniRoute's configured providers". Rule distilled: **the environment inventory is a primary source read from the OWNER's live assets (probe the host, read their runbooks) before any venue is classified — a sandbox probe describes the sandbox, not the project.**

**2026-09-03 — GitNexus first index killed by the tool-call timeout (240s) on this 3.8k-file tree ("Terminated", `.gitnexus/run.cjs` absent):** the post-commit hook runs `analyze` in the BACKGROUND for exactly this reason. Fix: `nohup gitnexus analyze` (resume-heal.sh / post-commit), never a foreground call under the Bash cap.

**2026-09-02 — Chairman probe falsified the council's S0-05 mechanism: bare `unshare --net` is TOTAL isolation (a host-local listener returns 200 outside, 000 inside), so a canary written on it would be a vacuous negative control for SELECTIVE egress.** Reproduced by the coordinator before landing. Rule confirmed (anti-hollow-green tactic 1, de-vacuous at write time): a negative control must fail for the mechanism under test and ONLY that mechanism. Registry row AF-AP-1.

**2026-09-02 — seed self-validation red on first run (`ac_564afc416084c18b`): the generated seed referenced the twelve proofs collectively, six ids appearing once.** The gate did its job; fix was the real content (per-proof appendix + the frozen spike mapping), never a rewritten assertion (tactic 4a). Registry row AF-AP-2.

**2026-09-02 — Ouroboros stdio quirks, all reproduced (CLAUDE.md Environment section carries the one-liners):** `IS_SANDBOX=1` required for every backend-driving call (question-less "cannot complete yet" otherwise) · `initial_context` cap (~1.5k) POISONS a session for every later round — start fresh · Synapse fan-out contract (`{key, content}` / `{key, undispatched:true}`, `data_context` exact schema, `question_identity` from `~/.ouroboros/data/fanout/<id>.json`, nothing retained between partial submissions) · shell metacharacters rejected in strings · `generate_seed` writes no file.

**2026-09-02 — Orchestrator rule (e) (commit at every boundary) bit on day one:** three council agents dispatched with the findings doc uncommitted; the container restarted mid-round, killing one agent's in-flight work. The doc survived on the volume by luck; the dead agent's completed round was recovered from its transcript file (`/tmp/claude-0/…/tasks/<agentId>.output`, last assistant text block). Fix: commit+push BEFORE any multi-agent dispatch; recover from transcripts before re-running. Corollary validated the same minute: the SessionStart hook re-provisioned the whole toolchain unattended on the fresh container. Registry row AF-AP-3.

**2026-09-03 — the owner's term "the quartet" was misread as the git-hook set (Phase 0: your own memory lies):** the answer described hooks; the owner meant the four code-intel tools — a section TITLE in the source repo's CLAUDE.md (`## Code-intelligence — the QUARTET`). Rule distilled: **an owner term of art is grepped in the owner's source repo BEFORE it is interpreted** — the source repo is a primary source for vocabulary, not only for code. Second misread the same message: vLLM assumed as a dependency because it was running on the PC; the owner's egress is OmniRoute (already running), vLLM is merely one of its upstreams.

**2026-09-03 — batch A of the setup port shipped `scripts/hooks/post-commit` with a syntax-error tail after its `exit 0`** (the dropped `slopo` block's closing lines survived the deletion). Invisible at runtime — bash parses incrementally and exited first — invisible to review; `bash -n` caught it during batch C. Fix: SHELL SYNTAX GATE in `scripts/hooks/pre-commit` (every staged shell script must parse) + `tests/test_shell_syntax.py` (all committed shell scripts parse; the gate's positive AND negative control run the real hook in a throwaway repo). Registry row AF-AP-5.

## ANTI-PATTERN REGISTRY (owner mandate, inherited from trading-system 2026-08-21)

> The behavioral anti-pattern classes that lead to wrong code in THIS repo. **Every /bug-echo
> run registers its class here** (id, one-line mechanism, greppable signature, proven instance)
> in the same increment — this registry IS the sweep corpus for the next echo. Rows whose
> signature is mechanical also extend `.claude/hooks/edit-snapshot.py`'s AP_SCREEN in the same
> increment. Note: that screen ships with the SOURCE repo's inherited signatures (AP-1…AP-70,
> mechanical tells proven there) — this project's own rows start below with the `AF-` prefix.
> Status: SWEPT(date) = clean at that date's HEAD; OPEN = known live sites; UNSWEPT = never swept.

| id | mechanism | greppable signature | proven instance | status |
|---|---|---|---|---|
| AF-AP-1 | total-isolation instrument offered as a selective-egress negative control (the canary fails for a reason other than the gate under test) | `unshare --net` in any S0-05 fixture without a positive-control leg reaching the allowed target | findings §6a (Chairman probe, reproduced) | OPEN until spike #6 lands the veth/proxy design |
| AF-AP-2 | collective reference satisfying a per-item gate by count (ids appear in a list, never as specified items) | seed/registry ids that appear only once in a spec | seed-stage0-v1 first self-validation | SWEPT(2026-09-02) — per-proof appendix |
| AF-AP-3 | uncommitted work at a multi-agent dispatch boundary (container reset vaporizes it) | dispatch with `git status` non-empty | council session 2026-09-02 | SWEPT(2026-09-02) — commit-before-dispatch |
| AF-AP-4 | sandbox-probe-as-world: venue classification from the sandbox alone while the owner's live host holds the capability | any "blocked_host/blocked_credential" label with no PC-bridge probe record | findings v1 §2 + council KC-1/KC-2 | SWEPT(2026-09-03) — spike #0 |
| AF-AP-5 | partial block deletion leaves orphaned lines past a top-level `exit`/`return` — unreachable at runtime, syntactically invalid, invisible to review | `bash -n` failure; any line after a top-level `exit 0` in a hook/script | `scripts/hooks/post-commit` after batch A (2026-09-03) | SWEPT(2026-09-03) — `tests/test_shell_syntax.py` over every committed shell script; mechanical enforcement = the pre-commit gate (a shell signature, so not an edit-snapshot AP_SCREEN row) |
