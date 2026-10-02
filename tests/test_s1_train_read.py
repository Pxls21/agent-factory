"""tests/test_s1_train_read.py — scripts/s1_train/read.py, the reading program of the first S1 training (task #471;
brief tasks/briefs/jev-laya/S4-2-READ-brief.md; docs/research/findings/s1-train/PREREG-441.md §2 and §8).

Fixtures go through the real producers, as tests/test_s1_train_view.py makes them: a session tree (a main transcript
and one lane transcript, in that file's record shapes; each stamp by hook_context.stamp) exported by
scripts/session_export.py's CLI (an init-key FAKE key, a fixture repo, --known-values key-only), a frozen build written
by build_s1.write_split, and scripts/s1_train/view.py run over them. The pre-registration is PREREG-441's own block
with the fixture's sha256s (computed here), a short window that some rows' states pass and others do not, and a short
tail. The session holds six scored injections in two files: two on one call (one position, two rows), two with one
text (one candidate), one whose candidate is over the render's cap; a thinking block in each file holds a marker.

The oracle is this file's own (R-3 to R-6 written out; never read.py's helpers): the fake tokenizer as a regex over
R-4's pieces, longest first, and the fake backend's update (decay, then add the id's embedding) folded over ids
computed here from the rendered text, block by block. The copy rule is the oracle's: `s` at a position is the fold of
the stream's ids before it, so a candidate read on the original state shows in every later `s`.

Every output of tokens, tails and --work is made under a temp directory in no git work tree (R-9 refuses one inside a
tree, and the basetemp may lie in a clone), as test_s1_train_view.py's _out does. The FAKE key is a canary of
session_export.CANARIES, assembled at run time; no assertion prints it. NOT run here: the hf tokenizer and the fla
backend (no torch or transformers in the sandbox; the brief forbids a test to import them).
"""
import array
import collections
import functools
import hashlib
import importlib.util
import json
import lzma
import math
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import types

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
READ = SCRIPTS / "s1_train" / "read.py"
VIEW = SCRIPTS / "s1_train" / "view.py"
EXPORTER = SCRIPTS / "session_export.py"
PREREG = ROOT / "docs" / "research" / "findings" / "s1-train" / "PREREG-441.md"
sys.path.insert(0, str(SCRIPTS))
from s1_train import features as F  # noqa: E402
from s1_train import read as RD  # noqa: E402
from s1_train import render as R  # noqa: E402
from laya_ft import build_s1 as B  # noqa: E402
from laya_ft import common as C  # noqa: E402
import hook_context as HC  # noqa: E402
from transcript_export import scrub_payload  # noqa: E402

# The module under test is this tree's: a mutant run in a scratch copy tests the copy (anti-hollow-green 3b).
assert pathlib.Path(RD.__file__).resolve() == READ, RD.__file__

SID = "0e0e0e0e-fake-4b4b-8c8c-00000000e1e1"
MAIN = "-home-user/%s.jsonl" % SID                                  # owner and coordinator; sorts first: file 0
LANE = "-home-user/%s/subagents/agent-azqread01.jsonl" % SID         # coordinator and agent: file 1
FAKE_COMMIT = "5be8cc0c" * 5
ID_PRE, ID_POST, ID_TWO1, ID_TWO2 = ("s1-00004a0%d" % i for i in range(1, 5))     # MAIN's
ID_LANE, ID_LONG = "s1-00004b01", "s1-00004b02"                                   # LANE's
HOOKS = "/home/user/agent-factory/.claude/hooks/"
WRAP = "python3 /home/user/agent-factory/scripts/hook_context.py %s -- python3 " + HOOKS + "%s.py"
PACK = "filepack scripts/s1_train/view.py: ledger 5, briefs 9"
LONG = "\n".join("read line %03d: each block is tokenized on its own, then read once" % i for i in range(70))
PLAN = "\n".join("plan step %02d: read the view, verify each input, then tokenize each block" % i for i in range(8))
MARK = "zq-thinking-marker-" + hashlib.sha256(b"s4-2-read thinking marker").hexdigest()[:12]
TXT = {ID_PRE: PACK, ID_POST: "READ CONTEXT: scripts/s1_train, last change b1df2d3",
       ID_TWO1: "EDIT SNAPSHOT: features.py\n  impact  module-level edit",
       ID_TWO2: "[system1 code-edit] skill build-loop, the governing lines", ID_LANE: PACK, ID_LONG: LONG}
SOURCE = {ID_PRE: "filepacks", ID_POST: "edit-snapshot", ID_TWO1: "edit-snapshot", ID_TWO2: "system1-context",
          ID_LANE: "filepacks", ID_LONG: "system1-context"}
ROWS = (("train", "true", ID_PRE), ("train", "false", ID_POST), ("heldout", "true", ID_TWO1),
        ("train", "true", ID_TWO2), ("heldout", "false", ID_LANE), ("train", "true", ID_LONG))
WINDOW, TAIL, SEGMENT = 400, 150, 64        # the fixture block's short window and tail; read's --segment
PIECES = ("\n\nH", "\n\nC", "\n\nR", "\n\nO", "\n\nA", "Hook:")    # R-4's pieces, ids 256 on, in read.py's order
DECAY = (1.0, 0.999, 0.99, 0.9, 0.75, 0.5, 0.25, 0.125)             # R-6's fake backend, written out
GIT = ["git", "-c", "user.name=zq", "-c", "user.email=zq@example.invalid", "-c", "commit.gpgsign=false",
       "-c", "core.hooksPath=/dev/null", "-c", "init.defaultBranch=main"]
Inj = collections.namedtuple("Inj", "stamped line ts")


# ---------------------------------------------------------------- the oracle (R-3 to R-6, written out)

ID_OF = {bytes([b]): b for b in range(256)}
ID_OF.update((p.encode("utf-8"), 256 + n) for n, p in enumerate(PIECES))
PIECE_OF = {i: b for b, i in ID_OF.items()}
TOKEN_RX = re.compile(b"|".join(re.escape(p.encode("utf-8")) for p in sorted(PIECES, key=len, reverse=True)) + b"|.",
                      re.S)                  # alternatives longest first: the first that matches is the longest


def encode(text):
    return [ID_OF[t] for t in TOKEN_RX.findall(text.encode("utf-8"))]


def decode(ids):
    return b"".join(PIECE_OF[i] for i in ids).decode("utf-8")


@functools.lru_cache(maxsize=None)
def emb(i):
    h = hashlib.sha256(("s1-fake %d" % i).encode("ascii")).digest()
    return tuple((h[d] - 127.5) / 128.0 for d in range(8))


def fold(ids, state=(0.0,) * 8):
    """The fake backend's readout after `ids`, read on `state`: per id, each dimension decays, then adds."""
    s = list(state)
    for i in ids:
        e = emb(i)
        s = [s[d] * DECAY[d] + e[d] for d in range(8)]
    return s


def f32(vec):
    return array.array("f", vec).tolist()


# ---------------------------------------------------------------- the session tree (test_s1_train_view.py's shapes)

class Tape:
    """One JSONL transcript in the harness's record shapes; add() returns the record's 1-based line."""

    def __init__(self, agent=None):
        self.lines, self.agent = [], agent

    @staticmethod
    def ts(line):
        return "2026-10-02T08:%02d:%02d.000Z" % divmod(line, 60)

    def _base(self, kind):
        n = len(self.lines) + 1
        r = {"parentUuid": None, "isSidechain": self.agent is not None, "userType": "external",
             "cwd": "/home/user/agent-factory", "sessionId": SID, "version": "2.1.0", "gitBranch": "fake",
             "type": kind, "uuid": "u-%05d" % n, "timestamp": self.ts(n)}
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

    def result(self, cid, content):
        return self.user([{"tool_use_id": cid, "type": "tool_result", "content": content, "is_error": False}],
                         sourceToolAssistantUUID="u-fake")

    def attachment(self, att):
        r = self._base("attachment")
        r["attachment"] = att
        return self.add(r)

    def write(self, path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(self.lines) + "\n")


def success(event, tool, cid, command, stdout, content=""):
    """A hook_success attachment with the real key set."""
    return {"type": "hook_success", "hookName": "%s:%s" % (event, tool) if tool else event, "hookEvent": event,
            "toolUseID": cid, "command": command, "content": content, "stdout": stdout, "stderr": "", "exitCode": 0,
            "durationMs": 7}


def stamped(t, inj, event, tool, cid, sid):
    """An S1 injection as the harness writes a hook_context-wrapped hook's: a hook_success holding the JSON stdout, its
    content empty, then the hook_additional_context holding the stamped text (two records, one run)."""
    s = HC.stamp(TXT[sid], SOURCE[sid], sid)
    stdout = json.dumps({"hookSpecificOutput": {"hookEventName": event, "additionalContext": s}}) + "\n"
    t.attachment(success(event, tool, cid, WRAP % (event, SOURCE[sid]), stdout))
    line = t.attachment({"type": "hook_additional_context", "content": [s], "hookEvent": event,
                         "hookName": "%s:%s" % (event, tool), "toolUseID": cid})
    inj[sid] = Inj(s, line, t.ts(line))


def build_main(inj):
    t = Tape()
    orient = "ORIENT: task #471 is next\nthe ledger is current\n"
    t.attachment(success("SessionStart", "startup", "zq-ss-01", "bash scripts/orient.sh", orient, orient))   # seq 0
    t.owner("Build the reading program of the S1 training, please. The brief is in tasks/briefs.")          # 1
    t.thinking("the marker is " + MARK)                                                                      # 2
    t.text("Reading the brief first: the view's rows, the render, then the features format.")               # 3
    t.call("toolu_zqr_01", "Bash", {"command": "ls scripts/s1_train", "description": "list the package"})   # 4
    stamped(t, inj, "PreToolUse", "Bash", "toolu_zqr_01", ID_PRE)                                           # 5, 6
    t.result("toolu_zqr_01", "features.py\nrender.py\nview.py\n")                                            # 7
    stamped(t, inj, "PostToolUse", "Bash", "toolu_zqr_01", ID_POST)                                         # 8, 9
    t.text(PLAN)                                                                     # 10: the states after it: long
    t.call("toolu_zqr_02", "Read", {"file_path": "/home/user/agent-factory/scripts/s1_train/features.py"})  # 11
    t.result("toolu_zqr_02", "     1\t#!/usr/bin/env python3\n")                                            # 12
    stamped(t, inj, "PostToolUse", "Read", "toolu_zqr_02", ID_TWO1)                                         # 13, 14
    stamped(t, inj, "PostToolUse", "Read", "toolu_zqr_02", ID_TWO2)                 # 15, 16: one call, one run
    t.text("S1-RATE %s rel=2 use=1\nDone." % ID_PRE)                                                         # 17
    return t


def build_lane(inj):
    t = Tape(agent="azqread01")
    t.user("You are the read lane. Read the brief first.")                                                   # seq 0
    t.thinking("lane thinking: the marker is " + MARK)                                                       # 1
    t.text("Reading the brief now.")                                                                         # 2
    t.call("toolu_zqr_11", "Edit", {"file_path": "/home/user/agent-factory/scripts/s1_train/read.py",
                                    "old_string": "x", "new_string": "y", "replace_all": False})            # 3
    t.result("toolu_zqr_11", "The file has been updated successfully.")                                     # 4
    stamped(t, inj, "PostToolUse", "Edit", "toolu_zqr_11", ID_LANE)                                         # 5, 6
    t.text("S1-RATE %s rel=1 use=0" % ID_LANE)                                                               # 7
    t.call("toolu_zqr_12", "Bash", {"command": "bash scripts/test_summary.sh tests/test_s1_train_read.py"})  # 8
    stamped(t, inj, "PreToolUse", "Bash", "toolu_zqr_12", ID_LONG)                                          # 9, 10
    t.result("toolu_zqr_12", "pytest-summary: 1 passed")                                                     # 11
    t.text("Done.")                                                                                          # 12
    return t


def make_build(out, inj):
    """A frozen S1 build through build_s1.write_split (test_s1_train_view.py's make_build, one source per row)."""
    q = C.S1_QUESTIONS[B.QID]
    pairs = {"train": [], "heldout": []}
    for n, (split, answer, sid) in enumerate(ROWS):
        chunk = B.cap(scrub_payload(B.chunk_of(inj[sid].stamped, True)), B.CAPS["chunk"], at_line=True)
        state = {"task": "Build the reading program, please.", "intent": "row %d" % n, "step": "the step of %s" % sid,
                 "kind": B.KINDS.get(SOURCE[sid], SOURCE[sid]), "chunk": chunk}
        ssha = C.state_sha(state)
        row = {"item_id": "s1-%s" % ssha[:20], "question_id": B.QID, "question_sha": C.question_sha(q),
               "state_sha": ssha, "options": C.options(q), "question": q, "state": state,
               "sources": [{"kind": "injection", "id": sid, "source": SOURCE[sid], "time": inj[sid].ts}]}
        pairs[split].append((row, answer))
    base = {"version": B.VERSION, "commit": FAKE_COMMIT, "cutoff": {}, "question": {B.QID: C.question_sha(q)},
            "caps": B.CAPS, "model": {}, "code": {}}
    for split in ("train", "heldout"):
        B.write_split(out, split, pairs[split], base, "2026-10-02T09:00:00.000Z")
    (pathlib.Path(out) / "summary.json").write_text(
        json.dumps({"version": B.VERSION, "commit": FAKE_COMMIT}, indent=1, sort_keys=True) + "\n")


# ---------------------------------------------------------------- helpers

def _run(*args, timeout=300):
    return subprocess.run([sys.executable, *map(str, args)], capture_output=True, text=True, timeout=timeout)


def _tokens(view, export, prereg, out):
    return _run(READ, "tokens", "--view", view, "--export", export, "--prereg", prereg, "--tokenizer", "fake",
                "--out", out)


def _tails(view, export, prereg, out):
    return _run(READ, "tails", "--view", view, "--export", export, "--prereg", prereg, "--out", out)


def _read(tokens, out, *extra, segment=SEGMENT):
    return _run(READ, "read", "--tokens", tokens, "--backend", "fake", "--segment", segment, *extra, "--out", out)


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


def _write_events(export, src, events):
    """One export file rewritten with `events`, its sha256 in the manifest (test_s1_train_view.py's)."""
    data = "".join(json.dumps(e, ensure_ascii=False, separators=(",", ":")) + "\n" for e in events).encode("utf-8")
    (export / (src + ".xz")).write_bytes(lzma.compress(data, preset=6))
    m = json.loads((export / "manifest.json").read_text())
    for s in m["sources"]:
        if s["src"] == src:
            s["output_sha256"] = _sha(export / s["output"])
    (export / "manifest.json").write_text(json.dumps(m, indent=1) + "\n")


def _rows(view):
    return [json.loads(line) for line in C.jsonl_lines((pathlib.Path(view) / "view.jsonl").read_text(encoding="utf-8"))]


def _write_rows(view, rows):
    """view.jsonl as view.py writes it."""
    (view / "view.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n"
                                             for r in rows), encoding="utf-8")


def _copy(src, tmp_path, name):
    return pathlib.Path(shutil.copytree(src, tmp_path / name))


def _ids(path):
    a = array.array("I")
    a.frombytes(pathlib.Path(path).read_bytes())
    if sys.byteorder != "little":
        a.byteswap()
    return a.tolist()


def _block(path):
    """A pre-registration's ```json block, parsed here (not by read.py)."""
    return json.loads(pathlib.Path(path).read_text(encoding="utf-8").split("```json\n", 1)[1].split("\n```", 1)[0])


def _prereg_text(view, export, **features):
    """PREREG-441's block with the fixture's sha256s, short window and tail; `features` replaces features.* keys."""
    block = _block(PREREG)
    block["inputs"].update(view_jsonl_sha256=_sha(view / "view.jsonl"), view_summary_sha256=_sha(view / "summary.json"),
                           export_manifest_sha256=_sha(export / "manifest.json"))
    block["features"].update(dict({"short_window_tokens": WINDOW}, **features))
    block["word_overlap"]["state_tail_chars"] = TAIL
    return "# A fixture pre-registration (tests/test_s1_train_read.py)\n\n```json\n%s\n```\n" % json.dumps(block, indent=2)


def _prereg(tmp_path, view, export, **features):
    path = tmp_path / "prereg.md"
    path.write_text(_prereg_text(pathlib.Path(view), pathlib.Path(export), **features), encoding="utf-8")
    return path


def _leaks(blob, canaries):
    """Names of the canaries whose value, or any 8-character window of it, is in `blob`. Never the values."""
    return sorted(n for n, v in canaries.items() if v in blob or any(v[i:i + 8] in blob for i in range(len(v) - 7)))


OUT_ROOT = {}                       # "root": this module's output root (the _out_root fixture)


def _root(tmp_path):
    """A new output directory for the test that owns tmp_path: in no git work tree (R-9 refuses one inside a tree, and
    the basetemp can lie in a clone: scripts/pc_suite.sh puts it under the PC's). New on each call: pyproject.toml's
    tmp_path_retention_policy removes a passing test's tmp_path, so a later test can get the same tmp_path.name."""
    return pathlib.Path(tempfile.mkdtemp(prefix=tmp_path.name + "-", dir=OUT_ROOT["root"]))


def _refused(r, reason, out):
    assert r.returncode == 2, (r.returncode, r.stderr[-800:])
    assert "s1-read: refused: " + reason in r.stderr, r.stderr[-800:]
    assert r.stdout == ""
    assert not pathlib.Path(out).exists()                    # nothing written


@pytest.fixture(scope="module", autouse=True)
def _out_root():
    root = pathlib.Path(os.path.realpath(tempfile.mkdtemp(prefix="zq-s1-read-")))
    try:
        assert [p for p in (root, *root.parents) if os.path.lexists(p / ".git")] == [], root   # in no git work tree
        OUT_ROOT["root"] = root
        yield root
    finally:
        OUT_ROOT.pop("root", None)
        shutil.rmtree(root, ignore_errors=True)


@pytest.fixture(scope="module")
def se():
    spec = importlib.util.spec_from_file_location("session_export_for_s1_read", EXPORTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def world(tmp_path_factory, _out_root):
    """The session tree exported by the real CLI, the frozen build, the view, the fixture pre-registration, and one
    run each of tokens and tails (read's run is the `feats` fixture: a refused read never hides the token tests)."""
    base = tmp_path_factory.mktemp("s1read")
    inj = {}
    for src, tape in ((MAIN, build_main(inj)), (LANE, build_lane(inj))):
        tape.write(base / "tree" / src)
    repo = base / "repo"
    repo.mkdir()
    (repo / "zq.md").write_text("A fixture repository for the export.\n")
    for args in (("init", "-q"), ("add", "."), ("commit", "-q", "-m", "zq")):
        r = subprocess.run(GIT + ["-C", str(repo), *args], capture_output=True, text=True, timeout=60)
        assert r.returncode == 0, r.stderr[-500:]
    key = base / "cfg" / "pseudonym.key"
    r = _run(EXPORTER, "init-key", "--key", key)
    assert r.returncode == 0, r.stderr[-500:]
    export = base / "export"
    r = _run(EXPORTER, "export", "--root", base / "tree", "--out", export, "--jobs", 1, "--key", key, "--repo", repo,
             "--known-values", "key-only")
    assert r.returncode == 0, (r.stdout[-1500:], r.stderr[-1500:])
    make_build(base / "build", inj)
    out = _out_root / "world"
    out.mkdir()
    view = out / "view"
    r = _run(VIEW, "--build", base / "build", "--export", export, "--out", view)
    assert r.returncode == 0, r.stderr[-2000:]
    prereg = _prereg(base, view, export)
    tokens, tails = out / "tokens", out / "tails"
    results = {"tokens": _tokens(view, export, prereg, tokens), "tails": _tails(view, export, prereg, tails)}
    for name, r in results.items():
        assert r.returncode == 0, (name, r.stderr[-2000:])
    return types.SimpleNamespace(base=base, out=out, export=export, build=base / "build", view=view, prereg=prereg,
                                 tokens=tokens, tails=tails, results=results, rows=_rows(view), inj=inj)


@pytest.fixture(scope="module")
def feats(world):
    """One read of the world's tokens: the fake backend, --segment 64."""
    features = world.out / "features"
    r = _read(world.tokens, features)
    assert r.returncode == 0, r.stderr[-2000:]
    return types.SimpleNamespace(features=features, result=r)


@pytest.fixture(scope="module")
def oracle(world):
    """Every token position and feature, computed here from the rendered text (R-3 to R-6)."""
    block = _block(world.prereg)
    q = encode(block["features"]["question_block"])
    cand = {r["candidate_sha256"]: encode(block["features"]["candidate_block"].replace("{body}", R.body(r["candidate"])))
            for r in world.rows}
    streams, pos, vec = {}, {}, {n: {} for n in F.ROW_ARRAYS + F.FREE_ARRAYS}
    for src in (MAIN, LANE):
        text, starts = R.render(_events(world.export, src))
        rows = [r for r in world.rows if r["src"] == src]
        last = max(r["state_end"] for r in rows)
        ids, before = [], {}
        for a, b in zip(starts, starts[1:] + [len(text)]):
            if b > a and a <= last:                    # a non-empty block, up to the one the last state ends at
                before[a] = len(ids)
                if a < last:
                    ids += encode(text[a:b])           # tokenized on its own
        streams[src] = types.SimpleNamespace(text=text, starts=starts, ids=ids, before=before, last=last)
        for r in rows:
            p = pos[r["id"]] = before[r["state_end"]]
            c = cand[r["candidate_sha256"]]
            s, s_w = fold(ids[:p]), fold(ids[max(0, p - WINDOW):p])
            c_ctx, c_ctx_w = fold(c, s), fold(c, s_w)
            for name, v in (("s", s), ("c_ctx", c_ctx), ("q_ctx", fold(q, c_ctx)), ("s_w", s_w),
                            ("c_ctx_w", c_ctx_w), ("q_ctx_w", fold(q, c_ctx_w))):
                vec[name][r["id"]] = v
    for h, c in cand.items():
        vec["c_free"][h] = fold(c)
        vec["q_free"][h] = fold(q, vec["c_free"][h])
    return types.SimpleNamespace(q=q, cand=cand, streams=streams, pos=pos, vec=vec)


# ---------------------------------------------------------------- normal behavior

def test_the_fixture_holds_the_shapes_the_rules_need(world, oracle):
    # the plants reached the view: six rows in two files, two at one position (one call), two with one candidate, one
    # candidate over the render's cap, states inside and past the window; a whole text tokenizes otherwise (R-4)
    by = {r["id"]: r for r in world.rows}
    assert sorted(by) == sorted(SOURCE) and {r["src"] for r in world.rows} == {MAIN, LANE}
    assert by[ID_TWO1]["state_end"] == by[ID_TWO2]["state_end"]
    assert by[ID_PRE]["candidate_sha256"] == by[ID_LANE]["candidate_sha256"] and len(oracle.cand) == 5
    assert len(R.body(by[ID_LONG]["candidate"])) < len(by[ID_LONG]["candidate"]) == len(LONG)
    assert min(oracle.pos.values()) <= WINDOW < max(oracle.pos.values())
    for src, st in oracle.streams.items():
        assert encode(st.text[:st.last]) != st.ids, src           # the pieces cross a block boundary
        assert decode(st.ids) == st.text[:st.last], src            # the stream is the text before the last state end
    # the copy rule is the oracle's: had ID_PRE's candidate and question been read on the original state, ID_POST's s
    # would differ (dimension 0 sums every id read)
    ids, pre, post = oracle.streams[MAIN].ids, oracle.pos[ID_PRE], oracle.pos[ID_POST]
    wrong = fold(ids[pre:post], fold(oracle.q, fold(oracle.cand[by[ID_PRE]["candidate_sha256"]], fold(ids[:pre]))))
    assert f32(wrong) != f32(oracle.vec["s"][ID_POST])


def test_the_real_prereg_block_is_read():
    psha, block, p = RD.read_prereg(PREREG)
    assert psha == _sha(PREREG) and block == _block(PREREG)
    assert p == {"view_jsonl_sha256": "29c5207de39d8f8b5c59b769ed2d56c577566189bb1d05c738ff714e09587a66",
                 "view_summary_sha256": "3c6cddc5ea182331ccbcc70d10e6ca93436bbfe66e4b298c9a067c0ab4bd917c",
                 "export_manifest_sha256": "ff049420ec74d5b044f84df7f2a75a265f01540836b4283986b626003bf060f6",
                 "candidate_block": "Hook: {body}\n\n",
                 "question_block": "Question: Is the hook text above useful for the next step?\n\nAnswer:",
                 "short_window_tokens": 2048, "state_tail_chars": 4000}


def test_the_token_streams_and_positions_equal_the_oracle(world, oracle):
    m = json.loads((world.tokens / "manifest.json").read_text(encoding="utf-8"))
    assert sorted(os.listdir(world.tokens)) == ["0.tok", "1.tok", "candidates.tok", "manifest.json"]
    assert m["version"] == "s1-tokens-v1" and [e["src"] for e in m["files"]] == [MAIN, LANE]
    for k, e in enumerate(m["files"]):
        st = oracle.streams[e["src"]]
        assert (e["file"], e["sha256"]) == ("%d.tok" % k, _sha(world.tokens / e["file"]))
        assert _ids(world.tokens / e["file"]) == st.ids
        assert (e["tokens"], e["blocks"]) == (len(st.ids), len(st.before) - 1)
        assert e["rows"] == sorted([[r["id"], oracle.pos[r["id"]]] for r in world.rows if r["src"] == e["src"]],
                                   key=lambda x: (x[1], x[0]))
    flat = _ids(world.tokens / "candidates.tok")
    assert sorted(m["candidates"]) == sorted(oracle.cand)
    for h, span in m["candidates"].items():
        assert flat[span["offset"]:span["offset"] + span["length"]] == oracle.cand[h]
    assert sum(len(c) for c in oracle.cand.values()) == len(flat)
    assert m["candidate_of"] == {r["id"]: r["candidate_sha256"] for r in world.rows}
    assert m["question"] == oracle.q
    assert m["sha256"] == {n: _sha(world.tokens / n) for n in ("0.tok", "1.tok", "candidates.tok")}
    assert (m["prereg_sha256"], m["prereg_block"]) == (_sha(world.prereg), _block(world.prereg))
    assert m["inputs"] == {"view_jsonl_sha256": _sha(world.view / "view.jsonl"),
                           "view_summary_sha256": _sha(world.view / "summary.json"),
                           "export_manifest_sha256": _sha(world.export / "manifest.json")}
    assert m["tokenizer"] == {"name": "fake", "vocab_size": 262, "pieces": list(PIECES)}


def test_every_feature_equals_the_oracle(oracle, feats):
    index, m = F.read(str(feats.features))
    assert index["dim"] == 8
    assert index["rows"] == sorted(oracle.pos) and index["free"] == sorted(oracle.cand)
    for name in F.ROW_ARRAYS + F.FREE_ARRAYS:
        assert sorted(oracle.vec[name]) == m[name].keys, name
        for key, v in oracle.vec[name].items():
            assert m[name].get(key) == f32(v), (name, key)
    assert m["s"].get(ID_TWO1) == m["s"].get(ID_TWO2) and m["c_ctx"].get(ID_TWO1) != m["c_ctx"].get(ID_TWO2)


def test_the_features_meta_holds_exactly_its_keys(world, oracle, feats):
    index, _m = F.read(str(feats.features))
    meta = index["meta"]
    assert sorted(meta) == ["backend", "counts", "prereg_block", "prereg_sha256", "tokens_manifest_sha256"]
    assert meta["backend"] == {"name": "fake", "version": "s1-fake-v1", "decay": list(DECAY), "device": "cpu"}
    assert meta["tokens_manifest_sha256"] == _sha(world.tokens / "manifest.json")
    assert (meta["prereg_sha256"], meta["prereg_block"]) == (_sha(world.prereg), _block(world.prereg))
    forwards = 2 * len(oracle.cand)                                # R-5: c_free and q_free per candidate
    for src, st in oracle.streams.items():
        at, poss = 0, [oracle.pos[r["id"]] for r in world.rows if r["src"] == src]
        for p in sorted(set(poss)):                                # the stream: forwards of 64 ending at each position
            forwards += -(-(p - at) // SEGMENT)
            at = p
        forwards += sum(2 + -(-min(WINDOW, p) // SEGMENT) + 2 for p in poss)    # per row: c, q; the window; c, q
    assert meta["counts"] == {"tokens": {src: len(st.ids) for src, st in oracle.streams.items()},
                              "forwards": forwards, "rows": 6}


def test_compare_of_a_run_with_itself_reads_one(feats):
    r = _run(READ, "compare", feats.features, feats.features)
    assert (r.returncode, r.stderr, r.stdout.count("\n")) == (0, "", 1), r.stderr[-800:]
    assert json.loads(r.stdout) == {"min": 1.0, "arrays": {
        n: {"n": 6 if n in F.ROW_ARRAYS else 5, "min": 1.0, "median": 1.0, "max": 1.0}
        for n in F.ROW_ARRAYS + F.FREE_ARRAYS}}


def test_compare_reads_the_cosine_per_key_both_runs_hold(tmp_path):
    # exactly representable vectors with known cosines: rows r2 (1/sqrt 2) and r3 (1) in both, r1 and r4 in one only;
    # the candidate c1 opposite (-1), c2 in one only
    def run(name, rows, free):
        arrays = {n: [rows[k] for k in sorted(rows)] for n in F.ROW_ARRAYS}
        arrays.update({n: [free[k] for k in sorted(free)] for n in F.FREE_ARRAYS})
        F.write(str(tmp_path / name), sorted(rows), sorted(free), 2, arrays, {})
        return tmp_path / name
    a = run("a", {"r1": [1.0, 0.0], "r2": [1.0, 1.0], "r3": [0.0, 2.0]}, {"c1": [3.0, 4.0]})
    b = run("b", {"r2": [1.0, 0.0], "r3": [0.0, 5.0], "r4": [1.0, 1.0]}, {"c1": [-3.0, -4.0], "c2": [1.0, 0.0]})
    r = _run(READ, "compare", a, b)
    assert r.returncode == 0, r.stderr[-800:]
    half = 1 / math.sqrt(2)
    assert json.loads(r.stdout) == {"min": -1.0, "arrays": dict(
        {n: {"n": 2, "min": half, "median": (half + 1.0) / 2, "max": 1.0} for n in F.ROW_ARRAYS},
        **{n: {"n": 1, "min": -1.0, "median": -1.0, "max": -1.0} for n in F.FREE_ARRAYS})}


def test_smoke_with_the_fake_backend_passes_and_says_which_checks_ran(tmp_path):
    out = tmp_path / "smoke.json"
    r = _run(READ, "smoke", "--backend", "fake", "--out", out)
    assert (r.returncode, r.stdout) == (0, "s1-read smoke: copy pass, head not run, split pass; pass\n"), r.stderr
    res = json.loads(out.read_text())
    assert res["pass"] is True and res["backend"]["name"] == "fake"
    assert res["checks"] == {"copy": {"ran": True, "pass": True}, "head": {"ran": False},
                             "split": {"ran": True, "cosine": 1.0, "min": 0.999, "pass": True}}
    again = _run(READ, "smoke", "--backend", "fake", "--out", out)
    assert again.returncode == 2 and "s1-read: refused: --out %s exists" % out in again.stderr
    assert json.loads(out.read_text()) == res


@pytest.mark.parametrize("fault", ["copy_is_the_original", "no_state_carried"])
def test_smoke_fails_a_backend_that_breaks_a_check(tmp_path, monkeypatch, capsys, fault):
    # the smoke's two checks are not tautologies: a copy that is the original fails the copy check; a read that carries
    # no state from the last one fails the split check (exit 1, the result written)
    if fault == "copy_is_the_original":
        monkeypatch.setattr(RD.FakeBackend, "copy", lambda self, state: state)
    else:
        real = RD.FakeBackend.read
        monkeypatch.setattr(RD.FakeBackend, "read", lambda self, state, ids: real(self, self.zero(), ids))
    out = tmp_path / "smoke.json"
    assert RD.main(["smoke", "--backend", "fake", "--out", str(out)]) == 1
    res = json.loads(out.read_text())
    failed = "copy" if fault == "copy_is_the_original" else "split"
    assert res["pass"] is False and [n for n, c in sorted(res["checks"].items()) if c["ran"] and not c["pass"]] \
        == [failed]
    assert capsys.readouterr().out.endswith("; FAIL\n")


def test_tails_hold_each_rows_last_characters(world, oracle):
    data = (world.tails / "tails.jsonl").read_bytes()
    recs = [json.loads(line) for line in C.jsonl_lines(data.decode("utf-8"))]
    assert [r["id"] for r in recs] == sorted(SOURCE)
    by = {r["id"]: r for r in world.rows}
    for rec in recs:
        end = by[rec["id"]]["state_end"]
        assert list(rec) == ["id", "tail"]
        assert rec["tail"] == oracle.streams[by[rec["id"]]["src"]].text[end - TAIL:end] and len(rec["tail"]) == TAIL
    m = json.loads((world.tails / "manifest.json").read_text())
    assert m == {"prereg_sha256": _sha(world.prereg), "view_jsonl_sha256": _sha(world.view / "view.jsonl"),
                 "view_summary_sha256": _sha(world.view / "summary.json"),
                 "export_manifest_sha256": _sha(world.export / "manifest.json"), "count": 6,
                 "tails_sha256": hashlib.sha256(data).hexdigest()}
    assert sorted(os.listdir(world.tails)) == ["manifest.json", "tails.jsonl"]


def test_stdout_carries_one_line_of_counts_and_no_session_text(world, oracle, feats):
    results = dict(world.results, read=feats.result)
    assert results["tokens"].stdout == "s1-read tokens: 2 files, 6 rows, 5 candidates, %d tokens in %d blocks\n" % (
        sum(len(st.ids) for st in oracle.streams.values()), sum(len(st.before) - 1 for st in oracle.streams.values()))
    assert results["read"].stdout.startswith("s1-read read: 2 files (0 resumed), 6 rows, 5 candidates, ")
    assert results["tails"].stdout == "s1-read tails: 6 rows, %d characters at most each\n" % TAIL
    for name, r in results.items():
        assert r.stdout.count("\n") == 1, name
        for t in [MARK, PLAN.split("\n")[0], "Reading the brief"] + [TXT[i].split("\n")[0] for i in TXT]:
            assert t not in r.stdout + r.stderr, (name, t)


# ---------------------------------------------------------------- failure behavior

@pytest.mark.parametrize("cmd", ["tokens", "tails"])
@pytest.mark.parametrize("which", ["view_jsonl", "view_summary", "export_manifest"])
def test_an_input_whose_sha256_is_not_the_blocks_is_refused(world, tmp_path, cmd, which):
    view, export = _copy(world.view, tmp_path, "view"), _copy(world.export, tmp_path, "export")
    path = {"view_jsonl": view / "view.jsonl", "view_summary": view / "summary.json",
            "export_manifest": export / "manifest.json"}[which]
    path.write_bytes(path.read_bytes() + b"\n")                   # the same JSON: only its sha256 differs
    name = {"view_jsonl": "view.jsonl", "view_summary": "summary.json",
            "export_manifest": "the export's manifest.json"}[which]
    out = _root(tmp_path) / "out"
    _refused({"tokens": _tokens, "tails": _tails}[cmd](view, export, world.prereg, out),
             "%s: its sha256 is not the block's inputs.%s_sha256" % (name, which), out)


@pytest.mark.parametrize("cmd", ["tokens", "tails"])
def test_a_summary_stream_sha256_that_is_not_the_renders_is_refused(world, tmp_path, cmd):
    view = _copy(world.view, tmp_path, "view")
    s = json.loads((view / "summary.json").read_text())
    s["streams"][LANE]["sha256"] = hashlib.sha256(b"another render").hexdigest()
    (view / "summary.json").write_text(json.dumps(s, indent=1, sort_keys=True) + "\n")
    prereg = _prereg(tmp_path, view, world.export)                 # the block holds the changed summary's sha256
    out = _root(tmp_path) / "out"
    _refused({"tokens": _tokens, "tails": _tails}[cmd](view, world.export, prereg, out),
             "%s: the sha256 of its render is not summary.json's" % LANE, out)


@pytest.mark.parametrize("cmd", ["tokens", "tails"])
@pytest.mark.parametrize("end", ["inside_a_block", "zero"])
def test_a_state_end_that_is_not_a_block_start_or_is_zero_is_refused(world, tmp_path, cmd, end):
    # the view and its sha256 in the fixture block both change, so only the state_end check can refuse it
    view = _copy(world.view, tmp_path, "view")
    rows = _rows(view)
    row = next(r for r in rows if r["id"] == ID_POST)
    row["state_end"] = row["state_end"] + 1 if end == "inside_a_block" else 0
    _write_rows(view, rows)
    text, starts = R.render(_events(world.export, MAIN))
    heads = {a for a, b in zip(starts, starts[1:] + [len(text)]) if b > a}
    assert (row["state_end"] in heads) == (end == "zero")          # 0 starts the first block: only "> 0" refuses it
    prereg = _prereg(tmp_path, view, world.export)
    out = _root(tmp_path) / "out"
    reason = ("%s: its state_end %d is not the start of a non-empty block" if end == "inside_a_block" else
              "%s: its state_end %d is not greater than 0") % (ID_POST, row["state_end"])
    _refused({"tokens": _tokens, "tails": _tails}[cmd](view, world.export, prereg, out), reason, out)


def test_a_candidate_whose_sha256_is_not_its_rows_is_refused(world, tmp_path):
    view = _copy(world.view, tmp_path, "view")
    rows = _rows(view)
    row = next(r for r in rows if r["id"] == ID_LANE)
    row["candidate"] += " and more"                                 # its sha256 stays the shared candidate's
    _write_rows(view, rows)
    out = _root(tmp_path) / "out"
    _refused(_tokens(view, world.export, _prereg(tmp_path, view, world.export), out),
             "%s: its candidate_sha256 is not its candidate's sha256" % ID_LANE, out)


@pytest.mark.parametrize("name", ["1.tok", "candidates.tok"])
def test_a_token_file_whose_bytes_changed_is_refused(world, tmp_path, name):
    tokens = _copy(world.tokens, tmp_path, "tokens")
    data = bytearray((tokens / name).read_bytes())
    data[8] ^= 1
    (tokens / name).write_bytes(bytes(data))
    out = tmp_path / "features"
    _refused(_read(tokens, out), "--tokens %s: %s: its sha256 is not the manifest's" % (tokens, name), out)


@pytest.mark.parametrize("form", ["none", "two", "invalid_json"])
def test_a_prereg_without_exactly_one_valid_block_is_refused(world, tmp_path, form):
    one = _prereg_text(world.view, world.export)
    path = tmp_path / "prereg.md"
    path.write_text({"none": one.replace("```json", "```text"), "two": one + "\n" + one,
                     "invalid_json": one.replace('"inputs": {', '"inputs": {,')}[form], encoding="utf-8")
    reason = {"none": "--prereg %s holds 0 ```json blocks, not one", "two": "--prereg %s holds 2 ```json blocks, not one",
              "invalid_json": "--prereg %s: its ```json block: JSONDecodeError: "}[form] % path
    out = _root(tmp_path) / "out"
    _refused(_tokens(world.view, world.export, path, out), reason, out)


@pytest.mark.parametrize("cmd", ["tokens", "tails"])
@pytest.mark.parametrize("body", ["missing", "twice"])
def test_a_candidate_block_without_body_exactly_once_is_refused(world, tmp_path, cmd, body):
    path = _prereg(tmp_path, world.view, world.export,
                   candidate_block="Hook: no body\n\n" if body == "missing" else "Hook: {body} {body}\n\n")
    out = _root(tmp_path) / "out"
    _refused({"tokens": _tokens, "tails": _tails}[cmd](world.view, world.export, path, out),
             "--prereg %s: features.candidate_block must hold {body} exactly once" % path, out)


@pytest.mark.parametrize("cmd", ["tokens", "tails", "work"])
@pytest.mark.parametrize("where", ["git_work_tree", "dotdot", "not_empty"])
def test_an_output_inside_git_named_with_dotdot_or_not_empty_is_refused(world, tmp_path, cmd, where):
    # R-9 for every output that holds session text; `dotdot` is AF-AP-261's shape: <root>/missing/../full names the
    # full directory once makedirs makes <root>/missing, and the text checks see a path that does not exist
    root = _root(tmp_path)
    full = root / "full"
    full.mkdir()
    (full / "keep.txt").write_text("keep\n")
    flag = "--work" if cmd == "work" else "--out"
    if where == "git_work_tree":
        out = world.base / "repo" / "zq-out"                       # the exporter's fixture repository
        reason = "--out %s lies inside a git work tree (%s)" % (out, os.path.join(os.path.realpath(world.base / "repo"),
                                                                                  ".git"))
    elif where == "dotdot":
        out = str(root / "missing") + "/../full"
        reason = "%s %s: an output named with a '..' part" % (flag, out)
    else:
        out = full
        reason = "--out %s exists and is not an empty directory" % out
    if cmd == "work":
        reason = reason if where == "dotdot" else "--work: " + reason
        r = _read(world.tokens, root / "features", "--work", out)
        assert not (root / "features").exists()
    else:
        r = {"tokens": _tokens, "tails": _tails}[cmd](world.view, world.export, world.prereg, out)
    assert (r.returncode, r.stdout) == (2, ""), r.stderr[-800:]
    assert "s1-read: refused: " + reason in r.stderr, r.stderr[-800:]
    assert os.listdir(full) == ["keep.txt"] and not (root / "missing").exists()
    assert not (world.base / "repo" / "zq-out").exists()


def test_a_work_dir_of_another_run_is_refused(world, tmp_path):
    root = _root(tmp_path)
    assert _read(world.tokens, root / "first", "--work", root / "work").returncode == 0
    r = _read(world.tokens, root / "second", "--work", root / "work", segment=2 * SEGMENT)    # another binding
    _refused(r, "--work %s holds another run's work: its work.json is not this run's" % (root / "work"),
             root / "second")


def test_an_only_that_names_no_file_is_refused(world, tmp_path):
    r = _read(world.tokens, tmp_path / "features", "--only=-home-user/zq-no-such.jsonl")
    _refused(r, "--only -home-user/zq-no-such.jsonl: the tokens hold no such file", tmp_path / "features")


@pytest.mark.parametrize("bad", ["segment_0", "out_not_empty", "out_dotdot"])
def test_reads_own_arguments_are_refused_before_the_run(world, tmp_path, bad):
    # features.write refuses such an --out only after every read: read.py refuses it first (a GPU window is scarce)
    full = tmp_path / "full"
    full.mkdir()
    (full / "keep.txt").write_text("keep\n")
    work, out = tmp_path / "work", {"segment_0": tmp_path / "features", "out_not_empty": full,
                                    "out_dotdot": str(tmp_path / "missing") + "/../full"}[bad]
    r = _read(world.tokens, out, "--work", work, segment=0 if bad == "segment_0" else SEGMENT)
    reason = {"segment_0": "--segment must be a positive int",
              "out_not_empty": "--out %s must not exist, or be an empty directory" % out,
              "out_dotdot": "--out %s: an output named with a '..' part" % out}[bad]
    assert (r.returncode, r.stdout) == (2, "") and "s1-read: refused: " + reason in r.stderr, r.stderr[-800:]
    assert os.listdir(full) == ["keep.txt"] and not work.exists() and not (tmp_path / "missing").exists()


# ---------------------------------------------------------------- the security boundary

def test_the_thinking_marker_is_in_no_token_stream_and_no_tail(world):
    for src in (MAIN, LANE):                                       # the plant reached the export, before every state
        events = _events(world.export, src)
        marked = [e for e in events if MARK in e["text"]]
        assert [e["kind"] for e in marked] == ["thinking"], src
        assert all(r["state_event"] > marked[0]["seq"] for r in world.rows if r["src"] == src)
    m = json.loads((world.tokens / "manifest.json").read_text())
    for name in ("0.tok", "1.tok", "candidates.tok"):
        assert MARK not in decode(_ids(world.tokens / name)), name
    assert MARK not in decode(m["question"]) and MARK not in json.dumps(m)
    assert MARK not in (world.tails / "tails.jsonl").read_text(encoding="utf-8")


def test_a_fake_key_planted_after_the_export_is_in_no_token_stream_and_no_tail(world, tmp_path, se):
    key = {"gh-result": se.CANARIES["gh-result"]}   # a FAKE GitHub-token shape, assembled at import by session_export
    export = _copy(world.export, tmp_path, "export")
    events = _events(export, MAIN)
    events[3]["text"] += " key " + key["gh-result"]                # a coordinator text inside every MAIN state
    i = world.inj[ID_TWO1].line - 1                                 # ID_TWO1's carrier: its candidate's text
    a = json.loads(events[i]["text"])
    a["content"][0] = a["content"][0].replace(TXT[ID_TWO1], TXT[ID_TWO1] + " key " + key["gh-result"])
    events[i]["text"] = _canon(a)
    _write_events(export, MAIN, events)                             # the export manifest's sha256 follows
    # every assertion below is on a plain name or on text already shown free of the key: a failure never prints it
    planted = _leaks(json.dumps(_events(export, MAIN)), key)
    assert planted == ["gh-result"], planted                        # the plant reached the export
    root = _root(tmp_path)
    r = _run(VIEW, "--build", world.build, "--export", export, "--out", root / "view")
    assert r.returncode == 0, "the view refused the planted export"
    prereg = _prereg(tmp_path, root / "view", export)               # the fixture block's sha256s follow
    rt = _tokens(root / "view", export, prereg, root / "tokens")
    rl = _tails(root / "view", export, prereg, root / "tails")
    assert (rt.returncode, rl.returncode) == (0, 0), "a run refused the planted export"
    streams = "".join(decode(_ids(root / "tokens" / n)) for n in ("0.tok", "1.tok", "candidates.tok"))
    tails = (root / "tails" / "tails.jsonl").read_text(encoding="utf-8")
    leaked = _leaks(streams + tails + rt.stdout + rt.stderr + rl.stdout + rl.stderr, key)
    assert leaked == [], leaked
    assert streams.count(" key gh<redacted>") == 2     # the scrub took it in the state and the candidate: read, not lost


# ---------------------------------------------------------------- determinism (R-10)

def test_two_runs_give_byte_identical_outputs(world, feats, tmp_path):
    root = _root(tmp_path)
    rs = {"tokens": _tokens(world.view, world.export, world.prereg, root / "tokens"),
          "read": _read(world.tokens, root / "features"),
          "tails": _tails(world.view, world.export, world.prereg, root / "tails")}
    for name, r in rs.items():
        assert r.returncode == 0, (name, r.stderr[-800:])
        assert r.stdout == dict(world.results, read=feats.result)[name].stdout, name
    for mine, theirs in ((root / "tokens", world.tokens), (root / "features", feats.features),
                         (root / "tails", world.tails)):
        assert sorted(os.listdir(mine)) == sorted(os.listdir(theirs))
        for n in os.listdir(mine):
            assert (mine / n).read_bytes() == (theirs / n).read_bytes(), n


def test_a_resumed_run_equals_an_uninterrupted_run_byte_for_byte(world, feats, tmp_path):
    root = _root(tmp_path)
    work = root / "work"
    first = _read(world.tokens, root / "first", "--only=" + MAIN, "--work", work)
    assert first.returncode == 0, first.stderr[-800:]
    assert first.stdout.startswith("s1-read read: 1 files (0 resumed), 4 rows, 4 candidates, ")
    assert F.read(str(root / "first"))[0]["rows"] == sorted([ID_PRE, ID_POST, ID_TWO1, ID_TWO2])
    full = _read(world.tokens, root / "full", "--work", work)
    assert full.returncode == 0, full.stderr[-800:]
    assert full.stdout.startswith("s1-read read: 2 files (1 resumed), 6 rows, 5 candidates, ")
    assert "s1-read: file 0: resumed in " in full.stderr and "s1-read: file 1: read in " in full.stderr
    assert sorted(os.listdir(root / "full")) == sorted(os.listdir(feats.features))
    for n in os.listdir(feats.features):
        assert (root / "full" / n).read_bytes() == (feats.features / n).read_bytes(), n
    timings = json.loads((work / "timings.json").read_text())
    assert (timings["0"]["resumed"], timings["1"]["resumed"]) == (True, False)
    assert sorted(os.listdir(work)) == ["0", "1", "timings.json", "work.json"]
