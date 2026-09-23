# VERIFY-J1-2-R1 — the targeted adversarial verify of the J1-2-R1 ledger repair (`src/agent_factory/decisions/ledger.py`)

**Role:** `adversarial-verifier`, IN THE SANDBOX, as root (the 4 KiB tmpfs short-write reproduction needs `mount`). Honey
`full`: line-bounded findings, evidence anchors, SOLID/UNSURE on every claim. Your report is DATA for the coordinator's gate;
you return a GATE RECOMMENDATION, never a verdict. Do NOT spawn subagents.

**PIN:** `8a7c7f0` (origin head; the decisions boundary is byte-identical to the J1-2-R1 landing `d4f4698`, measured below).
Work on the tree READ-ONLY. Every mutant, fixture and hostile ledger lives in a scratch copy under
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vj12r1/` (a `git archive 8a7c7f0` of `src/`, `tests/`
and `scripts/`; run it with `PYTHONPATH=<scratch>/src`). The ONLY file you write in the tree is your report. ANOTHER LANE (E3,
the S0-05 launch recipe) is LIVE in the same working tree: never `git stash`, `git checkout`, `git restore`, `git add` or `git
reset` in `/home/user/agent-factory`, and never touch `proofs/S0-05/`, `scripts/netns_lib.sh`-class S0-05 files or
`tests/test_s0_05_egress.py`. Unmount every tmpfs you mount and remove every scratch tree before you finish (the sandbox has about
2 GB free). No model, no network: this module must never call Laya (KC-J1). Test secrets are FAKE invented strings only.

## What landed (L = `src/agent_factory/decisions/ledger.py`, T = `tests/test_decisions_ledger.py`, C = `src/agent_factory/decisions/canonical.py`, V = `src/agent_factory/decisions/volatile.py`)

**Frozen contract:** `tasks/briefs/laya/J1-2-R1-brief.md` — R1-R8, its 25-row hostile table, and its mutant list; plus
`tasks/briefs/laya/J1-2-brief.md` items 1-7 with AMENDMENT J1-A1, and the declared limits in L's docstring (L:13-25). The
builder's report `tasks/briefs/laya/J1-2-R1-report.md` (with its COORDINATOR TOUCH section) is an INPUT to attack, never
evidence. The seam map: `_validate_path` L:106, `_validate_row` L:128, `_resolve_ledger_path` L:285, `_check_line` L:308,
`make_row` L:336, `append` L:433 (open flags L:471-472, `S_ISREG` L:477, `size_before` L:483, `os.write` L:485, the truncate
L:490-491, the final `os.fsync` L:501), `replay` L:508 (open L:523, `S_ISREG` L:538, `data.split(b"\n")` L:554).

**Coordinator touches at landing (attack these too):** (1) both DirEntry tests (T:914, T:983) now `monkeypatch.chdir(tmp_path)`
after the lane's N5 mutant run left a 723-byte `<DirEntry 'ledger.jsonl'>` in the repo root; (2) L:73's two literal separators
became the escapes ` `/` ` (the set claimed unchanged); (3) the report's citations were re-anchored after the lint
fix AF-AP-132.

## PREMISE — MEASURED at authoring (2026-09-23 05:2xZ, sandbox, /home/user/agent-factory@8a7c7f0)

```
$ git diff --stat d4f4698 8a7c7f0 -- src/agent_factory/decisions tests/test_decisions_ledger.py tests/test_decisions_canonical.py tests/fixtures/decisions tasks/briefs/laya/J1-2-R1-report.md
(empty = byte-identical)
$ identities (sha256[:16] lines path) at 8a7c7f0
c5c15240fdc4d9eb 617 src/agent_factory/decisions/ledger.py
bc9cb1d03fdb77a4 77 src/agent_factory/decisions/canonical.py
b48899c883c7231f 295 src/agent_factory/decisions/volatile.py
2aec3875f71213e4 21 src/agent_factory/decisions/__init__.py
fed3ea5c7f1b8005 1468 tests/test_decisions_ledger.py
48fdf09e8038a146 340 tests/test_decisions_canonical.py
9dcec5fe8e1ca75d 186 tasks/briefs/laya/J1-2-R1-report.md
$ bash scripts/pc_suite.sh set-id -- tests/test_decisions_ledger.py tests/test_decisions_canonical.py
2 files set=16a7b628685e
$ /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_ledger.py tests/test_decisions_canonical.py -q -p no:cacheprovider --basetemp=/tmp/j12f/bt   (root, twice, on these bytes)
53 passed in 0.23s
53 passed in 0.24s
$ setpriv --reuid=65534 --regid=65534 --clear-groups env PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python3 -m pytest tests/test_decisions_ledger.py tests/test_decisions_canonical.py -q -p no:cacheprovider --basetemp=/tmp/j12fnr/bt
52 passed, 1 skipped in 0.25s
$ python3 scripts/report_lint.py --min-refs 12 --map L=src/agent_factory/decisions/ledger.py --map T=tests/test_decisions_ledger.py tasks/briefs/laya/J1-2-R1-report.md --root .
report_lint: 57 refs — OK 47, NEAR 8, MISS 0, UNCHECKABLE 2, UNRESOLVED 0 (worktree)
$ python3 scripts/ap_screen.py --tests tests/test_decisions_ledger.py
--- TEST_SCREEN over 1 path(s): 1 hits over 1 files ---
AP-70: 1
    tests/test_decisions_ledger.py:1292: except Exception:
$ the pre-commit screen at landing (advisory) named AF-AP-58 on T's signal handler install (T:837 installs SIG_DFL for SIGALRM, T:850 restores it)
$ grep -n 'split\|splitlines' src/agent_factory/decisions/ledger.py
236:    if ".." in path.split("/"):
554:    parts = data.split(b"\n")
$ the coordinator's own mutant re-runs on a scratch copy at landing (the lane's rows, not new ones)
N1 (written-count check -> if False): 2 failed: test_short_write_spy, test_short_write_real_tmpfs
N6 (closed-shape check -> if False): 1 failed: test_extra_top_level_key_refused
N5 (os.fspath -> str), cwd = a scratch dir, BEFORE the chdir touch: 2 failed (both DirEntry tests); a 723-byte "<DirEntry 'ledger.jsonl'>" appeared in the scratch cwd
N5, AFTER the chdir touch: 2 failed; the scratch cwd empty; the file in tmp_path (test_direntry_duplicate_refuse0/<DirEntry 'ledger.jsonl'> 723)
$ _PATH_BAD_CHARS before/after touch (2): 36 members, sha256(repr(sorted(set)))[:16] = 9323478b39b9d6e1 both
```

## ITEMS (discovery exhaustive; disposition disciplined)

1. **Re-measure the premise** at `8a7c7f0` with the commands above. Any mismatch: stop, return `CONTRACT-INVALID` with the diff.
2. **R1, the short write, through the real `append`.** Reproduce on a real 4 KiB tmpfs (root) and through a spy on `os.write`:
   after a refusal the file's bytes equal the pre-write bytes, the reason is `decision-ledger-short-write:
   <path>:<written>/<expected>`, `replay` succeeds, and the next `append` succeeds. New shapes: a short write into an EMPTY
   ledger; `os.ftruncate` raising (the `truncate-failed` branch at L:490-495) — what does the file hold after, and what does
   `replay` say?; a second writer appending between the `fstat` (L:476) and the `write` (L:485) — the docstring declares one
   writer at a time: confirm the limit is declared and describe what the truncate does to the other writer's bytes. The
   declared limit decides the disposition; a hazard the docstring does not declare is a finding.
3. **R2, no bare exception from content.** Replay each hostile line as line 2 of a ledger whose line 1 is valid: a UTF-8 BOM
   prefix, CRLF line ends, trailing spaces, `NaN`/`Infinity` tokens, an integer of 5000 digits, 100000-deep arrays, a NUL byte,
   invalid UTF-8 (`\xff`), a lone `\r`, a JSON string holding U+2028. Each must be `decision-ledger-unparseable: <path>:2` (or a
   named row refusal where the line parses and is canonical). Any other exception type is a finding.
4. **R3 and the builder's N11 EQUIVALENT claim.** The claim: append's pre-write `_check_line` can never refuse a row that
   `_validate_row` accepted. Question for you (not measured at authoring): can you find a row `_validate_row` accepts whose
   `canonical(row)` line `_check_line` refuses? Try non-NFC strings (C NFC-normalizes), key order, floats (`-0.0`, `1e-7`,
   `1e16`, `1.0`), large ints, U+2028/U+2029 in a value. A row found = a discriminator: report it. None found = state what you
   tried; the claim stands as INFERRED.
5. **R4, one spelling per path**, beyond the lane's 11 refused spellings: `a//b`, `a/./b`, `a/b/`, `./a`, `a\\b`, a
   full-width solidus, the same name in NFC and in NFD (`é` composed vs decomposed — is that "one spelling per path"?), a
   zero-width joiner, U+2028 inside the path (touch 2), 4096-character and 300-component paths. Record accept/refuse per row;
   a refusal must read `decision-row-invalid: source_ref.path=<value[:80]>` from `make_row` AND from `append`.
6. **R5, the path argument.** A PathLike whose `__fspath__` returns bytes; one whose `__fspath__` raises; a `str` subclass;
   `pathlib.PurePosixPath`; an `os.DirEntry`. With the cwd set to a fresh scratch dir, confirm nothing is written outside the
   named ledger (touch 1).
7. **R6, the file type.** `append` and `replay` on a FIFO (must return at once with `decision-ledger-not-regular`, never
   hang), a symlink to a regular file, a symlink to `/dev/null`, a directory, a UNIX socket, `/dev/zero` (replay must refuse,
   never read forever), and a regular file swapped for a symlink between two appends.
8. **R7, `make_row`.** A non-str `question_id`, an unknown `question_id`, `raw_state` not a dict, `raw_state` with extra keys,
   `source_ref` with a wrong-shape `source_digest`: each a named refusal before any J1-1 call, never a bare exception.
9. **Mutation audit with NEW mutants** (never the lane's M11-M20 / N1-N11), one at a time on the scratch copy, each compiled and
   collected (AF-AP-78). Your own list; include at least: truncate to `size_before + 1`; the `os.fsync` after the truncate
   removed; `os.O_NONBLOCK` dropped from append's open (the FIFO test must not hang the run: use a timeout); `" "`
   removed from L:73; replay's `data.split(b"\n")` replaced by `data.decode("utf-8").splitlines()` encoded back (AF-AP-132 in
   production code); `_resolve_ledger_path` accepting bytes. Questions, not measured at authoring: does a test red on each?
   A survivor with a real discriminator is a finding; an equivalent mutant needs its reason.
10. **The AF-AP-58 screen hit** on T's FIFO watchdog (T:837-850): does the handler window matter here (can the alarm fire
    outside the `try` that restores it)? Judge and report.
11. **Gates, yourself:** root twice and uid 65534 once with the premise commands; pyflakes on L and T; `python3
    scripts/no_laya_in_gates.py`; `grep -c vj12r1 /proc/mounts` = 0 at the end.

## Deliverable

`tasks/briefs/laya/VERIFY-J1-2-R1-report.md` — the finding inventory (every observation numbered, each BLOCKER / FOLLOW-UP /
INFO / UNVERIFIED with evidence level, contract mapping, canonical-path status, material effect, reproduction command and a
suggested fix), the mutant table (compiles / collected / result / killed-by), the gate lines pasted verbatim, what you
reproduced vs reviewed statically, and ONE gate recommendation line (`MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` /
`NOT-READY` / `CONTRACT-INVALID`). Cite code as `L:<line>` / `T:<line>` / `C:<line>` / `V:<line>`, then run
`python3 scripts/report_lint.py --min-refs 12 --map L=src/agent_factory/decisions/ledger.py --map T=tests/test_decisions_ledger.py --map C=src/agent_factory/decisions/canonical.py --map V=src/agent_factory/decisions/volatile.py tasks/briefs/laya/VERIFY-J1-2-R1-report.md --root .`
— apply its `fix:` hints for at most three rounds, then paste the line and finish. Write the report incrementally (a partial
report survives a stop).

**Standing do-nots:** no subagents; no outward-facing actions (no PRs, comments, pushes, issues); never touch the PC bridge;
never kill a process you did not start; touch no file in the tree except your report.
