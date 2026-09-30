# K2 round 4: provenance by blob (task #353, D-115), the builder's report of record

> **Coordinator note (2026-09-30 05:5xZ).** The builder's hand-back, saved verbatim below (the original K2 builder,
> a sandbox code-implementer, resumed; harvest run s-20260930T055202Z-433fbb: 433 assistant records dated 2026-09-30 (this
> round) and 1457 over the lane's life, every one claude-opus-5-5, 0 refusal stops, 5 compactions over the lane's life; hand-back
> sha256 prefix afebe7dafaa5). Every claim is a hypothesis until VERIFY-K2-R4. The harness flagged the hand-back as
> matching an instruction-shaped pattern (settings-json) and neutralized its control tags: the text describes K2's
> registration patch, which adds hooks to `.claude/settings.json`; nothing in it was acted on as an instruction, and the
> registration stays unapplied until its own landing after the verify. At the landing the coordinator applied
> `tasks/briefs/jev-trim/K2-R4.patch` (sha256 7e126aea) at the branch head after the LS-B12 landing: the five files'
> sha256 prefixes equal the report's table, and both K2 patches (registration, post-commit) still apply there
> (a temp-index `git apply --check`), although LS-B12 changed one line of `tests/test_session_hooks.py` after the PIN.
> The report's two line citations lint OK on the patched tree (`scripts/report_lint.py`: OK 2, MISS 0). The builder's
> item-7 pick is RE-SCOPE, on one condition (the file's own symbols from the committed blob, never from graft). Under
> D-115 there is no round 5: a same-class blocker in VERIFY-K2-R4 sends K2 to the owner as RE-SCOPE or PARK.

---

# K2 round 4 (task #353, D-115): provenance by blob. Builder report

Written 2026-09-30 05:4xZ (`date -u` 05:44:43Z). Builder: the original K2 builder (sandbox code-implementer), resumed. PIN: origin 14ecd8b.

Deliverable: `/home/user/agent-factory/tasks/briefs/jev-trim/K2-R4.patch`. It is untracked in the shared tree, 1407 lines, sha256 `7e126aea056518cbec121dc472e2fbb5a3e85a03f720b00c32f567592ceb2ff1`.

**TL;DR:** The committed blob is now the rule for every caller and test name.
- **Builder:** keeps a name only when two things hold. The graph's record must equal the file's committed blob. The name must also sit on its line in that blob (deviation D1).
- **Reader:** re-checks each kept name's blob against BLOBS.txt.
- **Red then clean:** every R3-1, NOT done 1 and NOT done 9 shape is red at the PIN and clean on the final bytes.
- **Gates:** green twice. Every named mutant is killed.
- **Item 7 pick:** RE-SCOPE.
- **Still open:** one known text channel, NOT done 7 (the file's own symbols, taken from graft). It is outside this round's contract.

## NOT done (first-class)

1. **NOT done 7 is still open.**
   - What it is: the file's own code part, meaning graft's symbols and signatures. It carries the stamp-then-read race (VERIFY-K2-R3 finding 3, rated FOLLOW-UP).
   - It was not in this round's contract, and I did not fix it.
   - It is the one known path by which uncommitted or untracked text can still reach the model (self-attack 1, with a proposal).
2. **Adjacent defects.** Reported, not fixed:
   - a. The tests line reads `tests of the file (code-review-graph) 0 (none found; a test that runs the file as a subprocess leaves no edge)` when the filter withheld every test (codemap.py:1005 and :1156). It says "none found" when tests were found and withheld. It shows in every probe log, for example logs/final-nd1.txt.
   - b. `instruments.gitnexus.unmatched` (codemap.py:818) stores GitNexus qualnames of the file itself that the pack's symbols lack. They can come from other bytes. They sit in the pack JSON and are never rendered.
   - c. The risk line's level and its `impacted` and `direct` counts come from GitNexus's whole graph, untracked files included. They are numbers and a level, never a name. Item 1's "total" is the callers total only.
   - d. The risk line renders a failed GitNexus section's `note` (codemap.py:934) and a symbol's `risk_error` (:938). `_rows` can put up to 80 characters of a malformed Cypher answer into such a note. Not probed.
3. **The `.claude/` manifest row must be regenerated at landing.** The registration patch changes `.claude/settings.json`. The brief expects this failure, and it is measured below.
4. **WIDEN_CAP** (VERIFY-K2-R3, [S, UNVERIFIED]) is untouched.

## DISCREPANCIES and deviations (loud)

- **D1. A second builder check, beyond item 1's letter** (`_named_here`, codemap.py:699).
  - What it adds: each name a graph gave in a file must sit on its line in the committed blob.
    - Python: a def or class of that bare name must start on that line, from the blob's own AST.
    - Other languages: the name must be a word on that line.
    - `<module>` callers are exempt.
  - Why: the record is the graph's own word. It can be newer than the graph's nodes; this is the measured GitNexus lie that `_moved` flags for the file itself. A graph can also re-index between its answer and the record read, because the record is read after the Cypher answers. In both cases, a record-only tie passes a name from other bytes. With the check, every name a pack shows is committed text at the place shown.
  - Red and green: `builder-names-unchecked` is the builder without the check. It fails `provenance-record-lies` with "a caller from bytes its graph's record does not describe entered the pack".
  - Cost: it fails closed. A file with one name that cannot be checked loses all its names and its totals.
- **D2. The class test replaced the old real-hook B1 test** (`test_untracked_callers_with_the_post_commit_patch`).
  - The old test's reader-only leak control can no longer leak end to end, because the builder now filters first.
  - Measured with mutdrv_r4.py:
    - builder guard off alone: KILLED by the class test;
    - reader guard off alone: SURVIVES it, as predicted.
  - The reader's clauses are proven by planted packs instead. The class test's leak control turns off both guards.
- **D3. Item 4's canaries sit in their own file's code-map pack on disk.**
  - Every code-map pack is built from the working copy. So `u1` and `u9`, uncommitted functions of the tracked caller_trk.py, are symbols in caller_trk.py's own pack.
  - The reader withholds that code part through the blob check (VERIFY-K2 F1).
  - What the class test asserts:
    - item 2's canaries: absent from every pack;
    - item 4's canaries: absent from alpha's pack and from every context.
- **D4. Item 3's shapes are points inside the one class test** (`late-outside` and `late-track-window`), not separate test functions. The red run at the PIN names each one.
- **D5. The 3-file set 804c19143d13 ran as two calls.** Together the files take about 11 minutes, over the 10-minute bound. The parts are db64e610236b and 395f8af3a0ce.
- **D6. One run is void.** My first filepacks gate passed `-q` a second time on top of the script's own. The script's summary line then held only dots. That run exited 0 with 188 dots. It is void as count evidence, and I re-ran it.
- **D7. The behavior changes beyond the file-pack reader.** The code-map CLI lookup and the L2b edit hook read the same packs. They now show only blob-vouched callers, and they show `callers in tracked files (the total is left out): …` when the builder dropped a total.
- **D8. I broke a standing rule (AF-AP-249): three top-level `cd` commands.**
  - Two went to /home/user/agent-factory, the primary directory, so they had no effect.
  - One went into a scratch experiment directory.
  - No write followed from a wrong directory.
- **D9. The verifier's `probe_r3.py` anchors on `_tracked_only`,** which is now `_committed_only`. My copy, `vk/probe_r4.py`, changes only that anchor line.
- **D10. `git apply` of K2-R4.patch warns of 3 whitespace errors.** All three are blank context lines of the embedded K2-registration.patch. The PIN's copy of that patch has 11 such lines.
- **D11. A graft index appeared in the fresh tree's root** (`graft/`, 77 MB) at 05:06:40-44Z, during the session_hooks and search_intercept run. The source is inferred from the timestamps [I]. It is existing test behavior, not K2's.

## Evidence per contract item

Tiers: [V] means verified by a run, [I] inferred, [A] assumed.

**Premise [V].** Re-run at 03:08Z: IDENTICAL (premise_expected equals premise_actual, sha256 3b6615f522dd2a5c).

**Item 1: provenance by blob [V].**
- **Builder (scripts/codemap.py):**
  - `_gitnexus` keeps every caller as `callers.all` (:497-498).
  - `_committed` (:669) reads each named file's blob id, sha256 and bytes at the build's commit, in one `git cat-file --batch` call.
  - `_named_here` (:699) is D1.
  - `_provenance` (:729) records `provenance = {commit, gitnexus: {file: {blob, indexed}}, code-review-graph: {...}}`. `indexed` is the blob only when the graph's record equals the blob's sha256 and every name is on its line.
  - `_proven` (:758).
  - `build_one` (:803-813) filters tests and callers to vouched files. The file itself also needs its graph fresh. When a name drops, `count` and `tests` become None.
  - The pack now carries `provenance` (:825).
- **Reader (scripts/filepacks.py:573):** `_committed_only` replaces `_tracked_only`, called at :649.
  - It keeps a name only when:
    - `rec.blob` is a string;
    - `rec.indexed == rec.blob`;
    - `rec.blob == packs.blob(f)`, from BLOBS.txt;
    - the path holds no newline.
  - The file itself also needs its graph fresh.
  - `all_kept` covers caller_files plus the file itself.
  - A pack with no provenance shows no names and no totals.
  - The path filter is gone; the blob tie replaces it, since BLOBS.txt lists only tracked files.

**Item 2: the class test [V].**
- Where: tests/test_filepacks.py:1959 `class_scenario` and :2101 `test_untracked_text_never_reaches_a_pack_through_the_real_hook[real|blob-tie-off]`.
- It runs through the REAL patched post-commit hook: each graph re-indexed, the code map refreshed, the file packs built, and the real wrapper.
- The shapes:
  - (a) untracked, outside the refresh paths: `a` in tools/u_out.py, and `e` in tests/test_u.py.
  - (b) untracked, inside the refresh paths:
    - `b` in scripts/u_in.py;
    - `c1` in scripts/late_in.py's untracked era, observed with the refresh held behind its lock after its commit.
  - (c) the untracked era of a file later committed with other text: `d1` in tools/late_out.py. No refresh follows that commit.
- Final-bytes table, real variant (logs/class-real-final-bytes.txt):
```
  c1-built               packs ['ok', 'okt', 'trk', 'u1']   alpha ['ok', 'okt']                        context ['ok', 'okt']
  late-outside           packs ['ok', 'okt', 'trk', 'u1']   alpha ['ok', 'okt']                        context ['okt']
  late-track-window      packs ['ok', 'okt', 'trk', 'u1']   alpha ['ok', 'okt']                        context ['okt']
  late-track-refreshed   packs ['c2', 'd2', 'ok', 'okt', 'trk', 'u1'] alpha ['c2', 'd2', 'ok', 'okt']            context ['c2', 'okt']
  nd9-build-stalled      packs ['c2', 'd2', 'ok', 'okt', 'trk', 'u1', 'u9'] alpha ['c2', 'd2', 'okt']                  context ['okt']
  nd9-built              packs ['c2', 'd2', 'ok', 'okt', 'trk', 'u1', 'u9'] alpha ['c2', 'd2', 'okt']                  context ['okt']
rc=0
```
- Leak control, blob comparison off at the builder and the reader (logs/class-off-final-bytes.txt). Each shape shows where LEAKS says:
  - c1-built: context ['a', 'b', 'c1', 'd1', 'e', 'ok', 'okt', 'trk', 'trkt', 'u1', 'u1t', …];
  - late-outside: ['d1', 'okt', 'trkt', 'u1t'];
  - late-track-window: ['c1', 'okt', 'trkt', 'u1t'];
  - nd9-build-stalled: ['ok', 'okt', 'trkt', 'u1t', 'u9'].
- Red at the PIN (logs/red-class-test-pin.txt, 03:55Z; the PIN's code with the new test file): `FAILED tests/test_filepacks.py::test_untracked_text_never_reaches_a_pack_through_the_real_hook[real]`, `1 failed in 60.95s (0:01:00)`.
  - Context leaked per point:
    - c1-built: [u1, u1t];
    - late-outside: [d1, u1t];
    - late-track-window: [c1, u1t];
    - late-track-refreshed: [u1t];
    - nd9-build-stalled: [u1t, u9];
    - nd9-built: [u1t].
  - alpha's pack held a, b, c1, d1, e, u1 and u1t.

**Item 3: R3-1's shapes [V].**
- As committed tests: the class test's points `late-outside` and `late-track-window` (D4). Red at the PIN above, clean after.
- The verifier's probes (my copy vk/probe_r4.py, run as `VK2_WT=<tree> python3 vk/probe_r4.py <S4> <mode>`):
  - late-outside, red at the PIN: `callers 2: <EARLY> tools/<CALLER_X>:6 · __init__ scripts/alpha.py:10` after all jobs, 30 s later, and after c3.
  - late-outside, final bytes (05:32Z): `callers in tracked files (the total is left out): __init__ scripts/alpha.py:10` at every point. EARLY is in no pack.
  - late-track, red at the PIN: in the window, `callers 2: <EARLY> scripts/<CALLER_X>:4 · __init__ scripts/alpha.py:10`.
  - late-track, final bytes: in the window, `callers in tracked files (the total is left out): __init__ scripts/alpha.py:10`. After the refresh, `callers 2: <LATER> scripts/<CALLER_X>:4 · …`, which is committed text.

**Item 4 [V].**
- **NOT done 1: CLOSED.** Evidence:
  - The class test: `u1` and `u1t` are absent from alpha's pack and every context. At the PIN, the context held u1 and u1t.
  - test_codemap `provenance`: the `unc` and `unct` canaries stay out.
  - Probe nd1 at the PIN: `<TRK> scripts/caller_trk.py:4 · <UNC> scripts/caller_trk.py:8` and tests `test_<TRK> · test_<UNC>`.
  - Probe nd1 on the final bytes: `__init__ scripts/alpha.py:10` and tests 0. The committed TRK names drop too, because the file's indexed bytes are not its blob (item 1's clause).
- **NOT done 9, the stalled-build shape: CLOSED.** Evidence:
  - The class test's nd9-build-stalled and nd9-built points: `u9` is absent from alpha and every context. At the PIN, the context held u9. The control `ctl.stalled` proves the build really stalled.
  - Probe nd9 at the PIN, with the build queued: `callers 3: <TRK> … · <U9> scripts/caller_trk.py:8 · …`.
  - Probe nd9 on the final bytes: `callers in tracked files (the total is left out): __init__ scripts/alpha.py:10`, both queued and done.

**Item 5 [V].** K2-registration.patch is rebased onto the PIN (298 lines).
- `.claude/settings.json`:
  - SessionStart: the reset group goes after task_sync and the catalog, and before ls_req.
  - PreToolUse: the tool hook (matcher `Read|Edit|Write|Bash`, through the wrapper) goes last.
- `scripts/install_session_hooks.py`: the `filepacks` and `filepacks_reset` groups, and the merge rule's `filepacks_marker`.
- `tests/test_session_hooks.py`:
  - `test_fresh_install_registers_and_prints_15_hooks` counts families through `hook_count`, {"ls_req": 3, "filepacks": 2}, 15 hooks in all;
  - three new tests.
- Both patches apply at the PIN: checked through a temp index, and with `git apply --check` in the fresh tree.
- K2-post-commit.patch is unchanged (sha256 71ba4c2c0cec81ab…) and applies at the PIN.

**Item 6: mutation, on the final bytes [V].**
- **Named mutants, one per clause of item 1:**

| clause | reader mutant (its check) | builder mutant (its check) |
|---|---|---|
| compare the path instead of the blob | blob-tie-by-path (blob-tie) | builder-path-not-blob (provenance) |
| skip the indexed hash | indexed-hash-skipped (blob-tie) | builder-indexed-hash-skipped (provenance-record-lies) |
| accept a missing blob | missing-blob-accepted (blob-tie) | builder-missing-blob-accepted (provenance) |
| keep the total when a name drops | total-kept-on-drop (blob-tie) | builder-total-kept-on-drop (provenance) |

- **Also killed:**
  - reader: legacy-pack-trusted, committed-filter-uncalled, blob-tie-off, blobs-newline-unguarded;
  - builder: builder-names-unchecked (D1), builder-working-bytes, builder-callers-unfiltered, builder-tests-unfiltered, builder-same-file-fresh-ignored.
- **The verifier's four checks,** ported from its mutdrv4.py n4: tail-path-caller, tests-graph, not-indexed, caller-files-missing. They kill its 8 survivors:
  - blob-key-substring;
  - tests-by-gitnexus, callers-by-crg, keep-rel-any-graph, tests-rel-unfiltered;
  - fresh-unless-stale, clause-not-indexed-passes;
  - files-not-list-ok.
- **My earlier mutants:**
  - The round-3 table, re-anchored where the code moved: same-file-names-from-stale-graphs, stale-gitnexus-total-stands, callers-total-always-dropped, caller-files-ignored.
  - One retired with the code it mutated: tracked-newline-unguarded. Its successor, blobs-newline-unguarded, mutates the same guard in `proven()`.
- **The committed tables:** every mutant is a parametrized negative control that must fail with its exact message.
  - test_filepacks: 67 checks and 103 mutants. Collection order puts the checks at positions 0-66, before the mutants at 67-169.
  - test_codemap:
    - lookup: 13 checks at 0-12, then 24 mutants at 13-36;
    - refresh: 5 checks at 40-44, then 6 mutants at 45-50;
    - FIFO: 5 at 55-59, then 5 at 60-64.
  - All passed in every gate run below, with PYTHONDONTWRITEBYTECODE=1. Each mutant is written into its own fresh fixture copy.
- **mutdrv_r4.py,** for the mutants outside the tables (scratch; logs/mutdrv-r4.txt). It runs the control first, turns bytecode off, clears every `__pycache__` before each run, and restores each file with a sha256 check. It ran in the both-patches tree:
```
pycache dirs cleared before the control: 0
CONTROL rc=0 64.8s: 6 passed in 64.61s (0:01:04)
preimage-unchecked               KILLED   (expected KILLED  ) rc=1 0.4s pycache=0 restored-sha=32d3bcd4e793 | 1 failed in 0.26s
reg-reset-after-chat-form        KILLED   (expected KILLED  ) rc=1 0.4s pycache=0 restored-sha=dad0bfef174d | 1 failed in 0.18s
reg-matcher-on-reset             KILLED   (expected KILLED  ) rc=1 0.4s pycache=0 restored-sha=dad0bfef174d | 1 failed in 0.19s
reg-tool-hook-unwrapped          KILLED   (expected KILLED  ) rc=1 0.5s pycache=0 restored-sha=dad0bfef174d | 1 failed, 1 passed in 0.25s
reg-marker-dropped               KILLED   (expected KILLED  ) rc=1 0.3s pycache=0 restored-sha=dad0bfef174d | 1 failed in 0.17s
settings-reset-after-chat-form   KILLED   (expected KILLED  ) rc=1 0.3s pycache=0 restored-sha=a1836538fd95 | 1 failed in 0.14s
settings-tool-hook-not-last      KILLED   (expected KILLED  ) rc=1 0.4s pycache=0 restored-sha=a1836538fd95 | 1 failed in 0.17s
class-builder-tie-off            KILLED   (expected KILLED  ) rc=1 63.3s pycache=0 restored-sha=e1a56e0b0cf8 | 1 failed in 63.02s (0:01:03)
class-reader-tie-off             SURVIVED (expected SURVIVED) rc=0 62.2s pycache=0 restored-sha=31606f07fa64 | 1 passed in 61.98s (0:01:01)
mutants as expected: 9 of 9
```
- `preimage-unchecked` is VERIFY-K2-R3 finding 5. It is killed by `test_a_wrong_unpatched_at_is_refused` ("DID NOT RAISE").

**Gates [V].** Counts are pasted from scripts/test_summary.sh; set ids come from `bash scripts/pc_suite.sh set-id`; `--basetemp` was under my scratch.

In wt (PIN + K2-R4.patch; the hook as at the PIN):
```
1 files set=db64e610236b   run 1: pytest-exit: 0 / pytest-summary: 188 passed in 238.72s (0:03:58)
                           run 2: pytest-exit: 0 / pytest-summary: 188 passed in 245.97s (0:04:05)
2 files set=395f8af3a0ce   run 1: pytest-exit: 0 / pytest-summary: 209 passed in 406.20s (0:06:46)
                           run 2: pytest-exit: 0 / pytest-summary: 209 passed in 429.79s (0:07:09)
(union of the two: 3 files set=804c19143d13, D5)
```

In the both-patches tree (a fresh PIN worktree + K2-R4.patch + K2-registration.patch + K2-post-commit.patch):
```
2 files set=2415789b9582   run 1: pytest-exit: 0 / pytest-summary: 144 passed in 50.35s
                           run 2: pytest-exit: 0 / pytest-summary: 144 passed in 47.73s
1 files set=21e700b8344c   -k test_committed_manifest_matches_fresh_generation
                           run 1: pytest-exit: 1 / pytest-summary: 1 failed, 56 deselected in 2.23s
                           run 2: pytest-exit: 1 / pytest-summary: 1 failed, 56 deselected in 2.87s
   control, the same tree with the PIN's .claude/settings.json: pytest-exit: 0 / pytest-summary: 1 passed, 56 deselected in 3.03s
1 files set=db64e610236b   run 1: pytest-exit: 0 / pytest-summary: 188 passed in 260.75s (0:04:20)
                           run 2: pytest-exit: 0 / pytest-summary: 188 passed in 250.48s (0:04:10)
2 files set=395f8af3a0ce   once, extra (the patched hook feeds test_codemap's refresh tests):
                           pytest-exit: 0 / pytest-summary: 209 passed in 399.34s (0:06:39)
```

`python3 scripts/vendored_manifest.py --check`, with the registration patch applied, exit 1. As the brief expects, it fails on the `.claude/` row only:
```
FAIL: vendored manifest drift: line 20: committed='| `.claude/ (kit-adapted)` | pxls21/sandbox-kit:dot-claude/ | `aeb3082 (adapted here)` | sandbox-kit/dot-claude.aeb3082.index.tsv | none found | none found | 17 | 0 | `568e8c0a2683418e107175e46fbe9070a5ec9526f7ba7bcd81998a8294e3591b` |'; generated='| `.claude/ (kit-adapted)` | pxls21/sandbox-kit:dot-claude/ | `aeb3082 (adapted here)` | sandbox-kit/dot-claude.aeb3082.index.tsv | none found | none found | 17 | 0 | `61127bdc6d895d70c56d5fce30e0f6fcb241140709c4859638971b0e0997a695` |'
```

**Patch proof [V].**
1. `git -C <wt> diff 14ecd8b` equals the scratch K2-R4.patch (cmp).
2. On a fresh PIN worktree (`worktree add -q --detach … 14ecd8b`, hooks off), `git apply --check` passes (3 whitespace warnings, D10).
3. After applying, all five files are byte-identical to wt's (cmp ×5). So wt's gates are the gates of the patch alone.
4. Then both other patches passed `apply --check`, were applied, and gave the both-patches gates above.
5. The shared-tree copy also applies at the PIN: `GIT_INDEX_FILE=<tmp> read-tree 14ecd8b && apply --check --cached`.

## Files

Final bytes (= PIN + K2-R4.patch):

| file | lines, PIN → final | +/− | sha256, final |
|---|---|---|---|
| scripts/codemap.py | 1156 → 1271 | +120 −5 | e1a56e0b0cf8e8ed5da42f718369592d9a690f4613641739824162b4c71f71e5 |
| scripts/filepacks.py | 1219 → 1226 | +25 −18 | 31606f07fa64c9481ac6e8201365c0c60e16386b9cb981e5e74f3aea3c8ec666 |
| tests/test_codemap.py | 943 → 1097 | +155 −1 | d8002fbbeb8217ae8dc9347ccadfb18450fa912ebe43dd987e798534f695b7d3 |
| tests/test_filepacks.py | 1836 → 2181 | +424 −79 | 32d3bcd4e7935ed749e3bd855d15829d4c26f7fcf82e5d08dc98e1f152c03716 |
| tasks/briefs/jev-trim/K2-registration.patch | 224 → 298 | +152 −78 | 1dc53684b8ae549009063ce9c8b428803e8b74a6e6f87037c88524967d4e532e |
| tasks/briefs/jev-trim/K2-post-commit.patch | 26 → 26 | unchanged | 71ba4c2c0cec81abd5d672d7f89d246a39a11cf0a530523b00d48e15affe9ef1 |
| K2-R4.patch (shared tree, the deliverable) | 1407 | 5 files, +876 −181 | 7e126aea056518cbec121dc472e2fbb5a3e85a03f720b00c32f567592ceb2ff1 |

- **In the both-patches tree:**
  - .claude/settings.json: 163 lines, sha256 a1836538fd9504ff…
  - scripts/install_session_hooks.py: 221 lines, dad0bfef174d0540…
  - tests/test_session_hooks.py: 745 lines, 334f69382cc749ee…
  - scripts/hooks/post-commit: 219 lines, fce110fe82d8b183…
- **Anchors:**
  - test_codemap.py: check_provenance :439, check_provenance_same_file :479 (rewritten: `cached` moves, callers stay on their lines), check_provenance_record_lies :510 (new), LOOKUP_CHECKS :560, builder mutants :603-627.
  - test_filepacks.py: committed_blob :170, provenance :179, check_blob_tie :1182, the n4 ports :1220-1268, MUTANTS :1369, test_a_wrong_unpatched_at_is_refused :1821, class_scenario :1959.
- **Scratch evidence** is kept in `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/k2-lane-353/r4/`:
  - logs/: gate1-*, gate2-*, both1-*, both2-*, both-vendored-manifest-*, mutdrv-r4.txt, collect-*.txt, red-*-pin.txt, final-*.txt, class-*-final-bytes.txt;
  - mutdrv_r4.py, vk/probe_r4.py, vk/class_probe.py, K2-R4.patch, PROGRESS.md.

## Self-attack: how could untracked text still reach the model?

1. **The file's own code part: NOT done 7, open.** [V at round 3, by the verifier; not re-probed]
   - What the reader shows: the file's own symbols and signatures, which come from graft's index. It shows them when the pack's blob equals BLOBS.txt's and graft is fresh by its own record. That record is read about 1.0-1.3 s before the skeleton read.
   - How it leaks: graft re-indexes other bytes inside that window, or graft keeps a record newer than its nodes. Either way, other bytes' names and signatures land in a pack that looks fresh.
   - Measured: the verifier forced it at round 3 with probe_nd7.py. `leak_<CANARY>` showed on Read; in the untracked shape with a stale TRACKED.txt, it showed on Read and on Edit.
   - Round 4 did not change this path.
   - The fix, following D1's principle:
     - check each graft symbol (qualname, start) against the AST of the pack's bytes;
     - mark graft stale when a symbol is missing or sits on another line;
     - check each signature against its def line;
     - add the verifier's re-stamp after the skeleton read.
2. **A name that passes D1 by coincidence** [I]. That is a name from other bytes that is also a def of that name on that line in the committed blob. The text shown IS then committed text; only the edge (who calls whom) can be wrong. For non-Python files the check is "a word on the line", and the same argument holds. I did not run it on JS or TS this round.
3. **Numbers, not names:** the risk level and the impacted and direct counts (NOT done 2c).
4. **Free text on a graph failure:** the risk line's note (NOT done 2d).
5. **The raw pack JSON on disk** (`.jev/codemap/*.json`).
   - What it holds: untracked paths in caller_files and provenance, `unmatched` (NOT done 2b), and an edited file's own pack with its uncommitted symbols (D3).
   - Why it is lower risk: no hook injects these. A model that reads `.jev/` directly can read the untracked file itself as well.
6. **A stale BLOBS.txt, from a stalled build.** A different blob drops the name. An equal blob means equal bytes, because blob ids are content hashes. The nd9 points cover this.
7. **A pack not written by the builder.**
   - The reader trusts `provenance` as written. It cannot re-read names against blob bytes within its millisecond budget.
   - Planted packs prove each reader clause. But a forged record that claims a blob for a name not in it would be believed.
   - Packs live in `.jev/`, and only codemap.py writes them, by atomic replace.

**The three most likely ways this change is wrong, and how each was ruled out:**
1. **D1 drops real names**, which would empty real packs.
   - Measured on GitNexus (scratch repo, 05:41Z): decorated callers get their def line. `cached_user` startLine 5 and `meth` 11 become lines 6 and 12 after codemap's +1.
   - Measured on code-review-graph (04:2xZ): decorated tests get their def line, `test_helper_param` 7 and `test_in_class` 13.
   - The controls that require committed names to stay all pass on the final bytes:
     - check_provenance: `cached` keeps (2, [fetch, main]);
     - the class test: ok, okt and c2 stay;
     - the late-track probe: `<LATER>` shows after the refresh.
   - Residual [A]: a JS or TS caller whose GitNexus name is not a word on its start line is dropped. Not measured.
2. **The double guard hides a dead reader clause.** Ruled out by mutants at each guard:
   - Planted packs kill every reader clause: blob-tie, tail-path-caller, tests-graph, not-indexed, caller-files-missing, caller-path-newline.
   - test_codemap's provenance checks kill every builder clause.
   - The class test kills the builder guard alone (class-builder-tie-off) and both guards together (the blob-tie-off leak control).
   - The reader guard alone survives the class test by design (D2).
3. **The rename `_tracked_only` → `_committed_only` breaks a caller.**
   - GitNexus impact on `_tracked_only` (the index at the PIN's code): LOW, 1 direct caller (`_code_part`), 3 impacted.
   - A text search of scripts/, tests/ and .claude/hooks/ finds no other reference.
   - `build_one`'s impact reads UNKNOWN. By text, its callers are `build` (codemap.py:863), test_filepacks.py:2160 and test_codemap.py:1014, and the gates cover all three.

## Item 7 pick: RE-SCOPE

- **Where the class lives.** The blocker class is in the derived code index, that is, a graph's view of the files. It is not in the file's own committed text. RE-SCOPE removes the class's whole surface: no callers, no tests, no names from any graph.
- **What PARK would lose.** The committed-text part of a pack, checked against BLOBS.txt, has not been a blocker in four rounds. PARK throws it away along with the index.
- **One condition.** RE-SCOPE must also take the file's own symbol list from the committed blob itself: the AST for Python, and no symbols for other languages. It must not come from graft's index. Otherwise NOT done 7, the one known open path, stays inside the re-scoped packs.
- **When PARK is the better pick.** Only if the owner judges packs without callers and tests not worth their context bytes. That is a question of value, not of safety.

## End state [V]

- **Worktrees:** wt, wt-pin, wt-reg and wt-fresh are all removed, hooks off. `git worktree list` shows none of mine.
- **Processes:** none of mine is running.
  - pids 223 and 311 are the harness's gitnexus MCP servers.
  - pids 11505, 14769-14773 and 23930 belonged to another lane.
- **Shared tree:** the only change is `?? tasks/briefs/jev-trim/K2-R4.patch`.
  - The only git writes were worktree add and remove, hooks off.
  - The temp-index `read-tree` and `apply --check --cached` wrote only a scratch index file.
- **Boundaries kept:**
  - No outward action, no PC bridge, no secret file, and no real transcript read.
  - No hook registered: install_session_hooks.py ran only inside the tests' temp targets.
  - `/home/user/.claude/settings.json`, the shared tree's `.claude/`, `scripts/hooks/` and the live `.jev/` are untouched.
- **S1-RATE lines** were each written as their own short text.
