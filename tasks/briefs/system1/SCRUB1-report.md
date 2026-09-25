# SCRUB1 report (task #280, AF-AP-224)

Lane: code-implementer (sandbox, Opus 5.5). Started 2026-09-25T18:17:33Z (bucket 18:1xZ). Written incrementally.
Tree at start: HEAD = origin = c3a00b7 (the dispatch message named origin 9db6ac6; c3a00b7 is one commit on top of it,
a push_clean transcript sync that changed only `transcripts/sandbox/chat-2026-09-25.md`). Brief PIN: 03ca747.

## STATUS

DONE (tests green, not committed): the four rules take keys glued after `_` and `__`; a value gate stands before every digest write; the Laya dataset bytes are unchanged and its manifest's code hash regenerated. Gate: `pytest-summary: 723 passed, 1 skipped` twice (15 files set=271f9e77620b) and `pytest-summary: 74 passed` twice (2 files set=daac8d7d6355); mutation 23 of 24 killed (M16 survives by design). Open: A1 (right-side glue) and push_clean's silent refusal (section 8).

## 1. PREMISE, re-measured (18:2xZ)

| # | Premise line | Measured now | Verdict |
|---|---|---|---|
| P1 | `sed -n 74,77p scripts/transcript_export.py`: the four rules start with `\b` | identical four lines; `git diff 03ca747 HEAD -- scripts/transcript_export.py tests/test_transcript_export.py` empty; last change ce2e1c5 | holds |
| P2 | fake keys (token_hex tails): standalone, `=`, quote scrubbed; `__`, letter, `_` not | same for sk, ghp, xoxb; digit-glued also not scrubbed (a context the premise did not list). AIza after `__` reads scrubbed=True: `mcp__srv__` + AIza + 32 hex is a 46-character run, so the opaque rule takes it, not the AIza rule | holds |
| P3 | known_values_check over `transcripts/sandbox/`: 14 forms, 18 files, 1 HIT (api.env:TYPESAFE_BASE_URL host whole=1), every secret whole=0 windows=0 | `known-values: 14 secret forms, 18 files, 3467168 bytes, 1 HIT(S)`, rc 3; the one hit is the same host form; every other form whole=0, windows 0 | holds (bytes grew from 3407965: c3a00b7 appended to chat-2026-09-25.md) |
| P4 | importers outside tests: 14 files | the same 14 plus `.claude/hooks/edit-snapshot.py`, which names transcript_export only in its AF-AP-224 screen comment (8d7f99d), no import | holds (one text mention added) |
| P5 | gitnexus `impact scrub --direction upstream`: risk UNKNOWN, direct 0 | ambiguous (2 candidates); disambiguated with `--uid Function:scripts/transcript_export.py:scrub`: **risk HIGH, 19 impacted**, depth 1: openjev_j2 `_scrubbed`, chat_find `hit_row`, hiccup_scan `_jev_cell`/`_plain`/`excerpt`, transcript_export `export`. Index 12 commits behind HEAD. It does not see `scrub_payload`/`scrub_strict` (session_export) or the path-loaded importers (laya_ft, hermes-session-export, qwen_matrix) | DISCREPANCY, not contract-breaking: the brief already makes every importer's tests part of the gate (item 4). **Flagged: HIGH risk** |
| P6 | the Laya record manifest pins `code[scripts/transcript_export.py]` = af9d73eab7af665b = sha256sum prefix | same, both `af9d73eab7af665b` | holds |
| P7 | `bash scripts/test_summary.sh tests/test_transcript_export.py tests/test_session_export.py`: 233 passed, set e8f27bcb91e7 | `pytest-summary: 233 passed in 13.13s`, `2 files set=e8f27bcb91e7` | holds |
| P8 | S0-04 echoes at check_compression.py:82 and capture_leg.py:46 | same two lines | holds (not touched) |
| P9 | free disk 1.8G | 2.0G | holds |

Verdict: the premise holds. No CONTRACT-INVALID.

## 2. Contract item 1: which left anchor, by measurement (18:3xZ)

Instrument: `<scratch>/scrub1/measure.py` (not committed; `<scratch>` = `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad`).
It builds each candidate from the PIN's own four rule bodies (it asserts the rules still start and end with `\b`), runs
scrub's first three rules (private key, credential, Bearer) first as scrub does, and counts every candidate match at a
position where the PIN's `\b` refuses. Each match is classed "known secret" (the premise's five sources read in process
with `known_values_check`'s helpers, TYPESAFE_BASE_URL skipped: the match holds a value whole or one of its 8-byte
windows) or "not known"; and "newly redacted" (the matched text survives the PIN's full scrub of the same text) or
"already hidden" (the PIN's opaque rule took the run anyway). It prints counts and masked shapes only.

```
$ python3 <scratch>/scrub1/measure.py <scratch>/scrub1/m-digests.json transcripts/sandbox/*.md
done files=18 texts=18 bytes=3454412 prefix=10 interesting=0 seconds=0.2
$ python3 <scratch>/scrub1/measure.py <scratch>/scrub1/m-root2.json /root/.claude/projects/-home-user-agent-factory/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl
done files=1 texts=561 bytes=775110 prefix=22 interesting=0 seconds=0.1
$ find /root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/subagents -name '*.jsonl' -print0 | sort -z | xargs -0 python3 <scratch>/scrub1/measure.py <scratch>/scrub1/m-sub.json
done files=334 texts=188419 bytes=113167946 prefix=4244 interesting=1945 seconds=28.8
$ python3 <scratch>/scrub1/measure.py <scratch>/scrub1/m-main.json /root/.claude/projects/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17.jsonl
done files=1 texts=1878733 bytes=241562338 prefix=11260 interesting=8003 seconds=37.5
```

Corpora: the 18 committed digests (3,467,168 bytes); this session's transcripts: the main JSONL (733,587,264 bytes,
137,706 lines), 334 subagent and workflow-agent JSONL files (521,606,186 bytes, 126,440 lines), the second project
root's JSONL (3,074,681 bytes, 519 lines). A JSONL text = every string of every record (decoded).

Candidates (the rule body and the trailing `\b` unchanged; only the left anchor differs):
PIN `\b` · **S1** `(?<![A-Za-z0-9])` · S1e `(?:(?<![A-Za-z0-9])|(?<=\\[nrt]))` (S1, plus a key after a JSON escape) ·
S2 no left anchor (a key glued to a letter or digit matches too).

**The table: new redactions at positions the PIN refuses, digests + transcripts (the digests gave 0 in every cell)**

| Set | Rule | Known secret | Not known, newly redacted | Not known, already hidden (opaque) |
|---|---|---|---|---|
| S1 | sk | 0 | 2 (glue `_`: len 15, tail U L D -; glue `__`: len 27, tail U only) | 0 |
| S1 | gh, AIza, xox | 0 | 0 | 0 |
| S1e | all four | 0 | the same 2 as S1 (decoded text has no JSON escape) | 0 |
| S2 | sk | 0 | 17,691 | 6 |
| S2 | AIza | 0 | 1 | 1 |
| S2 | gh, xox | 0 | 0 | 0 |

S2's letter-glued `sk` matches by the word they end (the word is printed only when it is on a fixed list of ordinary
words): task 17,258 (the `<task-notification>` tag; `grep -c task-notification` on the main JSONL: 4,669 lines),
desk 257, flask 123, risk 17, disk 12, ask 9, tsk 4, whisk 4, mask 2, not on the list 3 (plus already hidden: desk 2,
risk 1, task 1, not on the list 2). Tails: 17,508 of the new ones hold lower case only. The 5 not on the list were
probed for masked context (`<scratch>/scrub1/probe_other.py`, `probe_fixture.py`): each sits in a tool result, runs of
23 to 59 characters, no known secret; they are short key-shaped strings of unverified origin (A6, section 9). S2's two AIza matches sit inside base64 runs of 3,064 and 76,780 characters (with `+` and `/`): random
text, not keys. Digit glue: 0 instances in every corpus.

Two probes beside the table:
- **JSON-escape context** (the raw JSONL line, which is what session_export's canonical JSON shows the rules): keys
  right after `\n`, `\r` or `\t`: `sk` known secret 8 (each inside a 40+ character run: the opaque rule takes it today,
  under every set), `sk` not known 1 (len 23, tail lower case only, visible), `gh` not known 1 (`ghp_`, len 26, tail
  U and D only, visible). PIN and S1 miss these 10; S1e matches them.
- **Right side** (the trailing `\b`, not in the contract): 0 key-shaped matches refused by the trailing `\b` in any
  corpus. The class exists with fake keys (section 9).

**Decision: S1, `(?<![A-Za-z0-9])`, on all four rules; the trailing `\b` unchanged.** No known secret is left under S1:
no known secret sits glued at all in decoded text, and the one that sits behind a JSON escape (8 times) is hidden by the
opaque rule under every set. S1 adds 0 ordinary-word redactions and takes the 2 underscore-glued key shapes the
transcripts hold. S2 would take no more known secrets (there are none) and add 17,692 redactions: 17,686 ordinary
words, the 2 that S1 takes too, 3 short key-shaped strings of unverified origin (A6) and 1 random base64 run. S1e ties S1 on both criteria in decoded text; its extra reach (8 known already hidden, 2 visible
placeholder-shaped strings) is session_export's canonical-JSON context, so it is left to the coordinator as an option
(section 9), not taken: the simplest rule that meets the criteria, and the brief's named anchor.

The Laya records under each set (contract item 4's re-scrub, run here on the PIN build's `state` fields): 0 of 6,196
change under PIN (control), S1, S1e and S2 (section 6).

## 3. What changed (18:5xZ)

`scripts/transcript_export.py` (the only code file):
- The four provider rules: the leading `\b` became `(?<![A-Za-z0-9])`; bodies and the trailing `\b` unchanged; the
  comment above them says why and cites the measurement.
- The value gate: `KNOWN_VALUE_SOURCES` (the five sources, named once: `.pc-bridge.env` beside the repo root,
  `/root/.codiv/api.env` with `TYPESAFE_BASE_URL` skipped, `/root/.config/session-export/pseudonym.key`, `GH_TOKEN`,
  `GITHUB_TOKEN`), `known_values()` (loads `known_values_check.py` by path at gate time, reuses its `_env_values`,
  `_forms`, `_raw_forms`, `_windows`, `MIN_VALUE`; a missing source is skipped with one stderr line; a present source that
  cannot be read refuses), `value_hits()` (known_values_check's count and its line format), `KnownValueRefusal`.
- `export()` builds every day's bytes first, runs the gate on exactly those bytes, and only then creates the out
  directory and writes (bytes, not text: the same UTF-8 the text-mode write produced, measured identical below).
- `main()` exits 4 on a refusal, one stderr line per hit: `transcript_export: REFUSED, nothing written: <source>:<name>
  <form> whole=N windows=H/T`. The docstring names the gate and exit 4.
- Every other mode: transcript_export.py has one writing path (`export()`, reached only through `main()`); the gate
  covers it for any `--out`. `scrub_payload`/`scrub_strict` write nothing; session_export.py is its own writer (outside
  this boundary).

`tests/test_transcript_export.py`: 13 new tests after the existing 161. It imports `os`, `re`, and `token_bytes` and
`token_hex` from `secrets` (an existing loop variable named `secrets` would shadow the module; pyflakes flags it). Every
fake is built at run time. `docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json`: the one code-hash line (section 6).

Byte identity on real data: the new exporter and the PIN's exporter over this session's main transcript write 18
digests, identical byte for byte (`diff -rq` empty); the gate passed with no stderr (all five sources present, 0 hits);
17 of the 18 equal the committed digests (chat-2026-09-25.md grew since the last sync). This run predates the final
comment edit; section 5 repeats it on the final bytes.
```
pin: 5.530 s wall   new: 6.125 s wall   (both rc 0; 733,587,264-byte transcript)
IDENTICAL: every digest byte-for-byte
```

## 4. Tests, red first on the PIN, then mutation

Red run: the new test file against the PIN's exporter (`git show 03ca747:scripts/transcript_export.py`, sha
af9d73eab7af665b) in `<scratch>/scrub1/redtree`: `9 failed, 164 passed in 2.44s`. Why each fails there:

| Test | On the PIN | Reason |
|---|---|---|
| every_provider_rule_takes_its_key_in_every_context | FAILED | `[('AIza', 'after __'), ...] == []`: the glued contexts miss (the exact reason) |
| glued_keys_never_reach_disk | FAILED | key prefixes whose tails reached the digest (the exact reason) |
| value_gate_refuses / counts_a_cut_copy / reads_a_variable_and_a_raw_key_file / hostname / fails_closed / skips_a_missing_source | FAILED | `AttributeError: no KnownValueRefusal` or `TypeError: unexpected keyword 'sources'`: the gate does not exist there (a missing API, not an assertion; the mutation pass below gives each an exact-reason kill) |
| cli_refuses_with_exit_4 | FAILED | `assert 0 == 4`: the PIN wrote the fake value to disk and exited 0 (the exact reason) |
| context_test_reds_on_the_pin_rules / ordinary_words_are_not_redacted / ordinary_words_red_on_rules_that_take_a_letter | passed | controls by design, green on both: the first two build the PIN's and a no-anchor rule set in the test and assert they fail exactly where expected; the ordinary-word test guards against an over-wide anchor |

The 13th test (`reads_the_scrubbed_text`) was added after the red run, from the mutation design (M21).

Mutation pass (`<scratch>/scrub1/mutate.py`): the unmutated control first, then 24 mutants of the new code; KILLED only
when a test FAILED (AF-AP-223), an anchor must occur exactly once or the mutant is INVALID.
```
CONTROL (unmutated): rc=0 174 passed in 2.59s
M1 gate disabled KILLED 7 failed · M2 out dir made before the gate KILLED 3 · M3 windows ignored KILLED 4 ·
M4 whole count ignored KILLED 4 · M5 skip list ignored KILLED 1 · M6 a missing source refuses KILLED 26 ·
M7 an unreadable source is skipped KILLED 1 · M8 main exits 0 on a refusal KILLED 1 · M9 the refusal line carries the
value KILLED 5 · M10-M13 each rule's anchor back to \b KILLED 2 each · M14 sk anchor dropped KILLED 1 · M15 gh anchor
dropped KILLED 1 · M16 anchor lets digits glue (sk) SURVIVED · M17 GH_TOKEN not a source KILLED 1 · M18
TYPESAFE_BASE_URL not skipped KILLED 1 · M19 no skip line KILLED 1 · M20 a short variable counts KILLED 1 · M21 the gate
reads the raw text KILLED 1 · M22 gate per file inside the write loop KILLED 3 · M23 main does not catch the refusal
KILLED 1 · M24 raw-file source read as empty KILLED 1
TOTAL {'KILLED': 23, 'SURVIVED': 1, 'INVALID': 0}
```
Re-run on the final bytes: `CONTROL (unmutated): rc=0 174 passed in 2.48s`, `TOTAL {'KILLED': 23, 'SURVIVED': 1,
'INVALID': 0}`, M16 the survivor again.

M16 survives by design, not by a gap in a gate: whether a digit before the prefix separates is not decided by any data
(0 digit-glued instances in every corpus, section 2), and pinning it would mean a test that asserts a key-shaped string
survives. Kept `(?<![A-Za-z0-9])`: the registry row's fix shape and the brief's named anchor. `(?<![A-Za-z])` is the
coordinator's option at no measured cost (DISCREPANCIES).

## 5. Contract item 2: the value gate's cost (19:5xZ, final bytes)

On the 18 committed digests (in process: `known_values()` then `value_hits()` over the files' bytes, three runs):
```
committed digests 18 bytes 3468131
run 1: load 3.9 ms, count 689.0 ms, forms 12, windows 327, hits 0
run 2: load 0.6 ms, count 683.4 ms, forms 12, windows 327, hits 0
run 3: load 0.5 ms, count 690.1 ms, forms 12, windows 327, hits 0
```
About 0.69 s per export, linear in the digests' size. 12 forms: the premise's 14 minus TYPESAFE_BASE_URL's value and
host. Hits 0: the premise's one hit (that host) no longer blocks. The whole export of this session's 733,587,264-byte
transcript, one run each: PIN 5.059 s, new 6.069 s wall, rc 0, 0 stderr lines, 18 files, `IDENTICAL: every digest
byte-for-byte` (`diff -rq` of the two out directories).

## 6. Contract item 4: the Laya lock holds; the dataset bytes did not change

- Control: the unchanged code's build at 434b727 reproduces the record (`dataset.jsonl` sha256 99070c33...,
  `PIN-code build manifest == committed record (control)`).
- Re-scrub of every stored record's `state` (the one field the builder scrubs: 1,652 strings and 4,544
  `{query, chunk}` dicts) with the final `scrub`: `records 6196, whose state changes under the final scrub: 0`.
  The same count under the PIN (control), S1e and S2: 0.
- Rebuild with the final code (K265's step, its report R10:
  `HF_HUB_OFFLINE=1 /root/venv-laya-probe/bin/python scripts/laya_ft/build_dataset.py --version 2 --commit 434b727dfd2b6daa5aa3cf4d638e706f5dfa59cb --out <scratch>/scrub1/v2final --model-dir /root/hf-laya-probe/hub/models--convaiinnovations--laya/snapshots/1c5edc17a7acd8701df6fc341c0d179f1c62c982/typed-decisions`):
  `dataset.jsonl IDENTICAL to the PIN-code build` (sha256 99070c33830832ca11e64226eddac1934ccd300c73b4d5d8d8c7bf5a36271f9d,
  12,800,855 bytes), `summary.json IDENTICAL`; the manifest differs in one line only.
- Regenerated: `<scratch>/scrub1/v2final/manifest.json` copied over the record's `dataset-manifest.json`; `git diff`:
  `-  "scripts/transcript_export.py": "af9d73eab7af665b..."` / `+  "scripts/transcript_export.py": "2136062e0af69815..."`
  (the full new value is the sha256 of the final file, 2136062e0af69815cb793809c76dd0c7ed49348ff89397fa79eacbbdc75e2e40).
- The venue test `test_version_2_record_rebuilds_byte_identically_at_the_pin` (it rebuilds twice, compares the
  manifest, rebuilds the labels and the summary and compares them to the record) passed in both final set-B runs.
- No other committed file pins the old hash (`af9d73eab7af665b` appears only in briefs, reports and a digest's text).

## 7. Gates (pasted)

Final bytes: `scripts/transcript_export.py` 2136062e0af69815, `tests/test_transcript_export.py` 2067ae7e642fb919,
the manifest dbfba4b69ffb9ee0 (sha256 prefixes).
```
$ bash scripts/test_summary.sh tests/test_transcript_export.py --basetemp=<scratch>/...     1 files set=73755bb9fbbf
pytest-summary: 174 passed in 2.76s
pytest-summary: 174 passed in 2.53s
$ bash scripts/test_summary.sh <set A> -rs                                                  15 files set=271f9e77620b
pytest-summary: 723 passed, 1 skipped in 106.74s (0:01:46)
pytest-summary: 723 passed, 1 skipped in 106.83s (0:01:46)
$ bash scripts/test_summary.sh tests/test_laya_ft.py tests/test_laya_systemone_server.py   2 files set=daac8d7d6355
pytest-summary: 74 passed in 408.63s (0:06:48)
pytest-summary: 74 passed in 547.68s (0:09:07)
```
Set A = tests/test_transcript_export.py tests/test_session_export.py tests/test_chat_find.py tests/test_hiccup_scan.py
tests/test_jev_client.py tests/test_jev_context.py tests/test_jev_locate_echo.py tests/test_recorded_labels.py
tests/test_qwen_jev.py tests/test_known_values_check.py tests/test_edit_snapshot_ap_screen.py tests/test_ship_to_pc.py
tests/test_push_clean_lock.py harness-ports/tests/test_hermes_session_export.py harness-ports/tests/test_qwen_matrix.py.
The one skip: `tests/test_qwen_jev.py:37: LOUD SKIP` (the PC's qwen-jev venv only). Before the last comment edit, the
same 17 files ran once as one set: `17 files set=944777352f9c`, `pytest-summary: 797 passed, 1 skipped in 577.58s
(0:09:37)` (723 + 74 = 797). pyflakes rc 0 on both code files; `scripts/lint_delta.py --base HEAD` rc 0 with two
advisory tells (AP-1 on the environment read, which is the secret's home; AF-AP-224 on the test file's `PIN_RULES`,
the negative control's own input). `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]'` prints 0 for all four files written.
`scripts/report_lint.py` on this report (`--map TE=scripts/transcript_export.py --map PC=scripts/push_clean.sh --map
IL=docs/INCIDENT-LOG.md`): `report_lint: 7 refs — OK 7, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`.

## 8. The brief's question: what push_clean's sync does when the gate refuses (from the code; not edited)

- The sync runs only in `--no-delegates-live` mode, after the code push:
  `TRANSCRIPT_SYNC:-1` at `scripts/push_clean.sh:184`.
  `--lanes-live` runs its inner push with `TRANSCRIPT_SYNC=0` (`scripts/push_clean.sh:64`) and exits before the sync.
- `scripts/push_clean.sh:185` runs `transcript_export.py --out transcripts/sandbox >/dev/null 2>&1`: both streams are
  discarded, so the gate's REFUSED lines (the source's name and counts) are lost.
- Exit 4 fails that `if`; nothing was written, so nothing is staged; the `else` branch prints on stdout
  `transcript sync: nothing new (or export unavailable)` (`scripts/push_clean.sh:193`),
  the same line as a push with no new turns, and push_clean exits 0 (that echo is its last command).
- **So a refused sync is not visible as a refusal.** The code push has already succeeded; the committed digests stay
  at their last good state; the transcript only grows, so every later push refuses the same way and the digests stop
  updating in silence, until someone runs the exporter by hand and reads its stderr. The protection holds (nothing
  holding a known value is written or committed); the visibility does not. Possible fix, not made (outside the
  boundary): keep the exporter's stderr, or test for exit 4 and print a `REFUSED by the value gate` line on stderr.

## 9. DISCREPANCIES and adjacent findings

Discrepancies:
- D1. Origin: the dispatch named 9db6ac6; the tree started at c3a00b7 (a transcript sync on top of it), and origin moved
  on during the lane (cac6fe6, 5dd9af9 and later: other work, none on my four files). The brief's PIN 03ca747 holds the
  same `transcript_export.py` and test file as c3a00b7.
- D2. GitNexus: `impact scrub` is ambiguous; by uid, **risk HIGH, 19 impacted** (the premise read UNKNOWN, direct 0).
  The index is 12 commits behind and misses the path-loading importers. The consumer gate covers the importers.
- D3. The 17-file set ran once (577.58 s, near the tool's 600 s cap, before the final comment edit); the final bytes
  ran as two subsets, twice each. "Twice with the set id" holds per subset, not for the combined id.
- D4. Mutant M16 (a digit before the prefix counted as a separator) survives: the digit decision is a design choice with
  no measured cost either way (0 digit-glued instances). `(?<![A-Za-z])` is the coordinator's option.
- D5. "A hostname is not a secret" is implemented as a skip of `TYPESAFE_BASE_URL` by name (its value and its host),
  not as "no host form counts": `PC_BRIDGE_URL`'s host is the bridge link's secret part (known_values_check's own
  docstring) and still counts. If every host form should be ignored, the change is small; flagged, not made.
- D6. `GH_TOKEN` and `GITHUB_TOKEN` in this sandbox hold the same 14-character value, lower case and hyphens: not a
  GitHub token's shape. Counted whole (under 16 characters, so no windows), as the premise did.

Adjacent findings (not fixed):
- A1. **Right-side glue**, the same four rules' trailing `\b` (fake keys built at run time): a key followed by `_` → the
  `xox` rule stops at the last hyphen and the final segment reaches the output (`last 8 chars gone=False`); `gh`
  survives unless its whole run reaches the opaque rule; `sk`, `gh` and `AIza` followed by a non-ASCII letter (`é`)
  survive whole. 0 instances in every measured corpus. The contract defines "glued" as glued to a PRECEDING character,
  so this stays open; a fix (`(?![A-Za-z0-9])` or no right anchor) moves more bytes and needs another Laya check.
- A2. **JSON-escape context**: in canonical JSON (session_export writes tool inputs that way) a key after `\n`, `\r` or
  `\t` sits after a letter, so no provider rule takes it: 8 known-secret occurrences in this session's raw lines, all
  inside 40+ runs (the opaque rule takes them; session_export writes a keyed pseudonym), and 2 short placeholder-shaped
  strings visible. S1e takes them (section 2).
- A3. The comment `# long opaque tokens (32+ url-safe chars)` at `scripts/transcript_export.py:90` is stale: the rule
  below it is `{40,}`. Pre-existing.
- A4. AF-AP-204's tell (pre-existing): `main()` reads only the newest `*.jsonl` under `/root/.claude/projects/-home-user/`;
  this session also has a transcript under `-home-user-agent-factory` (3,074,681 bytes), which no digest reads.
- A5. The other outward writers of `scrub`'s output have no value gate: hiccup_scan's page, chat_find's excerpts,
  hermes-session-export on the PC, jev's requests, the Laya dataset; session_export has its own shape gate and canaries
  (its shipper's known-values step is backlog). Contract item 2 covers transcript_export.py only.
- A6. Five letter-glued `sk-` shapes in two J1-1 redactor lanes' tool results (agent-a1ae84 lines 207 and 217,
  agent-a2fe7f lines 165 and 255): 18 to 24 characters (the one sk-shaped known secret here is 49), not known secrets,
  not committed text, never typed in those lanes' commands, not current J1-1 fixtures; computed by the lanes' redactor
  probes (inferred fakes). S1 leaves the 3 outside a 40+ run visible in those transcripts' scrubbed exports.
- A7. The AF-AP-224 registry row (`docs/INCIDENT-LOG.md:753`) still reads OPEN and names the screen as firing on lines
  74-77: it now fires 0 times (`python3 scripts/ap_screen.py`: 4 hits on the PIN copy, 0 on the new file). The row and a
  sibling row for A1 are the coordinator's.

## 10. NOT done

- No git write: the four files are changed in the working tree for the coordinator to commit (`safe_commit.sh` with the
  paths of section 12).
- No PC bridge; no CI run read (nothing pushed).
- A1 and A2 not changed; the S0-04 detectors untouched; `scripts/push_clean.sh` untouched.
- The full `tests/` suite not run: the brief's consumer set only (17 files).
- No bug-echo and no registry edit for A1 (`docs/INCIDENT-LOG.md` is outside the boundary).

## 11. Self-attack: the three likeliest ways this is wrong

1. **The gate refuses the real sync on a false positive, and push_clean hides it.** Checked: the export of this
   session's transcript passes (rc 0, no stderr, 0 hits over 12 forms and 327 windows); the committed digests hold 0;
   the premise's one hit is skipped by name. Residual (inferred): a hex window of the pseudonym key matching a hash in a
   digest by chance, about 1e-8 per hex 8-gram; and the visibility gap of section 8 is real.
2. **The anchor moves bytes a consumer pins.** Checked: the Laya dataset rebuilds byte-identical and 0 of 6,196 stored
   records change; the 18 digests from this session's transcript equal the PIN exporter's; 797 consumer tests pass;
   over every string of this session's transcripts the new rules add 2 redactions. Residual: session_export's next real
   export changes at those 2 underscore-glued sites (the intended redaction).
3. **The gate crashes or is skipped through its loading or a source edge.** Checked: `known_values_check.py` is loaded
   only inside `known_values()`, so the path-loading importers never touch it (laya_ft, hermes-session-export and
   qwen_matrix tests pass); an unreadable source refuses (test, M7); a missing one is skipped with one line (test, M6,
   M19); a short variable is skipped (test, M20). Not tested: `known_values_check.py` absent (the load raises before
   any write: fail closed with a traceback and exit 1, not 4; read from the code).

## 12. Evidence tiers and files

- Verified here: the premise table; the measurement table and its probes; byte identity; the red run; the mutation
  pass; the gates; the gate cost; the Laya lock; the push_clean answer (read from the code).
- Inferred: A6's provenance; the false-positive rate; CI's behavior (a non-root runner reads the `/root` sources as
  missing, since `os.path.exists` under a 0700 parent is False: not run in CI).
- Assumed: `TYPESAFE_BASE_URL` is public (the brief says so); the `GH_TOKEN` value is a placeholder (its shape only).

Files changed (for the coordinator's commit):
- `scripts/transcript_export.py` (sha256 2136062e0af69815): docstring 12-15 and 19-21; `import importlib.util` 25; the
  four rules and their comment 80-87; the gate 230-293 (`KNOWN_VALUE_SOURCES`, `KnownValueRefusal`, `known_values`,
  `value_hits`); `export` 296-316; `main` 332-338.
- `tests/test_transcript_export.py` (2067ae7e642fb919): imports at 6, 8, 11; the SCRUB1 tests 665-862.
- `docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json` (dbfba4b69ffb9ee0): line 10 only.
- `tasks/briefs/system1/SCRUB1-report.md`: this report.
Scratch, not committed: `<scratch>/scrub1/` holds `measure.py`, `probe_other.py`, `probe_fixture.py`, `mutate.py` and
the `m-*.json` counts (48K; the builds, trees and logs are deleted). `measure.py` asserts it runs on the PIN's rules: to
rerun it, put `git show 03ca747:scripts/transcript_export.py` at `<scratch>/scrub1/pin/transcript_export.py` and load it
as `transcript_export` first, as `probe_fixture.py` does.
