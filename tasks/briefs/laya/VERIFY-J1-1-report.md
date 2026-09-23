# VERIFY-J1-1 — report (sandbox continuation, task #130)

ROLE: adversarial-verifier, sandbox (Opus 5.5). PIN 52c02ee. Sandbox HEAD at start: 179fa77 (the brief's 3d89549 + one commit that adds only the two briefs).
Contract: `tasks/briefs/laya/J1-1-brief.md` items 1-6 + Tests + mutant rows; seed AC 1 / AC 3; breakdown pinned decisions + row J1-1; verdict acceptance test 1.
Evidence rule: every row below is my own run in this session (instrument named). The PC partial draft was read as hypotheses only; nothing in it is cited as evidence.
Status legend: SOLID = reproduced here with a deterministic command; UNSURE = reasoning or partial measurement.
Scratch: `/tmp/vj11s/` (a `git archive 52c02ee` copy for mutants; ledgers under it). Interpreter `/root/venv-agent-factory/bin/python` 3.11.15.

## 0. PREMISE re-measured (item 1 identities)

```
$ date -u   -> 2026-09-23T10:58:09Z (start);  git rev-parse --short HEAD -> 179fa77
$ git show --stat 179fa77  -> only tasks/briefs/laya/VERIFY-J1-1-pc-draft-PARTIAL.md + VERIFY-J1-1-sandbox.md
$ git diff --stat 52c02ee HEAD -- <11 boundary files>  -> (empty), rc=0
sha256[:16] at PIN / HEAD / worktree, lines:
2aec3875f71213e4 2aec3875f71213e4 2aec3875f71213e4   21 src/agent_factory/decisions/__init__.py
bc9cb1d03fdb77a4 bc9cb1d03fdb77a4 bc9cb1d03fdb77a4   77 src/agent_factory/decisions/canonical.py
b48899c883c7231f b48899c883c7231f b48899c883c7231f  295 src/agent_factory/decisions/volatile.py
48fdf09e8038a146 48fdf09e8038a146 48fdf09e8038a146  340 tests/test_decisions_canonical.py
59fb4a16b20ffb1c x3   19 golden/ap.violates_row.json   | fd8d0b3e63e26505 x3 15 golden/b1.finding_kind.json
19d9938ddf81e0bd x3   15 golden/b1.finding_sev.json    | f955714a99c6ad99 x3 15 golden/b2.hit_role.json
9013f618e3976149 x3   13 golden/d1.bug_echo_scores.json| ef01963a2041265a x3 25 golden/v1.finding_class.json
e0dc010dc24c50ca x3   17 golden/wf.drift.json
```
At the finish (2026-09-23T11:27:19Z) HEAD was e4ce195 (other lanes committed during the run; the brief commit 179fa77 became c700276 on push); `git diff --stat 179fa77 HEAD` over the J1-1 boundary was empty, and the working tree still equalled 52c02ee on the boundary (`tree == 52c02ee on the boundary`).
The premise holds: the boundary is byte-identical at the PIN, HEAD and the working tree. `ledger.py` exists at HEAD (J1-2 `9d11c25`, J1-2-R1 `d4f4698`). No CONTRACT-INVALID stop on the premise.

## 1. Item 1 — landing gates (reproduction table)

| # | Claim | Instrument | Observed (pasted) | Status |
|---|---|---|---|---|
| 1.1 | suite green x2 | `python -m pytest tests/test_decisions_canonical.py -q -p no:cacheprovider --basetemp=/tmp/vj11s/bt` twice, basetemp removed between | `run1-rc=0 :: 14 passed in 0.03s` · `run2-rc=0 :: 14 passed in 0.06s` | SOLID |
| 1.2 | per-test outcomes bitwise equal | `-v` outcome lines of two runs, `cmp` | 14 lines each, sha `3a541a0f76e05610` both, `per-test outcomes bitwise equal` | SOLID |
| 1.3 | pyflakes clean | `python -m pyflakes` on the four files; again on the HEAD glob `decisions/*.py` (adds `ledger.py`) | `pyflakes-rc=0` · `pyflakes-glob-rc=0` (0 hits) | SOLID |
| 1.4 | AP screen (FLAG form) | `python3 scripts/ap_screen.py --tests <canonical.py volatile.py test file>` | `--- TEST_SCREEN over 3 path(s): 0 hits over 3 files ---` `ap-screen-rc=0` | SOLID |
| 1.5 | seed AC 3 verbatim | `python -m pytest tests/test_decisions_canonical.py -q` (`python` = `/usr/local/bin/python` 3.11.15) | `14 passed in 0.03s` `AC3-rc=0` | SOLID |
| 1.6 | seed AC 1 verbatim at HEAD (a question, not an expectation) | `python3 -c "import agent_factory.decisions as d, agent_factory.decisions.canonical, agent_factory.decisions.ledger; print('OK')"` | system `python3` = `/usr/local/bin/python3`: `ModuleNotFoundError: No module named 'agent_factory'` `AC1-bare-rc=1` (the package is not on that interpreter's path; the ledger import is never reached) | SOLID |
| 1.7 | AC 1 with the path fixed | same command with `PYTHONPATH=src` (system python3) and with the venv interpreter (no PYTHONPATH; the venv holds `__editable__.agent_factory-0.1.0.pth`) | `OK` `AC1-src-rc=0` · `OK` `AC1-venv-no-PYTHONPATH-rc=0` | SOLID |
| 1.8 | the PC brief's "AC 1 RED on the ledger import by design" | 1.6 + 1.7 | FALSE at HEAD: `ledger.py` exists; the import succeeds whenever the package is importable. AC 1's only red is environmental (the seed command names bare `python3`) | SOLID |
| 1.9 | builder lint, no maps | `python3 scripts/report_lint.py tasks/briefs/laya/J1-1-report.md --root .` | `report_lint: 15 refs — OK 3, NEAR 0, MISS 0, UNCHECKABLE 12, UNRESOLVED 0 (worktree)` | SOLID |
| 1.10 | builder lint, five maps | same with `--map C=… V=… T=… B=… L=…` | `report_lint: 29 refs — OK 17, NEAR 0, MISS 0, UNCHECKABLE 12, UNRESOLVED 0 (worktree)` = the builder's own final line | SOLID |

Observation O-1 (INFO): with the five maps, 17 of the builder report's 29 refs check OK and 12 (41%) are UNCHECKABLE; without the maps only 3 refs check OK. The report's claims were therefore re-derived here, not trusted.
Observation O-2 (INFO): AC 1's verify_command names bare `python3`; it is green only where the package is importable (the sandbox venv or `PYTHONPATH=src`). Not a J1-1 code defect.

## 2. Item 2 — the seven schemas vs contract item 1

Instrument: `/tmp/vj11s/probes/item2.py` (imports `SCHEMAS` and `normalize` from the tree's `src/`).

| question_id | contract keys (`tasks/briefs/laya/J1-1-brief.md:8-15`, the `SCHEMAS` list) | `SCHEMAS[qid]` measured (kind, limit, case, enum) | match |
|---|---|---|---|
| b2.hit_role | sym, file (repo-relative), snippet | sym(str,120) file(path) snippet(str,400) | keys EXACT |
| b1.finding_sev | file, kind, msg | file(path) kind(str,80) msg(str,200) | keys EXACT |
| b1.finding_kind | file, kind, msg; options_max 8 | same + `OPTIONS_MAX`=8 | keys EXACT |
| d1.bug_echo_scores | class_slug, finding_title | class_slug(str,80) finding_title(str,120); `OPTIONS_MAX`=30 | keys EXACT |
| v1.finding_class | lane (PIN suffix stripped), finding_id, title, paths (sorted), disposition | lane(str,80,strip_pin) finding_id(str,80) title(str,120) paths(list) disposition(str,40,upper, enum BLOCKING, NON-BLOCKING) | keys EXACT |
| ap.violates_row | action_kind ∈ 4, action_target (path or leading token), action_excerpt ≤ 400, row_id, row_title | action_kind(str,20,lower,enum 4) action_target(target, no limit) action_excerpt(str,400) row_id(str,40) row_title(str,120) | keys EXACT, enum EXACT |
| wf.drift | step_id ∈ 10, expected, observed ≤ 400, drift_kind ∈ 5 | step_id(str,40,lower,enum 10) expected(str,400) observed(str,400) drift_kind(str,40,lower,enum 5) | keys EXACT, enums EXACT |

The limits 120/80/40/20 on the short keys and `MSG_LIMIT` 200 are the builder's own choice (the contract names only 400, for the excerpts). `EXCERPT_LIMIT` 400 and `MSG_LIMIT` 200 are set at `src/agent_factory/decisions/volatile.py:26-27`. The `SCHEMAS` mapping sits at `src/agent_factory/decisions/volatile.py:153`. SOLID.

Refusal strings, measured on EACH type (probe output pasted in part):
- unknown key: all 7 types x 5 locator keys (`line`, `timestamp`, `run_id`, `pin_sha`, `abs_path`) = 35/35 give exactly `decision-state-unknown-key: <qid>.<key>`, e.g. `decision-state-unknown-key: wf.drift.run_id`. SOLID.
- missing key: every key of every type (25/25, counted from the probe output: `missing: 25 (exact-string: 25)`) gives exactly `decision-state-missing-key: <qid>.<key>`, e.g. `decision-state-missing-key: ap.violates_row.row_title`. SOLID.
- bad enum: the 4 enum keys (v1.disposition, ap.action_kind, wf.step_id, wf.drift_kind) x {`'MAYBE'`, `5`, `''`, `' '`} = 16/16 refused, e.g. `decision-state-bad-enum: v1.finding_class.disposition=5`. The other 4 types have no enum key (not applicable). SOLID.
- unknown question: `decision-question-unknown: nope.none`; the case variant `B1.finding_sev` is refused too. SOLID.
- extra refusal outside the contract: a non-dict state gives `decision-state-not-mapping: b1.finding_sev` (fail-closed; INFO).

Observation O-3 (INFO): precedence is per-key first, the unknown-key sweep second (`src/agent_factory/decisions/volatile.py:255-261`, `decision-state-unknown-key`): a state with both an unknown key and a bad path reports the path. The contract names no precedence.
Observation O-4 (INFO): the bad-enum text carries the RAW value unbounded (`src/agent_factory/decisions/volatile.py:267`, `decision-state-bad-enum`). The contract's format asks for `<value>`, so this is by design; a secret-shaped or 10 KB value reaches the exception text verbatim.

"Never accepted as state KEYS" (line numbers, timestamps, absolute paths, run ids, PIN SHAs): refused as keys on all 7 types (above). SOLID.
The same shapes as VALUES inside an allowed key (instrument `/tmp/vj11s/probes/item2b.py`; "digest ==" compares against the same state with another locator value):

| key | value | normalize output | digest equal to the other locator? |
|---|---|---|---|
| b1.msg | `… (2026-09-22T20:47:50Z)` vs `… (2026-09-23T01:02:03Z)` | unchanged | False |
| b2.snippet | `42: def validate_ledger(args):` vs `57: …` | unchanged | False |
| b1.msg | `src/x.py:42: unused import` vs `:57:` | unchanged | False |
| v1.title | `… at 330803c` vs `… at 52c02ee` | unchanged | False |
| b1.msg | `run 20260922-204750 failed` vs another run id | unchanged | False |
| b1.msg / d1.finding_title | `see /home/rocco/agent-factory/src/x.py` vs `see src/x.py` | unchanged (no relativization in free text) | False |
| wf.observed | `ran at <ts> on line 42` vs another ts and line | unchanged | False |
| v1.finding_id | `F-7@330803c` vs `F-7@52c02ee` | unchanged | False |
| v1.lane | `pc-j1-1--330803c` vs `pc-j1-1` | `pc-j1-1` (stripped) | True |

Finding F-2 (FOLLOW-UP): locator-shaped VALUES pass through normalize into the digest. Only `v1.lane`'s PIN suffix and path-kind keys are normalized. The closed schema keeps locators out as KEYS (the brief's reading of AC 3 at `tasks/briefs/laya/J1-1-brief.md:16`); the seed's AC 3 text ("strip line numbers, timestamps, absolute paths, and run ids") is not met for free text, and the breakdown row J1-1 names "a re-landed finding (line numbers, PIN, abs path, timestamp changed) hashes identical". Stripping line numbers from free prose cannot be done without false positives, so this is a harvest (J1-3) extraction duty or a contract clarification, not a J1-1 repair. SOLID (measured), contract mapping UNSURE.

Fixture-variant classes actually exercised (char-level classification of `variant` vs `state`, same probe):

| fixture | exercised | VACUOUS (named by item 5, not exercised) | other |
|---|---|---|---|
| b2.hit_role | abs-path-under-root, extra-whitespace | pin-suffix, nfd, line-numbers | — |
| b1.finding_sev | abs-path-under-root, extra-whitespace | pin-suffix, nfd, line-numbers | — |
| b1.finding_kind | abs-path-under-root, extra-whitespace | pin-suffix, nfd, line-numbers | — |
| d1.bug_echo_scores | extra-whitespace, nfd (variant `e`+U+0301; state U+00E9) | abs-path (no path key), pin-suffix, line-numbers | — |
| v1.finding_class | abs-path-under-root, pin-suffix, extra-whitespace | nfd, line-numbers | enum-case, list-order |
| ap.violates_row | abs-path-under-root, extra-whitespace | pin-suffix, nfd, line-numbers | — |
| wf.drift | extra-whitespace | abs-path (no path key), pin-suffix, nfd, line-numbers | — |

Totals: line-numbers 0/7 (VACUOUS for every type; if exercised in a value it would FAIL, table above), timestamp 0/7, nfd 1/7, pin-suffix 1/7 (only v1 has a pin-stripped key), abs-path 5/7 (d1 and wf have no path key), whitespace 7/7. SOLID.
Correction to the PC draft (hypothesis H-2e): d1's variant exercises whitespace AND nfd, not "nfd-vs-nfc ONLY".

## 3. Item 3 — normalize shapes (instrument `/tmp/vj11s/probes/item3.py`; every output pasted from its run)

Legend: STABLE = two spellings, one digest · REFUSED = named reason · WRONG = silently accepted with a wrong or colliding value · INFO = accepted, plausible.

Paths (`b1.finding_sev.file`, root `/home/rocco/agent-factory` unless named; "same" = digest equal to `src/x.py`):

| input | output | class |
|---|---|---|
| `<root>/src/x.py` | `src/x.py`, same=True | STABLE |
| `/etc/passwd` | `decision-state-abs-path: file` | REFUSED |
| `<root>` and `<root>/` | `.` | INFO |
| `~/x.py`, `~` | `decision-state-abs-path: file` (never expanded) | REFUSED |
| `..`, `../x.py`, `...`, `..foo` | `decision-state-abs-path: file` (`...`/`..foo` are legal names: over-refusal) | REFUSED |
| `a/../b`, `src/../src/x.py` | `decision-state-abs-path: file` | REFUSED (while `<root>/../agent-factory/src/x.py` gives `src/x.py`: the absolute spelling is accepted, the relative one refused) |
| `x/..` | `x/..` | WRONG (not normalized; means `.`) |
| `./src/x.py`, `src//x.py`, `src/x.py/`, `src/./x.py` | unchanged, same=False each | WRONG (C-F4 reproduced) |
| `' src/x.py '` | `src/x.py`, same=True | STABLE |
| `src/my  file.py` | `src/my file.py` (two names collapse into one) | WRONG (0 tracked paths hold whitespace: `git ls-files` count 0) |
| root with trailing `/` | `src/x.py`, same=True | STABLE |
| relative root `rocco/agent-factory` + absolute path | `decision-state-abs-path: file` | REFUSED |
| root `None` + absolute path | `decision-state-abs-path: file` | REFUSED (fail-closed) |
| root `/` + `/src/x.py` | `decision-state-abs-path: file` (root `/` refuses every absolute path) | INFO |
| root `''` + absolute path | refused | INFO |
| root as `PosixPath` | `src/x.py` | STABLE |
| `<root>X/src/x.py` (sibling prefix) | refused | REFUSED (correct) |
| `<root>/src/../../etc/passwd` | refused | REFUSED (correct) |
| `''`, `.` | `''`, `.` accepted | INFO (an empty path is accepted) |
| `src\x.py`, `C:\x.py` | unchanged | INFO |

Whitespace kinds in `msg` (`'a' + WS + 'b'`): tab, newline, CR, CRLF, NBSP U+00A0, U+2028, U+2029, VT, FF, U+3000, U+202F, U+0085, two spaces all give `'a b'` (STABLE). Zero-width and format characters are NOT whitespace to `\s`: ZWSP U+200B → `'a\u200bb'`, WJ U+2060, BOM U+FEFF, U+180E are kept (a variant with them hashes differently; INFO). Leading and trailing runs are stripped. SOLID.

NFC: `é` NFC vs NFD same digest True; Hangul syllable U+AC01 vs jamo same True; U+212B vs U+00C5 same True; the `ﬁ` ligature vs `fi` differ (NFKC only; the contract says NFC). SOLID.

Truncation (`ap.violates_row.action_excerpt`, limit 400; the cut is on code points after NFC and the collapse):

| input | len in → out | tail | note |
|---|---|---|---|
| exactly 400 | 400 → 400 | `aaa` | |
| 401 | 401 → 400 | `aaa` | |
| 399 x `a` + `' b'` | 401 → 400 | `'aa '` | **the output ENDS WITH A SPACE** |
| 398 x `a` + a 3-space run + `b` | 402 → 400 | `a b` | the run collapses before the cut |
| 399 x `a` + `e`+U+0301 | 401 → 400 | `aaé` (NFC composed first) | |
| 399 x `a` + `q`+U+0301 | 401 → 400 | `aaq` (the combining mark is cut off; the result is still NFC) | INFO |
| 400 x (`e`+U+0301) | 800 → 400 | `ééé` | |

Finding F-3 (FOLLOW-UP in J1-1; its integration effect is measured in section 8): normalize is not idempotent. The collapse and strip run BEFORE the cut (`src/agent_factory/decisions/volatile.py:138`, `_nfc_collapse`, then the cut at `src/agent_factory/decisions/volatile.py:143`, `s = s[: f.limit]`), so a cut that lands after a space leaves a trailing space. Pasted: `idempotence: normalize(normalize(x)) == normalize(x) for '399a + space + b': False | len 400 -> 399`; the same on `msg` (limit 200): `'199m + space + z' -> 200 trailing_space True`. Item 2 says "collapse runs of whitespace to one space and strip"; the output is not stripped. SOLID.

strip_pin (`v1.lane`): `--330803c` (7 hex), 40 hex, `--330803CA` (upper hex), `team--alpha--330803c` → `team--alpha`, `pc-j1-1.md--52c02ee` → `pc-j1-1.md`: stripped. 41 hex, 6 hex, `--zzzzzzz`, a single `-` (`pc-j1-1-330803c`), a trailing `--` after the PIN, and a PIN followed by U+200B: kept. Edge: `--330803c` alone becomes `''` (an empty lane; INFO). Case is kept: `PC-J1-1--330803C` → `PC-J1-1` (differs from `pc-j1-1`; INFO). The rule matches `re.sub(r"--[0-9a-fA-F]{7,40}$", …)` at `src/agent_factory/decisions/volatile.py:89`. SOLID.

Target (`ap.violates_row.action_target`):

| input (action_kind) | output | class |
|---|---|---|
| `/usr/bin/python3 -m pytest` (command) | `decision-state-abs-path: action_target` | REFUSED (C-F7 reproduced) |
| `/usr/bin/env python3 x.py` (command) | `decision-state-abs-path: action_target` | REFUSED (C-F7 family) |
| `python3 -m pytest` | `python3` | STABLE |
| `sudo x` | `sudo` | INFO (the leading token is `sudo`, not the command) |
| `FOO=bar python3 x.py` | `FOO=bar` | WRONG (an env prefix is taken as the command) |
| `PC_BRIDGE_TOKEN=abcdef0123456789 curl x` (a FAKE value) | `PC_BRIDGE_TOKEN=abcdef0123456789` after normalize; redact then gives `PC_BRIDGE_TOKEN=<redacted:envval>` (section 4) | INFO |
| `''`, `'   '` | `''` | INFO (an empty target is accepted) |
| `<root>/scripts/check.py --x` | `scripts/check.py` | STABLE |
| `~/bin/tool arg`, `../x.sh` | refused | REFUSED |
| `./scripts/x.sh --flag` | `./scripts/x.sh` (not normalized; C-F4 family) | WRONG |
| 5,000-char token | 5,000 chars kept (the target has no limit) | INFO |
| `docs/my file.md` with `action_kind=edit` | `docs/my` | WRONG: the leading-token rule runs for EVERY action_kind (`src/agent_factory/decisions/volatile.py:147`, `s.split()[0]`), while item 1 reserves it for a command. 0 tracked paths hold whitespace, so not material today |

Non-string values in string keys (C-F5 reproduced): `msg` 5 → `'5'`, `{'a': 1}` → `"{'a': 1}"`, 1.5 → `'1.5'`, None → `'None'`, True → `'True'`, `['x']` → `"['x']"`, `b'bytes'` → `"b'bytes'"`. Type collisions measured: None vs `'None'` same digest True; 5 vs `'5'` True; True vs `'True'` True. Path keys too: `file=None` → `'None'`, `file=5` → `'5'`. A float in state never reaches `canonical()`'s float refusal through `state_digest` (normalize stringifies it first). `paths`: a str, tuple or dict → `decision-state-bad-type: paths` (REFUSED); `[]` accepted; `[1, None]` → `['1', 'None']`; `[{'a': 1}]` → `["{'a': 1}"]`; `[['nested']]` → `["['nested']"]`; duplicates kept (`['b','a','a']` → `['a','a','b']`; `[<root>/a, 'a']` → `['a','a']`, which differs from `['a']`). SOLID.

## 4. Item 4 — redact shapes (instruments `/tmp/vj11s/probes/item4a.py`, `/tmp/vj11s/probes/item4b.py`; all secrets FAKE)

"secret in output" = the FAKE material appears in `canonical(redact(normalize(...)))`. Pasted from the runs.

| class / shape | input form (FAKE) | secret in output | output tail |
|---|---|---|---|
| sk positive | `key sk-FAKEfake…` | False | `key <redacted:sk>` |
| sk negative | `sk-ABCDEFG` (7 after `sk-`) | True (below the class minimum) | unchanged |
| bearer positive, lower/upper case | `Authorization: Bearer …`, `bearer …`, `BEARER …` | False | `<redacted:bearer>` |
| bearer negative | 15-char value | True (below 16) | unchanged |
| token | `token: <32hex>`, `Token: `, `token=`, `token `, `token<32>` | False | `token: <redacted:token>` etc. |
| token negative | 31 hex | True (below 32) | unchanged |
| C-F3 `token = <32>` | spaces around `=` | **True** | unchanged |
| C-F3 `"token": "<32>"` (JSON) | | **True** | unchanged |
| C-F3 `token: "<32>"` (quoted) | | **True** | unchanged |
| C-F3 `access_token=<32>`, `?access_token=<32>` in a URL | `\b` fails after `_` | **True** | unchanged |
| C-F3 `?api_key=<fake>` | | **True** | unchanged |
| C-F3 lowercase `password=<fake>`, `PASSWORD = <fake>`, `password: <fake>` | | **True** | unchanged |
| envval | `API_KEY=`, `PASSWORD=`, `AWS2_SECRET=` (digits), `AWS_SECRET_ACCESS_KEY=`, `export TOKEN="…"` | False | `NAME=<redacted:envval>` |
| envval colon form | `SECRET_KEY: <fake>` | **True** | unchanged |
| bridge `PC_BRIDGE_TOKEN=<fake>`, `AGENT_TOKEN=<fake32>` | | False | `…=<redacted:envval>` |
| bridge `PC_BRIDGE_TOKEN: <fake32>`, `AGENT_TOKEN: <fake32>` | colon form of the banner name (`PC-BRIDGE.md:10` names `AGENT_TOKEN`) | **True** | unchanged |
| bridge `X-Agent-Token: <fake32>` / 40-char base64 | the only accepted auth form (`PC-BRIDGE.md:21`, `X-Agent-Token`) | False | `X-Agent-Token: <redacted:token>` |
| token run with `-` (base64url) | `token: <16>-<16>` | True (the run class `[A-Za-z0-9+/]` stops at `-`) | unchanged |
| not contract classes | `GITHUB_PAT=ghp_…`, `Authorization: Basic …` | True | unchanged (INFO) |
| PEM RSA, EC, OPENSSH, ENCRYPTED, PKCS8, DSA | BEGIN…END with newlines (collapsed by normalize first) | False | `<redacted:privkey>` |
| PEM with END missing in the INPUT | | **True** | `-----BEGIN RSA PRIVATE KEY----- MIIEFAKEQQQ…` |
| PEM with a mismatched END label | | False | redacted |
| PGP `PRIVATE KEY BLOCK`, a mixed-case `Private` header | | True | unchanged (INFO: not contract classes; `scripts/transcript_export.py:29` covers PGP) |
| overlaps: `Bearer sk-…`, `TOKEN=sk-…`, `token: sk-…`, `sk-` inside a PEM | | False each | `Bearer <redacted:sk>`, `TOKEN=<redacted:envval>`, `token: <redacted:sk>`, `<redacted:privkey>` |
| idempotence `redact(redact(s)) == redact(s)` | each placeholder, `API_KEY=<redacted:envval>`, `token: <redacted:token>`, mixed strings | True for all 12 | |

C-F2 (word boundary) reproduced: `task-implementer failed` → `ta<redacted:sk> failed`; `disk-space-check ok`, `risk-assessment note`, `flask-sqlalchemy pin`, `mask-generation step`, `ask-questions-first rule` likewise. `'task-implementer failed' vs 'task-runner-queue failed' same digest: True`. The token class over-redacts identifiers too: `TokenizationPipelineConfigurationManager broke` → `Token<redacted:token> broke`. Frequency in real committed sources (`/tmp/vj11s/probes/freq.py`, 174 files = every `tasks/briefs/*/*-report.md` + `docs/INCIDENT-LOG.md`): `sk- matches=14, preceded by a letter (a word, not a key start)=2` (`task-implementer`, `disk-different`). SOLID.

The C-F1 straddle sweep (`item4b.py`): each bounded key, each class, the cut moved through every position of the secret; the cell is the longest prefix of the FAKE secret material found in the canonical output (max over positions) and the kept length where it occurs.

| key | limit | sk | bearer | token | envval | privkey |
|---|---|---|---|---|---|---|
| b2.hit_role.sym | 120 | 7 @10 | 15 @22 | 31 @38 | 0 | 88 @119 |
| b2.hit_role.snippet | 400 | 7 @10 | 15 @22 | 31 @38 | 0 | 368 @399 |
| b1.finding_sev.kind / b1.finding_kind.kind | 80 | 7 @10 | 15 @22 | 31 @38 | 0 | 48 @79 |
| b1.finding_sev.msg / b1.finding_kind.msg | 200 | 7 @10 | 15 @22 | 31 @38 | 0 | 168 @199 |
| d1.class_slug, v1.lane, v1.finding_id | 80 | 7 @10 | 15 @22 | 31 @38 | 0* | 48 @79 |
| d1.finding_title, v1.title, ap.row_title | 120 | 7 @10 | 15 @22 | 31 @38 | 0* | 88 @119 |
| ap.violates_row.action_excerpt | 400 | 7 @10 | 15 @22 | 31 @38 | 0* | 368 @399 |
| ap.violates_row.row_id | 40 | 7 @10 | 15 @22 | 31 @38 | 0 | 8 @39 |
| wf.drift.expected / observed | 400 | 7 @10 | 15 @22 | 31 @38 | 0 | 368 @399 |

\* the raw sweep printed `1ch@keep=1` on v1.lane, v1.title, ap.action_excerpt and ap.row_title: a metric artifact (the letter `F` of the FAKE material also occurs in the fixtures' `F-7` / `AF-AP-76`); envval leaks 0 characters because `NAME=\S+` replaces any 1+ character value.
Every class with a minimum length or an END marker leaks at every bounded key: sk up to 7 characters, bearer 15, token 31, and a private key up to (limit − 32) body characters. The coordinator's two inputs reproduce exactly: `sk straddling 400: 'sk-ABCDEF' in output = True | placeholder = False`; `PEM body 1500: header in output = True | key chars 'Q' in output = 344 | 'MIIEpAIBAAKCAQEA' in output = True`. SOLID.

Item 6's IDENTITY half also fails for any over-limit excerpt, even with the secret wholly INSIDE the limit (the cut keeps a different amount of the tail because the secret and its placeholder differ in length). Pasted: `sk secret-state digest == clean-state digest: False | len after redact: secret-form 374 vs clean-form 400`; bearer 374 vs 400; token 380 vs 400; envval 381 vs 400; privkey 308 vs 400. Control without the tail: `same digest True` for all five. SOLID.

Redaction can push a field PAST its bound (item 1 says `action_excerpt` is ≤ 400): `398 chars + ' KEY=x' (envval grows by 17) in=399 out=415 > 400: True`; `389 chars + ' sk-ABCDEFGH' (sk 11 -> 13) in=400 out=402 > 400: True`. SOLID.

## 5. Item 5 — canonical shapes (instrument `/tmp/vj11s/probes/item5.py`; printed with `ascii()`)

| input to `canonical()` | result | note |
|---|---|---|
| `{"k": True}`, `{"k": False}` | `decision-canonical-float: $.k` | C-F6 reproduced: a bool is refused (correct) under the float reason |
| `{"k": None}` | `decision-canonical-float: $.k` | C-F6 reproduced |
| `1.5`, NaN, inf | `decision-canonical-float: $.k` | correct |
| `10**100`, `-5` | `{"k":1000…}`, `{"k":-5}` | ints accepted |
| `10**5000` | `RAISED ValueError: Exceeds the limit (4300 digits) for integer string conversion` | an unnamed exception, not a DecisionStateError (also through `state_digest`: normalize's `str()` raises it) |
| nested dict and list; `{}`; `[]` | `{"a":{},"b":[1,{"a":[2,"y"],"z":"x"}]}` | sorted keys, list order kept |
| tuple, bytes, set | `decision-canonical-type: $.k` | refused |
| a non-str key `1`, `(1, 2)`, `None` | `{"1":"a"}`, `{"(1, 2)":"a"}`, `{"None":"a"}` | key types are not closed (INFO) |
| keys `5` and `"5"` in one dict | `{"5":"a","5":"b"}` vs `{"5":"b","5":"a"}` by insertion order | duplicate output keys, order-dependent (non-canonical; INFO: state keys are schema strings, so not reachable through `state_digest`) |
| an NFC key and its NFD twin | `{"é":2,"é":1}` | TWO output keys (duplicate after NFC) |
| the same logical dict with the key NFC vs NFD (`{"é":1,"f":2}`) | `'{"f":2,"\xe9":1}'` vs `'{"\xe9":1,"f":2}'`, equal: False | keys are sorted by the RAW string and emitted NFC (`src/agent_factory/decisions/canonical.py:47`, `sorted(value, key=lambda key: str(key))`); canonical is not NFC-invariant for non-ASCII keys (INFO: unreachable through the ASCII schema keys) |
| `"line1\nline2"`, `"a\rb"` | `decision-canonical-newline: line1\nline2` | refused |
| U+2028, U+0085 | `{"k":"a b"}`, `{"k":"a\x85b"}` accepted raw | "\n-free" holds literally; these are line breaks to `str.splitlines()` (AF-AP-132's class). Through the pipeline normalize collapses them first; J1-2 row fields that bypass normalize can carry them (adjacent, INFO) |
| lone surrogate `"\ud800"` | canonical OK; `state_digest` → `RAISED UnicodeEncodeError` | unnamed exception in J1-1 (J1-2's `make_row` wraps it, per its docstring) |
| top-level str / int / list | `"x"`, `5`, `[3,1,2]` | accepted |

The newline refusal copies the value's first 32 characters into the exception text (`src/agent_factory/decisions/canonical.py:30`, `decision-canonical-newline`, `s[:32]`). Measured with a FAKE key: `exception text: 'decision-canonical-newline: sk-FAKEfakeFAKEfake0123456789\nmo' | detail carries 'sk-FAKE': True`. Inside the pipeline normalize removes every newline first, so this never fires on state. It CAN fire when `canonical()` runs on un-redacted values outside the pipeline: J1-2's `make_row` calls `canonical()` on `incumbent_answer` and each `source_ref` field (`src/agent_factory/decisions/ledger.py:380`, `canonical(val).encode("utf-8")`). Finding F-5 (FOLLOW-UP, adjacent): a refusal text can carry up to 32 characters of a secret. SOLID.
Cross-check: `canonical(o) == json.dumps(o, sort_keys=True, ensure_ascii=False, separators=(",", ":"))` on a nested NFC str/int structure: True. SOLID.

## 6. Item 6 — golden independence (instrument `/tmp/vj11s/probes/item6.py`)

| fixture | Oracle A: sha256(stdlib `json.dumps` of the RAW committed clean `state`), NO J1-1 import | Oracle B (the brief's): stdlib json over `redact(normalize(state))` | variant through Oracle B | `state_digest` | clean state is a fixed point of `redact∘normalize` |
|---|---|---|---|---|---|
| ap.violates_row | == fixture, == test table | True | True | True | True |
| b1.finding_kind | == fixture, == test table | True | True | True | True |
| b1.finding_sev | == fixture, == test table | True | True | True | True |
| b2.hit_role | == fixture, == test table | True | True | True | True |
| d1.bug_echo_scores | == fixture, == test table | True | True | True | True |
| v1.finding_class | == fixture, == test table | True | True | True | True |
| wf.drift | == fixture, == test table | True | True | True | True |

The test's `GOLDEN_DIGESTS` table (`tests/test_decisions_canonical.py:42`) has 7 entries; all 7 equal the fixture `expected_digest`, and all 7 equal Oracle A. SOLID.
What this proves: `canonical()` + sha256 agree with the stdlib on these states; the goldens are the plain hash of hand-written, already-normal clean states (not a mirror of the code); each variant's equality therefore really exercises normalize's classes listed in section 2.
What it does NOT prove: Oracle B shares normalize and redact with the code, so a defect in them passes both sides. Oracle A shows the golden test itself would stay green with normalize and redact replaced by the identity (every clean state is a fixed point): `test_golden_digests_exact` pins canonical + sha256 + the fixture bytes only. No golden carries a secret, an over-limit field, a line number or a non-space whitespace kind, so none of C-F1, C-F2, C-F3, F-3 can show in a golden. SOLID.

## 7. Item 7 — mutants (driver `/tmp/vj11s/mutants.py` on the `git archive 52c02ee` copy; AF-AP-78)

Import check first: the copy's pytest imports `VOLATILE_FILE /tmp/vj11s/copy/src/agent_factory/decisions/volatile.py` (the venv's static `.pth` appends the tree's `src`; pytest's `pythonpath` puts the copy's `src` first). Run at `2026-09-23T11:18:10Z`. Baseline `rc=0 14 passed in 0.02s … collected=14`; final after all restores `rc=0 14 passed in 0.03s`; `restore sha verified after every row: {'V': 'b48899c883c7231f', 'C': 'bc9cb1d03fdb77a4'}`. Every row: py_compile rc 0, collected 14 (no syntax kill).

| # | mutant | pytest line | result | killing test(s) |
|---|---|---|---|---|
| m1 | drop normalize in `state_digest` | 2 failed, 12 passed | KILLED | test_order_is_normalize_then_redact, test_relanding_stable |
| m2 | drop redact in `state_digest` | 2 failed, 12 passed | KILLED | test_order_is_normalize_then_redact, test_secret_redacted_every_class |
| m3 | drop NFC in normalize (`_nfc_collapse`) only | 14 passed | **SURVIVED** | — |
| m3c | drop NFC in normalize AND `_canon_str` | 1 failed, 13 passed | KILLED | test_relanding_stable |
| m4 | allow floats | 1 failed, 13 passed | KILLED | test_float_refused |
| m5 | swap the order | 1 failed, 13 passed | KILLED | test_order_is_normalize_then_redact |
| m6 | open the schema | 2 failed, 12 passed | KILLED | test_closed_schema_refuses_incumbent_answer_key, test_unknown_key_refused |
| m7 | drop `sorted()` of list keys | 1 failed, 13 passed | KILLED | test_relanding_stable |
| m8 | drop strip_pin | 2 failed, 12 passed | KILLED | test_command_target_uses_leading_token_and_pin_strip_is_exact, test_relanding_stable |
| m9 | remove the bool refusal | 1 failed, 13 passed | KILLED | test_float_refused |
| m10 | sk placeholder text | 1 failed, 13 passed | KILLED | test_secret_redacted_every_class |
| m10b | token placeholder text | 2 failed, 12 passed | KILLED | test_order_is_normalize_then_redact, test_secret_redacted_every_class |
| m10c | bearer placeholder text | 1 failed, 13 passed | KILLED | test_secret_redacted_every_class |
| m10d | envval placeholder text | 14 passed | **SURVIVED** | — |
| m10e | privkey placeholder text | 1 failed, 13 passed | KILLED | test_secret_redacted_every_class |
| m11 | `EXCERPT_LIMIT` 400 → 401 | 14 passed | **SURVIVED** | — |
| m12 | collapse `\s+` → `' +'` | 14 passed | **SURVIVED** | — |
| m13 | drop the enum case rule | 2 failed, 12 passed | KILLED | test_command_target_uses_leading_token_and_pin_strip_is_exact, test_relanding_stable |
| m14 | drop the NFC in `_canon_str` | 14 passed | **SURVIVED** | — |
| m15a | token separator widened to `\s*[:=]?\s*` | 1 failed, 13 passed | KILLED | test_order_is_normalize_then_redact (the order test is coupled to the narrow separator) |
| m16 | drop `re.S` from `_PRIVKEY` | 14 passed | SURVIVED (equivalent on production paths, below) | — |
| m17 | `_SK` minimum 8 → 12 | 14 passed | **SURVIVED** | — |
| m18 | no truncation at all | 14 passed | **SURVIVED** | — |
| m19 | accept an abs path outside the root | 1 failed, 13 passed | KILLED | test_abs_path_outside_root_refused |
| m20 | drop the relative `..` refusal | 14 passed | **SURVIVED** | — |
| m21 | target keeps the whole command | 1 failed, 13 passed | KILLED | test_command_target_uses_leading_token_and_pin_strip_is_exact |
| m22 | root None accepts an abs path | 14 passed | **SURVIVED** | — |
| m23 | canonical key order unsorted | 2 failed, 12 passed | KILLED | test_golden_digests_exact, test_relanding_stable |
| m24 | drop the missing-key refusal | 1 failed, 13 passed | KILLED | test_missing_key_refused |
| m25 | drop the bad-enum refusal | 1 failed, 13 passed | KILLED | test_bad_enum_refused |

Survivors: equivalent or not (driver `/tmp/vj11s/equiv.py`, the pristine output vs the mutant output on one discriminating input; restores sha-verified):

| mutant | discriminating input | pristine → mutant | verdict |
|---|---|---|---|
| m3 | 400 x (`e`+U+0301) in `action_excerpt` | digest `5442c63281905e96` → `a5e3f87f76665280` | NOT equivalent: NFC must run before the cut (800 code points cut at 400 = 200 characters); untested |
| m10d | `API_KEY=<fake>` | `<redacted:envval>` → `<redacted:ENVVAL>` | NOT equivalent: the clean form's placeholder is re-redacted by `NAME=\S+`, so the envval identity check is vacuous for the placeholder text; untested |
| m11 | a 450-char excerpt | 400 → 401 | NOT equivalent; the 400 bound is untested |
| m12 | `a\tb` vs `a b` | equal True → False | NOT equivalent; non-space whitespace collapse is untested (every variant uses spaces) |
| m14 | `canonical({"k": "é"})` | `{"k":"\xe9"}` → `{"k":"é"}` | NOT equivalent; canonical's own NFC (item 4) is untested |
| m16 | a multi-line PEM | pipeline False → False; direct `redact()` on raw multi-line text False → True | equivalent on every production path: all three production callers run `redact(normalize(...))` (graft callers: `state_digest`, `_validate_row`, `make_row`; literal sweep: `src/agent_factory/decisions/canonical.py:75` `redacted = redact(normed)`, and the two `redact(normalize(` calls at `src/agent_factory/decisions/ledger.py:274`, `src/agent_factory/decisions/ledger.py:405`), and normalize turns every newline into a space first. Not equivalent for a direct `redact()` call on raw text (none in production) |
| m17 | `k sk-FAKE1234` (8 after `sk-`) | leak False → True | NOT equivalent; the class minimum is untested (the test's key has 16) |
| m18 | a 450-char excerpt | 400 → 450 | NOT equivalent; NO test exercises the bound at all |
| m20 | `../x.py` | refused → accepted | NOT equivalent; the relative traversal refusal is untested |
| m22 | `/etc/passwd`, root None | refused → accepted | NOT equivalent; the root-None refusal is untested |

Builder claims vs this run: m1, m2, m4, m5, m6 reproduce (same killing tests as the builder's rows). The builder's m3 row ("drop NFC → 1 failed … test_relanding_stable") reproduces only as m3c (both NFCs dropped); dropping normalize's NFC alone survives. SOLID.
Finding F-6 (FOLLOW-UP): 9 non-equivalent survivors = 9 untested properties (m3, m10d, m11, m12, m14, m17, m18, m20, m22). m18 means the BOUNDED property of the pinned decision has no test at all, which is how C-F1 passed the landing gate.

## 8. Item 8 — materiality through the REAL ledger append path (instrument `/tmp/vj11s/probes/item8_ledger.py`)

Each C-F input went through J1-2's public API (`make_row` then `append`, then `replay`), one ledger file per case under `/tmp/vj11s/ledger/`; the written BYTES were searched for the FAKE secret. The ledger is outside this lane's boundary: its behavior here is evidence of J1-1's material effect, never a J1-2 finding. Pasted:

```
C-F1 sk straddle 400                       APPENDED … secret_bytes_in_ledger=True
C-F1 PEM body 1500                         APPENDED … secret_bytes_in_ledger=True
C-F1 bearer straddle msg 200               APPENDED … secret_bytes_in_ledger=True
C-F1 token straddle title 120              APPENDED … secret_bytes_in_ledger=True
C-F2 'task-implementer failed'             APPENDED … secret_bytes_in_ledger=False
C-F3 'token = <32>'                        APPENDED … secret_bytes_in_ledger=True
C-F3 'password=<fake>'                     APPENDED … secret_bytes_in_ledger=True
C-F3 'access_token=<32>'                   APPENDED … secret_bytes_in_ledger=True
C-F3 'PC_BRIDGE_TOKEN: <32>'               APPENDED … secret_bytes_in_ledger=True
C-F3 'AGENT_TOKEN: <32>'                   APPENDED … secret_bytes_in_ledger=True
control 'token: <32>'                      APPENDED … secret_bytes_in_ledger=False
control 'sk-<fake>' short                  APPENDED … secret_bytes_in_ledger=False
C-F5 msg None                              APPENDED …   |  C-F5 msg 'None'  APPENDED …
F-3 trailing space at the cut (excerpt)    REFUSED decision-row-state-not-canonical: 4597e9c3…
F-3 trailing space at the cut (msg)        REFUSED decision-row-state-not-canonical: ff9a8bea…
F-4 envval grows past the bound            APPENDED row_id=57b8e45004e9 bytes=1078 (a 415-char action_excerpt is stored)
F-4 sk grows past the bound                REFUSED decision-row-state-not-canonical: 9b26a6e1…
control short excerpt                      APPENDED
C-F7 abs interpreter                       REFUSED decision-state-abs-path: action_target
C-F2 two different msgs: state_digest equal: True | row_id equal: True
C-F2 second append (different msg, different answer, same locator): decision-row-duplicate: 64bea4ce…
```
The refusals come from J1-2's fixed-point check (`src/agent_factory/decisions/ledger.py:274`, `restate = redact(normalize(qid, row["state"], None))`) and the composition at `src/agent_factory/decisions/ledger.py:405` (`s = redact(normalize(question_id, raw_state, root))`); both re-measured at HEAD, as VERIFY-AF-AP-127 cited them. Real-source frequency of F-3 (`freq.py`): `F-3 at limit 200: paragraphs longer than the limit=4729, cut lands after a space=634 (13.4%)`; `at limit 400: … 3109 … 451 (14.5%)`. SOLID.

Feasibility (driver `/tmp/vj11s/feas_driver.py` on a separate copy with HEAD's `ledger.py`; the copy reset and sha-verified after):

| variant | J1-1 suite | C-F1 leak / identity / bound | F-3 | C-F3 token forms | ledger: 450-char excerpt / F-3 row |
|---|---|---|---|---|---|
| F0 control (as landed) | 14 passed | leak True (344 Q) / identity False / 415 | trailing space True | leak True x5 | APPENDED / REFUSED `decision-row-state-not-canonical` |
| F1 bound AFTER redact (+ strip), ledger unchanged | 14 passed | leak False (0 Q) / identity True / 400 | False | leak True x5 | **REFUSED `decision-row-digest-mismatch` / REFUSED `decision-row-digest-mismatch`** |
| F1 + both ledger call sites use the ONE composed function | 14 passed | leak False / True / 400 | False | leak True x5 | APPENDED / APPENDED |
| F2 `_TOKEN` = `(?i)token["']?\s?[:=]?\s?["']?(run)` | 14 passed (the order test still discriminates) | unchanged | unchanged | **leak False x5** | unchanged |
| F3 `.rstrip()` after the cut | 14 passed | unchanged | False | unchanged | APPENDED / APPENDED |

And the hazard for the planned repair (#139): with F1 applied to J1-1 alone, `tests/test_decisions_ledger.py` + `tests/test_decisions_canonical.py` stay green, `('53 passed in 0.32s', [])` (driver `/tmp/vj11s/feas_j12.py`), while the real `make_row` refuses every over-limit row (above). Neither suite has an over-limit field. SOLID.

## 9. Item 9 — v1.finding_class carries part of its own answer

- Contract: v1 options are {SOLID, UNSURE} × {BLOCKING, NON-BLOCKING} (`tasks/briefs/laya/J1-1-brief.md:13`); its state includes `disposition` ∈ {BLOCKING, NON-BLOCKING}. The state therefore carries one of the two answer axes. The pinned decision lists `disposition` in v1's state too (`tasks/laya-j1-breakdown.md:16`, `finding_class`), so the code conforms: `disposition(str,40,upper,enum BLOCKING|NON-BLOCKING)` measured in section 2.
- The lane's own principle contradicts this schema: `test_closed_schema_refuses_incumbent_answer_key` asserts an answer key never enters state (`tests/test_decisions_canonical.py:226`, `Incumbent answers belong to row provenance`), and the code comment says the same (`src/agent_factory/decisions/volatile.py:151`, `Incumbent answers`). The test checks b2's `role` only.
- Sharper, from the committed J0 probe fixture `tests/fixtures/decisions/probe/questions.json`: every v1 question asks `"Does this finding represent a blocking defect that must be fixed before merge?"` with options `["false", "true"]`, and its state carries `"disposition": "blocking"` / `"non-blocking"`. There the state holds the WHOLE answer.
- Grade: FOLLOW-UP (a contract design defect, not a J1-1 code defect; J1 only captures, and J0 measures latency and determinism, not accuracy). It must be settled before J3 infers on v1: drop `disposition` from v1's state, or make v1's options {SOLID, UNSURE} given the disposition. SOLID (measured), impact on J3 UNSURE (not built).

## 10. Item 10 — the tests themselves

| contract test (`tasks/briefs/laya/J1-1-brief.md:24`, the list from `test_golden_digests_exact`) | function | present | what it pins / what it misses |
|---|---|---|---|
| test_golden_digests_exact (7 x2 bitwise) | `test_golden_digests_exact` | yes | canonical + sha256 + fixture bytes; stays green with normalize and redact replaced by the identity (section 6) |
| test_relanding_stable (7 variants) | `test_relanding_stable` | yes | whitespace 7/7, abs path 5/7, pin 1/7, NFD 1/7, line numbers 0/7 (section 2) |
| test_secret_redacted_every_class (5) | `test_secret_redacted_every_class` | yes | one SHORT state per class; no secret near any bound; the envval identity is vacuous for the placeholder text (m10d survives) |
| unknown-key / missing-key / bad-enum / unknown-question (exact strings) | the four refusal tests | yes | exact strings, but ONE type each (b1, b1, v1, —); the other types were measured here (section 2), not by the suite |
| test_abs_path_outside_root_refused | same | yes | the relative `..` refusal and the root-None refusal are untested (m20, m22 survive) |
| test_float_refused | same | yes | also pins the bool refusal (m9 killed) |
| test_normalize_does_not_redact / test_redact_does_not_normalize / test_order_is_normalize_then_redact | same | yes | the order test is coupled to the token rule's narrow separator (m15a killed) |
| (extra) test_closed_schema_refuses_incumbent_answer_key, test_command_target_uses_leading_token_and_pin_strip_is_exact | — | extra | see item 9; the leading-token test uses only a bare `python3` |

No contract test is missing (12 named + 2 extra = 14 collected). No test places a secret near a bound; no test exercises truncation at all (m11 and m18 survive, section 7). A constant-digest mutant (`state_digest` returns 64 zeros; py_compile rc 0; collected 14) is killed only by `test_golden_digests_exact` and `test_relanding_stable` (`2 failed, 12 passed`): the digest-identity assertions in the secret test and the order test are vacuous against a constant, but both tests also assert over the direct `canonical(redact(normalize(…)))` composition, so neither is a pure mirror. SOLID.

Evidence audit of the builder report (`tasks/briefs/laya/J1-1-report.md`): the seven golden digests match (Oracle A); m1, m2, m4, m5, m6 rows reproduce; the m3 row reproduces only as m3c (UNSURE which NFC the builder dropped; as written it overstates the coverage); the lint line reproduces with the five maps; the `no_laya_in_gates` line now reads `no_laya_in_gates: 40 files scanned, clean` `no-laya-rc=0` (33 at the builder's run; the gate list grew since); its RED→GREEN history is a past state, NOT re-run (UNVERIFIED).

## 11. Predicate table (D-031: contract-mapped · canonical reproduction · material effect · discriminator · in boundary)

| id | finding | reproduced (own run) | contract mapping | material effect (measured) | discriminator | in boundary | disposition |
|---|---|---|---|---|---|---|---|
| C-F1 | the bound runs BEFORE redaction (`src/agent_factory/decisions/volatile.py:143`, `s = s[: f.limit]`) | yes: sweep over 16 bounded keys x 5 classes; coordinator's 2 inputs exact | items 2 (cut inside normalize) + 3 (redact after normalize) vs item 6 + verdict AT1 (`docs/research/COUNCIL-VERDICT-JEV-LAYA-v1.md:96`, `never appear in the ledger`) + item 1 (≤ 400): jointly UNSATISFIABLE for over-limit fields (proof below). Also names AF-AP-127 (`docs/INCIDENT-LOG.md:483`, `AF-AP-127`), registered after the dispatch, explicitly for this component | secret bytes written to the ledger (sk 7 chars, bearer 15, token 31, PEM 344 key chars); a 415-char excerpt stored (bound broken); an sk ending at the limit refused by the ledger | `action_excerpt = "a"*390 + " sk-ABCDEFGHIJKLMNOPQRST"` → `sk-ABCDEF` in the ledger bytes | code yes; the repair needs a contract amendment and a J1-2 call-site co-change | **CONTRACT-INVALID** (in the other reading: CONTRACT-DEFECT; both route to an amendment) |
| C-F3a | token-run forms missed: `token = <run>`, `access_token=<run>`, `"token": "<run>"`, `PC_BRIDGE_TOKEN: <run>`, `AGENT_TOKEN: <run>` | yes (section 4 and section 8) | item 3's own class text: "a 32+ hex/base64 run after `token` → token" (`tasks/briefs/laya/J1-1-brief.md:18`, `PC_BRIDGE_TOKEN`); every input has a 32-hex run after `token`; "replace every match"; item 6 no-bytes | FAKE 32-hex run written to the ledger bytes for all five forms (control `token: <32>` redacted) | msg `token = 0123456789abcdef0123456789abcdef` | yes: `src/agent_factory/decisions/volatile.py:48` (`_TOKEN`); F2 shows a regex that fixes all five and keeps the order discriminator (14 passed) | **BLOCKER** |
| C-F2 | `sk-` matches inside words | yes | the code implements the contract's own regex exactly (`tasks/briefs/laya/J1-1-brief.md:18`, `sk-[A-Za-z0-9_-]{8,}`): no code defect | distinct states collapse (same digest True); the ledger refuses a different decision as `decision-row-duplicate` when the locator matches; 2 of 14 `sk-` hits in 174 real sources are words | `task-implementer failed` → `ta<redacted:sk> failed` | contract amendment | FOLLOW-UP (amend the regex: a left boundary, as the scrubber's `\bsk-` at `scripts/transcript_export.py:36`) |
| C-F3b | lowercase / spaced / colon env forms: `password=`, `PASSWORD = `, `password: `, `SECRET_KEY: `, `?api_key=` | yes | outside the literal text (`KEY=…`/`TOKEN=…`/`SECRET=…`/`PASSWORD=…`, uppercase, no spaces) | secret bytes in the ledger (`password=<fake>` APPENDED, True) | msg `password=FAKE…` | contract amendment | FOLLOW-UP (match the scrubber's case-insensitive `\s*[:=]\s*` form, `scripts/transcript_export.py:33`) |
| C-F4 | relative path shapes not normalized; `a/../b` refused while `<root>/a/../b` accepted; `x/..` accepted | yes | item 2 names only absolute-path relativization; item 5's variants name only "an absolute path under the root" | two spellings, two digests (no ledger harm beyond identity) | `./src/x.py` vs `src/x.py` | yes | FOLLOW-UP |
| C-F5 | value types not closed | yes | item 2 governs strings; item 4's type rule holds on the stringified state; not a violation of frozen text | None/5/True collide with `'None'`/`'5'`/`'True'`; both APPENDED | msg `None` vs `'None'` | yes | FOLLOW-UP (refuse non-str scalars with `decision-state-bad-type: <key>`) |
| C-F6 | bool and None refused under `decision-canonical-float` | yes | the contract names that reason for a float; refusing is correct | none through `state_digest`; a misleading reason via direct `canonical()` | `canonical({"k": True})` | yes | INFO (use `decision-canonical-type`, `src/agent_factory/decisions/canonical.py:67`) |
| C-F7 | an absolute interpreter as a command's leading token is refused | yes (also through `make_row`) | the code follows items 1 + 2 literally | commands like `/usr/bin/python3 …` cannot become rows (fail-closed, named); frequency in real transcripts NOT measured here | `/usr/bin/python3 -m pytest` | contract (J1-3 design) | FOLLOW-UP (contract: e.g. basename an absolute command binary) |
| F-2 | locator-shaped VALUES pass into state | yes | the brief reads AC 3 as keys; AC 3's own text says "strip"; UNSURE | re-landed free text with a new line number or timestamp hashes differently | `line 42` vs `line 57` in `snippet` | J1-3 extraction or contract | FOLLOW-UP |
| F-3 | normalize is not idempotent: a cut after a space leaves a trailing space | yes | contested: item 2 lists "strip" before "truncate" and the code follows that literal order | the ledger refuses the row (`decision-row-state-not-canonical`); 13.4% (limit 200) / 14.5% (limit 400) of over-limit paragraphs in 174 real sources | `"a"*399 + " b"` | yes (F3: one `.rstrip()`, 14 passed) | FOLLOW-UP (material; fold into the C-F1 amendment: strip after the bound) |
| F-5 | the newline refusal copies 32 characters of the value into the exception text | yes | none in J1-1's text | reachable only via direct `canonical()` on un-redacted fields (J1-2) | a FAKE `sk-…` + `\n` | yes | FOLLOW-UP |
| F-6 | 9 non-equivalent surviving mutants (m3, m10d, m11, m12, m14, m17, m18, m20, m22) | yes | the properties are in items 2-4; the Tests list does not require them | no test sees the bound, NFC-before-cut, non-space whitespace, the sk minimum, `..`, root None, canonical's NFC, the envval placeholder | section 7 | yes | FOLLOW-UP (tests) |
| F-8 | v1's state carries its own answer axis (item 9) | yes | the pinned decision includes it; the code conforms | none in J1 (capture only); a label leak for J3 | the J0 probe fixture | contract | FOLLOW-UP (contract) |
| F-9 | a bound-after-redact repair in J1-1 alone passes both suites (`53 passed`) while `make_row` refuses every over-limit row | yes (F1 row, `feas_j12.py`) | repair hazard, not a J1-1 defect | the planned repair could land green and break the ledger | a 450-char excerpt through `make_row` | J1-1 repair + J1-2 co-change | FOLLOW-UP (bind into the amendment) |

Proof that C-F1's frozen text is unsatisfiable (my own argument; it does not need the "neither relies on the other" rule). Take a field with limit L, a prefix P, a secret S matched by a class with placeholder PH where len(S) > len(PH), and a tail R with len(P)+len(PH)+len(R) > L. Item 2 makes normalize truncate at L, so the secret-bearing state keeps at most L−len(P)−len(S) tail characters; redact runs after (item 3) and can only replace S by PH, never restore dropped tail. The clean state keeps L−len(P)−len(PH) tail characters. The two outputs differ, so item 6's identity fails for every such state (measured: `sk … secret-form 374 vs clean-form 400`, False for all five classes). The leak half (a straddling prefix below the class minimum) is avoidable only by making normalize secret-aware or by adding remnant patterns to redact; both break other frozen text (the separation rule, or the ≤ 400 bound once the placeholder grows). Under the other reading (item 6 and AT1 only specify one short test state per class) J1-1 meets its text, and C-F1 becomes a CONTRACT-DEFECT: an exact-production-path defect that puts secret bytes in the ledger (section 8). Either reading routes to an explicit amendment, not a plain repair.

The smallest amendment that makes items 2, 3 and 6 hold together (checked by F1 in section 8):
1. Item 2: remove "truncate the bounded excerpts at their limit on a character boundary" from normalize.
2. Item 4: `state = bound(redact(normalize(state)))`, where `bound` truncates each bounded field at its limit on a character boundary and then strips trailing whitespace (this also closes F-3); `state_digest = sha256(canonical(state))`.
3. J1-1 exports that composition as ONE public function, and every consumer calls it. J1-2 composes the pipeline itself at `src/agent_factory/decisions/ledger.py:274` and `src/agent_factory/decisions/ledger.py:405` (`redact(normalize(`); both call sites must switch in the same repair, or every over-limit row is refused with `decision-row-digest-mismatch` while both suites stay green (F-9).
4. Tests: one straddle case per class at a bounded key, one over-limit identity case, one over-limit ledger append.

## 12. Finding inventory (no severity filter)

| # | id | class | evidence | contract mapping | canonical path | material effect | reproduction | suggested fix |
|---|---|---|---|---|---|---|---|---|
| 1 | C-F1 | CONTRACT-INVALID | SOLID | items 2+3 vs 6, AT1, item 1; AF-AP-127 | `state_digest`, `make_row`, `append` | secret bytes in the ledger; bound broken; rows refused | `item4b.py`, `item8_ledger.py` | the amendment above |
| 2 | C-F3a | BLOCKER | SOLID | item 3 token class, item 6 | same | secret bytes in the ledger | `item4a.py`, `item8_ledger.py` | F2's `_TOKEN` (or the scrubber's form), keeping the order test |
| 3 | C-F2 | FOLLOW-UP | SOLID | contract regex itself | same | digest collapse; a duplicate refusal | `item4a.py`, `item8_ledger.py` | left boundary on `sk-` (contract) |
| 4 | C-F3b | FOLLOW-UP | SOLID | outside literal text | same | secret bytes in the ledger | `item4a.py`, `item8_ledger.py` | case-insensitive, spaced, colon env forms (contract) |
| 5 | C-F4 | FOLLOW-UP | SOLID | none | `state_digest` | identity only | `item3.py` | `posixpath.normpath` on relative paths, refuse an escape |
| 6 | C-F5 | FOLLOW-UP | SOLID | none | `state_digest`, `make_row` | type collisions | `item3.py`, `item8_ledger.py` | refuse non-str scalars |
| 7 | C-F6 | INFO | SOLID | reason naming | `canonical()` direct | none via state | `item5.py` | `decision-canonical-type` |
| 8 | C-F7 | FOLLOW-UP | SOLID (frequency NOT measured) | code follows the text | `make_row` | commands with absolute interpreters unrecordable | `item3.py`, `item8_ledger.py` | contract rule for absolute command binaries (J1-3) |
| 9 | F-2 | FOLLOW-UP | SOLID; mapping UNSURE | AC 3 text vs brief | `state_digest` | re-landing instability for free-text locators | `item2b.py` | harvest extraction or contract text |
| 10 | F-3 | FOLLOW-UP (material) | SOLID | contested | `make_row` | ~14% of long real excerpts refused | `item3.py`, `item8_ledger.py`, `freq.py` | strip after the cut (in the amendment) |
| 11 | F-4 | part of C-F1 | SOLID | item 1 ≤ 400 | `make_row` | 415-char field stored; sk-at-limit refused | `item4b.py`, `item8_ledger.py` | the amendment |
| 12 | F-5 | FOLLOW-UP (adjacent) | SOLID | none | direct `canonical()` | up to 32 secret chars in an exception text | `item5.py` | no value bytes in refusal texts |
| 13 | F-6 | FOLLOW-UP | SOLID | items 2-4 properties | tests | 9 untested properties | `mutants.py`, `equiv.py` | one test per survivor |
| 14 | F-7 | INFO | SOLID | item 1 (leading token for a command only) | `normalize` | a path with a space cut to its first token; 0 such tracked paths | `item3.py` | split only when `action_kind == command` |
| 15 | F-8 | FOLLOW-UP | SOLID | pinned decision includes it | — | label leak for J3 | the J0 probe fixture | contract |
| 16 | F-9 | FOLLOW-UP | SOLID | repair hazard | both suites | a green-but-broken repair possible | `feas_j12.py` | bind into the amendment |
| 17 | F-10 | INFO | SOLID | "BOUNDED" names no limit for these | `normalize` | `action_target`, path keys, `paths` count unbounded (a 5,000-char token kept) | `item3.py` | limits for them |
| 18 | F-11 | INFO | SOLID | privkey needs END | `redact` | a PEM with no END in the input leaks | `item4a.py` | BEGIN … (END or end of value), as the scrubber at `scripts/transcript_export.py:29` |
| 19 | F-12 | INFO | SOLID | not contract classes | `redact` | base64url runs with `-`, GitHub PATs, Basic auth leak | `item4a.py` | optional classes |
| 20 | F-13 | INFO | SOLID | none | `normalize` | `FOO=bar` or `sudo` taken as the command; empty target/path; `--330803c` → `''` | `item3.py` | J1-3 extraction rules |
| 21 | F-14 | INFO | SOLID | none (unreachable via state) | `canonical()` direct | duplicate keys, raw-key order, U+2028 raw; lone surrogate and 10**5000 raise unnamed errors through `state_digest` | `item5.py` | named refusals |
| 22 | F-15 | INFO | SOLID | NFC only | `normalize` | zero-width characters kept | `item3.py` | none needed |
| 23 | O-1..O-4 | INFO | SOLID | — | — | report checkability; AC 1's bare `python3`; precedence; raw enum value | sections 1-2 | — |
| 24 | F-16 | INFO | SOLID/UNSURE | builder report | — | the builder's m3 row overstates | `mutants.py` | name the mutated line |
| 25 | A-1..A-7 | adjacent J1-2 (never J1-1 blockers) | SOLID | J1-2 | `make_row`, `append` | A-1 F-3 refusals; A-2 sk-at-limit refusal; A-3 415-char field stored; A-4 duplicate refusal from C-F2; A-5 C-F7 passes through; A-6 un-redacted fields reach `canonical()`; A-7 the pipeline composed at two call sites | `item8_ledger.py`, `feas_driver.py` | for the J1-2 verify lane |

Reproduced vs static vs skipped:
- Reproduced here: every item-1 gate; all schema refusals on all types; every shape in the tables; the C-F1 sweep; the ledger append path; the golden oracles; 31 mutants + 10 equivalence probes + the constant-digest mutant; 5 feasibility variants; real-source frequencies.
- Static only: the contract readings (item 6 universal vs existential) and the impossibility argument (a proof, backed by the measured `374 vs 400`).
- Skipped, with reasons: C-F7's frequency in real transcripts (it needs parsing the committed transcripts; not required to grade it); the full-tree suite (the budget is targeted; the adjacent `tests/test_decisions_ledger.py` ran: `53 passed`); any PC, bridge or network step (the brief forbids them); grading J1-2's own defects (out of boundary).

## GATE RECOMMENDATION

**CONTRACT-INVALID** — C-F1: the frozen J1-1 text (items 2 and 3 put the bound inside normalize, before redact) cannot satisfy item 6 and the verdict's acceptance test 1 for any over-limit field (proof and measurements in sections 4, 8 and 11). Stop and amend the contract as named in section 11 (bound after redact, then strip; ONE composed state function used by `state_digest` and by both ledger call sites; straddle and over-limit tests), then run ONE focused repair (task #139) against the amended revision. Fold into that same repair the in-contract BLOCKER C-F3a (the token-run forms; F2 shows a feasible rule that keeps the order test) and the material FOLLOW-UP F-3 (closed by the amendment's strip). This recommendation rests on reproduced measurements only; its one judgment call is reading item 6 and AT1 as universal. The other reading makes C-F1 a CONTRACT-DEFECT, which also requires an amendment. The coordinator owns the gate.


Lint (`python3 scripts/report_lint.py --min-refs 15 tasks/briefs/laya/VERIFY-J1-1-report.md --root .`, no `--map`, round 3 of 3): `report_lint: 39 refs — OK 39, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)`
