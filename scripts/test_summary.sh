#!/usr/bin/env bash
# test_summary.sh — run pytest and print a mechanical summary line.
# Usage: scripts/test_summary.sh [pytest paths...]  (default: tests/)
# Prints:
#   pytest-exit: <exit code>
#   pytest-summary: <last non-empty output line>
# Exits with pytest's exit code.
set -u

# S0-01 real-leg corpus as a DECLARED input (VERIFY-CK10 F-R10-25): the sandbox venue and its corpus path are the
# defaults here, so a checker run without the corpus FAILS by declaration instead of skipping green. Export both to
# override; the PC pair comes from scripts/pc_suite.sh; CI leaves S0_01_VENUE unset and skips by declaration.
# Restore a fresh container: bash scripts/realleg_sync.sh pull
export S0_01_VENUE="${S0_01_VENUE:-sandbox}"
export S0_01_REAL_LEG_DIR="${S0_01_REAL_LEG_DIR:-/root/s0-01-realleg/golden}"

paths=("${@:-tests/}")

output=$(python3 -m pytest "${paths[@]}" -q -rs -p no:cacheprovider 2>&1)
rc=$?

echo "$output"

# Extract last non-empty line.
last_line=$(echo "$output" | grep -v '^$' | tail -n 1)

echo "pytest-exit: $rc"
echo "pytest-summary: $last_line"
exit "$rc"
