# J1-1-R2 report — a secret name that an earlier class consumes never frees its value (task #192)

LANE: j1-1-r2 (sandbox, `code-implementer`, shared tree, no worktree). Brief: `tasks/briefs/laya/J1-1-R2-brief.md`.
PIN d556c9b; origin head at start 98e2efc. Status: DONE in the sandbox, uncommitted (the coordinator commits). The eight V-1
rows close (`leaking: 0`), 0 new leaks in the 43-shape differential and in 160,000 byte-exact fuzz inputs, goldens unchanged,
`121 passed` on set `16a7b628685e`, 30 of 30 mutants killed. Read DISCREPANCIES D-1 and D-3 (section 12) first.

## 0. PREMISE — re-measured (item 1)

```
$ date -u +%Y-%m-%dT%H:%MZ
2026-09-23T14:06Z
$ git rev-parse --short origin/claude/soundbox-kit-migration-iz1jwf ; git rev-parse --short HEAD
98e2efc
98e2efc
$ git diff --quiet d556c9b -- src/agent_factory/decisions tests/test_decisions_canonical.py tests/test_decisions_ledger.py tests/fixtures/decisions && echo ...
identical PIN(d556c9b) vs worktree
identical origin(98e2efc) vs worktree
identical PIN vs origin (incl transcript_export)
$ blob[:12] lines (worktree)
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
```
Verdict: the boundary is byte-identical to the brief's blob table (all six ids match). No CONTRACT-INVALID stop.
Other lanes' dirt in the shared tree at start (NOT mine, untouched): `proofs/S0-02/**`, `tests/test_s0_02_buzz_authz.py`,
`tasks/briefs/s0-02-support/B10-report.md`, two `tasks/briefs/pc/*k1-h*` files.

The appendix driver, copied verbatim to `/tmp/j11r2/v1_rows.py` (lines 163-201 of the brief; sha256[:16] `76b471d70524727b`), run at
the PIN (the worktree equals the PIN on the boundary; `volatile from: /home/user/agent-factory/src/agent_factory/decisions/volatile.py`):
```
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
rc=0
$ /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_canonical.py tests/test_decisions_ledger.py -q -p no:cacheprovider --basetemp=/tmp/j11r2/bt/r0
72 passed in 2.44s
rc=0
$ bash scripts/pc_suite.sh set-id -- tests/test_decisions_canonical.py tests/test_decisions_ledger.py
2 files set=16a7b628685e
```
PREMISE: holds, byte for byte with the brief's block.

## 1. Design (measured before any test was written; scratch copies only)

Instruments: the pack (`scripts/lane_context.sh … -o /tmp/j11r2/pack.md`, rc=0, 176 lines). `_SK`/`_BEARER` impact is UNKNOWN in
GitNexus (module constants read by bare name); two other instruments agree on the readers: a literal sweep finds them only at
`src/agent_factory/decisions/volatile.py@d556c9b:329-330` (`_SK.sub`, `_BEARER.sub`), and `graft ask` names `redact` as the only caller of `_redact_str`. `_redact_str`:
LOW, 5 impacted, 2 flows (`make_row`, `append`).

**The rule (v2).** sk and bearer fire exactly where their PIN forms fire (`sk-` then 8+ run characters; `bearer`, whitespace, 16+),
so the prefix is always replaced. The replaced run ends before a secret assignment that a later class redacts: an upper-case
`NAME=` (`_ENVVAL`, any value but `=` padding), a name with `:`/`=` and an 8+ value (`_ENVVAL_WIDE`), or `token` with a quote or
space and a 32+ run (`_TOKEN`). It yields only when that value holds no further assignment head, because the value would swallow
the second name and free its value. Then the run keeps its PIN form.

Why each part, from measurement:
- **No left boundary on `sk-`.** The verifier's option B (`\bsk-` plus a bearer lookahead) newly exposes body bytes in 36 of
  3,000 fuzz inputs (below; for example `mask--56Z45…` stops being redacted). A boundary removes PIN redactions; V-1 does not need it.
- **Fire where the PIN fires; move only the end of the span.** A form that stays silent when the run yields (the floor applied
  to the truncated run) is not a fixed point under the bound cut: `task-password: v` at the PIN gives `task-password: <envval>`,
  and a cut right after `password` makes the second pass redact `sk-password`. Replacing the prefix in every case keeps the second
  pass silent. Mutant m4g below measures it.
- **The value condition.** Without it, a token whose tail spells a name (`Bearer QZJ8QZJ8QZJ8Qkey: ok`) is split, and `key` shows
  for nothing. With it, the output is the PIN's.
- **The chain guard (v1 had none).** The v1 prototype (yield on any assignment) closed the 14 driver rows and the 43-shape
  differential, but the byte-exact fuzz found 6 of 120,000 inputs with NEW body exposure. Example:
  `flask-tapasswd=aAPI_KEY : X4Z9…` — the PIN's sk ate `sk-tapasswd`, so the widened class later found `API_KEY : X4Z9…`. v1 yielded
  to `passwd=`, whose value `aAPI_KEY` swallowed the second name, and `X4Z9…` showed. The same chain leaks at the PIN with no sk
  prefix (a pre-existing gap of the widened value, reported below as F-1, not fixed here):
```
'passwd=aAPI_KEY : X4Z92Q0X1ZX02Z71' -> 'passwd=<redacted:envval> : X4Z92Q0X1ZX02Z71'
"token='_API_KEY = 6Z4Z02ZX6Z4Z" -> "token='<redacted:envval> = 6Z4Z02ZX6Z4Z"
"password='-db_password: 62669Q3JJ88ZX5466" -> "password='<redacted:envval> 62669Q3JJ88ZX5466"
'key: service-API_KEY: QZJ8QZJ8QZJ8' -> 'key: <redacted:envval> QZJ8QZJ8QZJ8'
```
  v2 does not yield when the value holds a head, so on a chain it gives the PIN's output byte for byte.

**Why v2 cannot expose a body byte the PIN redacts (by construction, then measured).** Where v2 does not yield, the match equals
the PIN's. Where it yields, the later classes (`_ENVVAL`, `_TOKEN`, `_ENVVAL_WIDE`, which run after sk and bearer) take the name and
replace its value. The guard means no head starts inside that value or straddles its end, so every match the PIN's later passes
made lies after the value and is made the same way. The only bytes that can newly show are the name that the run no longer covers
(and a following `=` that the PIN's `=*` padding covered).

**The byte-exact differential fuzz** (`/tmp/j11r2/tools/fuzz_diff.py`). Each real pattern is wrapped by a proxy whose `.sub` runs
the real pattern's `finditer` and the real replacement, and tracks which ORIGINAL characters survive. The proxy output is asserted
equal to the real `_redact_str` output. Body bytes = `Q Z J X 0-9`; no name, separator, placeholder or filler holds one. The
generator mixes names (31 spellings, prefixed and glued), sk/bearer prefixes, 20 separators, bodies of 1-48 characters,
placeholders and cut placeholders.
```
control 1, PIN vs PIN:      inputs=3000 seed=1 outputs_differ=0 new_body_exposure_inputs=0 nonbody_bytes_kept_inputs=0
control 2, PIN vs option B: inputs=3000 seed=1 outputs_differ=74 new_body_exposure_inputs=36 nonbody_bytes_kept_inputs=74
v1 (no chain guard):        seeds 1/2/3, 40000 each: new_body_exposure_inputs=2 / 3 / 1
v2 (the design):            inputs=40000 seed=1 outputs_differ=131 new_body_exposure_inputs=0 nonbody_bytes_kept_inputs=129
                            inputs=40000 seed=2 outputs_differ=122 new_body_exposure_inputs=0 nonbody_bytes_kept_inputs=118
                            inputs=40000 seed=3 outputs_differ=139 new_body_exposure_inputs=0 nonbody_bytes_kept_inputs=138
v2, every non-body run it keeps that the PIN replaced (seed 1): {'password': 28, 'secret': 14, 'key': 13, 'token': 9,
  'KEY': 8, 'API_KEY': 7, 'PASSWORD': 7, 'APIKEY': 6, 'Password': 6, 'apikey': 5, 'Token': 4, 'PASSWD': 4, 'password=': 2,
  'passwd': 2, 'Key': 2, 'api_key': 2, 'TOKEN': 2, 'SECRET': 2, 'PASSWORD=': 1, 'token=': 1, 'APIKEY=': 1, 'Password=': 1,
  'TOKEN=': 1, 'secret=': 1}   (seeds 2 and 3: the same set of words; pasted in section 8)
```

## 2. What changed (files:lines, final tree)

- `src/agent_factory/decisions/volatile.py:4`: the module docstring names `AMENDMENT 2, D-057` (the sk and bearer class forms).
- `src/agent_factory/decisions/volatile.py:45-56`: the comment that states the rule (`# sk and bearer (AMENDMENT 2, D-057`).
- `src/agent_factory/decisions/volatile.py:57`: `_SECRET_NAME`, the six secret names, case-blind.
- `src/agent_factory/decisions/volatile.py:61`: `_ASSIGNMENT_HEAD`, the start of an assignment a later class could take.
- `src/agent_factory/decisions/volatile.py:62`: `_ENVVAL_HEAD`, the upper-case `NAME=` head.
- `src/agent_factory/decisions/volatile.py:67-73`: `_YIELD`, the three assignments sk and bearer yield to, each with its value condition and chain guard.
- `src/agent_factory/decisions/volatile.py:74-76`: `_BEARER`, the new bearer form.
- `src/agent_factory/decisions/volatile.py:77`: the new sk form, _SK (`sk-(?=[A-Za-z0-9_-]{8})`).
- Nothing else in `volatile.py` changed (section 4 measures it): `_redact_str`, the placeholders, the other classes, `bound`, the schemas, the limits.
- `tests/test_decisions_canonical.py:18`: the docstring's contract line names `tasks/briefs/laya/J1-1-R2-brief.md (B1-B5)`.
- `tests/test_decisions_canonical.py:853`: the section header `# J1-1-R2 -- AMENDMENT 2 to J1-1`; the section runs to line 1060 (35 new test items).
- `tests/test_decisions_ledger.py:1538`: the section header `# J1-1-R2 (D-057, B1 + B2)`; the section runs to line 1612 (14 new test items).

The new tests (41 items at the first red run, 49 final; every body FAKE `QZJ8…` or `QZXJ…`):
- `test_v1_name_swallowed_by_sk_or_bearer_frees_no_value[V1-a..V1-h]` (8): at `decision_state`, no byte of the value body
  (`Q Z J 8`, one character at a time) in the output or `canonical()` of it, `abcdefgh` (V1-h's sk value) absent, the exact
  redacted text, a fixed point, and two different fake values hash the same.
- `test_v1_control_keeps_its_pin_redaction[C-1..C-6]` (6): the same checks, green at both; the negative control is a mutant.
- `test_v1_class_beyond_the_driver[…]` (19): ten more V-1-class shapes that leak at the PIN (the SECRET, PASSWD and API_KEY
  names after a prefix; V1-f's upper-case `NAME=` short-value form under KEY, TOKEN, SECRET, PASSWD and API_KEY; the token
  class's space form under sk and under bearer) and nine guard rows that keep the PIN's own output (three chain guards plus
  two more chain shapes, no value, a lower-case `=`, `=` padding, `token` with no 32+ run).
- `test_v1_rows_straddle_every_bounded_key_and_stay_fixed_points` (1): each V-1 text straddles every bounded key's limit at
  every cut; no body byte, the digest equals the value-placeholder form's, every field within its limit, a fixed point.
- `test_verifier_shapes_keep_every_pin_redaction` (1): the verifier's 43 shapes rebuilt; the 35 that are body-free after
  (27 the PIN redacts, 8 V-1 rows) stay body-free and are fixed points.
- `test_v1_row_no_value_byte_reaches_the_ledger_file[V1-a..V1-h]` (8) and
  `test_v1_control_keeps_its_redaction_in_the_ledger_file[C-1..C-6]` (6): the brief's appendix driver as tests, through the real
  `make_row` then `append`, then the JSONL file's bytes (no upper-case `Q Z J`), then `replay` accepts the row.

## 3. RED at the PIN, GREEN after

Two defects of MY test data were caught by running the controls at the PIN before counting anything, and fixed: the ledger
locator `"the J1-1-R2 driver"` held a `J` (every ledger control went red on `['J']`), and a guard row's filler `abcdefgh`
collided with the V1-h check. Both runs below use the final test files.

RED: a scratch copy whose `volatile.py` is the PIN blob, with the final test files (`/tmp/j11r2/pinnew`), 2026-09-23T14:44:45Z:
```
20ebcd54f3ed src/agent_factory/decisions/volatile.py
2502a4e3abb0 tests/test_decisions_canonical.py
6648679bd40a tests/test_decisions_ledger.py
FAILED tests/test_decisions_canonical.py::test_v1_name_swallowed_by_sk_or_bearer_frees_no_value[V1-a]   (… V1-b … V1-h: 8)
FAILED tests/test_decisions_canonical.py::test_v1_class_beyond_the_driver[name-secret]
FAILED tests/test_decisions_canonical.py::test_v1_class_beyond_the_driver[name-passwd]
FAILED tests/test_decisions_canonical.py::test_v1_class_beyond_the_driver[name-api_key]
FAILED tests/test_decisions_canonical.py::test_v1_class_beyond_the_driver[token-space-sk]
FAILED tests/test_decisions_canonical.py::test_v1_class_beyond_the_driver[token-space-bearer]
FAILED tests/test_decisions_canonical.py::test_v1_rows_straddle_every_bounded_key_and_stay_fixed_points
FAILED tests/test_decisions_canonical.py::test_verifier_shapes_keep_every_pin_redaction
FAILED tests/test_decisions_ledger.py::test_v1_row_no_value_byte_reaches_the_ledger_file[V1-a]   (… V1-b … V1-h: 8)
23 failed, 93 passed in 3.03s
rc=1
```
Each failure's reason (the first red run, `--tb=line`, the same set): `value body bytes ['8', 'J', 'Q', 'Z'] in '{"file":"src/a.py",
"kind":"k","msg":"set ta<redacted:sk>: QZJ8QZJ8…` (canonical), `value body bytes ['J', 'Q', 'Z'] reached the ledger file` (ledger),
`b2.hit_role.sym V1-a k=18: the straddling value does not hash as its placeholder form` (the straddle sweep). The 93 that pass:
the PIN's 72, the 12 controls (6 per file) and the 9 guard rows, which pin the PIN's own output by design.

GREEN: the shared tree, the brief's gate command, 2026-09-23T14:44:59Z:
```
bf04415d72c1   395 src/agent_factory/decisions/volatile.py
2502a4e3abb0  1054 tests/test_decisions_canonical.py
6648679bd40a  1612 tests/test_decisions_ledger.py
$ mkdir -p /tmp/j11r2/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_canonical.py tests/test_decisions_ledger.py -q -p no:cacheprovider --basetemp=/tmp/j11r2/bt/r1 -rA
116 passed in 3.77s
r1-rc=0
$ (the same, --basetemp=/tmp/j11r2/bt/r2)
116 passed in 3.65s
r2-rc=0
g1: 116 PASSED lines, sha=c0e7335e8738aabd
g2: 116 PASSED lines, sha=c0e7335e8738aabd
$ bash scripts/pc_suite.sh set-id -- tests/test_decisions_canonical.py tests/test_decisions_ledger.py
2 files set=16a7b628685e
```
The PIN's `72 passed` rises to `116 passed` on the same set id; no test was skipped or deleted. No regression: the PIN's own
test files (blobs `0afbf1b821ed`, `4a8bccead05f`, unmodified) against the new `volatile.py` (`bf04415d72c1`), in `/tmp/j11r2/pintests`:
`72 passed in 2.37s`, rc=0.

The test files grew once more after the section-3 runs: five rows (`upper-*-short`) killed five survivors of the first mutation
run (section 9), four guard rows were added and three separator rows were rewritten from literal NBSP/U+3000 characters to
` `/`　` escapes (same strings). The FINAL runs, on the final files:
```
RED  (the PIN's volatile.py 20ebcd54f3ed; tests 440ac2426d8f / 6648679bd40a), 2026-09-23T14:52:20Z:
     28 failed, 93 passed in 2.62s   rc=1
     failed = the 8 V1 rows at decision_state, the 10 leaking class rows (name-secret, name-passwd, name-api_key,
     upper-{key,token,secret,passwd,api_key}-short, token-space-sk, token-space-bearer), the straddle sweep, the
     43-shape test, and the 8 V1 rows through the ledger
GREEN (the shared tree; volatile.py bf04415d72c1, 395 lines; tests 440ac2426d8f 1060 lines / 6648679bd40a 1612 lines),
     2026-09-23T14:52:32Z:
     $ /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_canonical.py tests/test_decisions_ledger.py -q -p no:cacheprovider --basetemp=/tmp/j11r2/bt/r1 -rA
     121 passed in 3.93s   r1-rc=0
     $ (the same, --basetemp=/tmp/j11r2/bt/r2)
     121 passed in 3.73s   r2-rc=0
     g1: 121 PASSED lines, sha=2475237d4d259cce
     g2: 121 PASSED lines, sha=2475237d4d259cce
     $ bash scripts/pc_suite.sh set-id -- tests/test_decisions_canonical.py tests/test_decisions_ledger.py
     2 files set=16a7b628685e
```
Counts: the PIN `72 passed` -> `121 passed` on set `16a7b628685e`. The 49 new items: 35 in the canonical file (8 V1 rows +
6 controls + 19 class rows + the straddle sweep + the 43-shape test) and 14 in the ledger file (8 V1 rows + 6 controls);
72 + 35 + 14 = 121. None skipped, none deleted.

## 4. Per contract line (B1-B5): where it lives and what pins it

**B1: the eight V-1 rows close.**
- `_YIELD` at `src/agent_factory/decisions/volatile.py:67-73`: the assignments the sk and bearer runs stop before.
- `_BEARER` at `src/agent_factory/decisions/volatile.py:74-76` and, on the next line, `_SK`, both tempered by `_YIELD`.
- `_SK` at `src/agent_factory/decisions/volatile.py:77` (`sk-(?=[A-Za-z0-9_-]{8})`, then the run tempered by `_YIELD`).
- The passes are unchanged: `_SK.sub` at `src/agent_factory/decisions/volatile.py:361`.
- `_BEARER.sub` at `src/agent_factory/decisions/volatile.py:362`, right after it (the order privkey, sk, bearer, env, token, widened stays).
- Pinned by `test_v1_name_swallowed_by_sk_or_bearer_frees_no_value` at `tests/test_decisions_canonical.py:945` (8 items).
- Pinned by `test_v1_row_no_value_byte_reaches_the_ledger_file` at `tests/test_decisions_ledger.py:1600` (8 items).
- Pinned by `test_v1_rows_straddle_every_bounded_key_and_stay_fixed_points` at `tests/test_decisions_canonical.py:988`.
- The appendix driver after: `leaking: 0` (section 5).

**B2: no new leak.** Each class fires where its PIN form fires (the lookaheads `(?=[A-Za-z0-9_-]{8})` in `_SK` and
`(?=[A-Za-z0-9._~+/-]{16})` in `_BEARER`); no left boundary; the value conditions and the three chain guards in `_YIELD`.
- Pinned by `test_v1_control_keeps_its_pin_redaction` at `tests/test_decisions_canonical.py:954` (C-1 … C-6).
- Pinned by `test_v1_control_keeps_its_redaction_in_the_ledger_file` at `tests/test_decisions_ledger.py:1609` (C-1 … C-6).
- Pinned by `test_v1_class_beyond_the_driver` at `tests/test_decisions_canonical.py:965` (its nine guard rows).
- Pinned by `test_verifier_shapes_keep_every_pin_redaction` at `tests/test_decisions_canonical.py:1050` (35 shapes).
- Measured: the 43-shape differential (section 6) and the byte-exact fuzz (sections 1 and 6).

**B3: the class forms only.** The diff has two hunks, the docstring and the class block (section 2). The pass order is unchanged,
so bearer stays ahead of the upper-case `NAME=value` class (`PASSWORD=Bearer …` stays redacted in the 43-shape test). The
PIN's own 72 tests pass unmodified against the new code. Measured below.

**B4: the identity rules.** Idempotence by construction: the prefix is always replaced where the PIN fires. Pinned by the
fixed-point assertion in every new row test, by the straddle sweep at every cut (it kills m4g on `V1-a k=13: not idempotent`),
and by the unchanged golden tests:
- `test_golden_digests_exact` at `tests/test_decisions_canonical.py:66`.
- `test_relanding_stable` at `tests/test_decisions_canonical.py:89`.
- Measured: the idempotence fuzz (section 7) and the golden digests (section 9).

**B5: linear cost.** Bounded lookaheads; a run holds at most one name that a separator follows. Measured in section 8.
- `test_env_assignment_redaction_does_not_backtrack_exponentially` at `tests/test_decisions_canonical.py:637` stays green.

B3 measured (two module loads, the PIN copy and the shared tree):
```
_TOKEN pattern identical to the PIN: True          _redact_str source identical to the PIN: True
_ENVVAL pattern identical to the PIN: True         _envval_wide source identical to the PIN: True
_ENVVAL_WIDE pattern identical to the PIN: True    redact / bound / normalize / decision_state source identical: True
_PRIVKEY pattern identical to the PIN: True        PLACEHOLDERS identical: True | limits: True
SCHEMAS identical by field values: True            (a plain == reads False: two loads make two _Field classes)
$ git diff -U0 -- src/agent_factory/decisions/volatile.py | grep -c '^@@'
2
```

## 5. The appendix driver, before and after

Before: section 0 (`replayed rows: 14 shapes: 14 leaking: 8`). After, on the shared tree:
```
volatile from: /home/user/agent-factory/src/agent_factory/decisions/volatile.py
ok   V1-a task-password: (sk eats name)       -> 'set ta<redacted:sk>password: <redacted:envval> now'
ok   V1-b ask-password= (sk eats name)        -> 'set a<redacted:sk>password=<redacted:envval> now'
ok   V1-c quoted task-password                -> 'set "ta<redacted:sk>password": "<redacted:envval>" now'
ok   V1-d desk-secret_key: (sk eats name)     -> 'set de<redacted:sk>key: <redacted:envval> now'
ok   V1-e flask-access_token= run             -> 'set fla<redacted:sk>token=<redacted:token> now'
ok   V1-f disk-PASSWORD= short                -> 'set di<redacted:sk>PASSWORD=<redacted:envval> now'
ok   V1-g bearer eats name                    -> 'set <redacted:bearer>password: <redacted:envval> now'
ok   V1-h sk- value then -password=           -> 'set <redacted:sk>password=<redacted:envval> now'
ok   C-1 control mask-token: run              -> 'set mask-token: <redacted:token> now'
ok   C-2 control task-api_key:                -> 'set task-api_key: <redacted:envval> now'
ok   C-3 control db_password=                 -> 'set db_password=<redacted:envval> now'
ok   C-4 control bearer token then colon      -> 'set Authorization: <redacted:bearer>: rejected now'
ok   C-5 control plain sk key                 -> 'set key <redacted:sk> used now'
ok   C-6 control quoted sk key                -> 'set "<redacted:sk>" now'
replayed rows: 14 shapes: 14 leaking: 0
rc=0
```
The names stay after the sk/bearer placeholder (`ta<redacted:sk>password`): the prefix keeps its PIN placeholder by design
(section 1). The over-redaction of the name's prefix is C-F2's, filed; it frees no byte.

## 6. The 43-shape differential (B2)

`/tmp/j11r2/tools/d43.py` rebuilds the table's shapes; each goes through `make_row` then `append`, is read back from the JSONL
line, and is fed to `decision_state` again; `replay` checks the whole file. Rebuild fidelity: at the PIN, all 43 `msg` outputs
equal the verifier's printed outputs (`PIN rows faithful to the verifier table: 43 of 43`; the PEM row compared on its printed
prefix), and `leaking cases: 16`, as in the table.
```
 # shape (verifier table name)              PIN   after idem same msg
 1 password: sk-                            ok    ok    True True
 2 KEY=sk-                                  ok    ok    True True
 3 token = run-b64url tail                  ok    ok    True True
 4 password: Bearer                         ok    ok    True True
 5 PASSWORD=Bearer                          ok    ok    True True
 6 api_key="Bearer .."                      ok    ok    True True
 7 TOKEN: Bearer                            ok    ok    True True
 8 literal placeholder in prose             ok    ok    True True
 9 password: literal placeholder            ok    ok    True True
10 KEY=literal placeholder                  ok    ok    True True
11 two secrets: password + token            ok    ok    True True
12 two secrets: sk + Bearer                 ok    ok    True True
13 two secrets: API_KEY= + password:        ok    ok    True True
14 two secrets glued by comma               ok    ok    True True
15 tab separator                            ok    ok    True True
16 NBSP separator                           ok    ok    True True
17 NBSP before colon                        ok    ok    True True
18 ideographic space                        ok    ok    True True
19 full-width colon                         LEAK  LEAK  True True
20 full-width equals                        LEAK  LEAK  True True
21 full-width equals, token run             LEAK  LEAK  True True
22 zero-width space before colon            LEAK  LEAK  True True
23 two spaces (collapsed by normalize)      ok    ok    True True
24 SK- upper                                LEAK  LEAK  True True
25 Sk- mixed                                LEAK  LEAK  True True
26 BEARER upper                             ok    ok    True True
27 bEaReR mixed                             ok    ok    True True
28 ToKeN mixed run                          ok    ok    True True
29 Password= mixed                          ok    ok    True True
30 Api_Key: mixed                           ok    ok    True True
31 Password= 7 chars                        LEAK  LEAK  True True
32 lower-case PEM label                     LEAK  LEAK  True True
33 task-password: (sk eats name)            LEAK  ok    True False
34 ask-password= (sk eats name)             LEAK  ok    True False
35 "task-password": ".."                    LEAK  ok    True False
36 desk-secret_key: (sk eats name)          LEAK  ok    True False
37 flask-access_token= run (sk eats name)   LEAK  ok    True False
38 disk-PASSWORD= short (PIN form)          LEAK  ok    True False
39 bearer eats name                         LEAK  ok    True False
40 sk- value then -password=                LEAK  ok    True False
41 control mask-token: run                  ok    ok    True True
42 control task-api_key:                    ok    ok    True True
43 control db_password=                     ok    ok    True True
PIN rows faithful to the verifier table: 43 of 43
ok -> LEAK: 0 | LEAK -> ok: 8 | LEAK -> LEAK: 8 | ok rows with a changed msg: 0 | non-idempotent after: 0
```
`replayed rows: 43 cases: 43 leaking cases: 8` after (16 at the PIN). The 8 left are V-6 (rows 19-22) and V-7 (24, 25, 31, 32),
filed follow-ups outside this repair. Beyond the table: the byte-exact fuzz (section 1; plus seed 4 on the shared-tree file:
`inputs=40000 seed=4 outputs_differ=130 new_body_exposure_inputs=0 nonbody_bytes_kept_inputs=128`, the kept runs again only
name words and a following `=`), and 0 of 73 golden and 0 of 3,102 J0 probe string values whose redaction changes:
```
golden: string values=73 redaction changed vs the PIN=0 values the new redact changes at all=0
probe: string values=3102 redaction changed vs the PIN=0 values the new redact changes at all=0
```

## 7. Idempotence (B4)

- Every driver row and every rebuilt shape: `idem=True` (sections 5 and 6); `replay` re-runs the fixed-point check
  (`restate = decision_state(qid, row["state"], None)` at `src/agent_factory/decisions/ledger.py:273`) on every row: 14 and 43 replayed.
- The straddle sweep asserts the fixed point at every cut of every V-1 text at all 16 bounded keys (more than 3,000 cases).
- A random fuzz (`/tmp/j11r2/tools/idem_fuzz.py`: the fuzz generator's texts, 80 % padded to straddle a bounded key's limit):
```
PIN:    states=60000 seed=11 refused=0 non-idempotent (new)=0 D-2 (known lane PIN suffix)=0
        states=60000 seed=12 refused=0 non-idempotent (new)=0 D-2 (known lane PIN suffix)=0
after:  states=60000 seed=11 refused=0 non-idempotent (new)=0 D-2 (known lane PIN suffix)=0
        states=60000 seed=12 refused=0 non-idempotent (new)=0 D-2 (known lane PIN suffix)=0
control, the fuzz on mutant m4g (the floor on the truncated run):
        states=60000 seed=11 refused=0 non-idempotent (new)=11 D-2 (known lane PIN suffix)=0
```

## 8. Cost (B5)

`/tmp/j11r2/tools/cost.py` (the verifier's section-5 method: best of 3 full `.sub` scans under a 5 s SIGALRM, max-ratio =
the largest t(n)/t(n/2) from 16k up). The shared-tree file, 2026-09-23T14:5xZ:
```
pattern / input                                                      4k       8k      16k      32k      64k     128k   (ms)
_SK: 'sk-' then one long run                                       0.67     1.28     2.38     4.88    10.17    21.03  max-ratio(>=16k)=2.09
_SK: 'sk-' repeated                                                0.63     1.17     2.31     4.94     9.66    24.75  max-ratio(>=16k)=2.56
_SK: 'sk-' + 'password' run (names, no separator)                  0.85     1.39     2.60     5.42    10.77    29.70  max-ratio(>=16k)=2.76
_SK: 'sk-' + '_token' run                                          0.64     1.34     2.72     5.31    11.08    23.20  max-ratio(>=16k)=2.09
_SK: 'sk-' + 'api_' run                                            0.64     1.26     2.53     5.15    10.19    21.85  max-ratio(>=16k)=2.15
_SK: one yield, a long widened value (chain scan)                  0.48     0.92     1.84     3.78     7.63    15.02  max-ratio(>=16k)=2.05
_SK: one yield, a long NAME= value (chain scan)                    0.43     0.85     1.76     3.43     6.88    14.36  max-ratio(>=16k)=2.09
_SK: one yield, a long token-space run (chain scan)                0.44     0.87     1.78     3.58     7.17    14.47  max-ratio(>=16k)=2.02
_SK: a widened value of 'key' runs (chain scan)                    0.57     1.10     2.23     4.45     8.87    17.88  max-ratio(>=16k)=2.02
_SK: 'sk-abcdpassword=' repeated (chained)                         0.91     1.72     3.44     6.98    13.79    31.10  max-ratio(>=16k)=2.26
_SK: 'sk-abcdpassword=QZJ8QZJ8 ' repeated                          0.34     0.70     1.41     3.02     5.73    11.93  max-ratio(>=16k)=2.15
_SK: 'sk-abcdpassword: ' + value + chained name                    0.50     0.99     1.94     4.01     7.92    15.92  max-ratio(>=16k)=2.07
_BEARER: 'bearer ' then one long run                               0.63     1.23     2.40     4.89     9.84    19.46  max-ratio(>=16k)=2.03
_BEARER: 'bearer ' repeated                                        0.06     0.11     0.22     0.44     0.87     1.78  max-ratio(>=16k)=2.05
_BEARER: 'bearer x' repeated                                       0.05     0.10     0.21     0.40     0.83     1.67  max-ratio(>=16k)=2.06
_BEARER: 'bearer ' + 'password' run                                0.67     1.35     2.63     5.48    11.29    22.06  max-ratio(>=16k)=2.08
_BEARER: 'bearer ' + whitespace run + 'x'                          0.09     0.18     0.38     0.78     1.49     3.04  max-ratio(>=16k)=2.04
_BEARER: one yield, a long widened value                           0.47     0.96     1.89     3.85     7.74    15.18  max-ratio(>=16k)=2.04
_BEARER: 'Bearer <16>key: <8>' repeated                            0.40     0.88     1.70     3.43     6.67    13.35  max-ratio(>=16k)=2.02
_BEARER: 'bearer abcdefghijklmnop-token ' + run                    0.45     0.93     1.89     3.85     7.64    15.38  max-ratio(>=16k)=2.04
--- end to end, the whole _redact_str, every generator at 64k and 128k (s)
  'sk-abcdpassword: ' + value + chained name                 64k 0.0221 s   128k 0.0307 s
  'sk-abcdpassword=' repeated (chained)                      64k 0.0200 s   128k 0.0400 s
  'sk-abcdpassword=QZJ8QZJ8 ' repeated                       64k 0.0160 s   128k 0.0327 s
  'Bearer <16>key: <8>' repeated                             64k 0.0147 s   128k 0.0285 s
  a widened value of 'key' runs (chain scan)                 64k 0.0119 s   128k 0.0244 s
worst max-ratio(>=16k) over 20 generators: 2.76
```
The two ratios above 2.2 are one 64k->128k step each; the same generators on the byte-identical prototype read 2.07 and 2.07, and
a re-measure (best of 9, out to 256k, load average 0.8) is linear:
```
'sk-' + 'password' run     32k..256k ms: 5.34 10.57 21.72 45.85  ratios: 1.98 2.05 2.11
'sk-' repeated             32k..256k ms: 4.76 9.44 19.33 39.74  ratios: 1.98 2.05 2.06
```
The price, disclosed: the PIN forms scan a 128k sk run in 0.23 ms, the new form in about 21 ms (each run character evaluates
`_YIELD`); the worst whole `_redact_str` input is 0.040 s at 128k (the PIN's worst on the same generators: 0.0169 s). Both linear.
`test_env_assignment_redaction_does_not_backtrack_exponentially` stays green (in the 121).

## 9. Golden digests (unchanged; no fixture touched)
```
ap.violates_row.json       committed=594584bde9869086 now(state)=594584bde9869086 now(variant)=594584bde9869086 unchanged=True
b1.finding_kind.json       committed=9e18ed7e5146a2c3 now(state)=9e18ed7e5146a2c3 now(variant)=9e18ed7e5146a2c3 unchanged=True
b1.finding_sev.json        committed=8c42d5dd1e8c349e now(state)=8c42d5dd1e8c349e now(variant)=8c42d5dd1e8c349e unchanged=True
b2.hit_role.json           committed=3ced4cd39a61faa5 now(state)=3ced4cd39a61faa5 now(variant)=3ced4cd39a61faa5 unchanged=True
d1.bug_echo_scores.json    committed=5a8c4ad2659c0e6b now(state)=5a8c4ad2659c0e6b now(variant)=5a8c4ad2659c0e6b unchanged=True
v1.finding_class.json      committed=f41a299c4a38ab30 now(state)=f41a299c4a38ab30 now(variant)=f41a299c4a38ab30 unchanged=True
wf.drift.json              committed=a51a56c48e98cca6 now(state)=a51a56c48e98cca6 now(variant)=a51a56c48e98cca6 unchanged=True
```
(`unchanged=True` also requires the digest to be one of the test constants in `tests/test_decisions_canonical.py`.)

## 10. Mutation audit (scratch copies of the final tree only; `/tmp/j11r2/tools/mut.py`)

Per mutant: a fresh copy of `/tmp/j11r2/final` (the three boundary files byte-identical to the shared tree, plus a scratch-only
`tests/test_zz_import_path.py` that asserts the copy imports its own `src`; no `__pycache__` copied), an exact-count edit of
`volatile.py` (count asserted 1), `py_compile`, the collection count equal to the baseline (AF-AP-78), the run, then every killing
test re-run on the UNMUTATED copy (AF-AP-138). Final run 2026-09-23T14:52:47Z to 14:55:16Z, on the final test files:
```
BASELINE (unmutated copy): rc=0 122 passed in 3.74s collected=122
kills credited (unmutated rerun rc=0): 30 | reruns not green: 0 | survivors: 0
```
Abbreviations: `c::` = `tests/test_decisions_canonical.py::`, `l::` = `tests/test_decisions_ledger.py::`; `v1row` =
`test_v1_name_swallowed_by_sk_or_bearer_frees_no_value`, `control` = `test_v1_control_keeps_its_pin_redaction`, `class` =
`test_v1_class_beyond_the_driver`, `straddle` = `test_v1_rows_straddle_every_bounded_key_and_stay_fixed_points`, `shapes43` =
`test_verifier_shapes_keep_every_pin_redaction`, `ledger-v1row` = `test_v1_row_no_value_byte_reaches_the_ledger_file`,
`ledger-control` = `test_v1_control_keeps_its_redaction_in_the_ledger_file`.

| id | mutant | run (mutated; collected 122/122, compile ok) | killing tests | unmutated re-run |
|---|---|---|---|---|
| m1 | _SK back to its PIN form | 25 failed, 97 passed :: KILLED | c::class[name-api_key], c::class[name-passwd], c::class[name-secret], c::class[token-space-sk], c::class[upper-api_key-short], c::class[upper-key-short], c::class[upper-passwd-short], c::class[upper-secret-short], c::class[upper-token-short], c::v1row[V1-a], c::v1row[V1-b], c::v1row[V1-c], c::v1row[V1-d], c::v1row[V1-e], c::v1row[V1-f], c::v1row[V1-h], c::straddle, c::shapes43, l::ledger-v1row[V1-a], l::ledger-v1row[V1-b], l::ledger-v1row[V1-c], l::ledger-v1row[V1-d], l::ledger-v1row[V1-e], l::ledger-v1row[V1-f], l::ledger-v1row[V1-h] | rc=0 25 passed |
| m2 | _BEARER back to its PIN form | 5 failed, 117 passed :: KILLED | c::class[token-space-bearer], c::v1row[V1-g], c::straddle, c::shapes43, l::ledger-v1row[V1-g] | rc=0 5 passed |
| m3 | the verifier's option-B bearer guard in place of mine (report section 11, exact) | 6 failed, 116 passed :: KILLED | c::class[no-value], c::class[token-space-bearer], c::control[C-4], c::v1row[V1-g], c::straddle, l::ledger-control[C-4] | rc=0 6 passed |
| m4a | _YIELD without the upper-case NAME= branch | 9 failed, 113 passed :: KILLED | c::class[upper-api_key-short], c::class[upper-key-short], c::class[upper-passwd-short], c::class[upper-secret-short], c::class[upper-token-short], c::v1row[V1-f], c::straddle, c::shapes43, l::ledger-v1row[V1-f] | rc=0 9 passed |
| m4b | _YIELD without the widened-form branch | 19 failed, 103 passed :: KILLED | c::class[name-api_key], c::class[name-passwd], c::class[name-secret], c::v1row[V1-a], c::v1row[V1-b], c::v1row[V1-c], c::v1row[V1-d], c::v1row[V1-e], c::v1row[V1-g], c::v1row[V1-h], c::straddle, c::shapes43, l::ledger-v1row[V1-a], l::ledger-v1row[V1-b], l::ledger-v1row[V1-c], l::ledger-v1row[V1-d], l::ledger-v1row[V1-e], l::ledger-v1row[V1-g], l::ledger-v1row[V1-h] | rc=0 19 passed |
| m4c | _YIELD without the token space-form branch | 2 failed, 120 passed :: KILLED | c::class[token-space-bearer], c::class[token-space-sk] | rc=0 2 passed |
| m4d1 | the widened branch without its chain guard | 1 failed, 121 passed :: KILLED | c::class[chain-widened] | rc=0 1 passed |
| m4d2 | the NAME= branch without its chain guard | 3 failed, 119 passed :: KILLED | c::class[chain-upper-past-a-stop], c::class[chain-upper-token-space], c::class[chain-upper] | rc=0 3 passed |
| m4d3 | the token branch without its chain guard | 1 failed, 121 passed :: KILLED | c::class[chain-token-run] | rc=0 1 passed |
| m4e | the widened branch without its 8+ value condition | 2 failed, 120 passed :: KILLED | c::class[lower-equals], c::class[no-value] | rc=0 2 passed |
| m4e3 | the token branch without its 32+ run condition | 2 failed, 120 passed :: KILLED | c::class[chain-token-run], c::class[token-space-no-run] | rc=0 2 passed |
| m4f | the NAME= branch accepts '=' padding as a value | 1 failed, 121 passed :: KILLED | c::class[padding] | rc=0 1 passed |
| m4g | _SK: the floor on the truncated run (silent when it yields) | 11 failed, 111 passed :: KILLED | c::class[name-api_key], c::class[name-passwd], c::class[name-secret], c::class[token-space-sk], c::v1row[V1-a], c::v1row[V1-b], c::v1row[V1-c], c::v1row[V1-d], c::v1row[V1-e], c::v1row[V1-f], c::straddle | rc=0 11 passed |
| m4g2 | _BEARER: the floor on the truncated run | 2 failed, 120 passed :: KILLED | c::v1row[V1-g], c::straddle | rc=0 2 passed |
| m4h | the widened branch without its NAME= exclusion | 1 failed, 121 passed :: KILLED | c::class[chain-upper-past-a-stop] | rc=0 1 passed |
| m4i | _ASSIGNMENT_HEAD without its token alternative | 1 failed, 121 passed :: KILLED | c::class[chain-upper-token-space] | rc=0 1 passed |
| m4j | _ASSIGNMENT_HEAD without its name alternative | 4 failed, 118 passed :: KILLED | c::class[chain-token-run], c::class[chain-upper-past-a-stop], c::class[chain-upper], c::class[chain-widened] | rc=0 4 passed |
| m4k | _BEARER with a global (?i) (the NAME= branch turns case-blind) | 1 failed, 121 passed :: KILLED | c::class[lower-equals] | rc=0 1 passed |
| m4n-KEY | _SECRET_NAME without KEY | 5 failed, 117 passed :: KILLED | c::class[chain-token-run], c::v1row[V1-d], c::straddle, c::shapes43, l::ledger-v1row[V1-d] | rc=0 5 passed |
| m4u-KEY | _ENVVAL_HEAD without KEY | 1 failed, 121 passed :: KILLED | c::class[upper-key-short] | rc=0 1 passed |
| m4n-TOKEN | _SECRET_NAME without TOKEN | 6 failed, 116 passed :: KILLED | c::class[chain-upper-past-a-stop], c::class[chain-upper], c::v1row[V1-e], c::straddle, c::shapes43, l::ledger-v1row[V1-e] | rc=0 6 passed |
| m4u-TOKEN | _ENVVAL_HEAD without TOKEN | 1 failed, 121 passed :: KILLED | c::class[upper-token-short] | rc=0 1 passed |
| m4n-SECRET | _SECRET_NAME without SECRET | 1 failed, 121 passed :: KILLED | c::class[name-secret] | rc=0 1 passed |
| m4u-SECRET | _ENVVAL_HEAD without SECRET | 1 failed, 121 passed :: KILLED | c::class[upper-secret-short] | rc=0 1 passed |
| m4n-PASSWORD | _SECRET_NAME without PASSWORD | 12 failed, 110 passed :: KILLED | c::v1row[V1-a], c::v1row[V1-b], c::v1row[V1-c], c::v1row[V1-g], c::v1row[V1-h], c::straddle, c::shapes43, l::ledger-v1row[V1-a], l::ledger-v1row[V1-b], l::ledger-v1row[V1-c], l::ledger-v1row[V1-g], l::ledger-v1row[V1-h] | rc=0 12 passed |
| m4u-PASSWORD | _ENVVAL_HEAD without PASSWORD | 5 failed, 117 passed :: KILLED | c::class[chain-upper-past-a-stop], c::v1row[V1-f], c::straddle, c::shapes43, l::ledger-v1row[V1-f] | rc=0 5 passed |
| m4n-PASSWD | _SECRET_NAME without PASSWD | 1 failed, 121 passed :: KILLED | c::class[name-passwd] | rc=0 1 passed |
| m4u-PASSWD | _ENVVAL_HEAD without PASSWD | 1 failed, 121 passed :: KILLED | c::class[upper-passwd-short] | rc=0 1 passed |
| m4n-APIKEY | _SECRET_NAME without API_?KEY | 1 failed, 121 passed :: KILLED | c::class[name-api_key] | rc=0 1 passed |
| m4u-APIKEY | _ENVVAL_HEAD without API_?KEY | 1 failed, 121 passed :: KILLED | c::class[upper-api_key-short] | rc=0 1 passed |

Required rows: m1 (`_SK` back) and m2 (`_BEARER` back) KILLED; m3 (the verifier's option-B bearer form, exact pattern from
section 11: `(?i)bearer\s+[A-Za-z0-9._~+/-]{16,}+=*+(?![\"']?\s?[:=])`) is killed by the C-4 test in BOTH files
(`c::control[C-4]`, `l::ledger-control[C-4]`), as the brief requires. m4 removes each further element on its own: the three
`_YIELD` branches (m4a-c), the three chain guards (m4d1-3), the value conditions (m4e, m4e3, m4f), the floor lookahead that makes
each class fire where its PIN form fires (m4g for sk, m4g2 for bearer; m4g dies on `V1-a k=13: not idempotent`), the NAME=
exclusion (m4h), each half of `_ASSIGNMENT_HEAD` (m4i, m4j), the scoped case flag (m4k), and each name of `_SECRET_NAME` (m4n-*)
and `_ENVVAL_HEAD` (m4u-*). The first full run (on the test files of section 3) had five survivors, m4u-KEY, m4u-TOKEN,
m4u-SECRET, m4u-PASSWD and m4u-APIKEY (`117 passed :: SURVIVED` each). Each was a real test gap, not an equivalent mutant: its
discriminator, V1-f's form under that name, leaks at the PIN and is closed by the change:
```
PIN:   'desk-SERVICE_KEY=QZJ8QZ'        -> 'set de<redacted:sk>=QZJ8QZ now' body=True idem=True     (TOKEN, SECRET, PASSWD, API_KEY: the same)
after: 'desk-SERVICE_KEY=QZJ8QZ'        -> 'set de<redacted:sk>KEY=<redacted:envval> now' body=False idem=True
```
The five `upper-*-short` rows were added, and each of the five mutants re-ran KILLED by its row (unmutated re-run `rc=0 1 passed`),
before the final full run above.

## 11. Gates (every command with its output)
```
$ mkdir -p /tmp/j11r2/bt && /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_canonical.py tests/test_decisions_ledger.py -q -p no:cacheprovider --basetemp=/tmp/j11r2/bt/r1   (twice; section 3)
121 passed in 3.93s   r1-rc=0
121 passed in 3.73s   r2-rc=0
$ bash scripts/pc_suite.sh set-id -- tests/test_decisions_canonical.py tests/test_decisions_ledger.py
2 files set=16a7b628685e
$ /root/venv-agent-factory/bin/python /tmp/j11r2/v1_rows.py   (the appendix driver, after; section 5)
replayed rows: 14 shapes: 14 leaking: 0
$ /root/venv-agent-factory/bin/python -m pyflakes src/agent_factory/decisions/volatile.py tests/test_decisions_canonical.py tests/test_decisions_ledger.py
pyflakes-rc=0
$ python3 scripts/ap_screen.py src/agent_factory/decisions/volatile.py
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---
$ python3 scripts/ap_screen.py --tests tests/test_decisions_canonical.py tests/test_decisions_ledger.py
--- TEST_SCREEN over 2 path(s): 1 hits over 2 files ---
AP-70: 1
    tests/test_decisions_ledger.py:1292: except Exception:
$ (the PIN's screens, on the PIN copies in /tmp/j11r2/pin)
--- AP_SCREEN over 1 path(s): 0 hits over 1 files ---
--- TEST_SCREEN over 2 path(s): 1 hits over 2 files ---
AP-70: 1
    /tmp/j11r2/pin/tests/test_decisions_ledger.py:1292: except Exception:
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 40 files scanned, clean
no-laya-rc=0
$ node .gitnexus/run.cjs detect-changes --scope all --repo .
Changes: 4 files, 5 symbols
Affected processes: 0
Risk level: low
Changed symbols:
  Variable _SK → src/agent_factory/decisions/volatile.py
  Variable _TOKEN → src/agent_factory/decisions/volatile.py
  Variable _ENVVAL → src/agent_factory/decisions/volatile.py
  Variable _ENVVAL_WIDE → src/agent_factory/decisions/volatile.py
  Function test_spec_negative_leg_reason_is_the_exact_observed_line → tests/test_s0_02_buzz_authz.py
```
New AP hits vs the PIN: 0 (production) and 0 (tests). The one AP-70 hit is the PIN's own
`except Exception:` at `tests/test_decisions_ledger.py:1292`.
`detect-changes` runs on a stale index: `_TOKEN`, `_ENVVAL` and `_ENVVAL_WIDE` are listed
because the insertion moved their lines; their patterns are identical to the PIN (section 4). The S0-02 function is lane B10's
file, not mine. It printed no `partial` or `truncated` flag.

## 12. DISCREPANCIES (flagged; each needs no action from me unless the coordinator rules otherwise)

- **D-1: name bytes the PIN's placeholder covered now show (B2's reading).** Where sk or bearer yields, the secret NAME stays
  visible after the sk/bearer placeholder (`ta<redacted:sk>password: <redacted:envval>`), and a following `=` that the PIN's `=*`
  padding covered shows too. Over 160,000 fuzz inputs these are the ONLY PIN-redacted bytes that now show: name words
  (`password`, `key`, `API_KEY`, …) and that `=`, never a body byte (section 1, and seed 4 in section 6). I read B2's "every value
  the PIN redacts stays redacted" as secret VALUES: A4's rule is that the name is kept and the value becomes the placeholder,
  and "an assignment wins its own class". If the coordinator counts a name word the sk run used to swallow as a value, B2 fails
  on these bytes; the alternative (swallow the name AND the value into the sk placeholder) was not built.
- **D-2: the brief's feasibility measure does not establish B2.** The brief measured "one class-form variant closes all 14
  driver rows with the 72 tests passing and the goldens unchanged". My v1 prototype met exactly that bar (and the 43-shape
  differential) and still newly exposed body bytes in 6 of 120,000 fuzz inputs (chained assignments, section 1). Any variant
  judged by the 14 rows, the 72 tests and the 43 shapes alone can carry that defect. The chain guard is what closes it here.
- **D-3: V-1 is closed for plain values, not for chained ones.** Where the name's value holds a second assignment head, the
  run keeps its PIN form (the guard), so that input behaves exactly as at the PIN, including the PIN's leak of the FIRST value
  if that value is secret (`mask-PASSWORD=<v1>;token: <v2>` keeps `<v1>` visible, at the PIN and after). This is the price of
  "no new leak": fixing it needs the chained-assignment gap F-1 below, outside this repair. The guard rows pin the PIN's own
  output (for example `plainvalue`, `abab…key` stay visible there); they pin "no worse than the PIN", not a desired end state.
- **D-4: new module-level names.** The class forms are built from four new pieces (`_SECRET_NAME`, `_ASSIGNMENT_HEAD`,
  `_ENVVAL_HEAD`, `_YIELD`, `src/agent_factory/decisions/volatile.py:57-73`). They exist only to build `_SK` and `_BEARER`; I read them as
  part of "the class forms". No other symbol changed.
- **D-5: three defects of my own, disclosed.** A ledger locator holding a `J`, a guard-row filler colliding with the V1-h check,
  and literal NBSP/U+3000 characters where I meant escapes. The first two were caught by running the controls at the PIN before
  any count was taken; the third by a byte-level read of the test file. All three are fixed in the final files.
- HEAD moved during the lane: origin and the shared tree's HEAD went from 98e2efc to 9801fb5 (other lanes' commits: S0-02,
  K1-h, B10, two ledger planes, transcripts). At 9801fb5 my three boundary files are still the PIN blobs (`20ebcd54f3ed`,
  `0afbf1b821ed`, `4a8bccead05f`), so nothing landed inside my boundary; the PIN (d556c9b) and 98e2efc hold the same
  boundary bytes (section 0).

## 13. Adjacent findings (reported, not fixed)

- **F-1 (pre-existing; new finding; same family as V-1): a chained assignment frees its second value.** A value class swallows
  a second secret name with its separator, and the second value leaks. The widened value `[^\s"'&,;]{8,}`, the upper-case
  class's `\S+` and the token class's run each do it; identical at the PIN and after:
```
'passwd=aAPI_KEY : X4Z92Q0X1ZX02Z71'                         -> 'passwd=<redacted:envval> : X4Z92Q0X1ZX02Z71'
'token: QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8QZJ8password: hunter2hunter2' -> 'token: <redacted:envval> hunter2hunter2'
'PASSWORD=x;token: QZJ8QZJ8QZJ8QZJ8'                         -> 'PASSWORD=<redacted:envval> QZJ8QZJ8QZJ8QZJ8'
```
  Sibling in the transcript scrubber's credential rule (`AGENT_TOKEN` … at `scripts/transcript_export.py:33`), run in-process
  (no file written):
  `'passwd=aAPI_KEY : X4Z92Q0X1ZX02Z71' -> 'passwd=<redacted> : X4Z92Q0X1ZX02Z71'`. A fix is a contract decision: a value that
  stops before a `NAME[:=]` opens other leaks (measured in design: `password: mykey=abc` would free `mykey=abc`).
- **The scrubber does not have V-1's mechanism.** Its credential rule runs before its Bearer and sk rules (names first). On the
  eight V1 shapes, in-process: seven fully redacted; `disk-PASSWORD=QZJ8QZ` is kept by its own 8-character value floor (the
  V-14 family), not by a swallowed name.
- **Cost constant.** The new forms scan sk/bearer runs about 90 times slower per character than the PIN forms (linear; the
  worst whole input is 0.040 s at 128k).
- **C-F2 persists.** `task-implementer` still becomes `ta<redacted:sk>`; the V-1 rows now read `ta<redacted:sk>password: …`.
  An identity collapse of names, never a leak; filed.

## 14. NOT-done (first-class)

- No commit, stage or push (the coordinator commits the three files and this report). No PC or bridge use.
- No full-tree suite. Run: the two decision test files (121), the PIN's own test files against the new code (72), the mutants
  (30, plus five re-runs), and the scratch drivers named per section.
- VERIFY-J1-1-R1 follow-ups V-2 … V-6, V-15, V-16 and #187's V-12 … V-14: not touched (out of scope).
- F-1 is reported, not fixed; D-3's chained V-1 shapes stay as at the PIN.
- No `/bug-echo` registry row: `docs/INCIDENT-LOG.md` is outside my boundary. The echo SCAN ran read-only: the transcript
  scrubber (no V-1 mechanism; an F-1 sibling), and the decisions redactor's own classes (F-1 via `_TOKEN` and `_ENVVAL`, section 13).
- The fuzz is a generator, not a proof: 160,000 inputs over 31 name spellings, 21 prefixes and 20 ASCII separators. Unicode
  separators (V-6) and texts before normalize are not generated.
- GitNexus was not re-indexed (a detached `analyze` outlives the Bash cap; the post-commit hook re-indexes). sentrux, slopo and
  ripwire comparisons were not run (advisory, not asked).
- Timings are from the shared sandbox, which other lanes load; section 8 re-measured the two outlying ratios.
- Scratch `/tmp/j11r2/` is removed at the end of the lane (the tools are described per section; each can be rebuilt).

## 15. Self-attack: the likeliest ways this change is wrong

1. **The chain guard leaves V-1 open on chained values (D-3).** Not ruled out; stated first-class. Ruled out as a regression:
   on those inputs the output is the PIN's byte for byte (the guard rows; fuzz: 0 new body exposure in 160,000 inputs).
2. **`_YIELD` mirrors `_ENVVAL`, `_TOKEN` and `_ENVVAL_WIDE` by hand and can drift from them.** Today each branch, guard,
   condition and name is killed by a named test (30 of 30 mutants), and the comment block names the classes it mirrors. Not
   ruled out for a future widening of those classes, which would not update `_YIELD` by itself; such a change should add its
   form to the V-1 class rows.
3. **The fuzz generator could miss an exposure family.** The instrument is validated both ways: it reports 0 on PIN vs PIN and
   36 of 3,000 on the verifier's option B, and it asserts its proxy output equals the real `_redact_str`. The by-construction
   argument (section 1) covers what the generator does not, but it is reasoning, not a proof (evidence tier INFERRED).

## 16. Evidence tiers

- VERIFIED (run in this session, output pasted): the premise; RED and GREEN on the final files; the PIN's tests against the new
  code; the driver before and after; the 43-shape differential; the fixture scan; the goldens; the fuzz (PIN vs option B, v1,
  v2, the final file); the idempotence fuzz and its m4g control; the cost table and its re-measure; the mutation table; the
  gates; the scrubber and sibling probes.
- INFERRED: the monotonicity argument of section 1 (backed by the fuzz, not proven); linear cost beyond 256k.
- ASSUMED: Python 3.11's `re` semantics (the sandbox interpreter; the forms use scoped flags `(?i:…)` and fixed-width
  lookbehind only).

## 17. Report lint (three fix rounds, the brief's cap)
```
$ python3 scripts/report_lint.py --min-refs 15 tasks/briefs/laya/J1-1-R2-report.md --root .
run 1: report_lint: 16 refs — OK 9, NEAR 1, MISS 4, UNCHECKABLE 2, UNRESOLVED 0 (worktree)   (FLOOR: OK 9 < 15)
run 2: report_lint: 32 refs — OK 29, NEAR 0, MISS 0, UNCHECKABLE 3, UNRESOLVED 0 (worktree)
run 3: report_lint: 32 refs — OK 30, NEAR 0, MISS 1, UNCHECKABLE 1, UNRESOLVED 0 (worktree)   (a backtick pairing artifact of my fix)
run 4: report_lint: 32 refs — OK 31, NEAR 0, MISS 0, UNCHECKABLE 1, UNRESOLVED 0 (worktree)   lint-rc=0
run 5 (after this section and the HEAD note in section 12 were appended; NOT fixed, the three-round cap):
       report_lint: 33 refs — OK 31, NEAR 0, MISS 1, UNCHECKABLE 1, UNRESOLVED 0 (worktree)
```
The run-5 MISS is the last sentence of this section, which names the UNCHECKABLE ref (its tokens `ap_screen` and
`UNCHECKABLE` are not on the cited code line); the cited line itself is right.
The one UNCHECKABLE is `tests/test_decisions_ledger.py:1292` inside the pasted `ap_screen` output of section 11 (verbatim).
