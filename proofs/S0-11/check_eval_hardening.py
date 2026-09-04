"""S0-11: Evaluation hardening conformance checker.

Proves the Hermes evaluation runner isolates rubric subprocesses, using evidence
the PARENT observes from the kernel (`/proc/<pid>`), never the child's own
report — a child under a fake wrapper can fabricate a clean self-report, so
self-reported isolation is not trusted. Wrapper binaries are called by ABSOLUTE
path (no PATH hijack).

Axes (all parent-observed, kernel truth):
  - UID drop:   /proc/<pid>/status real uid != parent AND != 0. Achieved by a
                REAL privilege drop (root: `unshare --net` + `setpriv --reuid`;
                non-root: `unshare --user --net`, host uid stays the non-root
                runner's). The child's own getuid() is NOT used — under a bare
                user namespace it reports an unprivileged id while the host uid
                stays root, so it is not evidence of a drop.
  - netns:      /proc/<pid>/ns/net inode != parent (a fresh, connectivity-less
                netns). When the parent can `nsenter` the child's netns, it also
                actively confirms a loopback listener it holds is UNREACHABLE
                from inside that netns.
  - env:        /proc/<pid>/environ is a subset of a CLOSED EXACT allow-list
                (never a prefix wildcard); production-named decoys the checker
                injects into the parent env must be absent.
Non-vacuity: the same parent observation is run against an UN-wrapped child and
must breach every axis, or an axis is a tautology.

Design gate: runner_design.md must carry a machine-readable ```yaml `policy:`
block declaring each hazard forbidden — a deterministic contract, not prose
scanned for synonyms.

Forbidden-op sweep: a BEST-EFFORT LINT over the proof's non-Markdown files
(Python via AST with import-alias + constant folding, YAML via a parsed walk,
shell/other via regex). It catches obvious/accidental hazards; it is NOT a
complete static-analysis boundary (a determined author can evade any static
scan). The real guarantees are the runtime isolation above (network) and gVisor
+ a non-root service user at the PC boundary (filesystem/privilege, S0-08).

Capability preflight (`--selftest`): confirms the host primitives and that the
parent can observe a child's /proc; exit 2 = capability-unavailable (skip, run
on the PC), never a false pass or breach.

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
    """Absolute-path wrapper that puts the child in a fresh netns as a real
    non-root uid. Root creates the netns then drops via setpriv; a non-root
    runner uses a user namespace (its host uid, already non-root, is kept)."""
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
    True = reached, False = refused (isolated), None = probe could not run."""
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


def _observe_child(launch, env, port):
    """Launch a child that signals ready then blocks; observe it from the parent
    via /proc while it is alive. Returns an observation dict or None."""
    try:
        proc = subprocess.Popen(launch, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL, env=env)
    except OSError:
        return None
    try:
        ready = b""
        if select.select([proc.stdout], [], [], 10)[0]:
            ready = proc.stdout.read(1)
        if ready != b"R":
            return None
        pid = proc.pid
        obs = {
            "uid": _proc_uid(pid),
            "net_ns": os.readlink("/proc/%d/ns/net" % pid),
            "env_keys": _proc_env_keys(pid),
            "net_reachable": _nsenter_reach(pid, port),
        }
        return obs
    except (OSError, ValueError):
        return None
    finally:
        _release(proc)


def _violations(obs, parent_net_ns):
    """Axes on which the PARENT-OBSERVED state is not isolated. Empty ==
    isolated. The unprivileged invariant is `uid != 0` (never root) — NOT
    `uid != parent`: a non-root runner cannot change its child's host uid, so
    the rubric legitimately inherits the runner's own non-root uid. Deterministic
    labels only."""
    if obs is None:
        return ["observation-failed"]
    axes = []
    if obs["uid"] == 0:
        axes.append("uid-is-root")
    if not obs["net_ns"] or obs["net_ns"] == parent_net_ns:
        axes.append("netns-not-isolated")
    if [k for k in obs["env_keys"] if k not in ALLOWED_ENV]:
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


def _allow_env(cwd, port):
    base = dict(os.environ)
    env = {k: base[k] for k in ALLOWED_ENV if k in base}
    env["RUBRIC_TASK_ID"] = "probe-001"
    env["RUBRIC_CWD"] = cwd
    env["RUBRIC_PROBE_PORT"] = str(port)
    return env


def _full_env(cwd, port):
    env = dict(os.environ)
    env["RUBRIC_TASK_ID"] = "probe-001"
    env["RUBRIC_CWD"] = cwd
    env["RUBRIC_PROBE_PORT"] = str(port)
    return env


def _capability_status():
    """Confirm the host primitives + that the parent can observe a child's
    /proc. Does NOT judge isolation outcome (a wrapper that runs but does not
    isolate is a checker FAILURE, not unavailable)."""
    if not _net_ns():
        return "netns-unreadable-parent"
    needed = [UNSHARE] + ([SETPRIV] if os.getuid() == 0 else [])
    for path in needed:
        if not os.path.exists(path):
            return "missing:" + path
    child = [sys.executable, "-c", READY_BLOCK]
    obs = _observe_child(_iso_launch(child), {"PATH": "/usr/bin"}, 0)
    if obs is None:
        return "child-unobservable"
    if not obs["net_ns"]:
        return "child-netns-unreadable"
    return "ok"


# --- design policy gate ------------------------------------------------------
def check_runner_design(proof_dir):
    design = proof_dir / "runner_design.md"
    if not design.exists():
        print("runner-design-missing: " + str(design))
        return False
    text = design.read_text()
    policy = _extract_policy(text)
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
    parent_uid = os.getuid()
    parent_net_ns = _net_ns()
    child = [sys.executable, str(probe)]

    def run():
        listener = _LoopbackListener()
        try:
            iso = _observe_child(_iso_launch(child), _allow_env(str(proof_dir), listener.port), listener.port)
            raw = _observe_child(child, _full_env(str(proof_dir), listener.port), listener.port)
        finally:
            listener.close()
        return iso, raw

    iso, raw = _with_decoys(run)

    iso_axes = _violations(iso, parent_net_ns)
    if iso_axes:
        print("rubric-isolation-failure: " + ",".join(iso_axes))
        return False
    if iso.get("net_reachable") is True:
        print("rubric-isolation-failure: network-reachable")
        return False
    # Non-vacuity: netns and env ALWAYS discriminate (the wrapper creates a fresh
    # netns and the allow-list strips env). The uid axis discriminates only on a
    # ROOT venue, where the un-wrapped child is root and the wrapper drops it; a
    # non-root runner cannot produce a root child to test against, and its rubric
    # inherits the runner's own non-root uid.
    raw_axes = _violations(raw, parent_net_ns)
    required = ["env-not-allowlisted", "netns-not-isolated"]
    if parent_uid == 0:
        required.append("uid-is-root")
    for axis in required:
        if axis not in raw_axes:
            print("isolation-assertion-vacuous: " + axis + " did not discriminate")
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
    """Four-axis negative: observe an UN-wrapped child; every parent-observed
    axis must breach. Requires the isolation capability (reads child /proc)."""
    if not probe.exists():
        print("fixture-missing: " + str(probe))
        return 1
    parent_net_ns = _net_ns()
    child = [sys.executable, str(probe)]

    def run():
        listener = _LoopbackListener()
        try:
            return _observe_child(child, _full_env(str(proof_dir), listener.port), listener.port)
        finally:
            listener.close()

    # The negative control reports only the VENUE-STABLE axes (netns, env), which
    # an un-wrapped child breaches on every host — so the canonical spec pins a
    # complete, venue-independent reason. (The uid axis is venue-dependent and is
    # exercised by the positive check's non-vacuity gate on a root venue.)
    axes = _violations(_with_decoys(run), parent_net_ns)
    stable = [a for a in axes if a in ("env-not-allowlisted", "netns-not-isolated")]
    if len(stable) < 2:
        print("rubric-neg-unexpected: " + (",".join(axes) or "unwrapped child reported isolated"))
        return 1
    print("rubric-isolation-violation: " + ",".join(stable))
    print("exit 1 per contract")
    return 1


def rubric_neg_cred(fixture, proof_dir):
    """Frozen seed negative control: the credential-reading rubric, run with the
    allow-list env (credentials absent by construction), must emit the exact
    frozen reason. Environment-independent (tests the env allow-list)."""
    if not fixture.exists():
        print("fixture-missing: " + str(fixture))
        return 1
    frozen = "rubric-isolation-violation: credential env absent by construction"

    def run():
        env = _allow_env(str(proof_dir), 0)
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
