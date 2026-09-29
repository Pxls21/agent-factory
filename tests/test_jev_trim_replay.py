"""T0-REPLAY tests (task #346, D-105; tasks/briefs/jev-trim/T0-REPLAY-brief.md item 6). Deterministic and LLM-free.

Every transcript here is synthetic, built at run time in the production record shapes (the key sets of
tests/fixtures/jev_pipes/record_shapes.json, captured from the real transcript). Each scenario check is a plain function
of a module: it runs on scripts/jev_trim/replay.py (and must pass) and on each named mutant of that file
(test_mutant_is_killed: it must fail with an AssertionError). Expected values come from the fixtures' own numbers,
computed by hand in the checks, never from the code under test.
"""
from __future__ import annotations

import datetime
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
             new_prompt: bool = True) -> None:
        if new_prompt:
            self.prompt += 1
        record = self._base("user")
        record.update({"promptId": f"p{self.prompt}", "message": {"role": "user", "content": body}})
        if origin:
            record["origin"] = {"kind": origin}
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

    def boundary(self, summary: str = "a summary of the earlier work") -> None:
        record = self._base("system")
        record.update({"subtype": "compact_boundary", "content": "Conversation compacted", "level": "info",
                       "compactMetadata": {"trigger": "auto", "preTokens": 1, "postTokens": 1},
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


def test_no_piece_of_a_secret_reaches_any_output_or_print(tmp_path):
    v = _secret()
    tx = Tx()
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
