# SCRUB1: the scrubber catches glued provider keys, and no digest is written with a known secret in it (AF-AP-224, task #280)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/system1/SCRUB1-report.md` (write it
incrementally from the start). PIN: 03ca747 (origin; `scripts/transcript_export.py` unchanged since long before it, measured
below). Evidence: the AF-AP-224 row in `docs/INCIDENT-LOG.md`; the scrubber corollary in skill `anti-hollow-green` (tactic 8).

## WHY

`transcript_export.scrub` is the one scrubber for text that leaves this machine or enters git: the transcript digests
committed at every push (`transcripts/sandbox/`), the session export, the hiccup page, the chat locator's excerpts, the Jev
calls and the Laya training data. Its four provider-key rules start with `\b`, so a key glued to a preceding `_`, letter or
digit passes whole unless the run reaches the 40-character opaque rule. Nothing has leaked (the value check below counts 0 for
every secret in the committed digests), but the shape list alone can never prove that: the scrubber corollary says a VALUE
check stands behind every export.

## CONTRACT

1. **The four rules match glued keys.** `sk-`, the `ghp_` family, `AIza` and `xox` keys match after `_` and `__` (anchor on
   `(?<![A-Za-z0-9])` or better). Decide whether a key glued to a letter or digit is matched too, by measurement: run each
   candidate rule set over the 18 committed digests and over this session's transcripts (in process), and report per rule
   the new redactions, split into "a known secret value" (checked in process, never printed) and "not a known secret"; for
   the second group print only a masked shape (the prefix, the length, the character classes), never the matched text.
   Choose the set with no known secret left and the fewest ordinary-word redactions; say why.
2. **A value gate before any write.** `transcript_export.py` counts known secret values in the scrubbed text before it writes
   any output file (the committed digests and every other mode it has), with the logic of `scripts/known_values_check.py`
   (reuse it by import; names and counts only). On a hit it writes nothing and exits non-zero, naming the secret's source
   name and the count. The sources are named once, in code; a missing source is skipped with one line. A hostname is not a
   secret: today's one hit is the host of `TYPESAFE_BASE_URL`, which must not block. Measure the gate's cost on the 18 digests.
3. **Tests**, with fake keys built at run time (`secrets.token_hex`): each rule in every context (standalone, after `=`, a
   quote, `_`, `__`, a letter and a digit if chosen, inside a URL, at a line start and end); ordinary words that must not be
   redacted (`task-…`, `risk-…`, `disk-…`, `skip-…`, `ghost_…`); the value gate refusing on a fixture source holding a fake
   value and passing without it, its output carrying names and counts only; a negative control proving each new test reds on
   the PIN's rules.
4. **The consumers stay green and the Laya lock holds.** Run the tests of every consumer (at least `test_transcript_export`,
   `test_session_export`, `test_chat_find`, the hiccup_scan, jev and laya_ft tests). The recorded dataset manifest
   (`docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json`) pins this file's sha256 as a code
   input: re-scrub every stored record with the new rules and count the records whose bytes change. If none change,
   regenerate the manifest's code hash the way K265 did (its report names the step) and prove the dataset bytes are
   identical. If any record changes, STOP and report the count: a data change is the coordinator's decision.

The S0-04 detectors with the same shape (`proofs/S0-04/check_compression.py:82`, `proofs/S0-04/tools/pc/capture_leg.py:46`)
are NOT touched: S0-04 is a minted, owner-signed proof, and a change re-mints it.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. The measurement table of item 1 and the gate's cost (item 2), each with its command.
3. `bash scripts/test_summary.sh` on your tests and the consumers' tests, twice, with the set id; pyflakes rc 0;
   `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0 for every file you write.
4. NOT-done and DISCREPANCIES.

## BOUNDARY

MODIFY: `scripts/transcript_export.py`, `tests/test_transcript_export.py` (or a new test file beside it), and the recorded
dataset manifest's code hash only under contract item 4. READ everything else, `scripts/push_clean.sh` included (its transcript
sync calls this file; do not edit it). Another lane (S1-L1-R1) is live in this tree on `.claude/hooks/system1-context.py`,
`.claude/hooks/system1-situations.json`, `tests/test_system1_context.py`, `scripts/install_session_hooks.py` and
`tests/test_session_hooks.py`: touch none of them.

## STANDING RULES

Secrets: never print, store or paste a secret value, a matched span that could be one, or a token from any env file; read
the known values in process only; test secrets are fake strings built at run time. Transcripts hold secrets: counts, ids and
masked shapes only. No git writes; no PC bridge; no outward-facing action. The disk is shared (2.0G free): scratch under
100 MB in `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/scrub1/`, deleted as you go; a short
`--basetemp` there with its parent created first. Test counts pasted from `scripts/test_summary.sh`; stamps from `date -u`.

## PREMISE — MEASURED at authoring (2026-09-25 18:1xZ)

```
$ sed -n "74,77p" scripts/transcript_export.py
    (re.compile(r"\bsk-[A-Za-z0-9_\-]{12,}\b"), "sk-<redacted>"),
    (re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b"), "gh<redacted>"),
    (re.compile(r"\bAIza[0-9A-Za-z_\-]{30,}\b"), "AIza<redacted>"),
    (re.compile(r"\bxox[abprs]-[A-Za-z0-9\-]{10,}\b"), "xox-<redacted>"),
$ scrub() on fake keys built at run time (secrets.token_hex(12) tails; the coordinator, after L5)
standalone scrubbed=True | after equals scrubbed=True | after quote scrubbed=True | after __ scrubbed=False | after letter scrubbed=False | after underscore scrubbed=False
$ python3 scripts/known_values_check.py --env-file .pc-bridge.env --env-file /root/.codiv/api.env --raw-file /root/.config/session-export/pseudonym.key --env GH_TOKEN --env GITHUB_TOKEN transcripts/sandbox/
known-values: 14 secret forms, 18 files, 3407965 bytes, 1 HIT(S)   <- the one hit: api.env:TYPESAFE_BASE_URL host whole=1 (a hostname, not a secret); every secret value whole=0 windows=0
$ git grep -l transcript_export -- "*.py" "*.sh" (importers outside tests)
docs/research/findings/j2b-variants/openjev_j2.py harness-ports/bin/hermes-session-export.py harness-ports/bin/qwen_matrix.py scripts/chat_find.py scripts/hiccup_scan.py scripts/jev.py scripts/jev_context.py scripts/laya_ft/build_dataset.py scripts/laya_ft/common.py scripts/laya_ft/teacher_label.py scripts/push_clean.sh scripts/session_export.py scripts/transcript_export.py src/agent_factory/decisions/volatile.py 
$ node .gitnexus/run.cjs impact scrub --direction upstream --repo .
risk UNKNOWN | direct callers: 0   (unresolved by the index: the importers above are the caller set)
$ the recorded Laya dataset manifest pins the scrubber as a code input
code[scripts/transcript_export.py] = af9d73eab7af665b
sha256sum scripts/transcript_export.py | cut -c1-16 = af9d73eab7af665b
$ bash scripts/test_summary.sh tests/test_transcript_export.py tests/test_session_export.py
pytest-summary: 233 passed in 13.61s
2 files set=e8f27bcb91e7
$ the same shape elsewhere (AF-AP-224 echo)
proofs/S0-04/check_compression.py:82:    ("sk-key", re.compile(r"\bsk-[A-Za-z0-9_-]{8,}")),
proofs/S0-04/tools/pc/capture_leg.py:46:LEAK_RE = re.compile(r"(?i)bearer\s+\S|\bsk-[A-Za-z0-9_-]{8,}")
$ df -h / | awk "NR==2{print \$4}"
1.8G
```

A question for you, not a fact: `push_clean.sh`'s transcript sync runs `transcript_export.py` and commits what it writes.
When your value gate refuses, what does the sync do today, and is a refused sync visible to the person pushing? Answer from
the code; do not edit `push_clean.sh`.
