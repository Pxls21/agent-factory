"""S0-11: Evaluation hardening conformance checker.

Proves the Hermes evaluation runner isolates rubric subprocesses, using evidence
the PARENT observes from the kernel (`/proc/<pid>`), never the child's own
report. Wrapper binaries are called by ABSOLUTE path (no PATH hijack).

Axes (all parent-observed, kernel truth):
  - UID:     /proc/<pid>/status real uid != 0 (never root). Not `!= parent`: a
             non-root runner cannot change its child's host uid, so the rubric
             inherits the runner's own non-root uid.
  - netns:   /proc/<pid>/ns/net inode != parent (a fresh netns).
  - cwd:     /proc/<pid>/cwd is a fresh working directory != the parent's cwd
             (the production workspace); the runner assigns a per-rubric temp dir.
  - env:     /proc/<pid>/environ is a subset of a CLOSED EXACT allow-list;
             production-named decoys the checker injects must be absent.
  - network: an ACTIVE paired control — the parent holds a loopback listener in
             its own netns and `nsenter`s each child's netns: the WRAPPED child
             must find it UNREACHABLE (isolated) and the UN-wrapped child must
             find it REACHABLE (the discriminator flips). A venue that cannot run
             `nsenter` (non-root) DEFERS via the preflight — the discriminator is
             never accepted as fail-open (None).
Non-vacuity: the same parent observation is run against an UN-wrapped child and
must breach netns, cwd, and env on every venue (and uid on a root venue, where
an un-wrapped child is actually root).

Design gate: runner_design.md must carry a machine-readable ```yaml `policy:`
block declaring each hazard forbidden.

Forbidden-op sweep: a BEST-EFFORT LINT (Python AST + YAML parse + regex). Not a
complete static-analysis boundary; the real guarantees are the runtime isolation
above and gVisor + a non-root service user at the PC boundary (S0-08).

Capability preflight (`--selftest`): confirms the host primitives AND that the
parent can observe a child's /proc AND run the `nsenter` network discriminator;
exit 2 = capability-unavailable (defer to a capable venue). Every namespace-
reading leg (`<proof-dir>`, `--rubric-neg`) runs this preflight and defers with
exit 2, so the canonical runner defers consistently. The env-only frozen
credential leg (`--rubric-neg-cred`) needs no namespaces and runs everywhere.

Usage:
  check_eval_hardening.py <proof-dir>
  check_eval_hardening.py --selftest
  check_eval_hardening.py --rubric-neg <probe> <proof-dir>
  check_eval_hardening.py --rubric-neg-cred <fixture> <proof-dir>

Exit 0 + "PASS"; 1 + reason on a real breach; 2 on capability-unavailable.
Output is byte-deterministic (no volatile inode/pid/port/path values printed).
"""
import ast
import os
import re
import select
import socket
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

ENV_ALLOWLIST = frozenset({"PATH", "HOME", "LANG", "LC_ALL", "LC_CTYPE", "TMPDIR"})
RUBRIC_ALLOWED = frozenset({"RUBRIC_TASK_ID", "RUBRIC_CWD", "RUBRIC_PROBE_PORT"})
ALLOWED_ENV = ENV_ALLOWLIST | RUBRIC_ALLOWED

DECOY_CREDENTIALS = {
    "OMNIROUTE_INTERNAL_API_KEY": "decoy-omniroute-do-not-use",
    "BUZZ_PRIVATE_KEY": "decoy-buzz-do-not-use",
    "STORAGE_ENCRYPTION_KEY": "decoy-storage-do-not-use",
}

UNSHARE = "/usr/bin/unshare"
SETPRIV = "/usr/bin/setpriv"
NSENTER = "/usr/bin/nsenter"
DROP_UID = "65534"  # nobody
DROP_GID = "65534"  # nogroup
READY_BLOCK = "import sys; sys.stdout.write('R'); sys.stdout.flush(); sys.stdin.read(1)"

HAZARDS = ("host_networking", "recursive_chmod_777", "production_credential_passing")


# --- parent-observed isolation ----------------------------------------------
def _net_ns():
    try:
        return os.readlink("/proc/self/ns/net")
    except OSError:
        return ""


def _iso_launch(child_cmd):
    """Absolute-path wrapper: fresh netns as a real non-root uid. Root creates
    the netns then drops via setpriv; a non-root runner uses a user namespace
    (its own non-root host uid is kept, which already satisfies uid != 0)."""
    if os.getuid() == 0:
        return [UNSHARE, "--net", "--", SETPRIV, "--reuid", DROP_UID,
                "--regid", DROP_GID, "--clear-groups", "--"] + child_cmd
    return [UNSHARE, "--user", "--net", "--"] + child_cmd


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


def _proc_uid(pid):
    with open("/proc/%d/status" % pid) as handle:
        for line in handle:
            if line.startswith("Uid:"):
                return int(line.split()[1])  # real uid
    raise OSError("no Uid line")


def _proc_env_keys(pid):
    with open("/proc/%d/environ" % pid, "rb") as handle:
        raw = handle.read()
    return sorted({entry.split(b"=", 1)[0].decode("utf-8", "replace")
                   for entry in raw.split(b"\x00") if entry})


def _nsenter_reach(pid, port):
    """Parent-driven: enter the child's netns and try the parent's listener.
    True = reached, False = refused (isolated), None = probe could not run
    (never accepted as a pass — a None is a capability gap, handled by defer)."""
    if os.getuid() != 0 or not os.path.exists(NSENTER):
        return None
    probe = ("import socket,sys\n"
             "try:\n s=socket.create_connection(('127.0.0.1',%d),timeout=2);"
             "s.close();print('REACHED')\n"
             "except OSError:\n print('REFUSED')" % port)
    try:
        r = subprocess.run([NSENTER, "--net=/proc/%d/ns/net" % pid, "--",
                            sys.executable, "-c", probe],
                           capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if "REACHED" in r.stdout:
        return True
    if "REFUSED" in r.stdout:
        return False
    return None


def _release(proc):
    try:
        if proc.stdin:
            proc.stdin.write(b"x")
            proc.stdin.close()
        proc.wait(timeout=5)
    except (OSError, subprocess.TimeoutExpired):
        try:
            proc.kill()
        except OSError:
            pass


def _observe_child(launch, base_env, port, fresh_cwd):
    """Launch a child that signals ready then blocks; observe it from the parent
    via /proc while it is alive. `fresh_cwd` True runs it in a per-rubric temp
    directory (the isolated runner behaviour); False lets it inherit the parent's
    cwd (the un-isolated control). Returns an observation dict or None."""
    ctx = tempfile.TemporaryDirectory(prefix="rubric-cwd-") if fresh_cwd else None
    cwd = ctx.name if ctx else None
    env = dict(base_env)
    env["RUBRIC_TASK_ID"] = "probe-001"
    env["RUBRIC_PROBE_PORT"] = str(port)
    env["RUBRIC_CWD"] = cwd if cwd else os.getcwd()
    try:
        proc = subprocess.Popen(launch, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL, cwd=cwd, env=env)
    except OSError:
        return None
    try:
        ready = b""
        if select.select([proc.stdout], [], [], 10)[0]:
            ready = proc.stdout.read(1)
        if ready != b"R":
            return None
        pid = proc.pid
        return {
            "uid": _proc_uid(pid),
            "net_ns": os.readlink("/proc/%d/ns/net" % pid),
            "cwd": os.readlink("/proc/%d/cwd" % pid),
            "env_keys": _proc_env_keys(pid),
            "net_reachable": _nsenter_reach(pid, port),
        }
    except (OSError, ValueError):
        return None
    finally:
        _release(proc)
        if ctx:
            ctx.cleanup()


def _violations(obs, parent_net_ns, parent_cwd):
    """Axes on which the PARENT-OBSERVED /proc state is not isolated. Empty ==
    isolated on these axes. The network axis is a paired control handled
    separately. Deterministic labels only."""
    if obs is None:
        return ["observation-failed"]
    axes = []
    if obs["uid"] == 0:
        axes.append("uid-is-root")
    if not obs["net_ns"] or obs["net_ns"] == parent_net_ns:
        axes.append("netns-not-isolated")
    if not obs["cwd"] or obs["cwd"] == parent_cwd:
        axes.append("cwd-not-isolated")
    if [k for k in obs["env_keys"] if k not in ALLOWED_ENV]:
        axes.append("env-not-allowlisted")
    return sorted(axes)


def _stable_breaches(obs, parent_net_ns, parent_cwd):
    """The venue-independent breach axes an un-wrapped child shows on every host
    (netns, cwd, env). The uid axis is venue-dependent (root only) and network is
    a paired positive control, so neither is in the canonical negative reason."""
    return [a for a in _violations(obs, parent_net_ns, parent_cwd)
            if a in ("cwd-not-isolated", "env-not-allowlisted", "netns-not-isolated")]


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


def _allow_env():
    base = dict(os.environ)
    return {k: base[k] for k in ENV_ALLOWLIST if k in base}


def _full_env():
    return dict(os.environ)


def _capability_status():
    """Confirm the host primitives + that the parent can observe a child's /proc
    AND run the nsenter network discriminator. Does NOT judge isolation outcome."""
    if not _net_ns():
        return "netns-unreadable-parent"
    needed = [UNSHARE, NSENTER] + ([SETPRIV] if os.getuid() == 0 else [])
    for path in needed:
        if not os.path.exists(path):
            return "missing:" + path
    child = [sys.executable, "-c", READY_BLOCK]
    listener = _LoopbackListener()
    try:
        obs = _observe_child(_iso_launch(child), {"PATH": "/usr/bin"}, listener.port, True)
    finally:
        listener.close()
    if obs is None:
        return "child-unobservable"
    if not obs["net_ns"]:
        return "child-netns-unreadable"
    if obs["net_reachable"] is None:
        return "nsenter-unavailable"  # the network discriminator cannot run here
    return "ok"


# --- design policy gate ------------------------------------------------------
def check_runner_design(proof_dir):
    design = proof_dir / "runner_design.md"
    if not design.exists():
        print("runner-design-missing: " + str(design))
        return False
    policy = _extract_policy(design.read_text())
    if policy is None:
        print("runner-design-no-policy-block: missing machine-readable ```yaml policy: block")
        return False
    for hazard in HAZARDS:
        value = str(policy.get(hazard, "")).strip().lower()
        if value not in ("forbidden", "false", "no", "denied"):
            print("runner-design-policy-not-forbidding: " + hazard + "=" + repr(policy.get(hazard)))
            return False
    return True


def _extract_policy(text):
    for match in re.finditer(r"```ya?ml\s*\n(.*?)```", text, re.DOTALL | re.IGNORECASE):
        try:
            import yaml
            doc = yaml.safe_load(match.group(1))
        except Exception:
            continue
        if isinstance(doc, dict) and isinstance(doc.get("policy"), dict):
            return doc["policy"]
    return None


# --- forbidden-op lint (best-effort; not the boundary) -----------------------
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


def _fold_int(node, int_consts):
    if isinstance(node, ast.Constant) and isinstance(node.value, int) and not isinstance(node.value, bool):
        return node.value
    if isinstance(node, ast.Name) and node.id in int_consts:
        return int_consts[node.id]
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.BitOr, ast.Add)):
        left = _fold_int(node.left, int_consts)
        right = _fold_int(node.right, int_consts)
        if left is not None and right is not None:
            return left | right if isinstance(node.op, ast.BitOr) else left + right
    return None


def _strings_of(node, str_lists):
    out = []
    for sub in ast.walk(node):
        if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
            out.append(sub.value)
        if isinstance(sub, ast.Name) and sub.id in str_lists:
            out.extend(str_lists[sub.id])
    return out


def _python_prohibited(text):
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return _text_prohibited(text)

    mod_aliases = {"subprocess": "subprocess", "os": "os"}
    from_shell = set()
    from_chmod = set()
    int_consts = {}
    str_lists = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in ("subprocess", "os"):
                    mod_aliases[alias.asname or alias.name] = alias.name
        elif isinstance(node, ast.ImportFrom):
            if node.module == "subprocess":
                for alias in node.names:
                    if alias.name in ("run", "call", "Popen", "check_call", "check_output"):
                        from_shell.add(alias.asname or alias.name)
            if node.module == "os":
                for alias in node.names:
                    if alias.name in ("system",):
                        from_shell.add(alias.asname or alias.name)
                    if alias.name == "chmod":
                        from_chmod.add(alias.asname or alias.name)
        elif isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
            name = node.targets[0].id
            folded = _fold_int(node.value, int_consts)
            if folded is not None:
                int_consts[name] = folded
            elif isinstance(node.value, (ast.List, ast.Tuple)):
                strings = [e.value for e in node.value.elts
                           if isinstance(e, ast.Constant) and isinstance(e.value, str)]
                if strings:
                    str_lists[name] = strings

    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = _call_name(node.func)
        parts = name.split(".") if name else []
        canon = None
        if len(parts) >= 2 and parts[0] in mod_aliases:
            canon = mod_aliases[parts[0]] + "." + ".".join(parts[1:])
        short = parts[-1] if parts else ""
        is_chmod = short in ("chmod", "fchmod", "lchmod") or name in from_chmod
        is_shell = canon in ("subprocess.run", "subprocess.call", "subprocess.Popen",
                             "subprocess.check_call", "subprocess.check_output",
                             "os.system") or name in from_shell
        if is_chmod:
            for arg in list(node.args) + [kw.value for kw in node.keywords]:
                mode = _fold_int(arg, int_consts)
                if mode is not None and (mode & 0o2):
                    return "world-writable chmod (call)"
        if is_shell:
            hit = _text_prohibited(" ".join(_strings_of(node, str_lists)))
            if hit:
                return hit + " (shell call)"
    return None


def _yaml_walk(node):
    if isinstance(node, dict):
        for key, value in node.items():
            kl = str(key).lower()
            if kl in ("network_mode", "network"):
                if "host" in str(value).strip().strip("\"'").lower():
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


def check_forbidden_ops(proof_dir):
    for path in sorted(proof_dir.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        suffix = path.suffix.lower()
        if suffix == ".md":
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


# --- isolation check ---------------------------------------------------------
def check_rubric_isolation(proof_dir):
    probe = proof_dir / "fixtures" / "rubric_probe.py"
    if not probe.exists():
        print("rubric-probe-missing: " + str(probe))
        return False
    parent_net_ns = _net_ns()
    parent_cwd = os.getcwd()
    child = [sys.executable, str(probe)]

    def run():
        listener = _LoopbackListener()
        try:
            iso = _observe_child(_iso_launch(child), _allow_env(), listener.port, True)
            raw = _observe_child(child, _full_env(), listener.port, False)
        finally:
            listener.close()
        return iso, raw

    iso, raw = _with_decoys(run)

    iso_axes = _violations(iso, parent_net_ns, parent_cwd)
    if iso_axes:
        print("rubric-isolation-failure: " + ",".join(iso_axes))
        return False
    # Active network control: the isolated child's netns must REFUSE the parent's
    # listener (False), never fail open on a missing observation (None/True).
    if iso["net_reachable"] is not False:
        print("rubric-isolation-failure: network-reachable")
        return False

    raw_axes = _violations(raw, parent_net_ns, parent_cwd)
    required = ["cwd-not-isolated", "env-not-allowlisted", "netns-not-isolated"]
    if os.getuid() == 0:
        required.append("uid-is-root")
    for axis in required:
        if axis not in raw_axes:
            print("isolation-assertion-vacuous: " + axis + " did not discriminate")
            return False
    # Non-vacuity of the network axis: the un-wrapped child must REACH the listener.
    if raw["net_reachable"] is not True:
        print("isolation-assertion-vacuous: network did not discriminate")
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
    """Namespace-reading negative control: observe an UN-wrapped child; the
    venue-stable /proc axes (netns, cwd, env) must all breach. Gated by the same
    preflight as the positive so it DEFERS (exit 2) on an incapable venue."""
    status = _capability_status()
    if status != "ok":
        print("isolation-capability-unavailable: " + status)
        return 2
    if not probe.exists():
        print("fixture-missing: " + str(probe))
        return 1
    parent_net_ns = _net_ns()
    parent_cwd = os.getcwd()
    child = [sys.executable, str(probe)]

    def run():
        listener = _LoopbackListener()
        try:
            return _observe_child(child, _full_env(), listener.port, False)
        finally:
            listener.close()

    stable = _stable_breaches(_with_decoys(run), parent_net_ns, parent_cwd)
    if len(stable) < 3:
        print("rubric-neg-unexpected: " + (",".join(stable) or "unwrapped child reported isolated"))
        return 1
    print("rubric-isolation-violation: " + ",".join(stable))
    print("exit 1 per contract")
    return 1


def rubric_neg_cred(fixture, proof_dir):
    """Frozen seed negative control: the credential-reading rubric, run with the
    allow-list env (credentials absent by construction), must emit the exact
    frozen reason. Environment-only — needs no namespaces, runs on every venue."""
    if not fixture.exists():
        print("fixture-missing: " + str(fixture))
        return 1
    frozen = "rubric-isolation-violation: credential env absent by construction"

    def run():
        env = _allow_env()
        env["RUBRIC_TASK_ID"] = "neg-cred"
        try:
            return subprocess.run([sys.executable, str(fixture)], capture_output=True,
                                  text=True, timeout=15, env=env)
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
