"""scripts/s1_train/render.py and scripts/s1_train/view.py (task #444; brief tasks/briefs/jev-laya/S3-5-VIEW-brief.md).

render.py is the ONE render of an exported event stream (D-1); view.py maps each source id of a frozen S1 build to where
its injection sits in its transcript's stream, the state before it, the injected text, and the build's label and split
(D-2 to D-7). Fixtures go through the real producers: a session tree (a main transcript and one lane transcript, in the
record shapes of tests/test_session_export.py's builders; each hook as the harness writes it, each stamp by
hook_context.stamp) exported by scripts/session_export.py's CLI (an init-key FAKE key, a fixture repo, --known-values
key-only), and a frozen build written by build_s1.write_split over constructed rows. The expected render and the expected
view rows are written out here, never computed by the code under test. The FAKE key is a canary of
session_export.CANARIES, assembled at run time; no assertion prints it (a printed canary would reach this session's
transcript, which the next real export's gate counts)."""
import collections
import hashlib
import importlib.util
import json
import lzma
import os
import pathlib
import shutil
import subprocess
import sys
import types

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
VIEW = SCRIPTS / "s1_train" / "view.py"
EXPORTER = SCRIPTS / "session_export.py"
sys.path.insert(0, str(SCRIPTS))
from s1_train import render as R  # noqa: E402
from s1_train import view as V  # noqa: E402
from laya_ft import build_s1 as B  # noqa: E402
from laya_ft import common as C  # noqa: E402
import hook_context as HC  # noqa: E402
from transcript_export import scrub_payload  # noqa: E402

# The modules under test are this tree's: a mutant run in a scratch copy tests the copy (anti-hollow-green 3b).
assert pathlib.Path(R.__file__).resolve() == SCRIPTS / "s1_train" / "render.py", R.__file__
assert pathlib.Path(V.__file__).resolve() == VIEW, V.__file__

SID = "0e0e0e0e-fake-4b4b-8c8c-00000000d0d0"
MAIN = "-home-user/%s.jsonl" % SID                                  # a session transcript: owner and coordinator
LANE = "-home-user/%s/subagents/agent-azqview01.jsonl" % SID         # a lane: coordinator and agent
FAKE_COMMIT = "5be8cc0c" * 5
COMMITTED = "test_zq_view_committed_name_that_runs_past_forty_chars"  # the fixture repo holds it, so the export keeps it
REQ = ('Begin your next text with "S1-RATE %s rel=R use=U" (+ a note <=120 chars: why, if a 0), one line per '
       'unscored injection. rel 0 unrelated,1 same area not this step,2 relevant to this step,3 governs it; '
       'use 0 noise/known,1 confirms,2 used it,3 changed what I did')        # hook_context's request line, written out
HOOKS = "/home/user/agent-factory/.claude/hooks/"
WRAP = "python3 /home/user/agent-factory/scripts/hook_context.py %s -- python3 " + HOOKS + "%s.py"
DENY_PREFIX = "PreToolUse:Grep hook error: [%s]: " % (WRAP % ("PreToolUse", "search-intercept"))
S1_SCORES = "/home/user/agent-factory/scripts/s1_scores.py"
RENDER_PY = "/home/user/agent-factory/scripts/s1_train/render.py"
ID_UPS, ID_PRE, ID_POST, ID_DENY, ID_PAR1, ID_PAR2 = ("s1-0000a00%d" % i for i in range(1, 7))
ID_TWO1, ID_TWO2, ID_LONG = "s1-0000b001", "s1-0000b002", "s1-0000b003"
ID_ABSENT, ID_UNSCORED = "s1-0000c001", "s1-0000d001"           # in the build only; in the stream only
PACK = "filepack scripts/s1_scores.py: ledger 5"
LONG_PACK = "\n".join("skill line %02d: render each event the same way" % i for i in range(40))   # 1,839 characters
CUT_RESULT = "a " * 1500 + "b " * 750 + "c " * 500                 # 5,499 characters once stripped: the render cuts it
MARK = "zq-thinking-marker-" + hashlib.sha256(b"s3-5-view thinking marker").hexdigest()[:12]
TXT = {ID_UPS: "the wiki excerpt for this prompt", ID_PRE: "filepack scripts: ledger 1, briefs 2",
       ID_POST: "READ CONTEXT: scripts, last change 610cb12", ID_DENY: "graft answer: scripts/s1_train/render.py:1 render",
       ID_PAR1: PACK, ID_PAR2: PACK, ID_TWO1: "EDIT SNAPSHOT · render.py\n  impact  module-level edit",
       ID_TWO2: "[system1 · code-edit] skill build-loop", ID_LONG: LONG_PACK}
SOURCE = {ID_UPS: "wiki-context", ID_PRE: "filepacks", ID_POST: "edit-snapshot", ID_DENY: "search-intercept",
          ID_PAR1: "filepacks", ID_PAR2: "filepacks", ID_TWO1: "edit-snapshot", ID_TWO2: "system1-context",
          ID_LONG: "system1-context", ID_ABSENT: "filepacks"}
# the build's rows: (split, answer, source ids); one row holds two ids (identical states merged)
ROWS = (("train", "true", (ID_UPS,)), ("train", "false", (ID_PRE,)), ("train", "true", (ID_POST,)),
        ("train", "true", (ID_PAR1, ID_PAR2)), ("train", "true", (ID_TWO1,)), ("train", "false", (ID_ABSENT,)),
        ("heldout", "true", (ID_DENY,)), ("heldout", "false", (ID_TWO2,)), ("heldout", "true", (ID_LONG,)))
TIME = {ID_POST: "2026-10-01T12:59:59.000Z", ID_ABSENT: "2026-10-01T12:30:00.000Z"}   # else the carrier record's
# id: (src, carrier, hook event, call id, step_event, state_event): seqs of the records written below
EXPECTED = {ID_UPS: (MAIN, "hook_additional_context", "UserPromptSubmit", "zq-ups-01", None, 2),
            ID_PRE: (MAIN, "hook_additional_context", "PreToolUse", "toolu_zqv_01", 6, 7),
            ID_POST: (MAIN, "hook_additional_context", "PostToolUse", "toolu_zqv_01", 6, 11),
            ID_DENY: (MAIN, "tool_result", "PreToolUse", "toolu_zqv_02", 14, 15),
            ID_PAR1: (MAIN, "hook_additional_context", "PreToolUse", "toolu_zqv_03", 18, 20),
            ID_PAR2: (MAIN, "hook_additional_context", "PreToolUse", "toolu_zqv_04", 19, 20),
            ID_TWO1: (LANE, "hook_additional_context", "PostToolUse", "toolu_zqv_11", 3, 5),
            ID_TWO2: (LANE, "hook_additional_context", "PostToolUse", "toolu_zqv_11", 3, 5),
            ID_LONG: (LANE, "hook_additional_context", "PreToolUse", "toolu_zqv_12", 10, 11)}
ROW_KEYS = ["id", "item_id", "split", "label", "source", "time", "src", "carrier", "hook_event", "call_id", "step_event",
            "state_event", "state_end", "candidate", "candidate_sha256"]
GIT = ["git", "-c", "user.name=zq", "-c", "user.email=zq@example.invalid", "-c", "commit.gpgsign=false",
       "-c", "core.hooksPath=/dev/null", "-c", "init.defaultBranch=main"]
Inj = collections.namedtuple("Inj", "stamped line ts")


# ---------------------------------------------------------------- the session tree

class Tape:
    """One JSONL transcript in the harness's record shapes (tests/test_session_export.py's Tape); add() returns the
    record's 1-based line."""

    def __init__(self, agent=None):
        self.lines, self.agent = [], agent

    @staticmethod
    def ts(line):
        return "2026-10-01T12:%02d:%02d.000Z" % divmod(line, 60)

    def _base(self, kind):
        n = len(self.lines) + 1
        r = {"parentUuid": None, "isSidechain": self.agent is not None, "userType": "external",
             "cwd": "/home/user/agent-factory", "sessionId": SID, "version": "2.1.0", "gitBranch": "fake", "type": kind,
             "uuid": "u-%05d" % n, "timestamp": self.ts(n)}
        if self.agent:
            r["agentId"] = self.agent
        return r

    def add(self, rec):
        self.lines.append(json.dumps(rec, separators=(",", ":")))
        return len(self.lines)

    def user(self, content, **extra):
        r = self._base("user")
        r["message"] = {"role": "user", "content": content}
        r.update(extra)
        return self.add(r)

    def owner(self, content):
        return self.user(content, origin={"kind": "human"}, promptSource="sdk")

    def assistant(self, blocks, stop="tool_use"):
        r = self._base("assistant")
        r["message"] = {"model": "claude-fake", "id": "msg_fake%05d" % len(self.lines), "type": "message",
                        "role": "assistant", "content": blocks, "stop_reason": stop,
                        "usage": {"input_tokens": 1, "output_tokens": 1}}
        return self.add(r)

    def text(self, text):
        return self.assistant([{"type": "text", "text": text}], stop="end_turn")

    def thinking(self, text):
        return self.assistant([{"type": "thinking", "thinking": text, "signature": "x"}])

    def call(self, cid, name, inp):
        return self.assistant([{"type": "tool_use", "id": cid, "name": name, "input": inp}])

    def result(self, cid, content, is_error=False):
        return self.user([{"tool_use_id": cid, "type": "tool_result", "content": content, "is_error": is_error}],
                         sourceToolAssistantUUID="u-fake")

    def attachment(self, att):
        r = self._base("attachment")
        r["attachment"] = att
        return self.add(r)

    def system(self, subtype, **fields):
        r = self._base("system")
        r["subtype"] = subtype
        r.update(fields)
        return self.add(r)

    def write(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(self.lines) + "\n")


def success(event, tool, cid, command, stdout, content=""):
    """A hook_success attachment with the real key set."""
    return {"type": "hook_success", "hookName": "%s:%s" % (event, tool) if tool else event, "hookEvent": event,
            "toolUseID": cid, "command": command, "content": content, "stdout": stdout, "stderr": "", "exitCode": 0,
            "durationMs": 7}


def hook_block(sid, source, text):
    """The expected block of a stamped injection, written out from the stamp format (never from hook_context)."""
    return "Hook: [S1 %s %s]\n%s\n%s\n\n" % (sid, source, text, REQ % sid)


class Session:
    """A transcript under construction and its expected render: one expected block per record (each record here becomes
    exactly one exported event, so an event's seq is its record's line minus 1) and its stamped injections."""

    def __init__(self, agent=None):
        self.tape, self.exp, self.inj = Tape(agent), [], {}

    def put(self, line, block):
        assert line == len(self.exp) + 1, (line, len(self.exp))
        self.exp.append(block)
        return line

    def stamped(self, event, tool, cid, text, source, sid, wrapped=True):
        """An S1 injection as the harness writes a hook_context-wrapped hook's: (wrapped) a hook_success holding the
        JSON stdout, its content empty, then the hook_additional_context holding the stamped text."""
        stamped = HC.stamp(text, source, sid)
        if wrapped:
            stdout = json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": stamped}}) + "\n"
            self.put(self.tape.attachment(success(event, tool, cid, WRAP % (event, source), stdout)), "")
        line = self.put(self.tape.attachment({"type": "hook_additional_context", "content": [stamped],
                                              "hookEvent": event, "hookName": "%s:%s" % (event, tool) if tool else event,
                                              "toolUseID": cid}), hook_block(sid, source, text))
        self.inj[sid] = Inj(stamped, line, self.tape.ts(line))


def build_main():
    s = Session()
    t = s.tape
    orient = "ORIENT: task #444 is next\nthe ledger is current\n"
    s.put(t.attachment(success("SessionStart", "startup", "zq-ss-01", "bash scripts/orient.sh", orient, orient)),
          "Hook: ORIENT: task #444 is next\nthe ledger is current\n\n")                                    # seq 0
    s.put(t.owner("Build the S3-5 view, please."), "Owner: Build the S3-5 view, please.\n\n")              # 1
    wiki = "wiki: live-state is fresh\n"
    s.put(t.attachment(success("UserPromptSubmit", None, "zq-ups-01", "python3 " + HOOKS + "wiki-hint.py", wiki,
                               wiki)), "Hook: wiki: live-state is fresh\n\n")                              # 2
    s.stamped("UserPromptSubmit", None, "zq-ups-01", TXT[ID_UPS], "wiki-context", ID_UPS, wrapped=False)  # 3
    s.put(t.thinking("the marker is " + MARK), "")                                                         # 4
    s.put(t.text("Evidence: %s passed." % COMMITTED), "Coordinator: Evidence: <opaque-redacted> passed.\n\n")  # 5
    s.put(t.call("toolu_zqv_01", "Bash", {"command": "ls scripts", "description": "list the scripts"}),
          'Coordinator calls Bash: {"command":"ls scripts","description":"list the scripts"}\n\n')        # 6
    nag = "graft first: ask graft before grep\n"          # a PreToolUse hook's plain stdout: the model never reads it
    s.put(t.attachment(success("PreToolUse", "Bash", "toolu_zqv_01", "python3 " + HOOKS + "graft-first-nag.py", nag,
                               nag)), "")                                                                  # 7
    s.stamped("PreToolUse", "Bash", "toolu_zqv_01", TXT[ID_PRE], "filepacks", ID_PRE)                      # 8, 9
    s.put(t.result("toolu_zqv_01", "README.md\nscripts\ntests\n"), "Result of Bash: README.md\nscripts\ntests\n\n")  # 10
    s.stamped("PostToolUse", "Bash", "toolu_zqv_01", TXT[ID_POST], "edit-snapshot", ID_POST)               # 11, 12
    s.put(t.user("<task-notification>\n<task-id>bzq9</task-id>\n<status>completed</status>\n</task-notification>",
                 origin={"kind": "task-notification"}), "")                                                # 13
    s.put(t.call("toolu_zqv_02", "Grep", {"pattern": "def render", "path": "scripts"}),
          'Coordinator calls Grep: {"path":"scripts","pattern":"def render"}\n\n')                         # 14
    stamped = HC.stamp(TXT[ID_DENY], "search-intercept", ID_DENY) + "\n"   # an exit-2 stderr: hook_context adds a LF
    line = s.put(t.result("toolu_zqv_02", DENY_PREFIX + stamped, is_error=True),
                 "Result of Grep: %s[S1 %s search-intercept]\n%s\n%s\n\n" % (DENY_PREFIX, ID_DENY, TXT[ID_DENY],
                                                                             REQ % ID_DENY))               # 15
    s.inj[ID_DENY] = Inj(stamped, line, t.ts(line))
    s.put(t.user("Summary of the session so far: the view is half built.", isCompactSummary=True,
                 isVisibleInTranscriptOnly=True), "Summary: Summary of the session so far: the view is half built.\n\n")
    s.put(t.text("Back after the summary."), "Coordinator: Back after the summary.\n\n")                   # 17
    for cid, offset in (("toolu_zqv_03", 1), ("toolu_zqv_04", 101)):                                      # 18, 19
        s.put(t.call(cid, "Read", {"file_path": S1_SCORES, "offset": offset, "limit": 100}),
              'Coordinator calls Read: {"file_path":"%s","limit":100,"offset":%d}\n\n' % (S1_SCORES, offset))
    s.stamped("PreToolUse", "Read", "toolu_zqv_03", PACK, "filepacks", ID_PAR1)                            # 20, 21
    s.stamped("PreToolUse", "Read", "toolu_zqv_04", PACK, "filepacks", ID_PAR2)                            # 22, 23
    s.put(t.result("toolu_zqv_03", "     1\t#!/usr/bin/env python3\n"), "Result of Read: 1\t#!/usr/bin/env python3\n\n")
    s.put(t.result("toolu_zqv_04", "   101\timport re\n"), "Result of Read: 101\timport re\n\n")        # 25
    s.put(t.call("toolu_zqv_05", "Bash", {"command": "python3 dump.py"}),
          'Coordinator calls Bash: {"command":"python3 dump.py"}\n\n')                                     # 26
    s.put(t.result("toolu_zqv_05", CUT_RESULT),
          "Result of Bash: " + "a " * 1500 + "\n[... 1499 characters cut ...]\n" + " c" * 500 + "\n\n")     # 27
    s.put(t.user("Stop hook feedback:\n[~/.claude/stop-hook.sh]: push the branch", isMeta=True),
          "Hook: Stop hook feedback:\n[~/.claude/stop-hook.sh]: push the branch\n\n")                      # 28
    s.put(t.system("stop_hook_summary", hookCount=1, hookInfos=[{"command": "~/.claude/stop-hook.sh", "durationMs": 3}],
                   hookErrors=[], preventedContinuation=False, stopReason="", hasOutput=True, level="suggestion",
                   toolUseID="zq-stop-01", hookAdditionalContext=[]), "")                                  # 29
    s.put(t.text("S1-RATE %s rel=2 use=1\nS1-RATE %s rel=0 use=0\nDone." % (ID_UPS, ID_PRE)),
          "Coordinator: S1-RATE s1-0000a001 rel=2 use=1\nS1-RATE s1-0000a002 rel=0 use=0\nDone.\n\n")      # 30
    return s


def build_lane():
    s = Session(agent="azqview01")
    t = s.tape
    s.put(t.user("You are the view lane. Read the brief first."),
          "Coordinator: You are the view lane. Read the brief first.\n\n")                                 # seq 0
    s.put(t.thinking("lane thinking: the marker is " + MARK), "")                                          # 1
    s.put(t.text("Reading the brief now."), "Agent: Reading the brief now.\n\n")                           # 2
    s.put(t.call("toolu_zqv_11", "Edit", {"file_path": RENDER_PY, "old_string": "x", "new_string": "y",
                                          "replace_all": False}),
          'Agent calls Edit: {"file_path":"%s","new_string":"y","old_string":"x","replace_all":false}\n\n' % RENDER_PY)
    s.put(t.result("toolu_zqv_11", "The file has been updated successfully."),
          "Result of Edit: The file has been updated successfully.\n\n")                                   # 4
    s.stamped("PostToolUse", "Edit", "toolu_zqv_11", TXT[ID_TWO1], "edit-snapshot", ID_TWO1)               # 5, 6
    s.stamped("PostToolUse", "Edit", "toolu_zqv_11", TXT[ID_TWO2], "system1-context", ID_TWO2)             # 7, 8
    s.put(t.text("S1-RATE %s rel=2 use=2\nS1-RATE %s rel=1 use=0" % (ID_TWO1, ID_TWO2)),
          "Agent: S1-RATE s1-0000b001 rel=2 use=2\nS1-RATE s1-0000b002 rel=1 use=0\n\n")                   # 9
    s.put(t.call("toolu_zqv_12", "Bash", {"command": "bash scripts/test_summary.sh tests/test_s1_train_view.py"}),
          'Agent calls Bash: {"command":"bash scripts/test_summary.sh tests/test_s1_train_view.py"}\n\n')  # 10
    s.stamped("PreToolUse", "Bash", "toolu_zqv_12", LONG_PACK, "system1-context", ID_LONG)                 # 11, 12
    s.put(t.result("toolu_zqv_12", "pytest-summary: 1 passed"), "Result of Bash: pytest-summary: 1 passed\n\n")
    s.stamped("PostToolUse", "Bash", "toolu_zqv_12", "an injection nobody scored", "edit-snapshot", ID_UNSCORED)
    s.put(t.text("Done."), "Agent: Done.\n\n")                                                             # 16
    return s


# ---------------------------------------------------------------- the frozen build

def make_build(out, inj, rows=ROWS, source=None, extra=None):
    """A frozen S1 build through build_s1.write_split over constructed rows: a row's chunk as build_s1 cuts it from the
    stamped text (ID_TWO1's is an older text: candidate_vs_chunk `differs`), each source's time its carrier record's
    (except TIME), each source an injection (`extra`: {id: fields that replace its source's}). Returns {id: item_id}."""
    q = C.S1_QUESTIONS[B.QID]
    src_of, extra = dict(SOURCE, **(source or {})), extra or {}
    pairs, items = {"train": [], "heldout": []}, {}
    for n, (split, answer, sids) in enumerate(rows):
        first = sids[0]
        if first == ID_TWO1:
            chunk = "an older snapshot of render.py"
        elif first in inj:
            chunk = B.cap(scrub_payload(B.chunk_of(inj[first].stamped, True)), B.CAPS["chunk"], at_line=True)
        else:
            chunk = "a pack nobody saw"
        state = {"task": "Build the S3-5 view, please.", "intent": "row %d" % n, "step": "the step of %s" % first,
                 "kind": B.KINDS.get(src_of[first], src_of[first]), "chunk": chunk}
        ssha = C.state_sha(state)
        row = {"item_id": "s1-%s" % ssha[:20], "question_id": B.QID, "question_sha": C.question_sha(q),
               "state_sha": ssha, "options": C.options(q), "question": q, "state": state,
               "sources": [dict({"kind": "injection", "id": s, "source": src_of[s], "time": TIME.get(s) or inj[s].ts},
                                **extra.get(s, {})) for s in sids]}
        pairs[split].append((row, answer))
        items.update(dict.fromkeys(sids, row["item_id"]))
    base = {"version": B.VERSION, "commit": FAKE_COMMIT, "cutoff": {}, "question": {B.QID: C.question_sha(q)},
            "caps": B.CAPS, "model": {}, "code": {}}
    for split in ("train", "heldout"):
        B.write_split(out, split, pairs[split], base, "2026-10-01T13:00:00.000Z")
    (pathlib.Path(out) / "summary.json").write_text(
        json.dumps({"version": B.VERSION, "commit": FAKE_COMMIT}, indent=1, sort_keys=True) + "\n")
    return items


# ---------------------------------------------------------------- helpers

def _run(*args, timeout=600):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, timeout=timeout)


def _view(build, export, out):
    return _run(VIEW, "--build", build, "--export", export, "--out", out, timeout=300)


def _sha(path):
    return hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest()


def _canon(obj):
    """session_export.canon: how the export writes an attachment as an event's text."""
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _events(export, src):
    dec = lzma.LZMADecompressor()
    raw = dec.decompress((pathlib.Path(export) / (src + ".xz")).read_bytes())
    assert dec.eof and not dec.unused_data
    return [json.loads(line) for line in C.jsonl_lines(raw.decode("utf-8"))]


def _set_sha(export, src):
    """The manifest entry's output_sha256 for the file as it is now."""
    m = json.loads((export / "manifest.json").read_text())
    for s in m["sources"]:
        if s["src"] == src:
            s["output_sha256"] = _sha(export / s["output"])
    (export / "manifest.json").write_text(json.dumps(m, indent=1) + "\n")


def _write_events(export, src, events):
    """One export file rewritten with `events` (each line as the exporter writes it), its sha256 in the manifest."""
    data = "".join(json.dumps(e, ensure_ascii=False, separators=(",", ":")) + "\n" for e in events).encode("utf-8")
    (export / (src + ".xz")).write_bytes(lzma.compress(data, preset=6))
    _set_sha(export, src)


def _set_labels_sha(build, split):
    """The split manifest's labels.sha256 for its labels.jsonl as it is now."""
    path = build / split / "manifest.json"
    man = json.loads(path.read_text())
    man["labels"]["sha256"] = _sha(build / split / "labels.jsonl")
    path.write_text(json.dumps(man, indent=1, sort_keys=True) + "\n")


def _copy(src, tmp_path, name):
    return pathlib.Path(shutil.copytree(src, tmp_path / name))


def _outputs(out, r):
    return "".join((out / n).read_text(encoding="utf-8") for n in ("view.jsonl", "summary.json")) + r.stdout + r.stderr


def _leaks(blob, canaries):
    """Names of the canaries whose value, or any 8-character window of it, is in `blob`. Never the values."""
    return sorted(n for n, v in canaries.items() if v in blob or any(v[i:i + 8] in blob for i in range(len(v) - 7)))


def _refused(r, reason, out):
    assert r.returncode == 2, (r.returncode, r.stderr[-800:])
    assert "s1-view: refused: " + reason in r.stderr, r.stderr[-800:]
    assert r.stdout == ""
    assert not pathlib.Path(out).exists()                    # nothing written


def _ev(role, kind, text, tool=None):
    return {"role": role, "kind": kind, "text": text, "tool": tool}


@pytest.fixture(scope="module")
def se():
    spec = importlib.util.spec_from_file_location("session_export_for_s1_view", EXPORTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    """The session tree, exported by the real CLI; the frozen build; one view of the build over the export."""
    base = tmp_path_factory.mktemp("s1view")
    sessions = {MAIN: build_main(), LANE: build_lane()}
    for src, s in sessions.items():
        s.tape.write(base / "tree" / src)
    repo = base / "repo"
    repo.mkdir()
    for args in (("init", "-q"), ("add", "."), ("commit", "-q", "-m", "zq")):
        if args[0] == "add":
            (repo / "zq.md").write_text("A committed run: %s\n" % COMMITTED)
        r = subprocess.run(GIT + ["-C", str(repo), *args], capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr[-500:]
    key = base / "cfg" / "pseudonym.key"
    r = _run(EXPORTER, "init-key", "--key", key)
    assert r.returncode == 0, r.stderr[-500:]
    r = _run(EXPORTER, "export", "--root", base / "tree", "--out", base / "export", "--jobs", 1, "--key", key,
             "--repo", repo, "--known-values", "key-only")
    assert r.returncode == 0, (r.stdout[-1500:], r.stderr[-1500:])
    inj = dict(sessions[MAIN].inj, **sessions[LANE].inj)
    items = make_build(base / "build", inj)
    result = _view(base / "build", base / "export", base / "out")
    assert result.returncode == 0, result.stderr[-2000:]
    rows = [json.loads(line) for line in C.jsonl_lines((base / "out" / "view.jsonl").read_text(encoding="utf-8"))]
    summary = json.loads((base / "out" / "summary.json").read_text(encoding="utf-8"))
    return types.SimpleNamespace(base=base, export=base / "export", build=base / "build", out=base / "out",
                                 result=result, rows=rows, summary=summary, sessions=sessions, inj=inj, items=items)


# ---------------------------------------------------------------- the render (D-1)

@pytest.mark.parametrize("role,kind,tool,label", [
    ("owner", "text", None, "Owner"), ("coordinator", "text", None, "Coordinator"), ("agent", "text", None, "Agent"),
    ("coordinator", "tool_call", "Bash", "Coordinator calls Bash"), ("agent", "tool_call", "Read", "Agent calls Read"),
    ("tool", "tool_result", "Grep", "Result of Grep"), ("tool", "tool_result", None, "Result of ?"),
    ("system", "summary", None, "Summary")])
def test_each_rendered_pair_has_its_label_and_the_newline_rule(role, kind, tool, label):
    # CR LF and CR become LF, a run of LFs one LF, and the body is stripped
    assert R.block(_ev(role, kind, " a\r\nb\rc\n\n\nd \n", tool)) == label + ": a\nb\nc\nd\n\n"


@pytest.mark.parametrize("role,kind", [("coordinator", "thinking"), ("agent", "thinking"), ("system", "notification"),
                                       ("system", "harness_notice"), ("system", "api_error"), ("tool", "file_change"),
                                       ("tool", "pruner_archive")])
def test_the_silent_pairs_render_nothing(role, kind):
    assert R.block(_ev(role, kind, "a text that never renders", "Bash")) == ""


@pytest.mark.parametrize("role,kind", [("owner", "thinking"), ("agent", "notification"), ("tool", "text"),
                                       ("hook", "text"), ("system", "text"), ("owner", "hook"),
                                       ("agent", "zq_future_kind")])
def test_any_other_pair_is_refused_by_name(role, kind):
    with pytest.raises(R.UnknownPair) as e:
        R.block(_ev(role, kind, "x"))
    assert repr((role, kind)) in str(e.value)


def test_an_empty_body_renders_nothing_and_the_cap_keeps_head_and_tail():
    counts = {}
    assert R.block(_ev("owner", "text", " \r\n\n\t "), counts) == ""
    at_cap = ("w" * 9 + " ") * 399 + "w" * 10                       # 4,000 characters: not cut
    assert R.block(_ev("owner", "text", at_cap), counts) == "Owner: " + at_cap + "\n\n"
    assert counts == {}
    over = at_cap + "w"                                             # 4,001: the first 3,000, the mark, the last 1,000
    assert R.block(_ev("owner", "text", over), counts) == (
        "Owner: " + ("w" * 9 + " ") * 300 + "\n[... 1 characters cut ...]\n" + "w" * 8 + " " + ("w" * 9 + " ") * 98
        + "w" * 11 + "\n\n")
    assert counts == {"cut": 1}


def test_the_scrub_runs_on_every_body(se):
    key = {"gh-result": se.CANARIES["gh-result"]}   # a FAKE GitHub-token shape, assembled at import by session_export
    counts = {}
    out = R.block(_ev("agent", "text", "the key is " + key["gh-result"]), counts)
    leaked = _leaks(out, key)          # a plain name: pytest's explanation of a failing assert never shows the key
    assert leaked == [], leaked
    assert out == "Agent: the key is gh<redacted>\n\n"           # reached only when `out` holds no piece of the key
    assert counts == {"scrub_changed": 1}


def test_a_hook_renders_what_it_handed_the_model():
    counts = {}

    def hook(a):
        return R.block(_ev("hook", "hook", json.dumps(a)), counts)
    ctx = {"type": "hook_additional_context", "content": ["first text", "second text"], "hookEvent": "PostToolUse",
           "hookName": "PostToolUse:Bash", "toolUseID": "t"}
    assert hook(ctx) == "Hook: first text\nsecond text\n\n"
    for event in ("UserPromptSubmit", "SessionStart"):            # s1_scores.PLAIN_EVENTS: the plain stdout reaches it
        assert hook(success(event, None, "t", "x", "plain\n", "plain\n")) == "Hook: plain\n\n"
    for event in ("PreToolUse", "PostToolUse", "SubagentStart"):  # it never does
        assert hook(success(event, "Bash", "t", "x", "plain\n", "plain\n")) == ""
    err = {"type": "hook_blocking_error", "hookEvent": "PostToolUse", "hookName": "PostToolUse:Edit", "toolUseID": "t",
           "blockingError": {"blockingError": "[cmd]: stop here", "command": "cmd"}}
    assert hook(err) == "Hook: [cmd]: stop here\n\n"
    for other in ({"type": "hook_system_message", "content": "x", "hookEvent": "SessionStart"},
                  {"type": "hook_cancelled", "hookEvent": "UserPromptSubmit"},
                  {"type": "system", "subtype": "stop_hook_summary", "hookErrors": ["x"]}, ["a", "list"]):
        assert hook(other) == ""
    for lead in ("", "\n "):                    # the exporter classes the text as a hook after lstrip(), so does this
        assert R.block(_ev("hook", "hook", lead + "Stop hook feedback:\n[x]: push it"), counts) == \
            "Hook: Stop hook feedback:\n[x]: push it\n\n"
    assert counts == {}
    assert R.block(_ev("hook", "hook", "a hook text that is no JSON"), counts) == ""
    assert counts == {"hook_unparsed": 1}


def test_starts_are_defined_for_events_that_render_nothing():
    events = [_ev("owner", "text", "a"), _ev("agent", "thinking", "t"), _ev("agent", "text", "b"),
              _ev("system", "notification", "n")]
    assert R.render(events) == ("Owner: a\n\nAgent: b\n\n", [0, 10, 10, 20])


def test_the_render_of_the_fixture_is_the_text_written_out_here(world):
    for src, s in world.sessions.items():
        events = _events(world.export, src)
        assert [e["seq"] for e in events] == list(range(len(s.exp)))      # one record, one event
        text, starts = R.render(events)
        assert text == "".join(s.exp), src
        assert starts == [sum(map(len, s.exp[:i])) for i in range(len(s.exp))]
        for ev, block in zip(events, s.exp):      # each block alone is its slice of the whole: it needs its event only
            assert R.block(ev) == block


# ---------------------------------------------------------------- the view (D-2 to D-7)

def test_every_present_id_is_found_once_where_it_sits(world):
    assert [r["id"] for r in world.rows] == [ID_UPS, ID_PRE, ID_POST, ID_DENY, ID_PAR1, ID_PAR2, ID_TWO1, ID_TWO2,
                                             ID_LONG]
    placed = {sid: (split, answer == "true") for split, answer, sids in ROWS for sid in sids}
    for r in world.rows:
        src, carrier, event, call_id, step, state = EXPECTED[r["id"]]
        assert list(r) == ROW_KEYS
        assert type(r["label"]) is bool
        assert r == {"id": r["id"], "item_id": world.items[r["id"]], "split": placed[r["id"]][0],
                     "label": placed[r["id"]][1], "source": SOURCE[r["id"]],
                     "time": TIME.get(r["id"]) or world.inj[r["id"]].ts, "src": src, "carrier": carrier,
                     "hook_event": event, "call_id": call_id, "step_event": step, "state_event": state,
                     "state_end": sum(map(len, world.sessions[src].exp[:state])), "candidate": TXT[r["id"]],
                     "candidate_sha256": hashlib.sha256(TXT[r["id"]].encode("utf-8")).hexdigest()}


def test_an_absent_build_id_is_counted_not_in_export_and_the_run_exits_0(world):
    assert world.result.returncode == 0
    assert world.summary["counts"]["not_found"] == {"ambiguous": 0, "not_in_export": 1}
    assert ID_ABSENT not in {r["id"] for r in world.rows} and ID_UNSCORED not in {r["id"] for r in world.rows}
    blocks = [b for s in world.sessions.values() for b in s.exp]
    assert world.result.stdout == ("s1-view: 10 build ids, 9 found, 1 not in the export, 0 ambiguous; 2 files, 48 events,"
                                   " %d blocks, %d characters rendered\n" % (sum(1 for b in blocks if b),
                                                                             sum(map(len, blocks))))


def test_the_summary_holds_counts_and_digests_and_no_session_text(world):
    s = world.summary
    assert sorted(s) == ["code", "counts", "inputs", "render", "streams", "version"]
    assert s["version"] == "s1-view-v1"
    assert s["render"] == {"version": "s1-render-v1", "cap": 4000, "head": 3000, "tail": 1000}
    names = ["summary.json"] + ["%s/%s" % (sp, f) for sp in ("train", "heldout")
                                for f in ("dataset.jsonl", "labels.jsonl", "manifest.json")]
    assert s["inputs"]["build"] == {"commit": FAKE_COMMIT, "files": {n: _sha(world.build / n) for n in names}}
    m = json.loads((world.export / "manifest.json").read_text())
    assert s["inputs"]["export"] == {"export_id": m["export_id"], "code_sha256": m["code_sha256"], "files_verified": 2}
    exp = {src: sess.exp for src, sess in world.sessions.items()}
    assert s["streams"] == {src: {"events": len(e), "rendered": sum(1 for b in e if b), "chars": len("".join(e)),
                                  "sha256": hashlib.sha256("".join(e).encode("utf-8")).hexdigest()}
                            for src, e in exp.items()}
    blocks = [b for e in exp.values() for b in e]
    assert s["counts"] == {
        "build_ids": 10, "found": 9, "not_found": {"ambiguous": 0, "not_in_export": 1},
        "carrier": {"hook_additional_context": 8, "tool_result": 1},
        "hook_event": {"PostToolUse": 3, "PreToolUse": 5, "UserPromptSubmit": 1},
        "split": {"heldout": 3, "train": 6}, "label": {"false": 2, "true": 7}, "step_found": {"false": 0, "true": 8},
        "time_equal": {"false": 1, "true": 8}, "candidate_vs_chunk": {"differs": 1, "equal": 7, "equal_prefix": 1},
        "hook_run_before": {"0": 1, "1+": 8}, "whole": {"false": 0, "true": 9},
        "render": {"cut": 1, "hook_unparsed": 0, "scrub_changed": 1, "events": 48,
                   "blocks": sum(1 for b in blocks if b), "chars": sum(map(len, blocks))}}
    text = (world.out / "summary.json").read_text(encoding="utf-8")
    for t in list(TXT.values()) + [MARK, COMMITTED, "the view is half built"]:
        assert t not in text
    for name in ("summary.json", "view.jsonl"):                  # no host path
        assert str(world.base) not in (world.out / name).read_text(encoding="utf-8")


CLOSURE = '''
import os, sys
sys.path.insert(0, sys.argv[1])
from s1_train import view  # noqa: F401
scripts = os.path.realpath(sys.argv[1]) + os.sep
for f in sorted({os.path.realpath(m.__file__) for m in list(sys.modules.values()) if getattr(m, "__file__", None)}):
    if f.startswith(scripts):
        print(os.path.relpath(f, sys.argv[2]))
'''


def test_the_code_digests_cover_every_module_the_view_loads_from_scripts(world):
    r = _run("-c", CLOSURE, SCRIPTS, ROOT, timeout=120)            # measured in a fresh interpreter
    assert r.returncode == 0, r.stderr[-1000:]
    assert sorted(r.stdout.split()) == sorted(V.CODE)
    assert world.summary["code"] == {p: _sha(ROOT / p) for p in V.CODE}


def test_two_runs_give_byte_identical_outputs(world, tmp_path):
    out = tmp_path / "out"
    out.mkdir()                                                    # an empty directory is a valid --out
    r = _view(world.build, world.export, out)
    assert r.returncode == 0, r.stderr[-1000:]
    assert sorted(os.listdir(out)) == ["summary.json", "view.jsonl"]
    for name in ("view.jsonl", "summary.json"):
        assert (out / name).read_bytes() == (world.out / name).read_bytes(), name
    assert r.stdout == world.result.stdout


def test_a_tool_result_carries_a_stamp_only_as_a_hook_error(world):
    deny = _events(world.export, MAIN)[15]
    found = V.carriers([deny], {ID_DENY})
    assert [c[:4] for c in found] == [(0, "tool_result", "PreToolUse", "toolu_zqv_02")]
    assert V.carriers([dict(deny, outcome={"is_error": False})], {ID_DENY}) == []    # s1_scores.injections_of's rule
    assert V.carriers([deny], {ID_PRE}) == []                                         # a stamp of no build id


# ---------------------------------------------------------------- the security boundary

def test_a_thinking_marker_is_in_no_output_and_no_rendered_stream(world):
    for src in (MAIN, LANE):
        events = _events(world.export, src)
        assert [e["kind"] for e in events if MARK in e["text"]] == ["thinking"]     # the plant reached the export
        assert MARK not in R.render(events)[0]
    assert MARK not in _outputs(world.out, world.result)


def test_a_fake_key_planted_after_the_export_is_in_no_output(world, tmp_path, se):
    key = {"gh-result": se.CANARIES["gh-result"]}
    export = _copy(world.export, tmp_path, "export")
    events = _events(export, MAIN)
    a = json.loads(events[21]["text"])                         # ID_PAR1's injection: the text its candidate is cut from
    a["content"][0] = a["content"][0].replace(PACK, PACK + " key " + key["gh-result"])
    events[21]["text"] = _canon(a)
    events[17]["text"] += " key " + key["gh-result"]          # and a coordinator text: its rendered stream
    _write_events(export, MAIN, events)
    # every assertion below is on a plain name or on text already shown free of the key: a failure never prints it
    planted = _leaks(json.dumps(_events(export, MAIN)), key)
    assert planted == ["gh-result"], planted                                          # the plant reached the export
    out = tmp_path / "out"
    res = _view(world.build, export, out)
    rc = res.returncode
    assert rc == 0, "the view refused the planted export"
    leaked = _leaks(_outputs(out, res), key) + _leaks(R.render(_events(export, MAIN))[0], key)
    assert leaked == [], leaked
    par1 = next(json.loads(line) for line in C.jsonl_lines((out / "view.jsonl").read_text(encoding="utf-8"))
                if json.loads(line)["id"] == ID_PAR1)
    assert par1["candidate"] == PACK + " key gh<redacted>"   # the scrub took it, not a lost text


def test_no_state_holds_its_own_id(world):
    for r in world.rows:
        text = R.render(_events(world.export, r["src"]))[0]
        assert r["id"] not in text[:r["state_end"]], r["id"]
        assert text.find(r["id"]) >= r["state_end"], r["id"]


def test_no_hook_text_of_the_carriers_run_is_in_its_state(world):
    # the run is found here from the record the fixture wrote the carrier to, never from the view's state_event: every
    # hook event next to the carrier, both ways (a tool_result carrier: the hooks right before it, and itself)
    for r in world.rows:
        events = _events(world.export, r["src"])
        text = R.render(events)[0]
        c = world.inj[r["id"]].line - 1                                  # one record, one event: seq = line - 1
        j, k = c, c + 1
        while j > 0 and events[j - 1]["kind"] == "hook":
            j -= 1
        while events[c]["kind"] == "hook" and k < len(events) and events[k]["kind"] == "hook":
            k += 1
        blocks = [b for b in map(R.block, events[j:k]) if b]
        assert any(r["candidate"] in b for b in blocks), r["id"]          # the run holds the carrier
        state = text[:r["state_end"]]
        for b in blocks:
            assert b.split(": ", 1)[1].rstrip("\n") not in state, r["id"]


# ---------------------------------------------------------------- refusals and failures (D-4, D-5, D-6)

def test_an_export_file_whose_bytes_differ_from_its_manifest_sha256_is_refused(world, tmp_path):
    export = _copy(world.export, tmp_path, "export")
    p = export / (MAIN + ".xz")
    data = bytearray(p.read_bytes())
    data[len(data) // 2] ^= 1
    p.write_bytes(bytes(data))
    _refused(_view(world.build, export, tmp_path / "out"),
             "%s: its bytes do not match the manifest's output_sha256" % MAIN, tmp_path / "out")


def test_bytes_after_the_xz_stream_are_refused(world, tmp_path):
    export = _copy(world.export, tmp_path, "export")
    p = export / (MAIN + ".xz")
    extra = lzma.compress(b'{"planted": "a second stream that lzma.open would read"}\n')
    p.write_bytes(p.read_bytes() + extra)
    _set_sha(export, MAIN)
    _refused(_view(world.build, export, tmp_path / "out"), "%s: %d bytes follow the xz stream" % (MAIN, len(extra)),
             tmp_path / "out")


def test_a_cut_xz_stream_is_refused(world, tmp_path):
    export = _copy(world.export, tmp_path, "export")
    p = export / (LANE + ".xz")
    p.write_bytes(p.read_bytes()[:-12])                     # the stream footer
    _set_sha(export, LANE)
    _refused(_view(world.build, export, tmp_path / "out"), "%s: the xz stream is cut" % LANE, tmp_path / "out")


def test_an_unknown_role_and_kind_is_refused(world, tmp_path):
    export = _copy(world.export, tmp_path, "export")
    events = _events(export, MAIN)
    events[17]["kind"] = "zq_future_kind"
    _write_events(export, MAIN, events)
    _refused(_view(world.build, export, tmp_path / "out"),
             "%s: unknown (role, kind) ('coordinator', 'zq_future_kind')" % MAIN, tmp_path / "out")


def test_a_seq_that_does_not_increase_is_refused(world, tmp_path):
    export = _copy(world.export, tmp_path, "export")
    events = _events(export, MAIN)
    events[10]["seq"] = 9
    _write_events(export, MAIN, events)
    _refused(_view(world.build, export, tmp_path / "out"), "%s: seq 9 comes after seq 9" % MAIN, tmp_path / "out")


@pytest.mark.parametrize("key", ["src", "output"])
def test_a_manifest_that_names_a_file_twice_is_refused(world, tmp_path, key):
    export = _copy(world.export, tmp_path, "export")
    m = json.loads((export / "manifest.json").read_text())
    m["sources"][1][key] = m["sources"][0][key]             # two entries, one src (or one output file read twice)
    (export / "manifest.json").write_text(json.dumps(m, indent=1) + "\n")
    _refused(_view(world.build, export, tmp_path / "out"), "the export's manifest.json names the same %s twice" % key,
             tmp_path / "out")


def test_a_manifest_entry_without_its_fields_is_refused(world, tmp_path):
    export = _copy(world.export, tmp_path, "export")
    m = json.loads((export / "manifest.json").read_text())
    del m["sources"][1]["output_sha256"]
    (export / "manifest.json").write_text(json.dumps(m, indent=1) + "\n")
    _refused(_view(world.build, export, tmp_path / "out"),
             "the export's manifest.json: an entry without src, output and output_sha256", tmp_path / "out")


@pytest.mark.parametrize("change", ["extra_key", "seq_str"])
def test_a_line_that_is_not_an_event_of_the_schema_is_refused(world, tmp_path, change):
    export = _copy(world.export, tmp_path, "export")
    events = _events(export, LANE)
    if change == "extra_key":
        events[3]["zq_extra"] = 1
    else:
        events[3]["seq"] = "3"
    _write_events(export, LANE, events)
    _refused(_view(world.build, export, tmp_path / "out"), "%s: line 4 is not an event of the export's schema" % LANE,
             tmp_path / "out")


def test_a_build_row_with_no_label_record_is_refused(world, tmp_path):
    build = _copy(world.build, tmp_path, "build")
    labels = build / "train" / "labels.jsonl"
    key = C.label_key(world.items[ID_UPS], B.QID)
    labels.write_text("".join(line + "\n" for line in C.jsonl_lines(labels.read_text())
                              if json.loads(line)["key"] != key))
    _set_labels_sha(build, "train")
    _refused(_view(build, world.export, tmp_path / "out"), "the build's train row %s has no label record" % key,
             tmp_path / "out")


def test_labels_that_hold_two_records_for_one_row_are_refused(world, tmp_path):
    build = _copy(world.build, tmp_path, "build")
    labels = build / "train" / "labels.jsonl"
    lines = C.jsonl_lines(labels.read_text())
    labels.write_text("".join(line + "\n" for line in lines + lines[:1]))
    _set_labels_sha(build, "train")
    _refused(_view(build, world.export, tmp_path / "out"),
             "the build's train labels hold two records for %s" % json.loads(lines[0])["key"], tmp_path / "out")


def test_labels_that_do_not_match_their_manifest_are_refused(world, tmp_path):
    build = _copy(world.build, tmp_path, "build")
    labels = build / "heldout" / "labels.jsonl"
    labels.write_text(labels.read_text() + "\n")
    _refused(_view(build, world.export, tmp_path / "out"),
             "the build's heldout/labels.jsonl does not match its manifest's sha256", tmp_path / "out")


def test_a_target_that_is_neither_true_nor_false_is_refused(world, tmp_path):
    build = _copy(world.build, tmp_path, "build")
    labels = build / "heldout" / "labels.jsonl"
    key = C.label_key(world.items[ID_DENY], B.QID)
    recs = [json.loads(line) for line in C.jsonl_lines(labels.read_text())]
    for rec in recs:
        if rec["key"] == key:
            rec["target"] = [0.5, 0.5]
    labels.write_text("".join(C.dumps(rec) + "\n" for rec in recs))
    _set_labels_sha(build, "heldout")
    _refused(_view(build, world.export, tmp_path / "out"),
             "the build's heldout row %s: its target [0.5, 0.5] is neither true nor false" % key, tmp_path / "out")


def test_a_build_source_that_is_not_an_injection_is_refused(world, tmp_path):
    # a commit source: common.load_dataset accepts its kind (row_identities), so this check is the only one that sees it
    items = make_build(tmp_path / "build", world.inj, extra={ID_LONG: {"kind": "commit", "commit": FAKE_COMMIT}})
    _refused(_view(tmp_path / "build", world.export, tmp_path / "out"),
             "the build's heldout row %s holds a source that is not an injection" % C.label_key(items[ID_LONG], B.QID),
             tmp_path / "out")


def test_a_build_without_its_summary_is_refused(world, tmp_path):
    build = _copy(world.build, tmp_path, "build")
    (build / "summary.json").unlink()
    r = _view(build, world.export, tmp_path / "out")
    _refused(r, "the build: [Errno 2] No such file or directory: ", tmp_path / "out")
    assert "summary.json" in r.stderr


def test_a_split_whose_dataset_differs_from_its_manifest_is_refused(world, tmp_path):
    build = _copy(world.build, tmp_path, "build")
    data = build / "train" / "dataset.jsonl"
    data.write_text(data.read_text() + "\n")                # common.load_dataset verifies the sha256
    _refused(_view(build, world.export, tmp_path / "out"), "the build's train split: ", tmp_path / "out")


def test_a_split_that_changed_between_the_two_reads_is_refused(world, monkeypatch):
    # read_build hashes its own read of each file; load_dataset reads them again: a manifest that differs between the
    # two reads (a writer between them) is refused, never joined
    real = C.load_dataset

    def load(ddir, *args, **kwargs):
        rows, manifest = real(ddir, *args, **kwargs)
        return rows, dict(manifest, dataset=dict(manifest["dataset"], sha256="0" * 64))
    monkeypatch.setattr(C, "load_dataset", load)
    with pytest.raises(V.Refused) as e:
        V.read_build(world.build)
    assert str(e.value) == "the build's train split changed while it was read"


def test_a_source_id_in_two_rows_is_refused(world, tmp_path):
    make_build(tmp_path / "build", world.inj, rows=ROWS + (("heldout", "true", (ID_PRE,)),))
    _refused(_view(tmp_path / "build", world.export, tmp_path / "out"),
             "source id %s is in two rows of the build" % ID_PRE, tmp_path / "out")


def test_an_id_with_two_carriers_is_counted_ambiguous_never_guessed(world, tmp_path):
    export = _copy(world.export, tmp_path, "export")
    events = _events(export, MAIN)
    events.append(dict(events[9], seq=len(events), line=events[-1]["line"] + 1))     # ID_PRE's carrier, once more
    _write_events(export, MAIN, events)
    out = tmp_path / "out"
    r = _view(world.build, export, out)
    assert r.returncode == 0, r.stderr[-800:]
    summary = json.loads((out / "summary.json").read_text())
    assert summary["counts"]["not_found"] == {"ambiguous": 1, "not_in_export": 1}
    assert summary["counts"]["found"] == 8
    assert ID_PRE not in (out / "view.jsonl").read_text()


def test_a_stamp_source_that_differs_from_the_builds_is_refused(world, tmp_path):
    make_build(tmp_path / "build", world.inj, source={ID_UPS: "filepacks"})
    _refused(_view(tmp_path / "build", world.export, tmp_path / "out"),
             "%s: the stamp's source 'wiki-context' is not the build's 'filepacks'" % ID_UPS, tmp_path / "out")


def test_an_out_dir_that_is_not_empty_is_refused(world, tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    (out / "keep.txt").write_text("keep\n")
    r = _view(world.build, world.export, out)
    assert r.returncode == 2 and "s1-view: refused: --out %s exists and is not an empty directory" % out in r.stderr
    assert sorted(os.listdir(out)) == ["keep.txt"] and (out / "keep.txt").read_text() == "keep\n"


def test_an_id_the_stream_holds_before_its_state_ends_is_refused(world, tmp_path):
    export = _copy(world.export, tmp_path, "export")
    events = _events(export, MAIN)
    events[1]["text"] += " See %s." % ID_PRE                        # the owner's prompt names the id before its run
    _write_events(export, MAIN, events)
    _refused(_view(world.build, export, tmp_path / "out"),
             "%s: the rendered stream of %s holds the id before its state ends" % (ID_PRE, MAIN), tmp_path / "out")


def test_an_id_the_render_holds_nowhere_is_refused(world, tmp_path):
    # the brief's check is text.find(id) >= state_end: an id its own carrier's block lost to the cap (both its stamp
    # line and its request line in the cut middle) is refused too
    export = _copy(world.export, tmp_path, "export")
    events = _events(export, MAIN)
    a = json.loads(events[21]["text"])
    a["content"] = ["x " * 1500] + a["content"] + ["z " * 600]
    events[21]["text"] = _canon(a)
    _write_events(export, MAIN, events)
    _refused(_view(world.build, export, tmp_path / "out"),
             "%s: the rendered stream of %s holds the id nowhere" % (ID_PAR1, MAIN), tmp_path / "out")
