# QM1 report — L1 concurrency-matrix runner

## Outcome

BLOCKED — the brief's required per-cell runner cannot be built honestly within its file boundary. This build lane stopped before product edits. It does not issue a gate verdict; sandbox-side adversarial verification still owns any acceptance decision.

## NOT done

- No `qwen_matrix.py`, `qwen-matrix.sh`, matrix tests, or `run-all.sh` wiring was written.
- No live matrix/load run occurred.
- No server stop, restart, reinstall, unit edit, or persistent server-side change occurred.

## Premise audit

- Verified the pinned launcher and history before editing. `qwen-server.sh` defines its process model path and safety inputs through `QWEN_LLAMA_SERVER`, `QWEN_MODEL_GGUF`, `QWEN_KEY_FILE`, and `QWEN_LANES_DIR` (S:22-45). It exposes its argv in `argv()` and builds the systemd unit in `unit()` (S:57-101); `install()` writes the unit before its live-lane refusal and owns the only guarded restart path (S:141-160).
- Verified live read-only server seams. `/metrics` supplies all five required names; `/props` supplies `model_alias`, `total_slots`, `default_generation_settings.n_ctx`, and `build_info`; `/tokenize` returns a `tokens` list. One authorized 64-token completion returned HTTP 200, model `qwen3.8-27b-local`, 59 prompt tokens, 36 completion tokens, and non-empty four-character content.
- Existing deterministic launcher suite: `qwen-server: 45 passed, 0 failed`. Its negative controls pin absent-binary rc 2, absent/mismatched/non-GGUF model rc 3, closed-port `health` rc 1, and unavailable `probe` rc 6 (S:112-130; S:172-184).

## Blocker

The brief requires the new runner to build cells through `qwen-server.sh`'s `QWEN_*` knobs, reuse or call its live-lane guard, and restore the baseline unit if `install` is the only path. The pinned launcher cannot satisfy that contract:

1. Cells B/C/F/H require `--cache-ram`, `-ctxcp`, `-cms`, selectable `--spec-type`, and `-ub`. The live binary supports all of them, but `qwen-server.sh` exposes none of their `QWEN_*` knobs. Its argv ends with fixed MTP flags (S:57-68). Literal capability sweep returned zero occurrences for `QWEN_CACHE_RAM`, `QWEN_CTXCP`, `QWEN_CMS`, `QWEN_SPEC_TYPE`, `QWEN_UBATCH`, and their required flags.
2. There is no reusable guard command/function. `qwen-server.sh guard` returns rc 64. The guard is inline inside `install()` (S:151-157), and it runs only after the candidate unit has already been written, daemon-reloaded, and enabled (S:145-155). Calling `install` under a live lane can therefore mutate persistent unit text before refusing.
3. The brief authorizes only new files plus one `run-all.sh` line. Repairing the real integration requires editing the read-only launcher to expose the missing knobs and a pre-side-effect guard (or approving a new launcher API). Copying/reimplementing the guard or bypassing the launcher would violate the brief and create a hollow safety green.
4. `/props` does not expose the exact cell flags. It contains no cache-RAM, checkpoint, speculation-mode/depth, KV-type, or ubatch fields. Therefore a `cell` block claimed to contain exact flags "read from `/props`" would be false for this live build. Exact argv needs a second authoritative source such as the launcher's rendered argv/unit, explicitly approved by the contract.

This is a blocker. I am NOT going to stub the missing knobs, copy the guard, call `systemctl` around the launcher, or label inferred defaults as `/props` evidence.

## Real options

1. Amend scope so QM1 may make a tested prerequisite edit to `harness-ports/bin/qwen-server.sh`: add the five cell knobs, render optional flags safely, expose a side-effect-free `guard-no-live-lanes` command, and move that check before every persistent write/restart. Then build QM1 against that real seam.
2. Split that launcher prerequisite into a separate increment, independently verify it, then re-dispatch QM1 on the resulting pin.
3. Amend the exact-flags contract: bind each result to both `/props` runtime fields and a saved `qwen-server.sh argv`/unit snapshot, since `/props` alone does not report the required flags.

## Evidence tiers

- VERIFIED this session: source/history seams, live metric names and values, `/props` field absence, `/tokenize` shape, one completion, live-lane census, binary `--help`, and the 45-check launcher suite.
- INFERRED: none used to justify a product change.
- ASSUMED: none. The unresolved launcher/API design belongs to the coordinator.

## Self-attack

1. The missing options might be accepted as raw environment overrides by a hidden launcher path. Ruled out: the only rendered argv path is `argv()` (S:57-68), and each required knob/flag has zero launcher occurrences.
2. `/props` might encode exact flags under an opaque nested field. Ruled out against the live JSON: its top-level/nested runtime settings expose context and slot count, but none of the required cache/checkpoint/speculation/KV/ubatch tokens.
3. A wrapper could source the launcher and call its inline shell function. Ruled out as an honest integration: sourcing executes the launcher's terminal `case` dispatch, the guard is not a function, and copying it is expressly forbidden by the brief.

## Discrepancies

- Brief premise conflict: it says the existing launcher has the matrix's `QWEN_*` knobs and a reusable guard. It has neither.
- Brief contract conflict: exact flags cannot be read from this build's `/props` response.
- `graft` indexed no shell definitions for `qwen-server.sh`; ripwire supplied the shell symbol map. GitNexus's clone index was 93 commits stale and ambiguously resolved `install`; risk remains UNKNOWN rather than low.
- Bug-echo/class sweep for "guard after persistent side effects": a literal sweep of `harness-ports/**/*.sh` found one production instance, this `install()` path; no sibling launcher instance was found. No fix was authorized, so the coordinator must register/repair the class if scope is widened.
- Final report lint: `report_lint: 9 refs — OK 9, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.

## Process census and hygiene

- Three live lane pidfiles were observed, including VERIFY-N5k and this lane. No process was killed, and no persistent/background process was started by QM1.
- `git status` retains the three coordinator-staged brief/pack files plus this untracked report. Product files are untouched.
- API key value was read only into process-local variables and was never printed.

## File identity

- `d059150d3dfdac152450ac58d3260b746deb9c992938466f4a9ae3e1232828ca` — `harness-ports/bin/qwen-server.sh`, 199 lines, unchanged.
- No product-byte identity exists because the premise conflict stopped the build before product edits. The only lane-authored artifact is this report.

## Handoff

Coordinator action required: choose option 1 or 2 and amend the `/props` exact-flags clause before re-dispatch. No proposal bytes exist for an adversarial verifier to grade yet.
