#!/usr/bin/env python3
"""Run the S0-01 negative probe (tools/acp_probe.py) against the PINNED hermes-acp on the PC.

The probe's env is built here from files (never argv): the same HERMES_HOME / bytecode / key
environment the positive legs give the agent, so the observed response is the pinned agent's.
Output dir: /home/rocco/s0-01-pinned/.markers/v2-negative (contract v2.1, negative section).
"""
import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
import pins  # noqa: E402
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pc_launch import read_kv, HERMES_ENV, BASE, REPO  # noqa: E402


def main():
    """Run the probe and PROPAGATE ITS EXIT CODE (SWEEP-prod #33).

    The wrapper used to end on a `print`, so it exited 0 whatever the probe returned: run_leg.sh runs it under
    `set -euo pipefail` and walked straight on to collect_leg.sh with a failed negative leg in hand.
    """
    FD = os.path.join(BASE, ".markers", "v2-negative")
    shutil.rmtree(FD, ignore_errors=True)
    os.makedirs(FD)
    env = {
        "PATH": pins.PINNED_PATH, "HOME": pins.PINNED_HOME,
        "HERMES_HOME": pins.PINNED_HERMES_HOME, "PYTHONDONTWRITEBYTECODE": "1",
        "OMNIROUTE_API_KEY": read_kv(HERMES_ENV, "OMNIROUTE_API_KEY"),
        "S0_01_AGENT": pins.PINNED_AGENT_REALPATH, "S0_01_FRAMEDIR": FD,
    }
    rc = subprocess.run(["/usr/bin/python3", os.path.join(REPO, "proofs/S0-01/tools/acp_probe.py")], env=env).returncode
    print("probe rc", rc)
    for name in sorted(os.listdir(FD)):
        print(name, os.path.getsize(os.path.join(FD, name)))
    tl = os.path.join(FD, "timeline.jsonl")
    if os.path.exists(tl):
        for line in open(tl):
            print(line[:300].rstrip())
    if rc < 0:
        # VERIFY-P5a F8: subprocess reports a signal death as -N, and `raise SystemExit(-9)` hands the OS a
        # status of 247 — a number no shell convention names, and one a `max(rc, 0)`-shaped regression could
        # turn into SUCCESS with no test able to see it. 128+signal is the convention run_leg.sh's `set -e`
        # and every reader already share (SIGKILL -> 137). The branch prints its reason rather than mapping
        # silently.
        print(f"probe killed by signal {-rc}; exit {128 - rc}")
        return 128 - rc
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
