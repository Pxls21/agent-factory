"""Model-free routing tests for the local Laya System One endpoint."""
from copy import deepcopy
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
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


class Recorder:
    def __init__(self):
        self.calls = []

    def system_one(self, state, questions):
        self.calls.append((deepcopy(state), deepcopy(questions)))
        question_id = next(iter(questions))
        return {
            "model": "recorder",
            "answers": {question_id: {"type": "noul", "noul": 0.5}},
            "usage": {"input_tokens": 1, "output_tokens": 0},
        }


def test_answer_fans_out_each_named_chunk_without_reusing_batch_state(monkeypatch):
    recorder = Recorder()
    monkeypatch.setattr(server.State, "agent", recorder)
    state = {
        "context": "agent-factory",
        "task": "run tests",
        "chunks": [{"id": "c1", "text": "routine output"}, {"id": "c2", "text": "AssertionError"}],
    }
    questions = {
        "c1": {"type": "noul", "instructions": "keep?"},
        "c2": {"type": "noul", "instructions": "keep?"},
    }

    result = server._answer(state, questions)

    assert result["answers"] == {
        "c1": {"type": "noul", "noul": 0.5},
        "c2": {"type": "noul", "noul": 0.5},
    }
    assert result["usage"] == {"input_tokens": 2, "output_tokens": 0}
    assert result["fan_out"] == 2
    assert recorder.calls == [
        (
            {"context": "agent-factory", "task": "run tests", "chunk": "routine output"},
            {"c1": questions["c1"]},
        ),
        (
            {"context": "agent-factory", "task": "run tests", "chunk": "AssertionError"},
            {"c2": questions["c2"]},
        ),
    ]


def test_answer_falls_back_once_for_a_question_without_a_matching_chunk(monkeypatch):
    recorder = Recorder()
    monkeypatch.setattr(server.State, "agent", recorder)
    state = {"context": "agent-factory", "chunks": [{"id": "c1", "text": "routine output"}]}
    questions = {"not-a-chunk": {"type": "noul", "instructions": "keep?"}}

    result = server._answer(state, questions)

    assert "fan_out" not in result
    assert recorder.calls == [(state, questions)]


def test_revision_guard_refuses_a_different_snapshot(tmp_path):
    snapshots = tmp_path / "hub" / "models--convaiinnovations--laya" / "snapshots"
    (snapshots / "not-the-pinned-revision").mkdir(parents=True)

    with pytest.raises(RuntimeError, match="expected pinned-revision; found: not-the-pinned-revision"):
        server._find_snapshot(str(tmp_path), "pinned-revision")
