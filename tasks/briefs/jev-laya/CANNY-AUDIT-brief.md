# CANNY-AUDIT — read-only evidence audit of qkal/canny @ f2c5e53 (owner ask 2026-09-23 00:0xZ)

Owner: "https://github.com/qkal/Canny — I found this repo as well that uses jev that we can integrate … in parallel with
what I requested before" (the 2026-09-22 Jev/Laya integration audit, `docs/research/findings/JEV-LAYA-AUDIT-2026-09-22.md`).

ROLE: evidence-gatherer (the EXPLORE lane). Collect evidence; do NOT conclude, recommend or rank — the coordinator
writes the verdict (Reflection Firewall).
SOURCE: `/home/user/qkal/canny` — a shallow read-only clone. HEAD `f2c5e53779445d60dc4a09d2dbced2308fccb820`
(2026-09-23 01:23:49 +0200, "chore(release): 0.3.0 (#21)"); MIT; package `canny-warden` 0.3.0; node >= 22; 2,039 lines
of TypeScript under `src/` (checks, cli, config, events, hook, install, jev, ledger, rules).
SAFETY (non-negotiable): STATIC READING ONLY. Never run, build, install or import anything from the clone — no
pnpm/npm/npx/node/tsc/vitest, no `bash test/smoke.sh`, no `.githooks/*`, no `bench/run.mjs`; never run `git config`
inside it (its `prepare` script sets `core.hooksPath`). No network calls. Write ONLY the deliverable below; touch no
other file in `/home/user/agent-factory` (the coordinator has uncommitted work there). No commits, pushes or outward
actions. Never print a credential value (name env vars only).
DELIVERABLE: `/home/user/agent-factory/docs/research/findings/jev-audit/canny-evidence.md` — evidence tables with
`canny/<path>:<line>` citations (paths relative to the clone root) and `af/<path>:<line>` for this repo, in the format of
the sibling files (read `jev-pruner-evidence.md` and `fast-jev-compaction-evidence.md` in that directory first).

## Questions (each answered with cited evidence; "not found" + the exact search you ran is a valid answer)
1. Architecture: each src/ module's role; the data flow from a hook event to a verdict; what BLOCKS vs what only NAGS —
   the README's "What blocks and what only nags" against the code, both cited, any mismatch flagged.
2. The done-gate: the exact predicate that refuses a "done" claim; how "a check" is recognized (test/build/lint/type-check
   classification); what counts as "an edit"; the "same command failed with the same output three times" rule; the
   secret-detection rule (its patterns).
3. The Jev client (`src/jev.ts`): endpoint URL(s), request and response shapes, question types, headers/auth (the key's
   env var NAME only), timeout, retries, caching, fail-open behavior; whether the base URL is configurable (env/config
   key); whether its request contract matches the System One contract our local endpoint serves (read the docstring and
   `_answer` of `af/scripts/laya_systemone_server.py`: `POST {model, state, questions}` -> `{answers: {id: {...}}}`).
   List EVERY place a Jev probability is consumed and show from code whether any of them can block.
4. The ledger: file format, location, write discipline (append-only? atomic? locking?), identity/digests, and the
   `canny replay` determinism claim — exactly what is replayed and compared.
5. Hook protocol: the Claude Code hook events it registers (the JSON read/written, exit codes), the Codex CLI path, the
   README's "four places they differ", and `src/install.ts` (which files it writes, where). Then list, facts only, the
   Hermes hook events our harness already adapts (`af/harness-ports/` — the hook shim, the Hermes hook adapter and its
   test). Do not assess fit; list both sides.
6. Configuration (`src/config.ts`, `src/rules.ts`): the config file schema, the rule format ("never hardcode model IDs"),
   defaults.
7. Egress and side effects: a table of every network call, file write, subprocess, env read and git invocation in src/,
   plus install-time side effects (`prepare`, `.githooks/pre-commit`); any telemetry.
8. Tests, CI and evidence of effect: what each test file covers; the CI workflows; the bench (`bench/run.mjs`,
   `bench/tasks/`) and the README's "Does it help?" numbers — cited, and whether the repo carries the data that produced
   them.
9. `dist/` vs `src/`: is the committed dist/ the build of src/? Read both; list any file whose logic visibly differs.
   Do NOT build.
10. Our side, facts only (cited into af/): the J1 decision-ledger contract (`seeds/seed-laya-j1-v1.yaml`,
    `tasks/laya-j1-breakdown.md`); KC-J1 and the never-a-gate screen (`scripts/no_laya_in_gates.py` docstring); our
    Stop hook (`.claude/hooks/turn-retro-gate.sh` or wherever `settings.json` points); the installed `fast-jev-output`
    and `aegis` plugins (read-only, under `/root/jev-plugins/` or `~/.claude/plugins/`); the prior audit's §7
    (constraints) and §8 (where a System One judgment fits). Quote the lines; do not interpret.

## Final message (<= 40 lines)
The deliverable path and size; the count of cited rows per section; everything you could not determine and why. No
recommendation.
