# PC lane — B8 (S0-02 runner follow-up: the three pre-existing execution defects B7 diagnosed + the four VERIFY-B67 follow-ups, issue #15)

PIN: 889f1cc

Role: code-implementer. Route: the LOCAL build route (`agentfactory-build-local`, the vLLM server default effort). Venue:
`tasks/briefs/pc/VENUE-MAP.md` — read it first. Honey mode: ultra Lever-2 (the report is DATA: files:lines, verbatim counts, NOT-done).

## WHAT YOU CLOSE (issue #15 + B7's report §"real defects found")
Boundary — EXACTLY these three files, nothing else: `R` = `proofs/S0-02/tools/pc/run_s0_02_legs.sh`, `D` = `proofs/S0-02/tools/pc/deliver_event.py`,
`T2` = `tests/test_s0_02_buzz_authz.py`. The live capture is NOT this lane's (three owner decisions pending, issue #11): the runner is
NEVER run past its preflight on this host — no launcher, no relay, no harness server is touched; every behavioral test drives R on a
scratch `S0_02_REPO=<tmp tree>` or sources R's functions with a labelled test double (below).

- **D1 (R:105, `wait_turn_window`)** — `n=$(grep -c '"method":"session/prompt"' "$FD/timeline.jsonl" 2>/dev/null || echo 0)`:
  `grep -c` prints `0` AND exits 1 on a file with no match, so `n` becomes `0<newline>0` and `[ "$n" -ge "$want" ]` errors ("integer
  expression expected") on every poll; the `|| echo 0` was there for `set -e` (R:18). Fix: `n=$(grep -c … "$FD/timeline.jsonl"
  2>/dev/null || true); n=${n:-0}` (absent file → 0; no match → 0; N matches → N) — measured, not assumed: paste the three cases.
- **D2 (R:113-123, `collect_leg`)** — `cp "$FD/buzzacp.log"` runs BEFORE `stop_leg` (R:148/159/169/189/194/199 then R:203) while
  the MASKED `buzzacp.log` is produced by `pc_launch.py` around its exit path (measure: `grep -n 'buzzacp' proofs/S0-01/tools/pc/pc_launch.py`
  at the PIN — cite the write line; the raw log at `:353` is never copied, R:117). Fix: collect `timeline.jsonl` when the leg's turn
  window closes, `stop_leg`, then wait (bounded, failure-aware: `buzz-acp.exit` present = the post step ran) for `buzzacp.log` and copy
  it; keep the 64-hex refusal (R:119-122, rc 7) exactly. If the launcher only writes the masked log AFTER the process exits, say so
  and make the order follow that fact — never a `sleep N` hope.
- **D3 (R:70-84 `launch_leg`, R:102-111)** — stale `$FD/launch.ready` / `$FD/buzz-acp.exit` from a previous run make `launch_leg`
  return 0 before the new launcher is ready, or return 4 / `wait_turn_window` return 6 on a dead-harness reading that is a ghost.
  `pc_launch.py` writes `launch.ready` at `:419` and `buzz-acp.exit` at `:367`/`:423`, `buzz-acp.pid` at `:358`. Fix: `launch_leg`
  removes exactly `$FD/launch.ready`, `$FD/buzz-acp.exit` and `$FD/buzz-acp.pid` BEFORE starting the launcher (files this runner's
  previous run created under the S0-01 launcher's frame dir — cite the launcher lines that recreate them; never `rm -rf $FD`).
- **#15 row 1 (D:84-89, D:194; consumer `proofs/S0-01/tools/nostr_verify.py:230-235`)** — a 64-hex key OUTSIDE the scalar range
  (`0`×64, `f`×64) passes the shape guard and exits 1 with a raw `ValueError("invalid private key")` traceback from `nv.sign_event`
  before any connection. Fix: `_privkey` refuses `int(key,16) == 0 or >= n` with a named `SystemExit` text (add the constant beside
  `REFUSE_TEXT`'s producer; `n` = secp256k1's order — take it from `nv` (`nv.n`), never retype it) BEFORE returning; the shape refusal
  text unchanged.
- **#15 row 2 (D:78, T2:1823, T2:1922-1990)** — B6's normalization is only SOURCE-tested. Add real-CLI cases through `_run_deliver_cli`
  (T2:1901) and the `_OwnedListener` (T2:1848): a PADDED valid throwaway key (`"  <key>\n"`) reaches the listener (count 1, rc 0 or the
  connecting outcome the existing positive control asserts); an UPPERCASE valid key reaches it; a whitespace-only key refuses with the
  exact EMPTY text (`BUZZ_PRIVATE_KEY is not in the environment …`, D:80-83) and count 0; `0`×64 and `f`×64 refuse with the new
  named text and count 0 (the traceback gone). Mutant m4 (drop `.strip()`) must now die at a CLI test.
- **#15 rows 3-4 (R:52-68; T2:1725-1760 `test_pc_runner_preflights_and_selects_the_s0_02_env_set`)** — the preflight pins are SOURCE
  MIRRORS (AF-AP-80): add ONE behavioral test that runs the REAL R with `S0_02_REPO=<scratch tree>` whose `proofs/S0-01/pins.py`
  carries only a COMMENTED exact-values line → rc 3, stdout/stderr contains `BLOCKER: pins.PINNED_ENV_KEYS_S0_02`, and `DEST` is ABSENT
  after the run (the order control); and the positive arm: a scratch pins.py carrying BOTH exact lines passes the preflight and stops at
  the NEXT step in a way that cannot launch anything on this host — measure what R does after `mkdir -p "$DEST"` (R:68) with a scratch
  `S0_02_PINNED` whose launcher path is a labelled STUB script (`pc_launch.py` = a two-line script that writes `launch.ready` and exits
  0, so `launch_leg` returns 0) and `S0_02_RELAY_HTTP` pointing at a closed loopback port; assert `DEST` exists and the run stops at
  `deliver` with its named refusal (no key in the environment) — or, if that chain cannot be made safe within this file set, assert only
  `DEST` created + the preflight passed and STOP the run by `S0_02_TURN_WAIT_S=0` + the stub. Mutants m5 (`grep -Fqx` → `grep -Fq`)
  and m6 (the preflight moved below `mkdir -p`) must die at these BEHAVIORAL asserts, not only at the source pins (keep the pins).
- **The ONE structural change permitted in R:** wrap the leg loop (R:136-206) and the argument/preflight top level in `main()` guarded by
  `if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then main "$@"; fi`, so tests can `source` R's functions with stubbed `FD`/`MARKERS`/`LAUNCHER`
  for D1-D3 unit tests (a labelled test double, never the real launcher). CLI behavior must stay byte-identical: measure the negative
  preflight arm (rc 3, the BLOCKER text, no DEST) BEFORE and AFTER the change and paste both.

## PREMISE — MEASURED at authoring (2026-09-22 08:0xZ, the sandbox clone at 889f1cc); re-measure as item 1
```
sha256 (first 16) at 889f1cc: R c092e8797ee7c42b (206 lines) · D a14c027b0da2f341 (221 lines) · T2 4444842b886ac7de (1991 lines)
git log --oneline 22bd6f5..889f1cc -- proofs/S0-02 tests/test_s0_02_buzz_authz.py   → (empty: the boundary is B7's landing, untouched since)
R seams: set -euo pipefail :18 · DEST :20 · REPO :22 · PINNED/SEC/MARKERS :23-25 · FD=$MARKERS/v2-run-1 :33 · TURN_WAIT_S :34 · POLL_S :35 ·
  MEMBERSHIP :41 · preflight :52-66 (exit 3) · mkdir -p "$DEST" :68 · launch_leg :70-84 · stop_leg :86-100 · wait_turn_window :102-111
  (the grep at :105) · collect_leg :113-123 (cp buzzacp.log :118, the 64-hex refusal :119-122) · deliver :125-130 · role_for :132 ·
  the leg loop :136-203 (collect_leg at :148/:159/:169/:189/:194/:199; stop_leg :203) · the tail :205-206
D seams: _privkey D:71-89 (strip+lower :78, empty refusal :79-83, shape refusal :84-88) · _nip98_header :92 · _post :106 · _normalise :118 ·
  main :165 (leg_dir.mkdir :180 BEFORE _privkey :182) · nv.sign_event at :194
NV: sign_event's key contract nostr_verify.py:230-235 (`re.fullmatch('[0-9a-f]{64}')` → ValueError; `d == 0 or d >= n` → ValueError("invalid private key"))
pc_launch.py: buzz-acp.pid :358-359 · buzz-acp.exit :367 (early death) and :423 (normal exit) · launch.ready :419 · buzzacp.raw.log :353 ·
  the masked log handling around :399-403 (the WRITE line is yours to cite)
T2: REFUSE_TEXT :1838 · _OwnedListener :1848 · _run_deliver_cli :1901 · test_cli_refuses_a_malformed_key_before_any_connection :1922 ·
  _throwaway_secp256k1_key :1949 · test_cli_with_a_valid_key_reaches_the_owned_listener :1961 · the runner tests :1675-1760 ·
  test_real_evidence_root_is_not_a_passing_bundle_today :807
2026-09-22T08:12Z sandbox (no venue var): python3 -m pytest -q tests/test_s0_02_buzz_authz.py → 130 passed, 21 skipped in 56.73s
  (with S0_01_VENUE=sandbox: 1 failed, 150 passed — test_relay_decided_leg_needs_no_debug_canary; INFO item 7 below)
VERIFY-B67 (tasks/briefs/s0-02-support/VERIFY-B67-report.md) on the PC with the PC pair: 151 passed in 11.36s / 151 passed in 11.16s (-n 4)
  and test_summary.sh 151 passed in 40.19s; mutants: m4 drop .strip() → CLI tests green, only T2:1823 red; m5 grep -Fqx→-Fq → only
  T2:1735 red, behavioral preflight wrongly passes (rc 99 safe stop, no DEST); m6 preflight below mkdir → only T2:1731 red, DEST created
B7 report §"real defects found" (tasks/briefs/s0-02-support/B7-report.md:93): the three runner defects, bypassed in a temporary diagnostic
  edit and reverted — never fixed
```

## ITEMS
1. PREMISE (first; stop on failure): re-run the identity/log lines and the two pytest shapes above on your worktree; paste. Reproduce D1
   on a scratch copy of R's function (a timeline file with zero matches → the "integer expression expected" line on stderr) and paste it.
   A mismatch → CONTRACT-INVALID, stop.
2. Red-first, one red test per defect BEFORE the fix (paste each red run): D1 (the zero-match timeline), D2 (collect_leg on an FD whose
   buzzacp.log does not yet exist — today `cp` fails and `set -e` kills the runner), D3 (stale `launch.ready` present → launch_leg returns
   0 without the launcher having run — with the STUB launcher that never writes ready), #15 rows 1-4 as specified.
3. Implement per WHAT YOU CLOSE; every fix minimal; the `main()` wrapper only if a sourced test needs it (say which tests do).
4. Mutants (compile/syntax-checked; on a scratch copy; each killed by a NAMED test or declared): revert each fix one at a time (D1, D2,
   D3, the scalar guard, the collect order); m4/m5/m6 from VERIFY-B67 re-run → now dead at BEHAVIORAL tests (name them).
5. Gates on this host (PC pair `S0_01_VENUE=pc S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden
   S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`, `python -m pytest -n 4 -q --basetemp <your lane dir>/scratch/bt tests/test_s0_02_buzz_authz.py`
   ×2, counts pasted with `date -u`; `bash -n R`; `python3 -m py_compile D`; pyflakes D + T2 0 new; `python3 scripts/ap_screen.py R D`
   (R 0 hits, D — paste; the delta vs the PIN 0 new) and `--tests T2` (11 pre-existing hits at the PIN; 0 new).
6. NEVER on this host: the runner past its preflight against `/home/rocco/agent-factory` (the real REPO/PINNED/relay), the launcher,
   the relay on :3999, the harness containers, `~/s0-01-pinned/.secrets/*` (names only, never read). Scratch and basetemps live under
   YOUR lane directory (`.lanes/<id>/scratch`, on /home), never `/tmp` (AF-AP-112: the PC's tmpfs ran out of inodes this morning).
7. INFO (measure, report, do not fix): `test_relay_decided_leg_needs_no_debug_canary` fails in the sandbox under `S0_01_VENUE=sandbox`
   and passes without the var; run it on this host with the PC pair and say whether it is a venue/corpus mismatch or a real red.
8. Report `tasks/briefs/s0-02-support/B8-report.md`: the identity table before/after, each defect's file:line span + its red-first
   paste, the mutant lines, the gate lines, NOT-done, `report_lint.py` summary with `--map R=proofs/S0-02/tools/pc/run_s0_02_legs.sh
   --map D=proofs/S0-02/tools/pc/deliver_event.py --map T2=tests/test_s0_02_buzz_authz.py --map NV=proofs/S0-01/tools/nostr_verify.py
   --map PL=proofs/S0-01/tools/pc/pc_launch.py --rev 889f1cc` — at most three fix rounds (AF-AP-76).

## VENUE NOTES (this host)
- `/home/rocco/venv-agent-factory/bin` FIRST on PATH; Hermes's `terminal` tool caps ONE call at 420 s — the suite runs in ~12 s with `-n 4`.
- Other lanes (K1-d, E1-R1, T90) and the vLLM `qwen` container share this host: never touch their trees, the container, OmniRoute or any
  server; never `pkill`/`killall` by name; every count PASTED beside `date -u`; every file:line by `sed -n` on the PIN.

**Authorization:** defensive testing of the owner's own capture runner with throwaway keys and stub launchers on the owner's own host; no
production unit is started; nothing leaves this host.
