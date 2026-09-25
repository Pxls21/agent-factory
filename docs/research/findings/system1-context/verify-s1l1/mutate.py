"""Mutants of the COPY's hook, one at a time, graded by the builder's own test file (copied beside it). Restores after each."""
import subprocess, sys
from pathlib import Path
RM = Path("repo_m").resolve()
HOOK = RM / ".claude/hooks/system1-context.py"
ORIG = HOOK.read_text(encoding="utf-8")
MUT = {
 "m1 window lock removed (no flock)": ("                fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)\n", "                pass\n"),
 "m2 budget counts characters, not bytes": ("            cost = len(ln.encode()) + 1 + (4 if gap else 0)", "            cost = len(ln) + 1 + (4 if gap else 0)"),
 "m3 telemetry logs the Write/Edit path": ('    rec["matched"] = [r["id"] for r in rows]\n', '    rec["matched"] = [r["id"] for r in rows]\n    rec["path"] = tool_fields(tool, ti, payload.get("cwd"))[0]\n'),
 "m4 telemetry logs the prompt's words (lower-cased)": ('    q = tokens(prompt[:PROMPT_SCAN_CHARS])\n', '    q = tokens(prompt[:PROMPT_SCAN_CHARS])\n    rec["words"] = sorted(q)\n'),
 "m5 marker stores the prompt's words": ('                if new:\n', '                if rec.get("event") == "UserPromptSubmit": new = list(new) + sorted(tokens(payload.get("prompt") or ""))\n                if new:\n'),
 "m6 continuation lines dropped (a single-string selector takes one line)": ("            while j + 1 < e and lines[j + 1].strip() and not ENTRY_START_RX.match(lines[j + 1]):\n                j += 1\n        else:",
                                                                   "            pass\n        else:"),
 "m7 the 7-day prune removed": ("        if hit or now - os.stat(path).st_mtime > MARKER_MAX_AGE_S:", "        if hit:"),
 "m8 unresolved rows raise instead of skip": ("        except LookupError:\n            rec[\"skipped\"]", "        except ZeroDivisionError:\n            rec[\"skipped\"]"),
}
for name, (a, b) in MUT.items():
    assert ORIG.count(a) == 1, (name, ORIG.count(a))
    HOOK.write_text(ORIG.replace(a, b), encoding="utf-8")
    try:
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", "tests/test_system1_context.py",
                            "--basetemp", str(RM.parent / "bt" / "mut")], cwd=str(RM), capture_output=True, text=True, timeout=280)
        last = [l for l in r.stdout.splitlines() if l.strip()][-1]
        failed = [l.split("::", 1)[1].split(" ")[0] for l in r.stdout.splitlines() if l.startswith("FAILED")]
        print(f"{'KILLED ' if r.returncode else 'SURVIVED'} {name:70s} {last[:60]} {failed[:1]}")
    finally:
        HOOK.write_text(ORIG, encoding="utf-8")
assert HOOK.read_text(encoding="utf-8") == ORIG
print("hook restored:", HOOK.read_text(encoding="utf-8") == ORIG)
