#!/usr/bin/env python3
"""Build the P1 replay's synthetic session transcript (deterministic; every string is synthetic, secret-shaped ones FAKE).

    python3 tests/fixtures/jev_pipes/make_fixture.py <dir>    # writes <dir>/transcript.jsonl and <dir>/persisted-0001.txt

The records carry the production key sets captured in record_shapes.json (tests/test_jev_pipes_replay.py holds them
equal, AF-AP-42). The conversation, in file order (tool_use ids toolu_fx_NN):
  01 Bash make test        a 150-line build log with one failure and a total    (scored)
  02 Bash cat report.json  a JSON document                                      (document, structured)
  03 Read render.py        numbered Python source                               (secondary; document, reference)
  04 Grep                  70 path:line matches                                 (secondary; scored)
  05 Bash ls -la           30 lines                                             (few_chunks)
  06 Bash env | grep       80 lines with a FAKE api key                         (scored; looksSecret, not archived)
  07 Bash make test again  an error result                                      (tool_error; a re-run of 01)
  -- compaction --
  08 Bash pytest           a 180-line test log                                  (scored)
  09 Bash tail build.log   persisted: a 150-line file behind a 2 KB preview    (persisted path)
  then assistant texts that reuse a module name from 08's middle (the miss lookahead's material).
"""
import json
import sys
from pathlib import Path

SESSION = "00000000-fixture-0000-0000-000000000000"
CWD = "/home/fixture/widget-demo"
VERSION = "2.1.274"
_counter = [0]


def _uuid():
    _counter[0] += 1
    return f"00000000-0000-4000-8000-{_counter[0]:012d}"


def _base(kind, parent):
    return {"cwd": CWD, "entrypoint": "cli", "gitBranch": "fixture", "isSidechain": False, "parentUuid": parent,
            "sessionId": SESSION, "slug": "fixture-session", "timestamp": f"2026-09-25T00:00:{_counter[0] % 60:02d}.000Z",
            "type": kind, "userType": "external", "uuid": _uuid(), "version": VERSION}


def prompt(parent, text):
    rec = _base("user", parent)
    rec.update({"message": {"content": text, "role": "user"}, "origin": {"kind": "human"}, "permissionMode": "default",
                "promptId": "prompt-fixture-1", "promptSource": "typed", "queueSkipAttachments": False, "turnOrigin": "human"})
    return rec


def assistant(parent, request, context, blocks):
    rec = _base("assistant", parent)
    usage = {"cache_creation_input_tokens": 1000, "cache_read_input_tokens": context - 1100, "input_tokens": 100,
             "output_tokens": 50}
    rec.update({"advisorModel": "fixture-advisor", "apiBlockIndex": 0, "effort": "high", "perTurnEffort": "high", "requestId": request,
                "message": {"container": None, "content": blocks, "context_management": None, "diagnostics": None,
                            "id": f"msg_{request}", "input_transformations": [], "model": "fixture-model", "role": "assistant",
                            "stop_details": None, "stop_reason": "tool_use", "stop_sequence": None, "type": "message",
                            "usage": usage}})
    return rec


def tool_use(uid, name, tool_input):
    return {"caller": {"type": "direct"}, "id": uid, "input": tool_input, "name": name, "type": "tool_use"}


def tool_result(parent, uid, content, record, is_error=False):
    rec = _base("user", parent)
    rec.update({"message": {"content": [{"content": content, "is_error": is_error, "tool_use_id": uid, "type": "tool_result"}],
                            "role": "user"},
                "promptId": "prompt-fixture-1", "sourceToolAssistantUUID": parent, "toolUseResult": record})
    return rec


def bash_record(stdout, stderr="", **extra):
    return dict({"interrupted": False, "isImage": False, "noOutputExpected": False, "stderr": stderr, "stdout": stdout}, **extra)


def build_log():
    lines = ["make: entering directory 'widget-demo'"]
    for i in range(1, 149):
        if i == 77:
            lines.append("FAILED tests/test_widget.py::test_render_7431 - AssertionError: widget frame 7431 misaligned")
        elif i % 25 == 0:
            lines.append(f"tests/test_widget.py::test_case_{i:04d} PASSED")
        else:
            lines.append(f"  compiling widget-demo/obj/module_{i:04d}.o from widget-demo/src/module_{i:04d}.c [cached]")
    lines.append("Tests: 1 failed, 147 passed, 148 total")
    return "\n".join(lines)


def report_json():
    return json.dumps({"target": "widget-demo", "tests": [{"name": f"test_case_{i:04d}", "status": "passed", "ms": 3 + i % 7}
                                                           for i in range(40)]}, indent=1)


def read_source():
    body = []
    for i in range(1, 61):
        body.append(f"def render_frame_{i:03d}(widget):" if i % 10 == 1 else f"    widget.draw(step={i}, frame=7431)")
    return "\n".join(f"{n:6d}\t{line}" for n, line in enumerate(body, start=1))


def grep_matches():
    return "\n".join(f"widget-demo/src/module_{i:04d}.c:{i * 3}:    render_7431(frame_{i:04d}, &state);" for i in range(70))


def ls_listing():
    return "\n".join(f"-rw-r--r-- 1 fixture fixture {1000 + i * 37:6d} Sep 25 00:00 artifact_{i:04d}.bin" for i in range(30))


def env_dump():
    lines = [f"FIXTURE_SETTING_{i:03d}=value-{i:03d}-for-the-widget-demo-fixture-environment" for i in range(79)]
    lines.insert(40, "FIXTURE_API_KEY=FAKE-KEY-0000-not-a-secret")
    return "\n".join(lines)


def pytest_log():
    lines = ["============================= test session starts =============================="]
    for i in range(1, 179):
        if i == 90:
            lines.append("widget-demo/tests/test_frames.py::test_frame_0090 FAILED")
        else:
            lines.append(f"widget-demo/tests/test_frames.py::test_frame_{i:04d} PASSED   [ {i * 100 // 180:3d}%]  obj/module_{i + 500:04d}.o")
    lines.append("========================= 1 failed, 177 passed in 12.34s =========================")
    return "\n".join(lines)


def persisted_log():
    return "\n".join(f"[{i:05d}] worker-{i % 4} processed batch_{i:05d} in 0.{i % 9}s" for i in range(150))


def build(directory):
    _counter[0] = 0
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    persisted_path = directory / "persisted-0001.txt"
    persisted_path.write_text(persisted_log())
    # the preview names the file by its base name only, so the model-visible text (and the pruner's maxChars) does not
    # depend on the directory a test builds into; the record's persistedOutputPath carries the real path
    preview = ("Output too large (" + str(len(persisted_log())) + " characters). Full output saved to: persisted-0001.txt"
               + "\n\nPreview (first 2KB):\n" + persisted_log()[:2000])
    recs = []
    last = None

    def add(rec):
        nonlocal last
        recs.append(rec)
        last = rec["uuid"]
        return rec

    add(prompt("00000000-0000-4000-8000-000000000000", "Build the widget-demo fixture and report the failing test names."))
    calls = [
        ("toolu_fx_01", "Bash", {"command": "make -C widget-demo test", "description": "Run the fixture tests"}, build_log(), False),
        ("toolu_fx_02", "Bash", {"command": "cat widget-demo/build/report.json", "description": "Read the report"}, report_json(), False),
        ("toolu_fx_03", "Read", {"file_path": "/home/fixture/widget-demo/src/render.py"}, read_source(), False),
        ("toolu_fx_04", "Grep", {"pattern": "render_7431", "path": "widget-demo", "output_mode": "content"}, grep_matches(), False),
        ("toolu_fx_05", "Bash", {"command": "ls -la widget-demo/build", "description": "List artifacts"}, ls_listing(), False),
        ("toolu_fx_06", "Bash", {"command": "env | grep FIXTURE", "description": "Show fixture settings"}, env_dump(), False),
    ]
    context = 20000
    for n, (uid, name, tool_input, output, error) in enumerate(calls, start=1):
        add(assistant(last, f"req_fx_{n:02d}", context, [{"text": f"Step {n}: running {name}.", "type": "text"},
                                                          tool_use(uid, name, tool_input)]))
        record = bash_record(output) if name == "Bash" else ({"file": {"content": output, "filePath": tool_input.get("file_path"),
                                                                      "numLines": 60, "startLine": 1, "totalLines": 60},
                                                             "type": "text"} if name == "Read" else
                                                            {"content": output, "filenames": [], "mode": "content",
                                                             "numFiles": 70, "numLines": 70})
        add(tool_result(last, uid, output, record, error))
        context += 3000
    failing = "Exit code 2\n" + build_log()
    add(assistant(last, "req_fx_07", context, [tool_use("toolu_fx_07", "Bash", {"command": "make -C widget-demo test",
                                                                                "description": "Re-run the fixture tests"})]))
    add(tool_result(last, "toolu_fx_07", failing, "Error: " + failing, True))
    boundary = _base("system", last)
    boundary.update({"compactMetadata": {"preTokens": context, "trigger": "auto"}, "content": "Conversation compacted",
                     "level": "info", "logicalParentUuid": last, "subtype": "compact_boundary"})
    boundary["parentUuid"] = None
    add(boundary)
    summary = _base("user", last)
    summary.update({"isCompactSummary": True, "isVisibleInTranscriptOnly": True, "promptId": "prompt-fixture-1",
                    "turnOrigin": "compact",
                    "message": {"content": "This session is being continued from a previous conversation. Summary: the "
                                           "widget-demo fixture build ran; test_render_7431 failed.", "role": "user"}})
    add(summary)
    add(assistant(last, "req_fx_08", 9000, [tool_use("toolu_fx_08", "Bash", {"command": "python3 -m pytest widget-demo -q",
                                                                              "description": "Run pytest"})]))
    add(tool_result(last, "toolu_fx_08", pytest_log(), bash_record(pytest_log())))
    add(assistant(last, "req_fx_09", 12000, [tool_use("toolu_fx_09", "Bash", {"command": "tail -n 150 widget-demo/build.log",
                                                                              "description": "Read the build log"})]))
    add(tool_result(last, "toolu_fx_09", preview, bash_record(persisted_log()[:2000], persistedOutputPath=str(persisted_path),
                                                              persistedOutputSize=len(persisted_log()))))
    add(assistant(last, "req_fx_10", 15000, [{"text": "The module_0547.o object is stale; test_frame_0090 failed.", "type": "text"}]))
    add(assistant(last, "req_fx_11", 15500, [{"text": "Done: one failure in the pytest run.", "type": "text"}]))
    path = directory / "transcript.jsonl"
    path.write_text("".join(json.dumps(r, sort_keys=True) + "\n" for r in recs))
    return path


if __name__ == "__main__":
    print(build(sys.argv[1]))
