# VERIFY-J1-0 — adversarial verify of the never-a-gate screen (KC-J1's mechanism)

Lane: VERIFY-J1-0 (sandbox, Opus 5 `adversarial-verifier`). PIN 98a604a (the J1-0 landing commit).
Frozen contract: `tasks/briefs/laya/J1-0-brief.md` (six contract items + nine tests + m1-m5) · `seeds/seed-laya-j1-v1.yaml` AC 5 `ac_508de0f12c24907c` + AC 6 `ac_77ae22bcda8a6aab` · `docs/research/COUNCIL-VERDICT-JEV-LAYA-v1.md:45` (`KC-J1 — gate reachability`).
Builder report `tasks/briefs/laya/J1-0-report.md` was treated as claims to attack, never as evidence.

**GATE RECOMMENDATION: NOT-READY** — two findings satisfy the complete blocking predicate (B1, B2), both in
`scripts/no_laya_in_gates.py`, both reproduced through a real `git commit` over the real `scripts/hooks/pre-commit`, both
with a corrected-vs-defective discriminator that keeps all nine frozen tests green. Everything else the contract names
works: the screen blocks a real violating commit, the negative control commits, the index is authoritative in both
directions, the completeness walk blocks an unlisted new checker, and no environment variable bypasses it.

## Venue, isolation, instruments

- The shared tree was READ-ONLY. Scratch copy `git archive 98a604a | tar -x -C /tmp/vj10/tree`; every mutant, fixture and
  commit ran in `/tmp/vj10/` (a lean throwaway git repo, a lean mutant tree, 40 fixture trees). The only file this lane
  writes in the repo is this report. `git status` of the repo before and after shows only the other lanes' untracked paths.
- The J1-0 files are byte-identical at the PIN and at the session's later HEAD (`git diff --stat 98a604a HEAD --` over the
  five boundary paths: empty), so every finding below describes the live code. Screen sha256[:16] `5b5f6bbdb82c5a32`.
- Instruments named per claim: the real script, the real hook, real `git commit`, pytest (venv python), `su nobody`,
  `scripts/ap_screen.py`, `scripts/report_lint.py`, whole-tree literal grep at the PIN, `graft ask`.

## A. Item 1 — the landing gates reproduced (all pasted)

| Gate | Command (scratch copy at the PIN) | Result |
|---|---|---|
| suite ×2 | `python -m pytest tests/test_no_laya_in_gates.py -q -p no:cacheprovider --basetemp=/tmp/vj10/bt` | `9 passed in 0.80s` / `9 passed in 0.76s` (rc 0, rc 0) |
| live screen, worktree mode | `python scripts/no_laya_in_gates.py --root .` | `no_laya_in_gates: 33 files scanned, clean` rc=0 |
| live screen, staged mode | `python scripts/no_laya_in_gates.py --staged` (repo) | `no_laya_in_gates: 33 files scanned, clean` rc=0 |
| seed AC 5 | `python -m pytest tests/test_no_laya_in_gates.py -q` | `9 passed in 0.48s` rc=0 |
| seed AC 6 | the seed's `python3 -c "…assert 'no_laya_in_gates' in t…"` | `WIRED` rc=0 |
| pyflakes | `python -m pyflakes scripts/no_laya_in_gates.py tests/test_no_laya_in_gates.py` | no output, rc=0 |
| `bash -n` | `bash -n scripts/hooks/pre-commit` | rc=0 |
| RED state | screen removed + hook block `111,118d` on the scratch copy | `9 failed in 0.17s`; restored → `9 passed in 0.46s`, sha unchanged |

Non-vacuity of `test_live_tree_clean`: 41 files in the tree carry the vocabulary (`grep -rilE 'laya' | wc -l` → `41`) and
none of them is one of the 33 scanned. The screen's clean verdict is a real discrimination, not an empty set.

**The production path, end to end (the builder's report contains no real `git commit`; these are mine).** A throwaway repo
holding exactly the 33 listed files plus the screen and the hook reproduces the same `33 files scanned, clean`, so it is a
faithful stand-in for the gate surface.

| Case | Setup | Outcome |
|---|---|---|
| A | `laya` staged into `scripts/report_lint.py`, real `git commit` | `/tmp/vj10/repo/scripts/report_lint.py:146:laya` → `COMMIT BLOCKED by the never-a-gate screen (rc=3)`, commit rc=1, HEAD unchanged |
| B (neg. control) | identical commit shape, token removed | `no_laya_in_gates: 33 files scanned, clean` → commit rc=0 |
| C | violation staged, worktree copy reverted | BLOCKED rc=3 (the index is authoritative) |
| D | violation in the worktree only, unrelated file staged | commit rc=0 (contract: staged content is the object) |
| E | new `proofs/S0-13/check_x.py` staged, unlisted | `gate-file-unlisted: proofs/S0-13/check_x.py` → BLOCKED rc=4 |
| I | `SKIP_LINT_DELTA/SKIP_ANCHOR_CHECK/SKIP_MANIFEST_CHECK/SKIP_MIRROR_CHECK/SKIP_LAYA_GATE_CHECK/SKIP_ALL/NO_VERIFY` all set | still `COMMIT BLOCKED by the never-a-gate screen (rc=3)` |
| J | `AF_VENV=/nonexistent` (venv absent → `PY="python3"`) | still BLOCKED rc=3 |
| L | pathspec commit `git commit -m x scripts/report_lint.py`, violation never `git add`ed | BLOCKED rc=3 — git's temporary index is what `git show :<path>` reads, so that unstaged-edit route is closed |

## B. Finding inventory (discovery exhaustive; disposition in §F)

### B1 — BLOCKER. In `--staged` (the only production mode) a listed gate file absent from the INDEX is silently unscanned and the screen exits 0 "clean"

- Evidence: SOLID, reproduced through the real path (real hook, real `git commit`).
- Mechanism, two sites: `scripts/no_laya_in_gates.py:210` (`if not args.staged:`) switches the required-file existence
  control OFF in staged mode, and `scripts/no_laya_in_gates.py:230` (`if content is None:`) then drops the file with no
  diagnostic, because `scripts/no_laya_in_gates.py:105` (`except subprocess.CalledProcessError:`) turns a failed
  `git show :<path>` into `None`. `scripts/no_laya_in_gates.py:242` still prints `files scanned, clean` and returns 0;
  the only trace is the count falling 33 → 32, which nothing asserts and no gate reads.
- Contract mapping: contradicts frozen contract item 2 — "A listed path that does not exist exits 4 with
  `gate-file-missing: <path>`", stated with no mode qualifier — while item 6 mandates `--staged` as the production
  invocation, so the implementation makes the two mutually exclusive. It also matches an OPEN repository-wide invariant
  verbatim: `docs/INCIDENT-LOG.md:329` AF-AP-40, "presence-gated check … a required-file list that is only consulted when
  the file is present … deleting the file switches the check off and the success line still prints (fail-open by omission)".
- Reproduction (canonical, deterministic):
  - `git mv scripts/report_lint.py scripts/report_lint_v2.py`; append `# laya …` to the new name; `git add`; `git commit`
    → `no_laya_in_gates: 32 files scanned, clean`, `[master 2c4a806] case F`, commit rc=0 — a gate file carrying the
    forbidden vocabulary lands in the commit.
  - Minimal form: `git rm --cached scripts/report_lint.py` with the violation on disk → `32 files scanned, clean`, rc 0.
  - Permanent form: after the rename, every subsequent commit screens 32 files and says clean (`case G2`, rc 0).
  - The same tree in worktree mode DOES catch it — `python scripts/no_laya_in_gates.py --root .` → rc=4
    `gate-file-missing: scripts/report_lint.py` — so the control exists and is unreachable from the only consumer.
- Discriminator (defective vs corrected, same index state): PIN → `rc=0 / no_laya_in_gates: 32 files scanned, clean`;
  corrected (the existence check runs in both modes, using `git ls-files --error-unmatch` as the staged authority) →
  `rc=4 / gate-file-missing: scripts/report_lint.py`, and through the real hook
  `COMMIT BLOCKED by the never-a-gate screen (rc=4)`, commit rc=1. The corrected form keeps `9 passed in 0.50s`.
- Suggested fix (one hunk, in boundary): replace `scripts/no_laya_in_gates.py:210`'s mode gate with a per-mode presence
  test — `git ls-files --error-unmatch <entry>` in staged mode, `exists()` otherwise — and make `content is None` a
  `gate-file-unreadable: <path>` exit-4 line instead of `continue`, so no listed path can leave the scanned set silently.

### B2 — BLOCKER. In `--staged` the allowlist itself is read from the WORKTREE, so an unstaged edit to `scripts/gate_files.txt` shrinks the scanned set and a staged violation lands

- Evidence: SOLID, reproduced through the real path.
- Mechanism: `scripts/no_laya_in_gates.py:187` (`list_path = root / "scripts" / "gate_files.txt"`) and
  `scripts/no_laya_in_gates.py:193` (`entries = _load_allowlist(list_path)`) read the filesystem unconditionally; the
  `--staged` switch is applied only to the *contents* of the listed files, never to the list that defines them.
- Contract mapping: frozen contract item 6 states the purpose of `--staged` as "so a violation cannot be dodged by an
  unstaged edit", and frozen contract item 1 makes the allowlist the definition of the scanned set. An unstaged edit
  dodges a staged violation, which is precisely the case item 6 exists to exclude, and KC-J1 is an absorbing barrier
  (`docs/research/COUNCIL-VERDICT-JEV-LAYA-v1.md:45`).
- Reproduction: stage `# laya …` into `scripts/report_lint.py`; remove that one line from `scripts/gate_files.txt` in the
  worktree **without staging it**; `git commit` → `no_laya_in_gates: 32 files scanned, clean`, `[master cb4b377] case H`,
  rc 0, `1 file changed`. The committed tree then holds the violation **and** an allowlist that still lists the file.
- Blast radius, measured: the three structural patterns protect 18 of the 33 entries — removing a structural entry is
  caught (`gate-file-unlisted: scripts/hooks/post-commit`, rc 4). The 15 non-structural entries
  (`scripts/gate_files.txt:13-28`, `scripts/report_lint.py` through `harness-ports/bin/pc-lane.sh`) have no such backstop.
- Discriminator: corrected (in staged mode the list comes from `git show :scripts/gate_files.txt`) → rc=3
  `/tmp/vj10/repo/scripts/report_lint.py:146:laya`; defective → rc=0 `32 files scanned, clean`. Corrected keeps `9 passed in 0.45s`.
- Suggested fix (same hunk as B1): in staged mode read the allowlist from the index, falling back to disk only when the
  path is absent from the index.
- Honest caveat on the contract leg: item 6's parenthetical states both a mechanism (`git show :<path>` for listed files)
  and a purpose (no unstaged dodge). The mechanism is implemented; the purpose is defeated. A coordinator who reads that
  clause narrowly may grade B2 a FOLLOW-UP. **B1 stands on its own and is sufficient for NOT-READY.**

### F3 — FOLLOW-UP. An unreadable listed file is silently skipped: rc 0 with "0 files scanned, clean"

SOLID, reproduced through the real script, **not** through the production consumer. `scripts/no_laya_in_gates.py:114` (`except (OSError, UnicodeDecodeError):`) returns
`None`, and `scripts/no_laya_in_gates.py:230` (`if content is None:`) drops the file. Run as `nobody` over a
world-readable fixture whose single listed gate file contains `laya`: mode 000 → `rc=0`, `0 files scanned, clean`; the
paired positive control, same user, same file at mode 644 → `rc=3`, `/tmp/vj10/c3/perm/scripts/hooks/pre-commit:2:laya`. Readability is the
only difference. Blocking predicate fails at condition 2: the production consumer is `--staged`, which reads the index and
never touches the file's mode. Same fix as B1 (fail loud on an unread listed path).

### F4 — FOLLOW-UP. A listed path that is a directory is silently skipped (rc 0, "0 files scanned, clean")

SOLID, real script, fixture tree. The presence test at `scripts/no_laya_in_gates.py:213` (`if not fp.exists():`) accepts a
directory, then `scripts/no_laya_in_gates.py:114` (`except (OSError, UnicodeDecodeError):`) swallows `IsADirectoryError`. Reachable in git (delete `scripts/hooks/pre-commit`, add
`scripts/hooks/pre-commit/x`) but contrived. Closed by the same fail-loud fix.

### F5 — INFO. An unreadable parent directory crashes with an uncaught `PermissionError`

SOLID, real script as `nobody`: traceback at `scripts/no_laya_in_gates.py:137` (`for p in hooks_dir.iterdir():`), rc 1.
Fail-CLOSED (the hook blocks on any non-zero), so not a defect — but the message a committer sees is a traceback.

### F6 — FOLLOW-UP (contract gap, not a build defect). The allowlist omits at least seven real gate predicates that no structural pattern covers

SOLID, enumerated from primary sources (the hooks and the two workflow files), reproduced as "unlisted and unreachable by
the walk". The builder shipped the list frozen contract item 1 dictates, entry for entry, so this is the contract's gap:

| Unlisted gate-defining file | Where it is a predicate |
|---|---|
| `harness-ports/bin/sync-skills.sh` | `scripts/hooks/pre-commit:69` — `COMMIT BLOCKED` on `--check` failure |
| `harness-ports/tests/test_context_mirrors.sh` | `scripts/hooks/pre-commit:80` — the MIRROR gate |
| `harness-ports/bin/sync-lane-skills.sh` | `scripts/hooks/pre-commit:91` — the LANE-SKILLS gate |
| `scripts/verify-planning-repo.sh` | `planning-checks.yml` line 17 and `stage0-ci.yml` line 100 (CI steps) |
| `harness-ports/tests/run-all.sh` | `stage0-ci.yml` line 56 (CI step) |
| `scripts/fubuki_pin_sync.sh` | `stage0-ci.yml` line 28 — a declared input whose failure fails CI |
| `proofs/S0-05/run_canaries.sh` (+ `netns_lib.sh`, `tools/pc/run_s0_05_units.sh`) | writes the evidence the listed `proofs/S0-05/check_egress.py` grades |

Latent: `scripts/hooks/pre-commit:30` names `scripts/mutant_anchor_precommit.py`, which does not exist today; the day it
lands it is a hook predicate outside both the list and the three patterns. Suggested fix: add the seven to
`scripts/gate_files.txt` in J1-1, or add `harness-ports/bin/*.sh` + `harness-ports/tests/*.sh` as a fourth pattern.

### F7 — FOLLOW-UP. `.github/workflows/*.yaml` is outside the structural walk

SOLID, real script. `scripts/no_laya_in_gates.py:143` (`for p in wf_dir.glob("*.yml"):`) matches only `.yml`; GitHub
Actions accepts `.yaml` equally. A fixture tree with `.github/workflows/ci.yaml` containing `laya` → rc 0, neither listed
nor flagged. Frozen contract item 2 says `.yml`, so the code is conformant and the gap is the contract's. Fix: glob both.

### F8 — INFO. The walk is one level deep by design

`proofs/S0-01/sub/check_x.py` and `scripts/hooks/sub/helper.sh` are not found (rc 0 in both fixture trees):
`scripts/no_laya_in_gates.py:151` (`for p in sub.glob("check_*.py"):`) and the `is_file()` filter at
`scripts/no_laya_in_gates.py:138` (`if p.is_file():`). Matches the frozen patterns `proofs/*/check_*.py` and `scripts/hooks/*`. Noted only so
a future reader does not mistake the walk for a recursive one.

### F9 — FOLLOW-UP. The nine frozen tests gate only a fraction of the frozen vocabulary and exit-code contract

SOLID, reproduced by mutation on a lean scratch copy (full table in §C). Six mutants survive with `9 passed`: dropping all
four `DOTTED_TOKENS` (`scripts/no_laya_in_gates.py:31`), dropping the structural import check
(`scripts/no_laya_in_gates.py:47`, `_IMPORT_RE = re.compile(`), reducing `SIMPLE_TOKENS` (`scripts/no_laya_in_gates.py:24`) to `{"laya"}` — i.e. 10 of
the 11 contract tokens deletable — dropping the self-listing refusal at `scripts/no_laya_in_gates.py:197`
(`if e == SELF_PATH:`), turning both usage exits into 0, and deleting the whole missing-file control. The frozen contract
lists exactly these nine tests and the builder shipped exactly these nine, so this is a contract gap. Note the pairing:
`test_import_check` is killed by neither the dotted-token mutant nor the import-check mutant alone, because the two
matchers overlap on its single fixture line — only both together turn it red.

### F10 — FOLLOW-UP. `test_precommit_wired` proves a string, not the block

SOLID, reproduced both ways. `tests/test_no_laya_in_gates.py:182` asserts (`The screen is not wired into pre-commit`) and
`tests/test_no_laya_in_gates.py:185` that no `SKIP_.*LAYA` appears. A hook that runs the screen and ignores its exit code
(`RC=$?` at `scripts/hooks/pre-commit:114` replaced by `RC=0`) keeps the suite at `9 passed` **and** lets a real violating commit
land: `/tmp/vj10/repo/scripts/ap_screen.py:98:laya` printed, commit rc=0. The live hook does enforce (case A), so this is an ungated
property, not a defect. Fix: one test that runs the real hook in a throwaway repo and asserts the commit is refused with
`COMMIT BLOCKED by the never-a-gate screen` (`scripts/hooks/pre-commit:116`).

### F11 — FOLLOW-UP. List entries are not confined to `--root`

SOLID, real script. An absolute entry (`/etc/hostname`) is read — `root / entry` discards the root — and the run reports
`2 files scanned`; a `../outside/leak.txt` entry is read and fires (`../outside/leak.txt:1:laya`, rc 3). The direction is
fail-closed (a false violation, never a miss) and the list is committed and reviewed, so this is hardening, not a hole.
Fix: reject any entry that is absolute or escapes the root, with exit 64.

### F12 — INFO. A missing allowlist exits 64 under the exit-4 message prefix

SOLID. `scripts/no_laya_in_gates.py:190` prints `gate-file-missing: %s` and returns 64, while frozen contract item 2
reserves `gate-file-missing:` for the exit-4 completeness control. Any consumer keying on the prefix conflates the two.
Fix: a distinct prefix, e.g. `gate-list-missing:`.

### F13 — INFO. An empty or comment-only allowlist reports "0 files scanned, clean" (rc 0) when nothing structural exists

SOLID, real script. On the real tree the structural walk saves it — an emptied `scripts/gate_files.txt` gives rc 4
(`gate-file-unlisted: scripts/hooks/pre-commit` and 17 siblings) — so this is fail-closed here. It is the same class as
B2: the 15 non-structural entries are protected by nothing but the file's own content.

### F14 — INFO. The self-listing refusal is spelling-exact

SOLID. `scripts/no_laya_in_gates.py:197` compares `e == SELF_PATH`; a `./scripts/no_laya_in_gates.py` entry evades the
refusal, and the screen then scans its own source and reports 22 hits (rc 3) instead of the contract's exit 64. Both
outcomes block, so this is cosmetic. Fix: normalise the entry before comparing.

### F15 — FOLLOW-UP (operational). The completeness walk reads the worktree, so an UNTRACKED structural file blocks every commit

SOLID, reproduced through the real hook: a never-staged `proofs/S0-13/check_x.py` sitting in the worktree makes an
unrelated commit fail with `gate-file-unlisted: proofs/S0-13/check_x.py`, rc 4. Fail-closed and contract-conformant, but
in this shared multi-lane tree a scratch checker dropped by any lane freezes the coordinator's commits. Today's untracked
set (`scripts/laya_probe.py`, `tests/fixtures/decisions/probe/`) matches no pattern, so nothing is blocked right now.

### F16 — FOLLOW-UP (out of the J1-0 boundary). The barrier lives only at pre-commit; `--no-verify` and CI both pass it

SOLID by two instruments: a whole-tree literal sweep at the PIN finds exactly one invocation,
`scripts/hooks/pre-commit:113` (`"$PY" "$REPO_ROOT/scripts/no_laya_in_gates.py" --staged`), and `graft ask` returns no
referencing file other than the script itself (lexical ranking; both instruments are blind to subprocess edges, which does
not matter here because the reference is a literal path). `git commit --no-verify` commits the violation with the hook
never running, and `scripts/hooks/pre-push` carries no equivalent gate. KC-J1 is written as continuous — "at any time
after the screen lands" (`docs/research/COUNCIL-VERDICT-JEV-LAYA-v1.md:45`) — which a commit-time-only hook cannot give.
Frozen contract item 6 asked for pre-commit only and forbade touching the workflows, so this is an escalation for J1-1+:
run `scripts/no_laya_in_gates.py --root .` as a CI step.

### F17 — INFO + bug-echo action. The AP screen flagged seven false AF-AP-40 hits in this file and missed the real one

SOLID, both reproduced. `python3 scripts/ap_screen.py scripts/no_laya_in_gates.py` returns `AF-AP-40: 7` at
`scripts/no_laya_in_gates.py:136`-`:152` (`if hooks_dir.is_dir():`); the builder called them
`necessary guards` at `tasks/briefs/laya/J1-0-report.md:127`, which is correct for all seven. The genuine AF-AP-40 instance — B1 — sits at
`scripts/no_laya_in_gates.py:210` and `scripts/no_laya_in_gates.py:230` and matches no current screen signature. Action for
the increment that fixes B1: add a signature for `if <var> is None: continue` inside a scanning loop, and for a required
check gated on a MODE flag, to the registry row and the `AP_SCREEN` list.

### F18 — INFO. Evidence audit of the builder's report: reproduces, with two loose phrasings

SOLID. Reproduced: the RED run (mine `9 failed in 0.17s` against the claimed `9 failed in 0.20s`), both GREEN runs, the
33-file count and its 3+2+14+1+13 decomposition, the 247/42/187/119 line counts, the block at `scripts/hooks/pre-commit:111`
through `:118` with `exit 0` at `scripts/hooks/pre-commit:119`, the seven AP-40 lines, and the lint summary
`21 refs — OK 14, NEAR 0, MISS 0, UNCHECKABLE 7, UNRESOLVED 0`. Two imprecisions, neither material: the m2 row at
`tasks/briefs/laya/J1-0-report.md:84` names one killing test where m2 actually turns two red (`test_identifier_boundary`
**and** `test_live_tree_clean`); and "the only `exit 0`" is true of executable lines only — the string also appears in the
comments at `scripts/hooks/pre-commit:12` and `scripts/hooks/pre-commit:97`, both carrying `exit 0` in prose. The report's `DISCREPANCIES: None` at
`tasks/briefs/laya/J1-0-report.md:142` is the claim this verify contradicts.

### F19 — INFO (contract consequence, not a defect). `laya_probe` / `laya-probe` do not fire; `laya.probe` does

SOLID, 21 vocabulary shapes through the real script (§D). The maximal-run rule at `scripts/no_laya_in_gates.py:43` (`_TOKEN_RE`)
is exactly what frozen contract item 3 specifies and what the builder
documented. The consequence worth naming for J1-1+: a gate file may invoke `scripts/laya_probe.py` — a real file in this
tree today — by name and the screen will not fire, because the maximal run is `laya_probe`. Any hyphen- or
underscore-joined compound (`sieve-runner`, `jevcached`, `foo-laya`) is likewise invisible. That is the frozen rule; if
KC-J1 is meant to catch a gate that *calls* a Laya artefact, the contract needs a path-shaped token in a later increment.

### F20 — FOLLOW-UP. Matching is line-local, and three listed Python gate files get no import check

SOLID, all reproduced through the real script. Not caught: `agent_factory.decisions` split over a line continuation;
`from agent_factory import ledger, decisions`; the parenthesised multi-line `from agent_factory import (\n decisions,\n)`.
Separately, `scripts/no_laya_in_gates.py:225` (`is_py = entry.endswith(".py")`) gates the import check on the extension,
but `scripts/gate_files.txt:18-20` list `scripts/validate-ledger`, `scripts/proof-runner` and
`scripts/ledger-gen`, all `#!/usr/bin/env python3` with no `.py` — a fixture `scripts/validate-ledger` containing
`from agent_factory import decisions` exits 0, while the same line in a `.py` exits 3. The dotted-token matcher still
covers the other two import forms there. Frozen contract item 3 says "in a listed `.py` file", so the code is conformant.
Fix: detect Python by shebang as well as extension.

### F21 — INFO (static, not probed). `--staged` combined with `--root <other tree>` reads the wrong index

Read from source: `scripts/no_laya_in_gates.py:100-101` runs `["git", "show", ":%s" % path]` with no `cwd`, so it uses the calling process's
repository while the completeness walk uses `--root`. No production consumer mixes the two flags (the hook passes only
`--staged`) and no test does either, so this is a latent trap for a future caller, not a live defect.

## C. Mutant table — the builder's five re-run, plus this lane's twelve

Every mutation was applied to a lean scratch copy (the 33 gate files + the screen + the suite, which reproduces the
baseline `33 files scanned, clean` and `9 passed`) and reverted from a held pristine copy; the shared tree never changed.

| Mutant | Mutation | Suite result | Killed by |
|---|---|---|---|
| m1 (builder) | `_glob_structural` returns `set()` | `1 failed, 8 passed` | `test_unlisted_structural_match` — confirmed |
| m2 (builder) | substring match instead of the maximal run | `2 failed, 7 passed` | `test_identifier_boundary` **and** `test_live_tree_clean` (the report names one) |
| m3 (builder) | the pre-commit block deleted (`111,118d`) | `1 failed, 8 passed` | `test_precommit_wired` — confirmed |
| m4 (builder) | `SKIP_LAYA_GATE_CHECK` / `SKIP_ALL` honoured | `1 failed, 8 passed` | `test_no_bypass` — confirmed |
| m5 (builder) | `--staged` reads the worktree | `1 failed, 8 passed` | `test_staged_mode` — confirmed |
| v1 | the missing-file control deleted (the `if not args.staged:` arm, `scripts/no_laya_in_gates.py:210`) | **`9 passed` — SURVIVES** | nothing (this is B1's blind spot) |
| v2 | `DOTTED_TOKENS` never scanned | **`9 passed` — SURVIVES** | nothing |
| v3 | the structural import check disabled | **`9 passed` — SURVIVES** | nothing |
| v4 | `SIMPLE_TOKENS` reduced to `{"laya"}` | **`9 passed` — SURVIVES** | nothing (10 of 11 tokens ungated) |
| v5 | the self-listing refusal removed | **`9 passed` — SURVIVES** | nothing |
| v6 | both usage exits return 0 instead of 64 | **`9 passed` — SURVIVES** | nothing |
| v7 | violations return 0 instead of 3 | `5 failed, 4 passed` | 5 tests |
| v8 | unlisted returns 0 instead of 4 | `1 failed, 8 passed` | `test_unlisted_structural_match` |
| v9 | the scan loop iterates an empty list | `5 failed, 4 passed` | 5 tests |
| v10 | the hook keeps the call but ignores `RC` | **`9 passed` — SURVIVES**, and a real violating commit lands | nothing (F10) |
| fix-1 | B1's corrected form (presence checked per mode) | `9 passed` | — flips case F to rc 4 / `COMMIT BLOCKED … (rc=4)` |
| fix-2 | B2's corrected form (allowlist from the index) | `9 passed` | — flips case H to rc 3 |

v11 (a mutant that removes the invocation but keeps the comment) was not run — a `sed` quoting error — and is fully
superseded by v10, which is the stronger form of the same class.

## D. Item 2 — hostile vocabulary matrix (each case a fixture tree through the real script)

FIRES (rc 3, token named): `LAYA` and `Laya` in a workflow value · `jev` inside a shell here-doc · bare `sieve` ·
`laya.probe` (as `laya`) · a token inside a comment · `systemone`, `system_one`, `system-one` · `sieve-run` · `jevcache` ·
`decide-harvest` and `decide_harvest` on one line (both reported) · `laya-decide` · `decisions.jsonl`, `decisions.ledger`,
`decisions.canonical` · `from agent_factory.decisions import ledger` · `import agent_factory.decisions` ·
`from agent_factory import decisions` · `importlib.import_module("agent_factory.decisions")` — the brief asked whether the
string form is covered: it is, as the dotted token, at `scripts/no_laya_in_gates.py:70`.

DOES NOT FIRE (rc 0): `sieves` and `receives` · `laya_probe` · `laya-probe` · `sieve-runner` · `jevcached` ·
`my_agent_factory.decisions` · `agent_factory.decisions_v2` · a Cyrillic-homoglyph `lаya` · the line-continuation and
multi-name import forms · `from agent_factory import decisions` in an extensionless Python gate file. The first six are
the frozen maximal-run rule working as specified (F19); the homoglyph is out of contract, as the verify brief states; the
last three are F20.

Fixture realism (item 8): `tests/fixtures/decisions/gate_violation/scripts/hooks/pre-commit:3` is
`echo "this line mentions laya for testing"` — a real gate path with the planted token on exactly the line
`tests/test_no_laya_in_gates.py:63` asserts (`scripts/hooks/pre-commit:3:laya`). No off-by-one.

Mirror check (item 8): replacing the screen with a bare `exit 0` fails 8 of the 9 tests (only `test_precommit_wired`, a
file-content test, survives) — the suite is not a mirror of the implementation. Its weakness is coverage, not tautology:
no assertion in it is true by construction, and the one non-behavioural test is F10.

## E. Item 4/5/7 — completeness, staged corners and fail-open probes (rc pasted, real script)

| Probe | rc | Output |
|---|---|---|
| new `proofs/S0-13/check_x.py` unlisted | 4 | `gate-file-unlisted: proofs/S0-13/check_x.py` |
| listed path is a directory | 0 | `0 files scanned, clean` — F4 |
| symlinked gate file, token in the target | 3 | followed and scanned |
| dangling symlink in the list | 4 | `gate-file-missing:` |
| trailing space on a list line | 3 | stripped, scanned |
| duplicate list lines | 3 | the hit reported twice |
| literal glob `proofs/*/check_*.py` in the list | 4 | `gate-file-unlisted: …` + `gate-file-missing: proofs/*/check_*.py` — refused, as the contract demands |
| empty list, structural files present | 4 | `gate-file-unlisted: scripts/hooks/pre-commit` |
| empty / comments-only list, no structural files | 0 | `0 files scanned, clean` — F13 |
| missing `scripts/gate_files.txt` | 64 | `gate-file-missing: <abs path>` — F12 |
| binary file in the list | 3 | `scripts/blob.bin:1:laya` |
| `--list` outside `--root` | 3 | honoured; with an empty list the walk still fires (rc 4) |
| self-listed exactly | 64 | `gate-file-self: scripts/no_laya_in_gates.py` |
| self-listed as `./…` | 3 | 22 self-hits — F14 |
| absolute / `../` entry | 3 | read outside the root — F11 |
| `.github/workflows/ci.yaml` | 0 | invisible — F7 |
| staged: violation in index only | 3 | index authoritative |
| staged: violation in worktree only | 0 | contract-correct |
| staged: new unlisted checker | 4 | blocks |
| staged: renamed listed file | 0 | **B1** |
| staged: deleted listed file | 0 | **B1** |
| staged: unstaged allowlist edit | 0 | **B2** |
| unreadable listed file (as `nobody`) | 0 | **F3**, control at mode 644 → 3 |

## F. The blocking predicate applied per finding

| # | 1 contract-mapped | 2 canonical repro | 3 material | 4 discriminator | 5 in boundary | Disposition |
|---|---|---|---|---|---|---|
| B1 | yes — item 2, and AF-AP-40 (OPEN) | yes — real `git commit` | yes — a violating gate file commits under "clean" | yes — rc 0 vs rc 4, 9/9 green | yes | **BLOCKER** |
| B2 | yes — item 6's no-dodge clause (see caveat) | yes — real `git commit` | yes — a violating gate file commits | yes — rc 0 vs rc 3, 9/9 green | yes | **BLOCKER** |
| F3 | partial | **no** (not the `--staged` consumer) | yes | yes | yes | FOLLOW-UP |
| F4 | partial | no (fixture only) | low | yes | yes | FOLLOW-UP |
| F6, F7, F20 | **no** — the code matches the frozen text | n/a | yes | yes | yes | FOLLOW-UP (contract gaps) |
| F9, F10 | no — the nine tests are the frozen list | yes (v10 lands a commit) | test strength only | yes | yes | FOLLOW-UP |
| F11, F15 | no | yes | hardening / operational | yes | yes | FOLLOW-UP |
| F16 | no — item 6 asked for pre-commit only | yes (`--no-verify`) | yes | yes | **no** | escalation for J1-1+ |
| F5, F8, F12, F13, F14, F17, F18, F19, F21 | no | mixed | none / cosmetic | mixed | yes | INFO |

**GATE RECOMMENDATION: NOT-READY.** Blocking: **B1** (`scripts/no_laya_in_gates.py:210`, `if not args.staged:`, plus `:230`) and **B2**
(`scripts/no_laya_in_gates.py:187`, `list_path = root`, and `:193`). Both are one file, one function, and belong in a single repair round; both
corrected forms were run here and keep the nine frozen tests green. The repair should also add the two regression tests
that would have caught them (a staged rename and an unstaged allowlist edit, each asserting the exit code), per the
pre-mint rule that a reviewer-reported mutation becomes a committed failing test before the artifact is re-accepted.
This recommendation rests on findings I reproduced myself end to end; nothing in it depends on an unreproduced claim.

## G. Deliberately not done

- No commit, push, bridge call or outward action; no file in the tree written but this report; `src/agent_factory/decisions/`,
  `scripts/laya_probe.py`, `upstream.lock.yaml` and `docs/HARNESS-PORTS.md` were never opened for edit (other lanes hold them).
- No recursive verification of pytest, `scripts/ap_screen.py`, `scripts/report_lint.py` or the other hooks' gates — none of
  them changed in this increment and no readiness claim depends on them.
- No sweep of the `content is None: continue` fail-open class across the other checkers: out of the J1-0 boundary. It is
  the natural bug-echo follow-up once B1 is fixed.
- The PC bridge was not used (verify lanes have no bridge carve-out beyond `pc_suite.sh`, and this suite runs in 0.5 s).

## H. Item 9 — lint and screen, pasted

```
$ python3 scripts/ap_screen.py scripts/no_laya_in_gates.py
--- AP_SCREEN over 1 path(s): 7 hits over 1 files ---
AF-AP-40: 7
    scripts/no_laya_in_gates.py:136: if hooks_dir.is_dir():
    ... (:138, :142, :144, :148, :150, :152 — the six siblings)
$ python3 scripts/ap_screen.py --tests tests/test_no_laya_in_gates.py scripts/no_laya_in_gates.py
--- TEST_SCREEN over 2 path(s): 0 hits over 2 files ---
$ python3 scripts/report_lint.py --min-refs 10 tasks/briefs/laya/J1-0-report.md
report_lint: 21 refs — OK 14, NEAR 0, MISS 0, UNCHECKABLE 7, UNRESOLVED 0 (worktree)
$ python3 scripts/report_lint.py --min-refs 12 tasks/briefs/laya/VERIFY-J1-0-report.md
report_lint: 57 refs — OK 43, NEAR 0, MISS 0, UNCHECKABLE 14, UNRESOLVED 0 (worktree)
```

The builder's lint summary reproduces exactly. Two lint rounds were used on this report, both to move a backticked token
onto its reference's own line; no reference number was changed to make the lint pass.
