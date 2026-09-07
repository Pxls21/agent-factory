# Lane D5i — S0-01 scripted backend, round 12: the precheck only on byte-view sinks, the invisible-separator CLASS closed by category, the record wiring pinned (sandbox Opus 4.6 `code-implementer`)

**PIN:** the HEAD this brief is committed in (the lane's work lands in the CHILD commit — say so in the report; the
D5h report cited the brief commit as the PIN, which checks out the parent implementation).
**Verdict graded:** `tasks/briefs/s0-01-d5i-support/verify-D5h.md` (VERIFY-D5h, round 11 on checkpoint 8o —
NOT-READY: D5h-F1/F2/F3 blocking; F4-F15 real; read it whole first: every finding carries a live repro, a paired
negative control and the exact red test).
**Scope (exactly three files + your report):** `proofs/S0-01/tools/scripted_backend.py` ·
`tests/test_s0_01_scripted_backend.py` · `tests/red/test_s0_01_backend_credential_screen.py`; report
`tasks/briefs/s0-01-d5i-support/D5i-report.md`. Other lanes hold uncommitted edits in this tree (tee) — never
`git stash/checkout/restore/reset/add/commit/push`; mutants on scratchpad COPIES only (the verifiers' harnesses are
under the session scratchpad `vd10/` and `vd11/`); kill only the backends you start; no outward actions. Bytes and
code points are written here as `0xNN` / `U+NNNN` — build them in code, never paste raw.

## Design (pinned by the coordinator — build it, do not redesign it)
1. **D5h-F1 — the precheck is a BYTE-VIEW test and runs only on byte-view sinks.** `_carries_secret(s, *,
   byte_view)`: `True` from header names, header values, path, query and the raw body (strings `http.server` hands
   over as a latin-1 view of wire bytes) — there the invalid-UTF-8 precheck stays and fails closed exactly as in 8o;
   `False` from the parsed-JSON leaf walk (`_iter_json_strings`) — those strings are already decoded and re-encoding
   them manufactures bytes that were never on the wire. Restate the function docstring accordingly (its premise
   "no legitimate producer" is true only for byte-view sinks — D5h-F13). Red test: the verifier's
   `test_ordinary_latin1_text_in_json_body_is_served` over `café / Müller / señor / £100 / 50°C / © 2026` (200 +
   record verbatim) — RED today.
2. **The lenient re-decode joins the CLOSURE as a DETECTION op (never as acceptance).** Add
   `utf8_redecode_lenient` (`encode("latin-1").decode("utf-8", errors="ignore")`, `except UnicodeEncodeError: return x`)
   to the implementation's ops so a decoded JSON leaf carrying latin-1 junk between the token halves (the D5g JSON
   twins `U+00C0 U+00A0` and `U+00E2 U+0080 U+0080 U+0080`, which item 1 takes away from the precheck) is still
   found through its form set. This is not the rejected "lenient instead of refuse": the precheck still REFUSES invalid
   wire bytes on byte-view sinks; the lenient op only widens what the closure can find. Legitimate text cannot false-
   positive through it (a form must EQUAL the token). The D5h JSON-twin tests must stay green — they become the
   killers for LENIENT-DEL-IMPL.
3. **D5h-F2 — the invisible-separator class closed by CATEGORY, not by list.** New op `strip_invis`, in the closure
   AND the oracle: drop every code point whose `unicodedata.category` is in {Cf, Cs, Cc, Mn, Me, Zs, Zl, Zp} plus the
   explicit fillers `_INVISIBLE_EXTRA = {U+115F, U+1160, U+3164, U+FFA0, U+2800, U+180E}` (Lo/So fillers and the
   Mongolian vowel separator). Keep `strip_zwc`/`strip_ctl`/`strip_ws` (they are now subsets; say so in the docstring
   and keep their named vectors so each op still dies alone — if an op becomes fully redundant, REMOVE it from both
   closure and oracle rather than keep an unpinnable member, and state which). Red tests: the verifier's
   `test_credential_invisible_separator_in_header_returns_400` over ZWNJ U+200C, ZWJ U+200D, LRM U+200E, RLM U+200F,
   BRAILLE BLANK U+2800, HANGUL FILLER U+3164, VS1 U+FE00, MVS U+180E (400 + MARKER + close), the JSON-escape twin
   (including the lone surrogate `\ud800` escape and a combining mark U+0301 split), and oracle vectors
   `zwnj_split`, `lrm_split`, `braille_split`, `hangul_filler_split`, `vs1_split`, `combining_split`, each red when
   `strip_invis` alone is dropped from the oracle (`O_INVIS`). Document the class boundary in the module docstring:
   confusable SUBSTITUTION (homoglyphs) is out of contract — the token's bytes are then not in the record.
4. **D5h-F3 — the record wiring pinned.** The verifier's `test_record_does_not_mutate_the_caller_body` (calls
   `State.record` directly; asserts the caller body unmutated); mutant `JSONSAFE_INLINE_IN_RECORD` must die on it.
5. **D5h-F4 — the C1 arm pinned by its WIRE form** (`test_credential_c1_control_wire_form_returns_400` over U+0080,
   U+0085, U+009F as UTF-8 bytes — valid UTF-8, so only `strip_ctl`/`strip_invis` catch it; mutant `CTL_PARTIAL_noC1`
   must die). **D5h-F5 — refuse ≠ repair:** `test_invalid_utf8_without_the_token_is_refused_not_repaired` (invalid
   wire bytes, no credential anywhere → 400 + MARKER; mutant `LENIENT_IN_IMPL` — precheck deleted — must die on it).
   **D5h-F11 — record-count deltas** (`n0 = len(_records(...))` before, `== n0 + 1` after) in the four tests that read
   `[-1]` without one; mutant `RECORDLESS_400_HDR` must die. **D5h-F12** — the O2 qualifier in the oracle docstring.
   **D5h-F14** — pin the precheck-before-closure ordering with a monkeypatch counter (`_normal_forms` not entered for an
   invalid-UTF-8 byte-view input), timing-free.
6. **Report discipline (D5h-F6/F7/F8/F9/F10 — the D5h report failed all five):** every `file:line` re-derived with
   `grep -n` on the FINAL tree (cite the decorator line for a parametrized test); PIN wording per the header above;
   the cost table with THREE columns (ordinary · invalid-UTF-8 fail-closed · bound-exceeded fail-closed at 1 KB /
   10 KB / 100 KB / 1000 KB) with the load average and the vector each column uses; red-before lines PASTED from the
   parent run (a missing attribute on the parent is an `AttributeError`, not an `AssertionError` — say what happened);
   each mutant row names the mutated line and the killer that actually fired.

## Mutants (scratchpad copies; `git status --porcelain` clean on the three files after each; paste the table)
The verifier's 31 rows (its items 5a/5b, including NOOP) re-run on the final tree, every survivor now KILLED by a NAMED
test: `JSONSAFE_INLINE_IN_RECORD`, `CTL_PARTIAL_noC1`, `LENIENT_IN_IMPL`, `RECORDLESS_400_HDR`;
`PRECHECK_AFTER_CLOSURE` becomes KILLED by the F14 counter test; plus new: `PRECHECK_ON_LEAVES` (byte_view forced
True on the leaf walk — killed by the café test), `INVIS_DEL` (drop `strip_invis` from the impl), `O_INVIS` (drop it
from the oracle), `INVIS_LIST_ONLY` (replace the category test with the eight named code points — killed by a
vector outside the list, e.g. U+2061 or U+E0020), `LENIENT_DEL_IMPL` (drop the lenient op from the closure — killed
by the D5g JSON twins). `O2_UQ` may stay "equivalent for a token containing no `+`" with the qualifier in-tree.

## Gates (paste verbatim)
`bash scripts/test_summary.sh tests/test_s0_01_scripted_backend.py tests/red/test_s0_01_backend_credential_screen.py`
twice · red standalone · pyflakes on the three files · `python3 scripts/lint_delta.py --base
origin/claude/soundbox-kit-migration-iz1jwf` · the 7 sinks × {6 invalid-UTF-8/control separators + 8 invisible
separators} matrix, every cell `400/MARKER/yes/yes` or the parser's `400/no_rec` with the mechanism named · the
legitimate-traffic table (CJK, emoji, decomposed and PRECOMPOSED Latin-1 text, percent-encoded non-ASCII in path and
query, a valid-UTF-8 header value) all 200 + verbatim · the live normal-traffic + streaming control after ≥ 50
redactions · `Connection: close` on every 4xx. PC leg: NOT run here (coordinator's). Report shape: FILE IDENTITY
(sha256 + lines), DONE table, MUTANT table, PROBE tables, NOT_DONE, DISCREPANCIES, SELF-ATTACK.
