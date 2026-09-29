<!-- Coordinator note (2026-09-29, AF-AP-154): the served models of this round, counted per assistant record at harvest (`python3 scripts/stack.py harvest agent=a4f24691b2f13e97e`, run s-20260929T004045Z-f2ff24): one refusal stop at 00:08:38Z, right after the tool call "Probe R4-F3's window with a mover at two moments"; claude-opus-5-5 served the lane until 00:08:58Z (the premise, R4-F1, R4-F3's measurements) and claude-opus-4-8 served its last 61 records, 00:09:17Z to 00:40:12Z (R4-F4, R4-F5, the 13 builder mutant rows and the extra mutants, validate-ledger, the gates, the verdict). This report does not state the mix; the harness switched the model without notice. The executed numbers of the second part agree with the builder's exactly (T 8 failed and 355 passed; X-R5-F3-never 2; X-R5-F4-bound-by-one 4). -->

# VERIFY-I59-F round 5 report (tasks #335 and #344)

STATUS: DONE (00:3xZ). Gate: MERGE-READY-WITH-FOLLOWUPS; see GATE and item 5 at the end.

Verifier: the sandbox adversarial-verifier lane (Opus 5.5), resumed for round 5. Contract:
`tasks/briefs/i59/VERIFY-I59-F-R5-brief.md` (a NARROW round: the four round-4 findings round 5 folds). Change under
test: `tasks/briefs/i59/I59-F.patch`, rounds 1 to 5. Every builder claim below is a hypothesis until I reproduce it.
Started 2026-09-28 23:5xZ; this report is written as I go.

## Premise (re-run 2026-09-28T23:53:47Z, the brief's block plus the host baseline)

```
2026-09-28T23:53:47Z
netns: 0
iptables stable form: 0528d077bca3781a
mounts: 2dd93d06015feb4d (27)
/tmp/e3-5t328okv
/tmp/e3-nw8nn6mk
/dev/vda          258020 25969     11970  69% /
b090cf4                         <- main-tree HEAD (local)
0c11fd1                         <- origin/claude/soundbox-kit-migration-iz1jwf
PIN-is-an-ancestor-of-HEAD
7382fdbacb103793  tasks/briefs/i59/I59-F.patch
1f3880cfdaec6fff  tasks/briefs/i59/I59-F-report.md
dcebc0bc5878d21e  tasks/briefs/i59/I59-F-R5-brief.md
be65de75d9c49032  tasks/briefs/i59/VERIFY-I59-F-R4-report.md
16                              <- porcelain lines of /home/user/i59-landing
same (15 of 15): .github/workflows/stage0-ci.yml, proofs/S0-01/check_acp_conformance.py,
  proofs/S0-01/tools/build_capture_record.py, proofs/S0-03/check_omniroute_roundtrip.py, proofs/S0-04/check_compression.py,
  proofs/S0-05/check_egress.py, the two S0-05 unit-identity fixtures, proofs/S0-05/tools/pc/run_s0_05_units.sh,
  tests/test_gpu_window.py, tests/test_no_laya_in_gates.py, tests/test_s0_03_omniroute.py,
  tests/test_s0_04_compression.py, tests/test_s0_05_egress.py, tests/test_s0_01_manifest_parse_linear.py
```

Every hash equals the brief's premise. The two `/tmp/e3-*` directories predate me and are not mine. The host
baseline (netns 0, iptables stable form `0528d077bca3781a`, mount hash `2dd93d06015feb4d` over 27 mounts) is the
round-4 form: `iptables-save`, comments dropped, counters masked; the sorted mount points of `/proc/self/mountinfo`.

## Scratch copies

- `/tmp/vi59f5/wt`: `git archive HEAD` of the whole main tree (HEAD b090cf4), `git init` there, one scratch commit
  (6936c94), then the round-5 patch applied: `15 files changed, 1807 insertions(+), 104 deletions(-)`; 15 of 15 files
  equal the lane's worktree. Hashes: 4721d03166294bb4 C, 6cae194d12743368 T3, af3badbb5c10f587 R, 6a4ca561aff32507 CE,
  c185c5f8c18eda3a T (the builder's final list, same prefixes).
- `/tmp/vi59f5/r4`: HEAD's copies of the 15 files with the round-4 patch applied (`git show
  d71197e:tasks/briefs/i59/I59-F.patch`, sha256 5cf9db295c98fddc, the R5 builder brief's premise value).

Abbreviations as in round 4: C = `proofs/S0-03/check_omniroute_roundtrip.py`, T3 = `tests/test_s0_03_omniroute.py`,
R = `proofs/S0-05/tools/pc/run_s0_05_units.sh`, CE = `proofs/S0-05/check_egress.py`, T = `tests/test_s0_05_egress.py`,
TA = `tests/test_attested_inputs.py`. Line numbers are the round-5 bytes unless marked r4.

## Item 1: each finding round 5 claims closed

### R4-F1 (C): a non-string key fails by its type — CLOSED, reproduced

Driver `/tmp/vi59f5/drv/r4f1_shapes.py` runs the real CLI (`python3 C <spec.json's flags> <bundle>`, the T3
`passing` bundle built the fixture's way) on 22 profile shapes, each with a fake value V built at run time
(`_fake_profile_value()`) and an int key K drawn at run time; it checks the exit, the exact line, an empty stderr, no
`Traceback`, and no case-folded 4-character run of V or of K's digits in stdout plus stderr.

| shape (beyond the builder's four) | round 4 bytes (`/tmp/vi59f5/r4tree`) | round 5 bytes |
|---|---|---|
| int key in a list item (`extra_list: [{K: V}]`) | exit 1, traceback | `... non-string key (int) under providers.s0-03-omniroute.extra_list.0` |
| int key in a list in a list | traceback | `... (int) under ....extra_list.0.1` |
| int key three mappings deep (`a.b.c`) | traceback | `... (int) under ....a.b.c` |
| YAML merge key, anchored `{K: V}` merged into a sub-mapping | traceback | `... (int) under ....extra` |
| merge key into the provider block itself | traceback | `... (int) under providers.s0-03-omniroute` |
| merge of a list `<<: [*a1, *a2]` | traceback | `... (int) under ....extra` |
| float key, `.nan`, `-.inf` | traceback | `... (float) under ...` |
| date key, timestamp key | traceback | `(date)`, `(datetime)` |
| `!!binary` key | traceback | `(bytes)` |
| YAML 1.1 `off:` key (loads as False) | traceback | `(bool)` |
| empty key `? :` | traceback | `(NoneType)` |
| `yes:` key in `extra_headers` | traceback | `(bool) under ....extra_headers` |
| int key in a recursive alias `&r {K: *r}` | traceback | `(int) under ....loop` (the type guard fires before any recursion) |
| tuple-like keys: `? [V, b]`, `? {V: b}`, `? !!python/tuple [V, 2]`, `<<: V` (a scalar merge) | `bundle: hermes/profile.yaml is not valid YAML (ConstructorError)` | the same line: `yaml.safe_load` refuses them before the walk |

Every round-5 row: exit 1, exactly one stdout line, empty stderr, no traceback, no run of V or of K. So the guard
holds for every key shape `safe_load` can build (int, float, bool, None, date, datetime, bytes); a sequence, a mapping
or a Python tuple cannot be a key after `safe_load` (ConstructorError before the walk, the round-4 line unchanged). The
guard sits in `_walk_node` before `is_credential_name` (C:797-801), and the printed path holds only string keys
already checked and list indices, so K never reaches the line.

Beyond the contract (INFO, pre-existing, not a round-5 change): the provider's own name, the key of `providers`, is
not under the provider block, so the new guard does not see it. `_provider_block` takes `str(name)`, and the name is
not graded at all: an int name, a string name `zzz-not-the-model-provider`, and `model.provider:
custom:somewhere-else` each PASS (exit 0) on HEAD's C, round 4's and round 5's alike. The name then prints in every
path-bearing failure line (the class round 1 accepted: keys print through paths). See I-1 in the inventory.

### R4-F3 (R): the handback cost is linear — CLOSED, reproduced; the window is bounded as documented

Measured through R's own handback program, cut from R's bytes exactly as T's `_handback_program` cuts it
(`/tmp/vi59f5/drv/walk_lib.py`, `program()`), on a descriptor-built chain of `d` levels. Opens of `".."` counted by a
profile hook in the child; clock and `ru_maxrss` from the child.

| depth d | round 4 bytes opens (per level) | round 5 opens (per level) | round 5 clock |
|---|---|---|---|
| 1,100 | 605,550 (550.5) | 35,642 (32.4) | 0.25 s |
| 2,200 | 2,421,100 (1100.5) | 71,905 (32.7) | 0.50 s |
| 3,300 | 5,446,650 (1650.5) | 108,216 (32.8) | 0.63 s |
| 6,600 | — | 217,078 (32.9) | 1.33 s |
| 40,000 | — | 1,319,234 (33.0) | 16.97 s |

Round 4 was O(d^2) in opens (per-level count rises with d). Round 5 is flat at ~33 opens/level across d from 32 to
40,000: O(d). The builder's own numbers (35,642 / 71,905 / 108,216) reproduce to the open. At and below
`CHECK_BUDGET` = 32 the walk still checks the whole way at every climb (16.5 opens/level at d=32).

**The window, bounded as R's comment states.** With a mover renaming the chain's top out of the root, the number of
climbs between the move and the stop tracks `ceil(depth/32)`: 2 at d=33 (bound 2), 7 at d=200 (bound 7), 31 at d=1000
(bound 32), 101 at d=3300 (bound 104). So the whole-way check does fire within `ceil(d/CHECK_BUDGET)` climbs, and the
walk then stops with `an ancestor of ... moved out of the root while it ran`. The comment's claim is accurate.

During that window the walk hands back entries it meets below the moved ancestor at their current location, which is
now outside the root — exactly what R's comment discloses ("until then the walk hands back what it finds below that
ancestor, where it now is"). Reproduced: at d=3300, up to ~197 decoy files below the moved ancestor were chowned to the
invoker while outside the root before the stop; a file created beside the moved directory during the window was chowned
too. This is the R4-F6 window class the coordinator already holds as a follow-up (not a round-5 regression: round 4 had
the same between-climbs window, only one climb wide). It requires a process actively moving the tree DURING teardown;
the runner's model is that no unit or canary is alive at handback (F-5's separate concern). Materiality below.

**A memory note (INFO, F-8's class, pre-existing, not in the contract).** RSS grows with depth because each stack
frame keeps the full joined path string (`path = os.path.join(where, name)`, R's while-loop). Measured maxRSS: 20.9 MB
at d=3,300, 108 MB at d=10,000, 1,550 MB at d=40,000. Attributed: replacing the frame's path with the bare name in a
throwaway experiment (`/tmp/vi59f5/exp-noname`, NOT a proposed patch) holds RSS at ~20 MB to d=40,000 with identical
opens and exit. The realistic evidence tree is shallow (a handful of levels), so this never bites the real proof; it is
a depth-bomb ceiling, the same F-8 resource class already a follow-up. See I-3.

Signal disposition unchanged (contract forbids touching it): `cleanup` still `trap '' INT TERM` (R:754), and the two
top-level `trap ... INT/TERM` lines (R:776-777) stand. Diff shows no change to the trap lines.

### R4-F4 (CE): the Groups line is graded, ids bounded — CLOSED, reproduced; the ungraded-groups-ceiling is immaterial

Driver `/tmp/vi59f5/drv/r4f4_ce.py` runs the real CE CLI (`python3 CE --units curl,hermes-acp <bundle>`) on the
synthetic-pass bundle with the `hermes-acp` identity mutated. 22 cases; every one behaves as the contract says.

| case | round 4 bytes | round 5 |
|---|---|---|
| `groups: [0]`, and `[1000,0,65534]` | exit 0 (ungraded) | exit 1, `unit-identity-invalid: hermes-acp supplementary group 0` |
| `groups: "junk"` | exit 0 | exit 1, `groups 'junk' is not the gids of the Groups line` |
| `groups: [True]` / `[-1]` / `[1000.0]` / `[None]` / `[[1000]]` | exit 0 | exit 1, `groups <repr> is not the gids of the Groups line` |
| `groups: []`, `[1000,65534]` (positive controls) | exit 0 | exit 0, pass |
| `gid`/`uid` = `[4294967295]*4` | exit 0 | exit 1, `<id> 4294967295 is above 4294967294` |
| `gid`/`uid` = `[4294967296]*4` | exit 0 | exit 1, `... 4294967296 is above 4294967294` |
| `uid` mixed `[1000,4294967295,1000,1000]` (max over) | exit 0 | exit 1 (uses `max(uid)`) |
| `uid`/`gid` = `[4294967294]*4` (boundary) | exit 0 | exit 0, pass (4294967294 is allowed) |
| `uid: [0]*4` (still caught) | exit 1 | exit 1, `uid 0` |

`_is_int` (CE:165) excludes bool (AF-AP-26), so `[True]` is refused; the shape check runs before `max()`, so `max()`
never sees a bool or a non-list. The bound uses `max(uid)`/`max(gid)`, so one over among four is caught. Round 4 passed
every new-refusal case (13 "would-be-red" rows confirmed on `/tmp/vi59f5/r4tree`): the grading is a real change.

**The builder's NOT-done (a group above 4294967294 still passes) — reproduced, judged immaterial.** `groups:
[4294967295]`, `[4294967296]` and `[10**30]` all pass CE on round 5 (exit 0). This does NOT matter before the re-mint:
- Groups values are evidence only; they are NEVER passed to `fchownat`. Only `uid` and `gid` reach the handback's
  `c_uint` chown (R's `own()`), which is exactly why those two carry the 4294967294 bound (4294967295 = `(uid_t)-1` =
  "no change", the fail-open R closed). `groups` has no such sink, so an out-of-range group is not a fail-open.
- The privileged-supplementary-group threat is group 0 (the root group), and CE refuses it (`supplementary group 0`).
  An id above 4294967294 is `nogroup`/`(gid_t)-1`, not a privilege the unit holds; `/proc` reports no larger value.
- So the missing ceiling on `groups` fails no assertion CE makes and opens no fail-open. It is at most one more
  `max(groups) > ID_MAX` line for symmetry — a FOLLOW-UP, not a re-mint blocker. See I-2.

### R4-F5 (T): the same-filesystem bind-mount row — CLOSED, mutant dies

`test_i59f_r5_the_walk_names_a_same_filesystem_bind_mount_on_its_way_up_as_a_mount` passes on round 5 (in the 7-test
run above). It bind-mounts a directory of the root's own filesystem onto the parent the walk climbs to; st_dev is then
identical (asserted in the test), so only the statx mount id can tell. My mutation `V4-mount-by-st_dev-only` (drop the
`or mount_id(at) != mnt` disjunct in `off_the_way`, so a mount is named by st_dev alone) is KILLED by exactly 1 FAILED
test (below), reproducing the builder's row. The verifier's round-4 surviving mutant is now dead.

## Item 4: mutation audit (harness `/tmp/vi59f5/drv/mutate_r5.py`, `run_muts.py`, `run_extra.py`)

Discipline (AF-AP-223): baseline first; KILLED = FAILED>0, ERROR=0, collected==baseline; each mutant restored and its
sha256 re-checked against `wt`. Scoped subsets: C-nonstr (T3, 4 collected), CE-a7 (T, 21 collected), walk (T, 12
collected). No mutant was pointed at a real protected resource; every run is in the throwaway tree on synthetic fixtures.

**All 13 builder rows reproduced as FAILED, each with its stated count** (including the two the brief names,
X-R5-F3-never and X-R5-F4-bound-by-one):

| row | mutation | FAILED (=builder's) |
|---|---|---|
| X-R5-F1-guard | C's non-string-key guard removed | 4 |
| X-R5-F1-ints | guard admits ints (`(str, int)`) | 3 |
| X-R5-F3-every | whole way at every climb (`levels = len(stack)`) | 1 |
| X-R5-F3-never | parent alone at every climb (`levels = 1`) | 2 |
| X-R5-F3-shallow-only | whole way only <= 32 deep | 1 |
| X-R5-F3-unpaid | budget never paid down (`budget -= 0`) | 1 |
| X-R5-F4-groups-zero | drop the supplementary-group-0 refusal | 1 |
| X-R5-F4-groups-shape | drop the groups shape check | 1 |
| X-R5-F4-groups-any | refuse any non-empty Groups line | 1 |
| X-R5-F4-uid-bound | drop the uid upper bound | 2 |
| X-R5-F4-gid-bound | drop the gid upper bound | 2 |
| X-R5-F4-bound-by-one | `ID_MAX = 4294967295` | 4 |
| V4-mount-by-st_dev-only | a mount named by st_dev alone | 1 |

**New mutants I added for round-5 clauses (leaks, boundaries, budget domain):**

| mutant | result | note |
|---|---|---|
| C guard message leaks the key (`{key!r}`) | KILLED (4) | T3 asserts no run of the key |
| C guard message leaks the value | KILLED (4) | T3 asserts no run of the value |
| C guard hardcodes `(int)` for the type | KILLED (2) | bool/null rows catch it |
| C guard behind `if False` | KILLED (4) | placement-before-`is_credential_name` covered |
| CE `max(uid) > ID_MAX` -> `uid[0] >` | **SURVIVED** | see I-4 (test gap: no mixed-list row) |
| CE `max(gid) > ID_MAX` -> `gid[0] >` | **SURVIVED** | same gap |
| CE id bound `>` -> `>=` (4294967294 refused) | **SURVIVED** | see I-5 (no positive 4294967294 row; fail-CLOSED direction) |
| R `CHECK_BUDGET = 1` | KILLED (2) | window too wide |
| R `CHECK_BUDGET = 8` | SURVIVED | equivalent mutant: a smaller budget is still linear and tighter (window test reads the constant from source) |
| R `CHECK_BUDGET = 256` | KILLED (1) | cost bound exceeded |
| R `CHECK_BUDGET = 100000` | KILLED (1) | effectively quadratic; cost test fails |
| R budget threshold `>=` -> `>` | SURVIVED | near-equivalent: one extra climb of window, inside the test's slack |
| R `off_the_way` last frame off-by-one (`- levels + 1`) | KILLED (2) | |

**Survivors named, all judged non-material (I-4, I-5):**
- `max(uid|gid) > ID_MAX` -> `[0] >`: a genuine coverage gap. The A7 table's id-bound rows use `[<over>]*4`, so the
  first element is also over-range; no row uses a mixed list where only a later element is over. Confirmed: under the
  mutant, `uid: [1000, 4294967295, 1000, 1000]` PASSES CE. Immaterial: the record's uid/gid LIST is evidence only and
  is never passed to `fchownat` (only the command-line `HANDBACK` uid:gid is, and R bounds those separately, tested by
  `test_i59f_b4_...` and R's own refusal); uid 0 is caught by `0 in uid` (an `in` test, not `[0]`); an out-of-range id
  is `(uid_t)-1`/nobody, not a privilege. FOLLOW-UP: add one mixed-list row so the bound's `max` is pinned.
- id bound `>` -> `>=`: no test pins that 4294967294 (the largest allowed id) PASSES through the A7 flow, so tightening
  to `>=` is not caught. This is the fail-CLOSED direction (it refuses a legitimate extreme id), so it cannot mint a
  false pass; it is a boundary-precision test gap. FOLLOW-UP.
- `CHECK_BUDGET = 8` and threshold `>` : equivalent / near-equivalent mutants (a different valid budget, or a one-climb
  boundary shift), still linear and still inside the window the comment states. Not defects; the window test correctly
  reads the constant from source, so it grades the invariant, not a magic number.

## Item 2: what else changed (round 4's patch vs round 5's)

`diff -u` of the round-4 bytes (`/tmp/vi59f5/r4`, HEAD + `git show d71197e:.../I59-F.patch`) against round-5 (`wt`),
changed non-context lines per file: **C 5, CE 25, R 40, T3 37, T 144; every other file 0** (`.github/...`, both S0-01
checkers, S0-04's checker, the two S0-05 fixtures, `test_gpu_window.py`, `test_no_laya_in_gates.py`,
`test_s0_04_compression.py`, `test_s0_01_manifest_parse_linear.py` — all unchanged r4->r5). I read all five diffs in
full:

- **C (5 lines):** only the `if not isinstance(key, str): raise Failure(...)` guard in `_walk_node`, before
  `is_credential_name`. No other message or branch touched. R4-F1 only.
- **CE (25 lines):** `ID_MAX = 4294967294`; `if max(uid) > ID_MAX: refuse(...)`; the same for gid; the `if "groups"
  in record:` block; and docstring/comment text (A7 comment, the module docstring). No change to the uid-0/gid-0
  checks, the pin checks, or the shape checks. R4-F4 only.
- **R (40 lines):** `CHECK_BUDGET = 32`; `off_the_way` gains a `levels` parameter and climbs only its top `levels`
  frames; the while-loop earns/spends the budget and passes `levels`; the comment paragraph. **`cleanup`'s `trap ''
  INT TERM` (R:754) and the two top-level `trap ... 130/143` lines (R:776-777) are unchanged** (diff shows no touch).
  R4-F3 only, and the contract's "do not change cleanup's signal disposition" is honoured.
- **T3 (37 lines):** only the `NON_STRING_KEYS` list and `test_a_non_string_key_in_the_provider_block_fails_by_its_type`.
  R4-F1.
- **T (144 lines):** the six new A7 table rows + ids; the `test_i59f_r4_...carries_the_groups` docstring and its planted
  line changed from a populated to an empty Groups line (complemented, not weakened, by the new positive control); the
  new `test_i59f_r5_the_checker_passes_a_groups_record_that_holds_no_0`; the bind-mount test + its helper; the cost and
  window tests + `_chain`/`COUNT_THE_WAY_UP` helpers; and two docstring edits on round-4 walk tests. All within the four
  items.

No behavior change outside R4-F1, R4-F3, R4-F4, R4-F5. Item-2 finding count: none.

## Item 3: the expected reds and the re-mint set

**`validate-ledger integrity` on the patched copy names exactly S0-01 to S0-05.** Run in `/tmp/vi59f5/wt`: S0-01
through S0-05 `INVALID` (attestation-mismatch), S0-06 through S0-12 `PRESENT`. I re-derived the mechanism from
`proof_attestation` directly: the attested inputs that differ from HEAD are S0-01 (`check_acp_conformance.py`,
`build_capture_record.py`), S0-02 (`check_acp_conformance.py`), S0-03 (`check_omniroute_roundtrip.py`,
`check_acp_conformance.py`), S0-04 (`check_compression.py`), S0-05 (`check_egress.py`, the two `unit-identity.json`
fixtures, `run_s0_05_units.sh`); **S0-06 to S0-12 have zero changed inputs.** So the re-mint set is exactly the five,
unchanged from round 4. The test files T3 and T are NOT attested inputs of any proof (confirmed: not in any closure).

**T's 8 failures, single cause F-11, read individually.** `8 failed, 355 passed in 355.50s`, set `9f0502080347`
(matches the builder). The eight:
`test_the_committed_live_root_needs_its_unit_list`, `test_every_spec_leg_behaves_exactly_as_declared`,
`test_the_committed_live_bundle_passes_with_every_line_pinned`, and
`test_a_hostile_copy_of_the_live_bundle_fails_by_name` at `[c2-egress-open]`, `[c1-proxy-new-spelling]`, `[gate-inert]`,
`[override-present]`, `[identity-not-pinned]`. Every message traces to the committed S0-05 evidence lacking a full
identity record (`unit-identity-invalid: buzz-acp unit-identity.json lacks one of unit, pid, exe_realpath, ...`), which
is F-11's single cause: the committed bundle predates the round-4/5 identity grading. It clears when the PC re-capture
writes full records. Confirmed NOT a round-5 regression: round-4 bytes fail the identical set for the identical reason.

**TA's S0-05 row.** `tests/test_attested_inputs.py`: `1 failed, 82 passed`; the one failure is
`test_every_repo_file_a_checker_reads_is_attested[S0-05]`, again the committed-evidence identity gap (F-11). Round-4
bytes fail the same S0-05 row (`1 failed, 11 passed` on the scoped run) — pre-existing, not introduced by round 5.

**Gates re-run here (set ids):** T3 `1 files set=696563f67d3c` -> `225 passed in 42.93s` (221+4, matches). T
`1 files set=9f0502080347` -> `8 failed, 355 passed in 355.50s` (matches). The round-5-only T subset (`-k "i59f_r5 or
i59f_r4_the_walk or bind_mount"`) -> `7 passed, 356 deselected`. I did not re-run the eight unchanged S0-01/S0-04 gate
files (frame-tee, scripted-backend, check-acp, etc.): round 5 changed zero of their bytes (item-2 diff), they are not
in the four-item scope, and re-running them (~7 min) would only re-confirm the builder's pasted counts. Named as a
deliberate skip.

## Finding inventory (no severity filter)

Every finding here is FOLLOW-UP or INFO. None satisfies the whole blocking predicate (contract mapping + canonical
reproduction + material effect + concrete discriminator + task ownership). Reproductions are in `/tmp/vi59f5/drv`.

**I-1 (INFO, pre-existing, not a round-5 change).** C does not grade the provider's own NAME (the key under
`providers`). An int provider name, a wrong string name, and `model.provider: custom:somewhere-else` each PASS (exit 0)
on HEAD, round 4 and round 5 alike. The name then prints in every path-bearing failure line (a chosen label, not a
credential value: the "keys print through paths" class round 1 accepted). Evidence: `r4f1_shapes.py`
int-provider-name rows. Contract mapping: none (R5 folds R4-F1, which is the non-string-key traceback, now closed).
Material effect: none (the name is operator-chosen, carries no secret). Fix (FOLLOW-UP, if wanted): grade the provider
name against the model section's `provider`.

**I-2 (FOLLOW-UP, the builder's NOT-done, the brief asked me to judge it).** CE bounds uid and gid above at 4294967294
but does not bound the `groups` entries: `groups: [4294967295]`, `[4294967296]`, `[10**30]` pass. **Judged immaterial
before the re-mint:** groups values are evidence only and never reach `fchownat` (only the command-line uid:gid do,
which is why those two carry the bound); the privileged case is group 0, which CE refuses; an over-range id is
`(gid_t)-1`/nobody, not a privilege. Reproduction: `r4f4_ce.py` groups-above-idmax rows (exit 0). Contract mapping:
none (R5 brief lists it as NOT-done). Material effect: none. Fix: one `max(groups) > ID_MAX` line for symmetry.

**I-3 (FOLLOW-UP, F-8 resource class, pre-existing shape).** R's handback keeps the full joined path in every stack
frame, so RSS grows with depth: 20.9 MB at 3,300 levels, 108 MB at 10,000, 1,550 MB at 40,000. Reproduction:
`r4f3_measure.py`; a throwaway names-only experiment holds RSS at ~20 MB to 40,000 levels. Contract mapping: none (R5
asked for linear TIME, delivered; memory was not in scope). Material effect: none on the real proof (evidence tree is a
handful of levels); a depth-bomb ceiling only, the F-8 class already a follow-up. Fix: store the name, rebuild the path
only when naming a `left`/`stopped` entry.

**I-4 (FOLLOW-UP, mutation survivor, test-coverage gap).** CE's id bound is `max(uid|gid) > ID_MAX`, but no A7 row uses
a mixed list, so `max(...)` -> `[0]` survives. Confirmed: under that mutant `uid: [1000, 4294967295, 1000, 1000]`
PASSES. Immaterial: the record's id LIST is evidence only (never reaches `fchownat`); uid 0 is caught by `0 in uid` (an
`in` test, unaffected); an over-range id grants nothing. Reproduction: `run_extra.py` N-CE-uid-max-to-0 / N-CE-gid-max-to-0.
Fix: add a mixed-list A7 row so `max` is pinned.

**I-5 (FOLLOW-UP, mutation survivor, boundary-precision gap).** No test pins that 4294967294 (the largest allowed id)
PASSES the A7 flow, so tightening `>` to `>=` (which would wrongly refuse it) survives. This is the fail-CLOSED
direction — it cannot mint a false pass. Reproduction: `run_extra.py` N-CE-uid-bound-ge. Fix: add a positive
4294967294 A7 row.

**I-6 (FOLLOW-UP, the R4-F6 window class, the brief asked "can a mover use it").** Deeper than CHECK_BUDGET levels, the
whole-way check fires at most every `ceil(d/32)` climbs; between checks the walk hands back entries below a moved
ancestor at their current location, which can be outside the root. Reproduced (`r4f3_window.py`): at d=3300 with a
mover, up to ~197 decoy files and a freshly planted file were chowned to the invoker outside the root before the stop;
the number of climbs to the stop tracks `ceil(d/32)`, as R's comment states. **Not a re-mint blocker and not a round-5
regression:** (a) for the REAL evidence tree (a handful of levels, well under 32) round 5 checks the whole way at EVERY
climb — behaviorally identical to round 4 (measured: 16.5 opens/level at d=32, climbs-after-move=2 at d=33 = the bound);
(b) it requires a process actively renaming the tree DURING teardown, which the runner's model (F-5) excludes (no unit
or canary alive at handback); (c) round 4 already had a one-climb window of the same shape, and the coordinator ruled
this the R4-F6 follow-up. The window only widens for pathologically deep trees, which the real capture never produces.
Contract mapping: none (R5 brief states the window as accepted design, R4-F6's class). Material effect on the real
proof: none. Fix (FOLLOW-UP, if the deep-tree window is ever a concern): a smaller budget, or an absolute cap on tree
depth entered.

## Item 5: what must hold before the re-mint and the PC re-capture (updated from round 4)

1. **Order.** S0-01 to S0-04 can re-mint now (their attested inputs changed; the dry-run legs are unchanged except
   S0-04's positive stdout). **Do not run `proof-runner` for S0-05 before the PC re-capture is committed:** its leg 1
   fails on the committed no-identity evidence and `proof-runner` deletes `proofs/S0-05/result.json` on a leg failure
   (round-4 measurement). This is the same order as round 4.
2. **The re-mint set is exactly S0-01 to S0-05.** Re-derived here two ways: `validate-ledger integrity` names those
   five INVALID and S0-06..12 PRESENT; `proof_attestation` shows zero changed inputs for S0-06..12. S0-02 is in the set
   because it attests S0-01's `check_acp_conformance.py`.
3. **The re-capture** runs the ROUND-5 runner (its handback and its A7 record). The re-captured `unit-identity.json`
   must carry a `gid` line and, since round 5, a `groups` line that CE now grades: with `--clear-groups` the Groups
   line is empty, which CE passes (the empty-groups control). Then re-pin T's `LIVE_OUTPUT` (R4-F2) to the new bundle's
   output, or T stays red on a line mismatch. Then re-mint S0-05.
4. **PC only (NOT run here: PC only).** The PC's `setpriv --clear-groups`, the real uid/gid/groups the units run as,
   the real statx mount-id path on the PC kernel, and real CI. This sandbox verified the checker/runner logic on
   synthetic fixtures; the live capture is the PC's.
5. **Decisions already made (folded this round).** R4-F1, R4-F3, R4-F4 and R4-F5 are in the patch, so the owner signs
   once. The five FOLLOW-UPs above (I-1..I-6, minus the two that are INFO) touch attested files (CE, R, C) and so, if
   ever taken, want their own re-mint — none is worth a second signature now; each is immaterial to the signed claim.

## GATE

Blocking predicate (skill `contract-gate`, D-031) with D-034's CORE-BLOCKING rule: **no finding meets all five
conditions.** Every folded item is reproduced through the real production path at the pin:
- R4-F1 closed: 22 key shapes fail by type, no traceback, no value/key leak (`r4f1_shapes.py`); red on round-4 bytes.
- R4-F3 closed: the handback is O(d) (~33 opens/level, flat to 40,000 levels; round 4 was O(d^2)); the window is
  bounded as R's comment states, and identical to round 4 for the real shallow tree.
- R4-F4 closed: CE grades the Groups line and bounds uid/gid; 22 cases correct; red on round-4 bytes. The groups
  ceiling (I-2) is immaterial.
- R4-F5 closed: the same-filesystem bind-mount row passes and kills V4-mount-by-st_dev-only.
- All 13 builder mutant rows reproduce as FAILED with their exact counts; the four survivors I found are equivalent
  mutants or immaterial fail-safe-direction test gaps.
- The expected reds are exactly F-11's cause (T's 8, TA's S0-05 row), and the re-mint set is exactly S0-01..S0-05.
- No behavior change outside the four items (item-2 diff: only the five files, only the four items' lines).

**Recommendation: MERGE-READY-WITH-FOLLOWUPS.** Six follow-ups (I-1..I-6), all immaterial to the signed claim and none
owed a repair loop. Not reproduced here (stated on the recommendation line): the PC venue — the re-capture, its
`setpriv --clear-groups`, the live uid/gid/groups, the PC-kernel statx mount-id, and real CI; those are the landing
steps in item 5, to run on the PC before the owner signs.

## Host state after (2026-09-29T00:39:19Z)

`/tmp/vi59f5/` and everything under it are removed. `ip netns list` 0 lines; iptables stable form `0528d077bca3781a`
and mount hash `2dd93d06015feb4d` (27 mounts), both equal to the baseline before I started; no uid-65534 process; the
two `/tmp/e3-*` that predate me remain. Every bind/tmpfs mount my drivers or the mutation harness made was unmounted by
its path in the run that made it (no `/tmp/vi59f5` mount remained before removal). I wrote nothing outside `/tmp/vi59f5/`
but this report, and made no git write.
