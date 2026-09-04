#!/usr/bin/env python3
"""S0-09 conformance checker: validates Foundry host decision ADR."""
import re
import sys

REQUIRED_SECTIONS = ["Context", "Alternatives", "Decision", "Consequences"]
JIT_FILES = ["memory.py", "planning.py", "action.py", "tool_policy.py", "prompt.yaml"]


def check(path):
    with open(path) as f:
        text = f.read()

    for section in REQUIRED_SECTIONS:
        if not re.search(rf"^##\s+{re.escape(section)}\b", text, re.MULTILINE | re.IGNORECASE):
            print(f"adr-incomplete: missing required section: {section}")
            return 1

    if "openharness" not in text.lower():
        print("adr-incomplete: missing required section: OpenHarness alternatives")
        return 1

    for jit_file in JIT_FILES:
        if jit_file not in text:
            print(f"adr-incomplete: missing JIT output file: {jit_file}")
            return 1

    print("PASS: all conformance checks satisfied")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <adr-path>", file=sys.stderr)
        sys.exit(2)
    sys.exit(check(sys.argv[1]))
