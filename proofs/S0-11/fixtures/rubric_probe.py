"""Rubric isolation probe: reports its own observed process state as JSON.

The checker (check_eval_hardening.py) runs this probe twice: once inside the
real isolation wrapper (positive control) and once without it (negative
control). The probe renders NO verdict — it only reports what it observes.
The checker evaluates the reported state against the four isolation axes
(UID drop, network-namespace identity, network reachability, environment
allow-list) and decides pass/fail.

Volatile values (netns inode, listener port, temp cwd) are reported here but
consumed internally by the checker and never echoed to the checker's own
stdout, so the proof stays byte-deterministic.
"""
import json
import os
import socket
import sys


def _net_ns():
    try:
        return os.readlink("/proc/self/ns/net")
    except OSError:
        return ""


def _listener_reachable():
    """Try to reach a loopback listener the checker started in its own netns.

    Under real network isolation the probe is in a fresh netns whose loopback
    is down, so the connection is refused/unreachable. Without isolation the
    probe shares the parent netns and reaches the listener. Returns None when
    no port was supplied (the axis is then unusable and the checker fails)."""
    port = os.environ.get("RUBRIC_PROBE_PORT")
    if not port:
        return None
    try:
        s = socket.create_connection(("127.0.0.1", int(port)), timeout=2)
        s.close()
        return True
    except OSError:
        return False


report = {
    "uid": os.getuid(),
    "net_ns": _net_ns(),
    "cwd": os.getcwd(),
    "env_keys": sorted(os.environ.keys()),
    "listener_reachable": _listener_reachable(),
}
json.dump(report, sys.stdout)
sys.exit(0)
