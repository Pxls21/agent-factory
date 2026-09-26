# PC lane I59-C (task #314, issue #59 batch): S0-04's capture tool never prints a profile value, and the leak rule's bounds are pinned

PIN: 2a50a65 (the origin head at authoring). Role: code-implementer. Route: the LOCAL build route
(`agentfactory-build-local`, medium; D-061/D-062: local only). Claim nothing about which model you are; the harvest
measures the provider mix. Venue: `tasks/briefs/pc/VENUE-MAP.md`, read it FIRST. Honey ultra, Lever-2: the report is DATA
(files:lines, verbatim counts, discrepancies, NOT-done). Keep your context small: `| tail -n 40` on long output, `sed -n`
ranges instead of whole-file reads. Do NOT spawn subagents. Code questions go to graft first (CODE INTEL FIRST).

AUTHORIZATION AND LIMITS: first-party work in the owner's repository on the owner's PC (issue #59 batch, planned in
`tasks/issue59-batch-plan.md`). The work is secret-leak hardening of the owner's own capture tool, defensive by nature:
every test secret is a FAKE string built at run time; never read a real secret, a real profile, `~/.hermes/`, or any
`*.env`. No network. No server touch. No outward-facing action (no push, no PR, no comment). Write only inside your lane
tree and your lane's `../scratch/` directory.

## WHY (read first)

The independent check of S0-04's leak-rule repair (`tasks/briefs/system1/VERIFY-S0-04-LEAK-R1-report.md`, gate
MERGE-READY-WITH-FOLLOWUPS) left three follow-ups. They change an attested file, so they ride the issue #59 batch: one
re-mint and one owner re-sign for all the batch's changes. You build and prove them; the coordinator lands them with the
batch. You do NOT re-mint S0-04 and do NOT write `proofs/S0-04/result.json`.

- **G2.** `do_config` in `proofs/S0-04/tools/pc/capture_leg.py` catches `yaml.YAMLError` only. An explicit scalar tag on a
  value (`api_key: !!int <v>`, `!!float`, and other tags whose constructor fails) makes PyYAML raise a plain `ValueError`
  or `KeyError`, and `main`'s catch-all prints `type: message`, and the message holds the whole value.
- **G5.** The six F1b tests are all ScannerErrors. With the handler narrowed to `ScannerError` (the verifier's mutant D5),
  a ParserError or a ComposerError prints the whole fake value, and all 156 tests still pass.
- **G6.** The K2 rule's tail bound of 4 name segments is pinned only as "at least 2" (the verifier's mutants A7-A9
  survive), and the upper-case `_ENV` exclusion is unpinned (A10).

## CONTRACT

1. **G2.** Every exception from parsing the profile in `do_config` is reported with its class and its position (line and
   column when PyYAML gives one) and never with its message, its snippet or its problem text: no part of any value can
   reach stderr through this path. The exit code stays what it is today for a parse failure. Nothing else in the tool
   changes.
2. **G5.** Tests that feed `do_config` a profile raising a ParserError and one raising a ComposerError, each holding a fake
   key, and assert that the key's value never appears in the output (and that the position does).
3. **G6.** Tests that pin the K2 rule's bounds in BOTH files that carry it (`proofs/S0-04/check_compression.py` and
   `proofs/S0-04/tools/pc/capture_leg.py`): a name with 4 segments after its listed word is caught, one with 5 passes, and
   `API_KEY_ENV=` with a long value is an ordinary control that passes. Tests only; the rules do not change.
4. **The kill table.** For each item, a named mutant fails a test as a FAILED test, never an error (AF-AP-223): for G2, the
   old `except yaml.YAMLError` handler; for G5, the handler narrowed to `ScannerError`; for G6, a tail bound of 3, a bound
   of 5, and the `_ENV` exclusion removed.

## BOUNDARY

- MODIFY: `proofs/S0-04/tools/pc/capture_leg.py` (item 1 only), `tests/test_s0_04_compression.py`.
- CREATE: your report, `tasks/briefs/i59/I59-C-report.md` (write it incrementally from the start).
- READ everything else. NEVER write `proofs/S0-04/result.json`, `proofs/ledger.json`, or any other file under `proofs/`.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report on any mismatch.
2. The four contract items, each with its test names and its kill-table row.
3. The gate: `python -m pytest -n 8 -q -p no:cacheprovider --basetemp ../scratch/bt tests/test_s0_04_compression.py`
   twice, both summaries pasted, with the set id (the floor below: 156 passed, set 2e5825a9019e). Then once over every test
   file that names a changed file: `grep -l -E 'capture_leg|test_s0_04_compression' tests/*.py`.
4. pyflakes on every file you write; `python3 scripts/no_laya_in_gates.py`; `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` prints
   0 for every file you write.
5. The report: files and lines, the pasted counts, the kill table, deviations, NOT-done.

## PREMISE — MEASURED at authoring (2026-09-26 05:5xZ; the sandbox tree at the PIN, where the lane files are identical to origin 2a50a65)

```
$ git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf | cut -c1-70
8d39d6a transcripts: scrubbed sandbox chat digests (2026-09-26)   (measured before the push to 2a50a65, which changed no file in the boundary)
$ sed -n '232,246p;315,322p' proofs/S0-04/tools/pc/capture_leg.py
def do_config(args) -> int:
    try:
        import yaml
    except ImportError as exc:
        raise CaptureError(
            "PyYAML is required for --config on this host; install it or export the Hermes "
            "profile to JSON — the provider block is not parsed by hand") from exc
    try:
        profile = yaml.safe_load(read_regular(Path(args.profile), "profile"))
    except yaml.YAMLError as exc:
        # PyYAML's message quotes the offending line in a window that can start inside a value, so an
        # inline key can print with its `sk-` cut off, past every shape rule (VERIFY-S0-04-LEAK F1b).
        # Report the position only, never the snippet or the problem text.
        mark = getattr(exc, "problem_mark", None) or getattr(exc, "context_mark", None)
        where = f"line {mark.line + 1}, column {mark.column + 1}" if mark is not None else "an unknown position"
        return do_capture(args, argv)
    except CaptureError as error:
        print(f"capture_leg: {safe(str(error))}", file=sys.stderr)
        return 1
    except Exception as exc:                                   # noqa: BLE001 - fail closed
        print(f"capture_leg: {safe(f'{type(exc).__name__}: {exc}')}", file=sys.stderr)
        return 1

$ grep -n 'passwd|secret|password' (the K2 rule lines) proofs/S0-04/check_compression.py proofs/S0-04/tools/pc/capture_leg.py
proofs/S0-04/check_compression.py:92:        r"(?i)(?<![A-Za-z0-9])(?:api[_-]?key|apikey|secret|password|passw
$ grep -n -E '^\| G(2|5|6) ' tasks/briefs/system1/VERIFY-S0-04-LEAK-R1-report.md | cut -c1-400
299:| G2 | FOLLOW-UP | `do_config` catches `yaml.YAMLError` only. An explicit scalar tag on the value makes PyYAML's constructor raise a plain `ValueError` or `KeyError`, and `main`'s catch-all prints the whole value: `!!int` -> `ValueError: invalid literal for int() with base 10: '<v>'`, `!!float` -> `could not convert string to float: '<v>'`, `!!bool` -> `KeyError: '<v>'` (32 of 32 characters, R
302:| G5 | FOLLOW-UP (test gap) | The six F1b tests are all ScannerErrors. With the handler narrowed to `ScannerError` (mutant D5), a ParserError or a ComposerError prints the whole fake value and all 156 tests pass | VERIFIED (section 6) | none | yes | none today (R1 catches every class, section 3) | `mutate_r1.py D5` + the mutated-copy probe | add a parser, a composer and a constructor case to `
303:| G6 | INFO (test gap) | The chosen tail bound 4 is pinned only as "at least 2" (A7-A9 survive), and the upper-case `_ENV` exclusion is unpinned (A10) | VERIFIED (section 6) | none | n/a | none | `mutate_r1.py` | a 4-segment catch, a 5-segment pass and `API_KEY_ENV=` as an ordinary control (tests only) |
347:| G2 type-tag constructor errors print a value | no (outside F1b's YAMLError scope; no assignment shape) | yes | no (hypothetical: a tagged non-`sk-` inline key in an operator-set profile) | yes | yes | no |
$ bash scripts/test_summary.sh tests/test_s0_04_compression.py
pytest-exit: 0
pytest-summary: 156 passed in 7.33s
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_04_compression.py
1 files set=2e5825a9019e
```
