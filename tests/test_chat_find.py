"""scripts/chat_find.py: the chat bug locator (D-090, L5), on fixture transcripts built at run time in the real record
shapes (the shapes and their keys were counted on the live transcripts on 2026-09-25: tool_use / tool_result blocks,
hook_success attachments, a refusal stop then a model switch, a thinking_drop attachment, system api_error records,
queued_command attachments, subagent and workflow-agent files, an unparsable line). Every secret below is a fake string
built at run time from a seeded generator. No test calls a model: the Jev tests use a dead loopback port (the real
fallback path) or an injected ranker. Every expected value is written out by hand from the fixture.
"""
import hashlib
import importlib.util
import json
import math
import pathlib
import random
import re
import shutil
import socket
import string
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts" / "chat_find.py"


def _load():
    spec = importlib.util.spec_from_file_location("chat_find_under_test", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


cf = _load()       # it puts scripts/ on sys.path, so jev_context below is the module chat_find imports
import jev_context  # noqa: E402

_R = random.Random(20260925)


def _fake(n):
    return "".join(_R.choice(string.ascii_letters + string.digits) for _ in range(n))


TOKEN, SK_VALUE, GH_VALUE, BEARER = _fake(32), _fake(24), _fake(36), _fake(30)
PASSWORD = _fake(6) + "7" + _fake(5)        # short with a digit: only the scrub hides it, the normalization does not
SECRETS = [TOKEN, SK_VALUE, GH_VALUE, BEARER, PASSWORD, re.sub(r"\d+", "N", PASSWORD)]

D = "2026-03-10T"
SESSION = "sess-main"


def env(ts, uuid, agent=None):
    rec = {"parentUuid": None, "isSidechain": agent is not None, "userType": "external",
           "cwd": "/home/user/agent-factory", "sessionId": SESSION, "version": "2.1.0", "gitBranch": "main",
           "uuid": uuid}
    if ts is not None:
        rec["timestamp"] = ts
    if agent:
        rec["agentId"] = agent
    return rec


def user_str(ts, uuid, text, agent=None):
    return dict(env(ts, uuid, agent), type="user", message={"role": "user", "content": text})


def assistant(ts, uuid, model, content, stop="tool_use", agent=None, **extra):
    rec = dict(env(ts, uuid, agent), type="assistant", requestId="req_" + uuid, **extra)
    rec["message"] = {"id": "msg_" + uuid, "type": "message", "role": "assistant", "model": model,
                      "content": content, "stop_reason": stop, "stop_sequence": None,
                      "usage": {"input_tokens": 1, "output_tokens": 1}}
    return rec


def tool_use(uid, name, **inp):
    return {"type": "tool_use", "id": uid, "name": name, "input": inp}


def result(ts, uuid, blocks, agent=None):
    return dict(env(ts, uuid, agent), type="user", message={"role": "user", "content": blocks},
                toolUseResult={"stdout": "", "stderr": "", "interrupted": False})


def tr(uid, content, is_error):
    b = {"tool_use_id": uid, "type": "tool_result", "content": content}
    if is_error is not None:
        b["is_error"] = is_error
    return b


def attachment(ts, uuid, att):
    return dict(env(ts, uuid), type="attachment", attachment=att)


def system(ts, uuid, subtype, **fields):
    return dict(env(ts, uuid), type="system", subtype=subtype, **fields)


HOOK = {"type": "hook_success", "hookName": "PostToolUse:Bash", "toolUseID": "toolu_m1", "hookEvent": "PostToolUse",
        "content": "hook saw password: " + PASSWORD, "stdout": "hook saw password: " + PASSWORD + " and sk-" + SK_VALUE,
        "stderr": "", "exitCode": 0, "command": "bash .claude/hooks/post.sh", "durationMs": 5}
ERROR_TEXT = ("Exit code 1\nTraceback (most recent call last):\nEngineDeadError: the engine core died at step 7 "
              "AGENT_TOKEN=" + TOKEN)
THINKING = "the engine died; check the budget. Authorization: Bearer " + BEARER

MAIN = [
    user_str(D + "09:00:00.000Z", "m1", "please find where the engine died"),                                   # 1
    assistant(D + "09:00:01.000Z", "m2", "claude-opus-5-5", [{"type": "text", "text": "running the probe now"}],
              stop=None),                                                                                        # 2
    assistant(D + "09:00:02.000Z", "m3", "claude-opus-5-5", [tool_use(
        "toolu_m1", "Bash", command="python3 probe.py --gh gh" + "p_" + GH_VALUE, description="run the probe")]),  # 3
    result(D + "09:00:03.000Z", "m4", [tr("toolu_m1", ERROR_TEXT, True)]),                                        # 4
    attachment(D + "09:00:04.000Z", "m5", HOOK),                                                                 # 5
    '{"type": "assistant", "message": ',                                                                         # 6
    assistant(D + "09:01:00.000Z", "m7", "claude-opus-5-5",
              [{"type": "thinking", "thinking": THINKING, "signature": "s"}], stop="refusal"),                    # 7
    assistant(D + "09:01:01.000Z", "m8", "<synthetic>", [{"type": "text", "text": "API Error: the request was refused"}],
              stop="refusal", isApiErrorMessage=True),                                                           # 8
    attachment(D + "09:01:02.000Z", "m9", {"type": "thinking_drop", "model": "claude-opus-4-8", "newlyDropped": 1}),  # 9
    assistant(D + "09:01:03.000Z", "m10", "claude-opus-4-8", [{"type": "text", "text": "continuing on the other model"}],
              stop="end_turn"),                                                                                  # 10
    system(D + "09:02:00.000Z", "m11", "api_error", level="error", error={"message": "overloaded upstream"},
           retryAttempt=1, maxRetries=10),                                                                       # 11
    {"type": "last-prompt", "lastPrompt": "zebracorn", "sessionId": SESSION},                                    # 12
    attachment(D + "09:03:00.000Z", "m13", {"type": "task_reminder", "itemCount": 1,
                                            "content": [{"subject": "zebracorn task", "status": "pending"}]}),   # 13
    attachment(D + "09:03:30.000Z", "m14", {"type": "queued_command", "prompt": "the owner asks: why did the engine die?",
                                            "commandMode": "prompt"}),                                           # 14
    assistant(D + "09:04:00.000Z", "m15", "claude-opus-4-8", [tool_use("toolu_m2", "Grep", pattern="EngineDeadError")]),  # 15
    result(D + "09:04:01.000Z", "m16", [tr("toolu_m2", "probe.log:3: EngineDeadError: the engine core died at step 12",
                                           None)]),                                                              # 16
]
SUB = [
    user_str(D + "08:59:00.000Z", "s1", "the brief: find the engine death", agent="afix1"),
    assistant(D + "08:59:10.000Z", "s2", "claude-opus-5-5", [tool_use("toolu_s1", "Bash", command="tail engine.log")],
              agent="afix1"),
    result(D + "08:59:11.000Z", "s3", [tr("toolu_s1", "EngineDeadError: the engine core died at step 3", False)],
           agent="afix1"),
]
WF = [assistant(D + "09:05:00.000Z", "w1", "claude-opus-5-5",
                [{"type": "text", "text": "the workflow agent saw no engine error"}], stop="end_turn", agent="awf1")]
JOURNAL = [user_str("2026-03-10T08:00:00.000Z", "j1", "EngineDeadError in the journal")]
ROOT_B = [user_str("2026-03-11T10:00:00.000Z", "b1", "EngineDeadError reported by the owner"),
          user_str(None, "b2", "EngineDeadError without a clock")]


def _write(path, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"".join((r if isinstance(r, str) else json.dumps(r)).encode("utf-8") + b"\n" for r in records))


def write_fixture(proj):
    _write(proj / "-home-x" / (SESSION + ".jsonl"), MAIN)
    _write(proj / "-home-x" / SESSION / "subagents" / "agent-afix1.jsonl", SUB)
    _write(proj / "-home-x" / SESSION / "subagents" / "workflows" / "wf_1" / "agent-awf1.jsonl", WF)
    _write(proj / "-home-x" / SESSION / "subagents" / "workflows" / "wf_1" / "journal.jsonl", JOURNAL)
    _write(proj / "-home-y" / "sess-b.jsonl", ROOT_B)
    return proj


@pytest.fixture
def proj(tmp_path):
    return write_fixture(tmp_path / "projects")


def run_cli(*args):
    return subprocess.run([sys.executable, str(TOOL), *map(str, args)], capture_output=True, text=True, timeout=120)


def ok(*args):
    r = run_cli(*args)
    assert r.returncode == 0, r.stderr
    return r


def as_json(*args):
    return json.loads(ok(*args, "--json").stdout)


def key(h):
    return (h["transcript"]["path"], h["line"], h["block"])


T_MAIN = {"root": "-home-x", "kind": "main", "session": "sess-main", "agent": None, "workflow": None,
          "path": "-home-x/sess-main.jsonl"}
T_SUB = {"root": "-home-x", "kind": "subagent", "session": "sess-main", "agent": "afix1", "workflow": None,
         "path": "-home-x/sess-main/subagents/agent-afix1.jsonl"}
T_WF = {"root": "-home-x", "kind": "workflow", "session": "sess-main", "agent": "awf1", "workflow": "wf_1",
        "path": "-home-x/sess-main/subagents/workflows/wf_1/agent-awf1.jsonl"}
T_B = {"root": "-home-y", "kind": "main", "session": "sess-b", "agent": None, "workflow": None,
       "path": "-home-y/sess-b.jsonl"}
DEFAULT_KINDS = ["assistant_text", "hook", "system", "thinking", "tool_error", "tool_input", "tool_result", "user_text"]


def hit(rank, time, tr_, line, kind, tool, call_id, call):
    return {"rank": rank, "score": None, "terms_matched": None, "time": time, "transcript": tr_, "line": line,
            "block": 0, "kind": kind, "tool": tool, "call_id": call_id, "call": call}


# ---------- every output field, pinned ----------

def test_error_string_json_every_field_pinned(proj):
    res = as_json("EngineDeadError", "--match", "error", "--projects-dir", proj)
    h1 = hit(1, "2026-03-10T08:59:11.000Z", T_SUB, 3, "tool_result", "Bash", "toolu_s1", "result")
    h2 = hit(2, "2026-03-10T09:00:03.000Z", T_MAIN, 4, "tool_error", "Bash", "toolu_m1", "result")
    h3 = hit(3, "2026-03-10T09:04:00.000Z", T_MAIN, 15, "tool_input", "Grep", "toolu_m2", "self")
    h4 = hit(4, "2026-03-10T09:04:01.000Z", T_MAIN, 16, "tool_result", "Grep", "toolu_m2", "result")
    h5 = hit(5, "2026-03-11T10:00:00.000Z", T_B, 1, "user_text", None, None, "none")
    h6 = hit(6, None, T_B, 2, "user_text", None, None, "none")
    assert res == {
        "tool": "chat_find", "match": "error", "order": "time", "order_requested": "lexical", "hits_asked": 10,
        "query": {"sha256_12": hashlib.sha256(b"EngineDeadError").hexdigest()[:12], "chars": 15, "terms": None},
        "window": {"since": None, "until": None}, "kinds": DEFAULT_KINDS,
        "corpus": {"transcripts": 4, "main": 2, "subagent": 1, "workflow": 1, "excluded": 0, "unreadable": 0,
                   "records": 21, "unparsable": 1, "documents": 18,
                   "documents_by_kind": {"assistant_text": 4, "hook": 1, "system": 1, "thinking": 1, "tool_error": 1,
                                         "tool_input": 3, "tool_result": 2, "user_text": 5},
                   "candidates": 6},
        "hits_total": 6, "first": h1, "per_transcript": [h1, h2, h5], "per_transcript_total": 3,
        "hits": [h1, h2, h3, h4, h5, h6]}


def test_error_string_text_output_pinned(proj):
    r = ok("EngineDeadError", "--match", "error", "--projects-dir", proj)
    sha = hashlib.sha256(b"EngineDeadError").hexdigest()[:12]
    s1 = "rank 1 | 2026-03-10T08:59:11.000Z | subagent -home-x afix1 | line 3 block 0 | tool_result | Bash toolu_s1 (result)"
    m4 = "rank 2 | 2026-03-10T09:00:03.000Z | main -home-x sess-main | line 4 block 0 | tool_error | Bash toolu_m1 (result)"
    b1 = "rank 5 | 2026-03-11T10:00:00.000Z | main -home-y sess-b | line 1 block 0 | user_text | - - (none)"
    assert r.stdout.splitlines() == [
        "chat_find: match=error order=time hits=10 window=-..- kinds=" + ",".join(DEFAULT_KINDS)
        + " query=sha256:%s chars=15 terms=-" % sha,
        "corpus: transcripts=4 (main 2, subagent 1, workflow 1) excluded=0 unreadable=0 records=21 unparsable=1 "
        "documents=18 candidates=6",
        "first: " + s1,
        "per transcript (the earliest hit in each, earliest first; 3 of 3 transcripts):",
        "  " + s1, "  " + m4, "  " + b1,
        "hits (6 shown of 6, in time order):",
        "  " + s1, "  " + m4,
        "  rank 3 | 2026-03-10T09:04:00.000Z | main -home-x sess-main | line 15 block 0 | tool_input | Grep toolu_m2 (self)",
        "  rank 4 | 2026-03-10T09:04:01.000Z | main -home-x sess-main | line 16 block 0 | tool_result | Grep toolu_m2 (result)",
        "  " + b1,
        "  rank 6 | - | main -home-y sess-b | line 2 block 0 | user_text | - - (none)"]
    assert re.fullmatch(r"chat_find: wall_s=\d+\.\d peak_rss_mb=\d+\.\d\n", r.stderr)


def test_every_record_kind_and_call_relation(proj):
    calls = {"names": {}, "last": (None, None, "none")}
    got = [cf.docs_of(r, calls) for r in MAIN if isinstance(r, dict)]
    bash, grep = ("Bash", "toolu_m1"), ("Grep", "toolu_m2")
    assert got == [
        [(0, "user_text", "", "please find where the engine died", None, None, "none")],
        [(0, "assistant_text", "", "running the probe now", None, None, "none")],
        [(0, "tool_input", "tool_use Bash", "python3 probe.py --gh gh" + "p_" + GH_VALUE + "\nrun the probe")
         + bash + ("self",)],
        [(0, "tool_error", "tool_result Bash is_error", ERROR_TEXT) + bash + ("result",)],
        [(0, "hook", "hook PostToolUse PostToolUse:Bash",
          "\n".join([HOOK["command"], HOOK["stdout"], "", HOOK["content"]])) + bash + ("named",)],
        [(0, "thinking", "stop_reason refusal", THINKING) + bash + ("preceding",)],
        [(0, "assistant_text", "stop_reason refusal", "API Error: the request was refused") + bash + ("preceding",)],
        [(0, "attachment", "attachment thinking_drop", "claude-opus-4-8\n1") + bash + ("preceding",)],
        [(0, "assistant_text", "", "continuing on the other model") + bash + ("preceding",)],
        [(0, "system", "system api_error", "overloaded upstream\n1\n10") + bash + ("preceding",)],
        [],
        [(0, "attachment", "attachment task_reminder", "1\nzebracorn task\npending") + bash + ("preceding",)],
        [(0, "user_text", "", "the owner asks: why did the engine die?") + bash + ("preceding",)],
        [(0, "tool_input", "tool_use Grep", "EngineDeadError") + grep + ("self",)],
        [(0, "tool_result", "tool_result Grep", "probe.log:3: EngineDeadError: the engine core died at step 12")
         + grep + ("result",)],
    ]


def test_discovery_takes_both_roots_and_workflow_agents_never_a_journal(proj):
    paths = [str(pathlib.Path(p).relative_to(proj)) for p in cf.discover(str(proj))]
    assert paths == [T_MAIN["path"], T_SUB["path"], T_WF["path"], T_B["path"]]
    journal = proj / "-home-x" / SESSION / "subagents" / "workflows" / "wf_1" / "journal.jsonl"
    assert b"EngineDeadError" in journal.read_bytes()          # the control: a searched journal WOULD be a hit
    res = as_json("EngineDeadError", "--match", "error", "--projects-dir", proj)
    assert "journal" not in json.dumps(res) and res["corpus"]["transcripts"] == 4


def test_line_numbers_are_physical_lines_after_an_unparsable_line(proj):
    assert MAIN[5] == '{"type": "assistant", "message": '       # line 6 does not parse
    res = as_json("budget", "--projects-dir", proj)
    assert [(key(h), h["kind"], h["tool"], h["call_id"], h["call"]) for h in res["hits"]] == [
        ((T_MAIN["path"], 7, 0), "thinking", "Bash", "toolu_m1", "preceding")]


# ---------- matching ----------

def test_bm25_scores_match_a_hand_derivation(tmp_path):
    p = tmp_path / "p"
    _write(p / "-r" / "s.jsonl", [user_str(D + "10:00:00.000Z", "a1", "alpha beta beta"),
                                  user_str(D + "10:00:01.000Z", "a2", "alpha gamma"),
                                  user_str(D + "10:00:02.000Z", "a3", "delta")])
    res = as_json("beta alpha", "--projects-dir", p)
    # BM25 from its definition: N = 3 documents of 3, 2 and 1 words (mean 2); beta is in 1 document, alpha in 2
    idf_beta, idf_alpha = math.log(1 + (3 - 1 + 0.5) / (1 + 0.5)), math.log(1 + (3 - 2 + 0.5) / (2 + 0.5))
    n1, n2 = 1.2 * (1 - 0.75 + 0.75 * 3 / 2), 1.2 * (1 - 0.75 + 0.75 * 2 / 2)
    s1 = idf_beta * 2 * 2.2 / (2 + n1) + idf_alpha * 1 * 2.2 / (1 + n1)
    s2 = idf_alpha * 1 * 2.2 / (1 + n2)
    assert [(h["line"], h["terms_matched"]) for h in res["hits"]] == [(1, 2), (2, 1)]
    assert abs(res["hits"][0]["score"] - s1) < 1e-4 and abs(res["hits"][1]["score"] - s2) < 1e-4
    assert (res["query"]["terms"], res["corpus"]["documents"], res["corpus"]["candidates"]) == (2, 3, 2)
    assert res["first"]["line"] == 1       # the earliest of the hits, not the best


def test_words_mode_first_appearance_and_per_transcript(proj):
    res = as_json("engine died", "--projects-dir", proj)
    got = sorted((key(h), h["terms_matched"]) for h in res["hits"])
    assert got == sorted([((T_MAIN["path"], 1, 0), 2), ((T_MAIN["path"], 4, 0), 2), ((T_MAIN["path"], 7, 0), 2),
                          ((T_MAIN["path"], 14, 0), 1), ((T_MAIN["path"], 16, 0), 2), ((T_SUB["path"], 1, 0), 1),
                          ((T_SUB["path"], 2, 0), 1), ((T_SUB["path"], 3, 0), 2), ((T_WF["path"], 1, 0), 1)])
    assert res["hits_total"] == 9 and res["corpus"]["candidates"] == 9
    assert key(res["first"]) == (T_SUB["path"], 1, 0) and res["first"]["time"] == "2026-03-10T08:59:00.000Z"
    assert [key(h) for h in res["per_transcript"]] == [(T_SUB["path"], 1, 0), (T_MAIN["path"], 1, 0),
                                                       (T_WF["path"], 1, 0)]
    top3 = as_json("engine died", "--projects-dir", proj, "--hits", "3")
    assert [h["rank"] for h in top3["hits"]] == [1, 2, 3] and top3["hits_total"] == 9
    assert all(h["terms_matched"] == 2 for h in top3["hits"])   # the documents holding both words lead
    shown = {key(h) for h in top3["hits"]}
    assert key(top3["first"]) in shown and {key(h) for h in top3["per_transcript"]} <= shown
    assert (T_SUB["path"], 1, 0) not in shown                  # the control: the earliest candidate is not a top-3 hit


def test_a_refusal_stop_is_searchable_by_its_field(proj):
    res = as_json("stop_reason refusal", "--projects-dir", proj)
    assert sorted((h["line"], h["kind"], h["terms_matched"]) for h in res["hits"]) == [
        (7, "thinking", 2), (8, "assistant_text", 2)]


def test_error_string_normalizes_numbers_and_a_changed_word_is_no_match(proj):
    res = as_json("EngineDeadError: the engine core died at step 99", "--match", "error", "--projects-dir", proj)
    assert [key(h) for h in res["hits"]] == [(T_SUB["path"], 3, 0), (T_MAIN["path"], 4, 0), (T_MAIN["path"], 16, 0)]
    spaced = as_json("EngineDeadError:   the engine \t core died", "--match", "error", "--projects-dir", proj)
    assert [key(h) for h in spaced["hits"]] == [key(h) for h in res["hits"]]
    none = as_json("EngineDeadError: the engine core died at stage 99", "--match", "error", "--projects-dir", proj)
    assert none["hits"] == [] and none["first"] is None and none["hits_total"] == 0


@pytest.mark.parametrize("query,doc", [
    ("abc123def ERR", "x abc456def ERR y"), ("EngineDeadError", "E: EngineDeadError at 3"),
    ("exit_code=1 failed", "exit_code=2 failed"), ("see https://a.example/x now", "see http://b.example/y now"),
    ("bad" + chr(0xD800), "so bad" + chr(0xDFFF) + " end"), ("step 7 of 9", "step 12 of 31"),
    ("EngineDeadError", "exit rc=1,EngineDeadError at 3")])
def test_the_error_anchor_is_in_every_matching_raw_document(query, doc):
    nq = cf.normalize(query)
    assert nq in cf.normalize(doc)                              # the pair matches
    a = cf.anchor_of(nq)
    assert a in doc and not set(a) & set("NTU ?")               # so the pre-filter keeps it


def test_an_error_inside_a_long_quoted_string_still_matches(tmp_path):
    # the live finding (AF-AP-181's first appearance): a CI log returned inside ONE JSON string, its newlines escaped, so
    # hiccup_scan's quoted-string rule would turn the whole log, the error with it, into one S
    log = json.dumps({"logs": "2026-09-24T10:49:52.1234567Z E   AssertionError: assert 'gone' == 'Z'\n"
                              "2026-09-24T10:49:52.1234568Z FAILED tests/test_x.py::test_zombie"})
    assert "S" in cf.normalize(hiccup_scan_quoted(log)) and "'gone' == 'Z'" not in hiccup_scan_quoted(log)  # the control
    p = tmp_path / "p"
    _write(p / "-r" / "s.jsonl", [assistant(D + "10:00:00.000Z", "q1", "claude-opus-5-5", [tool_use("toolu_q1", "mcp__gh__logs", job=1)]),
                                  result(D + "10:00:01.000Z", "q2", [tr("toolu_q1", [{"type": "text", "text": log}], None)])])
    res = as_json("'gone' == 'Z'", "--match", "error", "--projects-dir", p)
    assert [(h["line"], h["kind"], h["tool"]) for h in res["hits"]] == [(2, "tool_result", "mcp__gh__logs")]


def hiccup_scan_quoted(text):
    """hiccup_scan's quoted-string rule alone, as its excerpt() applies it."""
    import hiccup_scan
    return hiccup_scan._QUOTED.sub("S", text)


def test_attachments_are_searched_only_when_asked(proj):
    res = as_json("zebracorn", "--projects-dir", proj)
    assert res["hits"] == [] and res["first"] is None and res["corpus"]["candidates"] == 0
    att = as_json("zebracorn", "--projects-dir", proj, "--kind", "attachment")
    assert [(key(h), h["kind"]) for h in att["hits"]] == [((T_MAIN["path"], 13, 0), "attachment")]
    assert att["corpus"]["documents_by_kind"] == {"attachment": 2}     # thinking_drop and task_reminder; never line 12


def test_the_time_window_is_a_prefix_bound_and_drops_records_with_no_clock(proj):
    def lines(*extra):
        return [key(h) for h in as_json("EngineDeadError", "--match", "error", "--projects-dir", proj, *extra)["hits"]]
    assert lines("--until", "2026-03-10T08:59") == [(T_SUB["path"], 3, 0)]
    assert lines("--since", "2026-03-10T09:04") == [(T_MAIN["path"], 15, 0), (T_MAIN["path"], 16, 0), (T_B["path"], 1, 0)]
    assert lines("--since", "2026-03-10T09:04:00.5") == [(T_MAIN["path"], 16, 0), (T_B["path"], 1, 0)]
    assert lines("--since", "2026-03-11", "--until", "2026-03-11Z") == [(T_B["path"], 1, 0)]
    assert (T_B["path"], 2, 0) in lines()                       # the record with no clock is a hit with no window


def test_exclude_takes_a_file_name_or_an_agent_id(proj):
    for name in ("afix1", "agent-afix1.jsonl"):
        res = as_json("EngineDeadError", "--match", "error", "--projects-dir", proj, "--exclude", name)
        assert res["corpus"]["excluded"] == 1 and T_SUB["path"] not in json.dumps(res)
        assert key(res["first"]) == (T_MAIN["path"], 4, 0)


# ---------- no transcript text by default ----------

def _all_outputs(proj, *extra):
    outs = []
    for q, mode in (("EngineDeadError", "error"), ("hook saw password", "words"), ("engine died budget", "words"),
                    ("EngineDeadError AGENT_TOKEN=" + TOKEN + " password: " + PASSWORD, "error")):
        for fmt in ((), ("--json",)):
            r = run_cli(q, "--match", mode, "--projects-dir", proj, *fmt, *extra)
            assert r.returncode == 0, r.stderr
            outs.append(r.stdout + r.stderr)
    return outs


def test_the_default_output_holds_no_transcript_text_and_no_secret(proj):
    raw = b"".join(p.read_bytes() for p in proj.rglob("*.jsonl"))
    assert all(s.encode() in raw for s in SECRETS[:5])          # the control: every fake secret IS in the fixture
    hook = as_json("hook saw password", "--projects-dir", proj)
    assert (T_MAIN["path"], 5, 0) in [key(h) for h in hook["hits"]]   # ... in a document that is a hit
    for out in _all_outputs(proj):
        for s in SECRETS + ["the engine core died", "hook saw", "overloaded upstream"]:
            assert s not in out


def test_the_excerpt_is_scrubbed_first_and_capped_at_160(proj):
    # the control: the normalization alone leaves the password (as hunterNhunter did in hiccup_scan's F-16)
    assert re.sub(r"\d+", "N", PASSWORD) in cf.normalize(HOOK["stdout"])
    for out in _all_outputs(proj, "--excerpt"):
        for s in SECRETS:
            assert s not in out
    res = as_json("hook saw password", "--projects-dir", proj, "--excerpt")
    ex = {key(h): h["excerpt"] for h in res["hits"]}
    assert all(len(e) <= 160 for e in ex.values())
    assert "hook saw password: " in ex[(T_MAIN["path"], 5, 0)]     # the excerpt is that hit's own text
    err = as_json("EngineDeadError", "--match", "error", "--projects-dir", proj, "--excerpt")
    assert err["hits"][1]["excerpt"].startswith("Exit code N Traceback (most recent call last): EngineDeadError: the "
                                                "engine core died at step N")
    text = ok("EngineDeadError", "--match", "error", "--projects-dir", proj, "--excerpt").stdout
    assert text.count("\n    excerpt: ") == 6


def test_a_tool_name_from_the_transcript_is_scrubbed(tmp_path):
    p = tmp_path / "p"
    name = "mcp__" + GH_VALUE + "zzzzz"                        # a 46-character opaque run: the scrub's opaque rule
    _write(p / "-r" / "s.jsonl", [assistant(D + "10:00:00.000Z", "t1", "claude-opus-5-5", [tool_use("toolu_t1", name, q="x")]),
                                  result(D + "10:00:01.000Z", "t2", [tr("toolu_t1", "quokka failure", True)])])
    for fmt in ((), ("--json",)):
        out = ok("quokka", "--projects-dir", p, *fmt).stdout
        assert "toolu_t1" in out and "<opaque-redacted>" in out and GH_VALUE not in out


def test_the_query_is_shown_as_a_hash_never_as_text(proj):
    q = "EngineDeadError AGENT_TOKEN=" + TOKEN
    out = ok(q, "--match", "error", "--projects-dir", proj).stdout
    assert TOKEN not in out and "query=sha256:%s " % hashlib.sha256(q.encode()).hexdigest()[:12] in out


# ---------- the Jev order ----------

def _dead_url():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return "http://127.0.0.1:%d" % port


def test_jev_down_falls_back_loudly_to_the_lexical_order(proj):
    lex = ok("engine died", "--projects-dir", proj)
    assert "fell back" not in lex.stdout + lex.stderr           # the control: a lexical run says nothing of the kind
    r = ok("engine died", "--projects-dir", proj, "--order", "jev", "--jev-url", _dead_url(), "--no-jev-log")
    loud = [ln for ln in r.stderr.splitlines() if ln.startswith("chat_find: --order jev fell back to the lexical order: ")]
    assert len(loud) == 1 and len(loud[0]) > len("chat_find: --order jev fell back to the lexical order: ")
    head, *rest = r.stdout.splitlines()
    lhead, *lrest = lex.stdout.splitlines()
    assert "order=lexical (jev fell back)" in head and head.replace(" (jev fell back)", "") == lhead
    assert rest == lrest
    res = as_json("engine died", "--projects-dir", proj, "--order", "jev", "--jev-url", _dead_url(), "--no-jev-log")
    assert res["order"] == "lexical" and res["order_requested"] == "jev" and res["jev_fallback"]


def test_jev_reorders_the_hits_and_never_replaces_them(proj, monkeypatch):
    seen = {}

    def fake_rank(query, chunks, instructions=None, url=None, timeout=None, log=True, protect=()):
        seen.update(query=query, chunks=chunks, url=url, log=log, protect=protect)
        return {c["id"]: (i + 1) / len(chunks) for i, c in enumerate(chunks)}, None, chunks   # the lexical last wins

    monkeypatch.setattr(jev_context, "jev_rank", fake_rank)
    lex = cf.search(cf.parse(["engine died", "--projects-dir", str(proj)]))
    jev = cf.search(cf.parse(["engine died", "--projects-dir", str(proj), "--order", "jev", "--no-jev-log"]))
    assert jev["order"] == "jev" and "jev_fallback" not in jev
    assert [key(h) for h in jev["hits"]] == [key(h) for h in reversed(lex["hits"])]
    assert [h["rank"] for h in jev["hits"]] == list(range(1, 10))
    assert key(jev["first"]) == key(lex["first"])              # the same hit set, so the same first appearance
    assert seen["log"] is False and seen["url"] is None and seen["protect"] == seen["chunks"]
    assert len(seen["chunks"]) == 9 and seen["query"] == "engine died"
    for c in seen["chunks"]:
        assert set(c) == {"id", "path", "line", "instruments", "text", "lexical", "agreement"}
        assert re.match(r"(thinking|tool_error|tool_result|tool_input|user_text|assistant_text|hook|system) ", c["text"])
        assert len(c["text"]) <= len("tool_result Bash\n") + cf.JEV_WINDOW
        for s in SECRETS:
            assert s not in c["text"]                          # nothing unscrubbed leaves for the model server
    thinking = next(c for c in seen["chunks"] if c["text"].startswith("thinking"))
    assert "Authorization: Bearer <redacted>" in thinking["text"]    # the control: the window held the token
    cf.search(cf.parse(["engine died", "--projects-dir", str(proj), "--order", "jev", "--no-jev-log", "--hits", "3"]))
    assert len(seen["chunks"]) == 3                            # Jev ranks the shown hits, no more


def test_jev_limits_and_the_shared_constant():
    assert cf.JEV_MAX == jev_context.MAX_JEV_CHUNKS


# ---------- usage, exits, determinism ----------

@pytest.mark.parametrize("args,why", [
    (["   "], "the query is empty"), (["x y z", "--hits", "0"], "--hits must be at least 1"),
    (["abc", "--match", "error", "--order", "jev"], "--order jev reorders word hits"),
    (["engine", "--order", "jev", "--hits", "49"], "at most 48 hits"),
    (["engine", "--kind", "nope"], "invalid choice"), (["engine", "--since", "2026-13-01"], "--since"),
    (["engine", "--until", "yesterday"], "--until must be"), (["engine", "--since", "2026-03-10T24"], "--since"),
    (["the and of"], "no word of 3+ letters"), (["\x01", "--match", "error"], "empty after normalization")])
def test_usage_errors_exit_64(proj, args, why):
    r = run_cli(*args, "--projects-dir", proj)
    assert r.returncode == 64 and why in r.stderr and r.stdout == ""


def test_no_projects_dir_or_no_transcript_exits_2(tmp_path):
    r = run_cli("engine", "--projects-dir", tmp_path / "absent")
    assert r.returncode == 2 and "no projects dir" in r.stderr and r.stdout == ""
    (tmp_path / "empty" / "-home-x").mkdir(parents=True)
    r = run_cli("engine", "--projects-dir", tmp_path / "empty")
    assert r.returncode == 2 and "no transcript" in r.stderr and r.stdout == ""


def test_the_peak_is_this_process_not_the_parent_that_launched_it(proj):
    # a parent holding 200 MB launches the tool; the kernel's ru_maxrss carries that high-water mark into the child
    code = ("import resource, subprocess, sys\n"
            "big = bytearray(200 * 1024 * 1024)\n"
            "for i in range(0, len(big), 4096): big[i] = 1\n"
            "c = subprocess.run([sys.executable, '-c', 'import resource; print(resource.getrusage(resource.RUSAGE_SELF)"
            ".ru_maxrss)'], capture_output=True, text=True)\n"
            "t = subprocess.run([sys.executable, sys.argv[1], 'engine died', '--projects-dir', sys.argv[2]],"
            " capture_output=True, text=True)\n"
            "print(c.stdout.strip()); print(t.stderr.strip())\n")
    r = subprocess.run([sys.executable, "-c", code, str(TOOL), str(proj)], capture_output=True, text=True, timeout=120)
    child_kb, stats = r.stdout.splitlines()
    assert int(child_kb) > 200 * 1024                           # the control: the inheritance is real here
    assert float(re.search(r"peak_rss_mb=(\d+\.\d)", stats).group(1)) < 150


def test_two_runs_give_identical_output_and_write_nothing(proj, tmp_path):
    before = {p: p.read_bytes() for p in proj.rglob("*") if p.is_file()}
    for args in (("engine died",), ("engine died", "--json"), ("EngineDeadError", "--match", "error", "--excerpt")):
        a, b = ok(*args, "--projects-dir", proj), ok(*args, "--projects-dir", proj)
        assert a.stdout == b.stdout
    assert {p: p.read_bytes() for p in proj.rglob("*") if p.is_file()} == before
    other = tmp_path / "other"
    shutil.copytree(proj, other)                                # the control: other bytes give other output
    with open(other / "-home-y" / "sess-b.jsonl", "a") as fh:
        fh.write(json.dumps(user_str("2026-03-12T10:00:00.000Z", "b3", "the engine died again")) + "\n")
    assert ok("engine died", "--projects-dir", other).stdout != ok("engine died", "--projects-dir", proj).stdout
