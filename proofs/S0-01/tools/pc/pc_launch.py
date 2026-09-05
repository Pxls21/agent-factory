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
BASE = os.path.dirname(pins.PINNED_HERMES_HOME)          # /home/rocco/s0-01-pinned
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--leg", required=True, choices=list(pins.LEGS))
    ap.add_argument("--model", required=True, choices=sorted(set(pins.EXPECTED_MODEL.values())))
    ap.add_argument("--respond-to", default="owner-only", choices=["owner-only", "allowlist"])
    ap.add_argument("--allowlist", default="")
    ap.add_argument("--settle-seconds", type=float, default=12.0)
    args = ap.parse_args()

    L = os.path.join(BASE, ".markers")
    SEC = os.path.join(BASE, ".secrets")
    FD = os.path.join(L, f"v2-{args.leg}")
    if pins.EXPECTED_MODEL[args.leg] != args.model:
        raise SystemExit(f"pc_launch: leg {args.leg} pins model {pins.EXPECTED_MODEL[args.leg]}, got {args.model}")
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
    cfg = os.path.join(pins.PINNED_HERMES_HOME, "config.yaml")
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

    # --- env from files (never argv) ---
    env = {
        "PATH": pins.PINNED_PATH,
        "HOME": pins.PINNED_HOME,
        "BUZZ_PRIVATE_KEY": read_kv(os.path.join(SEC, "agent.env"), "BUZZ_PRIVATE_KEY"),
        "BUZZ_RELAY_URL": pins.PINNED_RELAY_URL,
        "BUZZ_ACP_AGENT_OWNER": open(os.path.join(SEC, "owner.pub")).read().strip(),
        "BUZZ_ACP_RESPOND_TO": args.respond_to,
        "BUZZ_ACP_SESSION_POLICY": pins.PINNED_SESSION_POLICY,
        "HERMES_HOME": pins.PINNED_HERMES_HOME,
        "OMNIROUTE_API_KEY": read_kv(HERMES_ENV, "OMNIROUTE_API_KEY"),
        "PYTHONDONTWRITEBYTECODE": "1",
        "S0_01_FRAMEDIR": FD,
        "S0_01_AGENT": pins.PINNED_AGENT_REALPATH,
    }
    if args.respond_to == "allowlist":
        env[pins.ENV_ALLOWLIST_KEY] = args.allowlist
    expected_keys = set(pins.PINNED_ENV_KEYS) | ({pins.ENV_ALLOWLIST_KEY} if args.leg == "two-users" else set())
    if set(env) != expected_keys:
        raise SystemExit(f"pc_launch: env key set drifted from pins: {sorted(set(env) ^ expected_keys)}")
    for k in ("BUZZ_PRIVATE_KEY", "OMNIROUTE_API_KEY"):
        if not env[k]:
            raise SystemExit(f"pc_launch: {k} is empty")
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
    live_env = {}
    for item in open(f"/proc/{pid}/environ", "rb").read().split(b"\x00"):
        if not item:
            continue
        k, _, v = item.decode("utf-8", errors="replace").partition("=")
        if red.search(k):
            live_env[k] = {"redacted": True, "len": len(v), "sha256_12": hashlib.sha256(v.encode("utf-8")).hexdigest()[:12]}
        else:
            live_env[k] = v
    open(os.path.join(FD, "env.json"), "w").write(json.dumps(live_env, indent=1, sort_keys=True) + "\n")

    # merge the buzz-acp identity into the tee's runtime-identity.json (wait for the tee to spawn)
    ident_path = os.path.join(FD, "runtime-identity.json")
    for _ in range(60):
        if os.path.exists(ident_path):
            break
        time.sleep(0.5)
    ident = json.load(open(ident_path)) if os.path.exists(ident_path) else {"_note": "tee identity absent at merge time"}
    exe_real = os.readlink(f"/proc/{pid}/exe")
    ident.update({
        "buzz_acp_pid": pid,
        "buzz_acp_exe_realpath": exe_real,
        "buzz_acp_exe_sha256": sha256_file(f"/proc/{pid}/exe"),
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
    open(os.path.join(FD, "launch.ready"), "w").write(utc_now() + "\n")
    print(f"[{utc_now()}] ready; waiting for buzz-acp exit")
    sys.stdout.flush()
    rc = proc.wait()
    open(os.path.join(FD, "buzz-acp.exit"), "w").write(f"{rc}\n")
    open(os.path.join(FD, "launch.exited"), "w").write(utc_now() + "\n")
    print(f"[{utc_now()}] buzz-acp exited rc={rc}")


if __name__ == "__main__":
    main()
