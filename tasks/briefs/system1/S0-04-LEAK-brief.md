# S0-04-LEAK: S0-04's leak detectors catch glued keys; the proof is re-minted for the owner's re-sign (task #287, D-091 item 3)

Role: code-implementer (sandbox, Opus 5.5). Do NOT spawn subagents. Report: `tasks/briefs/system1/S0-04-LEAK-report.md`
(write it incrementally from the start). PIN: 37f720a (origin). Evidence: AF-AP-224 in `docs/INCIDENT-LOG.md`; SCRUB1's
report (`tasks/briefs/system1/SCRUB1-report.md`, section 2: the left anchor chosen by measurement for the same rule shape);
the last S0-04 re-mint, whose commit message is the recipe (the S4H landing, 2026-09-22 04:34Z: `git log -1 --format=%B`
on the commit whose subject starts "S0-04 checker: S4H LANDS").

## WHY

The owner (D-091): "fix the checkers; I'll re-sign." S0-04's credential screen (`LEAK_PATTERNS` in
`proofs/S0-04/check_compression.py`) and the capture tool's exception guard (`LEAK_RE` in
`proofs/S0-04/tools/pc/capture_leg.py`) anchor the `sk-` rule on `\b`, so a key glued to a preceding `_` passes (AF-AP-224;
the scrubber had the same shape and SCRUB1 fixed it with `(?<![A-Za-z0-9])`). The key-assignment rule has the same anchor on
the name side: `\b(?:api[_-]?key|…)` does not match inside `SOMETHING_API_KEY=`, because `_` is a word character. S0-04 is
minted and owner-signed (`accepted/S0-04`, D-069); the checker AND the capture tool are attested inputs of the mint (the
premise lists the attestation), so a fix re-mints the result and the owner signs the new one.

## CONTRACT

1. **The detectors.** Every rule in both files whose left anchor refuses a key or a key name glued to `_` gets an anchor
   that accepts it and still refuses a letter or digit before it (SCRUB1's measured choice; re-measure it here). Measure
   each candidate over S0-04's own bundle files (the committed evidence and every fixture) and the lane's gates: the real
   evidence must stay free of hits (a new hit there is either a real leak, which STOPS the lane and is reported as such, or a
   false positive, which means the candidate is wrong). Rules whose anchors are already right stay byte-identical.
2. **Tests** in `tests/test_s0_04_compression.py`, with fake keys built at run time (`secrets.token_hex`), never a real
   value: a bundle file holding a key glued after `_` and `__`, and a `<PREFIX>_API_KEY=<value>` assignment, fails the checker
   with the exact reason string the checker emits for a leak; the capture tool's guard refuses the same shapes in an
   exception message; ordinary text does not trip them (`task-…`, `risk-…`, `disk-…`, a header name like
   `x-api-key-id`, a path ending `_API_KEY_FILE`). A negative control: each new test reds on the PIN's rules.
3. **The re-mint.** Regenerate the attested result exactly as the S4H landing did (the runner on this sandbox venue, then the
   ledger integrity check and the ledger regeneration); the result stays PASS for the same assertions, and the only changed
   attestation entries are the two changed files' hashes (and the ledger line that follows from them). Show the diff of `result.json` and
   `proofs/ledger.json`, field by field.
4. **The anchor state.** After the re-mint, `scripts/check-proof-status.py` refuses: the minted result changed since
   `accepted/S0-04`. That is correct until the owner re-signs; do not change the checker, the ledger, `docs/governance/` or
   any tag. Prove the two states in a scratch copy: (a) as the tree stands, the exact error; (b) with the committed tag
   object removed, the local tag ref absent and a `PROOF-ANCHOR: S0-04 = PENDING-OWNER-TAG …` line in the ledger, rc 0 with
   the pending WARNING. The coordinator makes (b) real at landing and hands the owner the re-sign command.
5. **Siblings.** Report (do not fix) every other leak screen in `proofs/`, `scripts/`, `src/` and `harness-ports/` with the
   same shape or a gap of the same class; the premise lists the ones in S0-01, which is also a signed proof.

## EVIDENCE DEMANDS

1. Premise: re-measure the block below; stop and report CONTRACT-INVALID on a mismatch that matters.
2. The measurement of contract item 1: per candidate and rule, the hits on the real evidence, on each fixture and on the
   test corpus, with the command.
3. `bash scripts/test_summary.sh` twice on `tests/test_s0_04_compression.py tests/test_proof_status.py` with the set id
   (`test_proof_status.py` needs a SHORT `--basetemp`, such as `/tmp/s4l/bt` with its parent created first: gpg's socket
   path overflows under the scratchpad and nine tests read red; after the re-mint, with the old tag still present, three
   committed-state tests fail BY DESIGN until the owner re-signs: read the assertions, never the count);
   pyflakes rc 0 on both S0-04 files and the test file; `scripts/ap_screen.py` on the changed files (name any pre-existing
   hit); `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>` prints 0 for every file you write.
4. A mutation pass on the changed rules (restore each old anchor alone, widen each new anchor to no anchor): each mutant
   reds a named test, classified by a FAILED test, never an error (AF-AP-223).
5. NOT-done and DISCREPANCIES.

## BOUNDARY

MODIFY: `proofs/S0-04/check_compression.py` (`LEAK_PATTERNS` only), `proofs/S0-04/tools/pc/capture_leg.py` (`LEAK_RE`
only), `tests/test_s0_04_compression.py`. REGENERATE by their own tools only: `proofs/S0-04/result.json`,
`proofs/ledger.json`. CREATE: your report. READ everything else. Never touch `docs/governance/`, the ledger
(`todo/BUILD-TASKLIST.md`), any git ref or tag, or another proof. Other lanes may be live in this tree; the coordinator's
`.lanes-live` file lists their paths: touch none of them.

## STANDING RULES

Secrets: never print, store or paste a secret value or a matched span that could be one; test keys are fake strings built
at run time; bundle scans print counts, file names and masked shapes only. No git writes in this tree (throwaway repositories
in your scratch are fine); no PC bridge; no outward-facing action. The disk is shared (1.3G free): scratch under 150 MB
in `/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/s004leak/`, deleted as you go; a short
`--basetemp` there with its parent created first. Test counts pasted from `scripts/test_summary.sh`; stamps from `date -u`.
Long commands in one foreground call; kill by pid, never by name.

## PREMISE — MEASURED at authoring (2026-09-25 19:5xZ, /home/user/agent-factory at the PIN's bytes for every file named)

```
$ git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf
37f720a SLOPO2 brief (task #285, D-091 item 5): a launcher that runs slopo with a pruning walker in place of its whole-t
$ sed -n '75,86p' proofs/S0-04/check_compression.py
# Credential screen over every bundle file (the S0-01 `_STDERR_LEAK_RE` idea, widened).
# The bare 64-hex rule would fire on the instrument's own `authorization_fingerprint`, which is
# a sha256 of the bearer and is the REDACTION, not the secret; that one value is validated for
# digest shape and then masked out of the text before the scan, so a SECOND 64-hex run anywhere
# still fails and a bearer smuggled into that field fails the shape check.
LEAK_PATTERNS = (
    ("bearer", re.compile(r"(?i)bearer\s+\S")),
    ("sk-key", re.compile(r"\bsk-[A-Za-z0-9_-]{8,}")),
    ("key-assignment", re.compile(
        r"(?i)\b(?:api[_-]?key|apikey|secret|password|passwd|token)\b"
        r"\s*[\"']?\s*[:=]\s*[\"']?[A-Za-z0-9_\-.+/]{8,}")),
    ("hex64", re.compile(r"(?<![0-9a-fA-F])[0-9a-fA-F]{64}(?![0-9a-fA-F])")),
$ grep -n -E '_leak_hit|LEAK_PATTERNS' proofs/S0-04/check_compression.py
80:LEAK_PATTERNS = (
98:def _leak_hit(text: str):
99:    for name, rx in LEAK_PATTERNS:
108:    return text if _leak_hit(text) is None else "<reason withheld: credential-shaped>"
173:            hit = _leak_hit(text)
$ sed -n '44,47p' proofs/S0-04/tools/pc/capture_leg.py
MAX_RECORD_FILE = 8 * 1024 * 1024
# An exception message must never become the leak the redaction elsewhere prevents.
LEAK_RE = re.compile(r"(?i)bearer\s+\S|\bsk-[A-Za-z0-9_-]{8,}")

$ grep -n 'LEAK_RE' proofs/S0-04/tools/pc/capture_leg.py
46:LEAK_RE = re.compile(r"(?i)bearer\s+\S|\bsk-[A-Za-z0-9_-]{8,}")
54:    return "<message withheld: credential-shaped>" if LEAK_RE.search(text) else text
$ grep -rn -E '\\bsk-|\\b\(\?:api|\\bghp|\\bAIza|\\bxox|bearer\\\\s' --include=*.py proofs/ scripts/ src/ harness-ports/ spikes/ | grep -v /archive/   (the sibling sweep)
proofs/S0-01/check_acp_conformance.py:150:_SENSITIVE_HEADER_VALUE_RE = re.compile(r"(?i)bearer\s|sk-|[0-9a-fA-F]{64}")
proofs/S0-01/check_acp_conformance.py:153:_STDERR_LEAK_RE = re.compile(r"(?i)[0-9a-fA-F]{64}|bearer\s|token[=:]\S")
proofs/S0-04/check_compression.py:81:    ("bearer", re.compile(r"(?i)bearer\s+\S")),
proofs/S0-04/check_compression.py:82:    ("sk-key", re.compile(r"\bsk-[A-Za-z0-9_-]{8,}")),
proofs/S0-04/check_compression.py:84:        r"(?i)\b(?:api[_-]?key|apikey|secret|password|passwd|token)\b"
proofs/S0-04/tools/pc/capture_leg.py:46:LEAK_RE = re.compile(r"(?i)bearer\s+\S|\bsk-[A-Za-z0-9_-]{8,}")
$ python3 -c 'attestation of proofs/S0-04/result.json: count, the checker, any tools/ entry'
44 entries; check_compression.py attested: True ; tools/ entries: ['proofs/S0-04/tools/pc/capture_leg.py', 'proofs/S0-04/tools/pc/run_s0_04_legs.sh']
$ python3 -c 'result.json classification, recorded_at, env_fingerprint'
execution_proof 2026-09-22T04:31:52.985441Z sandbox:vm
$ git cat-file -p accepted/S0-04 | head -1; git diff --quiet fa20942 HEAD -- proofs/S0-04/result.json; echo rc=$?
object fa20942e4dc792745c9a8338b3cfcae8d34c8779
result.json identical at the tagged commit and HEAD: rc=0
$ ls docs/governance/tags/accepted-S0-04.tag; grep -c '^PROOF-ANCHOR' todo/BUILD-TASKLIST.md
docs/governance/tags/accepted-S0-04.tag
0
$ python3 scripts/check-proof-status.py . ; echo rc
check-proof-status rc=0
$ grep -n -E 'PENDING_ANCHOR =|changed since|stale declaration' scripts/check-proof-status.py
85:PENDING_ANCHOR = re.compile(r"^PROOF-ANCHOR:\s+(S0-[0-9]{2})\s*=\s*PENDING-OWNER-TAG\b.*$", re.MULTILINE)
136:                      f"PENDING — a stale declaration (remove it)")
178:        errors.append(f"{proof_id}: the minted {rel} changed since {tag} (regenerated after acceptance) — "
$ bash scripts/test_summary.sh --basetemp=<the session scratchpad>/... tests/test_s0_04_compression.py tests/test_proof_status.py
pytest-summary: 9 failed, 103 passed in 7.68s
   (false reds: gpg's socket path under the long scratchpad basetemp; env-tool-quirks, test_proof_status)
$ mkdir -p /tmp/ps && bash scripts/test_summary.sh --basetemp=/tmp/ps/bt tests/test_s0_04_compression.py tests/test_proof_status.py
pytest-summary: 112 passed in 9.47s
2 files set=2fa20f3af1f3
$ git log -1 --format='%h %ci %s' --grep='S4H LANDS' origin/claude/soundbox-kit-migration-iz1jwf | cut -c1-110   (the re-mint recipe is its message)
a815883 2026-09-22 04:34:30 +0000 S0-04 checker: S4H LANDS (issue #7 batch 2) — the four un-killed guards ge
$ git log -1 --format=%B <that commit> | grep -o -E 'python3 scripts/proof-runner[^;]*|validate-ledger[^;]*|ledger-gen[^;]*' | head -3
python3 scripts/proof-runner run --proof S0-04 --venue sandbox --root .` rc 0
ledger-gen` rewrote proofs/ledger.json (the S0-04 normalized_digest line only)
$ grep -n 'Decision: S1' tasks/briefs/system1/SCRUB1-report.md
83:**Decision: S1, `(?<![A-Za-z0-9])`, on all four rules; the trailing `\b` unchanged.** No known secret is left under S1:
$ git log -1 --format='%h %ci %s' -- proofs/S0-04/tools/pc/capture_leg.py | cut -c1-110
be6be79 2026-09-19 13:19:43 +0000 S0-04: provider_block reads the real Hermes schema (api/transport), not just
$ git log -1 --format='%h %ci %s' -- proofs/S0-04/evidence | cut -c1-110
5e2a541 2026-09-19 14:22:21 +0000 S0-04 MINTED: compression contract proven live end-to-end (execution_proof 6
```

A question for you, not a fact: the capture tool runs on the PC and IS an attested input of the mint (the premise lists the
attestation); its last change precedes the evidence commit by an hour (the premise's two log lines). After the fix, does a re-mint that attests
the new bytes over the old evidence stay honest, or does the spec need a new live capture? Answer from the spec, the runner
and the checker. If a capture is needed, stop after the code, the tests and the sandbox re-mint, and say so: the
coordinator runs the PC capture.
