# VERIFY-I59-F round 4 report (tasks #335 and #344): the verify fold and the S0-01 parse, attacked before the re-mint

Written 2026-09-28 21:2xZ onward by the resumed VERIFY-I59-F lane (sandbox adversarial-verifier, Opus 5.5), as I go.
No subagent, no PC bridge, no outward action, no git write outside my scratch `/tmp/vi59f4/`.

STATUS: DONE (22:0xZ). Gate: MERGE-READY-WITH-FOLLOWUPS; see GATE and the must-hold list at the end.

Aliases (round-4 bytes in `/tmp/vi59f4/wt` unless written otherwise): C = `proofs/S0-03/check_omniroute_roundtrip.py`,
T3 = `tests/test_s0_03_omniroute.py`, CC = `proofs/S0-04/check_compression.py`, T4 = `tests/test_s0_04_compression.py`,
R = `proofs/S0-05/tools/pc/run_s0_05_units.sh`, T = `tests/test_s0_05_egress.py`, CE = `proofs/S0-05/check_egress.py`,
S1C = `proofs/S0-01/check_acp_conformance.py`, BCR = `proofs/S0-01/tools/build_capture_record.py`,
T1L = `tests/test_s0_01_manifest_parse_linear.py`, TA = `tests/test_attested_inputs.py`, NL, GW and W as in round 1.

## Premise (re-measured)

- The main tree's HEAD is d773575, which is the PIN d71197e plus only `tasks/briefs/i59/VERIFY-I59-F-R4-brief.md`
  (`git diff --stat d71197e d773575`: that one file). The patch `tasks/briefs/i59/I59-F.patch` is `5cf9db295c98fddc`, the
  builder's report `231bfe78ba5b31f9`: both as the premise says.
- Copy: `/tmp/vi59f4/wt`, a WHOLE-tree `git archive HEAD` (202,127,360 bytes; no partial-copy artifacts this round),
  `git init`, one scratch commit 16f95c4 (the base bytes), then `git apply` of the patch: `15 files changed, 1586
  insertions(+), 102 deletions(-)`.
- Every one of the 15 changed files equals the lane worktree's (`cmp`, the worktree read only), and its sha256 prefix
  equals the builder's final list: 41014abdff4601cf S1C, 1557dc3010401225 BCR, 4784750397ef56ca T1L,
  1e69424390142b44 C, 9720944aa3e6da44 T3, 09c45268d76dbfd1 CC, ffd707f874d74f28 T4, 5c4600661faeaf29 R,
  aaca225c88805245 T, 383bbddc7b8140bc CE, af1b9d92cbc1e4e7 and 7b176e89a4892b85 (the two fixtures'
  `unit-identity.json`), 594fc5b0d0564392 W, df54c0b7b883d2d1 NL, d0f1d1e6bbdc6411 GW.
- Round 3's patch, for item 4: `git show a1a639b:tasks/briefs/i59/I59-F.patch` is `dc64a3f5853b48d8`, the bytes I
  verified in round 1.
- Host before (21:28:20Z): `ip netns list` 0 lines; iptables stable form `0528d077bca3781a`; mount hash
  `2dd93d06015feb4d` (27 mounts); `/tmp/e3-5t328okv` and `/tmp/e3-nw8nn6mk` predate me. Disk 11,813 MB free.

## Gates (re-run here; pasted from `scripts/test_summary.sh`, a private `--basetemp` under `/tmp/vi59f4/`)

| file | set | summary | builder's |
|---|---|---|---|
| T1L | `1 files set=b00026b98230` | `pytest-summary: 15 passed in 10.30s` | 15 |
| T4 | `1 files set=2e5825a9019e` | `pytest-summary: 201 passed in 22.92s` | 201 |
| `test_edit_snapshot_ap_screen.py` | `1 files set=3d4383148bd3` | `pytest-summary: 197 passed in 0.52s` | 197 |
| `test_pc_suite_set_id.py` | `1 files set=aca91e7d0b0f` | `pytest-summary: 3 passed in 0.20s` | 3 |
| T3 | `1 files set=696563f67d3c` | `pytest-summary: 221 passed in 43.32s` | 221 |
| `test_s0_01_audit_cp5_controls.py` | `1 files set=17a682bf802d` | `pytest-summary: 3 passed in 1.32s` | 3 |
| `test_s0_01_pc_tools.py` | `1 files set=852dc4610aeb` | `pytest-summary: 106 passed in 2.55s` | 106 |
| `test_s0_01_spec_runner.py` | `1 files set=cf2007c5ce13` | `pytest-summary: 15 passed in 16.95s` | 15 |
| `test_s0_01_frame_tee.py` | `1 files set=7756619494e8` | `pytest-summary: 121 passed in 187.08s (0:03:07)` | 121 |
| `test_s0_01_scripted_backend.py` | `1 files set=b10e41027c9e` | `pytest-summary: 348 passed in 101.28s (0:01:41)` | 348 |
| `test_s0_01_check_acp_conformance.py` (alone, 21:40:20Z-21:42:51Z) | `1 files set=31306c49985e` | `pytest-summary: 468 passed in 151.33s (0:02:31)` | 468 in 156.72 s and 160.58 s |
| T (foreground, 21:42:59Z-21:48:46Z) | `1 files set=9f0502080347` | `pytest-summary: 8 failed, 345 passed in 346.28s (0:05:46)` | 8 failed, 345 passed |
| TA rows S0-01 to S0-05 of `test_every_repo_file_a_checker_reads_is_attested` | 5 node ids | `pytest-summary: 1 failed, 4 passed in 17.57s` | S0-01, S0-04 pass; S0-05 red |
| `test_validate_ledger.py` | `1 files set=852bbd75ee1d` | `pytest-summary: 2 failed, 33 passed in 9.95s` | 2 failed, 33 passed |
| `test_proof_status.py` (basetemp `/tmp/vi59f4/ps/bt`) | `1 files set=cce0ecd44cb2` | `pytest-summary: 1 failed, 32 passed in 6.64s` | 1 failed, 32 passed |

Every count equals the builder's. After T: `ip netns list` 0 lines, iptables `0528d077bca3781a`, mounts `2dd93d06015feb4d`.

## Item 3: the reds the builder calls expected (VERIFIED, one cause each)

- **T's 8 failures**, each read from its own failure section: `test_the_committed_live_root_needs_its_unit_list`,
  `test_every_spec_leg_behaves_exactly_as_declared`, `test_the_committed_live_bundle_passes_with_every_line_pinned`, and
  `test_a_hostile_copy_of_the_live_bundle_fails_by_name` rows `c2-egress-open`, `c1-proxy-new-spelling`, `gate-inert`,
  `override-present` and `identity-not-pinned`. Every one carries the same checker line, `unit-identity-invalid:
  buzz-acp unit-identity.json lacks one of unit, pid, exe_realpath, entrypoint_realpath, entrypoint_sha256, uid, gid,
  argv`: the committed evidence has no gid and CE now requires one (F-11). No other cause.
- TA's one red is the S0-05 row: `leg(s) did not grade ... (1, 1, 0, 'unit-identity-invalid: buzz-acp
  unit-identity.json lacks one of ...')`, the same cause. The S0-01 to S0-04 rows pass (S0-02 and S0-03 included:
  they read S1C).
- `test_validate_ledger.py`'s two (`test_registry_rows_carry_no_key_the_validator_does_not_read`,
  `test_committed_pc_bridge_spike_validates_and_declares_all_effects`) and `test_proof_status.py`'s one
  (`test_committed_state_passes_status_and_ledger`) fail on the integrity call, as the builder says.
- `python3 scripts/validate-ledger integrity --root .` on the patched copy: rc 1, S0-01 to S0-05 INVALID, exactly
  `attestation-mismatch: S0-01 proofs/S0-01/check_acp_conformance.py`, `... S0-02 proofs/S0-01/check_acp_conformance.py`,
  `... S0-03 proofs/S0-01/check_acp_conformance.py`, `... S0-04 proofs/S0-04/check_compression.py`, `... S0-05
  proofs/S0-05/check_egress.py`.
- **The complete re-mint set is S0-01 to S0-05, and each changed-input list equals the builder's.** From the
  validator's own `proof_attestation` against every committed `result.json` (all twelve): S0-01: S1C, BCR. S0-02: S1C.
  S0-03: S1C, C. S0-04: CC. S0-05: CE, both fixtures' `unit-identity.json`, R. S0-06 to S0-12: none changed.
- **A consequence the builder does not name (finding R4-F2 below):** T:729-744 `LIVE_OUTPUT` pins the committed live
  bundle's whole checker output, pids included (`buzz-acp pid 930321`, `hermes-acp pid 929556`) and the DROP counters.
  After the PC re-capture, `test_the_committed_live_bundle_passes_with_every_line_pinned` will stay red on a NEW cause
  (a line mismatch) until `LIVE_OUTPUT` is re-pinned to the new bundle's output. T is not an attested input, so that
  edit needs no re-sign, but the re-capture is not done until it lands.

## Item 2: task #344, the S0-01 manifest parse (VERIFIED)

**Byte identity, by my own oracle.** Script `/tmp/vi59f4/oracle344.py` (scratch) loads four parsers in one process:
the OLD S1C and BCR (base bytes from my scratch commit, 868b8705699b5e78 and c9709755c60bfe99, the builder's "HEAD's
bytes") and the NEW ones, plus an oracle independent of both tools: the manifest's BYTES split on `\n`, a section per
`## ` header, each non-empty line fed to an incremental sha256 followed by one `\n` (no string is built). On every
committed golden manifest (`proofs/S0-01/evidence/golden/**/manifest-*.txt.gz`, 11 of them, 34,033 lines and 4
sections each): `11 of 11 golden manifests: S1C old == S1C new == BCR old == BCR new == the streaming oracle`.

**Linear, measured** (in-process, four trees of N lines each; seconds):

| N per tree (lines in all) | S1C new | BCR new | S1C old | BCR old |
|---|---|---|---|---|
| 10,000 (40,000) | 0.06 | 0.06 | 1.52 | 1.37 |
| 20,000 (80,000) | 0.15 | 0.16 | 6.32 | 6.25 |
| 40,000 (160,000) | 0.19 | 0.24 | 28.36 | 27.37 |
| 50,000 (200,000) | 0.28 | 0.35 | - | - |
| 100,000 (400,000) | 0.52 | 0.67 | - | - |
| 200,000 (800,000) | 1.07 | 1.46 | - | - |

The new code doubles with the input; the old code grows about fourfold per doubling (quadratic) and already exceeds
the 20 s bound at 160,000 lines. T1L's two bound tests against the old code (a scratch tree that differs from the
patched one only in S1C and BCR, the old hashes checked): `FAILED ...test_the_checker_parses_200000_lines_within_the_bound`,
`FAILED ...test_the_record_builder_parses_200000_lines_within_the_bound`, `2 failed, 3 deselected in 41.49s` (pytest's
own line, a scratch run): the 20-second bound is red on the old code and has a margin of more than 50 times on the new.
The checker's bound test times the line loop only (the pinned per-tree count refuses the big manifest before the
join), which is where the `+=` was.

**D-R4-5 (the comment kept on the changed line).** The only LIVE line-number pins into S1C are
`tests/test_s0_01_check_acp_conformance.py:1605` and `:1621` (S1C:1561-1565, content unchanged); the whole file passed
(468). Every citation of S1C:1050-1080 or BCR:35-50 in the tree is in a historical lane pack or report under
`tasks/briefs/` (for example `tasks/briefs/s0-01-p5c-support/VERIFY-P5c-pack.md:51` quoting BCR:45's old `return`),
records of their day. The line-neutral edit hides nothing. Note (INFO): a test that pins source line numbers made a
line-neutral edit necessary; that is AF-AP-233's class (a test pinning an incidental property of a live file).

Small observation (INFO): BCR splits with `str.splitlines()` and S1C with `split("\n")`, so a manifest line holding
`\r`, `\x0b`, `\x0c`, `\x1c`-`\x1e`, `\x85`, U+2028 or U+2029 would be cut differently by the two tools. Pre-existing and
unchanged by #344; no committed manifest has such a line (the five-way equality above).

## Item 1: my round-1 findings, re-run on the round-4 bytes through the real path

Drivers (scratch, deleted at the end): `/tmp/vi59f4/e1_r4_driver.py` (the real C and CC CLIs; fakes built at run
time; `leak_runs` = case-folded 4-character runs of the fake in stdout plus stderr), `/tmp/vi59f4/hb_r4_driver.py`
(R's own handback program cut from R's bytes, with a mover or a mount injected, as T's `_handback_program()` does).

| finding | round-4 result, reproduced | verdict |
|---|---|---|
| F-1 (known set) | the real bundle `proofs/S0-04/evidence`: rc 0, `observation: config api_mode = openai_chat (RECORDED, not asserted - task #35 was decided by D-021 on 2026-09-08)`; `codex_responses` by name; `openai_chat ` (trailing space), `Openai_Chat` and `openai_responses` by shape | CLOSED. No pinned source in the tree names a Responses transport: every `transport:` value in a YAML, JSON, Markdown or Python file is `openai_chat` (26) or an unrelated word; `openai_responses` appears only as the builder's mutant name, `anthropic_messages` only as a variable in vendored `sandbox-kit/aleph`. A Responses transport would print by its shape (fail-safe), as the builder's NOT-done says |
| F-2 | a JSON array, string, number and `null` each: rc 1, the one line `failure_reason: config: provider block is not a JSON object`, 0 leak runs; `{}` reaches `config-header-absent: extra_headers` | CLOSED |
| F-3 | N1, N2, N3 on the round-4 runner: KILLED by the new rows (item 5) | CLOSED |
| F-8 | N4, N5: KILLED (item 5); an 18-digit int key_env prints `int, 18 characters, sha256 ...` | CLOSED |
| F-9 | api_mode a list or a map: `transport: profile api_mode (list, 28 characters, ...)`; `key_env: &r [*r, ...]` and a map inside itself: `has a recursive alias under providers.s0-03-omniroute.key_env.0` / `...loop.again`; not UTF-8: `cannot be read (UnicodeDecodeError)` (D-R4-2); mode 0000 read as 65534: `cannot be read (PermissionError)`; every row stderr empty, 0 leak runs | CLOSED for the two named cases and the read error. The same traceback class stays for a non-string KEY (item 6) |
| F-4 | the ancestor `p` moved out while the walk was two levels below: `then it stopped: an ancestor of .../p/child/x moved out of the root while it ran`; `outside/p/zz-decoy` untouched (65534:65534) | CLOSED as specified (every climb checks up to the root). The window between two climbs stays, as R:603-608 now says: an ancestor moved while the walk read `p/a` got `outside/p/a/f2`..`f5` handed back OUTSIDE the root (4 entries) before the next climb stopped it; `d` moved while read got `outside/d/b` handed back, then the climb from `b` stopped the walk (`outside/d/c` untouched; round 3 handed both back) |
| F-12 | a tmpfs on `d` while read: `a mount appeared above .../d/b`; a SAME-filesystem bind mount on the parent `p`: `a mount appeared above .../p/child/x` (the mount-id branch), the bind source untouched | CLOSED. T covers the tmpfs kind only (the V4-mount-by-st_dev-only survivor, item 5) |
| F-6 | both `_shape` docstrings say "high-entropy" and "brute force"; T3 and T4 pin it | CLOSED |
| F-7 | setpriv here is `util-linux 2.39.3`, `--clear-groups  clear supplementary groups`. With a copy of `/etc/group` listing `nobody` in `root` bind-mounted in a private mount namespace (host file untouched): `--init-groups` gives `Groups: 0 65534`, `--clear-groups` gives `Groups:` empty. R launches both units (R:909, R:914) and the probe (R:883) with `--clear-groups`; A7 records `groups` and refuses a 0 (T's live leg pins `"groups": []`) | CLOSED here. The PC's setpriv: NOT run here: PC only (`--clear-groups` has been in util-linux since 2.23, so INFERRED present) |
| F-10 | the observation line above; no `open decision` or `ADR 0002 deviation` left in CC | CLOSED |
| F-11 | CE, the synthetic-pass bundle with its gid changed: missing -> `lacks one of ..., uid, gid, argv`; `[1000,1000,1000,0]` -> `gid 0`; `[-1]*4`, `[1000.0]*4`, five entries, strings -> `is not the four gids of the Gid line`; the uid0 fixture still fails on `uid 0` | CLOSED. CE accepts `[4294967296]*4` (no upper bound, as for the uid; /proc cannot report it) and does not grade `groups`: a record with `"groups": [0]` or `"groups": "junk"` passes CE (finding R4-F4) |
| F-13 | R's three id patterns spell `[123456789][0123456789]`; T's pattern test guards them | CLOSED. R:319 `[[ "$mode" =~ ^[0-7]{1,4}$ ]]` (a mode, not an id) and `netns_lib.sh:172` (item 6) keep ranges |
| F-14 | the explicit and resolved unit-user refusals quote with `printf %q` (T's newline row passes on one line) | CLOSED. The SUDO refusals (R:134, R:138) still quote raw (the builder's NOT-done) |

**The cost of F-4's check, measured apart from any test row** (the handback program alone, a chain of N directories
under RLIMIT_NOFILE 1024; one run each):

| levels | round 4 | round 3 |
|---|---|---|
| 1,100 | 2.33 s | 0.07 s |
| 2,200 | 11.18 s | 0.10 s |
| 3,300 | 24.04 s | 0.15 s |

Round 4 is quadratic in depth (about 2.2 µs x N²); round 3 was linear. The builder's "4.8 s against 2.4 s per row"
compared whole test rows (a real leg each), which hides a 33-fold ratio at 1,100 levels. Extrapolated: about 3.7 min
at 10,000 levels and about 6 h at 100,000. The handback runs in `cleanup`, whose first command is `trap '' INT TERM`, so
the Python child inherits both ignores: Ctrl-C and `kill` do nothing, and only a signal left at its default (KILL, HUP,
QUIT) ends it, with the handback then not done. A unit that leaves a deep tree in its scratch HOME can hold the
runner's exit for hours (finding R4-F3). A real Hermes scratch tree is a few
levels deep, so the PC re-capture is not affected.

## Item 4: round 4 against round 3 (VERIFIED by reading every changed line)

Round 3's bytes: the base plus `git show a1a639b:tasks/briefs/i59/I59-F.patch` (`dc64a3f5853b48d8`), applied in
`/tmp/vi59f4/r3`; round 4's: the copy. Changed lines per file (`diff -u`, `+`/`-` lines): S1C 6, BCR 6, C 36, CC 28,
CE 13, each fixture 6, R 76, T3 108, T4 95, T 164; W, NL and GW 0; T1L new (134 lines).
- Every production change maps to a fold item: C = F-6 (docstring), F-9 (the read in its own `try` with `cannot be
  read`, the credential walk's `_open` set, the api_mode type check); CC = F-1 (the set and its cited sources), F-6,
  F-2 (the guard), F-10 (comment and text); CE = F-11; the fixtures = F-11; R = F-13 (explicit classes), F-14 (`%q`),
  F-7 (the Groups line, `supplementary group 0`, `--clear-groups` at both launches), F-4 and F-12 (`off_the_way`, the
  corrected comments); S1C and BCR = #344 (list, then one join).
- Behavior changes, each inside its ruling: a non-UTF-8 profile now reads `cannot be read (UnicodeDecodeError)`
  (D-R4-2; S0-04's C-1 rows name a decode error on the read's line too, so I accept it); a provider block that is a
  number or `null` now fails by name, where it read `malformed evidence: TypeError` (D-R4-3); the handback's cost
  became quadratic in depth (R4-F3, measured in item 1).
- No test assertion was weakened: every removed assertion line has a stricter or equal replacement (the %q pins, the
  A7 reason with the Groups line, the gid rows, the longer BAD_UNIT_USERS; the round-3 gid reader test became the
  groups reader test because CE now grades the gid itself). The listener ports moved from 18160+ to 18180+ because the
  list grew to 17 rows (18160 + 16 would reach 18170-18175, used by other tests).
- CC's comment cites six sources by `file:line`; each holds what it claims on these bytes (C:215, capture_leg.py:121,
  both configs' `transport: openai_chat`, `hermes-provider.json:2`, the decision log's D-021 row at :32).
- No behavior change outside the fold. No finding.

## Item 5: mutation (VERIFIED)

Harness `/tmp/vi59f4/mutate_r4.py` (scratch): the unmutated baseline of each target set first (all passed: WALK 4,
CEID 13, T1L 15, C 11, CC 13, PAT 1, A1 18, LIVE 1, R3 2), one anchored replacement (every anchor counted once), a
static check (`py_compile`, or `bash -n` and R's five heredocs), the target tests with a private `--basetemp`, then
the file restored from a saved copy and its sha256 checked. KILLED = FAILED lines, no ERROR, the collected count
equal to the baseline's (AF-AP-223). The counts are pytest's own summary lines (scratch probes, not gates). Every file
ended at its round-4 hash (S1C 41014abdff4601cf, C 1e69424390142b44, CC 09c45268d76dbfd1, CE 383bbddc7b8140bc, R
5c4600661faeaf29).

| row | source | mutant | verdict | FAILED / collected |
|---|---|---|---|---|
| X-R4-F4-chain | builder | `off_the_way` never opens `..` | KILLED | 1/4 (the clean-tree control) |
| X-R4-F7-launch | builder | `--init-groups` at the agent launch | KILLED | 1/1 (the live leg) |
| X-R4-F11-gid0 | builder | CE's `gid 0` refusal removed | KILLED | 1/13 (`effective-gid-0`) |
| X-344-c-bytes | builder | S1C joins with `"\n".join(lines)` | KILLED | 11/15 (the 11 golden rows) |
| X-R4-F2-guard | builder | the not-an-object guard off | KILLED | 3/13 |
| X-R4-F9-cycle | builder | the recursive-alias check never fires | KILLED | 2/11 |
| X-R4-F1-drop | builder | CC's set without `openai_chat` | KILLED | 3/13 |
| X-R4-F13-range | builder | the SUDO pattern's first class `[1-9]` | KILLED | 1/1 |
| N1 | round 1 survivor | only the uid bound removed | KILLED | 2/18 (`4294967296:65534`, `4294967295:65534`) |
| N2 | round 1 survivor | only the gid bound removed | KILLED | 2/18 |
| N3 | round 1 survivor | the explicit pattern admits uid 0 | KILLED | 1/18 (`0:65534`) |
| N4 | round 1 survivor | C's `_shape` prints a non-string | KILLED | 2/11 |
| N5 | round 1 survivor | CC's `_shape` prints a non-string | KILLED | 1/13 |
| V4-walk-skips-root-frame | new | `off_the_way` never checks the root's own frame | KILLED | 1/4 (the ancestor test) |
| V4-CE-gid-shape-off | new | CE's gid shape check off | KILLED | 2/13 |
| V4-C-read-catches-OSError-only | new | the read catches `OSError` only | KILLED | 1/11 (`not-utf-8`) |
| V4-CC-guard-lists-only | new | the F-2 guard refuses lists only | KILLED | 2/13 (string, number) |
| V4-resolved-pattern-range | new | the resolved-user pattern back to `[1-9][0-9]` | KILLED | 1/1 |
| **V4-mount-by-st_dev-only** | new | `off_the_way` names a mount by `st_dev` only (the mount-id check dropped) | **SURVIVED** | 0/4 |
| V4-gid0-refusal-raw | new | the resolved gid-0 refusal quotes raw | SURVIVED, EQUIVALENT | 0/2 |

Eight of the builder's 30 rows reproduced as FAILED tests, the four the brief names among them. Survivors:
- V4-mount-by-st_dev-only is a test gap (finding R4-F5): T's mount test mounts a tmpfs, which changes `st_dev`, so
  the mount-id half of the check is never needed; a SAME-filesystem bind mount on a parent (my item-1 row, which the
  real code names correctly) would be worded "moved" under the mutant. The walk stops either way.
- V4-gid0-refusal-raw is equivalent: a resolved value is `stat -Lc '%u:%g'` output (digits and one colon), which
  `printf %q` returns unchanged, so no input tells the two apart.

## Item 6: the builder's two adjacent defects (both CONFIRMED)

- **C's credential walk on a non-string key.** Through the real CLI, a key `123`, `true` or `null` under the provider
  block: rc 1, empty stdout, stderr's last line `AttributeError: 'int' object has no attribute 'upper'` (`'bool'`,
  `'NoneType'`): a traceback, F-9's class, with no value printed (0 leak runs). `is_credential_name(key)` calls
  `key.upper()` (C:195-209) before any type check. Present in round 3 and round 4 alike (finding R4-F1).
- **`proofs/S0-05/netns_lib.sh:172`** reads `if [[ "$owner_pid" =~ ^[1-9][0-9]{0,9}$ ]] && kill -0 "$owner_pid"`:
  ranges, against the file's own rule X1 (`every class is an explicit list`). The value is the runner's own `$$`,
  read back from the owner file; a widened range would at worst let `kill -0` refuse a non-ASCII pid and the record
  be tombstoned as stale: fail-safe. Outside I59-F's boundary. R:319 `^[0-7]{1,4}$` (a file mode from `stat`) is the
  one range left in R, and not an id pattern.

## The re-mint, dry-run in my copy (VERIFIED)

`python3 scripts/proof-runner run --proof <id> --venue sandbox --root .` for S0-01 to S0-05 (with `test_summary.sh`'s
sandbox defaults for S0-01's corpus), then `validate-ledger integrity`:
- S0-01, S0-02, S0-03: rc 0, PRESENT; every leg byte-identical (exit, stdout and stderr hashes, failure reasons),
  only the attestation changed (S0-01: S1C, BCR; S0-02: S1C; S0-03: S1C, C).
- S0-04: rc 0, PRESENT; the positive leg's `stdout_sha256` changed (the observation now `openai_chat` with the D-021
  text), the negative leg unchanged, CC's attestation changed.
- **S0-05: rc 1, `leg-exit-mismatch: S0-05 positive expected 0 got 1`, and the runner DELETED
  `proofs/S0-05/result.json` (by design, VERIFY-N5g F8): integrity then reads `S0-05 ABSENT`.** Re-minting S0-05
  before the PC re-capture is committed destroys its minted artifact.

## Finding inventory, round 4 (no severity filter)

**R4-F1. FOLLOW-UP (attested file C; decide before the re-mint): F-9's traceback class stays for a non-string KEY.**
- Evidence: VERIFIED through the real CLI (item 6): a key `123`, `true` or `null` under the provider block ends in
  `AttributeError: 'int' object has no attribute 'upper'` (exit 1, empty stdout), no value printed.
- Contract mapping: F-9 names "an unhashable api_mode and a recursive alias"; both closed. This input is the same
  class, not named; the builder found and reported it (not fixed). Material: a traceback where a `failure_reason:`
  line belongs; nothing leaks. Fix: in `_walk_node`, refuse a non-string key by name (`key {type} under <path>`)
  before `is_credential_name`, with a T3 row.

**R4-F2. MUST HOLD at the PC re-capture (a precondition, not a patch defect): T pins the old live bundle's output.**
- Evidence: VERIFIED by reading T:729-744. `LIVE_OUTPUT` pins the committed bundle's whole checker output, including
  `buzz-acp pid 930321`, `hermes-acp pid 929556` and the DROP counters `0 -> 6`.
- Effect: after the re-capture, `test_the_committed_live_bundle_passes_with_every_line_pinned` stays red on a new
  cause (a line mismatch) until `LIVE_OUTPUT` is re-pinned to the new bundle; the other seven of T's 8 reds should
  then grade (their hostile copies start from the new bundle). T is not an attested input, so the re-pin needs no
  re-sign, but CI stays red until it lands.

**R4-F3. FOLLOW-UP (attested file R): the per-climb check made the handback quadratic in depth.**
- Evidence: VERIFIED (item 1): 2.33 s / 11.18 s / 24.04 s at 1,100 / 2,200 / 3,300 levels, against round 3's
  0.07 s / 0.10 s / 0.15 s. `cleanup` ignores INT and TERM, and the handback inherits it.
- Contract mapping: none violated (the F-4 contract asks for the per-climb check; the round-1 B-3 bound, 1,100
  levels under 1024 descriptors, still holds). The builder disclosed "quadratic" but quoted whole-row times.
- Material: a unit that leaves a deep tree can hold the runner's exit for minutes to hours (about 3.7 min at 10,000
  levels by the fit); only KILL, HUP or QUIT end it, and then without the handback. A real Hermes tree is shallow.
- Fix options: cap the depth the walk will enter (leave and count what lies below), or check the whole chain only
  every k climbs plus once at the end, or give the handback a time budget and name what it leaves.

**R4-F4. FOLLOW-UP (attested file CE): CE grades the gid but not the new Groups record, and bounds neither id above.**
- Evidence: VERIFIED (item 1): a record with `"groups": [0]` or `"groups": "junk"` passes CE; so does a gid of
  `[4294967296]*4` (the uid has the same form). A7 refuses a group 0 at capture time.
- Contract mapping: none (F-7 asked the readers only to keep reading the new record, "as in round 3"). It is round 1's
  F-11 class again, for the groups: the committed evidence cannot show what A7 saw. Fix: grade `groups` when present
  (refuse a 0, require a list of non-negative ints); the re-captured records carry it, so the new evidence passes.

**R4-F5. FOLLOW-UP (test gap; T only, can land after the re-mint): the mount wording is tested for a tmpfs only.**
V4-mount-by-st_dev-only survives (item 5). Fix: a T row that bind-mounts a same-filesystem directory on a parent at the
first climb (my item-1 row shows the real code names it `a mount appeared above ...`).

**R4-F6. INFO: the window between two climbs remains, as R's comment now says.** VERIFIED: an ancestor moved while the
walk read `p/a` got `outside/p/a/f2`..`f5` handed back outside the root before the next climb stopped the walk. It
needs a live mover (F-5, out of scope by the ruling).

**R4-F7. INFO: V4-gid0-refusal-raw is an equivalent mutant** (a resolved value is digits and a colon).

**R4-F8. INFO: the SUDO refusals (R:134, R:138) still quote their values raw** (the builder's NOT-done; sudo sets
digits).

**R4-F9. INFO: two ranged patterns remain:** R:319's mode pattern and `netns_lib.sh:172` (item 6, the builder's second
adjacent defect, outside the boundary, fail-safe).

**R4-F10. INFO (pre-existing):** BCR splits manifest text with `splitlines()`, S1C with `split("\n")`; no committed
manifest holds an exotic separator (item 2's five-way equality).

**R4-F11. INFO (report accuracy):** the builder's cost line ("4.8 s against 2.4 s per row") compares whole T rows and
understates the handback's own ratio (33 times at 1,100 levels). Every other count, hash and red I re-ran matched.

**R4-F12. INFO:** the test that pins S1C line numbers (`tests/test_s0_01_check_acp_conformance.py:1605`, `:1621`) forced
a line-neutral edit (D-R4-5): nothing is hidden, but it is AF-AP-233's class.

**R4-F13. INFO (the builder's discrepancies, checked):** D-R4-1 (S0-02 joins the re-mint) CONFIRMED by the validator's own
attestation; D-R4-2 (a non-UTF-8 profile is a read error) ACCEPTED, consistent with S0-04's C-1 rows; D-R4-3 CONFIRMED
(a number and `null` refuse by name); D-R4-5 CONFIRMED harmless; D-R4-4, D-R4-6 to D-R4-8 are process notes.

**R4-F14. UNVERIFIED (PC only):** the PC's setpriv takes `--clear-groups`, and the PC's units need no supplementary
group (the owner's uid 1000 loses its groups, `wheel` included, at the launch). The re-capture itself will show it: a
unit that needs a group-owned resource would end in a `not-run` leg, not in a containment gap.

## What I reproduced, reviewed statically, and skipped

- Reproduced: the premise; the 15 gates the builder ran (every count equal); T's 8 reds and each message; TA's rows;
  the expected reds; integrity; every proof's changed inputs; item 1's rows (C, CC, CE, the handback, setpriv); #344's
  five-way byte identity, its scaling and T1L's red on the old code; 20 mutants; the dry-run re-mint.
- Reviewed statically: the r3-to-r4 diff line by line; CC's six cited sources; T's `LIVE_OUTPUT`; the two adjacent
  defects' code.
- Skipped: the PC (the re-capture, its setpriv and /etc/group: `NOT run here: PC only`); real CI;
  `test_s0_01_check_acp_conformance.py`'s "before" wall time (1,298 s in four chunks per the builder; I measured the
  parse itself instead, item 2); `tests/test_lane_gate.py` and the whole `test_vendored_manifest.py` (the brief's
  rules); W, NL and GW's gates (unchanged since round 2, gated in round 1).

## Host state after (22:08:24Z)

`/tmp/vi59f4/` and everything under it are removed. `ip netns list` 0 lines; iptables stable form `0528d077bca3781a`
and mount hash `2dd93d06015feb4d` (27 mounts), both equal to before; no uid-65534 process; the two `/tmp/e3-*` that
predate me remain. Every tmpfs and bind mount my drivers made was unmounted by its path, in the run that made it. I
wrote nothing outside `/tmp/vi59f4/` but this report, and made no git write outside my scratch copy.

## GATE

Blocking predicate (skill `contract-gate`, D-031) with D-034's CORE-BLOCKING rule: no finding meets all five
conditions. Every fold item and task #344 hold through the real path. R4-F1, R4-F3 and R4-F4 are outside the frozen
rulings (a sibling input of F-9's class; the cost of the ruled check; a reader the F-7 ruling did not ask to grade).
R4-F5 is a test gap that can land later. R4-F2 is a re-capture step, not a defect. Every other finding is INFO.

**Recommendation: MERGE-READY-WITH-FOLLOWUPS** (not reproduced: the PC venue, meaning the re-capture, its setpriv and
its /etc/group, and real CI).

## Must hold before the re-mint and the PC re-capture

1. **Order.** S0-01 to S0-04 can re-mint now: the dry run gives each PRESENT, every leg identical except S0-04's
   positive stdout (the `openai_chat` line). **Do not run `proof-runner` for S0-05 before the PC re-capture is
   committed: it fails leg 1 and deletes `proofs/S0-05/result.json` (measured here: `S0-05 ABSENT`).**
2. **The re-mint set is S0-01 to S0-05, and nothing else.** The validator's own attestation shows no changed input for
   S0-06 to S0-12. S0-02 is in the set because it attests S1C (D-R4-1).
3. **The re-capture** runs the round-4 runner, whose A7 writes the gid and the Groups line, so the round-4 CE passes
   it. Then `LIVE_OUTPUT` (T:729-744) is re-pinned to the new bundle's output (R4-F2); until then T stays red on a line
   mismatch. Then S0-05 is re-minted.
4. **Decide first, because each changes an attested file** (after the re-mint, each means another signature): R4-F1
   (C: a non-string key ends in a traceback), R4-F3 (R: the quadratic handback), R4-F4 (CE: `groups` ungraded, no upper
   id bound). Fold them now or file them as follow-ups for a later re-sign.
5. **PC only (R4-F14):** the PC's setpriv takes `--clear-groups`, and its units need no supplementary group. The
   re-capture itself shows it; a `not-run` leg there would name the cause.
6. **Can wait (test files only, no attested input):** R4-F5's bind-mount row. F-5 stays a follow-up issue by the
   ruling.
