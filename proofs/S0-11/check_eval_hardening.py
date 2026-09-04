"""S0-11: Evaluation hardening conformance checker.

Proves that the Hermes evaluation runner isolates rubric subprocesses on the
four axes the AlphaEval hazards demand, and that the isolation actually FIRED
(no tautology greens). Asserts:

  1. Runner design doc covers the three AlphaEval hazards (host networking,
     recursive chmod 777, production credential passing).

  2. Rubric isolation — a probe run through the real wrapper
     ``unshare --user --net`` must report, on every axis:
       - UID drop:      probe uid != parent uid (privilege dropped, not root)
       - netns identity: probe /proc/self/ns/net inode != parent's (fresh netns)
       - network:        a loopback listener the checker holds in its own netns
                         is UNREACHABLE from the probe (the netns blocks it)
       - environment:    the probe's env is a subset of an ALLOW-LIST — no
                         credential-shaped or unexpected variable survives,
                         including production-named decoys injected for the run.
     Non-vacuity gate: the SAME predicate is run against the probe WITHOUT the
     wrapper; every axis must flip to "breached" there. An axis that does not
     discriminate is a tautology and fails the proof
     (``isolation-assertion-vacuous``). This kills the pass-through-``unshare``,
     real-credential-name, and 1.1.1.1-tautology mutants by construction.

  3. Grep sweep — zero recursive/world-writable ``chmod`` (octal or symbolic)
     and zero host-networking directives (``--network host``,
     ``network_mode: host``, ``hostNetwork: true``, ...) in the proof's
     executable/config surface. All files are scanned except Markdown docs
     (which name the hazards on purpose) and this checker itself.

Filesystem containment is NOT asserted here: a separate cwd is not a jail, and
the sandbox userns does not enforce host file ownership. Real FS containment is
delivered by gVisor + a mapped user namespace at the PC/production boundary
(standing rule 11) and is listed as not-verified-in-sandbox in runner_design.md.

Usage:
  check_eval_hardening.py <proof-dir>
  check_eval_hardening.py --rubric-neg <probe> <proof-dir>

Exit 0 + "PASS" on success; exit 1 + reason on failure. Output is
byte-deterministic (volatile inode/port/path values are never printed).
"""
import json
import os
import socket
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

# Environment ALLOW-LIST (not a blacklist): only these names, plus any RUBRIC_*
# runner variable, may reach a rubric process. Everything else — every present
# or future credential, whatever it is named — is stripped by construction.
ENV_ALLOWLIST = frozenset({"PATH", "HOME", "LANG", "LC_ALL", "LC_CTYPE", "TMPDIR"})
RUBRIC_PREFIX = "RUBRIC_"

# Production-realistic credential names that a NAME blacklist would miss. Injected
# into the parent environment for the run so the allow-list is proven to strip a
# credential that is actually present (positive) and the non-isolated control is
# proven to leak it (negative). None end in _SECRET/_TOKEN/_CREDENTIAL.
DECOY_CREDENTIALS = {
    "OMNIROUTE_INTERNAL_API_KEY": "decoy-omniroute-do-not-use",
    "BUZZ_PRIVATE_KEY": "decoy-buzz-do-not-use",
    "STORAGE_ENCRYPTION_KEY": "decoy-storage-do-not-use",
}

ISO_WRAPPER = ["unshare", "--user", "--net", "--"]

HAZARD_COVERAGE = {
    "host-networking": (
        "no host network", "network isolation", "netns",
        "unshare --net", "clone_newnet",
    ),
    "chmod-777": (
        "chmod 777", "permission hardening", "recursive permission",
    ),
    "credential-passing": (
        "credential pass", "credential isolation", "strip", "allow-list",
        "allowlist",
    ),
}

# --- Prohibited-pattern detection (grep sweep) -------------------------------
import re  # noqa: E402  (kept next to the patterns it defines)

# World-writable octal modes: the world (last) octal digit carries the write
# bit -> digit in {2,3,6,7}. Matches 777, 0777, 666, 662; NOT 644, 755, 600.
_CHMOD_OCTAL = re.compile(r"chmod\b[^\n]*?\b[0-7]?[0-7]{2}[2367]\b")
# Symbolic chmod tokens: [who][+=][perms]; flagged when write is granted to
# others/all (who contains o or a, or is empty = "all" subject to umask).
_CHMOD_SYM_TOKEN = re.compile(r"\b([ugoa]*)[+=]([rwxXst]*)")
_HOST_NET = re.compile(
    r"(--network[=\s]+host\b"
    r"|--net[=\s]+host\b"
    r"|network_mode\s*[:=]\s*[\"']?host\b"
    r"|(?:^|\s)network\s*:\s*[\"']?host\b"
    r"|hostNetwork\s*:\s*true\b)",
    re.MULTILINE,
)


def _symbolic_world_write(text: str) -> bool:
    for line in text.splitlines():
        idx = line.find("chmod")
        if idx < 0:
            continue
        rest = line[idx + len("chmod"):]
        for who, perms in _CHMOD_SYM_TOKEN.findall(rest):
            if "w" not in perms:
                continue
            if who == "" or "o" in who or "a" in who:
                return True
    return False


def _prohibited(text: str):
    if _CHMOD_OCTAL.search(text):
        return "world-writable chmod (octal)"
    if _symbolic_world_write(text):
        return "world-writable chmod (symbolic)"
    if _HOST_NET.search(text):
        return "host networking"
    return None


# --- isolation probe machinery ----------------------------------------------
def _net_ns() -> str:
    try:
        return os.readlink("/proc/self/ns/net")
    except OSError:
        return ""


class _LoopbackListener:
    """A TCP listener in the checker's own netns; reachable only by a process
    that shares that netns (i.e. one the wrapper did NOT isolate)."""

    def __init__(self):
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(("127.0.0.1", 0))
        self.port = self._sock.getsockname()[1]
        self._sock.listen(16)
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

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


def _probe_env(allowlisted: bool, cwd: str, port: int) -> dict:
    base = dict(os.environ)  # DECOY_CREDENTIALS were injected into os.environ
    if allowlisted:
        env = {k: base[k] for k in ENV_ALLOWLIST if k in base}
        env.update({k: v for k, v in base.items() if k.startswith(RUBRIC_PREFIX)})
    else:
        env = base
    env["RUBRIC_TASK_ID"] = "probe-001"
    env["RUBRIC_CWD"] = cwd
    env["RUBRIC_PROBE_PORT"] = str(port)
    return env


def _run_probe(probe: Path, isolated: bool, port: int):
    """Run the probe; return its parsed report dict, or None on failure."""
    with tempfile.TemporaryDirectory(prefix="rubric-") as cwd:
        cmd = (ISO_WRAPPER if isolated else []) + [sys.executable, str(probe)]
        env = _probe_env(allowlisted=isolated, cwd=cwd, port=port)
        try:
            r = subprocess.run(cmd, capture_output=True, text=True,
                               timeout=20, cwd=cwd, env=env)
        except (OSError, subprocess.TimeoutExpired):
            return None
        if r.returncode != 0:
            return None
        try:
            report = json.loads(r.stdout)
        except json.JSONDecodeError:
            return None
        report["_cwd_root"] = cwd
        return report


def _violations(report: dict, parent_uid: int, parent_net_ns: str):
    """Axes on which the reported state is NOT isolated. Empty == fully isolated.
    Deterministic labels only (no volatile inode/port/path values)."""
    axes = []
    if report is None:
        return ["probe-no-report"]
    if report.get("uid") == parent_uid:
        axes.append("uid-not-dropped")
    ns = report.get("net_ns", "")
    if ns == "" or ns == parent_net_ns:
        axes.append("netns-not-isolated")
    if report.get("listener_reachable") is not False:
        axes.append("network-reachable")
    extra = [k for k in report.get("env_keys", [])
             if k not in ENV_ALLOWLIST and not k.startswith(RUBRIC_PREFIX)]
    if extra:
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


def check_runner_design(proof_dir: Path) -> bool:
    design = proof_dir / "runner_design.md"
    if not design.exists():
        print("runner-design-missing: " + str(design))
        return False
    text = design.read_text().lower()
    for hazard_name, needles in HAZARD_COVERAGE.items():
        if not any(n in text for n in needles):
            print("runner-design-incomplete: missing coverage of " + hazard_name)
            return False
    return True


def check_rubric_isolation(proof_dir: Path) -> bool:
    probe = proof_dir / "fixtures" / "rubric_probe.py"
    if not probe.exists():
        print("rubric-probe-missing: " + str(probe))
        return False

    parent_uid = os.getuid()
    parent_net_ns = _net_ns()

    def run():
        listener = _LoopbackListener()
        try:
            iso = _run_probe(probe, isolated=True, port=listener.port)
            raw = _run_probe(probe, isolated=False, port=listener.port)
        finally:
            listener.close()
        return iso, raw

    iso, raw = _with_decoys(run)

    # Positive: the wrapped probe must be isolated on every axis.
    iso_axes = _violations(iso, parent_uid, parent_net_ns)
    if iso_axes:
        print("rubric-isolation-failure: " + ",".join(iso_axes))
        return False

    # Non-vacuity: the SAME predicate must flag the unwrapped probe as breached
    # on every axis, or an axis is a tautology.
    raw_axes = _violations(raw, parent_uid, parent_net_ns)
    for axis in ("uid-not-dropped", "netns-not-isolated",
                 "network-reachable", "env-not-allowlisted"):
        if axis not in raw_axes:
            print("isolation-assertion-vacuous: " + axis + " did not discriminate")
            return False

    return True


def check_grep_sweep(proof_dir: Path) -> bool:
    for path in sorted(proof_dir.rglob("*")):
        if not path.is_file():
            continue
        if path.name == "check_eval_hardening.py":
            continue
        if path.suffix == ".md":  # documentation names the hazards on purpose
            continue
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(errors="replace")
        label = _prohibited(text)
        if label:
            rel = path.relative_to(proof_dir)
            print("grep-sweep-violation: " + str(rel) + ": " + label)
            return False
    return True


def rubric_neg(probe: Path, proof_dir: Path) -> int:
    """Negative control: run the probe WITHOUT the wrapper; the isolation
    predicate must report a violation (isolation genuinely broken)."""
    if not probe.exists():
        print("fixture-missing: " + str(probe))
        return 1

    parent_uid = os.getuid()
    parent_net_ns = _net_ns()

    def run():
        listener = _LoopbackListener()
        try:
            return _run_probe(probe, isolated=False, port=listener.port)
        finally:
            listener.close()

    raw = _with_decoys(run)
    axes = _violations(raw, parent_uid, parent_net_ns)
    if not axes:
        print("rubric-neg-unexpected-pass: unwrapped probe reported isolated")
        return 1
    print("rubric-isolation-violation: " + ",".join(axes))
    print("exit 1 per contract")
    return 1


def main():
    if len(sys.argv) < 2:
        print("usage: check_eval_hardening.py <proof-dir>")
        print("       check_eval_hardening.py --rubric-neg <probe> <proof-dir>")
        return 1

    if sys.argv[1] == "--rubric-neg":
        if len(sys.argv) != 4:
            print("usage: check_eval_hardening.py --rubric-neg <probe> <proof-dir>")
            return 1
        return rubric_neg(Path(sys.argv[2]).resolve(), Path(sys.argv[3]).resolve())

    proof_dir = Path(sys.argv[1]).resolve()
    if not proof_dir.is_dir():
        print("proof-dir-missing: " + str(proof_dir))
        return 1

    if not check_runner_design(proof_dir):
        return 1
    if not check_rubric_isolation(proof_dir):
        return 1
    if not check_grep_sweep(proof_dir):
        return 1

    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
