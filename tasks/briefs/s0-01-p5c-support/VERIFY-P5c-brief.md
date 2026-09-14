# VERIFY-P5c — adversarial grade of lane P5c-c (S0-01 PC capture tools round 3: every required artifact content-validated by a version-aware constraint, the header grammar strict, the idiom table pinned as data, the S0-02-only environment extension) plus the coordinator's landing amendment

You are an adversarial-verifier (the PC Hermes verify lane; the venue map `tasks/briefs/pc/VENUE-MAP.md` applies). Repo agent-factory,
branch claude/soundbox-kit-migration-iz1jwf. **PIN: `a91f256`** — the round-3 LANDING: the coordinator's harvest of lane P5c-c's PC
tree (PIN 3614dc9, built under AMENDMENT 1 + AMENDMENT 2), a straight copy plus ONE coordinator amendment at landing: the parser idiom
`_PY_DIRFD` (`T:105-109`) and its row `_IDIOMS["_PY_DIRFD"] = 3` (`T:128-130`), because checkpoint 9d's probe creates three of its four
leaves through `_leaf_handle(framedir_fd, framedir, "x", mode)` and the lane's coverage floor fired on HEAD (`the parse resolves 1
framedir names, below the pinned floor 4`). FILE IDENTITY at the PIN (lines, sha256[:8]): `proofs/S0-01/pins.py` (629, `41fa933d`) ·
`proofs/S0-01/tools/build_capture_record.py` (221, `c9709755`) · `proofs/S0-01/tools/pc/pc_launch.py` (429, `1082e419`) ·
`tests/conftest.py` (72, `0be8f3c5`) · `tests/test_s0_01_pc_tools.py` (1124, `e8bcee7d` — the lane's 1115 lines plus the amendment) ·
`tests/test_s0_01_pc_post_scan.py` (451, `9e939cf9`); the lane's report `tasks/briefs/s0-01-p5c-support/P5c-report.md`, the two
blocker reports `P5c-BLOCKERS.md`, the transcript `transcripts/pc/pc-p5c-c.md--3614dc9.md`. Grade the bytes of `git archive a91f256`
from a scratch copy under your lane's scratch dir; every mutant and every sweep on scratch COPIES; every pytest run with an explicit
SHORT absolute `--basetemp`, `/home/rocco/venv-agent-factory/bin` FIRST on PATH and the venue exports (`S0_01_VENUE=pc
S0_01_REAL_LEG_DIR=/home/rocco/s0-01-pinned/realleg/golden S0_02_BUZZ_SRC=/home/rocco/s0-01-pinned/buzz`); the real corpus under
`/home/rocco/s0-01-pinned/realleg/golden` is READ-ONLY (copy a leg, then mutate the copy); every FIFO/hang probe standalone under
`timeout`; kill only what you start, by pid; never background a run and stop; no outward actions; NEVER launch buzz-acp, the agent,
Hermes, the tee or the relay — the tools are graded through their unit surface, their subprocess argv validation and the corpus's
collected files; never read, print or commit a credential. Authorization: the owner's own capture tools under test on the owner's
system. Do NOT spawn subagents.

**Inputs (read in this order):** VERIFY-P5b's report `tasks/briefs/s0-01-p5b-support/VERIFY-P5b-report.md` (the round's contract: F1
and F4 blocking, F5 A5l's, F2 and F3 real) · the lane brief
`tasks/briefs/s0-01-p5c-pc-tools-every-required-artifact-validated-the-header-strict-the-s0-02-env-extension.md` (10 items) with
`P5c-AMENDMENT-1.md` and `P5c-AMENDMENT-2.md` (item 1 replaced twice; AMENDMENT 2's corpus MEASUREMENT table is the contract) ·
the lane's report (DEVIATIONS first: the `tests/conftest.py` boundary deviation, VERIFY-P5b's 40 mutants NOT individually re-run,
`test_proof_status.py` reds in its tree; its APPENDIX refs — lint at the landing with the six maps of item 10: `16 refs — OK 15, NEAR
0, MISS 1, UNCHECKABLE 0, UNRESOLVED 0 (at a91f256)`, the MISS being the coordinator's +8/+9 shift of the test file's refs at or after
`:173` — stamped atop the report) · `P5c-BLOCKERS.md` (the red-befores of items 1-3) · the pack
`tasks/briefs/s0-01-p5c-support/VERIFY-P5c-pack.md` · `docs/INCIDENT-LOG.md` (AF-AP-40, AF-AP-56, AF-AP-62, AF-AP-63, AF-AP-65,
AF-AP-72, AF-AP-73).

## Item 0 — the mechanical gates, pasted
The coordinator's gates: sandbox `RESULT: rev=3614dc994e5b files=13 deleted=0 runs=2 identical=yes rc=0 summary="123 passed in 46.62s
123 passed in 7.24s"` (the lane's bytes), then `124 passed` twice after the amendment (the coordinator's; the wrong-count mutant
`_PY_DIRFD = 2` red); the lane's `123 passed in 7.87s` / `123 passed in 8.09s` and its joint S0-01 set `2524 passed, 22 skipped, 9
xfailed, 4 failed in 317.94s` (its four = `test_proof_status.py` in ITS tree; at the landed tip the four are the S0-11 re-acceptance
class, AF-AP-56); the PC union run `4 failed, 1561 passed, 9 xfailed in 232.41s` (8 workers, 20260914T121247Z-c6c384a). Agree or
disagree by your own runs: the two test files (expect `124`, twice) and the joint S0-01 set (`tests/test_s0_01_*.py` — the checker
and backend tests consume `pins`; the floor `1556 passed, 9 xfailed`). Then `ap_screen.py --s0-01` (the coordinator's run at the
landing: 83 hits over 11 files — AP-32 ×22; AF-AP-40 ×19, among them `B:102,126,131` `if <path>.exists():`, DOMINATED by the
completeness gate on the build path (`B:74-80`) but that gate is build-only — classify each by run in BOTH modes; AF-AP-72 ×9 —
`P:567` ×3 inside a `try/except ValueError` → a named `ConstraintFailure`, `L:162`, … — classify) and `--tests` over the three test
files (0 hits); pyflakes; the FILE IDENTITY table against the PIN; the report lint reproduced with `--rev a91f256 --map
P=proofs/S0-01/pins.py --map B=proofs/S0-01/tools/build_capture_record.py --map L=proofs/S0-01/tools/pc/pc_launch.py --map
T=tests/test_s0_01_pc_tools.py --map S=tests/test_s0_01_pc_post_scan.py --map C=proofs/S0-01/check_acp_conformance.py`; the
external-command census by pid.

## Items
1. **F4 — the version-aware content constraint (`P:326-338` `_CONTENT_BY_EXT`, first match wins; `P:339-368` `_CONTENT_CONSTRAINTS` and
   the fill loop; `P:450` `content_constraint`; `P:464-574` `validate_artifact`; `B:70-96` the two paths: `corpus_version` first, the
   completeness gate build-only, then every required file — `--check` SKIPS absent ones, `B:90-91`).** Re-measure AMENDMENT 2's corpus
   table on the golden four (`stat -c %s`, `head -1`) and paste it; derive the 25 v2.2 / 26 v2.4 rows YOURSELF and diff against the
   table; re-run both sweeps from your own harness (v2.2 on a copy of `run-1`: 25 named refusals, the untouched copy rc 0, the
   `shutdown` copy rc 0 with its 0-byte after-scan; v2.4 on the synthetic leg: 26 named). Then attack each kind: `int-exit-code` —
   `"-1"`, `"+3"`, `" 7 "`, `"0\n0\n"`, `"１２"` (fullwidth digits: `int()` accepts Unicode decimals), `"1e3"`, `"300"` (is "one int" the
   whole contract for an exit code and a pid, or a range?); `json-object` — `{}`, a top-level `"s"`, `null`, duplicate keys, a
   100 000-deep nested array (`RecursionError` is not a `ValueError`: `B:94-96` catches only `ConstraintFailure` — reproduce the raw
   traceback and its rc); `jsonl-nonempty` — a blank line mid-file, a scalar line, CRLF, a trailing partial line; `gzip-text-nonempty`
   — a valid gzip header over a CORRUPT deflate body (`zlib.error` is neither `OSError` nor `EOFError`: `P:541-543` — reproduce the
   traceback), a member followed by trailing garbage, an empty decompressed body (named), a 1 GiB decompressed body (the read is
   unbounded — state the cost, never run it to completion on the shared host); `text-nonempty` — whitespace only; `launch.ready` with
   arbitrary text (the corpus writes a 28-byte UTC stamp — is the kind honest or too wide: decide); `empty-marker` — one byte, a
   symlink to an empty file, a directory named like the marker (which guard fires first, `require_regular_file` `P:19`?);
   `utf8-text-maybe-empty` — `\xff`, a UTF-8 BOM, a `#` line on line 2 of a v2.2 after-scan (AMENDMENT 2 says `corpus_version`
   refuses it — reproduce on the build path AND on `--check`); `scan-headed` — CRLF (`splitlines()` at `P:552` accepts `\r\n` while
   `corpus_version` refuses CRLF, `S:432` — which answer wins in each mode), a header with trailing spaces, a two-field body row, a pid
   `"٣"`. Then the `--check` asymmetry: a leg missing 24 of 25 required files whose one present file is valid and whose `capture.json`
   matches → `--check` rc 0 — the lane's F1/F16 reasoning (`B:56-68`): a design or a hollow? Optional entries (`entry_allowlist()`
   `P:385`) are validated NOWHERE — list every optional name the checker READS; each is a finding with its row.
2. **F2 — `corpus_version` strict (`P:395-449`; `_SCAN_HEADER_VERSION_RE` `P:282`; `_SCAN_HEADER_FULL_RE` `P:289-…` mirroring the
   checker's `check_acp_conformance.py:158-161` by COPY — which test binds the two grammars, and what reds when the checker's changes?).**
   Attacks: a BOM before `#`; `# process-scan v2.4 ` with one trailing space; `v2.10` (`_version_key` `P:367`); `V2.4`; a header on
   line 1 and a `#` comment on line 3; the smear (a headerless leg carrying `tee-status.json`) — the exact message `S:444`; a v2.3
   header on a leg that also carries a v2.4-only name; the two scan files with DIFFERENT headers (after v2.4, teardown v2.3 — which
   wins, or refused); an empty after-scan beside a headed teardown; the golden four parse `v2.2` — reproduce on the PC corpus.
3. **F3 — the idiom table as DATA (`T:100-110` the seven regexes; `T:118-136` `_IDIOMS`; `T:142` `_framedir_names`; `T:386` the exact-count
   test; `T:451` the recognition rows; `T:85` `_PRODUCERS`).** Re-measure EVERY count over the tree's producers at the PIN with your
   own scratch probe — `_PY_JOIN 22 · _PY_PATH 0 · _PY_DIV 9 · _PY_FSTR 4 · _SH_FD 22 · _SH_OUT_ASSIGN 6 · _PY_DIRFD 3` — any
   disagreement is a finding (the coordinator's 3 = `env.json`, `runtime-identity.json`, `timeline.jsonl`; `agent-stderr.txt` reaches
   the parse through `_PY_JOIN`). Attack `_PY_DIRFD`: `_leaf_handle(framedir_fd, framedir, NAME, …)` with a variable, other parameter
   names, a keyword call — each invisible to the parse: does the per-producer floor or the exact table catch the blindness, and how
   soon? A 13th idiom planted in a producer copy (VERIFY-P5b's item-1 list) — which test reds; VERIFY-P5b's M10 (a row deleted) red
   twice?
4. **The S0-02-only environment extension (`P:76-77`; `L:242-280` `launch_env`, the unknown set refused by name `L:250-251`, the
   selected set's closed check `L:266-275`; `L:289` `--env-set` with argparse `choices`; `L:196-203` `env_json_with_set_marker`;
   `L:382` the live use).** Attacks: `--env-set S0-02` (case) and `s0-02 ` as a subprocess (argparse refuses — paste); `launch_env(…,
   env_set="s0-02 ")` direct; a live variable literally named `env_set` colliding with the marker; a leaked `RUST_LOG` under `s0-01`
   (refused as outside the closed set — the message); `RUST_LOG=info` under `s0-02` (is the pinned VALUE enforced, or only the key?);
   the default byte-identical (`T:1039-1063`); the S0-01 checker's `check_env` (`C:445-451`) still exact on an `s0-01` `env.json`.
   Then the CHAIN the extension serves: the S0-02 runner will pass `--env-set s0-02` on its three buzz-acp-decided legs →
   `RUST_LOG=debug` → `buzzacp.log` DEBUG lines → S0-02's level-aware canary; the S0-02 bundle carries NO `env.json` (its per-leg
   table `proofs/S0-02/check_buzz_authz.py:143-152` at c6c384a) — state what the S0-02 proof can and cannot see of the set that
   launched a leg, and whether that is a gap.
5. **The conftest deviation (`tests/conftest.py:23-72` `synthetic_leg`, now contract-valid).** Its consumers are
   `tests/test_s0_01_pc_tools.py` AND `tests/test_s0_01_scripted_backend.py`: run the backend file on the PIN; diff the fixture's bytes
   `3614dc9^..a91f256`; was the change the MINIMAL one (only the values the new constraints refuse), and does any backend test now
   pass for a different reason than before?
6. **Item 5 of the brief and the coordinator's stamp.** The P5b report's STATUS line present (`head -1` at the PIN)? The coordinator's
   landing stamp atop the P5c report — the shifted refs it names (`:173→:181`, `:378→:386`, `:1030→:1039`, `:1055→:1064`,
   `:1069→:1078`) — resolve each against the PIN.
7. **Mutants ≥ 50, every one on a scratch copy, the killer line pasted, by-construction survivors named.** VERIFY-P5b's 40 individually
   re-run (the lane did NOT — its DEVIATION), the lane's six (M-R1…M-R6 from your reconstruction), the coordinator's wrong-count mutant
   (`_PY_DIRFD = 2`), and yours from items 1-4 (each constraint row removed → its named test red; the `zlib.error` and
   `RecursionError` escapes; the `--check` skip; the CRLF disagreement; the pinned RUST_LOG value).
8. **The 18-class re-scan** on the six files by RUN; every `if <field> == <literal>:` without a raising other arm (AF-AP-65); the three
   `exists()` in `B` by mode (AF-AP-40); `os.environ` never read below `main()` (`L:32`).
9. **What CAN run on the PC without launching anything:** `build_capture_record.py` build + `--check` over EVERY golden leg;
   `pc_launch.py --help` and its argv validation as a subprocess; the sweeps. State what stays NEVER executed end to end (the live
   capture; VB-F12/F13/F14 are the coordinator's).
10. **Discipline** — `file:line` by `sed -n` on the PIN; `report_lint.py` on your own report with the six maps of item 0 pasted (MISS 0,
    UNRESOLVED 0); the process census by pid.
11. **The design.** Is the record builder now a CONTENT gate, or a presence gate with content rows (the `--check` asymmetry, the
    unvalidated optional entries, the unbounded reads)? F5 (A5l's): what exactly A5l must consume from `pins` so the checker and the
    producer agree (`is_pinned_argv`, `required_files`, `entry_allowlist`, `corpus_version`, and now `content_constraint`?). What round
    4 (P5d) must do, if anything, before the re-capture — or state that nothing but A5l and the coordinator's capture remains.

## Report
Write it to `tasks/briefs/s0-01-p5c-support/VERIFY-P5c-report.md` inside your tree, draft after EACH item, and return it whole as your
final message. Findings: ALL, no severity filtering, each with `file:line` on the PIN, expected vs observed, the failing input, the
minimal fix, the exact red test, SOLID/UNSURE; reproduced vs reviewed vs skipped; verdict MERGE-READY or NOT-READY with the blocking set
and the cheapest path; the items that are the coordinator's, A5l's or the owner's named as such.
