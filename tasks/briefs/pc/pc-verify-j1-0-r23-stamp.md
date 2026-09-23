# VERIFY-J1-0-R23-STAMP — the independent adversarial verify of J1-0-R2 (a listed gate file must be regular), J1-0-R3 (the screen follows its in-process include edges) and the future-stamp pre-commit gate, on the PC

PIN: 5a00d13 (origin head at authoring; every boundary file below is byte-identical to its last change: `scripts/no_laya_in_gates.py` 6a6cd4a, `scripts/stamp_check.py` and `scripts/hooks/pre-commit` 8d50443. The dispatcher builds your lane tree AT this PIN. Re-measure the identities first.)
LANE: pc-verify-j1-0-r23-stamp
ROLE: adversarial-verifier on the STRICT local route (`HERMES_MODEL=qwen-local/qwen3.8-27b-local`). The contract-gate predicate (D-031): a finding BLOCKS only if contract-mapped · reproduced through the real production path (here: the REAL `scripts/hooks/pre-commit` on a real `git commit` in a throwaway repo, or the real screen/gate CLI) · materially effective · a concrete discriminator · in boundary. Emit ONE GATE RECOMMENDATION PER COMPONENT — (A) J1-0-R2, (B) J1-0-R3, (C) the stamp gate — never a verdict. The coordinator owns the gate. (B) and (C) were BUILT BY THE COORDINATOR in the main loop, and (A) was graded only by the coordinator's own tests: yours is their first independent pass (rule 0f).

COMPONENTS + CONTRACTS (frozen; the builders' notes are INPUTS to attack, never evidence):
- (A) J1-0-R2 (5eae256) — contract: `tasks/briefs/laya/J1-0-brief.md:16` (AMENDMENT 1), which answers `tasks/briefs/laya/VERIFY-J1-0-R1-report.md:121` (finding R3: a listed gate file replaced by a symlink passes as clean). Code: `scripts/no_laya_in_gates.py` `_index_mode` (:513) and the regular-file checks in `main` (:596-604); `REGULAR_INDEX_MODES` (:38). Tests in `tests/test_no_laya_in_gates.py`, measured at the PIN (`grep -n -E '^def test_.*(symlink|fifo|regular|executable|mode|gitlink)'`): `test_staged_mode` (:136), `test_staged_symlinked_gate_file_is_not_regular` (:357), `test_worktree_symlinked_gate_file_is_not_regular` (:383), `test_executable_regular_gate_file_stays_clean` (:400). No test names a FIFO, a directory or a gitlink: the on-disk `not-a-regular-file` branch (:604) and the `160000` mode have no named test (A2 decides whether they are exercised at all).
- (B) J1-0-R3 (6a6cd4a) — contract: `tasks/briefs/laya/J1-0-brief.md:17` (AMENDMENT 2) + `tasks/briefs/laya/J1-0-R3-brief.md` (its STATUS note at the top overrides the text below it where they differ) + the registry row AF-AP-120 (`docs/INCIDENT-LOG.md:446`). Code: `_command_segments` (:99), `_source_errors` (:189), `_package_files` (:271), `_import_errors` (:307), `EXTERNAL_MODULES` (:68), `IMPORT_SEARCH_DEPTH`/`IMPORT_SEARCH_ROOTS` (:72-73), `ALLOWED_SOURCES` (:78). "Exec edges stay a declared, measured limit" (AMENDMENT 2): decide per shape below whether it is an include edge (in contract) or an exec edge (the declared limit), and say so.
- (C) the future-stamp gate (8d50443; the CI fixture fix in 5f6919b) — contract: the ledger note `FUTURE-STAMP GATE LANDED 2026-09-23 02:0xZ` (`todo/BUILD-TASKLIST.md:181`), the incident entry `docs/INCIDENT-LOG.md:16`, build-loop rule 2's gate sentence (`.claude/skills/build-loop/SKILL.md:266`), and the module docstring (`scripts/stamp_check.py:1-21`: the scope, the declared limits, the exit codes). Code: `scripts/stamp_check.py`; the FUTURE-STAMP GATE block of `scripts/hooks/pre-commit` (:111-123); `tests/test_stamp_check.py`; the throwaway-repo fixture in `tests/test_shell_syntax.py` (`_throwaway_repo`).

THE COORDINATOR'S MEASURED SHAPES (appendix B's script, pasted output below; each an INPUT to reproduce and grade): through the real screen in `--root` mode, S0 (the direct-token control) exits 3; S2b (a static import of an unlisted helper) and S5/S6 (a source on a YAML run-block continuation line, a source inside `$( )`) exit 4; but S1 (`sys.path.insert(0, "harness-ports/bin"); import secrets` with a vocabulary-carrying `harness-ports/bin/secrets.py`), S2 (`importlib.import_module("helper")`), S3a (`builtin source scripts/h.sh`), S3b (`command . scripts/h.sh`) and S4 (`eval "$(cat scripts/h.sh)"`) all exit 0 clean while the helper carries the vocabulary. Grade each: is it an in-process include edge the amendment closes (then a defect), or an exec edge inside the declared limit?

BUDGET: a targeted verify of three landings — the named hunks, their controls, and their blast radius on the real hook. Discovery exhaustive inside that scope.

AUTHORIZATION + DO-NOTS:
- The owner's PC; user scope only; no sudo; never touch any server. No network access needed.
- Every experiment in a THROWAWAY repo or tree under `$HOME/tmp-vj10/` (never the PC's tmpfs `/tmp`, AF-AP-112; never the lane tree's own `.git`, never `~/agent-factory`). A throwaway repo gets `core.hooksPath` pointed at a COPY of the PIN's `scripts/hooks/` and copies of the scripts the hook runs; git identity set locally in that repo (`user.name`/`user.email`), `commit.gpgsign=false`.
- The hook's `$PY` is `${AF_VENV:-/root/venv-agent-factory}/bin/python`, falling back to `python3` (`scripts/hooks/pre-commit:13-14`): on this host that is the system `python3`; paste its version. Other hook gates need tooling this host may not have; say which gates ran and which printed a skip, and never count a skipped gate as green.
- Mutants in scratch copies only, restored by copy with the sha verified; a mutant must COMPILE (`python3 -m py_compile` / `bash -n`) and its suite must COLLECT (AF-AP-78).
- pytest with `-p no:cacheprovider --basetemp=$HOME/tmp-vj10/bt`, removed after; one `terminal` call under 420 s.
- The test vocabulary in fixtures is the screen's own closed list; fixture files live only in your throwaway trees. Never commit, push, or touch the ledger, the wiki or any brief; no outward action.

## Items (each with pasted output; SOLID/UNSURE per observation)

### (A) J1-0-R2
A1. **Reproduce the landing gates at the PIN** (identities first): `tests/test_no_laya_in_gates.py tests/test_stamp_check.py tests/test_shell_syntax.py` twice (counts bitwise), the live screen in both modes (`38 files scanned, clean`, rc 0; `scanned` equals the allowlist's entry count), pyflakes on the two scripts and the three tests.
A2. **AMENDMENT 1 through the REAL hook** in a throwaway repo holding the allowlist's shape: (a) the motivating case (a listed gate file replaced in the index by a `120000` symlink to an unlisted file carrying the vocabulary; real `git commit`) → exit 4 `gate-file-not-regular: <path> mode=120000`, commit refused, HEAD unchanged; (b) a `160000` gitlink at a listed path; (c) a `100755` listed file stays clean; (d) on disk (the screen without `--staged`): a symlink → `symlink`; a FIFO and a directory → `not-a-regular-file` (confirm the FIFO is never opened: no hang, paste the time the call took); (e) a regular listed file whose PARENT directory is a symlink (both modes: what does each read, and can the parent symlink point outside the repo?); (f) a listed path that is a regular file in the index but a symlink in the worktree, and the reverse, in `--staged` mode (which one is judged?).
A3. **The positive staged path**: which test pins a CLEAN exit 0 on a well-formed index with an executable (`100755`) gate file? A test suite that only asserts failures would pass a screen that fails everything.

### (B) J1-0-R3
B1. **Reproduce the coordinator's shapes** S0-S6 (appendix B, adapted to `$HOME/tmp-vj10/`) and paste each line.
B2. **Shell include shapes** (a table: caught / clean, and include-edge vs exec-edge): `builtin source x`, `command . x`, `source <(cat x)`, `exec 3<x; . /dev/fd/3`, `. "$(dirname "$0")/x"`, `shopt -s expand_aliases; alias s=source; s x`, a backslash-newline between `source` and its target, `$'...'` quoting around the target, `<<-` heredocs with tab-indented delimiters and quoted delimiters, a `source` inside a function body, `trap '. x' EXIT`, `bash -c '. x'`, `eval ". x"`, `${var#prefix}` followed on the same line by `; . x` (does the scanner read `#` in a parameter expansion as a comment start and hide what follows?), `$(( a # b ))`-style arithmetic, a `case` pattern `x) . y ;;`. For every CLEAN in-process shape, state whether AMENDMENT 2's text ("A `source` or `.` command in any listed non-Python gate file") covers it.
B3. **Python include shapes**: S1 (sys.path + a stdlib-named helper outside `IMPORT_SEARCH_ROOTS`), S2 (`importlib.import_module`), `__import__("x")`, `exec(open("x").read())`, `runpy.run_path("x.py")`, `importlib.util.spec_from_file_location`, an import inside a function, a relative import in a directory without `__init__.py`, a star import, `import a.b.c` where only `a/b.py` exists, a repo `yaml.py` beside a gate (a name in `EXTERNAL_MODULES`: the repo-first search should flag it; confirm), a module deeper than `IMPORT_SEARCH_DEPTH`. Then read the real resolution order (`_import_errors` :338-360) against Python's own for `python3 <gate>` (`sys.path[0]` is the script's directory) and say where they differ.
B4. **The ALLOWED_SOURCES pairs**: both are in `scripts/pc_lane.sh` (`"$ROOT/.pc-bridge.env"`, `"$PC_LANE_BRIDGE_FN"`). The second sources a file named by an ENVIRONMENT variable. Is "neither loads repo code" (the comment at :75-77) a property the screen can see, or a claim about the runtime environment? Grade it. Then: can a different gate file reuse an allowed target text (the pair is (file, target), confirm), and does a whitespace or quoting variant of the target (`"$ROOT"/.pc-bridge.env`, `$ROOT/.pc-bridge.env` unquoted) fall outside the pair and get flagged?
B5. **Mutants** (scratch copy; the killing test NAMED): drop the heredoc skip; drop the quote masking; drop `_LEADING_KEYWORD_RE`; drop the YAML key strip; drop the relative-import branch; `IMPORT_SEARCH_DEPTH` 2 → 1; drop the ambiguity refusal; empty `ALLOWED_SOURCES` (the live screen must then fail on `scripts/pc_lane.sh`: paste it); add `builtin` to the keyword set (does any test notice either way?). A mutant no test kills is a finding or a proven equivalent.

### (C) The stamp gate
C1. **Reproduce**: `tests/test_stamp_check.py` twice (`20 passed` each), and the live pair through the REAL hook in a throwaway repo whose HEAD holds a `todo/BUILD-TASKLIST.md`: a staged future stamp (`date -u -d '+30 min' +'%Y-%m-%d %H:%M'`Z) → the exact refusal line, rc 1, no commit made; a stamp pasted from `date -u` → rc 0.
C2. **Shapes** (a table, each through the real CLI or hook): a renamed plane file (`git mv todo/BUILD-TASKLIST.md todo/X.md` — outside the plane list, so unchecked: is that in scope?) and a rename INTO the plane; a stamp moved from one plane file to another (new in the second file, so checked); the slack boundary (now + 119 s, + 121 s); each form (`YYYY-MM-DD HH:MxZ`, `YYYY-MM-DD HH:MMZ`, `YYYY-MM-DDTHH:MM:SSZ`); lowercase `z`; an offset form (`+00:00`) and a space-separated `UTC`; a stamp inside a fenced code block; invalid instants (`2026-02-30`, `24:00Z`, `12:6xZ`, `12:4x:30Z`); a far-future year typo; `git commit -a`; a partial commit `git commit -m x -- <plane file>` (git gives hooks a temporary index through `GIT_INDEX_FILE`: does `git show :<path>` in the gate's subprocess read it? paste the environment variable the hook sees); `git commit --amend` adding a future stamp; a merge commit (which hook runs on a clean `git merge`, `pre-commit` or `pre-merge-commit`? read `git help hooks` on this host, then run it).
C3. **The bypass**: `SKIP_STAMP_CHECK=1` prints its line and skips only this gate (the never-a-gate screen still runs: prove it with a staged vocabulary violation plus the bypass). Does anything in the repository set `SKIP_STAMP_CHECK` (grep the tree, including `harness-ports/` and `.claude/`), and do the PC lanes' environments carry it (`/proc/<lane pid>/environ`, the NAME only, for the live lanes' pidfiles under `~/agent-factory/.lanes/*/lane.pid` — read, never signal)?
C4. **The clock**: the gate reads this host's clock. Paste `timedatectl` (read-only) and the offset against an HTTP `Date:` header you can read locally (e.g. from OmniRoute's own response headers on 127.0.0.1:20128 — a GET of `/` with `curl -sI`, headers only; never a request that consumes a model). What skew would let a future stamp through, and what skew would refuse a pasted one?
C5. **The fixture in `tests/test_shell_syntax.py`**: `_throwaway_repo` now copies `lint_delta.py`, `no_laya_in_gates.py` and `stamp_check.py` and writes a three-line allowlist. Mutant: drop `stamp_check.py` from the copy list → the positive control reds with `can't open file` (the CI red it fixed)? Then: does the negative control still fail for the EXACT reason (`bash -n failed on bad.sh`) and not for a missing script?

### Common
D1. `python3 scripts/ap_screen.py --tests scripts/no_laya_in_gates.py scripts/stamp_check.py tests/test_no_laya_in_gates.py tests/test_stamp_check.py` (the flag BEFORE the paths): each hit pre-existing at 07ff690 or new?

## Report (`tasks/briefs/laya/VERIFY-J1-0-R23-STAMP-report.md`)
DATA, not prose, one section per component: the reproduction table (claim → instrument → observed → SOLID/UNSURE), the shape tables (A2, B1-B3, C2), the mutant table (B5 + your own), the predicate table (every finding against the five conjuncts), then that component's GATE RECOMMENDATION. A shape you could not run is `NOT run: <reason>`, never omitted. `python3 scripts/report_lint.py --min-refs 15 <your report> --root .` WITHOUT `--map` flags: cite full repo-relative paths (≤ 3 fix rounds, then paste and finish).

## PREMISE — MEASURED at authoring (sandbox @ 5a00d13)
```
$ date -u; git log -1 --format='%h %s' origin/claude/soundbox-kit-migration-iz1jwf | cut -c1-70
2026-09-23T02:46:55Z
5a00d13 transcripts: scrubbed sandbox chat digests (2026-09-23)
$ for f in <boundary>; do sha256(git show 5a00d13:$f)[:16]; lines; done
a8a1e114d32c1528  653 scripts/no_laya_in_gates.py
c911a5bd773e0b2c  655 tests/test_no_laya_in_gates.py
e3db42b85de898a4   49 scripts/gate_files.txt
f8f587f999ae46a0  133 scripts/hooks/pre-commit
a7adc991c1bf0d29  109 scripts/stamp_check.py
f1f463bbae3f3d0f  192 tests/test_stamp_check.py
4ea0979cdfcc166c  103 tests/test_shell_syntax.py
$ git diff --quiet 5a00d13 -- <boundary> && echo 'tree == 5a00d13 on the boundary'
tree == 5a00d13 on the boundary
$ git log --format='%h %s' -3 -- scripts/no_laya_in_gates.py | cut -c1-110
6a6cd4a J1-0-R3: the never-a-gate screen follows its in-process include edges (AMENDMENT 2, AF-AP-120) + the C
5eae256 J1-0-R2: the never-a-gate screen refuses a listed gate file that is not a REGULAR file (VERIFY-J1-0-R1
07ff690 J1-0-R1: the never-a-gate screen's --staged mode made index-consistent (VERIFY-J1-0 B1 + B2, D-031 one
$ git log --format='%h %s' -3 -- scripts/stamp_check.py scripts/hooks/pre-commit | cut -c1-110
8d50443 Future-stamp pre-commit gate (task #135, AF-AP-37's timestamp half): a new ledger-plane stamp later th
98a604a J1-0: the never-a-gate screen (KC-J1's mechanism) — scripts/no_laya_in_gates.py + scripts/gate_files
1309479 hooks: the vendored-manifest gate on pre-commit (staged path under a root) and pre-push (outgoing rang
$ mkdir -p /tmp/vj10/p && python -m pytest tests/test_no_laya_in_gates.py tests/test_stamp_check.py tests/test_shell_syntax.py -q -p no:cacheprovider --basetemp=/tmp/vj10/p/bt | tail -1   (x2)
57 passed in 4.70s
57 passed in 4.88s
$ python3 scripts/no_laya_in_gates.py; python3 scripts/no_laya_in_gates.py --staged
no_laya_in_gates: 38 files scanned, clean
no_laya_in_gates: 38 files scanned, clean
$ grep -n '^def test_' tests/test_no_laya_in_gates.py | wc -l; grep -n '^def test_' tests/test_stamp_check.py | wc -l
33
15
$ grep -n -E '^(ALLOWED_SOURCES|EXTERNAL_MODULES|STRUCTURAL|VOCAB|[A-Z_]+ =)|^def |gate-file-(not-regular|sources|import-)' scripts/no_laya_in_gates.py | cut -c1-150
7:  4   completeness control (gate-file-unlisted, gate-file-missing, gate-file-not-regular,
8:      gate-file-unreadable, gate-file-sources, gate-file-unparseable,
9:      gate-file-import-unlisted, gate-file-import-unresolved or gate-file-import-ambiguous)
38:REGULAR_INDEX_MODES = frozenset(["100644", "100755"])
47:SIMPLE_TOKENS = frozenset([
54:DOTTED_TOKENS = (
62:SELF_PATH = "scripts/no_laya_in_gates.py"
68:EXTERNAL_MODULES = frozenset(["fubuki_os", "jsonschema", "lint", "pyflakes", "yaml"])
72:IMPORT_SEARCH_DEPTH = 2
73:IMPORT_SEARCH_ROOTS = ("scripts", "src")
78:ALLOWED_SOURCES = frozenset([
84:_SOURCE_RE = re.compile(r"^(?:source|\.)[ \t]+(\S.*)$")
85:_LEADING_KEYWORD_RE = re.compile(r"^(?:then|do|else|elif|if|while|until|!)[ \t]+")
86:_HEREDOC_RE = re.compile(r"<<(-?)[ \t]*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2")
88:_YAML_KEY_RE = re.compile(r"^(?:-[ \t]+)?(?:[A-Za-z_][A-Za-z0-9_-]*:[ \t]*)?")
91:def _is_python_gate(entry, content):
99:def _command_segments(content, yaml):
189:def _source_errors(entry, content):
190:    """`gate-file-sources` lines for every command segment that sources a file, unless the
207:        errors.append("gate-file-sources: %s:%d: %s" % (entry, lineno, target))
271:def _package_files(tree, base, parts, names):
298:def _flagged_by_vocabulary(entry, module, names):
307:def _import_errors(entry, content, tree, listed_set):
336:                errors.append("gate-file-import-unresolved: %s:%d imports %s" % (entry, lineno, label))
351:                errors.append("gate-file-import-unresolved: %s:%d imports %s" % (entry, lineno, module))
355:                errors.append("gate-file-import-ambiguous: %s:%d imports %s -> %s" % (entry, lineno, module, where))
360:                errors.append("gate-file-import-unlisted: %s:%d imports %s -> %s" % (entry, lineno, label, path))
365:_TOKEN_RE = re.compile(r"[A-Za-z0-9_-]+")
366:_ID_CHARS = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-")
369:_IMPORT_RE = re.compile(
378:def _check_line(line, is_py):
419:def _read_staged(path):
431:def _read_file(root, path):
442:def _parse_allowlist(text):
453:def _load_allowlist(list_path):
458:def _glob_structural(root):
484:def _glob_structural_staged():
504:def _exists_staged(path):
513:def _index_mode(path):
525:def main():
596:                completeness_errors.append("gate-file-not-regular: %s mode=%s" % (entry, mode))
600:                completeness_errors.append("gate-file-not-regular: %s symlink" % entry)
604:                completeness_errors.append("gate-file-not-regular: %s not-a-regular-file" % entry)
$ grep -n -E 'never-a-gate|no_laya_in_gates|FUTURE-STAMP|stamp_check|SKIP_STAMP_CHECK|SHELL SYNTAX|ADVISORY-EXCLUSION|^PY=|PY=' scripts/hooks/pre-commit | cut -c1-150
13:PY="${AF_VENV:-/root/venv-agent-factory}/bin/python"
14:[ -x "$PY" ] || PY="python3"
96:# SHELL SYNTAX GATE (2026-09-03): a ported hook shipped with a syntax-error tail
111:# FUTURE-STAMP GATE (2026-09-23, AF-AP-37's timestamp half, second bite): a NEW date-prefixed
114:# clock, never typed. Bypass (printed, so it shows in review): SKIP_STAMP_CHECK=1 git commit ...
115:if [ -n "${SKIP_STAMP_CHECK:-}" ]; then
116:  echo "pre-commit: SKIP_STAMP_CHECK set — the future-stamp gate bypassed." >&2
118:  "$PY" "$REPO_ROOT/scripts/stamp_check.py" --staged
125:# ADVISORY-EXCLUSION SCREEN (KC-J1): forbidden vocabulary must never appear
127:"$PY" "$REPO_ROOT/scripts/no_laya_in_gates.py" --staged
130:  echo "COMMIT BLOCKED by the never-a-gate screen (rc=$RC)" >&2
$ sed -n '64,88p' scripts/no_laya_in_gates.py
# ---------- Include edges (AMENDMENT 2) ----------

# Third-party modules a Python gate may import. Closed: a new one is a reviewed change here.
# fubuki_os and lint come from S0-07's pinned fubuki-os checkout, outside this repo.
EXTERNAL_MODULES = frozenset(["fubuki_os", "jsonschema", "lint", "pyflakes", "yaml"])

# Where a first-party import is looked for, besides the importing file's own directory
# and its subdirectories (to this depth).
IMPORT_SEARCH_DEPTH = 2
IMPORT_SEARCH_ROOTS = ("scripts", "src")

# The source edges a gate file may keep: (gate file, the exact target text). Closed: a new
# one is a reviewed change here. Both load no repo code: the first is the untracked bridge
# link file the owner pastes (KEY=VALUE lines), the second the dispatcher tests' fake-bridge seam.
ALLOWED_SOURCES = frozenset([
    ("scripts/pc_lane.sh", '"$ROOT/.pc-bridge.env"'),
    ("scripts/pc_lane.sh", '"$PC_LANE_BRIDGE_FN"'),
])

# A command segment that sources a file, read on the MASKED segment (quoted text replaced).
_SOURCE_RE = re.compile(r"^(?:source|\.)[ \t]+(\S.*)$")
_LEADING_KEYWORD_RE = re.compile(r"^(?:then|do|else|elif|if|while|until|!)[ \t]+")
_HEREDOC_RE = re.compile(r"<<(-?)[ \t]*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\2")
# In YAML a command follows a list dash and a key: `- run: . x` sources x.
_YAML_KEY_RE = re.compile(r"^(?:-[ \t]+)?(?:[A-Za-z_][A-Za-z0-9_-]*:[ \t]*)?")
$ bash <the coordinator's probe script, appendix B>   (sandbox, the real screen at 5a00d13)
[S0 direct token in a listed gate (control)] rc=3 :: scripts/g.sh:2:laya 
[S1 sys.path + stdlib-named helper] rc=0 :: no_laya_in_gates: 1 files scanned, clean 
[S2 importlib.import_module(helper)] rc=0 :: no_laya_in_gates: 1 files scanned, clean 
[S2b static import helper (control)] rc=4 :: gate-file-import-unlisted: scripts/g.py:1 imports helper -> scripts/helper.py 
[S3a builtin source] rc=0 :: no_laya_in_gates: 1 files scanned, clean 
[S3b command .] rc=0 :: no_laya_in_gates: 1 files scanned, clean 
[S4 eval cat] rc=0 :: no_laya_in_gates: 1 files scanned, clean 
[S5 yaml run-block continuation] rc=4 :: gate-file-sources: .github/workflows/w.yml:6: scripts/h.sh 
[S6 source inside $( )] rc=4 :: gate-file-sources: scripts/g.sh:2: scripts/h.sh 
```

### Appendix B — the coordinator's shape probe (`VJ10_BASE=$HOME/tmp-vj10/probe bash <this script>` from the lane tree)
```bash
#!/bin/bash
# The coordinator's include-edge probe: one scratch tree per shape, the REAL screen in --root mode.
SCREEN="$(pwd)/scripts/no_laya_in_gates.py"
BASE="${VJ10_BASE:-/tmp/vj10/probe}"; rm -rf "$BASE"; mkdir -p "$BASE"
mk() { local t="$BASE/$1"; mkdir -p "$t/scripts" "$t/harness-ports/bin"; printf '%s\n' "${@:2}" > "$t/scripts/gate_files.txt"; echo "$t"; }
run() { local t="$1" label="$2"; out="$(python3 "$SCREEN" --root "$t" 2>&1)"; rc=$?; echo "[$label] rc=$rc :: $(echo "$out" | tr '\n' ' ' | cut -c1-200)"; }
# S0 positive control: a listed gate that names the vocabulary directly
t=$(mk s0 scripts/g.sh); printf '#!/bin/bash\necho laya\n' > "$t/scripts/g.sh"; run "$t" "S0 direct token in a listed gate (control)"
# S1 a stdlib-named helper outside the search roots, reached through sys.path
t=$(mk s1 scripts/g.py); printf 'import sys\nsys.path.insert(0, "harness-ports/bin")\nimport secrets\n' > "$t/scripts/g.py"; printf 'X = "laya"\n' > "$t/harness-ports/bin/secrets.py"; run "$t" "S1 sys.path + stdlib-named helper"
# S2 a dynamic import of an unlisted repo helper
t=$(mk s2 scripts/g.py); printf 'import importlib\nm = importlib.import_module("helper")\n' > "$t/scripts/g.py"; printf 'X = "laya"\n' > "$t/scripts/helper.py"; run "$t" "S2 importlib.import_module(helper)"
# S2b the same helper through a static import (control for S2)
t=$(mk s2b scripts/g.py); printf 'import helper\n' > "$t/scripts/g.py"; printf 'X = "laya"\n' > "$t/scripts/helper.py"; run "$t" "S2b static import helper (control)"
# S3 builtin source / command .
t=$(mk s3 scripts/g.sh); printf '#!/bin/bash\nbuiltin source scripts/h.sh\n' > "$t/scripts/g.sh"; printf 'echo laya\n' > "$t/scripts/h.sh"; run "$t" "S3a builtin source"
t=$(mk s3b scripts/g.sh); printf '#!/bin/bash\ncommand . scripts/h.sh\n' > "$t/scripts/g.sh"; printf 'echo laya\n' > "$t/scripts/h.sh"; run "$t" "S3b command ."
# S4 eval of a file's text (an exec edge)
t=$(mk s4 scripts/g.sh); printf '#!/bin/bash\neval "$(cat scripts/h.sh)"\n' > "$t/scripts/g.sh"; printf 'echo laya\n' > "$t/scripts/h.sh"; run "$t" "S4 eval cat"
# S5 a YAML run block with the source on a continuation line
t=$(mk s5 .github/workflows/w.yml); mkdir -p "$t/.github/workflows"; printf 'jobs:\n  a:\n    steps:\n      - run: |\n          echo hi\n          . scripts/h.sh\n' > "$t/.github/workflows/w.yml"; printf 'echo laya\n' > "$t/scripts/h.sh"; run "$t" "S5 yaml run-block continuation"
# S6 a source inside a command substitution
t=$(mk s6 scripts/g.sh); printf '#!/bin/bash\nx=$(. scripts/h.sh; echo ok)\n' > "$t/scripts/g.sh"; printf 'echo laya\n' > "$t/scripts/h.sh"; run "$t" "S6 source inside \$( )"
```
