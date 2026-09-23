# J1-1-R1 — the decision state is bounded AFTER redaction, and no secret class leaks into the ledger (task #139; the ONE focused repair under D-056)

PIN: the post-push SHA of the commit that adds this brief (named in the dispatch prompt; read it with
`git log --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf -8`). The boundary files are byte-identical to local ce0a3be
(measured below); re-measure them first.
LANE: j1-1-r1 (sandbox; agent `code-implementer` on the D-054 pin, in the SHARED tree, no worktree isolation). Honey `ultra`
Lever-2: your report is DATA — files:lines, pasted counts, discrepancies, NOT-done. Do NOT spawn subagents.

WHY: VERIFY-J1-1 (`tasks/briefs/laya/VERIFY-J1-1-report.md`) returned the J1-1 contract CONTRACT-INVALID (C-F1) with one in-contract
BLOCKER (C-F3a). The J1-1 brief (`tasks/briefs/laya/J1-1-brief.md`, items 2-4) cuts each bounded field inside `normalize`
(`src/agent_factory/decisions/volatile.py:142-143`) and redacts after it, so a secret that straddles a field's limit loses its tail
before any pattern sees it: up to 7 (sk), 15 (bearer), 31 (token run) or limit-32 (PEM body) secret characters reach the ledger
through the real `make_row` → `append` path. The coordinator amended the contract (D-056, `docs/08_DECISION_LOG.md`); this lane
builds the amended contract. It is AF-AP-127's class (a bound before a pattern redaction), marked OPEN for this repair.

CONTRACT SOURCES (read whole before you design): `tasks/briefs/laya/J1-1-brief.md` (items 1-6, still in force except where AMENDMENT 1
below replaces them) · D-056 in `docs/08_DECISION_LOG.md` · `tasks/briefs/laya/VERIFY-J1-1-report.md` sections 4, 8 and 11 (the C-F1
proof and the smallest amendment, which the verifier checked on a scratch copy) · the code as it stands at the PIN.

## The contract — AMENDMENT 1 to J1-1 (D-056; decided, do not re-litigate; a contradiction is a DISCREPANCY)

A1 **normalize never cuts.** Remove the bound from `_normalize_field` (`src/agent_factory/decisions/volatile.py:142-143`). Every other
normalize step stays as it is (relativize, NFC, whitespace collapse and strip, case, pin-suffix strip, the command's leading token).

A2 **bound(question_id, state) runs after redact.** For each field with a limit, cut the string at the limit on a code-point boundary,
then strip trailing whitespace (this closes VERIFY-J1-1 F-3: a cut after a space left a trailing space and `make_row` refused the row).
Lists and unbounded fields pass unchanged. The output of every bounded field is at most its limit.

A3 **ONE public composition.** `decision_state(question_id, state, root=None) = bound(redact(normalize(question_id, state, root)))`,
exported from `agent_factory.decisions`. `state_digest` (`src/agent_factory/decisions/canonical.py:70-76`) becomes
`sha256(canonical(decision_state(...)))`, and BOTH ledger call sites switch to it in this repair: the fixed-point check
(`src/agent_factory/decisions/ledger.py:271-274`, today `redact(normalize(qid, row["state"], None))`) and `make_row`
(`src/agent_factory/decisions/ledger.py:405`, today `redact(normalize(question_id, raw_state, root))`). Nothing else in `ledger.py`
changes. `decision_state` is idempotent on its own output, including when the cut lands inside a placeholder (the ledger's fixed-point
check depends on it). Update the module docstrings that state the old composition.

A4 **The secret classes that leak today.**
- C-F3a (token): a 32+ `[A-Za-z0-9+/]` run after `token`, `*_token` or `*_TOKEN` in the assignment forms `token = <run>`,
  `access_token=<run>`, `"token": "<run>"`, `PC_BRIDGE_TOKEN: <run>`, `AGENT_TOKEN: <run>` is redacted (today `_TOKEN`,
  `src/agent_factory/decisions/volatile.py:48`, takes one separator shape only).
- C-F3b (envval): the env-assignment names (`KEY`, `TOKEN`, `SECRET`, `PASSWORD`, `PASSWD`, `API_KEY`/`APIKEY`, with a prefix) are
  matched without regard to case, with optional spaces around a `=` or `:` separator and an optional quote around the value
  (`password=`, `PASSWORD = `, `password: `, `SECRET_KEY: `, `"api_key": "…"`). Take the shape of the transcript scrubber's credential
  rule (`scripts/transcript_export.py:33`: a value of at least 8 characters) so prose such as `key: sorted` is not redacted; the
  name is kept and the value becomes the `envval` placeholder, as today.
- privkey: take the transcript scrubber's label family (`scripts/transcript_export.py:29-31`,
  `[A-Z0-9 ]*(?:PRIVATE|SECRET) KEY(?: BLOCK)?`, GnuPG armor included), and redact to the end of the value when the END line is missing
  (VERIFY-J1-1 F-11). Measured at authoring (below): today GnuPG armor and an END-less block leave their body in the state.
The placeholders, the class order rule ("an assignment wins its own class"; the private-key block first) and the existing forms stay.
NOT in this repair: the `sk-` word boundary (C-F2) and every other VERIFY-J1-1 follow-up; they are filed as one issue.

A5 **Item 6's identity holds for over-limit fields.** A state whose bounded field carries a secret that straddles the limit hashes
IDENTICAL to the same state with the secret's placeholder in its place (the existing clean-form design, `volatile.py:30-32`), for
every class, and no byte of the secret's body is in `decision_state`'s output, in `canonical()` of it, or in the ledger file.

Nothing else changes: the seven schemas, the limits' values, the refusal texts, `canonical()`, the ledger's row shape, provenance,
append-only and replay rules. A golden digest (`tests/fixtures/decisions/golden/*.json`) may change ONLY when A1-A4 explain it for that
state; paste the old and new digest and the reason per file, or STOP and report if a digest changes that A1-A4 do not explain.

## Tests (each RED at the PIN, GREEN after; paste both runs)

In `tests/test_decisions_canonical.py`: one straddle case per class at a bounded key (the secret's first characters before the limit,
the rest after it), asserting no body bytes survive `decision_state` and `state_digest` equals the placeholder form's; an over-limit
identity case per class; a PEM or GnuPG block longer than the limit; the C-F3a and C-F3b forms (and a prose negative control such as
`key: sorted order` that must NOT be redacted); GnuPG armor and an END-less block; `bound`'s cut on a code-point boundary with no
trailing whitespace and every bounded field at most its limit; `decision_state` idempotent, including a cut inside each placeholder.
In `tests/test_decisions_ledger.py`: `make_row` then `append` on an over-limit state with a straddling secret — accepted, the ledger
file's bytes hold no secret body byte, `replay` verifies the row, and the fixed-point check accepts it (today the order of the two call
sites would refuse it once J1-1 alone changed: VERIFY-J1-1 F-9).

## Mutation audit (scratch copies only: never `git checkout`, `git restore` or `git stash` in this shared tree)

At least: m1 bound before redact (the old order) · m2 drop the trailing-whitespace strip · m3 `ledger.py:405` back to
`redact(normalize(...))` · m4 `ledger.py:274` back · m5 `_TOKEN` back to its PIN pattern · m6 the envval class back to upper case and
`=` only · m7 the private-key class back to `PRIVATE KEY-----` only · m8 drop the END-less alternative · m9 `bound` without the cut.
Each mutant compiles and collects (AF-AP-78); before you count a kill, run the killing test on the UNMUTATED tree and paste that it
passes (AF-AP-138). Paste the killing test per row. A survivor is reported, never hidden.

## Gates (paste every command with its output)

`mkdir -p /tmp/j11r1/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_canonical.py tests/test_decisions_ledger.py -q -p no:cacheprovider --basetemp=/tmp/j11r1/bt/r<n>`
twice (rm -rf after each), with `bash scripts/pc_suite.sh set-id -- tests/test_decisions_canonical.py tests/test_decisions_ledger.py` ·
`/root/venv-agent-factory/bin/python -m pyflakes src/agent_factory/decisions/*.py tests/test_decisions_canonical.py tests/test_decisions_ledger.py` ·
`python3 scripts/ap_screen.py src/agent_factory/decisions/volatile.py src/agent_factory/decisions/canonical.py src/agent_factory/decisions/ledger.py` and
`python3 scripts/ap_screen.py --tests tests/test_decisions_canonical.py tests/test_decisions_ledger.py` (new hits vs the PIN) ·
`python3 scripts/no_laya_in_gates.py` (read-only; the tree must stay `clean`).

## Boundary and standing do-nots

MODIFY ONLY: `src/agent_factory/decisions/volatile.py`, `src/agent_factory/decisions/canonical.py`,
`src/agent_factory/decisions/__init__.py`, `src/agent_factory/decisions/ledger.py` (the two call sites and the docstring lines that
state the composition; nothing else), `tests/test_decisions_canonical.py`, `tests/test_decisions_ledger.py`, and
`tests/fixtures/decisions/golden/*.json` only as stated above. CREATE `tasks/briefs/laya/J1-1-R1-report.md` (write it incrementally).
Other sandbox agents work in this tree on disjoint files: `proofs/S0-02/`, `proofs/S0-05/` (E3-R1), `tests/test_s0_05_egress.py`,
`tasks/briefs/s0-02-support/`, `tasks/briefs/s0-05-support/`, `tasks/briefs/continuity/`, and a verify lane reading
`scripts/no_laya_in_gates.py`: never touch, run a writer against, or revert them. Never run `git stash`, `git checkout -- …`,
`git restore`, `git add`, `git commit` or `git push`: the coordinator commits your files. No outward-facing action; no PC or bridge
use. Every secret in a fixture or test is FAKE (never a key a tool generated for use). Scratch lives under `/tmp/j11r1/` and is removed
at the end (the sandbox had about 1.3 GB free at authoring). Run each gate in ONE foreground call.

CODE INTEL FIRST: `graft ask` before any grep for code questions; the pack:
`scripts/lane_context.sh -q 'where is a decision state normalized, redacted, bounded and hashed, and who composes it' -s normalize -s redact -s _normalize_field -s state_digest -s make_row -o /tmp/j11r1/pack.md src/agent_factory/decisions/volatile.py src/agent_factory/decisions/canonical.py src/agent_factory/decisions/ledger.py`.

## Report (`tasks/briefs/laya/J1-1-R1-report.md`)

PREMISE re-measured · per contract line A1-A5: files:lines and the tests that pin each · the golden-digest table (unchanged, or old →
new with the A-line that explains it) · the mutation table · the gates pasted · DISCREPANCIES · NOT-done. Report lint:
`python3 scripts/report_lint.py --min-refs 15 tasks/briefs/laya/J1-1-R1-report.md --root .` (at most three fix rounds, then paste).

## PREMISE — MEASURED at authoring (2026-09-23 11:30Z-11:3xZ, sandbox @ local ce0a3be)
```
$ git log -1 --format='%h %s' | cut -c1-80
ce0a3be VERIFY-J1-1 home (task #130): CONTRACT-INVALID on C-F1, BLOCKER C-F3a; t
$ blob[:12] lines
00c00847b33d    21 src/agent_factory/decisions/__init__.py
cda5c198d321    77 src/agent_factory/decisions/canonical.py
6d3d6a34150c   295 src/agent_factory/decisions/volatile.py
9531cff7d697   617 src/agent_factory/decisions/ledger.py
aa22d19cb94d   340 tests/test_decisions_canonical.py
132f9d4e1df0  1468 tests/test_decisions_ledger.py
$ git log --format="%h %s" -5 -- src/agent_factory/decisions | cut -c1-110
d4f4698 J1-2-R1 landed (GATED-PENDING-VERIFY): the decision ledger refuses short writes, closes its row shape
9d11c25 Laya J1-2 landed (GATED-PENDING-VERIFY): the append-only decision ledger with mandatory provenance, ro
01ca7d5 J1-1 landed (GATED-PENDING-VERIFY): the decisions module (seven closed state schemas, normalize -> red
$ grep -n (the seams, volatile.py)
26:EXCERPT_LIMIT = 400            # ap.violates_row.action_excerpt, wf.drift.observed/expected
27:MSG_LIMIT = 200               # b1.finding_sev / b1.finding_kind msg (bounded, not verbatim)
33:PLACEHOLDERS = {
41:_BEARER = re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/-]{16,}=*")
42:_SK = re.compile(r"sk-[A-Za-z0-9_-]{8,}")
48:_TOKEN = re.compile(r"(?i)\btoken(?:[:=] ?| )?([A-Za-z0-9+/]{32,})")
52:_ENVVAL = re.compile(
53:    r"(?P<name>(?:[A-Z][A-Z0-9_]*_)*(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY))=\S+"
56:_PRIVKEY = re.compile(
57:    r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----",
130:def _normalize_field(f: _Field, key: str, value, root):
142:    if f.limit is not None:
143:        s = s[: f.limit]
242:def normalize(question_id: str, state: dict, root: str | os.PathLike | None = None) -> dict:
271:def redact(state: dict) -> dict:
286:def _redact_str(text: str) -> str:
$ grep -n (the composition sites)
src/agent_factory/decisions/canonical.py:70:def state_digest(question_id: str, state: dict, root: str | None = None) -> str:
src/agent_factory/decisions/canonical.py:74:    normed = normalize(question_id, state, root)
src/agent_factory/decisions/canonical.py:75:    redacted = redact(normed)
src/agent_factory/decisions/ledger.py:271:    # (d) fixed-point check: redact(normalize(qid, state, None)) == state.
src/agent_factory/decisions/ledger.py:274:        restate = redact(normalize(qid, row["state"], None))
src/agent_factory/decisions/ledger.py:405:        s = redact(normalize(question_id, raw_state, root))
src/agent_factory/decisions/ledger.py:406:        sd = state_digest(question_id, raw_state, root)
src/agent_factory/decisions/__init__.py:21:__all__ = ["DecisionStateError", "normalize", "redact", "state_digest"]
$ grep -n "^def test" tests/test_decisions_canonical.py
63:def test_golden_digests_exact():
86:def test_relanding_stable():
108:def test_secret_redacted_every_class():
193:def test_unknown_key_refused():
203:def test_missing_key_refused():
211:def test_bad_enum_refused():
225:def test_closed_schema_refuses_incumbent_answer_key():
233:def test_command_target_uses_leading_token_and_pin_strip_is_exact():
255:def test_unknown_question_refused():
262:def test_abs_path_outside_root_refused():
272:def test_float_refused():
291:def test_normalize_does_not_redact():
303:def test_redact_does_not_normalize():
314:def test_order_is_normalize_then_redact():
$ gates (twice)
/root/venv-agent-factory/bin/python -m pytest tests/test_decisions_canonical.py tests/test_decisions_ledger.py -q -p no:cacheprovider --basetemp=...
53 passed in 0.37s
53 passed in 0.36s
bash scripts/pc_suite.sh set-id -- tests/test_decisions_canonical.py tests/test_decisions_ledger.py
2 files set=16a7b628685e
$ ls tests/fixtures/decisions/golden/
ap.violates_row.json b1.finding_kind.json b1.finding_sev.json b2.hit_role.json d1.bug_echo_scores.json v1.finding_class.json wf.drift.json
$ PYTHONPATH=src python (the real redact on FAKE blocks; body = "MIIEpAIB+AAKCAQ/EAx7Qe+Wz3k/Rt9L" * 3)
RSA PRIVATE KEY          body-left=False placeholder=True
PGP PRIVATE KEY BLOCK    body-left=True placeholder=False
PGP SECRET KEY BLOCK     body-left=True placeholder=False
RSA, no END              body-left=True placeholder=False
```
Not measured at authoring, and so written as questions for the lane: whether any golden digest changes under A1-A4, and whether the
widened envval class redacts any text in the seven golden states or the J0 probe fixture (`tests/fixtures/decisions/probe/questions.json`)
that is not a secret (count it and say).
