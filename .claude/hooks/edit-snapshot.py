#!/usr/bin/env python3
"""EDIT-SNAPSHOT hook (owner directive 2026-08-25): after every Edit/Write,
hand the coordinator an automatic snapshot of what the edit touched — the
enclosing symbol(s), their upstream blast radius (GitNexus), and a screen of
the new code against the ANTI-PATTERN REGISTRY's mechanical signatures
(docs/INCIDENT-LOG.md) — so per-edit awareness is presented, not remembered.

Contract: PostToolUse hook on Edit|Write. Reads the hook JSON on stdin,
prints a compact snapshot to stdout, ALWAYS exits 0 — this hook informs,
it never blocks (a broken instrument must not stop an edit; the reviewer
loop stays the enforcement point). Every external probe is time-bounded.

Extend the AP screen when a new registry row lands (bug-echo mandate:
registry and this screen move together).
"""
import os
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

_EMIT_OPEN = re.compile(r"emit_(?:runtime_event|event|decision|metric)\s*\(")
_NONE_KWARG = re.compile(r"=\s*None\s*(?:#.*)?$")


class _EmitNoneKwarg:
    """AP-59 tell with a balanced-paren scan (TN3-F7, 2026-09-02).

    The regex form `emit_x\\((?:[^)]|\\n)*?=\\s*None` cannot cross the `)` of an
    earlier kwarg that is itself a call (`per_fold_coverage=list(...)`), so it
    was blind to every real emit — including the one the registry cites. This
    walks the emit's argument list and flags a DEPTH-1 kwarg whose value is the
    literal None. Same `.search()` surface as a compiled regex.
    """

    def search(self, text):
        for m in _EMIT_OPEN.finditer(text):
            depth, buf = 1, []
            i = m.end()
            while i < len(text) and depth:
                c = text[i]
                if c in "([{":
                    depth += 1
                elif c in ")]}":
                    depth -= 1
                if depth == 1 and c == ",":
                    if _NONE_KWARG.search("".join(buf).strip()):
                        return m
                    buf = []
                elif depth >= 1:
                    buf.append(c)
                i += 1
            if _NONE_KWARG.search("".join(buf).rstrip(") \n").strip()):
                return m
        return None


# Mechanical signatures distilled from the ANTI-PATTERN REGISTRY (id: regex,
# message). Only patterns that are cheaply greppable in a diff hunk belong
# here; judgment-class rows stay in review.
AP_SCREEN = [
    ("AP-44", re.compile(r"(run_gate|gate_final_population)\((?![^)]*deflator_n_override)"),
     "gate call without deflator_n_override — weak-default gate mints the strict 'certified' spelling (AP-44); thread deflator/threshold/admission or state the weak arm in the label"),
    ("AP-1", re.compile(r"os\.environ\.get|getenv\("),
     "env read in edited code — config channel? resolve ONCE at construction, thread explicitly"),
    ("AP-2", re.compile(r"os\.environ\[[^\]]+\]\s*=|environ\.setdefault\("),
     "os.environ WRITE — process-global and sticky; almost always wrong mid-run"),
    ("AP-3", re.compile(r"\bisnan\b(?![^\n]*isfinite)"),
     "isnan without isfinite nearby — inf rides through; guard the WHOLE unusable class"),
    ("AP-31", re.compile(r"(Integer|Real)\(bounds="),
     "numeric-bounded search variable — if its values are category labels/slots, use Choice (router bug class)"),
    ("AP-32", re.compile(r"(sha256|md5|hash)\("),
     "hashing in edited code — is the hashed form EXACTLY what the store holds? (stamp-store mismatch class)"),
    ("AP-24", re.compile(r"except\s+(Exception|BaseException)?\s*:\s*(pass|continue)\b"),
     "swallowed exception — fail-soft must be fail-LOUD"),
    # AF-AP-12 (2026-09-03): jsonschema registers `date-time` only when rfc3339-validator imports;
    # a FormatChecker built without asserting its checkers leaves every `format` keyword unchecked.
    ("AF-AP-12", re.compile(r"FormatChecker\(\)"),
     "FormatChecker() without asserting the needed checkers are registered — an unregistered `format` is silently unchecked; assert presence and fail loud (AF-AP-12)"),
    ("AP-39", re.compile(r"(api_key|api_secret|auth_token|bearer_token)\s*:\s*Optional\[str\]\s*=\s*None"),
     "optional credential param — verify a PRODUCTION call site supplies it (cred-param-without-supplier class)"),
    ("AP-x", re.compile(r"int\(round\("),
     "int(round(...)) coercion — silent rounding masked a data-path defect once; prefer strict"),
    ("AP-36", re.compile(r"^\s+from\s+agent_factory\.[a-z_.]+\s+import\s"),
     "indented from-import — if the function uses this name on an EARLIER line, it is UnboundLocalError-on-arrival (late-local-import shadow; prefer the module-level import)"),
    ("AP-34", re.compile(r'(open\([^)]*,\s*["\']w|shutil\.copy2?\()[^\n]*(prod|_path|batch_|stages|runner)'),
     "write/copy toward a possibly-PRODUCTION path — a test/audit must mutate a tmp_path COPY, never the real module (crash window hard-wires the mutant; RA-8 F1)"),
    ("AP-50", re.compile(r'["\'][a-z_]+_applied["\']\s*:'),
     "provenance '*_applied' stamp — stamp the value only when the transform actually RAN, never the requested param (provenance-stamps-intent class)"),
    ("AP-51", re.compile(r"byte-identical|bitwise-identical", re.IGNORECASE),
     "byte/bitwise-identity claim — if this diff adds a dataclass field feeding an asdict sink, the claim is FALSE (fields serialize as null keys); say 'additive keys, null when OFF'"),
    # ECHO-V4 (2026-09-02). AP-59 misses None nested inside a payload dict
    # (depth-1 kwargs only); AP-54 is the noisiest row — fires on the
    # OFF-path analysis scripts too, informational only.
    ("AP-59", _EmitNoneKwarg(),
     "decision emit with a literal-None kwarg — if that field is a CONJUNCT of the decision, thread the value or NARRATE the absence in `reason` (UNMEASURED, not zero); pattern to copy: stages.py:3088-3104 (AP-59)"),
    ("AP-54", re.compile(r"generate_signals\((?![^)]*(?:flat_specialist_enabled|\*\*))"),
     "generate_signals without flat_specialist_enabled and without a **flags splat — resolve_blend_flags returns ONLY the 4 _BLEND_FLAG_KEYS, so an un-merged **blend_flags does NOT carry the flat flag; check the sibling callees in this same function (AP-54)"),
]

# V6 (2026-09-02). Test files skip AP_SCREEN (production-only), so AP-66 gets its
# own screen: a direct attribute reassignment on something other than self/cls
# (`EM.emit = spy`, `setattr(mod, "emit", spy)`) with no restore leaks into every
# later test in the process. monkeypatch.setattr never matches (method call).
# AP-63/64/65 have no regex shape — the registry names their instruments.
TEST_SCREEN = [
    # AF-AP-11 (2026-09-03): a repo CLI spawned through its shebang runs on whatever python3 PATH
    # finds — the PC's system python carried jsonschema and minted a green the venv could not.
    ("AF-AP-11", re.compile(r"subprocess\.(?:run|Popen|check_output|check_call|call)\(\s*\[\s*str\("),
     "CLI spawned through its shebang — inherits the host interpreter's site-packages, not the declared toolchain; put sys.executable first (AF-AP-11)"),
    # AF-AP-33 (2026-09-05): an unmanaged OmniRoute squatted :20128 serving the wrong DB while
    # /api/health said 200 — port-level health is blind to WHICH instance answers.
    ("AF-AP-33", re.compile(r"""/(?:api/)?health["']"""),
     "health-endpoint-only liveness — a squatting duplicate answers 200 while serving the wrong dataset; also assert ownership (pid -> cgroup/pidfile) and a dataset-discriminating probe (AF-AP-33)"),
    # AF-AP-34 (2026-09-04): four `pkill -x buzz-relay` aimed at an isolated relay restarted the
    # owner's production relay container — a bare binary name is shared across installs.
    ("AF-AP-34", re.compile(r"\b(?:pkill|killall)\b|\bkill\b[^\n]*\$\(\s*pgrep"),
     "name-based process kill — matches other installs and container processes on a shared host; kill the PID from YOUR pidfile after /proc/<pid>/exe or the cgroup confirms ownership (AF-AP-34)"),
    # AF-AP-35 (2026-09-04): a redaction built from the secret's VALUE echoed the value into the log.
    ("AF-AP-35", re.compile(r"(?:re\.sub|\.replace)\(\s*(?:re\.escape\()?\s*\w*(?:key|secret|token|password|passwd)\w*\b", re.I),
     "redaction keyed on a secret's VALUE — the value lands in argv/output/transcript; redact by KEY NAME or pattern class and dry-run on a dummy (AF-AP-35)"),
    ("AP-66", re.compile(r"^\s*(?:(?!self\.|cls\.)[A-Za-z_][\w.]*\.\w+\s*=\s*(?!=)|setattr\(\s*(?!self\b|cls\b)\w+\s*,)", re.MULTILINE),
     "direct attribute reassignment in a test — leaks into every later test unless restored; use monkeypatch.setattr or a finally-restoring context manager (AP-66)"),
    # TN3-F4 (2026-09-02): a blanket except in a test hollows any call-count
    # assertion — the loop aborting on item 1 satisfies `call_count == 1` too.
    ("AP-70", re.compile(r"except\s*(?:\([^)\n]*\bException\b[^)\n]*\)|Exception)\s*:\s*\n\s*(?:pass|continue)\b"),
     "blanket except swallowing the run under test — a call-count/once assertion after it cannot tell hoisted from aborted; size the fixture and drop the swallow, or add an iteration counter (AP-70)"),
]

MAX_SYMBOLS = 2
PROBE_TIMEOUT = 8

# Rows whose tell needs the WHOLE file, not just the hunk (ECHO 2026-09-02,
# I3g: AP-60 free-variable-resolved-only-in-caller, AP-61 np/pd used with
# no module-level import). Both are hard-blocked at commit time by
# scripts/hooks/pre-commit (pyflakes delta); this is the same detector at
# edit time. A regex "is the name bound anywhere in the file" tell was tried
# first and MISSED the real AP-60 shape (the name WAS bound — inside main(),
# a different scope), so scoping is left to pyflakes, not re-implemented.
_NP_PD = re.compile(r"(?<![\w.])(np|pd)\.")
_VENV_PY = os.environ.get("AF_VENV", "/root/venv-agent-factory") + "/bin/python"  # PC lanes export AF_VENV


def _pyflakes_msgs(py: str, text: str) -> dict:
    """pyflakes messages for one source text, line numbers dropped (a hunk
    above shifts every line; the delta compares WHAT, not WHERE)."""
    p = subprocess.run([py, "-m", "pyflakes"], input=text, capture_output=True,
                       text=True, timeout=PROBE_TIMEOUT)
    out: dict = {}
    for l in p.stdout.splitlines():
        parts = l.split(":", 3)  # <stdin>:LINE:COL: message
        msg = parts[3].strip() if len(parts) == 4 else l.strip()
        out[msg] = out.get(msg, 0) + 1
    return out


def pyflakes_delta(fp: str, src: str) -> list[str]:
    """NEW pyflakes hits in this file vs its HEAD version. [] when the venv
    pyflakes is absent or anything fails — a tell, never a blocker."""
    if not Path(_VENV_PY).exists():
        return []
    try:
        root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                              cwd=Path(fp).parent, timeout=PROBE_TIMEOUT).stdout.strip()
        rel = str(Path(fp).resolve().relative_to(root)) if root else fp
        shown = subprocess.run(["git", "show", f"HEAD:{rel}"], capture_output=True, text=True,
                               cwd=root or None, timeout=PROBE_TIMEOUT)
        base = _pyflakes_msgs(_VENV_PY, shown.stdout) if shown.returncode == 0 else {}
        now = _pyflakes_msgs(_VENV_PY, src)
    except Exception:
        return []
    new = {m: n - base.get(m, 0) for m, n in now.items() if n > base.get(m, 0)}
    out = []
    for m in sorted(new):
        if m.startswith("undefined name") and m.split("'")[1] not in ("np", "pd"):
            tag = "AP-60 "
        elif m.startswith("undefined name") or "imported but unused" in m:
            tag = "AP-61 "
        else:
            tag = "LINT  "
        out.append(f"  {tag} NEW pyflakes hit vs HEAD: {m}" + (f" (x{new[m]})" if new[m] > 1 else "")
                   + " — the pre-commit hook will BLOCK on this")
    return out


def file_aware_screen(hunk: str, src: str) -> list[str]:
    out = []
    mods = {"np": "numpy", "pd": "pandas"}
    for alias in sorted({m.group(1) for m in _NP_PD.finditer(hunk)}):
        if not re.search(rf"^import {mods[alias]} as {alias}\b", src, re.M):
            out.append(f"  AP-61  `{alias}.` used but no module-level `import {mods[alias]} as {alias}` in THIS file — "
                       "an import in a sibling module / docstring / embedded script string does not bind it (AP-61)")
    return out


def enclosing_symbols(src: str, needle: str) -> list[str]:
    """Names of the innermost def/class containing the first occurrence of
    needle's first non-empty line. Best-effort; [] on any failure."""
    first_line = next((l for l in needle.splitlines() if l.strip()), "")
    if not first_line:
        return []
    pos = src.find(first_line.strip())
    if pos < 0:
        return []
    lineno = src.count("\n", 0, pos) + 1
    try:
        tree = ast.parse(src)
    except SyntaxError:
        return []
    hits: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            end = getattr(node, "end_lineno", node.lineno)
            if node.lineno <= lineno <= end:
                hits.append((end - node.lineno, node.name))
    hits.sort()  # innermost (smallest span) first
    return [name for _, name in hits[:MAX_SYMBOLS]]


def chronology(symbol: str, fp: str, n: int = 4) -> list[str]:
    """Last n edits to the function (git log -L funcname), one line each —
    the owner's 'histogram at a glance'. [] on any failure/timeout."""
    try:
        out = subprocess.run(
            ["git", "log", "-n", str(n), "--format=%h %ad %s", "--date=short",
             "-L", f":{symbol}:{fp}", "--no-patch"],
            capture_output=True, text=True, timeout=PROBE_TIMEOUT,
        ).stdout
        return [l for l in out.splitlines() if l.strip()][:n]
    except Exception:
        return []


def file_chronology(fp: str, n: int = 3) -> list[str]:
    try:
        out = subprocess.run(
            ["git", "log", "-n", str(n), "--format=%h %ad %s", "--date=short", "--", fp],
            capture_output=True, text=True, timeout=PROBE_TIMEOUT,
        ).stdout
        return [l for l in out.splitlines() if l.strip()][:n]
    except Exception:
        return []


def gitnexus_impact(symbol: str) -> str:
    try:
        out = subprocess.run(
            ["gitnexus", "impact", symbol],
            capture_output=True, text=True, timeout=PROBE_TIMEOUT,
        ).stdout
        d = json.loads(out[out.index("{"):])
        if d.get("risk") in (None, "UNKNOWN"):
            return f"{symbol}: not in index (new symbol? index rebuilding)"
        s = d.get("summary", {}) or {}
        return (f"{symbol}: risk {d.get('risk')} · {s.get('direct', '?')} direct callers · "
                f"{s.get('processes_affected', '?')} flows")
    except Exception:
        if Path("/tmp/gitnexus-analyze.lock").exists():
            return f"{symbol}: index rebuilding (post-commit reanalyze) — impact unmapped THIS edit; re-check before commit"
        return f"{symbol}: impact unavailable (instrument down — unmapped, not safe)"


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0
    tin = payload.get("tool_input") or {}
    tool = payload.get("tool_name", "")
    fp = tin.get("file_path", "")
    if not fp.endswith(".py") or "sandbox-kit/" in fp:
        return 0
    if "/tests/" in fp:
        # test files get only the test-specific screen (AP-66); no impact/history
        if tool == "Read":
            return 0
        hunk = tin.get("new_string") or tin.get("content") or ""
        hits = [f"  {ap_id:6s}{msg}" for ap_id, rx, msg in TEST_SCREEN if rx.search(hunk)]
        if hits:
            print(f"EDIT SNAPSHOT · {Path(fp).name}\n  registry screen (TELLS, not verdicts):")
            print("\n".join(hits))
        return 0
    p = Path(fp)
    if not p.is_file():
        return 0

    # READ branch (owner directive 2026-08-25, "histogram at a glance"): a
    # lightweight file-level chronology on every production-code read — the
    # full per-symbol treatment stays on edits, where the stakes are.
    if tool == "Read":
        hist = file_chronology(fp)
        if hist:
            print(f"READ CONTEXT · {p.name} — last {len(hist)} changes "
                  f"(full story: scripts/why.sh {fp} [symbol]):")
            for h in hist:
                print(f"  {h}")
        return 0

    new_code = tin.get("new_string") or tin.get("content") or ""
    if not new_code.strip():
        return 0
    try:
        src = p.read_text()
    except Exception:
        return 0

    lines = [f"EDIT SNAPSHOT · {p.name}"]
    syms = enclosing_symbols(src, new_code)
    if syms:
        for s in syms:
            lines.append("  impact  " + gitnexus_impact(s))
        hist = chronology(syms[0], fp)
        if hist:
            lines.append(f"  history {syms[0]} — last {len(hist)} edits "
                         f"(why: scripts/why.sh {fp} {syms[0]}):")
            lines.extend(f"    {h}" for h in hist)
    else:
        lines.append("  impact  module-level edit (no enclosing symbol resolved)")
        hist = file_chronology(fp)
        if hist:
            lines.append("  history file — last changes:")
            lines.extend(f"    {h}" for h in hist)

    flagged = []
    for ap_id, rx, msg in AP_SCREEN:
        if rx.search(new_code):
            flagged.append(f"  {ap_id:6s}{msg}")
    flagged.extend(file_aware_screen(new_code, src))
    flagged.extend(pyflakes_delta(fp, src))
    if flagged:
        lines.append("  registry screen (verify each — these are TELLS, not verdicts):")
        lines.extend(flagged)
    else:
        lines.append("  registry screen: no mechanical anti-pattern tells in this hunk")

    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
