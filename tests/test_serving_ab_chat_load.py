"""Self-test of scripts/serving_ab/chat_load.py's replay against a local HTTP server that streams like an
OpenAI-compatible one (task #462).

It checks the harness's own accounting (first-token time, decode rate, usage, errors, the loop flag, the
plan check, the summary), the cut and retry of a request with no first event (task #454's second window),
and that the replay sends the workload's text byte for byte; the A/B itself runs only against the real
servers."""
import http.server
import json
import pathlib
import sys
import threading
import time

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from serving_ab import chat_load  # noqa: E402

FAKE_KEY = "k" + "x" * 11  # a fake, built at run time
RUN_ID_LINE = "Run id: 00000000."


class Handler(http.server.BaseHTTPRequestHandler):
    """Modes: ok (first event after 0.3 s); err (503); loop (a looping reply); slow_first (the first attempt of each
    request waits 1.0 s before its first event, a later attempt of the same request 0.1 s: a server that kept the
    work of the cut attempt); always_slow (every attempt waits 1.0 s); stall (the first event after 0.1 s, then 1.0 s
    of nothing)."""
    mode = "ok"
    seen = []
    attempts = {}
    disconnects = 0

    def log_message(self, *a):
        pass

    def refuse(self, code):
        body = b'{"error":"refused"}'
        self.send_response(code)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path != "/metrics":
            return self.refuse(404)
        if self.headers.get("Authorization") != "Bearer " + FAKE_KEY:
            return self.refuse(401)
        body = b"# HELP x\nvllm:num_preemptions_total 0.0\nvllm:prefix_cache_hits_total 5.0\nother 1\n"
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        n = int(self.headers["Content-Length"])
        req = json.loads(self.rfile.read(n))
        Handler.seen.append({"auth": self.headers.get("Authorization"), "req": req})
        if self.path != "/v1/chat/completions":
            return self.refuse(404)
        if self.headers.get("Authorization") != "Bearer " + FAKE_KEY:
            return self.refuse(401)
        if Handler.mode == "err":
            body = b'{"error":"busy"}'
            self.send_response(503)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        delay = 0.3  # the first token arrives after 0.3 s
        if Handler.mode in ("slow_first", "always_slow"):
            k = json.dumps(req["messages"], sort_keys=True)
            n = Handler.attempts.get(k, 0)
            Handler.attempts[k] = n + 1
            delay = 1.0 if Handler.mode == "always_slow" or n == 0 else 0.1
        elif Handler.mode == "stall":
            delay = 0.1
        time.sleep(delay)
        words = ["ab " * 1000] if Handler.mode == "loop" else ["Hello", " there", "."]
        try:
            for i, w in enumerate(words):
                ev = {"choices": [{"index": 0, "delta": {"content": w}}]}
                self.wfile.write(f"data: {json.dumps(ev)}\n\n".encode())
                self.wfile.flush()
                time.sleep(1.0 if Handler.mode == "stall" and i == 0 else 0.1)
            usage = {"prompt_tokens": 1234, "completion_tokens": 30, "prompt_tokens_details": {"cached_tokens": 1000}}
            self.wfile.write(f"data: {json.dumps({'choices': [], 'usage': usage})}\n\n".encode())
            self.wfile.write(b"data: [DONE]\n\n")
        except (BrokenPipeError, ConnectionResetError):
            Handler.disconnects += 1  # the client left first


@pytest.fixture()
def server():
    Handler.mode, Handler.seen, Handler.attempts, Handler.disconnects = "ok", [], {}, 0
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    yield f"http://127.0.0.1:{srv.server_address[1]}/v1"
    srv.shutdown()


def workload(planned=(1234, 1200, 999)):
    chats = [{"idx": i, "target": 0, "first_prompt_tokens": p, "worst_last_prompt_tokens": 0,
              "turns": [{"content": f"chat {i} turn {t} text", "files": [], "content_tokens": 5} for t in (1, 2)]}
             for i, p in enumerate(planned)]
    return {"version": 1, "thinking": "off", "max_reply_tokens": 64, "turns": 2, "run_id_line": RUN_ID_LINE,
            "system": RUN_ID_LINE + "\nYou are a test.\n", "chats": chats}


def run(server, tmp_path, *extra, key=None, wl=None):
    wlf = tmp_path / "wl.json"
    wlf.write_text(json.dumps(wl or workload()))
    keyf = tmp_path / "key"
    keyf.write_text((FAKE_KEY if key is None else key) + "\n")
    out = tmp_path / "out"
    rc = chat_load.main(["--arm", "t", "--base-url", server, "--model", "m", "--api-key-file", str(keyf),
                         "--workload", str(wlf), "--chats", "2", "--stagger-s", "0", "--out", str(out), *extra])
    return rc, out


def records(out):
    return [json.loads(x) for x in (out / "requests.jsonl").read_text().splitlines()]


def test_records_and_summary(server, tmp_path, capsys):
    rc, out = run(server, tmp_path)
    assert rc == 0
    recs = records(out)
    assert sorted((r["chat"], r["turn"]) for r in recs) == [(0, 1), (0, 2), (1, 1), (1, 2)]
    for r in recs:
        assert r["status"] == 200 and r["error"] is None and r["usage_seen"]
        assert 0.25 <= r["ttft_s"] < 5 and r["ttft_s"] <= r["total_s"] - 0.2, r
        assert r["prompt_tokens"] == 1234 and r["completion_tokens"] == 30 and r["cached_tokens"] == 1000
        assert r["decode_tok_s"] > 0 and not r["loop"] and not r["over_limit"]
        assert r["planned_prompt_tokens"] == ({0: 1234, 1: 1200}[r["chat"]] if r["turn"] == 1 else None)
        assert r["attempts"] == 1 and r["cuts"] == 0 and not r["cut"] and abs(r["attempt_ttft_s"] - r["ttft_s"]) < 0.01
    s = json.loads((out / "summary.json").read_text())
    assert s["requests"] == 4 and s["ok"] == 4 and s["errors"] == 0 and s["missed_80s"] == 0
    assert s["cut_requests"] == 0 and s["unanswered"] == 0
    assert s["turn1_plan_diff_max"] == 34  # chat 1 planned 1200, the server counted 1234
    assert (out / "metrics-before.txt").read_text().splitlines() == [
        "vllm:num_preemptions_total 0.0", "vllm:prefix_cache_hits_total 5.0"]
    # the key went in the header and nowhere in the outputs or the printed text
    assert all(x["auth"] == "Bearer " + FAKE_KEY for x in Handler.seen)
    printed = capsys.readouterr().out
    for f in out.iterdir():
        assert FAKE_KEY not in f.read_text(), f.name
    assert FAKE_KEY not in printed


def test_the_replay_sends_the_workload_text_and_settings(server, tmp_path):
    rc, out = run(server, tmp_path)
    reqs = [x["req"] for x in Handler.seen]
    run_id = json.loads((out / "run.json").read_text())["run_id"]
    assert len(run_id) == 8 and run_id.isdigit()
    for r in reqs:
        assert r["messages"][0]["content"] == f"Run id: {run_id}.\nYou are a test.\n"
        assert r["max_tokens"] == 64 and r["chat_template_kwargs"] == {"enable_thinking": False}
    first = sorted((r for r in reqs if len(r["messages"]) == 2), key=lambda r: r["messages"][1]["content"])
    assert [r["messages"][1]["content"] for r in first] == ["chat 0 turn 1 text", "chat 1 turn 1 text"]
    second = sorted((r for r in reqs if len(r["messages"]) == 4), key=lambda r: r["messages"][3]["content"])
    assert [r["messages"][3]["content"] for r in second] == ["chat 0 turn 2 text", "chat 1 turn 2 text"]
    assert all(r["messages"][2] == {"role": "assistant", "content": "Hello there."} for r in second)


def test_each_run_gets_its_own_run_id(server, tmp_path):
    ids = set()
    for k in range(3):
        sub = tmp_path / str(k)
        sub.mkdir()
        rc, out = run(server, sub)
        ids.add(json.loads((out / "run.json").read_text())["run_id"])
    assert len(ids) == 3


def test_server_error_is_recorded_not_raised(server, tmp_path):
    Handler.mode = "err"
    rc, out = run(server, tmp_path, "--stop-chat-on-error")
    assert rc == 0
    recs = records(out)
    assert len(recs) == 2 and all(r["status"] == 503 and "busy" in r["error"] and r["over_limit"] for r in recs)
    s = json.loads((out / "summary.json").read_text())
    assert s["errors"] == 2 and s["ok"] == 0 and s["missed_80s"] == 2 and s["turn1_plan_diff_max"] is None


def test_loop_flag(server, tmp_path):
    Handler.mode = "loop"
    rc, out = run(server, tmp_path)
    assert all(r["loop"] for r in records(out))
    assert json.loads((out / "summary.json").read_text())["loops"] == 4


def test_refuses_existing_out(server, tmp_path):
    (tmp_path / "out").mkdir()
    with pytest.raises(SystemExit) as e:
        run(server, tmp_path)
    assert e.value.code == 2


def test_refuses_more_chats_than_the_workload_holds(server, tmp_path):
    with pytest.raises(SystemExit) as e:
        run(server, tmp_path, "--chats", "4")
    assert e.value.code == 2 and not (tmp_path / "out").exists() and Handler.seen == []


def test_refuses_a_workload_without_its_run_id_line(server, tmp_path):
    wl = workload()
    wl["system"] = "You are a test.\n"
    with pytest.raises(SystemExit) as e:
        run(server, tmp_path, wl=wl)
    assert e.value.code == 2 and Handler.seen == []


def test_unreachable_server_is_an_error_record(tmp_path):
    rc, out = run("http://127.0.0.1:9/v1", tmp_path, "--stop-chat-on-error")
    recs = records(out)
    assert rc == 0 and len(recs) == 2 and all(r["status"] is None and r["error"] for r in recs)


def test_wrong_key_is_refused_and_recorded(server, tmp_path):
    rc, out = run(server, tmp_path, "--stop-chat-on-error", key="y" * 12)
    recs = records(out)
    assert rc == 0 and len(recs) == 2 and all(r["status"] == 401 for r in recs)
    assert (out / "metrics-before.txt").read_text() == "\n"


def test_wrong_path_is_refused(server, tmp_path):
    rc, out = run(server.rsplit("/v1", 1)[0] + "/v2", tmp_path, "--stop-chat-on-error")
    assert all(r["status"] == 404 for r in records(out))


def test_a_cut_request_is_sent_again_and_answered(server, tmp_path):
    # OmniRoute ends a request with no event in its limit; Hermes sends it again. Here the server kept the cut
    # attempt's work, so the second attempt answers fast; the lane's wait still counts from the first attempt.
    Handler.mode = "slow_first"
    rc, out = run(server, tmp_path, "--cut-after", "0.5", "--retries", "2")
    recs = records(out)
    assert rc == 0 and len(recs) == 4
    for r in recs:
        assert r["status"] == 200 and r["error"] is None and not r["cut"], r
        assert r["attempts"] == 2 and r["cuts"] == 1
        assert r["attempt_ttft_s"] < 0.5 <= r["ttft_s"] < 1.0, r
    s = json.loads((out / "summary.json").read_text())
    assert s["cut_requests"] == 4 and s["unanswered"] == 0 and s["errors"] == 0 and s["ok"] == 4
    bodies = [json.dumps(x["req"], sort_keys=True) for x in Handler.seen]
    assert len(bodies) == 8 and all(bodies.count(b) == 2 for b in bodies)  # each retry resends the same request
    time.sleep(1.5)  # each cut attempt's handler wakes after 1.0 s and finds its client gone
    assert Handler.disconnects == 4


def test_a_request_cut_on_every_attempt_is_unanswered(server, tmp_path):
    Handler.mode = "always_slow"
    rc, out = run(server, tmp_path, "--cut-after", "0.3", "--retries", "1", "--stop-chat-on-error")
    recs = records(out)
    assert rc == 0 and len(recs) == 2
    for r in recs:
        assert r["cut"] and r["attempts"] == 2 and r["cuts"] == 2 and r["ttft_s"] is None and r["over_limit"]
        assert r["error"] == "cut: no event in 0.3 s", r["error"]
    s = json.loads((out / "summary.json").read_text())
    assert s["unanswered"] == 2 and s["cut_requests"] == 2 and s["missed_80s"] == 2 and s["errors"] == 2


def test_without_cut_after_a_slow_first_event_is_waited_for(server, tmp_path):
    Handler.mode = "always_slow"
    rc, out = run(server, tmp_path)
    recs = records(out)
    assert len(recs) == 4
    assert all(r["attempts"] == 1 and r["cuts"] == 0 and not r["cut"] and r["ttft_s"] >= 1.0 for r in recs)


def test_a_stall_after_the_first_event_is_a_timeout_not_a_cut(server, tmp_path):
    Handler.mode = "stall"
    rc, out = run(server, tmp_path, "--cut-after", "0.3", "--retries", "2", "--timeout", "0.5", "--stop-chat-on-error")
    recs = records(out)
    assert len(recs) == 2
    for r in recs:
        assert not r["cut"] and r["attempts"] == 1 and r["cuts"] == 0 and r["ttft_s"] is not None
        assert r["error"].startswith("TimeoutError"), r["error"]


@pytest.mark.parametrize("flag,value", [("--cut-after", "-1"), ("--cut-after", "nan"), ("--cut-after", "inf"),
                                        ("--retries", "-1"), ("--retries", "11")])
def test_refuses_a_bad_cut_or_retry_setting(server, tmp_path, capsys, flag, value):
    with pytest.raises(SystemExit) as e:
        run(server, tmp_path, flag, value)
    # the tool's own refusal, not argparse's ("unrecognized arguments" also exits 2)
    assert e.value.code == 2 and f"chat_load: {flag} " in capsys.readouterr().err
    assert not (tmp_path / "out").exists() and Handler.seen == []
