"""scripts/jev.py: the endpoint's real request contract (D-1, D-2), fail-open (D-4), scrub then cap (D-5), the call log
(D-6), the PC path through an injected bridge runner (D-3), and jev_local.sh's offline branches.

The loopback HTTP test double below RECORDS every request it gets: it checks the client's request bytes and its error
handling. Its answers only have the server's SHAPE (scripts/laya_systemone_server.py); no number it returns is ever a
claimed model answer (the live runs against the real server are A1 in the lane report). No test here calls the real
bridge: every PC-path test injects a runner and a fake env file. Every secret below is a fake string.
"""
import base64
import hashlib
import http.server
import importlib.util
import json
import os
import pathlib
import re
import socket
import stat
import subprocess
import sys
import threading
import time

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
TOOL = ROOT / "scripts" / "jev.py"
LOCAL_SH = ROOT / "scripts" / "jev_local.sh"


def _load():
    spec = importlib.util.spec_from_file_location("jev_under_test", TOOL)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


jev = _load()

# the transcript scrubber's classes (tests/test_transcript_export.py PLANTED); fake values only
PLANTED = [
    "AGENT_TOKEN=cVMjXl1uWH1c9Ogzoc_-k60yOL5KP5pr",
    "PC_BRIDGE_TOKEN=abcdefghijklmnop123456",
    "X-Agent-Token: zzzzzzzzzzzzzzzzzzzzzz",
    "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.payload.sig",
    "sk-3c3d5f1e8a2b4c6d9e0f1234567890ab",
    "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
    "AIzaSyA1234567890abcdefghijklmnopqrstuv",
    "api_key: sk-live-0123456789abcdef0123",
    "https://leading-twist-aruba-pulse.trycloudflare.com/exec",
    "token=" + "Q" * 44,
]
RAW_SECRETS = ["cVMjXl1uWH1c9Ogzoc_-k60yOL5KP5pr", "abcdefghijklmnop123456", "zzzzzzzzzzzzzzzzzzzzzz",
               "eyJhbGciOiJIUzI1NiJ9", "3c3d5f1e8a2b4c6d9e0f1234567890ab", "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
               "AIzaSyA1234567890abcdefghijklmnopqrstuv", "sk-live-0123456789abcdef0123", "leading-twist-aruba-pulse",
               "Q" * 44]
BIND_WARNING = "/home/rocco/.local/share/tirith/shell/lib/bash-hook.bash: line 12: bind: warning: line editing not enabled"
FAKE_URL = "https://fake-bridge-link-for-tests.example.invalid"
FAKE_TOKEN = "fake-bridge-token-0123456789"


# ---------- the recording test double ----------

def shaped_reply(req, scores=None):
    """A reply with the server's shape for `req` (answers per question id; `fan_out` when every id names a chunk)."""
    qs, st = req["questions"], req["state"]
    answers = {}
    for i, (qid, q) in enumerate(sorted(qs.items())):
        if q["type"] == "noul":
            v = (scores or {}).get(qid, round(0.9 - 0.1 * i, 4))
            answers[qid] = {"type": "noul", "noul": v, "confidence": max(v, 1 - v), "action": {"act_probability": 1.0}}
        elif q["type"] == "choice":
            keys = list(q["criteria"])
            answers[qid] = {"type": "choice", "choice": keys[-1], "confidence": 0.2, "action": {"act_probability": 1.0},
                            "probabilities": {k: round(1.0 / len(keys), 4) for k in keys}}
        else:
            answers[qid] = {"type": "score", "score": 1.0, "confidence": 0.3, "action": {"act_probability": 1.0},
                            "legend": {str(j): c for j, c in enumerate(q["criteria"])},
                            "probabilities": {str(j): round(1.0 / len(q["criteria"]), 4) for j in range(len(q["criteria"]))}}
    out = {"model": "double", "answers": answers, "usage": {"input_tokens": 1, "output_tokens": 0}, "latency_ms": 1.0}
    chunks = st.get("chunks") if isinstance(st, dict) else None
    if isinstance(chunks, list) and set(qs) <= {c.get("id") for c in chunks if isinstance(c, dict)}:
        out["fan_out"] = len(qs)
    return out


class Double:
    def __init__(self, behave):
        self.requests = []
        outer = self

        class H(http.server.BaseHTTPRequestHandler):
            def _serve(self, method):
                n = int(self.headers.get("content-length") or 0)
                body = self.rfile.read(n) if n else b""
                outer.requests.append({"method": method, "path": self.path, "headers": dict(self.headers), "body": body})
                status, payload, delay = behave(method, self.path, body)
                if delay:
                    time.sleep(delay)
                data = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
                try:
                    self.send_response(status)
                    self.send_header("content-type", "application/json")
                    self.send_header("content-length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                except OSError:
                    pass

            def do_GET(self):
                self._serve("GET")

            def do_POST(self):
                self._serve("POST")

            def log_message(self, *args):
                pass

        class S(http.server.ThreadingHTTPServer):
            daemon_threads = True

            def handle_error(self, request, client_address):
                pass

        self.srv = S(("127.0.0.1", 0), H)
        threading.Thread(target=self.srv.serve_forever, daemon=True).start()
        self.url = "http://127.0.0.1:%d" % self.srv.server_address[1]

    def posts(self):
        return [json.loads(r["body"]) for r in self.requests if r["method"] == "POST"]

    def close(self):
        self.srv.shutdown()
        self.srv.server_close()


def ok_behaviour(scores=None):
    def behave(method, path, body):
        if method == "GET" and path == "/health":
            return 200, {"ok": True, "device": "cpu"}, 0
        return 200, shaped_reply(json.loads(body), scores), 0
    return behave


@pytest.fixture
def double():
    made = []

    def make(behave=None):
        d = Double(behave or ok_behaviour())
        made.append(d)
        return d
    yield make
    for d in made:
        d.close()


@pytest.fixture
def refused_url():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))           # bound, never listening: every connect is refused
    yield "http://127.0.0.1:%d" % s.getsockname()[1]
    s.close()


def cli(*args, timeout=60):
    return subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True, timeout=timeout)


# ---------- D-1 / D-2: the request contract ----------

def test_rank_sends_the_list_form_with_one_noul_question_per_chunk(double, tmp_path):
    d = double(ok_behaviour({"c0": 0.2, "c1": 0.7, "c2": 0.5}))
    res = jev.rank("why did pytest fail", ["note zero", "note one", "note two"], url=d.url, log_path=tmp_path / "l" / "c.jsonl")
    (req,) = d.posts()
    assert d.requests[0]["path"] == "/v1/systemone"
    assert req["model"] == "laya"
    assert req["state"] == {"query": "why did pytest fail",
                            "chunks": [{"id": "c0", "text": "note zero"}, {"id": "c1", "text": "note one"},
                                       {"id": "c2", "text": "note two"}]}
    assert req["questions"] == {c: {"type": "noul", "instructions": jev.RANK_INSTRUCTIONS} for c in ("c0", "c1", "c2")}
    assert res["fan_out"] == 3 and res["venue"] == "url"
    assert res["ranking"] == [["c1", 0.7], ["c2", 0.5], ["c0", 0.2]]


def test_rank_keeps_caller_ids_and_the_cli_prints_one_json_line(double, tmp_path):
    d = double()
    r = cli("rank", "--url", d.url, "--log-file", str(tmp_path / "c.jsonl"), "--query", "q", "--chunk", "a", "--chunk", "b")
    assert r.returncode == 0 and r.stderr == "", r.stderr
    out = json.loads(r.stdout)
    assert out["cmd"] == "rank" and out["fan_out"] == 2 and [x[0] for x in out["ranking"]] == ["c0", "c1"]
    d2 = double()
    res = jev.rank("q", [{"id": "AF-AP-92", "text": "x"}, {"id": "CLAUDE.md:433", "text": "y"}], url=d2.url, log=False)
    assert [c["id"] for c in d2.posts()[0]["state"]["chunks"]] == ["AF-AP-92", "CLAUDE.md:433"]
    assert {x[0] for x in res["ranking"]} == {"AF-AP-92", "CLAUDE.md:433"}


def test_rank_refuses_a_reply_without_per_chunk_fan_out(double, tmp_path):
    # the batch form (measured 12:17Z): no fan_out and one shared score; a ranking over it would be hollow
    def batch(method, path, body):
        req = json.loads(body)
        return 200, {"answers": {q: {"type": "noul", "noul": 0.5372, "confidence": 0.5372} for q in req["questions"]}}, 0
    d = double(batch)
    assert jev.rank("q", ["a", "b"], url=d.url, log=False) is None
    assert "no per-chunk fan-out" in jev.last_reason
    r = cli("rank", "--url", d.url, "--no-log", "--query", "q", "--chunk", "a", "--chunk", "b")
    assert r.returncode == 3 and r.stdout == ""
    assert r.stderr.splitlines() == ["jev: unavailable: url: no per-chunk fan-out (fan_out=None for 2 chunks)"]


def test_classify_sends_one_native_choice_question(double):
    d = double()
    res = jev.classify("state text", ["alpha", "beta", "gamma"], url=d.url, log=False)
    (req,) = d.posts()
    assert req["state"] == "state text"
    assert req["questions"] == {"q": {"type": "choice", "instructions": jev.CLASSIFY_INSTRUCTIONS,
                                      "criteria": ["alpha", "beta", "gamma"]}}
    assert res["choice"] == "gamma" and set(res["probabilities"]) == {"alpha", "beta", "gamma"}


def test_ask_sends_one_typed_question(double):
    d = double()
    a = jev.ask("s", "is it?", url=d.url, log=False)
    b = jev.ask("s", "how bad?", qtype="score", criteria=["low", "mid", "high"], url=d.url, log=False)
    reqs = d.posts()
    assert reqs[0]["questions"] == {"q": {"type": "noul", "instructions": "is it?"}}
    assert reqs[1]["questions"] == {"q": {"type": "score", "instructions": "how bad?", "criteria": ["low", "mid", "high"]}}
    assert a["answer"]["type"] == "noul" and b["answer"]["type"] == "score"


def test_health_is_a_get_and_a_not_ok_health_is_unavailable(double):
    d = double()
    assert jev.health(url=d.url, log=False)["health"]["ok"] is True
    assert d.requests[0]["method"] == "GET" and d.requests[0]["path"] == "/health"
    d2 = double(lambda m, p, b: (200, {"ok": False}, 0))
    assert jev.health(url=d2.url, log=False) is None and jev.last_reason == "url: health is not ok"


# ---------- D-4 / A2: fail-open ----------

def _fail(status, body, delay=0):
    return lambda m, p, b: (status, body, delay)


FAILURES = [
    ("http500", _fail(500, {"error": "system_one failed: KeyError: 'instructions'"}), [],
     "url: HTTP 500 (system_one failed: KeyError: 'instructions')"),
    ("http503", _fail(503, {"error": "model not loaded"}), [], "url: HTTP 503 (model not loaded)"),
    ("non-json", _fail(200, b"<html>this is not json</html>"), [], "url: non-JSON reply"),
    ("timeout", _fail(200, {"answers": {}}, delay=3), ["--timeout", "0.5"], "url: timeout after 0.5s"),
    ("nan", lambda m, p, b: (200, b'{"answers": {"q": {"type": "noul", "noul": NaN, "confidence": 0.5}}}', 0), [],
     "url: noul is not a finite number in [0, 1]"),
]


@pytest.mark.parametrize("name,behave,extra,reason", FAILURES, ids=[f[0] for f in FAILURES])
def test_failure_is_exit_3_with_one_reason_line_and_none_from_the_api(double, tmp_path, name, behave, extra, reason):
    d = double(behave)
    r = cli("ask", "--url", d.url, "--log-file", str(tmp_path / "c.jsonl"), "--state", "s", "--instructions", "i?", *extra)
    assert r.returncode == 3, (r.stdout, r.stderr)
    assert r.stdout == ""
    assert r.stderr.splitlines() == ["jev: unavailable: " + reason]
    timeout = float(extra[1]) if extra else 30.0
    assert jev.ask("s", "i?", url=d.url, timeout=timeout, log=False) is None
    assert jev.last_reason == reason


def test_connection_refused_is_exit_3_and_none(refused_url, tmp_path):
    r = cli("health", "--url", refused_url, "--no-log")
    assert (r.returncode, r.stdout, r.stderr.splitlines()) == (3, "", ["jev: unavailable: url: connection refused"])
    assert jev.rank("q", ["a"], url=refused_url, log=False) is None
    assert jev.last_reason == "url: connection refused"


@pytest.mark.parametrize("args", [
    [],
    ["rank", "--query", "q"],
    ["ask", "--state", "s"],
    ["classify", "--state", "s", "--label", "only-one"],
    ["ask", "--state", "s", "--instructions", "i", "--timeout", "nan"],
    ["ask", "--state", "s", "--instructions", "i", "--max-chars", "0"],
    ["ask", "--state", "s", "--instructions", "i", "--type", "choice", "--criterion", "one"],
    ["ask", "--state", "s", "--instructions", "i", "--url", "http://10.0.0.8:47411"],
    ["rank", "--query", "q", "--chunks-file", "/nonexistent/chunks.json"],
], ids=["no-command", "rank-no-chunks", "ask-no-instructions", "one-label", "timeout-nan", "max-chars-0",
        "choice-one-criterion", "non-loopback-url", "missing-chunks-file"])
def test_usage_errors_exit_64_and_send_nothing(double, args):
    d = double()
    has_url = "--url" in args
    r = cli(*args, *([] if has_url or not args else ["--url", d.url]), "--no-log") if args else cli()
    assert r.returncode == 64, (r.stdout, r.stderr)
    assert r.stdout == "" and d.requests == []


def test_import_api_never_raises_on_bad_input(double):
    d = double()
    assert jev.rank("q", [], url=d.url, log=False) is None and "at least one chunk" in jev.last_reason
    assert jev.rank("q", [{"id": "bad id!", "text": "x"}], url=d.url, log=False) is None
    assert jev.rank("q", [{"id": "a", "text": "x"}, {"id": "a", "text": "y"}], url=d.url, log=False) is None
    assert jev.ask(None, "i", url=d.url, log=False) is None
    assert jev.ask("s", "i", url=d.url, timeout=float("inf"), log=False) is None
    assert d.requests == []


# ---------- D-5 / A3: scrub, then cap ----------

LEAD = "tool output line " * 30


@pytest.mark.parametrize("secret,keep", [("AGENT_TOKEN=cVMjXl1uWH1c9Ogzoc_-k60yOL5KP5pr", 19),
                                          ("sk-3c3d5f1e8a2b4c6d9e0f1234567890ab", 10)], ids=["named-token", "sk-key"])
def test_a_secret_straddling_the_cap_never_reaches_the_request(double, secret, keep):
    # AF-AP-127: capped first, the cut leaves 7 value characters, under each rule's floor (a named value needs 8, an
    # sk- key 12), so that stub would be sent; scrubbed first, nothing of the value is.
    stub = secret[keep - 7:keep]
    cap = len(LEAD) + keep
    d = double()
    assert jev.ask(LEAD + secret, "is it?", url=d.url, max_chars=cap, log=False) is not None
    assert jev.rank(LEAD + secret, [LEAD + secret], url=d.url, max_chars=cap, log=False) is not None
    body = b"".join(r["body"] for r in d.requests).decode()
    assert stub not in body, "a %d-char stub of the secret was sent" % len(stub)
    ask_req, rank_req = d.posts()
    assert len(ask_req["state"]) == cap and ask_req["state"].startswith(LEAD)          # the cap did apply
    assert len(rank_req["state"]["query"]) == cap and len(rank_req["state"]["chunks"][0]["text"]) == cap


def test_every_scrubber_class_is_removed_from_every_text_sent(double):
    d = double()
    blob = "KEEP-ME " + " ".join(PLANTED)
    assert jev.ask(blob, "instr " + PLANTED[0], url=d.url, log=False) is not None
    assert jev.rank(blob, [blob, "plain"], instructions="rank " + PLANTED[4], url=d.url, log=False) is not None
    assert jev.classify(blob, ["label " + PLANTED[1], "other"], url=d.url, log=False) is not None
    sent = b"".join(r["body"] for r in d.requests).decode()
    for s in RAW_SECRETS:
        assert s not in sent, "secret sent: %s..." % s[:10]
    assert sent.count("KEEP-ME") == 4 and "<redacted>" in sent


# ---------- D-076 (b): the rank window budget (VERIFY-JT1 F-24) ----------
# The query and each chunk share Laya's 1,024-token window after a head of up to 256 tokens, and the server puts the
# query first; live, a query of about 3,900 characters tied every chunk at 0.4958 with fan_out 3 and rc 0. After the
# scrub, rank cuts the query to 1,000 characters and each chunk to 2,500; a rank whose scores are all equal is refused.

def test_rank_cuts_the_query_to_1000_and_each_chunk_to_2500_characters(double):
    d = double()
    query = "why did pytest fail? " + "E   FileNotFoundError: No such file or directory: '/tmp/ps/bt'\n" * 70
    chunk = "a note about the basetemp parent " * 120
    assert len(query) > 4000 and len(chunk) > 3000
    assert jev.rank(query, [chunk, "a short note"], url=d.url, log=False) is not None
    (req,) = d.posts()
    assert req["state"]["query"] == query[:1000]
    assert [c["text"] for c in req["state"]["chunks"]] == [chunk[:2500], "a short note"]
    assert jev.rank(query, [chunk, "b"], url=d.url, max_chars=300, log=False) is not None     # the smaller cut wins
    req = d.posts()[1]
    assert (len(req["state"]["query"]), len(req["state"]["chunks"][0]["text"])) == (300, 300)
    r = cli("rank", "--url", d.url, "--no-log", "--query", query, "--chunk", chunk, "--chunk", "b")
    assert r.returncode == 0, r.stderr
    req = d.posts()[2]
    assert (len(req["state"]["query"]), len(req["state"]["chunks"][0]["text"])) == (1000, 2500)


@pytest.mark.parametrize("where,cut", [("query", 1000), ("chunk", 2500)])
def test_a_secret_straddling_the_window_cut_never_reaches_the_request(double, where, cut):
    # scrub, THEN cut (AF-AP-127): cut first, 7 value characters would be left, under the named rule's floor of 8
    secret = "AGENT_TOKEN=cVMjXl1uWH1c9Ogzoc_-k60yOL5KP5pr"
    text = ("w " * cut)[:cut - 20] + " " + secret + " and the rest of the line"
    assert text[:cut].endswith("AGENT_TOKEN=cVMjXl1")
    d = double()
    args = (text, ["x", "y"]) if where == "query" else ("q", [text, "y"])
    assert jev.rank(*args, url=d.url, log=False) is not None
    (req,) = d.posts()
    sent = req["state"]["query"] if where == "query" else req["state"]["chunks"][0]["text"]
    assert len(sent) == cut and "cVMjXl1" not in d.requests[0]["body"].decode()


def test_rank_refuses_a_signal_free_ranking_whose_scores_are_all_equal(double, tmp_path):
    tie = double(ok_behaviour({"c0": 0.4958, "c1": 0.4958, "c2": 0.4958}))       # F-24's live answer
    log = tmp_path / "calls.jsonl"
    assert jev.rank("q", ["a", "b", "c"], url=tie.url, log_path=log) is None
    assert jev.last_reason == "url: signal-free rank: all 3 chunks scored 0.4958"
    (e,) = [json.loads(x) for x in log.read_text().splitlines()]
    assert (e["ok"], e["reason"]) == (False, "url: signal-free rank: all 3 chunks scored 0.4958")
    r = cli("rank", "--url", tie.url, "--no-log", "--query", "q", "--chunk", "a", "--chunk", "b", "--chunk", "c")
    assert (r.returncode, r.stdout) == (3, "")
    assert r.stderr.splitlines() == ["jev: unavailable: url: signal-free rank: all 3 chunks scored 0.4958"]
    near = double(ok_behaviour({"c0": 0.49581, "c1": 0.49584}))                  # equal to 4 decimals: refused
    assert jev.rank("q", ["a", "b"], url=near.url, log=False) is None
    assert jev.last_reason == "url: signal-free rank: all 2 chunks scored 0.4958"
    spread = double(ok_behaviour({"c0": 0.4958, "c1": 0.4959}))                 # a spread at the 4th decimal ranks
    assert jev.rank("q", ["a", "b"], url=spread.url, log=False)["ranking"] == [["c1", 0.4959], ["c0", 0.4958]]
    one = double(ok_behaviour({"c0": 0.4958}))                                   # one chunk is never refused
    assert jev.rank("q", ["a"], url=one.url, log=False)["ranking"] == [["c0", 0.4958]]


# ---------- D-6 / A4: the call log ----------

def test_call_log_never_holds_the_state_and_has_the_modes(double, tmp_path):
    marker = "MARKER-7f3a-state-text"
    d = double()
    log = tmp_path / "jevlog" / "calls.jsonl"
    jev.ask("before " + marker, "is it?", url=d.url, log_path=log)
    jev.rank(marker + " query", [marker + " chunk", "x"], url=d.url, log_path=log)
    jev.classify(marker, ["a", "b"], url=d.url, log_path=log)
    sent = b"".join(r["body"] for r in d.requests).decode()
    assert sent.count(marker) == 4                         # the marker WAS sent, so its absence below means something
    text = log.read_text()
    assert marker not in text and "before" not in text
    assert stat.S_IMODE(os.stat(log.parent).st_mode) == 0o700
    assert stat.S_IMODE(os.stat(log).st_mode) == 0o600
    lines = [json.loads(x) for x in text.splitlines()]
    keys = {"ts", "venue", "cmd", "n_questions", "qtypes", "state_sha256", "answers", "latency_ms", "ok", "reason"}
    assert len(lines) == 3 and all(set(e) == keys for e in lines)
    assert [(e["cmd"], e["n_questions"], e["qtypes"], e["ok"]) for e in lines] == [
        ("ask", 1, ["noul"], True), ("rank", 2, ["noul"], True), ("classify", 1, ["choice"], True)]
    for e, req in zip(lines, d.posts()):               # the hash is of the state exactly as it was sent
        canon = json.dumps(req["state"], sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        assert e["state_sha256"] == hashlib.sha256(canon).hexdigest()
        assert e["answers"] == shaped_reply(req)["answers"]


def test_a_failed_call_is_logged_with_its_reason_and_no_log_writes_nothing(refused_url, tmp_path):
    log = tmp_path / "calls.jsonl"
    assert jev.health(url=refused_url, log_path=log) is None
    (e,) = [json.loads(x) for x in log.read_text().splitlines()]
    assert (e["ok"], e["venue"], e["reason"], e["answers"], e["state_sha256"]) == (
        False, None, "url: connection refused", None, None)
    log2 = tmp_path / "none" / "calls.jsonl"
    jev.health(url=refused_url, log=False, log_path=log2)
    r = cli("health", "--url", refused_url, "--no-log", "--log-file", str(log2))
    assert r.returncode == 3 and not log2.exists() and not log2.parent.exists()


# ---------- D-3 / A5: the PC path through an injected runner ----------

def bridge_env(tmp_path):
    p = tmp_path / "fake-bridge.env"
    p.write_text("PC_BRIDGE_URL=%s\nPC_BRIDGE_TOKEN=%s\n" % (FAKE_URL, FAKE_TOKEN))
    return p


def request_in(cmd):
    m = re.search(r"printf %s '([A-Za-z0-9+/=]+)' \| base64 -d \| curl ", cmd)
    assert m, cmd[:120]
    return json.loads(base64.b64decode(m.group(1)))


def runner_replying(place):
    calls = []

    def run(cmd, url, token, attempts=3, max_time=110):
        calls.append({"cmd": cmd, "url": url, "token": token, "attempts": attempts, "max_time": max_time})
        sys.stderr.write("pc_bridge_exec: curl exited 6: could not resolve %s\n" % FAKE_URL)   # must never surface
        body = json.dumps(shaped_reply(request_in(cmd)))
        out = {"status-line": body + "\n200" + BIND_WARNING + "\n",
               "data-line": body + BIND_WARNING + "\n200\n",
               "leading": BIND_WARNING + "\n" + body + "\n200\n",
               "none": body + "\n200\n"}[place]
        return {"rc": 0, "stdout": out, "stderr": ""}
    return run, calls


@pytest.mark.parametrize("place", ["none", "status-line", "data-line", "leading"])
def test_pc_path_sends_the_request_base64_encoded_and_survives_the_bind_warning(tmp_path, capsys, place):
    run, calls = runner_replying(place)
    res = jev.rank("the query", ["one", "two"], venue="pc", bridge_env=bridge_env(tmp_path), runner=run, log=False)
    assert res is not None, jev.last_reason
    assert res["venue"] == "pc" and res["fan_out"] == 2
    (c,) = calls
    assert (c["url"], c["token"], c["attempts"]) == (FAKE_URL, FAKE_TOKEN, 1)
    assert FAKE_TOKEN not in c["cmd"] and FAKE_URL not in c["cmd"]
    assert "curl -sS --noproxy '*'" in c["cmd"] and "--data-binary @- " in c["cmd"]
    assert c["cmd"].endswith(" http://127.0.0.1:47411/v1/systemone")
    req = request_in(c["cmd"])
    assert req["state"] == {"query": "the query", "chunks": [{"id": "c0", "text": "one"}, {"id": "c1", "text": "two"}]}
    assert capsys.readouterr().err == ""


def test_pc_health_is_a_curl_get_on_the_pc_loopback(tmp_path):
    seen = []

    def run(cmd, url, token, attempts=3, max_time=110):
        seen.append(cmd)
        return {"rc": 0, "stdout": '{"ok": true}' + BIND_WARNING + "\n200\n", "stderr": ""}
    res = jev.health(venue="pc", bridge_env=bridge_env(tmp_path), runner=run, log=False)
    assert res["health"] == {"ok": True} and res["venue"] == "pc"
    assert seen[0].startswith("curl -sS --noproxy '*' -m ") and seen[0].endswith(" http://127.0.0.1:47411/health")


@pytest.mark.parametrize("env,reason", [
    ({"rc": 7, "stdout": "", "stderr": "curl: (7) Failed to connect to 127.0.0.1 port 47411"},
     "pc: remote rc 7 (curl: (7) Failed to connect to 127.0.0.1 port 47411)"),
    ({"rc": 0, "stdout": '{"error": "model not loaded"}\n503\n', "stderr": ""}, "pc: HTTP 503 (model not loaded)"),
    ({"rc": 0, "stdout": "not json\n200\n", "stderr": ""}, "pc: non-JSON reply"),
    ({"rc": 0, "stdout": BIND_WARNING, "stderr": ""}, "pc: no HTTP status in the bridge reply"),
    ({"rc": 4, "stdout": "", "stderr": "bridge error"}, "pc: remote rc 4 (bridge error)"),
], ids=["curl-refused", "http503", "non-json", "no-status", "bridge-error"])
def test_pc_failures_fail_open(tmp_path, capsys, env, reason):
    res = jev.ask("s", "i?", venue="pc", bridge_env=bridge_env(tmp_path), runner=lambda *a, **k: env, log=False)
    assert res is None and jev.last_reason == reason
    assert capsys.readouterr().err == ""


def test_pc_without_a_bridge_env_is_unavailable_and_never_runs(tmp_path):
    ran = []
    res = jev.ask("s", "i?", venue="pc", bridge_env=tmp_path / "absent.env", runner=lambda *a, **k: ran.append(a), log=False)
    assert res is None and jev.last_reason == "pc: no bridge env file" and ran == []


def test_auto_prefers_a_healthy_local_endpoint(double, tmp_path, monkeypatch):
    d = double()
    monkeypatch.setattr(jev, "LOCAL_URL", d.url)
    ran = []
    res = jev.ask("s", "i?", bridge_env=bridge_env(tmp_path), runner=lambda *a, **k: ran.append(a), log=False)
    assert res["venue"] == "local" and ran == []
    assert [r["path"] for r in d.requests] == ["/health", "/v1/systemone"]


def test_auto_falls_back_to_the_pc_when_local_is_refused_or_slow(double, refused_url, tmp_path, monkeypatch):
    run, calls = runner_replying("data-line")
    monkeypatch.setattr(jev, "LOCAL_URL", refused_url)
    res = jev.rank("q", ["a"], bridge_env=bridge_env(tmp_path), runner=run, log=False)
    assert res["venue"] == "pc" and len(calls) == 1
    slow = double(lambda m, p, b: (200, {"ok": True}, 2.0))            # /health must answer within 1 s (D-3)
    monkeypatch.setattr(jev, "LOCAL_URL", slow.url)
    res = jev.rank("q", ["a"], bridge_env=bridge_env(tmp_path), runner=run, log=False)
    assert res["venue"] == "pc" and len(calls) == 2
    assert [r["path"] for r in slow.requests] == ["/health"]
    both_down = jev.rank("q", ["a"], bridge_env=tmp_path / "absent.env", runner=run, log=False)
    assert both_down is None and jev.last_reason.startswith("local: ") and "; pc: no bridge env file" in jev.last_reason


# ---------- jev_local.sh (offline branches; the live start/stop is in the lane report) ----------

def local_copy(tmp_path, port):
    """jev_local.sh with only its port and snapshot path swapped, so no branch here can reach the real server."""
    (tmp_path / "scripts").mkdir(parents=True)
    text = LOCAL_SH.read_text()
    assert text.count("PORT=47411\n") == 1 and text.count("SNAPSHOT=$HF_HOME_DIR/hub/") == 1
    text = text.replace("PORT=47411\n", "PORT=%d\n" % port)
    text = re.sub(r"SNAPSHOT=\$HF_HOME_DIR/hub/\S+", "SNAPSHOT=%s" % (tmp_path / "no-such-snapshot"), text)
    p = tmp_path / "scripts" / "jev_local.sh"
    p.write_text(text)
    return p


def sh(script, *args):
    return subprocess.run(["bash", str(script), *args], capture_output=True, text=True, timeout=30)


def test_jev_local_does_not_count_a_squatter_on_its_port_as_its_server(double, tmp_path):
    # AF-AP-33: an ok /health alone would accept any process on the port; the pinned revision must match too
    pinned = re.search(r"^REVISION=([0-9a-f]{40})$", LOCAL_SH.read_text(), re.M).group(1)
    squat = double(lambda m, p, b: (200, {"ok": True, "revision": "0" * 40}, 0))
    s1 = local_copy(tmp_path / "squat", int(squat.url.rsplit(":", 1)[1]))
    assert (sh(s1, "status").returncode, sh(s1, "status").stdout) == (3, "down\n")
    r = sh(s1, "start")
    assert r.returncode == 2 and "no Laya snapshot" in r.stderr          # it did not take the squatter for itself
    ours = double(lambda m, p, b: (200, {"ok": True, "revision": pinned}, 0))
    s2 = local_copy(tmp_path / "ours", int(ours.url.rsplit(":", 1)[1]))
    r = sh(s2, "status")
    assert r.returncode == 0 and json.loads(r.stdout) == {"ok": True, "revision": pinned}
    r = sh(s2, "start")
    assert r.returncode == 0 and r.stdout.startswith("jev_local: already running: ")


def test_jev_local_names_a_missing_snapshot_and_reports_down(tmp_path, refused_url):
    port = int(refused_url.rsplit(":", 1)[1])
    sh = local_copy(tmp_path, port)
    r = subprocess.run(["bash", str(sh), "start"], capture_output=True, text=True, timeout=30)
    assert r.returncode == 2 and r.stdout == ""
    assert r.stderr.splitlines() == ["jev_local: no Laya snapshot at %s" % (tmp_path / "no-such-snapshot")]
    assert not (tmp_path / ".jev" / "server.pid").exists()
    r = subprocess.run(["bash", str(sh), "status"], capture_output=True, text=True, timeout=30)
    assert (r.returncode, r.stdout) == (3, "down\n")
    r = subprocess.run(["bash", str(sh), "stop"], capture_output=True, text=True, timeout=30)
    assert (r.returncode, r.stdout) == (0, "jev_local: not running (no pidfile)\n")


# A STAND-IN for the model server, used only to test the launcher's own mechanics (setsid nohup, the pidfile, idempotent
# start while loading, stop by pid). It answers /health with the pinned revision and the argv it was given; it never
# answers a model question. The real server's start is not re-run here: the lane adopted the running one (D-7).
STAND_IN = r'''
import http.server, json, sys, time
args = sys.argv[1:]
port = int(args[args.index("--port") + 1])
time.sleep(1.0)
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        ok = self.path == "/health"                      # the real server answers 404 on any other path
        body = json.dumps({"ok": True, "revision": REV, "argv": args} if ok else {"error": "not found"}).encode()
        self.send_response(200 if ok else 404)
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def log_message(self, *a):
        pass
http.server.HTTPServer(("127.0.0.1", port), H).serve_forever()
'''


def _alive(pid):
    try:
        with open("/proc/%d/stat" % pid) as fh:
            return fh.read().rsplit(")", 1)[1].split()[0] != "Z"
    except OSError:
        return False


def test_jev_local_start_is_idempotent_and_stop_kills_only_its_pid(tmp_path):
    pinned = re.search(r"^REVISION=([0-9a-f]{40})$", LOCAL_SH.read_text(), re.M).group(1)
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    script = local_copy(tmp_path, port)
    text = script.read_text().replace("SNAPSHOT=%s" % (tmp_path / "no-such-snapshot"), "SNAPSHOT=%s" % tmp_path)
    assert text.count("PY=/root/venv-laya-probe/bin/python\n") == 1
    script.write_text(text.replace("PY=/root/venv-laya-probe/bin/python\n", "PY=%s\n" % sys.executable))
    (tmp_path / "scripts" / "laya_systemone_server.py").write_text(STAND_IN.replace("REV", repr(pinned)))
    pidfile = tmp_path / ".jev" / "server.pid"
    pid = None
    try:
        r = sh(script, "start", "--threads", "3")
        assert r.returncode == 0 and r.stdout.startswith("jev_local: started (pid "), (r.stdout, r.stderr)
        pid = int(pidfile.read_text())
        assert "laya_systemone_server.py" in open("/proc/%d/cmdline" % pid).read()   # the pid IS the server process
        assert stat.S_IMODE(os.stat(tmp_path / ".jev").st_mode) == 0o700
        r = sh(script, "start")                                   # still loading: no second start
        assert r.returncode == 0 and r.stdout == "jev_local: already starting (pid %d); /health answers once the model has loaded\n" % pid
        for _ in range(100):
            r = sh(script, "status")
            if r.returncode == 0:
                break
            time.sleep(0.1)
        health = json.loads(r.stdout)
        assert health["argv"] == ["--device", "cpu", "--threads", "3", "--host", "127.0.0.1", "--port", str(port),
                                  "--hf-home", "/root/hf-laya-probe"]
        r = sh(script, "start")
        assert r.returncode == 0 and r.stdout.startswith("jev_local: already running: ") and int(pidfile.read_text()) == pid
        r = sh(script, "stop")
        assert (r.returncode, r.stdout) == (0, "jev_local: stopped (pid %d)\n" % pid)
        assert not _alive(pid) and not pidfile.exists()
        assert sh(script, "status").stdout == "down\n"
        # a pidfile naming some other live process: stop removes the pidfile and never signals that process
        other = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
        try:
            pidfile.write_text("%d\n" % other.pid)
            r = sh(script, "stop")
            assert (r.returncode, r.stdout) == (0, "jev_local: the pidfile named no running server; removed it\n")
            assert other.poll() is None and not pidfile.exists()
        finally:
            other.kill()
            other.wait()
    finally:
        if pid and _alive(pid):
            os.kill(pid, 9)


@pytest.mark.parametrize("args", [[], ["restart"], ["start", "--threads", "0"], ["start", "--threads", "two"],
                                  ["stop", "now"], ["status", "-v"]])
def test_jev_local_usage_errors_exit_64(args):
    r = subprocess.run(["bash", str(LOCAL_SH), *args], capture_output=True, text=True, timeout=30)
    assert r.returncode == 64 and r.stdout == "" and r.stderr.startswith("jev_local: ")
