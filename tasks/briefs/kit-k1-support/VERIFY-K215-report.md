# VERIFY-K215 report (task #219: verifies K215 = task #215, and the anti-hollow-green bake = task #218)

> **COORDINATOR HARVEST NOTE (2026-09-24 07:5xZ).** Graded MERGE-READY-WITH-FOLLOWUPS: K215 (task #215) and the anti-hollow-green bake (task #218) are VERIFIED. Served model: `claude-opus-5-5` on 385 of 385 replies, no refusal stop. The coordinator reproduced the gate at 9e6821b in a private clone (`226 passed in 149.07s`, set 2a60fb528bf2), F-3's M16 (11 hits drop to 6 over `scripts/`, `harness-ports/`, `proofs/`, `src/` and `.github/`; the test file still reads `170 passed`), F-2 (by reading) and F-7, which is wider than reported: through a quoted heredoc the Bash tool also turned a typed backslash-u-0041 into `A`. F-6 is fixed in the harvest commit. The other follow-ups go to issue #65.

LANE: VERIFY-K215 (sandbox, adversarial-verifier, Opus 5.5). PIN: bfe66ec. Started 2026-09-24T06:50:16Z (date -u).
Shared tree: /home/user/agent-factory, read-only apart from this report. Scratch: /tmp/vk215/.

STATUS: DONE (07:4xZ). Every item ran fully; the recommendation is MERGE-READY-WITH-FOLLOWUPS (section PREDICATE AND RECOMMENDATION).

## 1. PREMISE — RAN FULLY

06:50:44Z-06:53:47Z, shared tree at HEAD 211dd03. The 19 command lines were extracted verbatim from the brief's block
(`sed -n '122,241p' … | grep '^\$ '`) and run as `bash scripts/premise_block.sh < /tmp/vk215/premise_cmds.txt` (rc 0). The output
was diffed against the brief's block lines 124-240: `diff /tmp/vk215/premise_brief.txt /tmp/vk215/premise_out.txt` -> no output,
`diff rc=0`. Every line is identical, including `226 passed`, `2 files set=2a60fb528bf2`, `boundary-identical-to-pin`, the blob ids,
the 20 self-screen hits, the 385-hit sweep and its per-row counts, `11` `task #215` rows, and the 3e/3f/(g) anchors.

Commits after the PIN (`git log --oneline bfe66ec..HEAD`): 4e73e3c (transcripts), 211dd03 (this brief), 7e09777 (ledger and wiki),
3bcd7bc (registry: the AF-AP-132 row now names the Edit/Write tools as a second source of the literal separator). Files changed since
the PIN: `docs/INCIDENT-LOG.md`, this brief, `todo/BUILD-TASKLIST.md`, a transcript digest, `wiki/topics/live-state.md`. None is in
the K215 code boundary. The registry rows are read at the PIN (`git show bfe66ec:docs/INCIDENT-LOG.md`) as the brief directs; the
post-PIN AF-AP-132 edit is noted where it matters (item 8).

## 2. SCREEN ROWS — RAN FULLY (per row: (i) registry instances, (ii) new near misses, (iii) fire count at the PIN)

Instruments. The pack (`scripts/lane_context.sh … -o /tmp/vk215/pack.md`, 06:55Z, 262 lines) leaves the hook UNMAPPED: `graft ask`
answered `nothing indexed under ".claude/hooks/"`, `graft skeleton` answered `no definitions indexed for this file`, and GitNexus
`impact main` answered `"risk": "UNKNOWN"`. The consumer and instance sweeps below are therefore literal-token searches (`git grep`,
`grep`), the named fallback. Near-miss harness: `/tmp/vk215/probe.py` loads the PIN's hook from the private clone and numbers a hit the
way `scripts/ap_screen.py:61` does (`text.count("\n", 0, m.start()) + 1`); the shapes are `/tmp/vk215/rows/r*.py`. Registry
instances were taken from history with `git show <fix>^:<path>` into `/tmp/vk215/inst/` and run through the PIN's
`scripts/ap_screen.py` (the real whole-file consumer).

(iii) The sweep at the PIN (`python3 scripts/ap_screen.py --limit 100000 $(git ls-files scripts src proofs harness-ports .claude/hooks)`
in the clone, 22.1 s, saved as `/tmp/vk215/sweep_pin.txt`) prints `--- AP_SCREEN over 960 path(s): 385 hits over 960 files ---` and
the per-row counts 132:13, 141:5, 145:7, 152:1, 175:12, 177:4, 139:1, 144:0, 149:0 — each equal to the builder's section 7.

### 2.1 AF-AP-132
(i) Fires on each named instance: `scripts/no_laya_in_gates.py:1443` (`content.splitlines`) and `scripts/vendored_manifest.py:759` (`path.read_text`)/`:798` (sweep); the two
tools the registry says were FIXED, taken at `ea18960^`: `report_lint.pre.py:77` (`for lineno, line in enumerate(report.read_text(errors="replace").splitlines(), 1):`)
and `ap_screen.pre.py:50` (`lines = text.splitlines()`, enumerated with a start six lines later) both HIT; the fixes at `ea18960` give 0.
The `ledger.py` literal-separator text never reached this branch (a byte sweep of every `src/agent_factory/decisions/ledger.py`
revision: 0 separator lines), so its shape was built in code (`chr(0x2028)`): fires. The report_lint `:55`/`:59` sites (a returned
list indexed later) are the indexed-list shape D-4 declares unscreened.
(ii) Missed, inside the registry's class: `enumerate(text.splitlines(keepends=True), 1)` and `enumerate(text.splitlines(True), 1)`
(the pattern needs the empty parentheses `\.splitlines\(\)`); an annotated list (`lines: list[str] = text.splitlines()`) or an attribute
list (`self.lines = …`) enumerated with a start; a list enumerated 0-based and printed as `i + 1`; a start more than 15 lines below;
`zip(itertools.count(1), text.splitlines())`; a separator on a line that also holds a real U+FFFD. No live site uses a missed
spelling: the only `keepends` sites (`harness-ports/bin/lane-profile.sh:162` and three in tests) edit or search text and report no
line number. Quiet, correctly, on six clean shapes (the `"\n"` split, a count, a set, the escape written as text, a prefix-named list).
(iii) 13 hits, all real line-numbering sites; I read each one's use of the number and agree with the builder's classification.

### 2.2 AF-AP-141
(i) Fires on `scripts/check-proof-status.py:164` (`returncode`) and `scripts/ci_gate.py:213` (`commit`) (sweep) and on the pre-fix `ci_gate.py` at
`5689d9f^:74` (`["git", "-C", args.root, "merge-base", "--is-ancestor", sha, args.origin_ref]`); quiet on the fix `5689d9f:207`
(`rc, _, err = _git(…)`) and on the two prose lines in that file.
(ii) Missed: a shell git held in a variable (`$GIT merge-base --is-ancestor "$a" "$b" 2>/dev/null`; branch B needs the word `git`).
Fires on three FIXED forms (false hits): `(rc, _, err) = _git(…)` in parentheses; `rc, out, err = _git(` with the argv on the next
line; a kept `CompletedProcess` whose `.stderr` is read on the next line. Fires, correctly, on a multi-line argv, a flag held in a
name, `rc, _, _ =` (error discarded) and both shell spellings.
(iii) 5 hits on 4 lines, as the builder classified. `scripts/no_laya_in_gates.py:1311` (`file`) and `scripts/pc_suite.sh:67` (`PC_AF_REPO`) are
real, unlisted shapes of the class.

### 2.3 AF-AP-144 (path attacks under item 3)
(i) The registry's instances: the S0-02 instance was S0-02 calling S0-01's reader (fixed by B9-R1); the earlier one,
`proofs/S0-01/tools/build_capture_record.py`, is not a `proofs/*/check_*.py` path, so it is outside the signature's scope. The WATCH
sites `proofs/S0-12/check_pin_diff.py:33` (`yaml.safe_load`) and the S0-07 reads fire through `for_path`. The WATCH sites S0-09 and S0-10
(`proofs/S0-09/check_conformance.py:11` and `proofs/S0-10/check_conformance.py:10`, `with open(path) as f:`, no handler) are
NOT seen: `open(` is not one of the signature's four calls. The builder declared this (its section 7 and NOT-done).
(ii) Through `for_path("proofs/S0-09/check_x.py")`: missed `json.load(fh)`, `open(p).read()`, `yaml.load(t, Loader=…)` and
`str(raw, 'utf-8')` (none is one of the four calls), and `p.read_text(errors='strict')` / `p.read_text(encoding=None)` (default-encoding
reads the `\.read_text\(\)` pattern does not match); fires on `raw.decode('utf-8', 'replace')`, which cannot raise.
(iii) 0 through `ap_screen.py` by design (the path-less callers get `None`); see item 3.

### 2.4 AF-AP-145 (the class is also item 3)
(i) Fires on every named instance, through `ap_screen.py`: the S0-05 runner at `97b589a^` (`:322 cleanup() {`, `:335 trap 'exit 130' INT`,
`:336 trap 'exit 143' TERM`); the matrix runner at `0c05970^` (`:94`, `:138`, `:139`); the WATCH runners
`proofs/S0-03/tools/pc/run_s0_03_legs.sh:83` (`stop_all`), `proofs/S0-06/tools/pc/run_s0_06_legs.sh:59` (`cleanup`), `proofs/S0-08/tools/pc/run_containment.sh:91` (`cleanup`);
the WATCH `spikes/selective-egress/probe.sh:26` (`cleanup`) (outside the five roots). Quiet on both fixes (`97b589a`, `0c05970`: 0 hits).
(ii) Missed, each inside the registry's signature (`trap <fn> EXIT` whose function, OR whose INT/TERM handler, does not open with the
ignore): `function cleanup {` (no parentheses); `cleanup()` with the brace on the next line; `trap 'cleanup; restore' EXIT`;
`trap -- 'cleanup' EXIT` and `trap -- cleanup EXIT`; `trap 'cleanup "$tmp"' EXIT`; `trap cleanup 0`; `set -e; trap cleanup EXIT`;
an UNQUOTED INT/TERM handler function with no ignore (`trap on_term INT TERM`, `on_term() { exit 143; }`: `_HANDLER` reads quoted
strings only and `_BODY` checks only EXIT-trapped names); a multi-line handler string. Fires on seven CORRECT forms: `trap '' HUP INT TERM`,
`trap '' SIGINT SIGTERM`, `trap '' 2 15`, `trap '' INT; trap '' TERM`, `local -r rc=$?` first, `rc="$?"` first, and a quoted
handler `trap 'on_term' TERM` whose function opens with the ignore. Correct on: `cleanup () {`, `function cleanup() {`, the ignore
after another command (fires), a comment line before the ignore (quiet), both quote styles of the fixed handler, `trap - INT TERM`.
Live-site check over the 96 first-party shell files: no `function name {`, no brace-on-next-line function, no `trap --`, no numeric
EXIT, no unquoted INT/TERM handler function; every live ignore is spelled `trap '' INT TERM` or `trap "" INT TERM`. So no live
instance is missed and no live correct form is flagged beyond the builder's list.
(iii) 7 hits, as the builder classified (three KNOWN WATCH runners, `harness-ports/bin/pc-lane.sh:127` (`stop_session`) the registry's OK, three
harness-ports/tests fixtures). D-10 reproduced: `:127` is `trap 'stop_session; cleanup; trap - EXIT; exit 143' TERM INT`, a handler
string that does not open with the ignore; the registry's OK rests on re-entry, which a line screen cannot see. Its `cleanup` at
`harness-ports/bin/pc-lane.sh:112` (`cleanup`) is a one-line body, which the row does not read (declared).

### 2.5 AF-AP-149
(i) Fires on both named redactors: `scripts/transcript_export.py` at `9932f34^:27` and the J1-1 redactor `src/agent_factory/decisions/volatile.py`
at `01ca7d5:57`; quiet on both fixes (`9932f34:29`, and the PIN's `volatile.py:149`).
(ii) Missed, each a one-label rule inside the registry's signature: `-----BEGIN\s+[A-Z ]*PRIVATE KEY-----…` (the row needs a literal
space after BEGIN); `-----BEGIN[ A-Z]*PRIVATE KEY-----…`; dashes written `-{5}`; a label alternation with no class
(`-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----`: the row's is-a-regex lookahead wants `.*`, `.+`, `[\s\S]`, `[A-Z` or `[^`);
a two-line rule whose END line has no `\Z`; a lower-case rule under `re.I`. Fires on a fixed rule that ends at `-----END …|$` (a `$`
end-of-text alternative is not recognised). Quiet, correctly, on a literal PGP armor fixture and on prose.
(iii) 0 hits at the PIN, as the builder said: both instances are fixed.

### 2.6 AF-AP-152
(i) Fires on the J1-1 `_ENVVAL` at `01ca7d5:53`. The second instance (task #187's unanchored widening) was caught at design and never
committed; its shape fires (the builder's fixture). The third (`scripts/no_laya_in_gates.py` `arith()`) is a hand-written scanner,
declared out of reach.
(ii) Missed, each measured super-linear on this sandbox (`/tmp/vk215/rows/r152_cost2.py`, `r152_cost.py`, 20 s cap per run):
the registry's own group with a CAPTURING paren `(?P<name>([A-Z][A-Z0-9_]*_)*(?:KEY|TOKEN))=\S+` (0.0079 s, 0.1223 s, 2.0550 s at 16,
20, 24 repeats of `A_`); a named group `(?P<p>[A-Z][A-Z0-9_]*_)*KEY=\S+` (0.0076, 0.1202, 1.9194 s); the classic `^(?:[a-z]+)*$`
(0.0021, 0.0336, 0.5369 s); `(?:[A-Z]+_?)*KEY` (0.0056, 0.0902, 1.5042 s); an unanchored class-star-literal as the FIRST alternative
`(?:[A-Za-z0-9]*[_-]key|api[_-]?key)` (1.6083, 2.5611, 3.5549 s at 16k, 20k, 24k characters: quadratic); a whole pattern
`[A-Za-z0-9]*_key` (0.3264, 0.5108, 0.8146 s). Fires on `{0,}` and a lazy `*?` outer quantifier; quiet, correctly, on a required
separator the class excludes, a possessive `*+`, an atomic group and a fixed-width body. Live-site check (`git grep -P` for
capturing, named and bare nested quantified groups over first-party Python): the five candidates (`.claude/hooks/edit-snapshot.py:101`,
`:108`, `:237`, `.claude/hooks/graft-first-nag.py:40`, `scripts/decide-harvest:41` (`KIND_RE`)) each need a disjoint separator per repeat, so
they stay linear. No live super-linear regex is missed.
(iii) 1 hit, `src/agent_factory/decisions/volatile.py:137` (`exponentially`), a comment quoting the old pattern: FALSE, as the builder said.

### 2.7 AF-AP-175
(i) Fires on both reads of the pre-R1 harvester (`0d62801^:141` `"HEAD")` and `:152` `f"HEAD:{path}"`) and on R1's single resolve
(`0d62801:145` `"HEAD^{commit}"`): the line form cannot tell one read from two, which the message and D-2 say.
(ii) Missed: every UNQUOTED `HEAD` — a shell `git ls-tree -r --name-only HEAD`, `git show HEAD:"$f"`, a Python `shell=True` string
`f"git show HEAD:{p}"`; a branch name (the registry says "or a branch name"). Fires on an HTTP method string `conn.request("HEAD", "/health")`
(a false hit; none at the PIN). Live count: 26 unquoted `HEAD` reads in git calls across the first-party shell files of the five roots
(`grep … | grep -v "['\"]HEAD"`), e.g. `scripts/push_clean.sh:14`, `:30`, `:109`, `:122`, `:123` in one process; none is a known
mixed-snapshot defect. The contract's fallback reads "a `HEAD` literal passed to a git call"; D-2 narrowed it to "every quoted `HEAD`
literal" and said so. Graded under D-2 below.
(iii) 12 hits, as the builder classified; `scripts/stamp_check.py:43` (`exists`) is a docstring (FALSE).

### 2.8 AF-AP-177
(i) Fires on `scripts/decide-harvest:686` (`isinstance`) and the variable-held form (reported at its binding line `scripts/decide-harvest:689` (`subagent_type`), the
registry cites `:691`: D-9), both at `0d62801` and `0d62801^`, and on `harness-ports/bin/qwen_matrix.py:263` (`message.get`).
(ii) Missed: a `frozenset({…})` membership; a `.get` with a nested call inside (`rec.get(key.lower()) in {…}`); a walrus
(`(role := inputs.get("t")) in {…}`); an annotated binding (`role: str | None = inputs.get(…)`); a test 9+ lines below the binding;
an `isinstance(other, str)` on ANOTHER name on the same line (it excuses the line). Fires on `os.environ.get("CI") in {"1", "true"}`
(an env value is always `str`: false hit) and on `isinstance(v, (str, int)) and v in {…}` (guarded: false hit). No live site uses a
missed spelling (four targeted greps over first-party Python: 0 each).
(iii) 4 hits, as the builder classified; `harness-ports/bin/lane-done-gate.py:148` (`payload.get`) is real (tested with `in {` two lines below).

## 4. F-06 (AF-AP-139 widened) — RAN FULLY
The PIN's row against the pre-K215 row (`git show 942ad5e:.claude/hooks/edit-snapshot.py`), `/tmp/vk215/rows/r139.py`:
`-> None` handler: OLD quiet, NEW fires; `HTTPStatus.OK`: OLD quiet, NEW fires; always-401 handler: quiet on both. Also fires on
`http.HTTPStatus.NO_CONTENT` (NEW only). Spellings inside the registry's scope ("the same 2xx for every path") the widening still
misses: `send_response(HTTPStatus.OK.value)`, `send_response(int(HTTPStatus.OK))`, `send_response(code=200)`,
`send_response(HTTPStatus(200))`, and `def do_GET(self) -> 'None':`. Both rows (old and new) also fire on two handlers that DO branch on
the path, `match self.path:` and `handler = ROUTES.get(self.path)`: pre-existing false hits, not introduced by K215. TEST_SCREEN over
`git ls-files tests harness-ports/tests`: 6 hits with the old row, 8 with the PIN's; the two added are the builder's own fixtures
(`tests/test_edit_snapshot_ap_screen.py:543` (`self.send_response`), `:547`). D-8's list (the message argument, delegation, an alias, `send_response_only`,
bodies over 1,000 characters) is recorded in `tasks/briefs/kit-k1-support/K215-report.md` D-8: confirmed, not graded.

## 3. THE TWO NEW CLASSES — RAN FULLY

### 3.1 `_PathScoped` (AF-AP-144)
Commit time, measured in the private clone (commits and staging allowed there): staged `proofs/S0-99/check_only144.py`, whose only body
line is `return json.loads(p.read_text())`, plus two other probe files, and ran the pre-commit screen as `scripts/hooks/pre-commit:16` (`lint_delta.py`) runs it
(`/root/venv-agent-factory/bin/python scripts/lint_delta.py --staged`): AF-AP-144 printed NOTHING, while AF-AP-145 fired on another staged
file in the same run (the instrument ran). A first staged file holding one instance of every new row gave AF-AP-139, -132, -141, -149,
-152, -175 and -177 at commit time, and no AF-AP-144. Mechanism (read, `scripts/lint_delta.py:145-146` (`screen`)): `for ap_id, rx, msg in screen: if
rx.search(added)` and `_PathScoped.search` returns `None` unconditionally. So AF-AP-144 can NEVER fire at commit time, nor in any
`scripts/ap_screen.py` sweep (`finditer` returns an empty iterator), which is the registry's bug-echo instrument.
Grade: the contract's s144 line says "If only a path-scoped line pattern is possible, scope it and say so"; the builder scoped it and
said so (D-3(b), and `tests/test_edit_snapshot_ap_screen.py:702` `test_the_path_less_callers_see_nothing` pins it). `scripts/lint_delta.py`
and `scripts/ap_screen.py` were READ-ONLY in K215's boundary, so passing the path there was out of reach, and returning the unscoped
match to path-less callers would flood (105 matches in 13 checker files alone). An acceptable, documented limit; the consumers owe a
follow-up (F-2 below).
Path shapes through the REAL `main` (the hook run as a process on an Edit payload, `/tmp/vk215/rows/r144_paths.sh`, each file on disk):
FIRES on an absolute worktree path, a relative `proofs/S0-02/check_pins.py` with cwd at the root (the Codex adapter's shape:
`harness-ports/bin/codex-hook-adapter.py` passes the patch header path and runs the hook with `cwd=str(root)`), `./proofs/…`, a path
through `scripts/../proofs/…`, a scratch copy whose directory name holds a space, and the real `proofs/S0-02/check_buzz_authz.py` in
the clone. QUIET on nested `proofs/S0-02/tools/check_y.py` and `proofs/S0-02/tools/pc/check_z.py` (outside the registry's
`proofs/*/check_*.py` glob, correct), `proofs/check_top.py` (no proof directory, correct), any path holding `/tests/` (main's TEST_SCREEN
branch runs first: a scratch copy under a directory named `tests` loses the row) and any path holding `sandbox-kit/` (main returns first).

### 3.2 `_ExitTrapCleanup` (AF-AP-145)
Cost (`/tmp/vk215/cost.py`, each case in its own process, 60 s cap): 50,000 trapped definitions with no ignore, 1,827,780 characters,
50,000 hits in 0.1379 s; 50,000 trap lines FIRST, then the 50,000 definitions: 50,000 hits in 0.1370 s (the trap-above-function claim
holds); one definition followed by 100,000 comment lines: 0.0696 s; a 100,000-character trap line with no INT/TERM: 0.0212 s; an
unclosed quote on a 100,000-character line: 0.0107 s; 50,000 handler lines: 0.0725 s; a 100,000-character function name: 0.0013 s.
LINEAR, as the builder claimed. Correctness: section 2.4 (nine missed spellings inside the signature, seven correct forms flagged,
none of either at a live site).

### 3.3 Every consumer of AP_SCREEN / TEST_SCREEN, and the methods it calls on a row
Loaders of the hook (`git grep -n -E 'edit.snapshot'` over `*.py *.sh scripts/hooks/*`): the hook's own `main`; `scripts/ap_screen.py:26` (`importlib.util.spec_from_file_location`);
`scripts/lint_delta.py:106` (`importlib.util.spec_from_file_location`); `sandbox-kit/reference-scripts/lint_delta.py:100` (`edit_snapshot`) (a vendored copy, same loop); `tests/test_edit_snapshot_ap_screen.py:15` (`edit_snapshot`);
`tests/test_s0_01_frame_tee.py:40` (`_ilu.spec_from_file_location`); `tests/test_ap_screen.py` through `ap_screen._load_screens()`. The harness adapters
(`.claude/settings.json:46`, `harness-ports/bin/codex-hook-adapter.py`, `harness-ports/bin/hermes-hook-adapter.py`) run the hook as a process.
Methods called on a row object: `search` (hook `main` for both lists, `scripts/lint_delta.py:146`, the vendored copy), `finditer` with a
`search` fallback (`scripts/ap_screen.py:54-57`), `for_path` (hook `main` only, behind `isinstance(rx, _PathScoped)`), and `findall` at
`tests/test_s0_01_frame_tee.py:3060` (`findall`), guarded by `if ap_id == "AF-AP-59"`. `_PathScoped` implements `search`/`finditer`/`for_path`;
`_ExitTrapCleanup` implements `search`/`finditer`; neither implements `findall`, `match` or `pattern` (probed: `findall` on the AF-AP-145
row raises `AttributeError("'_ExitTrapCleanup' object has no attribute 'findall'")`). So every consumer at the PIN calls only implemented
methods; the frame_tee guard is load-bearing (`tests/test_s0_01_frame_tee.py -k test_grandchild_cleanup_is_own_pid_scoped`: `1 passed`).
The pre-existing `_EmitNoneKwarg` (AP-59) already had this shape (`search` only), so the hazard is not new.

### 3.4 The literal separator at edit time and commit time (bears on AF-AP-132 and TEST_SCREEN)
Through the real hook `main`: a hunk `BAD = 'a<U+2028>b'` on `scripts/only132c.py` FIRES AF-AP-132; the same hunk on
`tests/test_vk215_sep.py` prints nothing (TEST_SCREEN holds no AF-AP-132 row). At commit time the branch is dead for every file:
`scripts/lint_delta.py:99` splits the diff with `splitlines()`, and the text it screens for the staged `scripts/only132c.py` is
`["BAD = 'a"]` (`separator-in-screened-text: False`). Three tracked TEST files hold literal separators at the PIN:
`tests/test_ap_screen.py:89` (`write_text`), `tests/test_decide_harvest.py:777` (`uncommitted`) (six lines through `:862`) and `tests/test_report_lint.py:118` (`gamma_delta`), all
deliberate fixtures of separator handling. The builder's "No class lives in tests" came from a sweep of the five roots, which do not
include `tests/`. The brief's clause ("Put a row in TEST_SCREEN too only when the class lives in tests") permits the row but does not
require it, and the three sites are deliberate: FOLLOW-UP (F-5 below), not a blocker.

## 5. F-03 (AF-AP-138, `assert_mutant_killed`) — RAN FULLY
Body identity: the statement bodies extracted by AST from `git show 942ad5e:tests/test_vendored_manifest.py`
(`test_required_mutants_are_killed`, lines 1279-1302, 24 lines) and `git show bfe66ec:…` (`assert_mutant_killed` without its
docstring, lines 1278-1301, 24 lines) differ on two lines only, `run_killer(killer, load_module(), baseline, mutant_name)` and
`run_killer(killer, mutant, mutated_work, mutant_name)` → `run(…)`; after replacing `run_killer(` with `run(` the diff is EMPTY.
At the PIN (private clone): `-k 'test_required_mutants_are_killed or test_af_ap_138'` → `12 passed, 44 deselected in 28.80s`,
all eleven mutant rows PASSED (every required mutant killed) and the control PASSED.
My own hollow killers, in scratch copies of the test file inside the clone (`tests/test_vk215_hollowA.py`, `…B.py`, removed after):
- A: the real `test_exclusions_do_not_affect_tree_record` killer made hollow (`assert module is None, label` as its first line): its
  row FAILS with `Failed: AF-AP-138: test_exclusions_do_not_affect_tree_record fails on the UNMUTATED module, so a kill of
  empty-exclusions is not attributable to the mutation` (`1 failed, 12 passed`). My unconditional killer (`raise AssertionError(label)`,
  fed through `run=`) is refused the same way (PASSED under `pytest.raises(pytest.fail.Exception, match="^AF-AP-138: …")`).
- B: the same copy with the harness's baseline control deleted: the hollow `[empty-exclusions]` row now PASSES (a hollow kill), and
  both `test_af_ap_138_control_refuses_a_killer_that_fails_on_the_unmutated_module` and my test FAIL with `Failed: DID NOT RAISE Failed`
  (`2 failed, 11 passed`). The control row is the discriminator the brief asked for.

## 6. F-07 and F-08 — RAN FULLY (driver `/tmp/vk215/mut.py`: exact-once replacement, `py_compile`, the named tests, restore proven by sha256)
F-07, `pyflakes_delta` in the clone's hook, tests `-k pyflakes_delta` (5 tests):
- K-PE catch narrowed to `PermissionError`: KILLED, `2 failed, 3 passed` — `…_venv_path_is_too_long` (`OSError: [Errno 36] File name too
  long`) and `…_venv_python_times_out` (`subprocess.TimeoutExpired`). The absent-venv control is among the 3 passed: D-1 REPRODUCED.
- K15 catch narrowed to `OSError`: KILLED, `1 failed` — `…_times_out`.
- K16 absent venv answers a line: KILLED, `1 failed` — `…_venv_is_absent`: `AssertionError: assert ['  LINT   venv absent'] == []`
  (D-1's other half REPRODUCED).
- K-HOIST (mine) the probe hoisted out of the `try` (AF-AP-44's original shape): KILLED, `2 failed` — `…_venv_probe_raises`, `…_path_is_too_long`.
- K-LINE (mine) a failure answers a line instead of `[]`: KILLED, `4 failed` (`assert ['  LINT   pyflakes failed'] == []`).
F-08, `parse_classes` in the clone's `scripts/vendored_manifest.py`, tests `-k test_malformed_claude_class_row_is_refused_by_line` (4 rows):
- M8d the header check removed: KILLED, `1 failed, 3 passed` — `[bad-header]`: `assert 'FAIL: .claude class file parse failure at line 1\n' in
  'FAIL: .claude class drift: byte length differs\n'`.
- M8e `len(cells) == 2` → `>= 2`: KILLED — `[extra-cell]`: `… parse failure at line 2\n' in 'FAIL: .claude class drift: …`.
- M8f (mine) the header checked on its first cell only: KILLED — `[bad-header]`, the same assertion.
- M8g (mine) `line.split("\t")[:2]` (extra cells cut before the check): KILLED — `[extra-cell]`.
`scripts/vendored_manifest.py` restored (`git diff --quiet` in the clone: clean).

## 7. SKILL BAKES — RAN FULLY
Texts read from `git diff ef21f88 bfe66ec` on the three `.claude` skills and their `.agents` twins; facts checked against
`git show bfe66ec:docs/INCIDENT-LOG.md`.
- b150 (`.claude/skills/deep-work/SKILL.md`, the bug-echo paragraph): rule = every first-party root named and the command pasted;
  facts = AF-AP-127's sweep read `scripts/` and `harness-ports/bin/`, missed the one-label key rule in `src/` (AF-AP-149), found while the
  J1-1-R1 brief was written, 2026-09-23. All match the AF-AP-150 row. The row also names AF-AP-127-R1's search; the bake omits it (no
  false fact).
- b151 (`.claude/skills/build-loop/SKILL.md`, step 2): rule = a change to the pre-commit hook, a script it runs or
  `scripts/gate_files.txt` also runs `tests/test_shell_syntax.py`, and a fixture derives its lists from the committed config; facts =
  J1-0-R4 listed the hook in `scripts/gate_files.txt`, CI run #983 failed the positive control (`gate-file-import-unlisted`), the gate
  had run only `tests/test_no_laya_in_gates.py`, run 917 failed the same fixture (`can't open file`). All match the AF-AP-151 row.
- b153 (`.claude/skills/anti-hollow-green/SKILL.md` 3e): rule = feed the old version's refusals and new hostile variants to both
  versions; facts = VERIFY-J1-0-R4 V-01, the ANSI-C `$'…'` delimiter, a four-line gate R3 rc 4 / R4 rc 0, 2026-09-23. All match the
  AF-AP-153 row. The pointer resolves: `.claude/skills/orchestration/SKILL.md:64` (0d″) carries "A verifier's PROPOSED FIX is a hypothesis
  too (2026-09-23, VERIFY-J1-1-R1's option B; AF-AP-153's class)".
- 2(g) (#218): rule and controls match the AF-AP-179 row (sitecustomize on `PYTHONPATH` inserting a `sys.meta_path` finder, attempts
  logged and asserted zero, three controls; J1-5, 2026-09-24). Its checkable Python claims, RUN in `/tmp/vk215/g/` with the venv python
  and a `sitecustomize.py` blocker on `PYTHONPATH` (a real package `blockedpkg` beside it): a plain import → `ImportError: blocked`,
  1 log line; a caught import → `caught`, 1 log line; an inheriting child → blocked, 1 log line; `importlib.import_module` → blocked,
  1 log line; a child started with `-I` → `ESCAPED imported`, 0 log lines; with `-S` → ESCAPED, 0; with `-E` → ESCAPED, 0; with an
  `env=` that drops `PYTHONPATH` → ESCAPED, 0. A `builtins.__import__` hook in a fresh process: the `import` statement → `blocked`;
  `importlib.import_module` under the same hook → `ESCAPED imported`. Every claim holds.
- 3f (#218): rule = a measured zero states its generator's alphabet; facts = VERIFY-J1-1-R3, 2026-09-24, D-067 void, D-068, the
  builder's zero, a generator that never drew a mixed-case `KEY` name and a body count blind to special letters, 9 of 165,000 inputs,
  orchestration 0f (`.claude/skills/orchestration/SKILL.md:94`). All match the 2026-09-24 06:1xZ incident entry.
Twins: each `.agents/skills/<skill>/SKILL.md` hunk says the same rule and facts in different sentences (no byte copy: the `.agents` and
`.claude` files differ, sha256 prefixes 584d33b0d7d7/ad2dd41c1255, 0c86871447d5/635a2c3c3964, f2e5d1a2cb2f/3def0a178f37), and I
found no claim in a twin that its `.claude` text lacks (the build-loop twin's "short gate list" matches the row's "three-line
list"). Each `.agents/lane-skills/<skill>/SKILL.md` equals its twin byte for byte (the same three sha256 prefixes; the premise's
`sync-lane-skills-check rc=0`).
`harness-ports/hand-ported.sha256` (`git log -p -3`): `b318135` changes exactly three lines — anti-hollow-green
`58db02c1…` → `68916b02…`, build-loop `f0508156…` → `635a2c3c…`, deep-work `88399611…` → `ad2dd41c…`; `bfe66ec` changes one line,
anti-hollow-green `68916b02…` → `3def0a17…`. Every other hand-ported skill's line is unchanged, so `--record` masked no drift; the
recorded values equal the current `.claude` files' sha256 (the prefixes above).

## 8. THE LEDGER-PLANE CHANGES — RAN FULLY
(a) The eleven rows holding `task #215` at the PIN (AF-AP-132, 141, 144, 145, 149, 150, 151, 152, 153, 175, 177) each match what landed:
132 "the enumerate and literal-separator tells; the indexed-list shape has no line signature" and "ten unlisted sites" (13 hits = 3
named + 10, section 2.1); 141 "extended to `cat-file -e`" (section 2.2); 144 "path-scoped, without the `main` and reader conditions (73
of 105 matches are false hits in catch-all mains)" — RE-DERIVED: `for_path` over every `proofs/*/check_*.py` at the PIN gives 105
matches, and an AST read of each `main`'s handlers puts 63 + 7 + 3 = 73 of them in the three mains that catch `Exception`
(`proofs/S0-01/check_acp_conformance.py`, `proofs/S0-01/check_initialize.py`, `proofs/S0-04/check_compression.py`); 145, 149, 152 "the
screen line LANDED"; 150 and 151 baked where stated; 153 "no screen line … baked into anti-hollow-green tactic 3e"; 175 "the LINE form,
every quoted `HEAD` literal"; 177 "with the variable-held form" and `harness-ports/bin/lane-done-gate.py:148` (`payload.get`). `bfe66ec` adds one
registry change, the AF-AP-179 row's "baked into anti-hollow-green tactic 2(g), 2026-09-24 (task #218)": true.
Stale after the landing (not among the eleven): the AF-AP-138 row still says "follow-up: the control has no committed negative control
(VERIFY-K150 F-03)", which K215's `tests/test_vendored_manifest.py:1314` (`test_af_ap_138_control_refuses_a_killer_that_fails_on_the_unmutated_module`) falsifies; the AF-AP-139 row still says "VERIFY-K150 F-06:
fixture gaps, and widening it to any status would add two false hits", with no word of the landed widening; the 06:1xZ entry still says
the 3f rule is "Owed to a skill once K215 frees `anti-hollow-green`". All three read the same at the shared HEAD 3bcd7bc, and again at 9e6821b (07:46Z, after a push and the VERIFY-J1-45 registry edit). F-6 below.
(b) The CLAUDE.md quirk line, REPRODUCED with my own Write tool: I typed `A = "\u2028"`, `B = "\u2029"`, `C = "\u0085"`, `D = "\t"` into
`/tmp/vk215/quirk_probe.txt`; `od -c` reads `"  342 200 250  "` and `"  342 200 251  "` on the first two lines (the literal separators),
and `\   u   0   0   8   5` and `\   t` as text on the other two. The line's byte check `LC_ALL=C grep -c $'\xe2\x80[\xa8\xa9]' <file>`
prints 2 on that file and 0 on files without a separator (`/tmp/vk215/probe.py`, and this report). Two limits of the check, INFO: it
counts LINES (two separators on one line print 1, still non-zero), and it does not look for U+0085 (the tool does not produce it,
but AF-AP-132's signature names it).
(b, continued) The quirk is WIDER than the CLAUDE.md line says. This report's own append of section 8 went through a Bash heredoc
(quoted `'EOF'`), and the file then held one separator line (`LC_ALL=C grep -c` printed 1): line 288 carried a literal U+2028 and
U+2029 exactly where I had typed the backslash-u-2028 and backslash-u-2029 escapes, while the typed backslash-u-0085 stayed text.
So the Bash tool's `command` parameter converts the same two escapes; the line names only "The Edit and Write tools". I repaired the
report with `chr()`-built text and re-checked it (0 separator lines). F-7 below.

## 9. MY MUTANTS — RAN FULLY (20 mutants, `/tmp/vk215/mut2.py`, each exact-once in the clone's hook, `py_compile`d, run through the
real `tests/test_edit_snapshot_ap_screen.py` (170 collected each time), restored and proven by sha256; the hook ends `git diff --quiet`)
KILLED (8), with the failing test and its assertion line:
- M01 AF-AP-132 list window `{0,15}?` → `{0,0}?`: `TestAFAP132::test_fires_on_a_list_from_splitlines_enumerated_with_a_start` — `assert None`.
- M02 AF-AP-132 the enumerate start no longer required: `TestAFAP132::test_no_fire_on_a_list_used_as_an_index` — `assert not <re.Match … '    lines = text.splitlines()\n    header = next(>`.
- M06 `_PathScoped.for_path` uses `match` (anchored): `TestAFAP144::test_fires_in_a_proof_checker` — `AssertionError: assert None`, and
  `test_af_ap_144_the_hook_applies_the_path_scope` — `assert 'AF-AP-144' in 'EDIT SNAPSHOT · check_pins.py\n  impact  module-level edit …'`.
- M07 the path regex's `[^/]+` → `.+` (nested accepted): `TestAFAP144::test_no_fire_outside_the_checker_paths` — `assert not <re.Match … match='yaml.safe_load('>`.
- M08 `main` scopes on `Path(fp).name`: `test_af_ap_144_the_hook_applies_the_path_scope` — `assert 'AF-AP-144' in 'EDIT SNAPSHOT · check_pins.py …'`.
- M17 AF-AP-177 variable-held window `{0,8}?` → `{0,0}?`: `TestAFAP177::test_fires_on_the_variable_held_form` — `assert None`.
- M19 F-06 the `-> None` allowance dropped: `TestAFAP139::test_fires_on_a_handler_annotated_to_return_none` — `AssertionError: assert None`.
- M20 `_PathScoped.finditer` returns the unscoped matches: `TestAFAP144::test_the_path_less_callers_see_nothing` — `assert [<re.Match ob...json.loads('>] == []`.
SURVIVED (12), each `170 passed`: M03 U+0085 dropped from AF-AP-132's literal class; M04 AF-AP-141's `(?!_\b)` removed (an `rc, _, _`
binding now excuses the line); M05 AF-AP-141's shell `merge-base --is-ancestor` alternative dropped; M09 `_IGNORE` accepts only `INT TERM`
(not `TERM INT`); M10 `_BODY` no longer allows a comment line before the ignore (the class comment says "a `$?` capture or a comment may
come first"); M11 `_TRAPPED` needs `EXIT` right after the name (`trap cleanup INT TERM EXIT` unseen); M12 `_HANDLER` reads TERM
handlers only; M13 AF-AP-149's BLOCK no longer excuses a label; M14 AF-AP-149's `\Z` no longer excuses an END; M15 AF-AP-152's `{m,n}`
outer quantifier dropped; M16 AF-AP-175's single quote dropped; M18 `NO_CONTENT` dropped from F-06's 2xx members.
Live effect of each survivor (`/tmp/vk215/live_impact.py`: the mutant applied to a COPY of the hook, its row counted over the same
five-root file list): ten change nothing live; M14 GAINS one hit (the hook's own AF-AP-149 line, `.claude/hooks/edit-snapshot.py:308`);
M16 LOSES 5 of the 12 live AF-AP-175 hits (`scripts/push_clean.sh:98` (`TREE_BEFORE`), `:103`, `scripts/fubuki_pin_sync.sh:36` (`tree_of`), `:66`,
`scripts/stamp_check.py:43` (`exists`)) while all 170 tests stay green. The contract asks each row for one positive and one negative fixture,
which every row has; per-branch pins are not required. FOLLOW-UP F-3 below; M16 is its sharpest case.

## 10. REGEX COST — RAN FULLY (`/tmp/vk215/cost.py`, each case in its own process, 60 s cap)
Per row, texts designed for that row (the three shapes the brief names plus row-specific ones):
- AF-AP-132: `enumerate(` ×10,000 on one 100,001-char line, no splitlines: **4.8461 s**; `x = ` + `a.splitlines()` ×7,000 then 15
  lines: 0.4257 s; 50,000 `x = t.splitlines()` lines: 0.2308 s; a 100k line ending in U+FFFD: 0.0072 s; 50,000 separator lines: 0.0177 s.
- AF-AP-141: `git ` ×25,000 on one 100,001-char line, no merge-base: **23.1988 s**; `"--is-ancestor", ` then `a, ` ×30,000: 0.0101 s;
  50,000 `cat-file -e` lines: 0.0808 s.
- AF-AP-144 (through `for_path`): `.decode(` ×11,000 on one line: 0.0014 s; 50,000 `json.loads(x)` lines: 0.0114 s.
- AF-AP-145: see section 3.2 — all seven cases ≤ 0.1379 s (linear).
- AF-AP-149: `-----BEGIN .*` ×8,000 on one 104,001-char line: **12.4757 s**; 50,000 rule lines: 0.0305 s.
- AF-AP-152: `(?:[` then 5,000 / 10,000 / 20,000 word characters, no `]`: 0.1185 / 0.4610 / **1.9351 s** (quadratic: the pattern's own
  `[^\]\n]*?([\w-])[^\]\n]*\]` is a lazy-then-greedy scan with no terminator, AF-AP-152's class inside the AF-AP-152 row);
  `|[` ×10,000 (20k chars) / ×20,000 (40k chars), no `]`: 0.9487 / **3.7934 s**; `(?:` ×33,000: 0.0033 s; 50,000 group lines: 0.0579 s.
- AF-AP-175: `"HEAD` ×20,000: 0.0025 s; 50,000 lines: 0.0103 s.
- AF-AP-177: `.get(` ×20,000: 0.0035 s; `v = ` + `d.get(k)` ×12,000 then 8 `isinstance(` lines: 0.7733 s; 50,000 binding lines: 0.3252 s.
Could a real file hold those lines? Measured over every first-party tracked text file (`/tmp/vk215/realmax.py`; vendored trees
excluded): the most any one line holds is 9 `git` words (`todo/BUILD-TASKLIST.md:473` (`test_committed_tree_anchor_state_is_the_declared_pending_one`)), 1 `enumerate(`, 1 `-----BEGIN `, 5 `|[`, 2 `(?:[`.
On the three largest real files, including the longest real line (`proofs/S0-02/evidence/neg-replayed/first/timeline.jsonl`, 943,195
characters, one line of 919,414), every new row costs ≤ 0.0562 s (`/tmp/vk215/realtime.py`). So no real file comes near 1 s; the
quadratic cases need thousands of trigger tokens on one line. The builder's self-attack line "Every final row's worst case on hostile
input is at most 0.0271 s" holds only for its own texts: FOLLOW-UP F-4 (and an evidence overstatement, INFO I-3).

## 11. GATES at the PIN — RAN FULLY (private clone `/tmp/vk215/clone`, detached at bfe66ec, clean before and after)
```
07:32:29Z $ /root/venv-agent-factory/bin/python -m pytest tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py -q -p no:cacheprovider --basetemp=/tmp/vk215/bt11/r1
226 passed in 144.15s (0:02:24)      rc=0
07:34:53Z (same command, --basetemp=/tmp/vk215/bt11/r2)
226 passed in 173.24s (0:02:53)      rc=0
$ bash scripts/pc_suite.sh set-id -- tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py
2 files set=2a60fb528bf2
$ … -m pytest tests/test_hooks_worktree.py -q -p no:cacheprovider --basetemp=/tmp/vk215/bt12/h
2 passed in 0.22s
$ … -m pyflakes .claude/hooks/edit-snapshot.py tests/test_edit_snapshot_ap_screen.py tests/test_vendored_manifest.py
(no output) pyflakes rc=0
$ python3 scripts/no_laya_in_gates.py
no_laya_in_gates: 40 files scanned, clean      rc=0
$ python3 scripts/ap_screen.py .claude/hooks/edit-snapshot.py | head -1
--- AP_SCREEN over 1 path(s): 20 hits over 1 files ---
$ python3 scripts/vendored_manifest.py --check | tail -1
PASS: sandbox-kit/VENDORED-MANIFEST.md matches 9 vendored roots      rc=0 (PIPESTATUS)
$ bash harness-ports/bin/sync-skills.sh --check | tail -1
sync-skills: .agents/skills is in sync with .claude/skills (410 skills)      rc=0
$ bash harness-ports/bin/sync-lane-skills.sh --check
sync-lane-skills: in sync (25 skills)
07:38:05Z-07:39:35Z $ bash harness-ports/tests/run-all.sh      rc=0; last lines:
test_lane_context.sh               5 passed, 0 failed
test_context_mirrors.sh            11 passed, 0 failed
test_sync_skills.sh                34 passed, 0 failed
build-roles --check                OK: 3 role config layers match their sources

ALL SUITES PASSED
```
The two runs agree (`226 passed` both, set `2a60fb528bf2`), as do the builder's and the premise's counts. Self-screen parity
re-derived (`/tmp/vk215/probe.py` over both hook texts): the PIN's rows give 20 hits on the 942ad5e hook and 20 on the PIN hook, with
identical (row, line text) multisets — the builder's section-6 claim holds.

## 12. ADJACENT CONSUMERS — RAN FULLY
- `scripts/ap_screen.py` (loads the hook in-process) on a real file: `python3 scripts/ap_screen.py --limit 2 scripts/decide-harvest` →
  `--- AP_SCREEN over 1 path(s): 4 hits over 1 files ---`, `AF-AP-177: 2`, rc 0.
- `scripts/lint_delta.py` (loads the hook in-process) on the real K215 change set: `lint_delta.py --base ef21f88` → rc 0,
  `lint_delta (worktree vs ef21f88): 2 .py changed, 0 NEW pyflakes hit(s), 0 removed`, 7 advisory tells. The two changed files are the
  tests: `scripts/lint_delta.py:71` lists `.claude/` in `_VENDORED`, so the hook itself never gets a commit-time pyflakes delta
  (pre-existing; INFO I-5).
- `scripts/lane_context.sh`'s screen section: the brief's pack, run at 06:55Z in the shared tree (whose boundary files and
  `scripts/lane_context.sh` are byte-identical to the PIN), printed `--- AP_SCREEN over 1 path(s): 20 hits over 1 files ---` for the hook,
  `--- TEST_SCREEN over 1 path(s): 31 hits over 1 files ---` for the test file, 2 hits for `scripts/ap_screen.py`, 3 for `scripts/lint_delta.py`.
- The pre-commit hook, run for real in the clone (`bash scripts/hooks/pre-commit` with a staged `proofs/S0-99/check_vk215.py` holding one
  instance of each new row's class and a staged `scripts/vk215_probe.sh` holding the AF-AP-145 and AF-AP-141 shell forms): `lint_delta
  (index vs HEAD): 1 .py changed, 0 NEW pyflakes hit(s)`, then tells for AF-AP-139, -132, -141, -145, -149, -152, -175, -177; NO AF-AP-144;
  the `.sh` file is not screened (only `.py` reaches `lint_delta`); the hook then stopped at `gate-file-unlisted:
  proofs/S0-99/check_vk215.py` / `COMMIT BLOCKED by the never-a-gate screen (rc=4)` (`no_laya_in_gates.py` wants a new checker listed in
  `scripts/gate_files.txt`; expected for a probe, unrelated to K215). The AF-AP-132 tell there came from the enumerate line: section 3.4 shows
  its literal-separator branch cannot fire at commit time. Which rows can fire at commit time: 132 (branches A/B only), 139, 141 (Python
  argv, and shell text inside a `.py`), 145 (only shell text inside a `.py`), 149, 152, 175, 177. Which cannot: 144 (path-less caller),
  132's literal-separator branch (the separator is split away), and every row on a `.sh` file.
- No new row raises: every new AP_SCREEN and TEST_SCREEN row (and `for_path(<the file's path>)` / `for_path("/abs/" + path)` for the scoped row),
  `finditer` and `search`, over every tracked file under `scripts/ src/ proofs/ harness-ports/ tests/ .claude/hooks/` (`/tmp/vk215/noraise.py`):
  `files=1057 row-calls=25368 exceptions=0 in 15.2 s`. `ap_screen.py` over the same 1,057 files: `--- AP_SCREEN over 1057 path(s): 910 hits
  over 1057 files ---` rc 0 and `--- TEST_SCREEN over 1057 path(s): 229 hits over 1057 files ---` rc 0, no Traceback in either output.

## GRADES of the builder's declared gaps (D-1..D-10, NOT-done)
- D-1 (f07): REPRODUCED (section 6). The contract line cannot hold for the absent-venv control: that branch returns `[]` before any
  raise, so no catch-narrowing mutant can red it. K16 is the right substitute. Acceptable.
- D-2 (s175, LINE form, every quoted `HEAD`): the contract offered this fallback, and the PIN's registry row adopts the wording
  ("in the LINE form, every quoted `HEAD` literal"). An acceptable, documented limit; the 26 unquoted shell reads it cannot see are F-8.
- D-3 (s144, path-scoped, scope only in `main`): the contract allowed it ("scope it and say so"). The 105/73 counts were re-derived
  (section 8). Acceptable; the consumers' side is F-2.
- D-4 (s132, the indexed-list shape unscreened; the U+FFFD narrowing): acceptable. The registry itself says that shape "has no line
  signature". The narrowing reproduces (264 unexcluded line hits in the 11 `.gz` files, 0 with it); the "275" is I-2.
- D-5 (AF-AP-153, no row): as the brief directed. The registry row at the PIN now says so ("no screen line … baked into
  anti-hollow-green tactic 3e"). Resolved.
- D-6 (sequencing): acceptable. Every final-tree gate reproduces at the PIN (section 11).
- D-7 (manifest header names a rewritten commit): informational, and it recurs at the PIN (I-6).
- D-8 (f06, the other near misses): confirmed recorded, not graded (as the brief directs).
- D-9 (s177, the hit at the binding line `:689`, not `:691`): acceptable. The match starts at the binding, and `ap_screen.py` numbers
  match starts.
- D-10 (s145, `harness-ports/bin/pc-lane.sh:127` (`stop_session`)): an acceptable, documented false hit. The registry's OK rests on re-entry, which no line
  screen can see.
- NOT-done: accurate as far as it goes, but it names fewer unseen shapes than exist. F-9 lists the rest.

## FINDING INVENTORY (no severity filter; the predicate is applied after)
Evidence levels: R = reproduced by a command in this lane; S = reviewed statically. Canonical path = the hook's `main`, `ap_screen.py`,
`lint_delta.py` / the real pre-commit hook, or the real test files at the PIN.

BLOCKER: none.

FOLLOW-UP
- F-1 AF-AP-145 misses nine shell spellings inside its registry signature and fires on seven correct forms (section 2.4). R; mapped to
  the AF-AP-145 row's signature; canonical (`ap_screen.py` is the row's only reach); material: none today (the live-site sweep found no
  missed spelling and no flagged correct form beyond the builder's list). Repro: `/tmp/vk215/rows/r145.py`. Fix: accept `function name {`,
  a brace on the next line, `trap --`, multi-name or argument trap strings, `0`, a mid-line trap; read the bodies of UNQUOTED INT/TERM
  handler functions; accept `TERM INT`, extra signals, `SIG` names and numbers in the ignore; one fixture per branch.
- F-2 AF-AP-144 can never fire at commit time or in any `ap_screen.py` sweep, the registry's bug-echo instrument (sections 3.1, 12). R;
  mapped (s144); canonical (real pre-commit hook, real `lint_delta.py`); material: the class is visible only at edit time, in one hook;
  the contract allowed it and the fix is outside K215's boundary. Fix: `scripts/lint_delta.py` and `scripts/ap_screen.py` call
  `rx.for_path(path)` when the row has it.
- F-3 Test gaps: 12 of my 20 mutants survive the real test file (section 9). The sharpest is M16: dropping `'` from AF-AP-175's quote
  class loses 5 of the 12 live hits while 170 tests pass. R; mapped to anti-hollow-green tactic 3 ("Demand BRANCH coverage"), not to a
  K215 contract line (the contract asks one positive and one negative fixture per row, which every row has); canonical; material: a
  future edit could silently narrow four rows. Repro: `/tmp/vk215/mut2.py`, `/tmp/vk215/live_impact.py`. Fix: pin `'HEAD^{tree}'`,
  U+0085, `rc, _, _ =`, the shell `merge-base --is-ancestor`, `trap '' TERM INT`, a comment before the ignore, `trap cleanup INT TERM EXIT`,
  an INT handler string, AF-AP-149's BLOCK-only and `|\Z` rules, a `{0,}` group and `HTTPStatus.NO_CONTENT` with one fixture each.
- F-4 Four rows are quadratic on one long line built from their own trigger (section 10): AF-AP-141 23.1988 s, AF-AP-149 12.4757 s,
  AF-AP-132 4.8461 s, AF-AP-152 1.9351 s and 3.7934 s (AF-AP-152's class inside the AF-AP-152 row). R; mapped to AF-AP-152's
  class and to item 10's bar; material: none on real text (no real line holds more than 9 trigger tokens; the longest real files cost
  ≤ 0.0562 s per row), so the ">1 s on a text a real file could hold" bar is not met. Repro: `/tmp/vk215/cost.py`. Fix: bound each lazy
  scan's reach, or split lines first, and pin a timing test on a repeated-trigger line.
- F-5 TEST_SCREEN has no AF-AP-132 separator row. A literal separator in a test file is flagged neither at edit time (the hook's
  `/tests/` branch) nor at commit time (`scripts/lint_delta.py:99` (`splitlines`) splits it away); three tracked tests hold them
  (`tests/test_ap_screen.py:89` (`write_text`), `tests/test_decide_harvest.py:777` (`uncommitted`), `tests/test_report_lint.py:118` (`gamma_delta`), all deliberate), and the tools
  produce them (F-7). The builder's "No class lives in tests" came from a sweep that excluded `tests/`. R; mapped to the brief's
  TEST_SCREEN clause, which PERMITS the row and does not require it; material: none today. Fix: a TEST_SCREEN row for the
  literal-separator branch alone, or `chr()` in the three fixtures.
- F-6 Stale ledger text after the landing (section 8): the AF-AP-138 row still calls the F-03 control missing; the AF-AP-139 row still
  says "fixture gaps" and omits the widening; the 06:1xZ entry still calls 3f "owed". R (the same text at the PIN, at 3bcd7bc and at 9e6821b); mapped to the
  stale-context duty; the coordinator's ledger, not K215's boundary. Fix: a three-line ledger edit.
- F-7 The CLAUDE.md quirk line is true but narrower than the fact: the Bash tool's `command` converts the same two escapes (this report's
  line 288 took a literal U+2028 and U+2029 from a quoted heredoc; repaired). R; mapped to item 8(b); material: a lane that trusts the
  line and types the escapes into a Bash heredoc writes the literal. Fix: name the Bash tool (every tool parameter) in the line.
- F-8 AF-AP-175 cannot see an unquoted `HEAD`: 26 git reads in first-party shell, e.g. `scripts/push_clean.sh:14`, `:30`, `:109`,
  `:122`, `:123` in one process (section 2.7). R; mapped to the contract's "a `HEAD` literal passed to a git call" and to D-2, which
  narrowed it to quoted literals, a narrowing the registry adopted; material: none known (no mixed-snapshot defect among them). Fix: a
  shell branch `\bgit\b[^\n]*\bHEAD\b` like AF-AP-141's branch B, measured for false hits first.
- F-9 Near misses the NOT-done list does not name (sections 2.1-2.8, 4): 132 `splitlines(keepends=True)`/`(True)`, annotated or
  attribute lists; 141 `$GIT`; 144 `json.load`, `yaml.load`, `read_text(errors=…)`; 149 `BEGIN\s+`, `-{5}`, a label alternation, `re.I`;
  152 capturing and named groups, `(?:[a-z]+)*`, an unanchored FIRST alternative (each measured super-linear); 177 walrus, `frozenset`,
  annotated binding, a nested call in `.get(…)`; 139 `.value`, `int(…)`, `code=`, `HTTPStatus(200)`. R; no live site uses any of them.
  Fix: widen where it is cheap and name the rest in each row's "Not seen" comment.

INFO
- I-1 Neither new class implements `findall`, `match` or `pattern`; the one consumer that calls `findall`
  (`tests/test_s0_01_frame_tee.py:3060` (`findall`)) guards it with `ap_id == "AF-AP-59"`. `_EmitNoneKwarg` already had this shape (section 3.3).
- I-2 "275 false hits in 11 .gz evidence files" (the hook comment above the AF-AP-132 row and the docstring of
  `test_no_fire_on_a_line_that_did_not_decode`) counts separator CHARACTERS (275); the row without the exclusion gives 264 line hits.
- I-3 The builder's "Every final row's worst case on hostile input is at most 0.0271 s" holds for its own texts only (F-4).
- I-4 `python3 scripts/report_lint.py --min-refs 15 tasks/briefs/kit-k1-support/K215-report.md` at 3bcd7bc: `OK 89, NEAR 0, MISS 11`.
  All 11 are registry line cites that moved two lines under later ledger commits; they matched at 06:25Z.
- I-5 `lint_delta.py` skips `.claude/` (the hook gets no commit-time pyflakes delta) and screens test files with AP_SCREEN, not
  TEST_SCREEN. Pre-existing.
- I-6 The manifest header at the PIN names `1c6d300f1214…`, which is not an ancestor of the PIN (D-7's class; `--check` ignores it).
- I-7 The CLAUDE.md byte check counts lines and ignores U+0085.
- I-8 The `{ap_id:6s}` format runs a 9-character id into its message (`AF-AP-139proofs/…`; VERIFY-K150 F-18, pre-existing).
- I-9 AF-AP-139, old and new, fires on handlers that branch on the path through `match self.path:` or `ROUTES.get(self.path)`. Pre-existing.
- I-10 `main` takes the `/tests/` branch for any path holding `/tests/`, so a scratch copy under a directory named `tests` loses AP_SCREEN.
  Pre-existing.

UNVERIFIED
- U-1 The builder's "a lookahead version took 0.68 s on 2,000 definitions": the discarded version is not in the tree. The shipped class is
  linear (measured, section 3.2).
- U-2 Of the builder's roughly forty RED runs I reproduced seven: K-PE, K15, K16, M8d, M8e, the F-03 control deletion, and the AF-AP-139
  pre-widening row on its two positives. The rest are claims; twenty of my own mutants stand beside them.

## PREDICATE AND RECOMMENDATION
No finding meets all five conditions. F-1, F-4, F-5, F-8 and F-9 have no material effect: no live site is missed or flooded, and no
real file comes near the cost bar. F-3 is not mapped to a frozen K215 line: the contract asks one positive and one negative fixture
per row, and every row has both. F-2 and F-8 are limits the contract allowed and the builder declared (D-3, D-2). F-6 and F-7 sit
in the coordinator's ledger and CLAUDE.md, outside K215's boundary. Every predicate-listed material class was checked and none was
found: a screen or consumer crash (0 exceptions in 25,368 row calls; every consumer rc 0), a row that floods clean code (fire counts
13/5/7/1/12/4 over 960 files), a hollow control or kill (F-03, F-07, F-08 and my twenty mutants discriminate), a bake that states a
false fact (every fact checked), a masked twin drift (`hand-ported.sha256` moved on the three K215 skills only, then on
anti-hollow-green only). The recommendation rests on no un-run item: U-1 and U-2 are not load-bearing, because the class's linearity
and the controls' kills were reproduced directly.

GATE RECOMMENDATION: MERGE-READY-WITH-FOLLOWUPS — all twelve items ran fully at bfe66ec; no blocker; follow-ups F-1..F-9 (sharpest: F-3's M16, F-2, F-6, F-7).

## DISCREPANCIES (this lane's own)
- VD-1 I hit the escape quirk myself (F-7): one append put a literal U+2028/U+2029 in this report. It was found by the byte check,
  repaired with `chr()`-built text, and re-checked at 0 separator lines after every later append.
- VD-2 Item 5's first `-k` filter matched the scratch module's name and ran the whole copied file. The evidence is the re-run by node id.
- VD-3 The first `live_impact.py` counts included my three staged probe files in the clone (AF-AP-132 14, AF-AP-145 8). The mutant
  deltas are unaffected. The files were removed afterwards and the clone is clean at bfe66ec.
- VD-4 Item 12's `scripts/lane_context.sh` screen evidence is the pack run in the SHARED tree at 3bcd7bc, not the clone. That tree's
  boundary files and `scripts/lane_context.sh` are byte-identical to the PIN (premise, and no post-PIN commit touches them).
- VD-5 One gate line first read `rc=$?` through a pipe; it was re-read with `PIPESTATUS` (`vendored_manifest rc=0`).

## NOT-done
- No PC or bridge use (the brief forbids it); no full-repository suite (the brief's gates only); no subagents.
- graft and GitNexus do not index `.claude/hooks/`, so the hook is unmapped by the code-intel tools. Every consumer and instance
  sweep here is a literal-token `git grep`/`grep`, named as the fallback.
- The builder's discarded lookahead implementation was not rebuilt (U-1), and 7 of its roughly 40 RED runs were reproduced (U-2).
- Nothing in the shared tree was changed except this report (`git status --short` at 07:46Z: only this file). The private clone `/tmp/vk215/clone` was removed at 07:46Z (0 status lines at bfe66ec before removal). At 07:46Z the shared HEAD is 9e6821b; its diff against the PIN leaves every boundary file, `CLAUDE.md` and `scripts/lane_context.sh` byte-identical (`boundary-identical-to-pin`).

## ITEMS RUN
1 PREMISE: fully. 2 SCREEN ROWS: fully (i, ii, iii for all eight rows; D-2, D-3, D-4, D-9, D-10 and NOT-done graded). 3 THE TWO NEW
CLASSES: fully. 4 F-06: fully. 5 F-03: fully. 6 F-07 and F-08: fully (D-1 reproduced). 7 SKILL BAKES: fully. 8 LEDGER-PLANE: fully.
9 MUTANTS: fully (20: 8 killed, 12 survivors reported). 10 REGEX COST: fully. 11 GATES: fully. 12 ADJACENT CONSUMERS: fully.
