"""scripts/hiccup_scan.py: exact counts over a fixture built from the REAL transcript record shapes (read from the E4.3
parsers in docs/research/findings/JEV-LEVERAGE-EVIDENCE-2026-09-24.md and from a streamed key-shape probe of the live
transcripts on 2026-09-24), secrets never on the page, malformed lines counted, byte-identical pages, the closed family
map, and the advisory Jev column (KC-J1b). Every secret below is a fake string. No test here calls a model: the Jev
column tests inject a recording `rank`. Every expected number is written out by hand from the fixture below.
"""
import datetime
import importlib.util
import json
import pathlib
import random
import re
import shutil
import subprocess
import sys
import time

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts" / "hiccup_scan.py"


def _load():
    spec = importlib.util.spec_from_file_location("hiccup_scan_under_test", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


hs = _load()

SECRETS = ["cVMjXl1uWH1c9Ogzoc_-k60yOL5KP5pr", "eyJhbGciOiJIUzI1NiJ9", "payload.sig", "3c3d5f1e8a2b4c6d9e0f1234567890ab",
           "leading-twist-aruba-pulse", "hunter2hunter", "hunterNhunter"]
AGENT = "afix0000000000001"
SESSION = "sess-0001"
LS = chr(0x2028)       # a LINE SEPARATOR inside transcript text; built from its code point, never typed


def _env(ts, uuid, agent=None):
    rec = {"parentUuid": None, "isSidechain": agent is not None, "userType": "external", "cwd": "/home/user/agent-factory",
           "sessionId": SESSION, "version": "2.1.0", "gitBranch": "main", "uuid": uuid, "timestamp": ts}
    if agent:
        rec["agentId"] = agent
    return rec


def _usage(ctx_k):
    return {"input_tokens": ctx_k, "cache_creation_input_tokens": 0, "cache_read_input_tokens": 1000 * ctx_k,
            "output_tokens": 7, "service_tier": "standard", "cache_creation": {}, "inference_geo": "", "iterations": [],
            "server_tool_use": {}, "output_tokens_details": {}, "speed": "standard"}


def assistant(ts, uuid, req, model, content, ctx_k, stop="tool_use", agent=None):
    rec = _env(ts, uuid, agent)
    rec.update(type="assistant", requestId=req, message={
        "id": "msg_" + req, "type": "message", "role": "assistant", "model": model, "content": content,
        "stop_reason": stop, "stop_sequence": None, "stop_details": None, "diagnostics": None, "usage": _usage(ctx_k)})
    return rec


def tool_use(uid, name, **inp):
    return {"type": "tool_use", "id": uid, "name": name, "input": inp}


def result(ts, uuid, blocks, tur=None, agent=None):
    rec = _env(ts, uuid, agent)
    rec.update(type="user", message={"role": "user", "content": blocks}, promptId="p1", sourceToolAssistantUUID="a",
               toolUseResult=tur if tur is not None else {"stdout": "", "stderr": "", "interrupted": False,
                                                          "isImage": False, "noOutputExpected": False})
    return rec


def tr(uid, content, is_error):
    b = {"tool_use_id": uid, "type": "tool_result", "content": content}
    if is_error is not None:
        b["is_error"] = is_error
    return b


def attachment(ts, uuid, att):
    rec = _env(ts, uuid)
    rec.update(type="attachment", attachment=att)
    return rec


D10, D11, D12 = "2026-03-10T", "2026-03-11T", "2026-03-12T"
TASK_REMINDER = attachment(D10 + "09:07:00.000Z", "u18", {"type": "task_reminder", "itemCount": 1, "content": [
    {"id": "1", "subject": "x", "description": "y", "activeForm": "z", "status": "pending", "blocks": [], "blockedBy": []}]})

MAIN = [
    dict(_env(D10 + "09:00:00.000Z", "u1"), type="user", message={"role": "user", "content": "please build it"}),
    assistant(D10 + "09:00:01.000Z", "u2", "req_1", "claude-opus-5-5", [{"type": "text", "text": "running"}], 1),
    assistant(D10 + "09:00:02.000Z", "u3", "req_1", "claude-opus-5-5", [tool_use("toolu_1", "Bash", command="ls")], 1),
    result(D10 + "09:00:03.000Z", "u4", [tr("toolu_1", "Exit code 1\n\nls: cannot access '/tmp/ps/bt': No such file or directory", True)]),
    assistant(D10 + "09:01:00.000Z", "u5", "req_2", "claude-opus-5-5", [tool_use("toolu_2", "Edit", file_path="/x")], 2),
    result(D10 + "09:01:01.000Z", "u6", [tr("toolu_2", "<tool_use_error>String to replace not found in file.\nString: foo</tool_use_error>", True)]),
    assistant(D10 + "09:02:00.000Z", "u7", "req_3", "claude-opus-5-5", [tool_use("toolu_3", "Bash", command="sleep 30")], 3),
    result(D10 + "09:02:01.000Z", "u8", [tr("toolu_3", "<tool_use_error>Blocked: sleep 30 followed by: cat /tmp/x.log. To wait for a condition, use Monitor with an until-loop</tool_use_error>", True)]),
    assistant(D10 + "09:03:00.000Z", "u9", "req_4", "claude-opus-5-5", [tool_use("toolu_4", "Bash", command="rm")], 4),
    result(D10 + "09:03:01.000Z", "u10", [tr("toolu_4", "Permission for this action was denied by the Claude Code auto mode classifier. Reason: [Modify Shared Resources]. If you have other tasks that don't depend on this action, continue with those.", True)]),
    assistant(D10 + "09:04:00.000Z", "u11", "req_5", "claude-opus-5-5", [tool_use("toolu_5", "mcp__github__get_job_logs", job_id=1)], 5),
    result(D10 + "09:04:01.000Z", "u12", [tr("toolu_5", [{"type": "text", "text": "failed to get job logs: HTTP 404 for sk-3c3d5f1e8a2b4c6d9e0f1234567890ab password: hunter2hunter\nsecond line"}], True)]),
    assistant(D10 + "09:05:00.000Z", "u13", "req_6", "claude-opus-5-5", [tool_use("toolu_6", "Bash", command="curl")], 6),
    result(D10 + "09:05:01.000Z", "u14", [tr("toolu_6", "Exit code 2\nAuthorization: Bearer eyJhbGciOiJIUzI1NiJ9.payload.sig and AGENT_TOKEN=cVMjXl1uWH1c9Ogzoc_-k60yOL5KP5pr at https://leading-twist-aruba-pulse.trycloudflare.com/exec", True)]),
    assistant(D10 + "09:05:30.000Z", "u15", "req_7", "claude-opus-5-5", [tool_use("toolu_7", "Bash", command="yes")], 7),
    result(D10 + "09:05:31.000Z", "u16", [tr("toolu_7", "ok\n" * 100, False)]),
    assistant(D10 + "09:06:00.000Z", "u17", "req_8", "claude-opus-5-5", [tool_use(
        "toolu_8", "Agent", description="Build JT1 fixture" + LS + "lane AGENT_TOKEN=cVMjXl1uWH1c9Ogzoc_-k60yOL5KP5pr",
        prompt="do it", subagent_type="code-implementer", model="opus")], 8),
    TASK_REMINDER,
    attachment(D10 + "09:08:00.000Z", "u19", {"type": "silent_turn_reminder", "text": "The user hasn't heard from you in a while - say in a few words what you are doing."}),
    dict(_env(D10 + "09:09:00.000Z", "u20"), type="system", subtype="compact_boundary", content="Conversation compacted",
         level="info", logicalParentUuid="u19", compactMetadata={"trigger": "auto", "preTokens": 786089, "postTokens": 40000,
                                                                 "durationMs": 60000, "cumulativeDroppedTokens": 0,
                                                                 "preCompactDiscoveredTools": []}),
    result(D10 + "10:30:00.000Z", "u21", [tr("toolu_8", [{"type": "text", "text": "done\nagentId: %s (use SendMessage to continue)" % AGENT}], None)],
           tur={"agentId": AGENT, "agentType": "code-implementer", "status": "completed", "prompt": "do it"}),
    assistant(D11 + "08:00:00.000Z", "u22", "req_9", "claude-opus-5-5", [{"type": "thinking", "thinking": "", "signature": "s"}], 9, stop="refusal"),
    '{"type": "assistant", "message": ',
    "[1, 2, 3]",
    b'\xff\xfe{"type": "user"}',
    {"type": "last-prompt", "lastPrompt": "x", "sessionId": SESSION},
    assistant(D12 + "12:00:00.000Z", "u27", "req_10", "claude-fable-5-1",
              [tool_use("toolu_10", "Edit", file_path="/y"), tool_use("toolu_11", "Bash", command="x")], 10),
    result(D12 + "12:00:01.000Z", "u28", [
        tr("toolu_10", "<tool_use_error>File has not been read yet. Read it first before writing to it.</tool_use_error>", True),
        tr("toolu_11", "<tool_use_error>InputValidationError: [{'code': 'invalid_type'}]</tool_use_error>", True)]),
]
SUB = [
    dict(_env(D10 + "09:06:05.000Z", "s1", AGENT), type="user", message={"role": "user", "content": "the brief"}),
    dict(assistant(D10 + "09:06:10.000Z", "s2", "req_s1", "claude-opus-4-8", [tool_use("toolu_s1", "Grep", pattern="x")], 0, agent=AGENT)),
    result(D10 + "09:06:40.000Z", "s3", [tr("toolu_s1", "Ripgrep search timed out after 20 seconds. The search may have matched files but did not complete in time.", True)], agent=AGENT),
    assistant(D10 + "10:29:00.000Z", "s4", "req_s2", "claude-opus-4-8", [{"type": "text", "text": "report"}], 0, stop="end_turn", agent=AGENT),
]
SUB[1]["message"]["usage"] = _usage(0) | {"input_tokens": 0, "cache_read_input_tokens": 5000}
SUB[3]["message"]["usage"] = _usage(0) | {"input_tokens": 0, "cache_read_input_tokens": 7000}


def _line(rec):
    if isinstance(rec, bytes):
        return rec + b"\n"
    return (rec if isinstance(rec, str) else json.dumps(rec)).encode("utf-8") + b"\n"


def write_fixture(d):
    d = pathlib.Path(d)
    (d / SESSION / "subagents").mkdir(parents=True)
    main = d / (SESSION + ".jsonl")
    sub = d / SESSION / "subagents" / ("agent-%s.jsonl" % AGENT)
    main.write_bytes(b"".join(_line(r) for r in MAIN))
    sub.write_bytes(b"".join(_line(r) for r in SUB))
    return main, sub


def run_cli(*args):
    return subprocess.run([sys.executable, str(TOOL), *map(str, args)], capture_output=True, text=True, timeout=120)


@pytest.fixture
def fixture_dir(tmp_path):
    write_fixture(tmp_path / "proj")
    return tmp_path / "proj"


# ---------- A6: exact counts over the real shapes ----------

def test_fixture_counts_are_exact(fixture_dir):
    sc = hs.Scan(hs.load_families())
    main, sub = fixture_dir / (SESSION + ".jsonl"), fixture_dir / SESSION / "subagents" / ("agent-%s.jsonl" % AGENT)
    sc.feed(str(main))
    sc.feed(str(sub))
    assert dict(sc.counts) == {"assistant_usage_model": 13, "tool_use": 11, "tool_result": 11, "tool_error": 9,
                               "task_reminder": 1, "silent_turn_reminder": 1, "compaction": 1, "refusal_stop": 1}
    assert sc.inputs == {"main": [1, main.stat().st_size, 28, 3], "subagent": [1, sub.stat().st_size, 4, 0]}
    assert sc.clock == "2026-03-12T12:00:01.000000000Z"
    assert len(sc.clusters) == 9 and sum(1 for c in sc.clusters.values() if c["family"] is None) == 1
    assert sc.task_reminder == [1, len(_line(TASK_REMINDER))]
    assert sc.agent_desc == {AGENT: "Build JTN fixture lane KEY=V"}
    assert sorted(sc.agents) == [AGENT] and len(sc.agents[AGENT]["requests"]) == 2


def test_page_rows_are_exact(fixture_dir, tmp_path):
    out = tmp_path / "HICCUPS.md"
    r = run_cli("--project-dir", fixture_dir, "--out", out)
    assert r.returncode == 0, r.stderr
    page = out.read_text(encoding="utf-8")
    main = fixture_dir / (SESSION + ".jsonl")
    sub = fixture_dir / SESSION / "subagents" / ("agent-%s.jsonl" % AGENT)
    want = [
        "Clock: 2026-03-12T12:00:01Z",
        "| main | 1 | %d | 28 | 3 |" % main.stat().st_size,
        "| subagent | 1 | %d | 4 | 0 |" % sub.stat().st_size,
        "| total | 2 | %d | 32 | 3 |" % (main.stat().st_size + sub.stat().st_size),
        # day | tool calls | errors | rate | compactions | ctx median | ctx p90 | refusals | not-heard | sleep | denials
        "| 2026-03-10 | 9 | 7 | 77.8% | 1 | 5002 | 8008 | 0 | 1 | 1 | 1 |",
        "| 2026-03-11 | 0 | 0 | - | 0 | 9009 | 9009 | 1 | 0 | 0 | 0 |",
        "| 2026-03-12 | 2 | 2 | 100.0% | 0 | 10010 | 10010 | 0 | 0 | 0 | 0 |",
        "| 2026-03-10 | claude-opus-5-5 9 · claude-opus-4-8 2 |",
        "| 2026-03-11 | claude-opus-5-5 1 |",
        "| 2026-03-12 | claude-fable-5-1 1 |",
        "| %s | `Build JTN fixture lane KEY=V` | claude-opus-4-8 2 | 2 | 1 | 0 | 2026-03-10 09:06 | 2026-03-10 10:29 |" % AGENT,
        "## Error clusters (top 9 of 9 clusters, 9 errors)",
        "Errors by family: edit anchor 2, UNCOVERED 1, auto-mode denial 1, exit code N 1, harness blocked a foreground "
        "sleep 1, input validation 1, missing path 1, ripgrep timeout 1.",
        "| 1 | `Exit code N :: ls: cannot access '/tmp/ps/bt': No such file or directory` | missing path | none | 1 | "
        "2026-03-10 09:00 | 2026-03-10 09:00 | Bash |",
        # D-076 (a): scrubbed on the raw text first, the sk- key reads `sk-<redacted>` (normalized first, it read `T`)
        "| 5 | `failed to get job logs: HTTP N for sk-<redacted> password: <redacted>` | UNCOVERED | - | 1 | "
        "2026-03-10 09:04 | 2026-03-10 09:04 | mcp__github__get_job_logs |",
        "| 6 | `Exit code N :: Authorization: Bearer <redacted> and KEY=V at U` | exit code N | none | 1 | 2026-03-10 09:05 | "
        "2026-03-10 09:05 | Bash |",
        "| 9 | `<tool_use_error>T: [{'code': 'invalid_type'}]</tool_use_error>` | input validation | none | 1 | "
        "2026-03-12 12:00 | 2026-03-12 12:00 | Bash |",
        "`task_reminder` attachments: 1 records, %d bytes," % len(_line(TASK_REMINDER)),
    ]
    for w in want:
        assert w in page, "missing: %s" % w
    sections = [ln for ln in page.splitlines() if ln.startswith("## ")]
    assert [s.split(" (")[0] for s in sections] == ["## Inputs", "## Per day", "## Served model per day", "## Agents",
                                                   "## Error clusters", "## Context cost", "## New this week"]


def test_fake_secrets_never_reach_the_page(fixture_dir, tmp_path):
    out = tmp_path / "HICCUPS.md"
    assert run_cli("--project-dir", fixture_dir, "--out", out).returncode == 0
    page = out.read_bytes()
    for s in SECRETS:
        assert s.encode() not in page, "secret on the page: %s..." % s[:8]
    text = page.decode("utf-8")
    assert "password: <redacted>" in text and "KEY=V" in text and "Bearer <redacted>" in text   # both stages ran
    assert b"\xe2\x80\xa8" not in page and b"\xe2\x80\xa9" not in page                        # U+2028 became a space


def test_malformed_lines_are_counted_never_a_crash(tmp_path):
    p = tmp_path / "junk.jsonl"
    p.write_bytes(b'{"type": "assistant"\n\xff\xfe\n[]\n"a string"\n{"type": "user", "message": {"content": [7, null]}}\n'
                  b'{"type": "assistant", "timestamp": 12, "message": {"content": "x", "usage": [], "model": 5}}\n')
    out = tmp_path / "H.md"
    r = run_cli("--transcript", p, "--out", out)
    assert r.returncode == 0, r.stderr
    assert "| main | 1 | %d | 6 | 4 |" % p.stat().st_size in out.read_text()
    assert "unparsable=4" in r.stdout and "clock=none" in r.stdout


def test_same_input_bytes_give_the_same_page_bytes_and_no_wall_clock(fixture_dir, tmp_path):
    a, b = tmp_path / "a.md", tmp_path / "b.md"
    assert run_cli("--project-dir", fixture_dir, "--out", a).returncode == 0
    time.sleep(1.1)
    assert run_cli("--project-dir", fixture_dir, "--out", b).returncode == 0
    assert a.read_bytes() == b.read_bytes()
    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    assert today not in a.read_text(), "the page carries the wall-clock date"
    assert re.findall(r"^Clock: (.*)$", a.read_text(), re.M) == ["2026-03-12T12:00:01Z"]


def test_limit_bytes_stops_before_the_line_that_would_pass_it(fixture_dir, tmp_path):
    main = fixture_dir / (SESSION + ".jsonl")
    first3 = sum(len(_line(r)) for r in MAIN[:3])
    out = tmp_path / "H.md"
    r = run_cli("--transcript", main, "--limit-bytes", first3 + len(_line(MAIN[3])) - 1, "--out", out)
    assert r.returncode == 0, r.stderr
    assert "| main | 1 | %d | 3 | 0 |" % first3 in out.read_text()
    assert "tool_use=1 tool_result=0 errors=0" in r.stdout
    assert run_cli("--transcript", main, "--limit-bytes", 0, "--out", out).returncode == 64


def test_no_input_and_a_missing_transcript_exit_2(tmp_path):
    r = run_cli("--project-dir", tmp_path, "--out", tmp_path / "x.md")
    assert r.returncode == 2 and "no transcript" in r.stderr and not (tmp_path / "x.md").exists()
    r = run_cli("--transcript", tmp_path / "absent.jsonl", "--out", tmp_path / "x.md")
    assert r.returncode == 2 and "no such transcript" in r.stderr


# ---------- D-9: the closed family map ----------

def test_family_map_is_closed_and_every_covering_rule_is_real():
    fams = hs.load_families()
    names = [n for _, n, _ in fams]
    assert len(names) == len(set(names)) and hs.SLEEP_FAMILY in names and hs.DENIAL_FAMILY in names
    registry = (ROOT / "docs" / "INCIDENT-LOG.md").read_text(encoding="utf-8")
    claude = (ROOT / "CLAUDE.md").read_text(encoding="utf-8").lower().replace("`", "").splitlines()
    for _, name, rule in fams:
        if rule == "none":
            continue
        m = re.fullmatch(r"AF-AP-(\d+)", rule)
        if m:
            assert re.search(r"^\| *AF-AP-%s *\|" % m.group(1), registry, re.M), rule
            continue
        assert rule.startswith("CLAUDE.md: "), "rule %r is neither none, an AF-AP id nor a CLAUDE.md phrase" % rule
        words = [w for w in re.findall(r"[a-z][a-z0-9_.-]{3,}", rule[len("CLAUDE.md: "):].lower())]
        windows = [" ".join(claude[i:i + 3]) for i in range(len(claude))]      # a CLAUDE.md sentence may wrap
        assert words and any(all(w in win for w in words) for win in windows), "no CLAUDE.md passage holds %r" % rule


# first lines as E4.3 printed them (JEV-LEVERAGE-EVIDENCE-2026-09-24.md, error classes), completed to their real form
SHAPES = [
    ("Exit code 1\nTraceback (most recent call last):\n  File x", "python exception"),
    ("Exit code 143\nTerminated", "Terminated (SIGTERM)"),
    ("Exit code 128\nfatal: not a git repository (or any of the parent directories): .git", "cwd is not the repo"),
    ("Exit code 1\n\n", "exit code N"),
    ("Permission for this action was denied by the Claude Code auto mode classifier. Reason: x", "auto-mode denial"),
    ("<tool_use_error>String to replace not found in file.", "edit anchor"),
    ("<tool_use_error>Found 2 matches of the string to replace, but replace_all is false.", "edit anchor not unique"),
    ("<tool_use_error>Blocked: sleep 30 followed by: cat /tmp/claude-0/x", "harness blocked a foreground sleep"),
    ("<tool_use_error>InputValidationError: TaskUpdate failed due to the following issues:", "input validation"),
    ("Ripgrep search timed out after 20 seconds. The search may have matched", "ripgrep timeout"),
    ("The user doesn't want to proceed with this tool use. The tool use was rejected (eg. if it was a file edit, "
     "the new_string was NOT written to the file). STOP what you are doing", "user declined"),
    ("The working-directory isolation context for this agent was lost, so this command would run", "worktree isolation lost"),
    ("failed to cancel workflow run: POST https://api.github.com/x 403 Resource not accessible", None),
]


@pytest.mark.parametrize("text,family", SHAPES, ids=[s[1] or "UNCOVERED" for s in SHAPES])
def test_real_first_line_shapes_map_to_their_families(text, family):
    assert hs.family_of(hs.cluster_key(text), hs.load_families())[0] == family


def test_an_apostrophe_is_not_a_quote_but_a_long_quoted_string_is():
    # the live denial line (12:39Z) read `donSs request` before the fix: `'t depend ... user'` was taken as a quoted string.
    # The span between the two apostrophes is 52 characters (over the rule's 40) and the key stays under the 160 cut.
    line = "Permission for this action was denied. If you have tasks that don't depend on this action or anything else in the user's request, STOP"
    key = hs.cluster_key(line)
    assert len(line) < hs.CUT and key == line
    assert hs.excerpt('run "' + "word " * 10 + '" now') == "run S now"                   # 50 characters: a string
    assert hs.excerpt("say 'short quoted text' now") == "say 'short quoted text' now"    # 17: kept


def test_a_malformed_family_map_is_refused(tmp_path):
    base = (ROOT / "scripts" / "hiccup_families.tsv").read_text(encoding="utf-8")
    cases = {"two-fields": base + "x\tonly two\n", "bad-regex": base + "(\tbroken\tnone\n",
             "duplicate": base + "zzz\tuser declined\tnone\n",
             "no-sleep-row": "".join(ln + "\n" for ln in base.splitlines() if hs.SLEEP_FAMILY not in ln)}
    for name, text in cases.items():
        p = tmp_path / (name + ".tsv")
        p.write_text(text, encoding="utf-8")
        with pytest.raises(ValueError):
            hs.load_families(str(p))


# ---------- D-10: the advisory Jev column ----------

def _strip_jev_column(page):
    """The page with the last cell of every row of both cluster tables removed."""
    out, inside = [], False
    for ln in page.split("\n"):
        if ln.startswith("## "):
            inside = ln.startswith(("## Error clusters", "## New this week"))
        if inside and ln.startswith("|"):
            body = ln[:-1]                                   # drop the closing pipe
            ln = body[:body.rfind("|") + 1] if set(body) <= set("|-: ") else body[:body.rfind(" |") + 2]
        out.append(ln)
    return "\n".join(out)


def test_the_jev_column_is_advisory_and_changes_nothing_else(fixture_dir):
    sc = hs.Scan(hs.load_families())
    for p in sorted(fixture_dir.rglob("*.jsonl")):
        sc.feed(str(p))
    asked = []

    def rank(query, chunks, instructions=None, venue=None, timeout=None):
        asked.append((query, [c["id"] for c in chunks], instructions))
        return {"ranking": [[chunks[-1]["id"], 0.4321]] + [[c["id"], 0.1] for c in chunks[:-1]]}
    cands = [("AF-AP-1", "failed job logs download"), ("AF-AP-2", "password redacted secret"),
             ("CLAUDE.md:7", "unrelated words entirely here")]
    targets = hs.jev_targets(sc)
    assert [k for k, _ in targets] == [k for k, _ in hs.top_clusters(sc)]     # the fixture's new rows are its top rows
    col = hs.jev_column(targets, rank=rank, cands=cands)
    uncovered = [k for k, c in targets if c["family"] is None]
    assert list(col) == uncovered and len(asked) == 1
    assert asked[0][0] == uncovered[0] and asked[0][2] == hs.JEV_INSTRUCTIONS
    assert asked[0][1] == ["AF-AP-1", "AF-AP-2"]                   # only candidates that share a word, at most 8
    assert col[uncovered[0]] == "AF-AP-2 0.4321"
    plain = hs.build_page(sc, "src").decode()
    with_col = hs.build_page(sc, "src", jev=col).decode()
    assert with_col.count("| Jev suggests (advisory) |") == 2 and with_col.count("AF-AP-2 0.4321") == 2   # both tables
    assert with_col != plain and _strip_jev_column(with_col) == plain      # KC-J1b: nothing else on the page moved


def test_jev_unavailable_says_na_with_the_reason_and_stops_asking():
    calls = []

    def rank(query, chunks, **kw):
        calls.append(query)
        return None
    top = [("alpha job failed", {"family": None}), ("beta job failed", {"family": None}), ("gamma", {"family": "x"}),
           ("zzz qqq", {"family": None})]
    cands = [("AF-AP-9", "job failed badly")]
    col = hs.jev_column(top, rank=rank, reason_of=lambda: "local: connection refused; pc: no bridge env file", cands=cands)
    assert col == {"alpha job failed": "n/a (local: connection refused; pc: no bridge env file)",
                   "beta job failed": "n/a (local: connection refused; pc: no bridge env file)",
                   "zzz qqq": "n/a (no lexical candidate)"}
    assert calls == ["alpha job failed"]


def test_a_jev_module_that_does_not_import_is_na_not_a_crash(monkeypatch):
    monkeypatch.setitem(sys.modules, "jev", None)          # `import jev` now raises ModuleNotFoundError (an ImportError)
    col = hs.jev_column([("job failed", {"family": None})], cands=[("AF-AP-9", "job failed badly")])
    assert col == {"job failed": "n/a (jev.py did not import: ModuleNotFoundError)"}


def test_candidates_are_every_registry_row_and_every_quirk_marker():
    cands = hs.load_candidates()
    ids = [c for c, _ in cands]
    registry = (ROOT / "docs" / "INCIDENT-LOG.md").read_text(encoding="utf-8")
    n_rows = len(re.findall(r"^\| *AF-AP-\d+ *\|", registry, re.M))
    n_marks = len(re.findall(r"bit 2026-", (ROOT / "CLAUDE.md").read_text(encoding="utf-8")))
    assert len(ids) == len(set(ids)) == n_rows + n_marks
    assert all(t.strip() for _, t in cands)
    assert sum(1 for c in ids if c.startswith("CLAUDE.md:")) == n_marks
    top = hs.lexical_top("Exit code N :: pytest basetemp parent missing mkdir", cands)
    assert 0 < len(top) <= 8 and top == hs.lexical_top("Exit code N :: pytest basetemp parent missing mkdir", cands)


# ---------- D-11: the size cap ----------

def test_the_page_trims_the_oldest_agents_to_fit_and_refuses_what_cannot_fit(fixture_dir, tmp_path, monkeypatch):
    sc = hs.Scan(hs.load_families())
    for p in sorted(fixture_dir.rglob("*.jsonl")):
        sc.feed(str(p))
    for i in range(400):
        aid = "a%016d" % i
        sc.agents[aid] = {"models": {"claude-opus-5-5": 1}, "requests": {"r"}, "errors": 0, "refusals": 0,
                          "first": "2026-03-12T0%d:00:00.000000000Z" % (i % 10), "last": "2026-03-12T10:%02d:00.000000000Z" % (i % 60)}
        sc.agent_desc[aid] = "d" * 150
    page = hs.build_page(sc, "src")
    assert len(page) < hs.PAGE_MAX_BYTES
    m = re.search(rb"^(\d+) older agents active in the window are not shown \(the page cap\)\.$", page, re.M)
    assert m and 0 < int(m.group(1)) < 401
    monkeypatch.setattr(hs, "PAGE_MAX_BYTES", 500)
    out = tmp_path / "H.md"
    assert hs.main(["--project-dir", str(fixture_dir), "--out", str(out)]) == 2 and not out.exists()


# ---------- D-076 (a): scrub the raw text, normalize, scrub again, cut (VERIFY-JT1 F-16) ----------
# The five F-16 shapes: values of 8-19 characters that the raw scrub redacts and that normalizing FIRST shrank under the
# rule's floor (a digit run reads N), so letters of the value reached the page. Fake values only: every value's letters
# start QZJ or X4Z (normalized first they read QZJN or XNZN).
F16 = [("password: QZJ8123456", "password: <redacted>"),
       ("Authorization: Bearer X4Z9123456789", "Authorization: Bearer <redacted>"),
       ("X-Agent-Token: QZJ8765432109", "X-Agent-Token: <redacted>"),
       ("sk-QZJ8x4z9123456", "sk-<redacted>"),
       ("xoxb-QZJ8123456789", "xox-<redacted>")]


def write_f16_fixture(path):
    """Each shape in an error's first line (both cluster tables) and in an Agent description (the agents table)."""
    recs = []
    for i, (shape, _) in enumerate(F16):
        t = "2026-03-12T10:%02d:%%02d.000Z" % i
        aid = "af16x%02d" % i
        recs += [assistant(t % 0, "a%d" % i, "r%d" % i, "claude-opus-5-5", [tool_use("te%d" % i, "Bash", command="curl")], 1),
                 result(t % 1, "u%d" % i, [tr("te%d" % i, "curl: server said %s then closed\nnext line" % shape, True)]),
                 assistant(t % 2, "b%d" % i, "q%d" % i, "claude-opus-5-5",
                           [tool_use("ta%d" % i, "Agent", description="lane with " + shape, prompt="x")], 1),
                 result(t % 3, "v%d" % i, [tr("ta%d" % i, [{"type": "text", "text": "done\nagentId: %s" % aid}], None)],
                        tur={"agentId": aid}),
                 assistant(t % 4, "s%d" % i, "rs%d" % i, "claude-opus-5-5", [{"type": "text", "text": "ok"}], 1,
                           stop="end_turn", agent=aid)]
    path.write_bytes(b"".join(_line(r) for r in recs))
    return path


def test_the_f16_shapes_leave_no_letter_of_the_value_on_the_page(tmp_path):
    src = write_f16_fixture(tmp_path / "f16.jsonl")
    out = tmp_path / "H.md"
    r = run_cli("--transcript", src, "--out", out)
    assert r.returncode == 0, r.stderr
    page = out.read_text(encoding="utf-8")
    for shape, shown in F16:
        assert page.count("server said %s then closed" % shown) == 2, shape.split()[0]     # both cluster tables
        assert page.count("lane with %s" % shown) == 1, shape.split()[0]                   # the agents table
    for stub in ("QZJ", "X4Z", "XNZ"):
        assert stub not in page, "a piece of a value reached the page: %s" % stub


@pytest.mark.parametrize("shape", ["password: ab1234cd", "Authorization: Bearer abc12345xyz", "X-Agent-Token: zq12345678",
                                   "api_key: qw12er34ty", "sk-abcdef123456", "xoxb-abc1234567"])
def test_excerpt_scrubs_the_raw_text_before_it_normalizes(shape):
    # VERIFY-JT1 F-16's own six: the raw scrub redacts each; normalized first, five of them kept letters of the value
    line = "curl: server said %s then closed" % shape
    assert hs.excerpt(line) == "curl: server said %s then closed" % hs.scrub(shape)


def test_excerpt_scrubs_again_after_it_normalizes():
    # a head that only the normalization reveals (the control character between the name and `=` becomes a space): the
    # raw scrub cannot see it, the second scrub takes its value
    assert hs.excerpt("token" + chr(1) + "=QZJ8123x4z9k2m7") == "token =<redacted>"


# ---------- D-076 (c): KC-J1b as bytes, pages over the cap included (VERIFY-JT1 F-18) ----------

KC_SRC = "the project directory's `*.jsonl` and `*/subagents/*.jsonl`; byte limit per file: none"   # main()'s source


def _kc_env(ts, uuid, agent=None):
    r = {"parentUuid": None, "isSidechain": agent is not None, "userType": "external", "sessionId": "s", "uuid": uuid,
         "timestamp": ts}
    if agent:
        r["agentId"] = agent
    return r


def write_kc_fixture(d, n_agents=181, pad=3):
    """VERIFY-JT1's F-18 fixture (its /tmp/vjt1/kc_confirm.py, the same records in the same order): n_agents subagent
    transcripts, each joined to its Agent call's description, and two COVERED error clusters, so --jev asks no model."""
    (d / "s" / "subagents").mkdir(parents=True)
    main = []
    for i in range(n_agents):
        aid = "a%015d" % i
        desc = "lane %d " % i + ("wo " * 60)[: (pad if i == 0 else 100)]
        ts = "2026-09-20T%02d:%02d:00Z" % (i // 60 % 24, i % 60)
        main.append(dict(_kc_env(ts, "m%d" % i), type="assistant", requestId="rq%d" % i, message={
            "id": "mm%d" % i, "model": "claude-opus-5-5", "content": [
                {"type": "tool_use", "id": "tu%d" % i, "name": "Agent", "input": {"description": desc}}],
            "usage": {"input_tokens": 1}}))
        main.append(dict(_kc_env(ts, "r%d" % i), type="user", message={"role": "user", "content": [
            {"tool_use_id": "tu%d" % i, "type": "tool_result", "content": "done agentId: %s" % aid}]},
            toolUseResult={"agentId": aid}))
        (d / "s" / "subagents" / ("agent-%s.jsonl" % aid)).write_text(json.dumps(dict(
            _kc_env(ts, "x%d" % i, aid), type="assistant", requestId="rx%d" % i, message={
                "id": "mx%d" % i, "model": "claude-opus-5-5", "content": [], "usage": {"input_tokens": 2}})) + "\n")
    for j, text in enumerate(["Exit code 143\nTerminated", "<tool_use_error>Blocked: sleep 30 followed by: x</tool_use_error>"]):
        main.append(dict(_kc_env("2026-09-21T00:00:0%dZ" % j, "e%d" % j), type="assistant", requestId="re%d" % j, message={
            "id": "me%d" % j, "model": "claude-opus-5-5", "content": [
                {"type": "tool_use", "id": "te%d" % j, "name": "Bash", "input": {}}], "usage": {"input_tokens": 1}}))
        main.append(dict(_kc_env("2026-09-21T00:00:1%dZ" % j, "f%d" % j), type="user", message={"role": "user", "content": [
            {"tool_use_id": "te%d" % j, "type": "tool_result", "content": text, "is_error": True}]}))
    (d / "s.jsonl").write_text("".join(json.dumps(r) + "\n" for r in main))


def _agent_rows(page):
    return sum(1 for ln in page.split("## Agents")[1].split("## Error")[0].splitlines() if ln.startswith("| a0"))


def write_kc_fixture_in_the_f18_zone(d):
    """The F-18 fixture, sized for the scanner under test so that its page WITHOUT the column is under the cap and its
    page WITH the (unfilled) column is not: F-18's own zone. The size moves with the first agent's description (the
    verifier's pad was 3 on the PIN scanner) and, past that range, the agent count. -> (the scan, the agent count)."""
    n, pad = 181, 3
    for _ in range(10):
        shutil.rmtree(d, ignore_errors=True)
        write_kc_fixture(d, n, pad)
        sc = hs.Scan(hs.load_families())
        for p in sorted(d.glob("*.jsonl")) + sorted(d.glob("*/subagents/*.jsonl")):
            sc.feed(str(p))
        plain, withcol = len(hs.render(sc, KC_SRC).encode("utf-8")), len(hs.render(sc, KC_SRC, {}).encode("utf-8"))
        if plain < hs.PAGE_MAX_BYTES <= withcol:
            return sc, n
        pad += hs.PAGE_MAX_BYTES - (withcol - plain) // 2 - plain           # about one byte per character of the pad
        while pad < 0:
            n, pad = n - 1, pad + 150
        while pad > 150:
            n, pad = n + 1, pad - 150
    raise AssertionError("no fixture size lands in F-18's zone")


def test_kcj1b_the_jev_page_minus_its_column_is_the_plain_page_near_the_cap(tmp_path):
    d = tmp_path / "kc"
    sc, n = write_kc_fixture_in_the_f18_zone(d)
    assert 170 <= n <= 200
    assert len(sc.clusters) == 2 and all(c["family"] is not None for c in sc.clusters.values())   # --jev asks no model
    plain, withcol = tmp_path / "plain.md", tmp_path / "jev.md"
    a = run_cli("--project-dir", d, "--out", plain)
    b = run_cli("--project-dir", d, "--out", withcol, "--jev", "--jev-venue", "local")
    assert a.returncode == 0 and b.returncode == 0, (a.stderr, b.stderr)
    assert "jev: uncovered_shown=0 filled=0" in b.stdout
    P, J = plain.read_bytes(), withcol.read_bytes()
    assert J.count(b"| Jev suggests (advisory) |") == 2
    assert _strip_jev_column(J.decode("utf-8")).encode("utf-8") == P              # KC-J1b, byte for byte
    assert len(P) < hs.PAGE_MAX_BYTES and len(J) < hs.PAGE_MAX_BYTES
    # this page sits within the column's room of the cap: BOTH pages drop the same oldest agents and say so
    assert _agent_rows(P.decode()) == _agent_rows(J.decode()) < n
    assert P.count(b"older agents active in the window are not shown (the page cap)") == 1


SWEEP_CELLS = ["AF-AP-148 0.5303", "CLAUDE.md:1234#2 0.5146", "n/a (no lexical candidate)",
               "n/a (local: connection refused; pc: no bridge env file)",                      # the short, real shapes
               "n/a (local: HTTP N (system_one failed: <redacted> | KeyError) " * 4 + ")",   # and ones that grow when
               "<" * 300, chr(0x1D518) * 120, "|" * 200 + ">", "n/a (" + "x" * 400 + ")"]    # printed (entities, UTF-8)


def _swept_scan(fixture_dir, agents, clusters):
    sc = hs.Scan(hs.load_families())
    for p in sorted(fixture_dir.rglob("*.jsonl")):
        sc.feed(str(p))
    for i, (aid, desc) in enumerate(agents):
        sc.agents[aid] = {"models": {"claude-opus-5-5": 1}, "requests": {"r"}, "errors": 0, "refusals": 0,
                          "first": "2026-03-11T%02d:00:00.000000000Z" % (i % 24),
                          "last": "2026-03-12T%02d:%02d:00.000000000Z" % (i % 12, i % 60)}
        sc.agent_desc[aid] = desc
    sc.clusters.update(clusters)
    return sc


def test_kcj1b_holds_on_a_sweep_of_generated_over_cap_pages(fixture_dir):
    # Per trial: random agents (the verifier's random description lengths), random clusters, and one of three columns
    # (none filled, as in F-18's 76-byte case; short real cells; cells that grow when printed). Two inputs per trial:
    # the most agents whose page WITHOUT the column is under the cap (F-18's edge: the column alone can push it over),
    # and a page well over the cap.
    rnd = random.Random(20260924)
    seen = {"inputs": 0, "over_cap": 0, "f18_edge": 0, "trimmed": 0}
    for trial in range(30):
        pool = [("g%03d%012d" % (trial, i), hs.excerpt("lane %d " % i + ("wo | <x> " * 20)[:rnd.randrange(0, 150)]))
                for i in range(320)]
        clusters = {}
        for k in range(rnd.randrange(0, 50)):
            fam = None if rnd.random() < 0.5 else "exit code N"
            clusters[hs.excerpt("injected error %d " % k + "e" * rnd.randrange(0, 150))] = {
                "count": rnd.randrange(1, 9), "first": "2026-03-12T0%d:00:00.000000000Z" % (k % 10),
                "last": "2026-03-12T11:00:00.000000000Z", "tools": {"Bash"}, "family": fam, "rule": None if fam is None else "none"}
        kind = trial % 3
        col = {} if kind == 0 else {key: rnd.choice(SWEEP_CELLS[:4] if kind == 1 else SWEEP_CELLS)
                                    for key in clusters if rnd.random() < 0.7}
        lo, hi = 0, len(pool)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if len(hs.render(_swept_scan(fixture_dir, pool[:mid], clusters), KC_SRC).encode("utf-8")) < hs.PAGE_MAX_BYTES:
                lo = mid
            else:
                hi = mid - 1
        for k in (lo, min(len(pool), lo + rnd.randrange(5, 120))):
            sc = _swept_scan(fixture_dir, pool[:k], clusters)
            seen["inputs"] += 1
            seen["over_cap"] += len(hs.render(sc, KC_SRC, col).encode("utf-8")) >= hs.PAGE_MAX_BYTES
            seen["f18_edge"] += len(hs.render(sc, KC_SRC).encode("utf-8")) < hs.PAGE_MAX_BYTES <= len(
                hs.render(sc, KC_SRC, col).encode("utf-8"))
            plain, withcol = hs.build_page(sc, KC_SRC), hs.build_page(sc, KC_SRC, jev=col)
            assert plain is not None and withcol is not None, (trial, k)
            assert _strip_jev_column(withcol.decode("utf-8")).encode("utf-8") == plain, (trial, kind, k)
            assert len(plain) < hs.PAGE_MAX_BYTES and len(withcol) < hs.PAGE_MAX_BYTES, (trial, kind, k)
            seen["trimmed"] += b"not shown (the page cap)" in plain
    assert seen["inputs"] == 60 and seen["over_cap"] >= 40 and seen["f18_edge"] >= 10 and seen["trimmed"] >= 40, seen


def test_an_advisory_cell_is_scrubbed_whole_before_it_is_cut(fixture_dir):
    # the cell's cut falls inside a fake value: cut first, 7 value characters would be left, under the named rule's
    # floor of 8 (AF-AP-127); scrubbed first, none are
    sc = hs.Scan(hs.load_families())
    for p in sorted(fixture_dir.rglob("*.jsonl")):
        sc.feed(str(p))
    cell = "n/a (" + "w " * 39 + "password: QZJ8x4z9k2m7n5)"
    assert cell[:100].endswith("password: QZJ8x4z")
    page = hs.build_page(sc, KC_SRC, jev={k: cell for k in sc.clusters})
    assert page.count(b"| n/a (w w w") == 18 and b"QZJ" not in page        # 9 clusters, both tables


def test_a_page_that_cannot_keep_the_column_room_is_refused_with_and_without_jev(fixture_dir, tmp_path, monkeypatch):
    sc = hs.Scan(hs.load_families())
    for p in sorted(fixture_dir.rglob("*.jsonl")):
        sc.feed(str(p))
    bare = len(hs.render(sc, KC_SRC, max_agents=0).encode("utf-8"))
    monkeypatch.setattr(hs, "PAGE_MAX_BYTES", bare + 1)       # with no agent row the plain page fits, its column does not
    assert hs.build_page(sc, KC_SRC) is None and hs.build_page(sc, KC_SRC, jev={}) is None
    out = tmp_path / "H.md"
    assert hs.main(["--project-dir", str(fixture_dir), "--out", str(out)]) == 2 and not out.exists()


# ---------- D-076 (d): tool, model and agent-id fields pass the same scrub (VERIFY-JT1 F-17) ----------

F17 = ["ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", "AGENT_TOKEN=cVMjXl1uWH1c9Ogzoc_-k60yOL5KP5pr",
       "https://leading-twist-aruba-pulse.trycloudflare.com/exec", "sk-3c3d5f1e8a2b4c6d9e0f1234567890ab",
       "xoxp-QZJ8x4z9k2m7n5"]
F17_VALUES = ["ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", "cVMjXl1uWH1c9Ogzoc", "leading-twist-aruba-pulse",
              "3c3d5f1e8a2b4c6d9e0f1234567890ab", "QZJ8x4z9k2m7n5"]


def test_tool_model_and_agent_id_fields_pass_the_scrub(tmp_path):
    t = "2026-03-12T11:%02d:%02d.000Z"
    recs = []
    for i, name in enumerate(F17):                     # each as a TOOL name, with an error result
        recs += [assistant(t % (i, 0), "a%d" % i, "r%d" % i, "claude-opus-5-5", [tool_use("tu%d" % i, name)], 1),
                 result(t % (i, 1), "u%d" % i, [tr("tu%d" % i, "<tool_use_error>Error: No such tool available</tool_use_error>", True)])]
    text = [{"type": "text", "text": "x"}]
    recs += [assistant(t % (9, 0), "m1", "rm1", F17[1], text, 1, stop="end_turn"),                   # MODEL names
             assistant(t % (9, 1), "m2", "rm2", F17[4], text, 1, stop="end_turn"),
             assistant(t % (9, 2), "g1", "rg1", "claude-opus-5-5", text, 1, stop="end_turn", agent=F17[0]),   # AGENT ids
             assistant(t % (9, 3), "g2", "rg2", F17[3], text, 1, stop="end_turn", agent=F17[3])]
    src = tmp_path / "f17.jsonl"
    src.write_bytes(b"".join(_line(r) for r in recs))
    out = tmp_path / "H.md"
    r = run_cli("--transcript", src, "--out", out)
    assert r.returncode == 0, r.stderr
    page = out.read_text(encoding="utf-8")
    for v in F17_VALUES:
        assert v not in page, "a secret on the page: %s..." % v[:8]
    assert hs.scrub(page) == page
    cost = page.split("## Context cost")[1].split("## New this week")[0]
    for shown in ("gh&lt;redacted&gt;", "AGENT_TOKEN=&lt;redacted&gt;", "https://&lt;bridge-link-redacted&gt;",
                  "sk-&lt;redacted&gt;", "xox-&lt;redacted&gt;"):
        assert "| %s | 1 |" % shown in cost, shown                  # the five tool rows are on the page, scrubbed
    models = page.split("## Served model per day")[1].split("## Agents")[0]
    assert "AGENT_TOKEN=&lt;redacted&gt; 1" in models and "xox-&lt;redacted&gt; 1" in models
    agents = page.split("## Agents")[1].split("## Error clusters")[0]
    assert "| gh&lt;redacted&gt; | - | claude-opus-5-5 1 |" in agents and "| sk-&lt;redacted&gt; | - | sk-&lt;redacted&gt; 1 |" in agents
