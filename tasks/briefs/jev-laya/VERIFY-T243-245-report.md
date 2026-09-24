# VERIFY-T243-245 report

Role: adversarial-verifier (sandbox, Opus 5.5). Brief: `tasks/briefs/jev-laya/VERIFY-T243-245-brief.md`.
Started 2026-09-24 21:41Z (`date -u`). Written incrementally; the final section carries the gate recommendations.

## 0. Premise re-measure (first action) — HOLDS

```
$ for f in ...; do echo "$(git rev-parse --short=12 HEAD:$f) $f"; done      (and git hash-object on the working tree: identical)
0d2a66ea9009 scripts/stale_ids.py
b3f0faeeaa81 scripts/push_clean.sh
38c9e4298dbe tests/test_stale_ids.py
fb10f06b680b scripts/ap_screen.py
ddcf5707a3fc scripts/hooks/pre-commit
bcfac0093ba7 tests/test_ap_screen.py
fd6d5d54a3df .claude/hooks/edit-snapshot.py
bc4e48d7d29f tests/test_edit_snapshot_ap_screen.py
$ bash scripts/test_summary.sh tests/test_stale_ids.py   (twice)
pytest-summary: 9 passed in 4.98s
pytest-summary: 9 passed in 4.88s
$ bash scripts/pc_suite.sh set-id -- tests/test_stale_ids.py
1 files set=89acd12051d2
$ bash scripts/test_summary.sh tests/test_edit_snapshot_ap_screen.py tests/test_ap_screen.py   (twice)
pytest-summary: 194 passed in 0.52s
pytest-summary: 194 passed in 0.52s
$ bash scripts/pc_suite.sh set-id -- tests/test_ap_screen.py tests/test_edit_snapshot_ap_screen.py
2 files set=62551bca597a
```

Local HEAD at measure: `19ebb94 transcripts: scrubbed sandbox chat digests (2026-09-24)`. Working tree: one untracked
file (`tasks/briefs/jev-laya/VERIFY-GW1-R1-report.md`, the other verifier's), none of the eight pinned files dirty.

## 1. Probes and reading notes

Harness: throwaway work repo + bare origin + a green CI record (`CI_GATE_RUNS_JSON`), the REAL
`/home/user/agent-factory/scripts/push_clean.sh` run with cwd in the throwaway repo (same shape as
`tests/test_stale_ids.py`). Scratch: `$SCRATCH/vt243/` (`h.py` harness, one `pN.py` per probe).

### P1 (reproduced): a refusal in `--no-delegates-live` mode is not sticky

`p1.py`: a trailer commit, then a note citing its local id (7 chars). Run 1: rc 4, `stale_ids: notes.md:1 cites
5f18d03 ... it is 01b6b72 on origin`, origin unchanged. But the refused run has ALREADY moved the local branch to the
rewritten chain (`local HEAD moved by the refused run: b309dd004a14 -> b72688162198`). Run 2, the tree and the note
unchanged: rc 0, NO stale_ids output at all, `0b14940..b726881 -> feat`; origin's notes.md still cites 5f18d03, which
does not exist on origin. Mechanism: run 2 records the already-rewritten ids as OLD_IDS, the rewrite is a no-op, so
`rewritten` is empty and `stale_ids.py:79` returns 0 before it reads the diff.

### P2 (reproduced): the partial-fix shape of P1

`p2.py`: two trailer commits A and B; ledger.md cites A's local id, wiki.md cites B's. Run 1: rc 4 naming BOTH
(`ledger.md:1 cites 0d08839 ... 169c107`, `wiki.md:1 cites a734291 ... d542fad`). The fixer corrects the ledger to
169c107 (a commit carrying the trailer, as coordinator commits do) and re-runs: rc 0, `9dc4d25..c28aa14 -> feat`, no
stale_ids line; origin's wiki.md still cites a734291, which does not exist on origin.

### P3 (reproduced): `--lanes-live` IS sticky, and its correction path works (A.6, A.7 hold there)

`p3.py` (the real scripts committed into the throwaway repo, a declared dirty lane file): run 1 rc 4 naming
`notes.md:1 cites 4a3091a ... 6277c18`; the branch ref unchanged, origin at base, one worktree (no leak). Run 2 with
the note unchanged: rc 4 again (the worktree re-derives the rewrite from the untouched branch). The note corrected to
6277c18: rc 0, the branch ref followed origin on tree identity, 6277c18 is a commit on origin, the lane edit kept.
Side observation: each `--lanes-live` refusal leaves `refs/original/HEAD` in the main repo (the worktree's
filter-branch backup; refs/original is shared across worktrees). Pre-existing filter-branch behaviour, not this
change.

### P4/P5 (reproduced): the diff-shape sweep for A.8

Each case: a fresh repo, a trailer commit, then a note citing its local id; the real push_clean.

| shape | outcome |
|---|---|
| control (plain) | REFUSED rc 4, `notes.md:1 cites efca505 ... e0985e1` |
| `diff.mnemonicPrefix`; `diff.noprefix`+`diff.mnemonicPrefix` | REFUSED |
| `color.ui=always`; `color.diff=always` | REFUSED |
| `diff.external` (a no-op script); `GIT_EXTERNAL_DIFF` env | REFUSED |
| `diff.relative=true`, run at the root | REFUSED |
| `diff.relative=true`, run from `sub/` | rc 3 `1 trailer(s) remain — ABORT.` (filter-branch refuses a subdirectory; the pre-existing trailer check aborts before the stale check, so `diff.relative` never reaches stale_ids; the same rc 3 with no config) |
| a path with a TAB / a newline / a `"` | REFUSED, label C-escaped (`my\tnotes.md:1`, `my\nnotes.md:1`, `my\"notes.md:1`) |
| a path with a space | REFUSED, label carries git's trailing TAB (`my notes.md<TAB>:1`) |
| a path under a directory named `b/` | REFUSED, `b/notes.md:1` (only one `b/` stripped) |
| `core.quotePath=false`, non-ASCII name | REFUSED, `nötes.md:1` |
| added text starting `+++ b/x`, `++ `, `--- a/x`, `diff --git`, `@@ -1 +1 @@` | REFUSED (all five) |
| full 40-char id; 12-char id; an id in a `.../commit/<id>#diff-1` URL; `<id>...HEAD` | REFUSED, the new id printed at the token's length |
| a binary file changed in the same range, sorted before the note | REFUSED (the binary does not derail the parser) |
| **a note with a NUL byte (git: binary)** | **PUSHED rc 0; origin carries the stale citation** |
| **`.gitattributes` `notes.md binary`** | **PUSHED rc 0; origin carries the stale citation** |
| **`.gitattributes` `*.md -diff`** | **PUSHED rc 0; origin carries the stale citation** |
| **`core.bigFileThreshold=100` (config), a 330-byte note** | **PUSHED rc 0; origin carries the stale citation** |
| **`.gitattributes` `*.md diff=hide` + `diff.hide.textconv` (a lossy textconv)** | **PUSHED rc 0; origin carries the stale citation** |
| **`.gitattributes` `*.md diff=bin` + `diff.bin.binary=true`** | **PUSHED rc 0; origin carries the stale citation** |
| a textconv that FAILS (`tr` with a file operand) | rc 4 via `REFUSED by stale_ids (rc 2)`: git diff failed, fail-closed |

Mechanism (primary source, `scripts/stale_ids.py:42`): the diff call passes `--no-color --no-ext-diff
--src-prefix=a/ --dst-prefix=b/ -U0` but neither `--text` nor `--no-textconv`. For a file git classifies as binary
(NUL byte, the `binary`/`-diff` attribute, a `diff.<driver>.binary` driver, or a size over `core.bigFileThreshold`)
git prints `Binary files a/notes.md and b/notes.md differ` and no `+` line; porcelain `git diff` runs a configured
textconv by default, so the scanned text is the converted text.

### P6/P7 (reproduced): the other refusal codes, the mapping, `STALE_ID_OK`'s scope

- A Latin-1 note (invalid UTF-8) in a range with a trailer commit and NO citation: `stale_ids.py` dies on
  `subprocess.run(..., text=True)` with `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9` (a traceback;
  `ValueError` is outside the `except (OSError, CalledProcessError)`), push_clean prints `REFUSED by stale_ids (rc 1):
  NOT pushed. Cite each commit by its subject or by the new id` (a false and misleading refusal: no citation exists),
  and `STALE_ID_OK` cannot rescue rc 1. Fail-closed, so A.5 holds on the first run. The repo holds 0 tracked
  non-UTF-8 text files today (scan of `git ls-files`), so this is latent.
- P7a/P7b: after an rc 1 (decode) or rc 2 (git diff failed: a failing textconv) refusal, a PLAIN re-run pushes (rc 0),
  for the P1 reason; in P7b origin then carries the stale citation. So A.5's "never a silent pass" also holds only
  for the first run.
- P6c: a merge in the range with every commit at the same committer timestamp; notes cite both sides' old ids at 9
  chars. The positional old-to-new mapping named the true new id for all three (checked against the rewritten
  commits by subject). The zip-by-position mapping holds for merges with tied dates.

### B1-B3 (reproduced through a real `git commit` and the real pre-commit hook)

Harness: a throwaway repo from `git archive HEAD scripts .claude/hooks` plus the 20 files the vocabulary gate
requires; `core.hooksPath` points at a directory holding only a byte-identical copy of `scripts/hooks/pre-commit`
(blob ddcf5707a3fc), so the real post-commit's background reindexing (shared `/tmp` locks, the shared
codebase-memory store) never runs from a throwaway repo. Every probe commit went through the whole hook.

| shape | screen output | commit |
|---|---|---|
| staged `run.sh` with the AF-AP-145 shape | `AF-AP-145: 2` (lines 2 and 6) + the advisory line | lands |
| staged clean file | silent | lands |
| **the INDEX holds the hit, the tree was fixed after staging (the committed blob == the hit)** | **silent (MISS)** | lands with the hit |
| **the INDEX is clean, the tree holds an unstaged hit (the committed blob == clean)** | **`AF-AP-145: 2` printed for content not committed** | lands clean |
| **staged with hits, then `rm` from the tree (committed blob == the hit)** | **silent (MISS: `read_text` OSError is skipped)** | lands with the hit |
| `git commit -a`; `git commit -- run.sh` with another .sh staged (only mode, temp index) | the committed file only | lands |
| nested path, `git commit` run from a subdirectory | screened | lands |
| names with a space, non-ASCII, a TAB, a newline | all 4 screened (the newline name splits the printed line) | lands |
| `sandbox-kit/v.sh`, `.claude/h.sh` vs `sandbox-kit-other/x.sh`, `.claude-x/y.sh`, `sub/.claude/z.sh` | only the three look-alikes screened | lands |
| a `.sh` staged for deletion | silent | lands |
| a pure rename of a `.sh` with hits | screened under the new name | lands |
| `RUN.SH`, `run.bash`, an extensionless `hooks/pre-push` | silent (outside `*.sh`) | lands |
| a staged symlink `link.sh -> sandbox-kit/v.sh` | the vendored TARGET's 2 hits printed (the committed object is the link text) | lands |
| a dangling `.sh` symlink | silent | lands |
| a typechange (symlink to a regular `.sh` with hits; status `T`) | silent (T is outside ACMR) | lands |
| `GIT_LITERAL_PATHSPECS=1` in the env | silent (the `*.sh` pathspec is literal) | lands |
| `GIT_GLOB_PATHSPECS=1`, `top.sh` + `deep/run.sh` | only `top.sh` screened | lands |
| `AF_VENV=/nonexistent` (`$PY` falls back to python3) | screened | lands |
| the screen module raises at import (a parseable `raise`) | a traceback printed | lands (B.2 holds) |
| the screen module has a SyntaxError | a traceback printed | BLOCKED, but by the vocabulary gate (`gate-file-unparseable: .claude/hooks/edit-snapshot.py`), not by the screen |
| 300 staged `.sh` files with hits | 600 hits, capped per class | lands, 2.23 s wall |

Mechanism of the three bold rows (`scripts/ap_screen.py:92-95` then `:51`): the NAMES come from the index
(`git diff --cached --name-only`), the CONTENT from the working tree (`Path(top) / n` then `read_text()`). The commit
message of "ap_screen: --staged-shell ..." names this as a known limit; the frozen contract B.3 ("Unstaged changes
... are not screened") and B.1 ("Every staged ... file ... is screened") carry no such carve-out.

Hang check: all 49 AP_SCREEN rows over the repo's 101 first-party `.sh` files x3 (2.4 MB): 1.81 s; eight adversarial
texts (200k spaces, 100k quotes, 50k nested parens/brackets, 300k-char words, `startswith("` x20000, `trap ` x50000):
under 0.15 s each. No hang.

Noise floor: `ap_screen.py` over all 101 first-party `.sh` files prints 93 hits (AP-32: 22, AP-51: 16, AF-AP-118: 13,
AF-AP-145: 10, AF-AP-72: 10, ...); most are Python rows firing on heredoc Python or comments. A commit touching one
of those files prints them every time. Advisory, so information, not a defect.

### C1 (reproduced: the row directly and the hook's real `main()`)

The AF-AP-200 row fires on `startswith("+++")`, `startswith('--- a/')`, `startswith( "+++ b/" )`, a
`startswith(` wrapped before its string, `startswith("+++b/")`; it stays silent on `startswith("---")`,
`startswith("---\n")`, `startswith("+")`, `startswith("++")`, YAML `startswith("--- ")`, `startswith("--- a")`,
`startswith("diff --git ")` and a docstring that mentions a `+++ ` line. Through the hook's `main()` (a PostToolUse
Edit payload for a scratch `.py`): the header parse prints the AF-AP-200 line; front matter prints none. It does NOT
fire on header parses the regex does not name: `startswith(r"+++ ")`, `startswith(b"+++ ")`, the tuple form
`startswith(("+++ ", "--- "))`, an f-string, `l[:4] == "+++ "`, `re.match(r"\+\+\+ b/", l)`, `"+++ b/" in l`,
`startswith("--- ")`, and shell (`grep '^+++ '`, `case "+++ "*`).

False-positive rate over first-party production code (the brief's command reads only the top-level `*.py` of each
directory, so I also ran every tracked first-party `*.py` and `*.sh`): 4 production hits, all diff parsers:
`harness-ports/bin/codex-hook-adapter.py:91`, `scripts/lint_delta.py:99`, `scripts/jev_echo.py:89` (the registry's
three WATCH sites; the registry names jev_echo at :54, the tell fires at the `+++ ` test on :89) and
`scripts/stale_ids.py:47` (the hardened form: `+++ ` read only inside the header block, reviewed-safe; the tell cannot
tell it from the broken form). 0 front-matter or single-`+` false positives. A `git grep` for `+++` / `--- a/` over
first-party code finds no parse site the tell misses today.

### P8-P10 (reproduced)

- P8 (the token-by-id loop): 301 rewritten commits, 30,000 added lines, 90,000 hex tokens (12 and 40 chars): the whole
  refused push_clean run 7.3 s; `stale_ids.py` alone, the same invocation push_clean makes: rc 4 in 1.71 s. Linear;
  no hang.
- P9 (the old-ids temp file): the refusal path (rc 4) removes it; the exit-3 path (`N trailer(s) remain — ABORT`,
  reached by running push_clean from a subdirectory) leaks `/tmp/push-clean-ids.*` (my P4 runs leaked two; I removed
  them). The exit-2 path (TREE MISMATCH) and an errexit failure at `push_clean.sh:99` leak the same way (static read:
  no trap; `rm -f` only at `:117`).
- P10 (`--lanes-live`, A.7): a lane holding a dirty, permissive `scripts/stale_ids.py` (`sys.exit(0)`, declared in
  `.lanes-live`) does not decide: the worktree's committed checker refuses (rc 4, origin at base); `STALE_ID_OK`
  reaches the inner run (`pushing anyway (STALE_ID_OK=FAKE ...)`, rc 0, the branch followed origin); a message
  citation warns in the inner run.
- Adjacent consumers, fresh: `python3 scripts/vendored_manifest.py --check` -> `PASS: sandbox-kit/VENDORED-MANIFEST.md
  matches 9 vendored roots` (the registry commit ran with SKIP_MANIFEST_CHECK=1); `bash scripts/test_summary.sh
  tests/test_ci_gate.py tests/test_hooks_worktree.py tests/test_shell_syntax.py tests/test_no_laya_in_gates.py` ->
  `pytest-summary: 248 passed in 26.97s` (4 files set=107840e24a49).
- A staged `dev.sh -> /dev/zero` (and `/dev/urandom`) symlink: `--staged-shell` reads the device until MemoryError
  (under a 1 GB `ulimit -v` in my probe: rc 1 after 3.5 s / 4.4 s). The real hook sets no cap, so it would consume the
  container's memory before the `|| true` lets the commit go. I did not run it uncapped.

## 1b. Mutation audit (scratch mirrors under `$SCRATCH/vt243/mut/`, one fresh copy per mutant, blobs from HEAD)

Baseline mirror: `9 passed` (tests/test_stale_ids.py), `194 passed` (the two B/C files; the mirror also needs
`tests/test_s0_01_frame_tee.py`, which TestAFAP181 reads). New-shape probes: `aprobes.py` (A), `bmut.py` (B).

| mutant | committed tests | my new-shape probes |
|---|---|---|
| A-m1 drop `--no-ext-diff` | **SURVIVED 9 passed** | red: diff.external |
| A-m2 drop `--no-color` | **SURVIVED 9 passed** | red: color.ui=always |
| A-m3 drop `--src-prefix/--dst-prefix` | SURVIVED 9 passed | none: an equivalent mutant (the hardened parser reads any `+++ ` header line as a label and never drops a line; the flags are defence in depth now) |
| A-m4 HEX max 40 -> 12 | **SURVIVED 9 passed** | red: the 40-char citation |
| A-m5 `STALE_ID_OK` rescues any rc | **SURVIVED 9 passed** | red: STALE_ID_OK + a git failure pushed |
| A-m6 drop `-U0` | **SURVIVED 9 passed** | red: the line label (line 5 reported wrong), the rename label |
| A-m7 keep `b/` in the label | KILLED 1 failed | red |
| A-m8 drop added lines starting `++` | KILLED 1 failed | - |
| A-m9 every id counts as rewritten | KILLED 2 failed | - |
| A-m10 mapping check removed | KILLED 1 failed | - |
| A-m11 `return 0` | KILLED 5 failed | red (6 probes) |
| A-m12 message citation fatal | KILLED 1 failed | - |
| A-m13 no lookbehind boundary | KILLED 1 failed | - |
| A-m14 rev-list without `--reverse` | KILLED 3 failed | red: full40 |
| A-m15 `+++ ` read as a header anywhere | KILLED 1 failed | - |
| A-m16 the checker call removed | KILLED 6 failed | red (7 probes) |
| B-m1 `--diff-filter=AM` (no R/C) | **SURVIVED 194 passed** | red: a renamed .sh |
| B-m2 vendored prefixes without the slash | **SURVIVED 194 passed** | red: `sandbox-kit-other/x.sh` |
| B-m3 quiet dropped | KILLED 1 failed | - |
| B-m4 `--cached` dropped | KILLED 2 failed | red |
| B-m5 split on newline, not NUL | KILLED 1 failed | red |
| B-m6 the hook's `|| true` dropped | KILLED 1 failed | - |
| C-m1 drop the `--- a/` alternative | KILLED 1 failed | - |
| C-m2 `+++` -> `++` | KILLED 1 failed | - |
| C-m3 neutered | KILLED 2 failed | - |
| C-m4 broadened to `---` | KILLED 1 failed | - |

Candidate fixes (to prove each blocker's discriminator separates the defective blob from a corrected one; NOT a
repair, nothing written to the repo):
- A sticky (`push_clean.sh`: `HEAD_BEFORE=$(git rev-parse HEAD)` before filter-branch; on a stale_ids refusal
  `git update-ref HEAD "$HEAD_BEFORE"`): the plain re-run is refused again; A.6 still holds (the reported new id
  c59ce7c is a commit on origin after the corrected note pushes: the rewrite is deterministic). The committed suite
  shows `1 failed, 8 passed`: its helper `_new_id` derives the new id from LOCAL history, which only a rewritten local
  branch provides (the test encodes P1's behaviour, not a contract item); it would read the id from the refusal
  message instead.
- A binary (`stale_ids.py`: `--text --no-textconv`, `errors="surrogateescape"`): `9 passed`; all five binary/config
  shapes refused with origin untouched; the Latin-1 note with no citation now pushes (rc 0); a 20 MB random binary
  with no citation pushes in 2.9 s (2.0 s at the PIN).
- B index (`ap_screen.py --staged-shell` screens `git cat-file blob :<path>` instead of the tree file): `194 passed`;
  all five B probes per contract (rename, look-alike, index hit + tree fixed, index clean + tree hit, staged then
  removed).

## 1c. Evidence audit (the builder's claims, re-derived)

- "the same file against the committed checker: 3 failed, 6 passed" (stale_ids commit): REPRODUCED, the current
  tests against blob `2304181:scripts/stale_ids.py` -> `3 failed, 6 passed in 4.57s`.
- The four new B tests red before the change: REPRODUCED, against `41b79a8^` ap_screen.py + pre-commit ->
  `4 failed, 6 passed`.
- TestAFAP200 red before the row: REPRODUCED as a collection error (`KeyError` on `_AP_BY_ID["AF-AP-200"]`), `1 error`.
- The builders' mutants: my equivalents agree (checker removed 6 failed at 9 tests; boundary 1; message fatal 1;
  quiet 1; `--cached` 2; `|| true` 1). "4 of 4 mutants killed" is true of the mutants chosen; the suites leave five A
  mutants and two B mutants alive (table above).
- The "Known limit" in the ap_screen commit message is TRUE and REPRODUCED, in both directions (a false hit from the
  tree, a miss of the committed blob); it is not carried into the frozen contract B.3.
- The registry's WATCH lines: `codex-hook-adapter.py:91`, `lint_delta.py:99` confirmed; `jev_echo.py:54` is the
  `_side_path` label function the row describes (the tell fires on `:89`; `:84`'s `startswith("--- ")` is a header
  parse the tell does not name).
- Live data during this run (read from the log, not observed): the ledger records the 21:4xZ push as refused once on
  `sandbox-kit/VENDORED-MANIFEST.md:4` and pushed after the correction ("VENDORED-MANIFEST: the provenance line cites
  the commit id push_clean gave it ..."); a second correction at 22:08:35Z ("... cites the rewritten id a9094a6 (the
  stale-id check, task #243 ...)") attributes itself to the check, and its message does not say whether a refusal
  preceded it. The first-run refusal and the fix-and-rerun path have worked in production at least once.

## 1d. Reproduced vs reviewed vs skipped

Reproduced through the real scripts: every row in sections 1 to 1c. Reviewed statically only: the origin ref moving
mid-run (a count change fails closed at `stale_ids.py:74-77`; a foreign push makes `git push` non-fast-forward); the
exit-2 and errexit temp-file leaks; the pre-existing race of a commit landing between the check and `git rev-parse
HEAD` at `push_clean.sh:127` (the trailer check shares it). Skipped: "a message citation of the commit's own old id"
(a commit cannot contain its own id; not constructible); anything on the PC or a real origin (no bridge, no outward
action); the code-intel quartet (the four files are small and were read whole; the only callers were found by a
literal `git grep`: `stale_ids.py` is called only at `push_clean.sh:116`, `--staged-shell` only at `pre-commit:148`,
and `core.hookspath=scripts/hooks` is set in the real repo's `.git/config`).

## 2. Finding inventory (no severity filter)

Evidence levels: REPRODUCED (a command in this run, through the real script), STATIC (read from primary source).
Canonical path: the real `push_clean.sh` (blob b3f0faeeaa81) calling the real `stale_ids.py` (0d2a66ea9009) in a
throwaway repo with a bare origin; a real `git commit` through a byte-identical `pre-commit` (ddcf5707a3fc) calling the
real `ap_screen.py` (fb10f06b680b); the real `edit-snapshot.py` (fd6d5d54a3df) row and its `main()`.

### A — the stale-id push check (task #243)

**A-F1 BLOCKER — a refusal in `--no-delegates-live` mode is not sticky: a plain re-run pushes the stale citation.**
- Evidence: REPRODUCED (P1, P2, P7a, P7b). Canonical: yes.
- Mechanism: the refused run's filter-branch has already moved the local branch to the rewritten commits
  (`push_clean.sh:101-104` rewrites `refs/heads/<branch>`; the refusal at `:118-124` leaves it there). The next run
  records the rewritten ids as OLD_IDS, the rewrite is a no-op, `rewritten` is empty, and `stale_ids.py:79` returns 0
  before it reads the diff: no refusal, no warning, no `STALE_ID_OK` needed. The same holds after an rc 1 or rc 2
  refusal (P7b: a git failure, then a silent push of the stale citation). `--lanes-live` does not have the defect
  (the branch ref is never moved on a refusal: P3 refused twice).
- Material effect: origin receives a note citing a commit id that does not exist there, the exact defect task #243
  exists to stop. The realistic trigger is the documented flow itself: "Cite each commit ... commit, and run
  push_clean again" after fixing only some of the named lines (P2: two named, one fixed, the other pushed silently).
- Contract mapping: A.1, read with A.6. A.6 frames the next run as part of the contract ("After a refusal, the note
  corrected to the new id pushes"), which implies an uncorrected note does not; the push that finally lands delivers
  the rewritten commits whose rewrite replaced the cited id. If the coordinator reads A.1's "this push's rewrite" per
  invocation instead, A-F1 is a CONTRACT-DEFECT (it falsifies evidence on the exact production path) returned for an
  explicit amendment.
- Discriminator: `aprobes.sticky` (refuse, re-run unchanged, expect rc 4 and origin at base): red at the PIN, green on a
  two-line candidate (record `HEAD_BEFORE`; on a stale_ids refusal `git update-ref HEAD "$HEAD_BEFORE"`), which keeps
  A.6 (the reported new id becomes real on origin after the corrected push).
- Suggested fix: restore the pre-rewrite head on any stale_ids refusal (or persist the old-to-new map across runs);
  update the committed test's `_new_id` helper to read the new id from the refusal line.

**A-F2 BLOCKER — a binary file, or a config that reshapes the diff, hides a citation (A.8).**
- Evidence: REPRODUCED (P4, P5). Canonical: yes.
- Shapes that push the stale citation (rc 0, origin carries it): a NUL byte in the note; `.gitattributes`
  `notes.md binary`; `*.md -diff`; `core.bigFileThreshold=100` (a config); `*.md diff=hide` + `diff.hide.textconv`
  (a lossy textconv); `*.md diff=bin` + `diff.bin.binary=true`.
- Mechanism: `stale_ids.py:42` passes neither `--text` nor `--no-textconv`; git prints `Binary files a/... and
  b/... differ` with no `+` line, and porcelain `git diff` runs a configured textconv by default.
- Material effect: a stale citation reaches origin. None of these attributes or configs exists in this repo today (no
  `.gitattributes`; `git config --list` shows no textconv or bigFileThreshold), so it does not bite the current tree.
- Contract mapping: A.8 ("a config (..., ...)" covers textconv, bigFileThreshold and a driver's `binary`; "a binary
  file" covers the NUL byte and the attributes). If "a binary file" meant only "a binary neighbour does not derail
  the parser", that reading HOLDS (P5); the three config shapes still fall under "a config".
- Discriminator: `aprobes.binary` red at the PIN; green on a candidate (`--text --no-textconv`,
  `errors="surrogateescape"`), with the 9 committed tests green and a 20 MB binary pushing in 2.9 s.
- Suggested fix: the candidate above (it also fixes A-F3).

**A-F3 FOLLOW-UP — a non-UTF-8 text file in the net diff makes a false, misleading refusal with no override.**
- Evidence: REPRODUCED (P6a). Canonical: yes. `subprocess.run(..., text=True)` (`stale_ids.py:28`) raises
  `UnicodeDecodeError`, which the `except (OSError, CalledProcessError)` at `:87` does not catch: a traceback, rc 1,
  `REFUSED by stale_ids (rc 1) ... Cite each commit by its subject`, though nothing cites anything; `STALE_ID_OK`
  cannot rescue rc 1. Fail-closed, so A.5 holds. Latent: 0 tracked non-UTF-8 text files today.
- Fix: decode with `errors="surrogateescape"` (the A-F2 candidate), or catch `ValueError` with a clear message.

**A-F4 FOLLOW-UP — the committed suite leaves five mutants alive; A.7 and most A.8 shapes have no committed test.**
- Evidence: REPRODUCED (section 1b). Alive: drop `--no-ext-diff`, drop `--no-color`, HEX max 40 to 12, `STALE_ID_OK`
  rescuing any rc, drop `-U0` (line labels wrong on a modified file). Untested: A.7 (`--lanes-live`), and in A.8
  `diff.mnemonicPrefix`, `color.*`, `diff.external`, a rename, a binary file.
- Fix: add the P3/P4/P10 shapes and `aprobes.py` cases as tests (each is a ready fixture).

**A-F5 FOLLOW-UP — the old-ids temp file leaks on the exit-2, exit-3 and errexit paths.**
- Evidence: REPRODUCED for exit 3 (P9), STATIC for exit 2 and an errexit at `push_clean.sh:99`. `rm -f` runs only at
  `:117`. Fix: `trap 'rm -f "$OLD_IDS"' EXIT` right after the `mktemp`.

**A-F6 INFO — path labels.** A path with a space prints git's trailing TAB (`my notes.md<TAB>:1`); quoted names print
C-escaped (`my\tnotes.md:1`, `my\"notes.md:1`). The token, the new id and the line are right.

**A-F7 INFO (pre-existing) — push_clean from a subdirectory aborts with rc 3 `1 trailer(s) remain — ABORT.`**
filter-branch refuses a subdirectory and `|| true` hides why; this also makes `diff.relative` unreachable for
stale_ids (at the root it has no effect: REFUSED as expected).

**A-F8 INFO (pre-existing) — each `--lanes-live` refusal leaves `refs/original/HEAD` in the main repo** (the
worktree's filter-branch backup; refs/original is shared).

**A-F9 INFO — the transcript-sync push (`push_clean.sh:135-146`) runs after the check by design.** The digests quote
local ids from the chat (`e0d2bdc`, `2b2aa18` in `transcripts/sandbox/chat-2026-09-24.md` at HEAD). A log, not a
note; outside the contract's purpose.

**A-F10 INFO — the explicit prefix flags are now detection-equivalent** (A-m3 survives with no probe red): the
hardened parser never drops an added line, so the committed noprefix test no longer discriminates them. Defence in
depth.

**A-F11 INFO — `stale_ids.py`'s docstring lists exits 0, 2 and 4; an uncaught exception exits 1 (A-F3).**

**A-F12 INFO — held under attack:** A.1 (7, 12 and 40-char tokens; an id in a `.../commit/<id>#diff` URL; `<id>...HEAD`;
a symlink target; a `b/` directory name; the file:line and new id at the same length); A.2; A.3; A.4; A.5 on the first
run (a failing textconv: rc 2 refused); A.6 in both modes; A.7 (the refusal sticky there, a dirty permissive checker
ignored, `STALE_ID_OK` and the message warning reach the inner run); A.8 for `diff.noprefix`, `diff.mnemonicPrefix`,
both together, `color.ui`/`color.diff=always`, `diff.external`, `GIT_EXTERNAL_DIFF`, `diff.relative` at the root,
TAB/newline/quote/space/non-ASCII names, `core.quotePath=false`, added text starting `+++ b/`, `++ `, `--- a/`,
`diff --git`, `@@`, a binary neighbour, a rename; a merge with tied timestamps (mapping correct); 301 rewritten
commits x 90,000 tokens in 1.71 s.

### B — the staged-shell screen (task #245)

**B-F1 BLOCKER (on the frozen B.3 wording) — the screen reads the working tree, not the staged content.**
- Evidence: REPRODUCED through real commits (B1, B3). Canonical: yes.
- Mechanism: `ap_screen.py:92-95` takes the NAMES from the index (`git diff --cached --name-only -z`) and the CONTENT
  from the tree (`Path(top) / n`, then `read_text()` at `:51`; an OSError is skipped at `:52-53`).
- Effect: (a) index holds the AF-AP-145 shape, tree fixed after staging: silent, and the commit lands with the shape;
  (b) index clean, tree holds an unstaged hit: `AF-AP-145: 2` printed for content not committed; (c) staged with
  hits then removed from the tree: silent, the commit lands with the hits.
- Contract mapping: B.3 ("Unstaged changes ... are not screened": (b) screens one) and B.1 ("Every staged ... file ...
  is screened": (a) and (c) screen something else). The builder's commit message names this as a known limit ("a
  file staged clean and then edited is screened as edited"); the frozen contract carries no such carve-out.
- Reach: none in the normal `scripts/safe_commit.sh` flow (it stages the named paths and commits at once); reached by
  stage-then-edit, a partial `git add -p` by a human, or stage-then-delete.
- Discriminator: `bmut.py` probes `b_partial_miss`, `b_partial_unstaged`, `b_removed`: red at the PIN, green on a
  candidate that screens `git cat-file blob :<path>`, with all 194 committed tests green.
- Suggested fix: screen the index blob (label with the repo path). If the coordinator instead amends B.3 to accept
  the known limit, B-F1 becomes a FOLLOW-UP.

**B-F2 FOLLOW-UP — a typechange is not screened.** A `.sh` symlink replaced by a regular script with hits has status
`T`, outside `--diff-filter=ACMR`: silent (B3). Fix: `ACMRT`.

**B-F3 FOLLOW-UP — a staged `*.sh` symlink is followed.** `link.sh -> sandbox-kit/v.sh` prints the vendored target's
hits (the committed object is the link text); `dev.sh -> /dev/zero` reads until MemoryError (1 GB cap in my probe:
3.5 s; the hook has no cap). Hostile and unlikely; the index-blob read removes both.

**B-F4 FOLLOW-UP — the `*.sh` pathspec depends on the environment.** `GIT_LITERAL_PATHSPECS=1`: nothing screened;
`GIT_GLOB_PATHSPECS=1`: only top-level files (`deep/run.sh` missed). Fix: list with `-z` and no pathspec, filter
`endswith(".sh")` in Python.

**B-F5 FOLLOW-UP — the committed suite leaves two mutants alive:** `--diff-filter=AM` (no rename) and the vendored
prefixes without the slash (`sandbox-kit-other/` excluded). No test covers a rename, a look-alike directory or a
partially staged file.

**B-F6 INFO — noise floor.** The Python-oriented AP_SCREEN rows print 93 hits over the 101 first-party `.sh` files
(AP-32: 22, AP-51: 16, AF-AP-118: 13, AF-AP-145: 10, AF-AP-72: 10, ...), mostly heredoc Python and comments; a commit
touching one of those files repeats them each time. Advisory; a shell-specific row subset is an option.

**B-F7 INFO — outside `*.sh`:** the extensionless shell hooks (`scripts/hooks/*`, which the SHELL SYNTAX GATE does
cover) and `*.bash` are not screened.

**B-F8 INFO — printed paths are absolute; a newline in a file name splits the printed line.**

**B-F9 INFO — held under attack:** B.2 (a module that raises at import prints a traceback and the commit lands; a
module with a SyntaxError is blocked by the vocabulary gate, `gate-file-unparseable`, not by the screen); B.3 for an
unstaged change to a file that is not staged, and for untracked files; look-alike directories screened, vendored
excluded; names with a space, non-ASCII, a TAB, a newline; a commit started in a subdirectory (also with
`diff.relative=true`); `git commit -a`; only mode with another file staged; a deletion silent; a rename screened under
its new name; `AF_VENV` missing; 300 files in 2.23 s; no regex hang (2.4 MB of shell in 1.81 s, adversarial texts
under 0.15 s each).

### C — the AF-AP-200 tell

**C-F1 INFO — the contract holds.** Fires on `startswith("+++`, `startswith('--- a/`, spaced and wrapped forms;
silent on front matter `startswith("---")`, `startswith("---\n")`, a single `+`, `++`, YAML `--- `, `--- a`,
`diff --git`, a docstring. Through the hook's `main()`: the header parse prints the AF-AP-200 line; front matter
none. The tests go red on the pre-row hook (collection error) and on four regex mutants.

**C-F2 FOLLOW-UP — header parses the regex does not name stay silent:** `startswith(b"+++ ")`, `startswith(r"+++ ")`,
the tuple form `startswith(("+++ ", "--- "))`, an f-string, `l[:4] == "+++ "`, `re.match(r"\+\+\+ b/", l)`,
`"+++ b/" in l`, `startswith("--- ")`, and shell (`grep '^+++ '`, `case "+++ "*`). A live instance:
`scripts/jev_echo.py:84` (`ln.startswith("--- ")`).

**C-F3 INFO — false positives over first-party production code: 1 of 4 hits.** The four: the registry's three WATCH
sites (`codex-hook-adapter.py:91`, `lint_delta.py:99`, `jev_echo.py:89`) and the hardened `stale_ids.py:47`
(reviewed-safe; a tell cannot tell the fixed form from the broken one). No front-matter or single-`+` false positive;
`git grep` finds no parse site the tell misses in the current code.

**C-F4 INFO — the brief's command (`ap_screen.py scripts proofs harness-ports`) reads only each directory's top-level
`*.py`** (`_files` does not recurse), so it misses `harness-ports/bin/codex-hook-adapter.py`; the recursive run finds it.

**C-F5 INFO (pre-existing) — the hook prints `AF-AP-200a diff header ...`** with no space: `{ap_id:6s}` pads to 6
characters, so every AF-AP id runs into its message.

**C-F6 INFO — the row cannot block a commit:** `lint_delta.py` blocks on new pyflakes hits only; its AP_SCREEN pass over
staged `.py` added lines prints tells.

## 3. Gate recommendations

### A — the stale-id push check: **NOT-READY** (A-F1 and A-F2; A-F1's mapping reads A.1 with A.6 as "the push that delivers the rewrite"; under a per-invocation reading A-F1 is a CONTRACT-DEFECT returned for amendment; A-F2's shapes do not exist in this repo today)

| predicate | A-F1 (non-sticky refusal) | A-F2 (binary / diff-reshaping config) |
|---|---|---|
| 1 contract mapping | A.1 with A.6 (only a CORRECTED note pushes after a refusal) | A.8: "a config (..., ...)" and "a binary file" |
| 2 canonical reproduction | real push_clean.sh at the PIN: P1, P2, P7a, P7b | real push_clean.sh at the PIN: P4, P5 (six shapes) |
| 3 material effect | a stale citation reaches origin, rc 0, silent | a stale citation reaches origin, rc 0, silent |
| 4 concrete discriminator | `aprobes.sticky`: red at the PIN, green on a 2-line candidate | `aprobes.binary`: red at the PIN, green on a 2-line candidate (9 committed tests green) |
| 5 task ownership | `push_clean.sh:101-125` | `stale_ids.py:28,42` |

One focused repair covers both, plus A-F3..A-F5 at little cost.

### B — the staged-shell screen: **NOT-READY** (B-F1, on the frozen B.1/B.3 text; if the coordinator amends B.3 to accept the builder's documented known limit, B is MERGE-READY-WITH-FOLLOWUPS)

| predicate | B-F1 (working tree read, not the staged blob) |
|---|---|
| 1 contract mapping | B.3 (an unstaged change IS screened) and B.1 (the staged content is NOT what is screened) |
| 2 canonical reproduction | a real `git commit` through the byte-identical pre-commit and the real ap_screen.py |
| 3 material effect | the only output names content not committed and misses content committed (reach: none in the normal safe_commit.sh flow) |
| 4 concrete discriminator | `b_partial_miss` / `b_partial_unstaged` / `b_removed`: red at the PIN, green on the index-blob candidate (194 committed tests green) |
| 5 task ownership | `ap_screen.py:92-95` |

### C — the AF-AP-200 tell: **MERGE-READY-WITH-FOLLOWUPS** (no finding meets the predicate; follow-up C-F2)

| predicate | C-F2 (unnamed header-parse shapes) |
|---|---|
| 1 contract mapping | none: C names `startswith("+++` / `startswith("--- a/`, which fire |
| 2 canonical reproduction | the row and the hook's `main()`: reproduced |
| 3 material effect | a coverage gap of an advisory tell; no stated output changes |
| 4 concrete discriminator | the C1 battery |
| 5 task ownership | `edit-snapshot.py:356` |
| blocks? | no (fails 1 and 3) |

Standing rules kept: no commit, push, PR, comment, GitHub write or bridge call; no git write in the real repo (every
git write ran in throwaway repos under `$SCRATCH/vt243/runs/`); `scripts/gpu_window.sh` and its tests untouched;
`.jev/intercept-off` neither created nor removed; mutants on scratch copies only; no kill of any process; FAKE strings
for the trailer (built from parts) and `STALE_ID_OK` reasons. Two `/tmp/push-clean-ids.*` files my P4 runs leaked
through A-F5 were removed. Separator check: 0 on the report and on all 27 scratch scripts. At the end I deleted my
throwaway repos and mirrors (`$SCRATCH/vt243/{runs,mut,bt}`, 379 MB; the disk was 94% full). The scripts rebuild them:
`h.py fresh()` for A; for B, `runs/bbase` = `git archive HEAD scripts .claude/hooks` plus the 20 files the vocabulary
gate names, one base commit, and `core.hooksPath` at a directory holding only a copy of `pre-commit`.
