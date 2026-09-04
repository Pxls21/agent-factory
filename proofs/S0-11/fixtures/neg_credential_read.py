"""Negative rubric fixture: attempts to read a credential env var.

When run through the isolation wrapper, credential env vars are absent
by construction. This fixture detects the absence and exits 1 with the
documented violation reason.

If credential env vars ARE present, isolation is broken and the fixture
exits 0 (which the checker treats as an unexpected pass = failure).
"""
import os
import sys

CREDENTIAL_KEYS = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "OMNIROUTE_API_KEY",
    "HERMES_API_KEY",
]

for key in CREDENTIAL_KEYS:
    val = os.environ.get(key)
    if val is not None:
        print("FAIL: credential leaked: " + key)
        sys.exit(0)

print("rubric-isolation-violation: credential env absent by construction")
sys.exit(1)
