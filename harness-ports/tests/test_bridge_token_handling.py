"""Prove the bridge token never lands in argv or on disk.

Extracts the bridge() python block from scripts/pc_lane.sh and runs it against a
fake `curl` on PATH that records its own argv and its stdin. Then asserts the
token appears in the stdin config (so it IS being sent) and NOT in argv (so `ps`
cannot see it).
"""
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

WT = Path(__file__).resolve().parents[2]
src = (WT / "scripts" / "pc_lane.sh").read_text()
m = re.search(r"python3 - \"\$1\" <<'PY'\n(.*?)\nPY", src, re.S)
assert m, "could not extract the bridge() python block"

tmp = Path(tempfile.mkdtemp())
argv_log, stdin_log = tmp / "argv.txt", tmp / "stdin.txt"
fake = tmp / "curl"
fake.write_text(
    "#!/usr/bin/env bash\n"
    f"printf '%s\\n' \"$@\" > {argv_log}\n"
    f"cat > {stdin_log}\n"
    "echo FAKE_BRIDGE_OK\n"
)
fake.chmod(0o755)

TOKEN = "SUPERSECRET-TOKEN-abc123"
env = dict(os.environ, PATH=f"{tmp}:{os.environ['PATH']}",
           PC_BRIDGE_URL="https://example.invalid/run",
           PC_BRIDGE_TOKEN=TOKEN)
script = tmp / "b.py"
script.write_text(m.group(1))
r = subprocess.run([sys.executable, str(script), "echo hello"],
                   capture_output=True, text=True, env=env, timeout=60)

argv = argv_log.read_text() if argv_log.exists() else ""
stdin = stdin_log.read_text() if stdin_log.exists() else ""
ok = True


def check(label, cond, why):
    global ok
    ok = ok and cond
    print(f"[{'PASS' if cond else 'FAIL'}] {label}\n         because: {why}")


check("bridge() reached curl at all", "FAKE_BRIDGE_OK" in r.stdout,
      f"stdout={r.stdout.strip()!r} stderr={r.stderr.strip()[:200]!r}")
check("token is NOT in curl's argv", TOKEN not in argv,
      f"argv would be visible to any `ps` on the box. argv={argv.strip()!r}")
check("token IS in the stdin config", TOKEN in stdin,
      "if it were absent the request would simply be unauthenticated")
check("argv is just --config -", argv.split() == ["--config", "-"],
      f"nothing else should be on the command line; got {argv.split()}")
check("the command payload survives", "echo hello" in stdin or "data-binary" in stdin,
      "the shell command travels as JSON via a temp data file")

# the temp data file must be cleaned up
leftovers = [p for p in Path(tempfile.gettempdir()).glob("*.json")
             if p.stat().st_mtime > (Path(script).stat().st_mtime - 5)
             and TOKEN in p.read_text(errors="ignore")]
check("no temp file contains the token", not leftovers,
      f"the data file holds the command, never the token; found {leftovers}")

print("\n" + ("ALL OK" if ok else "PROBLEMS"))
raise SystemExit(0 if ok else 1)
