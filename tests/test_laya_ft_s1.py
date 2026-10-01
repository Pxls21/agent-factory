"""The Laya S1 dataset builder (task #438; tasks/laya-s3-breakdown.md): scripts/laya_ft/build_s1.py and the S1 parts of
scripts/laya_ft/common.py. A fixture session (a main thread and one lane) built in a temp folder; a fake window fit
(the real one needs the Laya venv and is K265's own test). The fake key is built at run time."""
import hashlib
import json
import secrets
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import hook_context as hc  # noqa: E402
from laya_ft import build_s1 as B  # noqa: E402
from laya_ft import common as C  # noqa: E402
from laya_ft import fit as FIT  # noqa: E402

SESSION = "sess-1"
CUTOFF = "2026-09-29T12:00:00.000Z"
FAKE = "fake-" + secrets.token_hex(16)
NO_J2 = {"v1": set(), "incident": set(), "v1_texts_scrubbed": set()}


class FakeFitter:
    """Fits every state whole, except a chunk over 700 characters (it overflows, as fit.py raises)."""
    fingerprint = {"fake": True, "max_len": 1024, "head_max_len": 256}

    def fit(self, state, question):
        assert question == C.S1_QUESTIONS["s1.inject"]
        if len(state["chunk"]) > 700:
            raise FIT.Unfit(state["chunk"], 0, 0)
        return state, []


class Session:
    """Writes a transcript the way Claude Code records it, and the hook wrapper's injections.jsonl."""

    def __init__(self, agent=None):
        self.agent, self.records, self.logged, self.minute = agent, [], [], 0

    def _t(self, hour):
        self.minute += 1
        return "2026-09-29T%02d:%02d:00.000Z" % (hour, self.minute)

    def _rec(self, hour, **kw):
        r = dict(kw, sessionId=SESSION, timestamp=self._t(hour))
        if self.agent:
            r["agentId"] = self.agent
        self.records.append(r)
        return r

    def prompt(self, hour, text):
        self._rec(hour, type="user", message={"role": "user", "content": text})

    def text(self, hour, text):
        self._rec(hour, type="assistant", message={"model": "m", "content": [{"type": "text", "text": text}]})

    def calls(self, hour, *calls):
        self._rec(hour, type="assistant", message={"model": "m", "content": [
            {"type": "tool_use", "id": tuid, "name": name, "input": inp} for tuid, name, inp in calls]})

    def inject(self, hour, sid, source, body, tuid=None, event="PreToolUse", tool="Bash", sha=None):
        stamped = hc.stamp(body, source, sid)
        self._rec(hour, type="attachment", attachment={
            "type": "hook_additional_context", "hookEvent": event, "hookName": "%s:%s" % (event, tool),
            "toolUseID": tuid, "content": [stamped]})
        self.logged.append({"id": sid, "session": SESSION, "source": source, "tool_use_id": tuid, "t": "x",
                            "sha256": sha or hashlib.sha256(stamped.encode("utf-8")).hexdigest()})

    def write(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(r) + "\n" for r in self.records), encoding="utf-8")


def fixture(tmp_path):
    """-> (main transcript path, jev folder). The rows each injection should give are in the tests below."""
    m = Session()
    m.prompt(10, "Make the widget export small.")
    m.text(10, "I read the widget first.")
    m.calls(10, ("tA", "Read", {"file_path": str(ROOT / "src" / "widget.py")}))
    m.inject(10, "s1-aaaa0001", "edit-snapshot", "EDIT SNAPSHOT · widget.py\nhistory: two changes", "tA",
             "PostToolUse", "Read")
    m.text(10, "S1-RATE s1-aaaa0001 rel=1 use=0 note: known\n\nNow the export command.")
    m.calls(10, ("tB", "Bash", {"command": "export OPENAI_API_KEY=%s; make widget" % FAKE}))
    m.inject(10, "s1-aaaa0002", "system1-context", "[system1 · build] skill build-loop, the lines:\nrun the gate", "tB")
    m.text(10, "S1-RATE s1-aaaa0002 rel=3 use=2\n\nDone with the build.")
    m.calls(10, ("tC", "Bash", {"command": "make test"}))
    m.inject(10, "s1-aaaa0003", "system1-context", "[system1 · test] skill build-loop", "tC", sha="0" * 64)
    m.text(10, "S1-RATE s1-aaaa0003 rel=2 use=1\n\nChecking twice.")
    m.calls(10, ("tD", "Bash", {"command": "ls"}), ("tE", "Bash", {"command": "ls"}))
    m.inject(10, "s1-aaaa0004", "system1-context", "[system1 · ls] the same lines", "tD")
    m.inject(10, "s1-aaaa0005", "system1-context", "[system1 · ls] the same lines", "tE")
    m.text(10, "S1-RATE s1-aaaa0004 rel=2 use=1\nS1-RATE s1-aaaa0005 rel=0 use=0 note: noise\n\nAgain twice.")
    m.calls(10, ("tF", "Bash", {"command": "pwd"}), ("tG", "Bash", {"command": "pwd"}))
    m.inject(10, "s1-aaaa0006", "system1-context", "[system1 · pwd] where am I", "tF")
    m.inject(10, "s1-aaaa0007", "system1-context", "[system1 · pwd] where am I", "tG")
    m.text(10, "S1-RATE s1-aaaa0006 rel=2 use=1\nS1-RATE s1-aaaa0007 rel=3 use=1\n\nA search.")
    m.calls(10, ("tK", "Grep", {"pattern": "widget", "path": str(ROOT / "src")}))
    m.inject(10, "s1-aaaa0012", "system1-context", "[system1 · grep] unrelated lines", "tK", tool="Grep")
    m.text(10, "S1-RATE s1-aaaa0012 rel=0 use=0 note: unrelated\n\nA long one.")
    m.calls(10, ("tL", "Bash", {"command": "cat big"}))
    m.inject(10, "s1-aaaa0013", "filepacks", "\n".join("line %03d of a big pack" % i for i in range(60)), "tL")
    m.text(10, "S1-RATE s1-aaaa0013 rel=2 use=1\n\nlater")
    # after the cutoff: the first state again (its label agrees), a prompt-time injection, an unscored one
    m.prompt(13, "Make the widget export small.")
    m.text(13, "I read the widget first.")
    m.calls(13, ("tH", "Read", {"file_path": str(ROOT / "src" / "widget.py")}))
    m.inject(13, "s1-aaaa0008", "edit-snapshot", "EDIT SNAPSHOT · widget.py\nhistory: two changes", "tH",
             "PostToolUse", "Read")
    m.text(13, "S1-RATE s1-aaaa0008 rel=1 use=0\n\nlater")
    m.prompt(13, "What is the plan?")
    m.inject(13, "s1-aaaa0009", "wiki-context", "wiki: the plan is X", event="UserPromptSubmit", tool="wiki")
    m.text(13, "S1-RATE s1-aaaa0009 rel=2 use=1\n\nThe plan.")
    m.calls(13, ("tM", "Bash", {"command": "true"}))
    m.inject(13, "s1-aaaa0011", "system1-context", "[system1 · x] never scored", "tM")
    m.text(13, "no score here")
    lane = Session(agent="x")
    lane.prompt(11, "Brief: fix the parser")
    lane.text(11, "Reading the parser.")
    lane.calls(11, ("tS", "Read", {"file_path": str(ROOT / "src" / "parser.py")}))
    lane.inject(11, "s1-aaaa0010", "edit-snapshot", "EDIT SNAPSHOT · parser.py", "tS", "PostToolUse", "Read")
    lane.text(11, "S1-RATE s1-aaaa0010 rel=2 use=2\n\nok")
    main = tmp_path / "proj" / "sess-1.jsonl"
    m.write(main)
    lane.write(tmp_path / "proj" / "sess-1" / "subagents" / "agent-x.jsonl")
    jev = tmp_path / "jev"
    jev.mkdir()
    (jev / "injections.jsonl").write_text("".join(json.dumps(r) + "\n" for r in m.logged + lane.logged),
                                          encoding="utf-8")
    return main, jev


@pytest.fixture
def built(tmp_path):
    main, jev = fixture(tmp_path)
    out = tmp_path / "out"
    summary = B.build([str(main)], str(jev), str(out), FakeFitter(), cutoff=CUTOFF)

    def split(name):
        rows, _manifest = C.load_dataset(out / name, heldout=NO_J2)
        labels, stats = C.read_labels(out / name / "labels.jsonl")
        joined = C.join_labels(rows, labels)
        assert stats == {"records": len(rows), "torn": 0, "duplicates": 0} and len(joined) == len(rows)
        return {s["id"]: (row, target) for row, target, _rec in joined for s in row["sources"]}
    return {"summary": summary, "out": out, "train": split("train"), "heldout": split("heldout"), "main": main,
            "jev": jev}


def test_every_scored_injection_is_built_or_counted_where_it_went(built):
    s = built["summary"]
    assert s["scored_injections"] == 12 and s["items"] == 11
    assert s["dropped"] == {"sha256_mismatch": 1}
    assert s["fit"] == {"unfit": 1, "cut_to_window": 0, "conflicting_states": 1, "cross_split_states": 1,
                        "merged_duplicates": 2}
    assert sorted(built["train"]) == ["s1-aaaa0002", "s1-aaaa0006", "s1-aaaa0007", "s1-aaaa0010", "s1-aaaa0012"]
    assert sorted(built["heldout"]) == ["s1-aaaa0001", "s1-aaaa0008", "s1-aaaa0009"]
    assert built["train"]["s1-aaaa0006"][0] is built["train"]["s1-aaaa0007"][0]   # one state, one row


def test_the_label_is_rel_two_or_more(built):
    target = {sid: t for d in (built["train"], built["heldout"]) for sid, (_row, t) in d.items()}
    assert target == {"s1-aaaa0002": [0.0, 1.0], "s1-aaaa0006": [0.0, 1.0], "s1-aaaa0007": [0.0, 1.0],
                      "s1-aaaa0010": [0.0, 1.0], "s1-aaaa0012": [1.0, 0.0], "s1-aaaa0001": [1.0, 0.0],
                      "s1-aaaa0008": [1.0, 0.0], "s1-aaaa0009": [0.0, 1.0]}


def test_the_state_carries_the_intent_without_any_score_line(built):
    bash = built["train"]["s1-aaaa0002"][0]["state"]
    assert bash == {"task": "Make the widget export small.", "intent": "Now the export command.",
                    "step": "Bash: export OPENAI_API_KEY=<redacted>; make widget", "kind": "skill lines",
                    "chunk": "[system1 · build] skill build-loop, the lines:\nrun the gate"}
    for d in (built["train"], built["heldout"]):
        for row, _t in d.values():
            assert "S1-RATE" not in json.dumps(row) and "rel=" not in json.dumps(row["state"])


def test_a_prompt_time_injection_and_a_lane_take_their_own_task(built):
    wiki = built["heldout"]["s1-aaaa0009"][0]["state"]
    assert wiki == {"task": "", "intent": "later", "step": "prompt: What is the plan?", "kind": "a wiki excerpt",
                    "chunk": "wiki: the plan is X"}
    lane = built["train"]["s1-aaaa0010"][0]["state"]
    assert (lane["task"], lane["intent"], lane["step"]) == ("Brief: fix the parser", "Reading the parser.",
                                                             "Read: src/parser.py")


def test_a_state_on_both_sides_is_held_out_only(built):
    row = built["heldout"]["s1-aaaa0001"][0]
    assert [s["id"] for s in row["sources"]] == ["s1-aaaa0001", "s1-aaaa0008"]
    assert row["state"]["step"] == "Read: src/widget.py"
    assert not {r["state_sha"] for r, _t in built["train"].values()} & {r["state_sha"] for r, _t in
                                                                         built["heldout"].values()}


def test_the_fake_key_is_in_no_output_byte(built):
    files = sorted(p for p in built["out"].rglob("*") if p.is_file())
    assert len(files) == 7
    for p in files:
        assert FAKE.encode() not in p.read_bytes(), p


def test_two_builds_are_byte_identical(built, tmp_path):
    again = tmp_path / "again"
    B.build([str(built["main"])], str(built["jev"]), str(again), FakeFitter(), cutoff=CUTOFF)
    for p in sorted(built["out"].rglob("*")):
        if p.is_file():
            assert p.read_bytes() == (again / p.relative_to(built["out"])).read_bytes(), p


def test_overlapping_paths_stop_the_build(built, tmp_path):
    folder = str(built["main"])[:-len(".jsonl")]
    with pytest.raises(SystemExit, match="read twice"):
        B.build([str(built["main"]), folder], str(built["jev"]), str(tmp_path / "o2"), FakeFitter(), cutoff=CUTOFF)


def test_the_cutoff_is_per_kind_when_none_is_given():
    items = [{"time": "t%d" % i, "state": {"kind": k}} for i, k in enumerate("aaaaab")]
    assert B.cutoffs_of(items, 0.2) == {"a": "t4", "b": "t5"}
    assert B.cutoffs_of(items, 0.2, cutoff="t3") == {"a": "t3", "b": "t3"}


def test_the_baselines_are_fitted_on_train_and_scored_on_heldout():
    def row(kind, chunk="c", step="s"):
        return {"state": {"kind": kind, "chunk": chunk, "step": step, "intent": ""}}
    train = [(row("a"), "true"), (row("a"), "true"), (row("b"), "false")]
    heldout = [(row("a"), "true"), (row("b"), "false"), (row("b"), "true"), (row("c"), "true")]
    b = B.baselines(train, heldout)
    assert b["always_true"] == 0.75 and b["majority"] == {"answer": "true", "accuracy": 0.75}
    assert b["kind_prior"] == {"rule": {"a": "true", "b": "false"}, "accuracy": 0.75}


def test_common_knows_the_injection_kind_and_still_refuses_an_unknown_one():
    assert C.row_identities({"item_id": "x", "sources": [{"kind": "injection", "id": "s1-1"}]}) == {
        ("injection", "s1-1")}
    with pytest.raises(C.DatasetError, match=r"^row x: unknown source kind 'transcript'$"):
        C.row_identities({"item_id": "x", "sources": [{"kind": "transcript"}]})
    assert "s1.inject" in C.ALL_QUESTIONS and "s1.inject" not in C.QUESTIONS   # the v1/v2 builders do not see it


def test_the_loader_refuses_an_s1_row_whose_question_text_drifted(built, tmp_path):
    d = tmp_path / "drift"
    d.mkdir()
    row = next(iter(built["train"].values()))[0]
    bad = dict(row, question=dict(row["question"], instructions="Is it relevant?"))
    data = (C.dumps(bad) + "\n").encode()
    (d / C.DATASET_FILE).write_bytes(data)
    (d / C.MANIFEST_FILE).write_text(json.dumps({"dataset": {"sha256": C.sha256_hex(data)},
                                                 "counts": {"rows_total": 1}}))
    with pytest.raises(C.DatasetError, match="the question is not this code's 's1.inject'"):
        C.load_dataset(d, heldout=NO_J2)
