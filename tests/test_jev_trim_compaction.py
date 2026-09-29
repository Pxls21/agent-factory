"""K1-COMPACTION-LOSS tests (task #352, D-106; tasks/briefs/jev-trim/K1-COMPACTION-LOSS-brief.md items 2-6).
Deterministic and LLM-free.

Every transcript is synthetic, built at run time with the record builders of tests/test_jev_trim_replay.py (the
production record shapes). Each scenario check is a plain function of a module: it runs on
scripts/jev_trim/compaction.py (and must pass) and on each named mutant of that file (test_mutant_is_killed: it must
fail with an AssertionError). Expected values are the fixtures' own numbers, set by hand; the R-C checks are
differential (one planted token or call switched on at a time), so the incidental tokens of the fixture cancel.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
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


# ---------------------------------------------------------------- R-C (item 3)

LOST, KEPT, FRESH, LATE = "Zqlostbeta", "Zqkeptalpha", "Zqfreshgamma", "Zqlatedelta"
READ_PATH, READ_AGAIN, EDIT_PATH = "/w/lib/core.py", "/w/lib/other.py", "/w/ed/target.py"


def _rc_fixture(tx: Tx, use: frozenset) -> None:
    """A pre segment that reads, edits, runs and plants tokens; a compaction whose summary keeps KEPT and re-injects
    READ_AGAIN; a post segment whose first request uses the tokens named in `use`, then one call of each re-fetch
    shape, then LATE at post request 20 (the 21st) when asked."""
    tx.user("go")
    tool(tx, 10000, "Read", f"{KEPT} {LOST} {LATE} {FRESH[:3]} body", file_path=READ_PATH)
    tool(tx, 10500, "Read", "other body", file_path=READ_AGAIN)
    tool(tx, 11000, "Edit", "ok", file_path=EDIT_PATH, old_string="a", new_string="b")
    step(tx, 12000, "built", command="make build")
    tool(tx, 13000, "ToolSearch", "found", query="select:Monitor")
    for j in range(3):
        step(tx, 14000 + j)
    tx.boundary(summary=f"summary keeps {KEPT}", post_tokens=500)
    tx.attach({"type": "file", "filename": READ_AGAIN, "content": {"type": "text", "file": {"filePath": READ_AGAIN}}})
    words = [w for w in (LOST, KEPT, FRESH, READ_PATH, EDIT_PATH) if w in use]
    step(tx, 20000, command="echo " + " ".join(words) if words else "echo nothing")  # post request 0
    tool(tx, 20100, "Read", "other body", file_path=READ_AGAIN)  # read_known_path, re-injected
    step(tx, 20200, "built", command="make  build")  # rerun_command (whitespace folded)
    tool(tx, 20300, "ToolSearch", "found", query="select:Monitor")  # identical_other_call
    tool(tx, 20400, "Grep", "hit", pattern="x", path="/root/.claude/projects/s/t.jsonl")  # search_transcript
    tool(tx, 20500, "Read", "ledger", file_path="/w/todo/BUILD-TASKLIST.md")  # search_ledger
    step(tx, 20600, "state", command="cat wiki/topics/live-state.md")  # search_live_state
    tool(tx, 20700, "Read", "new", file_path="/w/new.py")  # no shape
    for j in range(12):  # post requests 8..19
        step(tx, 21000 + j)
    step(tx, 22000, command=f"echo {LATE}" if LATE in use else "echo late")  # post request 20
    for j in range(5):
        step(tx, 23000 + j)


def _rc(m, where: Path, use: frozenset = frozenset()) -> dict:
    tx = Tx()
    _rc_fixture(tx, use)
    _, _, tl = _built(tx, where)
    (row,) = m.compaction_loss(tl)["boundaries"]
    return row


def check_rc_miss(m, where: Path) -> None:
    """Item 3: a token of the pre segment the window used is missed unless the kept start holds it."""
    base = _rc(m, where / "base")

    def delta(use: str, n: str, key: str = "missed") -> int:
        return _rc(m, where / use.strip("/").replace("/", "_"), frozenset({use}))["windows"][n][key] - \
            base["windows"][n][key]

    assert delta(LOST, "20") == 1  # in the pre segment, not in the kept start: missed
    assert delta(KEPT, "20") == 0 and delta(KEPT, "20", "reused") == 1  # the summary keeps it: reused, not missed
    assert delta(FRESH, "20") == 0 and delta(FRESH, "20", "reused") == 0  # never before the boundary
    assert delta(LATE, "20") == 0  # used at post request 20: outside the first 20
    assert delta(LATE, "100") == 1 and delta(LATE, "rest") == 1
    assert delta(READ_PATH, "20", "missed_paths") == 1 and delta(READ_PATH, "20", "missed_paths_read_before") == 1
    assert delta(EDIT_PATH, "20", "missed_paths_edited_before") == 1
    assert base["kept"]["files_reinjected"] == 1 and base["class"] == "200k_window"


def check_rc_refetch(m, where: Path) -> None:
    """Item 3: each re-fetch shape counted once, with the tokens and requests the calls cost."""
    tx = Tx()
    _rc_fixture(tx, frozenset())
    _, _, tl = _built(tx, where)
    (row,) = m.compaction_loss(tl)["boundaries"]
    w = row["windows"]["20"]
    assert {s: v["calls"] for s, v in w["refetch"].items()} == {
        "read_known_path": 1, "rerun_command": 1, "identical_other_call": 1, "search_transcript": 1,
        "search_ledger": 1, "search_live_state": 1}
    assert w["read_known_path_reinjected"] == 1 and w["refetch_total"]["requests"] == 6
    post = tl.segments[1]
    calls = [it for it in post.items if it.kind == "tool_input"][1:7]  # the six re-fetch calls, in order
    assert [c.name for c in calls] == ["Read", "Bash", "ToolSearch", "Grep", "Read", "Bash"]
    results = {it.tool_use_id: it.size for it in post.items if it.kind == "tool_result"}
    assert w["refetch_total"]["tokens"] == pytest.approx(sum(c.size + results[c.tool_use_id] for c in calls), abs=0.2)


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


# ---------------------------------------------------------------- the control (item 4)

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


def check_control(m, where: Path) -> None:
    """Item 4: a pseudo-boundary at the middle of each segment of 200+ requests; nothing removed, so no miss."""
    tx = Tx()
    _control_fixture(tx)
    _, _, tl = _built(tx, where)
    rc = m.compaction_loss(tl)
    assert [(c["segment"], c["requests"], c["position"]) for c in rc["control"]] == [(0, 250, 125)]
    (point,) = rc["control"]
    assert all(w["missed"] == 0 for w in point["windows"].values())
    assert point["windows"]["20"]["refetch"]["rerun_command"]["calls"] == 1  # request 130 re-runs request 10's
    assert point["windows"]["20"]["reused"] > 0
    assert len(rc["boundaries"]) == 2


# ---------------------------------------------------------------- R-B (item 5)

FUTURE_STAMP = "COMMIT BLOCKED by the future-stamp gate (rc=1) — paste the stamp from date -u or the commit clock."


def _quality_fixture(tx: Tx) -> None:
    tx.user("go")
    tool(tx, 50000, "Read", "a", file_path="/w/a.py")  # r0
    tool(tx, 60000, "Read", "a", file_path="/w/a.py")  # r1: a re-read, no edit between
    tool(tx, 70000, "Edit", "old_string not found", error=True, file_path="/w/a.py", old_string="x",
         new_string="y")  # r2: a failed edit (the file counts as changed, as the probe)
    tool(tx, 150000, "Read", "a", file_path="/w/a.py")  # r3: not a re-read (an edit between)
    tool(tx, 160000, "Bash", "make: failed", error=True, command="make x")  # r4: a tool error
    tool(tx, 170000, "Bash", "ok", command="make   x")  # r5: a re-run, no edit between
    tool(tx, 250000, "Edit", "ok", file_path="/w/b.py", old_string="p", new_string="q")  # r6
    tool(tx, 260000, "Bash", "ok", command="make x")  # r7: not a re-run (an edit between)
    tool(tx, 270000, "Bash", "hooks ran\n" + FUTURE_STAMP, error=True, command="git commit -m y")  # r8: refused
    tool(tx, 280000, "Read", '   12\t  echo "' + FUTURE_STAMP + '"', file_path="/w/hook.sh")  # r9: the text, no refusal
    tool(tx, 290000, "Grep", "PreToolUse:Grep hook error: [x]: SEARCH INTERCEPT (search-intercept.py): this Grep was "
         "answered here and did NOT run", error=True, pattern="y")  # r10: the intercept
    tool(tx, 295000, "Bash", "SEARCH INTERCEPT (search-intercept.py) in a log", command="echo hi")  # r11: no error


def check_quality(m, where: Path) -> None:
    tx = Tx()
    _quality_fixture(tx)
    path, size = tx.write(where / "t.jsonl")
    q = m.quality(path, size)
    b0, b1, b2 = (q["bins"][k] for k in ("0k-100k", "100k-200k", "200k-300k"))
    assert (b0["requests"], b0["calls"], b0["errors"], b0["failed_edits"], b0["edits"], b0["reads"], b0["rereads"]) \
        == (3, 3, 1, 1, 1, 2, 1)
    assert (b1["calls"], b1["errors"], b1["reads"], b1["rereads"], b1["bash"], b1["reruns"]) == (3, 1, 1, 0, 2, 1)
    assert (b2["calls"], b2["errors"], b2["edits"], b2["failed_edits"], b2["bash"], b2["reruns"], b2["reads"],
            b2["rereads"]) == (6, 2, 1, 0, 3, 0, 1, 0)
    assert b2["refusals_by_gate"] == {"future_stamp": 1, "search_intercept": 1}
    assert b1["errors_by_tool"] == {"Bash": 1} and b2["errors_by_tool"] == {"Bash": 1, "Grep": 1}
    first, middle, last = (q["thirds"][t] for t in ("first", "middle", "last"))
    assert (first["calls"], first["errors"], first["rereads"]) == (4, 1, 1)
    assert (middle["calls"], middle["errors"], middle["reruns"]) == (4, 1, 1)
    assert (last["calls"], last["errors"], sum(last["refusals_by_gate"].values())) == (4, 2, 2)
    assert q["calls_without_a_request"] == 0 and q["calls"] == 12


# ---------------------------------------------------------------- the cost model (item 6)

def check_simulate(m, where: Path) -> None:
    # kept 100, steps of 10, X 125: fills 100 110 120 | 100 110 (the step to 130 is a compaction)
    got = m.simulate([10.0] * 4, 100.0, 125.0)
    assert (got["compactions"], got["requests"], got["mean_fill"]) == (1, 5, 108.0)
    assert (got["cache_read_tokens"], got["cache_write_tokens"], got["summarizer_read_tokens"]) == (310.0, 230.0, 120.0)
    # a fill equal to X is not past it: 100 110 120 | 100
    assert m.simulate([10.0] * 3, 100.0, 120.0)["mean_fill"] == 107.5


def check_cost_model(m, where: Path) -> None:
    """The model leaves out segments that end in a compaction under CLASS_SPLIT and multiplies the per-boundary means."""
    tx = Tx()
    tx.user("go")
    for c in (100000, 200000, 300000):  # segment 0 ends in a compaction at 300k: the 200k-window class
        step(tx, c, TOKENS_1000)
    tx.boundary()
    for j in range(6):  # segment 1: 500k + 100k a request, then a compaction at 1M
        step(tx, 500000 + 100000 * j, TOKENS_1000)
    tx.boundary()
    for j in range(3):
        step(tx, 500000 + 100000 * j, TOKENS_1000)
    _, _, tl = _built(tx, where)
    rc = m.compaction_loss(tl)
    model = m.cost_model(tl, rc)
    assert model["included_segments"] == 2 and model["excluded_segments"] == [0]
    assert model["kept_start_mean"] == 500000.0 and model["observed_compactions_in_included"] == 1
    at = {row["X"]: row for row in model["rows"]}
    # steps 100k x5, 0 (the observed compaction), 100k x2 from 500k: past 700k after two steps each time
    assert at[700_000]["compactions"] == 2
    mean = model["loss_means_per_boundary"]["20"]["real"]
    assert mean["boundaries"] == 1  # the 1M_window boundary only
    assert at[700_000]["loss"]["20"]["raw"]["missed"] == pytest.approx(round(2 * mean["missed"], 1))


# ---------------------------------------------------------------- pins (item 2)

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


# ---------------------------------------------------------------- normal behavior

def test_rc_counts_a_missed_token_only_when_the_kept_start_lacks_it(tmp_path):
    check_rc_miss(compaction, tmp_path)


def test_rc_counts_each_refetch_shape_with_its_cost(tmp_path):
    check_rc_refetch(compaction, tmp_path)


def test_the_run_stops_when_accounting_miss_disagrees(tmp_path):
    check_miss_guard(compaction, tmp_path)


def test_the_control_takes_the_middle_of_long_segments_and_misses_nothing(tmp_path):
    check_control(compaction, tmp_path)


def test_quality_signals_per_bin_and_third(tmp_path):
    check_quality(compaction, tmp_path)


def test_the_simulation_on_hand_computed_numbers(tmp_path):
    check_simulate(compaction, tmp_path)


def test_the_cost_model_leaves_out_the_small_window_and_scales_the_loss(tmp_path):
    check_cost_model(compaction, tmp_path)


def test_a_pin_stops_at_a_record_boundary(tmp_path):
    check_pins(compaction, tmp_path)


def test_select_takes_parsed_boundaries_and_names_the_unpinned(tmp_path):
    check_select(compaction, tmp_path)


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
    assert rc["boundaries"] == []


def test_a_transcript_with_no_requests(tmp_path):
    tx = Tx()
    tx.user("go")
    path, size = tx.write(tmp_path / "t.jsonl")
    out = tmp_path / "out"
    done = subprocess.run([sys.executable, str(TOOL), "run", "--transcript", path, "--pin", str(size), "--label", "e",
                           "--out", str(out)], capture_output=True, text=True, timeout=120)
    assert done.returncode == 0, done.stderr
    result_ = json.loads((out / "run-e.json").read_text())
    assert result_["rc"]["boundaries"] == [] and result_["cost_model"]["rows"] == []
    summary = subprocess.run([sys.executable, str(TOOL), "summary", "--out", str(out), "--stamp", "fixed"],
                             capture_output=True, text=True, timeout=120)
    assert summary.returncode == 0 and "## Pins: NO pins.json" in (out / "SUMMARY.md").read_text()


def _secret() -> str:
    return "tok-" + "Q".join(secrets.token_hex(2) for _ in range(8))


def test_no_piece_of_a_secret_reaches_any_output_or_print(tmp_path):
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
    for j in range(4):
        step(tx, 70000 + j, f"later {v}", command=f"echo {v} /w/{v}/a.py")
    path, size = tx.write(tmp_path / "t.jsonl")
    out = tmp_path / "out"
    prints = []
    for args in (["run", "--transcript", path, "--pin", str(size), "--label", "s", "--out", str(out)],
                 ["summary", "--out", str(out), "--stamp", "fixed"]):
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
    assert "## Subagent files pooled: 2 files, 0 boundaries, 0 control points" in (out / "SUMMARY.md").read_text()


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
