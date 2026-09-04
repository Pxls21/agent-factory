"""S0-11: Evaluation hardening conformance checker.

Proves the Hermes evaluation runner isolates rubric subprocesses on four axes
and that the isolation actually FIRED (no tautology greens):

  1. Runner design doc covers the three AlphaEval hazards and does not assert any
     of them as enabled/required (semantic inversion guard).

  2. Rubric isolation — a probe run through ``unshare --user --net`` must report,
     on every axis, and a well-formed report is mandatory (missing evidence is a
     failure, never a silent pass):
       - UID drop:       probe uid != parent uid AND uid != 0 (never root)
       - netns identity: probe /proc/self/ns/net inode != parent's (fresh netns)
       - network:        a loopback listener the checker holds in its own netns
                         is UNREACHABLE from the probe (the netns blocks it)
       - environment:    the probe env is a subset of a CLOSED allow-list — an
                         EXACT set of names (ENV_ALLOWLIST + a fixed RUBRIC_* set),
                         never a prefix wildcard. Production-named decoys are
                         injected and must be absent.
     Non-vacuity gate: the same predicate is re-run against the probe WITHOUT the
     wrapper; every axis must flip to breached, or an axis is a tautology.
     Capability preflight (``--selftest``): the positive check first proves the
     host can actually create+read the namespaces it consumes; where it cannot,
     the checker returns exit 2 ("capability unavailable", NOT a pass, NOT a
     breach) so the proof is skipped there and runs on the PC/gVisor host.

  3. Forbidden-op sweep — STRUCTURED, not a regex list: Python via AST (real
     ``os.chmod(…, 0o777)`` calls and shell-command string args), YAML via a
     parsed walk (``network_mode: host``, ``hostNetwork: true`` incl. bool True),
     shell/other text via regex. Every non-Markdown file is scanned, the checker
     itself included (AST ignores its own pattern string literals, so no
     self-exclusion hole).

Filesystem containment is NOT asserted here (a separate cwd is not a jail; the
sandbox userns does not enforce host ownership) — it is delivered by gVisor + a
mapped user namespace at the PC/production boundary (standing rule 11, S0-08) and
listed not-verified in runner_design.md.

Usage:
  check_eval_hardening.py <proof-dir>
  check_eval_hardening.py --selftest
  check_eval_hardening.py --rubric-neg <probe> <proof-dir>
  check_eval_hardening.py --rubric-neg-cred <fixture> <proof-dir>

Exit 0 + "PASS"; 1 + reason on a real breach; 2 on capability-unavailable.
Output is byte-deterministic (no volatile inode/port/path values printed).
"""
import ast
import json
import os
import re
import socket
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

# Closed environment allow-list: the ONLY names that may reach a rubric process.
# Not a blacklist, and not a prefix wildcard — an EXACT set. Everything else,
# every present or future credential whatever it is named, is stripped.
ENV_ALLOWLIST = frozenset({"PATH", "HOME", "LANG", "LC_ALL", "LC_CTYPE", "TMPDIR"})
RUBRIC_ALLOWED = frozenset({"RUBRIC_TASK_ID", "RUBRIC_CWD", "RUBRIC_PROBE_PORT"})
ALLOWED_ENV = ENV_ALLOWLIST | RUBRIC_ALLOWED

# Production-realistic credential names a NAME blacklist would miss. Injected into
# the parent env for the run so the allow-list is proven to strip a present
# credential (positive) and the non-isolated control is proven to leak it.
DECOY_CREDENTIALS = {
    "OMNIROUTE_INTERNAL_API_KEY": "decoy-omniroute-do-not-use",
    "BUZZ_PRIVATE_KEY": "decoy-buzz-do-not-use",
    "STORAGE_ENCRYPTION_KEY": "decoy-storage-do-not-use",
}

ISO_WRAPPER = ["unshare", "--user", "--net", "--"]

HAZARD_COVERAGE = {
    "host-networking": ("no host network", "network isolation", "netns",
                        "unshare --net", "clone_newnet"),
    "chmod-777": ("chmod 777", "permission hardening", "recursive permission"),
    "credential-passing": ("credential pass", "credential isolation", "strip",
                           "allow-list", "allowlist"),
}

# Hazard-ENABLING assertions in the design doc: a doc that says a hazard is
# enabled/required/allowed (or isolation disabled) is not a passing design.
_DESIGN_INVERSIONS = [
    re.compile(r"(host network\w*|network isolation)[^.\n]{0,40}\b(disabled|enabled|required|allowed|permitted|off)\b", re.I),
    re.compile(r"chmod\s*-?[rR]?\s*0?777[^.\n]{0,40}\b(required|allowed|enabled|permitted|needed)\b", re.I),
    re.compile(r"credential[^.\n]{0,30}\b(passing|passed|sharing|shared)\b[^.\n]{0,40}\b(enabled|required|allowed|permitted)\b", re.I),
    re.compile(r"(credential (isolation|stripping|allow-?list))[^.\n]{0,20}\b(disabled|removed|off)\b", re.I),
]

# --- forbidden-op detection --------------------------------------------------
# World-writable octal shell modes: the world (last) digit carries the write bit.
_CHMOD_OCTAL = re.compile(r"chmod\b[^\n]*?\b[0-7]?[0-7]{2}[2367]\b")
_CHMOD_SYM_TOKEN = re.compile(r"\b([ugoa]*)[+=]([rwxXst]*)")
_HOST_NET = re.compile(
    r"(--network[=\s]+host\b|--net[=\s]+host\b"
    r"|network_mode\s*[:=]\s*[\"']?host\b"
    r"|(?:^|\s)network\s*:\s*[\"']?host\b"
    r"|hostNetwork\s*:\s*true\b)",
    re.IGNORECASE | re.MULTILINE,
)


def _symbolic_world_write(text):
    for line in text.splitlines():
        idx = line.find("chmod")
        if idx < 0:
            continue
        for who, perms in _CHMOD_SYM_TOKEN.findall(line[idx + len("chmod"):]):
            if "w" in perms and (who == "" or "o" in who or "a" in who):
                return True
    return False


def _text_prohibited(text):
    if _CHMOD_OCTAL.search(text):
        return "world-writable chmod (octal)"
    if _symbolic_world_write(text):
        return "world-writable chmod (symbolic)"
    if _HOST_NET.search(text):
        return "host networking"
    return None


def _call_name(func):
    parts = []
    node = func
    while isinstance(node, ast.Attribute):
        parts.append(node.attr)
        node = node.value
    if isinstance(node, ast.Name):
        parts.append(node.id)
    return ".".join(reversed(parts))


_SHELL_CALLS = {"os.system", "subprocess.run", "subprocess.call", "subprocess.Popen",
                "subprocess.check_call", "subprocess.check_output"}


def _python_prohibited(text):
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return _text_prohibited(text)
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node.func)
        short = name.split(".")[-1] if name else ""
        if short in ("chmod", "fchmod", "lchmod"):
            for arg in list(node.args) + [kw.value for kw in node.keywords]:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, int) and (arg.value & 0o2):
                    return "world-writable chmod (os.chmod)"
        if name in _SHELL_CALLS:
            strings = [n.value for n in ast.walk(node)
                       if isinstance(n, ast.Constant) and isinstance(n.value, str)]
            hit = _text_prohibited(" ".join(strings))
            if hit:
                return hit + " (shell call)"
    return None


def _yaml_walk(node):
    if isinstance(node, dict):
        for key, value in node.items():
            kl = str(key).lower()
            if kl in ("network_mode", "network") and str(value).strip().strip("\"'").lower() == "host":
                return "host networking (yaml)"
            if kl == "hostnetwork":
                if value is True or str(value).strip().lower() in ("true", "yes", "on"):
                    return "host networking (yaml)"
            if isinstance(value, str):
                hit = _text_prohibited(value)
                if hit:
                    return hit + " (yaml)"
            hit = _yaml_walk(value)
            if hit:
                return hit
    elif isinstance(node, list):
        for item in node:
            hit = _yaml_walk(item)
            if hit:
                return hit
    elif isinstance(node, str):
        return _text_prohibited(node)
    return None


def _yaml_prohibited(text):
    try:
        import yaml
        for doc in yaml.safe_load_all(text):
            hit = _yaml_walk(doc)
            if hit:
                return hit
    except Exception:
        return _text_prohibited(text)
    return None


# --- isolation probe machinery ----------------------------------------------
def _net_ns():
    try:
        return os.readlink("/proc/self/ns/net")
    except OSError:
        return ""


class _LoopbackListener:
    def __init__(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(("127.0.0.1", 0))
        self.port = self._sock.getsockname()[1]
        self._sock.listen(16)
        threading.Thread(target=self._serve, daemon=True).start()

    def _serve(self):
        while True:
            try:
                conn, _ = self._sock.accept()
                conn.close()
            except OSError:
                return

    def close(self):
        try:
            self._sock.close()
        except OSError:
            pass


def _probe_env(allowlisted, cwd, port):
    base = dict(os.environ)  # decoys were injected into os.environ for the run
    if allowlisted:
        env = {k: base[k] for k in ALLOWED_ENV if k in base}
    else:
        env = base
    env["RUBRIC_TASK_ID"] = "probe-001"
    env["RUBRIC_CWD"] = cwd
    env["RUBRIC_PROBE_PORT"] = str(port)
    return env


def _run_probe(probe, isolated, port):
    with tempfile.TemporaryDirectory(prefix="rubric-") as cwd:
        cmd = (ISO_WRAPPER if isolated else []) + [sys.executable, str(probe)]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=20,
                               cwd=cwd, env=_probe_env(isolated, cwd, port))
        except (OSError, subprocess.TimeoutExpired):
            return None
        if r.returncode != 0:
            return None
        try:
            return json.loads(r.stdout)
        except json.JSONDecodeError:
            return None


def _report_defects(report):
    if not isinstance(report, dict):
        return ["report-not-dict"]
    defects = []
    if not isinstance(report.get("uid"), int):
        defects.append("report-uid-missing")
    if not isinstance(report.get("net_ns"), str) or not report.get("net_ns"):
        defects.append("report-netns-missing")
    if not isinstance(report.get("env_keys"), list):
        defects.append("report-envkeys-missing")
    if not isinstance(report.get("listener_reachable"), bool):
        defects.append("report-reachability-missing")
    return defects


def _violations(report, parent_uid, parent_net_ns):
    """Axes on which the report is NOT isolated. Empty == fully isolated. A
    malformed report (missing mandatory evidence) is itself a set of defects,
    never a silent pass. Deterministic labels only."""
    defects = _report_defects(report)
    if defects:
        return sorted(defects)
    axes = []
    if report["uid"] == parent_uid or report["uid"] == 0:
        axes.append("uid-not-dropped")
    if report["net_ns"] == parent_net_ns:
        axes.append("netns-not-isolated")
    if report["listener_reachable"] is not False:
        axes.append("network-reachable")
    if [k for k in report["env_keys"] if k not in ALLOWED_ENV]:
        axes.append("env-not-allowlisted")
    return sorted(axes)


def _with_decoys(fn):
    saved = {k: os.environ.get(k) for k in DECOY_CREDENTIALS}
    os.environ.update(DECOY_CREDENTIALS)
    try:
        return fn()
    finally:
        for k, v in saved.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def _capability_status():
    """Exercise every primitive the positive checker consumes: parent netns
    readable, `unshare --user --net` runs, child netns + uid readable. Returns
    "ok" or a reason. Does NOT judge isolation OUTCOME (a pass-through wrapper
    that runs but does not isolate is a checker FAILURE, not unavailable)."""
    if not _net_ns():
        return "netns-unreadable-parent"
    probe = ("import os,json;"
             "print(json.dumps({'uid':os.getuid(),"
             "'ns':os.readlink('/proc/self/ns/net')}))")
    try:
        r = subprocess.run(ISO_WRAPPER + [sys.executable, "-c", probe],
                           capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        return "unshare-unavailable"
    if r.returncode != 0:
        return "unshare-rc-" + str(r.returncode)
    try:
        d = json.loads(r.stdout)
    except json.JSONDecodeError:
        return "probe-no-report"
    if not d.get("ns"):
        return "netns-unreadable-child"
    if not isinstance(d.get("uid"), int):
        return "uid-unreadable"
    return "ok"


def check_runner_design(proof_dir):
    design = proof_dir / "runner_design.md"
    if not design.exists():
        print("runner-design-missing: " + str(design))
        return False
    text = design.read_text()
    lowered = text.lower()
    for hazard_name, needles in HAZARD_COVERAGE.items():
        if not any(n in lowered for n in needles):
            print("runner-design-incomplete: missing coverage of " + hazard_name)
            return False
    for pattern in _DESIGN_INVERSIONS:
        if pattern.search(text):
            print("runner-design-inverts-hazard: a hazard is asserted enabled/required/disabled")
            return False
    return True


def check_rubric_isolation(proof_dir):
    probe = proof_dir / "fixtures" / "rubric_probe.py"
    if not probe.exists():
        print("rubric-probe-missing: " + str(probe))
        return False
    parent_uid = os.getuid()
    parent_net_ns = _net_ns()

    def run():
        listener = _LoopbackListener()
        try:
            iso = _run_probe(probe, True, listener.port)
            raw = _run_probe(probe, False, listener.port)
        finally:
            listener.close()
        return iso, raw

    iso, raw = _with_decoys(run)

    iso_axes = _violations(iso, parent_uid, parent_net_ns)
    if iso_axes:
        print("rubric-isolation-failure: " + ",".join(iso_axes))
        return False
    raw_axes = _violations(raw, parent_uid, parent_net_ns)
    for axis in ("uid-not-dropped", "netns-not-isolated",
                 "network-reachable", "env-not-allowlisted"):
        if axis not in raw_axes:
            print("isolation-assertion-vacuous: " + axis + " did not discriminate")
            return False
    return True


def check_forbidden_ops(proof_dir):
    for path in sorted(proof_dir.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        suffix = path.suffix.lower()
        if suffix == ".md":  # documentation names the hazards on purpose
            continue
        text = path.read_text(errors="replace")
        if suffix == ".py":
            label = _python_prohibited(text)
        elif suffix in (".yml", ".yaml"):
            label = _yaml_prohibited(text)
        else:
            label = _text_prohibited(text)
        if label:
            print("forbidden-op: " + str(path.relative_to(proof_dir)) + ": " + label)
            return False
    return True


def positive(proof_dir):
    status = _capability_status()
    if status != "ok":
        print("isolation-capability-unavailable: " + status)
        return 2
    if not check_runner_design(proof_dir):
        return 1
    if not check_rubric_isolation(proof_dir):
        return 1
    if not check_forbidden_ops(proof_dir):
        return 1
    print("PASS")
    return 0


def rubric_neg(probe, proof_dir):
    """Four-axis negative: run the probe WITHOUT the wrapper; every axis must be
    breached. Environment-independent (no userns needed for the unwrapped run)."""
    if not probe.exists():
        print("fixture-missing: " + str(probe))
        return 1
    parent_uid = os.getuid()
    parent_net_ns = _net_ns()

    def run():
        listener = _LoopbackListener()
        try:
            return _run_probe(probe, False, listener.port)
        finally:
            listener.close()

    axes = _violations(_with_decoys(run), parent_uid, parent_net_ns)
    if not axes:
        print("rubric-neg-unexpected-pass: unwrapped probe reported isolated")
        return 1
    print("rubric-isolation-violation: " + ",".join(axes))
    print("exit 1 per contract")
    return 1


def rubric_neg_cred(fixture, proof_dir):
    """Frozen seed negative control: run the credential-reading fixture with the
    allow-list env (credentials absent by construction) and require the exact
    frozen reason. Environment-independent (tests the env allow-list, not netns)."""
    if not fixture.exists():
        print("fixture-missing: " + str(fixture))
        return 1
    frozen = "rubric-isolation-violation: credential env absent by construction"

    def run():
        with tempfile.TemporaryDirectory(prefix="rubric-cred-") as cwd:
            try:
                return subprocess.run(
                    [sys.executable, str(fixture)], capture_output=True, text=True,
                    timeout=15, cwd=cwd, env=_probe_env(True, cwd, 0))
            except (OSError, subprocess.TimeoutExpired):
                return None

    result = _with_decoys(run)
    if result is None:
        print("rubric-neg-cred-failed: fixture did not run")
        return 1
    combined = result.stdout + result.stderr
    if result.returncode == 0:
        print("rubric-neg-cred-unexpected-pass: credential leaked into rubric env")
        return 1
    if frozen not in combined:
        print("rubric-neg-cred-wrong-reason: " + repr(result.stdout))
        return 1
    print(frozen)
    print("exit 1 per contract")
    return 1


def main():
    argv = sys.argv[1:]
    if not argv:
        print("usage: check_eval_hardening.py <proof-dir>")
        print("       check_eval_hardening.py --selftest")
        print("       check_eval_hardening.py --rubric-neg <probe> <proof-dir>")
        print("       check_eval_hardening.py --rubric-neg-cred <fixture> <proof-dir>")
        return 1

    if argv[0] == "--selftest":
        status = _capability_status()
        print(status)
        return 0 if status == "ok" else 2
    if argv[0] == "--rubric-neg":
        if len(argv) != 3:
            print("usage: check_eval_hardening.py --rubric-neg <probe> <proof-dir>")
            return 1
        return rubric_neg(Path(argv[1]).resolve(), Path(argv[2]).resolve())
    if argv[0] == "--rubric-neg-cred":
        if len(argv) != 3:
            print("usage: check_eval_hardening.py --rubric-neg-cred <fixture> <proof-dir>")
            return 1
        return rubric_neg_cred(Path(argv[1]).resolve(), Path(argv[2]).resolve())

    proof_dir = Path(argv[0]).resolve()
    if not proof_dir.is_dir():
        print("proof-dir-missing: " + str(proof_dir))
        return 1
    return positive(proof_dir)


if __name__ == "__main__":
    sys.exit(main())
