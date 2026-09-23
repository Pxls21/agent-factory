# VERIFY-J1-1 — the independent adversarial verify of J1-1 (the decisions module: seven closed state schemas, normalize → redact → canonical → sha256, the seven golden digests), on the PC

PIN: 52c02ee (origin head; the J1-1 landing is 01ca7d5, and 52c02ee only adds the transcripts sync on top, so every boundary file below is byte-identical at both. The dispatcher builds your lane tree AT this PIN. Re-measure the identities first.)
LANE: pc-verify-j1-1
ROLE: adversarial-verifier on the STRICT local route (`HERMES_MODEL=qwen-local/qwen3.8-27b-local`). The contract-gate predicate (D-031): a finding BLOCKS only if it is contract-mapped · reproduced through the real production path (here: `state_digest` / `normalize` / `redact` / `canonical` as a caller imports them) · materially effective · a concrete discriminator · in boundary. Emit ONE GATE RECOMMENDATION (`MERGE-READY` / `MERGE-READY-WITH-FOLLOWUPS` / `NOT-READY` / `CONTRACT-INVALID`); never a verdict. The coordinator owns the gate.

COMPONENT + CONTRACT (frozen; the builder's report is an INPUT to attack, never evidence):
- Contract: `tasks/briefs/laya/J1-1-brief.md` (items 1-6, the Tests list, the six mutant rows) · `seeds/seed-laya-j1-v1.yaml` AC 1 (`ac_bdaf2f13a1cee8c9`, RED until J1-2 by design) and AC 3 (`ac_348ab0ae10309609`) · `tasks/laya-j1-breakdown.md:16-17` (the pinned decisions "state = a BOUNDED, CLOSED, per-question-type extraction" and "order of transforms: normalize → redact → canonical → sha256") and row J1-1 at `:30` · `docs/research/COUNCIL-VERDICT-JEV-LAYA-v1.md:96` (acceptance test 1, redaction: "the secret's bytes never appear in the ledger").
- Code under test: `src/agent_factory/decisions/__init__.py`, `canonical.py`, `volatile.py`; `tests/test_decisions_canonical.py`; `tests/fixtures/decisions/golden/*.json` (seven). Builder report `tasks/briefs/laya/J1-1-report.md` (its refs use the aliases C/V/T/B/L; its lint line reproduces only with `--map C=src/agent_factory/decisions/canonical.py --map V=src/agent_factory/decisions/volatile.py --map T=tests/test_decisions_canonical.py --map B=tasks/briefs/laya/J1-1-brief.md --map L=tasks/laya-j1-breakdown.md`).
- NOT in scope: `ledger.py` (J1-2, not built), `scripts/decide-harvest` (J1-3, not built), the never-a-gate screen (its own verify lane runs in parallel), anything under `scripts/`.

THE COORDINATOR'S FINDINGS (measured at the PIN, pasted below; each is an INPUT to reproduce and grade, never a conclusion):
- C-F1 — the bound runs before redaction. Item 2 puts "truncate the bounded excerpts at their limit" inside normalize (`volatile.py:143`, `s = s[: f.limit]`), item 3 applies redact after normalize, and item 6 plus the verdict's acceptance test 1 require that the secret's bytes appear in no output. Measured: a PEM key with a 1,500-character body in `ap.violates_row.action_excerpt` keeps its BEGIN line and 344 key characters in the canonical bytes; an `sk-` key straddling the 400 limit leaks `sk-ABCDEF`. The contract's items cannot all hold at the boundary: grade whether this is NOT-READY (the code can satisfy item 6 without breaking items 2-3, e.g. by redacting before the cut inside normalize) or CONTRACT-INVALID (no implementation can satisfy the frozen text as written), and name the amendment.
- C-F2 — `sk-` has no word boundary (`volatile.py:42`): "task-implementer failed" becomes `ta<redacted:sk> failed`; distinct states collapse into one digest.
- C-F3 — missed forms: `token = <run>` (spaces around `=`) and lowercase `password=…` are not redacted; `Token: <run>` is.
- C-F4 — relative paths are not normalized: `./src/x.py`, `src//x.py`, `src/x.py/`, `src/./x.py` each hash differently from `src/x.py` (item 2 names only absolute-path relativization; is a stability claim over re-landed sources hollow for these shapes?).
- C-F5 — value types are not closed: a non-string value in a string key is `str()`-coerced (`msg: 5` becomes `'5'`; `msg: {'a': 1}` becomes the Python repr `"{'a': 1}"`).
- C-F6 — `canonical()` refuses bool and None with the reason `decision-canonical-float` (`canonical.py:58`, `:64`); the contract names that reason for a float only.
- C-F7 — an absolute command binary as `action_target` (`/usr/bin/python3 -m pytest`) is refused with `decision-state-abs-path: action_target`; most transcript commands in this project start with an absolute interpreter path. A J1-3 consequence: grade it against item 1's "a command's LEADING TOKEN only" and item 2's refusal rule.

BUDGET: a targeted verify of one landing — scope = the three modules, the test file, the seven fixtures and their consumers' contract. Discovery exhaustive inside that scope.

AUTHORIZATION + DO-NOTS:
- The owner's PC; user scope only; no sudo. Never stop, restart or touch any server (OmniRoute, the vLLM `qwen` container, the Laya unit, Ollama, the Buzz relay). You need no network access at all.
- Read-only on the lane tree except your report. Every mutant in a SCRATCH COPY under `$HOME/tmp-vj11/` (never the PC's tmpfs `/tmp`, AF-AP-112); restore by copy and sha-verify each restore; a mutant must COMPILE and COLLECT (AF-AP-78: paste `py_compile` rc and the collected count per row; a syntax kill is INVALID, never "killed").
- Interpreter `/home/rocco/venv-agent-factory/bin/python` (the venv is not editable: pytest reads `pythonpath = ["src"]` from `pyproject.toml`; a bare `python -c` import needs `PYTHONPATH=src`). pytest with `-p no:cacheprovider --basetemp=$HOME/tmp-vj11/bt`, removed after. One `terminal` call stays under 420 s.
- Test secrets are FAKE, invented strings only (the shapes below). Never read, print or paste any real key, `.env` or token (AF-AP-39).
- Never commit, push, or touch the ledger, the wiki or any brief; no outward action.

## Items (each with pasted output; SOLID/UNSURE per observation)
1. **Reproduce the landing gates at the PIN** (identities first, the table below): the suite twice (`14 passed` each, counts bitwise), pyflakes on the four files, `python3 scripts/ap_screen.py --tests src/agent_factory/decisions/canonical.py src/agent_factory/decisions/volatile.py tests/test_decisions_canonical.py`, the seed's AC 3 command verbatim, AC 1 with `PYTHONPATH=src` (RED on the ledger import by design: paste the line), the builder's lint with and without the five maps.
2. **The seven schemas against contract item 1**, key by key: a table of (question_id, the contract's keys, `SCHEMAS[qid]` keys, enum sets, case rule, limit). Every refusal string exact for each of the four classes (unknown key, missing key, bad enum, unknown question) on EACH of the seven types, not one. Then the "never accepted as state keys" list of item 1 (line numbers, timestamps, absolute paths, run ids, PIN SHAs): as extra KEYS (refused?) and as VALUES inside an allowed key (a timestamp inside `msg`, `line 42:` inside `snippet`, a PIN inside `title`): what does normalize do with each? Item 5 says a re-landed variant with line numbers hashes identical: for each of the seven fixtures, list which of the named variant classes (absolute path under the root, a PIN suffix, extra whitespace, NFD, line numbers) its `variant` actually exercises. A variant class a fixture does not exercise is a vacuous re-landing claim for that type: say so per type.
3. **normalize shapes** (a table; paste each output): paths (absolute under the root, outside it, the root itself, `~/x`, `..`, `a/../b`, `./x`, `x//y`, `x/`, `x/./y`, a root given with a trailing slash, a relative root); whitespace kinds (tab, newline, NBSP U+00A0, U+2028, a zero-width space U+200B); NFD vs NFC (`é` both ways, a Hangul syllable both ways); truncation exactly at the limit, one over, a combining sequence cut at the limit; `strip_pin` (a 7-hex and a 40-hex suffix, uppercase hex, a 41-hex suffix, `--` inside the name, a suffix without `--`); `target` (a command with an absolute binary, `sudo x`, an empty string, only whitespace); non-string values in string keys (C-F5) and a non-list in `paths`. For each shape: stable (two spellings, one digest), refused (name the reason), or silently wrong.
4. **redact shapes** (a table): per class a positive, a negative, the STRADDLE at each bounded key's limit (C-F1: `EXCERPT_LIMIT` 400 on `action_excerpt`/`expected`/`observed`/`snippet`, `MSG_LIMIT` 200 on `msg`, and the shorter limits on `title`/`row_title`/`finding_title`/`sym`), PEM variants (EC, OPENSSH, ENCRYPTED, a PEM whose END line is missing in the input itself), the word-boundary shapes of C-F2, the separator shapes of C-F3 (`token=`, `token: `, `token = `, `"token": "…"`, `?api_key=…` in a URL), bearer case variants, env names with digits (`AWS2_SECRET=`), overlapping classes (a bearer value that starts with `sk-`), idempotence (`redact(redact(s)) == redact(s)` for every placeholder). For each: the secret bytes in the canonical output yes/no.
5. **canonical shapes**: bool, None, float, NaN, a big int, a negative int, a nested dict and list, two keys equal after NFC (an NFD key beside its NFC twin: two output keys or one?), a non-str key, the newline refusal (`canonical.py:30` puts `s[:32]` of the offending value into the exception text: can that be a secret when `canonical()` is called outside the pipeline?). C-F6's reason naming.
6. **Golden independence**: the seven digests recomputed with an oracle the lane did not write — stdlib `json.dumps(redact(normalize(...)), sort_keys=True, ensure_ascii=False, separators=(",", ":"))` → sha256 — equal to the test's pasted table? (The coordinator measured equal; reproduce.) Then say what that equality does and does not prove: normalize and redact are shared by both sides, so a defect in them passes both.
7. **Mutants** (scratch copy, AF-AP-78 discipline, the killing test NAMED per row): re-run the lane's m1-m6 (the brief's rows) and add at least: m7 drop the `sorted()` of list keys; m8 drop `strip_pin`; m9 remove the bool refusal (`canonical.py:56-58`); m10 change one placeholder's text; m11 `EXCERPT_LIMIT` 400 → 401; m12 whitespace collapse `\s+` → ` +`; m13 drop the enum case rule; m14 drop the NFC in `_canon_str`. A mutant no test kills is a finding (the property is untested) or an equivalent mutant (prove it).
8. **Grade C-F1..C-F7** by the predicate, one row each: reproduced yes/no (your own run), contract-mapped (which item; a contract self-contradiction is CONTRACT-INVALID, not a code defect), materially effective (what reaches J1-2's ledger when it lands), the discriminator (the smallest input), in boundary. For C-F1 name the smallest contract amendment that makes items 2, 3 and 6 hold together.
9. **v1.finding_class**: its state carries `disposition ∈ {BLOCKING, NON-BLOCKING}` while its options are `{SOLID, UNSURE} × {BLOCKING, NON-BLOCKING}` (item 1). Does the state carry half of the answer the question asks for? Grade against the pinned decision at `tasks/laya-j1-breakdown.md:16` and the lane's `test_closed_schema_refuses_incumbent_answer_key`.
10. **The tests themselves**: each of the 14 against the contract's Tests list (which contract test maps to which function; any contract test missing; any test that would pass with the pipeline replaced by a constant digest, i.e. a mirror). `test_secret_redacted_every_class` uses secrets far below every limit: say whether any test places a secret near a bound.

## Report (`tasks/briefs/laya/VERIFY-J1-1-report.md`)
DATA, not prose: the reproduction table (claim → instrument → observed → SOLID/UNSURE), the shape tables (items 3, 4, 5), the fixture-variant table (item 2), the mutant table (item 7), the predicate table (C-F1..C-F7 + your own findings against the five conjuncts), then the GATE RECOMMENDATION. A shape you could not run is `NOT run: <reason>`, never omitted. `python3 scripts/report_lint.py --min-refs 15 <your report> --root .` WITHOUT `--map` flags: cite full repo-relative paths (≤ 3 fix rounds, then paste and finish).

## PREMISE — MEASURED at authoring (2026-09-23T02:42:17Z, sandbox @ 52c02ee)
```
$ date -u; git rev-parse --short HEAD; git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf | cut -c1-70
2026-09-23T02:42:17Z
52c02ee
52c02ee transcripts: scrubbed sandbox chat digests (2026-09-23)
$ for f in <boundary>; do sha256(git show 52c02ee:$f)[:16]; lines; done
2aec3875f71213e4   21 src/agent_factory/decisions/__init__.py
bc9cb1d03fdb77a4   77 src/agent_factory/decisions/canonical.py
b48899c883c7231f  295 src/agent_factory/decisions/volatile.py
48fdf09e8038a146  340 tests/test_decisions_canonical.py
59fb4a16b20ffb1c   19 tests/fixtures/decisions/golden/ap.violates_row.json
fd8d0b3e63e26505   15 tests/fixtures/decisions/golden/b1.finding_kind.json
19d9938ddf81e0bd   15 tests/fixtures/decisions/golden/b1.finding_sev.json
f955714a99c6ad99   15 tests/fixtures/decisions/golden/b2.hit_role.json
9013f618e3976149   13 tests/fixtures/decisions/golden/d1.bug_echo_scores.json
ef01963a2041265a   25 tests/fixtures/decisions/golden/v1.finding_class.json
e0dc010dc24c50ca   17 tests/fixtures/decisions/golden/wf.drift.json
$ git diff --quiet 52c02ee -- src/agent_factory/decisions tests/test_decisions_canonical.py tests/fixtures/decisions/golden && echo 'tree == 52c02ee on the boundary'
tree == 52c02ee on the boundary
$ mkdir -p /tmp/vj11/p && /root/venv-agent-factory/bin/python -m pytest tests/test_decisions_canonical.py -q -p no:cacheprovider --basetemp=/tmp/vj11/p/bt | tail -1
14 passed in 0.03s
$ grep -n '^def test_' tests/test_decisions_canonical.py
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
$ grep -n -E '^_(SK|TOKEN|BEARER|ENVVAL|PRIVKEY) = |^EXCERPT_LIMIT|^MSG_LIMIT|s = s\[: f.limit\]|^def (normalize|redact|_redact_str|_path|_normalize_field|_strip_pin_suffix)|split\(\)\[0\]|startswith\("\.\."\)' src/agent_factory/decisions/volatile.py
26:EXCERPT_LIMIT = 400            # ap.violates_row.action_excerpt, wf.drift.observed/expected
27:MSG_LIMIT = 200               # b1.finding_sev / b1.finding_kind msg (bounded, not verbatim)
41:_BEARER = re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/-]{16,}=*")
42:_SK = re.compile(r"sk-[A-Za-z0-9_-]{8,}")
48:_TOKEN = re.compile(r"(?i)\btoken(?:[:=] ?| )?([A-Za-z0-9+/]{32,})")
52:_ENVVAL = re.compile(
56:_PRIVKEY = re.compile(
83:def _strip_pin_suffix(value: str) -> str:
98:def _path(key: str, value: str, root: str | os.PathLike | None) -> str:
110:            return rel if not rel.startswith("..") else _refuse_path(key, s)
113:    if rel.startswith("..") or "/../" in rel:
130:def _normalize_field(f: _Field, key: str, value, root):
143:        s = s[: f.limit]
147:        return _path(key, s.split()[0] if s.split() else s, root)
242:def normalize(question_id: str, state: dict, root: str | os.PathLike | None = None) -> dict:
271:def redact(state: dict) -> dict:
286:def _redact_str(text: str) -> str:
$ grep -n -E 'decision-canonical-|sorted\(value|^def ' src/agent_factory/decisions/canonical.py
26:def _canon_str(value) -> str:
30:        raise DecisionStateError("decision-canonical-newline", s[:32])
34:def canonical(obj) -> str:
42:def _canon(value, path: str) -> str:
47:        for k in sorted(value, key=lambda key: str(key)):
58:        raise DecisionStateError("decision-canonical-float", path)
62:        raise DecisionStateError("decision-canonical-float", path)
64:        raise DecisionStateError("decision-canonical-float", path)
67:    raise DecisionStateError("decision-canonical-type", path)
70:def state_digest(question_id: str, state: dict, root: str | None = None) -> str:
$ python3: each golden fixture's top-level keys and root
ap.violates_row.json ['expected_digest', 'question_id', 'root', 'state', 'variant'] root= /home/rocco/agent-factory
b1.finding_kind.json ['expected_digest', 'question_id', 'root', 'state', 'variant'] root= /home/rocco/agent-factory
b1.finding_sev.json ['expected_digest', 'question_id', 'root', 'state', 'variant'] root= /home/rocco/agent-factory
b2.hit_role.json ['expected_digest', 'question_id', 'root', 'state', 'variant'] root= /home/rocco/agent-factory
d1.bug_echo_scores.json ['expected_digest', 'question_id', 'root', 'state', 'variant'] root= /home/rocco/agent-factory
v1.finding_class.json ['expected_digest', 'question_id', 'root', 'state', 'variant'] root= /home/rocco/agent-factory
wf.drift.json ['expected_digest', 'question_id', 'root', 'state', 'variant'] root= /home/rocco/agent-factory
$ /root/venv-agent-factory/bin/python /tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vj11_probe.py   (the coordinator's probe script, reproduced in the brief's appendix)
-- goldens: fixture expected_digest == the test's pasted table == pipeline; canonical() == stdlib json form
ap.violates_row fixture==pipeline: True | in test table: True | canonical()==json.dumps: True
b1.finding_kind fixture==pipeline: True | in test table: True | canonical()==json.dumps: True
b1.finding_sev fixture==pipeline: True | in test table: True | canonical()==json.dumps: True
b2.hit_role fixture==pipeline: True | in test table: True | canonical()==json.dumps: True
d1.bug_echo_scores fixture==pipeline: True | in test table: True | canonical()==json.dumps: True
v1.finding_class fixture==pipeline: True | in test table: True | canonical()==json.dumps: True
wf.drift fixture==pipeline: True | in test table: True | canonical()==json.dumps: True
-- C-F1 (the bound before redaction)
sk- straddling 400: 'sk-ABCDEF' in output = True | placeholder = False
PEM body 1500: header in output = True | key chars 'Q' in output = 344
-- C-F2 (sk- without a word boundary)
'task-implementer failed' -> "msg":"ta<redacted:sk> failed"}
'disk-space-check ok' -> "msg":"di<redacted:sk> ok"}
'risk-assessment note' -> "msg":"ri<redacted:sk> note"}
-- C-F3 (missed forms)
'token = AAAAAAAAAAAAAAAA' redacted = False
'password=hunter2secret' redacted = False
'Token: AAAAAAAAAAAAAAAAA' redacted = True
-- edge shapes (questions for the lane, measured here)
'./src/x.py' == 'src/x.py' digest: False
'src//x.py' == 'src/x.py' digest: False
'src/x.py/' == 'src/x.py' digest: False
'src/./x.py' == 'src/x.py' digest: False
canonical True -> decision-canonical-float: $.k
canonical None -> decision-canonical-float: $.k
canonical 1.5 -> decision-canonical-float: $.k
target '/usr/bin/python3 -m pytest' refused: decision-state-abs-path: action_target
msg int 5 -> '5'
msg dict -> "{'a': 1}"
```

### Appendix — the coordinator's probe script (run it from the lane tree: `/home/rocco/venv-agent-factory/bin/python <this script>`)
```python
import glob, hashlib, json, sys
sys.path.insert(0, "src")
from agent_factory.decisions.volatile import normalize, redact, DecisionStateError
from agent_factory.decisions.canonical import canonical, state_digest
T = open("tests/test_decisions_canonical.py").read()
print("-- goldens: fixture expected_digest == the test's pasted table == pipeline; canonical() == stdlib json form")
for f in sorted(glob.glob("tests/fixtures/decisions/golden/*.json")):
    d = json.load(open(f)); q = d["question_id"]; st = redact(normalize(q, d["state"], d.get("root")))
    std = json.dumps(st, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    dig = state_digest(q, d["state"], d.get("root"))
    print(q, "fixture==pipeline:", d["expected_digest"] == dig, "| in test table:", dig in T, "| canonical()==json.dumps:", canonical(st) == std)
base = {"action_kind": "edit", "action_target": "src/x.py", "row_id": "AF-AP-1", "row_title": "t"}
def out(q, s, root=None): return canonical(redact(normalize(q, s, root)))
print("-- C-F1 (the bound before redaction)")
o = out("ap.violates_row", dict(base, action_excerpt="a"*390 + " sk-ABCDEFGHIJKLMNOPQRST"))
print("sk- straddling 400: 'sk-ABCDEF' in output =", "sk-ABCDEF" in o, "| placeholder =", "<redacted:sk>" in o)
pem = "-----BEGIN RSA PRIVATE KEY-----\nMIIEpAIBAAKCAQEA" + "Q"*1500 + "\n-----END RSA PRIVATE KEY-----"
o = out("ap.violates_row", dict(base, action_excerpt="context: " + pem))
print("PEM body 1500: header in output =", "BEGIN RSA PRIVATE KEY" in o, "| key chars 'Q' in output =", o.count("Q"))
print("-- C-F2 (sk- without a word boundary)")
for w in ("task-implementer failed", "disk-space-check ok", "risk-assessment note"):
    o = out("b1.finding_sev", {"file": "src/x.py", "kind": "k", "msg": w}); print(repr(w), "->", o[o.index('"msg":'):])
print("-- C-F3 (missed forms)")
for s in ("token = " + "A"*40, "password=hunter2secret", "Token: " + "A"*40):
    o = out("ap.violates_row", dict(base, action_excerpt=s)); print(repr(s[:24]), "redacted =", "<redacted:" in o)
print("-- edge shapes (questions for the lane, measured here)")
for p in ("./src/x.py", "src//x.py", "src/x.py/", "src/./x.py"):
    try: print(repr(p), "== 'src/x.py' digest:", state_digest("b1.finding_sev", {"file": p, "kind": "k", "msg": "m"}) == state_digest("b1.finding_sev", {"file": "src/x.py", "kind": "k", "msg": "m"}))
    except DecisionStateError as e: print(repr(p), "refused:", e)
for v in (True, None, 1.5):
    try: canonical({"k": v})
    except DecisionStateError as e: print("canonical", repr(v), "->", e)
try: print("target '/usr/bin/python3 -m pytest' ->", normalize("ap.violates_row", dict(base, action_kind="command", action_target="/usr/bin/python3 -m pytest", action_excerpt="x"), "/home/rocco/agent-factory")["action_target"])
except DecisionStateError as e: print("target '/usr/bin/python3 -m pytest' refused:", e)
try: print("msg int 5 ->", repr(normalize("b1.finding_sev", {"file": "src/x.py", "kind": "k", "msg": 5})["msg"]))
except DecisionStateError as e: print("msg int refused:", e)
try: print("msg dict ->", repr(normalize("b1.finding_sev", {"file": "src/x.py", "kind": "k", "msg": {"a": 1}})["msg"]))
except DecisionStateError as e: print("msg dict refused:", e)
```
