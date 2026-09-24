# J1-1-R4 — the redaction pass REDESIGNED (task #198; owner ruling D-069; contract amendment D-070)

**Role:** code-implementer (sandbox, Opus 5.5). **PIN:** the origin head named in the dispatch message.
**Status of the code you replace:** J1-1 is NOT-READY (VERIFY-J1-1-R3, D-068): 9 of 165,000 generated inputs put a secret
value into the appended ledger line through `make_row -> append`, and `replay` accepted the row. Three patch rounds each
closed the named leak and left or added another. The owner ruled (D-069): redesign, no fourth patch; regex whack-a-mole is
the failure mode to leave behind.

## Why the patches kept failing (read this first)
`_redact_str` (`src/agent_factory/decisions/volatile.py`) runs six SEQUENTIAL substitution passes. Each pass sees the text
the earlier passes left, so a match in one pass can eat a secret NAME another pass needed (AF-AP-157), and the guards
added to stop that (`_yield_pattern`, `_YIELD`, `_BEARER_MERGE`) read the text differently from the passes they guard
(AF-AP-161; R-1, R-2, R-4; F-1, F-2). Every fix added another interaction.

## The design (D-070; the coordinator measured a prototype of it at authoring, see PREMISE)
1. **Detect on one text.** Every detector reads the SAME normalized input string and returns character spans. No
   detector ever sees another detector's output, so no match can hide a name from another class.
2. **Every start, overlaps included.** Each detector finds a match at EVERY start position, including starts inside
   another match of the same detector (`re.finditer` skips those: in `flask-tapasswd=aAPI_KEY : <value>` the second head
   `API_KEY :` starts inside the first value and its value leaked in the coordinator's first prototype).
3. **Union, then one replacement.** Overlapping spans merge. Each merged span becomes ONE placeholder: the class of the
   member span with the earliest start; a tie at the same start goes by the fixed priority
   held > privkey > sk > bearer > envval (upper `NAME=`) > token > envval (widened form). Text outside every span is kept
   byte for byte.
4. **Held placeholders are atomic.** An existing full placeholder (`<redacted:(sk|token|bearer|envval|privkey)>`) is a
   protected span of its own class with top priority, so a second pass never relabels it (idempotence). A widened-form
   value that is a proper prefix of a placeholder AND ends at the end of the text is a placeholder that `bound` cut: it
   is not a span (the current guard's meaning, kept).
5. **Values are greedy to their natural end** (whitespace, a quote, `&`, `,`, `;`; the class regexes as today), never
   stopped at another head: the other head is detected on its own (rule 2), and the union covers both. This is what
   removes the "stub" class the verifier measured for a value-stop rule (`password: mykey=X4Z9Q` is hidden WHOLE).
6. **The detector classes and their forms stay** (placeholders, the widened form's 8-character floor for a standalone
   value, the token class's 32-character run, sk's 8, bearer's 16 with the special letters matched as today, the
   private-key block). DELETE the yield / merge machinery (`_yield_pattern`, `_YIELD`, `_BEARER_MERGE`, the guards that
   only existed to order passes) and every comment that describes it.

## Contract (what must hold; D-070)
- **C1 leak:** for every input, no byte of a secret value that a detector's form covers appears in the output of
  `decision_state`, in `canonical(...)`, or in the appended ledger line (`make_row -> append`), and `replay` of such a row
  holds no byte either. Prove it with a canary oracle independent of the implementation: a seeded generator that plants
  random secret values (letters, digits, symbols from each class's alphabet, special letters U+0130, U+0131, U+017F) in
  the forms the detectors define, embedded in random context (prose, delimiters, other names in random case and with
  prefixes, glued `bearer` and `sk-` runs, existing placeholders, chains of two and three assignments), and checks that no
  planted value's distinctive substring (4+ characters) survives. At least 100,000 generated inputs per run, two seeds,
  the counts pasted.
- **C2 no regression against BOTH references:** on the same generator, every planted value that d556c9b hides (blob
  20ebcd54f3ed) and every planted value that the PIN's current code hides (blob 2d5cf0072469) is hidden by the new code.
  Run each reference from `git show <rev>:src/agent_factory/decisions/volatile.py` in a scratch directory, never by
  editing the tree. Newly visible count: 0 against each, pasted.
- **C3 idempotence:** `decision_state(q, decision_state(q, s)) == decision_state(q, s)` for every generated state and
  every schema; the ledger's fixed-point check (`src/agent_factory/decisions/ledger.py` `restate`) stays green.
- **C4 goldens:** the seven committed golden digests are unchanged (their fixtures hold no secret; see PREMISE).
- **C5 the named shapes:** the verifier's F-1 and F-2 hand shapes (`tasks/briefs/laya/VERIFY-J1-1-R3-report.md`
  sections 4, 5 and 11: N1-*, N2-*, R4-n2-a), the V-1 rows (D-057), R-1..R-4 rows (D-059), and the stub example
  `password: mykey=X4Z9Q` each get a named test that asserts no value byte in the output.
- **C6 cost:** the detection stays near-linear. Measure the worst case you can construct (for example 20,000 characters
  of repeated `API_KEY=` heads, of `sk-` runs, and of `bearer ` runs) and paste the times; each under 2 s on this sandbox.
- **C7 no model:** `tests/test_decisions_no_model.py` stays green; nothing in `src/agent_factory/decisions/` imports a
  model package. (Jev/Laya is NOT in the redaction path: a classifier's miss is a leak, and J1-5's closure and KC-J1
  forbid it. The owner's Jev idea becomes a separate OFFLINE leak hunter, task #223, not this lane.)

## The existing tests
The redesign changes the OUTPUT LAYOUT for many inputs (it masks more, for example `ta<redacted:sk>password: ...`
becomes `ta<redacted:sk>: ...`, because the sk run and the value no longer negotiate). Tests that pin the old layout will
fail; that is expected. For each such test: keep EVERY input row; keep or add the no-value-byte assertion on every row;
replace the exact expected string with the new layout, and state in a one-line comment which rule produces it. Never
delete an input row, never weaken a no-value-byte assertion, never skip or xfail a test. The coordinator's prototype
failed these 48 at authoring (PREMISE), all layout pins, none of them a leak assertion.

## Boundary
MODIFY `src/agent_factory/decisions/volatile.py`, `tests/test_decisions_canonical.py`, `tests/test_decisions_ledger.py`.
CREATE `tests/test_decisions_redaction_properties.py` (the generator, the canary oracle, C1/C2/C3/C6),
`tasks/briefs/laya/J1-1-R4-report.md`. READ everything else. Do not touch `ledger.py`, `canonical.py`, the schemas, the
placeholders, the limits, the golden fixtures, or any file outside the boundary; report an adjacent defect, never fix it.

## Gates (run each, paste the output)
- `/root/venv-agent-factory/bin/python -m pytest tests/test_decisions_canonical.py tests/test_decisions_ledger.py
  tests/test_decisions_no_model.py tests/test_decide_harvest.py tests/test_decisions_redaction_properties.py -q
  -p no:cacheprovider --basetemp /tmp/j1r4b/bt` twice (mkdir -p the parent first), identical counts; the property file
  may run its full 100,000-input sweep behind an environment flag, but a 5,000-input sweep runs by default.
- The C2 differential against both references and the C6 timings, pasted.
- Mutation: at least 8 mutants of the new code (drop the overlap rule; drop one detector; the priority table reversed;
  the held-placeholder protection removed; the cut-placeholder guard removed; `finditer` in place of every-start;
  the union replaced by first-wins; the widened floor at 0), each RED by a named test. Run them on a scratch copy only.
- `python3 scripts/lint_delta.py` clean for your files; `node .gitnexus/run.cjs detect-changes --scope all --repo .`
  output pasted (the index may be stale; say so if it is).

## Report (`tasks/briefs/laya/J1-1-R4-report.md`)
What changed (functions added and removed), each contract row C1-C7 with its pasted evidence, the test rows whose
expected layout changed (count per test function), the mutant table, what you could not do and why. No verdict on
yourself: the independent verify decides (rule 0f).

## Standing rules
Do not spawn subagents. No outward actions (no pushes, PRs, comments, GitHub writes). Do not commit: the coordinator
commits. Never print a real secret; test secrets are fake strings only. Absolute paths. The shared tree may hold other
agents' untracked files; touch only your boundary.

## PREMISE — MEASURED at authoring (2026-09-24 11:1xZ, /home/user/agent-factory at 78f9cc2)
```
$ git log --format='%h %s' -4 -- src/agent_factory/decisions/volatile.py
fdac751 J1-1-R3 landed GATED-PENDING-VERIFY: the redaction regressions fixed; C4 amended (D-06...
fb016d0 J1-1-R2 landed (task #192; GATED-PENDING-VERIFY): the sk and bearer classes yield to a...
f0e431f J1-1-R1 landed (task #139; GATED-PENDING-VERIFY): bound after redact, the widened secr...
01ca7d5 J1-1 landed (GATED-PENDING-VERIFY): the decisions module (seven closed state schemas, ...
$ git rev-parse --short=12 <rev>:src/agent_factory/decisions/volatile.py
d556c9b 20ebcd54f3ed   fb016d0 bf04415d72c1   HEAD 2d5cf0072469
$ pytest tests/test_decisions_canonical.py tests/test_decisions_ledger.py tests/test_decisions_no_model.py tests/test_decide_harvest.py -q
248 passed in 60.39s (0:01:00)        set id: 4 files set=25abb828084e
$ grep -l redacted tests/fixtures/decisions/golden/*.json    (no output: the seven golden fixtures hold no placeholder)
$ callers of decision_state: src/agent_factory/decisions/ledger.py:273 (restate), :404 (make_row); canonical.py:77
# the coordinator's prototype of the design (scratch copy /tmp/j1r4/proto, the three J1 test files):
first prototype (finditer)      -> 'flask-tapasswd=aAPI_KEY : <value>' leaked the value (rule 2 exists because of this)
every-start prototype           -> 48 failed, 133 passed; 0 failures carry a value-byte / visible / leak message;
                                   the 48 pin the old layout (15 test_v1_class_beyond_the_driver, 8
                                   test_v1_name_swallowed_by_sk_or_bearer_frees_no_value, 6
                                   test_r4_env_check_reads_the_value_after_the_bearer_merge, 5
                                   test_bearer_merge_step_keeps_every_j1_1_r2_redaction, 4
                                   test_surviving_mutant_rows_stay_redacted, 4
                                   test_r2_token_check_reads_the_run_as_the_token_class_does, 3
                                   test_r3_upper_name_equals_space_value_behind_sk_or_bearer, 1
                                   test_token_named_residual_shape_redacted; 2 in test_decisions_no_model.py failed
                                   only because the scratch copy lacks the repository layout — check them in the tree)
'password: mykey=X4Z9Q'         -> 'password: <redacted:envval>'
'task-password: QZJ8QZJ8QZJ8QZJ8QZJ8' -> 'ta<redacted:sk>: <redacted:envval>'
'Authorization: Bearer abcdefghijklmnopqrstuv: rejected' -> 'Authorization: <redacted:bearer>: rejected'
```

## The coordinator's prototype core (a measured sketch, NOT a spec: verify it, then write the real one)
```python
_P_PRIV = _PRIVKEY
_P_SK = re.compile(r"sk-[A-Za-z0-9_-]{8,}")
_P_BEARER = re.compile(r"(?i:bearer)\s+(?i:[A-Za-z0-9._~+/-]){16,}=*")
_P_ENVVAL = re.compile(r"(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY)=(\S+)")
_P_TOKEN = re.compile(r"(?i:(?:\b|(?<=_))token[\"']?(?: ?[:=] ?| )?[\"']?)((?i:[A-Za-z0-9+/]){32,})")
_P_WIDE = re.compile(r"(?i:KEY|TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY)[\"']?\s?[:=]\s?[\"']?([^\s\"'&,;]{8,})")
_P_HELD = re.compile(r"<redacted:(?:sk|token|bearer|envval|privkey)>")
# priority: lower wins a tie at the same start
_RANK = {"held": 0, "privkey": 1, "sk": 2, "bearer": 3, "envval": 4, "token": 5, "wide": 6}


def _every(pattern: re.Pattern, text: str):
    """Every match at every start, overlapping ones included (finditer skips a head inside a value)."""
    look = re.compile("(?=" + pattern.pattern + ")", pattern.flags)
    for m in look.finditer(text):
        yield m


def _spans(text: str) -> list:
    out = []
    for m in _P_HELD.finditer(text):
        out.append((m.start(), m.end(), "held", m.group(0)[len("<redacted:"):-1]))
    for m in _P_PRIV.finditer(text):
        out.append((m.start(), m.end(), "privkey", "privkey"))
    for pat, kind in ((_P_SK, "sk"), (_P_BEARER, "bearer")):
        for m in _every(re.compile("(" + pat.pattern + ")", pat.flags), text):
            out.append((m.start(1), m.end(1), kind, kind))
    for m in _every(_P_ENVVAL, text):
        out.append((m.start(1), m.end(1), "envval", "envval"))
    for m in _every(_P_TOKEN, text):
        out.append((m.start(1), m.end(1), "token", "token"))
    for m in _every(_P_WIDE, text):
        v = m.group(1)
        if m.end(1) == len(text) and any(p.startswith(v) and p != v for p in PLACEHOLDERS.values()):
            continue  # a placeholder that bound cut
        out.append((m.start(1), m.end(1), "wide", "envval"))
    return out


def _redact_str(text: str) -> str:
    spans = sorted(_spans(text), key=lambda s: (s[0], _RANK[s[2]]))
    merged = []
    for s, e, kind, cls in spans:
        if merged and s < merged[-1][1]:
            ms, me, mk, mc = merged[-1]
            merged[-1] = (ms, max(me, e), mk, mc)
        else:
            merged.append((s, e, kind, cls))
    out, pos = [], 0
    for s, e, kind, cls in merged:
        out.append(text[pos:s])
        out.append(PLACEHOLDERS[cls])
        pos = e
    out.append(text[pos:])
    return "".join(out)
```
