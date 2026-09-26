"""S1-RATE (task #295, D-092 item 3): the stamp scripts/hook_context.py puts on every text it hands the model, its
telemetry line, and scripts/s1_scores.py, which pairs each stamp in the transcripts with the agent's score of it.

The oracle stays independent of the code: this file imports neither script. It runs the wrapper as the harness does (a
subprocess with a fake hook command and a fixture payload on stdin) and the extractor as a CLI over fixture transcripts,
and it writes every expected line as a literal: the stamp line's shape, the request line, the score lines. The fixture
records copy the SHAPE of real ones (the keys and value types of hook_additional_context, hook_success, a blocked call's
tool_result and assistant text records, read from this session's transcripts on 2026-09-25) with fake content. State
never touches the real .jev/: AF_S1_RATE_STATE points the wrapper at a tmp dir, and --jev the extractor.

Each test names its red: on the PIN (425cc61, "skills: four held lessons baked") the wrapper stamps nothing and the
extractor does not exist; the other controls are named mutants, run by the lane's mutation harness (S1-RATE report).
"""
import hashlib
import json
import os
import re
import secrets
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
WRAP = ROOT / "scripts" / "hook_context.py"
SCORES = ROOT / "scripts" / "s1_scores.py"
STAMP = re.compile(r"\[S1 (s1-[0-9a-f]{8}) ([A-Za-z0-9_.-]+)\]")
REQUEST = ('Begin your next text with "S1-RATE {id} rel=R use=U" (+ a note <=120 chars: why, if a 0), one line per '
           'unscored injection. rel 0 unrelated,1 same area not this step,2 relevant to this step,3 governs it; '
           'use 0 noise/known,1 confirms,2 used it,3 changed what I did')
PIN_FORM = b'{"hookSpecificOutput": {"hookEventName": "%s", "additionalContext": "line one\\nline two"}}\n'
TWO_LINES = ["printf", "line one\nline two\n"]
BLOCK = ["sh", "-c", "echo out; echo blocked >&2; exit 2"]
SESSION = "5e55f1a7-0000-4000-8000-00000000fa11"


def wrap(event, cmd, state, payload=None):
    data = payload if isinstance(payload, bytes) else json.dumps(payload or {}).encode()
    env = dict(os.environ, AF_S1_RATE_STATE=str(state))
    return subprocess.run([sys.executable, str(WRAP), event, "--", *cmd], input=data, capture_output=True, timeout=60,
                          env=env)


def unstamp(text, source):
    """(id, the lines between the stamp line and the request line) of a stamped text, each line checked."""
    first, _, rest = text.partition("\n")
    m = STAMP.fullmatch(first)
    assert m and m.group(2) == source, first[:80]
    body, _, last = rest.rpartition("\n")
    assert last == REQUEST.format(id=m.group(1)), last[:80]
    return m.group(1), body


def context(r):
    assert r.returncode == 0 and r.stderr == b"", (r.returncode, r.stderr[:200])
    obj = json.loads(r.stdout)
    assert list(obj) == ["hookSpecificOutput"] and list(obj["hookSpecificOutput"]) == ["hookEventName",
                                                                                     "additionalContext"]
    return obj["hookSpecificOutput"]["additionalContext"]


def telemetry(state):
    p = Path(state) / "injections.jsonl"
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines()] if p.exists() else []


# ---- the stamp

@pytest.mark.parametrize("event", ["PreToolUse", "PostToolUse", "UserPromptSubmit"])
def test_the_stamp_on_each_event(event, tmp_path):
    """The hook's text reaches the model between the stamp line and the request line, byte for byte, with a fresh id
    per call. Red on the PIN: the context is the bare text."""
    ids = []
    for _ in range(2):
        r = wrap(event, TWO_LINES, tmp_path)
        assert json.loads(r.stdout)["hookSpecificOutput"]["hookEventName"] == event
        sid, body = unstamp(context(r), "printf")
        assert body == "line one\nline two"
        ids.append(sid)
    assert ids[0] != ids[1]


def test_the_source_is_the_wrapped_hooks_file_stem(tmp_path):
    hook = tmp_path / "fixture-hook.py"
    hook.write_text("print('a line\\n\\nafter a blank line')\n")
    sid, body = unstamp(context(wrap("PreToolUse", [sys.executable, str(hook)], tmp_path)), "fixture-hook")
    assert body == "a line\n\nafter a blank line"


@pytest.mark.parametrize("event", ["PreToolUse", "PostToolUse"])
def test_a_blocking_stderr_is_stamped_and_keeps_its_exit_code_and_stdout(event, tmp_path):
    """Exit 2 on a tool event blocks, and the model reads the stderr: it is stamped, the exit code and stdout stay. A
    stderr with no newline at its end gets one before the request line. Red on the PIN: the stderr is bare."""
    for script, want_body in (("echo out; echo blocked >&2; exit 2", "blocked"),
                              ("echo out; printf 'two\\nlines' >&2; exit 2", "two\nlines")):
        r = wrap(event, ["sh", "-c", script], tmp_path)
        assert (r.returncode, r.stdout) == (2, b"out\n")
        err = r.stderr.decode()
        sid = STAMP.fullmatch(err.split("\n", 1)[0]).group(1) if STAMP.fullmatch(err.split("\n", 1)[0]) else None
        assert sid and err == f"[S1 {sid} sh]\n{want_body}\n{REQUEST.format(id=sid)}\n", err[:120]


def test_other_exits_pass_through_unchanged(tmp_path):
    """Any other non-zero exit, a prompt's exit 2 (the harness shows it to the person only) and an exit 2 with nothing
    on stderr pass through byte for byte, and log nothing. Red on the named mutants stamp-every-nonzero-exit and
    stamp-a-prompt-block."""
    cases = [("PreToolUse", "echo o; echo e >&2; exit 1", 1, b"o\n", b"e\n"),
             ("PostToolUse", "echo o; echo e >&2; exit 3", 3, b"o\n", b"e\n"),
             ("UserPromptSubmit", "echo blocked >&2; exit 2", 2, b"", b"blocked\n"),
             ("PreToolUse", "echo o; exit 2", 2, b"o\n", b""),
             ("PreToolUse", "printf '  \\n' >&2; exit 2", 2, b"", b"  \n")]
    for event, script, rc, out, err in cases:
        r = wrap(event, ["sh", "-c", script], tmp_path)
        assert (r.returncode, r.stdout, r.stderr) == (rc, out, err), (event, script)
    assert telemetry(tmp_path) == []


def test_the_off_switch_gives_the_pins_bytes(tmp_path):
    """With <state>/s1-rate-off (a file, or a dangling link) the output is the PIN's, byte for byte, and nothing is
    logged; without it the stamp is back. Red on the named mutant no-off-switch."""
    off = tmp_path / "s1-rate-off"
    off.touch()
    assert wrap("PostToolUse", TWO_LINES, tmp_path).stdout == PIN_FORM % b"PostToolUse"
    r = wrap("PreToolUse", BLOCK, tmp_path)
    assert (r.returncode, r.stdout, r.stderr) == (2, b"out\n", b"blocked\n")
    off.unlink()
    off.symlink_to(tmp_path / "nowhere")
    assert wrap("UserPromptSubmit", TWO_LINES, tmp_path).stdout == PIN_FORM % b"UserPromptSubmit"
    assert telemetry(tmp_path) == []
    off.unlink()
    unstamp(context(wrap("PostToolUse", TWO_LINES, tmp_path)), "printf")        # the control: on again


def test_a_stamping_failure_hands_over_the_unstamped_context(tmp_path):
    """A payload the telemetry cannot read (JSON nested past Python's recursion limit) fails the stamp: the model gets
    the PIN's form, exit 0, and the failure's type is logged. Red on the named mutant no-fallback."""
    deep = b"[" * 100000 + b"]" * 100000
    r = wrap("PreToolUse", TWO_LINES, tmp_path, payload=deep)
    assert (r.returncode, r.stdout) == (0, PIN_FORM % b"PreToolUse")
    (rec,) = telemetry(tmp_path)
    assert set(rec) == {"t", "event", "error"} and (rec["event"], rec["error"]) == ("PreToolUse", "RecursionError")
    r = wrap("PreToolUse", ["sh", "-c", "echo blocked >&2; exit 2"], tmp_path, payload=deep)
    assert (r.returncode, r.stdout, r.stderr) == (2, b"", b"blocked\n")


def test_a_text_the_stamp_would_push_over_the_harness_limit_goes_unstamped(tmp_path):
    """The harness swaps a hook text over 10,000 characters for a 2 KB preview of its head (AF-AP-183), which would
    drop the hook's own text: a stamped text over 9,500 UTF-16 units goes out unstamped, and a `too-long` line is
    logged. The count is UTF-16 units, as the harness counts: 4,650 characters outside the BMP are 9,300 units. Red on
    the named mutants no-size-cap and count-code-points."""
    py = [sys.executable, "-c"]
    sid, body = unstamp(context(wrap("PostToolUse", py + ["print('x' * 9000)"], tmp_path)), Path(sys.executable).name)
    assert body == "x" * 9000                                                   # 9,000 and the stamp: under the cap
    assert context(wrap("PostToolUse", py + ["print('x' * 9300)"], tmp_path)) == "x" * 9300
    emoji = "\U0001F600" * 4650
    assert context(wrap("PostToolUse", py + ["print('\\U0001F600' * 4650)"], tmp_path)) == emoji
    recs = telemetry(tmp_path)
    assert [r.get("skipped") for r in recs] == [None, "too-long", "too-long"] and "id" in recs[0]


def test_the_telemetry_line(tmp_path):
    """One line per stamp: the time, id, source, event, tool, the payload's tool_use_id, session, agent (or main),
    exit code, and the bytes and sha256 of the stamped text as the model receives it; never the text (a canary in the
    hook's output and in the payload stays out). Red on the PIN: no injections.jsonl."""
    canary = "cnry" + secrets.token_hex(8)
    payload = {"session_id": "sess-s1rate-1", "agent_id": "agent-s1rate", "tool_name": "Bash",
               "tool_use_id": "toolu_s1rate_1", "hook_event_name": "PreToolUse", "tool_input": {"command": canary}}
    ctx = context(wrap("PreToolUse", ["printf", f"{canary}\n"], tmp_path, payload=payload))
    sid, body = unstamp(ctx, "printf")
    (rec,) = telemetry(tmp_path)
    assert set(rec) == {"t", "id", "source", "event", "tool", "tool_use_id", "session", "agent", "exit", "bytes", "sha256"}
    assert ((rec["id"], rec["source"], rec["event"], rec["tool"], rec["tool_use_id"], rec["session"], rec["agent"],
             rec["exit"]) == (sid, "printf", "PreToolUse", "Bash", "toolu_s1rate_1", "sess-s1rate-1", "agent-s1rate", 0))
    assert rec["bytes"] == len(ctx.encode()) and rec["sha256"] == hashlib.sha256(ctx.encode()).hexdigest()
    assert re.fullmatch(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", rec["t"])
    log = tmp_path / "injections.jsonl"
    assert canary[4:].encode() not in log.read_bytes() and (log.stat().st_mode & 0o777) == 0o600
    context(wrap("UserPromptSubmit", TWO_LINES, tmp_path, payload={"session_id": "sess-s1rate-1", "prompt": canary}))
    r = wrap("PreToolUse", ["sh", "-c", "echo blocked >&2; exit 2"], tmp_path, payload=payload)
    ups, blk = telemetry(tmp_path)[1:]
    assert (ups["event"], ups["tool"], ups["tool_use_id"], ups["agent"]) == ("UserPromptSubmit", None, None, "main")
    assert blk["exit"] == 2 and blk["bytes"] == len(r.stderr) and blk["sha256"] == hashlib.sha256(r.stderr).hexdigest()
    assert canary[4:].encode() not in log.read_bytes()


# ---- the extractor, over fixture transcripts

class Transcript:
    """Records with the SHAPE of real ones (their keys and value types), fake content, written one compact JSON line
    each, as the harness writes them. `agent` makes every record a subagent's (isSidechain, agentId)."""

    def __init__(self, path, agent=None):
        self.path, self.agent, self.recs = Path(path), agent, []

    def _rec(self, kind, agent=None):
        n = len(self.recs) + 1
        agent = agent or self.agent
        r = {"parentUuid": f"fx-{n - 1:04d}", "isSidechain": agent is not None, "userType": "external",
             "cwd": "/home/user", "sessionId": SESSION, "version": "2.1.280", "gitBranch": "HEAD", "slug": "fixture-slug",
             "type": kind, "uuid": f"fx-{n:04d}", "timestamp": f"2026-09-25T20:{n // 60:02d}:{n % 60:02d}.000Z",
             "entrypoint": "cli"}
        if agent:
            r["agentId"] = agent
        self.recs.append(r)
        return r

    def context(self, text, event="PreToolUse", tool="Bash", tuid="toolu_fx", agent=None):
        name = f"{event}:{tool}" if tool else event
        r = self._rec("attachment", agent)
        r["attachment"] = {"type": "hook_additional_context", "content": [text], "hookName": name, "toolUseID": tuid,
                           "hookEvent": event}
        r["rendered"] = [{"content": f"<system-reminder>\n{name} hook additional context: {text}\n</system-reminder>"}]

    def success(self, event, command, stdout, content=""):
        r = self._rec("attachment")
        r["attachment"] = {"type": "hook_success", "hookName": event, "toolUseID": "toolu_fx", "hookEvent": event,
                           "content": content, "stdout": stdout, "stderr": "", "exitCode": 0, "command": command,
                           "durationMs": 12}
        if content:
            r["rendered"] = [{"content": f"<system-reminder>\n{event} hook success: {content}\n</system-reminder>"}]

    def blocked(self, stderr, tool="Grep", tuid="toolu_fx",
                command="python3 /repo/scripts/hook_context.py PreToolUse -- python3 /repo/.claude/hooks/x-intercept.py"):
        body = f"PreToolUse:{tool} hook error: [{command}]: {stderr}"
        r = self._rec("user")
        r["message"] = {"role": "user", "content": [{"type": "tool_result", "content": body, "is_error": True,
                                                     "tool_use_id": tuid}]}
        r.update(toolUseResult="Error: " + body, toolDenialKind="hook", promptId="prompt-fx",
                 sourceToolAssistantUUID="fx-0000")

    def post_block(self, stderr, tool="Edit",
                   command="python3 /repo/scripts/hook_context.py PostToolUse -- python3 /repo/.claude/hooks/y-check.py"):
        """A PostToolUse exit 2: the record kind and fields as the Claude Code 2.1.280 binary builds them (this session's
        transcripts hold no sample)."""
        r = self._rec("attachment")
        r["attachment"] = {"type": "hook_blocking_error", "hookName": f"PostToolUse:{tool}", "toolUseID": "toolu_fx",
                           "hookEvent": "PostToolUse",
                           "blockingError": {"blockingError": f"[{command}]: {stderr}", "command": command}}

    def prompt(self, text):
        self._rec("user")["message"] = {"role": "user", "content": text}

    def text(self, text, synthetic=False, agent=None):
        r = self._rec("assistant", agent)
        r["message"] = {"model": "<synthetic>" if synthetic else "claude-opus-5-5", "id": f"msg_fx{len(self.recs)}",
                        "type": "message", "role": "assistant", "content": [{"type": "text", "text": text}],
                        "stop_reason": None, "stop_sequence": None, "usage": {"input_tokens": 1, "output_tokens": 1}}
        r["requestId"] = f"req_fx{len(self.recs)}"
        if synthetic:
            r["isApiErrorMessage"] = True

    def write(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text("".join(json.dumps(r, separators=(",", ":")) + "\n" for r in self.recs), encoding="utf-8")


def stamped(sid, source, body):
    return f"[S1 {sid} {source}]\n{body}\n{REQUEST.format(id=sid)}"


def extract(path, jev, out):
    r = subprocess.run([sys.executable, str(SCORES), "--jev", str(jev), "--out", str(out), str(path)],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr[-2000:]
    return [json.loads(x) for x in Path(out).read_text(encoding="utf-8").splitlines()], r.stdout


def sha16(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


BLOCK1 = ("[system1 · commit] skill env-tool-quirks, the governing lines verbatim:\nfake governing line {canary}\n"
          "full details: .claude/skills/env-tool-quirks/SKILL.md § Shell quirks")
BLOCK2 = ("[system1 · commit-increment] skill build-loop, the governing lines verbatim:\nfake line two\n…\n"
          "fake line three\nfull details: .claude/skills/build-loop/SKILL.md § The operative core")


def fixture_session(tmp_path, canary, secret):
    """A session: the main transcript (with one older-layout subagent, b2, inside it) and one subagents/ file (a1)."""
    main = Transcript(tmp_path / "proj" / f"{SESSION}.jsonl")
    blocks = BLOCK1.format(canary=canary) + "\n" + BLOCK2
    main.prompt(f"a person's prompt {canary}")
    main.context(stamped("s1-0000000a", "system1-context", blocks))
    main.text("S1-RATE s1-0000000a rel=3 use=2\nOn to the next step.")                    # scored
    main.context(stamped("s1-0000000b", "edit-snapshot", "EDIT SNAPSHOT · fixture.py"), "PostToolUse", "Read")
    main.context(stamped("s1-0000000c", "system1-context", "[system1 · prompt] skill k, the section:\nfake\n"
                         "full details: .claude/skills/k/SKILL.md § H"), "UserPromptSubmit", None)
    main.text(f"S1-RATE s1-0000000b rel=1 use=0 stale: {secret}\n\nDone.")                   # b scored; c waits
    main.context(stamped("s1-0000000d", "edit-snapshot", "EDIT SNAPSHOT · other.py"), "PostToolUse", "Edit")
    main.text("S1-RATE s1-0000000c rel=2 use=2\nMore.")                                       # c late; d waits
    main.text("Nothing to rate here.")                                                        # d: missing at the end
    for sid in ("s1-0000000e", "s1-0000000f", "s1-00000010"):
        main.context(stamped(sid, "search-intercept", "fake answer"))
    main.text("S1-RATE s1-000000e rel=2 use=1\nS1-RATE s1-0000000f rel=4 use=1\nS1-RATE s1-00000010 use=1 rel=2\nText.")
    main.context(stamped("s1-00000011", "system1-context", "fake"))
    main.text("I read it first.\nS1-RATE s1-00000011 rel=2 use=1")                            # below other text
    main.context(stamped("s1-000000cc", "system1-context", "fake"), agent="b2")               # the older layout
    main.text("S1-RATE s1-0000abcd rel=1 use=1\nS1-RATE s1-0000000a rel=0 use=0\nS1-RATE s1-000000aa rel=2 use=2\n"
              "S1-RATE s1-000000cc rel=1 use=1")                             # unknown, duplicate, a1's and b2's ids
    main.text("S1-RATE s1-000000cc rel=3 use=3", agent="b2")                                  # b2 scores its own
    main.blocked(stamped("s1-00000012", "x-intercept", "QUIRK GUARD fixture answer") + "\n")
    main.text("S1-RATE s1-00000012 rel=2 use=3")                                              # a blocked call's
    main.post_block(stamped("s1-00000016", "y-check", "a post-edit check failed") + "\n")
    main.text("S1-RATE s1-00000016 rel=2 use=2")                                              # a PostToolUse block's
    main.success("UserPromptSubmit", "python3 /repo/.claude/hooks/wiki-context.py", f"wiki {canary}\n",
                 content=f"wiki {canary}")                                                     # unstamped plain stdout
    main.context(stamped("s1-00000013", "system1-context", "fake"))
    main.text("API Error: overloaded", synthetic=True)                                        # not a text
    main.text("S1-RATE s1-00000013 rel=1 use=1")
    main.context("[S1 s1-00000015 system1-context]\nthe head of a text the harness cut")      # no request line
    main.text("S1-RATE s1-00000015 rel=0 use=0")
    main.context(stamped("s1-00000014", "system1-context", "fake"))                          # no text after it
    main.write()
    sub = Transcript(tmp_path / "proj" / SESSION / "subagents" / "agent-a1.jsonl", agent="a1")
    sub.context(stamped("s1-000000aa", "system1-context", "fake"))
    sub.text("Working.")                                                                      # main's score: no
    sub.context(stamped("s1-000000bb", "edit-snapshot", "fake"))
    sub.text("S1-RATE s1-000000bb rel=2 use=1\nS1-RATE s1-0000000d rel=2 use=2")               # main's d: unknown here
    sub.write()
    return main.path, blocks


def test_the_extractor_pairs_every_status_and_keeps_threads_apart(tmp_path):
    """Every status on one fixture session. Red on the PIN (no extractor) and on the named mutants first-text-only,
    no-below-text, loose-range, no-duplicate, no-synthetic-skip, no-open and one-thread-per-file."""
    canary, secret = "cnry" + secrets.token_hex(8), "sk-" + secrets.token_hex(12)
    path, _ = fixture_session(tmp_path, canary, secret)
    rows, _ = extract(path, tmp_path / "no-jev", tmp_path / "rows.jsonl")
    got = {(r["agent"], r["id"], r["kind"] == "score"): (r["status"], r["why"], r["rel"], r["use"]) for r in rows}
    assert got == {
        ("main", "s1-0000000a", False): ("scored", None, 3, 2),
        ("main", "s1-0000000b", False): ("scored", None, 1, 0),
        ("main", "s1-0000000c", False): ("late", None, 2, 2),
        ("main", "s1-0000000d", False): ("missing", None, None, None),
        ("main", "s1-0000000e", False): ("malformed", "bad-id", None, None),
        ("main", "s1-0000000f", False): ("malformed", "range", None, None),
        ("main", "s1-00000010", False): ("malformed", "order", None, None),
        ("main", "s1-00000011", False): ("malformed", "below-text", None, None),
        ("main", "s1-0000abcd", True): ("unknown-id", None, 1, 1),
        ("main", "s1-0000000a", True): ("duplicate", None, 0, 0),
        ("main", "s1-000000aa", True): ("unknown-id", None, 2, 2),
        ("main", "s1-000000cc", True): ("unknown-id", None, 1, 1),
        ("b2", "s1-000000cc", False): ("scored", None, 3, 3),
        ("main", "s1-00000012", False): ("scored", None, 2, 3),
        ("main", "s1-00000016", False): ("scored", None, 2, 2),
        ("main", "s1-00000013", False): ("scored", None, 1, 1),
        ("main", "s1-00000015", False): ("scored", None, 0, 0),
        ("main", "s1-00000014", False): ("open", None, None, None),
        ("a1", "s1-000000aa", False): ("missing", None, None, None),
        ("a1", "s1-000000bb", False): ("scored", None, 2, 1),
        ("a1", "s1-0000000d", True): ("unknown-id", None, 2, 2),
    }
    by = {(r["agent"], r["id"]): r for r in rows if r["kind"] != "score"}
    a = by[("main", "s1-0000000a")]
    assert (a["source"], a["event"], a["tool"], a["kind"], a["session"], a["whole"]) == (
        "system1-context", "PreToolUse", "Bash", "hook_additional_context", SESSION, True)
    assert by[("main", "s1-0000000c")]["event"] == "UserPromptSubmit" and by[("main", "s1-0000000c")]["tool"] is None
    blk = by[("main", "s1-00000012")]
    assert (blk["kind"], blk["source"], blk["event"], blk["tool"], blk["whole"]) == (
        "tool_result", "x-intercept", "PreToolUse", "Grep", True)
    post = by[("main", "s1-00000016")]
    assert (post["kind"], post["source"], post["event"], post["tool"], post["whole"]) == (
        "hook_blocking_error", "y-check", "PostToolUse", "Edit", True)
    assert by[("main", "s1-00000015")]["whole"] is False                        # the harness's preview: no request line
    assert by[("main", "s1-0000000b")]["note"] == "stale: sk-<redacted>"


def test_the_extractor_reads_the_sections_and_joins_the_state_files(tmp_path):
    """Each injection's pointer lines give its sections, a System-1 block with the sha of its text from label to
    pointer: from the transcript alone when .jev/ is gone, and with the state files present the wrapper's tool_use_id
    and sha_ok (a wrong sha reads false) and the hook's row and key. Red on the PIN (no extractor) and on the named
    mutant block-sha-off-by-a-line."""
    canary, secret = "cnry" + secrets.token_hex(8), "sk-" + secrets.token_hex(12)
    path, blocks = fixture_session(tmp_path, canary, secret)
    b1, b2 = BLOCK1.format(canary=canary), BLOCK2
    want = [{"file": ".claude/skills/env-tool-quirks/SKILL.md", "heading": "Shell quirks", "sha": sha16(b1)},
            {"file": ".claude/skills/build-loop/SKILL.md", "heading": "The operative core", "sha": sha16(b2)}]
    rows, _ = extract(path, tmp_path / "no-jev", tmp_path / "bare.jsonl")
    a = next(r for r in rows if r["id"] == "s1-0000000a" and r["kind"] != "score")
    assert a["sections"] == want and "sha_ok" not in a and "tool_use_id" not in a
    jev = tmp_path / "jev"
    jev.mkdir()
    text_a = stamped("s1-0000000a", "system1-context", blocks)
    lines = [{"t": "2026-09-25T20:00:01Z", "id": "s1-0000000a", "source": "system1-context", "event": "PreToolUse",
              "tool": "Bash", "tool_use_id": "toolu_a", "session": SESSION, "agent": "main", "exit": 0,
              "bytes": len(text_a.encode()), "sha256": hashlib.sha256(text_a.encode()).hexdigest()},
             {"t": "2026-09-25T20:00:02Z", "id": "s1-0000000b", "source": "edit-snapshot", "event": "PostToolUse",
              "tool": "Read", "tool_use_id": "toolu_b", "session": SESSION, "agent": "main", "exit": 0, "bytes": 1,
              "sha256": "0" * 64}]
    (jev / "injections.jsonl").write_text("".join(json.dumps(x) + "\n" for x in lines))
    (jev / "system1.jsonl").write_text(json.dumps({"event": "PreToolUse", "tool_use_id": "toolu_a", "injected": [
        {"row": "commit", "key": "env-tool-quirks § Shell quirks", "lines": 1, "bytes": 9, "sha": sha16(b1)}]}) + "\n")
    rows, _ = extract(path, jev, tmp_path / "joined.jsonl")
    by = {r["id"]: r for r in rows if r["kind"] != "score" and r["agent"] == "main"}
    assert (by["s1-0000000a"]["tool_use_id"], by["s1-0000000a"]["sha_ok"]) == ("toolu_a", True)
    assert (by["s1-0000000b"]["tool_use_id"], by["s1-0000000b"]["sha_ok"]) == ("toolu_b", False)
    assert by["s1-0000000a"]["sections"] == [dict(want[0], row="commit", key="env-tool-quirks § Shell quirks"), want[1]]


def test_the_extractor_prints_ids_and_counts_only_and_scrubs_notes(tmp_path):
    """The summary holds ids and counts, never an injection's text or a prompt; a fake secret in a note never reaches the
    rows or the summary (the note goes through transcript_export.scrub). Red on the PIN (no extractor) and on the named
    mutant no-scrub."""
    canary, secret = "cnry" + secrets.token_hex(8), "sk-" + secrets.token_hex(12)
    path, _ = fixture_session(tmp_path, canary, secret)
    out = tmp_path / "rows.jsonl"
    r = subprocess.run([sys.executable, str(SCORES), "--jev", str(tmp_path / "no-jev"), "--out", str(out), str(path)],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr[-2000:]
    everything = out.read_text(encoding="utf-8") + r.stdout + r.stderr
    assert secret not in everything and secret[3:] not in everything and "sk-<redacted>" in everything
    assert canary[4:] not in everything                                         # no injection text, no prompt
    kinds = dict(re.findall(r"^  (\w+)\s+injections\s+(\d+\s+stamped\s+\d+)", r.stdout, re.M))
    assert {k: " ".join(v.split()) for k, v in kinds.items()} == {
        "hook_additional_context": "14 stamped 14", "hook_success": "1 stamped 0", "hook_blocking_error": "1 stamped 1",
        "tool_result": "1 stamped 1"}                                           # 12 main-thread contexts, 2 of a1
    assert "score rows of their own: unknown-id 4  duplicate 1  malformed 0" in r.stdout
    assert re.search(r"^  wiki-context\s+injections\s+1\s+stamped\s+0\b", r.stdout, re.M)
    r2 = subprocess.run([sys.executable, str(SCORES), "--jev", str(tmp_path / "no-jev"), "--out", "-", str(path)],
                        capture_output=True, text=True, timeout=120)
    assert r2.stdout == out.read_text(encoding="utf-8") and "score rows of their own" in r2.stderr


def test_a_real_stamp_is_found_paired_and_joined(tmp_path):
    """The wrapper's own output, recorded as the harness records it (the additionalContext in a hook_additional_context
    record; an exit-2 stderr in a blocked call's tool_result), is found, paired with its score and joined to the
    wrapper's telemetry line: the tool_use_id, and a sha256 equal to the text found. Red on the PIN: no stamp."""
    jev = tmp_path / "jev"
    payload = {"session_id": SESSION, "tool_name": "Bash", "tool_use_id": "toolu_real_1", "hook_event_name": "PreToolUse"}
    ctx = context(wrap("PreToolUse", TWO_LINES, jev, payload=payload))
    sid1, _ = unstamp(ctx, "printf")
    err = wrap("PreToolUse", ["sh", "-c", "echo 'QUIRK GUARD fixture' >&2; exit 2"], jev,
               payload=dict(payload, tool_use_id="toolu_real_2")).stderr.decode()
    sid2, _ = unstamp(err[:-1], "sh")
    t = Transcript(tmp_path / "proj" / f"{SESSION}.jsonl")
    t.context(ctx, tuid="toolu_real_1")
    t.blocked(err, tool="Bash", tuid="toolu_real_2")
    t.text(f"S1-RATE {sid1} rel=2 use=1\nS1-RATE {sid2} rel=3 use=3 the quirk guard was right")
    t.write()
    rows, _ = extract(t.path, jev, tmp_path / "rows.jsonl")
    by = {r["id"]: r for r in rows}
    assert set(by) == {sid1, sid2}
    assert [(by[s]["status"], by[s]["kind"], by[s]["source"], by[s]["tool_use_id"], by[s]["sha_ok"], by[s]["whole"])
            for s in (sid1, sid2)] == [("scored", "hook_additional_context", "printf", "toolu_real_1", True, True),
                                       ("scored", "tool_result", "sh", "toolu_real_2", True, True)]
    assert by[sid2]["note"] == "the quirk guard was right"
