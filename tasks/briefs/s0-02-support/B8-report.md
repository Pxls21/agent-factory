# B8 — S0-02 runner defects D1–D3 and issue #15 follow-ups

NOT BUILT

- No live capture ran. The real runner, launcher, relay, harness server,
  containers, and host secret files were not touched. Every runner behavior test
  used a scratch repository plus labelled launcher/post doubles.
- No evidence was minted, no commit/push/outward action occurred, and the three
  owner decisions tracked by issue #11 remain external prerequisites.

IDENTITY

| file | PIN 889f1cc | final |
|---|---|---|
| R | `c092e8797ee7c42b` / 206 lines | modified, 253 lines |
| D | `a14c027b0da2f341` / 221 lines | modified, 234 lines |
| T2 | `4444842b886ac7de` / 1991 lines | modified, 2437 lines |

REPORT-LINT PIN ANCHORS

- `R@889f1cc:52` contains `grep -Eq` for the old source preflight.
- `R@889f1cc:53` contains `grep -Fqx` for the exact values preflight.
- `R@889f1cc:65` contains `exit 3` for the preflight refusal.
- `R@889f1cc:68` contains `mkdir -p "$DEST"` after the old preflight.
- `R@889f1cc:70` contains `launch_leg()` before the old launcher body.
- `R@889f1cc:76` contains `launch.ready` in the old readiness check.
- `R@889f1cc:77` contains `buzz-acp.exit` in the old early-death check.
- `R@889f1cc:105` contains `grep -c` in the old turn-window count.
- `R@889f1cc:113` contains `collect_leg()` in the old collector.
- `R@889f1cc:118` contains `cp "$FD/buzzacp.log"` before old stop.
- `D@889f1cc:78` contains `strip().lower()` in the old key normalizer.
- `D@889f1cc:84` contains `len(key)` in the old shape guard.
- `D@889f1cc:89` contains `return key` before any scalar guard existed.
- `NV@889f1cc:234` contains `d_prime == 0 or d_prime >= n`.
- `PL@889f1cc:353` contains `buzzacp.raw.log`.
- `PL@889f1cc:358` contains `buzz-acp.pid`.
- `PL@889f1cc:419` contains `launch.ready`.

VERIFIED CHANGES

- D1 — `R:44` removes only stale `launch.ready`, `buzz-acp.exit`, and
  `buzz-acp.pid` before `setsid` launches. `PL@889f1cc:358` contains
  `buzz-acp.pid`; `PL@889f1cc:367`/`PL@889f1cc:423` contain
  `buzz-acp.exit`; and `PL@889f1cc:419` contains `launch.ready`.
  `T2:2317` proves a no-ready labelled launcher returns rc 4 and preserves
  unrelated frame content.
- D1 count defect — `R:81` contains `grep -c` with `n=${n:-0}`. The pre-fix
  scratch probe against `R@889f1cc:105` contains `grep -c` and printed
  `integer expression expected` for a zero-match timeline. Final direct
  measurement pasted: absent `n=0`, zero `n=0`, three `n=3`; the three-arm test
  is `T2:2135`.
- D2 — `R:91` contains `collect_leg()` and leaves it timeline-only. `R:119`
  contains `post_leg()` after `stop_leg`, and `R:99` contains
  `collect_masked()` requiring both `buzz-acp.exit` and `buzzacp.log` before
  copying. The producer is `proofs/S0-01/tools/pc/pc_post.sh:107` (`mask
  "$FD/buzzacp.raw.log" > "$FD/buzzacp.log"`); raw output begins at
  `PL@889f1cc:353` with `buzzacp.raw.log` and is not copied. The 64-hex refusal
  remains `R:111`/`R:113` with `grep -Eq`/`return 7`.
- Wrapper — `R:144` contains `main()` for arguments, exact pin preflight,
  evidence creation, and the loop. `R:251` contains `BASH_SOURCE` guard.
  `T2:2394` proves rc 3, `BLOCKER: pins.PINNED_ENV_KEYS_S0_02`, and no `DEST`
  for a non-exact scratch pin.
- #15 scalar range — `D:100` rejects zero and `>= nv.n` with a named
  `SystemExit`, after the shape refusal at `D:93`. `NV@889f1cc:233` parses the
  scalar and `NV@889f1cc:234` contains `d_prime == 0 or d_prime >= n`. Direct
  and CLI tests at `T2:2345`/`T2:2371` assert named text, zero connection, and
  no traceback for both boundary cases.
- #15 normalization — `T2:2354` drives the real CLI with padded and uppercase
  throwaway keys through `_OwnedListener`; each reaches it exactly once. The
  empty-key case is covered with the range cases at `T2:2371`.
- #15 behavioral preflight — `T2:2394` runs real R against scratch
  `S0_02_REPO`; `T2:2414` proves exact pins create `DEST`, use the labelled
  launcher, and stop at the labelled delivery refusal. No service can start:
  every invoked path is in the scratch tree and the relay URL is closed loopback.

RED-FIRST / MUTATIONS

- PIN D1 red: zero-match `grep -c … || echo 0` printed `0` plus the fallback
  `0`; `[ "$n" -ge … ]` emitted `integer expression expected`.
- PIN D2 red: `collect_leg` failed with `cp: cannot stat …/buzzacp.log` before
  the post producer existed.
- PIN D3 red: stale ready caused `launch_leg` to return 0 with a labelled
  never-ready launcher.
- PIN scalar red: zero/`f×64` reached `nv.sign_event` and raised raw
  `ValueError: invalid private key`.
- Scratch mutations syntax-checked: D1, D2, D3, scalar, m4 (`.strip()`
  dropped), m5 (`grep -Fqx`→`grep -Fq`), m6 (preflight after destination).
  Killed: D1 by `test_wait_turn_window_handles_absent_zero_and_n_matches`; D2
  by `test_collect_leg_succeeds_before_masked_log_exists`; D3 by
  `test_launch_leg_removes_only_stale_owned_markers_before_launcher`; scalar
  by `test_cli_refuses_empty_and_out_of_range_keys_before_connecting`; m4 by
  `test_cli_normalises_padded_and_uppercase_keys_before_connecting`; m5 and m6
  by `test_main_orders_stop_post_and_masked_collection`; the actual post call
  is exercised by `test_post_leg_invokes_the_scratch_post_after_exit`.

GATES

- `bash -n R` — rc 0.
- `python3 -m py_compile D` — rc 0.
- `python3 -m pyflakes D T2` — rc 0; `lint_delta --base 889f1cc --no-ap`:
  `2 .py changed, 0 NEW pyflakes hit(s), 0 removed`.
- B8 focused tests: `11 passed, 151 deselected in 11.67s`.
- PC pair run 1 (`-n 4`): `162 passed in 16.20s`, 2026-09-22T12:59:48Z.
- PC pair run 2 (`-n 4`): `162 passed in 21.04s`, 2026-09-22T13:00:26Z.
- Authoritative final summary: `pytest-summary: 162 passed in 51.08s`,
  2026-09-22T13:02:38Z.
- `test_relay_decided_leg_needs_no_debug_canary` under the PC pair:
  `1 passed, 161 deselected in 0.76s`; the earlier sandbox red is a venue/corpus
  mismatch, not a PC-pair red.
- AP screens: R `0 hits`; D `2` pre-existing hits (AP-1 key resolution,
  AP-32 hash); T2 `11` pre-existing hits (AF-AP-80 ×7, AF-AP-34 ×4), zero new.
- Report-lint bounded final: `report_lint: 49 refs — OK 22, NEAR 0, MISS 16,
  UNCHECKABLE 10, UNRESOLVED 1 (at 889f1cc)` after the allowed fix rounds;
  floor satisfied (`OK 22 >= --min-refs 12`).

DISCREPANCIES

1. The brief attributes masked-log writing to `pc_launch.py`; measured source
   shows `pc_post.sh:107` is the producer. `pc_launch.py` writes raw log at
   `PL@889f1cc:353` and the exit marker at `PL@889f1cc:423`.
2. The first static-gate attempt used the system Python, which lacks pyflakes:
   `/usr/bin/python3: No module named pyflakes`. Re-run with
   `/home/rocco/venv-agent-factory/bin` first on PATH passed.
3. GitNexus `detect-changes` reported `3 files, 2 symbols, 0 affected processes,
   risk low`; it maps the clone index and did not map changed shell functions,
   so this is an index limitation, not a reachability claim.

SELF-ATTACK

1. The post command may have more real stack dependencies than the scratch
   double represents. The runner invokes the real `pc_post.sh` only after its
   owned stop; this lane did not execute a live leg. Independent adversarial
   review must exercise the full scratch leg in the approved venue.
2. A changed S0-01 producer contract could break the log wait. The wait proves
   both the exit marker and masked log exist; it fails loud with rc 9 rather
   than copying a stale or raw log.
3. A scalar edge could bypass the pre-network guard. Tests drive both 0 and
   `f×64` through the CLI and owned listener, asserting named refusal and zero
   connections.

RETRO

- Found: the original D2 premise named the wrong producer. Lesson belongs in
  `vendor-first`: trace the file-writing producer, not merely the launcher
  that owns the child process. Coordinator should record this as a B8 finding;
  no skill edit performed in this lane.

GATE RECOMMENDATION

MERGE-READY-WITH-FOLLOWUPS. This is a build-lane proposal, not an independent
verdict. The prohibited live capture and full real post-step behavior require
sandbox adversarial verification.
