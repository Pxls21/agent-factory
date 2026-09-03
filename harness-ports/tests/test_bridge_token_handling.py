"""The bridge token never reaches argv or the filesystem: scripts/pc_bridge_exec.py hands it to
curl through `--config -` on STDIN only. Static checks over the helper's source (the behavioural
proof — header carried, envelope unwrapped — is harness-ports/tests/test_pc_bridge_exec.py).
Rewritten 2026-09-03 when the inline bridge() block moved out of scripts/pc_lane.sh."""
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC = (ROOT / "scripts" / "pc_bridge_exec.py").read_text()
LANE = (ROOT / "scripts" / "pc_lane.sh").read_text()

checks = 0
assert re.search(r'\["curl",\s*"--config",\s*"-"\]', SRC), "curl must read its config from stdin"
assert "input=cfg" in SRC, "the config (with the token) must be passed as stdin input"
checks += 2
assert "X-Agent-Token: {token}" in SRC, "token travels as a header inside the stdin config"
assert not re.search(r'\["curl"[^\]]*token', SRC), "token must not be a curl argv element"
body_line = [l for l in SRC.splitlines() if "body = json.dumps" in l][0]
assert "token" not in body_line, "token must not be in the JSON body written to the temp file"
checks += 3
assert "shell=True" not in SRC, "a shell would expose the config through the process table"
checks += 1
assert 'python3 "$ROOT/scripts/pc_bridge_exec.py" "$1"' in LANE, "pc_lane.sh must delegate every bridge call"
assert "export PC_BRIDGE_URL PC_BRIDGE_TOKEN" in LANE, "pc_lane.sh must export the env for the helper"
LANE_CODE = "\n".join(l for l in LANE.splitlines() if not l.lstrip().startswith("#"))
assert "X-Agent-Token" not in LANE_CODE, "no inline token handling may remain in pc_lane.sh (comments excepted)"
checks += 3
print(f"test_bridge_token_handling: {checks} checks passed — ALL OK")
