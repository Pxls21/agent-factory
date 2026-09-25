#!/usr/bin/env python3
"""Tests for scripts/qwen_jev.py, the DIRECT vLLM path (D-079, D-082, task #241).

Deterministic, LLM-free: the real pinned simple-jev oracle (imported from ~/simple-jev at its
pinned revision), the real served tokenizer (~/qwen-jev-tokenizer), and a FAKE send that stands
in for the vLLM NETWORK only. The fake is built from the CAPTURED real /v1/completions responses
(tests/fixtures/qwen_jev/completion-{choice,noul}.json, the raw bytes the vLLM server returned on
2026-09-25), so a change in the response shape (the dict top_logprobs, the usage keys) reds a
test; the fake never mirrors the code's own assumption (AF-AP-42). The key is a FAKE key file
(QWEN_JEV_KEY_FILE); the real ~/.config/qwen-builder/api-key is never read here.

  tests/test_qwen_jev.py

Negative controls (each guard has a paired red case): the count mismatch is refused; a bounded
label is named; the served model other than the id sent is refused; the chat (list) logprob shape
is refused; a checkout at another revision is refused; the port is taken; the FAKE key is absent
from the request body, the server's view, the response and the error; the /v1/completions body
carries exactly D-3's five keys (no echo, no prompt_logprobs, no best_of, no n).
"""
import json
import os
import socket
import sys
import threading
from http.server import BaseHTTPRequestHandler
from pathlib import Path

import pytest

# Declared venue: the PC's qwen-jev venv, which alone holds this module's inputs (transformers in ~/venv-qwenjev, the
# served tokenizer ~/qwen-jev-tokenizer, the pinned ~/simple-jev checkout). A run there exports QWEN_JEV_VENUE=pc:
#   QWEN_JEV_VENUE=pc PATH="$HOME/venv-qwenjev/bin:$PATH" bash scripts/test_summary.sh tests/test_qwen_jev.py
# Everywhere else the module skips LOUDLY: CI, the sandbox, and the PC's default suite venv (scripts/pc_suite.sh exports
# S0_01_VENUE=pc with ~/venv-agent-factory, which has no transformers). With the declaration set, a missing input fails at
# import (the pin assert, the tokenizer load), never skips.
if os.environ.get("QWEN_JEV_VENUE") != "pc":
    pytest.skip("LOUD SKIP: tests/test_qwen_jev.py runs only in the PC's qwen-jev venv (QWEN_JEV_VENUE=pc; transformers, "
                "~/simple-jev at its pin, ~/qwen-jev-tokenizer); QWEN_JEV_VENUE=%r" % os.environ.get("QWEN_JEV_VENUE"),
                allow_module_level=True)

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import scripts.qwen_jev as qwen_jev  # noqa: E402

from scripts.qwen_jev import (  # noqa: E402
    JevService,
    TOKENIZER_DIR,
    completions_body,
    make_service,
    read_key,
    verify_pin,
)

# The real served tokenizer (tokenizers only; transformers in the venv is fine without torch).
from transformers import AutoTokenizer  # noqa: E402

TZ = AutoTokenizer.from_pretrained(TOKENIZER_DIR)

# D-1 precondition: the oracle is used at its pinned revision (module-level, like the J2 probe).
assert verify_pin()[0], "pinned simple-jev checkout does not match upstream.lock.yaml"
qwen_jev.load_oracle()

FIXTURES = HERE / "fixtures" / "qwen_jev"
SERVED_ID = "qwen3.8-27b-local"  # the id the captured fixtures carry (D-3: read from /v1/models)
FAKE_KEY = "FAKE-KEY-DO-NOT-LEAK"


def load_fixture(name):
    """The captured real response, with vLLM's diagnostic extras dropped (prompt_token_ids and
    prompt_logprobs in particular: prompt_logprobs is the one that OOM-killed the shared engine,
    AF-AP-201; this test must never echo it). Everything the adapter reads is kept."""
    with open(FIXTURES / ("completion-%s.json" % name)) as fh:
        d = json.load(fh)
    c = d["choices"][0]
    c.pop("prompt_token_ids", None)
    c.pop("prompt_logprobs", None)
    c.pop("routed_experts", None)
    return d


class FakeVLLM:
    """The test double for the vLLM network. It returns the CAPTURED real response for the branch
    (the fixture is rebuilt per call, so a test may mutate it) and records every request: the
    exact body and the Authorization header, so D-3/D-6 are asserted against what would be sent."""

    def __init__(self, name, served=SERVED_ID, status=200, error_body=None):
        self.name = name
        self.served = served
        self.status = status
        self.error_body = error_body
        self.requests = []

    def __call__(self, branch, named):
        body = completions_body(self.served, branch.token_ids)
        self.requests.append({"body": body, "auth": FAKE_KEY})
        if self.status == 200:
            return 200, load_fixture(self.name)
        # the transport error shape JevService produces
        return self.status, (self.error_body or {"error": {"message": "fake failure"}})


def compile_branches(svc, state, questions):
    """The oracle's own compile, as _single does it."""
    creq = qwen_jev._oracle["ClassifierRequest"].model_validate(
        {"model": svc.sent_id, "state": state, "questions": questions})
    qwen_jev._oracle["prepare_policy"](creq, "v1", svc.policy)
    return svc.compiler.compile(creq)


def make_service_for_tests(policy="examples_binary", send=None):
    """A JevService with the real oracle, the real tokenizer, the fixture's served id and a
    FAKE send. No key file is read (the send is fake; D-6's key-reading is covered separately)."""
    return JevService(TZ, policy, key=FAKE_KEY, served_id=SERVED_ID, send=send)


# ---------- D-1: the pin ----------------------------------------------------------------------

def test_pin_passes_and_refuses_when_unpinned(tmp_path, monkeypatch):
    """The pinned checkout passes; a checkout at another revision is refused."""
    ok, expected, actual, _reason = verify_pin()
    assert ok and expected == actual
    # negative control: a checkout at a different revision must be refused
    other = tmp_path / "other-jev"
    other.mkdir()
    monkeypatch.setattr(qwen_jev, "SIMPLE_JEV", str(other))
    ok2, _exp2, _act2, reason = verify_pin()
    assert not ok2, "an unpinned checkout must be refused"
    assert "not a checkout" in reason or "!=" in reason


def test_make_service_refuses_unpinned_checkout(tmp_path, monkeypatch):
    """A checkout at another revision refuses the WHOLE service, not just the check."""
    other = tmp_path / "other-jev"
    other.mkdir()
    monkeypatch.setattr(qwen_jev, "SIMPLE_JEV", str(other))
    try:
        make_service("examples_binary", key_file=os.path.expanduser("~/.config/qwen-builder/api-key"))
    except SystemExit as e:
        assert "REFUSED to serve" in str(e)
        return
    raise AssertionError("make_service must refuse an unpinned checkout")


def test_pin_refuses_when_lock_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(qwen_jev, "UPSTREAM_LOCK", str(tmp_path / "missing.lock"))
    ok, _exp, _act, reason = verify_pin()
    assert not ok
    assert "no advisory_jev_runtimes" in reason


# ---------- D-3: the body ---------------------------------------------------------------------

def test_body_keys_exactly_d3():
    """The body carries exactly D-3's five keys: a body carrying echo, prompt_logprobs, best_of
    or n cannot be built (AF-AP-201: prompt_logprobs OOM-killed the shared engine)."""
    body = completions_body(SERVED_ID, [1, 2, 3])
    assert set(body) == {"model", "prompt", "max_tokens", "temperature", "logprobs"}
    assert body["model"] == SERVED_ID
    assert body["prompt"] == [1, 2, 3]
    assert body["max_tokens"] == 1
    assert body["temperature"] == 0
    assert body["logprobs"] == 20
    for forbidden in ("echo", "prompt_logprobs", "best_of", "n"):
        assert forbidden not in body, "%s in the body (AF-AP-201)" % forbidden


# ---------- D-4: parity and the label reader ---------------------------------------------------

def test_count_mismatch_refused():
    """D-4: usage.prompt_tokens != len(token_ids) is refused (not scored). The noul fixture's count
    matches its branch; corrupt it and the branch must be refused and named."""
    fake = FakeVLLM("noul")
    svc = make_service_for_tests(send=fake)
    compiled = compile_branches(svc, {"finding": "A real break, reproduced through the real path."},
                                {"q": {"type": "noul", "instructions": "Does it block?"}})
    branch = compiled.branches[0]
    resp = load_fixture("noul")
    resp["usage"]["prompt_tokens"] = len(branch.token_ids) + 7  # a count that cannot be the compiler's
    svc._send = lambda b, named: (200, resp)
    out = svc._single({"finding": "A real break, reproduced through the real path."},
                      {"q": {"type": "noul", "instructions": "Does it block?"}})
    assert out["answers"]["q"].get("refused"), "a count mismatch must be refused"
    a = out["answers"]["q"]
    assert "token count" in a["refused"]
    assert a.get("noul") is None and a.get("choice") is None
    assert "probabilities" not in a, "a refused branch must carry no score"


def test_served_model_other_than_sent_refused():
    """D-3: the response's model must equal the id sent; any other id is refused."""
    fake = FakeVLLM("noul", served=SERVED_ID)
    svc = make_service_for_tests(send=fake)
    out = svc._single({"finding": "A real break, reproduced through the real path."},
                      {"q": {"type": "noul", "instructions": "Does it block?"}})
    assert not out["answers"]["q"].get("refused")
    resp = load_fixture("noul")
    resp["model"] = "qwen3.8-27b"  # the other id vLLM lists (the one that is not the local serving)
    svc._send = lambda b, named: (200, resp)
    out2 = svc._single({"finding": "A real break, reproduced through the real path."},
                       {"q": {"type": "noul", "instructions": "Does it block?"}})
    assert out2["answers"]["q"].get("refused"), "a different served model must be refused"
    assert "not the id sent" in out2["answers"]["q"]["refused"]


def test_chat_list_shape_refused():
    """The CHAT logprob shape is a different response and is refused, not guessed at: the
    adapter's scoring path is /v1/completions (D-3). The red is the fixture's dict replaced by
    the chat list-of-dicts shape."""
    fake = FakeVLLM("noul")
    svc = make_service_for_tests(send=fake)
    resp = load_fixture("noul")
    # the chat shape: a list of per-token entries, each a dict of {token, logprob}
    resp["choices"][0]["logprobs"]["top_logprobs"] = [
        [{"token": "A", "logprob": -0.001}, {"token": "B", "logprob": -6.876}]]
    svc._send = lambda b, named: (200, resp)
    out = svc._single({"finding": "A real break, reproduced through the real path."},
                      {"q": {"type": "noul", "instructions": "Does it block?"}})
    assert out["answers"]["q"].get("refused")
    assert "not the token->logprob dict" in out["answers"]["q"]["refused"]


def test_bounded_label_named():
    """D-4: a label absent from the top 20 is BOUNDED (the lowest logprob shown, an upper bound)
    and named in the answer; it is never silently filled with a real value."""
    fake = FakeVLLM("noul")
    svc = make_service_for_tests(send=fake)
    resp = load_fixture("noul")
    top = resp["choices"][0]["logprobs"]["top_logprobs"][0]
    # drop the label token 'B' from the 20 so the reader must bound it
    assert "B" in top
    del top["B"]
    while len(top) < 20:
        top["fill%d" % len(top)] = -16.0
    svc._send = lambda b, named: (200, resp)
    out = svc._single({"finding": "A real break, reproduced through the real path."},
                      {"q": {"type": "noul", "instructions": "Does it block?"}})
    a = out["answers"]["q"]
    assert a.get("bounded_labels") == ["B"], "the bounded label must be named"
    assert "refused" not in out, "a bounded (not missing) label is still scored, bounded"
    # the bounded label got the lowest shown logprob, not a fabricated real value
    assert a["noul"] is not None


def test_scoring_equals_oracle_on_fixed_logprobs():
    """Scoring must equal simple-jev's own build_response on the same logprobs: the adapter adds
    no maths of its own (D-1: the oracle is used, never re-implemented)."""
    fake = FakeVLLM("choice")
    svc = make_service_for_tests(send=fake)
    state = {"incident": "The ball on the table is red and round."}
    questions = {"q": {"type": "choice", "instructions": "What color is the ball?",
                       "criteria": {"red": "The ball is red.", "blue": "The ball is blue."}}}
    compiled = compile_branches(svc, state, questions)
    branch, sq = compiled.branches[0], compiled.plan.questions[0]
    # the oracle's own scoring on the same row the adapter would build
    top = load_fixture("choice")["choices"][0]["logprobs"]["top_logprobs"][0]
    row = {}
    for i, lab in enumerate(sq.output_labels):
        tok = TZ.decode([branch.output_ids[i]])
        row[lab] = top[tok]
    creq = qwen_jev._oracle["ClassifierRequest"].model_validate(
        {"model": SERVED_ID, "state": state, "questions": questions})
    p, _bk = qwen_jev._oracle["prepare_policy"](creq, "v1", svc.policy)
    expected = qwen_jev._oracle["build_response"](
        p, {branch.branch_id: row}, input_tokens=len(branch.token_ids))
    out = svc._single(state, questions)
    a, ea = out["answers"]["q"], expected["answers"]["q"]
    assert a["type"] == ea["type"] == "choice"
    for k in ("choice", "score", "confidence", "probabilities"):
        if k in ea:
            assert a.get(k) == ea[k], "%s: %r != oracle %r" % (k, a.get(k), ea[k])
    assert a["choice"] == "red", "the fixture's argmax is the 'red' label (its token is the generated 'A')"


# ---------- D-5: the wire contract ------------------------------------------------------------

def _fanout_request(svc, fake):
    """A D-5 fan-out request: two question ids that name state.chunks ids."""
    return {
        "state": {"finding": "A real break, reproduced through the real path.",
                  "chunks": [{"id": "c1", "text": "chunk one text"},
                             {"id": "c2", "text": "chunk two text"}]},
        "questions": {"c1": {"type": "noul", "instructions": "Does it block?"},
                      "c2": {"type": "noul", "instructions": "Does it block?"}},
    }


def test_fanout_per_chunk():
    """D-5: every question id naming a chunks id -> one call per chunk, fan_out set, usage summed.
    The fake proves the fan-out: exactly two sends, each seeing only its own chunk."""
    fake = FakeVLLM("noul")
    svc = make_service_for_tests(send=fake)
    out = svc.systemone(_fanout_request(svc, fake))
    assert out["fan_out"] == 2
    assert set(out["answers"]) == {"c1", "c2"}
    assert out["usage"]["input_tokens"] > 0
    assert len(fake.requests) == 2, "the fan-out must send one request per chunk"
    assert out["model"] == SERVED_ID


def test_no_model_key_gets_served_id():
    """D-5: a request without a model gets the served id (the runner never has to name it)."""
    fake = FakeVLLM("noul")
    svc = make_service_for_tests(send=fake)
    body = _fanout_request(svc, fake)
    assert "model" not in body
    out = svc.systemone(body)
    assert out["model"] == SERVED_ID


# ---------- D-6: the key ----------------------------------------------------------------------

def test_key_file_read_and_permissions(tmp_path):
    """D-6: the key is read from the file the caller names (QWEN_JEV_KEY_FILE overrides the path)."""
    keyfile = tmp_path / "fake.key"
    keyfile.write_text(FAKE_KEY + "\n")
    os.chmod(keyfile, 0o600)
    assert read_key(str(keyfile)) == FAKE_KEY
    # an empty key file is a refusal, not an empty Authorization header
    empty = tmp_path / "empty.key"
    empty.write_text("\n")
    try:
        read_key(str(empty))
    except RuntimeError:
        return
    raise AssertionError("an empty key file must be refused")


class _Handler(BaseHTTPRequestHandler):
    """A fake vLLM that records the Authorization header and the raw body it received, and
    returns the captured fixture. It is the second independent view of the wire (D-6: the key
    must be in the header only, never in the body)."""
    server_version = "fake-vllm"
    got_auth = None
    got_body = None
    fail = False

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/v1/models":
            return self._send(200, {"data": [{"id": SERVED_ID}]})
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        n = int(self.headers.get("content-length") or 0)
        body = self.rfile.read(n)
        _Handler.got_auth = self.headers.get("Authorization")
        _Handler.got_body = body
        if _Handler.fail:
            return self._send(500, {"error": {"message": "internal fake failure"}})
        return self._send(200, load_fixture("noul"))

    def _send(self, code, obj):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)


def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


def test_key_in_header_only_via_live_local_http():
    """D-6, through the REAL local HTTP wire (not the fake object): the key rides the
    Authorization header only; it is never in the body the server receives, never in the
    response, and never in a 500 error the server returns."""
    port = _free_port()
    srv = threading.Thread(target=lambda: __import__("http.server", fromlist=["ThreadingHTTPServer"]).ThreadingHTTPServer(
        ("127.0.0.1", port), _Handler).serve_forever(), daemon=True)
    srv.start()
    os.environ["QWEN_JEV_VLLM"] = "http://127.0.0.1:%d" % port
    try:
        svc = make_service_for_tests()
        svc.vllm_base = "http://127.0.0.1:%d" % port
        out = svc._single({"finding": "A real break, reproduced through the real path."},
                          {"q": {"type": "noul", "instructions": "Does it block?"}})
        assert "refused" not in out
        # the key is in the header
        assert _Handler.got_auth == "Bearer " + FAKE_KEY
        # the key is NOT in the body (the server received a body; it is the recorded raw bytes)
        got_body = _Handler.got_body  # type: ignore[union-attr]
        assert FAKE_KEY not in got_body.decode("utf-8", "replace")
        # the key is NOT in the response
        assert FAKE_KEY not in json.dumps(out)
        # and a 500 error must not name it either
        _Handler.fail = True
        out2 = svc._single({"finding": "A real break, reproduced through the real path."},
                           {"q": {"type": "noul", "instructions": "Does it block?"}})
        assert out2["answers"]["q"].get("refused"), "a transport 500 is a refusal"
        assert FAKE_KEY not in json.dumps(out2), "the key must not appear in an error"
    finally:
        os.environ.pop("QWEN_JEV_VLLM", None)


# ---------- D-7: the port ---------------------------------------------------------------------

def test_runner_refuses_lane_mismatch_on_health(monkeypatch):
    """D-7 (the runner's half of the port rule, AF-AP-33): before the first request the J2 runner
    checks /health and refuses to score a listener whose revision is not this lane's LANE_ID."""
    import importlib.util
    from pathlib import Path as _P
    mod = importlib.util.spec_from_file_location(
        "qwen27b_j2", _P(HERE.parent / "docs" / "research" / "findings" / "j2b-variants" / "qwen27b_j2.py"))
    m = importlib.util.module_from_spec(mod)
    mod.loader.exec_module(m)

    class _H(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def do_GET(self):
            return self._send(200, {"ok": True, "model": SERVED_ID,
                                    "revision": "some-other-lane", "oracle_revision": "x"})

        def _send(self, code, obj):
            b = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)

    port = _free_port()
    srv = threading.Thread(target=lambda: __import__("http.server", fromlist=["ThreadingHTTPServer"]).ThreadingHTTPServer(
        ("127.0.0.1", port), _H).serve_forever(), daemon=True)
    srv.start()
    import time as _t
    _t.sleep(0.3)  # let the server thread finish binding before the client fires
    monkeypatch.setenv("LANE_ID", "pc-qj2.md--d6a2142")
    try:
        try:
            m.check_health("http://127.0.0.1:%d" % port)
        except SystemExit as e:
            assert "D-7" in str(e) and "some-other-lane" in str(e)
            return
        raise AssertionError("a lane-mismatched listener must be refused")
    finally:
        monkeypatch.delenv("LANE_ID", raising=False)


def test_runner_accepts_matching_health(monkeypatch):
    """D-7 (positive control): a /health carrying THIS lane's revision passes the runner's check."""
    import importlib.util
    from pathlib import Path as _P
    mod = importlib.util.spec_from_file_location(
        "qwen27b_j2", _P(HERE.parent / "docs" / "research" / "findings" / "j2b-variants" / "qwen27b_j2.py"))
    m = importlib.util.module_from_spec(mod)
    mod.loader.exec_module(m)

    class _H(BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def do_GET(self):
            return self._send(200, {"ok": True, "model": SERVED_ID,
                                    "revision": "pc-qj2.md--d6a2142", "oracle_revision": "x"})

        def _send(self, code, obj):
            b = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(b)))
            self.end_headers()
            self.wfile.write(b)

    port = _free_port()
    srv = threading.Thread(target=lambda: __import__("http.server", fromlist=["ThreadingHTTPServer"]).ThreadingHTTPServer(
        ("127.0.0.1", port), _H).serve_forever(), daemon=True)
    srv.start()
    import time as _t
    _t.sleep(0.3)  # let the server thread finish binding before the client fires
    monkeypatch.setenv("LANE_ID", "pc-qj2.md--d6a2142")
    try:
        h = m.check_health("http://127.0.0.1:%d" % port)
        assert h["revision"] == "pc-qj2.md--d6a2142"
    finally:
        monkeypatch.delenv("LANE_ID", raising=False)


def test_port_taken_refuses_to_start(monkeypatch, tmp_path):
    """D-7 (AF-AP-33): a listener the adapter did not start is never treated as itself: when its
    port is taken it refuses to start with a clear error and a non-zero exit. The port check is
    patched to report a squatter; make_service is patched to prove the refusal happens BEFORE
    the service is ever built (no network, no oracle load)."""
    monkeypatch.setattr(qwen_jev, "_port_taken", lambda port: True)
    monkeypatch.setattr(qwen_jev, "make_service",
                        lambda *a, **k: (_ for _ in ()).throw(AssertionError("must not build")))
    try:
        qwen_jev.main(["--port", "47420", "--policy", "examples_binary"])
    except SystemExit as e:
        assert "already taken" in str(e), "the refusal must name the port (AF-AP-33)"
        return
    raise AssertionError("a taken port must refuse to start")
