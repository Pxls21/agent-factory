# K1-h report (task #137) — the `.claude/ (first-party)` row split

**OUTCOME: `DONE:` (build lane's self-graded report — a PROPOSAL until the sandbox-side
adversarial-verifier lane grades it; I issue no gate verdict).**
Route: the LOCAL build route (the vLLM server default effort). The route is **HYBRID** in
practice: a cloud step serves a turn when the local step refuses with the chat-template 400
(it did once this lane). I claim nothing about which model wrote the code.
Lane: `pc-k1-h.md--74aa8c5`, PIN `74aa8c5`, venue `tasks/briefs/pc/VENUE-MAP.md` (PC = execution
host). Honey mode ultra, Lever-2: DATA only.

**NOT-done (first-class):** the adversarial verify is a SEPARATE lane (single-model harness — I
cannot self-accept); the coordinator commits (a lane never commits); the `V`/`C` files are
regenerated artifacts I produced with `--write` and leave in the worktree for the coordinator to
land.

## 1. Premise — verified by run (brief premise vs measured at the PIN)

Command (on the PIN's committed `sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv`):
`cut -f2 sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv | tail -n +2 | sort | uniq -c` →
`129 first-party`, `14 kit-adapted`, `2958 kit-verbatim`. The 129 first-party paths grouped by
set prefix (the brief's own awk, run at the PIN):
`47 aegis · 19 honey · 46 other · 12 prism · 3 provenance-files · 2 typesafe`. Each first-party
path whose git blob equals a blob under a declared `sandbox-kit/<name>/` root:
`20 council-of-high-intelligence · 19 honey-for-devs · 13 llm-wiki-compiler · 4 output-styles`
(56 total, **no path matches two roots** — the ambiguity refusal has no live case, as the brief
says). The 12 remainder (no copy, outside the three sets) — 9 non-PROVENANCE files + 3
`PROVENANCE-*.md`:

```
agents/codebase-memory-auditor.md   agents/codebase-memory-scout.md   agents/codebase-memory.md
commands/fetch-bookmarks.md         commands/wiki-ingest.md           commands/wiki-visualize.md
skills/codebase-memory/SKILL.md     skills/session-start-hook/SKILL.md skills/wiki-compiler/SKILL.md
skills/PROVENANCE-AEGIS.md          skills/PROVENANCE-PRISM.md        skills/PROVENANCE-TYPESAFE.md
```

Provenance files carry the pin + `owner/repo` (the source's `owner/repo`, not the URL host):
`grep -n` at the PIN — aegis `PROVENANCE-AEGIS.md:3` (`GanyuanRan/Aegis @ 60321ed`, line 3 carries
both); prism `PROVENANCE-PRISM.md:3` source + `:4` commit `ffe2d10042041dcc23325f013e8b7e607e069952`;
typesafe `PROVENANCE-TYPESAFE.md:3` source + `:5` commit `65a39f3`. `find .claude/skills -maxdepth 2
-iname "LICENSE*"` → only `.claude/skills/typesafe-ai/LICENSE` (aegis/prism have none).
**Premise holds exactly. No `CONTRACT-INVALID`.**

## 2. Class table — before vs after (per class; counts from the class file)

| class | before (PIN, `C`) | after (`--write` on the worktree) |
|---|---:|---:|
| `kit-verbatim` | 2958 | 2958 (unchanged) |
| `kit-adapted` | 14 | 14 (unchanged) |
| `first-party` | 129 | **12** |
| `copy:sandbox-kit/council-of-high-intelligence/` | — (absent) | **20** |
| `copy:sandbox-kit/honey-for-devs/` | — (absent) | **19** |
| `copy:sandbox-kit/llm-wiki-compiler/` | — (absent) | **13** |
| `copy:sandbox-kit/output-styles/` | — (absent) | **4** |
| `vendored:aegis` | — (absent) | **47** |
| `vendored:prism` | — (absent) | **12** |
| `vendored:typesafe` | — (absent) | **2** |

Total `.claude/` paths: 3101 before and after. The 129 → 12 + 56 copies + 61 set members (20+19+13+4=56; 47+12+2=61; 12+56+61=129).

## 3. New rows in `V` (pasted from `sandbox-kit/VENDORED-MANIFEST.md:22-28`; lines 19-21 unchanged)

```
| `.claude/ (copy of sandbox-kit/council-of-high-intelligence/)` | https://github.com/0xNyk/council-of-high-intelligence | `aeb3082` | sandbox-kit/VENDORED-FROM.md:3-5 (kit snapshot) | MIT (`LICENSE`) | `678df73993b4b6709cd80aed556263ef5cdcffd5e7d6a7d796c828bf36baa4c7` | 20 | 0 | `284fa16159854b2d1c156c0d8ee06219c3707cccfdb9d6b1625a7d70f71711fa` |
| `.claude/ (copy of sandbox-kit/llm-wiki-compiler/)` | https://github.com/ussumant/llm-wiki-compiler | `0f734fd3fba7dbc6a3b58efb4fb5fbaf7ce7565d` | sandbox-kit/llm-wiki-compiler/README.md:3-5 | MIT (`LICENSE`) | `572ca8dd67a969ba171c89979adeb309eb4905d786ea9fc347bddda70456b933` | 13 | 0 | `e08a761e7903d60c2a8a29bda4c1064059524b0dab8983f79f139bd1f0b58cc4` |
| `.claude/ (copy of sandbox-kit/output-styles/)` | https://github.com/alexgreensh/attention-span | `unpinned (vendored copy)` | sandbox-kit/output-styles/PROVENANCE.md:3-5 | none found | none found | 4 | 0 | `0e48adce21aebec5e8dfe55494dbeb0621b8d70ef8b4c8c9621c4647d0125099` |
| `.claude/ (copy of sandbox-kit/honey-for-devs/)` | https://github.com/Green-PT/honey-for-devs | `unpinned (vendored copy)` | sandbox-kit/VENDORED-FROM.md:21-23 | MIT (`LICENSE`) | `ad2744bb9fe963f5b629d581bcb916c666641f625062a55bef8505e45d60e4cc` | 19 | 0 | `64ce76ad6d350f5d487d0c342eb6ba4c589cb88b7808fc3d7b913cf52eb15d38` |
| `.claude/ (vendored: aegis)` | https://github.com/GanyuanRan/Aegis | `60321ed` | .claude/skills/PROVENANCE-AEGIS.md:3 | MIT (declared) | none found | 47 | 0 | `505ea9c1e009b2874e5a13931f1504d6669a995906c3e6609380d5a5d2efe404` |
| `.claude/ (vendored: prism)` | https://github.com/Cranot/super-hermes | `ffe2d10042041dcc23325f013e8b7e607e069952` | .claude/skills/PROVENANCE-PRISM.md:4 | MIT (declared) | none found | 12 | 0 | `fe35a89ba057ae7f5d1b3ea19d631fd4b50789d2b80d497c4d1bc25522fe0cf6` |
| `.claude/ (vendored: typesafe)` | https://github.com/typesafe-ai/skills | `65a39f3` | .claude/skills/PROVENANCE-TYPESAFE.md:5 | MIT (LICENSE) (`skills/typesafe-ai/LICENSE`) | `835f233f1d6ed84a9b9a351aba0689b47644a4137d6316911fc7957bde523b02` | 2 | 0 | `5682eb18d232a5731e67e779dd2c0272cc874a002008a15a93a292904477a241` |
```

The `.claude/ (first-party)` row (`V:21`) keeps only the 12-file remainder (count 12, 0 symlinks,
digest `d5722f7d…`). The pin-source cell is computed, not typed (aegis:3, prism:4, typesafe:5).
`git diff --stat -- sandbox-kit/`: **only `V` (13 +-) and `C` (234 +/120 -) change** — in `V` only
the two header lines and the 8 `.claude/` rows (old 5 rows → new 8).

## 4. RED→GREEN pairs (controls (a)-(d))

RED = at the PIN (`scratch/k1h_red`: the PIN's `M` + the NEW `T`), each fails for its **exact
expected reason** (the mechanism is not there yet); GREEN = on the worktree after the change.
The `-k k1h` selection at the PIN: **`6 failed, 45 deselected in 13.91s`** (6 of the 7 below —
`test_real_claude_split` is not `-k k1h`-named but IS red at the PIN, see the note).

| control | test | RED at the PIN (`T:line` — exact reason) | GREEN after |
|---|---|---|---|
| (a) honey byte change | `test_k1h_honey_copy_byte_change_falls_back_to_first_party` | `T:556` — no copy rule, class stays `first-party` (expected `copy:…honey-for-devs/`) | passes |
| (b1) new aegis file | `test_k1h_new_aegis_file_is_vendored_set_member` | `T:508` — no set rule, class `first-party` (expected `vendored:aegis`) | passes |
| (b2) aegis pin removed | `test_k1h_aegis_provenance_pin_removed_is_refused` | `T:533`/`T:534` — rc 0 (no provenance verification; expected `manifest: provenance mismatch: aegis pin`, rc 1) | passes |
| (c) ambiguous blob | `test_k1h_ambiguous_copy_blob_is_refused_by_name` | `T:585` — no ambiguity refusal (no copy rule) | passes |
| (d) check drift | `test_k1h_check_passes_then_honey_copy_flip_names_class_drift` | `T:602`/`T:610` — `--check` rc 0 (no copy class to drift; expected rc 1 + drift message) | passes |
| 129-pin (replaced) | `test_real_claude_split_counts_and_class_file` | `T:379` — `['129','0'] == ['12','0']` (old code produces 129, new test wants 12) | passes |

Both halves of each control are green on the worktree (`7 passed` for the 7 tests above).

## 5. Mutant battery (scratch copies only; each compiled + collected, AF-AP-78)

| mutant | mutation (exact) | battery (`-k "k1h or real_claude_split"`, 8 tests) | full 51 | dying test (exact) |
|---|---|---|---|---|
| m1 | copy rule dropped (the `matched` block removed; `copy:` class never produced) | 1 failed, 7 passed | 1 failed, 50 passed | `test_k1h_honey_copy_byte_change_falls_back_to_first_party` |
| m2 | copies matched by **file name** (not blob) instead of the blob map | 5 failed, 3 passed | 6 failed, 45 passed | `test_k1h_honey_copy_byte_change_falls_back_to_first_party`, `test_k1h_new_aegis_file_is_vendored_set_member`, `test_k1h_aegis_provenance_pin_removed_is_refused`, `test_k1h_ambiguous_copy_blob_is_refused_by_name`, `test_k1h_check_passes_then_honey_copy_flip_names_class_drift` |
| m3 | `claude_records` no longer calls `verify_declared_sets` (provenance verification skipped) | 6 failed, 2 passed | 6 failed, 45 passed | `test_k1h_new_aegis_file_is_vendored_set_member`, `test_k1h_aegis_provenance_pin_removed_is_refused`, `test_k1h_honey_copy_byte_change_falls_back_to_first_party`, `test_k1h_ambiguous_copy_blob_is_refused_by_name`, `test_k1h_check_passes_then_honey_copy_flip_names_class_drift`, `test_k1h_real_manifest_claude_rows` |
| m4 | **sets decided AFTER copies** (the set check moved below the copy rule) | 0 failed, 8 passed | 0 failed, 51 passed (59.73s) | **NONE — a genuine no-op.** No path changes class: a set file is not a kit-root copy (no `vendored:*` path's blob is under a `sandbox-kit/<root>/`), so the copy rule never fires on set members and the set rule is reached either way. This is exactly what the brief predicted ("no set file is a copy today; if equivalent, say so and why") — stated here as the measurement. |
| m5 | **one set dropped from the table** (the `typesafe` `DeclaredSet` removed from `CLAUDE_DECLARED_SETS`) | 2 failed, 6 passed | 2 failed, 49 passed | `test_k1h_claude_classification_and_remainder` (typesafe count 2→0, first-party 12→14), `test_k1h_real_manifest_claude_rows` (the typesafe row vanishes) |

The brief named m4 as "sets decided AFTER copies" and m5 as "one set dropped"; I implemented both
exactly. m4 is the equivalence the brief anticipated; m5 kills on the typesafe set (the smallest
set, 2 files — the clearest count delta).

## 6. Gates (pasted verbatim)

```
$ python -m pytest -n 8 tests/test_vendored_manifest.py -q -p no:cacheprovider   # run 1 (worktree)
51 passed in 23.27s
$ python -m pytest -n 8 tests/test_vendored_manifest.py -q -p no:cacheprovider   # run 2 (worktree, brief requires twice)
51 passed in 23.22s
$ python3 scripts/vendored_manifest.py --write
WROTE sandbox-kit/VENDORED-MANIFEST.md (9 roots)
WROTE sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv (3101 paths)
$ python3 scripts/vendored_manifest.py --check
PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots
$ git diff --stat -- sandbox-kit/
 sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv | 234 ++++++++++++++++----------------
 sandbox-kit/VENDORED-MANIFEST.md        |  13 +--
 2 files changed, 127 insertions(+), 120 deletions(-)
$ /home/rocco/venv-agent-factory/bin/python -m pyflakes scripts/vendored_manifest.py tests/test_vendored_manifest.py
<no output, rc 0>
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 38 files scanned, clean
```

`--write` is idempotent (a second `--write` reproduces the identical bytes; `--check` then PASS).
`report_lint.py --min-refs 10` (3 bounded rounds per the standing rule) — see DISCREPANCIES for
the final summary line.

## 7. FILE IDENTITY (the brief's 5 boundary files; nothing else touched)

| file | status | note |
|---|---|---|
| `M` `scripts/vendored_manifest.py` | edited | the only code change; `+134 -9` |
| `T` `tests/test_vendored_manifest.py` | edited | 6 new tests + the 129-pin replaced; `+145 -3` |
| `V` `sandbox-kit/VENDORED-MANIFEST.md` | regenerated by `--write` | 2 header lines + 8 `.claude/` rows |
| `C` `sandbox-kit/VENDORED-CLAUDE-CLASSES.tsv` | regenerated by `--write` | 129→12 first-party + 4 copy + 3 set classes |
| `R` `tasks/briefs/kit-k1-support/K1-h-report.md` | new | this report |

**No** `PROVENANCE-*.md`, no skill, nothing under `.agents/` is edited (the only `PROVENANCE-*`
touch is a temp-tree mutation inside the pytest fixtures, never the committed files). The overlaid
`scripts/report_lint.py` (the dispatcher's CURRENT copy) is not listed as mine.

## 8. M changes (what the code does now)

- `M:183-213` `CLAUDE_DECLARED_SETS` — the closed table (aegis/prism/typesafe: name, prefix,
  provenance file, source, pin, license label, license file).
- `M:214` `CLAUDE_SET_PREFIXES` — derived from the table (prefix → `vendored:<name>`).
- `M:457-485` `verify_declared_sets` — each set's provenance file must exist and contain the
  `owner/repo` and the pin string, else `manifest: provenance mismatch: <set> <field>` (the
  `pin` field is `M:482`); called at `M:858` (top of `build_manifest_data`, before any digest
  work) so **any** invocation (`--write`/`--check`) verifies before writing.
- `M:537-558` `claude_records` — the per-`.claude/`-path class order: (a) kit index →
  `kit-verbatim`/`kit-adapted`; (b) declared-set prefix → `vendored:<set>`; (c) blob matches a
  `sandbox-kit/<name>/` root → `copy:sandbox-kit/<name>/` (ambiguous = two roots → refuse by name,
  `M:552-556`); (d) `first-party`. Copies match by blob identity only.
- `M:910-957` the copy-row block; `M:962-1001` the set-row block — after the 3 existing `.claude/`
  rows, one row per non-empty copy root (source cells copied from the kit root's own row) then one
  per non-empty declared set. The first-party row keeps the remainder.
- `M:1153-1218` `main` — `--write` writes both files after `build_manifest_data` (which calls
  `verify_declared_sets` at `M:858`); `--check` compares the generated text to the committed bytes
  (a class flip changes the class file → drift message).

## 9. DISCREPANCIES

1. **`-k k1h` at the PIN is `6 failed, 45 deselected`, not 7.** The 7th red test at the PIN is the
   pre-existing `test_real_claude_split` (`T:379`), which is **not** `-k k1h`-named (it predates
   K1-h; the brief's "7 new tests" = 6 new + this 1 modified). The brief's item-5 "paste both"
   for the `-k` line is met: RED `6 failed, 45 deselected` / GREEN `7 passed, 44 deselected`
   (the 7 = the 6 new + `test_real_claude_split` by name).
2. **m4 is a no-op** (0 failed / full 51 passed) — as the brief anticipated; recorded as an
   equivalence, not a dead mutant.
3. **m3 kills 6 tests, m2 kills 5** (the draft had 6 and 3 respectively — the full battery shows
   the exact sets in §5). m2's name-matching drops the honey byte-change test (the name still
   matches) but breaks the ambiguity/aegis/refusal controls (those plant/rely on a blob, and
   name-matching mis-assigns the planted dup).
4. **`report_lint` final summary line** (3 fix-hint rounds, the brief's cap; the `M:NN`/`T:NN` refs
   cite the live worktree file, whose line numbers the heuristic cannot resolve against the PIN):
   **`report_lint: 32 refs — OK 15, NEAR 3, MISS 13, UNCHECKABLE 1, UNRESOLVED 0 (worktree)`**
   (trace 16→14→13). The 13 surviving MISSes are range-citations (`M:537-558`, `M:945-957`,
   `V:22-28`, `T:602/610`, …) where the lint checks only the range's FIRST line against a claim
   token that sits on a later line of the range — a known heuristic limitation, not a factual
   error; reported per the standing rule, not chased. `--min-refs 10` floor is met (32 refs, all
   byte-verified against the live file).
5. **`V:21` first-party digest** `d5722f7d…` is a **generated** value over the 12-file remainder
   (not the brief's 129-file pin `15898f91…`); the 129-pin test's old assertion `T:379`/`T:382`
   is replaced by the K1-h 12-count, so the pin is gone from the test by design.
6. **Adjacent untracked artifact (not mine, not fixed):** `git status` shows an untracked
   `downloaded_files/dashboard.lock` (0 bytes, mtime 13:55, created after this lane's edits and
   not at the PIN). It is outside the boundary (`M/T/V/C/R`) and was not created by this lane;
   reported here only so the coordinator does not mistake it for a lane output. The worktree
   otherwise carries exactly the 4 boundary files (M/T/V/C) plus the new report R.

## 10. Self-attack — the three most likely ways this is wrong, and how each was ruled out

1. **The copy match is by name, not blob, so a renamed file still reads as a copy.** Ruled out:
   m2 (name-matched) is red on 5/8 tests including the honey byte-change control (a 1-byte change
   to a same-named file breaks a name match but not a blob match — the control fails under m2 and
   passes under the blob rule). The code matches `sha256_bytes(path.read_bytes())` against the
   root blob map (`M:537-558`), never the filename.
2. **Provenance verification is bypassed on a code path (e.g. `--check` only), so a tampered pin
   slips through.** Ruled out: `verify_declared_sets` is called at the top of `build_manifest_data`
   (`M:858`, before any digest work), and both `--write` and `--check` flow through
   `build_manifest_data` (`M:855`), so neither can write or pass without the verification. m3
   (the call skipped: `set_pin_lines = verify_declared_sets(root)` at `M:858` becomes `set_pin_lines = {}`)
   is red on 6/8 incl. the pin-removed control; the committed files pass `--check` only because
   they are intact.
3. **The manifest/digest is hollow-green (the row exists but the digest is over the wrong files).**
   Ruled out: the copy rows' digests are computed over the `.claude/` copies themselves
   (`digest_records(row_files)` over the `row_files` list, `M:945-957`), not the kit source; the 8 rows' digests + counts are
   asserted by `test_k1h_real_manifest_claude_rows` against the regenerated `V` (not a hardcoded
   constant), and `--check` re-derives them from the tree. A wrong digest fails `--check`.

## 11. NOT-done

- **Independent adversarial verify** — a separate lane (single-model harness; I cannot
  self-accept). This report is a PROPOSAL.
- **Commit** — the coordinator harvests the worktree (a lane never commits). The `V`/`C`
  regenerated files are left in the tree.
- **The `.agents/` mirrors** (out of scope — not a declared root).
- **`report_lint` MISSes** that survive 3 rounds — reported, not chased (the refs are the live
  file's line numbers; the heuristic resolves against the PIN).
