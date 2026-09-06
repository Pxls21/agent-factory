#!/usr/bin/env python3
"""VERIFY-B5b mutation harness.

Each mutant: a fresh scratch tree copied from the PRISTINE round-6 files
(never the shared repo tree), one targeted edit to frame_tee.py, then the
FULL committed suite.  A mutant is KILLED if >=1 test fails, SURVIVED if the
suite is all-green.  Prints the killing test ids.
"""
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import time

# PROBE_WORK: the work dir holding base/ (a copy or symlink of the tree under test) — sandbox default below.
_VB6 = os.environ.get("PROBE_WORK", "/tmp/claude-0/-home-user/bdab799a-dc80-5933-9c9e-c80f206f9a17/scratchpad/vb6")

BASE = pathlib.Path(_VB6 + "")
PRISTINE_TEE = BASE / "pristine" / "frame_tee.py"
PRISTINE_TEST = BASE / "pristine" / "test_s0_01_frame_tee.py"
RUNS = BASE / "mutruns"

# (id, description, [(old, new), ...])
MUTANTS = [
    # --- Area A: the c2a drain (R5-B5-F1) ---
    ("A1", "delete the c2a drain loop (exit as soon as the agent exits)",
     [("    while ti.is_alive():\n        time.sleep(0.1)\n        current_rec = state[\"recorded_c2a\"]",
       "    while False and ti.is_alive():\n        time.sleep(0.1)\n        current_rec = state[\"recorded_c2a\"]")]),
    ("A2", "c2a drain stall timeout 5s -> 0s (give up immediately)",
     [("        elif time.monotonic() - stall_start_c2a >= stall_timeout:",
       "        elif time.monotonic() - stall_start_c2a >= 0:")]),
    ("A3", "drop the 'drain c2a: stopped' write_errors entry",
     [("    if c2a_stalled and state[\"forwarded_c2a\"] < state[\"recorded_c2a\"]:\n        state[\"write_errors\"].append(",
       "    if False and c2a_stalled and state[\"forwarded_c2a\"] < state[\"recorded_c2a\"]:\n        state[\"write_errors\"].append(")]),
    ("A4", "swap the two counts in the 'drain c2a' message",
     [("            \"drain c2a: stopped with %d recorded, %d forwarded\"\n            % (state[\"recorded_c2a\"], state[\"forwarded_c2a\"]))",
       "            \"drain c2a: stopped with %d recorded, %d forwarded\"\n            % (state[\"forwarded_c2a\"], state[\"recorded_c2a\"]))")]),
    ("A5", "c2a pump stops recording after a forward error (revert the F1 fix)",
     [("                if not forward_broken:\n                    try:\n                        dst.write(line)\n                        dst.flush()\n                        state[\"forwarded_%s\" % direction] += 1\n                    except BrokenPipeError:\n                        state[\"write_errors\"].append(\"forward %s: BrokenPipeError\" % direction)\n                        forward_broken = True\n                        if close_dst:",
       "                if not forward_broken:\n                    try:\n                        dst.write(line)\n                        dst.flush()\n                        state[\"forwarded_%s\" % direction] += 1\n                    except BrokenPipeError:\n                        state[\"write_errors\"].append(\"forward %s: BrokenPipeError\" % direction)\n                        forward_broken = True\n                        break\n                        if close_dst:")]),
    ("A6", "drained ignores the c2a direction (a2c-only, the round-4 shape)",
     [("    drained = (state[\"forwarded_a2c\"] == state[\"recorded_a2c\"]\n               and state[\"forwarded_c2a\"] == state[\"recorded_c2a\"])",
       "    drained = (state[\"forwarded_a2c\"] == state[\"recorded_a2c\"])")]),

    # --- Area B: the a2c drain ---
    ("B1", "drop the 'drain a2c: stopped' write_errors entry",
     [("    if a2c_stalled and state[\"forwarded_a2c\"] < state[\"recorded_a2c\"]:\n        state[\"write_errors\"].append(",
       "    if False and a2c_stalled and state[\"forwarded_a2c\"] < state[\"recorded_a2c\"]:\n        state[\"write_errors\"].append(")]),
    ("B2", "swap the two counts in the 'drain a2c' message",
     [("            \"drain a2c: stopped with %d recorded, %d forwarded\"\n            % (state[\"recorded_a2c\"], state[\"forwarded_a2c\"]))",
       "            \"drain a2c: stopped with %d recorded, %d forwarded\"\n            % (state[\"forwarded_a2c\"], state[\"recorded_a2c\"]))")]),
    ("B3", "'drain a2c' -> 'drain c2a' (direction inverted in the message)",
     [("            \"drain a2c: stopped with %d recorded, %d forwarded\"",
       "            \"drain c2a: stopped with %d recorded, %d forwarded\"")]),

    # --- Area C: the A21d running-status writes ---
    ("C1", "no running status from the c2a pump (drop _write_status in pump_fd)",
     [("                _write_status()\n        finally:\n            df.close()\n            if direction == \"c2a\":",
       "                pass\n        finally:\n            df.close()\n            if direction == \"c2a\":")]),
    ("C2", "no running status from the a2c pump (drop _write_status in pump_pipe)",
     [("                _write_status()\n        finally:\n            df.close()\n            if close_dst and not forward_broken:",
       "                pass\n        finally:\n            df.close()\n            if close_dst and not forward_broken:")]),
    ("C3", "final write always says final=False",
     [("            obj = {\n                \"final\": final,", "            obj = {\n                \"final\": False,")]),
    ("C4", "exit fields populated even when not final",
     [("                \"agent_returncode\": agent_rc if final else None,",
       "                \"agent_returncode\": agent_rc,"),
      ("                \"exit_code\": exit_code_val if final else None,",
       "                \"exit_code\": exit_code_val,")]),
    ("C5", "updated_seq frozen at 0",
     [("                \"updated_seq\": seq[0],", "                \"updated_seq\": 0,")]),
    ("C6", "updated_seq off by one",
     [("                \"updated_seq\": seq[0],", "                \"updated_seq\": max(0, seq[0] - 1),")]),
    ("C7", "drop the updated_utc key",
     [("                \"updated_utc\": _utc_now(),\n", "")]),
    ("C8", "add an extra key to the status (A21d says exactly twelve)",
     [("                \"updated_utc\": _utc_now(),",
       "                \"updated_utc\": _utc_now(),\n                \"tee_version\": \"v2\",")]),
    ("C9", "drained hard-coded true in the status",
     [("            obj = {\n                \"final\": final,\n                \"agent_returncode\": agent_rc if final else None,\n                \"drained\": _drained,",
       "            obj = {\n                \"final\": final,\n                \"agent_returncode\": agent_rc if final else None,\n                \"drained\": True,")]),

    # --- Area D: atomicity ---
    ("D1", "non-atomic write straight onto tee-status.json (no tmp+replace)",
     [("            try:\n                with open(_status_tmp, \"w\") as f:\n                    json.dump(obj, f, indent=2)\n                    f.write(\"\\n\")\n                os.replace(_status_tmp, _status_path)",
       "            try:\n                with open(_status_path, \"w\") as f:\n                    json.dump(obj, f, indent=2)\n                    time.sleep(0.0005)\n                    f.write(\"\\n\")")]),
    ("D2", "unlink+rename instead of atomic replace",
     [("                os.replace(_status_tmp, _status_path)",
       "                try:\n                    os.unlink(_status_path)\n                except OSError:\n                    pass\n                time.sleep(0.0005)\n                os.rename(_status_tmp, _status_path)")]),
    ("D3", "status write no longer serialised (drop status_lock)",
     [("    def _write_status(final=False, exit_code_val=None, agent_rc=None):\n        with status_lock:",
       "    def _write_status(final=False, exit_code_val=None, agent_rc=None):\n        if True:")]),

    ("D1b", "non-atomic write, no artificial delay (is test_rewrite_is_atomic robust?)",
     [("            try:\n                with open(_status_tmp, \"w\") as f:\n                    json.dump(obj, f, indent=2)\n                    f.write(\"\\n\")\n                os.replace(_status_tmp, _status_path)",
       "            try:\n                with open(_status_path, \"w\") as f:\n                    json.dump(obj, f, indent=2)\n                    f.write(\"\\n\")")]),
    # --- Area E: the SIGTERM handler (F4) ---
    ("E1", "SIGTERM handler not installed",
     [("    signal.signal(signal.SIGTERM, _sigterm_handler)", "    pass")]),
    ("E2", "SIGTERM handler does not record the reason",
     [("        state[\"write_errors\"].append(\"terminated: SIGTERM\")", "        pass")]),
    ("E3", "SIGTERM handler exits 0",
     [("        _write_status(final=True, exit_code_val=70, agent_rc=agent_rc)\n        os._exit(70)",
       "        _write_status(final=True, exit_code_val=0, agent_rc=agent_rc)\n        os._exit(0)")]),
    ("E4", "SIGTERM handler writes a non-final status",
     [("        _write_status(final=True, exit_code_val=70, agent_rc=agent_rc)",
       "        _write_status(final=False, exit_code_val=70, agent_rc=agent_rc)")]),
    ("E5", "SIGTERM handler writes no status at all",
     [("        _write_status(final=True, exit_code_val=70, agent_rc=agent_rc)\n        os._exit(70)",
       "        os._exit(70)")]),

    # --- Area F: write_errors arms and their exact text ---
    ("F1", "forward BrokenPipe reason drops the direction (round-5 survivor V36)",
     [("                        state[\"write_errors\"].append(\"forward %s: BrokenPipeError\" % direction)\n                        forward_broken = True\n                        if close_dst:",
       "                        state[\"write_errors\"].append(\"forward: BrokenPipeError\")\n                        forward_broken = True\n                        if close_dst:")]),
    ("F2", "forward BrokenPipe direction INVERTED in both pumps (round-5 survivor V37)",
     [("\"forward %s: BrokenPipeError\" % direction",
       "\"forward %s: BrokenPipeError\" % (\"a2c\" if direction == \"c2a\" else \"c2a\")")]),
    ("F3", "forward OSError arm removed from pump_pipe (F5 regression)",
     [("                    except OSError as e:\n                        state[\"write_errors\"].append(\"forward %s: %s\" % (direction, e))\n                        forward_broken = True\n                _write_status()\n        finally:\n            df.close()\n            if close_dst and not forward_broken:",
       "                _write_status()\n        finally:\n            df.close()\n            if close_dst and not forward_broken:")]),
    ("F4", "directional write error reason drops the errno text",
     [("                    state[\"write_errors\"].append(\"directional %s: %s\" % (direction, e))",
       "                    state[\"write_errors\"].append(\"directional %s: write failed\" % direction)")]),
    ("F5", "timeline write error reason drops the seq",
     [("                            state[\"write_errors\"].append(\"timeline %s seq %d: %s\" % (direction, seq[0], e))",
       "                            state[\"write_errors\"].append(\"timeline %s: %s\" % (direction, e))")]),
    ("F6", "forward_broken latch removed (round-5 survivor V16: unbounded repeats)",
     [("                        forward_broken = True\n                        if close_dst:\n                            try:\n                                dst.close()\n                            except Exception:\n                                pass\n                    except OSError as e:\n                        state[\"write_errors\"].append(\"forward %s: %s\" % (direction, e))\n                        forward_broken = True",
       "                        if close_dst:\n                            try:\n                                dst.close()\n                            except Exception:\n                                pass\n                    except OSError as e:\n                        state[\"write_errors\"].append(\"forward %s: %s\" % (direction, e))\n                        forward_broken = True")]),
    ("F7", "status write failure never printed (F10 regression)",
     [("                if final:\n                    print(\"frame_tee: failed to write tee-status.json: %s\" % e, file=sys.stderr)",
       "                pass")]),

    # --- Area G: framedir validation (F7) ---
    ("G1", "lexists -> exists (dangling symlink regression)",
     [("    if os.path.lexists(framedir) and not os.path.isdir(framedir):",
       "    if os.path.exists(framedir) and not os.path.isdir(framedir):")]),
    ("G2", "empty-framedir check removed",
     [("    if not framedir:\n        print(\"frame_tee: S0_01_FRAMEDIR is empty\", file=sys.stderr)\n        raise SystemExit(64)",
       "    pass")]),
    ("G3", "not-a-directory check removed entirely",
     [("    if os.path.lexists(framedir) and not os.path.isdir(framedir):\n        print(\"frame_tee: S0_01_FRAMEDIR is not a directory: %s\" % framedir, file=sys.stderr)\n        raise SystemExit(64)",
       "    pass")]),
    ("G4", "framedir exit code 64 -> 1",
     [("        print(\"frame_tee: S0_01_FRAMEDIR is not a directory: %s\" % framedir, file=sys.stderr)\n        raise SystemExit(64)",
       "        print(\"frame_tee: S0_01_FRAMEDIR is not a directory: %s\" % framedir, file=sys.stderr)\n        raise SystemExit(1)")]),

    # --- Area H: exit-code decision ---
    ("H1", "exit_code always the agent's code (ignore drained/write_errors)",
     [("    if drained and not state[\"write_errors\"]:\n        exit_code = agent_code\n    else:\n        exit_code = 70",
       "    exit_code = agent_code")]),
    ("H2", "write_errors ignored in the exit decision (drained only)",
     [("    if drained and not state[\"write_errors\"]:", "    if drained:")]),
    ("H3", "signal normalisation removed (A21b)",
     [("    rc = proc.returncode\n    if rc < 0:\n        agent_code = 128 + (-rc)\n    else:\n        agent_code = rc",
       "    rc = proc.returncode\n    agent_code = rc")]),
    ("H4", "stdin_reader_done never set (round-5 4-F14)",
     [("            if direction == \"c2a\":\n                state[\"stdin_reader_done\"] = True", "            pass")]),
]


def run_one(mid, desc, edits, only=None):
    if only and mid not in only:
        return None
    d = RUNS / mid
    if d.exists():
        shutil.rmtree(d)
    (d / "tests").mkdir(parents=True)
    (d / "proofs" / "S0-01" / "tools").mkdir(parents=True)
    src = PRISTINE_TEE.read_text()
    for old, new in edits:
        if old not in src:
            print("%-4s SKIPPED-PATCH-DID-NOT-APPLY  %s" % (mid, desc))
            return {"id": mid, "desc": desc, "result": "PATCH-FAILED"}
        n = src.count(old)
        src = src.replace(old, new)
        if mid in ("F2",) and n != 2:
            print("%-4s note: pattern applied %d times" % (mid, n))
    (d / "proofs" / "S0-01" / "tools" / "frame_tee.py").write_text(src)
    shutil.copy(PRISTINE_TEST, d / "tests" / "test_s0_01_frame_tee.py")
    t0 = time.time()
    p = subprocess.run([sys.executable, "-m", "pytest", "tests/test_s0_01_frame_tee.py",
                        "-q", "-p", "no:cacheprovider", "--timeout=300"] if False else
                       [sys.executable, "-m", "pytest", "tests/test_s0_01_frame_tee.py",
                        "-q", "-p", "no:cacheprovider"],
                       cwd=str(d), capture_output=True, text=True, timeout=1500)
    el = time.time() - t0
    out = p.stdout + p.stderr
    fails = sorted(set(re.findall(r"^(?:FAILED|ERROR) (\S+)", out, re.M)))
    if not fails:
        fails = sorted(set(re.findall(r"^(tests/\S+::\S+) ", out, re.M)))
    summary = [l for l in out.splitlines() if l.strip()][-1] if out.strip() else "(no output)"
    killed = p.returncode != 0
    print("%-4s %-9s rc=%-3d %6.1fs  %-58s | %s" % (
        mid, "KILLED" if killed else "SURVIVED", p.returncode, el, summary[:58], desc))
    if fails:
        print("      killed by: %s" % ", ".join(f.split("::")[-1] for f in fails[:8]))
    return {"id": mid, "desc": desc, "result": "KILLED" if killed else "SURVIVED",
            "summary": summary, "killers": [f.split("::")[-1] for f in fails], "secs": round(el, 1)}


if __name__ == "__main__":
    only = set(sys.argv[1:]) or None
    RUNS.mkdir(exist_ok=True)
    res = []
    for mid, desc, edits in MUTANTS:
        r = run_one(mid, desc, edits, only)
        if r:
            res.append(r)
    outp = BASE / ("mutresults-%s.json" % (("-".join(sorted(only)) if only and len(only) < 6 else "batch")))
    outp.write_text(json.dumps(res, indent=1))
    k = sum(1 for r in res if r["result"] == "KILLED")
    print("TOTAL %d  KILLED %d  SURVIVED %d  PATCH-FAILED %d"
          % (len(res), k, sum(1 for r in res if r["result"] == "SURVIVED"),
             sum(1 for r in res if r["result"] == "PATCH-FAILED")))
