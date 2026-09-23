# E3-R1 — report (task #175, lane s0-05-e3-r1, sandbox, agent `code-implementer` on claude-opus-5-5)

STATUS: COMPLETE (2026-09-23 11:3xZ). R1, R2 and R3 are built and GREEN; the gates below are pasted.
- Root: `263 passed` twice. Non-root: `204 passed, 59 skipped`.
- Mutants: 13 run, 12 KILLED, 1 SURVIVED. The survivor, M1b, is expected: it is VERIFY-E3's one-line repair, which
  section 2 shows to be insufficient.
- The final census reads empty.
- The headline finding (D1): a second signal microseconds after the first still aborts ALL of `cleanup` when only
  `cleanup` ignores INT and TERM. So each stop handler ignores them too.
Key: PC = `proofs/S0-05/tools/pc/run_s0_05_units.sh`, T = `tests/test_s0_05_egress.py`, L = `proofs/S0-05/netns_lib.sh`.
Nothing in this lane ran on the PC.

## 1. PREMISE — re-measured (sandbox, uid 0, before any edit)

````
$ date -u; git rev-parse --short HEAD; git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
Wed Sep 23 10:36:50 UTC 2026
a361204
de33838
$ git diff 2ebd486 HEAD -- proofs/S0-05 tests/test_s0_05_egress.py | wc -l      # HEAD a361204 is 2 commits of docs past the PIN
0
$ git diff -- proofs/S0-05 tests/test_s0_05_egress.py | wc -l                     # working tree vs HEAD
0
$ for f in PC T; do echo "$(git rev-parse --short=12 HEAD:$f) $(git hash-object $f | cut -c1-12) $(wc -l <$f) $f"; done
5d58951f392a 5d58951f392a 578 proofs/S0-05/tools/pc/run_s0_05_units.sh
50bf20a92986 50bf20a92986 2999 tests/test_s0_05_egress.py
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_05_egress.py
1 files set=9f0502080347
$ baseline census (before anything of mine exists)
netns: (none) · /etc/netns: empty · veth: (none) · nat PREROUTING: -P PREROUTING ACCEPT · /run/s0-05-egress: empty
route_localnet: all=0 default=0 eth0=0 ifb0=0 ifb1=0 lo=0 · df /tmp: 1.5G free
````

PREMISE HOLDS: both boundary files are byte-identical to the PIN blobs the brief lists (5d58951f392a, 50bf20a92986) and to
2ebd486 (VERIFY-E3's tree); the set id is 9f0502080347. The sandbox baseline matches the dispatch baseline.

## 2. Design measurement before any edit: the ignore's placement (standalone bash probes, `/tmp/e3r1/probe/`)

Code intel: `scripts/lane_context.sh -q 'how does the S0-05 runner clean up and census S0-01' -s cleanup -s _s0_01_census -o
/tmp/e3r1/pack.md PC` ran (67 lines); graft indexes no definitions under `proofs/S0-05/tools/pc/` ("unmapped — graft ask
unavailable"), crg found `_s0_01_census` with 0 tests_for, ripwire 0 callers (blind to shell). Fallback instrument: the file read
whole (578 lines) plus the library's `_egress_ns_teardown` / `egress_relay_reach_del` (L:324-410).

VERIFY-E3's one-line repair (`trap '' INT TERM` as `cleanup`'s first line) closes F3's measured shapes, where the second signal
lands long after `cleanup` began. A second TERM that lands MICROSECONDS after the first is a different case: bash records it as
pending, and runs its handler at the next command boundary. If that boundary comes after `exit 143` entered the EXIT trap but
before `cleanup`'s first line, the handler's own `exit` abandons the EXIT trap, so no teardown step runs at all. Measured with a
minimal script shaped like `cleanup` and its traps at PC@de33838:322-336 (`f3c.sh`: `cleanup` writes step1 and step2; the shell waits in `wait`; a Python driver
sends TERM, busy-waits <gap> µs, sends TERM again; 60 trials per cell):

````
$ timeout 300 python3 /tmp/e3r1/probe/window.py        (design 0 = PIN; 1 = ignore as cleanup's first line;
                                                         2 = design 1 + `trap "" INT TERM` as each handler's first command)
design=0 gap_us=50  rc=143 cleanup=none count=1      design=0 gap_us=100 cleanup=none 33, partial 7    design=0 gap_us=200 none 2, partial 10
design=1 gap_us=20  rc=143 cleanup=none count=1      design=1 gap_us=50  rc=143 cleanup=none count=1
design=1 gap_us=100 rc=143 cleanup=full count=34     design=1 gap_us=100 rc=143 cleanup=none count=26
design=1 gap_us=0, 200, 400: full 60/60 each
design=2 gap_us=0, 20, 50, 100, 200, 400: rc=143 cleanup=full count=60 (each; 0 aborts in 360)
````

So this lane builds design 2: the ignore is the first command of `cleanup` AND of each stop handler. The mechanism is INFERRED
from bash's pending-trap handling, not observed: a second signal pending before the handler's ignore runs a nested handler,
which sets the same ignore and exits before the EXIT trap starts, so `cleanup` still runs whole. MEASURED: 0 of 360. The one-line repair alone is NOT sufficient (26 of 60 at 100 µs).
Two negative results, kept: a TERM and an INT pending together while the shell waits on a foreground `sleep 1`, or in `wait`, gave
rc 143 with both steps in all three designs (inferred: bash dropped the pending INT; that probe cannot open the window). A first
probe whose handler re-sent TERM to itself recursed until bash segfaulted (rc 139). It was malformed, and it proves nothing.

## 3. RED on the PIN bytes (PC blob 5d58951f392a, unmodified; T with the new and amended tests)

````
$ echo "PC vs HEAD: $(git diff -- PC | wc -l) lines; blob $(git hash-object PC | cut -c1-12)"
PC vs HEAD: 0 lines; blob 5d58951f392a
$ mkdir -p /tmp/e3r1/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e3r1/bt -k "e3r1 or test_a2_s0_01_tree_change_fails_the_leg" --tb=short > /tmp/e3r1/red.log 2>&1
RED pipestatus=1
13 failed, 250 deselected in 82.67s (0:01:22)
(each test's first failing assertion, from /tmp/e3r1/red.log)
test_a2_s0_01_tree_change_fails_the_leg                          assert (['/tmp/e3-_yu...ers/v2-run-1'] == ['v2-run-1']      (A2': relative path)
test_e3r1_r1_b_...[term-then-term-to-the-pid]    ({'netns': True, 'veth': True, 'etc_netns': True, 'owner_dir': ['s0-05-hermes-acp.owner']}, 143, ...)
test_e3r1_r1_b_...[term-then-int-to-the-pid]     ({'netns': True, 'veth': True, 'etc_netns': True, 'owner_dir': ['s0-05-hermes-acp.owner']}, 130, ...)
test_e3r1_r1_b_...[int-then-term-to-the-group]   ({'netns': True, 'veth': True, 'etc_netns': True, 'owner_dir': ['s0-05-hermes-acp.owner']}, 143, ...)
test_e3r1_r1_c_...[term-to-the-pid]              ({'all': '0', 'default': '0', 'ehda7d8593': '1'}, {'all': '0', 'default': '0', 'ehda7d8593': None}, ...)
test_e3r1_r1_c_...[term-to-the-group]            (['-A PREROUTING -d 10.201.219.1/32 -i ehda7d8593 -p tcp -m tcp --dport 3999 -j DNAT --to-destination 127.0.0.1:3999'] ...)
test_e3r1_r1_c_...[int-to-the-group]             (['-A PREROUTING -d 10.201.219.1/32 -i ehda7d8593 -p tcp -m tcp --dport 3999 -j DNAT --to-destination 127.0.0.1:3999'] ...)
test_e3r1_r1_a_signal_while_cleanup_reaps_...[pid]    ({'netns': False, 'veth': False, 'etc_netns': False, 'owner_dir': ['s0-05-hermes-acp.owner']}, 143, ...)
test_e3r1_r1_a_signal_while_cleanup_reaps_...[group]  ({'netns': True, 'veth': False, 'etc_netns': False, 'owner_dir': ['s0-05-hermes-acp.owner']}, 143, ...)
test_e3r1_r2_each_in_place_write_fails_the_leg_by_name                assert ({'buzz-acp.pi...frames.jsonl'} <= set()     (nothing named: F2)
test_e3r1_r2_a_symbolic_link_is_recorded_by_its_target_never_followed assert ['.'] == ['link-retargeted']       (.markers' times named, the link not)
test_e3r1_r2_an_unchanged_tree_passes                                 assert ['/tmp/e3-7t6...ned/.markers'] == []  (times compared)
test_e3r1_r2_a_census_that_cannot_be_taken_fails_the_leg              no census-failed line; NotADirectoryError in snap, then JSONDecodeError
$ census after the RED run: netns [] veth [] etc_netns [] owner_dir [] · nat PREROUTING -P PREROUTING ACCEPT · route_localnet all 0

$ /root/venv-agent-factory/bin/python -B /tmp/e3r1/pin_census_crash.py   (the PIN runner, the base a regular file, via T's _census_leg)
rc 1 | checker ran: True | census file: None
stderr tail: json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
````

Every RED is the PIN's behaviour, not an import error. Each R1 row shows the leftover: the namespace set, a dead runner's
owner record, `route_localnet=1` or D-051's DNAT itself. Rows b-2 and b-3 also show the wrong status (the second signal's).
The last probe confirms the fail-open that the census test's docstring claims: at the PIN a crashed census wrote no census file,
and the run still went on to its checker.

## 4. GREEN, and what changed per contract line (PC 578 -> 641 lines, T 2999 -> 3367 lines)

````
$ bash -n PC ; echo "bash -n rc=$?"
bash -n rc=0
$ mkdir -p /tmp/e3r1/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e3r1/bt -k "e3r1 or test_a2_s0_01_tree_change_fails_the_leg" --tb=short > /tmp/e3r1/green1.log 2>&1
GREEN pipestatus=0
13 passed, 250 deselected in 75.45s (0:01:15)
````

**R1 (F3): a second INT/TERM cannot abort `cleanup`.** The design is measured in section 2 (design 2).
- PC:383 `trap '' INT TERM`: `cleanup`'s first command. It covers a run that ends on its own, and every command `cleanup`
  starts inherits the ignore (the held `iptables -D`, `ip netns del`, `sleep`).
- PC:404-405 `trap 'trap "" INT TERM; exit 130' INT` and `... exit 143' TERM`: each stop handler ignores both signals
  BEFORE its `exit`. This closes the microsecond window that the one-line repair leaves open (section 2, and M1b below).
  PC:403 `trap cleanup EXIT` is unchanged, so R4 keeps its shape: `cleanup` runs once, on EXIT, with 130 or 143.
- Tests (all drive the REAL runner, each in its own session with pgid = pid):
  - T:3057 `test_e3r1_r1_b_a_second_signal_while_cleanup_waits_for_a_slow_unit`, three cases:
    `[term-then-term-to-the-pid]`, `[term-then-int-to-the-pid]`, `[int-then-term-to-the-group]`. Shape (b): the unit's
    SIGTERM handler takes 3 s (T:3023 `SLOW_STOP`), and the second signal fires on the unit's marker that proves `cleanup`'s
    TERM reached it.
  - T:3099 `test_e3r1_r1_c_a_second_signal_inside_the_relay_reach_removal`, three cases: `[term-to-the-pid]`,
    `[term-to-the-group]`, `[int-to-the-group]`. Shape (c): the pair, with a PATH `iptables` hold on the teardown's
    `-t nat -D` (T:2415 `_iptables_shim` gained a `match` argument, T:2423; the default keeps its three callers unchanged).
  - T:3147 `test_e3r1_r1_a_signal_while_cleanup_reaps_at_the_runs_own_end_changes_nothing`, `[pid]` and `[group]`: the
    natural-exit path, where no handler ran and only PC:383 `trap '' INT TERM` protects. It is the one killer of M1a.
  - Each asserts, after exit: the census `CLEAN` (no namespace, veth, `/etc/netns/<ns>` or owner record); no nat rule naming
    the host interface; `route_localnet` of all, default and the host interface equal to its value before the run (T:3048
    `_route_localnet_state`); the FIRST signal's status (T:3019 `STOP_RC`; 1 on the natural path, the checker's own
    `exit 1 per contract`); no units.json, no census file and no checker after a stop.

**R2 (F2, A2 amended to A2'): the census covers every entry under `.markers`.**
- PC:211-285 `_s0_01_census` (`snap` and `compare`):
  - `record(path)` (PC:230) stores type, mode, uid, gid and size for every entry; a regular file adds its `sha256` (PC:247); a
    symbolic link adds its `target` (PC:235). It uses `lstat` and opens files with `O_NOFOLLOW | O_NONBLOCK` (PC:238).
  - `census()` (PC:249) walks the whole tree without following links, and `"."` is `.markers` itself. An absent tree reads
    `{}` (PC:253: `absent on this venue`).
  - `side(entries)` (PC:266) gives each side's entry count and one sha256 over its sorted records.
    PC:275 `sides["before"] == sides["after"]` makes the verdict the two sides' count and digest; the names come from the per-entry diff.
  - The census file holds `base`, `tree`, `before`, `after`, `changed` and `changed_records` (PC:280: the CHANGED
    entries only).
  - Each changed entry's path on disk is printed as raw bytes by `sys.stdout.buffer.write` (PC:284).
- PC:407 `CENSUS_BEFORE=$(_s0_01_census snap)`: the before census lives in memory only, never on disk or in the evidence.
- PC:591-595 `compare` gets it on fd 3 through a here-string. At the PC's scale (33,865 entries, a synthetic tree), `snap`
  took 0.5-0.6 s through `$()`, `compare` 0.83 s, and the census file was 621 bytes.
- PC:631-634: a census that could not be taken fails the leg (`census_failed`); this is an addition, see DISCREPANCIES D2.
  PC:636: the existing line, `s0-01-tree-changed: $path`.
- Tests:
  - T:3254 `test_e3r1_r2_each_in_place_write_fails_the_leg_by_name`: the four writes, the same-size pid rewrite, full records;
    forty untouched entries are counted and never listed ("the census file carries no full entry list").
  - T:3299 `test_e3r1_r2_a_symbolic_link_is_recorded_by_its_target_never_followed`.
  - T:3339 `test_e3r1_r2_an_unchanged_tree_passes`: new times plus a byte-identical new inode (A2' compares neither).
  - T:3358 `test_e3r1_r2_a_census_that_cannot_be_taken_fails_the_leg`: the addition.
  - T:2082 `test_a2_s0_01_tree_change_fails_the_leg` changed its expectations for A2' (T:2110-2118, `changed_records`): a relative path in
    the census file, and counts instead of the whole `after` list.
  - The helpers are T:3183 `_s0_01_tree`, T:3203 `_entries_under` (an independent `os.walk` count) and T:3218 `_census_leg`.

**R3 (text).**
- PC:44-45 limit 2 now says `cleanup` cannot be cut short by a second SIGINT or SIGTERM (F19's limit-2 part).
- PC:56-58: a new limit 7 (`S0-01 census (A2')`) says what the census compares and does not compare.
- PC:211-222: the census comment (`the coordinator's amendment of A2`) is rewritten for A2'.
- PC:379-381: the comment above `cleanup` (`its first command ignores SIGINT and SIGTERM`).
- PC:395-402: the comment above the traps (`a SECOND SIGINT or SIGTERM`) says what a second signal does and what stays open (a stop in the microseconds at
  the run's own end, and SIGKILL).
- PC:591-592: the compare comment (`the census after the last unit`).

## 5. Mutation audit (scratch copies only; the harness is `/tmp/e3r1/mut/mut.py`)

Method: a fresh copy of the base per mutant, with ONE exact replacement per pair; each old text had to occur exactly once, and
none was refused. Each mutant then passes `bash -n` and a compile of the census heredoc, and the WHOLE file must collect 263.
Then the killer selection runs WITHOUT `-x`, so every killing test is listed. KILLED = rc 1 with FAILED tests; SURVIVED = rc 0.
AF-AP-138 comes first: every killer selection runs on the UNMUTATED base.

````
$ /root/venv-agent-factory/bin/python -B /tmp/e3r1/mut/mut.py baseline        (11:12:21Z)
cmp proofs/S0-05/tools/pc/run_s0_05_units.sh: identical
cmp tests/test_s0_05_egress.py: identical
cmp proofs/S0-05/netns_lib.sh: identical
cmp proofs/S0-05/check_egress.py: identical
cmp proofs/S0-01/pins.py: identical
collect on the base: 263 tests collected in 0.41s
UNMUTATED base, every killer selection (e3r1_r1, e3r1_r2, A2): rc=0 | 13 passed, 250 deselected in 75.13s (0:01:15)
````

| Mutant | What it does | Compiles | Collected | Verdict and killers (FAILED) |
|---|---|---|---|---|
| M1 | the protection removed: all three ignores gone (`trap '' INT TERM` at PC:383; the handlers' ignore before `exit 130` and `exit 143` at PC:404-405), which gives the PIN's trap lines | bash -n rc=0 + heredoc compiles | 263 | KILLED, all 8 `e3r1_r1` tests fail (b x3, c x3, natural end x2), 25.52s |
| M1a | `cleanup`'s own ignore removed (PC:383 `trap '' INT TERM`); the handlers keep theirs | same | 263 | KILLED by `..._reaps_at_the_runs_own_end_changes_nothing[pid]` and `[group]` only; b and c pass, because the handlers' ignore covers them |
| M1b | the handlers' ignore removed (PC:404-405, before `exit 130` and `exit 143`); `cleanup` keeps its own. This is VERIFY-E3's one-line repair | same | 263 | **SURVIVED** (8 passed). EXPECTED: only a second signal a few µs after the first reaches the gap, and no deterministic test through the real runner can place one there. The standalone probe of section 2 separates them: 26 of 60 aborts at 100 µs for this design, 0 of 360 for PC's |
| M2 | the protection scoped to INT only, in all three places | same | 263 | KILLED, 6 fail: b `[term-then-term-to-the-pid]` and `[int-then-term-to-the-group]`, all three c cases, both natural-end cases. The two INT-second shapes pass: INT is still ignored |
| M3 | caught, not ignored (`trap : INT TERM` in all three places): bash goes on, but children get the default disposition | same | 263 | KILLED by c `[term-to-the-group]`, c `[int-to-the-group]` and natural-end `[group]`: the held `iptables -D` / `ip netns del` dies. This pins "children inherit the same protection" |
| M4 | the census back to directory `lstat` only (`.markers` + each `v2-*` directory) | same | 263 | KILLED by the four-writes, symlink and unchanged-tree tests |
| M5 | the sha256 dropped from file records (PC:247 `digest.hexdigest()`) | same | 263 | KILLED by `test_e3r1_r2_each_in_place_write_fails_the_leg_by_name`: the same-size pid rewrite goes unseen |
| M6 | symbolic links followed (`os.stat`, and no `O_NOFOLLOW`) | same | 263 | KILLED by `test_e3r1_r2_a_symbolic_link_is_recorded_by_its_target_never_followed` |
| M7a | the digest computed but never compared: the sides always read equal (PC:275 `sides["before"] == sides["after"]` becomes `True`) | same | 263 | KILLED by the four-writes and symlink tests |
| M7b | the digest computed but never compared: the sides never read equal (PC:275 `sides["before"] == sides["after"]` becomes `False`) | same | 263 | KILLED by `test_e3r1_r2_an_unchanged_tree_passes` (named ".") |
| M8 | extra: times compared (`st_mtime_ns` in the record) | same | 263 | KILLED by the unchanged-tree, four-writes and symlink tests |
| M9 | extra: a census that could not be taken no longer fails the leg (PC:631-634, the `census_failed` branch, removed) | same | 263 | KILLED by `test_e3r1_r2_a_census_that_cannot_be_taken_fails_the_leg` |
| M10 | extra: the census file also holds the whole after-list | same | 263 | KILLED by `test_e3r1_r2_each_in_place_write_fails_the_leg_by_name` (the key set, and "untouched" appears in the file) |

Tally: 13 mutants. 12 KILLED; 1 SURVIVED (M1b), expected and explained. The census after each batch read netns [], veth [],
/etc/netns [], owner dir [], nat `-P PREROUTING ACCEPT`.

## 6. Gates (the brief's, pasted; after every edit)

````
$ mkdir -p /tmp/e3r1/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e3r1/bt | tail -1; rm -rf /tmp/e3r1/bt
Wed Sep 23 11:18:44 UTC 2026
263 passed in 238.11s (0:03:58)
ROOT1 pipestatus=0
Wed Sep 23 11:22:48 UTC 2026
263 passed in 241.35s (0:04:01)
ROOT2 pipestatus=0

$ rm -rf /tmp/e3r1nr && mkdir -p /tmp/e3r1nr && chmod 1777 /tmp/e3r1nr && setpriv --reuid=65534 --regid=65534 --clear-groups env PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_s0_05_egress.py -q -p no:cacheprovider --basetemp=/tmp/e3r1nr/bt | tail -1
204 passed, 59 skipped in 9.31s
NONROOT pipestatus=0

$ bash -n proofs/S0-05/tools/pc/run_s0_05_units.sh ; echo "bash -n rc=$?"
bash -n rc=0
$ /root/venv-agent-factory/bin/python -m pyflakes tests/test_s0_05_egress.py ; echo "pyflakes rc=$?"
pyflakes rc=0
$ python3 scripts/ap_screen.py --tests tests/test_s0_05_egress.py
--- TEST_SCREEN over 1 path(s): 26 hits over 1 files ---          (the PIN file: 24 hits)
$ diff of the hit TEXTS, PIN vs now (line numbers stripped; --limit 1000 on both):
>     tests/test_s0_05_egress.py: assert "untouched" not in census_file.read_text()                 # counted on both sides, never lis
>     tests/test_s0_05_egress.py: assert (outside / "dir" / "new-file").exists() and "longer" in (outside / "target.txt").read_text()
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 40 files scanned, clean
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_05_egress.py
1 files set=9f0502080347
$ command -v shellcheck
shellcheck: absent
````

Counts: root `263 passed` twice. That is the premise floor `251 passed` plus the 12 new root tests (b 3, c 3, natural end 2,
census 4). Non-root `204 passed, 59 skipped`: the floor's 204 pass, and the 12 new tests are root-only, so they skip (47 + 12).
Both new ap_screen hits are AF-AP-80's mechanical signature (`in <path>.read_text()`), and both are false positives: neither
reads source text. T:3284 `census_file.read_text()` reads the runner's REAL output (the census file). Its property, "no full entry list", is a property of
that file, and M10 (the whole after-list written) is killed by it. T:3316 reads the files the unit wrote behind the links (`target.txt`), as
the check that the instrument fired.

## 7. DISCREPANCIES (flagged; none is a silent edit)

- **D1 — VERIFY-E3's one-line repair is NOT sufficient; this lane builds design 2 (measured, section 2).** With
  `trap '' INT TERM` only as `cleanup`'s first line, a second TERM landing 20-100 µs after the first aborted the WHOLE
  `cleanup`: no step ran, in 26 of 60 trials at a 100 µs gap. The handler's `exit` runs at bash's next command, which can
  come before `cleanup`'s first line. The same ignore as each handler's first command gave 0 aborts in 360. Consequence for
  the registry: AF-AP-145's fix text (docs/INCIDENT-LOG.md:501, "`trap '' INT TERM` as cleanup's first line") and task #176
  (`harness-ports/bin/qwen-matrix.sh`, the same three traps) need the handler half too. The registry is outside this lane's
  boundary, so the coordinator decides. The deterministic suite cannot separate the two designs: M1b SURVIVES (section 5).
  The standalone probe is the only discriminator; it is reproduced below so it outlives this lane's scratch.
- **D2 — an addition to A2': a census that cannot be taken fails the leg** (`census_failed`, PC:591-595 and PC:631-634; stderr
  `=== S0-01's tree census failed (exit <n>): the leg FAILS ===`; T:3358). A2' names no behaviour for a census error. At the
  PIN a crashed census left `census_changed` empty and the run went on to its checker (measured, section 3). This lane's census
  reads every file's bytes, so it has more ways to fail than the PIN's `lstat`. "Absent" stays as today: only a missing
  `.markers` (FileNotFoundError). An ENOTDIR base, an unreadable file, or an entry that changes type mid-census fails the leg.
  The E3 operator recipe (E3-report.md:447 lists `s0-01-tree-changed` only) has no row for this line: the coordinator's
  update.
- **D3 — a decision the brief left open: the printed form of `<path>`.** The stderr line keeps TODAY's form: the path on disk,
  absolute. So the existing assertion `s0-01-tree-changed: {v2}` is unchanged, and the operator reads the file to inspect.
  The census file records paths relative to `.markers`, as A2' says; the two join through `base`.
- **D4 — the contract's two lines meet at one extreme.** "The full before and after records of the CHANGED entries" and "it
  never holds the whole entry list" collide when a unit changes EVERY entry. Then the changed records ARE the whole list. The
  build follows the first line (changed entries only, uncapped); "never" holds whenever at least one entry is unchanged.
- **D5 — `.markers` itself is an entry (`"."`).** A2' says "every entry under `.markers`"; the PIN's census also covered
  `.markers` itself, so this keeps that coverage: a chmod of `.markers` fails the leg. On a filesystem where a directory's
  size counts its entries (btrfs on the PC), adding a file also names its parent directory; the four-writes test allows
  exactly that parent (`logs`), measured on ext4 here.
- **D6 — text added beyond the letter of R3:** declared limit 7 (PC:56-58, `S0-01 census (A2')`: what the census compares and what it does not).
  The comment above the traps also names what stays open: a stop in the microseconds between the run's own end and
  `cleanup`'s first command, and SIGKILL. F19's other parts stay issue #39's: limit 3's C0 text, the SIGKILL residue and the
  stop latency in the header.
- **D7 — docs outside the boundary now describe the superseded census:** E3-report.md:173 (the map row "lstat of `.markers`
  + every `v2-*` dir"). E3-report.md:424 (`s0-01-census.json` with `"changed": []`) stays true. Read-only here.
- **D8 — `ap_screen --tests`: 2 new hits, both AF-AP-80 signature false positives** (section 6).

The window probe (D1), as run (minimal script shaped like `cleanup` and its traps at PC@de33838:322-336; `D` is the design, `LOG` a file):

````
f3c.sh:  cleanup() { [ "$D" -ge 1 ] && trap '' INT TERM; echo step1 >> "$LOG"; echo step2 >> "$LOG"; }
         D=$1; LOG=$2; : > "$LOG"; trap cleanup EXIT
         if [ "$D" = 2 ]; then trap 'trap "" INT TERM; exit 130' INT; trap 'trap "" INT TERM; exit 143' TERM
         else trap 'exit 130' INT; trap 'exit 143' TERM; fi
         echo ready > "$LOG.ready"; sleep 5 & wait $!
window.py: per design 0/1/2, per gap 0/20/50/100/200/400 µs, 60 trials: start f3c.sh, wait for .ready + 10 ms,
         os.kill(pid, SIGTERM); busy-wait <gap> µs; os.kill(pid, SIGTERM); classify the steps full / partial / none
````

## 8. Self-attack: the three likeliest ways this change is wrong, and how each was checked

1. **The ignore changes the FIRST stop (R4) or leaks into a unit.** If a unit ever inherited SIG_IGN for TERM, the
   teardown's TERM would not stop it. Checked:
   - Units launch only inside the main loop. A handler's `exit` ends that loop, and `cleanup` runs only on EXIT, so no unit
     can start under the ignore.
   - The existing R4 and X4 tests pass unchanged in both root runs: `test_e3b_r4_sigint_stops_the_runner_with_130`,
     `..._a_stop_in_the_first_leg_starts_no_second_leg` (exactly one `netns del` after STOP), and
     `test_x4_runner_cleanup_reaps_its_own_namespace_at_exit`.
   - The (b) cases pin the first signal's status against a different second signal: 143 after an INT, 130 after a TERM.
2. **The census passes a changed tree.**
   - The verdict is the count and the digest over records of type, mode, uid, gid, size, sha256 and target.
   - The four VERIFY-E3 writes, a same-size rewrite and a retargeted link are each named (T:3254 `each_in_place_write`, T:3299 `symbolic_link_is_recorded_by_its_target`).
   - M4-M7a and M10 are killed.
   - Not compared, by A2' or by declared limit 7: times, inodes, link counts, xattrs/ACLs, a device node's rdev, and a
     change undone before the census after.
   - Checked beyond the tests on synthetic trees: a FIFO in the tree never blocks; a non-UTF-8 name is recorded and printed
     raw; a symlinked `.markers` or a directory link is not entered; an absent tree reads `entries: 0`.
3. **The tests pass for the wrong reason (a hollow green).**
   - The R1 tests assert that the runner is still alive right before the second signal (`runner.poll() is None`). The
     second signal fires only on a marker that proves `cleanup` is mid-step: the unit's TERM marker, or the shim's hold
     marker (`held.read_text() == "held\n"`).
   - All 8 R1 tests were RED on the PIN with the leftover shown, and M1 turns all 8 red.
   - The R2 tests assert that their instrument fired: the new inode, `st_mtime == 1`, and the bytes written behind the links.
   - Every count is checked against an independent `os.walk` count (T:3203 `_entries_under`).
   - Timing: the (c) and natural-end holds are 2 s and the (b) handler 3 s, while the test polls every 0.1 s. These tests were
     green in 4 separate runs (GREEN, the mutant baseline, ROOT1, ROOT2).
   - Residual: M1b survives by construction (D1).

## 9. NOT-done (first-class)

- The PC live run is the coordinator's, with the owner's sudo. Nothing here ran on the PC; the census at the PC's scale ran
  on a synthetic 33,865-entry tree in the sandbox only. Its timing, on the PC's btrfs and with the real S0-01 tree, is not
  measured.
- Issue #39's findings are untouched: F1, F4-F18, F20, and F19 except its limit-2 part (limit 3's C0 text, the SIGKILL
  residue and the PID-directed stop latency in the header).
- The microsecond window at the run's OWN end is declared, not closed (PC:400-402). Closing it would mean `cleanup` running
  inside the handlers (the `pc-lane.sh` pattern AF-AP-145 names). That changes R4's shape, so it was not built.
- M1b has no deterministic killer (D1).
- AF-AP-145's text and the qwen-matrix runner (task #176) are outside this boundary (D1).
- No commit, stage or push. Only the two boundary files and this report were written in the repository.

## 10. The report lint (the brief's floor: --min-refs 12), three rounds, then paste and finish

````
$ python3 scripts/report_lint.py --min-refs 12 --map PC=proofs/S0-05/tools/pc/run_s0_05_units.sh --map T=tests/test_s0_05_egress.py tasks/briefs/s0-05-support/E3-R1-report.md --root .
round 1: report_lint: 63 refs — OK 29, NEAR 4, MISS 18, UNCHECKABLE 12, UNRESOLVED 0 (worktree)
round 2: report_lint: 63 refs — OK 61, NEAR 0, MISS 1, UNCHECKABLE 1, UNRESOLVED 0 (worktree)
round 3: report_lint: 63 refs — OK 62, NEAR 0, MISS 0, UNCHECKABLE 1, UNRESOLVED 0 (worktree)
````

Round 1's misses were correct line numbers whose report line carried no token from the cited line. The fixes added one token
copied from each cited line. The two citations of the PIN's trap lines are now pinned to the PIN revision (`PC@de33838`). The
one UNCHECKABLE is the absent-tree citation in section 4. Its backticked phrase is on the cited line, but the lint does not take
it as a claim token; the citation is right.

## 11. Final census (pasted) and the tree

````
$ date -u
Wed Sep 23 11:30:46 UTC 2026
$ ip netns list
(end)
$ ip -o link show type veth
(end)
$ iptables -t nat -S PREROUTING
-P PREROUTING ACCEPT
$ ls -A /etc/netns
(end)
$ ls -A /run/s0-05-egress
(end)
$ route_localnet: all / default / any interface set to 1
0
0
(none)
$ ls -d /tmp/e3r1 /tmp/e3r1nr /tmp/e3-*
ls: cannot access '/tmp/e3r1': No such file or directory
ls: cannot access '/tmp/e3r1nr': No such file or directory
ls: cannot access '/tmp/e3-*': No such file or directory
$ ps (processes of this lane: stand-ins, listeners, runners, probe shells)
(no process of mine)
$ git status --porcelain      (mine: the two boundary files and this report; the others are other lanes')
 M proofs/S0-05/tools/pc/run_s0_05_units.sh
 M tests/test_s0_05_egress.py
?? tasks/briefs/continuity/VERIFY-AF-AP-127-R1-REPIN-a-R2-report.md
?? tasks/briefs/s0-02-support/VERIFY-B9-R1-report.md
?? tasks/briefs/s0-05-support/E3-R1-report.md
$ HEAD moved to ce0a3be while this lane ran (other lanes' commits). git diff de33838 HEAD -- proofs/S0-05 proofs/S0-01/pins.py T | wc -l
0
$ blobs: HEAD:PC 5d58951f392a (the PIN) -> worktree 076f863a54b9 (641 lines); HEAD:T 50bf20a92986 (the PIN) -> worktree 8b2f1f042bdf (3367 lines)
````

The census matches the dispatch baseline. Every namespace, veth, nat rule, sysctl, owner record and stand-in this lane created
was destroyed by NAME or PID: the tests' own `finally` blocks (`egress_ns_destroy <name>`, `_stop(<Popen>)`) and the harness's.
Nothing was killed with `pkill -f`. Every scratch copy, basetemp and probe lived under `/tmp/e3r1/`, and is gone.
