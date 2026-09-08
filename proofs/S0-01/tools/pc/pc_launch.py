#!/usr/bin/env python3
"""S0-01 leg launcher — runs ON THE OWNER'S PC, detached, one buzz-acp per leg.

Contract v2.1 producer for: env.json, argv.txt, runtime-identity.json (merge), startup-line.txt,
hermes-model.txt, hermes-config.sha256, buzz-acp.pid, buzz-acp.exit, backend-healthz-before.json,
manifest-pre.* (via pc_manifest.sh, detached).

Secret handling (AF-AP-35 / owner rule "never pass keys in argv"): every secret is READ FROM A FILE
into this process and handed to buzz-acp through the Popen env dict only. Nothing secret is printed,
and nothing secret appears in any argv (the v1/v2 shell launcher put the keys into `bash -c "..."`
argv, visible in /proc/*/cmdline — this file replaces it).

Detached invocation (the caller returns immediately; poll <framedir>/launch.ready):
  setsid /usr/bin/python3 /home/rocco/agent-factory/proofs/S0-01/tools/pc/pc_launch.py \
      --leg run-1 --model s0-01-pong </dev/null > /home/rocco/s0-01-pinned/.markers/v2-run-1.launch.log 2>&1 &
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request

# The launcher lives in the PC clone of this repo; the pin module sits three directories up.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import pins  # noqa: E402  (the single pin module; the launch argv comes from it verbatim)
# Resolved ONCE, here, and threaded explicitly from main() (never re-read from os.environ deeper down): the
# S0-01 default, or the tree another proof declares through $S0_01_HERMES_HOME. pins.hermes_home() validates
# the override and exits 64 if it does not name a directory; it deliberately does NOT move
# pins.PINNED_HERMES_HOME, which is what the checker compares a captured leg's env.json against.
HERMES_HOME = pins.hermes_home()
BASE = os.path.dirname(HERMES_HOME)                      # /home/rocco/s0-01-pinned
REPO = os.path.abspath(os.path.join(os.path.dirname(pins.PINNED_TEE_PATH), "..", "..", ".."))  # /home/rocco/agent-factory
HERMES_ENV = os.path.join(pins.PINNED_HOME, ".hermes", "profiles", "agentfactory", ".env")

HEX64 = re.compile(r"[0-9a-f]{64}")
ANSI = re.compile(r"\x1b\[[0-9;]*m")


def utc_now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def read_kv(path, key):
    """Read KEY=VALUE from a dotenv-style file; strip quotes/CR. Never echo the value."""
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\r\n")
            if line.startswith(key + "="):
                return line[len(key) + 1:].strip().strip('"').strip("'")
    raise SystemExit(f"pc_launch: {key} not found in {path}")


def alive_pinned_buzz(pidfile):
    try:
        pid = int(open(pidfile).read().strip())
    except (OSError, ValueError):
        return None
    try:
        exe = os.readlink(f"/proc/{pid}/exe")
    except OSError:
        return None
    return pid if exe == pins.PINNED_BUZZ_ACP_EXE_REALPATH else None


def masked_log_text(raw_path):
    data = open(raw_path, "rb").read().replace(b"\x00", b"").decode("utf-8", errors="replace")
    data = ANSI.sub("", data)
    return HEX64.sub("<HEX>", data)


def wait_for_manifest(fd, phase, tries=600):
    """Wait for pc_manifest.sh's `.done` marker, FAILURE-AWARE (SWEEP-prod #32).

    pc_manifest.sh is silent on success — every step writes to a file — and its own SystemExit reason lands in
    manifest-<phase>.log through stderr=STDOUT while `.done` is never touched. A success-only exit condition
    therefore spends the full 300 s on a manifest that died in its first second and then blames a timeout. A
    non-empty log with no marker IS the failure signature; its tail is surfaced instead of hidden.

    An EMPTY log with no marker is deliberately NOT that signature (VERIFY-P5a F14): pc_manifest.sh reports
    through stderr=STDOUT, so no bytes means it has not spoken yet — this wait then spends its whole budget
    and says so (`pc_launch: pre manifest did not finish within 300 s`), which is honest but does not
    distinguish "still running" from "died before writing a word".
    """
    done = os.path.join(fd, f"manifest-{phase}.done")
    log = os.path.join(fd, f"manifest-{phase}.log")
    for _ in range(tries):
        if os.path.exists(done):
            return
        if os.path.exists(log) and os.path.getsize(log) > 0:
            tail = open(log, encoding="utf-8", errors="replace").read()[-800:].strip()
            raise SystemExit(f"pc_launch: {phase} manifest failed before its .done marker; "
                             f"manifest-{phase}.log tail: {tail}")
        time.sleep(0.5)
    raise SystemExit(f"pc_launch: {phase} manifest did not finish within {tries // 2} s")


def summary_tail(path):
    """Last line of a manifest summary, or a named placeholder (SWEEP-prod #48).

    An empty or truncated summary used to raise IndexError from `[-1]` on a display-only read, killing the
    launcher right after the 300 s manifest wait and before env.json/argv.txt were ever written.
    """
    lines = open(path, encoding="utf-8", errors="replace").read().splitlines()
    return lines[-1] if lines else "<empty summary>"


def wait_for_tee_identity(fd, tries=60):
    """Wait for frame_tee.py to create runtime-identity.json (SWEEP-prod #31).

    The old default — `{"_note": "tee identity absent at merge time"}` — let the launcher report success and
    pushed the diagnosis downstream, where the checker's reason is a runtime-identity KEY SET mismatch that
    never says "the tee never started".
    """
    ident_path = os.path.join(fd, "runtime-identity.json")
    for _ in range(tries):
        if os.path.exists(ident_path):
            return ident_path
        time.sleep(0.5)
    raise SystemExit(f"pc_launch: the tee did not write runtime-identity.json within {tries // 2} s")


def buzz_identity(pid, rc):
    """Realpath + sha256 of a live buzz-acp's executable, or a NAMED exit (SWEEP-prod #12).

    buzz-acp can exit between the settle poll and here; both expressions then raise FileNotFoundError and the
    launcher dies with a bare traceback — no identity merge, no owned-pids.json, no launch.ready, so run_leg.sh
    spins its whole READY poll before reporting "launch failed" with no reason.
    """
    try:
        return os.readlink(f"/proc/{pid}/exe"), sha256_file(f"/proc/{pid}/exe")
    except OSError as exc:
        raise SystemExit(f"pc_launch: buzz-acp exited during identity capture (rc={rc}): {exc}")


def session_closure(pid):
    """The descendant closure of `pid`, scoped to ITS SESSION (SWEEP-prod #52).

    buzz-acp is spawned with start_new_session=True, so it leads session <pid> and every descendant it did not
    detach shares that session. Walking the FULL `ps -eo pid,ppid` table instead adopts any foreign row whose
    ppid happens to land in the owned set — a pid-reuse race writing a stranger into owned-pids.json.
    """
    ps = subprocess.run(["ps", "-s", str(pid), "-o", "pid,ppid", "--no-headers"],
                        capture_output=True, text=True)
    rows = []
    for line in ps.stdout.splitlines():
        parts = line.split()
        if len(parts) == 2:
            rows.append((int(parts[0]), int(parts[1])))
    if ps.returncode != 0 or not rows:
        raise SystemExit(f"pc_launch: ps -s {pid} listed no process (rc={ps.returncode}); "
                         "the buzz-acp session is gone")
    owned = {pid}
    changed = True
    while changed:
        changed = False
        for cpid, cppid in rows:
            if cppid in owned and cpid not in owned:
                owned.add(cpid)
                changed = True
    return owned


def redact_environ(raw, red):
    """/proc/<pid>/environ bytes -> env.json mapping, fingerprints taken on the RAW bytes (SWEEP-prod #25).

    len/sha256_12 computed after a lossy decode describe a MANGLED value, not the secret, and check_env only
    asserts `redacted is True` — so nothing downstream would ever notice the fingerprint was wrong.
    """
    live_env = {}
    for item in raw.split(b"\x00"):
        if not item:
            continue
        kb, _, vb = item.partition(b"=")
        k = kb.decode("utf-8", errors="replace")
        if red.search(k):
            live_env[k] = {"redacted": True, "len": len(vb),
                           "sha256_12": hashlib.sha256(vb).hexdigest()[:12]}
        else:
            live_env[k] = vb.decode("utf-8", errors="replace")
    return live_env


def leg_framedir(markers, leg):
    """The one place a leg name becomes a framedir path (`<markers>/v2-<leg>`)."""
    return os.path.join(markers, f"v2-{leg}")


def resolve_launch_profile(leg, model, profile, hermes_home):
    """Which Hermes config.yaml and which HERMES_HOME this launch runs against — and whether the leg name is
    admitted at all. Returns (hermes_home, config_path).

    S0-01's own legs keep their CLOSED sets (pins.LEGS, pins.EXPECTED_MODEL): a leg name or a model the proof
    does not pin must never start a capture the checker will then grade under that name. Those sets used to be
    argparse `choices`, which also made them unopenable — S0-03's leg B is pinned to this capture path by
    invocation and could not use it at all (tasks/briefs/s0-03-support/O1-report.md section 6, which refused to
    run rather than fork the launcher).

    `--profile <config.yaml>` is the seam: it admits a FOREIGN leg name and model, and points the launch at
    that proof's own Hermes config, whose directory becomes HERMES_HOME for the launch — so no other proof
    ever writes into S0-01's pinned tree. The constraint is symmetric and stays fail-closed in both
    directions: without --profile only S0-01's legs launch, and WITH it an S0-01 leg is refused, so an S0-01
    capture can never silently be taken against a foreign config.
    """
    if profile is None:
        if leg not in pins.LEGS:
            raise SystemExit(f"pc_launch: --leg {leg!r} is not an S0-01 leg ({', '.join(pins.LEGS)}); "
                             "a leg from another proof needs --profile <hermes config.yaml>")
        if pins.EXPECTED_MODEL[leg] != model:
            raise SystemExit(f"pc_launch: leg {leg} pins model {pins.EXPECTED_MODEL[leg]}, got {model}")
        return hermes_home, os.path.join(hermes_home, "config.yaml")
    if leg in pins.LEGS:
        raise SystemExit(f"pc_launch: --leg {leg} is an S0-01 leg and always launches against the pinned "
                         "Hermes home; --profile is for another proof's leg")
    if not os.path.isfile(profile):
        raise SystemExit(f"pc_launch: --profile {profile!r} is not an existing file")
    return os.path.dirname(os.path.abspath(profile)), os.path.abspath(profile)


def launch_env(leg, framedir, hermes_home, respond_to, allowlist, sec_dir, hermes_env):
    """The environment buzz-acp is launched with — every secret READ FROM A FILE into this dict and never put
    into an argv (AF-AP-35). The key SET is pinned, so a key added or dropped here fails loudly instead of
    changing what the capture proves.
    """
    env = {
        "PATH": pins.PINNED_PATH,
        "HOME": pins.PINNED_HOME,
        "BUZZ_PRIVATE_KEY": read_kv(os.path.join(sec_dir, "agent.env"), "BUZZ_PRIVATE_KEY"),
        "BUZZ_RELAY_URL": pins.PINNED_RELAY_URL,
        "BUZZ_ACP_AGENT_OWNER": open(os.path.join(sec_dir, "owner.pub")).read().strip(),
        "BUZZ_ACP_RESPOND_TO": respond_to,
        "BUZZ_ACP_SESSION_POLICY": pins.PINNED_SESSION_POLICY,
        "HERMES_HOME": hermes_home,
        "OMNIROUTE_API_KEY": read_kv(hermes_env, "OMNIROUTE_API_KEY"),
        "PYTHONDONTWRITEBYTECODE": "1",
        "S0_01_FRAMEDIR": framedir,
        "S0_01_AGENT": pins.PINNED_AGENT_REALPATH,
    }
    if respond_to == "allowlist":
        env[pins.ENV_ALLOWLIST_KEY] = allowlist
    expected_keys = set(pins.PINNED_ENV_KEYS) | ({pins.ENV_ALLOWLIST_KEY} if leg == "two-users" else set())
    if set(env) != expected_keys:
        raise SystemExit(f"pc_launch: env key set drifted from pins: {sorted(set(env) ^ expected_keys)}")
    for k in ("BUZZ_PRIVATE_KEY", "OMNIROUTE_API_KEY"):
        if not env[k]:
            raise SystemExit(f"pc_launch: {k} is empty")
    return env


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--leg", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--profile", default=None,
                    help="another proof's Hermes config.yaml; required for a --leg outside S0-01's set")
    ap.add_argument("--respond-to", default="owner-only", choices=["owner-only", "allowlist"])
    ap.add_argument("--allowlist", default="")
    ap.add_argument("--settle-seconds", type=float, default=12.0)
    args = ap.parse_args()

    hermes_home, cfg = resolve_launch_profile(args.leg, args.model, args.profile, HERMES_HOME)
    L = os.path.join(BASE, ".markers")
    SEC = os.path.join(BASE, ".secrets")
    FD = leg_framedir(L, args.leg)
    if (args.respond_to == "allowlist") != (args.leg == "two-users"):
        raise SystemExit("pc_launch: allowlist mode is exactly the two-users leg")
    if args.respond_to == "allowlist" and not re.fullmatch(r"[0-9a-f]{64}", args.allowlist):
        raise SystemExit("pc_launch: --allowlist must be one 64-hex pubkey")

    old = alive_pinned_buzz(os.path.join(L, "buzz-acp.pid"))
    if old is not None:
        raise SystemExit(f"pc_launch: a pinned buzz-acp is still alive (pid {old}); run pc_post.sh (teardown) first")

    shutil.rmtree(FD, ignore_errors=True)
    os.makedirs(os.path.join(FD, "mentions"))
    os.makedirs(os.path.join(FD, "upstream-records"))
    print(f"[{utc_now()}] leg={args.leg} framedir={FD}")

    # --- Hermes model route for this leg (config.yaml default model) ---
    s = open(cfg, encoding="utf-8").read()
    s2 = re.sub(r"(?m)^(\s*default:\s*)s0-01-scripted/s0-01-\w+\s*$", rf"\g<1>{pins.PINNED_ROUTE_PREFIX}/{args.model}", s, count=1)
    s2 = re.sub(r"(?m)^(\s*default_model:\s*)s0-01-scripted/s0-01-\w+\s*$", rf"\g<1>{pins.PINNED_ROUTE_PREFIX}/{args.model}", s2)
    if s2 != s:
        open(cfg, "w", encoding="utf-8").write(s2)
    default_lines = [ln for ln in s2.splitlines() if ln.strip().startswith("default:")]
    if not default_lines:
        raise SystemExit("pc_launch: config.yaml has no `default:` line")
    open(os.path.join(FD, "hermes-model.txt"), "w").write(default_lines[0] + "\n")
    open(os.path.join(FD, "hermes-config.sha256"), "w").write(sha256_file(cfg) + "\n")
    print("model line:", default_lines[0].strip())

    # --- backend record count before ---
    try:
        with urllib.request.urlopen("http://127.0.0.1:20201/healthz", timeout=5) as r:
            hz = r.read()
    except Exception as e:  # a 401/refused here means the v2 backend is not the one on :20201
        raise SystemExit(f"pc_launch: backend /healthz probe failed ({type(e).__name__}: {e}); run pc_backend_restart.sh first")
    if json.loads(hz).get("ok") is not True:
        raise SystemExit("pc_launch: backend /healthz did not report ok:true")
    open(os.path.join(FD, "backend-healthz-before.json"), "wb").write(hz)
    print("healthz before:", hz.decode()[:120])

    # --- pre manifest (detached) ---
    man_env = {"PATH": "/usr/bin:/bin", "HOME": pins.PINNED_HOME, "PHASE": "pre", "FD": FD, "BASE": BASE}
    with open(os.path.join(FD, "manifest-pre.log"), "wb") as mlog:
        subprocess.Popen(["setsid", "bash", os.path.join(REPO, "proofs/S0-01/tools/pc/pc_manifest.sh")],
                         env=man_env, stdin=subprocess.DEVNULL, stdout=mlog, stderr=subprocess.STDOUT)

    # the PRE manifest must COMPLETE before anything spawns (its timestamp is the "before" mark)
    wait_for_manifest(FD, "pre")
    print(f"[{utc_now()}] pre manifest done: {summary_tail(os.path.join(FD, 'manifest-pre.summary'))}")

    # --- env from files (never argv) ---
    env = launch_env(args.leg, FD, hermes_home, args.respond_to, args.allowlist, SEC, HERMES_ENV)
    print("env keys:", sorted(env))

    # --- launch the pinned buzz-acp with the PINNED argv ---
    raw_log_path = os.path.join(FD, "buzzacp.raw.log")
    raw_log = open(raw_log_path, "ab")
    proc = subprocess.Popen(pins.PINNED_LAUNCH_ARGV, env=env, stdin=subprocess.DEVNULL,
                            stdout=raw_log, stderr=subprocess.STDOUT, start_new_session=True)
    pid = proc.pid
    open(os.path.join(FD, "buzz-acp.pid"), "w").write(f"{pid}\n")
    open(os.path.join(L, "buzz-acp.pid"), "w").write(f"{pid}\n")
    open(os.path.join(L, "current-framedir"), "w").write(FD + "\n")
    print(f"[{utc_now()}] buzz-acp pid {pid}")

    time.sleep(args.settle_seconds)
    if proc.poll() is not None:
        print("LAUNCH FAILED rc", proc.returncode)
        print(masked_log_text(raw_log_path)[-2000:])
        open(os.path.join(FD, "buzz-acp.exit"), "w").write(f"{proc.returncode}\n")
        raise SystemExit(4)

    # argv.txt: one arg per line, exactly as /proc/<pid>/cmdline says (empty --agent-args value = empty line)
    cmdline = open(f"/proc/{pid}/cmdline", "rb").read().decode("utf-8")
    argv = cmdline.split("\x00")
    if argv and argv[-1] == "":
        argv = argv[:-1]
    open(os.path.join(FD, "argv.txt"), "w").write("\n".join(argv) + "\n")
    if argv != pins.PINNED_LAUNCH_ARGV:
        print("ARGV DRIFT:", argv)

    # env.json from the live process environment, redacted by KEY NAME (pins.REDACTED_ENV_KEY_RE)
    red = re.compile(pins.REDACTED_ENV_KEY_RE)
    live_env = redact_environ(open(f"/proc/{pid}/environ", "rb").read(), red)
    open(os.path.join(FD, "env.json"), "w").write(json.dumps(live_env, indent=1, sort_keys=True) + "\n")

    # merge the buzz-acp identity into the tee's runtime-identity.json (wait for the tee to spawn)
    ident_path = wait_for_tee_identity(FD)
    ident = json.load(open(ident_path))
    exe_real, exe_sha = buzz_identity(pid, proc.poll())
    ident.update({
        "buzz_acp_pid": pid,
        "buzz_acp_exe_realpath": exe_real,
        "buzz_acp_exe_sha256": exe_sha,
        "buzz_acp_version": "n/a: this buzz-acp build has no --version flag (identity = exe sha256 above)",
        "launch_argv": argv,
    })
    open(ident_path, "w").write(json.dumps(ident, indent=1, sort_keys=True) + "\n")
    print("identity keys:", sorted(ident))

    # startup line (masked) — the config echo the checker pins
    masked = masked_log_text(raw_log_path)
    start_lines = [ln for ln in masked.splitlines() if "buzz-acp starting:" in ln]
    if not start_lines:
        print("NO STARTUP LINE YET; log tail:", masked[-800:])
    else:
        open(os.path.join(FD, "startup-line.txt"), "w").write(start_lines[0] + "\n")
        toks = start_lines[0].split(" ")
        echo = {t.split("=")[0]: t for t in toks if t.startswith(("idle_timeout=", "max_turn=", "session_policy=", "respond_to="))}
        print("config echo:", " ".join(echo.values()))
        if echo.get("max_turn") != f"max_turn={pins.PINNED_MAX_TURN}" or echo.get("idle_timeout") != f"idle_timeout={pins.PINNED_IDLE_TIMEOUT}":
            print("CONFIG ECHO MISMATCH — the checker will fail this leg")
    # owned process set at READY: the closure of buzz-acp's descendants inside ITS OWN session
    # (recomputed in memory; only owned lines are persisted by pc_post.sh)
    owned = session_closure(pid)
    for key in ("tee_pid", "agent_child_pid"):
        if isinstance(ident.get(key), int) and ident[key] not in owned:
            print(f"OWNED-SET DRIFT: identity {key}={ident[key]} not in the descendant closure {sorted(owned)}")
    open(os.path.join(FD, "owned-pids.json"), "w").write(json.dumps({"buzz_acp_pid": pid, "owned": sorted(owned), "taken_at": "ready"}, indent=1) + "\n")
    print("owned pids at ready:", sorted(owned))
    open(os.path.join(FD, "launch.ready"), "w").write(utc_now() + "\n")
    print(f"[{utc_now()}] ready; waiting for buzz-acp exit")
    sys.stdout.flush()
    rc = proc.wait()
    open(os.path.join(FD, "buzz-acp.exit"), "w").write(f"{rc}\n")
    open(os.path.join(FD, "launch.exited"), "w").write(utc_now() + "\n")
    print(f"[{utc_now()}] buzz-acp exited rc={rc}")


if __name__ == "__main__":
    main()
