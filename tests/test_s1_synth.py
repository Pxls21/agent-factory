"""SYNTH1 (task #308, D-096): scripts/s1_synth.py on fixture transcripts, with local fake HTTP servers standing in for
the PC's vLLM and for OpenJev. No request reaches a real labeler and no real secret source is opened: the value gate
reads a fixture env file, and the vLLM key is a fixture file.

The oracles stay independent of the tool. The hook's ranking is recomputed by this file's own instances of the hook
(loaded by path, the four floors lifted here by name); a section's text is checked against its skill file line by
line; the fake servers keep the raw bytes they receive; every number the validator must give is a literal worked out
by hand below. The fixture records copy the SHAPE of real ones (keys and value types, as this session's transcripts hold
them) with fake content and fake secrets. Each test names the mutants of s1_synth.py that red it; the lane's mutation
run (SYNTH1 report) shows each mutant killed by a FAILED test.
"""
import datetime
import fcntl
import hashlib
import http.server
import importlib.util
import json
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import hook_context as HC  # noqa: E402  stamps a fixture injection (fixture data, never an oracle)
import s1_synth as SY  # noqa: E402
import transcript_export as TE  # noqa: E402

HOOK = ROOT / ".claude" / "hooks" / "system1-context.py"
SESSION = "fx-session-synth"
REPO = str(ROOT)
FLOORS = ("MIN_PROMPT_SCORE", "ONE_LEAD_MIN_SCORE", "SHORT_MIN_SCORE", "NAMED_MIN_SCORE")   # the brief's four gates
FORBIDDEN = ("prompt_logprobs", "best_of", "echo", "n")                                    # AF-AP-201, this file's copy
BODY_KEYS = {"model", "messages", "max_tokens", "temperature", "chat_template_kwargs"}
FAKE_KEY = "QZJ8-fake-vllm-key-5c1d9e7a"
SHAPED = ("QZJ8fakefakefake1234", "X4Z9fakefakefake5678", "QZJ8fakefakefakefake")   # values the scrubber's shapes take
PLAIN = "QZJ8plainwordvalue77"            # a value no shape takes: only the value gate stops it
ABSENT = "Qz7Kx9Vw2Jm4Pd8Rt6"              # a fixture source's value that the fixture never holds
KEEP = ("cnryprompt4a1", "cnrycommand4a2")                                             # must reach the items
DROP = ("cnrythinking4b1", "cnryassistant4b2", "cnrythinking4b3", "cnrydispatch4b4", "cnrytask4b5", "cnryinterrupt4b6",
        "cnrymeta4b7", "cnrycompact4b8", "cnryresult4b9", "cnryassistant4c1")          # must never leave
P1 = ("Write the delegate brief for the next build lane: the orchestration rules for briefs, the worktree pins and the "
      "parallel agents. Keep token=%s out of it; the passphrase is %s. %s" % (SHAPED[0], PLAIN, KEEP[0]))
BASH1 = ("git commit -m 'fixture' && bash scripts/pc.sh 'ls' && curl -H 'Authorization: Bearer %s' "
         "http://example.invalid/ && echo %s" % (SHAPED[1], KEEP[1]))
WRITE1 = {"file_path": REPO + "/tasks/briefs/fixture/FX1-brief.md",
          "content": "# FX1 brief\n\nThe contract names the premise; the key sk-%s stays out.\n" % SHAPED[2]}
EDIT1 = {"file_path": REPO + "/scripts/fixture_mod.py", "old_string": "def fixture():\n    return 0\n",
         "new_string": "def fixture():\n    return 1\n"}
READ1 = {"file_path": REPO + "/docs/INCIDENT-LOG.md"}
GREP1 = {"pattern": "AF-AP-201", "path": REPO + "/docs"}
SUB_BASH = {"command": "python3 -m pytest tests/test_fixture.py -q"}
SUB_EDIT = {"file_path": REPO + "/tests/test_fixture.py", "old_string": "x", "new_string": "def test_x():\n    assert 1\n"}
INPUTS = {"toolu_fxbash1": ("Bash", {"command": BASH1, "description": "a fixture"}), "toolu_fxwrite1": ("Write", WRITE1),
          "toolu_fxedit1": ("Edit", EDIT1), "toolu_fxread1": ("Read", READ1), "toolu_fxgrep1": ("Grep", GREP1),
          "toolu_fxbash2": ("Bash", {"command": "git status"}), "toolu_fxsub1": ("Bash", SUB_BASH),
          "toolu_fxsub2": ("Edit", SUB_EDIT)}         # toolu_fxbash3 repeats toolu_fxbash2: left out as a repeat


def sha16(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def sha256(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode("utf-8")).hexdigest()


def hook_module(name, ungated=False):
    spec = importlib.util.spec_from_file_location(name, HOOK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if ungated:
        for f in FLOORS:
            setattr(mod, f, float("-inf"))
    return mod


# ---------------------------------------------------------------- the fixture session

def iso(seconds):
    return (datetime.datetime(2026, 9, 25, 20, 0, 0) + datetime.timedelta(seconds=seconds)).isoformat(
        timespec="milliseconds") + "Z"


class Transcript:
    """Records with the shape of real ones (their keys and value types), fake content, one compact JSON line each."""

    def __init__(self, path, agent=None, prefix="fx"):
        self.path, self.agent, self.prefix, self.recs, self.clock = Path(path), agent, prefix, [], 0.0

    def _rec(self, kind, secs=1.0):
        self.clock += secs
        n = len(self.recs) + 1
        r = {"parentUuid": "%s-%04d" % (self.prefix, n - 1) if n > 1 else None, "isSidechain": self.agent is not None,
             "userType": "external", "cwd": REPO, "sessionId": SESSION, "version": "2.1.280", "gitBranch": "HEAD",
             "type": kind, "uuid": "%s-%04d" % (self.prefix, n), "timestamp": iso(self.clock), "entrypoint": "cli"}
        if self.agent:
            r["agentId"] = self.agent
        self.recs.append(r)
        return r

    def user(self, content, origin="human", **flags):
        r = self._rec("user")
        r["message"] = {"role": "user", "content": content}
        r["promptId"] = "%08d-%s" % (len(self.recs), self.prefix)
        if origin:
            r["origin"] = {"kind": origin}
        r.update(flags)
        return r

    def assistant(self, *blocks):
        r = self._rec("assistant")
        r["message"] = {"model": "claude-opus-5-5", "id": "msg_%s%d" % (self.prefix, len(self.recs)), "type": "message",
                        "role": "assistant", "content": list(blocks), "stop_reason": None,
                        "usage": {"input_tokens": 1, "output_tokens": 1}}
        return r

    def attachment(self, text, event, tool=None, tuid=None, secs=1.0):
        r = self._rec("attachment", secs)
        r["attachment"] = {"type": "hook_additional_context", "content": [text], "toolUseID": tuid, "hookEvent": event,
                           "hookName": "%s:%s" % (event, tool) if tool else event}
        return r

    def write(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("".join(json.dumps(r, separators=(",", ":")) + "\n" for r in self.recs), encoding="utf-8")


def text(t):
    return {"type": "text", "text": t}


def thinking(t):
    return {"type": "thinking", "thinking": t, "signature": "fx-signature"}


def tool_use(tuid, name, ti):
    return {"type": "tool_use", "id": tuid, "name": name, "input": ti}


def fixture_session(base):
    """The main transcript (two human prompts, excluded records, tool calls, two stamped System-1 injections and their
    scores), one subagent file, the wrapper's telemetry (.jev) and an S1-ALL appendix."""
    hook = hook_module("fx_hook_session")
    table = hook.load_table()
    main = Transcript(base / "proj" / (SESSION + ".jsonl"))
    p1 = main.user([text(P1)])
    ups, ups_rec, _ = hook.plan_prompt({"prompt": P1}, table, set(), str(base / "fx-cache.json"))
    assert ups_rec["injected"], "the fixture prompt must be one the live gate injects"
    b_text = HC.stamp(ups, "system1-context", "s1-0000000b")
    main.attachment(b_text, "UserPromptSubmit", secs=0.1)
    main.assistant(text("S1-RATE s1-0000000b rel=3 use=2\nOn it."))
    main.assistant(thinking(DROP[0] + " the human"), text(DROP[1] + " the human"),
                   tool_use("toolu_fxbash1", *INPUTS["toolu_fxbash1"]))
    pre, pre_rec, _ = hook.plan_tool({"tool_name": "Bash", "tool_input": {"command": BASH1}, "cwd": REPO}, table, set())
    assert pre_rec["injected"], "the fixture command must match a situation row"
    a_text = HC.stamp(pre, "system1-context", "s1-0000000a")
    main.attachment(a_text, "PreToolUse", "Bash", "toolu_fxbash1", secs=0.1)
    main.user([{"type": "tool_result", "tool_use_id": "toolu_fxbash1", "content": DROP[8] + " the human"}])
    main.assistant(text("S1-RATE s1-0000000a rel=2 use=1\nNext."))
    main.assistant(text(DROP[9] + " the human"), tool_use("toolu_fxwrite1", *INPUTS["toolu_fxwrite1"]))
    for tuid in ("toolu_fxedit1", "toolu_fxread1", "toolu_fxgrep1", "toolu_fxbash2"):
        main.assistant(tool_use(tuid, *INPUTS[tuid]))
    main.assistant(tool_use("toolu_fxbash3", "Bash", {"command": "git status"}))
    p2 = main.user("Ok go ahead")                       # no word after the stopwords: why no-tokens
    main.user("<task-notification>%s the human</task-notification>" % DROP[4], origin="task-notification")
    main.user("[Request interrupted by user] %s the human" % DROP[5], origin=None)
    main.user("%s the human" % DROP[6], isMeta=True)
    main.user("This session is being continued. %s the human" % DROP[7], isCompactSummary=True)
    main.write()
    sub = Transcript(base / "proj" / SESSION / "subagents" / "agent-a1.jsonl", agent="a1", prefix="sa")
    sub.user("You are a lane. %s the human asked for it." % DROP[3], origin=None)
    sub.assistant(thinking(DROP[2] + " the human"), tool_use("toolu_fxsub1", *INPUTS["toolu_fxsub1"]))
    sub.assistant(tool_use("toolu_fxsub2", *INPUTS["toolu_fxsub2"]))
    sub.write()
    jev = base / "jev"
    jev.mkdir()
    (jev / "injections.jsonl").write_text("".join(json.dumps(r) + "\n" for r in (
        {"id": "s1-0000000b", "source": "system1-context", "event": "UserPromptSubmit", "tool": None, "tool_use_id": None,
         "session": SESSION, "agent": "main", "sha256": sha256(b_text)},
        {"id": "s1-0000000a", "source": "system1-context", "event": "PreToolUse", "tool": "Bash",
         "tool_use_id": "toolu_fxbash1", "session": SESSION, "agent": "main", "sha256": sha256(a_text)})))
    pid8 = p1["promptId"][:8]
    s1all = base / "s1all.md"
    s1all.write_text("# fixture\n\n## Appendix E. The labels (fixture)\n\n```\n%s orchestration R   %s build-loop N   "
                     "%s rwkv P   ffffffff deep-work N\n```\n" % (pid8, pid8, pid8), encoding="utf-8")
    return {"main": main.path, "jev": jev, "s1all": s1all, "p1": "p-" + p1["uuid"], "p2": "p-" + p2["uuid"],
            "pid8": pid8, "ups": ups_rec["injected"], "pre": pre_rec["injected"]}


def sources(base, value):
    env = base / ("secrets-%s.env" % value[:4])
    env.write_text("FIXTURE_SECRET=%s\n" % value, encoding="utf-8")
    return (("env-file", str(env), ()),)


def run_candidates(base, value=ABSENT, extra=()):
    """The CLI in process, the value gate reading a fixture env file (the module's tuple replaced while it runs)."""
    fx = fixture_session(base)
    out = base / "cand"
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(TE, "KNOWN_VALUE_SOURCES", sources(base, value))
        rc = SY.main(["candidates", "--transcript", str(fx["main"]), "--out", str(out), "--jev", str(fx["jev"]),
                      "--s1-all", str(fx["s1all"]), "--cache", str(base / "cache.json"), "--sample", "100"]
                     + list(extra))
    return rc, out, fx


_BUILT = {}


def built(tmp_path_factory):
    """One candidates run over the fixture, shared by the tests that read it (built inside a test body, so a crash is a
    FAILED test, never an error: AF-AP-223)."""
    if "run" not in _BUILT:
        _BUILT["run"] = run_candidates(tmp_path_factory.mktemp("synth"))
    return _BUILT["run"]


def read_dir(out):
    items = [json.loads(x) for x in (out / "items.jsonl").read_text(encoding="utf-8").splitlines()]
    secs = {s["sha"]: s for s in (json.loads(x) for x in (out / "sections.jsonl").read_text(encoding="utf-8")
                                  .splitlines())}
    return items, secs


def all_bytes(out):
    return b"".join(p.read_bytes() for p in sorted(out.iterdir()))


# ---------------------------------------------------------------- local fake servers

@pytest.fixture(autouse=True)
def _loopback_never_proxied(monkeypatch):
    for name in ("http_proxy", "HTTP_PROXY", "https_proxy", "HTTPS_PROXY"):
        monkeypatch.delenv(name, raising=False)


class FakeServer:
    """A local HTTP server: `respond(path, body, n) -> (status, bytes)`; it keeps every request's path, headers and raw
    body, counts the requests in flight, and can hold the first `hold` requests until that many are in flight."""

    def __init__(self, respond, hold=0, delay=0.0):
        self.requests, self.respond, self.hold, self.delay = [], respond, hold, delay
        self.cond, self.in_flight, self.max_in_flight, self.arrivals = threading.Condition(), 0, 0, []
        outer = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                raw = self.rfile.read(int(self.headers.get("content-length") or 0))
                with outer.cond:
                    outer.requests.append({"path": self.path, "headers": dict(self.headers), "raw": raw})
                    outer.arrivals.append(time.monotonic())
                    n = len(outer.requests)
                    outer.in_flight += 1
                    outer.max_in_flight = max(outer.max_in_flight, outer.in_flight)
                    outer.cond.notify_all()
                    if n <= outer.hold:
                        outer.cond.wait_for(lambda: outer.in_flight >= outer.hold, timeout=3.0)
                try:
                    time.sleep(outer.delay)
                    status, body = outer.respond(self.path, json.loads(raw), n)
                finally:
                    # counted out BEFORE the answer is written: once the client reads it, it may send its next
                    # request, and a count still held here would read one request too many in flight
                    with outer.cond:
                        outer.in_flight -= 1
                        outer.cond.notify_all()
                self.send_response(status)
                self.send_header("content-type", "application/json")
                self.send_header("content-length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        self.httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = "http://127.0.0.1:%d" % self.httpd.server_address[1]
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()


@pytest.fixture
def server():
    made = []

    def make(respond, **kw):
        made.append(FakeServer(respond, **kw))
        return made[-1]

    yield make
    for s in made:
        s.close()


def chat(content, model="qwen3.8-27b-local", status=200):
    return status, json.dumps({"id": "cmpl-fx", "object": "chat.completion", "model": model,
                               "choices": [{"index": 0, "message": {"role": "assistant", "content": content},
                                            "finish_reason": "stop"}],
                               "usage": {"prompt_tokens": 100, "completion_tokens": 7}}).encode()


def vllm_ok(path, body, n):
    user = body["messages"][1]["content"]
    rel = 3 if "skill fx-skill-0," in user or "skill orchestration," in user else 1
    return chat("rel=%d use=%d fixture reason %d" % (rel, rel - 1, n))


def openjev_answer(body, bad=False):
    answers = {}
    for qid, q in body["questions"].items():
        names = list(q["criteria"])
        answers[qid] = {"type": "choice", "choice": names[2], "probabilities": dict(zip(names, [0.1, 0.2, 0.6, 0.1])),
                        "confidence": 0.6}
    if bad:
        answers["skill.governs"]["probabilities"]["unrelated"] = 0.9      # sums to 1.7: common.distribution refuses
    return {"model": "stand-in-openjev", "answers": answers, "usage": {"input_tokens": 11, "output_tokens": 0}}


def key_file(base):
    p = base / "api-key"
    p.write_text(FAKE_KEY + "\n", encoding="utf-8")
    return p


def env_file(base, url):
    p = base / "api.env"
    p.write_text("TYPESAFE_BASE_URL=%s\nTYPESAFE_API_KEY=%s\n" % (url, FAKE_KEY), encoding="utf-8")
    return p


class Sleeps:
    def __init__(self):
        self.slept = []

    def __call__(self, s):
        self.slept.append(s)


def run_label(cdir, out, url, backend="vllm", extra=(), sleep=None, clock=None, post=None):
    argv = ["label", "--candidates", str(cdir), "--out", str(out), "--backend", backend]
    argv += (["--url", url, "--key-file", str(key_file(out.parent))] if backend == "vllm"
             else ["--env-file", str(env_file(out.parent, url))])
    return SY.main(argv + list(extra), clock=clock or time.monotonic, sleep=sleep or Sleeps(), post=post)


def labels_of(path):
    return [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]


def hand_candidates(d, n_items=4, per_item=3):
    """A candidates directory written by hand (the label steps' input), independent of the ranking."""
    d.mkdir(parents=True, exist_ok=True)
    items, secs = [], {}
    for i in range(n_items):
        cands = []
        for j in range(per_item):
            body = "[system1 · prompt] skill fx-skill-%d, the section:\nfixture line %d.%d\nfull details: .claude/skills/" \
                   "fx-skill-%d/SKILL.md § H%d" % (j, i, j, j, j)
            sha = sha16(body)
            secs[sha] = {"sha": sha, "skill": "fx-skill-%d" % j, "heading": "H%d" % j, "project": True, "source": "rank",
                         "row": None, "text": body, "bytes": len(body.encode())}
            cands.append({"sha": sha, "skill": "fx-skill-%d" % j, "heading": "H%d" % j, "project": True,
                          "source": "rank", "rank": j + 1, "score": 90.0 - 10 * j, "row": None, "gate": j == 0})
        t = "fixture step %d: write the brief" % i
        items.append({"id": "p-hand-%d" % i, "kind": "prompt", "tool": None, "uuid": "hand-%d" % i,
                      "prompt_id": "%08d-hd" % i, "session": SESSION, "time": iso(10 * i), "gold": [], "text": t,
                      "text_sha": sha256(t), "candidates": cands})
    ib = "".join(json.dumps(x, sort_keys=True) + "\n" for x in items).encode()
    sb = "".join(json.dumps(secs[k], sort_keys=True) + "\n" for k in sorted(secs)).encode()
    (d / "items.jsonl").write_bytes(ib)
    (d / "sections.jsonl").write_bytes(sb)
    (d / "manifest.json").write_text(json.dumps({"files": {"items.jsonl": {"sha256": sha256(ib)},
                                                           "sections.jsonl": {"sha256": sha256(sb)}}}))
    return items, secs


# ---------------------------------------------------------------- CONTRACT 1: the items

def test_items_are_human_prompts_and_tool_inputs_only(tmp_path_factory):
    """The items are exactly the human-origin prompts and the tool inputs; no byte of an assistant text, a thinking block,
    a dispatch prompt, a task notification, an interrupt, a meta record, a compaction summary or a tool result reaches
    any file. The prompt's and the command's canaries do (the positive control: the search can see an item's text).
    Red on the mutants items-origin-dropped (a prompt with no origin counts) and items-assistant-blocks (a text or
    thinking block read as a tool input)."""
    rc, out, fx = built(tmp_path_factory)
    assert rc == 0
    items, _ = read_dir(out)
    assert {it["id"] for it in items} == {fx["p1"], fx["p2"]} | {"t-" + t for t in INPUTS}
    data = all_bytes(out)
    for c in KEEP:
        assert c.encode() in data, c
    for c in DROP:
        assert c.encode() not in data, c
    kinds = {it["id"]: (it["kind"], it["tool"]) for it in items}
    assert kinds[fx["p1"]] == ("prompt", None)
    assert {kinds["t-" + t] for t in INPUTS} == {("tool", n) for n, _ in INPUTS.values()}
    assert next(it for it in items if it["id"] == fx["p2"])["why"] == "no-tokens"


def test_scrubbing_happens_before_any_byte_leaves(tmp_path_factory, server):
    """Every value the scrubber's shapes take (a token assignment in a prompt, a Bearer header in a command, a provider key
    in a written file) is absent from every candidates file and from every request both backends send; the redaction
    markers stand in their place. Red on the mutant scrub-identity."""
    rc, out, _ = built(tmp_path_factory)
    assert rc == 0
    data = all_bytes(out)
    for v in SHAPED:
        assert v.encode() not in data, v
    assert b"token=<redacted>" in data and b"Bearer <redacted>" in data and b"sk-<redacted>" in data
    base = out.parent
    v = server(vllm_ok)
    assert run_label(out, base / "labels-vllm.jsonl", v.url, extra=["--limit", "12"]) == 0
    o = server(lambda path, body, n: (200, json.dumps(openjev_answer(body)).encode()))
    fc = FakeClock()
    assert run_label(out, base / "labels-openjev.jsonl", o.url, backend="openjev", extra=["--limit", "4"],
                     clock=fc.now, sleep=fc.sleep) == 0
    sent = b"".join(r["raw"] for r in v.requests + o.requests)
    assert len(v.requests) == 12 and len(o.requests) == 4
    assert b"token=<redacted>" in sent                       # the gold prompt goes first: its text was sent
    for s in SHAPED:
        assert s.encode() not in sent, s


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def now(self):
        return self.t

    def sleep(self, s):
        self.t += s


def test_the_value_gate_refuses_before_any_write(tmp_path):
    """A value no shape takes (a plain word after `passphrase is`) survives the scrubber; the value gate, reading the
    known source, refuses and nothing is written (exit 4). With a source that holds another value, the same run writes.
    Red on the mutant gate-skipped."""
    rc, out, _ = run_candidates(tmp_path, value=PLAIN)
    assert rc == 4
    assert not out.exists()
    rc, out, _ = run_candidates(tmp_path / "again", value=ABSENT)
    assert rc == 0 and PLAIN.encode() in (out / "items.jsonl").read_bytes()


def test_a_dry_run_writes_nothing_opens_no_secret_and_prints_counts_only(tmp_path, capsys, monkeypatch):
    """--dry-run prints the counts (JSON), writes no file, never calls the value gate's source reader (it would open the
    real secret sources), and prints no prompt, command, canary or secret. Red on the mutant dry-run-writes."""
    fx = fixture_session(tmp_path)

    def no_sources(*a, **k):
        raise AssertionError("the dry run opened a secret source")

    monkeypatch.setattr(TE, "known_values", no_sources)
    before = sorted(p.name for p in tmp_path.iterdir())
    rc = SY.main(["candidates", "--transcript", str(fx["main"]), "--dry-run", "--jev", str(fx["jev"]),
                  "--s1-all", str(fx["s1all"]), "--sample", "100"])
    out = capsys.readouterr().out
    assert rc == 0
    counts = json.loads(out)
    assert counts["dry_run"] is True and counts["items_total"] == 2 + len(INPUTS)
    assert sorted(p.name for p in tmp_path.iterdir()) == before
    for word in KEEP + DROP + SHAPED + (PLAIN, "delegate brief", "git commit", "fixture_mod"):
        assert word not in out, word


# ---------------------------------------------------------------- CONTRACT 1: the candidates are the hook's own

def section_ok(sec, skill, heading, row, project):
    """The oracle for a composed section, read from the skill file itself: the hook's label line, the pointer line, and
    every line between them a whole line of the skill (or the gap mark, or a library skill's description line)."""
    lines = sec["text"].split("\n")
    skill_lines = set((ROOT / ".claude" / "skills" / skill / "SKILL.md").read_text(encoding="utf-8").split("\n"))
    if row is None:
        assert lines[0] == "[system1 · prompt] skill %s, the section that matches this prompt, verbatim:" % skill
    else:
        assert lines[0] == "[system1 · %s] skill %s, the governing lines verbatim:" % (row, skill)
    assert lines[-1] == "full details: .claude/skills/%s/SKILL.md § %s" % (skill, heading)
    body = lines[1:-1]
    if not project and row is None:
        assert body and body[0].startswith("description: ")
        body = body[1:]
    assert all(line == "…" or line in skill_lines for line in body)
    assert any(line.lstrip("#").strip() == heading for line in skill_lines if line.startswith("#"))
    assert sha16(sec["text"]) == sec["sha"]


def test_the_candidates_are_the_hooks_own_ranking(tmp_path_factory):
    """Each item's ranked candidates are, in order, the top 10 of the hook's rank_prompt with the four floors lifted (this
    file's own instance of the hook), with its scores; `gate` is the live plan_prompt's choice; a tool call's rows are
    match_rows over its scrubbed input and `gate` the live plan_tool's; each section's text passes the skill-file oracle;
    the live gate's first excerpt has the very sha the tool stored; a gold skill below the top 10 is added at its rank.
    Red on the mutants floors-kept, ranking-reversed, top-cut, rows-dropped and sha-of-label."""
    rc, out, fx = built(tmp_path_factory)
    assert rc == 0
    items, secs = read_dir(out)
    live, ungated = hook_module("fx_oracle_live"), hook_module("fx_oracle_ungated", ungated=True)
    table = live.load_table()
    project = set(table["project_skills"])
    cache = str(out.parent / "oracle-cache.json")
    idx = live.corpus_index(cache)
    checked_gate = 0
    for it in items:
        ranked = [c for c in it["candidates"] if c["source"] == "rank"]
        _, live_rec, _ = live.plan_prompt({"prompt": it["text"]}, table, set(), cache)
        if live_rec.get("why"):
            assert ranked == []
            continue
        scored, _ = ungated.rank_prompt(it["text"], idx, project)
        top = [(e[1], e[2], e[0]) for e in scored[:10]]
        assert [(c["skill"], c["heading"], c["score"]) for c in ranked if c["rank"] <= 10] == top
        assert [c["rank"] for c in ranked if c["rank"] <= 10] == list(range(1, len(top) + 1))
        injected = {(e["skill"], e["heading"]): e["sha"] for e in live_rec["injected"]}
        for c in ranked:
            assert c["gate"] == ((c["skill"], c["heading"]) in injected)
            section_ok(secs[c["sha"]], c["skill"], c["heading"], None, c["skill"] in project)
        if live_rec["injected"]:
            first = live_rec["injected"][0]
            assert next(c["sha"] for c in ranked if (c["skill"], c["heading"]) == (first["skill"], first["heading"])) \
                == first["sha"]
            checked_gate += 1
        if it["kind"] == "tool":
            name, ti = INPUTS[it["tool_use_id"]]
            clean = {k: TE.scrub_payload(v) if isinstance(v, str) else v for k, v in ti.items()}
            want = [r["id"] for r in live.match_rows(table, name, clean, REPO)] if name in live.TOOLS else []
            rows = [c for c in it["candidates"] if c["source"] == "row"]
            assert it["rows"] == want and [c["row"] for c in rows] == want
            _, tool_rec, _ = live.plan_tool({"tool_name": name, "tool_input": clean, "cwd": REPO}, table, set())
            for c in rows:
                assert c["gate"] == (c["row"] in {e["row"] for e in tool_rec["injected"]})
                section_ok(secs[c["sha"]], c["skill"], c["heading"], c["row"], True)
        if it["id"] == fx["p1"]:
            deeper = {}
            for i, e in enumerate(scored, 1):
                if i > 10:
                    deeper.setdefault(e[1], i)                 # a skill's best rank below the top 10
            for skill in ("build-loop", "rwkv"):
                if skill in {e[1] for e in scored[:10]} or skill not in deeper:
                    continue
                assert any(c["skill"] == skill and c["rank"] == deeper[skill] for c in ranked), skill
    assert checked_gate >= 1                                  # the live gate's own sha was compared at least once
    bash = next(it for it in items if it["id"] == "t-toolu_fxbash1")
    assert [c["gate"] for c in bash["candidates"] if c["source"] == "row"] == [
        r in {e["row"] for e in fx["pre"]} for r in bash["rows"]]
    assert len([c for c in bash["candidates"] if c["source"] == "row"]) >= 2   # a row the budget left out is kept


# ---------------------------------------------------------------- CONTRACT 2: the labeler

def test_the_vllm_body_never_carries_a_forbidden_parameter(tmp_path, server):
    """Every body the vLLM backend sends has exactly the allowed keys (thinking off, temperature 0, max_tokens 64); and a
    body carrying any of the four forbidden keys is refused before a byte is sent. Red on the mutants guard-off and
    body-adds-n."""
    cdir = tmp_path / "cand"
    hand_candidates(cdir, 2, 2)
    s = server(vllm_ok)
    assert run_label(cdir, tmp_path / "labels.jsonl", s.url) == 0
    assert len(s.requests) == 4
    for r in s.requests:
        body = json.loads(r["raw"])
        assert set(body) == BODY_KEYS
        assert body["chat_template_kwargs"] == {"enable_thinking": False}
        assert body["temperature"] == 0 and body["max_tokens"] == 64 and body["model"] == "qwen3.8-27b-local"
        assert r["path"] == "/v1/chat/completions"
    items, secs = hand_candidates(tmp_path / "c2", 1, 1)
    client = SY.VllmClient(s.url, "qwen3.8-27b-local", FAKE_KEY, 5.0, sleep=Sleeps())
    for k in FORBIDDEN:
        body = SY.chat_body("qwen3.8-27b-local", items[0], next(iter(secs.values())), False, 64)
        body[k] = 1
        with pytest.raises(SY.ForbiddenParam):
            client.ask(body)
    assert len(s.requests) == 4                               # nothing more reached the server


def test_concurrency_reaches_and_never_passes_its_bound(tmp_path, server):
    """--concurrency 3 over 12 pairs: the fake server holds the first three until three are in flight, so the bound is
    reached; at no moment are more than three in flight. Red on the mutants pool-plus-two and pool-of-one."""
    cdir = tmp_path / "cand"
    hand_candidates(cdir, 4, 3)
    s = server(vllm_ok, hold=3, delay=0.05)
    assert run_label(cdir, tmp_path / "labels.jsonl", s.url, extra=["--concurrency", "3"]) == 0
    assert len(s.requests) == 12 and len(labels_of(tmp_path / "labels.jsonl")) == 12
    assert s.max_in_flight == 3


def test_a_rerun_skips_the_done_keys(tmp_path, server):
    """The first run stores three labels, then the server answers 503 until the retries are spent (the backoff 2, 4, 8,
    16, 32, 60 s on a fake sleep): exit 3, three records. The rerun sends only the five pending pairs; the file holds
    eight keys once each. Red on the mutant done-keys-ignored."""
    cdir = tmp_path / "cand"
    hand_candidates(cdir, 4, 2)
    out = tmp_path / "labels.jsonl"
    first = server(lambda path, body, n: vllm_ok(path, body, n) if n <= 3 else (503, b'{"error": "busy"}'))
    sleeps = Sleeps()
    assert run_label(cdir, out, first.url, extra=["--concurrency", "1"], sleep=sleeps) == 3
    assert len(labels_of(out)) == 3 and sleeps.slept == [2.0, 4.0, 8.0, 16.0, 32.0, 60.0]
    second = server(vllm_ok)
    assert run_label(cdir, out, second.url) == 0
    assert len(second.requests) == 5
    keys = [r["key"] for r in labels_of(out)]
    assert len(keys) == 8 == len(set(keys))


def test_a_malformed_answer_is_stored_as_malformed_never_guessed(tmp_path, server):
    """Only one line `rel=<0-3> use=<0-3> <reason>` parses, after an EMPTY leading <think></think> (a template can emit
    one with thinking off). Out of range, no reason, prose around it, two lines, a reason over 120 characters, a think
    block WITH content while thinking is off: each is stored with status malformed, rel and use None, the raw answer
    kept; a rerun asks nothing again. Red on the mutants lenient-parse, empty-think-kept and any-think-dropped."""
    answers = [("rel=2 use=1 a fine reason", (2, 1)), ("<think>\n\n</think>\n\nrel=3 use=2 after an empty block", (3, 2)),
               ("rel=4 use=1 out of range", None), ("rel=2 use=1", None), ("The answer: rel=2 use=1 because", None),
               ("rel=2 use=1 two\nlines", None), ("rel=1 use=0 " + "x" * 121, None),
               ("<think>the model thought here</think>\nrel=1 use=1 after a thought", None)]
    cdir = tmp_path / "cand"
    hand_candidates(cdir, 1, len(answers))
    s = server(lambda path, body, n: chat(answers[int(body["messages"][1]["content"].split("fixture line 0.")[1][0])][0]))
    out = tmp_path / "labels.jsonl"
    assert run_label(cdir, out, s.url, extra=["--concurrency", "2"]) == 0
    got = {r["section"]: r for r in labels_of(out)}
    items = [json.loads(x) for x in (cdir / "items.jsonl").read_text().splitlines()]
    for c, (ans, want) in zip(items[0]["candidates"], answers):
        r = got[c["sha"]]
        if want:
            assert (r["status"], r["rel"], r["use"], r["raw"]) == ("ok", want[0], want[1], None), ans
        else:
            assert (r["status"], r["rel"], r["use"], r["raw"]) == ("malformed", None, None, ans[:300]), ans
    again = server(vllm_ok)
    assert run_label(cdir, out, again.url) == 0 and again.requests == []


def test_the_openjev_backend_reuses_teacher_label(tmp_path, server, capsys):
    """One request per pair to /v1/systemone with model openjev-latest, the state {query, chunk} and both questions; the
    key rides only the Authorization header (never stdout, stderr or the labels); the answers are distributions, rel and
    use their most probable options; a distribution common.distribution refuses is stored as malformed. One Limiter
    serves every thread: with a real clock, three threads' four requests arrive at least 1 s apart. Red on the mutant
    limiter-per-thread."""
    cdir = tmp_path / "cand"
    hand_candidates(cdir, 2, 2)
    s = server(lambda path, body, n: (200, json.dumps(openjev_answer(body, bad=n == 4)).encode()))
    out = tmp_path / "labels.jsonl"
    assert run_label(cdir, out, s.url, backend="openjev", extra=["--concurrency", "3"], clock=time.monotonic,
                     sleep=time.sleep) == 0
    assert len(s.requests) == 4
    gaps = [b - a for a, b in zip(s.arrivals, s.arrivals[1:])]
    assert min(gaps) >= 0.9, gaps
    for r in s.requests:
        body = json.loads(r["raw"])
        assert r["path"] == "/v1/systemone" and body["model"] == "openjev-latest"
        assert set(body["state"]) == {"query", "chunk"} and body["questions"] == SY.QUESTIONS
        assert r["headers"].get("Authorization") == "Bearer " + FAKE_KEY
    recs = labels_of(out)
    assert sorted(r["status"] for r in recs) == ["malformed", "ok", "ok", "ok"]
    assert all((r["rel"], r["use"]) == (2, 2) for r in recs if r["status"] == "ok")
    printed = capsys.readouterr()
    assert FAKE_KEY not in printed.out + printed.err and FAKE_KEY not in out.read_text()


def test_the_key_never_reaches_a_message(tmp_path, server, capsys):
    """A 401 whose body echoes the Authorization header: the run refuses (exit 3) and the printed reason carries `<key>`,
    never the key; the labels file holds nothing. Red on the mutant safe-keeps-key."""
    cdir = tmp_path / "cand"
    hand_candidates(cdir, 1, 1)
    s = server(lambda path, body, n: (401, ("bad key: Bearer %s" % FAKE_KEY).encode()))
    out = tmp_path / "labels.jsonl"
    assert run_label(cdir, out, s.url) == 3
    printed = capsys.readouterr()
    assert "<key>" in printed.err and FAKE_KEY not in printed.out + printed.err
    assert labels_of(out) == [] and len(s.requests) == 1


def test_a_second_run_on_the_same_labels_file_is_refused(tmp_path, server):
    """Another run holds the labels file: exit 75 and no request. Red on the mutant lock-dropped."""
    cdir = tmp_path / "cand"
    hand_candidates(cdir, 1, 2)
    out = tmp_path / "labels.jsonl"
    s = server(vllm_ok)
    with open(out, "a") as held:
        fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert run_label(cdir, out, s.url) == 75
    assert s.requests == []


# ---------------------------------------------------------------- CONTRACT 3: the validator on hand-made gold

def cand(sha, skill, heading, source="rank", rank=None, score=None, row=None, gate=False):
    return {"sha": sha, "skill": skill, "heading": heading, "source": source, "rank": rank, "score": score, "row": row,
            "gate": gate, "project": True}


def lab(item, sha, rel, use=0, status="ok"):
    return {"key": SY.label_key(item, sha, "vllm", "r1"), "item": item, "section": sha, "backend": "vllm", "rubric": "r1",
            "status": status, "rel": rel, "use": use}


def test_the_validator_numbers_on_hand_made_gold():
    """Two gold sources, every expected number worked out by hand (the file's docstring rule).

    S1-ALL (7 labels): aaaaaaaa's orchestration R -> c1 (the BEST-ranked orchestration section, not c4), build-loop N ->
    c2, deep-work P -> c3; bbbbbbbb's pc-bridge-lanes R -> c5, luck N -> c6, rwkv P -> no section; cccccccc -> no item.
    The labeler's rel: c1 3, c2 1, c3 2, c5 2, c6 0; gold ordinal (N0 P1 R2): 2, 0, 1, 2, 0.
      map A (0,1->N 2->P 3->R): 2 0 1 1 0 -> exact 4/5 = 0.8, within one 5/5; Wilson(4, 5) = [0.3755, 0.9638]
      map B (0->N 1,2->P 3->R): 2 1 1 1 0 -> exact 3/5 = 0.6, within one 5/5
      Spearman, raw rel vs ordinal: ranks x [5, 2, 3.5, 3.5, 1], y [4.5, 1.5, 3, 4.5, 1.5]; sxy 8.25, sxx 9.5, syy 9
        -> 8.25 / sqrt(85.5) = 0.8922
      map A: Spearman 8.25 / 9 = 0.9167; Kendall tau-b: 7 concordant, 0 discordant, 1 x-tie, 1 y-tie -> 7/8 = 0.875;
        kappa (linear): observed 0.1, expected 0.46 -> 1 - 0.1/0.46 = 0.7826
      the plain order (hook scores 90, 50, 40, 80, 20): ranks [5, 3, 2, 4, 1]; sxy 7.5, sxx 10 -> 7.5/sqrt(90) = 0.7906
    S1-RATE here (its counts; its numbers are the next test's): gold is the `scored` rows ONLY (the caveat: a long reply
    loses its text, so scored rows are a subsample). r1 (tool, rel 2 use 1) carries c7 (same text) and c8 (other text);
    r3 (prompt, 0.1 s after p-u1, rel 1) c1; r4 (rel 0) names a tool call with no item; r6 (rel 2) comes 5 s after its
    prompt (over 2 s): no item. r2 is late and r5 missing: not gold. So 5 gold sections from 4 injections, 3 joined
    (2 with the same text), 2 with no item; gold rel 2, 2, 1, 0, 2 -> the most common (2) holds 3/5 = 0.6, median_low
    2, and 4 of 5 lie within one of it (the 0 does not): 0.8. Rows by status: scored 4, late 1, missing 1.
    Red on the mutants exact-is-within-one, spearman-no-ties, map-a-is-b, prompt-link-10s, s1all-worst-rank and
    late-counted."""
    t0 = "2026-09-25T20:00:00.000Z"
    items = [
        {"id": "p-u1", "kind": "prompt", "tool": None, "uuid": "u1", "prompt_id": "aaaaaaaa-p1", "session": "S",
         "time": t0, "candidates": [cand("s01", "orchestration", "H1", rank=1, score=90.0, gate=True),
                                    cand("s02", "build-loop", "H2", rank=2, score=50.0),
                                    cand("s03", "deep-work", "H3", rank=3, score=40.0),
                                    cand("s04", "orchestration", "H4", rank=4, score=30.0)]},
        {"id": "p-u2", "kind": "prompt", "tool": None, "uuid": "u2", "prompt_id": "bbbbbbbb-p2", "session": "S",
         "time": "2026-09-25T21:00:00.000Z", "candidates": [cand("s05", "pc-bridge-lanes", "H5", rank=1, score=80.0),
                                                           cand("s06", "luck", "H6", rank=2, score=20.0)]},
        {"id": "t-toolu_1", "kind": "tool", "tool": "Bash", "session": "S", "time": t0,
         "candidates": [cand("s07", "env-tool-quirks", "Shell", "row", row="commit", gate=True),
                        cand("s08", "build-loop", "Core", "row", row="commit-increment", gate=True)]},
        {"id": "t-toolu_2", "kind": "tool", "tool": "Bash", "session": "S", "time": t0,
         "candidates": [cand("s09", "pc-bridge-lanes", "PC", "row", row="pc-call", gate=True)]}]
    s1_all = [("aaaaaaaa", "orchestration", "R"), ("aaaaaaaa", "build-loop", "N"), ("aaaaaaaa", "deep-work", "P"),
              ("bbbbbbbb", "pc-bridge-lanes", "R"), ("bbbbbbbb", "luck", "N"), ("bbbbbbbb", "rwkv", "P"),
              ("cccccccc", "orchestration", "N")]

    def row(rid, event, status, rel, use, secs, tuid=None, time=t0):
        return {"id": rid, "event": event, "tool": None, "session": "S", "agent": "main", "time": time,
                "status": status, "rel": rel, "use": use, "tool_use_id": tuid,
                "sections": [{"skill": a, "heading": b, "sha": c} for a, b, c in secs]}

    gold_rows = [row("s1-1", "PreToolUse", "scored", 2, 1, [("env-tool-quirks", "Shell", "s07"),
                                                            ("build-loop", "Core", "sXX")], "toolu_1"),
                 row("s1-2", "PreToolUse", "late", 3, 3, [("pc-bridge-lanes", "PC", "s09")], "toolu_2"),
                 row("s1-3", "UserPromptSubmit", "scored", 1, 0, [("orchestration", "H1", "s01")],
                     time="2026-09-25T20:00:00.100Z"),
                 row("s1-4", "PreToolUse", "scored", 0, 0, [("luck", "L", "s99")], "toolu_404"),
                 row("s1-5", "PreToolUse", "missing", None, None, [("luck", "L", "s98")], "toolu_1"),
                 row("s1-6", "UserPromptSubmit", "scored", 2, 2, [("orchestration", "H1", "s01")],
                     time="2026-09-25T20:00:05.000Z")]
    labels = {r["key"]: r for r in (lab("p-u1", "s01", 3), lab("p-u1", "s02", 1), lab("p-u1", "s03", 2),
                                    lab("p-u1", "s04", 0), lab("p-u2", "s05", 2), lab("p-u2", "s06", 0),
                                    lab("t-toolu_1", "s07", 2, 1), lab("t-toolu_1", "s08", 3, 2),
                                    lab("t-toolu_2", "s09", 3, 2))}
    res = SY.validate(items, labels, gold_rows, s1_all, "vllm", "r1")
    a = res["s1-all"]
    assert a["gold"] == 7 and a["counts"] == {"joined": 5, "no section": 1, "no item": 1, "labeled": 5}
    assert a["gold_grade"] == {"R": 2, "N": 3, "P": 2}
    assert (a["map_a"]["exact"], a["map_a"]["within_one"], a["map_a"]["exact_ci"]) == (0.8, 1.0, [0.3755, 0.9638])
    assert (a["map_b"]["exact"], a["map_b"]["within_one"]) == (0.6, 1.0)
    assert a["rel_spearman_raw"] == 0.8922
    assert (a["map_a"]["spearman"], a["map_a"]["kendall_tau_b"], a["map_a"]["kappa_linear"]) == (0.9167, 0.875, 0.7826)
    assert a["plain_order_same_pairs"] == 0.7906
    # Fisher z of 0.8922 at n 5: z = atanh(0.8922186) = 1.4326985, se = sqrt(1.06 / 2) = 0.7280110; z -+ 1.959964 se
    # -> tanh(0.0058232) = 0.0058, tanh(2.8595738) = 0.9935; its lower bound is under the plain order: no win yet
    assert a["rel_spearman_raw_ci"] == [0.0058, 0.9935] and a["beats_plain_order"] is False
    assert a["confusion_raw"] == {"N": {"0": 1, "1": 1, "2": 0, "3": 0}, "P": {"0": 0, "1": 0, "2": 1, "3": 0},
                                  "R": {"0": 0, "1": 0, "2": 1, "3": 1}}
    r = res["s1-rate"]
    assert r["gold"] == 5 and r["counts"] == {"joined": 3, "no item": 2, "labeled": 3} and r["injections"] == 4
    assert r["same_text"] == 2 and r["rel"]["n"] == 3    # its numbers: the next test, on labels of its own
    assert r["gold_rel"] == {"2": 3, "1": 1, "0": 1}
    assert r["constant_baseline"] == {"majority_exact": 0.6, "median": 2, "median_within_one": 0.8}
    assert r["rows_by_status"] == {"scored": 4, "late": 1, "missing": 1}
    assert "scored rows only" in r["caveat"] and "200 characters" in r["caveat"]


def test_the_validator_numbers_on_hand_made_s1_rate_gold():
    """S1-RATE on labels of its own, worked out by hand. Joined in order: c7 (gold rel 2), c8 (2), c9 (3), c1 (1); the
    labeler's rel 2, 3, 3, 2 -> exact 2/4 = 0.5, within one 4/4 = 1.0; Spearman: ranks x [1.5, 3.5, 3.5, 1.5],
    y [2.5, 2.5, 4, 1], sxy 3, sxx 4, syy 4.5 -> 3 / sqrt(18) = 0.7071. use: gold 1, 1, 3, 0 against 1, 2, 2, 0 ->
    exact 0.5, within one 1.0. The confusion table as listed. A LATE row (rel 0 on c9) is not gold: counted, it would add
    the pair (gold 0, label 3) -> exact 2/5 = 0.4, within one 4/5 = 0.8. Red on the mutants exact-is-within-one and
    late-counted."""
    t0 = "2026-09-25T20:00:00.000Z"
    items = [{"id": "p-u1", "kind": "prompt", "tool": None, "uuid": "u1", "prompt_id": "aaaaaaaa-p1", "session": "S",
              "time": t0, "candidates": [cand("s01", "orchestration", "H1", rank=1, score=90.0, gate=True)]},
             {"id": "t-toolu_1", "kind": "tool", "tool": "Bash", "session": "S", "time": t0,
              "candidates": [cand("s07", "env-tool-quirks", "Shell", "row", row="commit", gate=True),
                             cand("s08", "build-loop", "Core", "row", row="commit-increment", gate=True)]},
             {"id": "t-toolu_2", "kind": "tool", "tool": "Bash", "session": "S", "time": t0,
              "candidates": [cand("s09", "pc-bridge-lanes", "PC", "row", row="pc-call", gate=True)]}]
    gold_rows = [
        {"id": "s1-1", "event": "PreToolUse", "session": "S", "time": t0, "status": "scored", "rel": 2, "use": 1,
         "tool_use_id": "toolu_1", "sections": [{"skill": "env-tool-quirks", "heading": "Shell", "sha": "s07"},
                                                {"skill": "build-loop", "heading": "Core", "sha": "sXX"}]},
        {"id": "s1-2", "event": "PreToolUse", "session": "S", "time": t0, "status": "scored", "rel": 3, "use": 3,
         "tool_use_id": "toolu_2", "sections": [{"skill": "pc-bridge-lanes", "heading": "PC", "sha": "s09"}]},
        {"id": "s1-3", "event": "UserPromptSubmit", "session": "S", "time": "2026-09-25T20:00:00.100Z",
         "status": "scored", "rel": 1, "use": 0, "tool_use_id": None,
         "sections": [{"skill": "orchestration", "heading": "H1", "sha": "s01"}]},
        {"id": "s1-7", "event": "PreToolUse", "session": "S", "time": t0, "status": "late", "rel": 0, "use": 0,
         "tool_use_id": "toolu_2", "sections": [{"skill": "pc-bridge-lanes", "heading": "PC", "sha": "s09"}]}]
    labels = {r["key"]: r for r in (lab("t-toolu_1", "s07", 2, 1), lab("t-toolu_1", "s08", 3, 2),
                                    lab("t-toolu_2", "s09", 3, 2), lab("p-u1", "s01", 2, 0))}
    r = SY.validate(items, labels, gold_rows, [], "vllm", "r1")["s1-rate"]
    assert r["counts"] == {"joined": 4, "labeled": 4} and r["same_text"] == 3
    assert (r["rel"]["exact"], r["rel"]["within_one"], r["rel"]["spearman"]) == (0.5, 1.0, 0.7071)
    assert (r["use"]["exact"], r["use"]["within_one"]) == (0.5, 1.0)
    assert r["constant_baseline"] == {"majority_exact": 0.5, "median": 2, "median_within_one": 1.0}
    assert r["rows_by_status"] == {"scored": 3, "late": 1}
    assert r["rel"]["confusion"] == {"0": {"0": 0, "1": 0, "2": 0, "3": 0}, "1": {"0": 0, "1": 0, "2": 1, "3": 0},
                                     "2": {"0": 0, "1": 0, "2": 1, "3": 1}, "3": {"0": 0, "1": 0, "2": 0, "3": 1}}


def test_the_validator_joins_the_real_readers_output_on_the_fixture(tmp_path_factory, server):
    """End to end through scripts/s1_scores.py: the fixture's two scored injections (the tool call's rows, the prompt's
    excerpts) and its S1-ALL appendix join the candidates; once labeled, every joined gold section has its label."""
    rc, out, fx = built(tmp_path_factory)
    assert rc == 0
    s = server(vllm_ok)
    labels = out.parent / "labels-validate.jsonl"
    assert run_label(out, labels, s.url) == 0
    res_path = out.parent / "validate.json"
    assert SY.main(["validate", "--candidates", str(out), "--transcript", str(fx["main"]), "--labels", str(labels),
                    "--jev", str(fx["jev"]), "--s1-all", str(fx["s1all"]), "--out", str(res_path)]) == 0
    res = json.loads(res_path.read_text())
    r = res["s1-rate"]
    assert r["gold"] == len(fx["pre"]) + len(fx["ups"]) and r["injections"] == 2
    assert r["counts"] == {"joined": r["gold"], "labeled": r["gold"]} and r["same_text"] == r["gold"]
    assert r["rows_by_status"] == {"scored": 2} and "scored rows only" in r["caveat"]
    a = res["s1-all"]
    assert a["gold"] == 4 and a["counts"]["no item"] == 1 and a["counts"]["labeled"] == a["counts"]["joined"]


# ---------------------------------------------------------------- CONTRACT 4: the dataset

def test_the_dataset_rows_join_with_laya_ft_and_the_loader_names_its_gap(tmp_path):
    """Two rows per ok label in build_dataset.make_row's shape; every digest matches its content; the one-hot target sits
    at the label's value; common.join_labels (the trainer's own join) accepts every label; a malformed label, another
    backend's and another rubric's give no row. common.load_dataset refuses the rows today with the exact reason: its
    QUESTIONS lack skill.governs and skill.helps (the NOT-done item this test pins; it goes red when common.py learns
    them). Red on the mutants target-off-by-one and question-sha-swapped."""
    from laya_ft import common as C
    cdir = tmp_path / "cand"
    items, secs = hand_candidates(cdir, 2, 2)
    recs = [lab(it["id"], c["sha"], rel, use) for it, (c, rel, use) in
            ((items[0], (items[0]["candidates"][0], 3, 2)), (items[0], (items[0]["candidates"][1], 0, 0)),
             (items[1], (items[1]["candidates"][0], 1, 1)))]
    recs.append(lab(items[1]["id"], items[1]["candidates"][1]["sha"], None, None, status="malformed"))
    other = lab(items[1]["id"], items[1]["candidates"][1]["sha"], 2, 2)
    other.update(backend="openjev", key=SY.label_key(items[1]["id"], items[1]["candidates"][1]["sha"], "openjev", "r1"))
    recs.append(other)
    labels = {r["key"]: r for r in recs}
    rows, out, counts = SY.dataset_rows(items, secs, labels, "vllm", "r1")
    assert len(rows) == 6 and len(out) == 6
    for row in rows:
        assert row["state_sha"] == C.state_sha(row["state"]) and row["question_sha"] == C.question_sha(row["question"])
        assert row["options"] == C.options(row["question"]) and row["item_id"] == "s1-" + row["state_sha"][:20]
        assert set(row["state"]) == {"query", "chunk"} and row["sources"][0]["kind"] == "transcript"
    by_key = {r["key"]: r for r in out}
    joined = C.join_labels(rows, by_key)
    assert len(joined) == 6
    want = {(recs[0]["section"], "skill.governs"): 3, (recs[0]["section"], "skill.helps"): 2,
            (recs[1]["section"], "skill.governs"): 0, (recs[2]["section"], "skill.helps"): 1}
    for row, target, rec in joined:
        k = (row["sources"][0]["section"], row["question_id"])
        if k in want:
            assert target == [1.0 if i == want[k] else 0.0 for i in range(4)], k
    ddir = tmp_path / "ds"
    ddir.mkdir()
    (ddir / "dataset.jsonl").write_bytes("".join(json.dumps(r) + "\n" for r in rows).encode())
    (ddir / "manifest.json").write_text(json.dumps({"dataset": {"sha256": sha256((ddir / "dataset.jsonl").read_bytes())},
                                                    "counts": {"rows_total": len(rows)}}))
    with pytest.raises(C.DatasetError, match="the question is not this code's 'skill.governs'"):
        C.load_dataset(ddir)


def test_the_dataset_command_keeps_text_out_of_the_commit_dir(tmp_path, monkeypatch):
    """dataset --commit-dir writes the manifest and the labels only: no step text and no section text reaches it, while
    --out holds the dataset with both. The value gate runs before --out is written."""
    cdir = tmp_path / "cand"
    items, secs = hand_candidates(cdir, 1, 2)
    labels = tmp_path / "labels.jsonl"
    labels.write_text("".join(json.dumps(lab(items[0]["id"], c["sha"], 2, 1)) + "\n" for c in items[0]["candidates"]))
    monkeypatch.setattr(TE, "KNOWN_VALUE_SOURCES", sources(tmp_path, ABSENT))
    commit = tmp_path / "commit"
    assert SY.main(["dataset", "--candidates", str(cdir), "--labels", str(labels), "--backend", "vllm",
                    "--out", str(tmp_path / "ds"), "--commit-dir", str(commit)]) == 0
    assert sorted(p.name for p in commit.iterdir()) == ["dataset-manifest.json", "labels.jsonl"]
    committed = b"".join(p.read_bytes() for p in commit.iterdir())
    assert b"fixture step 0" not in committed and b"fixture line 0." not in committed
    assert b"fixture step 0" in (tmp_path / "ds" / "dataset.jsonl").read_bytes()
    manifest = json.loads((commit / "dataset-manifest.json").read_text())
    assert manifest["counts"]["rows_total"] == 4 and manifest["fitted"] is False


# ---------------------------------------------------------------- the cut and the sample

def test_the_cut_comes_after_the_scrub(tmp_path):
    """A prompt of 3,990 characters of words, then a token assignment straddling the hook's 4,000-character cut: the
    scrubber takes the whole value first, so the cut lands inside the marker and no part of the value survives (a cut
    first would leave `token=QZJ8`, 4 characters, under the rule's 8-character floor: AF-AP-127). The item is exactly
    4,000 characters and marked cut. Red on the mutants cut-before-scrub and cut-dropped."""
    main = Transcript(tmp_path / "proj" / (SESSION + ".jsonl"))
    main.user([text("word " * 798 + "token=%s and the tail of the prompt" % SHAPED[0])])
    main.write()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(TE, "KNOWN_VALUE_SOURCES", sources(tmp_path, ABSENT))
        assert SY.main(["candidates", "--transcript", str(main.path), "--out", str(tmp_path / "cand"), "--jev",
                        str(tmp_path / "no-jev"), "--s1-all", "", "--sample", "0"]) == 0
    items, _ = read_dir(tmp_path / "cand")
    assert len(items) == 1 and len(items[0]["text"]) == 4000 and items[0]["capped"] is True
    assert items[0]["text"].endswith("token=<red")
    assert b"token=QZJ8" not in all_bytes(tmp_path / "cand")


def fake_call(n, tool, rows, gold=False):
    return {"id": "t-%s-%03d" % (tool, n), "tool": tool, "gold": ["s1-rate"] if gold else [], "file_index": 0, "line": n,
            "stratum": "%s|%s" % (tool, rows)}


def test_the_sample_takes_tools_in_turn_then_strata_in_turn():
    """Gold first; then one call per tool a round (Bash, Read, Write, Edit, Grep), each tool's own queue one call per
    stratum a round. Worked by hand for 2 gold + Bash 30 (strata -: 20, commit: 8, pc-call: 2), Read 5, Write 4 (-: 2,
    brief: 2), Grep 1, budget 14: rounds give Bash -, Read, Write -, Grep; Bash commit, Read, Write brief; Bash pc-call,
    Read, Write -; Bash -, Read -> Bash 4 (- 2, commit 1, pc-call 1), Read 4, Write 3 (- 2, brief 1), Grep 1, plus the
    2 gold. The same seed gives the same calls. Red on the mutants tools-not-in-turn and gold-dropped."""
    calls = [fake_call(i, "Bash", "-", gold=True) for i in range(2)]
    calls += [fake_call(100 + i, "Bash", "-") for i in range(20)] + [fake_call(200 + i, "Bash", "commit") for i in range(8)]
    calls += [fake_call(300 + i, "Bash", "pc-call") for i in range(2)] + [fake_call(400 + i, "Read", "-") for i in range(5)]
    calls += [fake_call(500 + i, "Write", "-") for i in range(2)] + [fake_call(600 + i, "Write", "brief") for i in range(2)]
    calls += [fake_call(700, "Grep", "-")]
    picked, strata = SY.sample_calls(calls, 14, 308)
    assert strata == 7 and len(picked) == 14
    assert [c["id"] for c in picked[:2]] == ["t-Bash-000", "t-Bash-001"]
    got = {}
    for c in picked[2:]:
        got[c["stratum"]] = got.get(c["stratum"], 0) + 1
    assert got == {"Bash|-": 2, "Bash|commit": 1, "Bash|pc-call": 1, "Read|-": 4, "Write|-": 2, "Write|brief": 1,
                   "Grep|-": 1}
    assert [c["id"] for c in SY.sample_calls(calls, 14, 308)[0]] == [c["id"] for c in picked]



LAYA_PY = "/root/venv-laya-probe/bin/python"
FIT_RUN = """
import json, sys
sys.path.insert(0, sys.argv[1])
import s1_synth as SY
from laya_ft import build_dataset as BD, common as C
items, secs, _ = SY.load_candidates(sys.argv[2])
labels, _ = SY.read_labels(sys.argv[3])
rows, recs, counts = SY.dataset_rows(items, secs, labels, "vllm", "r1", BD.Fitter(C.DEFAULT_MODEL_DIR))
print(json.dumps({"rows": [[r["sources"][0]["item"], r["question_id"], bool(r.get("cut")),
                            r["state"]["chunk"] == secs[r["sources"][0]["section"]]["text"]] for r in rows],
                  "counts": counts, "joined": len(C.join_labels(rows, {x["key"]: x for x in recs}))}))
"""


def test_the_dataset_fits_laya_window_in_the_laya_venue(tmp_path):
    """build_dataset.Fitter (Laya's own tokenizer and build_sequence, run by the Laya venv's python in a subprocess): a
    short state is kept whole; a long step is cut and its section kept whole; a section that alone overflows the window
    gives no row, counted, never a crash; the fitted rows still join their labels. Skipped, loudly, where the Laya venv
    or its model is absent (CI). Red on the mutant unfit-not-caught."""
    from laya_ft import common as C
    if not Path(LAYA_PY).exists() or not Path(C.DEFAULT_MODEL_DIR).exists():
        pytest.skip("LOUD SKIP: the Laya venv (%s) or its model is absent on this venue" % LAYA_PY)
    cdir = tmp_path / "cand"
    items, secs = hand_candidates(cdir, 3, 1)
    items[1]["text"] = "fixture step 1: " + "word " * 3000
    big = items[2]["candidates"][0]["sha"]
    secs[big]["text"] = secs[big]["text"].replace("fixture line 2.0", "a line of a very long section\n" * 400)
    newsha = sha16(secs[big]["text"])
    secs[newsha] = dict(secs.pop(big), sha=newsha)
    items[2]["candidates"][0]["sha"] = newsha
    ib = "".join(json.dumps(x, sort_keys=True) + "\n" for x in items).encode()
    sb = "".join(json.dumps(secs[k], sort_keys=True) + "\n" for k in sorted(secs)).encode()
    (cdir / "items.jsonl").write_bytes(ib)
    (cdir / "sections.jsonl").write_bytes(sb)
    (cdir / "manifest.json").write_text(json.dumps({"files": {"items.jsonl": {"sha256": sha256(ib)},
                                                              "sections.jsonl": {"sha256": sha256(sb)}}}))
    labels = tmp_path / "labels.jsonl"
    labels.write_text("".join(json.dumps(lab(it["id"], it["candidates"][0]["sha"], 2, 1)) + "\n" for it in items))
    r = subprocess.run([LAYA_PY, "-c", FIT_RUN, str(ROOT / "scripts"), str(cdir), str(labels)], capture_output=True,
                       text=True, timeout=600)
    assert r.returncode == 0, r.stderr[-1500:]
    got = json.loads(r.stdout.strip().splitlines()[-1])
    rows = {(item, q): (cut, kept) for item, q, cut, kept in got["rows"]}
    for q in ("skill.governs", "skill.helps"):
        assert rows[("p-hand-0", q)] == (False, True)
        assert rows[("p-hand-1", q)] == (True, True)
        assert ("p-hand-2", q) not in rows and got["counts"]["unfit." + q] == 1
    assert got["joined"] == 4 and len(got["rows"]) == 4


def test_the_files_are_ascii_json_and_a_line_separator_round_trips(tmp_path):
    """A prompt holding U+2028 and U+2029 is stored as ASCII JSON: no raw separator byte reaches items.jsonl (a
    str.splitlines() reader would cut the record there), and load_candidates gives the text back exactly. Red on the
    mutant non-ascii-json."""
    main = Transcript(tmp_path / "proj" / (SESSION + ".jsonl"))
    prompt = "write the orchestration brief\u2028for the lane\u2029and its worktree pins"
    main.user([text(prompt)])
    main.write()
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(TE, "KNOWN_VALUE_SOURCES", sources(tmp_path, ABSENT))
        assert SY.main(["candidates", "--transcript", str(main.path), "--out", str(tmp_path / "cand"), "--jev",
                        str(tmp_path / "no-jev"), "--s1-all", "", "--sample", "0"]) == 0
    data = (tmp_path / "cand" / "items.jsonl").read_bytes()
    assert b"\xe2\x80\xa8" not in data and b"\xe2\x80\xa9" not in data and b"\\u2028" in data
    items, _, _ = SY.load_candidates(tmp_path / "cand")
    assert [it["text"] for it in items] == [prompt]
