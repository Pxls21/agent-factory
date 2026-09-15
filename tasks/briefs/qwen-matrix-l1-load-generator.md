# Lane QM1 — the L1 concurrency-matrix runner for the local Qwen3.8-27B server: a replay load generator + a per-cell server runner, with the measurement lines the digest needs (build lane: PC Hermes `code-implementer` on the CLOUD build route)

**STATUS 2026-09-15 12:21Z: lane QM1 came home BLOCKED, correctly — three premises below were false (the launcher has no cell knobs, its guard is inline and runs AFTER the unit write, `/props` carries no cell flags; `tasks/briefs/qwen-matrix-support/QM1-report.md`). AMENDMENT 1 (12:3xZ): the launcher prerequisite is lane QM0 (`tasks/briefs/qwen-server-qm0-cell-knobs-and-guard-before-write.md`): the six knobs `QWEN_CACHE_RAM`, `QWEN_CTXCP`, `QWEN_CMS`, `QWEN_UBATCH`, `QWEN_SPEC_P_MIN`, `QWEN_SPEC_TYPE` and the side-effect-free `qwen-server.sh guard` (rc 7 = a LOCAL-route lane is alive; cloud lanes never block). QM1-b re-runs on QM0's landing with these changes to items 2-3: the per-cell runner sets the cell through those knobs and calls `guard` before any restart (never its own census); the cell record binds `/props` runtime fields (`model_alias`, `total_slots`, `default_generation_settings.n_ctx`, `build_info`) + the text and sha256 of `qwen-server.sh argv` rendered with the cell's env + the sha256 of `qwen-server.sh unit` — never a flag "read from /props"; the restore is `install` with the baseline env, proven by the unit-text sha returning to the baseline's. Everything else in the brief stands.**

PIN: `efde78d` (re-pinned 2026-09-15 15:1xZ for QM1-b on QM0's landing 8aecbf8; the first run was on `47549c7`)

**Why.** `docs/research/findings/RESEARCH-FINDINGS-1-VERIFIED.md` §4 defines the matrix (cells A–H) that decides the MTP-vs-`-np` fork,
the `--cache-ram` and checkpoint levers, and the q8_0 fit. Nothing runs it yet. Build the two tools; do NOT run the matrix in this lane
(the model unit may not be restarted under a live lane — the coordinator runs the cells when the slot is free).

**Authorization + boundaries.** New files only: `harness-ports/bin/qwen_matrix.py` (the load generator + metrics reader),
`harness-ports/bin/qwen-matrix.sh` (the per-cell runner: builds the cell's server command from `harness-ports/bin/qwen-server.sh`'s
`QWEN_*` env knobs — read that script; it already refuses to restart under a live lane via `QWEN_LANES_DIR` — and never edits the unit
file permanently), `harness-ports/tests/test_qwen_matrix.py`, `harness-ports/tests/test_qwen_matrix_sh.sh` (wired into
`harness-ports/tests/run-all.sh` — append one line, the existing pattern), and the report `tasks/briefs/qwen-matrix-support/QM1-report.md`.
Read-only: everything else. The code-intel pack for the existing server tooling is `tasks/briefs/qwen-matrix-support/QM1-pack.md`.

## Items
1. **The replay corpus builder** (`qwen_matrix.py build-corpus --from <exported session .md> --target-tokens 100000 --out <dir>`): reads a
   Hermes session export (the shape of `~/qwen-builder/ab/n5k-medium-armA.md` — inspect it; the lane tree carries no copy, so read the
   real file on this host, read-only), extracts the system prompt + the first N user/assistant/tool turns until the prompt reaches the
   target token count (count with the server's `/tokenize` endpoint — it is loopback, keyed by `QWEN_KEY_FILE`; never print the key), and
   writes `prompt-<k>.json` files in OpenAI chat shape. Deterministic test: a synthetic export fixture → the expected turn cut and token
   count (the tokenizer mocked by a stub that counts words; the real endpoint used only under `QWEN_MATRIX_LIVE=1`).
2. **The load generator** (`qwen_matrix.py run --prompts <dir> --concurrency N --max-tokens 1000 --rounds R --out <json>`): opens N
   streams at once against `http://127.0.0.1:8080/v1/chat/completions` (stream=false), each round rotating prompts so slots ALTERNATE
   (the prompt-cache test), and records per request: wall time, prompt tokens, completion tokens (from `usage`), and the server's
   `timings` block when present; before/after each round it snapshots `/metrics` (`llamacpp:prompt_tokens_total`,
   `llamacpp:tokens_predicted_total`, `llamacpp:prompt_seconds_total`, `llamacpp:tokens_predicted_seconds_total`,
   `llamacpp:n_busy_slots_per_decode` — read the real names from `/metrics` on this host and pin them in a test fixture) and counts the
   `forcing full prompt re-processing` lines appended to `~/qwen-builder/logs/server.log` during the round (tail from the byte offset
   taken at the start). Output: one JSON with the per-round aggregate decode t/s, prompt t/s, re-prefill count, and a `cell` block with the
   exact server flags read from `/props`. Deterministic tests: the metrics parser on a captured `/metrics` text fixture; the aggregate
   arithmetic on a fixture of timings; a negative control (a metrics page missing a counter → a named failure, never 0).
3. **The per-cell runner** (`qwen-matrix.sh <cell-name> -- <QWEN_* overrides…>`): refuses if any `.lanes/*/lane.pid` is alive (reuse
   `qwen-server.sh`'s guard function, or call its check — do not copy the logic); writes the cell's overrides to
   `~/qwen-builder/matrix/<cell>/env`, restarts the unit through `qwen-server.sh` with those overrides (read how `install` builds
   `ExecStart` and whether a non-persistent restart exists — if `install` is the only path, the runner must restore the baseline unit
   afterwards and the test proves the restore), waits for `/health`, runs `qwen_matrix.py run` with the cell's concurrency, and stores
   the JSON under the cell dir with `nvidia-smi --query-gpu=memory.used` peaks sampled every 5 s. Shell test: a fake `qwen-server.sh` on
   PATH records the calls; the live-lane guard is proven with a fake pidfile (rc 64, the lane named, nothing restarted).
4. **The matrix table** (`qwen_matrix.py table <cell-dirs…>`): prints the §4 table with the cells' numbers and the two decision rules
   evaluated (`>= 1.5x aggregate over A`, `re-prefills < A`). Test: fixture cells → the expected table and verdict lines.
5. **Report** at `tasks/briefs/qwen-matrix-support/QM1-report.md`: file:line for every seam (`qwen-server.sh`'s knobs and guard, the
   `/metrics` names, the `/props` fields, the export format), the pasted test lines (`harness-ports/tests/run-all.sh` → `ALL SUITES
   PASSED`), a dry-run of the runner against the fake server, NOT-done (the live matrix). Lint LAST with
   `python3 scripts/report_lint.py --map S=harness-ports/bin/qwen-server.sh --map M=harness-ports/bin/qwen_matrix.py --min-refs 8`,
   at most THREE rounds, then paste and finish.
6. **Discipline.** Never restart, stop or reinstall the `qwen-builder` unit in this lane (a live lane runs on it); never print the API key;
   kill by pid; scratch under your lane dir; no git writes.
