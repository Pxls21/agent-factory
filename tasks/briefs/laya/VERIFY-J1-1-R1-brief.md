# VERIFY-J1-1-R1 — independent adversarial verify of the decisions redactor (J1-1-R1) and the transcript scrubber (#187), batched (task #189)

PIN: the origin commit of this brief (the post-push SHA, named in the dispatch prompt). The boundary files are byte-identical to
local 5718ea0 / a318b8a (measured below); re-measure them first.
LANE: verify-j1-1-r1 (sandbox; agent `adversarial-verifier`, model opus, in the SHARED tree, no worktree isolation). Honey `full`.
Do NOT spawn subagents. Report EVERY meaningful observation, with no severity filter; the coordinator ranks them.

WHY: Two redaction changes landed GATED-PENDING-VERIFY. The only gates on them so far are their builders' own (rule 0f).
- **J1-1-R1** (5718ea0, task #139) is the one focused repair of VERIFY-J1-1 under AMENDMENT 1 (D-056), finished under the
  coordinator's D-1 ruling (option D).
  - `decision_state` = bound(redact(normalize(state))) is the one public composition.
  - bound cuts AFTER redact.
  - The redact passes run in this order: privkey → sk → bearer → the upper-case `NAME=\S+` form (TOKEN included) → the token
    class → the widened env form (case-insensitive, at most one space around `=`/`:`, an optional quote, a value of 8+
    characters, TOKEN included), behind a guard that never replaces a placeholder or a cut prefix of one.
  - `_ENVVAL`'s nested name-prefix group is removed (D-3, AF-AP-152).
  - The builder: 72 tests, 23 of 23 mutants killed. The coordinator re-ran the gates and mutants d1a and d1b; that is the same
    oracle.
- **#187** (a318b8a) is the coordinator's own change to `scripts/transcript_export.py:33`.
  - The credential rule now takes a quoted name (`"api_key": "…"`) and a compound `*_key` / `*-key` name.
  - The compound class is anchored by `(?<![A-Za-z0-9])`; unanchored it is quadratic, AF-AP-152.
  - The coordinator's own tests and five mutants are the only gate.
  - `harness-ports/bin/hermes-session-export.py` imports these patterns by path.
Both are the same family: a secret pattern written for one spelling (AF-AP-149). Attack both with NEW shapes, never the builders'
own cases.

AUTHORIZATION: this is defensive work on the owner's own redactors. Every secret you plant is a FAKE string you make up (never a
real key, token or password from any file or environment), in scratch under `/tmp/vj11r1/`.

CONTRACT SOURCES (read before you attack):
- `tasks/briefs/laya/J1-1-R1-brief.md` (AMENDMENT 1) and `tasks/briefs/laya/J1-1-R1-report.md` § 12 (the D-1 ruling applied, with
  its two flagged points N-1 and N-2).
- The #187 contract, in the message of commit a318b8a (`git show -s a318b8a`). Every existing name form is kept; the value floor
  of 8 characters and the replacement are unchanged; the private-key rule runs first; the scan is linear.
- The code and tests at the PIN.
- KNOWN and filed; confirm or extend, never re-file as new:
  - issue #47: O-1, the widened class over-redacts real text; D-2, the PIN-suffix idempotence counterexample; O-4.
  - AF-AP-149's two WATCH sites (`scripts/t93r1_apply_profile.sh:58`, `proofs/S0-01/check_acp_conformance.py:153`).

## Items

1. **PREMISE.** Re-measure the premise block below (identities, counts and set ids). Stop CONTRACT-INVALID on a mismatch you
   cannot explain.
2. **The D-1 order under conflict.** Find inputs where two classes compete, and report every one where a secret byte survives
   `decision_state`, or where a placeholder is relabelled. Directions to try:
   - `password: sk-…`, `KEY=sk-…`, `token = <32+ run>-<base64url tail>`, `Bearer` inside an env value;
   - a literal placeholder already in the input (`<redacted:token>` in prose);
   - two secrets on one line; a secret split across a list;
   - separators the ASCII classes do not name (full-width `＝` or `：`, a no-break space, a tab), where you check what
     `normalize` does to them first;
   - upper/lower/mixed case at every pass.
   Every shape runs through the real `decision_state` AND through the ledger (`make_row` / append); say what reaches the JSONL.
3. **The guard (`_envval_wide`).** Can a value that is a real secret pass untouched because it starts like a placeholder or a cut
   one? Can the guard keep a secret tail after a placeholder? Prove your answer with a driver, not a reading.
4. **Bound after redact.** Straddle every bounded field's limit with every class, including the widened forms and the quoted and
   compound names. Check A3's idempotence on your new shapes; D-2 is known. Is any secret prefix left on disk after the cut?
5. **Cost.** Give every pattern pathological inputs, doubling the size and timing each step:
   - `_BEARER`, `_SK`, `_TOKEN`, `_ENVVAL`, `_ENVVAL_WIDE` and `_PRIVKEY` in `src/agent_factory/decisions/volatile.py`;
   - all of `SECRET_PATTERNS` in `scripts/transcript_export.py`, especially the compound class and the private-key rule's
     `.*?` across many BEGIN lines.
   Report any growth faster than linear (AF-AP-152) with the table of sizes and times.
6. **#187 by new shapes.** Report every leak and every false positive on prose, and show what `hermes-session-export.py` emits for
   the same inputs. Shapes to try:
   - names the rule should now take: `"client_secret": "…"`, `access-key: …`, `X-API-KEY: …`, `private-key = …`, `db_password=…`;
   - the same names with backticks, in YAML block scalars (`key: |`), after `export `, in URLs (`?api_key=…&`);
   - names it must still take: every form of the PIN rule.
7. **The goldens.** Are the 7 golden digests bound, so that mutating one golden file or one pass reds the golden test? Is the
   order test's discriminator (the whitespace run before normalize) still a discriminator after D-1's ≤1-space rule?
8. **Mutants (NEW; never the builder's 23 or the coordinator's five).** At least ten, across both boundaries. Examples:
   - swap the sk and bearer passes; move the token class before the upper-case env form;
   - widen `\s?` to `\s*` in `_ENVVAL_WIDE`; drop the guard's prefix half; drop `(?<=_)` from `_TOKEN`; change bound's `rstrip`;
   - in the scrubber, drop `re.I`; drop the second `[\"']?`; replace the lookbehind with `\b`.
   Each mutant compiles and collects (AF-AP-78). Paste the killing test green on the unmutated copy before you count a kill
   (AF-AP-138). A survivor is a finding.
9. **Every write path.** Is there any path in `src/agent_factory/decisions/` that writes or digests a state without
   `decision_state`? Trace both ledger call sites and `state_digest`, from the code.
10. **The alarm-guarded backtracking test** (`tests/test_decisions_canonical.py`, the `_Runaway` handler). Can it leave SIGALRM
    armed, fire outside its `try`, or hang the suite on a slow box? The screen flagged AF-AP-58's signature at the commit.

PREDICATE: a finding blocks only if all five hold:
- it is contract-mapped (AMENDMENT 1, the D-1 ruling, or the #187 contract);
- it is reproduced through the real functions (`decision_state`, `redact`, the ledger's append, or the `transcript_export.py` CLI);
- it is materially effective: a secret byte of a class the contract names survives into the ledger or the transcript digest, or a
  stated claim is false as stated, or an input of 64 KB or less takes more than 1 s;
- it has a concrete discriminator;
- it is in the boundary.
Everything else is a follow-up. Emit ONE GATE RECOMMENDATION: `MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` /
`CONTRACT-INVALID`, one for J1-1-R1 and one for #187. The coordinator owns the final gate.

## Boundary and standing do-nots

CREATE `tasks/briefs/laya/VERIFY-J1-1-R1-report.md` (write it incrementally). Everything else is read-only. Scratch lives under
`/tmp/vj11r1/`; remove it when you finish (the sandbox has about 1.5 GB free).

Other agents work in this tree on disjoint files. Never touch, run or revert them:
- J1-0-R5: `scripts/no_laya_in_gates.py`, `tests/test_no_laya_in_gates.py`, `tasks/briefs/laya/J1-0-R5-report.md`;
- VERIFY-E3-R1: `proofs/S0-05/`, `tests/test_s0_05_egress.py`, `tasks/briefs/s0-05-support/`.

Nothing under `.claude/` is edited. Never run `git stash`, `git checkout -- …`, `git restore`, `git add`, `git commit` or
`git push` in this tree. Mutants run in scratch copies only. No outward-facing action, and no PC or bridge use.

CODE INTEL FIRST: `graft ask` before any grep for code questions. The pack:
`scripts/lane_context.sh -q 'how does decision_state redact and bound a state, and how does the transcript scrubber match credential names' -s decision_state -s _redact_str -s _envval_wide -s bound -s scrub -o /tmp/vj11r1/pack.md src/agent_factory/decisions/volatile.py src/agent_factory/decisions/ledger.py scripts/transcript_export.py`.

## Report (`tasks/briefs/laya/VERIFY-J1-1-R1-report.md`)

The report holds:
- the PREMISE, re-measured;
- one section per item, each with drivers and pasted outputs;
- the mutant table;
- the FINDING INVENTORY (V- ids, each classified against the predicate);
- the two GATE RECOMMENDATIONs;
- DISCREPANCIES;
- NOT-done.
State your served model in the header. If any of your calls ends in a refusal, say which one and what ran after it (AF-AP-154).

Lint floor: `python3 scripts/report_lint.py --min-refs 15 tasks/briefs/laya/VERIFY-J1-1-R1-report.md --root .` (full
repo-relative paths, no `--map`). Apply its `fix:` hints for at most three rounds, then paste and finish.

## PREMISE — MEASURED at authoring (2026-09-23 13:0xZ, sandbox @ local 5718ea0 plus the uncommitted ledger plane)
```
$ git log -1 --format='%h %s' -- src/agent_factory/decisions | cut -c1-100
5718ea0 J1-1-R1 landed (task #139; GATED-PENDING-VERIFY): bound after redact, the widened secret cla
$ git log -1 --format='%h %s' -- scripts/transcript_export.py | cut -c1-100
a318b8a Transcript scrubber: quoted and compound credential names are scrubbed (task #187, O-3; AF-A
$ for f in src/agent_factory/decisions/volatile.py src/agent_factory/decisions/canonical.py src/agent_factory/decisions/ledger.py src/agent_factory/decisions/__init__.py tests/test_decisions_canonical.py tests/test_decisions_ledger.py scripts/transcript_export.py tests/test_transcript_export.py harness-ports/bin/hermes-session-export.py; do echo "$(git rev-parse HEAD:$f) $f"; done
20ebcd54f3ed7e180543c0d8036d545eb38764cd src/agent_factory/decisions/volatile.py
607b65b613e24063ca228a39f83026829735df83 src/agent_factory/decisions/canonical.py
71fc398a5340ab25076210313d87d8d4c103520f src/agent_factory/decisions/ledger.py
377ccd53da0cbb7b6ef981a08008126137cc1343 src/agent_factory/decisions/__init__.py
0afbf1b821ed9e59a7a08b7697e258b5eb4de5e5 tests/test_decisions_canonical.py
4a8bccead05fd147ecf1e8194f62694aabd55b13 tests/test_decisions_ledger.py
a47e0e5861c90912df2e3eee31a77b5bf66e1e7b scripts/transcript_export.py
8d1723beb46ecde73fdddf6a6048df32ff5635b5 tests/test_transcript_export.py
04326ece5b7a6ac59b76e2fc2a3d7ec6ff5b7c70 harness-ports/bin/hermes-session-export.py
$ git diff --quiet HEAD -- src/agent_factory/decisions tests/test_decisions_canonical.py tests/test_decisions_ledger.py scripts/transcript_export.py tests/test_transcript_export.py && echo 'worktree == HEAD for the boundary'
worktree == HEAD for the boundary
$ git log -1 --format='%h %ad' --date=short -- tests/fixtures/decisions/golden
01ca7d5 2026-09-23
$ grep -n '^_ENVVAL\|^_ENVVAL_WIDE\|^_TOKEN\|^_PRIVKEY\|^_SK\|^_BEARER\|^def _envval_wide\|^def _redact_str\|^def bound\|^def decision_state\|text = _' src/agent_factory/decisions/volatile.py
44:_BEARER = re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/-]{16,}=*")
45:_SK = re.compile(r"sk-[A-Za-z0-9_-]{8,}")
53:_TOKEN = re.compile(r"(?i)(?:\b|(?<=_))token[\"']?(?: ?[:=] ?| )?[\"']?([A-Za-z0-9+/]{32,})")
73:_ENVVAL = re.compile(r"(?P<name>(?:KEY|TOKEN|SECRET|PASSWORD|PASSWD|API_?KEY)=)\S+")
74:_ENVVAL_WIDE = re.compile(
82:_PRIVKEY = re.compile(
311:def _envval_wide(m: re.Match) -> str:
322:def _redact_str(text: str) -> str:
328:    text = _PRIVKEY.sub(PLACEHOLDERS["privkey"], text)
329:    text = _SK.sub(PLACEHOLDERS["sk"], text)
330:    text = _BEARER.sub(PLACEHOLDERS["bearer"], text)
331:    text = _ENVVAL.sub(lambda m: m.group("name") + PLACEHOLDERS["envval"], text)
332:    text = _TOKEN.sub(lambda m: m.group(0).replace(m.group(1), PLACEHOLDERS["token"]), text)
333:    text = _ENVVAL_WIDE.sub(_envval_wide, text)
337:def bound(question_id: str, state: dict) -> dict:
355:def decision_state(question_id: str, state: dict, root: str | os.PathLike | None = None) -> dict:
$ grep -n 'decision_state' src/agent_factory/decisions/canonical.py src/agent_factory/decisions/ledger.py
src/agent_factory/decisions/canonical.py:7:    state_digest = sha256(canonical(decision_state(state)))
src/agent_factory/decisions/canonical.py:8:    decision_state = bound(redact(normalize(state)))
src/agent_factory/decisions/canonical.py:23:    decision_state,
src/agent_factory/decisions/canonical.py:72:    """sha256(canonical(decision_state(state))), hex. The pipeline is
src/agent_factory/decisions/canonical.py:77:    text = canonical(decision_state(question_id, state, root))
src/agent_factory/decisions/ledger.py:42:    decision_state,
src/agent_factory/decisions/ledger.py:270:    # (d) fixed-point check: decision_state(qid, state, None) == state.
src/agent_factory/decisions/ledger.py:273:        restate = decision_state(qid, row["state"], None)
src/agent_factory/decisions/ledger.py:404:        s = decision_state(question_id, raw_state, root)
$ sed -n 33p scripts/transcript_export.py | cut -c1-120
    (re.compile(r"((?:AGENT_TOKEN|PC_BRIDGE_TOKEN|X-Agent-Token|(?<![A-Za-z0-9])[A-Za-z0-9]*[_-]key|api[_-]?key|token|se
$ bash scripts/pc_suite.sh set-id -- tests/test_decisions_canonical.py tests/test_decisions_ledger.py
2 files set=16a7b628685e
$ PYTHONDONTWRITEBYTECODE=1 /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_canonical.py tests/test_decisions_ledger.py -q -p no:cacheprovider --basetemp=/tmp/vj11p/bt1 | tail -1
72 passed in 2.34s
$ bash scripts/pc_suite.sh set-id -- tests/test_transcript_export.py
1 files set=73755bb9fbbf
$ PYTHONDONTWRITEBYTECODE=1 /root/venv-agent-factory/bin/python -m pytest tests/test_transcript_export.py -q -p no:cacheprovider --basetemp=/tmp/vj11p/bt2 | tail -1
23 passed in 0.97s
$ python3 harness-ports/tests/test_hermes_session_export.py | tail -1
test_hermes_session_export: 15 checks passed
```
