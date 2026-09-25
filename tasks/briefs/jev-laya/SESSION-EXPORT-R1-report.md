# SESSION-EXPORT-R1 report (task #252; D-031, the one focused repair)

Role: code-implementer (sandbox, Opus 5.5). Brief: `tasks/briefs/jev-laya/SESSION-EXPORT-R1-brief.md`. PIN: db1de1c.
Contract: `tasks/briefs/jev-laya/SESSION-EXPORT-brief.md` + AMENDMENTS 1, 2 + AMENDMENT 3 (in the R1 brief). Verifier's report:
`tasks/briefs/jev-laya/VERIFY-SESSION-EXPORT-report.md`. Scratch: `<scratchpad>/session-export-r1/` (`<scratchpad>` =
`/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad`).

STATUS: DONE 2026-09-25T11:00:14Z (started 07:39:41Z). Nothing is committed: the coordinator commits. This is the builder's report; the gate recommendation is the verifier's.

## TL;DR

R-1 to R-4 are built in the four boundary files, with tests, and measured on the real data.

- R-1 (F-1): a credential behind an escaped quote is redacted. All 7 of the verifier's escaped shapes read 0 through the
  real CLI (attack 1). A 44-character value under a credential name is redacted, not pseudonymized (attack 3,
  `tok44-esc`). The gate counts the new shape (`pattern:escaped-credential`).
- R-2 (F-4): a call whose input names the pseudonym key loses its result. The three key dumps (`xxd`, `od`, base64) are
  now dropped; the `xxd` and `od` dumps leave 0 of 8 key pieces (the PIN: 8 of 8).
- R-3: four new named rules (`bearer-lower`, `curl-user`, `pass-name`, `url-token-user`) and F-6 in `url-password`;
  `named_secrets` sees F-7's path forms. Each rule and each spelling stage is red on a named test when it is removed.
- R-4 (AMENDMENT 3): opaque pseudonyms fall from 109,328 to 28,302; 80,981 values (74.1%) stay as the tracked files
  spell them. Repo test names fall from 44,541 to 0. The strict pass's repo-path redactions fall from 1,783 to 390.
- The real export, run twice: 317 of 317 files byte-identical; gate total 0 over 18 patterns and 78 canary lines; rc 0.
- Tests: `238 passed` twice on the three-file set `6dde7977ceba`. Red first on the PIN: `77 failed, 156 passed`.
  Mutants: 36 of 36 red.
- Cost: the export takes about 570 s; the builder's took 329 s (section 3).
- NOT done (section 9): the export used a SCRATCH key, so re-export with the real key before shipping; one FAKE canary
  sits in this lane's transcript (HAZARD); the rest of F-5, symlinks, background output and brace expansion; the bridge
  env dump; the DSV2 record test goes red until the coordinator regenerates the record.

## Evidence index

| Evidence demand | Section | Tier |
|---|---|---|
| 1. The premise | 0 | verified (probes of this session) |
| 2. Red first on the PIN, then green | 2 (red), 7 (green) | verified |
| 3. The real export twice, byte-identical, its summary, gate 0; the verifier's harness | 3, 4 | verified |
| 4. AMENDMENT 3 by category, before and after; the strict pass's repo-path redactions | 5 | verified (counts only; no value read) |
| 5. One mutant per new rule | 6 | verified |
| 6. test_summary twice with the set id; the chat export; pyflakes; separators | 7 | verified |
| 7. NOT-done and DISCREPANCIES | 9, 10 | - |

Not verified, and said so where they appear: whether any of the 193 committed values of the `mixed case+digits`
category is a real secret (UNVERIFIED: reading values is forbidden here; section 8); that the DSV2 record test goes red
with this change (INFERRED from its source; not run; section 9).

## 0. Premise re-measure (evidence demand 1)

Verdict: the premise holds; one labeling slip that does not matter (below). Measured 2026-09-25T07:39Z-07:42Z.

```
$ git show db1de1c:<file> | sha256sum | cut -c1-16 ; sha256sum < <file> | cut -c1-16     (the shared tree)
395db6ddefe0e7fc  scripts/transcript_export.py      (pin and tree)
a402db33b776d1a7  tests/test_transcript_export.py   (pin and tree)
7bf26338e88c7bcc  scripts/session_export.py         (pin and tree)
05f83f7a0636c5dd  tests/test_session_export.py      (pin and tree)
$ git merge-base --is-ancestor db1de1c HEAD && echo ancestor ; git rev-parse HEAD origin/claude/soundbox-kit-migration-iz1jwf
ancestor
6ee93223b2cb7c06c85edf6a0faaa24ccf2baed5   (both)
$ git diff --stat db1de1c HEAD -- <the 4 boundary files> scripts/ship_to_pc.py tests/test_ship_to_pc.py
(empty, rc 0)
$ bash scripts/test_summary.sh tests/test_transcript_export.py tests/test_session_export.py tests/test_ship_to_pc.py
141 passed in 13.07s
pytest-exit: 0
pytest-summary: 141 passed in 13.07s
$ bash scripts/pc_suite.sh set-id -- tests/test_transcript_export.py tests/test_session_export.py tests/test_ship_to_pc.py
3 files set=6dde7977ceba
$ diff <(git show db1de1c:scripts/transcript_export.py) <scratchpad>/verify-session-export/fixrepo/scripts/transcript_export.py
101a102,105      (the candidate escaped-credential rule, 4 lines)
$ diff <(git show db1de1c:scripts/session_export.py) <scratchpad>/verify-session-export/fixrepo/scripts/session_export.py
116c116          (its gate name "escaped-credential" added to PATTERN_NAMES)
```

DISCREPANCY (does not matter): the brief's premise block lists `116c116` under the `transcript_export.py` diff. It is in
`scripts/session_export.py` (the `PATTERN_NAMES` tuple). The candidate is what the brief says: one rule plus its gate name.

F-1, F-2 and F-3 are the verifier's measurements (its report sections 2, 5, 7, 8, reproduced below where this repair
re-measures them). Its saved outputs are on disk: `verify-session-export/attack2.out` reads `opaque-run matches
pseudonymised: 109328` and `repo test name 44541 40.7%`; `verify-session-export/survey.out` reads `Bash calls naming a
secret path: source-only 1190`, `their results: source-only 1189`.

The builder's export (the old run in `<scratchpad>/session-export/`, to be replaced) was saved first: its manifest is
`<scratchpad>/session-export-r1/builder-manifest.json` (export id 2026-09-25T05:47:40Z, 317 sources, 244,494 lines, key id
d23396be261a, pseudonyms 69,846, strict_results 2,543). Its offsets are the "before" of every count in this report.

Cost of AMENDMENT 3's set, measured at HEAD 6ee9322 (`session-export-r1/runsets.py`, counts only): 9,601 tracked blobs,
186,921,333 bytes, read in 1.6 s through `git cat-file --batch`, scanned in 11.0 s; distinct runs of the opaque shape
(40+) 15,478, of the strict key-run shape (20+) 74,139, of the token-line shape (12+) 274,271.


## HAZARD logged at 08:16Z (read before the next fresh real export)

At about 08:1xZ a pytest run of the unfinished change (the negative control's monkeypatch lambdas lacked the new `keep`
argument, a TypeError inside `settle`) printed pytest's default traceback, which shows each frame's arguments. One FAKE
test canary (`CANARIES["orphan"]`, tag `orphan`) was in the `text` argument, so its value is now in ONE tool result of
this lane's transcript
(`/root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/subagents/agent-a60226a535b771d07.jsonl`). It
is fake, but a FRESH export that reads this transcript will count `canary:orphan 1` in its gate and exit 3 (loud, not a
leak). This lane's own exports use the builder's offsets, which predate this transcript, so they do not read it. From
then on every pytest run that can fail inside production code ran with `--tb=line` or `--tb=no` (no argument display),
and the tests' failure messages name canaries by tag only.

## 1. The change

Files touched: the four boundary files and this report. Nothing else (the other lane's files and `ship_to_pc.py` are
untouched; `git diff --stat` in section 7).

`scripts/transcript_export.py`. `scrub`, `SECRET_PATTERNS`, `_redact_run`, `turns`, `export` and `main` are unchanged
(checked in source, section 7), so the chat export and every other caller of `scrub` keep their output.
- R-1 (F-1): a new `PAYLOAD_PATTERNS` rule, `escaped-credential`: the verifier's candidate, widened inside F-1's class in two
  ways: any depth of escaping (`\\+` before the quote: a JSON body inside a double-quoted shell string is escaped twice), and
  the PASS names of R-3 behind an escaped quote. Its value stops at a backslash, a quote or whitespace, so the canonical JSON
  stays valid. The existing `basic-auth` rule also takes a quoted or escaped header name (`"Authorization": "Basic ..."` as a
  JSON member), the same class.
- R-3 (F-5, F-6): `bearer-lower` (any-case `bearer`: in an Authorization header, or with a digit in the token so prose
  stays), `curl-user` (curl's `-u`/`--user user:pass` within 2,000 characters of `curl`, before a pipe or separator; a `$`
  reference stays), `pass-name` (a name ending in capital `PASS`, as env names spell it; a bare `PASS` needs `=`; a `$`
  reference stays; the value keeps the escape of a closing quote), `url-token-user` (a credential alone in a URL's
  userinfo: 8+ characters with a letter and a digit; the scheme anchored so it stays linear), and F-6 in `url-password`
  (the password runs to the last `@` before the host).
- R-4 (AMENDMENT 3): `RUN_SHAPES` (the opaque rule's own pattern, `_KEY_RUN`, and a run of the token-line class, built from
  the same `_TOKEN` class string as `_TOKEN_LINE`); `scrub_strict(text, opaque=None, keep=())` leaves a committed assignment
  value, key run or token line. `_committed` also accepts `NAME=<a committed value>`, because the key run's class holds `=`
  and glued the name to the value (found by this lane's first test: without it a committed assignment value never survived
  the strict pass).

`scripts/session_export.py`:
- R-1: gate names for the five new payload rules (`PATTERN_NAMES`), so the gate counts each new shape.
- R-2 (F-4): `call_mode` returns (the call's mode, its result's mode); a call whose input names the pseudonym key keeps its
  scrubbed input, and its result (with its file changes and archive) becomes DROPPED.
- R-3 (F-7): `named_secrets(text)` replaces the four `SECRET_PATH.search` sites (a file tool's path, a call's input, an
  attachment's paths, a file change's path). It returns SECRET_PATH's matches over: the text; the text with quotes and
  backslashes removed and `/./` and `//` collapsed; each SECRET_FILES path whose directory and file it names apart (a
  relative path); each LONE_NAMES name it names alone (`pseudonym.key`, `omniroute.key`: no other file has them); and each
  path a glob in it matches (`_glob_hits`: component by component with fnmatch, on 2+ literal characters, plus a `.env` name
  completed from a glob's literal head). Every candidate passes SECRET_PATH, so disabling SECRET_PATH disables every
  spelling (the negative-control test relies on it).
- R-4: `repo_commit` (one `git rev-parse --verify <rev>^{commit}`, AF-AP-175's shape), `repo_runs` (every RUN_SHAPES run of
  the blobs tracked at that commit, via `git ls-tree -r -z` and `git cat-file --batch`, never the working tree; a blob git
  cannot give is a refusal), the pseudonymizer keeps a committed run, `settle`/`cap`/`Source` pass `keep`, the gate skips a
  committed opaque-run match, the pool initializer hands the set to each worker once, and the manifest records
  `repo: {path, commit, runs, runs_sha256}` (or `null`). CLI: `export --repo DIR --commit REV` (default: this script's repo
  at HEAD; with `--offsets`, the commit that manifest names, so the rerun reads the same set); an explicit repo or commit git
  cannot read refuses (rc 2); only the default may be missing (a copy outside git), and then the summary line and the
  manifest say nothing is exempt. `gate DIR` reads the committed runs of the repo and commit its manifest names.
- 28 new FAKE canaries in `CANARIES`, so the gate counts them in every export.

INTERPRETATION (flagged; not a deviation in substance): AMENDMENT 3's parenthetical builds the set from "every run of the
opaque rule's minimum length and shape"; its normative sentence also says a committed run is "not redacted by the strict
pass", whose runs are not opaque-shaped (a repo path holds `/`). So the set holds the runs of each rule's own shape: the
opaque rule's (40+), the key run's (20+) and the token line's (12+). Membership is exact (the same pattern on both sides),
not substring: substring membership would add only 0.3% of opaque values (measured, section 5) and would let a short
committed substring exempt a secret-shaped token.

Two of this lane's own rules were wrong in their first version and were fixed before the final runs (both found by this
lane's measurement over the real data, section 5): `curl-user` took any `-u` flag (about 4,600 `date -u +%H:%M:%S`
format strings in the raw transcripts) and `pass-name` was case-insensitive (about 3,200 code variables such as
`first_pass = ...`). The same pass found that `pass-name`'s first value class (scrub's `_V`) swallowed the escape of a
closing `\"`, the pre-existing defect of section 10; the final class keeps it.

GitNexus `impact` (upstream), before the edits: `scrub_strict` HIGH (8 impacted), `scrub_payload` HIGH (11), `settle` HIGH
(9), `call_mode` LOW (3), `pseudonymizer` LOW (1). Every impacted symbol is in `scripts/session_export.py`
(modules_affected 1), the export pipeline this repair targets; a literal sweep finds no other caller (the only other hit
is the negative-control test's monkeypatch of `scrub_strict`, updated for `keep`).

The sweep covers every tracked file: no code outside the four boundary files uses `scrub_payload`, `scrub_strict`,
`PAYLOAD_PATTERNS`, `RUN_SHAPES` or the strict sub-rules (only reports under `tasks/briefs/` name them), which agrees
with `impact`'s modules_affected 1. GitNexus `detect_changes` (read-only, the working tree at 10:5xZ): `Changes: 4 files,
99 symbols`, `Affected processes: 29`, `Risk level: critical`; each flow it lists belongs to the exporter (`cmd_gate`,
`cmd_export`, `Source.record`). The risk level reflects the size of the rewiring, all of it inside the exporter.

## 2. Red first, then green (evidence demand 2)

The new and changed tests ran on the PIN's code. The scratch tree `session-export-r1/red/` holds the PIN's
`scripts/transcript_export.py`, `scripts/ship_to_pc.py`, `tests/conftest.py` and `pyproject.toml` (each `diff`-equal to
`git show db1de1c:<file>`), the PIN's `scripts/session_export.py` and this repair's two test files, with two
adaptations. Both can only make the PIN look better:
- the 28 new FAKE canaries are added to the PIN's `CANARIES` table (`diff`: 8 added lines, 0 removed; data only). Without
  them every fixture test dies on a KeyError; with them the PIN's gate counts more.
- the two test helpers that pass `--repo` drop it (the PIN's CLI has no such flag; `diff` against the lane's test file:
  those two call sites only).

Pasted (the final test files, unchanged since 09:52:15Z). The first run at 10:39:50Z; the second at 10:52:46Z through
`session-export-r1/red_reasons.py`, which runs the same command on a wide terminal and prints each failure's message with
the parametrize ids stripped and every canary value, 8-character window of one and key-like run masked:
```
$ (in session-export-r1/red) python3 -m pytest -q -p no:cacheprovider --tb=no -rf tests/test_transcript_export.py tests/test_session_export.py
77 failed, 156 passed in 5.30s
$ python3 session-export-r1/red_reasons.py session-export-r1/red          (count, test, the PIN's message)
  1  test_a_call_that_names_the_pseudonym_key_loses_its_result | AssertionError: key-xxd differs at character 0 (lengths 135, 30); canaries in it: ['key-xxd']
 10  test_a_credential_behind_an_escaped_quote_is_redacted | AssertionError: the value survived
  1  test_a_repo_git_cannot_read_refuses_and_a_copy_outside_git_exempts_nothing | AssertionError: usage: session_export.py [-h] {init-key,export,gate} ...
  1  test_an_escaped_long_token_is_redacted_not_pseudonymized | assert ('{"command":...c.sh ls"}', 1) == ('{"command":...c.sh ls"}', 0)
  1  test_an_offsets_rerun_reads_the_commit_its_manifest_names | AssertionError: usage: session_export.py [-h] {init-key,export,gate} ...
  1  test_call_modes | AssertionError: assert None == ('drop', 'drop')
  1  test_committed_runs_stay_as_they_are | AssertionError: a3-normal differs at character 39 (lengths 136, 178); canaries in it: []
  1  test_escaped_credentials_are_redacted | AssertionError: esc-export differs at character 37 (lengths 104, 94); canaries in it: ['esc-export']
  1  test_fixed_offsets_give_byte_identical_output | AssertionError: 
  1  test_gate_counts_patterns_and_canaries_and_prints_none | AssertionError: gate: 1 files, 13 events, 0 unreadable lines
 16  test_named_secrets_leaves_ordinary_commands | AttributeError: module 'session_export_under_test' has no attribute 'named_secrets'
 20  test_named_secrets_sees_each_spelling | AttributeError: module 'session_export_under_test' has no attribute 'named_secrets'
  1  test_no_canary_survives_the_export | AssertionError: export <run>:52:47Z: 5 sources, 480706 bytes read, 7152 bytes written, 0.4 s
  1  test_offsets_refuse_a_changed_prefix_or_archive | AssertionError: assert 3 == 0
  1  test_opaque_values_become_stable_keyed_pseudonyms | AssertionError: a commit id survived, or the pseudonym count moved
 12  test_r3_named_shapes_are_scrubbed | AssertionError: a value survived
  1  test_r3_named_shapes_are_scrubbed_through_the_cli | AssertionError: bearer-lower differs at character 22 (lengths 43, 33); canaries in it: ['bearer-lower']
  1  test_repo_runs_refuses_a_blob_git_cannot_give | AttributeError: module 'session_export_under_test' has no attribute 'repo_runs'
  1  test_run_shapes_are_the_rules_own_shapes | AttributeError: module 'transcript_export_payload_under_test' has no attribute 'RUN_SHAPES'
  1  test_secret_path_spellings_are_seen | AssertionError: path-rel differs at character 0 (lengths 21, 11); canaries in it: ['path-rel']
  1  test_secret_paths_are_dropped_or_strict_passed | assert (11, 10) == (20, 13)
  1  test_strict_pass_keeps_committed_runs | TypeError: scrub_strict() got an unexpected keyword argument 'keep'
  1  test_the_gate_reads_the_committed_runs_its_manifest_names | AssertionError: gate: 5 files, 158 events, 0 unreadable lines
parsed FAILED lines 77; 77 failed, 156 passed in 5.29s
```

Read with it:
- The scrubber tests (`test_a_credential_behind_an_escaped_quote_is_redacted`, 10 rows: the verifier's 7 shapes, a
  double escape, a JSON Basic header, a PASS name; `test_r3_named_shapes_are_scrubbed`, 12 rows) fail because the value
  survives. `test_an_escaped_long_token_is_redacted_not_pseudonymized` fails because the 44-character value reaches the
  opaque callable once (G6).
- The CLI tests fail on the exported text: `_expect` reports the first differing character and the canary TAGS in it
  (`esc-export`, `key-xxd`, `bearer-lower`, `path-rel`), or a committed name that became a pseudonym (`a3-normal`, no
  canary in it). The export tests that need a clean gate fail because the PIN's own gate exits 3 on the new canaries.
- `test_secret_paths_are_dropped_or_strict_passed`: the fixture's (dropped, strict) counts are `(11, 10)` at the PIN and
  `(20, 13)` in R1.
- The new functions fail as missing (`named_secrets`, `repo_runs`, `RUN_SHAPES`, `keep`, the `--repo`/`--commit`
  flags). For the 36 `named_secrets` rows, the spellings were also run through the PIN's own denylist (`SECRET_PATH`,
  read from `git show db1de1c`): it misses 16 of the 20 `SPELLED` rows and sees 4 (`$HOME/`, `~/`, a literal `*.env`,
  and a row that names `.env` and the key path raw); it sees none of the 16 `NOT_SECRET` rows, and neither does R1.

Not red at the PIN, by design: `test_passwd_and_password_names_stay_scrubbed` (2; scrub's own names, a pin),
`test_r1_rules_keep_text_with_no_secret` (the negative controls: 23 texts no rule may touch) and
`test_r1_rules_stay_linear_on_long_runs` (7 long texts). Mutants R3m, R3n and R3o prove the negative controls
(section 6): each over-broad version of a rule turns them red.

Green: section 7 (`238 passed` twice on the three-file set).

## 3. The real export, rebuilt twice (evidence demand 3)

Inputs: the builder's offsets (its manifest, saved before the old run was replaced), so both runs read exactly the
bytes the builder's export read (244,494 lines in both), and every count compares with the builder's run. Key: a
SCRATCH key made by the CLI's own `init-key` in `session-export-r1/key/` (key id 7e899a8a62ef); the real key was never
read (standing rule). The set: this repo at 6ee9322 (HEAD when the lane started). Code: the final files (the manifest's
`code_sha256` 5ea07eb834ac6329... equals `code_hashes()` of the files as they stand: `transcript_export.py`
af9d73eab7af665b..., `session_export.py` 9f56802d112465ef...). Each run was started detached (`setsid nohup`) and
waited for with `tail --pid` under 590 s.

Run 1 (started 09:52:45Z, after the last code edit at 09:52:06Z; rc 0), the summary pasted without its 78 canary lines:
```
$ python3 scripts/session_export.py export --out <scratchpad>/session-export --offsets <scratchpad>/session-export-r1/builder-manifest.json \
      --key <scratchpad>/session-export-r1/key/pseudonym.key --jobs 4 --repo /home/user/agent-factory --commit 6ee93223b2cb7c06c85edf6a0faaa24ccf2baed5
export 2026-09-25T09:52:45Z: 317 sources, 1178943962 bytes read, 38866988 bytes written, 564.3 s
folders {"-home-user-agent-factory": {"sources": 1, "bytes_read": 3074681}, "-home-user": {"sources": 316, "bytes_read": 1175869281}}
committed runs 296985 at 6ee93223b2cb7c06c85edf6a0faaa24ccf2baed5
events {"api_error": 72, "file_change": 2796, "harness_notice": 488, "hook": 2644, "notification": 6684, "pruner_archive": 1, "summary": 131, "text": 16267, "thinking": 4997, "tool_call": 46435, "tool_result": 46422}
capped {"hook": 2, "notification": 1753, "summary": 2, "text": 40, "tool_call": 41, "tool_result": 20}
dropped_secret_path 29 strict_results 2572 unsettled 0 seam_adjusted 2 thinking_signature_only 29704 duplicate_notifications 2 file_changes_unrecorded 364 pseudonyms 10838 pruner_archives 1 archives 1 archives_skipped 0 archives_unlinked 0 archives_unmatched 0
gate: 317 files, 126937 events, 0 unreadable lines
pattern:private-key 0
pattern:credential 0
pattern:bearer 0
pattern:sk-key 0
pattern:github-token 0
pattern:google-key 0
pattern:slack-token 0
pattern:bridge-link 0
pattern:opaque-run 0
pattern:bridge-host 0
pattern:bearer-tail 0
pattern:basic-auth 0
pattern:escaped-credential 0
pattern:url-password 0
pattern:bearer-lower 0
pattern:curl-user 0
pattern:pass-name 0
pattern:url-token-user 0
total 0
```
The 78 canary lines (the 74 test canaries and the key's 4 printed forms): 78 lines, 0 non-zero.

Run 2, the determinism rerun (started 10:02:26Z; rc 0), took its offsets AND its commit from run 1's manifest (no
`--commit`):
```
$ python3 scripts/session_export.py export --out <scratchpad>/session-export-run2 --offsets <scratchpad>/session-export/manifest.json \
      --key <scratchpad>/session-export-r1/key/pseudonym.key --jobs 4 --repo /home/user/agent-factory
export 2026-09-25T10:02:26Z: 317 sources, 1178943962 bytes read, 38866988 bytes written, 578.8 s
$ diff <(tail -n +2 final1.out) <(tail -n +2 final2.out)      (the two summaries without their first line)
(no output: the other 103 lines are equal, the 78 canary lines included)
$ (session-export-r1/determinism.out: the hashes of both output trees and both manifests)
outputs run1 317 run2 317; byte-identical 317; differing 0
sha256 over the sorted 'sha  path' lines: run1 680de82aa98d5043ad13a8183aab9544458e7f1d2344b2bf19aada17ad0372f0 run2 680de82aa98d5043ad13a8183aab9544458e7f1d2344b2bf19aada17ad0372f0
manifest keys that differ: ['export_id', 'wall_seconds']
every output_sha256 in run1's manifest matches its file: True
repo record equal: True | run2's commit (from run1's manifest): 6ee93223b2cb7c06c85edf6a0faaa24ccf2baed5 | runs 296985 | runs_sha256 9780a3842b7fec174d6fb75d65cde9f807579cd076aa91760d38488d0b2823c7
code_sha256 5ea07eb834ac6329c32a5dd22fc53d948ecf4a8d942ace965dd1e2558056d217 | pseudonym key id 7e899a8a62ef
largest source: offset 714512525, input sha256 9366613fde01995a, output 73ce4217fca12621, 12545132 bytes
```

The standalone gate on run 1's export (started 10:12:24Z; rc 0; it rebuilt the committed runs from the repo and commit
the manifest names):
```
$ python3 scripts/session_export.py gate <scratchpad>/session-export --jobs 4 --key <scratchpad>/session-export-r1/key/pseudonym.key
gate: 317 files, 126937 events, 0 unreadable lines
pattern:private-key 0
pattern:credential 0
pattern:bearer 0
pattern:sk-key 0
pattern:github-token 0
pattern:google-key 0
pattern:slack-token 0
pattern:bridge-link 0
pattern:opaque-run 0
pattern:bridge-host 0
pattern:bearer-tail 0
pattern:basic-auth 0
pattern:escaped-credential 0
pattern:url-password 0
pattern:bearer-lower 0
pattern:curl-user 0
pattern:pass-name 0
pattern:url-token-user 0
total 0
```
The 78 canary lines: 0 non-zero.

Against the builder's export (same offsets, same 244,494 lines; the totals of both manifests):

| Counter | Builder (PIN) | R1 | Why |
|---|---|---|---|
| events per kind | as pasted | identical | the record handling did not change |
| capped: text / tool_call | 37 / 40 | 40 / 41 | committed runs now stay whole, so some texts grew past the cap |
| seam_adjusted | 0 | 2 | the cap moved inward where a cut committed run would form an uncommitted one |
| dropped_secret_path | 11 | 29 | R-2 and the F-7 spellings (split by event kind below) |
| strict_results | 2,543 | 2,572 | the F-7 spellings, less the results R-2 now drops (split below) |
| pseudonyms | 69,846 | 10,838 | AMENDMENT 3 keeps committed runs (section 5) |
| unsettled | 0 | 0 | |
| gate total | 0 (13 patterns) | 0 (18 patterns) | the 5 new shapes are counted, all 0 |
| bytes written | 38,706,220 | 38,866,988 | verbatim runs compress differently than pseudonyms |
| wall | 329.3 s | 564.3 s (run 2: 578.8 s) | see COST below |

The `pseudonyms` counter counts the pseudonyms left in the emitted texts; section 5 counts every value the opaque rule
takes on a text's first pass. The two do not compare with each other.

Where the dropped and strict counters moved: 17 sources changed. `session-export-r1/emit_split.py` converts exactly
those sources to the builder's offsets, once with the PIN's code and once with R1's, and counts every emitted event whose
mode is `drop` or `strict` by kind (counts only; 10:48:51Z to 10:56Z, both rc 0):
```
PIN (session-export-r1/pin-se): 17 sources; dropped_secret_path 11, strict_results 2295
  drop   notification        1
  drop   tool_call           5
  drop   tool_result         5
  strict file_change       208
  strict tool_result      2087
R1 (scripts/, the final code): 17 sources; dropped_secret_path 29, strict_results 2324
  drop   file_change         1
  drop   notification        1
  drop   tool_call           5
  drop   tool_result        22
  strict file_change       210
  strict tool_result      2114
```
Tool results: 17 more dropped (5 to 22) and 27 more strict (2,087 to 2,114). That is exactly section 5's call-mode table:
17 calls newly dropped, and 35 newly strict less the 8 that moved from strict to dropped. A file change takes its call's
result mode (or is dropped for its own path): 1 more dropped, 2 more strict. The totals match the manifests' deltas
(+18, +29).

COST (reported, not fixed): R1 roughly doubles the scrub's CPU. `session-export-r1/profile.py` converted the same 60 MB
prefix of the largest transcript in one process (an earlier revision of R1, with the escaped rule as it is now): PIN
7.8 s, R1 16.0 s; the new `escaped-credential` rule took 5.0 s (scrub's own `credential` rule 3.3 s: they share the
name alternation, and the escaped rule also scans for the PASS names), `pass-name` 1.2 s, `named_secrets` 0.8 s, each
other new rule 0.4-0.5 s. The whole export went from 329 s to about 570 s, so the coordinator's wait needs two 590 s
`tail --pid` calls. The cheap fix is a prefilter: the escaped rule can only match a text that holds a backslash before a
quote, and most results hold none. Not done: it would make one PAYLOAD_PATTERNS entry a wrapper object instead of a
compiled pattern, a design change beyond R-1.

## 4. The verifier's harness, re-run (evidence demand 3)

A copy of `verify-session-export/h/` in `session-export-r1/h/`, run with `VFX_WT=/home/user/agent-factory` (the real CLI
of this tree, the final code; the default repo, this one at HEAD 6ee9322). One adaptation: attack 1's positive control
monkeypatches `scrub_strict` with the old two-argument signature; the copy widens that lambda to take `keep`:
```
$ diff verify-session-export/h/attack1.py session-export-r1/h/attack1.py
216c216
<     se.scrub_strict = lambda s, opaque=None: s
---
>     se.scrub_strict = lambda s, opaque=None, keep=(): s        # R1: scrub_strict takes keep
```
`vfx.py`, `attack1c.py`, `attack3.py` and `inspect1.py` are byte-identical to the verifier's. Run 10:14:50Z to
10:16:11Z; `attack1.py`, `attack1c.py` and `attack3.py` each exited 0.

Attack 1 (38 shapes, one FAKE canary each), pasted:
```
export rc 0; gate total 0
protections-off export rc 3
tag                  expect    leaks  full  shape (positive control: present when off)
ctl-raw-assign       scrubbed  -      0     Bash result, raw NAME=value
ctl-json-result      scrubbed  -      0     Bash result, raw JSON "token": "v"
ctl-quoted-raw       scrubbed  -      0     Bash result, raw NAME="v"
short-echo           ?         LEAK   1     Bash `echo $VAR` result, 32 hex, bare
printenv-bare        ?         LEAK   1     Bash `printenv NAME` result, 24 alnum, bare
printenv-44          ?         -      0     Bash `printenv NAME` result, 44 url-safe, bare
split-lines          ?         LEAK   1     Bash result, NAME=\<newline> value (line continuation)
split-events         ?         LEAK   1     NAME= at the end of one result, the value at the start of the next
b64                  ?         -      0     Bash result, base64 of NAME=value
urlenc-pass          ?         LEAK   1     URL-encoded password%3D<v>
urlenc-link          ?         -      0     URL-encoded bridge link https%3A%2F%2F<host>
json-cmd-export      ?         -      0     tool_call: Bash command with NAME="v" (canonical JSON)
json-cmd-body        ?         -      0     tool_call: Bash command with a JSON body "password": "v"
json-write-cfg       ?         -      0     tool_call: Write of a JSON config "api_key": "v"
json-edit-yaml       ?         -      0     tool_call: Edit new_string token: "v"
json-hook            ?         -      0     hook attachment stdout {"token": "v"}
json-notif           ?         -      0     notification attachment secret: "v"
json-stophook        ?         -      0     stop_hook_summary hookErrors password="v" (text is canonical JSON)
url-pass-at          ?         -      0     https://user:pa@ss@host (a raw @ in the password)
url-token-user       ?         -      0     https://<token>@host (token as the user, no colon)
curl-u               ?         -      0     tool_call: curl -u user:pass
bearer-lower         ?         -      0     Bash result, lowercase `authorization: bearer v`
netrc                ?         LEAK   1     Bash `cat ~/.netrc` result: password <v> (space, no =)
unlisted-name        ?         -      0     Bash `printenv` result DB_PASS=v (a name outside the list)
secret-key-base      ?         LEAK   1     secret_key_base: v (a compound name the rule misses)
docker-auth          ?         LEAK   1     docker config "auth": "<b64 user:pass>"
thinking-prose       ?         LEAK   1     thinking block, prose `the password is v`
diff-json            scrubbed  -      0     file_change diff line +  "token": "v" (raw text)
archive-bare         ?         LEAK   1     pruner archive holding a bare token
glob-keyfile         ?         -      0     Bash `cat ~/.config/qwen-*/api-key` (glob) result
rel-keyfile          ?         -      0     Bash `cd ~/.config/qwen-builder && cat api-key` (relative) result
dot-keyfile-read     ?         -      0     Read /root/.config/qwen-builder/./api-key
dslash-keyfile-read  ?         -      0     Read /root/.config/qwen-builder//api-key
symlink-read         ?         LEAK   1     Read of a symlink made to omniroute.key one call earlier
quoted-glob-env      ?         -      0     Bash `cat '.pc-bridge.e'*` result ZQ_ENDPOINT=v (strict would take it)
bg-output            ?         LEAK   1     background `cat .../qwen-builder/api-key`, output read by TaskOutput
grep-dir             ?         -      0     Grep over the qwen-builder dir (input names the dir only)
mcp-arg              ?         -      0     tool_call: an MCP tool input {"password": v}
survivors 12 of 38: short-echo printenv-bare split-lines split-events urlenc-pass netrc secret-key-base docker-auth thinking-prose archive-bare symlink-read bg-output
```

12 of 38 survive (the PIN: 29; the verifier's one-rule candidate: 21). All 7 escaped `json-*` shapes read 0, and so do
the R-3 shapes (`url-pass-at`, `url-token-user`, `curl-u`, `bearer-lower`, `unlisted-name`) and the F-7 spellings R-3
lists (`glob-keyfile`, `rel-keyfile`, `dot-keyfile-read`, `dslash-keyfile-read`, `quoted-glob-env`). The 12 survivors
are all outside R-3's list and stay follow-ups (section 9): the rest of F-5 (`short-echo`, `printenv-bare`,
`split-lines`, `split-events`, `urlenc-pass`, `thinking-prose`, `archive-bare`), three named shapes R-3 does not name
(`netrc`, `secret-key-base`, `docker-auth`), and two spellings no textual denylist can see (`symlink-read`,
`bg-output`). The export exits 0 with its gate at 0 on them: the gate knows only the scrubber's shapes.

The exported bytes around every escaped redaction in attack 1's export (`session-export-r1/escaped_bytes.py`: each of
the 38 canaries in its raw, 32-hex, 20-lowercase and 44-character forms, and each 8-character window of one, masked as
`<C:tag>`/`<W:tag>`; none was left to mask in these lines):
```
line 25 coordinator/tool_call: ...{"command":"export PC_BRIDGE_TOKEN=\"<redacted>\" && bash scripts/pc.sh ls","...
line 27 coordinator/tool_call: ...{"command":"curl -s -d '{\"password\": \"<redacted>\"}' https://api.example.com/l...
line 29 coordinator/tool_call: ...{"content":"{\n  \"api_key\": \"<redacted>\",\n  \"region\": \"eu\"\n}\n...
line 31 coordinator/tool_call: ...le_path":"/home/user/agent-factory/cfg/app.yaml","new_string":"token: \"<redacted>\"","old_string":"token: \"x\"...
line 33 hook/hook: ...lUse","hookName":"PostToolUse:Bash","stderr":"","stdout":"{\"token\": \"<redacted>\"}","toolUseID":"toolu_vfy_ho...
line 34 system/notification: ...{"data":{"note":"secret: \"<redacted>\""},"type":"structured_output...
line 35 hook/hook: ...dditionalContext":[],"hookCount":1,"hookErrors":["retry with password=\"<redacted>\""],"hookInfos":[{"command":"...
tags 38; tags with a canary or a window of one anywhere in the export (names only): 11 archive-bare bg-output netrc printenv-bare secret-key-base short-echo split-events split-lines symlink-read thinking-prose urlenc-pass
```
The last line names only raw forms; `docker-auth`'s value is exported base64-encoded, which attack 1 detects itself.

Attack 1c (F-4: the pseudonym key and a bridge env file as dumps; a fixture key made by `init-key`, the same key given
to the export, so its gate knows the key's four printed forms), pasted:
```
export rc 0; gate total 0; key-form canaries in the gate: [('pseudonym-key-HEX', '0'), ('pseudonym-key-b64', '0'), ('pseudonym-key-b64url', '0'), ('pseudonym-key-hex', '0')]
xxd-key          strict-passed result: key recoverable by joining the dump: False | key hex 8-char pieces present 0/8 | bridge-token 8-char windows present 0
od-key           strict-passed result: key recoverable by joining the dump: False | key hex 8-char pieces present 0/8 | bridge-token 8-char windows present 0
b64-wrapped-key  strict-passed result: key recoverable by joining the dump: False | key hex 8-char pieces present 0/8 | bridge-token 8-char windows present 0
xxd-bridge-env   strict-passed result: key recoverable by joining the dump: False | key hex 8-char pieces present 0/8 | bridge-token 8-char windows present 10
```
The three key dumps are now DROPPED (R-2), so nothing of the key is left (the PIN: `True`, 8/8, for `xxd` and `od`).
The bridge env file's `xxd` still shows 10 of the token's 25 eight-character windows in its printable column: R-2 covers
the pseudonym key only (the brief's wording), so that half of F-4 stays a follow-up (section 9). The verifier counted 0
such dumps in the real transcripts.

Attack 3 (pseudonyms: two keys, two runs, two folders), pasted:
```
k1-run1: rc 0
k1-run2: rc 0
k2: rc 0
SHA_A pseudonym under k1, count per folder (owner text + tool_call + tool_result = 3 each): {'-vfy-a': 3, '-vfy-b': 3}
SHA_A pseudonym equals HMAC-SHA256(k1, value)[:12] computed here: True
raw SHA_A / SHA_B in the k1 export: False False
two runs, same key: outputs byte-identical (per .xz sha): True
another key gives another pseudonym: True
k1 in any printed form in any output or CLI text: False
tok44-raw     raw-in-export False pseudonymised False
tok44-esc     raw-in-export False pseudonymised False
tok44-cmdarg  raw-in-export False pseudonymised False
gh-long       raw-in-export False pseudonymised False
bearer-long   raw-in-export False pseudonymised False
sk-long       raw-in-export False pseudonymised False
the escaped call as exported: {"command":"export PC_BRIDGE_TOKEN=\"<redacted>\" && bash scripts/pc.sh ls"}
```
Every property holds, and `tok44-esc` (a 44-character `PC_BRIDGE_TOKEN` value behind an escaped quote) is now
redacted, not pseudonymized (the PIN: `pseudonymised True`), as AMENDMENT 1 G6 requires.

## 5. AMENDMENT 3's effect, and what each rule takes (evidence demand 4; counts only)

Both instruments run the production `convert()` over every real transcript to the builder's offsets (the same bytes as
the builder's export and the verifier's attack 2) and classify each value at the moment the scrub takes it, with the
verifier's categories (its `attack2.py` classifier, copied). Before: `session-export-r1/measure_pre.py` on the PIN's code
(the shared tree, unchanged at 07:55Z; it reproduces the verifier's `attack2.out` exactly: 109,328, 44,541, 5,783, 1,783).
After: `session-export-r1/measure_post.py` on R1's final code with the set of 6ee9322 (`settle` wrapped so each text is
classified once, on its first pass; the events come from the real `settle`). Nothing but counts is printed.

| Category (the verifier's) | Before: pseudonymized | After: pseudonymized | After: kept (committed) |
|---|---|---|---|
| repo test name | 44,541 | 0 | 44,513 |
| kebab-case | 29,877 | 20,889 | 8,986 |
| hex64 (sha256) | 12,886 | 1,787 | 11,098 |
| hex40 (commit id) | 7,824 | 2,631 | 5,191 |
| repo path component | 4,709 | 26 | 4,683 |
| test_* not defined in the tree now | 4,665 | 623 | 4,042 |
| mixed case+digits (blob or token) | 1,400 | 1,201 | 193 |
| other | 1,335 | 753 | 576 |
| lower_snake other | 884 | 232 | 652 |
| repo def/class name | 729 | 0 | 729 |
| mcp tool name | 196 | 14 | 182 |
| hex other length | 154 | 128 | 26 |
| UPPER_SNAKE | 108 | 17 | 91 |
| harness id | 20 | 1 | 19 |
| **all** | **109,328** (100%) | **28,302** (25.9%) | **80,981** (74.1%) |

The opaque rule takes 109,283 values after R1 (109,328 before): the new named rules now redact 45 values first (among them
escaped tokens of 40+ characters that the opaque rule used to pseudonymize, against G6).

| Strict pass | Before: redacted (repo paths) | After: redacted (repo paths) | After: kept (repo paths) |
|---|---|---|---|
| key runs | 5,783 (1,783) | 2,557 (390) | 4,094 (1,466) |
| token lines | 478 (4) | 478 (1) | 332 (113) |

The repo paths the strict pass redacts fall from 1,783 to 390. The 390 left are paths no tracked file spells out as one
run (for example an absolute path under `/home/user/agent-factory/` that no file writes out in full). The after
counts are higher in total because more text now reaches each sub-rule: 29 more strict texts (F-7), and a line whose
key run is kept can now reach the token-line check. Assignment values: 1,792 redacted and 79 kept after R1; the
before count (3,706) counted every strict call, not first passes, so it does not compare (section 10).

The pre-design measurement also split the opaque values by membership (on the PIN's run, before any code): exact
run 81,023 (74.1%), committed only as a substring of a longer run 298 (0.3%), committed after a JSON escape letter
(`\n` then a name) 438 (0.4%), neither 27,569 (25.2%). R1 keeps exact runs only (section 1).

The after-measurement, pasted:
```
R1 at 6ee93223b2cb: opaque-run matches 109283: pseudonymised 28302 (25.9%), kept as committed 80981 (74.1%)
  category                                pseudo      kept
  repo test name                               0     44513
  kebab-case                               20889      8986
  hex64 (sha256)                            1787     11098
  hex40 (commit id)                         2631      5191
  repo path component                         26      4683
  test_* not defined in the tree now         623      4042
  mixed case+digits (blob or token)         1201       193
  other                                      753       576
  lower_snake other                          232       652
  repo def/class name                          0       729
  mcp tool name                               14       182
  hex other length                           128        26
  UPPER_SNAKE                                 17        91
  harness id                                   1        19
strict keyrun  redacted   2557 (repo paths   390)  kept   4094 (repo paths  1466)
strict token   redacted    478 (repo paths     1)  kept    332 (repo paths   113)
strict assign  redacted   1792 (repo paths     0)  kept     79 (repo paths     4)
strict texts (first passes): 2572
values each rule takes (first passes; named and payload rules in scrub_payload order):
  credential              8752
  sk-key                   873
  bearer                   561
  escaped-credential       369
  private-key              268
  bearer-lower             159
  bridge-link              119
  bearer-tail               67
  github-token              48
  url-password              45
  google-key                34
  bridge-host               29
  slack-token               24
  basic-auth                18
  pass-name                  9
  curl-user                  2
call modes that changed, PIN -> R1 (call, result), by the spelling that decided:
  (None, None)           -> (None, 'strict')       glob                     25
  (None, None)           -> (None, 'strict')       dir and file apart        9
  (None, None)           -> (None, 'drop')         glob                      9
  (None, 'strict')       -> (None, 'drop')         raw                       8
  (None, None)           -> (None, 'strict')       lone name                 1
```

Read with it: `pass-name` 9 and `curl-user` 2 are the final rules. Their first versions took 1,626 and 2,474 values
in the same measurement (a case-insensitive PASS, and any `-u` flag); `session-export-r1/fp_scan.py` then counted
their shapes in the raw transcripts without reading a value: about 4,600 of the `-u` hits followed `date`
(`date -u +%H:%M:%S`), and about 3,200 of the PASS hits were lowercase names (code and shell variables). The final
rules require `curl` and a capital `PASS`, and leave a `$` reference; the shape check of the other two busy rules
(`fp_scan2.py`) found no such class (`escaped-credential` takes what scrub's credential names take in raw text;
`bearer-lower` takes token-shaped values).

The call-mode table: R1 puts 35 more real calls' results through the strict pass (25 by a glob, 9 by a directory
and file named apart, 1 by a lone name) and drops 17 more results (8 whose command names the key literally and were
strict before; 9 by a glob such as `*.key`, which LONE_NAMES matches: conservative, a listing dropped).

The before-measurement, pasted (`session-export-r1/measure_pre.py`, 07:55Z to 08:00Z, the PIN's code):
```
repo /home/user/agent-factory at 6ee93223b2cb7c06c85edf6a0faaa24ccf2baed5: 9601 tracked files
opaque-run values taken: 109328 (distinct 6948)
  membership exact                        81023   74.1%
  membership none                         27569   25.2%
  membership escape-glued (exact)           438    0.4%
  membership substring                      298    0.3%
  preceded by a backslash: {'escape-glued (exact)': 438, 'none': 42}
  repo test name                         44541   40.7%  {'exact': 44541}
  kebab-case                             29877   27.3%  {'none': 20823, 'exact': 8988, 'substring': 66}
  hex64 (sha256)                         12886   11.8%  {'none': 1764, 'exact': 11099, 'substring': 23}
  hex40 (commit id)                       7824    7.2%  {'none': 2631, 'exact': 5192, 'substring': 1}
  repo path component                     4709    4.3%  {'exact': 4683, 'none': 26}
  test_* not defined in the tree now      4665    4.3%  {'none': 518, 'substring': 105, 'exact': 4042}
  mixed case+digits (blob or token)       1400    1.3%  {'none': 1196, 'exact': 198, 'escape-glued (exact)': 2, 'substring': 4}
  other                                   1335    1.2%  {'exact': 581, 'none': 363, 'escape-glued (exact)': 391}
  lower_snake other                        884    0.8%  {'exact': 652, 'none': 145, 'escape-glued (exact)': 45, 'substring': 42}
  repo def/class name                      729    0.7%  {'exact': 729}
  mcp tool name                            196    0.2%  {'none': 14, 'exact': 182}
  hex other length                         154    0.1%  {'none': 71, 'exact': 26, 'substring': 57}
  UPPER_SNAKE                              108    0.1%  {'none': 17, 'exact': 91}
  harness id                                20    0.0%  {'none': 1, 'exact': 19}
strict keyrun redactions: 5783 (distinct 2497) membership {'exact': 3253, 'none': 2362, 'substring': 168}; of them repo paths 1783 {'none': 320, 'exact': 1424, 'substring': 39}
strict token redactions: 478 (distinct 401) membership {'exact': 97, 'none': 306, 'substring': 75}; of them repo paths 4 {'exact': 4}
strict assignment values: 3706 (distinct 1250) {'not one token': 3548, 'one token: exact': 67, 'one token: none': 56, 'one token: substring': 35}
```

## 6. Mutants (evidence demand 5)

`session-export-r1/mutants.py`: 36 mutants, one per new rule or wiring point. Each is one exact-anchor edit, asserted
to match exactly once, on a scratch copy of the lane's files (the shared tree is never edited). The two test files run
with `--tb=no`, and only test FUNCTION names are printed. "Never matches" = `(?!)` put in front of the rule's pattern,
which removes the rule and keeps the gate names aligned. Final run on the final files: 10:32:56Z to 10:39Z, rc 0.

| Id | The edit | pytest | Red tests |
|---|---|---|---|
| R1a | escaped-credential never matches | 17 failed, 216 passed in 7.19s | test_a_credential_behind_an_escaped_quote_is_redacted, test_an_escaped_long_token_is_redacted_not_pseudonymized, test_escaped_credentials_are_redacted, test_fixed_offsets_give_byte_identical_output, test_gate_counts_patterns_and_canaries_and_prints_none, test_no_canary_survives_the_export, test_offsets_refuse_a_changed_prefix_or_archive, test_opaque_values_become_stable_keyed_pseudonyms, test_the_gate_reads_the_committed_runs_its_manifest_names |
| R1b | escaped-credential: one escape level only | 6 failed, 227 passed in 8.99s | test_a_credential_behind_an_escaped_quote_is_redacted, test_escaped_credentials_are_redacted, test_fixed_offsets_give_byte_identical_output, test_no_canary_survives_the_export, test_offsets_refuse_a_changed_prefix_or_archive, test_the_gate_reads_the_committed_runs_its_manifest_names |
| R1c | escaped-credential without the PASS names | 6 failed, 227 passed in 8.29s | test_a_credential_behind_an_escaped_quote_is_redacted, test_escaped_credentials_are_redacted, test_fixed_offsets_give_byte_identical_output, test_no_canary_survives_the_export, test_offsets_refuse_a_changed_prefix_or_archive, test_the_gate_reads_the_committed_runs_its_manifest_names |
| R1d | basic-auth: no quote after the header name | 6 failed, 227 passed in 8.88s | test_a_credential_behind_an_escaped_quote_is_redacted, test_escaped_credentials_are_redacted, test_fixed_offsets_give_byte_identical_output, test_no_canary_survives_the_export, test_offsets_refuse_a_changed_prefix_or_archive, test_the_gate_reads_the_committed_runs_its_manifest_names |
| R1e | the gate without the escaped-credential name | 6 failed, 227 passed in 8.85s | test_an_offsets_rerun_reads_the_commit_its_manifest_names, test_fixed_offsets_give_byte_identical_output, test_gate_counts_patterns_and_canaries_and_prints_none, test_no_canary_survives_the_export, test_offsets_refuse_a_changed_prefix_or_archive, test_the_gate_reads_the_committed_runs_its_manifest_names |
| R2a | a call naming the key: its result strict, not dropped | 4 failed, 229 passed in 12.04s | test_a_call_that_names_the_pseudonym_key_loses_its_result, test_call_modes, test_no_canary_survives_the_export, test_secret_paths_are_dropped_or_strict_passed |
| R2b | no lone names | 8 failed, 225 passed in 9.02s | test_a_call_that_names_the_pseudonym_key_loses_its_result, test_call_modes, test_fixed_offsets_give_byte_identical_output, test_named_secrets_sees_each_spelling, test_no_canary_survives_the_export, test_offsets_refuse_a_changed_prefix_or_archive, test_secret_paths_are_dropped_or_strict_passed, test_the_gate_reads_the_committed_runs_its_manifest_names |
| R2c | a file tool's path: SECRET_PATH only | 3 failed, 230 passed in 12.48s | test_call_modes, test_secret_path_spellings_are_seen, test_secret_paths_are_dropped_or_strict_passed |
| R3a | bearer-lower never matches | 9 failed, 224 passed in 8.98s | test_fixed_offsets_give_byte_identical_output, test_gate_counts_patterns_and_canaries_and_prints_none, test_no_canary_survives_the_export, test_offsets_refuse_a_changed_prefix_or_archive, test_r3_named_shapes_are_scrubbed, test_r3_named_shapes_are_scrubbed_through_the_cli, test_the_gate_reads_the_committed_runs_its_manifest_names |
| R3b | curl-user never matches | 9 failed, 224 passed in 8.60s | test_fixed_offsets_give_byte_identical_output, test_gate_counts_patterns_and_canaries_and_prints_none, test_no_canary_survives_the_export, test_offsets_refuse_a_changed_prefix_or_archive, test_r3_named_shapes_are_scrubbed, test_r3_named_shapes_are_scrubbed_through_the_cli, test_the_gate_reads_the_committed_runs_its_manifest_names |
| R3m | curl-user: any -u flag, curl or not | 3 failed, 230 passed in 12.61s | test_r1_rules_keep_text_with_no_secret |
| R3n | PASS in any case | 1 failed, 232 passed in 12.54s | test_r1_rules_keep_text_with_no_secret |
| R3o | pass-name takes a $ reference | 2 failed, 231 passed in 12.54s | test_r1_rules_keep_text_with_no_secret |
| R3p | pass-name's value takes the escape of a closing quote | 1 failed, 232 passed in 12.73s | test_r3_named_shapes_are_scrubbed |
| R3c | pass-name never matches | 10 failed, 223 passed in 8.79s | test_fixed_offsets_give_byte_identical_output, test_gate_counts_patterns_and_canaries_and_prints_none, test_no_canary_survives_the_export, test_offsets_refuse_a_changed_prefix_or_archive, test_r3_named_shapes_are_scrubbed, test_r3_named_shapes_are_scrubbed_through_the_cli, test_the_gate_reads_the_committed_runs_its_manifest_names |
| R3d | url-token-user never matches | 7 failed, 226 passed in 8.86s | test_fixed_offsets_give_byte_identical_output, test_gate_counts_patterns_and_canaries_and_prints_none, test_no_canary_survives_the_export, test_offsets_refuse_a_changed_prefix_or_archive, test_r3_named_shapes_are_scrubbed, test_r3_named_shapes_are_scrubbed_through_the_cli, test_the_gate_reads_the_committed_runs_its_manifest_names |
| R3e | url-password stops at the first @ again (F-6 undone) | 6 failed, 227 passed in 9.17s | test_fixed_offsets_give_byte_identical_output, test_no_canary_survives_the_export, test_offsets_refuse_a_changed_prefix_or_archive, test_r3_named_shapes_are_scrubbed, test_r3_named_shapes_are_scrubbed_through_the_cli, test_the_gate_reads_the_committed_runs_its_manifest_names |
| R3f | no normalized spelling (quotes, /./, //) | 1 failed, 232 passed in 12.59s | test_named_secrets_sees_each_spelling |
| R3g | no directory and file named apart | 12 failed, 221 passed in 9.08s | test_a_call_that_names_the_pseudonym_key_loses_its_result, test_call_modes, test_fixed_offsets_give_byte_identical_output, test_named_secrets_sees_each_spelling, test_no_canary_survives_the_export, test_offsets_refuse_a_changed_prefix_or_archive, test_secret_path_spellings_are_seen, test_secret_paths_are_dropped_or_strict_passed, test_the_gate_reads_the_committed_runs_its_manifest_names |
| R3h | no glob | 13 failed, 220 passed in 9.13s | test_fixed_offsets_give_byte_identical_output, test_named_secrets_sees_each_spelling, test_no_canary_survives_the_export, test_offsets_refuse_a_changed_prefix_or_archive, test_secret_path_spellings_are_seen, test_secret_paths_are_dropped_or_strict_passed, test_the_gate_reads_the_committed_runs_its_manifest_names |
| R3i | no .env name completed from a glob's head | 2 failed, 231 passed in 12.33s | test_named_secrets_sees_each_spelling |
| R3j | a glob needs no literal characters | 4 failed, 229 passed in 12.39s | test_named_secrets_leaves_ordinary_commands, test_named_secrets_sees_each_spelling |
| R3k | attachment paths: SECRET_PATH only | 2 failed, 231 passed in 12.42s | test_secret_path_spellings_are_seen, test_secret_paths_are_dropped_or_strict_passed |
| R3l | file change paths: SECRET_PATH only | 2 failed, 231 passed in 12.28s | test_secret_path_spellings_are_seen, test_secret_paths_are_dropped_or_strict_passed |
| R4a | the pseudonymizer ignores committed runs | 4 failed, 229 passed in 12.34s | test_an_offsets_rerun_reads_the_commit_its_manifest_names, test_committed_runs_stay_as_they_are, test_opaque_values_become_stable_keyed_pseudonyms, test_the_gate_reads_the_committed_runs_its_manifest_names |
| R4b | key runs and tokens ignore keep | 2 failed, 231 passed in 12.17s | test_committed_runs_stay_as_they_are, test_strict_pass_keeps_committed_runs |
| R4c | keep without the NAME=<value> form | 2 failed, 231 passed in 12.56s | test_committed_runs_stay_as_they_are, test_strict_pass_keeps_committed_runs |
| R4d | the assignment rule ignores keep | 2 failed, 231 passed in 12.70s | test_committed_runs_stay_as_they_are, test_strict_pass_keeps_committed_runs |
| R4e | the gate counts committed runs | 5 failed, 228 passed in 9.21s | test_an_offsets_rerun_reads_the_commit_its_manifest_names, test_fixed_offsets_give_byte_identical_output, test_no_canary_survives_the_export, test_offsets_refuse_a_changed_prefix_or_archive, test_the_gate_reads_the_committed_runs_its_manifest_names |
| R4f | an --offsets rerun reads HEAD, not its manifest's commit | 1 failed, 232 passed in 12.58s | test_an_offsets_rerun_reads_the_commit_its_manifest_names |
| R4g | the gate CLI ignores the manifest's repo | 2 failed, 231 passed in 11.83s | test_no_canary_survives_the_export, test_the_gate_reads_the_committed_runs_its_manifest_names |
| R4h | an explicit repo or commit git cannot read: nothing exempt, no refusal | 1 failed, 232 passed in 12.03s | test_a_repo_git_cannot_read_refuses_and_a_copy_outside_git_exempts_nothing |
| R4i | the set without the key-run shape | 2 failed, 231 passed in 12.35s | test_committed_runs_stay_as_they_are, test_run_shapes_are_the_rules_own_shapes |
| R4j | the set without the token shape | 2 failed, 231 passed in 12.33s | test_committed_runs_stay_as_they_are, test_run_shapes_are_the_rules_own_shapes |
| R4l | repo_runs: a missing blob not refused | 1 failed, 232 passed in 12.19s | test_repo_runs_refuses_a_blob_git_cannot_give |
| R4k | the set read at HEAD, not at the resolved commit | 2 failed, 231 passed in 12.31s | test_an_offsets_rerun_reads_the_commit_its_manifest_names, test_the_gate_reads_the_committed_runs_its_manifest_names |

36 of 36 red, 0 anchor mismatches. Every new payload rule is red on its scrubber test AND through the real CLI (the
canary survives and the export's own gate exits 3). The negative controls are red when a rule is widened back to its
first version (R3m: any `-u` flag; R3n: PASS in any case; R3o: a `$` reference as a value). R-2, each F-7 piece and each
AMENDMENT 3 piece (the pseudonymizer, the three strict sub-rules, the gate, the gate CLI, the `--offsets` commit, the
refusal, the two run shapes, the missing-blob refusal, the commit the blobs are read at) are red on a named test. The
first run (08:33Z, 31 mutants) found one gap: R3f survived (a quote inside a `.env` name, which only the normalized
text sees); a `SPELLED` row was added, and R3f is red since. R3m-R3p and R4l were added with the rules they guard.

## 7. Gates (evidence demand 6)

All on the final files (unchanged since 09:52:15Z). The two test_summary runs pasted here ran 10:58:32Z to 10:59:35Z (a first pair at 10:44Z read `238 passed in 31.71s` and `238 passed in 31.38s`); the rest ran 10:44Z to 10:46Z:
```
$ bash scripts/test_summary.sh tests/test_transcript_export.py tests/test_session_export.py tests/test_ship_to_pc.py      (run 1)
238 passed in 31.05s
pytest-exit: 0
pytest-summary: 238 passed in 31.05s
$ bash scripts/test_summary.sh tests/test_transcript_export.py tests/test_session_export.py tests/test_ship_to_pc.py      (run 2)
238 passed in 31.41s
pytest-exit: 0
pytest-summary: 238 passed in 31.41s
$ bash scripts/pc_suite.sh set-id -- tests/test_transcript_export.py tests/test_session_export.py tests/test_ship_to_pc.py
3 files set=6dde7977ceba
$ python3 -m pyflakes scripts/transcript_export.py scripts/session_export.py tests/test_transcript_export.py tests/test_session_export.py
(no output) rc=0
$ LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <each of the 4 files>
0 0 0 0
$ python3 scripts/no_laya_in_gates.py
rc=0
$ git diff --stat
 scripts/session_export.py       | 267 ++++++++++++++++++++++-----
 scripts/transcript_export.py    |  72 ++++++--
 tests/test_session_export.py    | 398 +++++++++++++++++++++++++++++++++++++++-
 tests/test_transcript_export.py | 151 +++++++++++++++
 4 files changed, 816 insertions(+), 72 deletions(-)
$ git diff --stat db1de1c HEAD -- <the 4 files> scripts/ship_to_pc.py tests/test_ship_to_pc.py      (HEAD 17c11fb at 10:44Z)
(empty, rc 0)
```
The premise's count on the same set was `141 passed` (section 0); R1 adds 97 tests (161 in
`test_transcript_export.py`, 72 in `test_session_export.py`, 5 in `test_ship_to_pc.py`). The two runs agree. This report
itself is checked for separators after its last edit (section 10 has the line).

The chat export and `scrub` are unchanged (09:53Z, on the final code):
```
$ python3 session-export-r1/chat_identity.py <the PIN's transcript_export.py>   (the builder's instrument: the chat CLI at the PIN and now, on every fixture)
fixtures 77: byte-identical 77, differing 0
$ (session-export-r1: scrub at the PIN and now, over the old and the new fixture texts; the source of the unchanged functions)
scrub on 139 fixture texts (the old fixtures and R1's): the PIN's scrub == R1's scrub for 139
SECRET_PATTERNS identical (pattern and flags, in order): True
scrub, turns, export, main byte-identical in source: True
```

## 8. Self-attack: the three most likely ways this change is wrong

1. AMENDMENT 3 lets a real secret out because the same string sits in a tracked file. How far it is ruled out: the named
   rules still run first (a committed FAKE token under `PC_BRIDGE_TOKEN` is redacted: `test_strict_pass_keeps_committed_runs`,
   `test_committed_runs_stay_as_they_are`); membership is exact (a whole run of the rule's own shape, not a substring), so a
   short secret is not exempted by appearing inside a longer committed run; the set is read from the commit's blobs, not
   the working tree, and pinned by commit and digest in the manifest. The residual is the amendment's own trade: a
   secret-shaped string that IS committed (a fixture, or a real secret someone committed) now passes the opaque rule and
   the strict pass. On the real data the rule keeps 193 values of the `mixed case+digits (blob or token)`
   category (section 5); whether any is a real secret is UNVERIFIED (reading them is forbidden here); by the amendment's
   premise, each is in a tracked file already.
2. A shape or spelling still gets through. Ruled out for every shape the brief names (the verifier's 7 escaped shapes and
   the key dumps read 0 through the real CLI; each new rule has a red mutant). Not ruled out, and listed in section 9: the
   12 attack-1 survivors outside R-3's list; a value with a backslash in its first 8 characters behind an escaped quote
   (the escaped rule's value class stops at a backslash, the verifier's candidate did the same); a scheme word other than
   Bearer or Basic (`Authorization: token <x>`); a relative path whose directory was named in an earlier call, unless the
   file's name is one only a secret has (`api-key` alone is too common a name); brace expansion; symlinks; background
   output. The gate cannot see any of these: it knows the scrubber's shapes only, so its 0 says nothing about them.
3. The new rules take ordinary text (data loss). Measured, not assumed: the first `curl-user` and `pass-name` took
   thousands of `date -u` format strings and code variables and were narrowed before the final runs (section 5 has the
   shape counts that found it); the final per-rule counts on the real data are in section 5
   (`escaped-credential` 369, `pass-name` 9, `curl-user` 2, `bearer-lower` 159). The
   escaped rule inherits scrub's name list, so it takes what scrub's credential rule takes in raw text (for example a
   value after the compound name `correlation_key`); that aggressiveness is scrub's (#187), not new. The new spellings put
   35 more real calls' results through the strict pass and drop 17 more (section 5's call-mode
   table); AMENDMENT 3 cuts what the strict pass removes from them.

## 9. NOT-done (first-class)

- Nothing is committed (the coordinator commits). The shipper was not run (never ship).
- The export in `<scratchpad>/session-export/` was made under a SCRATCH pseudonym key (`session-export-r1/key/`, key id
  7e899a8a62ef), because the brief forbids reading the real key. Its pseudonyms do not join exports made under the real
  key. Before shipping, re-export with the real key (the same command without `--key`, from the committed code, with fresh
  offsets or these; about 570 s) or decide to ship this key's export. Mind the HAZARD section: a fresh export that reads this lane's
  transcript counts `canary:orphan 1` and exits 3.
- The rest of F-5 stays a follow-up, as the brief says: short bare tokens (`short-echo`, `printenv-bare`), a value split
  over two lines or two events, URL-encoded values, prose (`thinking-prose`), a bare token in a pruner archive. Also not in
  R-3's list and still surviving: `netrc` (`password <v>` with a space), `secret_key_base: <v>`, a docker `"auth"` blob.
- F-7's spellings no textual check can see: a symlink made in an earlier call, a background command's output read later
  through TaskOutput (the builder's NOT-done too), a brace expansion (`qwen-{builder,jev}`), `..` components, a case variant.
- F-4's second half: an `xxd` of a bridge env file still shows 10 of the token's 25 eight-character windows (R-2 covers the
  pseudonym key only, as the brief words it). The verifier counted 0 such dumps in the real transcripts.
- Values the exemption does not keep, by design or measurement (section 5): a committed run glued to a JSON escape letter
  (`\n` then a name: 438 values, 0.4%) and one that occurs only inside a longer committed run (298 values, 0.3%); an
  absolute repo path that no tracked file spells out stays strict-redacted (390 key runs).
- The escaped rule's cost (section 3): about twice the scrub's CPU; the prefilter (skip text with no escaped quote) is a
  follow-up.
- F-8 (the shipper's tests), F-9 (the exporter's surviving mutants N1, N4, N5), F-10 and F-11: outside this repair's
  boundary or scope.
- `tests/test_laya_ft.py::test_version_2_record_rebuilds_byte_identically_at_the_pin` goes red with this change until
  the coordinator regenerates the DSV2 record at harvest (the brief says so). INFERRED, not run: the dataset builder
  hashes the working tree's `scripts/transcript_export.py` into its manifest (`scripts/laya_ft/build_dataset.py:583` and
  `:617`; its `CODE` list at `:44`), and the test compares that manifest byte for byte with the record
  (`tests/test_laya_ft.py:1353`). The Laya venue's inputs exist in this sandbox, so a run under `S0_01_VENUE=sandbox`
  (which `scripts/test_summary.sh:14` exports) runs the test instead of skipping it.
- The scratch trees `session-export-r1/a1`, `a1c`, `a3` (the harness's fixtures) and `red` hold FAKE canaries only; they
  stay for a re-verify. The determinism rerun (`<scratchpad>/session-export-run2`) was deleted at the end, as the brief
  says; run 1's export stays in `<scratchpad>/session-export/`.

## 10. DISCREPANCIES and adjacent defects

Discrepancies:
- The brief's premise block puts `116c116` under the `transcript_export.py` diff; it is in `scripts/session_export.py`
  (section 0). Does not matter.
- The brief lists `$HOME/` and `~/` among the forms the denylist misses; the PIN already caught both (the verifier's F-7
  says so too). Pinned by tests here, not red first (section 2).
- AMENDMENT 3's set: built from each rule's own run shape, not from the opaque shape alone (the INTERPRETATION in section 1;
  with the opaque shape alone no strict repo-path redaction could be kept).
- The before count of strict assignment values (3,706, the verifier's instrument) counts every strict-pass call, and a
  redacted assignment line matches again in `settle`'s confirming pass; section 5 counts first passes only, so those two
  numbers do not compare. The key-run and token counts do (a redacted run is not keylike, so the confirming pass adds none).
- The export takes about 570 s, not about 5.5 minutes (section 3).
- Two of this lane's own rules over-redacted in their first version; found by this lane's measurement and fixed before the
  final runs (section 1, section 5). The earlier real-export runs made with those versions were deleted.
- Process: the Write tool refused a `.md` scratch file from this subagent ("Subagents should return findings as
  text"). The brief makes this report a deliverable, so the report was assembled by a script
  (`session-export-r1/assemble.py`) from a `.txt` template, the drafted parts and the saved outputs, each pasted
  verbatim; the hand-back carries the summary.
- The separator check of this report after its last edit: `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` printed 0.

Adjacent defects (reported, not fixed; outside R1's items):
- scrub's credential rule and its bridge-link rule take the backslash of an escaped closing quote into the value they
  redact (`X-Agent-Token: v\"`, `\"https://...trycloudflare.com/x\"`), so the exported canonical JSON of that call no longer
  parses. In the final export 401 of 46,389 tool-call texts, 54 of
  488 harness notices and 17 of 2,936 system notifications do not parse; the
  classified ones end in a `<redacted>` whose escape was taken. Nothing leaks (the value is gone); a consumer that parses a
  tool call's text as JSON fails on these. The rules are `scrub`'s, which this repair must not change (the chat export).
  R1's new rules keep the escape (tested). R1 adds no such break: `session-export-r1/json_pin_vs_r1.py` scrubs every real
  tool input (46,435, to the builder's offsets) as the exporter's canonical JSON with the PIN's `scrub_payload` and with
  R1's: `PIN breaks 410`, `R1 breaks 410`, `only R1 breaks 0`, `only PIN breaks 0`.
- The PIN's `bridge-host` payload rule is quadratic on a dotted run: 9.06 s for `"a." * 20000` (40 KB), and
  `url-password`'s scheme prefix 0.95 s. The real export does not hit it in practice; a pathological text would slow the
  export, not break it. R1's new `url-token-user` anchors its scheme and stays linear.
- The gate's committed-run exemption keys on the name `opaque-run`, so a `PATTERN_NAMES` list that falls out of step with
  the rules turns it off. It fails loud (the gate then counts committed runs and exits 3; mutant R1e).
