#!/usr/bin/env python3
"""Deterministic contract tests for the Hermes lane done gate."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GATE = ROOT / "harness-ports" / "bin" / "lane-done-gate.py"
_spec = importlib.util.spec_from_file_location("lane_done_gate", GATE)
assert _spec is not None and _spec.loader is not None
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

PASS = 0
FAIL = 0


def check(label: str, condition: bool, why: str) -> None:
    global PASS, FAIL
    if condition:
        PASS += 1
    else:
        FAIL += 1
    print(f"[{'PASS' if condition else 'FAIL'}] {label}\n         because: {why}")


def run(mode: str, payload, *, raw: bool = False):
    data = payload if raw else json.dumps(payload)
    return subprocess.run(
        [sys.executable, str(GATE), mode],
        input=data,
        capture_output=True,
        text=True,
        cwd=ROOT,
        timeout=30,
    )


def ledger(session: str) -> Path:
    tag = hashlib.sha256(str(ROOT).encode()).hexdigest()[:12]
    sid = "".join(c for c in session if c.isalnum() or c in "-_")[:64] or "default"
    return Path(tempfile.gettempdir()) / f"lane-done-gate-{tag}-{sid}.jsonl"


def clear(*sessions: str) -> None:
    for session in sessions:
        ledger(session).unlink(missing_ok=True)


def edit(session: str, path: str, tool: str = "write_file", tool_input=None):
    args = tool_input if tool_input is not None else {"path": path, "content": "x"}
    return run("record", {
        "hook_event_name": "post_tool_call", "tool_name": tool,
        "tool_input": args, "session_id": session, "cwd": str(ROOT), "extra": {},
    })


def terminal(session: str, command: str, exit_code=0, *, result_marker=True):
    result = {"output": "", "error": None}
    if result_marker:
        result["exit_code"] = exit_code
    return run("record", {
        "hook_event_name": "post_tool_call", "tool_name": "terminal",
        "tool_input": {"command": command}, "session_id": session, "cwd": str(ROOT),
        "extra": {"result": json.dumps(result), "status": "ok", "tool_call_id": "fake"},
    })


def gate(session: str, paths):
    return run("gate", {
        "hook_event_name": "pre_verify", "tool_name": None, "tool_input": None,
        "session_id": session, "cwd": str(ROOT),
        "extra": {"changed_paths": paths, "attempt": 0, "final_response": "SECRET REPORT", "coding": True},
    })


def one_stderr_line(proc) -> bool:
    return proc.stderr.count("\n") == 1 and bool(proc.stderr.strip())


def fact(session: str):
    return json.loads(ledger(session).read_text().splitlines()[-1])


def test_order_and_gate() -> None:
    clear("order-a", "order-b", "noncheck")
    edit("order-a", "src/covered.py")
    terminal("order-a", "pytest -q tests/test_x.py", 0)
    result = gate("order-a", ["src/covered.py"])
    check("edit then passing check leaves the gate silent",
          result.returncode == 0 and result.stdout == "" and result.stderr == "",
          f"rc={result.returncode} stdout={result.stdout!r} stderr={result.stderr!r}")

    terminal("order-b", "bash harness-ports/tests/test_pc_lane.sh", 0)
    edit("order-b", "harness-ports/bin/changed.sh")
    result = gate("order-b", ["harness-ports/bin/changed.sh"])
    data = json.loads(result.stdout)
    check("passing check then edit nudges with path and last check",
          data.get("decision") == "block"
          and "harness-ports/bin/changed.sh" in data.get("reason", "")
          and "bash harness-ports/tests/test_pc_lane.sh" in data.get("reason", "")
          and "COMPLETE final report" in data.get("reason", "")
          and "SECRET REPORT" not in result.stdout
          and len(result.stdout.encode()) <= 1500,
          f"stdout={result.stdout.strip()!r}")

    terminal("noncheck", "echo ok", 0)
    terminal("noncheck", "pytest -q | tail -1", 0)
    edit("noncheck", "src/noncheck.py")
    result = gate("noncheck", ["src/noncheck.py"])
    check("zero-exit non-checks do not silence the gate",
          json.loads(result.stdout).get("decision") == "block"
          and fact("noncheck")["kind"] == "edit",
          "echo and a pipe without pipefail both preceded the edit; gate blocked")


def test_exit_codes_and_bad_result() -> None:
    cases = [(1, True, "exit 1"), (0, False, "missing"), ("0", True, "string"), (True, True, "bool")]
    outcomes = []
    for index, (value, present, label) in enumerate(cases):
        session = f"exit-{index}"
        clear(session)
        proc = terminal(session, "pytest -q tests/test_x.py", value, result_marker=present)
        outcomes.append((label, fact(session), proc))
    check("nonzero, missing, string and bool exit codes are never passing",
          all(row[1]["passing"] is False for row in outcomes)
          and outcomes[0][1]["exit_code"] == 1
          and all(row[1]["exit_code"] is None for row in outcomes[1:]),
          ", ".join(f"{label}:{item['reason']}" for label, item, _ in outcomes))

    clear("bad-json", "result-missing")
    proc = run("record", {
        "hook_event_name": "post_tool_call", "tool_name": "terminal",
        "tool_input": {"command": "pytest -q"}, "session_id": "bad-json",
        "cwd": str(ROOT), "extra": {"result": "not json"},
    })
    check("unparseable extra.result records not-passing and one stderr line",
          proc.returncode == 0 and proc.stdout == "" and one_stderr_line(proc)
          and fact("bad-json")["passing"] is False
          and "not JSON" in fact("bad-json")["reason"],
          f"rc={proc.returncode} stderr={proc.stderr.strip()!r} fact={fact('bad-json')}")

    missing = run("record", {
        "hook_event_name": "post_tool_call", "tool_name": "terminal",
        "tool_input": {"command": "pytest -q"}, "session_id": "result-missing",
        "cwd": str(ROOT), "extra": {},
    })
    check("missing extra.result records not-passing and one stderr line",
          missing.returncode == 0 and missing.stdout == "" and one_stderr_line(missing)
          and fact("result-missing")["passing"] is False,
          f"stderr={missing.stderr.strip()!r} fact={fact('result-missing')}")


def test_code_paths_and_patch() -> None:
    clear("paths-md", "paths-text", "paths-transcript", "paths-shebang", "v4a")
    terminal("paths-md", "pytest -q", 0)
    edit("paths-md", "notes/report.md")
    result = gate("paths-md", ["notes/report.md"])
    check("Markdown edits never trigger the gate", result.stdout == "", f"stdout={result.stdout!r}")

    edit("paths-text", "notes/report.txt")
    edit("paths-transcript", "transcripts/tool.py")
    text_result = gate("paths-text", ["notes/report.txt"])
    transcript_result = gate("paths-transcript", ["transcripts/tool.py"])
    check("text and transcript edits never trigger the gate",
          text_result.stdout == "" and transcript_result.stdout == "",
          f"text={text_result.stdout!r} transcript={transcript_result.stdout!r}")

    with tempfile.TemporaryDirectory(prefix="done-gate-code-", dir=ROOT.parent) as td:
        script = Path(td) / "runner"
        script.write_bytes(b"#!/bin/sh\nexit 0\n")
        rel = os.path.relpath(script, ROOT)
        edit("paths-shebang", rel)
        result = gate("paths-shebang", [rel])
        check("an extensionless shebang file counts as code",
              json.loads(result.stdout).get("decision") == "block",
              f"path={rel} stdout={result.stdout.strip()!r}")

    patch_text = """*** Begin Patch
*** Add File: src/a.py
+x
*** Update File: scripts/b.sh
@@
-old
+new
*** Delete File: src/c.ts
*** Move to: src/d.ts
*** Update File: src/a.py
*** End Patch
"""
    result = edit("v4a", "unused", "patch", {"mode": "patch", "patch": patch_text})
    rows = [json.loads(line) for line in ledger("v4a").read_text().splitlines()]
    paths = [row.get("path") for row in rows if row.get("kind") == "edit"]
    check("V4A multi-file patch records every named path once",
          result.stdout == "" and paths
          == ["src/a.py", "scripts/b.sh", "src/c.ts", "src/d.ts"],
          f"paths={paths}")


def test_sessions_location_and_malformed() -> None:
    clear("session-a", "session-b")
    edit("session-a", "src/a.py")
    edit("session-b", "src/b.py")
    a, b = ledger("session-a"), ledger("session-b")
    a_rows = [json.loads(line) for line in a.read_text().splitlines()]
    b_rows = [json.loads(line) for line in b.read_text().splitlines()]
    a_paths = [row.get("path") for row in a_rows]
    b_paths = [row.get("path") for row in b_rows]
    foreign_cwd = run("record", {
        "hook_event_name": "post_tool_call", "tool_name": "write_file",
        "tool_input": {"path": "src/c.py", "content": "x"},
        "session_id": "session-a", "cwd": str(ROOT.parent), "extra": {},
    })
    check("sessions use separate ledgers outside the repository",
          a != b and a.is_file() and b.is_file()
          and a_paths == ["src/a.py"]
          and b_paths == ["src/b.py"]
          and foreign_cwd.returncode == 0
          and not a.resolve().is_relative_to(ROOT.resolve())
          and not b.resolve().is_relative_to(ROOT.resolve()),
          f"a={a} b={b}")

    result = run("record", "{bad", raw=True)
    check("malformed stdin is fail-soft with empty stdout and one stderr line",
          result.returncode == 0 and result.stdout == "" and one_stderr_line(result),
          f"rc={result.returncode} stderr={result.stderr.strip()!r}")


def test_terminal_only_edit_rule() -> None:
    clear("unknown-none", "unknown-pass")
    result = gate("unknown-none", ["src/terminal-only.py"])
    check("terminal-only code edit nudges when no passing check exists",
          json.loads(result.stdout).get("decision") == "block"
          and "src/terminal-only.py" in result.stdout,
          f"stdout={result.stdout.strip()!r}")

    terminal("unknown-pass", "pytest -q", 0)
    result = gate("unknown-pass", ["src/terminal-only.py"])
    check("terminal-only code edit is reported but does not nudge after a passing check",
          result.stdout == "" and one_stderr_line(result)
          and "unknown edit order" in result.stderr,
          f"stdout={result.stdout!r} stderr={result.stderr.strip()!r}")


def test_nudge_path_limit() -> None:
    session = "path-limit"
    clear(session)
    paths = [f"src/file-{index}.py" for index in range(8)]
    for path in paths:
        edit(session, path)
    result = gate(session, paths)
    data = json.loads(result.stdout)
    reason = data["reason"]
    check("nudge names at most five paths and summarizes the remainder",
          data.get("decision") == "block"
          and all(path in reason for path in paths[:5])
          and all(path not in reason for path in paths[5:])
          and "and 3 more" in reason
          and len(result.stdout.encode()) <= 1500,
          f"bytes={len(result.stdout.encode())} reason={reason!r}")


DIRECT_ACCEPTED = [
    "pytest -q tests/test_x.py",
    "python -m pytest -q tests/test_x.py",
    "python3 -m pytest -n 8 -q tests/test_x.py",
    "/opt/venv/bin/python -m pytest -q tests/test_x.py",
    "timeout 180 python -m pytest -q tests/test_x.py",
    "S0_01_VENUE=pc python -m pytest -q tests/test_x.py",
    "bash harness-ports/tests/test_pc_lane.sh",
    "python3 harness-ports/tests/test_hermes_spool.py",
    "bash scripts/lane_gate.sh -r abc -f x -t y",
    "bash scripts/test_summary.sh tests/test_x.py",
    "cargo test",
    "ruff check .",
]
WRAPPED_ACCEPTED = [
    "set -o pipefail; bash harness-ports/tests/test_pc_lane.sh | tee out.log; rc=${PIPESTATUS[0]}; exit \"$rc\"",
    "set -o pipefail; python3 harness-ports/tests/test_hermes_spool.py | tee out.log; rc=${PIPESTATUS[0]}; printf 'RC=%s\\n' \"$rc\"; exit \"$rc\"",
    "set -o pipefail; bash scripts/lane_gate.sh -r abc -f x -t y | tee out.log; rc=${PIPESTATUS[0]}; echo rc=$rc; exit $rc",
    "set -o pipefail; bash scripts/test_summary.sh tests/test_x.py | tee out.log; rc=${PIPESTATUS[0]}; exit $rc",
]
REJECTED = [
    "bash -n harness-ports/bin/pc-lane.sh",
    "python -m pyflakes scripts/x.py",
    "echo ok",
    "pytest -q | tail -1",
    "set -o pipefail; bash harness-ports/tests/test_pc_lane.sh | tee out; rc=${PIPESTATUS[1]}; exit \"$rc\"",
    "set -o pipefail; bash harness-ports/tests/test_pc_lane.sh | tee out; rc=${PIPESTATUS[0]}; exit 0",
    "set -o pipefail; bash harness-ports/tests/test_pc_lane.sh | tee out; rc=${PIPESTATUS[0]}; true; exit \"$rc\"",
    "set -o pipefail; bash harness-ports/tests/test_pc_lane.sh | tee out; rc=${PIPESTATUS[0]}; exit \"$rc\" || true",
    "set -o pipefail; bash harness-ports/tests/test_pc_lane.sh | tee out; rc=${PIPESTATUS[0]}; exit \"$rc\" &",
    "set -o pipefail; bash harness-ports/tests/test_pc_lane.sh | tee out; rc=${PIPESTATUS[0]}; exit \"$rc\"; echo done",
    "printf x; bash harness-ports/tests/test_pc_lane.sh",
    "bash harness-ports/tests/test_pc_lane.sh | tee out; rc=${PIPESTATUS[0]}; exit \"$rc\"",
    "set -o pipefail; bash harness-ports/tests/not_a_test | tee out; rc=${PIPESTATUS[0]}; exit \"$rc\"",
    "set -o pipefail; bash harness-ports/tests/test_pc_lane.sh | tee out; rc=${PIPESTATUS[0]}; printf x; exit 0",
    "bash harness-ports/tests/test_pc_lane.sh && true",
    "printf x; bash harness-ports/tests/test_pc_lane.sh",
]


def _grade_command(command: str, stub_exit: int, scratch: Path) -> int:
    replacements = [
        r"/opt/venv/bin/python -m pytest -q tests/test_x\.py",
        r"timeout 180 python -m pytest -q tests/test_x\.py",
        r"S0_01_VENUE=pc python -m pytest -q tests/test_x\.py",
        r"python3 -m pytest -n 8 -q tests/test_x\.py",
        r"python -m pytest -q tests/test_x\.py",
        r"pytest -q tests/test_x\.py",
        r"python3 harness-ports/tests/test_hermes_spool\.py",
        r"bash harness-ports/tests/test_pc_lane\.sh",
        r"bash scripts/lane_gate\.sh -r abc -f x -t y",
        r"bash scripts/test_summary\.sh tests/test_x\.py",
        r"cargo test",
        r"ruff check \." ,
    ]
    rendered = command
    for pattern in replacements:
        rendered, count = re.subn(pattern, f"./check-stub {stub_exit}", rendered, count=1)
        if count:
            break
    else:
        raise AssertionError(f"accepted shape had no grade replacement: {command}")
    result = subprocess.run(["bash", "-c", rendered], cwd=scratch, capture_output=True, text=True)
    return result.returncode


def test_classifier_and_bash_grade() -> None:
    decisions = [(cmd, *_mod.counts_as_check(cmd)) for cmd in DIRECT_ACCEPTED + WRAPPED_ACCEPTED + REJECTED]
    accepted_ok = all(counts for _, counts, _ in decisions[:len(DIRECT_ACCEPTED) + len(WRAPPED_ACCEPTED)])
    rejected_ok = all(not counts for _, counts, _ in decisions[len(DIRECT_ACCEPTED) + len(WRAPPED_ACCEPTED):])
    check("closed classifier accepts all intended shapes and rejects 16 near misses",
          accepted_ok and rejected_ok,
          f"intended_accepted={len(DIRECT_ACCEPTED) + len(WRAPPED_ACCEPTED)} "
          f"near_misses_rejected={sum(1 for _, value, _ in decisions[len(DIRECT_ACCEPTED) + len(WRAPPED_ACCEPTED):] if not value)}")

    with tempfile.TemporaryDirectory(prefix="done-gate-grade-") as td:
        scratch = Path(td)
        stub = scratch / "check-stub"
        stub.write_text("#!/usr/bin/env bash\nexit \"$1\"\n")
        stub.chmod(0o755)
        grades = [(cmd, _grade_command(cmd, 1, scratch), _grade_command(cmd, 0, scratch))
                  for cmd in DIRECT_ACCEPTED + WRAPPED_ACCEPTED]
    check("every accepted shape propagates a failing and passing stub through bash",
          all(fail_rc != 0 and pass_rc == 0 for _, fail_rc, pass_rc in grades),
          f"graded={len(grades)} failures={[(c, f, p) for c, f, p in grades if f == 0 or p != 0]}")
    check("bash -n is rejected because syntax is not behavioral verification",
          _mod.counts_as_check("bash -n harness-ports/bin/pc-lane.sh")[0] is False,
          "classifier=False; syntax-only commands do not cover changed behavior")


def test_corpus_reclassification() -> None:
    # The full 109-command corpus is a coordinator read-only measurement. These
    # supplied representative rows cover each distinct command class in it.
    corpus = [
        "bash harness-ports/tests/test_pc_lane.sh",
        "bash harness-ports/tests/test_pc_lane.sh > out 2>&1; rc=$?; tail -40 out; echo rc=$rc",
        WRAPPED_ACCEPTED[0],
        "set -o pipefail; bash harness-ports/tests/run-all.sh | tee out.log; rc=${PIPESTATUS[0]}; printf 'RUN_ALL_RC=%s\\n' \"$rc\"; exit \"$rc\"",
        WRAPPED_ACCEPTED[2],
        "bash -n harness-ports/bin/pc-lane.sh scripts/pc_lane.sh && echo syntax-ok",
        "python3 harness-ports/tests/test_hermes_session_export.py && python3 harness-ports/tests/test_qwen_matrix.py",
        "bash scripts/test_summary.sh tests/test_x.py",
        "timeout 180 /opt/venv/bin/python -m pytest -q tests/test_x.py",
        "mkdir -p bt && S0_01_VENUE=pc python -m pytest -q tests/test_x.py",
        "python -m pyflakes scripts/x.py; python3 scripts/ap_screen.py scripts/x.py",
        "git status --short",
    ]
    after = [cmd for cmd in corpus if _mod.counts_as_check(cmd)[0]]
    check("supplied corpus classes reclassify from C1's 0/109 to the closed project set",
          len(after) == 7
          and corpus[1] not in after and corpus[5] not in after and corpus[10] not in after,
          f"representative_before=0/12 representative_after={len(after)}/12; full baseline supplied=0/109")


def main() -> int:
    try:
        test_order_and_gate()
        test_exit_codes_and_bad_result()
        test_code_paths_and_patch()
        test_sessions_location_and_malformed()
        test_terminal_only_edit_rule()
        test_nudge_path_limit()
        test_classifier_and_bash_grade()
        test_corpus_reclassification()
    finally:
        tag = hashlib.sha256(str(ROOT).encode()).hexdigest()[:12]
        for path in Path(tempfile.gettempdir()).glob(f"lane-done-gate-{tag}-*"):
            path.unlink(missing_ok=True)
    print(f"\nlane done gate: {PASS} passed, {FAIL} failed")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
