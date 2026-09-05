#!/usr/bin/env bash
# test_summary.sh — run pytest and print a mechanical summary line.
# Usage: scripts/test_summary.sh [pytest paths...]  (default: tests/)
# Prints:
#   pytest-exit: <exit code>
#   pytest-summary: <last non-empty output line>
# Exits with pytest's exit code.
set -u

paths=("${@:-tests/}")

output=$(python3 -m pytest "${paths[@]}" -q -rs -p no:cacheprovider 2>&1)
rc=$?

echo "$output"

# Extract last non-empty line.
last_line=$(echo "$output" | grep -v '^$' | tail -n 1)

echo "pytest-exit: $rc"
echo "pytest-summary: $last_line"
exit "$rc"
