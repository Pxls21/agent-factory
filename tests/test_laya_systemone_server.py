"""Tests for the local Laya System One endpoint (scripts/laya_systemone_server.py) and its per-chunk fit
(scripts/laya_ft/fit.py, the dataset builder's own fit; task #265, K265 contract rev 2).

Model-free, run everywhere: the device choice, the chunk map, the revision guard; the fit over a fake builder that keeps
one token per character (the real one's shape: a fixed frame, then the state cut to the window's room); the fan-out
through the real fit module over that fake builder, and the handler's 422. The states are compared by ORDER (their JSON
text or key list), never by dict equality: Laya serializes a state in key order and keeps only its first tokens
(`laya.common.build_sequence`, `st[:room]`), and a dict-equality test cannot see order (AF-AP-208).

In the Laya venv, as a subprocess: the real builder and tokenizer read the state the server builds (tokenizer only; the
model is never loaded). As in tests/test_laya_ft.py, the venv and the snapshot are declared inputs of the sandbox venue
(S0_01_VENUE, which scripts/test_summary.sh exports): elsewhere a LOUD SKIP; missing on the sandbox venue, a FAIL.
"""
from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
import io
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "laya_systemone_server.py"
SPEC = spec_from_file_location("laya_systemone_server_under_test", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
server = module_from_spec(SPEC)
sys.modules[SPEC.name] = server
SPEC.loader.exec_module(server)


MIB = 1024 * 1024
GIB = 1024 * MIB
LOW_FREE = 101 * MIB


@pytest.mark.parametrize(
    ("requested", "cuda_available", "free_bytes", "expected"),
    [
        ("auto", True, LOW_FREE, ("cpu", "auto: CUDA has 101 MiB free; need 3072 MiB")),
        ("auto", True, 8 * GIB, ("cuda", "auto: CUDA has 8192 MiB free")),
        ("auto", False, LOW_FREE, ("cpu", "auto: CUDA unavailable (101 MiB free; need 3072 MiB)")),
        ("auto", False, 8 * GIB, ("cpu", "auto: CUDA unavailable (8192 MiB free; need 3072 MiB)")),
        ("cuda", True, LOW_FREE, (None, "cuda requested but only 101 MiB free; need 3072 MiB")),
        ("cuda", True, 8 * GIB, ("cuda", "cuda requested with 8192 MiB free")),
        ("cuda", False, LOW_FREE, (None, "cuda requested but CUDA unavailable (101 MiB free; need 3072 MiB)")),
        ("cuda", False, 8 * GIB, (None, "cuda requested but CUDA unavailable (8192 MiB free; need 3072 MiB)")),
        ("cpu", True, LOW_FREE, ("cpu", "cpu explicitly requested")),
        ("cpu", True, 8 * GIB, ("cpu", "cpu explicitly requested")),
        ("cpu", False, LOW_FREE, ("cpu", "cpu explicitly requested")),
        ("cpu", False, 8 * GIB, ("cpu", "cpu explicitly requested")),
    ],
)
def test_pick_device_matrix(requested, cuda_available, free_bytes, expected):
    assert server._pick_device(requested, cuda_available, free_bytes) == expected


def test_chunk_map_accepts_only_a_complete_chunk_list():
    assert server._chunk_map({"chunks": [{"id": "c1", "text": "first"}, {"id": "c2", "text": "second"}]}) == {
        "c1": "first",
        "c2": "second",
    }
    assert server._chunk_map({"chunks": {"id": "c1", "text": "first"}}) is None
    assert server._chunk_map({"chunks": [{"id": "c1"}]}) is None


# ---------- the fakes: a builder that keeps one token per character, an agent that records its forward pass ----------

class FakeTok:
    """One token per character, called the way laya.common.build_sequence calls a tokenizer."""

    mask_token = "[MASK]"

    def __call__(self, text, add_special_tokens=False):
        return {"input_ids": [ord(c) for c in text]}


class FakeCommon:
    """The two names the fit reads from laya.common. build_sequence: a fixed 5-token frame, then the state's tokens cut
    to the room left in max_len (`st[:room]`, as the real one does), then [SEP]; each call lands in `events`."""

    def __init__(self, events):
        self.events = events

    @staticmethod
    def serialize_state(state):
        return state if isinstance(state, str) else json.dumps(state, ensure_ascii=False)

    def build_sequence(self, tok, state, q, max_len=512, head_max_len=192):
        self.events.append(("build", self.serialize_state(state), q, max_len, head_max_len))
        frame = [1, 2, 3, 4, 3]   # [CLS] head [SEP] [MASK]option [SEP]
        room = max(0, max_len - len(frame) - 1)
        st = tok(self.serialize_state(state).replace(tok.mask_token, " "), add_special_tokens=False)["input_ids"]
        return (frame + st[:room] + [3])[:max_len], [3]


class Recorder:
    """A fake agent: its forward pass recorded (also in `events`), plus the tokenizer and window the fit reads.
    FakeTok with max_len 80 keeps 74 state tokens (one per character of the state's JSON)."""

    def __init__(self, events):
        self.events, self.calls = events, []
        self.tok, self.cfg = FakeTok(), {"max_len": 80, "head_max_len": 8}

    @staticmethod
    def _to_internal(qdef):   # the shape of laya.agent.Agent._to_internal
        return {"t": qdef["type"], "ins": qdef["instructions"], "crit": qdef.get("criteria")}

    def system_one(self, state, questions):
        question_id = next(iter(questions))
        self.events.append(("ask", question_id))
        self.calls.append((deepcopy(state), deepcopy(questions)))
        return {
            "model": "recorder",
            "answers": {question_id: {"type": "noul", "noul": 0.5}},
            "usage": {"input_tokens": 1, "output_tokens": 0},
        }


@pytest.fixture
def fitmod(monkeypatch):
    """scripts/laya_ft/fit.py (the module the server imports) over FakeCommon; -> (module, events)."""
    monkeypatch.syspath_prepend(str(SCRIPT.parent))
    from laya_ft import fit
    events = []
    common = FakeCommon(events)
    monkeypatch.setattr(fit, "_laya_builder", lambda: (common.build_sequence, common.serialize_state))
    return fit, events


@pytest.fixture
def fake(monkeypatch, fitmod):
    """The server over a Recorder agent and the real fit module on FakeCommon; -> (agent, events)."""
    _fit, events = fitmod
    agent = Recorder(events)
    monkeypatch.setattr(server.State, "agent", agent)
    monkeypatch.setattr(server.State, "calls", 0)
    return agent, events


Q = {"t": "noul", "ins": "keep?", "crit": None}   # an internal question: its text is FakeCommon's fixed frame


def _fit(fit, state, max_len=80):
    return fit.fit_state(FakeTok(), Q, max_len, 8, state)


# ---------- the fit (scripts/laya_ft/fit.py) over the fake builder ----------

def test_fit_returns_a_state_that_fits_as_it_came(fitmod):
    fit, _ = fitmod
    state = {"task": "t", "chunk": "c"}
    out, cuts = _fit(fit, state)
    assert out is state and cuts == []


def test_fit_cuts_the_longest_field_first_a_list_by_whole_entries_and_keeps_the_order(fitmod):
    fit, _ = fitmod
    state = {"context": "ctx", "history": ["aaaaa", "bbbbb", "ccccc", "ddddd"], "chunk": "CHUNK"}   # 85 characters
    out, cuts = _fit(fit, state, max_len=64)   # 58 kept
    assert json.dumps(out) == '{"context": "ctx", "history": ["aaaaa"], "chunk": "CHUNK"}'
    assert cuts == [("history", 4, 1)]
    assert state["history"] == ["aaaaa", "bbbbb", "ccccc", "ddddd"]   # the caller's state is not changed


def test_fit_empties_a_field_that_cannot_absorb_the_cut_then_cuts_the_next_by_characters(fitmod):
    fit, _ = fitmod
    state = {"context": "ctx-0123456789", "history": ["aaaaa", "bbbbb", "ccccc", "ddddd"], "chunk": "CHUNK"}
    out, cuts = _fit(fit, state, max_len=64)
    assert json.dumps(out) == '{"context": "ctx-012345", "history": [], "chunk": "CHUNK"}'
    assert cuts == [("history", 4, 0), ("context", 14, 10)]


def test_fit_breaks_a_tie_in_the_request_order(fitmod):
    fit, _ = fitmod
    for first, second in (("aa", "zz"), ("zz", "aa")):   # equal lengths: the first in the request is cut, either name
        out, cuts = _fit(fit, {first: "x" * 20, second: "y" * 20, "chunk": "CHUNK"}, max_len=64)   # 78 -> 58 kept
        assert json.dumps(out) == '{"%s": "", "%s": "%s", "chunk": "CHUNK"}' % (first, second, "y" * 20)
        assert cuts == [(first, 20, 0)]


def test_fit_measures_a_value_by_its_json_as_laya_writes_it_without_the_key(fitmod):
    fit, _ = fitmod
    e5 = chr(0xE9) * 5   # 7 characters as Laya writes it (ensure_ascii=False); 32 escaped, 28 with its long key
    out, cuts = _fit(fit, {"accented_long_key": e5, "xs": "x" * 10, "chunk": "CHUNK"}, max_len=70)   # 68 -> 64 kept
    assert json.dumps(out, ensure_ascii=False) == '{"accented_long_key": "%s", "xs": "xxxxxx", "chunk": "CHUNK"}' % e5
    assert cuts == [("xs", 10, 6)]   # "xs" (12) is the longer value: cut first


def test_fit_keeps_a_field_that_is_neither_a_string_nor_a_list_whole(fitmod):
    fit, _ = fitmod
    out, cuts = _fit(fit, {"meta": {"k": "v"}, "n": 7, "history": ["aaaaa", "bbbbb"], "chunk": "C"}, max_len=64)
    assert json.dumps(out) == '{"meta": {"k": "v"}, "n": 7, "history": [], "chunk": "C"}'
    assert cuts == [("history", 2, 0)]
    with pytest.raises(fit.Unfit) as refused:   # the cut reaches the dict: kept whole, so the request is refused
        _fit(fit, {"meta": {"k": "v"}, "history": ["aaaaa"], "chunk": "C" * 40}, max_len=64)
    assert (refused.value.kept, refused.value.own) == (58, 88)


def test_fit_cuts_the_dataset_shapes_a_text_and_a_query(fitmod):
    fit, _ = fitmod
    assert _fit(fit, "s" * 100, max_len=64) == ("s" * 58, [(None, 100, 58)])
    out, cuts = _fit(fit, {"query": "q" * 50, "chunk": "row"}, max_len=64)
    assert json.dumps(out) == '{"query": "%s", "chunk": "row"}' % ("q" * 29) and cuts == [("query", 50, 29)]


def test_fit_never_cuts_the_chunk_and_refuses_one_that_does_not_fit_with_every_other_field_empty(fitmod):
    fit, _ = fitmod
    state = {"task": "t", "chunk": "C" * 60}   # {"task": "", "chunk": "CCC..."} is 85 characters; 58 kept
    before = json.dumps(state)
    with pytest.raises(fit.Unfit) as refused:
        _fit(fit, state, max_len=64)
    assert isinstance(refused.value, ValueError)   # the dataset builder's error type is kept
    assert str(refused.value) == "the chunk alone overflows Laya's window: %r" % ("C" * 60,)
    assert (refused.value.kept, refused.value.own) == (58, 85)
    assert json.dumps(state) == before


def test_fit_blanks_the_mask_token_and_counts_characters_as_laya_writes_them(fitmod):
    fit, _ = fitmod
    state = {"history": ["aaaaa"], "chunk": "é [MASK]"}   # 43 characters as Laya writes it, 38 once [MASK]
    out, cuts = _fit(fit, state, max_len=46)   # reads as one space; 40 kept: it fits only so (an escaped é adds 5)
    assert out is state and cuts == []


# ---------- the fan-out through the real fit module (on the fake builder) ----------

def test_answer_fans_out_each_named_chunk_without_reusing_batch_state(fake):
    agent, events = fake
    state = {
        "context": "ctx",
        "history": ["aaaaa", "bbbbb", "ccccc", "ddddd"],
        "task": "go",
        "chunks": [{"id": "c1", "text": "C1"}, {"id": "c2", "text": "é [MASK]"}],
    }
    questions = {
        "c1": {"type": "noul", "instructions": "keep c1?"},
        "c2": {"type": "noul", "instructions": "keep c2?"},
    }

    result = server._answer(state, questions)

    assert result["answers"] == {
        "c1": {"type": "noul", "noul": 0.5},
        "c2": {"type": "noul", "noul": 0.5},
    }
    assert result["usage"] == {"input_tokens": 2, "output_tokens": 0}
    assert result["fan_out"] == 2
    # the order the model reads is the training shape (the fields, then `chunk` last), and it reads it FITTED: each
    # state alone would be 96 characters against 74 kept, so the history lost its tail entries, whole ones
    assert [json.dumps(sent, ensure_ascii=False) for sent, _ in agent.calls] == [
        '{"context": "ctx", "history": ["aaaaa"], "task": "go", "chunk": "C1"}',
        '{"context": "ctx", "history": ["aaaaa"], "task": "go", "chunk": "é [MASK]"}',
    ]
    assert [asked for _, asked in agent.calls] == [{"c1": questions["c1"]}, {"c2": questions["c2"]}]
    # every per-chunk state is fitted, under its own question, before the model is asked about any chunk
    kinds = [e[0] for e in events]
    assert kinds.index("ask") > max(i for i, kind in enumerate(kinds) if kind == "build")
    assert {json.dumps(e[2]) for e in events if e[0] == "build"} == {
        json.dumps(agent._to_internal(questions["c1"])), json.dumps(agent._to_internal(questions["c2"]))}


def test_answer_falls_back_once_for_a_question_without_a_matching_chunk(fake):
    agent, events = fake
    state = {"history": [{"i": 0, "text": "a long segment of the conversation"}], "context": "agent-factory",
             "chunks": [{"id": "c1", "text": "routine output"}]}
    questions = {"not-a-chunk": {"type": "noul", "instructions": "keep?"}}

    result = server._answer(state, questions)
    server._answer("a plain text state", questions)

    assert "fan_out" not in result
    # the one-call path hands the model the request's state as it came: the same bytes, the same key order
    assert [(json.dumps(sent), asked) for sent, asked in agent.calls] == [
        (json.dumps(state), questions), (json.dumps("a plain text state"), questions)]
    assert [e[0] for e in events] == ["ask", "ask"]   # and fits nothing


REFUSED = ("chunk 'c2' does not fit Laya's window with every other field empty: 74 of its 106 state tokens kept; "
           "no chunk was asked")


def _over_request():
    """c2 does not fit even as {"task": "", "chunk": "xxx..."} (106 characters; 74 kept); c1 and c3 fit."""
    return ({"task": "run tests", "chunks": [{"id": "c1", "text": "routine output"}, {"id": "c2", "text": "x" * 81},
                                             {"id": "c3", "text": "done"}]},
            {cid: {"type": "noul", "instructions": "keep %s?" % cid} for cid in ("c1", "c2", "c3")})


def test_answer_refuses_the_whole_request_when_one_chunk_does_not_fit(fake):
    agent, _ = fake
    state, questions = _over_request()

    with pytest.raises(server.FitRefused) as refused:
        server._answer(state, questions)

    assert str(refused.value) == REFUSED
    assert agent.calls == []   # c1 fits and was not asked either: a refused request has no answers
    assert "max_tokens_exceeded" not in str(refused.value)   # on that text the pruner retries (output.ts:371-372, :441)


def _post(body):
    """Handler.do_POST on an in-memory request (no socket, no port): -> (status, JSON body)."""
    raw = json.dumps(body).encode()
    handler = server.Handler.__new__(server.Handler)   # BaseHTTPRequestHandler.__init__ would serve a socket
    handler.path, handler.command, handler.request_version = "/v1/systemone", "POST", "HTTP/1.1"
    handler.requestline, handler.client_address = "POST /v1/systemone HTTP/1.1", ("127.0.0.1", 0)
    handler.headers = {"content-length": str(len(raw))}
    handler.rfile, handler.wfile = io.BytesIO(raw), io.BytesIO()
    handler.do_POST()
    head, _, payload = handler.wfile.getvalue().partition(b"\r\n\r\n")
    return int(head.split(b" ", 2)[1]), json.loads(payload)


def test_handler_answers_a_fit_refusal_with_422_and_its_reason(fake):
    agent, _ = fake
    state, questions = _over_request()

    assert _post({"model": "jev-latest", "state": state, "questions": questions}) == (422, {"error": REFUSED})
    assert agent.calls == [] and server.State.calls == 0

    state["chunks"][1]["text"] = "AssertionError"   # the positive control: every chunk fits
    status, reply = _post({"model": "jev-latest", "state": state, "questions": questions})
    assert (status, reply["fan_out"], sorted(reply["answers"])) == (200, 3, ["c1", "c2", "c3"])
    assert len(agent.calls) == 3 and server.State.calls == 1


def test_an_agent_without_a_tokenizer_is_a_500_refusal_never_a_bypass(fake):
    agent, _ = fake
    del agent.tok   # a production agent that lost its tokenizer: the fit cannot run, so nothing is answered
    state, questions = _over_request()
    state["chunks"][1]["text"] = "AssertionError"

    status, reply = _post({"model": "jev-latest", "state": state, "questions": questions})

    assert status == 500 and reply["error"].startswith("system_one failed: AttributeError: ")
    assert agent.calls == [] and server.State.calls == 0


def test_the_fit_reads_the_agents_own_window_and_the_asked_question(fake, monkeypatch):
    agent, events = fake
    question = {"type": "noul", "instructions": "keep?", "criteria": {"true": "a needed line", "false": "noise"}}
    state = {"chunks": [{"id": "c1", "text": "twenty characters!!!"}]}   # {"chunk": ...} is 33 characters
    monkeypatch.setattr(agent, "cfg", {"max_len": 32, "head_max_len": 8})   # 26 kept: refused

    with pytest.raises(server.FitRefused, match=r"^chunk 'c1' does not fit .*: 26 of its 33 state tokens kept"):
        server._answer(state, {"c1": question})
    builds = [e for e in events if e[0] == "build"]
    assert builds and {(e[3], e[4]) for e in builds} == {(32, 8)}
    assert all(e[2] == agent._to_internal(question) for e in builds)

    monkeypatch.setattr(agent, "cfg", {})   # no lengths in the config: Agent.system_one's defaults, 512 and 192
    events.clear()
    assert server._answer(state, {"c1": question})["fan_out"] == 1
    assert {(e[3], e[4]) for e in events if e[0] == "build"} == {(512, 192)}


def test_revision_guard_refuses_a_different_snapshot(tmp_path):
    snapshots = tmp_path / "hub" / "models--convaiinnovations--laya" / "snapshots"
    (snapshots / "not-the-pinned-revision").mkdir(parents=True)

    with pytest.raises(RuntimeError, match="expected pinned-revision; found: not-the-pinned-revision"):
        server._find_snapshot(str(tmp_path), "pinned-revision")


# ---------- the Laya venv: the real builder and tokenizer read what the server sends (tokenizer only) ----------

LAYA_PY = "/root/venv-laya-probe/bin/python"
LAYA_HF_HOME = "/root/hf-laya-probe"   # the server's --hf-home default when HF_HOME is unset


def _present(path):
    try:   # AF-AP-44: a venue probe returns absent on any OSError, never raises
        os.stat(path)
        return True
    except OSError:
        return False


@pytest.fixture(scope="module")
def laya_venue():
    venue = os.environ.get("S0_01_VENUE")
    if venue != "sandbox":
        pytest.skip("LOUD SKIP: the Laya venv and snapshot are declared inputs of the sandbox venue only (S0_01_VENUE=%r;"
                    " CI declares none, and the PC's Laya paths are not declared to this file)" % venue)
    model_dir = os.path.join(LAYA_HF_HOME, "hub", "models--convaiinnovations--laya", "snapshots", server.PINNED_REVISION,
                             "typed-decisions")   # the checkpoint main() serves by default (--subfolder)
    missing = [p for p in (LAYA_PY, os.path.join(model_dir, "rl_agent_config.json"),
                           os.path.join(model_dir, "tokenizer", "tokenizer.json")) if not _present(p)]
    if missing:
        pytest.fail("declared input missing on the sandbox venue: %s" % missing)
    return {"py": LAYA_PY, "model_dir": model_dir}


def _laya(venue, script, *args, timeout=600):
    proc = subprocess.run([venue["py"], "-c", script, *args], capture_output=True, text=True, timeout=timeout,
                          env=dict(os.environ, HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1"))
    assert proc.returncode == 0, proc.stderr[-3000:]
    return json.loads(proc.stdout.strip().splitlines()[-1])


THROUGH_THE_FAN_OUT = r"""
import json, sys
from importlib.util import module_from_spec, spec_from_file_location
import laya.common as LC
from laya.agent import Agent
from transformers import AutoTokenizer

spec = spec_from_file_location("laya_systemone_server_in_venv", sys.argv[1])
server = module_from_spec(spec)
spec.loader.exec_module(server)
with open(sys.argv[2] + "/rl_agent_config.json") as f:
    cfg = json.load(f)                                           # what Agent.cfg holds
tok = AutoTokenizer.from_pretrained(sys.argv[2] + "/tokenizer")  # what Agent.tok holds; the model is never loaded
L, H = cfg.get("max_len", 512), cfg.get("head_max_len", 192)    # as Agent.system_one reads them


class TokenizerOnlyAgent:
    # Agent's tokenizer, config and question form; the forward pass is replaced by a recorder
    _to_internal = staticmethod(Agent._to_internal)

    def __init__(self):
        self.tok, self.cfg, self.calls = tok, cfg, []

    def system_one(self, state, questions):
        self.calls.append(state)
        qid = next(iter(questions))
        return {"model": "tokenizer-only", "answers": {qid: {"type": "noul", "noul": 0.5}},
                "usage": {"input_tokens": 0, "output_tokens": 0}}


def words(tag, n):   # synthetic filler of n characters: no session text
    out, size, i = [], 0, 0
    while size < n:
        out.append("%s%d" % (tag, i))
        size, i = size + len(out[-1]) + 1, i + 1
    return " ".join(out)[:n]


def question(cid):   # the pruner's noul question shape (vendor/jev-pruner/src/output.ts questionFor), synthetic text
    return {"type": "noul", "instructions": "Chunk %s holds a line the agent still needs. %s" % (cid, words("need", 320)),
            "criteria": {"true": words("keep", 330), "false": words("drop", 370)}}


def request(chunks):   # the pruner's state shape (output.ts stateFor): 53 history entries (3 short, then 50 long)
    return {"context": words("context", 900), "category": "build", "categoryGuidance": words("guide", 380),
            "task": words("goal", 500),
            "history": [{"i": i, "role": ("user", "assistant")[i % 2], "text": words("h%d-" % i, 20 if i < 3 else 1400)}
                        for i in range(53)],
            "command": "python -m pytest tests -q",
            "diagnosticsAndResults": ["FAILED tests/test_x.py::test_y - AssertionError"],
            "chunks": [{"id": cid, "text": text} for cid, text in chunks]}


def whole(state, q):   # the builder keeps every state token: the same length as with no window
    return len(LC.build_sequence(tok, state, q, L, H)[0]) == len(LC.build_sequence(tok, state, q, 10 ** 6, H)[0])


def seen(state, q, text):   # the oracle: the state tokens the real builder keeps, decoded; the chunk inside?
    ids = LC.build_sequence(tok, state, q, L, H)[0]
    empty = len(LC.build_sequence(tok, "", q, L, H)[0])
    kept = tok.decode(ids[empty - 1:len(ids) - 1], clean_up_tokenization_spaces=False)
    return json.dumps(text, ensure_ascii=False)[1:-1] in kept


chunk = "\n".join("tests/test_x.py::test_case_%d FAILED AssertionError: expected %d, got %d" % (i, i, i + 1)
                  for i in range(8))
over = "\n".join("step %d: %s" % (i, words("progress%d-" % i, 90)) for i in range(60))
q1, q2 = question("c1"), question("c2")
i1 = Agent._to_internal(q1)
req = request([("c1", chunk)])
agent = server.State.agent = TokenizerOnlyAgent()
server._answer(req, {"c1": q1})
sent = agent.calls[0]
pin = dict({k: v for k, v in req.items() if k != "chunks"}, chunk=chunk)   # the PIN's state, unfitted
out = {"keys": list(sent), "pin_keys": list(pin), "pin_chars": len(json.dumps(pin, ensure_ascii=False)),
       "history_sent": len(sent["history"]), "history_asked": len(req["history"]),
       "sent_whole": whole(sent, i1), "chunk_seen": seen(sent, i1, chunk), "chunk_seen_unfitted": seen(pin, i1, chunk),
       "other_fields_as_asked": all(sent[k] == req[k] for k in sent if k not in ("history", "chunk"))}
agent = server.State.agent = TokenizerOnlyAgent()
try:
    server._answer(request([("c1", chunk), ("c2", over)]), {"c1": q1, "c2": q2})
    out["refused"] = None
except server.FitRefused as e:
    out["refused"] = str(e)
out["asked_after_refusal"] = len(agent.calls)
print(json.dumps(out))
"""


def test_laya_builder_reads_the_whole_state_the_fan_out_sends(laya_venue):
    out = _laya(laya_venue, THROUGH_THE_FAN_OUT, str(SCRIPT), laya_venue["model_dir"])
    # the incident's shape (53 history segments, about 70,000 characters) in the training order, the chunk last
    assert out["pin_keys"] == out["keys"] == ["context", "category", "categoryGuidance", "task", "history", "command",
                                              "diagnosticsAndResults", "chunk"]
    assert out["pin_chars"] > 70000 and out["chunk_seen_unfitted"] is False   # unfitted, as the PIN sent it: lost
    # fitted: the builder keeps every token, the chunk among them; the history lost whole entries, nothing else was cut
    assert out["sent_whole"] is True and out["chunk_seen"] is True
    assert 0 < out["history_sent"] < out["history_asked"] == 53 and out["other_fields_as_asked"] is True
    # a chunk that cannot fit even with every other field empty: the whole request refused, the model asked nothing
    assert out["refused"].startswith("chunk 'c2' does not fit Laya's window with every other field empty: ")
    assert out["asked_after_refusal"] == 0
