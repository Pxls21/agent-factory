# VERIFY-J1-1 report draft — adversarial-verifier lane (attempt 2; attempt 1 died on a stream timeout with no edits; this is a from-zero run)
# PIN: 52c02ee5. All runs: /home/rocco/venv-agent-factory/bin/python (python3.11), lane tree at /home/rocco/agent-factory/.lanes/pc-verify-j1-1.md--52c02ee/tree

## ITEM 1 — landing gates at the PIN (reproduced this session)

IDENTITIES — sha256[:16] + line counts, measured 2026-09-23T04:49Z:
- src/agent_factory/decisions/__init__.py: 2aec3875f71213e4 (21 lines) — matches brief premise
- src/agent_factory/decisions/canonical.py: bc9cb1d03fdb77a4 (77)
- src/agent_factory/decisions/volatile.py: b48899c883c7231f (295)
- tests/test_decisions_canonical.py: 48fdf09e8038a146 (340)
- fixtures: ap.violates_row 59fb4a16b20ffb1c (19) · b1.finding_kind fd8d0b3e63e26505 (15) · b1.finding_sev 19d9938ddf81e0bd (15) · b2.hit_role f955714a99c6ad99 (15) · d1.bug_echo_scores 9013f618e3976149 (13) · v1.finding_class ef01963a2041265a (25) · wf.drift e0dc010dc24c50ca (17)
- 01ca7d5f (J1-1 landing) vs 52c02ee5 (PIN): all 11 boundary files byte-identical (git diff --quiet per file: all clean)

GATES (all paste-exact, one foreground call each):
- pytest run 1: `14 passed in 0.02s`, run1-rc=0; run 2 (fresh basetemp): `14 passed in 0.02s`, run2-rc=0 — counts bitwise equal. SOLID.
- pyflakes on the four files: rc=0, 0 hits. SOLID.
- ap_screen --tests (the three source files): `--- TEST_SCREEN over 3 path(s): 0 hits over 3 files ---`, rc=0. SOLID.
- Seed AC 1 (ac_bdaf2f13a1cee8c9) verbatim with PYTHONPATH=src: `ModuleNotFoundError: No module named 'agent_factory.decisions.ledger'`, AC1-rc=1 — RED-until-J1-2, exactly as the brief's Gates item predicts (ledger.py is J1-2's; no stub exists in the tree — verified: `ls src/agent_factory/decisions/` = __init__.py canonical.py volatile.py only). SOLID (the red is the expected red).
- Seed AC 3 (ac_348ab0ae10309609) verbatim: `14 passed in 0.02s`, AC3-rc=0. SOLID.
- Builder report lint WITHOUT the five --map flags: `report_lint: 15 refs — OK 3, NEAR 0, MISS 0, UNCHECKABLE 12, UNRESOLVED 0 (worktree)`.
- Builder report lint WITH the five maps (as the brief names them): `report_lint: 29 refs — OK 17, NEAR 0, MISS 0, UNCHECKABLE 12, UNRESOLVED 0 (worktree)` — matches the builder report's own final line (J1-1-report.md:88) exactly. SOLID.

## ITEM 2 — seven schemas vs contract item 1 (reproduced; probe /home/rocco/tmp-vj11/probe23.py)

Schema table (SCHEMAS, measured — kind/limit/case/strip_pin/enum per key; all match the brief's item 1 key sets exactly; no extra keys, no missing keys):
- b2.hit_role: sym(str,120) file(path) snippet(str,400)
- b1.finding_sev: file(path) kind(str,80) msg(str,200)
- b1.finding_kind: file(path) kind(str,80) msg(str,200) — open slug (no enum; OPTIONS_MAX=8 recorded)
- d1.bug_echo_scores: class_slug(str,80) finding_title(str,120)
- v1.finding_class: lane(str,80,strip_pin) finding_id(str,80) title(str,120) paths(list) disposition(str,40,upper,enum BLOCKING|NON-BLOCKING)
- ap.violates_row: action_kind(str,20,lower,enum edit|command|brief|report) action_target(target) action_excerpt(str,400) row_id(str,40) row_title(str,120)
- wf.drift: step_id(str,40,lower,enum 10 values) expected(str,400) observed(str,400) drift_kind(str,40,lower,enum 5 values)
- Limits: EXCERPT_LIMIT=400 (volatile.py:26), MSG_LIMIT=200 (:27) — match item 2.

Refusal strings, each of the four classes, on EACH of the seven types (all 28+ combinations measured, all exact):
- unknown key: every type refuses timestamp/line/run_id/pin_sha as extra keys with exactly `decision-state-unknown-key: <qid>.<key>` (28/28 measured)
- missing key: every type refuses with exactly `decision-state-missing-key: <qid>.<firstkey>` (7/7)
- bad enum: v1.disposition=TOTALLY-NOPE → `decision-state-bad-enum: v1.finding_class.disposition=TOTALLY-NOPE`; wf.step_id / wf.drift_kind likewise; non-str enum value (5) → same reason with `=5`. Types without enums have none.
- unknown question: `decision-question-unknown: nope.none` (exact). Non-dict state → `decision-state-not-mapping: b1.finding_sev` (a refusal the contract does not name — SOLID: extra strictness, fail-closed, not a contract contradiction; INFO).

Never-accepted-as-KEYS: verified as extra keys (refused, exact strings) on all 7 types.
As VALUES inside allowed keys (what normalize does): a timestamp in msg, `line 42:` in snippet/msg, a run id, a PIN `330803c` in title/excerpt/msg → ALL ACCEPTED verbatim (only whitespace-collapsed). An absolute path under root in a non-path str key (msg, finding_title) → accepted verbatim (no relativization — item 2 relativizes only path/target keys; the contract names this only for paths). An absolute path in a path key with root=None → REFUSED `decision-state-abs-path` (never silently relativized — the correct fail-closed reading of item 2). So: locator-shaped VALUES pass through into the digest; the key-level closure holds, the value-level stripping does not (the contract's item 2 enumerates value-level stripping only for paths; line numbers/timestamps/run-ids as values are not in item 2's normalize list — see grading C-V1).

Fixture-variant classes ACTUALLY exercised (measured by char-level diff; the brief's item 5 lists five classes):
- ap.violates_row: abs-path-under-root + extra-whitespace (VACUOUS for: pin-suffix, nfd, line-numbers)
- b1.finding_kind: abs-path-under-root + extra-whitespace (VACUOUS: pin, nfd, line-numbers)
- b1.finding_sev: abs-path-under-root + extra-whitespace (VACUOUS: pin, nfd, line-numbers)
- b2.hit_role: abs-path-under-root + extra-whitespace (VACUOUS: pin, nfd, line-numbers)
- d1.bug_echo_scores: nfd-vs-nfc ONLY (the variant's é is e+U+0301) (VACUOUS: abs-path — the type has no path key, pin, line-numbers)
- v1.finding_class: abs-path-under-root + pin-suffix (`pc-j1-1--330803c`) + extra-whitespace + case-fold of disposition (VACUOUS: nfd, line-numbers)
- wf.drift: extra-whitespace ONLY (VACUOUS: abs-path — no path key, pin, nfd, line-numbers)
SOLID: of the five re-landing classes the brief names, line-numbers is exercised by NO fixture (every type), nfd by exactly one (d1), pin by exactly one (v1); abs-path by six (wf.drift has no path key), extra-whitespace by all seven. A re-landing claim over line-number variants is VACUOUS for all seven types — no test would go red if line-number stripping (a contract AC 3 claim: "strip line numbers") were deleted. The mechanism itself: normalize does NOT strip line numbers from values at all (measured: `line 42:` passes through) — it only refuses line numbers as KEYS. See grading C-V1.

## ITEM 3 — normalize shapes (reproduced; out23.txt; all pasted values are the measured outputs)

paths (root=/home/rocco/agent-factory, key=b1.finding_sev.file):
- abs under root → 'src/x.py' · abs of root itself → '.' · root with trailing slash → 'src/x.py' (root normpath'd, works) · abs OUTSIDE root → REFUSED `decision-state-abs-path: file` · `~/x.py` → REFUSED (abs-path; ~ is never expanded — a home-relative path is refused, not resolved; the contract is silent on ~ — INFO) · `..` / `../x` / `a/../b` → REFUSED (path-traversal guard, V:113) · `./src/x.py` → `./src/x.py` UNCHANGED · `src//x.py` → unchanged · `src/x.py/` → unchanged · `src/./x.py` → unchanged (C-F4 confirmed: relative-path shapes are not canonicalized; each hashes differently from 'src/x.py') · relative root with a relative path → 'src/x.py' (works, no crash)

whitespace (msg, all collapse to one space + strip): tab · newline · \r · \r\n · NBSP U+00A0 · U+2028 · vtab · ff — all → 'a b' (python re \s covers all). ZERO-WIDTH SPACE U+200B is NOT \s → PASSES THROUGH UNCHANGED (a secret split with U+200B instead of a space-run would evade the order discriminator — but the token rule requires its own separator; a zero-width-split 'token\u200b<run>' does not match either way; INFO, not material: no class matches a zero-width-split form).

NFC: é-NFD and é-NFC hash IDENTICAL (digest equality measured True); Hangul syllable NFC vs jamo NFD hash IDENTICAL (True). normalize outputs NFC (measured: NFD input → 'é-gate' precomposed). SOLID.

truncation (the cut is on python str = code points, AFTER nfc+collapse): exactly 400 → 400; 401 → 400 (both 'a' and 'b' — the char boundary is exact); a 401-char combining sequence on msg (limit 200) → 200; a 400-char string ending in a combining mark → 200 (the cut can split a base+combiner pair: 'e\u0301'*300+'z' (601 chars) → 200 chars, NFC-stable True — the cut at an odd position leaves a base without its combiner but the string stays NFC-valid; no crash, no surrogate). SOLID (the cut is a char boundary, never a UTF-16/byte split).

strip_pin (v1.lane): `--330803c` (7hex) stripped · `--330803CA` (7 uppercase hex) stripped · 40hex stripped · 41hex NOT stripped (the 7..40 range is exact) · `a--b--330803c` → `a--b` (only the FINAL `--<hex>` is stripped; a literal earlier `--` is preserved, V:87) · `--zzzzzzz` (non-hex) preserved · trailing `--` after the suffix: 'lane--330803c--' → unchanged (the $ anchor + trailing dash means no match — a lane name ending in a second `--` after a PIN keeps it; a real lane name never ends that way; INFO) · 'x--fffffffG' (8th char non-hex) preserved. SOLID (the pin strip is exact per the test T:233-252).

target (action_target, kind=target): '/usr/bin/python3 -m pytest' → REFUSED `decision-state-abs-path: action_target` (C-F7 confirmed: an absolute INTERPRETER binary is refused — the leading token is path-processed, and an interpreter is outside the repo root) · 'sudo x' → 'sudo' · '' → '' · '   ' → '' (whitespace collapses first, then the leading token) · '  python3   scripts/x.py  ' → 'python3' · '/home/rocco/agent-factory/scripts/check.py --x' (abs under root) → 'scripts/check.py' (relativized, leading token) · '~/bin/tool arg' → REFUSED.

non-string values (C-F5): msg=5 → '5' · msg={'a':1} → Python repr "{'a': 1}" · msg=1.5 → '1.5' · msg=None → 'None' (a JSON null becomes the literal string "None" — it collides with a real string "None": digests equal, measured) · msg=True → 'True' · file=5 → '5' · paths='str' or paths=tuple → REFUSED `decision-state-bad-type: paths` (the list check is real) · a non-str ITEM inside a list is str()-coerced ('1'). No type refusal for string keys — the value types are NOT closed (C-F5 confirmed).
