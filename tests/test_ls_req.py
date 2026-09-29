"""Tests for the chat form (T2) of the stack runner, scripts/ls_req.py: task #364, D-108 item 6, brief
tasks/briefs/labeling/LS-B10-brief.md (CONTRACT items 1 to 10, TESTS section).

Every hook test drives the REAL entry (`python3 scripts/ls_req.py <subcommand>`, its payload on stdin) against a
fixture transcript written in the harness's own record shapes (compact JSON, one content block per assistant record,
as measured on this session's transcript 2026-09-29), and every request runs through the REAL scripts/stack.py: the
committed registry for `premise`, or a temporary registry of tiny real programs (a sleeper, an argv printer) for the
budget and verbatim tests, the way tests/test_stack.py does. The state lives under tmp_path (AF_REQ_STATE), the
runner's log under --log-dir in tmp_path, the runner's tree is a temporary git repository: no test writes the
repository's .jev/. The one exception makes the default place its subject (a temporary repository holding a copy of
the scripts).
Each test's docstring names the mutant of scripts/ls_req.py that turns it into a FAILED test (AF-AP-223).
"""
import importlib.util
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time
import types
from pathlib import Path

import pytest

ROOT = Path(os.path.realpath(Path(__file__).resolve().parents[1]))
LS = ROOT / "scripts" / "ls_req.py"
PY = sys.executable
GIT_ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
           "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1"}
NONCE_RX = re.compile(r"Chat form \(LS-B10\) nonce ([0-9a-f]{12}): ")
OLD = "0123456789ab"                 # a nonce-shaped token no prompt minted
TAG = "<" + "system-reminder>"       # built at run time (a tag literal in a Write input can lose its shape)


def load():
    spec = importlib.util.spec_from_file_location("ls_req_under_test", LS)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


M = load()


def git(cwd, *args):
    r = subprocess.run(["git", "-C", str(cwd), *args], capture_output=True, text=True, env={**os.environ, **GIT_ENV},
                       timeout=60)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def make_repo(path):
    """A git repository with one commit and the small programs the test registry runs."""
    path.mkdir(parents=True)
    git(path, "init", "-q", "-b", "main")
    (path / "a.txt").write_text("a\n")
    (path / "b.txt").write_text("b\n")
    (path / "argv.py").write_text("import json, sys\nprint(json.dumps(sys.argv[1:]))\n")
    (path / "slowstep.py").write_text("import os, sys, time\nopen(sys.argv[1], 'w').write(str(os.getpid()))\n"
                                      "time.sleep(120)\n")
    git(path, "add", ".")
    git(path, "commit", "-q", "--no-verify", "-m", "one")
    return Path(os.path.realpath(path))


TEST_REGISTRY = """version = 1
[tools]

[stacks.slow]
summary = "sleeps two minutes, its pid written first"
replaces = "nothing"
outward = false
[stacks.slow.params.pidfile]
type = "text"
required = true
[[stacks.slow.steps]]
id = "sleep"
argv = ["python3", "slowstep.py", "{pidfile}"]
timeout = 600

[stacks.echoargs]
summary = "prints its argument vector as JSON"
replaces = "nothing"
outward = false
[stacks.echoargs.params.q]
type = "text"
required = true
[[stacks.echoargs.steps]]
id = "show"
argv = ["python3", "argv.py", "{q}"]
"""


def base_env(**extra):
    env = {k: v for k, v in os.environ.items() if k not in ("AF_REQ_STATE", "CLAUDE_CODE_STOP_HOOK_BLOCK_CAP")}
    env.update(extra)
    return env


class World:
    """A runner tree (a temporary git repository), a fixture transcript, a state dir and a stack log dir."""

    def __init__(self, tmp_path, session="s1", registry=None):
        self.tmp = tmp_path
        self.repo = make_repo(tmp_path / "repo")
        self.tx = tmp_path / "transcript.jsonl"
        self.tx.write_bytes(b"")
        self.state = tmp_path / "jev"
        self.log = tmp_path / "stacklog"
        self.session = session
        self.env = base_env(AF_REQ_STATE=str(self.state))
        self.registry = registry
        self.n = 0

    def rec(self, obj, spaced=False):
        line = json.dumps(obj) if spaced else json.dumps(obj, separators=(",", ":"))
        with open(self.tx, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def _id(self, prefix):
        self.n += 1
        return "%s%d" % (prefix, self.n)

    def user(self, text, origin="human"):
        uid = self._id("u")
        self.rec({"type": "user", "uuid": uid, "turnOrigin": origin, "isSidechain": False,
                  "message": {"role": "user", "content": text}})
        return uid

    def text(self, text, msg=None, **kw):
        uid = self._id("a")
        self.rec({"type": "assistant", "uuid": uid, "isSidechain": False,
                  "message": {"id": msg or self._id("m"), "role": "assistant", "content": [{"type": "text",
                                                                                             "text": text}]}}, **kw)
        return uid

    def thinking(self, text, msg):
        uid = self._id("t")
        self.rec({"type": "assistant", "uuid": uid, "message": {"id": msg, "role": "assistant", "content": [
            {"type": "thinking", "thinking": text, "signature": "sig"}]}})
        return uid

    def tool_use(self, msg=None):
        uid = self._id("a")
        self.rec({"type": "assistant", "uuid": uid, "message": {"id": msg or self._id("m"), "role": "assistant",
                                                                "content": [{"type": "tool_use", "id": "toolu_1",
                                                                             "name": "Bash",
                                                                             "input": {"command": "ls"}}]}})
        self.rec({"type": "user", "uuid": self._id("r"), "message": {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": "toolu_1", "content": "a.txt"}]}})
        return uid

    def summary(self, blocking):
        uid = self._id("s")
        self.rec({"type": "system", "subtype": "stop_hook_summary", "uuid": uid, "hookCount": 3,
                  "hookErrors": ["blocked"] if blocking else [], "preventedContinuation": False})
        return uid

    def compact_summary(self, origin="human"):
        """A compaction's summary record: a user record with turnOrigin AND isCompactSummary (measured on this
        session's transcript, 7 of 7 compactions in its last 40 MB)."""
        uid = self._id("c")
        self.rec({"type": "user", "uuid": uid, "turnOrigin": origin, "isCompactSummary": True, "isSidechain": False,
                  "message": {"role": "user", "content": "This session is being continued from a previous "
                                                         "conversation."}})
        return uid

    def interrupt(self):
        uid = self._id("i")
        self.rec({"type": "user", "uuid": uid, "message": {"role": "user", "content": [
            {"type": "text", "text": "[Request interrupted by user]"}]}})
        return uid

    def api_error(self):
        uid = self._id("e")
        self.rec({"type": "system", "subtype": "api_error", "level": "error", "uuid": uid})
        return uid

    def hook(self, cmd, payload, *args, env=None, timeout=120, raw=None):
        data = raw if raw is not None else json.dumps(payload).encode()
        return subprocess.run([PY, str(LS), cmd, *args], input=data, capture_output=True, text=False,
                              env=env or self.env, timeout=timeout)

    def payload(self, **kw):
        return {"session_id": self.session, "transcript_path": str(self.tx), **kw}

    def prompt(self, text="go", env=None):
        r = self.hook("prompt", self.payload(prompt=text), env=env)
        assert r.returncode == 0 and r.stderr == b"", r.stderr
        ctx = json.loads(r.stdout)["hookSpecificOutput"]
        assert ctx["hookEventName"] == "UserPromptSubmit"
        self.context = ctx["additionalContext"]
        return NONCE_RX.search(self.context).group(1)

    def stop(self, lam=None, active=False, args=(), cwd=None, env=None, timeout=120, **kw):
        p = self.payload(stop_hook_active=active, cwd=str(cwd or self.repo), **kw)
        if lam is not None:
            p["last_assistant_message"] = lam
        opts = ["--tree", str(self.repo), "--log-dir", str(self.log)]
        if self.registry:
            opts += ["--registry", str(self.registry)]
        return self.hook("stop", p, *opts, *args, env=env, timeout=timeout)

    def ledger(self):
        path = self.state / "req" / "ledger.jsonl"
        return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []

    def runs(self):
        path = self.log / "runs.jsonl"
        return [json.loads(x) for x in path.read_text().splitlines() if '"run"' in x] if path.exists() else []

    def hooklog(self):
        return [json.loads(x) for x in (self.state / "req" / "hooks.jsonl").read_text().splitlines()]

    def st(self):
        return json.loads((self.state / "req" / "sessions" / (self.session + ".json")).read_text())


def res_lines(r):
    return [ln for ln in r.stderr.decode().split("\n") if ln.startswith("RES ")]


def receipts(r, nonce):
    """{id: the RES line's status} of a Stop's feedback (a malformed line's id is ?)."""
    out = {}
    for ln in res_lines(r):
        _res, n, cid, status = ln.split(" ", 3)
        assert n == nonce, ln
        out.setdefault(cid, []).append(status)
    return out


def end_step(pidfile, wait_s=5.0):
    """None when no step wrote its pid; False when the step is gone within wait_s; True when it outlived that (it is
    then killed, so no test leaves a sleeper behind)."""
    if not (pidfile.exists() and pidfile.read_text()):
        return None
    pid = int(pidfile.read_text())
    deadline = time.monotonic() + wait_s
    while time.monotonic() < deadline:
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return False
        time.sleep(0.1)
    try:
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        return False
    return True


@pytest.fixture
def w(tmp_path):
    return World(tmp_path)


@pytest.fixture
def wt(tmp_path):
    reg = tmp_path / "test-stacks.toml"
    reg.write_text(TEST_REGISTRY)
    return World(tmp_path, registry=reg)


# ---------------------------------------------------------------- the grammar (CONTRACT item 1)

def parse(text, nonces=("aaaaaaaaaaaa",)):
    return M.parse_message([("u1", text, 0)], list(nonces), "transcript")


N = "aaaaaaaaaaaa"


def test_a_well_formed_line_parses_into_the_runners_tokens():
    """Mutant: the params split on any whitespace, or the label taken as a param (the request dict shifts)."""
    [c] = parse("prose first\nREQ %s r1 premise files=a.txt,b.txt" % N)
    assert (c.kind, c.nonce, c.id, c.label, c.params, c.reason, c.line) == (
        "request", N, "r1", "premise", [["files", "a.txt,b.txt"]], None, 1)


def test_a_block_carries_backquotes_fences_and_request_shaped_lines_verbatim():
    """The body between key=<<WORD and WORD is the value, byte for byte: fences, backquotes, a $() and a line shaped
    like a request stay text (not a second request). Mutants: body lines stripped; the terminator matched with
    startswith (END2 would close END); block bodies scanned for request lines."""
    body = ["```python", "print(`x`)  # a backquote", "REQ %s r9 premise files=b.txt" % N, "$(rm -rf /) ; | &&",
            "END2", "   indented", "```"]
    [c] = parse("REQ %s r1 find q=<<END\n%s\nEND  \n" % (N, "\n".join(body)))
    assert (c.id, c.reason, c.params) == ("r1", None, [["q", "\n".join(body)]])
    two = parse("REQ %s r1 ctx q=<<A sym=<<B\nfirst value\nA\nsecond\nB" % N)
    assert [(c.id, c.params, c.reason) for c in two] == [("r1", [["q", "first value"], ["sym", "second"]], None)]


def test_an_unclosed_block_is_malformed_and_swallows_the_rest():
    """Mutant: an unclosed block accepted with the text so far (a half request would run)."""
    [c] = parse("REQ %s r1 find q=<<END\nline one\nline two" % N)
    assert c.reason == "an unclosed block: no line END before the end of the message"


def test_a_non_breaking_space_bold_markup_and_a_fence_are_malformed_never_silent():
    """The current nonce anywhere is intent (PM P3c): a non-breaking space, bold, a list mark, an upper-case nonce and a
    quoted receipt each give ONE malformed candidate with its reason. Mutants: only lines starting with REQ checked for
    the nonce (bold/list silent); the nonce test case-sensitive (upper case silent)."""
    nb = chr(0xA0)
    cases = {"REQ%s%s r1 premise files=a.txt" % (nb, N): "U+00A0",
             "REQ %s r1 premise%sfiles=a.txt" % (N, nb): "U+00A0",
             "**REQ %s r1 premise files=a.txt**" % N: "markup before REQ",
             "- REQ %s r1 premise files=a.txt" % N: "markup before REQ",
             "REQ %s r1 premise files=a.txt" % N.upper(): "12 lowercase hex",
             "RES %s r1 ran rc=0 run=s-x" % N: "a receipt quoted with the nonce",
             "see nonce %s above" % N: "the nonce outside a request line"}
    for line, why in cases.items():
        got = parse(line)
        assert [(c.kind, c.id) for c in got] == [("malformed", "?")], line
        assert why in got[0].reason, (line, got[0].reason)


def test_a_line_over_200_characters_parses():
    """PM P3c: the draft parser dropped a REQ line over 200 characters. Mutant: a length cap on request lines."""
    files = ",".join(["a.txt"] * 60)
    line = "REQ %s r1 premise files=%s" % (N, files)
    assert len(line) > 300
    [c] = parse(line)
    assert (c.kind, c.reason, c.params) == ("request", None, [["files", files]])


def test_request_lines_followed_by_more_text_are_all_refused_as_malformed():
    """The request lines close the message's text (PM P3's change): prose after them refuses every request of that
    message; blank lines and blocks are fine. Mutants: the closing rule dropped; only the last request refused."""
    got = parse("REQ %s r1 premise files=a.txt\n\nREQ %s r2 premise files=b.txt\nthat is all" % (N, N))
    assert [(c.id, c.reason) for c in got] == [
        ("r1", "text after the request lines: they close the message's text"),
        ("r2", "text after the request lines: they close the message's text")]
    fenced = parse("```\nREQ %s r1 premise files=a.txt\n```" % N)
    assert [(c.id, c.reason is not None) for c in fenced] == [("r1", True)]
    ok = parse("```\nREQ %s r1 premise files=a.txt\n\n   " % N)          # an unclosed fence before: it runs
    assert [(c.id, c.reason) for c in ok] == [("r1", None)]


def test_a_stale_shaped_line_is_a_request_and_prose_without_the_nonce_is_nothing():
    """A well-formed line with another nonce is a (stale) request; a broken line without the current nonce is text.
    Mutant: every REQ-looking line taken as a candidate (prose about REQ lines would get receipts)."""
    got = parse("REQ %s r1 premise files=a.txt" % OLD)
    assert [(c.kind, c.nonce, c.id) for c in got] == [("request", OLD, "r1")]
    assert parse("REQ lines close the text; REQ %s r1 (no label)" % OLD) == []


# ---------------------------------------------------------------- the transport through the real hook (items 2-4)

def test_a_request_runs_through_the_real_runner_with_its_run_id(w):
    """A real `premise` run: RES ran rc=0 run=<id>, the runner's print after it, exit 2 (the blocking channel), the
    run's record in the stack log and its step outputs saved. Mutant: the receipt without the run id, or exit 0."""
    n = w.prompt()
    w.text("Checking.\nREQ %s r1 premise files=a.txt" % n)
    r = w.stop()
    assert r.returncode == 2, r.stderr
    [res] = res_lines(r)
    m = re.fullmatch(r"RES %s r1 ran rc=0 run=(s-[0-9]{8}T[0-9]{6}Z-[0-9a-f]{6})" % n, res)
    assert m, res
    run = m.group(1)
    assert "stack premise · run %s · exit 0" % run in r.stderr.decode()
    [rec] = w.runs()
    assert (rec["run"], rec["label"], rec["params"]) == (run, "premise", {"files": ["a.txt"]})
    assert (w.log / run / "sha.out").read_text().split()[1] == "a.txt"


def test_a_request_in_an_earlier_text_block_of_the_final_message_runs(w):
    """PM P3a: the Stop input carries only the final message's last text block. Mutant: requests read from
    last_assistant_message only (r1 would get no receipt)."""
    n = w.prompt()
    w.text("Two stacks.\nREQ %s r1 premise files=a.txt" % n, msg="m-final")
    w.thinking("considering", msg="m-final")
    last = "REQ %s r2 premise files=b.txt" % n
    w.text(last, msg="m-final")
    r = w.stop(lam=last)
    assert r.returncode == 2
    assert {k: v[0].split(" ")[0] for k, v in receipts(r, n).items()} == {"r1": "ran", "r2": "ran"}


def test_a_request_before_a_thinking_only_final_block_runs(w):
    """PM P3b: the final block is thinking, so last_assistant_message is empty; the transcript still holds the
    request. Mutant: an empty last_assistant_message read as 'no request' (the hook returns at once)."""
    n = w.prompt()
    w.text("REQ %s r1 premise files=a.txt" % n, msg="m1")
    w.thinking("done thinking", msg="m1")
    r = w.stop(lam="")
    assert r.returncode == 2 and list(receipts(r, n)) == ["r1"]


def test_stop_hook_active_true_still_runs(w):
    """PM P1: stop_hook_active stays true for the rest of a user turn. Mutant: `if stop_hook_active: exit 0`."""
    n = w.prompt()
    w.text("REQ %s r1 premise files=a.txt" % n)
    r = w.stop(active=True)
    assert r.returncode == 2 and receipts(r, n)["r1"][0].startswith("ran rc=0")


def test_requests_inside_a_thinking_block_never_run_and_it_is_never_decoded(w, monkeypatch):
    """Never read a thinking block: a request line inside one gets no receipt (through the real hook), and the
    classifier skips a thinking record by its bytes, never decoding it: json.loads is counted, 0 calls for a thinking
    record, 1 for a text record (the control that the counter sees a decode). A thinking block whose type is spelled
    so the byte skip misses it (r8, in a record beside a text block) is decoded but never read as text. Mutants:
    thinking blocks read as text (r8 would get a receipt); the byte skip dropped (1 decode, not 0)."""
    n = w.prompt()
    w.thinking("REQ %s r9 premise files=a.txt" % n, msg="m1")
    with open(w.tx, "a") as fh:     # a type spelled so the byte skip misses it, beside a text block: the record is
        fh.write('{"type":"assistant","uuid":"t8","message":{"id":"m0","role":"assistant","content":[{"type":'
                 '"\\u0074hinking","thinking":"REQ %s r8 premise files=a.txt","signature":"s"},{"type":"text",'
                 '"text":"Plain."}]}}\n' % n)                  # decoded, and only its text block is read
    w.text("REQ %s r1 premise files=a.txt" % n, msg="m1")
    r = w.stop()
    assert list(receipts(r, n)) == ["r1"]
    decodes, real = [], json.loads
    monkeypatch.setattr(M, "json", types.SimpleNamespace(loads=lambda raw: decodes.append(1) or real(raw)))

    def record(block):
        return json.dumps({"type": "assistant", "uuid": "x1", "message": {"id": "m9", "role": "assistant",
                                                                         "content": [block]}},
                          separators=(",", ":")).encode() + b"\n"
    line = "REQ %s r9 premise files=a.txt" % N
    assert M.classify(record({"type": "thinking", "thinking": line, "signature": "s"}), 0) is None and decodes == []
    got = M.classify(record({"type": "text", "text": line}), 0)
    assert (got.kind, got.text, len(decodes)) == ("text", line, 1)


def test_a_spaced_json_transcript_is_read_too(w):
    """A writer that spaces its JSON ("type": "text") must not blind the byte prefilters. Mutant: the compact
    pattern only (the request would get no receipt: a silent drop)."""
    n = w.prompt()
    w.text("REQ %s r1 premise files=a.txt" % n, spaced=True)
    r = w.stop()
    assert r.returncode == 2 and list(receipts(r, n)) == ["r1"]


def test_the_argument_vector_carries_a_block_verbatim_and_no_shell_runs_it(wt):
    """A block's value reaches the step as ONE argument, backquotes, $(), ; and | intact: printed back by a step that
    echoes its argv as JSON, and no file the text names is created. A multi-line block reaches the runner, whose
    text rule refuses it (a parameter the runner refuses). Mutants: the value shell-joined; the block value stripped."""
    n = wt.prompt()
    value = "who calls `parse_lock`? $(touch pwned) ; echo hi | cat && x"
    wt.text("REQ %s r1 echoargs q=<<Q\n%s\nQ\nREQ %s r2 echoargs q=<<Q\nline one\nline two\nQ" % (n, value, n))
    r = wt.stop()
    got = receipts(r, n)
    assert got["r1"][0].startswith("ran rc=0"), got
    assert json.dumps([value]) in r.stderr.decode()
    assert not (wt.repo / "pwned").exists()
    assert got["r2"] == ["refused: q=line one line two refused: a text holds no NUL and no newline"], got["r2"]


# ---------------------------------------------------------------- the nonce (item 2)

def test_no_nonce_this_turn_means_the_hook_does_nothing(w):
    """No prompt hook ran (no state): request-shaped lines never run and nothing is written. Mutant: a Stop without
    state treating any 12-hex token as current."""
    w.text("REQ %s r1 premise files=a.txt" % OLD)
    r = w.stop()
    assert (r.returncode, r.stdout, r.stderr) == (0, b"", b"")
    assert w.ledger() == [] and w.runs() == [] and not (w.state / "req" / "sessions").exists()


def test_a_stale_nonce_never_runs_and_alone_never_blocks_but_is_reported_next_prompt(w):
    """An old nonce: refused: stale nonce, never run. Beside a current request it rides in the feedback; alone it
    never blocks (item 10) and the next prompt reports it (nothing drops silently). Mutants: stale lines run; a
    stale-only Stop blocks; the stale receipt never reported."""
    n = w.prompt()
    w.text("REQ %s r1 premise files=a.txt\nREQ %s r2 premise files=a.txt" % (OLD, n))
    r = w.stop()
    lines = res_lines(r)                           # the old nonce's line is answered under its own nonce
    assert lines[0] == "RES %s r1 refused: stale nonce (not this turn's)" % OLD
    assert lines[1].startswith("RES %s r2 ran rc=0" % n)
    assert len(w.runs()) == 1
    w.summary(blocking=True)
    w.text("REQ %s r3 premise files=b.txt" % OLD)
    r = w.stop(active=True)
    assert (r.returncode, r.stderr) == (0, b"") and len(w.runs()) == 1
    w.summary(blocking=False)
    w.prompt()
    assert "delivered late: RES %s r3 refused: stale nonce (not this turn's)" % OLD in w.context
    assert [x["status"] for x in w.ledger() if x["id"] == "r3"] == ["refused"]


def test_a_duplicate_id_is_refused_within_a_round_and_across_rounds(w):
    """Each request line takes a new id. Mutants: the second r1 in a round runs; an id answered last round runs
    again."""
    n = w.prompt()
    w.text("REQ %s r1 premise files=a.txt\nREQ %s r1 premise files=b.txt" % (n, n))
    r = w.stop()
    got = receipts(r, n)
    assert got["r1"][0].startswith("ran") and got["r1"][1].startswith("refused: duplicate id")
    w.summary(blocking=True)
    w.text("REQ %s r1 premise files=b.txt" % n)
    r = w.stop(active=True)
    assert receipts(r, n)["r1"][0].startswith("refused: duplicate id") and len(w.runs()) == 1


def test_the_valid_set_keeps_the_last_nonces_while_the_query_runs(w):
    """UserPromptSubmit fires for messages absorbed mid-turn (7 of 23 prompt-hook batches in this session's
    transcript): the new nonce joins the set while the query runs, and an ended query resets it. Mutants: every prompt
    resets the set (the first nonce is stale mid-turn); the set never resets (an ended turn's nonce stays live)."""
    n1 = w.prompt()
    w.tool_use()
    n2 = w.prompt("a message absorbed mid-turn")
    assert n2 != n1 and w.st()["nonces"] == [n1, n2]
    w.text("REQ %s r1 premise files=a.txt" % n1)
    r = w.stop()
    assert res_lines(r)[0].startswith("RES %s r1 ran" % n1)
    w.summary(blocking=False)
    n3 = w.prompt()
    assert w.st()["nonces"] == [n3]
    w.text("REQ %s r2 premise files=a.txt\nREQ %s r3 premise files=a.txt" % (n1, n3))
    lines = res_lines(w.stop())
    assert lines[0] == "RES %s r2 refused: stale nonce (not this turn's)" % n1 and lines[1].startswith(
        "RES %s r3 ran" % n3)
    for _ in range(5):
        w.prompt()
    assert len(w.st()["nonces"]) == M.KEEP_NONCES and n3 not in w.st()["nonces"]


def test_the_prompt_hook_injects_one_line_with_the_nonce_and_the_grammar(w):
    """ONE line, the nonce three times (the fixed prefix, the REQ form, the RES form). Mutant: a multi-line text."""
    n = w.prompt()
    assert "\n" not in w.context and w.context.count(n) == 3 and "key=<<END" in w.context
    assert len(w.context) < 600


# ---------------------------------------------------------------- the cap and the budget (item 3)

def test_the_cap_refusal_at_cap_minus_one_runs_nothing(w):
    """PM P2: the harness counts consecutive blocking Stops with no tool call between; above the cap it ends the turn
    and drops the feedback. Blocking summaries since the last tool call put this Stop at cap-1: every request is
    refused loudly and nothing runs. One fewer: it runs. A tool call in between resets; a compaction's summary record
    (it carries turnOrigin) does not. Mutants: the count ignores the transcript's summaries; the cap read without the
    env; `>` for `>=`; no reset on a tool call; a compaction's summary taken for a new prompt (the count resets)."""
    env = dict(w.env, CLAUDE_CODE_STOP_HOOK_BLOCK_CAP="4")
    n = w.prompt()
    w.summary(blocking=True)
    w.compact_summary()                           # a compaction between the two: not a new prompt
    w.summary(blocking=True)                      # two blocking Stops: this one would be the third = cap - 1
    w.text("REQ %s r1 premise files=a.txt" % n)
    r = w.stop(active=True, env=env)
    assert r.returncode == 2 and w.runs() == []
    [res] = res_lines(r)
    assert res == ("RES %s r1 refused: cap: nothing ran; continue with tool calls (python3 scripts/stack.py premise "
                   "...): this is blocking Stop 3 in a row with no tool call, and above 4 the harness ends the "
                   "turn" % n)
    assert "REFUSED AT THE CAP" in r.stderr.decode()
    w.tool_use()                                   # a tool round resets the harness count
    w.summary(blocking=True)
    w.text("REQ %s r2 premise files=a.txt" % n)
    r = w.stop(active=True, env=env)
    assert receipts(r, n)["r2"][0].startswith("ran rc=0") and len(w.runs()) == 1


def test_the_default_cap_is_8_and_the_own_count_holds_without_summaries(w):
    """With the env unset the cap is 8: six blocking Stops before this one refuse (7 = cap - 1). The hook's own count
    covers rounds whose summaries the transcript lacks. Mutants: a default other than 8; the own count not kept."""
    n = w.prompt()
    for _ in range(6):
        w.summary(blocking=True)
    w.text("REQ %s r1 premise files=a.txt" % n)
    [res] = res_lines(w.stop(active=True))
    assert res.startswith("RES %s r1 refused: cap: nothing ran;" % n) and "blocking Stop 7 in a row" in res, res
    assert res.endswith("above 8 the harness ends the turn"), res
    w2 = World(w.tmp / "second")
    env = dict(w2.env, CLAUDE_CODE_STOP_HOOK_BLOCK_CAP="3")
    m = w2.prompt()
    w2.text("REQ %s r1 premise files=a.txt" % m)
    assert receipts(w2.stop(env=env), m)["r1"][0].startswith("ran")
    w2.text("REQ %s r2 premise files=a.txt" % m)   # no summary written, no tool call: the hook's own count is 1
    assert receipts(w2.stop(active=True, env=env), m)["r2"][0].startswith("refused: cap")


def test_the_budget_stops_a_run_and_refuses_what_it_cannot_start(wt):
    """Requests past the round's budget get refused: budget: the running one is stopped (SIGTERM to the runner, which
    kills its steps) and the next is never started; the hook returns inside the budget plus the grace, and the
    sleeping step is gone. Mutants: no timeout on the run (the hook waits two minutes); the runner killed with SIGKILL
    first (its step would outlive it)."""
    n = wt.prompt()
    pidfile = wt.tmp / "sleeper.pid"
    wt.text("REQ %s r1 slow pidfile=%s\nREQ %s r2 echoargs q=never" % (n, pidfile, n))
    t0 = time.monotonic()
    try:
        r = wt.stop(args=("--budget", "7"), timeout=60)
    finally:
        took = time.monotonic() - t0
        outlived = end_step(pidfile)                # never leaves the sleeper behind, whatever failed
    got = receipts(r, n)
    assert got["r1"][0].startswith("refused: budget (stopped after"), got
    assert got["r2"][0].startswith("refused: budget (") and "not started" in got["r2"][0], got
    assert outlived is False, "the sleeping step outlived the budget"
    assert 6 < took < 7 + M.KILL_GRACE_S + 3, took


@pytest.mark.parametrize("sig", [signal.SIGTERM, signal.SIGINT])
def test_a_signal_to_the_hook_ends_its_runner_and_the_request_is_reported(wt, sig):
    """The harness stops a hook by a signal (its timeout, an interrupt). The runner runs in its own session, so only
    the hook can pass the signal on: the hook ends it (SIGTERM to its group, the runner kills its steps), exits 128+N,
    and the request, which got no receipt, is reported at the next prompt. Mutants: no handler for the signal (the
    runner and its sleeping step outlive the hook: an orphan run nobody reports); the handler not ending the runner."""
    n = wt.prompt()
    pidfile = wt.tmp / "sleeper.pid"
    wt.text("REQ %s r1 slow pidfile=%s" % (n, pidfile))
    p = wt.payload(stop_hook_active=False, cwd=str(wt.repo))
    hook = subprocess.Popen([PY, str(LS), "stop", "--tree", str(wt.repo), "--log-dir", str(wt.log), "--registry",
                             str(wt.registry)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            env=wt.env)
    hook.stdin.write(json.dumps(p).encode())
    hook.stdin.close()
    try:
        for _ in range(300):
            if pidfile.exists() and pidfile.read_text():
                break
            time.sleep(0.05)
        else:
            pytest.fail("the step never started")
        hook.send_signal(sig)
        rc = hook.wait(timeout=30)
    finally:
        if hook.poll() is None:
            hook.kill()
            hook.wait()
        hook.stdout.close()
        hook.stderr.close()
        outlived = end_step(pidfile)
    assert rc == 128 + sig and outlived is False, (rc, outlived)
    stopped = wt.interrupt()
    wt.prompt()
    assert "unanswered: r1 slow (an interrupt, transcript record %s)" % stopped in wt.context
    assert [(x["id"], x["status"]) for x in wt.ledger()] == [("r1", "unanswered")] and wt.runs() == []


# ---------------------------------------------------------------- receipts, the ledger and the pairing (items 4, 6)

def test_exactly_one_receipt_per_request_line_refusals_included_and_one_ledger_row_each(w):
    """A round of every kind: a malformed line, a run, an unknown label, a parameter the runner refuses, a stale nonce,
    a duplicate id. Each line: ONE RES line and ONE ledger row. Re-running the same Stop from its old offset (a crash
    before the state was saved) adds nothing and runs nothing. Mutants: a malformed line dropped; the runner's
    refusal lost; the (uuid, line) identity not checked (the re-run duplicates every row)."""
    n = w.prompt()
    w.text("**REQ %s r7 premise files=a.txt**\nREQ %s r1 premise files=a.txt\nREQ %s r2 nosuch x=1\n"
           "REQ %s r3 premise files=\nREQ %s r4 premise files=a.txt\nREQ %s r1 premise files=b.txt" % (
               n, n, n, n, OLD, n))
    before = w.st()
    r = w.stop()
    lines = res_lines(r)
    assert len(lines) == 6, lines
    assert lines[0].startswith("RES %s ? refused: malformed (text or markup before REQ" % n)
    assert lines[1].startswith("RES %s r1 ran rc=0" % n)
    assert lines[2].startswith("RES %s r2 refused: unknown label 'nosuch' (the stacks: " % n)
    assert lines[3].startswith("RES %s r3 refused: files= refused: an empty" % n)
    assert lines[4] == "RES %s r4 refused: stale nonce (not this turn's)" % OLD
    assert lines[5].startswith("RES %s r1 refused: duplicate id" % n)
    rows = w.ledger()
    assert [(x["id"], x["status"]) for x in rows] == [("?", "refused"), ("r1", "ran"), ("r2", "refused"),
                                                      ("r3", "refused"), ("r4", "refused"), ("r1", "refused")]
    assert len(w.runs()) == 1
    (w.state / "req" / "sessions" / "s1.json").write_text(json.dumps(before))     # the crash: the offset rolled back
    again = w.stop()
    assert (again.returncode, again.stderr) == (0, b"") and len(w.ledger()) == 6 and len(w.runs()) == 1


def test_a_ledger_row_pairs_the_chat_before_a_request_with_its_label_and_its_result(w):
    """CONTRACT item 6, the export's join on a fixture (the export itself is not built): from a ledger row, the
    transcript record by uuid holds the request line; the records before it are the chat that led to it; the run's
    record in runs.jsonl and its saved outputs are the result. Mutants: the row without the record uuid, the run id
    or the run dir."""
    n = w.prompt()
    asked = w.user("what does a.txt hold?")
    w.text("Looking.\nREQ %s r1 premise files=a.txt" % n)
    w.stop()
    [row] = w.ledger()
    assert {"session", "nonce", "id", "label", "status", "run", "uuid", "transcript", "run_dir"} <= set(row)
    records = [json.loads(x) for x in Path(row["transcript"]).read_text().splitlines()]
    at = next(i for i, x in enumerate(records) if x.get("uuid") == row["uuid"])
    carrier = records[at]["message"]["content"][0]["text"].split("\n")[row["line"]]
    assert carrier == "REQ %s r1 premise files=a.txt" % n
    chat = [x["uuid"] for x in records[:at] if x.get("type") in ("user", "assistant")]
    assert asked in chat
    [run] = [x for x in w.runs() if x["run"] == row["run"]]
    assert run["label"] == row["label"] == "premise"
    assert row["run_dir"] == os.path.realpath(w.log / row["run"]) and (Path(row["run_dir"]) / "tracked.out").is_file()


def test_the_feedback_is_capped_with_every_res_line_whole_and_the_cut_named(wt):
    """Over FEEDBACK_CAP the runner prints are cut, largest first, every RES line kept whole, each cut naming its saved
    file (the note names their directory once); control tags in the feedback are neutralized. 28 large prints force the
    cap; a request the runner refuses has a short print that carries a tag and stays whole. Mutants: no cap; a RES
    line cut; the saved print not named; the neutralizer not applied (the tag raw in r29's receipt); the smallest print
    cut first (r29's print cut)."""
    n = wt.prompt()
    reqs = ["REQ %s r%d echoargs q=%s%d" % (n, i, "x" * 400, i) for i in range(1, 29)]
    reqs.append("REQ %s r29 echoargs q=-%s" % (n, TAG))
    wt.text("\n".join(reqs))
    r = wt.stop()
    text = r.stderr.decode()
    outdir = wt.state / "req" / "out" / "s1"
    assert r.returncode == 2 and M.u16(text) <= M.FEEDBACK_CAP < M.u16(
        "".join(p.read_text() for p in outdir.iterdir()))
    got = receipts(r, n)
    assert sorted(got) == sorted("r%d" % i for i in range(1, 30)) and all(len(v) == 1 for v in got.values()), got
    assert all(got["r%d" % i][0].startswith("ran rc=0 run=s-") for i in range(1, 29)), got
    neut = "<\\" + TAG[1:]
    assert got["r29"] == ["refused: q=-%s refused: '-%s' begins with '-' (option injection)" % (neut, neut)]
    assert TAG not in text and ("stack: q=-%s refused:" % neut) in text
    assert ("a cut print is saved in full in %s/, under the name its cut gives" % outdir) in text
    sections = {s.split(" ", 3)[2]: s for s in re.split(r"(?m)^(?=RES )", text)[1:]}
    for i in range(1, 29):
        name = "%s-r%d.txt" % (n, i)
        assert ("characters cut; in full: %s\n" % name) in sections["r%d" % i], sections["r%d" % i]
        assert (outdir / name).is_file()
    assert "characters cut" not in sections["r29"]
    assert TAG in (outdir / ("%s-r29.txt" % n)).read_text()          # the saved file keeps the print as it was


def test_receipts_past_the_cap_are_carried_to_the_next_prompt(w):
    """When even the RES lines are over FEEDBACK_CAP (100 lines that carry the nonce, each refused as malformed), the
    feedback shows the receipts that fit and says how many more there are, and the next prompt's context carries the
    rest: every line gets its receipt, none silently. Mutants: the receipts past the cap dropped from the undelivered
    list; the RES lines not capped."""
    n = w.prompt()
    w.text("\n".join("see %s here %d" % (n, i) for i in range(100)))
    r = w.stop()
    text, shown = r.stderr.decode(), res_lines(r)
    assert r.returncode == 2 and M.u16(text) <= M.FEEDBACK_CAP and 50 < len(shown) < 100, (M.u16(text), len(shown))
    assert ("\u2026 %d more receipts: the next prompt's context carries them\n" % (100 - len(shown))) in text
    assert len(w.ledger()) == 100 and len(w.st()["undelivered"]) == 100 - len(shown)
    w.summary(blocking=True)
    w.prompt()
    late = [x for x in w.context.split("\n") if x.startswith(
        "delivered late: RES %s ? refused: malformed (the nonce outside a request line" % n)]
    assert len(late) == 100 - len(shown) and w.st()["undelivered"] == []


# ---------------------------------------------------------------- the reconciler (item 5)

def test_an_interrupted_turn_is_reported_unanswered_at_the_next_prompt_and_never_run(w):
    """PM P3d: no Stop hook runs on an interrupt. The next prompt reports `unanswered: r1 premise (an interrupt,
    transcript record <uuid>)`, writes that receipt, and runs nothing. Mutants: no reconciler (silence); the
    reconciler runs the request."""
    n = w.prompt()
    w.text("%s see %s\nREQ %s r1 premise files=a.txt" % (TAG, n, n))
    stopped = w.interrupt()
    w.prompt()
    assert "unanswered: r1 premise (an interrupt, transcript record %s)" % stopped in w.context
    assert ("unanswered: ? (a line with the nonce: <\\%s see %s) (an interrupt" % (TAG[1:], n)) in w.context
    assert TAG not in w.context                    # the report's lines are neutralized like the Stop feedback
    assert w.runs() == []
    assert [(x["status"], x["id"], x["delivered"]) for x in w.ledger()] == [("unanswered", "?", "context"),
                                                                           ("unanswered", "r1", "context")]


def test_an_api_error_and_an_unknown_ending_are_named(w):
    """The reconciler names how the turn ended: an API error record, or unknown. Mutant: every ending read as an
    interrupt."""
    n = w.prompt()
    w.text("REQ %s r1 premise files=a.txt" % n)
    err = w.api_error()
    w.prompt()
    assert "unanswered: r1 premise (an API error, transcript record %s)" % err in w.context
    n = w.prompt()
    w.text("REQ %s r2 premise files=a.txt" % n)
    w.summary(blocking=False)                      # a Stop that did not answer: the hook was not registered, say
    w.prompt()
    assert "unanswered: r2 premise (unknown: no interrupt or error after it" in w.context


def test_a_request_with_a_receipt_is_not_reported(w):
    """Mutant: the reconciler ignores the ledger (an answered request reported as unanswered)."""
    n = w.prompt()
    w.text("REQ %s r1 premise files=a.txt" % n)
    assert w.stop().returncode == 2
    w.summary(blocking=True)
    w.text("Done.")
    w.summary(blocking=False)
    n2 = w.prompt()
    assert w.context == M.NONCE_LINE.format(n=n2), w.context      # the nonce line alone: nothing reported


def test_session_start_keeps_a_running_query_and_reconciles_an_ended_one(w):
    """A compaction inside a running query: the current nonce comes back (the compaction dropped it from the context)
    and the pending request is left to the next Stop, which runs it. A restart (source resume) ends the query: its
    unanswered request is reported with the restart named, no nonce is injected and the form is off until the next
    prompt, after which the old nonce is stale. Mutants: no SessionStart reconcile; the nonce not re-injected at a
    compaction; a compaction inside a running query reconciled as ended (r1 answered `unanswered`, never run); the old
    nonce still valid after a restart."""
    n = w.prompt()
    w.tool_use()
    w.text("REQ %s r1 premise files=a.txt" % n)
    w.compact_summary()
    r = w.hook("session-start", w.payload(source="compact"))
    ctx = json.loads(r.stdout)["hookSpecificOutput"]
    assert (ctx["hookEventName"], ctx["additionalContext"]) == ("SessionStart", M.NONCE_LINE.format(n=n))
    assert w.st()["nonces"] == [n] and w.ledger() == []
    assert receipts(w.stop(), n)["r1"][0].startswith("ran rc=0")
    w.summary(blocking=True)
    w.text("REQ %s r2 premise files=a.txt" % n)
    r = w.hook("session-start", w.payload(source="resume"))
    ctx = json.loads(r.stdout)["hookSpecificOutput"]["additionalContext"]
    assert ("unanswered: r2 premise (unknown: the session restarted (SessionStart, source resume) before a Stop "
            "answered it)") in ctx, ctx
    assert NONCE_RX.search(ctx) is None and w.st()["nonces"] == [] and len(w.runs()) == 1
    assert [(x["id"], x["status"]) for x in w.ledger()] == [("r1", "ran"), ("r2", "unanswered")]
    w.text("REQ %s r3 premise files=a.txt" % n)
    assert (w.stop().returncode, len(w.runs())) == (0, 1)             # off until the next prompt
    n2 = w.prompt()
    assert w.st()["nonces"] == [n2]
    w.text("REQ %s r4 premise files=a.txt\nREQ %s r5 premise files=a.txt" % (n, n2))
    lines = res_lines(w.stop())
    assert lines[0] == "RES %s r3 refused: stale nonce (not this turn's)" % n, lines
    assert lines[1] == "RES %s r4 refused: stale nonce (not this turn's)" % n, lines
    assert lines[2].startswith("RES %s r5 ran rc=0" % n2) and len(lines) == 3, lines
    r = w.hook("session-start", {"session_id": "never-seen", "transcript_path": str(w.tx), "source": "startup"})
    assert (r.returncode, r.stdout, r.stderr) == (0, b"", b"")


# ---------------------------------------------------------------- the retro gate's deferral and the git check (item 7)

def test_defer_check_says_defer_only_when_this_stop_answers_a_current_nonce(w):
    """The retro gate asks: a current nonce in a text written since the last Stop (whose summary record the harness
    writes after the hooks end), or in last_assistant_message, prints `defer`, exit 0: this Stop answers requests. An
    earlier round's request (a Stop summary after it), a stale nonce, a thinking-only final message and a failure exit
    1 with nothing on stdout. Mutants: defer on any REQ-shaped line; defer on a request an earlier Stop answered;
    only the last message read (r3 before a tool call missed); exit 0 on a failure."""
    n = w.prompt()

    def ask(**kw):
        r = w.hook("defer-check", w.payload(**kw))
        return r.returncode, r.stdout.decode()

    w.text("REQ %s r1 premise files=a.txt" % n)
    assert ask() == (0, "defer\n")
    w.summary(blocking=True)                       # the Stop that answered r1
    w.tool_use()
    w.text("All done, no requests.")
    assert ask() == (1, "")
    assert ask(last_assistant_message="REQ %s r2 premise files=a.txt" % n) == (0, "defer\n")
    assert ask(last_assistant_message="REQ %s r2 premise files=a.txt" % OLD) == (1, "")
    w.summary(blocking=False)
    w.text("REQ %s r3 premise files=a.txt" % n)    # this round: a request, then a tool call, then plain text
    w.tool_use()
    w.text("Plain.")
    assert ask() == (0, "defer\n")
    w.summary(blocking=True)
    w.thinking("only thinking", msg="m-last")      # a thinking-only final message after the answered round
    assert ask(last_assistant_message="") == (1, "")
    r = w.hook("defer-check", None, raw=b"not json")
    assert (r.returncode, r.stdout) == (1, b"")


def remote_repo(tmp_path):
    """A repository with a bare origin that holds its main branch."""
    origin = tmp_path / "origin.git"
    git(tmp_path, "init", "-q", "--bare", "-b", "main", str(origin))
    repo = make_repo(tmp_path / "work")
    git(repo, "remote", "add", "origin", str(origin))
    git(repo, "push", "-q", "origin", "main")
    return repo


def test_the_chain_end_runs_the_git_checks_once_in_the_harness_checks_words(w):
    """PM P4: after a receipt round the harness git check is silent (stop_hook_active); at the chain's end this hook
    runs its dirty and unpushed checks in the payload's cwd, reports the first hit in its words, once per chain.
    Mutants: the report every Stop (a loop); the report while stop_hook_active is false (the harness check speaks
    then); the unpushed check left out; the untracked check left out."""
    repo = remote_repo(w.tmp)
    n = w.prompt()
    w.text("REQ %s r1 premise files=a.txt" % n)
    assert w.stop(active=True, cwd=repo).returncode == 2
    (repo / "new.txt").write_text("x\n")
    w.summary(blocking=True)
    w.text("Done.")
    r = w.stop(active=True, cwd=repo)
    assert r.returncode == 2 and r.stderr.decode().endswith(M.GIT_UNTRACKED + "\n")
    w.summary(blocking=True)
    w.text("Still done.")
    assert (w.stop(active=True, cwd=repo).returncode, w.stop(active=True, cwd=repo).stderr) == (0, b"")
    (repo / "new.txt").unlink()
    git(repo, "commit", "-q", "--allow-empty", "--no-verify", "-m", "local")
    w.summary(blocking=False)
    n = w.prompt()
    w.text("REQ %s r2 premise files=a.txt" % n)
    assert w.stop(active=True, cwd=repo).returncode == 2
    w.summary(blocking=True)
    w.text("Done again.")
    r = w.stop(active=True, cwd=repo)
    assert r.returncode == 2 and r.stderr.decode().endswith(
        "There are 1 unpushed commit(s) on branch 'main'. Please push these changes to the remote repository.\n")
    w.summary(blocking=False)
    n = w.prompt()
    w.text("REQ %s r3 premise files=a.txt" % n)
    assert w.stop(active=False, cwd=repo).returncode == 2
    w.summary(blocking=True)
    w.text("Done.")
    assert w.stop(active=False, cwd=repo).returncode == 0


def test_the_git_report_mirrors_the_harness_check(tmp_path):
    """The words and the order of /root/.claude/stop-hook-git-check.sh: uncommitted first, then untracked, then
    unpushed; no remote or no repository: nothing. Mutant: the order changed (untracked reported over uncommitted)."""
    repo = remote_repo(tmp_path)
    assert M.git_report(str(repo)) is None
    (repo / "a.txt").write_text("changed\n")
    (repo / "new.txt").write_text("x\n")
    assert M.git_report(str(repo)) == M.GIT_UNCOMMITTED
    git(repo, "checkout", "--", "a.txt")
    assert M.git_report(str(repo)) == M.GIT_UNTRACKED
    bare = make_repo(tmp_path / "noremote")
    (bare / "new.txt").write_text("x\n")
    assert M.git_report(str(bare)) is None and M.git_report(str(tmp_path)) is None


# ---------------------------------------------------------------- the off switch, fail loud (items 9, 10)

@pytest.mark.parametrize("dangling", [False, True])
def test_the_off_switch_silences_every_subcommand_and_writes_nothing(w, dangling):
    """While <state>/req-off exists (a dangling link counts): with a live state and a pending current-nonce request,
    the Stop runs nothing and blocks nothing, defer-check says no, SessionStart and the prompt hook inject nothing, and
    no file changes; with the switch gone the same Stop runs the request (the state was intact: the switch alone held
    it). Mutants: the switch read by the prompt hook only; `exists` for `lexists` (a dangling link ignored)."""
    n = w.prompt()
    w.text("REQ %s r1 premise files=a.txt" % n)
    before = {p: p.read_bytes() for p in (w.state / "req").rglob("*") if p.is_file()}
    off = w.state / "req-off"
    if dangling:
        os.symlink(w.tmp / "absent", off)
    else:
        off.write_text("off\n")
    r = w.stop()
    assert (r.returncode, r.stdout, r.stderr, w.runs()) == (0, b"", b"", [])
    r = w.hook("defer-check", w.payload())
    assert (r.returncode, r.stdout) == (1, b"")
    r = w.hook("session-start", w.payload(source="compact"))
    assert (r.returncode, r.stdout, r.stderr) == (0, b"", b"")
    r = w.hook("prompt", w.payload(prompt="go"))
    assert (r.returncode, r.stdout, r.stderr) == (0, b"", b"")
    assert {p: p.read_bytes() for p in (w.state / "req").rglob("*") if p.is_file()} == before
    off.unlink()
    assert receipts(w.stop(), n)["r1"][0].startswith("ran rc=0")


def test_a_hook_error_is_one_line_and_never_blocks(w):
    """A broken payload, a missing transcript, a corrupt state: one line naming what failed, exit 0 (defer-check 1).
    The prompt hook says it in the context and starts a fresh state, so the chat form does not stay off. Mutants:
    exit 2 on an error (a stall); a traceback; the corrupt state kept (every later prompt fails)."""
    r = w.hook("stop", None, raw=b"{broken")
    assert r.returncode == 0 and r.stderr.decode().count("\n") == 1 and "not JSON" in r.stderr.decode()
    r = w.hook("stop", {"session_id": "s1", "transcript_path": str(w.tmp / "missing.jsonl")})
    assert r.returncode == 0 and "transcript_path" in r.stderr.decode()
    n = w.prompt()
    (w.state / "req" / "sessions" / "s1.json").write_text("{not json")
    w.text("REQ %s r1 premise files=a.txt" % n)
    r = w.stop()
    assert r.returncode == 0 and "unreadable" in r.stderr.decode() and r.stderr.decode().count("\n") == 1
    n2 = w.prompt()
    assert "unreadable" in w.context and n2 != n and w.st()["nonces"] == [n2]
    w.text("REQ %s r2 premise files=a.txt" % n2)
    (w.state / "req" / "ledger.jsonl").mkdir()     # an unreadable ledger is an error, never an empty ledger
    r = w.stop()
    err = r.stderr.decode()
    assert (r.returncode, err.count("\n"), w.runs()) == (0, 1, []), err
    assert err.startswith("ls_req stop: the ledger %s is unreadable (IsADirectoryError)" % (
        w.state / "req" / "ledger.jsonl")), err


def test_a_failed_ledger_write_still_delivers_the_receipts(w):
    """The requests ran, so their receipts go out even when the ledger cannot be written, with the failure named.
    Mutant: the write error propagates (exit 0: the results are lost)."""
    n = w.prompt()
    w.text("REQ %s r1 premise files=a.txt" % n)
    (w.state / "req" / "ledger.lock").mkdir(parents=True)   # the lock cannot be opened: every append fails, the
    r = w.stop()                                            # read of the (absent) ledger does not
    assert r.returncode == 2 and receipts(r, n)["r1"][0].startswith("ran rc=0") and len(w.runs()) == 1
    assert "NOT WRITTEN: the ledger row of r1 ([Errno 21] Is a directory" in r.stderr.decode()
    assert not (w.state / "req" / "ledger.jsonl").exists()


def test_the_default_state_is_the_main_trees_even_from_a_worktree(tmp_path):
    """No AF_REQ_STATE: the state lands in the MAIN tree's .jev/req, found through git's common dir, also when the
    scripts run from a linked worktree (AF-AP-235's class), and the off switch is the main tree's .jev/req-off.
    Mutant: the state under the script's own tree (a worktree would keep its own ledger)."""
    repo = tmp_path / "main"
    (repo / "scripts").mkdir(parents=True)
    for name in ("ls_req.py", "stack.py", "stacks.toml", "handback_extract.py"):
        shutil.copyfile(ROOT / "scripts" / name, repo / "scripts" / name)
    git(repo, "init", "-q", "-b", "main")
    git(repo, "add", ".")
    git(repo, "commit", "-q", "--no-verify", "-m", "scripts")
    lane = tmp_path / "lane"
    git(repo, "worktree", "add", "-q", "--detach", str(lane), "HEAD")
    tx = tmp_path / "t.jsonl"
    tx.write_text("")
    payload = json.dumps({"session_id": "s9", "transcript_path": str(tx), "prompt": "go"}).encode()
    r = subprocess.run([PY, str(lane / "scripts" / "ls_req.py"), "prompt"], input=payload, capture_output=True,
                       env=base_env(), timeout=60)
    assert r.returncode == 0 and b"nonce" in r.stdout, r.stdout
    assert (repo / ".jev" / "req" / "sessions" / "s9.json").is_file() and not (lane / ".jev").exists()
    (repo / ".jev" / "req-off").write_text("")
    r = subprocess.run([PY, str(lane / "scripts" / "ls_req.py"), "prompt"], input=payload, capture_output=True,
                       env=base_env(), timeout=60)
    assert (r.returncode, r.stdout) == (0, b"")


# ---------------------------------------------------------------- the offsets and the time (item 3)

def test_the_stop_reads_from_its_stored_offset_never_the_whole_file(w):
    """A current-nonce request line BEFORE the stored offset is never collected, and the hook's own record counts the
    bytes it read: the window, not the file. Mutant: the scan from byte 0 (the old line runs; the bytes are the
    file's)."""
    n = w.prompt()
    w.text("REQ %s r1 premise files=a.txt" % n)
    st = w.st()
    size = w.tx.stat().st_size
    st.update(turn_start=size, read=size)
    (w.state / "req" / "sessions" / "s1.json").write_text(json.dumps(st))
    w.text("No request here.")
    r = w.stop()
    assert (r.returncode, r.stderr) == (0, b"") and w.runs() == []
    rec = [x for x in w.hooklog() if x["event"] == "stop"][-1]
    assert rec["bytes"] == w.tx.stat().st_size - size


def test_the_stop_hook_time_on_a_large_transcript_is_bounded(w):
    """40 MB of records before the turn (the coordinator's transcript passed 800 MB): the prompt and the Stop read
    only the turn, and the Stop with a real run stays under a bound. Mutant: a scan of the whole file (the bytes and the
    time grow with it)."""
    filler = json.dumps({"type": "user", "uuid": "f", "message": {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": "t", "content": "y" * 4000}]}}, separators=(",", ":")) + "\n"
    with open(w.tx, "w") as fh:
        fh.write(filler * (40 * 1024 * 1024 // len(filler)))
    t0 = time.monotonic()
    n = w.prompt()
    w.text("REQ %s r1 premise files=a.txt" % n)
    r = w.stop()
    took = time.monotonic() - t0
    assert r.returncode == 2 and receipts(r, n)["r1"][0].startswith("ran")
    recs = w.hooklog()
    assert [x["event"] for x in recs] == ["prompt", "stop"] and recs[0]["bytes"] == 0 and recs[1]["bytes"] < 2000
    assert took < 10, took


def test_the_transcript_catch_up_wait_and_the_last_assistant_message_fallback(w):
    """The harness writes the transcript asynchronously: when last_assistant_message holds a request the transcript
    does not show, the hook waits (bounded) and then answers from that text, the row with no record uuid; when the
    record appears later, it is the same request, not a duplicate. Mutants: no fallback (a silent drop); the later
    record answered again as a duplicate."""
    n = w.prompt()
    last = "REQ %s r1 premise files=a.txt" % n
    r = w.stop(lam=last, args=("--catchup", "0.3"))
    assert r.returncode == 2 and receipts(r, n)["r1"][0].startswith("ran")
    assert "the last_assistant_message fallback" in r.stderr.decode()
    [row] = w.ledger()
    assert (row["uuid"], row["source"]) == (None, "last_assistant_message")
    w.text(last)                                   # the record reaches the transcript after the Stop
    w.summary(blocking=True)
    r = w.stop(active=True)
    assert (r.returncode, r.stderr) == (0, b"") and len(w.ledger()) == 1 and len(w.runs()) == 1
