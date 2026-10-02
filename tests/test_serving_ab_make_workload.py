"""Self-test of scripts/serving_ab/make_workload.py against a local /tokenize stand-in (task #462).

The stand-in counts two tokens per word, four per chat message and four for the generation prompt, so every
count is even: an odd target can never be hit exactly, and the longest prompt within it is target - 1. That
makes a stored count that was not measured (the target itself, or the first count over it) visible."""
import http.server
import json
import pathlib
import sys
import threading

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
from serving_ab import make_workload  # noqa: E402

FAKE_KEY = "k" + "x" * 11  # a fake, built at run time


def fake_count(body):
    if "messages" in body:
        words = sum(len(m["content"].split()) for m in body["messages"])
        return 2 * words + 4 * len(body["messages"]) + (4 if body.get("add_generation_prompt") else 0)
    return 2 * len(body["prompt"].split())


class Handler(http.server.BaseHTTPRequestHandler):
    max_len = 4000
    seen = []

    def log_message(self, *a):
        pass

    def answer(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        req = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        Handler.seen.append(req)
        if self.path != "/tokenize":
            return self.answer(404, {"error": "no such path"})
        if self.headers.get("Authorization") != "Bearer " + FAKE_KEY:
            return self.answer(401, {"error": "Unauthorized"})
        n = fake_count(req)
        self.answer(200, {"count": n, "max_model_len": Handler.max_len, "tokens": [7] * n, "token_strs": None})


@pytest.fixture()
def server():
    Handler.max_len, Handler.seen = 4000, []
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    th = threading.Thread(target=srv.serve_forever, daemon=True)
    th.start()
    yield f"http://127.0.0.1:{srv.server_address[1]}/tokenize"
    srv.shutdown()


def build(server, tmp_path, *extra, key=None, files=12):
    sysf = tmp_path / "system.md"
    sysf.write_text("You are a test agent with a short system prompt.\n")
    corpus = tmp_path / "corpus"
    corpus.mkdir(exist_ok=True)
    for i in range(files):
        (corpus / f"f{i:02d}.md").write_text("\n".join(f"w{i}_{k} " * 8 for k in range(60)))
    keyf = tmp_path / "key"
    keyf.write_text((FAKE_KEY if key is None else key) + "\n")
    out = tmp_path / "wl.json"
    rc = make_workload.main(["--tokenize-url", server, "--model", "m", "--api-key-file", str(keyf),
                             "--system-file", str(sysf), "--corpus", str(corpus), "--turns", "3",
                             "--turn-tokens", "121", "--max-reply-tokens", "40", *extra, "--out", str(out)])
    return rc, out


def chat_count(system, contents):
    return fake_count({"messages": [{"role": "system", "content": system}] +
                       [{"role": "user", "content": c} for c in contents], "add_generation_prompt": True})


def test_first_prompts_land_one_under_their_odd_targets(server, tmp_path):
    rc, out = build(server, tmp_path, "--first-prompt-tokens", "901,601,751")
    assert rc == 0
    wl = json.loads(out.read_text())
    assert wl["system"].startswith("Run id: 00000000.\n") and wl["ctx_limit"] == 4000
    assert [c["target"] for c in wl["chats"]] == [901, 601, 751]
    for c in wl["chats"]:
        first = c["turns"][0]["content"]
        assert first.endswith("\n\n" + make_workload.QUESTION)
        # an independent count of the stored first prompt: the longest one within an odd target
        assert c["first_prompt_tokens"] == chat_count(wl["system"], [first]) == c["target"] - 1
        assert len(c["turns"]) == 3
        for t in c["turns"][1:]:
            assert t["content_tokens"] == fake_count({"prompt": t["content"]}) == 120
        assert c["worst_last_prompt_tokens"] + 40 <= wl["ctx_limit"]


def test_chats_share_no_file_and_turns_follow_on(server, tmp_path):
    rc, out = build(server, tmp_path, "--first-prompt-tokens", "901,601,751")
    wl = json.loads(out.read_text())
    seen = {}
    for c in wl["chats"]:
        names = [n for t in c["turns"] for n in t["files"]]
        for n in names:
            assert seen.setdefault(n, c["idx"]) == c["idx"], f"{n} in two chats"
        for t in c["turns"]:
            for n in t["files"]:
                assert f"=== file: {n} ===" in t["content"]
    assert len(seen) >= 6


def test_a_workload_over_the_context_limit_stops_the_build(server, tmp_path):
    Handler.max_len = 1100  # 901 + two 120-token turns + two 80-token replies + a 40-token reply passes it
    with pytest.raises(SystemExit) as e:
        build(server, tmp_path, "--first-prompt-tokens", "901")
    assert e.value.code == 2 and not (tmp_path / "wl.json").exists()


def test_a_corpus_too_small_stops_the_build(server, tmp_path, capsys):
    with pytest.raises(SystemExit) as e:
        build(server, tmp_path, "--first-prompt-tokens", "99999")
    assert e.value.code == 2 and "too small" in capsys.readouterr().err


def test_a_target_below_the_base_prompt_stops_the_build(server, tmp_path, capsys):
    with pytest.raises(SystemExit) as e:
        build(server, tmp_path, "--first-prompt-tokens", "9")
    assert e.value.code == 2 and "below the prompt" in capsys.readouterr().err


def test_a_wrong_key_stops_the_build_and_is_never_printed(server, tmp_path, capsys):
    with pytest.raises(SystemExit) as e:
        build(server, tmp_path, "--first-prompt-tokens", "901", key="y" * 12)
    cap = capsys.readouterr()
    assert e.value.code == 2 and "HTTP 401" in cap.err
    assert FAKE_KEY not in cap.err + cap.out and "y" * 12 not in cap.err + cap.out


def test_refuses_existing_out(server, tmp_path):
    (tmp_path / "wl.json").write_text("{}")
    with pytest.raises(SystemExit) as e:
        build(server, tmp_path, "--first-prompt-tokens", "901")
    assert e.value.code == 2 and Handler.seen == []


def test_the_thinking_setting_reaches_every_chat_count(server, tmp_path):
    build(server, tmp_path, "--first-prompt-tokens", "901")
    chat = [r for r in Handler.seen if "messages" in r]
    assert chat and all(r["chat_template_kwargs"] == {"enable_thinking": False} for r in chat)
    assert all(r["model"] == "m" for r in Handler.seen)


def test_the_worst_last_prompt_counts_each_reply_at_its_cap_plus_the_margin(server, tmp_path):
    # a 10-token cap: "word " x 10 counts 20 here, under 10 + the 16-token margin, so the dummy must grow
    rc, out = build(server, tmp_path, "--first-prompt-tokens", "901", "--max-reply-tokens", "10")
    c = json.loads(out.read_text())["chats"][0]
    follow = sum(4 + t["content_tokens"] for t in c["turns"][1:])
    replies = (len(c["turns"]) - 1) * (4 + 10 + make_workload.REPLY_MARGIN)
    assert c["worst_last_prompt_tokens"] >= c["first_prompt_tokens"] + follow + replies
