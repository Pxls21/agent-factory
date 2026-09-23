# J1-1-R2 — a secret name that an earlier class consumes never frees its value (task #192; the second focused repair, coordinator-authorized under D-057)

PIN: d556c9b (origin head at authoring). The boundary is byte-identical at that head and at every later origin head until this lane
lands (blob ids below; re-measure them first).
LANE: j1-1-r2 (sandbox; agent `code-implementer`, in the SHARED tree, no worktree isolation). Honey `ultra` Lever-2: your report is
DATA — files:lines, pasted counts, discrepancies, NOT-done. Do NOT spawn subagents.

WHY: VERIFY-J1-1-R1 (`tasks/briefs/laya/VERIFY-J1-1-R1-report.md`, sections 2, 11 and 12, finding V-1) returned J1-1-R1 NOT-READY on one
blocker. J1-1-R1's A4 (C-F3b, `tasks/briefs/laya/J1-1-R1-brief.md` line 41) promises that a secret NAME "with a prefix" is matched and
its value becomes the `envval` placeholder. `_SK` (`src/agent_factory/decisions/volatile.py:45`: no left boundary, its class takes `-`
and `_`) and `_BEARER` (`:44`) run before the assignment classes (`:329-330` before `:331-333`) and consume a hyphen-prefixed name:
`task-password: v` becomes `ta<redacted:sk>: v`, the widened class finds no name, and `v` reaches the ledger file through the real
`make_row` -> `append` path; `replay` accepts the row. Measured at authoring: 8 of 8 shapes leak (premise below). It is not a
regression (the parent of J1-1-R1 leaked these too), but it is the promise J1-1-R1 was the repair for, so the coordinator authorized
this second repair (D-031: a first repair that failed to close a qualifying blocker) and recorded the contract amendment D-057.

CONTRACT SOURCES (read whole before you design): `tasks/briefs/laya/J1-1-R1-brief.md` (A1-A5 still in force) · D-056 and D-057 in
`docs/08_DECISION_LOG.md` · `tasks/briefs/laya/VERIFY-J1-1-R1-report.md` sections 2, 4, 8, 11 and 12 · the code at the PIN.

## The contract — AMENDMENT 2 to J1-1 (D-057; decided, do not re-litigate; a contradiction is a DISCREPANCY)

B1 **The eight V-1 rows close.** For each row of the appendix driver marked V1-a … V1-h, no byte of the fake value body is in
`decision_state`'s output, in `canonical()` of it, or in the appended ledger line on disk, and `replay` accepts the row.

B2 **No new leak.** Every value the PIN redacts stays redacted. At minimum: the driver's six controls C-1 … C-6 stay `ok`, and the
verifier's 43-shape table (report section 2) is a differential: no row that is `ok` at the PIN becomes `LEAK` (rebuild the shapes from
the table; the verifier's scratch driver was removed). Measured at authoring: the verifier's option B (section 11: `\bsk-` plus a
negative lookahead after the bearer run) opens a NEW leak on C-4 — `Authorization: Bearer <token>: rejected` keeps the token (option B
on a scratch copy: `leaking: 2`, V1-h and C-4). Do not adopt it as written.

B3 **The class forms may change; the placeholders, the refusal texts, the seven schemas, the limits, `canonical()`, the ledger's row
shape and the D-1 class order stay.** D-057 lifts D-056's exclusion of the `sk-` form (C-F2 "an identity collapse, not a leak" is
falsified by V-1): `_SK` and `_BEARER` may change. If you change the pass ORDER instead, paste the measured row that needs it, and keep
bearer ahead of the upper-case NAME=value class (section 11: moving bearer after it leaks `PASSWORD=Bearer <token>`). Feasibility was
measured at authoring: at least one change to the two class forms alone closes all 14 driver rows with the 72 tests passing and the
goldens unchanged. The design is yours.

B4 **The identity rules still hold.** `decision_state` is idempotent on its own output for every driver row and every rebuilt shape
(the ledger's fixed-point check, `src/agent_factory/decisions/ledger.py:273`, depends on it). No golden digest
(`tests/fixtures/decisions/golden/*.json`) changes; if one does, STOP and report it (nothing in this amendment explains a change).

B5 **Cost stays linear.** For each pattern you change, time adversarial inputs of 16k, 32k, 64k and 128k characters built to make it
backtrack (the verifier's section 5 shows the method), paste the timings, and keep the existing
`test_env_assignment_redaction_does_not_backtrack_exponentially` green.

## Tests (each B1 test RED at the PIN, GREEN after; paste both runs)

In `tests/test_decisions_ledger.py`: one test per V1 row through `make_row` -> `append` -> the file bytes -> `replay` (the body must be
absent from the file), and one per control (green at both; its negative control is a mutant). In `tests/test_decisions_canonical.py`:
the same rows at `decision_state` level, idempotence on each, and the no-new-leak control for C-4.

## Mutation audit (scratch copies only: never `git checkout`, `git restore` or `git stash` in this shared tree)

At least: m1 `_SK` back to its PIN form · m2 `_BEARER` back to its PIN form · m3 the verifier's option-B bearer guard (the exact
pattern in report section 11) in place of yours · m4 each further element of your change removed on its own. Each mutant compiles and
collects (AF-AP-78); before you count a kill, run the killing test on the UNMUTATED tree and paste that it passes (AF-AP-138). Paste
the killing test per row. A survivor is reported, never hidden. m3 must be killed by the C-4 test.

## Gates (paste every command with its output)

`mkdir -p /tmp/j11r2/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_canonical.py tests/test_decisions_ledger.py -q -p no:cacheprovider --basetemp=/tmp/j11r2/bt/r<n>`
twice (rm -rf after each), with `bash scripts/pc_suite.sh set-id -- tests/test_decisions_canonical.py tests/test_decisions_ledger.py`
(the PIN: `72 passed`, set `16a7b628685e`; the new tests add to it, none is skipped or deleted) · the appendix driver after your
change (`leaking: 0`) · `/root/venv-agent-factory/bin/python -m pyflakes src/agent_factory/decisions/volatile.py tests/test_decisions_canonical.py tests/test_decisions_ledger.py` ·
`python3 scripts/ap_screen.py src/agent_factory/decisions/volatile.py` and
`python3 scripts/ap_screen.py --tests tests/test_decisions_canonical.py tests/test_decisions_ledger.py` (new hits vs the PIN) ·
`python3 scripts/no_laya_in_gates.py` (read-only; the tree must stay `clean`).

## Boundary and standing do-nots

MODIFY ONLY: `src/agent_factory/decisions/volatile.py` (the class forms, their comments and the module docstring lines that state
them), `tests/test_decisions_canonical.py`, `tests/test_decisions_ledger.py`. CREATE `tasks/briefs/laya/J1-1-R2-report.md` (write it
incrementally from the start). READ-ONLY: every other file, including `src/agent_factory/decisions/ledger.py`,
`src/agent_factory/decisions/canonical.py`, `tests/fixtures/decisions/**` and `scripts/transcript_export.py` (the transcript scrubber
has the same bearer shape; it is VERIFY-J1-1-R1's V-13 follow-up, NOT this repair). Other sandbox agents work in this tree on disjoint
files (`proofs/S0-02/`, `tests/test_s0_02_buzz_authz.py`, `tasks/briefs/s0-02-support/`, and possibly `scripts/no_laya_in_gates.py`
read by a verify lane): never touch, run a writer against, or revert them. Never run `git stash`, `git checkout -- …`, `git restore`,
`git add`, `git commit` or `git push`: the coordinator commits your files. No outward-facing action; no PC or bridge use. Every secret
in a fixture or test is FAKE (the driver's `QZJ8…` bodies; never a key a tool generated for use). Scratch lives under `/tmp/j11r2/` and
is removed at the end (the sandbox had about 1.7 GB free at authoring). Run each gate in ONE foreground call.

CODE INTEL FIRST: `graft ask` before any grep for code questions; the pack:
`scripts/lane_context.sh -q 'how does the decision-state redactor order its secret classes and which class can consume a secret name' -s _redact_str -s _envval_wide -s decision_state -s make_row -o /tmp/j11r2/pack.md src/agent_factory/decisions/volatile.py src/agent_factory/decisions/ledger.py`.

NOT IN SCOPE (report, do not build): VERIFY-J1-1-R1's follow-ups V-2 … V-6, V-15, V-16 (the class-order test that cannot tell the
order apart, the `~` idempotence case, the full-width separators, the case and length floors, the alarm test) and #187's V-12 … V-14;
they are filed as one verify-followup issue.

## Report (`tasks/briefs/laya/J1-1-R2-report.md`)

PREMISE re-measured · per contract line B1-B5: files:lines and the tests that pin each · the driver before and after · the 43-shape
differential (PIN column, after column) · the cost table · the golden digests (unchanged) · the mutation table · the gates pasted ·
DISCREPANCIES · NOT-done. Report lint: `python3 scripts/report_lint.py --min-refs 15 tasks/briefs/laya/J1-1-R2-report.md --root .`
(at most three fix rounds, then paste).

## PREMISE — MEASURED at authoring (2026-09-23 14:0xZ, sandbox @ local 774d764; origin d556c9b)
```
$ date -u +%Y-%m-%dT%H:%MZ
2026-09-23T14:01Z
$ git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf
d556c9b
$ git diff --quiet origin/claude/soundbox-kit-migration-iz1jwf -- src/agent_factory/decisions tests/test_decisions_canonical.py tests/test_decisions_ledger.py tests/fixtures/decisions && echo identical
identical
$ blob[:12] lines
377ccd53da0c    24 src/agent_factory/decisions/__init__.py
607b65b613e2    78 src/agent_factory/decisions/canonical.py
20ebcd54f3ed   363 src/agent_factory/decisions/volatile.py
71fc398a5340   616 src/agent_factory/decisions/ledger.py
0afbf1b821ed   848 tests/test_decisions_canonical.py
4a8bccead05f  1534 tests/test_decisions_ledger.py
$ git log --format='%h %s' -3 -- src/agent_factory/decisions | cut -c1-110
f0e431f J1-1-R1 landed (task #139; GATED-PENDING-VERIFY): bound after redact, the widened secret classes in th
d4f4698 J1-2-R1 landed (GATED-PENDING-VERIFY): the decision ledger refuses short writes, closes its row shape 
9d11c25 Laya J1-2 landed (GATED-PENDING-VERIFY): the append-only decision ledger with mandatory provenance, ro
$ grep -n (the seams, volatile.py)
44:_BEARER = re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/-]{16,}=*")
45:_SK = re.compile(r"sk-[A-Za-z0-9_-]{8,}")
53:_TOKEN = re.compile(r"(?i)(?:\b|(?<=_))token[\"']?(?: ?[:=] ?| )?[\"']?([A-Za-z0-9+/]{32,})")
73:_ENVVAL = re.compile(r"(?P<name>(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY)=)\S+")
74:_ENVVAL_WIDE = re.compile(
82:_PRIVKEY = re.compile(
116:    return re.sub(r"--[0-9a-fA-F]{7,40}$", "", value)
122:    return re.sub(r"\s+", " ", s).strip()
322:def _redact_str(text: str) -> str:
328:    text = _PRIVKEY.sub(PLACEHOLDERS["privkey"], text)
329:    text = _SK.sub(PLACEHOLDERS["sk"], text)
330:    text = _BEARER.sub(PLACEHOLDERS["bearer"], text)
331:    text = _ENVVAL.sub(lambda m: m.group("name") + PLACEHOLDERS["envval"], text)
332:    text = _TOKEN.sub(lambda m: m.group(0).replace(m.group(1), PLACEHOLDERS["token"]), text)
333:    text = _ENVVAL_WIDE.sub(_envval_wide, text)
355:def decision_state(question_id: str, state: dict, root: str | os.PathLike | None = None) -> dict:
$ python3 -m pytest tests/test_decisions_canonical.py tests/test_decisions_ledger.py -q -p no:cacheprovider --basetemp /tmp/pm/bt | tail -1
72 passed in 2.47s
$ bash scripts/pc_suite.sh set-id -- tests/test_decisions_canonical.py tests/test_decisions_ledger.py
2 files set=16a7b628685e
$ python3 v1_rows.py   (the driver in the appendix, at the PIN)
LEAK V1-a task-password: (sk eats name)       -> 'set ta<redacted:sk>: QZJ8QZJ8QZJ8QZJ8QZJ8 now'
LEAK V1-b ask-password= (sk eats name)        -> 'set a<redacted:sk>=QZJ8QZJ8QZJ8QZJ8QZJ8 now'
LEAK V1-c quoted task-password                -> 'set "ta<redacted:sk>": "QZJ8QZJ8QZJ8QZJ8QZJ8" now'
LEAK V1-d desk-secret_key: (sk eats name)     -> 'set de<redacted:sk>: QZJ8QZJ8QZJ8QZJ8QZJ8 now'
LEAK V1-e flask-access_token= run             -> 'set fla<redacted:sk>=QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8 now'
LEAK V1-f disk-PASSWORD= short                -> 'set di<redacted:sk>=QZJ8QZ now'
LEAK V1-g bearer eats name                    -> 'set <redacted:bearer>: QZJ8QZJ8QZJ8QZJ8QZJ8 now'
LEAK V1-h sk- value then -password=           -> 'set <redacted:sk>=QZJ8QZJ8QZJ8QZJ8QZJ8 now'
ok   C-1 control mask-token: run              -> 'set mask-token: <redacted:token> now'
ok   C-2 control task-api_key:                -> 'set task-api_key: <redacted:envval> now'
ok   C-3 control db_password=                 -> 'set db_password=<redacted:envval> now'
ok   C-4 control bearer token then colon      -> 'set Authorization: <redacted:bearer>: rejected now'
ok   C-5 control plain sk key                 -> 'set key <redacted:sk> used now'
ok   C-6 control quoted sk key                -> 'set "<redacted:sk>" now'
replayed rows: 14 shapes: 14 leaking: 8
$ (option B, the verifier's section 11 patterns, on a scratch copy; the same driver)
LEAK V1-h sk- value then -password=           -> 'set <redacted:sk>=QZJ8QZJ8QZJ8QZJ8QZJ8 now'
LEAK C-4 control bearer token then colon      -> 'set Authorization: Bearer QZJ8QZJ8QZJ8QZJ8QZJ8: rejected now'
replayed rows: 14 shapes: 14 leaking: 2
$ (a class-form variant on a scratch copy, NOT a prescription; the same driver, then the two test files)
replayed rows: 14 shapes: 14 leaking: 0
72 passed in 2.55s
```

## Appendix — the premise driver (copy it to `/tmp/j11r2/v1_rows.py` and run it from the repo root; do not redesign it)
```python
"""V-1 premise driver: each shape as b1.finding_sev's msg, through make_row -> append -> the JSONL on disk -> replay.
FAKE value bodies only. Prints one line per shape: LEAK when the fake body is in the appended line on disk."""
import json, os, sys, tempfile
sys.path.insert(0, os.path.join(os.getcwd(), "src"))
from agent_factory.decisions.ledger import make_row, append, replay
V = "QZJ8" * 5            # 20-char fake value body
RUN = "QZJ8" * 10         # 40-char fake token run
G = json.load(open("tests/fixtures/decisions/golden/b1.finding_sev.json"))
SRC = {"kind": "incident_log", "path": "docs/INCIDENT-LOG.md", "source_digest": "a" * 64, "locator": "premise"}
ROWS = [
    ("V1-a task-password: (sk eats name)", f"task-password: {V}", V),
    ("V1-b ask-password= (sk eats name)", f"ask-password={V}", V),
    ("V1-c quoted task-password", f'"task-password": "{V}"', V),
    ("V1-d desk-secret_key: (sk eats name)", f"desk-secret_key: {V}", V),
    ("V1-e flask-access_token= run", f"flask-access_token={RUN}", RUN),
    ("V1-f disk-PASSWORD= short", "disk-PASSWORD=QZJ8QZ", "QZJ8QZ"),
    ("V1-g bearer eats name", f"bearer my-service-password: {V}", V),
    ("V1-h sk- value then -password=", f"sk-abcdefgh-password={V}", V),
    ("C-1 control mask-token: run", f"mask-token: {RUN}", RUN),
    ("C-2 control task-api_key:", f"task-api_key: {V}", V),
    ("C-3 control db_password=", f"db_password={V}", V),
    ("C-4 control bearer token then colon", f"Authorization: Bearer {V}: rejected", V),
    ("C-5 control plain sk key", f"key sk-{V} used", V),
    ("C-6 control quoted sk key", f'"sk-{V}"', V),
]
d = tempfile.mkdtemp(prefix="v1rows-", dir="/tmp")
led = os.path.join(d, "ledger.jsonl")
leaks = 0
for name, shape, body in ROWS:
    st = dict(G["state"]); st["msg"] = f"set {shape} now"
    row = make_row(producer="decide-harvest/incident-log", question_id="b1.finding_sev", raw_state=st,
                   incumbent_answer="accepted", source_ref=dict(SRC, locator=name), root=G.get("root"))
    append(led, row)
    line = open(led, encoding="utf-8").read().splitlines()[-1]
    leak = body in line
    leaks += leak
    print(f"{'LEAK' if leak else 'ok  '} {name:40s} -> {json.loads(line)['state']['msg']!r}")
print(f"replayed rows: {len(replay(led))} shapes: {len(ROWS)} leaking: {leaks}")
import shutil; shutil.rmtree(d)
```
