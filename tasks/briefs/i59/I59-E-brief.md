# I59-E: S0-03's bundle reader never lets a parse error print a value (task #327, issue #59 batch; AF-AP-232's echo)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/i59/I59-E-report.md` (write it
incrementally). If the harness refuses a report-file write ("Subagents should return findings as text"), return the rest of the
report as the text of your final message; never work around the refusal. PIN: origin 3ee246d. Plan: `tasks/issue59-batch-plan.md`.
Source: I59-C's adjacent finding (`tasks/briefs/i59/I59-C-report.md`, its hand-back summary) and AF-AP-232 in
`docs/INCIDENT-LOG.md`. The sibling fix to copy the shape of: S0-04's `do_config` in `tasks/briefs/i59/I59-C.patch` (held for
the batch, not in the tree).

AUTHORIZATION AND LIMITS: first-party, defensive secret-leak hardening of the owner's own proof checker. Every test secret is a
FAKE string built at run time. No network. No outward-facing action.

## WHY

`_read_yaml` in `proofs/S0-03/check_omniroute_roundtrip.py` (C:263-270) catches `yaml.YAMLError` and `UnicodeDecodeError`
only, and `main` (C:936-952) catches only `Usage`, `Deferred` and `Failure`. PyYAML also raises builtins: an explicit tag's
constructor raises a `ValueError` or `KeyError` that quotes the value (`!!float` and `!!bool` lower-cased), a bad `!!timestamp`
an `AttributeError`, and a deep nesting a `RecursionError`. Each escapes to a traceback; the first ones print the value. The
checker is attested, so the fix rides the issue #59 batch: one re-mint and one owner re-sign for all its changes.

## CONTRACT

1. **The reader.** Every exception from parsing the file (the read and `yaml.safe_load`) becomes the checker's own
   `Failure("bundle: <name> is not valid YAML (<Class>)")`, the form C:270 already uses: the class name only, never the
   message, a snippet or the problem text. `_require_file` stays outside and unchanged. Nothing else in the checker changes.
2. **Tests** in `tests/test_s0_03_omniroute.py`, through the checker's real CLI (`main`), on a bundle whose
   `hermes/profile.yaml` holds a fake value under each of: `!!int`, `!!float`, `!!bool` (with a mixed-case value, so the
   lower-cased leak is visible), a bad `!!timestamp`, and a deep nesting. Each run exits 1 with the exact
   `failure_reason: bundle: hermes/profile.yaml is not valid YAML (<Class>)` line, and no case-folded run of 8 characters of the
   value appears in stdout or stderr. Each row first asserts, in process, that PyYAML raises exactly that class on that text, and
   (where the class quotes input) that PyYAML's own message carries the value, so the handler is the only reason it is absent.
3. **The kill table**, each a FAILED test, never an error (AF-AP-223): the PIN's handler (`yaml.YAMLError` and
   `UnicodeDecodeError`); a handler that adds `ValueError` and `KeyError` to those; a handler whose message carries `str(exc)`.
4. **Nothing else:** do NOT re-mint S0-03 and do NOT write `proofs/S0-03/result.json` or `proofs/ledger.json`.

## BOUNDARY

- MODIFY: `proofs/S0-03/check_omniroute_roundtrip.py` (`_read_yaml` only), `tests/test_s0_03_omniroute.py`.
- CREATE: your report.
- READ everything else. NEVER write any other file under `proofs/`.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. The tests for items 1-2 (red at the PIN, green after), with their names, and the kill table.
3. `bash scripts/test_summary.sh tests/test_s0_03_omniroute.py` twice, pasted with the set id (the floor: 195 passed, set
   696563f67d3c). The only test file that names the checker is that one (`grep -l`, below).
4. pyflakes on both files; `python3 scripts/no_laya_in_gates.py`; `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` prints 0 for every
   file you write.
5. NOT-done and DISCREPANCIES; every deviation, loud.

## STANDING RULES

- No git writes of any kind, no PC bridge, no outward-facing action.
- Never read a real secret source: `.pc-bridge.env`, any `*.env`, `/root/.codiv/api.env`, `~/.config/qwen-*`,
  `/root/.config/session-export/pseudonym.key`, and the GH_TOKEN and GITHUB_TOKEN variables.
- Other lanes hold this tree: SCRUB2-R1 (`scripts/transcript_export.py`, `scripts/session_export.py`, possibly
  `scripts/known_values_check.py` and their tests, its report) and I59-B (`proofs/S0-05/tools/pc/run_s0_05_units.sh`,
  `tests/test_s0_05_egress.py`, its report). `.lanes-live` lists every live lane's files. Never touch them.
- The disk is shared: scratch under 100 MB in `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/i59e/`, deleted as you go; a short `--basetemp`; never run the whole
  `tests/test_vendored_manifest.py`.
- Test counts are pasted from `scripts/test_summary.sh`. Stamps are substituted from `date -u`, never typed.
- Run long commands in one foreground call, each under 10 minutes. Kill by pid only.
- When a hook injection stamped `[S1 <id> <source>]` reaches you, write `S1-RATE <id> rel=<0-3> use=<0-3>` as a short text of
  its own (under 200 characters; a note only for a 0).

## PREMISE — MEASURED at authoring (2026-09-26 08:5xZ, the sandbox tree; HEAD = origin 3ee246d)

C = `proofs/S0-03/check_omniroute_roundtrip.py`. The escape probe loads C through `importlib` and calls `_read_yaml` on a
scratch file holding a fake value (`sk-FAKE` followed by hex digits, built in the probe).

```
$ git log -1 --format='%h %ci %s' -- proofs/S0-03/check_omniroute_roundtrip.py | cut -c1-90
5977bc0 2026-09-19 05:11:30 +0000 S0-03 realign complete: fixtures + tests to the artifact
$ grep -n -E 'def _read_yaml|except \(yaml.YAMLError|^def main|except (Deferred|Failure)' proofs/S0-03/check_omniroute_roundtrip.py
263:def _read_yaml(path: Path, name: str):
269:    except (yaml.YAMLError, UnicodeDecodeError) as exc:
936:def main(argv) -> int:
945:    except Deferred as exc:
948:    except Failure as exc:
$ grep -l -E 'check_omniroute_roundtrip' tests/*.py
tests/test_s0_03_omniroute.py
$ the escape probe (at HEAD)
!!int -> ESCAPES ValueError | message quotes the value: True
!!float -> ESCAPES ValueError | message quotes the value: True
deep nesting -> ESCAPES RecursionError | message quotes the value: False
$ bash scripts/test_summary.sh tests/test_s0_03_omniroute.py
pytest-exit: 0
pytest-summary: 195 passed in 22.39s
$ bash scripts/pc_suite.sh set-id -- tests/test_s0_03_omniroute.py
1 files set=696563f67d3c
```
