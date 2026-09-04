"""Rubric isolation stand-in: signals readiness, then blocks.

Deliberately authors NO report about its own isolation. A child under a fake or
pass-through wrapper could fabricate a clean self-report, so the S0-11 checker
does not trust child-authored evidence — it observes this process from the
PARENT via /proc/<pid> (real uid, network namespace, environment) while it is
alive here, then releases it by sending one byte to stdin.

Protocol: write 'R' to stdout (so the parent knows the post-privilege-drop
process is running and can be observed), then read one byte from stdin and exit.
"""
import sys

sys.stdout.write("R")
sys.stdout.flush()
sys.stdin.read(1)
