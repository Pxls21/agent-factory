# I59-C: S0-04's capture tool never prints a profile value, and the leak rule's bounds are pinned (task #314, issue #59 batch; the sandbox re-run)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/i59/I59-C-report.md` (write it
incrementally from the start). PIN: origin 7a050b6 (the boundary files are byte-identical to 2a50a65's, where the PC lane
started). Plan: `tasks/issue59-batch-plan.md`. Source findings: `tasks/briefs/system1/VERIFY-S0-04-LEAK-R1-report.md`
(G2, G5, G6; its section 6 and the mutants D5, A7-A10).

The first run was a PC lane on the local route (`tasks/briefs/pc/pc-i59c.md`, the same contract). It died at 07:52Z in a
vLLM crash (AF-AP-231) after 100 messages, with no report. Its partial diff of the two boundary files, UNVERIFIED (it stopped
before its gate), is at `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/i59c/pc-lane-partial.diff` (8,703 bytes, sha256 prefix 1f6f47b47bc91fee; it applies to HEAD).
Read it if useful; judge it against the contract below, and never copy it blind.

AUTHORIZATION AND LIMITS: first-party work in the owner's repository (issue #59 batch). The work is secret-leak hardening of
the owner's own capture tool, defensive by nature: every test secret is a FAKE string built at run time; never read a real
secret, a real profile, `~/.hermes/`, or any `*.env`. No network. No outward-facing action.

## WHY

The independent check of S0-04's leak-rule repair (`VERIFY-S0-04-LEAK-R1-report.md`, gate MERGE-READY-WITH-FOLLOWUPS) left
three follow-ups. They change an attested file, so they ride the issue #59 batch: one re-mint and one owner re-sign for all
the batch's changes. You build and prove them; the coordinator lands them with the batch. You do NOT re-mint S0-04 and do NOT
write `proofs/S0-04/result.json`.

- **G2.** `do_config` in `proofs/S0-04/tools/pc/capture_leg.py` catches `yaml.YAMLError` only. An explicit scalar tag on a
  value (`api_key: !!int <v>`, `!!float`, and other tags whose constructor fails) makes PyYAML raise a plain `ValueError`
  or `KeyError`, `main`'s catch-all prints `type: message`, and the message holds the whole value.
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
   old `except yaml.YAMLError` handler, and a handler that catches only `ValueError` and `KeyError` beside it; for G5, the
   handler narrowed to `ScannerError`; for G6, a tail bound of 3, a bound of 5, and the `_ENV` exclusion removed.

## BOUNDARY

- MODIFY: `proofs/S0-04/tools/pc/capture_leg.py` (item 1 only), `tests/test_s0_04_compression.py`.
- CREATE: your report.
- READ everything else. NEVER write `proofs/S0-04/result.json`, `proofs/ledger.json`, or any other file under `proofs/`.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. The four contract items, each with its test names and its kill-table row.
3. The gate: `bash scripts/test_summary.sh tests/test_s0_04_compression.py` twice, both summaries pasted, with the set id
   (the floor below: 156 passed, set 2e5825a9019e). The only test file that names a changed file is that one (`grep -l`,
   below); if you add another, run it too.
4. pyflakes on every file you write; `python3 scripts/no_laya_in_gates.py`; `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'`
   prints 0 for every file you write.
5. The report: files and lines, the pasted counts, the kill table, deviations, NOT-done, DISCREPANCIES.

## STANDING RULES

- No git writes, no PC bridge, no outward-facing action.
- Never read a real secret source: `.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`,
  `/root/.config/session-export/pseudonym.key`, and the GH_TOKEN and GITHUB_TOKEN variables.
- Other lanes hold this tree: SCRUB2-R1 (`scripts/transcript_export.py`, `tests/test_transcript_export.py`, possibly
  `scripts/known_values_check.py`, `scripts/session_export.py` and their tests, its report) and I59-B
  (`proofs/S0-05/tools/pc/run_s0_05_units.sh`, `tests/test_s0_05_egress.py`, its report). Never touch their files.
- The disk is shared (about 1.8G free): scratch under 100 MB in `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/i59c/`, deleted as you go (keep the partial diff);
  a short `--basetemp`; never run the whole `tests/test_vendored_manifest.py`.
- Test counts are pasted from `scripts/test_summary.sh`. Stamps are substituted from `date -u`, never typed.
- Run long commands in one foreground call, each under 10 minutes. Kill by pid only.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short text of
  its own (under 200 characters; a note only for a 0).

## PREMISE — MEASURED at authoring (2026-09-26 08:1xZ, the sandbox tree; HEAD's boundary files = origin 7a050b6's)

```
$ git log --oneline 2a50a65..HEAD -- proofs/S0-04/tools/pc/capture_leg.py tests/test_s0_04_compression.py proofs/S0-04/check_compression.py | wc -l
0
$ grep -n -E '^def do_config|except yaml.YAMLError|except Exception as exc|^def main' proofs/S0-04/tools/pc/capture_leg.py
232:def do_config(args) -> int:
241:    except yaml.YAMLError as exc:
271:def main(argv=None) -> int:
319:    except Exception as exc:                                   # noqa: BLE001 - fail closed
$ grep -n 'passw' proofs/S0-04/check_compression.py proofs/S0-04/tools/pc/capture_leg.py | cut -c1-110   (the K2 rule lines)
proofs/S0-04/check_compression.py:92:        r"(?i)(?<![A-Za-z0-9])(?:api[_-]?key|apikey|secret|password|passw
proofs/S0-04/tools/pc/capture_leg.py:49:    r"|(?<![A-Za-z0-9])(?:api[_-]?key|apikey|secret|password|passwd|to
$ grep -l -E 'capture_leg|test_s0_04_compression' tests/*.py
tests/test_s0_04_compression.py
$ bash scripts/test_summary.sh tests/test_s0_04_compression.py
pytest-exit: 0
pytest-summary: 156 passed in 7.27s
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_04_compression.py
1 files set=2e5825a9019e
$ sha256sum /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/i59c/pc-lane-partial.diff | cut -c1-16; git apply --check <it> && echo applies
1f6f47b47bc91fee
applies to HEAD
```

What `yaml.safe_load` raises on crafted profiles (PyYAML 6.0.1 without libyaml, the sandbox; measured at authoring with a
fake value `sk-FAKE0123456789`). Two facts matter for the tests: a deep nesting raises `RecursionError`, a class outside
`YAMLError`, `ValueError` and `KeyError` (so it discriminates a handler that catches only those); and `!!float` and `!!bool`
leak the value LOWER-CASED (PyYAML's constructors lowercase it first), so a leak check that compares case-sensitively misses
them.

```
deep nesting -> RecursionError | bases: ['RuntimeError', 'Exception'] | msg holds FAKE: False
!!int tag -> ValueError | bases: ['Exception', 'BaseException'] | msg holds FAKE: True
!!float tag -> ValueError | bases: ['Exception', 'BaseException'] | msg holds FAKE: False
!!bool tag -> KeyError | bases: ['LookupError', 'Exception'] | msg holds FAKE: False
!!timestamp bad -> ValueError | bases: ['Exception', 'BaseException'] | msg holds FAKE: False
huge int -> ValueError | bases: ['Exception', 'BaseException'] | msg holds FAKE: False
pyyaml 6.0.1 cext False
!!float ValueError | case-sensitive: False | lowercased: True
!!bool KeyError | case-sensitive: False | lowercased: True
```
