"""K1-COMPACTION-LOSS tests (task #352, D-106): round 1 (tasks/briefs/jev-trim/K1-COMPACTION-LOSS-brief.md items 2-6)
and round 2 (tasks/briefs/jev-trim/K1-R2-brief.md items 2-8). Deterministic and LLM-free.

Every transcript is synthetic, built at run time with the record builders of tests/test_jev_trim_replay.py (the
production record shapes). Each scenario check is a plain function of a module: it runs on
scripts/jev_trim/compaction.py (and must pass) and on each named mutant of that file (test_mutant_is_killed: it must
fail with an AssertionError). Expected values are the fixtures' own numbers, set by hand; the R-C checks are
differential (one planted token or call switched on at a time), so the incidental tokens of the fixture cancel. The
mutants are round 1's, VERIFY-K1's N01 to N22 (tasks/briefs/jev-trim/VERIFY-K1-report.md, item 6: one fixture case
per clause) and round 2's. VERIFY-K1's red tests R1 and R2 are at the end, as they are.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import math
import random
import secrets
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
TOOL = REPO / "scripts" / "jev_trim" / "compaction.py"
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from jev_pipes import accounting  # noqa: E402
from jev_trim import compaction, replay  # noqa: E402
from test_jev_trim_replay import TOKENS_1000, Tx, call, step  # noqa: E402
from test_jev_trim_replay import text as text_block  # noqa: E402


def result(tx: Tx, tid: str, body: str, *, error: bool = False) -> None:
    """A tool_result record (Tx.results writes is_error False only)."""
    record = tx._base("user")
    record.update({"promptId": f"p{tx.prompt}", "sourceToolAssistantUUID": "u00000",
                   "message": {"role": "user", "content": [
                       {"type": "tool_result", "tool_use_id": tid, "content": body, "is_error": error}]},
                   "toolUseResult": {"stdout": "", "stderr": "", "interrupted": False, "isImage": False,
                                     "noOutputExpected": False}})
    tx.add(record)


def tool(tx: Tx, context: int, name: str, body: str = "ok", *, error: bool = False, **tool_input) -> str:
    """One request making one call of `name`, and its result."""
    tid = tx.tool_id()
    tx.request(context, [call(tid, name, **tool_input)], output=10, thinking=0)
    result(tx, tid, body, error=error)
    return tid


def _built(tx: Tx, where: Path, *, sidechain: bool = False):
    path, size = tx.write(where / "t.jsonl")
    return path, size, replay.build(path, size, sidechain=sidechain)


# ---------------------------------------------------------------- R-C (round 1 item 3; round 2 F7)

LOST, KEPT, FRESH, LATE = "Zqlostbeta", "Zqkeptalpha", "Zqfreshgamma", "Zqlatedelta"
SNAP, TEXT_T, REL = "Zqsnapepsilon", "Zqtextzeta", "lib/core.py"
READ_PATH, READ_AGAIN, EDIT_PATH = "/w/lib/core.py", "/w/lib/other.py", "/w/ed/target.py"
THIRD_PATH = "/w/lib/third.py"  # read before and after the boundary, not re-injected
TASK_OUTPUT = "/tmp/claude-0/s/tasks/a1b2c3.output"


def _rc_fixture(tx: Tx, use: frozenset) -> None:
    """A pre segment that reads, edits, runs and plants tokens (SNAP is in the post segment's prompt_snapshot too, REL
    is READ_PATH's relative name, EDIT_PATH is read and edited); a compaction whose summary keeps KEPT and re-injects
    READ_AGAIN; a post segment whose first request uses the tokens named in `use` (TEXT_T in an assistant text), then
    one call of each re-fetch shape and a listing that matches only half a marker group, then LATE at post request 20
    (the 21st) when asked."""
    tx.user("go")
    tool(tx, 10000, "Read", f"{KEPT} {LOST} {LATE} {FRESH[:3]} {SNAP} {TEXT_T} {REL} body", file_path=READ_PATH)
    tool(tx, 10500, "Read", "other body", file_path=READ_AGAIN)
    tool(tx, 10600, "Read", "third body", file_path=THIRD_PATH)
    tool(tx, 10800, "Read", "target body", file_path=EDIT_PATH)
    tool(tx, 11000, "Edit", "ok", file_path=EDIT_PATH, old_string="a", new_string="b")
    step(tx, 12000, "built", command="make build")
    tool(tx, 13000, "ToolSearch", "found", query="select:Monitor")
    for j in range(3):
        step(tx, 14000 + j)
    tx.boundary(summary=f"summary keeps {KEPT}", post_tokens=500)
    tx.attach({"type": "prompt_snapshot", "content": f"the system prompt holds {SNAP}"})
    tx.attach({"type": "file", "filename": READ_AGAIN, "content": {"type": "text", "file": {"filePath": READ_AGAIN}}})
    words = [w for w in (LOST, KEPT, FRESH, READ_PATH, EDIT_PATH, SNAP, REL) if w in use]
    blocks = (text_block(f"recall {TEXT_T}"),) if TEXT_T in use else ()
    step(tx, 20000, command="echo " + " ".join(words) if words else "echo nothing", blocks=blocks)  # post request 0
    tool(tx, 20100, "Read", "other body", file_path=READ_AGAIN)  # read_known_path, re-injected
    step(tx, 20200, "built", command="make  build")  # rerun_command (whitespace folded)
    tool(tx, 20300, "ToolSearch", "found", query="select:Monitor")  # identical_other_call
    tool(tx, 20400, "Grep", "hit", pattern="x", path="/root/.claude/projects/s/t.jsonl")  # search_transcript
    tool(tx, 20500, "Read", "ledger", file_path="/w/todo/BUILD-TASKLIST.md")  # search_ledger
    step(tx, 20600, "state", command="cat wiki/topics/live-state.md")  # search_live_state
    tool(tx, 20650, "Read", "task out", file_path=TASK_OUTPUT)  # search_transcript: a group's two markers
    step(tx, 20660, "listing", command="ls /tmp/claude-0/s/tasks/")  # one marker of that group only: no shape
    tool(tx, 20670, "Read", "third again", file_path=THIRD_PATH)  # read_known_path, not re-injected
    tool(tx, 20700, "Read", "new", file_path="/w/new.py")  # no shape
    for j in range(9):  # post requests 11..19
        step(tx, 21000 + j)
    step(tx, 22000, command=f"echo {LATE}" if LATE in use else "echo late")  # post request 20
    for j in range(5):
        step(tx, 23000 + j)


def _rc(m, where: Path, use: frozenset = frozenset(), shape_set: str = "v2") -> dict:
    tx = Tx()
    _rc_fixture(tx, use)
    _, _, tl = _built(tx, where)
    (row,) = m.compaction_loss(tl, shape_set)["boundaries"]
    return row


def check_rc_miss(m, where: Path, shape_set: str = "v2") -> None:
    """A token of the pre segment the window used is missed unless the kept start or the history holds it."""
    base = _rc(m, where / "base", shape_set=shape_set)

    def delta(use: str, n: str, key: str = "missed") -> int:
        return _rc(m, where / use.strip("/").replace("/", "_"), frozenset({use}), shape_set)["windows"][n][key] - \
            base["windows"][n][key]

    assert delta(LOST, "20") == 1  # in the pre segment, not in the kept start: missed
    assert delta(KEPT, "20") == 0 and delta(KEPT, "20", "reused") == 1  # the summary keeps it: reused, not missed
    assert delta(FRESH, "20") == 0 and delta(FRESH, "20", "reused") == 0  # never before the boundary
    assert delta(LATE, "20") == 0  # used at post request 20: outside the first 20
    assert delta(LATE, "100") == 1 and delta(LATE, "rest") == 1
    assert delta(READ_PATH, "20", "missed_paths") == 1 and delta(READ_PATH, "20", "missed_paths_read_before") == 1
    assert delta(EDIT_PATH, "20", "missed_paths_edited_before") == 1
    assert delta(EDIT_PATH, "20", "missed_paths_read_before") == 0  # read and edited: counted as edited only (N04)
    assert delta(REL, "20", "missed_paths_read_before") == 1  # a relative path names the file it ends (N03)
    assert delta(SNAP, "20") == 0 and delta(SNAP, "20", "reused") == 0  # the prompt_snapshot holds it (N05, N06)
    assert delta(TEXT_T, "20") == 1  # used in an assistant text (N07)
    assert base["kept"]["files_reinjected"] == 1 and base["class"] == "200k_window"
    assert base["kept"]["post_tokens"] == 500  # the boundary record's postTokens (N21)


def check_rc_refetch(m, where: Path, shape_set: str = "v2") -> None:
    """Each re-fetch shape counted once, with the tokens and requests the calls cost."""
    tx = Tx()
    _rc_fixture(tx, frozenset())
    _, _, tl = _built(tx, where)
    (row,) = m.compaction_loss(tl, shape_set)["boundaries"]
    w = row["windows"]["20"]
    assert {s: v["calls"] for s, v in w["refetch"].items()} == {
        "read_known_path": 2, "rerun_command": 1, "identical_other_call": 1, "search_transcript": 2,
        "search_ledger": 1, "search_live_state": 1}  # the /tasks/ output read counts, the half-group listing not
    assert w["read_known_path_reinjected"] == 1  # READ_AGAIN only, not THIRD_PATH (N18)
    assert w["refetch_total"]["requests"] == 8
    post = tl.segments[1]
    calls = [it for it in post.items if it.kind == "tool_input"]
    counted = [calls[i] for i in (1, 2, 3, 4, 5, 6, 7, 9)]  # the eight re-fetch calls, in order
    assert [c.name for c in counted] == ["Read", "Bash", "ToolSearch", "Grep", "Read", "Bash", "Read", "Read"]
    results = {it.tool_use_id: it.size for it in post.items if it.kind == "tool_result"}
    assert w["refetch_total"]["tokens"] == pytest.approx(sum(c.size + results[c.tool_use_id] for c in counted), abs=0.2)


def check_miss_guard(m, where: Path) -> None:
    """The run stops when accounting.miss's count and the set disagree (the guard fires; the control is the plain
    run passing)."""
    tx = Tx()
    _rc_fixture(tx, frozenset({LOST}))
    _, _, tl = _built(tx, where)
    m.compaction_loss(tl)  # the control: agreement passes
    real = m.accounting.miss
    m.accounting.miss = lambda *a: (real(*a)[0] + 1, False)
    try:
        m.compaction_loss(tl)
    except AssertionError as err:
        assert "accounting.miss counted" in str(err)
    else:
        raise AssertionError("the guard did not fire on a disagreeing count")
    finally:
        m.accounting.miss = real


# ---------------------------------------------------------------- the control (round 1 item 4)

def _control_fixture(tx: Tx) -> None:
    tx.user("go")
    for j in range(250):  # segment 0: 250 requests; a command at request 10 runs again at request 130
        step(tx, 10000 + 10 * j, command="make test" if j in (10, 130) else None)
    tx.boundary()
    for j in range(199):  # segment 1: 199 requests, too short for a pseudo-boundary
        step(tx, 10000 + 10 * j)
    tx.boundary()
    for j in range(5):
        step(tx, 20000 + j)


def check_control(m, where: Path, shape_set: str = "v2") -> None:
    """A pseudo-boundary at the middle of each segment of 200+ requests; nothing removed, so no miss."""
    tx = Tx()
    _control_fixture(tx)
    _, _, tl = _built(tx, where)
    rc = m.compaction_loss(tl, shape_set)
    assert [(c["segment"], c["requests"], c["position"]) for c in rc["control"]] == [(0, 250, 125)]
    (point,) = rc["control"]
    assert all(w["missed"] == 0 for w in point["windows"].values())
    assert point["windows"]["20"]["refetch"]["rerun_command"]["calls"] == 1  # request 130 re-runs request 10's (N08)
    assert point["windows"]["20"]["reused"] > 0
    assert point["class"] == "200k_window"  # the segment ends in a compaction at 12,490 (N20)
    assert len(rc["boundaries"]) == 2


# ---------------------------------------------------------------- R-B (round 1 item 5; round 2 F7)

FUTURE_STAMP = "COMMIT BLOCKED by the future-stamp gate (rc=1) — paste the stamp from date -u or the commit clock."


def _quality_fixture(tx: Tx) -> None:
    tx.user("go")
    tool(tx, 50000, "Read", "a", file_path="/w/a.py")  # r0
    tool(tx, 60000, "Read", "a", file_path="/w/a.py")  # r1: a re-read, no edit between
    tool(tx, 70000, "Edit", "old_string not found", error=True, file_path="/w/a.py", old_string="x",
         new_string="y")  # r2: a failed edit (the file counts as changed, as the probe)
    tool(tx, 150000, "Read", "a", file_path="/w/a.py")  # r3: not a re-read (an edit between)
    tool(tx, 160000, "Bash", "make: failed", error=True, command="make x")  # r4: a tool error
    tool(tx, 170000, "Bash", "ok", command="make   x")  # r5: a re-run, no edit between (whitespace folded: N19)
    tool(tx, 250000, "Edit", "ok", file_path="/w/b.py", old_string="p", new_string="q")  # r6
    tool(tx, 260000, "Bash", "ok", command="make x")  # r7: not a re-run (an edit between)
    tool(tx, 270000, "Bash", "hooks ran\n" + FUTURE_STAMP, error=True, command="git commit -m y")  # r8: refused
    tool(tx, 280000, "Read", '   12\t  echo "' + FUTURE_STAMP + '"', file_path="/w/hook.sh")  # r9: the text, no refusal
    tool(tx, 290000, "Grep", "PreToolUse:Grep hook error: [x]: SEARCH INTERCEPT (search-intercept.py): this Grep was "
         "answered here and did NOT run", error=True, pattern="y")  # r10: the intercept
    tool(tx, 295000, "Bash", "SEARCH INTERCEPT (search-intercept.py) in a log", command="echo hi")  # r11: no error
    tx.boundary()  # a new segment: re-read and re-run state starts over (N09)
    tool(tx, 350000, "Read", "a", file_path="/w/a.py")  # r12: not a re-read of r3
    tool(tx, 355000, "Read", "a", file_path="/w/a.py", offset=10)  # r13: another offset, not a re-read (N12)
    tool(tx, 360000, "Bash", "ok", command="make x")  # r14: not a re-run of r7
    tx.request(365000, [call(tx.tool_id(), "Bash", command="echo s")], model="<synthetic>")  # not a request (N10)
    tx.request(370000, [call(tx.tool_id(), "Bash", command="echo o")], sidechain=not tx.side)  # other thread (N13)
    tid = tx.tool_id()
    tx.request(380000, [text_block("two records"), call(tid, "Bash", command="echo two")], output=10, thinking=0)
    record = json.loads(tx.lines[-1])  # r15: its later usage record says 480000; the first defines the fill (N11)
    record["message"]["usage"]["cache_read_input_tokens"] += 100000
    tx.lines[-1] = json.dumps(record)
    result(tx, tid, "ok")


def check_quality(m, where: Path) -> None:
    tx = Tx()
    _quality_fixture(tx)
    path, size = tx.write(where / "t.jsonl")
    q = m.quality(path, size)
    b0, b1, b2, b3 = (q["bins"][k] for k in ("0k-100k", "100k-200k", "200k-300k", "300k-400k"))
    assert (b0["requests"], b0["calls"], b0["errors"], b0["failed_edits"], b0["edits"], b0["reads"], b0["rereads"]) \
        == (3, 3, 1, 1, 1, 2, 1)
    assert (b1["calls"], b1["errors"], b1["reads"], b1["rereads"], b1["bash"], b1["reruns"]) == (3, 1, 1, 0, 2, 1)
    assert (b2["calls"], b2["errors"], b2["edits"], b2["failed_edits"], b2["bash"], b2["reruns"], b2["reads"],
            b2["rereads"]) == (6, 2, 1, 0, 3, 0, 1, 0)
    assert b2["refusals_by_gate"] == {"future_stamp": 1, "search_intercept": 1}
    assert b1["errors_by_tool"] == {"Bash": 1} and b2["errors_by_tool"] == {"Bash": 1, "Grep": 1}
    assert (b3["requests"], b3["calls"], b3["reads"], b3["rereads"], b3["bash"], b3["reruns"]) == (4, 4, 2, 0, 2, 0)
    assert "400k-500k" not in q["bins"]
    first, middle, last = (q["thirds"][t] for t in ("first", "middle", "last"))
    assert (first["calls"], first["errors"], first["rereads"]) == (6, 1, 1)  # r0-r3, then r12, r13
    assert (middle["calls"], middle["errors"], middle["reruns"]) == (5, 1, 1)  # r4-r7, then r14
    assert (last["calls"], last["errors"], sum(last["refusals_by_gate"].values())) == (5, 2, 2)  # r8-r11, then r15
    assert (q["calls"], q["calls_without_a_request"], q["requests"], q["segments_with_requests"]) == (16, 0, 16, 2)


# ---------------------------------------------------------------- the cost model (round 1 item 6)

def check_simulate(m, where: Path) -> None:
    # kept 100, steps of 10, X 125: fills 100 110 120 | 100 110 (the step to 130 is a compaction)
    got = m.simulate([10.0] * 4, 100.0, 125.0)
    assert (got["compactions"], got["requests"], got["mean_fill"]) == (1, 5, 108.0)
    assert (got["cache_read_tokens"], got["cache_write_tokens"], got["summarizer_read_tokens"]) == (310.0, 230.0, 120.0)
    # a fill equal to X is not past it: 100 110 120 | 100
    assert m.simulate([10.0] * 3, 100.0, 120.0)["mean_fill"] == 107.5
    # a negative step writes nothing: fills 100 110 105 115; writes 100 + 10 + 0 + 10 (N15)
    got = m.simulate([10.0, -5.0, 10.0], 100.0, 125.0)
    assert (got["compactions"], got["cache_read_tokens"], got["cache_write_tokens"]) == (0, 315.0, 120.0)


def _cost_fixture(tx: Tx) -> None:
    tx.user("go")
    for c in (100000, 250000, 450000):  # segment 0: a compaction at 450k, the 1M class: included, opens no boundary
        step(tx, c, TOKENS_1000)
    tx.boundary()
    for c in (100000, 200000, 300000):  # segment 1: a compaction at 300k, the 200k class: left out
        step(tx, c, TOKENS_1000)
    tx.boundary()
    for j in range(6):  # segment 2: 500k + 100k a request, then a compaction at 1M
        step(tx, 500000 + 100000 * j, TOKENS_1000)
    tx.boundary()
    for j in range(3):
        step(tx, 500000 + 100000 * j, TOKENS_1000)


def check_cost_model(m, where: Path) -> None:
    """The model leaves out segments that end in a compaction under CLASS_SPLIT, takes K from the included segments
    that open at a boundary, and multiplies the per-boundary means."""
    tx = Tx()
    _cost_fixture(tx)
    _, _, tl = _built(tx, where)
    rc = m.compaction_loss(tl)
    model = m.cost_model(tl, rc)
    assert model["included_segments"] == 3 and model["excluded_segments"] == [1]
    assert model["kept_start_mean"] == 500000.0  # segments 2 and 3, not segment 0's 100k (N22)
    assert model["observed_compactions_in_included"] == 2
    assert (model["steps"], model["negative_steps"]) == (11, 0)  # 2 + 1 + 5 + 1 + 2: a 0 step per compaction (N14)
    at = {row["X"]: row for row in model["rows"]}
    # from 500k: +150k +200k (past 700k) | 0 +100k +100k +100k (past) | +100k +100k 0 +100k (past) | +100k
    assert at[700_000]["compactions"] == 3
    mean = model["loss_means_per_boundary"]["20"]["real"]
    assert mean["boundaries"] == 2  # boundaries 1 and 3: the 1M class
    assert at[700_000]["loss"]["20"]["raw"]["missed"] == pytest.approx(round(3 * mean["missed"], 1))


def _excess_fixture(tx: Tx) -> None:
    tx.user("go")
    tool(tx, 400000, "Read", "k body", file_path="/w/k.py")  # pre request 0: a known file
    for j in range(1, 210):  # segment 0: 210 requests from 400k (the 1M class); request 110 re-runs request 10's
        step(tx, 400000 + 100 * j, command="make test" if j in (10, 110) else None)
    tx.boundary()
    for j in range(30):  # post requests 1-3 Read the known file again
        if j in (1, 2, 3):
            tool(tx, 100000 + 100 * j, "Read", "k body", file_path="/w/k.py")
        else:
            step(tx, 100000 + 100 * j)


def check_loss_excess(m, where: Path) -> None:
    """The excess is the real mean minus the control's (per boundary), and v2's is the rate's excess times the real
    window length: 3 real re-fetches in 20 requests against 1 at C1."""
    tx = Tx()
    _excess_fixture(tx)
    _, _, tl = _built(tx, where)
    rc = m.compaction_loss(tl)
    means = m._loss_means(rc)["20"]
    assert (means["real"]["refetch_calls"], means["control"]["refetch_calls"]) == (3, 1)
    assert means["excess"]["refetch_calls"] == 2  # real minus control, not plus (N16)
    assert m._loss_means_v2(rc)["20"]["refetch_total"]["C1"]["calls"] == 2.0


# ---------------------------------------------------------------- pins (round 1 item 2; round 2 F11)

def check_pins(m, where: Path) -> None:
    where.mkdir(parents=True, exist_ok=True)
    cut = where / "cut.jsonl"
    cut.write_bytes(b'{"a": 1}\n{"b": 2}\n{"c": ')
    assert m.pin_of(str(cut)) == len(b'{"a": 1}\n{"b": 2}\n')  # a cut record is not pinned
    whole = where / "whole.jsonl"
    whole.write_bytes(b'{"a": 1}\n')
    assert m.pin_of(str(whole)) == 9


def check_select(m, where: Path) -> None:
    subs = where / "subagents"
    subs.mkdir(parents=True, exist_ok=True)
    real, text, none, late = Tx(sidechain=True), Tx(sidechain=True), Tx(sidechain=True), Tx(sidechain=True)
    for tx in (real, text, none, late):
        tx.user("go", origin="coordinator")
        step(tx, 10000)
    real.boundary()
    late.boundary()
    real.lines = [line.replace('"isSidechain": false', '"isSidechain": true') for line in real.lines]
    late.lines = [line.replace('"isSidechain": false', '"isSidechain": true') for line in late.lines]
    text.user('a note quoting "subtype":"compact_boundary" in a text', origin="coordinator")
    sizes = []
    for name, tx in (("agent-real.jsonl", real), ("agent-text.jsonl", text), ("agent-none.jsonl", none)):
        _, size = tx.write(subs / name)
        sizes.append({"file": name, "pin": size})
    late.write(subs / "agent-late.jsonl")  # a boundary, but not measured at the start
    main = Tx()
    main.user("go")
    step(main, 10000)
    main_path, main_size = main.write(where / "main.jsonl")
    sizes.append({"file": "main.jsonl", "pin": main_size})
    got = m.select(main_path, str(subs), {s["file"]: s["pin"] for s in sizes})
    assert [(p["file"], p["role"], p["boundaries"]) for p in got["pins"]] == [
        ("main.jsonl", "main", 0), ("agent-real.jsonl", "subagent", 1)]
    assert got["not_pinned_with_a_boundary_now"] == ["agent-late.jsonl"]


def check_pin_guard(m, where: Path) -> None:
    """A pin beyond the file's size stops with PinBeyondFileSize; the file's own size runs (the control)."""
    tx = Tx()
    tx.user("go")
    step(tx, 10000)
    path, size = tx.write(where / "t.jsonl")
    assert m.run(path, size, "e", False)["pin"] == size
    try:
        m.run(path, size + 1, "e", False)
    except m.PinBeyondFileSize as err:
        assert f"{size + 1:,}" in str(err)
    else:
        raise AssertionError("a pin beyond the file's size ran")


# ---------------------------------------------------------------- round 2 item 4: reads apart from writes (F2)

DIRECTION_CASES = (
    ("cat todo/BUILD-TASKLIST.md", "read"),
    ("grep -n TASK todo/BUILD-TASKLIST.md | head -3", "read"),
    ("grep -c x todo/BUILD-TASKLIST.md > /dev/null 2>&1", "read"),
    ("sed -i 's/a/b/' todo/BUILD-TASKLIST.md", "write"),
    ("python3 scripts/anchor_edit.py todo/BUILD-TASKLIST.md --insert-after A B", "write"),
    ("echo x >> todo/BUILD-TASKLIST.md", "write"),
    ("cp /tmp/a todo/BUILD-TASKLIST.md", "write"),
    ("mv a b", "write"),
    ("printf x | tee -a wiki/topics/live-state.md", "write"),
    ("cat > /tmp/m.txt <<'EOF'\nthe ledger's line\nEOF", "write"),
    ("bash scripts/safe_commit.sh -m 'm' todo/BUILD-TASKLIST.md", "commit"),
    ("git add todo/BUILD-TASKLIST.md && git commit -m m", "commit"),
    ("scripts/push_clean.sh --no-delegates-live", "commit"),
    ("python3 scripts/chat_tail.py --n 5", "script"),
    ("python3 - <<'EOF'\nopen('todo/BUILD-TASKLIST.md', 'w').write('x')\nEOF", "script"),  # a heredoc body: not parsed
    ("cat <<'EOF'\nsed -i 's/a/b/' todo/BUILD-TASKLIST.md\nEOF", "read"),
    ("sed -n '1,5p' todo/BUILD-TASKLIST.md # a note: sed -i here would write", "read"),
    ("grep -n x todo/BUILD-TASKLIST.md \\\n  | head -3", "read"),
    ("git log --oneline -3 -- todo/BUILD-TASKLIST.md", "read"),
    ("cd /w && ls", "read"),
    ("echo hi", "other"),
)


def _r1_fixture(tx: Tx) -> None:
    """VERIFY-K1's R1 scenario: after the boundary, two edits, a commit and an anchor edit name the ledger or the
    live-state file; one grep reads the ledger."""
    tx.user("go")
    tool(tx, 10000, "Read", "a", file_path="/w/lib/a.py")
    for j in range(3):
        step(tx, 11000 + j)
    tx.boundary(summary="a summary", post_tokens=500)
    tool(tx, 20000, "Edit", "ok", file_path="/w/todo/BUILD-TASKLIST.md", old_string="a", new_string="b")
    step(tx, 20100, command="bash scripts/safe_commit.sh -m m todo/BUILD-TASKLIST.md")
    step(tx, 20200, command="python3 scripts/anchor_edit.py todo/BUILD-TASKLIST.md --insert-after A B")
    tool(tx, 20300, "Edit", "ok", file_path="/w/wiki/topics/live-state.md", old_string="a", new_string="b")
    step(tx, 20400, command="grep -n TASK todo/BUILD-TASKLIST.md")
    for j in range(4):
        step(tx, 21000 + j)


def check_direction(m, where: Path) -> None:
    """Each command's direction by the brief's rules; a search shape counts its reads only and reports the rest."""
    for command, want in DIRECTION_CASES:
        assert m._bash(command)[1] == want, command
    for name, want in (("Edit", "write"), ("Write", "write"), ("Read", "read"), ("Grep", "read"), ("Glob", "read"),
                       ("ToolSearch", "other")):
        assert m._direction(replay.Item(0, 0, 0, "tool_input", name, 2, 0, 0, text="{}")) == want, name
    tx = Tx()
    _r1_fixture(tx)
    _, _, tl = _built(tx, where)
    (row,) = m.compaction_loss(tl, "v2")["boundaries"]
    w = row["windows"]["20"]
    assert (w["refetch"]["search_ledger"]["calls"], w["refetch"]["search_live_state"]["calls"]) == (1, 0)
    assert w["directions"]["search_ledger"] == {"read": 1, "script": 0, "other": 0, "write": 2, "commit": 1}
    assert w["directions"]["search_live_state"] == {"read": 0, "script": 0, "other": 0, "write": 1, "commit": 0}
    assert w["refetch_total"]["calls"] == w["k1_total"]["calls"] == 1
    (v1_row,) = m.compaction_loss(tl, "v1")["boundaries"]  # the control: v1 counts the writes, as round 1
    assert v1_row["windows"]["20"]["refetch"]["search_ledger"]["calls"] == 4


# ---------------------------------------------------------------- round 2 item 5: the strict and loose shapes (F3)

def _strict_fixture(tx: Tx) -> None:
    tx.user("go")
    tool(tx, 10000, "Read", f"core {LOST} body", file_path=READ_PATH)  # read
    tool(tx, 10500, "Edit", "ok", file_path=EDIT_PATH, old_string="a", new_string="b")  # edited
    step(tx, 11000, "viewed", command="cat src/viewed.py")  # viewed through Bash, a relative name
    step(tx, 11500, "log", command="git log --oneline -5")
    step(tx, 12000, "blame", command=f"git blame -w {READ_PATH}")
    for j in range(3):
        step(tx, 13000 + j)
    tx.boundary(summary="a summary", post_tokens=500)
    step(tx, 20000, command=f"sed -n '1,40p' {READ_PATH}")  # (a) a view of a file read
    step(tx, 20100, command=f"head -n 5 {EDIT_PATH}")  # (a) of a file edited
    step(tx, 20200, command="tail -3 ./src/viewed.py")  # (a) of a file viewed, spelled with ./
    step(tx, 20300, command="cat /w/unknown.py")  # a view of an unknown file: none
    tool(tx, 20400, "Read", "viewed", file_path="/w/src/viewed.py")  # (b) a Read of a file viewed through Bash
    step(tx, 20500, command="git log --oneline -3")  # (c) the same non-flag arguments (none)
    step(tx, 20600, command=f"git blame {READ_PATH}")  # (c) the same subcommand and arguments
    step(tx, 20700, command="git log -3 scripts/other.py")  # other arguments: loose, git_any
    step(tx, 20800, command="git show HEAD")  # loose, git_any
    tool(tx, 20900, "Read", "core", file_path="/w/lib/./core.py")  # (d) a known file spelled another way
    tool(tx, 21000, "Grep", "hit", pattern=LOST)  # loose: a grep for a token of the pre segment
    step(tx, 21100, command="rg -n Zqnewtoken /w")  # a grep for a new token: none
    step(tx, 21200, command=f'graft ask "where is {LOST} set"')  # loose
    step(tx, 21300, command=f"sed -i 's/a/b/' {READ_PATH}")  # a write of a known file: none
    step(tx, 21400, command=f"cat {READ_PATH} > /tmp/copy")  # a view into a file is a write: none
    for j in range(4):
        step(tx, 22000 + j)


def check_strict_loose(m, where: Path) -> None:
    tx = Tx()
    _strict_fixture(tx)
    _, _, tl = _built(tx, where)
    (row,) = m.compaction_loss(tl, "v2")["boundaries"]
    w = row["windows"]["20"]
    assert {k: v["calls"] for k, v in w["strict"].items()} == {
        "bash_view_known_file": 3, "read_bash_viewed_file": 1, "git_repeated_args": 2, "read_known_path_respelled": 1}
    assert {k: v["calls"] for k, v in w["loose"].items()} == {"grep_known_token": 2, "git_any": 2}
    assert (w["k1_total"]["calls"], w["strict_total"]["calls"], w["refetch_total"]["calls"]) == (0, 7, 7)
    assert (w["loose_total"]["calls"], w["with_loose_total"]["calls"]) == (4, 11)  # loose: its own total


# ---------------------------------------------------------------- round 2 item 6: windows and controls

def _windows_fixture(tx: Tx) -> None:
    tx.user("go")
    tool(tx, 400000, "Read", "core body", file_path=READ_PATH)  # pre request 0
    for j in range(1, 210):  # segment 0: 210 requests from 400k (the 1M class); request 209 is its last
        step(tx, 400000 + 100 * j, command=f"cat {READ_PATH}" if j in (120, 209) else None)
    tx.boundary()
    views = {10: f"cat -n {READ_PATH}", 50: f"sed -n 1,5p {READ_PATH}", 125: f"head -3 {READ_PATH}"}
    for j in range(150):  # segment 1: 150 requests
        step(tx, 100000 + 100 * j, command=views.get(j))


def check_windows_controls(m, where: Path) -> None:
    """The 20-99 window; C1 at the middle; C2 PSEUDO_GAP requests before the compaction, the final request's call
    counted; C5 every 20 requests from request 100, whole windows only."""
    tx = Tx()
    _windows_fixture(tx)
    path, size = tx.write(where / "t.jsonl")
    tl, tails = m.timeline(path, size, False)
    rc = m.compaction_loss(tl, "v2", tails)

    def strict(windows: dict) -> dict:
        return {label: w["strict_total"]["calls"] for label, w in windows.items()}

    (real,) = rc["boundaries"]
    assert strict(real["windows"]) == {"20": 1, "20-99": 1, "100": 2, "rest": 3}
    assert real["windows"]["20-99"]["requests"] == 80
    (c1,) = rc["control"]
    assert (c1["segment"], c1["position"], strict(c1["windows"])) == (0, 105, {"20": 1, "20-99": 0, "100": 1,
                                                                               "rest": 1})
    (c2,) = rc["control_c2"]
    assert (c2["boundary"], c2["position"], c2["tail_calls"]) == (1, 110, 1)
    assert strict(c2["windows"]) == {"20": 1, "20-99": 1, "100": 2, "rest": 2}  # the last request's view counted
    assert [(p["segment"], p["position"], sorted(p["windows"])) for p in rc["control_c5"]] == [
        (0, 100, ["100", "20", "20-99"]), (0, 120, ["20"]), (0, 140, ["20"]), (0, 160, ["20"]), (0, 180, ["20"]),
        (1, 100, ["20"]), (1, 120, ["20"])]
    got = {(p["segment"], p["position"]): strict(p["windows"]) for p in rc["control_c5"]}
    assert got[(0, 100)] == {"20": 0, "20-99": 1, "100": 1} and got[(0, 120)] == {"20": 1}
    assert got[(1, 120)] == {"20": 1}  # the head at request 125, of a file viewed before the point
    (bare,) = m.compaction_loss(tl, "v2")["control_c2"]  # the control: no tails, the last request's view missing
    assert strict(bare["windows"])["100"] == 1


def check_bootstrap(m, where: Path) -> None:
    """The interval against an independent re-computation of the rule (random() from Random(seed), nearest rank)."""
    assert m._seed("x") == int(hashlib.sha256(b"x").hexdigest()[:16], 16)
    real, ctrl = [(0, 10), (3, 10), (1, 10), (5, 10)], [(1, 10), (0, 10), (2, 10)]

    def oracle(replicates: int, seed: int) -> tuple:
        rng = random.Random(seed)
        diffs = []
        for _ in range(replicates):
            r = [real[int(rng.random() * len(real))] for _ in real]
            c = [ctrl[int(rng.random() * len(ctrl))] for _ in ctrl]
            diffs.append(100 * sum(u[0] for u in r) / sum(u[1] for u in r) - 100 * sum(u[0] for u in c) /
                         sum(u[1] for u in c))
        diffs.sort()
        return diffs[math.ceil(0.025 * replicates) - 1], diffs[math.ceil(0.975 * replicates) - 1]

    assert m.bootstrap(real, ctrl, 500, 7) == oracle(500, 7)
    assert m.bootstrap(real, ctrl, 500, 7) != oracle(500, 8)  # the control: the seed matters
    assert m.bootstrap([(2, 20)] * 3, [(1, 20)] * 2, 200, 1) == (5.0, 5.0)  # no spread: the point estimate
    assert m.bootstrap([], ctrl, 10, 1) is None


# ---------------------------------------------------------------- round 2 item 7: the position-aware cost model (F5)

def check_position_model(m, where: Path) -> None:
    """Hand-computed: 24 steps, 20 of 10 (positions 0-19) and 4 of 5 (20-23); kept 100; X 250. A step takes the
    position of the request it leaves."""
    steps, positions = [10.0] * 20 + [5.0] * 4, list(range(24))
    means = m.growth_means(steps, positions)
    assert means == [10.0, 5.0, 5.0]  # the empty 100+ bucket takes the 20-99 mean
    assert m.growth_means([10.0, 0.0, 30.0], [0, -1, 0]) == [20.0, 20.0, 20.0]  # a step across a compaction: left out
    got = m.simulate_positions(steps, positions, 100.0, 250.0, means)
    # 100, +10 to 250 (steps 1-15, positions 0-14); step 16 passes 250: a compaction, back to 100 at position 0; steps
    # 17-20 +10 (positions 0-3); steps 21-24 are observed at 20-23 (g 5) but modeled at 4-7 (g 10): +10 each, to 180
    assert (got["compactions"], got["requests"], got["mean_fill"]) == (1, 25, 162.4)
    assert (got["cache_read_tokens"], got["cache_write_tokens"], got["summarizer_read_tokens"]) == (3630.0, 430.0, 250.0)
    assert m.simulate(steps, 100.0, 250.0)["mean_fill"] != got["mean_fill"]  # the control: the flat model differs
    assert m.calibrate(steps, positions, 100.0, 250.0, means, 1) == (1.0, 1, 1)
    scale, unscaled, scaled = m.calibrate(steps, positions, 100.0, 250.0, means, 2)
    assert (unscaled, scaled) == (1, 2) and 1.0 < scale < 2.0


def check_cost_model_v2(m, where: Path) -> None:
    tx = Tx()
    _cost_fixture(tx)
    _, _, tl = _built(tx, where)
    model = m.cost_model(tl, m.compaction_loss(tl, "v2"))
    assert model["growth_steps"] == {"0-19": 9, "20-99": 0, "100+": 0}
    assert model["growth_means"]["0-19"] == pytest.approx(1_050_000 / 9, abs=0.1)
    pa = model["position_aware"]
    # every step in bucket 0: unscaled, the flat stream, 3 compactions at 785k against 2 observed
    assert (pa["compactions_at_the_last_x_unscaled"], pa["compactions_at_the_last_x"], pa["target_compactions"]) \
        == (3, 2, 2)
    assert 0 < pa["scale"] < 1 and (pa["rows"][-1]["compactions"], pa["rows"][-1]["compactions_unscaled"]) == (2, 3)
    # the usage records: 12 included requests, each with 3 input tokens and the rest read from the cache
    assert model["actual_usage"] == {"requests": 12, "cache_read_tokens": 7_100_000 - 3 * 12, "cache_write_tokens": 0,
                                     "mean_context": 591666.7}
    loss = model["rows"][0]["loss_v2"]["20"]["refetch_total"]
    assert set(loss) == {"real", "C1", "C2", "C5"}


# ---------------------------------------------------------------- round 2 items 3 and 9: v1 stays round 1's bytes

GOLDEN_V1 = {  # captured from the committed round-1 code (compaction.py sha256 95e160625dd2cd10...) on _golden_fixture
    "run-g.json": "360a8c7c27c427555829de7c5a8cefda8e7bd631f459906c6b668691b6abd730",
    "SUMMARY.md": "99f455d625fc5692c2882eb8aee84d84bf1ccf0be4831831ce2490b503e1c439",
}


def _golden_fixture(tx: Tx) -> None:
    _rc_fixture(tx, frozenset({LOST, LATE, REL}))
    tx.boundary()
    for j in range(210):  # a long last segment: a control point
        step(tx, 30000 + 10 * j, command="make test" if j in (5, 120) else None)


def check_v1_golden(m, where: Path) -> None:
    """The command line without --shapes writes, byte for byte, what the round-1 code wrote."""
    tx = Tx()
    _golden_fixture(tx)
    path, size = tx.write(where / "t.jsonl")
    out = where / "out"
    for args, name in ((["run", "--transcript", path, "--pin", str(size), "--label", "g", "--out", str(out)],
                        "run-g.json"), (["summary", "--out", str(out), "--stamp", "fixed"], "SUMMARY.md")):
        assert m.main(args) == 0
        assert hashlib.sha256((out / name).read_bytes()).hexdigest() == GOLDEN_V1[name], name  # each as it is written


# ---------------------------------------------------------------- normal behavior

@pytest.mark.parametrize("shape_set", ["v1", "v2"])
def test_rc_counts_a_missed_token_only_when_the_kept_start_lacks_it(tmp_path, shape_set):
    check_rc_miss(compaction, tmp_path, shape_set)


@pytest.mark.parametrize("shape_set", ["v1", "v2"])
def test_rc_counts_each_refetch_shape_with_its_cost(tmp_path, shape_set):
    check_rc_refetch(compaction, tmp_path, shape_set)


def test_the_run_stops_when_accounting_miss_disagrees(tmp_path):
    check_miss_guard(compaction, tmp_path)


@pytest.mark.parametrize("shape_set", ["v1", "v2"])
def test_the_control_takes_the_middle_of_long_segments_and_misses_nothing(tmp_path, shape_set):
    check_control(compaction, tmp_path, shape_set)


def test_quality_signals_per_bin_and_third(tmp_path):
    check_quality(compaction, tmp_path)


def test_the_simulation_on_hand_computed_numbers(tmp_path):
    check_simulate(compaction, tmp_path)


def test_the_cost_model_leaves_out_the_small_window_and_scales_the_loss(tmp_path):
    check_cost_model(compaction, tmp_path)


def test_the_excess_is_the_real_mean_minus_the_control(tmp_path):
    check_loss_excess(compaction, tmp_path)


def test_a_pin_stops_at_a_record_boundary(tmp_path):
    check_pins(compaction, tmp_path)


def test_select_takes_parsed_boundaries_and_names_the_unpinned(tmp_path):
    check_select(compaction, tmp_path)


def test_a_search_counts_reads_and_reports_writes_and_commits(tmp_path):
    check_direction(compaction, tmp_path)


def test_the_strict_and_loose_shapes(tmp_path):
    check_strict_loose(compaction, tmp_path)


def test_the_windows_and_the_three_controls(tmp_path):
    check_windows_controls(compaction, tmp_path)


def test_the_bootstrap_interval(tmp_path):
    check_bootstrap(compaction, tmp_path)


def test_the_position_aware_model_on_hand_computed_numbers(tmp_path):
    check_position_model(compaction, tmp_path)


def test_the_position_aware_model_is_calibrated_and_the_usage_read(tmp_path):
    check_cost_model_v2(compaction, tmp_path)


def test_v1_writes_the_round_one_bytes(tmp_path):
    check_v1_golden(compaction, tmp_path)


def test_the_miss_set_is_accounting_miss_on_the_full_texts(tmp_path):
    """Why the set, not texts cut down to the used tokens: a non-ASCII letter after a path hides the path's inner
    identifier from the full text, and a cut text shows it again."""
    original, kept = "see x/abcdefé here", ""
    used = frozenset({"x/abcdef", "abcdef"})
    got = compaction._miss(accounting.tokens(original), accounting.tokens(kept), frozenset(), used, (original, kept))
    assert got == {"x/abcdef"}
    assert accounting.miss(original, kept, frozenset(), [used], [], None)[0] == 1
    assert accounting.miss("x/abcdef", "", frozenset(), [used], [], None)[0] == 2  # the cut text is not the same


def test_the_miss_on_real_items_equals_accounting_miss_on_their_texts(tmp_path):
    """The run's own check, on a fixture: the set over the items' tokens and accounting.miss on the joined texts."""
    tx = Tx()
    _rc_fixture(tx, frozenset({LOST, READ_PATH, KEPT}))
    _, _, tl = _built(tx, tmp_path)
    pre, post = tl.segments
    opening = [it for it in post.items if it.start]
    look, _, _ = compaction._window(post, 0, None)
    used = frozenset().union(*(it.toks for it in look))
    original = "\n".join(it.text for it in pre.items if it.text is not None)
    kept = "\n".join(it.text for it in opening if it.text is not None)
    got = compaction._miss(compaction.facts(pre.items).tokens, compaction.facts(opening).tokens, post.fixed, used)
    assert len(got) == accounting.miss(original, kept, post.fixed, [used], [], None)[0] > 0


def test_v2_runs_write_identical_bytes_and_a_summary_with_intervals(tmp_path):
    tx = Tx()
    _windows_fixture(tx)
    path, size = tx.write(tmp_path / "t.jsonl")
    digests = []
    for n in (1, 2):
        out = tmp_path / f"out{n}"
        for args in (["run", "--transcript", path, "--pin", str(size), "--label", "w", "--out", str(out), "--shapes",
                      "v2"], ["summary", "--out", str(out), "--stamp", "fixed"]):
            done = subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True, timeout=300)
            assert done.returncode == 0, done.stderr
        digests.append([hashlib.sha256((out / f).read_bytes()).hexdigest() for f in ("run-w.json", "SUMMARY.md")])
    assert digests[0] == digests[1]
    summary = (tmp_path / "out1" / "SUMMARY.md").read_text()
    assert summary.startswith("# K1 round 2 results")
    assert "| K1's + strict (refetch_total) | 20 | 5.00 (1; 20) | 5.00: +0.00 [" in summary
    assert json.loads((tmp_path / "out1" / "run-w.json").read_text())["schema"] == 2


# ---------------------------------------------------------------- failure behavior and the boundary

def test_a_boundary_without_requests_on_one_side_is_skipped(tmp_path):
    tx = Tx()
    tx.user("go")
    step(tx, 10000)
    tx.boundary()
    tx.boundary()  # an empty segment between two boundaries
    step(tx, 20000)
    _, _, tl = _built(tx, tmp_path)
    rc = compaction.compaction_loss(tl)
    assert [(s["boundary"], s["pre_has_requests"], s["post_has_requests"]) for s in rc["skipped"]] == [
        (1, True, False), (2, False, True)]
    assert rc["boundaries"] == [] and rc["control_c2"] == []


@pytest.mark.parametrize("shapes", ["v1", "v2"])
def test_a_transcript_with_no_requests(tmp_path, shapes):
    tx = Tx()
    tx.user("go")
    path, size = tx.write(tmp_path / "t.jsonl")
    out = tmp_path / "out"
    done = subprocess.run([sys.executable, str(TOOL), "run", "--transcript", path, "--pin", str(size), "--label", "e",
                           "--out", str(out), "--shapes", shapes], capture_output=True, text=True, timeout=120)
    assert done.returncode == 0, done.stderr
    result_ = json.loads((out / "run-e.json").read_text())
    assert result_["rc"]["boundaries"] == [] and result_["cost_model"]["rows"] == []
    summary = subprocess.run([sys.executable, str(TOOL), "summary", "--out", str(out), "--stamp", "fixed"],
                             capture_output=True, text=True, timeout=120)
    assert summary.returncode == 0 and "## Pins: NO pins.json" in (out / "SUMMARY.md").read_text()


def test_a_pin_beyond_the_file_stops_with_a_named_error(tmp_path):
    check_pin_guard(compaction, tmp_path)
    tx = Tx()
    tx.user("go")
    path, size = tx.write(tmp_path / "t.jsonl")
    out = tmp_path / "out"
    done = subprocess.run([sys.executable, str(TOOL), "run", "--transcript", path, "--pin", str(size + 1), "--label",
                           "e", "--out", str(out)], capture_output=True, text=True, timeout=120)
    assert done.returncode == 2 and "PinBeyondFileSize" in done.stderr and not (out / "run-e.json").exists()


def test_a_summary_refuses_a_directory_that_mixes_shape_sets(tmp_path):
    tx = Tx()
    _rc_fixture(tx, frozenset())
    path, size = tx.write(tmp_path / "t.jsonl")
    out = tmp_path / "out"
    for label, shapes in (("a", "v1"), ("b", "v2")):
        done = subprocess.run([sys.executable, str(TOOL), "run", "--transcript", path, "--pin", str(size), "--label",
                               label, "--out", str(out), "--shapes", shapes], capture_output=True, text=True,
                              timeout=120)
        assert done.returncode == 0, done.stderr
    done = subprocess.run([sys.executable, str(TOOL), "summary", "--out", str(out), "--stamp", "fixed"],
                          capture_output=True, text=True, timeout=120)
    assert done.returncode != 0 and "mixes v1 and v2 runs" in done.stderr


def _secret() -> str:
    return "tok-" + "Q".join(secrets.token_hex(2) for _ in range(8))


@pytest.mark.parametrize("shapes", ["v1", "v2"])
def test_no_piece_of_a_secret_reaches_any_output_or_print(tmp_path, shapes):
    v = _secret()
    tx = Tx()
    tx.user(f"my key is {v}")
    tool(tx, 10000, "Read", f"body {v} " + TOKENS_1000, file_path=f"/w/{v}/a.py")
    step(tx, 20000, f"out {v}", command=f"grep {v} /root/.claude/projects/x.jsonl")
    tool(tx, 30000, "Bash", f"COMMIT BLOCKED by the future-stamp gate {v}", error=True, command=f"git commit -m {v}")
    for j in range(4):
        step(tx, 40000 + j, f"more {v} " + TOKENS_1000)
    tx.boundary(summary=f"summary {v}")
    tx.attach({"type": "file", "filename": f"/w/{v}/a.py", "content": {"type": "text", "file": {"filePath": v}}})
    tool(tx, 50000, "Read", f"again {v}", file_path=f"/w/{v}/a.py")
    step(tx, 60000, f"x {v}", command=f"grep {v} /root/.claude/projects/x.jsonl")
    step(tx, 61000, f"y {v}", command=f"cat /w/{v}/a.py | head -3")
    for j in range(4):
        step(tx, 70000 + j, f"later {v}", command=f"echo {v} /w/{v}/a.py")
    path, size = tx.write(tmp_path / "t.jsonl")
    out = tmp_path / "out"
    prints = []
    for args in (["run", "--transcript", path, "--pin", str(size), "--label", "s", "--out", str(out), "--shapes",
                  shapes], ["summary", "--out", str(out), "--stamp", "fixed"]):
        done = subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True, timeout=300)
        assert done.returncode == 0, done.stderr
        prints.append(done.stdout + done.stderr)
    blob = "\n".join(prints + [f.read_text() for f in sorted(out.iterdir())])
    assert v[:8] in Path(path).read_text()  # the control: the fixture holds the value
    forms = {v, json.dumps(v)[1:-1]}
    assert not any(f[i:i + 8] in blob for f in forms for i in range(len(f) - 7))
    rc = json.loads((out / "run-s.json").read_text())["rc"]
    assert rc["boundaries"][0]["windows"]["rest"]["missed"] > 0  # the outputs covered a missed token
    assert rc["boundaries"][0]["windows"]["rest"]["refetch_total"]["calls"] >= 2


def test_the_summary_pools_the_subagent_runs(tmp_path):
    """Two sidechain runs: the summary pools their boundaries and sums their R-B tables key by key."""
    out = tmp_path / "out"
    tables = []
    for n in (1, 2):
        tx = Tx(sidechain=True)
        _quality_fixture(tx)
        path, size = tx.write(tmp_path / f"s{n}.jsonl")
        done = subprocess.run([sys.executable, str(TOOL), "run", "--transcript", path, "--pin", str(size), "--label",
                               f"sub-{n}", "--sidechain", "--out", str(out)], capture_output=True, text=True, timeout=120)
        assert done.returncode == 0, done.stderr
        tables.append(json.loads((out / f"run-sub-{n}.json").read_text())["quality"]["bins"])
    assert tables[0]["0k-100k"]["calls"] == 3  # the control: the sidechain thread was read
    pooled = compaction._pool(tables)
    assert pooled["200k-300k"]["calls"] == 12 and pooled["200k-300k"]["refusals_by_gate"] == {
        "future_stamp": 2, "search_intercept": 2}
    assert pooled["0k-100k"]["mean_fill"] == tables[0]["0k-100k"]["mean_fill"]
    done = subprocess.run([sys.executable, str(TOOL), "summary", "--out", str(out), "--stamp", "fixed"],
                          capture_output=True, text=True, timeout=120)
    assert done.returncode == 0, done.stderr
    assert "## Subagent files pooled: 2 files, 2 boundaries, 0 control points" in (out / "SUMMARY.md").read_text()


def test_two_runs_write_identical_bytes(tmp_path):
    tx = Tx()
    _rc_fixture(tx, frozenset({LOST, LATE}))
    path, size = tx.write(tmp_path / "t.jsonl")
    digests = []
    for n in (1, 2):
        out = tmp_path / f"out{n}"
        for args in (["run", "--transcript", path, "--pin", str(size), "--label", "d", "--out", str(out)],
                     ["summary", "--out", str(out), "--stamp", "fixed"]):
            done = subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True, timeout=300)
            assert done.returncode == 0, done.stderr
        digests.append([hashlib.sha256((out / f).read_bytes()).hexdigest() for f in ("run-d.json", "SUMMARY.md")])
    assert digests[0] == digests[1]


# ---------------------------------------------------------------- the mutants

MUTANTS = {
    # round 1
    "kept-start-ignored": ("opening = [it for it in post.items if it.start]", "opening = []", check_rc_miss),
    "window-one-request-long": ("end = len(offsets) if n is None else min(len(offsets), pos + n)",
                                "end = len(offsets) if n is None else min(len(offsets), pos + n + 1)", check_rc_miss),
    "read-shape-takes-any-read": ('if it.name == "Read" and _file_of(it) in (pre.reads | pre.edits):',
                                  'if it.name == "Read":', check_rc_refetch),
    "miss-check-dropped": ("if count != len(missed):", "if False:", check_miss_guard),
    "pseudo-gap-ignored": ("if n < 2 * PSEUDO_GAP:", "if n < 2:", check_control),
    "control-kept-is-empty": ("**measure(pre_facts.tokens, pre_facts.tokens, segment.fixed, look,",
                              "**measure(pre_facts.tokens, frozenset(), segment.fixed, look,", check_control),
    "reread-ignores-edits": ('reads[key] = "changed"', 'reads[key] = "clean"', check_quality),
    "rerun-ignores-edits": ('call["rerun"] = commands.get(key) == edits', 'call["rerun"] = key in commands',
                            check_quality),
    "gate-marker-anywhere": ('_GATE_RE = {gate: re.compile("(?m)^" + re.escape(marker))',
                             "_GATE_RE = {gate: re.compile(re.escape(marker))", check_quality),
    "error-gate-without-an-error": ('if rule == "error" and is_error and marker in text:',
                                    'if rule == "error" and marker in text:', check_quality),
    "compaction-at-X-not-past-it": ("if fill + step > point:", "if fill + step >= point:", check_simulate),
    "compaction-resets-to-zero": ("summarizer += fill\n            fill = float(kept)",
                                  "summarizer += fill\n            fill = 0.0", check_simulate),
    "small-window-segments-included": ('included = [s for s in tl.segments if _segment_class(tl, s) == "1M_window"]',
                                       "included = list(tl.segments)", check_cost_model),
    "pin-keeps-a-cut-record": ("return start + cut + 1", "return size", check_pins),
    "select-by-text-match": ('if record.get("type") == "system" and record.get("subtype") == "compact_boundary":\n'
                             "            count += 1",
                             'if "compact_boundary" in json.dumps(record):\n            count += 1', check_select),
    # VERIFY-K1's N01-N22 (its item 6), one per clause
    "N01-tasks-output-group-dropped": ('("/tasks/", ".output"), ', "", check_rc_refetch),
    "N02-a-group-matches-on-any-marker": ("if any(all(marker in text for marker in group) for group in groups):",
                                          "if any(any(marker in text for marker in group) for group in groups):",
                                          check_rc_refetch),
    "N03-no-relative-path-suffix": (
        'return any(f == token or (not token.startswith("/") and f.endswith("/" + token)) for f in files)',
        "return any(f == token for f in files)", check_rc_miss),
    "N04-read-before-takes-edited-paths": (
        "read = sum(1 for t in paths if not _names_file(t, pre.edits) and _names_file(t, pre.reads))",
        "read = sum(1 for t in paths if _names_file(t, pre.reads))", check_rc_miss),
    "N05-reused-ignores-history": ('"reused": len((original - history) & used)', '"reused": len(original & used)',
                                   check_rc_miss),
    "N06-miss-ignores-history": ("missed = set((original - kept - history) & used)",
                                 "missed = set((original - kept) & used)", check_rc_miss),
    "N07-look-without-assistant-text": ('LOOK_KINDS = frozenset({"tool_input", "assistant_text"})',
                                        'LOOK_KINDS = frozenset({"tool_input"})', check_rc_miss),
    "N08-control-history-takes-the-split-request": ("before = [it for it in segment.items if it.offset < split]",
                                                     "before = [it for it in segment.items if it.offset <= split]",
                                                     check_control),
    "N09-rb-state-kept-across-a-boundary": ("reads, commands, edits = {}, {}, 0",
                                            "reads, commands, edits = reads, commands, edits", check_quality),
    "N10-rb-keeps-synthetic-records": ('if message.get("model") == "<synthetic>":', "if False:", check_quality),
    "N11-rb-last-usage-record-defines-the-fill": ("if rid and rid not in requests and isinstance(usage, dict):",
                                                  "if rid and isinstance(usage, dict):", check_quality),
    "N12-reread-key-ignores-offset-and-limit": (
        'key = (tool_input.get("file_path"), tool_input.get("offset"), tool_input.get("limit"))',
        'key = (tool_input.get("file_path"), None, None)', check_quality),
    "N13-rb-reads-both-threads": ("for offset, record in transcript.iter_records(path, pin, stats):\n"
                                  '        side = record.get("isSidechain")\n'
                                  "        if isinstance(side, bool) and side is not sidechain:",
                                  "for offset, record in transcript.iter_records(path, pin, stats):\n"
                                  '        side = record.get("isSidechain")\n'
                                  "        if False:", check_quality),
    "N14-no-zero-step-across-a-compaction": ("steps.append(0.0)  # the step across an observed compaction",
                                             "pass  # the zero step dropped", check_cost_model),
    "N15-a-negative-step-writes": ("writes += max(0.0, step)", "writes += abs(step)", check_simulate),
    "N16-excess-is-real-plus-control": (
        'excess = {k: means["real"][k] - means["control"][k] for k in means["real"] if k != "boundaries"}',
        'excess = {k: means["real"][k] + means["control"][k] for k in means["real"] if k != "boundaries"}',
        check_loss_excess),
    "N17-thirds-reversed": ('third[rid] = ("first", "middle", "last")[i * 3 // len(rids)]',
                            'third[rid] = ("last", "middle", "first")[i * 3 // len(rids)]', check_quality),
    "N18-reinjected-takes-any-known-read": ('if shape == "read_known_path" and _file_of(it) in reinjected:',
                                            'if shape == "read_known_path":', check_rc_refetch),
    "N19-rb-rerun-without-whitespace-folding": ('key = transcript.rerun_key("Bash", tool_input)',
                                                'key = ("Bash", tool_input.get("command"))', check_quality),
    "N20-control-class-always-1m": ('"class": _segment_class(tl, segment), "windows": windows})',
                                    '"class": "1M_window", "windows": windows})', check_control),
    "N21-post-tokens-ignored": ('"post_tokens": _post_tokens(post),', '"post_tokens": None,', check_rc_miss),
    "N22-k-from-all-included-segments": ("starts = [s.requests[0].context for s in included if s.index >= 1]",
                                         "starts = [s.requests[0].context for s in included]", check_cost_model),
    # round 2: items 3 to 8
    "v2-search-counts-writes": ("return None  # a search counts reads only (F2)",
                                "pass  # a search counts reads only (F2)", check_direction),
    "v2-dev-null-is-a-write": ('if any(t != "/dev/null" for t in targets):', "if targets:", check_direction),
    "v2-heredoc-body-parsed": ("        if waiting:\n            delimiter, tabs = waiting[0]",
                               "        if False:\n            delimiter, tabs = waiting[0]", check_direction),
    "v2-comment-parsed": ('elif ch == "#" and prev in " \\t\\n;&|()":', "elif False:", check_direction),
    "v2-commit-scripts-unseen": ("if script.endswith(COMMIT_SCRIPTS):", "if False:", check_direction),
    "v2-view-takes-any-file": ("if _is_view(argv) and any(pre.known_files.has(f) for f in _view_files(argv)):",
                               "if _is_view(argv) and _view_files(argv):", check_strict_loose),
    "v2-git-args-ignored": ("if git is not None and git[0] in GIT_STRICT and git in pre.git:",
                            "if git is not None and git[0] in GIT_STRICT and any(k[0] == git[0] for k in pre.git):",
                            check_strict_loose),
    "v2-dot-slash-not-folded": ('while name.startswith("./"):\n        name = name[2:]',
                                "while False:\n        name = name[2:]", check_strict_loose),
    "v2-no-suffix-match": ('return absolute.endswith("/" + relative)', "return False", check_strict_loose),
    "v2-bash-views-not-collected": ("out.viewed.update(_view_files(argv))", "pass", check_strict_loose),
    "v2-loose-merged-into-refetch-total": ('"refetch_total": _total(k1 + strict),',
                                           '"refetch_total": _total(k1 + strict + loose),', check_strict_loose),
    "v2-grep-takes-any-pattern": ("if any(accounting.tokens(p) & pre.tokens for p in patterns):", "if patterns:",
                                  check_strict_loose),
    "v2-writes-reach-the-labels": ("        if direction in NOT_A_READ:\n            return None\n        label =",
                                   "        label =", check_strict_loose),
    "v2-c2-drops-the-tail": ('calls = calls + [it for it in tail if it.kind == "tool_input"]', "calls = calls",
                             check_windows_controls),
    "v2-c2-at-the-middle": ("point = _control_point(pre, len(pre.requests) - PSEUDO_GAP, results, tail, False)",
                            "point = _control_point(pre, len(pre.requests) // 2, results, tail, False)",
                            check_windows_controls),
    "v2-c5-keeps-clipped-windows": ("if whole and (length is None or pos + skip + length > n):",
                                    "if whole and length is None:", check_windows_controls),
    "v2-c5-from-request-0": ("positions = range(C5_START, n - C5_STEP + 1, C5_STEP)",
                             "positions = range(0, n - C5_STEP + 1, C5_STEP)", check_windows_controls),
    "v2-window-20-99-from-request-0": ("look, calls, length = _span(post, 0, 20, 80)",
                                       "look, calls, length = _span(post, 0, 0, 80)", check_windows_controls),
    "v2-bootstrap-seed-ignored": ("rng = random.Random(seed)", "rng = random.Random(0)", check_bootstrap),
    "v2-bootstrap-upper-rank-off": ("diffs[max(0, math.ceil(0.975 * len(diffs)) - 1)]",
                                    "diffs[max(0, math.ceil(0.95 * len(diffs)) - 1)]", check_bootstrap),
    "v2-position-never-resets": ("summarizer += fill\n            fill, m = float(kept), 0",
                                 "summarizer += fill\n            fill, m = float(kept), m", check_position_model),
    "v2-position-ratio-inverted": ("grown = scale * step * means[_bucket(m)] / means[_bucket(position)]",
                                   "grown = scale * step * means[_bucket(position)] / means[_bucket(m)]",
                                   check_position_model),
    "v2-calibration-skipped": ("    if first == target:\n        return 1.0, first, first",
                               "    if True:\n        return 1.0, first, first", check_cost_model_v2),
    "v2-actual-reads-are-contexts": ('"cache_read_tokens": sum(r.read for r in requests)',
                                     '"cache_read_tokens": sum(r.context for r in requests)', check_cost_model_v2),
    "v2-pin-guard-dropped": ("if pin > size:", "if False:", check_pin_guard),
    "v1-schema-is-2": ('"schema": 1 if shape_set == "v1" else 2', '"schema": 2', check_v1_golden),
    "v1-params-take-v2-keys": ('    if shape_set == "v2":\n        params.update(', '    if True:\n        params.update(',
                               check_v1_golden),
    "v1-cli-defaults-to-v2": ('choices=SHAPE_SETS, default="v1",', 'choices=SHAPE_SETS, default="v2",',
                              check_v1_golden),
}


def _load_mutant(source: str, where: Path, name: str):
    where.mkdir(parents=True, exist_ok=True)
    path = where / f"compaction_{name.replace('-', '_')}.py"
    path.write_text(source)
    module_name = f"jev_trim_compaction_mutant_{name.replace('-', '_')}"
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
    source = TOOL.read_text()
    assert source.count(old) == 1, f"the anchor of mutant {name} must occur exactly once in compaction.py"
    check(compaction, tmp_path / "original")  # the unmutated file passes this check
    mutant = _load_mutant(source.replace(old, new), tmp_path / "mutant", name)
    with pytest.raises(AssertionError):
        check(mutant, tmp_path / "mutant-run")


# ---------------------------------------------------------------- VERIFY-K1 red tests R1 and R2 (K1-R2 brief item 2)
# Copied as they are from tasks/briefs/jev-trim/VERIFY-K1-report.md, "Red tests and discriminator".

def _tool(tx, context, name, body="ok", **tool_input):
    tid = tx.tool_id(); tx.request(context, [call(tid, name, **tool_input)], output=10, thinking=0); tx.results((tid, body))

def test_a_write_is_not_a_search(tmp_path):                 # R1 (F2): committed -> (4, 1)
    tx = Tx(); tx.user("go"); _tool(tx, 10000, "Read", "a", file_path="/w/lib/a.py")
    for j in range(3): step(tx, 11000 + j)
    tx.boundary(summary="a summary", post_tokens=500)
    _tool(tx, 20000, "Edit", "ok", file_path="/w/todo/BUILD-TASKLIST.md", old_string="a", new_string="b")
    step(tx, 20100, command="bash scripts/safe_commit.sh -m m todo/BUILD-TASKLIST.md")
    step(tx, 20200, command="python3 scripts/anchor_edit.py todo/BUILD-TASKLIST.md --insert-after A B")
    _tool(tx, 20300, "Edit", "ok", file_path="/w/wiki/topics/live-state.md", old_string="a", new_string="b")
    step(tx, 20400, command="grep -n TASK todo/BUILD-TASKLIST.md")        # the only search
    for j in range(4): step(tx, 21000 + j)
    path, size = tx.write(tmp_path / "t.jsonl")
    (row,) = compaction.compaction_loss(replay.build(path, size))["boundaries"]
    w = row["windows"]["20"]["refetch"]
    assert (w["search_ledger"]["calls"], w["search_live_state"]["calls"]) == (1, 0)

def test_a_bash_view_of_a_file_read_before_is_a_refetch(tmp_path):   # R2 (F3, the amendment): committed -> 0
    tx = Tx(); tx.user("go"); _tool(tx, 10000, "Read", "body", file_path="/w/lib/core.py")
    step(tx, 10500, command="git log --oneline -5")
    for j in range(3): step(tx, 11000 + j)
    tx.boundary(summary="a summary", post_tokens=500)
    step(tx, 20000, command="sed -n '1,40p' /w/lib/core.py"); step(tx, 20100, command="git log --oneline -3")
    for j in range(4): step(tx, 21000 + j)
    path, size = tx.write(tmp_path / "t.jsonl")
    (row,) = compaction.compaction_loss(replay.build(path, size))["boundaries"]
    assert row["windows"]["20"]["refetch_total"]["calls"] == 2
