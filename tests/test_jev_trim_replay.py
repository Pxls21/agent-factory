"""T0-REPLAY tests (task #346, D-105; tasks/briefs/jev-trim/T0-REPLAY-brief.md item 6, T0-REPLAY-R2-brief.md items
2-7). Deterministic and LLM-free.

Every transcript here is synthetic, built at run time in the production record shapes (the key sets of
tests/fixtures/jev_pipes/record_shapes.json, captured from the real transcript). Each scenario check is a plain function
of a module: it runs on scripts/jev_trim/replay.py (and must pass) and on each named mutant of that file
(test_mutant_is_killed: it must fail with an AssertionError). Expected values come from the fixtures' own numbers,
computed by hand in the checks, never from the code under test.
"""
from __future__ import annotations

import bisect
import collections
import datetime
import hashlib
import importlib.util
import json
import secrets
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
REPLAY = REPO / "scripts" / "jev_trim" / "replay.py"
sys.path.insert(0, str(REPO / "scripts"))

from jev_pipes import accounting  # noqa: E402
from jev_trim import replay  # noqa: E402

TOKENS_1000 = "word " * 580  # 2,900 characters: 1,000 tokens at the brief's 2.90 characters per token (spaced: a
# long run of path characters with no slash costs accounting.tokens quadratic time, so fixtures avoid one)


def think() -> dict:
    return {"type": "thinking", "thinking": "", "signature": "c2lnbmF0dXJl"}


def text(body: str) -> dict:
    return {"type": "text", "text": body}


def call(tool_use_id: str, name: str, **tool_input) -> dict:
    return {"type": "tool_use", "id": tool_use_id, "name": name, "input": tool_input, "caller": {"type": "direct"}}


class Tx:
    """A synthetic Claude Code transcript, one method per record kind."""

    def __init__(self, sidechain: bool = False, day: str = "2026-09-26"):
        self.lines: list[str] = []
        self.side = sidechain
        self.clock = datetime.datetime.fromisoformat(day + "T10:00:00")
        self.n = self.req = self.prompt = self.tool = 0

    def at(self, day: str) -> None:
        self.clock = datetime.datetime.fromisoformat(day + "T10:00:00")

    def _base(self, kind: str) -> dict:
        self.n += 1
        self.clock += datetime.timedelta(seconds=7)
        return {"type": kind, "uuid": f"u{self.n:05d}", "parentUuid": f"u{self.n - 1:05d}", "isSidechain": self.side,
                "timestamp": self.clock.strftime("%Y-%m-%dT%H:%M:%S.000Z"), "sessionId": "fixture-session",
                "cwd": "/work", "version": "2.1.283", "userType": "external", "entrypoint": "cli", "gitBranch": "b",
                "slug": "fixture"}

    def add(self, record: dict) -> None:
        self.lines.append(json.dumps(record))

    def tool_id(self) -> str:
        self.tool += 1
        return f"toolu_fx{self.tool:04d}"

    def request(self, context: int, blocks: list, *, output: int = 60, thinking: int | None = None, write: int = 0,
                model: str = "claude-opus-5-5", usage: bool = True, sidechain: bool | None = None) -> str:
        """One API request, one assistant record per block as the harness writes them: the first records carry a
        partial usage (output 1), the last the final one (with the thinking count when given)."""
        self.req += 1
        rid, mid = f"req_fx{self.req:04d}", f"msg_fx{self.req:04d}"
        for i, block in enumerate(blocks):
            last = i == len(blocks) - 1
            record = self._base("assistant")
            if sidechain is not None:
                record["isSidechain"] = sidechain
            message = {"id": mid, "model": model, "role": "assistant", "type": "message", "content": [block],
                       "stop_reason": "tool_use" if block.get("type") == "tool_use" else "end_turn"}
            if usage:
                u = {"input_tokens": 3, "cache_creation_input_tokens": write,
                     "cache_read_input_tokens": context - 3 - write, "output_tokens": output if last else 1,
                     "cache_creation": {"ephemeral_1h_input_tokens": write, "ephemeral_5m_input_tokens": 0}}
                if last and thinking is not None:
                    u["output_tokens_details"] = {"thinking_tokens": thinking}
                message["usage"] = u
            record.update({"requestId": rid, "message": message})
            self.add(record)
        return rid

    def results(self, *pairs) -> None:
        record = self._base("user")
        record.update({"promptId": f"p{self.prompt}", "sourceToolAssistantUUID": "u00000",
                       "message": {"role": "user", "content": [
                           {"type": "tool_result", "tool_use_id": tid, "content": body, "is_error": False}
                           for tid, body in pairs]},
                       "toolUseResult": {"stdout": "", "stderr": "", "interrupted": False, "isImage": False,
                                         "noOutputExpected": False}})
        self.add(record)

    def user(self, body: str, *, origin: str | None = "human", meta: bool = False, source: str | None = None,
             new_prompt: bool = True, handback: bool = False) -> None:
        if new_prompt:
            self.prompt += 1
        record = self._base("user")
        record.update({"promptId": f"p{self.prompt}", "message": {"role": "user", "content": body}})
        if origin:
            record["origin"] = {"kind": origin}
            if handback:  # a peer message the harness flags as a subagent's hand-back
                record["origin"]["handback"] = True
        if meta:
            record["isMeta"] = True
        if source:
            record["sourceToolUseID"] = source
        self.add(record)

    def attach(self, attachment: dict) -> None:
        record = self._base("attachment")
        record["attachment"] = attachment
        self.add(record)

    def reminder(self, number: int, subject: str = "fixture task") -> None:
        self.attach({"type": "task_reminder", "itemCount": 1,
                     "content": [{"id": number, "status": "pending", "subject": f"{subject} {number}"}]})

    def hook(self, name: str, body: str) -> None:
        self.attach({"type": "hook_additional_context", "content": [body], "hookName": name,
                     "hookEvent": name.split(":")[0], "toolUseID": "toolu_hook"})

    def stop(self) -> None:
        record = self._base("system")
        record.update({"subtype": "stop_hook_summary", "hookCount": 1, "hookInfos": [], "hookErrors": [],
                       "preventedContinuation": False, "stopReason": "", "hasOutput": False, "level": "suggestion",
                       "toolUseID": "toolu_stop"})
        self.add(record)

    def boundary(self, summary: str = "a summary of the earlier work", post_tokens: int = 1) -> None:
        record = self._base("system")
        record.update({"subtype": "compact_boundary", "content": "Conversation compacted", "level": "info",
                       "compactMetadata": {"trigger": "auto", "preTokens": 1, "postTokens": post_tokens},
                       "logicalParentUuid": "u00000", "parentUuid": None})
        self.add(record)
        self.prompt += 1
        record = self._base("user")
        record.update({"promptId": f"p{self.prompt}", "isCompactSummary": True, "isVisibleInTranscriptOnly": True,
                       "message": {"role": "user", "content": summary}})
        self.add(record)

    def garbage(self) -> None:
        self.lines.append('{"type": "user", "message": ')

    def write(self, path: Path) -> tuple[str, int]:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(self.lines) + "\n")
        return str(path), path.stat().st_size


def step(tx: Tx, context: int, body: str = "ok", *, command: str | None = None, blocks: tuple = (),
         thinking: int | None = 0, output: int = 10) -> str:
    """A request with one Bash call (and optional extra blocks first) and the call's result."""
    tid = tx.tool_id()
    tx.request(context, list(blocks) + [call(tid, "Bash", command=command or f"echo {tid}")], output=output,
               thinking=thinking)
    tx.results((tid, body))
    return tid


def _hidden(v: str, out: str) -> bool:
    """No 8-character piece of v, as written or as JSON writes it, is in out (the repo's pattern,
    tasks/briefs/system1/vscrub2r2/vscrub2r1r2_red.py)."""
    forms = {v, json.dumps(v)[1:-1]}
    return not any(f[i:i + 8] in out for f in forms for i in range(len(f) - 7))


def _built(m, tx: Tx, where: Path, **kwargs):
    path, size = tx.write(where / "fixture.jsonl")
    tl = m.build(path, size, **kwargs)
    return tl, m.indexes(tl)


# ---------------------------------------------------------------- the scenario checks (module in, assertions)

def check_timeline(m, where: Path) -> None:
    tx = Tx()
    tx.user("please start the fixture work")
    a = tx.tool_id()
    tx.request(20000, [think(), text("working on it"), call(a, "Bash", command="ls /work")], output=500, thinking=400)
    tx.results((a, "x" * 290))
    tx.reminder(1)
    b = tx.tool_id()
    tx.request(21000, [call(b, "Read", file_path="/work/a.py")], output=30)  # no thinking count: modeled sizes
    tx.results((b, "y" * 580))
    tx.stop()
    tx.user("second prompt")
    tx.request(0, [text("No response requested.")], output=0, model="<synthetic>")
    tx.request(9999, [text("a subagent's record")], output=5, sidechain=True)
    c = tx.tool_id()
    tx.request(22000, [call(c, "Bash", command="pwd")], output=20)
    tx.results((c, "z" * 29))
    tl, _ = _built(m, tx, where)
    assert [q.context for q in tl.requests] == [20000, 21000, 22000]
    assert [q.output for q in tl.requests] == [500, 30, 20]
    assert tl.stats["synthetic_records_excluded"] == 1 and tl.stats["records_on_the_other_thread"] == 1
    assert tl.stats["items_after_their_segments_last_request"] == 2  # the last call and its result enter no request
    seg = tl.segments[0]
    got = [(it.kind, it.name, it.req, it.turn_stop, it.turn_prompt, round(it.size, 3), it.tool_use_id) for it in seg.items]
    visible = len("working on it") + len(json.dumps({"command": "ls /work"}))
    assert got == [
        ("typed_user_text", "human", 0, 0, 0, round(len("please start the fixture work") / 2.9, 3), ""),
        ("thinking", "thinking", 1, 0, 0, 400.0, ""),
        ("assistant_text", "assistant_text", 1, 0, 0, round(100 * len("working on it") / visible, 3), ""),
        ("tool_input", "Bash", 1, 0, 0, round(100 * len(json.dumps({"command": "ls /work"})) / visible, 3), a),
        ("tool_result", "Bash", 1, 0, 0, 100.0, a),
        ("task_reminder", "task_reminder", 1, 0, 0, round((420 + len("#1. [pending] fixture task 1\n")) / 2.9, 3), ""),
        ("tool_input", "Read", 2, 0, 0, round(len(json.dumps({"file_path": "/work/a.py"})) / 3.0, 3), b),
        ("tool_result", "Read", 2, 0, 0, 200.0, b),
        ("typed_user_text", "human", 2, 1, 1, round(len("second prompt") / 2.9, 3), ""),
    ]
    assert seg.items[0].first_user and seg.items[0].typed and not seg.items[8].first_user
    assert seg.items[7].key == ("Read", "/work/a.py")
    assert tl.stats["thinking_sized_exact"] == 1 and tl.stats["visible_output_sized_model"] == 2


def check_r3_age_boundary(m, where: Path) -> None:
    tx = Tx()
    tx.user("go")
    for j in range(8):
        step(tx, 10000 + 1000 * j, TOKENS_1000)
    tl, idx = _built(m, tx, where)
    sim = m.simulate(tl, m.Cell(1, 0, 3, ("R3",), "per-request", "request", 0), idx, keep_map=True)
    seg = tl.segments[0]
    marks = {pos: mark for (_, pos), mark in sim["archive"].items()}
    assert sorted(seg.items[p].req for p in marks) == [1, 2, 3]  # results entering at requests 1..3 reach age 4
    for pos, mark in marks.items():
        assert seg.items[pos].kind == "tool_result" and mark[0] == "R3"
        assert mark[2] - seg.items[pos].req == 4  # archived when its age first exceeds A = 3, never at age 3


def check_r1_supersede(m, where: Path) -> None:
    tx = Tx()
    tx.user("go")
    reads = {}

    def read(path):
        tid = tx.tool_id()
        tx.request(10000 + 100 * tx.req, [call(tid, "Read", file_path=path)], output=10, thinking=0)
        tx.results((tid, TOKENS_1000))
        reads.setdefault(path, []).append(tid)

    read("/work/a.py")
    tx.reminder(1)
    tx.hook("PreToolUse:Bash", "h" * 300)
    read("/work/b.py")
    tx.hook("SessionStart", "s" * 300)
    step(tx, 10500)
    tx.reminder(2)
    tx.hook("PreToolUse:Bash", "k" * 300)
    read("/work/a.py")
    tx.reminder(3)
    for j in range(3):
        step(tx, 11000 + j)
    tl, idx = _built(m, tx, where)
    sim = m.simulate(tl, m.Cell(1, 0, 0, ("R1",), "per-request", "request", 0), idx, keep_map=True)
    seg = tl.segments[0]
    archived = {(seg.items[p].kind, seg.items[p].name, seg.items[p].tool_use_id or seg.items[p].text[:1])
                for (_, p) in sim["archive"]}
    assert archived == {("tool_result", "Read", reads["/work/a.py"][0]),  # the first read of a.py, re-read later
                        ("task_reminder", "task_reminder", "#"), ("hook_context", "PreToolUse:Bash", "h")}
    reminders = [it for it in seg.items if it.kind == "task_reminder"]
    assert [(seg.index, it.pos) in sim["archive"] for it in reminders] == [True, True, False]  # the newest is kept


def check_r2_thinking(m, where: Path) -> None:
    tx = Tx()
    tx.user("go")
    for turn in range(3):
        for j in range(3):
            step(tx, 10000 + 1000 * tx.req, blocks=(think(),), thinking=500, output=520)
        tx.stop()
        tx.user(f"turn {turn + 1}")
    step(tx, 30000)
    tl, idx = _built(m, tx, where)
    sim = m.simulate(tl, m.Cell(1, 0, 0, ("R2",), "per-request", "stop", 0), idx, keep_map=True)
    seg = tl.segments[0]
    marks = {pos: mark for (_, pos), mark in sim["archive"].items()}
    assert marks and all(seg.items[p].kind == "thinking" and m_[0] == "R2" for p, m_ in marks.items())
    for pos, mark in marks.items():
        assert seg.items[pos].turn_stop < tl.requests[mark[2]].turn_stop  # only thinking before the current turn
    last_turn = max(it.turn_stop for it in seg.items)
    assert not any(seg.items[p].turn_stop == last_turn for p in marks)
    assert sum(1 for it in seg.items if it.kind == "thinking" and it.turn_stop < last_turn) == len(marks)


def check_hysteresis(m, where: Path) -> dict:
    tx = Tx()
    tx.user("go")
    for c in (1000, 2000, 3000, 4000, 5000, 5100, 5200, 5300):
        step(tx, c, TOKENS_1000)
    tl, idx = _built(m, tx, where)
    sim = m.simulate(tl, m.Cell(5000, 3000, 0, ("R3",), "per-request", "request", 0), idx, keep_map=True)
    assert [t["request"] for t in sim["trims"]] == [5]  # not at 5,000 (not past B); at 5,100; then only appends
    assert sim["trims"][0]["items"] == 3  # 5,100 - 3 x 960 = 2,220: at or under L = 3,000 after three
    assert [round(a, 1) for _, a in sim["active"]] == [1000, 2000, 3000, 4000, 5000, 2220, 2320, 2420]
    return {"tl": tl, "sim": sim}


def check_between_turn(m, where: Path) -> None:
    tx = Tx()
    tx.user("go")
    for turn in range(4):
        for j in range(3):
            step(tx, 100000 + 1000 * tx.req, TOKENS_1000)
        tx.stop()
        tx.user(f"turn {turn}")
    step(tx, 200000)
    tl, idx = _built(m, tx, where)
    starts = {q.index for i, q in enumerate(tl.requests) if i == 0 or q.turn_stop != tl.requests[i - 1].turn_stop}
    between = m.simulate(tl, m.Cell(1, 0, 2, ("R3",), "between-turn", "stop", 0), idx)
    per = m.simulate(tl, m.Cell(1, 0, 2, ("R3",), "per-request", "stop", 0), idx)
    assert between["trims"] and all(t["request"] in starts for t in between["trims"])
    assert any(t["request"] not in starts for t in per["trims"])  # the control: per-request does trim inside a turn


def _rich(tx: Tx) -> None:
    """Five stop-turns holding every kind the rules touch, with typed text, a first message and a skill body."""
    tx.user("the brief: build the fixture")
    s = tx.tool_id()
    tx.request(90000, [call(s, "Skill", skill="build-loop")], output=10, thinking=0)
    tx.results((s, "Launching skill: build-loop"))
    tx.user("SKILL BODY " * 300, origin=None, meta=True, source=s, new_prompt=False)
    for turn in range(5):
        for j in range(3):
            w = tx.tool_id()
            tx.request(100000 + 5000 * tx.req, [think(), call(w, "Write", file_path=f"/w/{turn}.py", content="code " * 600)],
                       output=1600, thinking=500)
            tx.results((w, "written"))
            tx.reminder(turn * 3 + j)
            tx.hook("PreToolUse:Bash", "hook context " * 30)
            r = tx.tool_id()
            tx.request(100000 + 5000 * tx.req, [call(r, "Read", file_path="/w/shared.py")], output=10, thinking=0)
            tx.results((r, TOKENS_1000))
            step(tx, 100000 + 5000 * tx.req, TOKENS_1000, blocks=(think(),), thinking=300, output=320)
        tx.stop()
        tx.user(f"typed message after turn {turn}: keep going")
    step(tx, 400000)


def check_protected(m, where: Path) -> None:
    tx = Tx()
    _rich(tx)
    tl, idx = _built(m, tx, where)
    sim = m.simulate(tl, m.Cell(1, 0, 0, ("R1", "R2", "R3", "R4"), "per-request", "stop", 2), idx, keep_map=True)
    seg = tl.segments[0]
    rules = set()
    for (_, pos), mark in sim["archive"].items():
        it = seg.items[pos]
        rules.add(mark[0])
        assert not (it.typed or it.first_user or it.name == "skill_body")
        assert it.turn_stop < tl.requests[mark[2]].turn_stop - 2  # never the current turn nor the last K = 2 turns
    assert rules == {"R1", "R2", "R3", "R4"}  # the control: every rule archived something here


def check_stub_pair(m, where: Path) -> None:
    tx = Tx()
    _rich(tx)
    tl, idx = _built(m, tx, where)
    sim = m.simulate(tl, m.Cell(1, 0, 0, ("R1", "R2", "R3", "R4"), "per-request", "stop", 0), idx, keep_map=True)
    seg = tl.segments[0]
    stubs = 0
    for q in seg.requests:
        listing = dict(m.active_list(seg, sim["archive"], q.index))
        calls = {seg.items[p].tool_use_id: s for p, s in listing.items() if seg.items[p].kind == "tool_input"}
        results = {seg.items[p].tool_use_id: s for p, s in listing.items() if seg.items[p].kind == "tool_result"}
        assert set(results) <= set(calls)  # every result's call is in the active list, kept or as a stub
        for p, state in listing.items():
            if state == "dropped":
                assert seg.items[p].kind == "thinking"  # only thinking leaves no stub
        stubs += sum(1 for s in results.values() if s == "stub")
    assert stubs > 0  # the control: results were stubbed and kept their pairs


def _uaa_fixture(tx: Tx, needle: str, *, kept_copy: bool, filler_after: int) -> None:
    tx.user("go")
    step(tx, 10000, "noise " * 200 + needle + " noise" * 200, command="make fixture")
    for j in range(2):
        step(tx, 11000 + j)
    if kept_copy:
        tx.user(f"note for later: {needle}")  # typed text, never archived, entering after the archived result
    for j in range(2 + filler_after):
        step(tx, 12000 + j)
    step(tx, 20000, command=f"grep {needle} /work")
    tx.request(21000, [text("done")], output=5, thinking=0)


def _uaa_rows(m, where: Path, *, kept_copy: bool, filler_after: int = 0) -> list[dict]:
    tx = Tx()
    needle = "Zqneedle" + secrets.token_hex(4)
    _uaa_fixture(tx, needle, kept_copy=kept_copy, filler_after=filler_after)
    tl, idx = _built(m, tx, where)
    sim = m.simulate(tl, m.Cell(1, 0, 2, ("R3",), "per-request", "request", 0), idx, keep_map=True)
    seg = tl.segments[0]
    rows = [row for row, ((_, pos), _) in zip(sim["uaa"], sim["archive"].items()) if needle in seg.items[pos].text]
    assert len(rows) == 1  # the one result that held the needle was archived
    return rows


def check_uaa_counts_one(m, where: Path) -> None:
    (row,) = _uaa_rows(m, where, kept_copy=False)
    assert row["m20"] is True and row["mh"] is True and row["hits20"] == 1


def check_uaa_negative_control(m, where: Path) -> None:
    (row,) = _uaa_rows(m, where, kept_copy=True)
    assert row["m20"] is False and row["mh"] is False and row["hits20"] == 0


def check_uaa_horizon_only(m, where: Path) -> None:
    (row,) = _uaa_rows(m, where, kept_copy=False, filler_after=25)
    assert row["m20"] is False and row["mh"] is True


# Round 2 (tasks/briefs/jev-trim/T0-REPLAY-R2-brief.md): version-2 cells.

R1_TO_R6 = ("R1", "R2", "R3", "R4", "R5", "R6")
AGENT_MESSAGE = '<agent-message from="a0fixture"> [Subagent hand-back] '
NOTIFICATION = "<task-notification> "


def _v2(m, budget, low, age, rules, mode, k, guard="none", opening="record"):
    return m.Cell(budget, low, age, rules, mode, "request", k, guard, 2, opening)


def _eight_steps(tx: Tx) -> None:
    for c in (1000, 2000, 3000, 4000, 5000, 5100, 5200, 5300):  # check_hysteresis's contexts
        step(tx, c, TOKENS_1000)


def check_request_window_between_turn(m, where: Path) -> None:
    """Item 2: a between-turn trim fires at stop-hook turn starts only; the current request and the last K requests are
    protected; the trim takes items of the turn that just finished once they are outside the window."""
    tx = Tx()
    tx.user("go")
    for turn in range(4):
        for j in range(5):
            step(tx, 100000 + 1000 * tx.req, TOKENS_1000)
        tx.stop()
        tx.user(f"turn {turn}")
    step(tx, 200000)
    tl, idx = _built(m, tx, where)
    starts = {q.index for i, q in enumerate(tl.requests) if i == 0 or q.turn_stop != tl.requests[i - 1].turn_stop}
    assert starts == {0, 5, 10, 15, 20}
    k = 3
    sim = m.simulate(tl, _v2(m, 1, 0, 0, ("R3",), "between-turn", k), idx, keep_map=True)
    seg = tl.segments[0]
    assert sim["trims"] and all(t["request"] in starts for t in sim["trims"])
    finished = 0
    for (_, pos), mark in sim["archive"].items():
        it = seg.items[pos]
        assert mark[2] - it.req > k  # never the current request nor the last K = 3
        finished += it.turn_stop == tl.requests[mark[2]].turn_stop - 1
    assert finished >= 3  # at each later turn start, the finished turn's results outside the window were taken
    per = m.simulate(tl, _v2(m, 1, 0, 0, ("R3",), "per-request", k), idx)
    assert any(t["request"] not in starts for t in per["trims"])  # the control: per-request trims inside a turn


def _opening_fixture(m, where: Path):
    tx = Tx()
    tx.boundary()
    tx.attach({"type": "nested_memory", "path": "/w/CLAUDE.md", "displayPath": "CLAUDE.md",
               "content": {"content": TOKENS_1000}})
    tx.attach({"type": "deferred_tools_delta", "addedNames": ["A"], "addedLines": [TOKENS_1000]})
    for j in range(4):
        step(tx, 10000 + 1000 * j, TOKENS_1000)
    tx.attach({"type": "nested_memory", "path": "/w/b/CLAUDE.md", "displayPath": "b/CLAUDE.md",
               "content": {"content": TOKENS_1000}})
    for j in range(4):
        step(tx, 20000 + 1000 * j)
    tl, idx = _built(m, tx, where)
    (seg,) = tl.segments
    opening = [it.pos for it in seg.items if it.start]
    assert [seg.items[p].name for p in opening] == ["compact_summary", "nested_memory", "deferred_tools_delta"]
    later = [it.pos for it in seg.items if it.attach_type == "nested_memory" and not it.start]
    return tl, idx, seg, opening, later


def check_opening_group(m, where: Path) -> None:
    """`group`: every item that entered before a segment's first request is its first user message (protected)."""
    tl, idx, seg, opening, later = _opening_fixture(m, where)
    sim = m.simulate(tl, _v2(m, 1, 0, 0, R1_TO_R6, "per-request", 0, opening="group"), idx, keep_map=True)
    archived = {pos for (_, pos) in sim["archive"]}
    assert not archived & set(opening)
    assert later and set(later) <= archived  # the control: the same type later in the segment is taken


def check_opening_record(m, where: Path) -> None:
    """`record` (round 1's reading, the default): only the first user text record is protected; R6 takes the
    opening attachments once they are older than A."""
    tl, idx, seg, opening, later = _opening_fixture(m, where)
    sim = m.simulate(tl, _v2(m, 1, 0, 0, R1_TO_R6, "per-request", 0), idx, keep_map=True)
    archived = {pos: mark for (_, pos), mark in sim["archive"].items()}
    summary, *attachments = opening
    assert summary not in archived  # the first user text record stays
    assert set(attachments) <= set(archived) and all(archived[p][0] == "R6" for p in attachments)


def _r5_fixture(tx: Tx) -> None:
    tx.user("go")
    step(tx, 10000)
    tx.user(NOTIFICATION + TOKENS_1000, origin="task-notification")  # structure: the origin
    step(tx, 11000)
    tx.user("a peer's report " + TOKENS_1000, origin="peer", handback=True)  # structure: the flag
    step(tx, 12000)
    tx.attach({"type": "queued_command", "commandMode": "task-notification", "prompt": NOTIFICATION + TOKENS_1000})
    step(tx, 13000)
    tx.attach({"type": "queued_command", "commandMode": "prompt", "prompt": AGENT_MESSAGE + TOKENS_1000})  # envelope
    step(tx, 14000)
    tx.user("please carry on with the plan " + TOKENS_1000)  # negative controls: an ordinary typed message,
    step(tx, 15000)
    tx.user("the log shows " + AGENT_MESSAGE + TOKENS_1000)  # one that quotes the tag without opening with it,
    step(tx, 16000)
    tx.user("a peer's note " + TOKENS_1000, origin="peer")  # and a peer message without the hand-back flag
    for j in range(6):
        step(tx, 17000 + j)


def check_r5(m, where: Path) -> None:
    """Item 3: hand-backs and task notifications are recognized by structure or envelope and stubbed once older than
    A requests; an ordinary user text is not taken."""
    tx = Tx()
    _r5_fixture(tx)
    tl, idx = _built(m, tx, where)
    rec = m.recognition(tl)
    assert {k: v["items"] for k, v in rec["r5_by_kind_name_route"].items()} == {
        "other_attachment:queued_command:structure": 1, "other_user_text:peer:structure": 1,
        "other_user_text:task-notification:structure": 1, "typed_user_text:queued_prompt:envelope": 1}
    sim = m.simulate(tl, _v2(m, 1, 0, 2, ("R5",), "per-request", 0), idx, keep_map=True)
    seg = tl.segments[0]
    taken = sorted((seg.items[p].name, mark[0], mark[2] - seg.items[p].req, mark[3])
                   for (_, p), mark in sim["archive"].items())
    assert taken == [("peer", "R5", 3, 40), ("queued_command", "R5", 3, 40), ("queued_prompt", "R5", 3, 40),
                     ("task-notification", "R5", 3, 40)]  # stubs, at the first request past A = 2


def _r6_fixture(tx: Tx) -> None:
    tx.user("go")
    step(tx, 10000)
    tx.attach({"type": "edited_text_file", "filename": "/w/a.py", "snippet": TOKENS_1000})
    step(tx, 11000)
    tx.attach({"type": "edited_text_file", "filename": "/w/b.py", "snippet": TOKENS_1000})
    tx.attach({"type": "deferred_tools_delta", "addedNames": ["A"], "addedLines": [TOKENS_1000]})
    step(tx, 12000)
    tx.attach({"type": "edited_text_file", "filename": "/w/a.py", "snippet": TOKENS_1000})  # a newer a.py
    tx.attach({"type": "deferred_tools_delta", "addedNames": ["B"], "addedLines": [TOKENS_1000]})  # no key: the type
    tx.attach({"type": "invoked_skills", "skills": [{"name": "build-loop", "content": TOKENS_1000}]})  # a skill body
    for j in range(6):
        step(tx, 13000 + j)


def check_r6(m, where: Path) -> None:
    """Item 4: an attachment superseded by a newer one of its type and key is archived; any other older than A becomes
    a stub; a skill body never."""
    tx = Tx()
    _r6_fixture(tx)
    tl, idx = _built(m, tx, where)
    seg = tl.segments[0]
    a1, b, d1, a2, d2, skill = [it.pos for it in seg.items if it.attach_type is not None]
    assert seg.items[skill].attach_type == "invoked_skills"

    def taken(age: int) -> dict:
        sim = m.simulate(tl, _v2(m, 1, 0, age, ("R6",), "per-request", 0), idx, keep_map=True)
        return {pos: mark for (_, pos), mark in sim["archive"].items()}

    superseded = taken(1000)  # no attachment gets that old here: supersession alone
    assert set(superseded) == {a1, d1}  # b.py is another file: a newer a.py supersedes only the older a.py
    assert all(mark[0] == "R6" and mark[3] == 40 for mark in superseded.values())
    aged = taken(2)
    assert set(aged) == {a1, b, d1, a2, d2}  # every attachment, older than A = 2, except the skill body
    assert all(mark[0] == "R6" for mark in aged.values())


def check_reach(m, where: Path) -> None:
    """Item 5, `reach`: a trim fires only when archiving every eligible item brings the context to L or below."""
    tx = Tx()
    tx.user("go")
    _eight_steps(tx)
    tl, idx = _built(m, tx, where)
    # K = 3 protects the results that entered at r-3..r. At request 5 (5,100 > B) one result is eligible: 5,100 - 960 =
    # 4,140 > L; at 6 two: 3,280 > L; at 7 three: 2,420 <= L, so the trim fires there and archives all three.
    sim = m.simulate(tl, _v2(m, 5000, 3000, 0, ("R3",), "per-request", 3, "reach"), idx)
    assert [(t["request"], t["items"]) for t in sim["trims"]] == [(7, 3)]
    assert sim["blocked"] == 2
    assert [round(a, 1) for _, a in sim["active"]] == [1000, 2000, 3000, 4000, 5000, 5100, 5200, 2420]
    none = m.simulate(tl, _v2(m, 5000, 3000, 0, ("R3",), "per-request", 3), idx)
    assert [(t["request"], t["items"]) for t in none["trims"]] == [(5, 1)]  # the control: no guard fires at 5


def check_cooldown(m, where: Path) -> None:
    """Item 5, `cooldown:C`: at most one trim per C requests."""
    tx = Tx()
    tx.user("go")
    for j in range(12):
        step(tx, 10000 + 1000 * j, TOKENS_1000)
    tl, idx = _built(m, tx, where)
    sim = m.simulate(tl, _v2(m, 1, 0, 0, ("R3",), "per-request", 0, "cooldown:3"), idx)
    assert [t["request"] for t in sim["trims"]] == [2, 5, 8, 11]  # the first eligible result enters at request 1
    assert sim["blocked"] == 6  # requests 3, 4, 6, 7, 9 and 10
    none = m.simulate(tl, _v2(m, 1, 0, 0, ("R3",), "per-request", 0), idx)
    assert [t["request"] for t in none["trims"]] == list(range(2, 12))  # the control


def check_pessimistic(m, where: Path) -> None:
    """Item 6: the pessimistic bound rewrites everything after the fixed start (first context - postTokens)."""
    tx = Tx()
    tx.boundary(post_tokens=600)
    _eight_steps(tx)
    tl, idx = _built(m, tx, where)
    (seg,) = tl.segments
    assert (seg.fixed_start, seg.fixed_source) == (400.0, "first_context_minus_post_tokens")  # 1,000 - 600 < 990
    sim = m.simulate(tl, _v2(m, 5000, 3000, 0, ("R3",), "per-request", 0), idx)
    (trim,) = sim["trims"]
    # As check_hysteresis: the trim at request 5 archives three results (saves 2,880), sends 2,220; the edit point
    # keeps 1,010 cached, so round 1's model writes 2,220 - 1,010 - 3 uncached = 1,207 again. The pessimistic bound
    # keeps only the fixed start: 2,220 - 400 - 3 = 1,817.
    assert (trim["request"], trim["items"]) == (5, 3)
    assert trim["extra_write_tokens"] == pytest.approx(1207)
    assert trim["extra_write_tokens_pessimistic"] == pytest.approx(1817)
    terms = m.cache_terms(tl, sim, 0.05, 2.0, key="extra_write_tokens_pessimistic")
    assert terms["extra_write_units"] == pytest.approx(1.95 * 1817, abs=0.05)
    assert terms["net_units"] == pytest.approx(1.95 * 1817 - 0.05 * 2880 * 3, abs=0.1)


def check_composition(m, where: Path) -> None:
    """Item 7: the composition is taken at the median request AFTER trimming."""
    tx = Tx()
    tx.user("go")
    _eight_steps(tx)
    tl, idx = _built(m, tx, where)
    cell = _v2(m, 5000, 3000, 0, ("R3",), "per-request", 0)
    sim = m.simulate(tl, cell, idx)
    comp = m.composition(tl, cell, sim, idx)
    go = len("go") / 2.9
    # Active after trimming: 1,000 2,000 3,000 4,000 5,000 2,220 2,320 2,420; the lower middle is 2,320 (request 6).
    # There: results 1-3 are stubs (3 x 40); results 4-6 (3 x 1,000) and inputs 0-5 (6 x 10) are kept; K = 0 protects
    # request 6's input and result (1,010) and "go" is typed text; inputs 0-4 (50) are outside R3.
    assert (comp["request"], comp["active"]) == (6, 2320)
    assert comp["by_kind"]["tool_result"] == 3000 and comp["by_kind"]["tool_input"] == 60
    assert (comp["stubs"], comp["stub_count"]) == (120, 3)
    assert comp["kept_protected"] == round(1010 + go, 1)
    assert comp["kept_outside_every_rule"] == 50 and comp["kept_a_rule_may_take_later"] == 2000
    assert comp["fixed_start"] == round(1000 - go, 1)
    assert comp["floor"] == round(1000 - go + 1010 + go + 50 + 120, 1)


# ---------------------------------------------------------------- normal behavior

def test_timeline_of_a_hand_built_transcript(tmp_path):
    check_timeline(replay, tmp_path)


def test_r1_archives_superseded_copies_and_keeps_the_newest(tmp_path):
    check_r1_supersede(replay, tmp_path)


def test_r2_archives_thinking_only_before_the_current_turn(tmp_path):
    check_r2_thinking(replay, tmp_path)


def test_r3_age_boundary(tmp_path):
    check_r3_age_boundary(replay, tmp_path)


def test_r4_archives_only_large_old_inputs(tmp_path):
    tx = Tx()
    tx.user("go")
    big, small = [], []
    for j in range(6):
        w = tx.tool_id()
        tx.request(10000 + j, [call(w, "Write", file_path=f"/w/{j}.py", content="code " * 1200)], output=2100, thinking=0)
        tx.results((w, "written"))
        big.append(w)
        small.append(step(tx, 10100 + j))
    tl, idx = _built(replay, tx, tmp_path)
    sim = replay.simulate(tl, replay.Cell(1, 0, 3, ("R4",), "per-request", "request", 0), idx, keep_map=True)
    seg = tl.segments[0]
    archived = {seg.items[p].tool_use_id: mark for (_, p), mark in sim["archive"].items()}
    assert set(archived) and set(archived) <= set(big)  # only the Write bodies (2,100 tokens each), never small inputs
    assert all(seg.items[p].kind == "tool_input" for (_, p) in sim["archive"])
    for (_, p), mark in sim["archive"].items():
        assert mark[2] - seg.items[p].req == 4


def test_hysteresis_fires_past_b_and_lands_at_or_under_l(tmp_path):
    check_hysteresis(replay, tmp_path)


def test_between_turn_never_trims_inside_a_turn(tmp_path):
    check_between_turn(replay, tmp_path)


def test_the_protected_set_is_never_archived(tmp_path):
    check_protected(replay, tmp_path)


def test_a_stub_keeps_its_pair(tmp_path):
    check_stub_pair(replay, tmp_path)


def test_the_cache_model_on_hand_computed_numbers(tmp_path):
    out = check_hysteresis(replay, tmp_path)
    tl, sim = out["tl"], out["sim"]
    # The trim at request 5 saves 3 x 960 = 2,880 tokens on requests 5, 6 and 7. Its edit point is the result that
    # entered at request 1: the context of request 0 (1,000) plus request 0's tool input (the exact visible rest,
    # output 10 - thinking 0 = 10), so 1,010 tokens stay cached; the tail rewritten = (5,100 - 2,880) - 1,010 = 1,210,
    # of which the real request wrote 0 and 3 were uncached: 1,207 extra write tokens.
    assert sim["saved"] == [0, 0, 0, 0, 0, 2880, 2880, 2880]
    assert sim["trims"][0]["extra_write_tokens"] == pytest.approx(1207)
    terms = replay.cache_terms(tl, sim, 0.05, 2.0)
    assert terms["read_saving_units"] == pytest.approx(0.05 * 2880 * 3, abs=0.05)
    assert terms["extra_write_units"] == pytest.approx(1.95 * 1207, abs=0.05)
    real = 0.05 * sum(c - 3 for c in (1000, 2000, 3000, 4000, 5000, 5100, 5200, 5300)) + 3 * 8
    assert terms["real_units"] == pytest.approx(real, abs=0.05)
    assert terms["net_units"] == pytest.approx(1.95 * 1207 - 0.05 * 2880 * 3, abs=0.1)


def test_use_after_archive_counts_a_token_only_the_archived_item_held(tmp_path):
    check_uaa_counts_one(replay, tmp_path)


def test_use_after_archive_is_zero_when_a_kept_item_holds_the_token(tmp_path):
    check_uaa_negative_control(replay, tmp_path)


def test_use_after_archive_beyond_twenty_counts_at_the_horizon_only(tmp_path):
    check_uaa_horizon_only(replay, tmp_path)


def test_visible_only_variant_counts_an_archived_earlier_copy(tmp_path):
    tx = Tx()
    needle = "Zqcopy" + secrets.token_hex(4)
    tx.user("go")
    step(tx, 10000, "first " * 300 + needle)
    step(tx, 10001, "second " * 300 + needle)
    for j in range(3):
        step(tx, 10002 + j)
    step(tx, 20000, command=f"cat {needle}")
    tx.request(21000, [text("done")], output=5, thinking=0)
    tl, idx = _built(replay, tx, tmp_path)
    sim = replay.simulate(tl, replay.Cell(1, 0, 2, ("R3",), "per-request", "request", 0), idx, keep_map=True)
    seg = tl.segments[0]
    rows = [row for row, ((_, p), _) in zip(sim["uaa"], sim["archive"].items()) if needle in seg.items[p].text]
    assert len(rows) == 2
    # The first copy is archived at request 4 while the second (still kept) holds the token: 0 under both. The second
    # is archived at request 5; the first copy is its earlier history, so the committed definition counts 0 although no
    # visible item holds the token any more (the under-count the variant exists to show); visible-only counts 1.
    assert [r["mh"] for r in rows] == [False, False]
    assert [r["visible_mh"] for r in rows] == [False, True]


def test_the_restricted_miss_calls_equal_unrestricted_calls(tmp_path):
    """The oracle recomputes each archived item's miss with FULL history and lookahead sets built from the archive
    map, calling accounting.miss directly, and must agree with the restricted, memoized rows."""
    tx = Tx()
    _rich(tx)
    tl, idx = _built(replay, tx, tmp_path)
    sim = replay.simulate(tl, replay.Cell(1, 0, 0, ("R1", "R3", "R4"), "per-request", "stop", 2), idx, keep_map=True)
    seg = tl.segments[0]
    look = [it for it in seg.items if it.kind in ("tool_input", "assistant_text")]
    checked = 0
    for row, ((_, q), mark) in zip(sim["uaa"], sim["archive"].items()):
        item, r = seg.items[q], mark[2]
        if not row["scored"]:
            continue
        history = set(seg.fixed)
        for it in seg.items:
            if it.req > r:
                continue
            other = sim["archive"].get((seg.index, it.pos))
            if it.pos < q or other is None or other[2] > r:
                history |= it.toks  # earlier items, and items still active after the trim
            elif other[3]:
                history |= it.stub_toks  # stubs stay in the context
        after = [it for it in look if it.req > r]
        calls = [it.rerun for it in after if it.kind == "tool_input"]
        used20 = set().union(*(it.toks for it in after[:accounting.LOOKAHEAD]))
        used_h = set().union(*(it.toks for it in after))
        hits20, rerun20 = accounting.miss(item.text, item.stub, history, [used20], calls[:accounting.LOOKAHEAD], item.rerun)
        hits_h, rerun_h = accounting.miss(item.text, item.stub, history, [used_h], calls, item.rerun)
        assert (hits20 > 0 or rerun20, hits_h > 0 or rerun_h, hits20) == (row["m20"], row["mh"], row["hits20"])
        checked += 1
    assert checked > 20


def test_thinking_is_sized_by_the_model_when_asked(tmp_path):
    tx = Tx()
    tx.user("go")
    a = tx.tool_id()
    tx.request(20000, [think(), call(a, "Bash", command="ls")], output=900, thinking=400)
    tx.results((a, "ok"))
    step(tx, 21000)
    path, size = tx.write(tmp_path / "t.jsonl")
    visible = len(json.dumps({"command": "ls"}))
    exact = replay.build(path, size)
    model = replay.build(path, size, thinking_size="model")
    think_exact = [it.size for it in exact.segments[0].items if it.kind == "thinking"]
    think_model = [it.size for it in model.segments[0].items if it.kind == "thinking"]
    assert think_exact == [400.0] and think_model == [pytest.approx(900 - visible / 3.0)]
    assert exact.params["thinking_check"] == {"requests_with_both": 1, "exact_thinking_tokens": 400,
                                              "modeled_thinking_tokens": round(900 - visible / 3.0, 1)}


def test_round_two_protects_a_request_window_in_between_turn_mode(tmp_path):
    check_request_window_between_turn(replay, tmp_path)


def test_round_two_protects_the_opening_group_when_read_as_a_group(tmp_path):
    check_opening_group(replay, tmp_path)


def test_round_two_protects_the_first_user_record_by_default(tmp_path):
    check_opening_record(replay, tmp_path)


def test_r5_recognizes_hand_backs_and_stubs_them(tmp_path):
    check_r5(replay, tmp_path)


def test_r6_archives_superseded_and_old_attachments_but_no_skill_body(tmp_path):
    check_r6(replay, tmp_path)


def test_the_reach_guard_fires_only_when_l_can_be_reached(tmp_path):
    check_reach(replay, tmp_path)


def test_the_cooldown_guard_spaces_the_trims(tmp_path):
    check_cooldown(replay, tmp_path)


def test_the_pessimistic_cache_bound_on_hand_computed_numbers(tmp_path):
    check_pessimistic(replay, tmp_path)


def test_the_composition_at_the_median_after_trimming(tmp_path):
    check_composition(replay, tmp_path)


def check_fixed_start(m, where: Path) -> None:
    """Item 6's fixed start: the lower of the first context minus the modeled opening items and the first context minus
    the compaction's postTokens (a segment without a compaction has only the first)."""
    tx = Tx()
    tx.user("go")
    for j in range(3):
        step(tx, 50000 + j)
    tx.boundary(post_tokens=45000)  # postTokens lower: 60,000 - 45,000 = 15,000 < 60,000 - the summary
    for j in range(3):
        step(tx, 60000 + j)
    tx.boundary(post_tokens=100)  # the modeled estimate lower: a large opening attachment postTokens leaves out
    tx.attach({"type": "nested_memory", "path": "/w/CLAUDE.md", "content": {"content": "word " * 5800}})
    for j in range(3):
        step(tx, 30000 + j)
    tl, _ = _built(m, tx, where)
    summary = len("a summary of the earlier work") / 2.9
    attachment = (len("/w/CLAUDE.md") + 1 + 29000) / 2.9  # its two strings, joined by one newline
    got = [(s.fixed_start, s.fixed_source) for s in tl.segments]
    assert got[0] == (pytest.approx(50000 - len("go") / 2.9), "first_context_minus_the_modeled_opening_items")
    assert got[1] == (15000.0, "first_context_minus_post_tokens")
    assert got[2] == (pytest.approx(30000 - summary - attachment), "first_context_minus_the_modeled_opening_items")
    assert tl.segments[2].fixed_estimates["first_context_minus_post_tokens"] == 29900.0  # the one not used


def test_the_fixed_start_is_the_lower_estimate(tmp_path):
    check_fixed_start(replay, tmp_path)
    rich = Tx()
    _rich(rich)
    tl, _ = _built(replay, rich, tmp_path / "rich")
    (seg,) = tl.segments
    assert seg.fixed_source == "first_context_minus_the_modeled_opening_items"
    assert seg.fixed_start == pytest.approx(90000 - len("the brief: build the fixture") / 2.9)


def _eligible_brute(it, rules, r, age, superseded, stub, opening="group") -> float:
    """The reach probe's oracle, written from the brief's rules, not from the probe: the gain of archiving one item."""
    gain = it.size - (0.0 if it.kind == "thinking" else stub)
    protected = ((it.typed and not it.handback) or it.first_user or (opening == "group" and it.start)
                 or it.name == "skill_body" or it.attach_type == "invoked_skills")
    if gain <= 0 or protected:
        return 0.0
    old = it.req < r - age
    attachment = it.attach_type is not None and not it.handback and not it.typed
    if (("R2" in rules and it.kind == "thinking")
            or ("R3" in rules and it.kind == "tool_result" and it.size > stub and old)
            or ("R4" in rules and it.kind == "tool_input" and it.size > 500 and old)
            or ("R5" in rules and it.handback and it.size > stub and old)
            or ("R6" in rules and attachment and it.size > stub and old)
            or ("R1" in rules and it.key is not None and it.pos in superseded["R1"])
            or ("R6" in rules and attachment and it.pos in superseded["R6"])):
        return gain
    return 0.0


@pytest.mark.parametrize("opening", ["record", "group"])
def test_the_reach_probe_equals_a_brute_force_sum(tmp_path, opening):
    """ReachProbe (the reach guard's O(log n) answer) against a plain sum over the items at every request of a fixture
    that holds every rule's items, for several rule sets, windows and ages, with items archived along the way."""
    tx = Tx()
    tx.boundary()  # an opening group: the two readings protect different items
    tx.attach({"type": "nested_memory", "path": "/w/CLAUDE.md", "content": {"content": TOKENS_1000}})
    _rich(tx)
    tx.user(NOTIFICATION + TOKENS_1000, origin="task-notification")
    tx.attach({"type": "edited_text_file", "filename": "/w/0.py", "snippet": TOKENS_1000})
    step(tx, 410000)
    tx.attach({"type": "edited_text_file", "filename": "/w/0.py", "snippet": TOKENS_1000})
    tx.attach({"type": "invoked_skills", "skills": [{"name": "build-loop", "content": TOKENS_1000}]})
    for j in range(5):
        step(tx, 420000 + j, TOKENS_1000)
    tl, idx = _built(replay, tx, tmp_path)
    (seg,) = tl.segments
    ix, items = idx[seg.index], seg.items
    checked = nonzero = 0
    for rules in (R1_TO_R6, ("R1", "R2", "R3", "R4"), ("R3",), ("R1", "R6"), ("R5", "R2")):
        for k, age in ((0, 0), (3, 2), (10, 5)):
            probe = replay.ReachProbe(items, ix, rules, 40, replay.protected_kind_of(
                replay.Cell(1, 0, age, rules, "per-request", "request", k, "reach", 2, opening)))
            superseded: dict = {"R1": set(), "R6": set()}
            archived: set = set()
            entered = 0
            for request in seg.requests:
                r = request.index
                while entered < len(items) and items[entered].req <= r:
                    for rule, older in (("R1", ix.supersedes[entered]), ("R6", ix.supersedes6[entered])):
                        if older is not None and rule in rules:
                            superseded[rule].add(older)
                            if older not in archived:
                                probe.supersede(older)
                    entered += 1
                protect_from = bisect.bisect_left(ix.req, r - k, 0, entered)
                age_from = bisect.bisect_left(ix.req, r - age, 0, entered)
                brute = sum(_eligible_brute(it, rules, r, age, superseded, 40, opening) for it in items[:protect_from]
                            if it.pos not in archived)
                assert probe.max_gain(protect_from, age_from) == pytest.approx(brute, abs=1e-6)
                checked += 1
                nonzero += brute > 0
                for it in items[:protect_from:7]:  # archive some items as a trim would, and keep checking
                    if it.pos not in archived and _eligible_brute(it, rules, r, age, superseded, 40, opening) > 0:
                        archived.add(it.pos)
                        probe.archive(it.pos)
    assert checked > 500 and nonzero > 200  # the control: the sums were not all zero


# Python 3.12 made sum() over floats compensated (Neumaier), so a cache total rounded to one decimal can land a tenth
# apart (508383.9 on 3.11, 508384.0 on 3.12 and 3.13; 144 values in run-d.json). The committed round-1 code (aed7d82)
# writes each hash below on its own interpreter family (measured 2026-09-29 with /usr/bin/python3.11, 3.12 and 3.13;
# CI run #1128 on 3.12 read the 3.12 hash), so the pin is per family and the claim stays "round 2 writes exactly what
# round 1 wrote on the same interpreter".
_RUN_D_BY_FAMILY = {
    "3.11": "234fdcb5f4c1567358e568eebab0b4abcd59c200c588df57ef9bc3ba4da5b1e6",
    "3.12+": "30072115fcbf247356c30a9dc3e3fc05e0a8810b5a112598657242b99d8af0a4",
}
GOLDEN_ROUND_ONE = {  # captured from the committed round-1 code (aed7d82, replay.py sha256 ff35dbb8541818bd...)
    "t.jsonl": "0a465650557e35c091b0430b59e7c925c0ebb647c8d554d8baf5cbbb510f2cb6",
    "run-d.json": _RUN_D_BY_FAMILY["3.12+" if sys.version_info >= (3, 12) else "3.11"],
    "SUMMARY.md": "c31ff84313887b019a70097d39f138a5a4cfbd65ce83973a14473131297dd812",
}


def test_round_one_outputs_stay_byte_identical(tmp_path):
    """The brief's rule: round 1's outputs stay byte-identical. Round 1's command lines on the rich fixture write the
    bytes the committed round-1 code wrote."""
    tx = Tx()
    _rich(tx)
    path, size = tx.write(tmp_path / "t.jsonl")
    out = tmp_path / "out"
    for args in (["run", "--transcript", path, "--pin", str(size), "--label", "d", "--out", str(out)],
                 ["summary", "--out", str(out), "--stamp", "fixed"]):
        done = subprocess.run([sys.executable, str(REPLAY), *args], capture_output=True, text=True, timeout=300)
        assert done.returncode == 0, done.stderr
    got = {name: hashlib.sha256(p.read_bytes()).hexdigest()
           for name, p in (("t.jsonl", Path(path)), ("run-d.json", out / "run-d.json"), ("SUMMARY.md", out / "SUMMARY.md"))}
    assert got == GOLDEN_ROUND_ONE


def test_round_two_grid_runs_and_writes_its_summary(tmp_path):
    tx = Tx()
    _rich(tx)
    _r5_fixture(tx)
    path, size = tx.write(tmp_path / "t.jsonl")
    out = tmp_path / "out"
    for args in (["run", "--grid", "r2", "--transcript", path, "--pin", str(size), "--label", "v2", "--out", str(out),
                  "--modes", "per-request"],
                 ["summary", "--out", str(out), "--stamp", "fixed"]):
        done = subprocess.run([sys.executable, str(REPLAY), *args], capture_output=True, text=True, timeout=300)
        assert done.returncode == 0, done.stderr
    result = json.loads((out / "run-v2.json").read_text())
    assert result["schema"] == 2 and len(result["cells"]) == len(replay.grid_r2(("per-request",))) == 288
    assert result["params"]["opening"] == "record"  # the default: round 1's reading, as the brief keeps the kinds
    assert {(c["K"], c["guard"], c["turn_unit"]) for c in result["cells"]} == {
        (k, g, "request") for k in replay.R2_WINDOWS for g in replay.GUARDS}
    assert all(c["composition_at_median"] is not None for c in result["cells"])
    assert result["recognition"]["r5_items"] == 4
    summary = (out / "SUMMARY.md").read_text()
    assert "## Run `v2`" in summary and "### Best row per budget, by stated criterion" in summary
    assert summary.count("| per-request |") >= 2 * 288  # the full grid and its composition table


def test_a_directory_mixing_the_rounds_is_refused(tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    (out / "run-a.json").write_text(json.dumps({"schema": 1, "label": "a"}))
    (out / "run-b.json").write_text(json.dumps({"schema": 2, "label": "b"}))
    with pytest.raises(ValueError, match="mixes round-1 and round-2 runs"):
        replay.write_summary(out, "fixed")


def test_the_opening_reading_is_named_in_the_outputs_and_refused_on_the_round_one_grid(tmp_path):
    tx = Tx()
    _rich(tx)
    path, size = tx.write(tmp_path / "t.jsonl")
    out = tmp_path / "out"
    done = subprocess.run([sys.executable, str(REPLAY), "run", "--grid", "r2", "--opening", "group", "--modes",
                           "per-request", "--transcript", path, "--pin", str(size), "--label", "g", "--out", str(out)],
                          capture_output=True, text=True, timeout=300)
    assert done.returncode == 0, done.stderr
    result = json.loads((out / "run-g.json").read_text())
    assert result["params"]["opening"] == "group" and {c["opening"] for c in result["cells"]} == {"group"}
    refused = subprocess.run([sys.executable, str(REPLAY), "run", "--opening", "group", "--transcript", path,
                              "--pin", str(size), "--label", "x", "--out", str(tmp_path / "x")],
                             capture_output=True, text=True, timeout=120)
    assert refused.returncode == 2 and "--opening belongs to the r2 grid" in refused.stderr


def test_turn_units_are_refused_on_the_round_two_grid(tmp_path):
    path, size = Tx().write(tmp_path / "t.jsonl")
    done = subprocess.run([sys.executable, str(REPLAY), "run", "--grid", "r2", "--turn-units", "stop", "--transcript",
                           path, "--pin", str(size), "--label", "x", "--out", str(tmp_path / "out")],
                          capture_output=True, text=True, timeout=120)
    assert done.returncode == 2 and "--turn-units belongs to the r1 grid" in done.stderr


def test_segments_restart_at_a_compaction(tmp_path):
    tx = Tx()
    tx.user("go")
    for j in range(3):
        step(tx, 50000 + j, TOKENS_1000)
    tx.boundary()
    for j in range(3):
        step(tx, 60000 + j, TOKENS_1000)
    tl, idx = _built(replay, tx, tmp_path)
    assert [len(s.requests) for s in tl.segments] == [3, 3]
    first = [it for it in tl.segments[1].items if it.first_user]
    assert [it.name for it in first] == ["compact_summary"]  # the new segment's first user message
    sim = replay.simulate(tl, replay.Cell(1, 0, 0, ("R3",), "per-request", "request", 0), idx)
    assert sim["saved"][3] == 0  # the savings restart with the segment


# ---------------------------------------------------------------- failure behavior

def test_an_unparseable_line_is_counted_and_skipped(tmp_path):
    tx = Tx()
    tx.user("go")
    step(tx, 10000)
    tx.garbage()
    step(tx, 11000)
    step(tx, 12000)
    tl, _ = _built(replay, tx, tmp_path)
    assert tl.stats["unparseable_lines"] == 1 and [q.context for q in tl.requests] == [10000, 11000, 12000]


def test_a_record_cut_at_the_pin_is_not_read(tmp_path):
    tx = Tx()
    tx.user("go")
    step(tx, 10000)
    step(tx, 11000)
    tx.request(12000, [text("the last word")], output=5)
    path, size = tx.write(tmp_path / "t.jsonl")
    tl = replay.build(path, size - 20)
    assert tl.stats["truncated_at_limit"] == 1 and [q.context for q in tl.requests] == [10000, 11000]


def test_a_request_without_usage_is_not_a_request(tmp_path):
    tx = Tx()
    tx.user("go")
    step(tx, 10000)
    a = tx.tool_id()
    tx.request(0, [call(a, "Bash", command="echo no usage")], usage=False)
    tx.results((a, TOKENS_1000))
    step(tx, 12000)
    tl, _ = _built(replay, tx, tmp_path)
    assert [q.context for q in tl.requests] == [10000, 12000]
    assert tl.stats["assistant_records_without_usage"] == 1
    assert [it.tool_use_id for it in tl.segments[0].items if it.kind == "tool_input"][1] == a  # still in the context


def test_a_transcript_with_no_requests(tmp_path):
    tx = Tx()
    tx.user("go")
    tx.reminder(1)
    path, _ = tx.write(tmp_path / "t.jsonl")
    out = tmp_path / "out"
    size = Path(path).stat().st_size
    tl = replay.build(path, size)
    assert tl.requests == [] and tl.segments == []
    cells, _ = replay.run(tl, replay.grid(("per-request",)))
    assert cells and all(c["requests"] == 0 and c["trims"]["count"] == 0 for c in cells)
    done = subprocess.run([sys.executable, str(REPLAY), "run", "--transcript", path, "--pin", str(size), "--label",
                           "empty", "--out", str(out)], capture_output=True, text=True, timeout=120)
    assert done.returncode == 0, done.stderr
    assert json.loads((out / "run-empty.json").read_text())["timeline"]["requests"] == 0
    summary = subprocess.run([sys.executable, str(REPLAY), "summary", "--out", str(out), "--stamp", "fixed"],
                             capture_output=True, text=True, timeout=120)
    assert summary.returncode == 0 and "Cross-check: NOT RUN" in (out / "SUMMARY.md").read_text()


def test_an_unknown_thinking_size_is_refused(tmp_path):
    path, size = Tx().write(tmp_path / "t.jsonl")
    with pytest.raises(ValueError, match="thinking_size"):
        replay.build(path, size, thinking_size="guess")


# ---------------------------------------------------------------- the cross-check

def test_crosscheck_per_day_against_an_audit_table(tmp_path):
    tx = Tx(day="2026-09-26")
    tx.user("go")
    for c in (100, 300, 200):
        step(tx, c)
    tx.at("2026-09-28")
    tx.boundary()
    for c in (100, 200, 301, 401):  # an even count: the median is (200 + 301) / 2 = 250.5, nearest-rank 200
        step(tx, c)
    path, size = tx.write(tmp_path / "t.jsonl")
    audit = tmp_path / "audit.md"
    audit.write_text("| Day | Active span | Requests | median | p90 | max | min | Compactions |\n"
                     "| 2026-09-26 | a span | 3 | 200 | 300 | 300 | 100 | 0 |\n"
                     "| 2026-09-27 | no records | 0 | — | — | — | — | 0\n"
                     "| 2026-09-28 | a span | 4 | 250 | 401 | 401 | 100 | 1 |\n")
    result = replay.crosscheck(path, size, audit)
    day26, day28 = result["days"]["2026-09-26"], result["days"]["2026-09-28"]
    assert all(day26["match"].values())
    assert day28["mine"]["median"] == 250.5 and day28["mine"]["median_nearest_rank"] == 200
    assert day28["match"] == {"requests": True, "median": False, "p90": True, "max": True, "min": True,
                              "compactions": True}
    assert day28["median_match_after_truncation"] is True
    assert "2026-09-27" not in result["days"]  # a row without numbers is no audit row


# ---------------------------------------------------------------- the security boundary

def _secret() -> str:
    # Built at run time; a 'Q' in every 8-character window, so no piece can collide with numbers or hex ids.
    return "tok-" + "Q".join(secrets.token_hex(2) for _ in range(8))


def _secret_fixture(tx: Tx, v: str) -> None:
    tx.user(f"my key is {v}")
    a = tx.tool_id()
    tx.request(100000, [{"type": "thinking", "thinking": f"thinking about {v}", "signature": "c2ln"},
                        text(f"I will use {v}"), call(a, "Bash", command=f"curl -H 'x-key: {v}' https://x")],
               output=500, thinking=100)
    tx.results((a, f"response body {v} " + TOKENS_1000))
    b = tx.tool_id()
    tx.request(110000, [call(b, "Read", file_path=f"/work/{v}/notes.md")], output=20, thinking=0)
    tx.results((b, f"notes {v} " + TOKENS_1000))
    tx.reminder(1, subject=f"rotate {v}")
    tx.hook("PreToolUse:Bash", f"hook saw {v} " * 20)
    tx.attach({"type": "queued_command", "commandMode": "prompt", "prompt": f"queued {v}"})
    tx.attach({"type": "nested_memory", "path": f"/work/{v}/CLAUDE.md", "content": {"content": f"memory {v}"}})
    tx.attach({"type": "prompt_snapshot", "systemPrompt": [f"system {v}"]})
    tx.stop()
    tx.boundary(summary=f"summary mentions {v}")
    for j in range(30):  # long enough that trims fire in the grid (ages up to 50 requests are not all reached)
        step(tx, 120000 + 3000 * j, f"later {v} " + TOKENS_1000, command=f"grep {v} /work",
             blocks=(think(),), thinking=200, output=260)
        tx.reminder(j + 2, subject=f"rotate {v}")
        tx.hook("PreToolUse:Bash", f"hook saw {v} " * 20)


def test_no_piece_of_a_secret_reaches_any_output_or_print(tmp_path):
    v = _secret()
    tx = Tx()
    _secret_fixture(tx, v)
    path, size = tx.write(tmp_path / "t.jsonl")
    audit = tmp_path / "audit.md"
    audit.write_text("| 2026-09-26 | span | 6 | 115,000 | 123,000 | 123,000 | 100,000 | 1 |\n")
    out = tmp_path / "out"
    prints = []
    for args in (["run", "--transcript", path, "--pin", str(size), "--label", "s", "--out", str(out),
                  "--turn-units", "stop", "prompt", "request"],
                 ["run", "--transcript", path, "--pin", str(size), "--label", "m", "--out", str(out),
                  "--thinking-size", "model"],
                 ["crosscheck", "--transcript", path, "--pin", str(size), "--audit", str(audit), "--out", str(out)],
                 ["summary", "--out", str(out), "--stamp", "fixed"]):
        done = subprocess.run([sys.executable, str(REPLAY), *args], capture_output=True, text=True, timeout=300)
        assert done.returncode == 0, done.stderr
        prints.append(done.stdout + done.stderr)
    files = sorted(out.iterdir())
    assert {f.name for f in files} == {"run-s.json", "run-m.json", "crosscheck.json", "SUMMARY.md"}
    blob = "\n".join(prints + [f.read_text() for f in files])
    assert v[:8] in (tmp_path / "t.jsonl").read_text()  # the control: the fixture does hold the value
    assert _hidden(v, blob)
    cells = json.loads((out / "run-s.json").read_text())["cells"]
    assert any(c["use_after_archive"]["archived_items"] for c in cells)  # the outputs did cover archived items


def test_no_piece_of_a_secret_reaches_a_round_two_output_or_print(tmp_path):
    """Round 2 reads more of each record (a hand-back's opening tag, an attachment's key field): none of it reaches
    an output. The secret sits in hand-backs, in attachment key fields (file names, paths) and in their bodies."""
    v = _secret()
    tx = Tx()
    _secret_fixture(tx, v)
    for j in range(12):
        tx.user(f"<task-notification> {v} " + TOKENS_1000, origin="task-notification")
        tx.attach({"type": "queued_command", "commandMode": "prompt", "prompt": AGENT_MESSAGE + v + TOKENS_1000})
        tx.user(f"a peer's report {v} " + TOKENS_1000, origin="peer", handback=True)
        tx.attach({"type": "edited_text_file", "filename": f"/w/{v}/{j % 3}.py", "snippet": f"{v} " + TOKENS_1000})
        tx.attach({"type": "nested_memory", "path": f"/w/{v}/CLAUDE.md", "content": {"content": f"{v} " + TOKENS_1000}})
        step(tx, 220000 + 3000 * j, f"later {v} " + TOKENS_1000, command=f"grep {v} /work")
    path, size = tx.write(tmp_path / "t.jsonl")
    out = tmp_path / "out"
    prints = []
    for args in (["run", "--grid", "r2", "--transcript", path, "--pin", str(size), "--label", "s", "--out", str(out)],
                 ["summary", "--out", str(out), "--stamp", "fixed"]):
        done = subprocess.run([sys.executable, str(REPLAY), *args], capture_output=True, text=True, timeout=300)
        assert done.returncode == 0, done.stderr
        prints.append(done.stdout + done.stderr)
    files = sorted(out.iterdir())
    assert {f.name for f in files} == {"run-s.json", "SUMMARY.md"}
    blob = "\n".join(prints + [f.read_text() for f in files])
    assert v[:8] in (tmp_path / "t.jsonl").read_text()  # the control: the fixture does hold the value
    assert _hidden(v, blob)
    result = json.loads((out / "run-s.json").read_text())
    rules = collections.Counter()
    for c in result["cells"]:
        rules.update(c["archived_items_by_rule"])
    assert rules["R5"] and rules["R6"]  # the outputs did cover items R5 and R6 archived
    assert result["recognition"]["r5_items"] >= 36


def _timeline_tokens(tl) -> set:
    seen = set()
    for segment in tl.segments:
        seen |= segment.fixed
        for it in segment.items:
            seen |= it.toks | it.stub_toks | ({it.text} if it.text else set())
    return seen


@pytest.mark.parametrize("where_planted, reaches", [("thinking", False), ("text", True)])
def test_a_thinking_blocks_text_never_enters_the_timeline(tmp_path, where_planted, reaches):
    """The brief's safety rule, as behavior: a token only a thinking block holds reaches no item's text, tokens or stub;
    the control plants it in a visible text block, where it must be found."""
    planted = "Zqthinkingonly" + secrets.token_hex(4)
    first = ({"type": "thinking", "thinking": f"private {planted}", "signature": "c2ln"} if where_planted == "thinking"
             else text(f"visible {planted}"))
    tx = Tx()
    tx.user("go")
    a = tx.tool_id()
    tx.request(20000, [first, call(a, "Bash", command="ls")], output=300, thinking=100)
    tx.results((a, "ok"))
    step(tx, 21000)
    tl, _ = _built(replay, tx, tmp_path)
    found = any(planted in t for t in _timeline_tokens(tl) if isinstance(t, str))
    assert found is reaches
    assert all(it.text is None for s in tl.segments for it in s.items if it.kind == "thinking")


# ---------------------------------------------------------------- determinism

def test_two_runs_write_identical_bytes(tmp_path):
    tx = Tx()
    _rich(tx)
    path, size = tx.write(tmp_path / "t.jsonl")
    outputs = []
    for n in (1, 2):
        out = tmp_path / f"out{n}"
        for args in (["run", "--transcript", path, "--pin", str(size), "--label", "d", "--out", str(out)],
                     ["summary", "--out", str(out), "--stamp", "fixed"]):
            done = subprocess.run([sys.executable, str(REPLAY), *args], capture_output=True, text=True, timeout=300)
            assert done.returncode == 0, done.stderr
        outputs.append(((out / "run-d.json").read_bytes(), (out / "SUMMARY.md").read_bytes()))
    assert outputs[0] == outputs[1]


# ---------------------------------------------------------------- the mutants

MUTANTS = {
    "age-boundary-off-by-one": ("not items[q].req < r - cell.age", "not items[q].req <= r - cell.age",
                                check_r3_age_boundary),
    "supersede-keeps-the-oldest": ("heapq.heappush(heap, older)", "heapq.heappush(heap, entered)", check_r1_supersede),
    "hysteresis-stops-at-B-not-L": ("target = cell.low", "target = cell.budget", check_hysteresis),
    "protected-set-ignored": ("protect_from = bisect.bisect_left(turn, cur - cell.k, 0, entered)",
                              "protect_from = entered", check_protected),
    "kept-item-check-dropped": ("kept = frozenset(t for t in item.toks if t in fixed or _visible(t, ix, archived, "
                                "stubs, entered, cache))", "kept = frozenset(t for t in item.toks if t in fixed)",
                                check_uaa_negative_control),
    "between-turn-fires-inside-a-turn": ('(cell.mode == "per-request" or turn_start)',
                                         '(cell.mode == "per-request" or True)', check_between_turn),
    "trim-fires-at-B-not-past-it": ("and active > cell.budget", "and active >= cell.budget", check_hysteresis),
    "stub-dropped-with-its-pair": ('stub = 0.0 if item.kind == "thinking" else stub_tokens', "stub = 0.0",
                                   check_stub_pair),
    "thinking-before-the-current-turn-ignored": ("protect_from = bisect.bisect_left(turn, cur - cell.k, 0, entered)",
                                                 "protect_from = bisect.bisect_left(turn, cur + 1, 0, entered)",
                                                 check_r2_thinking),
    # Round 2 (tasks/briefs/jev-trim/T0-REPLAY-R2-brief.md items 2-7).
    "check-points-follow-the-protection-unit": ('check_unit = "stop" if v2 else cell.unit', "check_unit = cell.unit",
                                                check_request_window_between_turn),
    "window-one-request-short": ("protect_from = bisect.bisect_left(turn, cur - cell.k, 0, entered)",
                                 "protect_from = bisect.bisect_left(turn, cur - cell.k + 1, 0, entered)",
                                 check_request_window_between_turn),
    "opening-group-not-protected": ("return item.start or _protected_kind_v2(item)", "return _protected_kind_v2(item)",
                                    check_opening_group),
    "record-reading-protects-the-group": (
        'return _protected_kind_v2_group if cell.opening == "group" else _protected_kind_v2',
        "return _protected_kind_v2_group", check_opening_record),
    "r5-envelope-anywhere": ("text.lstrip().startswith(ENVELOPES)", "any(e in text for e in ENVELOPES)", check_r5),
    "hand-back-protected-as-typed-text": ("((item.typed and not item.handback) or item.first_user",
                                          "(item.typed or item.first_user", check_r5),
    "r6-key-ignored": ("return (atype, value) if isinstance(value, str) else (atype,)", "return (atype,)", check_r6),
    "skill-body-not-protected": ('or item.name == "skill_body" or item.attach_type in SKILL_BODY_TYPES)',
                                 'or item.name == "skill_body")', check_r6),
    "reach-guard-never-blocks": ("probe.max_gain(protect_from, age_from) > target",
                                 'probe.max_gain(protect_from, age_from) > float("inf")', check_reach),
    "reach-probe-ignores-the-window": ("probe.max_gain(protect_from, age_from)", "probe.max_gain(entered, age_from)",
                                       check_reach),
    "cooldown-off-by-one": ("r - last_trim < cooldown", "r - last_trim <= cooldown", check_cooldown),
    "pessimistic-bound-uses-the-edit-point": ("sent - segment.fixed_start - request.write",
                                              "sent - prefix - request.write", check_pessimistic),
    "fixed-start-takes-the-larger-estimate": ("segment.fixed_start, segment.fixed_source = min(candidates)",
                                              "segment.fixed_start, segment.fixed_source = max(candidates)",
                                              check_fixed_start),
    "composition-before-trimming": ("mark is not None and mark[2] <= r_star", "mark is not None and False",
                                    check_composition),
}


def _load_mutant(source: str, where: Path, name: str):
    where.mkdir(parents=True, exist_ok=True)
    path = where / f"replay_{name.replace('-', '_')}.py"
    path.write_text(source)
    module_name = f"jev_trim_replay_mutant_{name.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module  # dataclasses resolve their module through sys.modules
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(module_name, None)
    return module


@pytest.mark.parametrize("name", sorted(MUTANTS))
def test_mutant_is_killed(name, tmp_path):
    old, new, check = MUTANTS[name]
    source = REPLAY.read_text()
    assert source.count(old) == 1, f"the anchor of mutant {name} must occur exactly once in replay.py"
    check(replay, tmp_path / "original")  # the unmutated file passes this check
    mutant = _load_mutant(source.replace(old, new), tmp_path / "mutant", name)
    with pytest.raises(AssertionError):
        check(mutant, tmp_path / "mutant-run")
