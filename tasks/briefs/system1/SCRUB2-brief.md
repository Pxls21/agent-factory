# SCRUB2: the scrubber's right side, escape contexts and shape gaps; its tests never read a real secret (task #292 widened; VERIFY-SCRUB1 F1-F3, F8-F10, F12-F14, F17)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/system1/SCRUB2-report.md` (write it
incrementally from the start). PIN: the local HEAD 4b3b699 (its push to origin is queued behind CI, so cite commits by subject in
anything you write). Grounds: `tasks/briefs/system1/VERIFY-SCRUB1-report.md` (section 9, the finding inventory, and its probes),
`tasks/briefs/system1/SCRUB1-brief.md` and `SCRUB1-report.md` (the method this lane repeats), AF-AP-224 in `docs/INCIDENT-LOG.md`.

Authorization, for the record: this is defensive work on the owner's own system. `scripts/transcript_export.py` scrubs the chat
digests that are committed and pushed; its rules and its value gate keep credentials out of them. Every key and value you build
is a fake made at run time (`secrets.token_hex`).

## WHY

VERIFY-SCRUB1 (MERGE-READY-WITH-FOLLOWUPS) found key shapes the scrubber still passes and a test file that reads the machine's
REAL secret sources: `main()` calls `export()`, whose `sources=` default was bound when the function was defined, and no test
replaces it, so every run of `tests/test_transcript_export.py` opens the real bridge env, API env and pseudonym key in process.
One lane fixes these together, so the Laya dataset manifests' code hash is regenerated once.

## CONTRACT

1. **The right side (F2, F12).** A key followed by a non-ASCII letter, a quote or (for `xox`) an `_` is taken whole in all four
   provider rules (their trailing `\b` fails between an ASCII letter and `é`, and an `xoxb` token followed by `_` leaks its last
   segment today), and the opaque 40+ rule takes a run glued to a non-ASCII letter on either side. For example an ASCII-only
   right anchor such as `(?![A-Za-z0-9])`; choose by measurement (item 6).
2. **Escape contexts (F3).** A key just after a JSON escape in raw JSON text (`\n`, `\t`, `\r`, `\uXXXX`) is caught, through
   `session_export.convert()` (its canonical JSON writes `\n` before a line start) and every other writer that scrubs raw
   JSON. SCRUB1 measured one candidate, `(?:(?<![A-Za-z0-9])|(?<=\\[nrt]))`; extend it to `\uXXXX` or show why not.
3. **Shape gaps (F14).** `passphrase`, `pwd` and `credentials` as credential-assignment names; a `Cookie:` session value;
   `Authorization: Token <v>`; a PEM block whose header lines are malformed. Each is decided by measurement (item 6): a shape
   that costs ordinary-text redactions goes in only with its count and your reason, else it is a DISCREPANCIES row.
4. **The tests never read a real source (F1), and the sources are pinned (F8, F9).** `main()` resolves the sources when it
   runs. Every test that reaches `export()` or `main()` runs against fixture sources (the premise block lists the files that
   call them: only `tests/test_transcript_export.py`). No seam may switch the production gate off silently: whatever lets a
   test replace the sources must be impossible to reach from `push_clean.sh`'s sync or the plain CLI. Pins: one test asserts
   the exact five-entry production tuple (`.pc-bridge.env` resolved to the repo root, the two env files, the raw key, the two
   variables); one assertion each for the AIza and xox letter anchors, the 8-character floor, and `TYPESAFE_BASE_URL` skipped
   in its own source only. Prove that no committed test opens a real source path (for example `strace -f -e trace=openat` over
   the whole test file, the opens of the five source paths counted: 0).
5. **The value-gate sources (F10, F13, in `scripts/known_values_check.py`).** A source that is not a regular file (a FIFO, a
   directory) refuses at once instead of hanging; a refusal line prints an env line's name only when it matches
   `[A-Za-z_][A-Za-z0-9_]*` (else `<malformed line N>`); a source kind outside the known three is an error, never a raw file.
   The inline-comment case of F10 stays as it is unless you find a reason: the coordinator measured the real env files (no
   value holds whitespace, `#` or a quote).
6. **Measurement, SCRUB1's method.** Each rule change over the 18 committed digests and this session's transcripts (in
   process): the new redactions per rule, as masked shapes only (the prefix, the length, the character classes; never the
   text). You cannot tell a known secret from an ordinary string (you never read a real source): write the new exporter's
   digests of this session's transcript to your scratch with `sources=()`, and the coordinator checks them for known values
   at landing. Old-to-new: no redaction the PIN makes may be lost.
7. **F17:** the stale opaque-rule comment (it says 32+, the rule is 40).
8. **The Laya lock.** The dataset manifests pin `scripts/transcript_export.py` as a code input. The lock check is the builder's
   pre-fit comparison (`collect_v2` at each manifest's recorded commit, run with the old and the new scrub, the items counted;
   VERIFY-SCRUB1 F11 and its `laya_rescrub.py`), not a re-scrub of stored states. 0 changed items: regenerate each manifest's
   code hash by K265's step (SCRUB1-report.md section 6 has the commands) and prove the dataset bytes identical. Any changed
   item: STOP and report the count; a data change is the coordinator's decision.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. The measurement table of item 6 and the Laya lock result of item 8, each with its command.
3. Tests with fake keys built at run time: each new rule in every context (standalone, after `=`, a quote, `_`, `__`, a JSON
   escape, a non-ASCII letter on either side, at a line start and end, inside a URL) through the real functions and through
   `export()` and `convert()` end to end; ordinary text that must not be redacted; the item 4 pins; the item 5 behaviours. A
   negative control reds for each on the PIN's code or on a named mutant (a kill is a FAILED test, never an error: AF-AP-223).
4. Until item 4's fix is in place, run `tests/test_transcript_export.py` only where the real sources are unreachable (VERIFY-
   SCRUB1's `<scratch>/vscrub1/masked.sh absent <copy> -- <cmd>`, a private mount namespace), never in the plain tree.
5. `bash scripts/test_summary.sh` twice on set A (the 15 files of SCRUB1-report.md section 5) with the set id; pyflakes rc 0;
   `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0 for every file you write.
6. NOT-done and DISCREPANCIES.

## BOUNDARY

MODIFY: `scripts/transcript_export.py`, `scripts/known_values_check.py`, `tests/test_transcript_export.py`,
`tests/test_known_values_check.py`, and the two `docs/research/findings/laya-ft-labels/*/dataset-manifest.json` (their code hash
only, by the builder's step). CREATE: your report. READ everything else. Report adjacent defects, never fix them (#291's
push_clean sync and #293's other writers are other tasks).

## STANDING RULES

No git writes in this tree; no PC bridge; no outward-facing action. **Never read a real secret source** (`.pc-bridge.env`,
`/root/.codiv/api.env`, `/root/.config/session-export/pseudonym.key`, any `*.env`, `~/.config/qwen-*`, the GH_TOKEN and
GITHUB_TOKEN variables); the exporter's default sources are never exercised outside the masking runner. Transcripts hold
secrets: read them in process only and print ids and counts, never a record's text. Another lane (S1-RATE) is live in this tree:
never touch its files (`scripts/hook_context.py`, `.claude/hooks/system1-context.py`, `tests/test_session_hooks.py`,
`tests/test_system1_context.py`, `scripts/s1_scores.py`, `tests/test_s1_rate.py`). The disk is shared (1.8G free at
authoring): scratch under 300 MB in `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/scrub2/`, deleted as you go; a short `--basetemp` with its parent created first.
Test counts pasted from `scripts/test_summary.sh`; stamps from `date -u`. Long commands in one foreground call; kill by pid, never
by name.

## PREMISE — MEASURED at authoring (2026-09-25 23:2xZ, the sandbox tree at 4b3b699)

```
$ git log --format=%h 49bf75e..HEAD -- scripts/transcript_export.py scripts/known_values_check.py tests/test_transcript_export.py tests/test_known_values_check.py scripts/session_export.py | wc -l
0
$ grep -n -E '\(\?<!\[A-Za-z0-9\]\)(sk-|\(\?:ghp|AIza|xox)|A-Za-z0-9_\\-\]\{40,\}' scripts/transcript_export.py | cut -c1-110
84:    (re.compile(r"(?<![A-Za-z0-9])sk-[A-Za-z0-9_\-]{12,}\b"), "sk-<redacted>"),
85:    (re.compile(r"(?<![A-Za-z0-9])(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b"), "gh<redacted>"),
86:    (re.compile(r"(?<![A-Za-z0-9])AIza[0-9A-Za-z_\-]{30,}\b"), "AIza<redacted>"),
87:    (re.compile(r"(?<![A-Za-z0-9])xox[abprs]-[A-Za-z0-9\-]{10,}\b"), "xox-<redacted>"),
91:    (re.compile(r"\b[A-Za-z0-9_\-]{40,}\b"), "<opaque-redacted>"),
$ grep -n -E '^def export|written = export\(' scripts/transcript_export.py
296:def export(transcript: str, out: str, cap: int, sources=KNOWN_VALUE_SOURCES) -> list:
333:        written = export(path, a.out, a.cap)
$ grep -n -E 'KNOWN_VALUE_SOURCES|GH_TOKEN' tests/test_transcript_export.py | cut -c1-110 | head -6
837:    assert ("env-file", "/root/.codiv/api.env", ("TYPESAFE_BASE_URL",)) in MOD.KNOWN_VALUE_SOURCES
850:    # the production source list through main(): GH_TOKEN is one of its sources, so a fake value in it is 
855:    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=dict(os.environ, GH_TOKEN=fake
857:    assert "transcript_export: REFUSED, nothing written: env:GH_TOKEN value whole=1 windows=25/25" in r.st
861:    r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=dict(os.environ, GH_TOKEN=fake
$ for f in tests/*.py harness-ports/tests/*.py; do n=$(grep -c -E 'transcript_export\.(main|export)\(|\.export\(' "$f"); [ "$n" != 0 ] && echo "$f calls=$n"; done
tests/test_transcript_export.py calls=9
$ ls docs/research/findings/laya-ft-labels/*/dataset-manifest.json
docs/research/findings/laya-ft-labels/2026-09-24-openjev/dataset-manifest.json
docs/research/findings/laya-ft-labels/2026-09-25-recorded/dataset-manifest.json
$ ls /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vscrub1/ | head -20
attrib.py
bytecmp.py
cost.py
e2e_probe.py
gate_probe.py
laya_rescrub.py
masked.sh
measure_v.py
mutate_v.py
old
pin
rules_probe.py
shapes.py
writers_probe.py
$ bash scripts/test_summary.sh <set A, the 15 consumer files of SCRUB1-report.md section 5>   (run by the coordinator; the transcript's clock reads 23:05:10Z for its result)
pytest-exit: 0
pytest-summary: 723 passed, 1 skipped in 102.26s (0:01:42)
15 files set=271f9e77620b
```

A question for you, not a fact: which writers scrub raw JSON text rather than decoded strings (the escape context of item 2
matters only there), and does any of them keep an escape the exporter's own writes drop?
