# Lane QM1 — the L1 concurrency-matrix runner for the local Qwen3.8-27B server: a replay load generator + a per-cell server runner, with the measurement lines the digest needs (build lane: PC Hermes `code-implementer` on the CLOUD build route)

PIN: `47549c7`

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
