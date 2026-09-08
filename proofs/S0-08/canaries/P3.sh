#!/bin/sh
# S0-08 canary P3 — the required tools work inside the contained runtime.
#
# The tool list is derived from the pinned image's own installs:
#   /opt/hermes/bin/hermes  the exec shim (Dockerfile:299-301), which itself
#                           drops to the hermes user (docker/hermes-exec-shim.sh:87)
#   python3 -c import hermes_cli   the installed package (pyproject.toml:587;
#                           there is NO top-level `hermes` package)
#   node                    Node 26, copied from the upstream image (Dockerfile:154-160)
#   uv                      copied from the uv source stage (Dockerfile:152)
#
# Emits ONE JSON line of OBSERVATIONS. The checker decides PASS/FAIL.
set -u

esc() {
    printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g' | tr -d '\000-\037'
}

# Capture a tool's OWN exit status. There must be no pipeline between the
# tool and `$?` — a piped status is the last stage's (`head`), which is
# always 0 and would report a missing tool as a success.
TOOL_OUT=""
TOOL_RC=0
run_tool() {
    TOOL_OUT=$("$@" 2>&1)
    TOOL_RC=$?
    TOOL_OUT=$(printf '%s\n' "$TOOL_OUT" | head -n 1)
}

run_tool /opt/hermes/bin/hermes --version
hermes_rc=$TOOL_RC; hermes_out=$TOOL_OUT

run_tool python3 -c 'import hermes_cli; print("import-ok")'
py_rc=$TOOL_RC; py_out=$TOOL_OUT

run_tool node --version
node_rc=$TOOL_RC; node_out=$TOOL_OUT

run_tool uv --version
uv_rc=$TOOL_RC; uv_out=$TOOL_OUT

rc=0

printf '{"canary":"P3","expect":"hermes, python3 -c import hermes_cli, node and uv each exit 0","observed":{"hermes_rc":"%d","hermes_out":"%s","python_import_rc":"%d","python_import_out":"%s","node_rc":"%d","node_out":"%s","uv_rc":"%d","uv_out":"%s"},"rc":%d}\n' \
    "$hermes_rc" "$(esc "$hermes_out")" \
    "$py_rc" "$(esc "$py_out")" \
    "$node_rc" "$(esc "$node_out")" \
    "$uv_rc" "$(esc "$uv_out")" "$rc"
