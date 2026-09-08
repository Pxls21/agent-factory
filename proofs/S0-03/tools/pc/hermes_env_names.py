#!/usr/bin/env python3
"""S0-03 assertion 3 instrument — the environment NAMES of the running hermes-acp process.

RUNS ON THE PC ONLY (it reads /proc of a process the S0-01 tee spawned).

Reads `/proc/<pid>/environ` and writes `<out-dir>/hermes-env-names.json`:

    {"pid": <int>, "exe": "<readlink /proc/<pid>/exe>", "agent_realpath": "<the tee's record>",
     "names": [sorted, unique]}

NAMES ONLY. The values are split off and discarded inside this process; nothing derived from a
value is written, printed, or returned. That is the whole point: the assertion "Hermes holds no
upstream provider key" is answerable from names alone, so reading values would add risk and no
evidence (AF-AP-35: never let a secret VALUE into an artifact or a transcript).

THE PID KEY IS THE ONE THE PRODUCER WRITES
------------------------------------------
The pid comes from the tee's `runtime-identity.json` (written once at spawn) unless `--pid`
overrides it, and the key is `agent_child_pid` — read from the PRODUCER,
`proofs/S0-01/tools/frame_tee.py` (`"agent_child_pid": proc.pid` in its identity dict), not from this file's
assumption about what a pid key is called. The four names this tool used to look for
(agent_pid/child_pid/hermes_pid/pid) exist in no real record: against the committed corpus at
`$S0_01_REAL_LEG_DIR/run-1/runtime-identity.json` the tool exited 1 and leg B could never take an
env record at all (VERIFY-O1 F-7 — build-loop step 1, the seam verified from the CONSUMER).

WHICH PROCESS THE NAMES BELONG TO
---------------------------------
Two identity fields ride with the names, because "some process holds no provider key" is not the
assertion — "HERMES holds none" is:
  * `exe` = readlink /proc/<pid>/exe. For the agent child this is the INTERPRETER, not the
    hermes-acp entry point (the tee records exactly this value as `agent_interpreter_realpath`,
    the tee's `agent_interpreter_realpath` key; in the real corpus it is /usr/bin/python3.13).
  * `agent_realpath` = the tee's own record of the binary it spawned (the tee's `agent_realpath` key), copied
    across when the pid was resolved from a runtime-identity.json. The checker pins it to
    `pins.PINNED_AGENT_REALPATH`.
A pid that has already been recycled is a LOUD failure, never an empty name list — an empty list
would sail through the checker's allow-list (every membership test is vacuously true over
nothing).

Usage: hermes_env_names.py --out-dir DIR (--pid N | --runtime-identity PATH)
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def parse_args(argv) -> dict:
    out_dir = pid = rid = None
    proc_root = os.environ.get("PROC_ROOT", "/proc")
    i = 0
    while i < len(argv):
        arg = argv[i]
        if arg in ("--out-dir", "--pid", "--runtime-identity", "--proc-root"):
            if i + 1 >= len(argv):
                raise SystemExit(f"hermes_env_names: {arg} needs a value")
            value = argv[i + 1]
            if arg == "--out-dir":
                out_dir = value
            elif arg == "--pid":
                pid = int(value)
            elif arg == "--runtime-identity":
                rid = value
            else:
                proc_root = value
            i += 2
            continue
        raise SystemExit(f"hermes_env_names: unknown argument {arg}")
    if not out_dir or (pid is None and rid is None):
        raise SystemExit("usage: hermes_env_names.py --out-dir DIR "
                         "(--pid N | --runtime-identity PATH)")
    return {"out_dir": Path(out_dir), "pid": pid, "rid": rid, "proc_root": Path(proc_root)}


# The key the tee actually writes, FIRST — proofs/S0-01/tools/frame_tee.py's identity dict. The rest are
# tolerated aliases for a hand-made record; none of them appears in a real one.
PID_KEYS = ("agent_child_pid", "agent_pid", "child_pid", "hermes_pid", "pid")


def resolve_identity(args):
    """Return (pid, agent_realpath). agent_realpath is None when --pid was used."""
    if args["pid"] is not None:
        return args["pid"], None
    path = Path(args["rid"])
    try:
        record = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise SystemExit(f"hermes_env_names: cannot read {path}: {exc.__class__.__name__}")
    agent_realpath = record.get("agent_realpath") if isinstance(record, dict) else None
    if not isinstance(agent_realpath, str):
        agent_realpath = None
    for key in PID_KEYS:
        value = record.get(key) if isinstance(record, dict) else None
        if isinstance(value, int):
            return value, agent_realpath
    raise SystemExit(
        f"hermes_env_names: {path} carries no agent pid "
        f"(keys: {sorted(record) if isinstance(record, dict) else type(record).__name__})"
    )


def env_names(proc_root: Path, pid: int):
    """Split /proc/<pid>/environ on NUL and keep only the part left of the first '='."""
    try:
        raw = (proc_root / str(pid) / "environ").read_bytes()
    except OSError as exc:
        raise SystemExit(
            f"hermes_env_names: cannot read {proc_root}/{pid}/environ "
            f"({exc.__class__.__name__}) — the process is gone or not ours"
        )
    names = set()
    for item in raw.split(b"\0"):
        if not item:
            continue
        name = item.split(b"=", 1)[0].decode("utf-8", errors="replace")
        if name:
            names.add(name)
    if not names:
        # Fail LOUD: an empty list satisfies every allow-list vacuously.
        raise SystemExit(f"hermes_env_names: /proc/{pid}/environ is empty")
    return sorted(names)


def main(argv) -> int:
    args = parse_args(argv[1:])
    pid, agent_realpath = resolve_identity(args)
    try:
        exe = os.readlink(str(args["proc_root"] / str(pid) / "exe"))
    except OSError as exc:
        raise SystemExit(
            f"hermes_env_names: cannot readlink /proc/{pid}/exe ({exc.__class__.__name__})"
        )
    names = env_names(args["proc_root"], pid)
    record = {"pid": pid, "exe": exe, "names": names}
    if agent_realpath is not None:
        record["agent_realpath"] = agent_realpath
    args["out_dir"].mkdir(parents=True, exist_ok=True)
    (args["out_dir"] / "hermes-env-names.json").write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"hermes-env-names: pid={pid} names={len(names)} agent={agent_realpath!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
