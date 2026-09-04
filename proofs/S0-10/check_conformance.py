#!/usr/bin/env python3
"""S0-10 conformance checker: validates GBrain seam decision ADR."""
import re
import sys

REQUIRED_SECTIONS = ["Context", "Alternatives", "Decision", "Consequences"]


def check(path):
    with open(path) as f:
        text = f.read()

    for section in REQUIRED_SECTIONS:
        if not re.search(rf"^##\s+.*{re.escape(section)}", text, re.MULTILINE | re.IGNORECASE):
            print(f"adr-incomplete: missing required section: {section}")
            return 1

    credential_patterns = [
        r"no ai-memory admin credential",
        r"no.*admin credential",
        r"receive no ai-memory admin",
    ]
    found = any(re.search(p, text, re.IGNORECASE) for p in credential_patterns)
    if not found:
        print("adr-incomplete: missing credential-isolation statement")
        return 1

    if not re.search(r"proposal.only", text, re.IGNORECASE):
        print("adr-incomplete: missing proposal-only contract")
        return 1

    print("PASS: all conformance checks satisfied")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <adr-path>", file=sys.stderr)
        sys.exit(2)
    sys.exit(check(sys.argv[1]))
