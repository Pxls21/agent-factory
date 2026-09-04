"""Rubric isolation stand-in: writes its workspace, signals readiness, then blocks.

Deliberately authors NO report about its own isolation. A child under a fake or
pass-through wrapper could fabricate a clean self-report, so the S0-11 checker
does not trust child-authored evidence — it observes this process from the
PARENT via /proc/<pid> (real uid, network namespace, environment, no_new_privs,
capability bounding set) while it is alive here, then releases it by sending one
byte to stdin.

Protocol:
  1. Write a real output file into the assigned workspace (RUBRIC_CWD) — a real
     AlphaEval rubric writes results and logs there. If the workspace is not
     writable by this (dropped) uid, the write fails and the parent's collection
     comes back empty, which fails the proof (workspace unusable).
  2. Write 'R' to stdout so the parent knows the post-privilege-drop process is
     running and can be observed.
  3. Read one byte from stdin and exit.
"""
import os
import sys

workspace = os.environ.get("RUBRIC_CWD", ".")
task_id = os.environ.get("RUBRIC_TASK_ID", "")
try:
    with open(os.path.join(workspace, "rubric-output.txt"), "w") as handle:
        handle.write("rubric-wrote:" + task_id)
except OSError:
    pass  # parent observes the missing collection and fails the proof

sys.stdout.write("R")
sys.stdout.flush()
sys.stdin.read(1)
