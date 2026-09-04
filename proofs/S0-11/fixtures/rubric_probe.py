"""Positive rubric fixture: reports observed isolation state.

Run through the isolation wrapper, this script observes its own
process environment and reports what it sees as JSON to stdout.
The checker asserts the correct isolation properties.
"""
import json
import os
import socket
import sys

CREDENTIAL_KEYS = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "OMNIROUTE_API_KEY",
    "HERMES_API_KEY",
]

report = {
    "uid": os.getuid(),
    "cwd": os.getcwd(),
    "has_credential_env": any(k in os.environ for k in CREDENTIAL_KEYS),
    "credential_keys_found": [k for k in CREDENTIAL_KEYS if k in os.environ],
    "rubric_task_id": os.environ.get("RUBRIC_TASK_ID", ""),
    "rubric_cwd": os.environ.get("RUBRIC_CWD", ""),
}

try:
    s = socket.create_connection(("1.1.1.1", 53), timeout=2)
    report["net_isolated"] = False
    s.close()
except OSError:
    report["net_isolated"] = True

json.dump(report, sys.stdout)
sys.exit(0)
