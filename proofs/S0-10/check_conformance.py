#!/usr/bin/env python3
"""S0-10 conformance checker: validates GBrain seam decision ADR."""
import re
import sys

REQUIRED_SECTIONS = ["Context", "Alternatives", "Decision", "Consequences"]


def check(path):
    with open(path) as f:
        text = f.read()

    for section in REQUIRED_SECTIONS:
        if not re.search(rf"^##\s+{re.escape(section)}\b", text, re.MULTILINE | re.IGNORECASE):
            print(f"adr-incomplete: missing required section: {section}")
            return 1

    credential_patterns = [
        r"\bno\s+ai-memory\s+admin\s+credential",
        r"\breceive\w*\s+no\s+(?:\w+\s+){0,2}admin\s+credential",
        r"\bno\s+(?:\w+\s+){0,3}admin\s+credential",
    ]
    found = any(re.search(p, text, re.IGNORECASE) for p in credential_patterns)
    if not found:
        print("adr-incomplete: missing credential-isolation statement")
        return 1

    if not re.search(r"\bproposal[.\s-]only\b", text, re.IGNORECASE):
        print("adr-incomplete: missing proposal-only contract")
        return 1

    print("PASS: all conformance checks satisfied")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <adr-path>", file=sys.stderr)
        sys.exit(2)
    sys.exit(check(sys.argv[1]))
