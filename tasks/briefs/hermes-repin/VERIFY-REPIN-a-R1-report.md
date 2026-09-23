# VERIFY-REPIN-a-R1 — report (task #173)

Lane: VERIFY-REPIN-a-R1, sandbox adversarial-verifier (claude-opus-5-5, D-054). Brief:
`tasks/briefs/hermes-repin/VERIFY-REPIN-a-R1-brief.md` (origin 415040b). PIN: **879ee98** (origin; the post-push SHA of the
local landing commit 2f46cc6). Started 2026-09-23 10:21:52Z (`date -u`). Status: COMPLETE.
**GATE RECOMMENDATION: `CONTRACT-INVALID`, scoped to R3(c) (CONTRACT-DEFECT F1+F2 returned); R1, R2, R4, R5, R3(a)(b): no blocker,
MERGE-READY-WITH-FOLLOWUPS on their own.** Details at the end.

Map: T = `tests/test_upstream_lock_lane_runtime.py` · L = `upstream.lock.yaml` · H = `docs/HARNESS-PORTS.md` ·
P = `harness-ports/bin/pc-lane.sh` · V = `scripts/vendored_manifest.py`.

## Item 1 — PREMISE (re-measured on the PIN)

**Verdict: the premise holds on 879ee98. No item is CONTRACT-INVALID by a premise mismatch.** SOLID.

- The PIN is on origin. 2f46cc6 and 879ee98 have the SAME tree (`e1147a601ef5829130a69eb79ff36014b625b119`) and the same parent
  (3846636); push_clean rewrote only the trailer. HEAD (de33838) and the working tree carry the same blobs for every component file.
- The three component blobs are byte-identical on 2f46cc6, 879ee98, HEAD and the working tree: T `0e64aba8ea20` (253 lines),
  L `65b0f05ef43a` (173), H `ee9ff9b5efd6` (745). The record `5725e15a885d` (148) and the builder report `6fd845c863b1` (454) match too.
  `git diff --stat 879ee98 HEAD` over T, L, H, P, V and `tasks/briefs/hermes-repin/` shows only the new brief file.
- T collects 16 tests and passes twice with identical counts (below). Set id `bbc177a039e2`.
- L:10-15 (`hermes-agent:` … `role: main_production_workhorse_and_native_acp_server`) show no trailing whitespace under `cat -A`.
- L:173 is the `verified:` value, byte-equal to the brief's premise. H:728 is `## 12. Lane runtime pin`; H:737-738 `lane_runtime` carry the R5 sentence.
- The literal grep for `lane_runtime` finds no reader outside T (see item 5 for a WIDER grep and the generic reader).
- P:217-218 truncate `prompt.md` (`: > "$PROMPT_FILE"`) — but only on a start that passes the state guard at P:102-109 `$REPORT` (see item 6b).
- The record has 111 date-led lines: 110 table rows plus the Rule's second line (record line 9). Column 2: 98 `report`, 12 `-`.
  Column 3: 4 `FAILED`, 106 `-`.

```
$ git log --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf -8   (the PIN is the 5th line)
de33838 transcripts: scrubbed sandbox chat digests (2026-09-23)
56a8f50 B9-R1 landed (task #168): …
59d8f00 Wiki live-state 10:0xZ: REPIN-a-R1 landed (GATED-PENDING-VERIFY), …
415040b Brief VERIFY-REPIN-a-R1 (task #173): …
879ee98 REPIN-a-R1 landed (task #169): the lane-runtime pin's golden is its six lines, …
$ echo "tree 2f46cc6: $(git rev-parse 2f46cc6^{tree})"; echo "tree 879ee98: $(git rev-parse 879ee98^{tree})"
tree 2f46cc6: e1147a601ef5829130a69eb79ff36014b625b119
tree 879ee98: e1147a601ef5829130a69eb79ff36014b625b119
$ for f in T L H record report ledger; do 2f46cc6 | 879ee98 | HEAD | worktree blob; done
2f46cc6 0e64aba8ea20 | 879ee98 0e64aba8ea20 | HEAD 0e64aba8ea20 | wt 0e64aba8ea20 253 tests/test_upstream_lock_lane_runtime.py
2f46cc6 65b0f05ef43a | 879ee98 65b0f05ef43a | HEAD 65b0f05ef43a | wt 65b0f05ef43a 173 upstream.lock.yaml
2f46cc6 ee9ff9b5efd6 | 879ee98 ee9ff9b5efd6 | HEAD ee9ff9b5efd6 | wt ee9ff9b5efd6 745 docs/HARNESS-PORTS.md
2f46cc6 5725e15a885d | 879ee98 5725e15a885d | HEAD 5725e15a885d | wt 5725e15a885d 148 tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md
2f46cc6 6fd845c863b1 | 879ee98 6fd845c863b1 | HEAD 6fd845c863b1 | wt 6fd845c863b1 454 tasks/briefs/hermes-repin/REPIN-a-R1-report.md
2f46cc6 eda847f24118 | 879ee98 eda847f24118 | HEAD 9ed814a5f164 | wt 9ed814a5f164 1332 todo/BUILD-TASKLIST.md
$ date -u; for i in 1 2; do rm -rf /tmp/vrr1/bt; bash scripts/test_summary.sh tests/test_upstream_lock_lane_runtime.py --basetemp /tmp/vrr1/bt | tail -1; done
Wed Sep 23 10:22:44 UTC 2026
pytest-summary: 16 passed in 0.18s
pytest-summary: 16 passed in 0.18s
$ bash scripts/pc_suite.sh set-id -- tests/test_upstream_lock_lane_runtime.py
1 files set=bbc177a039e2
$ R=tasks/briefs/hermes-repin/REPIN-a-R1-lane-record.md; grep -cE '^2026-09-[0-9]{2}T' $R; … awk '{print $2}' | sort | uniq -c; … '{print $3}'
111
     12 -
     98 report
      1 the
    106 -
      4 FAILED
      1 owner's
```

## How the attacks ran (all scratch, all through the real code)

`/tmp/vrr1/h.py` copies the REAL T, a mutated copy of L (or H, or T) and `pyproject.toml` into `/tmp/vrr1/w/<case>/` and runs
`python3 -m pytest tests/test_upstream_lock_lane_runtime.py -q -rfE` there (the interpreter `scripts/test_summary.sh` uses:
`/usr/local/bin/python3`, Python 3.11.15, PyYAML 6.0.1 pure-Python, no libyaml). Each case also records `py_compile` and the collect
count. `/tmp/vrr1/cons.py` puts the same lock copy through the lock's two other REAL consumers: V's `parse_lock` and
`validate_pin_agreement` (V:592-622 `parse_lock`, V:652-677, imported read-only from the repo path) and `proofs/S0-12/check_pin_diff.py`
(a subprocess on a scratch root with the real `SBOM.yaml`). The UNMUTATED control ran first: T `16 passed`; V `parse_lock` 24 entries,
hermes `('527da608…', 'selected_core.hermes-agent')`, `validate_pin_agreement` OK; S0-12 `rc=0 PASS`. Every case dir and basetemp
was removed after its run.

## Item 2 — R1, the line golden: new shapes (never the builder's G1-G7)

**Verdict: R1 holds for every shape that changes the six lines. The parsed view carries its own weight: it alone catches S5. One shape
survives everything (S5e, FOLLOW-UP F4), and the V reader mis-parses a quoted key (FOLLOW-UP F5).** SOLID (every row reproduced).

The extractor T:93-113 `_hermes_agent_entry` ends the entry at T:112 `re.match(r"  \S|[^\s#]", lines[j])`: a line with exactly two
spaces and a non-space, or a top-level key. A blank line, a 4-space line and a column-0 `#` line do NOT end it.

| # | shape (on a scratch copy of L) | T:200 `test_hermes_agent_entry_lines_golden` (byte view) | T:185 `test_hermes_agent_entry_unchanged` (parsed view) | verdict |
|---|---|---|---|---|
| S1 | `  # comment` INSIDE the entry (after `commit:`) | RED: `differs from its golden at entry line 4 (upstream.lock.yaml line 13): expected '    observed_version: 0.21.0', got '<no line>'` | green | killed by the byte view (message nit: F9) |
| S2 | `  # comment` right AFTER the entry (before `  buzz:`) | green | green | EQUIVALENT: the comment ends the entry (T:112 `re.match` `  \S`); the six lines are unchanged |
| S2b | `    # comment` (4 spaces) right after | RED: entry line 7 (L line 16), `expected '<no line>', got '    # comment'` | green | killed (conservative: swallowed into the entry) |
| S2c | `# comment` (column 0) right after | RED: entry line 7, `got '# comment'` | green | killed (conservative) |
| S3 | blank line INSIDE the entry | RED: entry line 4 (L line 13), `got ''` | green | killed by the byte view |
| S3b | blank line right AFTER the entry | RED: entry line 7, `got ''` | green | killed (conservative false red, F10) |
| S4 | `   commit:` (three spaces) | RED: entry line 3 (L line 12), `got '   commit: 527da6…'` | RED: `yaml.parser.ParserError` | killed; 15 of 16 red (every loader test raises ParserError) |
| S4b | `   role:` (three spaces, the last child) | RED: entry line 6 (L line 15) | RED: ParserError | killed; 15 red |
| S5 | `  "hermes-agent":` as a SECOND key LATER in `selected_core:` (after `gvisor`), another commit | **green (blind: T:101 matches the exact unquoted line only)** | RED: `hermes-agent entry differs from golden: {… 'commit': '0123456789abcdef…'}` | killed by the PARSED view ONLY |
| S5q | the same with single quotes `  'hermes-agent':` | green | RED (same message) | killed by the parsed view only |
| S5s | S5 with the SAME six values | green | green | EQUIVALENT for T and S0-12 (PyYAML keeps the last duplicate, which is equal); NOT equivalent for V (F5) |
| S5e | the quoted key placed EARLIER (right after `selected_core:`), another commit | green | green | **SURVIVES: all 16 green, V OK, S0-12 PASS** (F4) |
| S5es | S5e with the SAME values | green | green | EQUIVALENT |
| S5u | an UNQUOTED second `  hermes-agent:` later, same values | RED: `has 2 lines equal to '  hermes-agent:' (at [10, 44])` | green | killed by the byte view |
| S6 | UTF-8 BOM at the file start | green | green | EQUIVALENT: outside the entry; PyYAML skips a leading U+FEFF |
| S7 | CRLF file | RED: `has 0 lines equal to '  hermes-agent:' (at []); lines that differ from it only in whitespace: [10]` | green | killed by the byte view only (`read_bytes` keeps `\r`, T:203) |
| S7b | one `\r` inside the entry (`license: MIT\r`) | RED: entry line 5 (L line 14), `got '    license: MIT\r'` | green | killed |
| S8 | the entry moved under `selected_later_planes:` | RED: `'  hermes-agent:' (line 40) is not under 'selected_core:' but under 'selected_later_planes:'` | RED: `hermes-agent entry missing from selected_core` | killed by both views |
| S8b | the entry moved to the END of `selected_core:` (still inside it) | RED: entry line 7 (L line 44), `got ''` | green | conservative false red (F10) |

S5q ran with the lane commit as its injected value, so its five control params also went red (`occurs 2 times`). That is a
collision of my fixture, not a finding: S5 and S5e were re-run with `0123456789abcdef…`, and the rows above are those runs.

Consumers on the duplicate shapes (cons.py; the same copies):

```
S5  : V.parse_lock hermes ('0123456789abcdef…', 'selected_core.gvisor') · gvisor None · 23 entries
      V.validate_pin_agreement ManifestError: pin disagreement for github.com/nousresearch/hermes-agent: upstream.lock.yaml selected_core.gvisor=0123…, SBOM.yaml hermes-agent=527da608…
      S0-12 rc=1 sbom-pin-drift: pin differs from upstream.lock.yaml for hermes-agent
S5s : V.parse_lock hermes ('527da608…', 'selected_core.gvisor') · gvisor None · 23 entries · validate_pin_agreement OK · S0-12 rc=0 PASS
S5e : V hermes ('527da608…', 'selected_core.hermes-agent') · gvisor present · 24 entries · OK · S0-12 rc=0 PASS · T 16 passed
```

Answers to the item's questions:
- **Which view catches the quoted later duplicate?** Only the parsed view (T:195 `assert entry == HERMES_AGENT_GOLDEN`). The byte view
  cannot: T:101 `line == "  hermes-agent:"` counts the exact unquoted line, and T:105's whitespace hint uses `line.strip()`, which
  keeps the quotes.
- **Is a same-valued duplicate an equivalent mutant?** For T (both views) and for S0-12: yes, the parsed data is identical. For V: no.
  V:605 `re.fullmatch(r"  ([a-z0-9][a-z0-9-]*):", line)` does not match a quoted header, so the header is skipped and its children
  are written into the PREVIOUS component (V:612 `entries[component][match.group(1)]`). In S5s, `gvisor` takes the hermes repository
  and leaves V's map (24 -> 23 entries) with no error: V's pin agreement silently stops checking gvisor. See F5.
- **Does the parsed-dict view still hold its own weight?** Yes. S5 and S5q are red ONLY through it. It is load-bearing, not a leftover.
- **Survivor:** S5e. A quoted `"hermes-agent":` with ANOTHER commit, placed before the original, passes T, V and S0-12. PyYAML keeps
  the last duplicate (the original). V skips the quoted header and, with no current component after `selected_core:`, drops its
  children (V:611 `if match and component`). A human reading the lock top-down, or any first-match reader, sees the other commit first.
  In contract? R1's letter is "Exactly one line equals `  hermes-agent:`", the unquoted spelling, and it holds. So this is OUT of
  R1's letter: FOLLOW-UP F4, not a blocker.

## Item 3 — R2, the live control: new shapes through the SAME loader

**Verdict: every rejection is by the named message. No value that is not a real 40-lowercase-hex string passes the helper.** SOLID.

Method: `/tmp/vrr1/item3.py` imports a scratch copy of T and follows the control's steps (T:241-253 `committed_line`): it replaces the committed line,
loads the copy through T:81 `_load_lock`, then calls T:85 `_check_lane_runtime_commit`, and compares the text with
`commit is not 40 lowercase hex: {loaded!r}`.

```
empty value (commit:)                                    loaded=NoneType REJECTED, named=True: commit is not 40 lowercase hex: None
null                                                     loaded=NoneType REJECTED, named=True: … None
tilde ~                                                  loaded=NoneType REJECTED, named=True: … None
quoted 40-hex + trailing space inside the quotes         loaded=str    REJECTED, named=True: … 'b3399c13…f60fbe1f4 '
quoted 40-hex + leading space inside the quotes          loaded=str    REJECTED, named=True: … ' b3399c13…f60fbe1f4'
octal-looking all-digit: "0"+39 octal digits             loaded=int    REJECTED, named=True: … 27127022726593908273617839343497884
0-led 40 digits containing 8/9 (stays a str)             loaded=str    PASSES the helper -> '0123456789123456789123456789123456789123' (len 40)
40 digits with underscores (YAML 1.1 int)                loaded=int    REJECTED, named=True: … 122222222222222222222222222222222222222
YAML list [a, b]                                         loaded=list   REJECTED, named=True: … ['a', 'b']
YAML block list (- x)                                    loaded=list   REJECTED, named=True: … ['b3399c13…f60fbe1f4']
YAML float 40 chars with a dot                           loaded=float  REJECTED, named=True: … 1.2345678901234568e+36
YAML float .nan                                          loaded=float  REJECTED, named=True: … nan
YAML bool true                                           loaded=bool   REJECTED, named=True: … True
YAML mapping {a: 1}                                      loaded=dict   REJECTED, named=True: … {'a': 1}
!!str tag on a 40-digit value                            loaded=str    PASSES the helper -> '1234567890123456789012345678901234567890' (len 40)
literal block scalar | (40 hex + newline)                loaded=str    REJECTED, named=True: … 'b3399c13…f60fbe1f4\n'
folded block scalar >- (40 hex, stripped)                loaded=str    PASSES the helper -> 'b3399c139624a0081d70397741a5b45f60fbe1f4' (len 40)
40 hex + trailing comment                                loaded=str    PASSES the helper -> 'b3399c139624a0081d70397741a5b45f60fbe1f4' (len 40)
hex int 0x + 38 hex                                      loaded=int    REJECTED, named=True: … 3996851900919250837250879783839056245626567649
commit key removed                                       KeyError('commit')   (not the named message; the positive test still goes red)
```

- Every rejection carries the exact named text. Every value that passes is a Python `str` of 40 characters from `[0-9a-f]`, so it
  IS a 40-lowercase-hex string: T:88 `re.fullmatch(r"[0-9a-f]{40}", commit)` uses a literal class (no `\d`, so no Unicode digits)
  and `fullmatch` refuses a trailing newline. The only non-`str` 40-hex spellings PyYAML produces are all-digit (int) and
  `0`+octal (octal int); T:88 `re.fullmatch`'s `isinstance(commit, str)` refuses both.
- INFO F11: an int is named by its DECIMAL repr, not by the text in the lock (the octal row prints `27127022726593908273617839343497884`
  for `0123456712345671234567…`). A removed `commit:` key raises `KeyError`, not the named message (outside R2's five shapes).

## Item 4 — the lane_runtime entry itself: duplicate keys and key order

**Verdict: a duplicate key inside `hermes-agent-lane-runtime` is refused by NOTHING when the pinned value comes last. It is OUT of
R1-R5's letter: FOLLOW-UP F6, a hazard for REPIN-b. A key reorder is pinned by nothing and is in-contract (R4 names values).** SOLID.

```
D1  two commit: lines, the FIRST another valid 40-hex, the second the pin : T 16 passed · V OK · S0-12 PASS · first-match reader -> 0123456789abcdef0123456789abcdef01234567
D1c two commit: lines, the FIRST the 7-hex b3399c1, the second the pin     : T 16 passed · V OK · S0-12 PASS · first-match reader -> b3399c1
D1b the pin FIRST, another 40-hex second                                   : T 7 failed (commit value, entry values, the five control params: the loaded value is the second)
D2  two verified: lines, the first a false claim, the second the pinned    : T 16 passed · V OK · S0-12 PASS
D3  the eight keys in REVERSED order                                       : T 16 passed · V OK · S0-12 PASS
unmutated L, first-match reader                                            : b3399c139624a0081d70397741a5b45f60fbe1f4
```

(The first-match reader is `awk '/^  hermes-agent-lane-runtime:/{f=1;next} f && /^    commit:/{print $2; exit}'`, the shape of the
bash drift check `REPIN-brief.md` §REPIN-b plans: "read the pinned commit from upstream.lock.yaml".)

- Why D1 and D1c pass: PyYAML keeps the LAST duplicate (the pin), so T:87 `hermes-agent-lane-runtime` reads the pin; the control's T:243 `committed_line`
  `text.count(committed_line) == 1` still holds, because the pinned line occurs once. D1c means a lock that CARRIES a 7-hex lane
  commit passes the whole R2 suite.
- In contract? R2 names five single-value replacements; R4 pins the eight PARSED values. No R-line names a duplicate key inside the
  lane-runtime entry (R1's duplicate `commit:` shape is on the hermes-agent entry). Out of letter: FOLLOW-UP F6. Its weight comes
  from REPIN-b. The first reader that will ACT on this entry is a line reader, and it reads the other value while every gate is green.
- D3 (reorder): R4 says "the whole expected dict … (all eight keys' exact values)", which names values, not order. In contract, and
  EQUIVALENT under R4.

## Item 5 — consumers, on two instruments (graft + grep)

**Verdict: §12's operative claim is TRUE at the PIN. No code acts on `lane_runtime`, and no dispatcher line reads the Hermes identity.
The literal words "nothing reads" are loose: V parses every line of the entry. The sentence is also incomplete (F8).** SOLID.

Instrument 1, graft (`graft ask "who reads lane_runtime hermes-agent-lane-runtime from upstream.lock.yaml"` and `graft ask "which
code parses every section of upstream.lock.yaml" --source`): no `lane_runtime` reader. Three whole-lock readers:
V:592-622 `parse_lock`, `proofs/S0-12/check_pin_diff.py:16-73` `main`, `proofs/S0-06/check_four_scope.py:205-227` `_lock`.
Instrument 2, grep (`git grep -n -I -e lane_runtime -e lane-runtime -- ':!tasks' ':!docs' ':!wiki' ':!todo' ':!transcripts' ':!*.md'`,
which covers the extension-less scripts `scripts/proof-runner`, `scripts/validate-ledger` and `scripts/ledger-gen` too): only T.
`grep -n -E 'hermes --version|rev-parse HEAD|lane_runtime|HERMES_BIN' scripts/pc_lane.sh P harness-ports/bin/pc-setup.sh
harness-ports/bin/lane-profile.sh` finds P:71 `HERMES_BIN:=hermes`, P:446 `"$HERMES_BIN" -p`, P:168 `rev-parse HEAD` (the lane
TREE's pin check, not Hermes) and `lane-profile.sh:12,81,199`: no Hermes identity check anywhere. No minted proof attests the real L
(only `proofs/S0-12/fixtures/mutated-root/upstream.lock.yaml` is hashed).

- **Does the lane-runtime entry reach `parse_lock`'s returned map?** No. V parses it: V:607-608 `match.group` name the component
  `hermes-agent-lane-runtime`, and V:610-612 store its `commit`. V:620 `if repository and pin` then drops it, because it has no
  `repository:`. The other seven keys are ignored (V:613 `elif line.startswith("    ") and ":" not in line` does not fire). Control
  run: V 24 entries, no lane entry.
- **One added `repository:` line in it** (scratch copies, the real V):

```
R5a + repository: https://github.com/NousResearch/hermes-agent.git   : T 2 failed (T:127 `test_lane_runtime_has_exact_keys` exact keys: extra={'repository'}; T:166 `test_lane_runtime_entry_values` entry values)
     V.parse_lock hermes ('b3399c139624a0081d70397741a5b45f60fbe1f4', 'lane_runtime.hermes-agent-lane-runtime')   <- the proof pin is REPLACED
     V.validate_pin_agreement ManifestError: pin disagreement for github.com/nousresearch/hermes-agent: upstream.lock.yaml lane_runtime.hermes-agent-lane-runtime=b3399c13…, SBOM.yaml hermes-agent=527da608…
     S0-12 rc=0 PASS (it reads four named sections only, check_pin_diff.py:37-38)
R5b + repository: https://www.github.com/NousResearch/Hermes-Agent/   : the same (normalize_repo, V:174-177 `normalize_repo`, folds www., case and the slash)
R5c + repository: https://github.com/example/hermes-agent-fork.git    : T 2 failed · V 25 entries, validate_pin_agreement OK (not in the SBOM)
```

  The later entry wins V:621 `normalize_repo` `parsed[normalize_repo(repository)] = …`, so V's hermes-agent agreement would compare the LANE commit,
  not the proof pin, with the SBOM. It fails closed today only because `SBOM.yaml:25-27` `name: hermes-agent` still pins 527da608.
- **Is the closed key set the only guard?** For a repository that the SBOM lists: no. V's `--check` also goes red
  (`validate_pin_agreement` runs inside `render`, V:808). For any other repository: yes. T:127 `test_lane_runtime_has_exact_keys`
  and T:166 `test_lane_runtime_entry_values` are the only guards.
- **Is §12's sentence TRUE at the PIN?** Operatively, yes. H:737-738 "nothing reads `lane_runtime`, so a `hermes update` or a
  `HERMES_BIN` override moves the lanes with no check failing": no check fails on a Hermes change (both instruments). Literally, it is
  loose: T reads the entry, and V reads its lines and its `commit`. "Nothing ACTS on" would be exact.
- **Is it complete?** No (FOLLOW-UP F8). Other movers with no check failing: (i) a retargeted `~/.local/bin/hermes` symlink or a
  `PATH` change (P:71 resolves `hermes` from PATH), (ii) a manual `git -C ~/.hermes/hermes-agent checkout`, (iii) a change to the
  venv's Python or SQLite with the commit unchanged. (iii) is the property the pin exists for (L `reason:` "SQLite >= 3.51.3 for WAL").
  INCIDENT-LOG.md:278 records that `hermes update` "repaired the embedded runtime to SQLite 3.53.1". `REPIN-brief.md` §REPIN-b compares
  only `rev-parse HEAD`, so "Until REPIN-b lands" implies a coverage REPIN-b will not add for `python`/`sqlite`.

## Item 6 — R3, the `verified:` value (L:173), piece by piece

**Verdict: piece (c) is FALSE as worded. "110 PC lanes FIRST launched at or after 2026-09-08 14:22:00Z" counts lanes by their LAST
launch. Five of the 110 rows are the five old-runtime lanes that the committed incident log says were first launched 11:40Z-14:12Z and
relaunched at 14:2xZ. One more row (`brief.md--0000000`) never ran Hermes. D1's "at or after" is numerically harmless; the word
"first" is not. Classified CONTRACT-DEFECT (F1): R3(c) dictates the false word.** Pieces (a), (b) and (e) are TRUE as worded.

### 6a — the counts: recount, the script, where 110/98/4 came from

Recount of the table (record lines 20-129; `sed -n '20,129p' … > rows.txt`): **110 rows; 98 `report`, 12 with no report; 4 `FAILED`,
all four among the 12; 8 no-report rows without FAILED.** The 12 no-report rows:

```
2026-09-08T17:23:53Z - FAILED pc-b5k.md--5e4f816                2026-09-15T17:09:44Z - - brief.md--0000000
2026-09-08T20:11:31Z - FAILED pc-d5n.md--887f341                2026-09-23T02:45:18Z - - pc-verify-j1-1.md--52c02ee
2026-09-08T20:23:49Z - FAILED pc-o3.md--887f341                 2026-09-23T02:51:29Z - FAILED pc-verify-j1-0-r23-stamp.md--5a00d13
2026-09-14T15:51:38Z - - pc-n5k.md--c6c384a                     2026-09-23T03:56:48Z - - pc-k1-h.md--74aa8c5
2026-09-14T21:35:12Z - - pc-n5k-xhigh.md--c6c384a               2026-09-23T07:14:08Z - - pc-verify-t92-t90r3-pcj1.md--433d15e
2026-09-14T21:56:34Z - - pc-n5k-xhigh-v2.md--c6c384a
2026-09-15T00:05:24Z - - pc-n5k-xhigh-v3.md--c6c384a
```

- **The record's script does NOT print the numbers it claims** (F7). It has no line that prints `n`, `r` or `f` (record lines
  135-147). The counters are incremented inside `for d in */; do … done | sort`: the loop is the left side of a pipeline, so it runs
  in a subshell and the counts die with it. Repro, the committed script extracted verbatim (`awk '/^```bash$/…'`, 13 lines) and run
  on a scratch `.lanes` with a scratch HOME (3 dirs at or after the cutoff, 1 before; one `report.md`, one `FAILED`):

```
--- the committed script, as recorded:
cutoff=2026-09-08T14:22:00Z now=2026-09-23T10:37:11Z
2026-09-10T00:00:00Z - - b--2
2026-09-10T00:00:00Z - FAILED c--3
2026-09-10T00:00:00Z report - a--1
rc=0
--- the same + one line after the pipeline: echo "n=$n r=$r f=$f"
n=0 r=0 f=0
```

- **Where 110/98/4 came from:** the record's Result line (record line 12) and the REPIN-a-R1 brief's premise line
  `lanes=110 with_report=98 failed_marker=4`. The committed script cannot print that line. Its producer is not in the record. The
  committed TABLE recounts to the same three numbers, so the numbers are consistent with the evidence. Their stated producer is not.
- `brief.md--0000000` (2026-09-15T17:09:44Z) is counted as a PC lane but never ran Hermes (F2). Its PIN is `0000000`, the
  dispatcher tests' fixture pin (`harness-ports/tests/test_pc_lane_dispatcher.sh:22-28` `PIN: 0000000`). P:165 `worktree add` `worktree add --detach
  "$TREE" "$PIN"` and P:168-171 `case "$HAVE" in "$PIN"*)` refuse a tree whose HEAD does not start with the PIN, before P:217 `PROMPT_FILE` writes
  `prompt.md` and before P:446 runs `"$HERMES_BIN"`. So the row is dated by the `brief.md` that scripts/pc_lane.sh:250-251 ships before
  launch (the record's "else brief.md" branch, record line 141). SOLID by code, on one assumption: no commit or ref in the PC clone
  resolves from `0000000`. How the directory came to exist on the PC is UNSURE (no committed record names it).

### 6b — "first launched": the mtime of `prompt.md` is the LAST launch

- P:217-218 `PROMPT_FILE="$LANE_DIR/prompt.md"` then `: > "$PROMPT_FILE"` truncate and rewrite `prompt.md` on EVERY start of a lane
  directory that passes the state guard: P:102 `if [ -s "$REPORT" ]` (a lane with a non-empty report exits before P:218 `PROMPT_FILE`) and P:106 `PIDFILE`
  (a live pidfile exits too). A relaunch of a stopped or refused lane (empty report) therefore resets the mtime. Both lines date from
  097b0e3 (2026-09-03, `git log -S`), before every row. The retry loop inside one run writes `prompt.attemptN.md` (P:321 `PROMPT_RUN`), never
  `prompt.md`.
- **Concrete rows, from the committed record.** `docs/INCIDENT-LOG.md:278` (2026-09-08 14:2xZ): "B2, VERIFY-B5j, VERIFY-N5i, VERIFY-M2
  and VERIFY-G2 (started 11:40Z-14:12Z on the 3.49.1 runtime) … the five old-runtime lanes stopped by pid … and relaunched staggered
  75 s apart on the repaired runtime (each resumes from its draft and tree under the RESUME note)". The record's lines 21-25:

```
2026-09-08T14:25:47Z report - pc-verify-b5j.md--01499e7
2026-09-08T14:27:09Z report - pc-verify-n5i.md--628da83
2026-09-08T14:28:43Z report - pc-b2.md--246bec7
2026-09-08T14:29:54Z report - pc-verify-m2.md--cb91edf
2026-09-08T14:31:16Z report - pc-verify-g2.md--887f021
```

  These are the same five names, 71-94 s apart. Second source for two of them: `todo/BUILD-TASKLIST.md:32` has VERIFY-B5j dispatched
  on 01499e7 after "lane B5j LANDED as checkpoint 9b 01499e7 (12:4xZ)", "resumed once after a Hermes storage death" (13:3xZ,
  INCIDENT-LOG.md:277). INCIDENT-LOG.md:277 has VERIFY-G2 dying "at item 0 after 35 min" at 14:11Z, so it was launched about 13:36Z.
  Third instance of last-launch dating, outside the cutoff: `pc-verify-t92-t90r3-pcj1.md--433d15e` reads 07:14:08Z, the relaunch
  CLAUDE.md records (AF-AP-140, "VERIFY-T92, 2026-09-23 07:14Z"); the lane was dispatched 01:28Z (`docs/08_DECISION_LOG.md` D-049).
- **Did the five run on b3399c1?** Partly. Each relaunch is a new pc-lane.sh process and a new Hermes process (P:446 `HERMES_BIN`), started after
  the 14:19Z repair ("VERIFY-D5m (started 14:22:31Z, after the repair at 14:19Z)", INCIDENT-LOG.md:278). So the resumed attempt ran the
  repaired runtime (INFERRED as b3399c1: no lane records its sha, and the 2026-09-23 probe reads b3399c1, committed 14:05:24Z on
  09-08). Every earlier attempt ran the old runtime, SQLite 3.49.1 (INCIDENT-LOG.md:277 names its source `58472d8`). The resumed
  session continued the old runtime's draft and tree (P:320-322, the RESUME note). Each of these five reports is a mixed-runtime product.
- **Is "first launched" the right word?** No. The rule measures the latest launch. On the committed evidence, at most 105 of the 110
  were first launched at or after 14:22:00Z (104 that ran Hermes, without `brief.md--0000000`), and 93 of those have a report. The
  record's own Rule line (record line 8, "its directory's first launch (the mtime of `prompt.md`, else `brief.md`)") carries the same
  error, and its "Limits, stated" list does not name it.
- D1 ("at or after 14:22:00Z" vs "after 14:22Z"): no row is at 14:22:00Z exactly (the earliest is 14:22:32Z), so both readings give
  the same table. D1 is TRUE as a count rule. The defect is the word "first", not the comparator. The cutoff itself is conservative:
  the record calls 14:22:00Z "the owner's `hermes update`", but INCIDENT-LOG.md:278 dates the repair 14:19Z (INFO).

### 6c — "with a report": what a non-empty `report.md` can be

- **A promoted draft** (SOLID by code): P:502-505. When the final report is empty and the draft is not, `report.md` becomes "DRAFT
  REPORT — the lane ended (harness rc=$rc) before writing its final report; … Grade it as PARTIAL evidence, never as a verdict." plus
  the draft. The record's `[ -s "$d/report.md" ]` counts it as `report`. How many of the 98 are drafts is not recorded
  (`head -c 12 report.md` would tell).
- **A harness failure line in a spelling the classifiers miss** (the regex behavior is SOLID; the rendering is UNSURE): P:305 `PERSIST_RX`
  `PERSIST_RX='^(⚠️ )?No reply: '` allows exactly one space after the glyph. T91 widened P:304 `SAFETY_RX` because "Hermes can
  render two, one, or zero spaces after the warning glyph, or no glyph" (P:302 `Hermes can render two`). `PERSIST_RX` did not get the same fix. Repro, P's
  own regex definitions `eval`ed from P:269-305 `CAPACITY_RX`:

```
PERSIST_RX=^(⚠️ )?No reply:
glyph+0 space(s): NOT retried NOT FAILED -> stands as report.md
glyph+1 space(s): retried(P:469 `LANE_CAPACITY_RETRIES`) FAILED(P:496)
glyph+2 space(s): NOT retried NOT FAILED -> stands as report.md
no glyph: matched
SAFETY glyph+0: matched      SAFETY glyph+1: matched      SAFETY glyph+2: matched
```

  A zero- or two-space `No reply:` line is neither retried (P:469 `LANE_CAPACITY_RETRIES`) nor made FAILED (P:496), so it stands as `report.md`, and the lane
  record counts it as `report`. The sandbox poller has the same one-space pattern (`scripts/pc_lane.sh:384`, `'^API call failed|^(⚠️
  )?No reply: '`). FOLLOW-UP F12 (outside the component; the dispatcher owner).
- Refusal lines of the 2026-09-07 class no longer stand after P:496-499, and a safety refusal is FAILED at P:459-467. A runner that
  predates a fix did let one stand: VERIFY-G2's 14:11Z `No reply:` "came home as its report once more" (INCIDENT-LOG.md:277), but
  that lane was relaunched, so its row's `report.md` is the later one.

### 6d — "harness-ports/tests/run-all.sh on the PC … (binary-free by its header)"

- The header: `harness-ports/tests/run-all.sh:2-3` `Deterministic` "Deterministic, LLM-free, no network, no harness binary required." The suites
  that touch Hermes inject a fake binary: `harness-ports/tests/test_pc_lane.sh:539` `HERMES_BIN="$FAKE_HERMES"`,
  `harness-ports/tests/test_lane_profile.sh:56` `export HERMES_BIN="$BIN/hermes"` (a stub). The pass (at 2ebd486, an ancestor of the
  PIN; `git diff --stat 2ebd486 879ee98 -- harness-ports/ .claude/hooks/` is empty) proves the harness adapters and the lane plumbing on
  the PC's shell and on the lanes' AF_VENV Python 3.13.11. It proves nothing about b3399c1, whose Python is 3.11.15.
- The ledger does NOT overclaim it: `todo/BUILD-TASKLIST.md:226` `F4 DECIDED` says "it proves the harness adapters on the PC's shell and Python,
  not b3399c1". §12 (H:728-745 `Lane runtime pin`) does not cite it.
- The value is weaker than the ledger (INFO F13). It is the FIRST piece of a field named `verified:` on the b3399c1 entry, and its
  only disclaimer is the parenthetical "(binary-free by its header)". A reader who does not know that "binary-free" means "never runs
  Hermes" can take the pass as a test OF b3399c1. It also names a second Python (3.13.11) beside the runtime's 3.11.15. The words are
  R3(a)'s, dictated "in these words or plainer", so the builder met the contract. The ledger's own clause would be plainer.

### 6e — the identity facts across L, H §12, the ledger, the decision log and CLAUDE.md

No contradiction on b3399c1 / v0.21.1 / Python 3.11.15 / SQLite 3.53.1 / WAL. SOLID:
- L:166-169 `commit: b3399c13…`, `version: "0.21.1"`, `python: "3.11.15"`, `sqlite: "3.53.1"`; L:173 the probe piece.
- H:730-731 "`b3399c1` (v0.21.1, python 3.11.15, SQLite 3.53.1)".
- `todo/BUILD-TASKLIST.md:226`: "08:58Z: `git rev-parse` b3399c13…, `Hermes Agent v0.21.1 (2026.9.7) · upstream b3399c13`, venv
  `3.11.15 3.53.1`, the shared state.db `wal`".
- `docs/08_DECISION_LOG.md:54` D-043: "`b3399c1` (dist 0.21.1, committed 2026-09-08 14:05:24Z, venv python 3.11.15, SQLite 3.53.1)
  … `journal_mode=wal`". D-048 item 3: "b3399c1 (0.21.1, python 3.11.15, SQLite 3.53.1, WAL)".
- `CLAUDE.md:79`: "it is WAL since (lane runtime b3399c1, SQLite 3.53.1; read-only probe 2026-09-23 08:58Z)".

INFO (outside the component): D-048 rejects option (a) because "the pinned venv's SQLite 3.47.2 carries the WAL-reset bug that killed
lanes". D-043 says of the same option: "the WAL-reset death class seen on 3.49.1 — NOT measured on 3.47.2". The two do not strictly
contradict (3.47.2 is below 3.51.3, the fixed version, so it carries the bug by version range), but "that killed lanes" names deaths
seen on 3.49.1. Also INFO: since T92/D-049 each lane runs on its own cloned profile (P:429-443 `per-lane clone`), so "shared state.db WAL" now
describes the owner's interactive profile's database, not the one a new lane writes.

## Item 7 — R4 and R5

**Verdict: R4 holds: every one of the eight values is pinned and named. R5 is a presence pin on prose. It stays green under negation,
contradiction, an HTML comment and a code fence (AF-AP-80's class). A behavioral pair is possible (FOLLOW-UP F14).** SOLID.

R4. T:62-71 `LANE_RUNTIME_EXPECTED` holds all eight keys. T:166-174 `test_lane_runtime_entry_values` compares the whole dict and names
every differing key (T:171 `entry.get(key, '<absent>')` `f"{key}: got …"`). One mutant per key on a scratch copy of L:

```
R4 commit               7 failed, 9 passed    entry_values names key: True  | + commit_value, the five control params (their de-vacuous assert, T:250 `hermes-agent-lane-runtime`)
R4 version              2 failed, 14 passed   entry_values names key: True  | + test_lane_runtime_version
R4 python               1 failed, 15 passed   entry_values names key: True
R4 sqlite               2 failed, 14 passed   entry_values names key: True  | + test_lane_runtime_sqlite
R4 role                 1 failed, 15 passed   entry_values names key: True
R4 reason               1 failed, 15 passed   entry_values names key: True
R4 diff_from_proof_pin  1 failed, 15 passed   entry_values names key: True
R4 verified             2 failed, 14 passed   entry_values names key: True  | + test_lane_runtime_verified_value
```

R5. T:213-222 `test_harness_ports_section_12_says_the_pin_is_unenforced` finds the one heading line (T:216 `line == SECTION_12_HEADING`),
takes §12 up to the next `## ` line (T:218 `for j in range(heads`), collapses whitespace (T:219 `section = " ".join(" ".join(lines` `" ".join(… .split())`) and checks for a SUBSTRING (T:220 `SECTION_12_UNENFORCED in section`
`SECTION_12_UNENFORCED in section`). Scratch copies of H:

```
H1 negated: "It is false that" before the sentence              : 16 passed   (SURVIVES)
H2 a contradicting sentence later in §12 ("REPIN-b has landed; the drift check runs and refuses a drifted lane.") : 16 passed (SURVIVES)
H3 the sentence inside an HTML comment (invisible when rendered): 16 passed   (SURVIVES)
H4 the sentence inside a fenced code block                      : 16 passed   (SURVIVES)
H5 the sentence moved OUT of §12 (into §11)                     : RED  docs/HARNESS-PORTS.md §12 (lines 731-746) lacks the sentence '…'
H6 §12 heading re-spelled "## 12. Lane-runtime pin"             : RED  docs/HARNESS-PORTS.md has 0 lines equal to '## 12. Lane runtime pin'
H7 whitespace re-flow of the sentence (one line, double spaces) : 16 passed   (EQUIVALENT by design: T:219 `split()` normalizes whitespace)
```

- R5's contract is "H §12 gains one sentence", so the presence pin meets its letter. The sentence, though, is a claim about behavior
  ("nothing reads `lane_runtime` … no check failing"). The pin guards the words, not the claim: the day REPIN-b adds a reader, T stays
  green with a false §12. That is AF-AP-80's shape (a presence assertion stands in for the property it names), accepted here by the
  contract's own wording. INFO for R5; FOLLOW-UP F14 for the pair.
- **A behavioral pair for prose is possible**, in two parts. (i) A state pair: while the sentence is present, assert that no code
  outside T names the entry (a scan of `scripts/`, `harness-ports/bin/` and `proofs/` for `hermes-agent-lane-runtime` / `lane_runtime`).
  REPIN-b's reader then turns it red and forces the sentence out in the same change. REPIN-b's own test asserts the sentence is gone.
  (ii) A shape pin: a byte golden of the whole §12 block (R1's method), which kills H1-H4 and makes any §12 edit a conscious update.

## Item 8 — the F1-class sibling at `tests/test_s0_01_pc_tools.py:1106` `set(pins.PINNED_ENV_KEYS)` (outside the component)

**Verdict: REAL hollow claim in the sandbox suite (SOLID). The test says the default `s0-01` env is "byte-identical to the
pre-extension launcher" but asserts only the key SET. Four value mutants of `launch_env` survive the whole file. The property IS
protected at the proof's own boundary: the conformance checker grades every captured value on a fresh PC capture. So the effect is
a later catch, not a silent pass of a proof. FOLLOW-UP F15, with the minimal killing test below.** One more sibling in the same file
(F16); none elsewhere in `tests/`.

- The claim: test_s0_01_pc_tools.py:1092-1094 (docstring: "The default `s0-01` … is byte-identical to the pre-extension launcher: no
  RUST_LOG, no env_set, exact set equality with PINNED_ENV_KEYS") and :1106 `assert set(s0_01) == set(pins.PINNED_ENV_KEYS)  # default
  byte-identical to today`. The other asserts: :1107 no `RUST_LOG`; :1110 `all(s0_02[k] == s0_01[k] …)`, which compares s0-02 WITH
  s0-01, two outputs of the same function, so a shared value change passes; :1111 no `env_set`.
- Other value pins of the default env in `tests/`: only test_s0_01_pc_tools.py:1069-1070 and :1075-1076 (`HERMES_HOME`,
  `S0_01_FRAMEDIR`). graft
  (`graft ask "which tests assert the values of the launch_env default s0-01 environment" --in tests`) and `git grep -n 'launch_env(' --
  tests` find no other caller.
- Mutants on a scratch copy (`/tmp/vrr1/s8`: `proofs/S0-01` + the file + `conftest.py` + `test_s0_01_pc_post_scan.py`; the unmutated
  copy first, `99 passed, 7 skipped`, equal to the real tree's `99 passed, 7 skipped in 1.31s`):

```
M8a "PYTHONDONTWRITEBYTECODE": "1" -> "0"                                  compiles=yes collected=106 -> 99 passed, 7 skipped (SURVIVED)
M8b "PATH": pins.PINNED_PATH -> pins.PINNED_PATH + ":/usr/local/sbin"       compiles=yes collected=106 -> 99 passed, 7 skipped (SURVIVED)
M8c "BUZZ_RELAY_URL": … .replace("ws", "wss", 1)                            compiles=yes collected=106 -> 99 passed, 7 skipped (SURVIVED)
M8d "S0_01_AGENT": pins.PINNED_AGENT_REALPATH + ".bak"                      compiles=yes collected=106 -> 99 passed, 7 skipped (SURVIVED)
```

- The downstream guard: `proofs/S0-01/check_acp_conformance.py:443-498` `check_env` grades a CAPTURED `env.json` value by value
  (`BUZZ_ACP_SESSION_POLICY`, `HERMES_HOME`, `BUZZ_RELAY_URL`, `S0_01_AGENT`, `PATH`, `HOME`, `PYTHONDONTWRITEBYTECODE`, the framedir,
  the respond-to and the owner). A launcher value regression therefore fails the next PC capture's grading. The committed real-leg
  corpus predates any such change, so the sandbox suite stays green.
- **Minimal killing test** (in the same test, after :1105): `assert s0_01 == {"PATH": pins.PINNED_PATH, "HOME": pins.PINNED_HOME,
  "BUZZ_PRIVATE_KEY": "fixture-value-not-a-key", "BUZZ_RELAY_URL": pins.PINNED_RELAY_URL, "BUZZ_ACP_AGENT_OWNER": "f" * 64,
  "BUZZ_ACP_RESPOND_TO": "owner-only", "BUZZ_ACP_SESSION_POLICY": pins.PINNED_SESSION_POLICY, "HERMES_HOME": home,
  "OMNIROUTE_API_KEY": "fixture-value-not-a-key", "PYTHONDONTWRITEBYTECODE": "1", "S0_01_FRAMEDIR": base_args[1], "S0_01_AGENT":
  pins.PINNED_AGENT_REALPATH}`. It kills M8a-M8d (not run here: never fix). It pins the launcher's MAPPING. A change to a pin value
  stays a pins.py change, which the checker governs.
- Sweep of `tests/` for the class "a message or comment claims byte identity, the assert compares a projection"
  (`git grep -n -i -E 'byte[- ]identical|byte for byte|byte-for-byte|bytewise|bitwise|byte-equal|identical to (today|the (pre|old|committed))' -- tests`,
  ten files, each read):
  - **Sibling F16:** test_s0_01_pc_tools.py:1130-1131 says the default "env.json is byte-identical to the pre-extension bytes". The
    assert, :1133 `pc_launch.env_json_with_set_marker(live, "s0-01") == live`, compares DICTS. The bytes come from
    `proofs/S0-01/tools/pc/pc_launch.py:383` `json.dumps(live_env, indent=1, sort_keys=True) + "\n"`. Mutant M8e (`indent=1` ->
    `indent=4`): compiles, 106 collected, `99 passed, 7 skipped` (SURVIVED). The checker reads env.json through `json.load`, so the
    byte format is pinned nowhere. Low effect: a formatting change, not a value change.
  - Real byte comparisons (not siblings): test_decisions_canonical.py:62-75 (digest equality with a pasted golden, twice);
    test_decisions_ledger.py:106-115 (`bytes_a == bytes_b`); test_s0_01_scripted_backend.py:181-199 (`a == b` on status + body bytes);
    test_s0_02_buzz_authz.py:3183 (`concat_ok` comes from `cmp -s`, :3142); test_s0_05_egress.py:2679-2687 (the exact
    `(returncode, stderr)`); T:200-210 `test_hermes_agent_entry_lines_golden` (the raw entry lines).
  - Prose, not an identity assert: test_s0_01_acp_probe.py:2252 (a measured signature), test_s0_01_turn_capture.py:6 (a disclaimer),
    test_s0_06_four_scope.py:204 (a helper comment).

## Item 9 — MUTANTS (new; never the builder's 28 rows)

Method (`/tmp/vrr1/item9.py`): each T-mutant is an exact one-site replacement on a scratch copy of T (the replacement asserted unique),
`py_compile`d, collected, then run on the COMMITTED L and H (the suite as CI runs it). R1, R4 and R5 are goldens with no committed
negative control over a hostile lock, so a mutant of their REJECTION path can only be told apart by a hostile input. Each such
mutant is also PAIRED with the input its line exists to catch, and the UNMUTATED T ran on that input first (AF-AP-138). The
committed-data control (unmutated T, committed L/H) is `16 passed` (item 2's CONTROL row). Verdicts: KILLED = a committed test goes
red on committed data; SURVIVED = the mutant accepts an input the unmutated T rejects, and no committed test catches it;
EQUIVALENT = no input changes the verdict toward acceptance.

| mutant (T line) | compiles | collected | committed L/H | paired hostile input: UNMUTATED -> MUTANT | verdict |
|---|---|---|---|---|---|
| M1 T:101 head test `line.strip() == "hermes-agent:"` | yes | 16 | 16 passed | HEAD3 `   hermes-agent:` 15 failed -> 15 failed · HEADTS trailing space 1 failed -> 1 failed · HEADTAB 15 -> 15 · CRLF 1 -> 1 | EQUIVALENT: the golden's first line (T:26 `"  hermes-agent:"`) re-checks the head bytes, so a loosened count only moves the message |
| M1b T:101 `line.startswith("  hermes-agent")` | yes | 16 | **1 failed**: `has 2 lines equal to '  hermes-agent:' (at [10, 165])` | — | KILLED on committed data by T:200 `test_hermes_agent_entry_lines_golden` (the near-miss `  hermes-agent-lane-runtime:` at L:165) |
| M2 T:109 `selected_core:` parent assert disabled (`assert True or …`) | yes | 16 | 16 passed | S8 (entry under `selected_later_planes:`) 2 failed -> 1 failed (the parsed view still red) · **S8Q (S8 + a same-valued quoted twin in selected_core) 1 failed -> 16 passed** | SURVIVED: on S8Q the parent assert is the ONLY catch, and no committed test exercises it |
| M3 T:112 `re.match` end regex narrowed to `r"  \S"` | yes | 16 | 16 passed | LASTNB (entry last in selected_core, no blank line after) 16 passed -> **1 failed** · S8 2 -> 2 · CRLF 1 -> 1 | EQUIVALENT for acceptance: a narrower end only lengthens the entry, so it is never weaker; it adds a false red on LASTNB |
| M4 T:88 `re.fullmatch` -> `re.match` | yes | 16 | **1 failed**: `test_bad_lane_runtime_commit_rejected[41-hex] - Failed: DID NOT RAISE ValueError` | — | KILLED by the live control [41-hex] |
| M5 T:88 `isinstance(commit, str)` guard removed | yes | 16 | **1 failed**: `[yaml-integer] - TypeError: expected string or bytes-like object, got 'int'` | — | KILLED by [yaml-integer] |
| M5b T:88 `isinstance(commit, str)` guard removed + `str(commit)` coercion | yes | 16 | **1 failed**: `[yaml-integer] - Failed: DID NOT RAISE ValueError` | — | KILLED by [yaml-integer] |
| M6 T:216 `SECTION_12_HEADING` heading match `line.startswith("## 12")` | yes | 16 | 16 passed | H6 (`## 12. Lane-runtime pin`) 1 failed -> **16 passed** | SURVIVED, benign: R5 fixes the sentence, not the heading's spelling |
| M7 T:243 `committed_line` control count assert disabled | yes | 16 | 16 passed | CMT (lane commit line + `  # pinned`) 5 failed (`occurs 0 times`) -> 5 failed (T:250 `hermes-agent-lane-runtime` `assert 'b3399c13…' == 'b3399c1'`) | EQUIVALENT: T:250's de-vacuous assert is a second guard |
| M10 T:185 `test_hermes_agent_entry_unchanged` parsed view disabled (renamed, 15 collected) | yes | 15 | 15 passed | S5 (quoted later duplicate, another commit) 1 failed -> **15 passed** | SURVIVED: the parsed view is load-bearing (item 2) |

The L- and H-level mutants of items 2-8 have their rows in those items: S1-S8b (item 2), 19 commit shapes (item 3), D1-D3 (item 4),
R5a-R5c (item 5), eight R4 values and H1-H7 (item 7), M8a-M8e (item 8, on `proofs/S0-01/tools/pc/pc_launch.py`). Survivors among them:
S5e (F4), D1/D1c/D2 (F6), H1-H4 (F14), M8a-M8e (F15/F16). Equivalents: S2, S5s/S5es (for T), S6, D3, H7.

Reading: the killable-on-committed-data set is exactly R2's helper (M4, M5, M5b) plus the exact-head near-miss (M1b). R1's parent
check (M2), R5's heading (M6) and the parsed view as a whole (M10) have no committed negative control; each is exercised only by the
scratch shapes in this report. That is in-contract (R1 asked for a golden plus the G1-G7 mutation table, not for committed hostile
fixtures), so it is recorded as FOLLOW-UP F17, not a blocker.

## Item 10 — gates (each command with its output; 2026-09-23 10:46:48Z)

```
$ bash scripts/test_summary.sh tests/test_upstream_lock_lane_runtime.py --basetemp /tmp/vrr1/bt   (run 1; rm -rf between)
pytest-exit: 0
pytest-summary: 16 passed in 0.20s
$ bash scripts/test_summary.sh tests/test_upstream_lock_lane_runtime.py --basetemp /tmp/vrr1/bt   (run 2)
pytest-exit: 0
pytest-summary: 16 passed in 0.18s
$ bash scripts/test_summary.sh tests/test_s0_12_license_sbom.py --basetemp /tmp/vrr1/bt12   (basetemp added: the brief's scratch rule)
pytest-exit: 0
pytest-summary: 5 passed in 0.22s
$ python3 scripts/vendored_manifest.py --check
PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots
rc=0
$ python3 scripts/validate-ledger integrity --root .      (10 PRESENT, 2 ABSENT = S0-02 and S0-05, unminted; 0 INVALID)
S0-01 PRESENT · S0-02 ABSENT · S0-03 PRESENT · S0-04 PRESENT · S0-05 ABSENT · S0-06 … S0-12 PRESENT
blocked_credential numerator=0 denominator=1 · blocked_host numerator=0 denominator=1
conformance_checked_decision numerator=3 denominator=3 · execution_proof numerator=7 denominator=9
rc=0
$ bash scripts/verify-planning-repo.sh
12_DOCKER_COMPOSE.md: OK
13_ENV_EXAMPLE.md: OK
planning repository verification passed
rc=0
$ python3 scripts/report_lint.py --min-refs 10 --map T=tests/test_upstream_lock_lane_runtime.py --map L=upstream.lock.yaml --map H=docs/HARNESS-PORTS.md tasks/briefs/hermes-repin/REPIN-a-R1-report.md --root .
report_lint: 43 refs — OK 43, NEAR 0, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
rc=0
```

Red-green (technique 3), reproduced: the landed T on the pre-repair L and H at 1978e55 (the R1 brief's PIN), through the harness ->
`3 failed, 13 passed`: `test_lane_runtime_entry_values` (`differs at verified: got 'harness-ports/tests/run-all.sh (sandbox) + 43
PC-lane HOME/LANDED notes …`), `test_lane_runtime_verified_value`, `test_harness_ports_section_12_says_the_pin_is_unenforced`. These are
the same three names as the builder report's RED-PIN row (its line 170). The builder's RED claim is TRUE.

## FINDING INVENTORY (no severity filter; each with the blocking predicate applied)

Predicate columns: (1) contract-mapped to R1-R5 / the frozen REPIN-a contract · (2) reproduced through the real path at the PIN ·
(3) materially effective · (4) a concrete discriminator · (5) in-boundary (T, L, H).

| id | class | where | what | evidence | (1) | (2) | (3) | (4) | (5) | fix (one line) |
|---|---|---|---|---|---|---|---|---|---|---|
| F1 | **CONTRACT-DEFECT** | L:173 `verified:` piece (c); T:58 `"110 PC lanes first launched at or after 2026-09-08 14:22:00Z (98 with a report), "`; record line 8 (the Rule) | "first launched" is false. The count dates each lane by `prompt.md`'s mtime, which P:218 `: > "$PROMPT_FILE"` resets on every start that passes P:102-109 `$REPORT`, so it is the LAST launch. Record lines 21-25 are the five lanes that INCIDENT-LOG.md:278 says started 11:40Z-14:12Z on the 3.49.1 runtime and were relaunched at 14:2xZ. At most 105 of the 110 were first launched at or after the cutoff; the five reports are mixed-runtime | SOLID: committed rows + INCIDENT-LOG.md:277-278 + BUILD-TASKLIST.md:32 + P:217-218 (the PC dirs not re-measured: no bridge) | R3 ("says what each piece proves") vs R3(c)'s dictated words: the frozen text is self-contradictory (its number counts last launches, its word names first launches) | yes: L:173 at the PIN, pinned by T:177-182 | yes: the repair's replacement evidence value is still false in a named way, the defect class R3 existed to close (F3 of VERIFY-REPIN-a) | `sed -n 21,25p` the record · `sed -n 278p docs/INCIDENT-LOG.md` · `sed -n 217,218p` P | the words are dictated by R3(c) and by the coordinator's record, so the builder cannot change them without an amendment -> RETURNED | amend R3(c): "110 PC lane directories last launched at or after 2026-09-08 14:22:00Z (98 with a non-empty report.md); 5 (B2, VERIFY-B5j/-N5i/-M2/-G2) first launched 11:40Z-14:12Z on 3.49.1 and resumed on the repaired runtime; 1 (brief.md--0000000) never ran Hermes"; T:58-59 and the record's Rule line to match |
| F2 | **CONTRACT-DEFECT** (part of F1) | record line 63 `brief.md--0000000` | counted among the "110 PC lanes", but it never ran Hermes: P:165-171 `worktree add` refuse PIN `0000000` before P:217 writes `prompt.md` and before P:446 `HERMES_BIN` runs Hermes, so the row is dated by the dispatcher's `brief.md` (scripts/pc_lane.sh:250-251) | SOLID by code (assumes no ref resolves from `0000000`); its origin UNSURE | R3(c) | yes | yes (1 of 110) | the row + P:165-171 | returned with F1 | fold into F1's wording |
| F3 | FOLLOW-UP | L:173 "(98 with a report)"; record line 9 | a non-empty `report.md` can be a promoted PARTIAL draft (P:502-505); how many of the 98 are drafts is not recorded | SOLID (code) / UNSURE (count) | R3(c) (wording) | — | low: the record defines `report` precisely | P:502-505 | the record is outside | record `head -c 12 report.md` per row; state "N final, M partial" |
| F4 | FOLLOW-UP | T:81 `_load_lock`; T:101 | S5e: a quoted `"hermes-agent":` with another commit placed BEFORE the original passes T (both views), V and S0-12 | SOLID (reproduced) | no: R1's letter is the unquoted head line | yes | latent: no current reader reads it; a human or first-match reader does | S5e row, item 2 | yes | a duplicate-key-refusing SafeLoader in `_load_lock` (kills S5, S5s, S5e, D1, D1c, D2 at once) |
| F5 | FOLLOW-UP (outside: V, a live PC lane owns it; task #170 holds V's parse bugs) | V:605 `re.fullmatch` header regex; V:611-612 `if match and component` | V skips a quoted two-space header and writes its children into the PREVIOUS component. S5s silently drops `gvisor` from V's pin agreement (24 -> 23 entries, `validate_pin_agreement` OK); S5 misnames the hermes pin `selected_core.gvisor` | SOLID (V run read-only on scratch copies) | none for this component | yes | yes, for V's pin agreement | S5s row, item 2 | no | V raises ManifestError on any two-space line that is not a recognized `  name:` header (AF-AP-25's line-parser class) |
| F6 | FOLLOW-UP | T:81 `_load_lock`, T:85-90; REPIN-b | a duplicate `commit:` (or `verified:`) in the lane-runtime entry, the pin LAST, passes all 16 tests, V and S0-12. A first-match reader reads the other value, even the 7-hex `b3399c1` (D1c) | SOLID (reproduced) | no: R2 names five single-value replacements, R4 the parsed values | yes | latent now; live when REPIN-b's bash reader lands | D1, D1c rows, item 4 | yes (T) / REPIN-b's brief | the same loader as F4; REPIN-b's contract carries a "duplicate key refused" control |
| F7 | FOLLOW-UP | record lines 135-147 | the committed script cannot print 110/98/4: no line prints `n`/`r`/`f`, and they die in the `for … done \| sort` subshell (repro: `n=0 r=0 f=0`). The producer of `lanes=110 with_report=98 failed_marker=4` is not committed; the table recounts to the same numbers | SOLID (repro) | R3 ("every number … copied from … the lane record") | yes | low: the numbers reproduce from the table | item 6a repro | no (the coordinator's record) | count from the printed rows (`… \| sort \| tee rows; awk …`) and commit the command that printed the summary |
| F8 | FOLLOW-UP | H:737-738 | the sentence is operatively true but loose ("nothing reads": V:598-613 parses the entry; T reads it) and incomplete (a PATH or symlink retarget, a manual checkout, a Python/SQLite change with the commit unchanged; REPIN-b as briefed checks only the commit) | SOLID (graft + grep + the dispatcher grep) | R5 dictated the words: in letter | yes | low | item 5 | yes (H) | "nothing ACTS on `lane_runtime` … REPIN-b will check the commit only, not python/sqlite" |
| F9 | INFO | T:205-210 | S1: the message says `got '<no line>'` at L line 13, which holds the comment that ended the entry | SOLID | R1 ("names the first differing line": the number is right) | yes | no | S1 row | yes | print the file's line when the slice is short |
| F10 | INFO | T:112 `re.match` | conservative false reds: a blank line, a 4-space or column-0 comment after the entry, or the entry moved to the end of `selected_core:` (S3b, S2b, S2c, S8b) | SOLID | — | yes | no (fail-closed) | item 2 rows | yes | none needed |
| F11 | INFO | T:89 | an int is named by its decimal repr (octal row); a missing `commit` key raises `KeyError`, not the named text | SOLID | outside R2's five shapes | yes | no | item 3 rows | yes | optional |
| F12 | FOLLOW-UP (outside: P, `scripts/pc_lane.sh:384`) | P:305 `PERSIST_RX` | only a one-space `⚠️ No reply:` is retried or made FAILED. T91 widened P:304 `SAFETY_RX` for 0/1/2 spaces (P:302 `Hermes can render two`). A 0- or 2-space line stands as `report.md` and counts as `report` | regex behavior SOLID (repro); Hermes's rendering UNSURE | none here | — | possible: a false report | item 6c repro | no | `'^(⚠️[[:space:]]*)?No reply: '` at P:305 and pc_lane.sh:384, plus three spacing fixtures |
| F13 | INFO | L:173 piece (a) | the only disclaimer is "(binary-free by its header)", first in `verified:` of the b3399c1 entry, beside a second Python (3.13.11); a reader can take the pass as a test OF b3399c1. The ledger (BUILD-TASKLIST.md:226) says it plainly | SOLID | R3(a) dictated the words: met | yes | low | item 6d | amendment | with F1: "(binary-free by its header: it tests the harness adapters on the PC's shell and Python, not b3399c1)" |
| F14 | FOLLOW-UP | T:213-222 | R5 is a presence pin (AF-AP-80's shape): H1 negation, H2 contradiction, H3 HTML comment, H4 code fence stay green; REPIN-b landing would leave §12 false and T green | SOLID (reproduced) | R5's letter is met | yes | latent | H1-H4 rows | yes | a state pair (no reader of the entry outside T while the sentence stands) and/or a byte golden of §12 |
| F15 | FOLLOW-UP (outside) | tests/test_s0_01_pc_tools.py:1092-1094, :1106 | "byte-identical" claim, key-SET assert; M8a-M8d survive the file; caught downstream by check_acp_conformance.py:443-498 on a fresh PC capture | SOLID (mutants) | none here | yes | medium: a late catch, not a silent proof pass | M8a-M8d | no | the dict golden in item 8 |
| F16 | FOLLOW-UP (outside) | tests/test_s0_01_pc_tools.py:1130-1133; pc_launch.py:383 | env.json "byte-identical" claim, dict assert; M8e (writer indent) survives; the byte format is pinned nowhere | SOLID (mutant) | none here | yes | low | M8e | no | assert the serialized bytes against a pasted golden |
| F17 | FOLLOW-UP | T (R1, R4, R5 tests) | no committed negative control over hostile L/H: M2 (parent check), M6 (heading) and M10 (the parsed view) survive the committed suite; only R2 has a live control | SOLID (item 9) | in contract (R1 asked for a golden + the G-table) | yes | latent | M2/S8Q, M6/H6, M10/S5 | yes | parametrize S8, S8Q, S5, H6 as committed controls, like R2's |
| F18 | INFO | record lines 8-9 | the cutoff 14:22:00Z is called "the owner's `hermes update`"; INCIDENT-LOG.md:278 dates the repair 14:19Z (conservative) | SOLID | — | — | no | the two lines | no | say "3 minutes after the 14:19Z repair" |
| F19 | INFO (outside) | docs/08_DECISION_LOG.md D-043 vs D-048 | D-048: 3.47.2 "carries the WAL-reset bug that killed lanes"; D-043: the death class is "NOT measured on 3.47.2". By version range, not a strict contradiction | SOLID | — | — | no | the two rows | no | D-048: "carries the bug by version (< 3.51.3); the deaths were on 3.49.1" |
| F20 | INFO | L:173 piece (b) | since T92/D-049 each lane runs on its own cloned profile (P:429-443 `per-lane clone`); "shared state.db WAL" now describes the owner's interactive profile's database | SOLID (code) | — | — | no | P:429-443 | amendment | optional clause |
| F21 | INFO (pre-existing, outside R5) | H:734-736 | "`~/.local/bin/hermes` resolves to the … install": D-043 says it is a wrapper that execs it (`readlink -f` returns itself). The R5 sentence sits in the "What this pin covers" paragraph although it states what is NOT enforced | SOLID | R5 said "nothing else in H changes" | — | no | D-043 row | yes | "is a wrapper that execs"; a paragraph break before "Until REPIN-b lands" |

Verified TRUE (reproduced, no finding): R1 kills every shape that changes the six lines, and the parsed view is load-bearing (S5);
R2 rejects every non-hex shape by the named text and passes no value that is not 40-lowercase-hex; R4 names all eight keys; the
builder's RED run; D1's comparator ("at or after 14:22:00Z" gives the same 110 rows as the table); pieces (a) and (b) as facts; the
b3399c1 / 0.21.1 / 3.11.15 / 3.53.1 / WAL identity across L, H, the ledger, D-043/D-048 and CLAUDE.md; L and H changed only on the
R-lines (`git diff 3846636 879ee98`: L:173 `verified:` and H:737-738 `lane_runtime`).

## GATE RECOMMENDATION

**`CONTRACT-INVALID` — scoped to R3(c) only.** The frozen text of R3(c), "110 PC lanes first launched after 2026-09-08 14:22Z (98 with
a report)" with "every number … copied from … the lane record", is self-contradictory. The record's 110 counts LAST launches (P:218 `PROMPT_FILE`),
and five of the 110 were first launched before the cutoff on the old runtime (INCIDENT-LOG.md:278), so no implementation can make the
value both "110" and "first launched" and true. It is returned as CONTRACT-DEFECT F1 (with F2) for an explicit amendment of R3(c) and
of the record's Rule line. It is not a repair of the builder's work: the builder met R3(c)'s words. R1, R2, R4, R5 and R3(a)(b) carry
NO blocker. On their own they are **MERGE-READY-WITH-FOLLOWUPS** (F3-F21 above). After the amendment, the re-landing is one value
(L:173 `verified:`) and its pin (T:58-59 `110 PC lanes first launched`).

Per-finding predicate result: F1, F2 meet (2), (3) and (4), fail (5) for the builder (the words are the contract's), and meet the
CONTRACT-DEFECT exception (the committed evidence is falsified): RETURNED, not a builder blocker. F3-F21 each fail (1) or (5): none
blocks.

This recommendation depends on committed records (the incident log, the ledger, the lane record) for the PC-side facts. The PC lane
directories themselves were not re-measured (no bridge, by the brief).

## What was reproduced, what was reviewed statically, what was skipped

- REPRODUCED (this session, scratch copies under `/tmp/vrr1/`, all removed): item 1's premise; every row of items 2, 3, 4, 5, 7, 8 and 9;
  the record-script counter repro (6a); the PERSIST_RX spacing repro (6c); the red-green run; all item-10 gates.
- STATIC (primary source read, not executed): P's prompt, report, draft and refusal paths (6b, 6c); `run-all.sh`'s header and its
  fake-binary injection (6d); the checker's `check_env` value grades (item 8); the incident-log and ledger records of the five relaunches.
- SKIPPED, with the reason: the PC `.lanes/` directories and the identity probe (no bridge: the brief attacks PC numbers by consistency
  only); `/bug-echo` sweeps (a verifier reports; the coordinator echoes); the builder's 28 mutant rows (the brief: new mutants only);
  thermo-nuclear full-stack review (not in this brief); running the S0-02/S0-05 tests (other lanes' boundary: read only).

## NOT done

- No fix of any finding (never fix; the boundary is this report).
- No PC re-measurement of the 110 directories, of `brief.md--0000000`'s origin, or of how many of the 98 reports are drafts.
- No test of Hermes's real `No reply:` rendering (F12 stays UNSURE on that point).
- No edit to V, P, the lane record, `tests/test_s0_01_pc_tools.py` or any other file.

## Lint (own report; three fix rounds, then paste)

```
$ python3 scripts/report_lint.py --min-refs 12 --map T=tests/test_upstream_lock_lane_runtime.py --map L=upstream.lock.yaml --map H=docs/HARNESS-PORTS.md --map P=harness-ports/bin/pc-lane.sh --map V=scripts/vendored_manifest.py tasks/briefs/hermes-repin/VERIFY-REPIN-a-R1-report.md --root .
report_lint: 162 refs — OK 161, NEAR 1, MISS 0, UNCHECKABLE 0, UNRESOLVED 0 (worktree)
```

Rounds: first run OK 101 / MISS 49 / UNCHECKABLE 9 -> OK 157 / MISS 1 -> OK 160 / MISS 1 -> OK 161 / MISS 0 (rc 0). The one NEAR is
item 7's reference to line 218 of T, which is right; the lint drops tokens that contain brackets.

