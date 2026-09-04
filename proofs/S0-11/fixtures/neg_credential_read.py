"""Frozen negative control (seed-stage0-v1, S0-11 negative_control): a rubric
fixture that attempts to read a credential env var.

Run through the credential-isolation env (allow-list), the credential is absent
by construction, so this fixture emits the exact frozen reason and exits 1. If a
credential IS present, isolation is broken and it exits 0 (the checker treats
that unexpected pass as a failure). The reason string is fixed by the seed and
must not change.

It scans for ANY variable that looks like a credential (name-shaped OR a decoy
the checker injected), so it does not encode a name blacklist as a boundary — it
only needs to detect leakage; the allow-list in the checker is the boundary.
"""
import os
import re
import sys

# Production-realistic credential names the checker injects as decoys, plus a
# generic name-shape screen (anything ending _API_KEY/_SECRET/_TOKEN/_KEY/etc).
DECOY_NAMES = (
    "OMNIROUTE_INTERNAL_API_KEY",
    "BUZZ_PRIVATE_KEY",
    "STORAGE_ENCRYPTION_KEY",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
)
CRED_SHAPE = re.compile(r"(_API_KEY|_SECRET|_TOKEN|_CREDENTIAL|_PRIVATE_KEY|_ENCRYPTION_KEY)$")

leaked = [k for k in DECOY_NAMES if k in os.environ]
leaked += [k for k in os.environ if CRED_SHAPE.search(k) and k not in leaked]

if leaked:
    print("FAIL: credential leaked into rubric env: " + ",".join(sorted(leaked)))
    sys.exit(0)

print("rubric-isolation-violation: credential env absent by construction")
sys.exit(1)
