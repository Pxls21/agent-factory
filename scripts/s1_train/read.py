#!/usr/bin/env python3
"""read.py — the reading program of the first S1 training (task #471, S4-2 of tasks/s1-heads-breakdown.md; brief
tasks/briefs/jev-laya/S4-2-READ-brief.md; docs/research/findings/s1-train/PREREG-441.md §2 and §8).

A frozen RWKV-7 reads each transcript's rendered stream once, and small heads (task #472) learn from what it read. This
program turns the view of the S1 dataset (scripts/s1_train/view.py) into those features, in five subcommands:

  tokens   The pre-registration's only ```json block (R-1) names the view's and the export's sha256s, the candidate
           and question blocks and the short window. Each input is verified before use (R-2): the three sha256s, every
           export file through view.read_manifest and view.stream_events, each file that holds rows rendered by
           render.render and equal to the view summary's sha256, each row's state_end the start of a non-empty block
           and greater than 0. Each non-empty block is tokenized ON ITS OWN (R-3: a live reader reads each event when
           it arrives); a file's stream is the concatenation, kept up to its last row's state_end, and a row's position
           is the number of tokens of the blocks before its state_end (R-4).
  read     Per file, from the zero state, the stream in forwards of at most --segment tokens that end at each row
           position: `s` is the readout there; the candidate block (c_ctx), then the question block (q_ctx), are read on
           a COPY of the state, which is then dropped. Per row, the last short_window_tokens tokens before its position
           from the zero state (s_w), then the candidate (c_ctx_w) and the question (q_ctx_w). Per distinct candidate
           of the rows read, from the zero state, the candidate (c_free), then the question (q_free) (R-5). Written by
           features.write; timings go to stderr and <work>/timings.json, never into the features.
  tails    Each row's last state_tail_chars characters of the rendered text before its state_end (R-7).
  compare  The cosine per row and per candidate of two feature runs: one JSON object on stdout (R-8).
  smoke    A backend's copy and split checks on fixed texts, and for fla the head check (R-8).

The backend (R-6): `fake` is pure Python, dimension 8, deterministic, and changes the state it reads on, as the fla
cache does; `fla` loads the checkpoint as the PC does. The tokenizer: `fake` (greedy longest match, R-4) or `hf` (the
checkpoint's own). The fla backend and the hf tokenizer import torch and transformers inside themselves only; no test
imports or runs them, and they first run on the PC (task #441's smoke job).

usage:
  read.py tokens --view DIR --export DIR --prereg FILE --tokenizer fake|hf [--model DIR] --out DIR
  read.py read --tokens DIR --backend fake|fla [--model DIR] [--only=SRC ...] [--segment N] [--work DIR] --out DIR
  read.py tails --view DIR --export DIR --prereg FILE --out DIR
  read.py compare FEATURES_A FEATURES_B
  read.py smoke --backend fake|fla [--model DIR] --out FILE
--only takes one src per occurrence, in the --only=SRC form: an exported src starts with '-'. The outputs of tokens and
tails, and --work, hold session text or what is read from it (R-9): each is named without a '..' part, and passes
view.py's D-10 rule (not a symbolic link, outside any git work tree, missing or an empty directory); the one non-empty
--work taken is one that holds this run's work.json (the same tokens, backend and segment), whose finished files are
read back (counted resumed). The same inputs give byte-identical outputs with the fake backend, a resumed run included
(R-10: no clock, no host path, no randomness). Nothing session-derived is printed: stdout carries one line of counts.
exit: 0 done; 1 smoke: a check failed (its result written); 2 refused (the reason on stderr).
"""
import argparse
import array
import copy
import fnmatch
import hashlib
import json
import math
import os
import shutil
import statistics
import sys
import time
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from s1_train import features as F  # noqa: E402  the ONE features format (task #472 reads it)
from s1_train import render as R  # noqa: E402  the ONE render
from s1_train import view as V  # noqa: E402  the export's checks and D-10's output rule
from laya_ft import common as C  # noqa: E402

TOKENS_VERSION = "s1-tokens-v1"
WORK_VERSION = "s1-read-work-v1"
FAKE_VERSION = "s1-fake-v1"
SEGMENT = 32768                        # R-5's default: tokens per forward, at most
SPLIT_MIN, HEAD_MIN = 0.999, 0.9999    # R-8's bounds
SHA_KEYS = ("view_jsonl_sha256", "view_summary_sha256", "export_manifest_sha256")
WORK_JSON, TIMINGS = "work.json", "timings.json"
SMOKE = ("Owner: Read the brief first, then run the tests.\n\n",                                  # A
         'Coordinator calls Bash: {"command":"pytest -q tests/test_s1_train_read.py"}\n\n',      # B
         "Hook: a context for the next step, read on a copy of the state\n\n")                  # C


class Refused(Exception):
    """An input or an output failed a check: exit 2, the reason on stderr."""


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def _bytes(path, what):
    try:
        with open(path, "rb") as fh:
            return fh.read()
    except OSError as e:
        raise Refused("%s: %s" % (what, e))


def json_bytes(obj):
    return (json.dumps(obj, sort_keys=True, indent=1, ensure_ascii=False) + "\n").encode("utf-8")


def u32(ids):
    """Token ids as a .tok file's bytes: uint32, little-endian (R-4)."""
    a = array.array("I", ids)
    if a.itemsize != 4:
        raise Refused("this Python's array('I') is not 4 bytes")
    if sys.byteorder != "little":
        a.byteswap()
    return a.tobytes()


def ids_of(data, name):
    a = array.array("I")
    if a.itemsize != 4 or len(data) % 4:
        raise Refused("%s: not a whole number of uint32 ids" % name)
    a.frombytes(data)
    if sys.byteorder != "little":
        a.byteswap()
    return a.tolist()


def cosine(a, b):
    na, nb = math.fsum(x * x for x in a), math.fsum(y * y for y in b)
    if not (math.isfinite(na) and math.isfinite(nb) and na > 0 and nb > 0):
        raise Refused("a vector of norm 0, or not finite, has no cosine")
    return math.fsum(x * y for x, y in zip(a, b)) / math.sqrt(na * nb)


# ---------------------------------------------------------------- the pre-registration (R-1)

def json_blocks(text):
    """The bodies of a Markdown text's fenced ```json blocks (a fence's info string follows its opening ```)."""
    out, info, body = [], None, []
    for line in text.split("\n"):
        s = line.strip()
        if info is None:
            if s.startswith("```"):
                info, body = s[3:].strip(), []
        elif s == "```":
            if info == "json":
                out.append("\n".join(body))
            info = None
        else:
            body.append(line)
    return out


def read_prereg(path):
    """(the file's sha256, its block, the values R-1 names) of the pre-registration's only ```json block."""
    data = _bytes(path, "--prereg %s" % path)
    try:
        found = json_blocks(data.decode("utf-8"))
    except UnicodeDecodeError as e:
        raise Refused("--prereg %s: %s" % (path, e))
    if len(found) != 1:
        raise Refused("--prereg %s holds %d ```json blocks, not one" % (path, len(found)))
    try:
        block = json.loads(found[0])
        p = dict({k: block["inputs"][k] for k in SHA_KEYS},
                 candidate_block=block["features"]["candidate_block"],
                 question_block=block["features"]["question_block"],
                 short_window_tokens=block["features"]["short_window_tokens"],
                 state_tail_chars=block["word_overlap"]["state_tail_chars"])
    except (RecursionError, ValueError, KeyError, TypeError) as e:
        raise Refused("--prereg %s: its ```json block: %s: %s" % (path, type(e).__name__, e))
    for k in SHA_KEYS:
        if not (isinstance(p[k], str) and len(p[k]) == 64 and set(p[k]) <= set("0123456789abcdef")):
            raise Refused("--prereg %s: inputs.%s is not a sha256" % (path, k))
    if not (isinstance(p["candidate_block"], str) and p["candidate_block"].count("{body}") == 1):
        raise Refused("--prereg %s: features.candidate_block must hold {body} exactly once" % path)
    if not (isinstance(p["question_block"], str) and p["question_block"]):
        raise Refused("--prereg %s: features.question_block must be a non-empty string" % path)
    for k, where in (("short_window_tokens", "features"), ("state_tail_chars", "word_overlap")):
        if not (type(p[k]) is int and p[k] > 0):
            raise Refused("--prereg %s: %s.%s must be a positive int" % (path, where, k))
    return sha256(data), block, p


# ---------------------------------------------------------------- the inputs (R-2)

def blocks(text, starts):
    """(start, end) of each non-empty block of one rendered file, in order (render.render's starts)."""
    return [(a, b) for a, b in zip(starts, starts[1:] + [len(text)]) if b > a]


def read_inputs(view_dir, export_dir, p):
    """(rows, {src: (text, starts)}): the view's rows and the rendered text of each file that holds rows, every input
    verified first (R-2). Only the files that hold rows are read."""
    vdata = _bytes(os.path.join(view_dir, "view.jsonl"), "--view %s: view.jsonl" % view_dir)
    sdata = _bytes(os.path.join(view_dir, "summary.json"), "--view %s: summary.json" % view_dir)
    mdata = _bytes(os.path.join(export_dir, "manifest.json"), "--export %s: manifest.json" % export_dir)
    for name, data, key in (("view.jsonl", vdata, SHA_KEYS[0]), ("summary.json", sdata, SHA_KEYS[1]),
                            ("the export's manifest.json", mdata, SHA_KEYS[2])):
        if sha256(data) != p[key]:
            raise Refused("%s: its sha256 is not the block's inputs.%s" % (name, key))
    try:
        rows = [json.loads(line) for line in C.jsonl_lines(vdata.decode("utf-8"))]
        summary = json.loads(sdata.decode("utf-8"))
        mjson = json.loads(mdata.decode("utf-8"))
    except (RecursionError, ValueError) as e:
        raise Refused("--view or --export: %s" % e)
    try:
        manifest, sources, paths = V.read_manifest(export_dir)
    except V.Refused as e:
        raise Refused(str(e))
    if manifest != mjson:                      # read_manifest read the file again: the bytes hashed are the bytes read
        raise Refused("the export's manifest.json changed while it was read")
    seen = set()
    for n, r in enumerate(rows, 1):
        if not (isinstance(r, dict) and isinstance(r.get("id"), str) and r["id"] and isinstance(r.get("src"), str)
                and type(r.get("state_end")) is int and isinstance(r.get("candidate"), str)
                and isinstance(r.get("candidate_sha256"), str)):
            raise Refused("view.jsonl line %d is not a row of the view" % n)
        if r["id"] in seen:
            raise Refused("view.jsonl holds the id %s twice" % r["id"])
        seen.add(r["id"])
        if V.sha256_text(r["candidate"]) != r["candidate_sha256"]:      # the free arrays are keyed by it
            raise Refused("%s: its candidate_sha256 is not its candidate's sha256" % r["id"])
    entries = {s["src"]: s for s in sources}
    files = {}
    for src in sorted({r["src"] for r in rows}):
        if src not in entries:
            raise Refused("%s: the view's rows name it and the export's manifest does not" % src)
        try:
            events = V.stream_events(paths[src], entries[src])
        except V.Refused as e:
            raise Refused(str(e))
        try:
            text, starts = R.render(events)
        except (RecursionError, TypeError, ValueError) as e:
            raise Refused("%s: %s" % (src, e))
        try:
            want = summary["streams"][src]["sha256"]
        except (KeyError, TypeError) as e:
            raise Refused("summary.json holds no stream sha256 for %s (%s)" % (src, e))
        if V.sha256_text(text) != want:
            raise Refused("%s: the sha256 of its render is not summary.json's" % src)
        files[src] = (text, starts)
    for src, (text, starts) in files.items():
        heads = {a for a, _b in blocks(text, starts)}
        for r in rows:
            if r["src"] != src:
                continue
            if r["state_end"] <= 0:
                raise Refused("%s: its state_end %d is not greater than 0" % (r["id"], r["state_end"]))
            if r["state_end"] not in heads:
                raise Refused("%s: its state_end %d is not the start of a non-empty block" % (r["id"], r["state_end"]))
    return rows, files


# ---------------------------------------------------------------- outputs (R-9)

def _named(flag, out):
    """AF-AP-261: os.makedirs creates the parts that are missing, and a missing part before a '..' changes what the
    '..' names once it exists, so no check of the text names the directory written: such a name is refused."""
    if ".." in str(out).replace("\\", "/").split("/"):
        raise Refused("%s %s: an output named with a '..' part" % (flag, out))


def check_out(flag, out):
    """R-9: named without a '..' part, then view.py's D-10 rule: not a symbolic link, outside any git work tree,
    missing or an empty directory."""
    _named(flag, out)
    try:
        V.check_out(out)
    except V.Refused as e:                     # view.py names it --out; another flag is named before its message
        raise Refused(str(e) if flag == "--out" else "%s: %s" % (flag, e))


def _put(out, name, data):
    part = os.path.join(out, name + ".part")
    with open(part, "wb") as fh:
        fh.write(data)
    os.replace(part, os.path.join(out, name))


def write_out(flag, out, files):
    """Each (name, bytes) under `out`, in order (the manifest last); `out` is checked again first, after the inputs
    were read, so nothing is written over another output."""
    check_out(flag, out)
    try:
        os.makedirs(out, exist_ok=True)
        for name, data in files:
            _put(out, name, data)
    except OSError as e:
        raise Refused("%s %s: %s" % (flag, out, e))


# ---------------------------------------------------------------- tokenizers (R-4)

class FakeTokenizer:
    """Greedy longest match over a fixed vocabulary: the 256 single bytes of the UTF-8 text (ids 0 to 255) and PIECES
    (ids from 256, in order). Each piece but the last crosses a block boundary when a whole text is tokenized at once
    (a block ends with a blank line, and the next starts with its label), so a whole text and its blocks tokenize
    differently."""
    PIECES = ("\n\nH", "\n\nC", "\n\nR", "\n\nO", "\n\nA", "Hook:")

    def __init__(self):
        self.vocab = {bytes([b]): b for b in range(256)}
        self.vocab.update((p.encode("utf-8"), 256 + n) for n, p in enumerate(self.PIECES))
        self.longest = max(map(len, self.vocab))

    def encode(self, text):
        data, ids, i = text.encode("utf-8"), [], 0
        while i < len(data):
            n = min(self.longest, len(data) - i)
            while data[i:i + n] not in self.vocab:
                n -= 1
            ids.append(self.vocab[data[i:i + n]])
            i += n
        return ids

    def identity(self):
        return {"name": "fake", "vocab_size": len(self.vocab), "pieces": list(self.PIECES)}


class HFTokenizer:
    """The checkpoint's own tokenizer, loaded as the PC loads it (docs/research/findings/j2b-variants/rwkv7_g0.py:138).
    Its identity: its class name, its vocabulary size and the sha256 of each file named *vocab* in the model directory
    (file names only, never a host path). NOT run in the sandbox (no transformers there)."""

    def __init__(self, model_dir):
        try:
            from transformers import AutoTokenizer
        except ImportError as e:
            raise Refused("--tokenizer hf: %s" % e)
        self.tok = AutoTokenizer.from_pretrained(model_dir, trust_remote_code=True, local_files_only=True)
        self.vocab_files = {n: C.sha256_file(os.path.join(model_dir, n)) for n in sorted(os.listdir(model_dir))
                            if fnmatch.fnmatch(n, "*vocab*") and os.path.isfile(os.path.join(model_dir, n))}

    def encode(self, text):
        return self.tok.encode(text, add_special_tokens=False)

    def identity(self):
        return {"name": "hf", "class": type(self.tok).__name__, "vocab_size": self.tok.vocab_size,
                "vocab_files": self.vocab_files}


def tokenizer(name, model):
    if name == "fake":
        return FakeTokenizer()
    if not model:
        raise Refused("--tokenizer hf needs --model")
    return HFTokenizer(model)


# ---------------------------------------------------------------- backends (R-6)

class FakeBackend:
    """Pure Python, dimension 8, deterministic. Each id read adds its fixed embedding (bytes 0 to 7 of
    sha256(b"s1-fake <id>"), each (b - 127.5) / 128) after a per-dimension decay; dimension 0 never decays, so every
    readout depends on every id read before it. read() changes the state it is given, as the fla cache is changed in
    place: a candidate read on the original state instead of a copy reaches every later readout."""
    name = "fake"
    DECAY = (1.0, 0.999, 0.99, 0.9, 0.75, 0.5, 0.25, 0.125)

    def __init__(self):
        self.emb = {}

    def identity(self):
        return {"name": self.name, "version": FAKE_VERSION, "decay": list(self.DECAY), "device": "cpu"}

    def dim(self):
        return len(self.DECAY)

    def zero(self):
        return [0.0] * len(self.DECAY)

    def read(self, state, ids):
        for i in ids:
            e = self.emb.get(i)
            if e is None:
                h = hashlib.sha256(b"s1-fake %d" % i).digest()
                e = self.emb[i] = [(h[d] - 127.5) / 128.0 for d in range(len(self.DECAY))]
            for d, k in enumerate(self.DECAY):
                state[d] = state[d] * k + e[d]
        return state, list(state)

    def copy(self, state):
        return list(state)


class FlaBackend:
    """The checkpoint as the PC loads it (docs/research/findings/j2b-variants/rwkv7_g0.py:135-149): bf16, on cuda,
    eval. A read is model.model(input_ids=..., past_key_values=state, use_cache=True) under torch.no_grad(); its readout
    is last_hidden_state[0, -1] (after the model's last norm) as floats; a copy is copy.deepcopy (rwkv7_g0.py:114).
    torch, transformers and fla are imported here only. NOT run in the sandbox: the PC's smoke job runs it first."""
    name = "fla"

    def __init__(self, model_dir):
        try:
            import torch
            import transformers
            import fla
            from transformers import AutoModelForCausalLM
        except ImportError as e:
            raise Refused("--backend fla: %s" % e)
        self.torch, self.dir = torch, model_dir
        self.versions = {"torch": torch.__version__, "transformers": transformers.__version__,
                         "fla": getattr(fla, "__version__", None)}     # rwkv7_g0.py reads it guarded too
        self.model = AutoModelForCausalLM.from_pretrained(model_dir, trust_remote_code=True, local_files_only=True,
                                                          torch_dtype=torch.bfloat16).to("cuda").eval()
        self.weights = {n: C.sha256_file(os.path.join(model_dir, n)) for n in sorted(os.listdir(model_dir))
                        if n.endswith(".safetensors")}

    def identity(self):
        return {"name": self.name, "versions": self.versions, "weights_sha256": self.weights, "dtype": "bfloat16",
                "device": self.torch.cuda.get_device_name(0)}

    def dim(self):
        return self.model.config.hidden_size

    def zero(self):
        return None

    def read(self, state, ids):
        torch = self.torch
        with torch.no_grad():
            out = self.model.model(input_ids=torch.tensor([ids], device="cuda"), past_key_values=state, use_cache=True)
        return out.past_key_values, out.last_hidden_state[0, -1].float().tolist()

    def copy(self, state):
        return copy.deepcopy(state)

    def head(self, ids):
        """R-8 (3): model.lm_head on the readout (in the model's dtype), and the model's own last-position logits, both
        from the zero state on `ids`."""
        torch = self.torch
        _, readout = self.read(self.zero(), ids)
        with torch.no_grad():
            mine = self.model.lm_head(torch.tensor(readout, dtype=self.model.dtype, device="cuda")).float().tolist()
            theirs = self.model(input_ids=torch.tensor([ids], device="cuda")).logits[0, -1].float().tolist()
        return mine, theirs


def make_backend(name, model):
    if name == "fake":
        return FakeBackend()
    if not model:
        raise Refused("--backend fla needs --model")
    return FlaBackend(model)


# ---------------------------------------------------------------- tokens (R-3, R-4)

def stream(tok, text, starts, last):
    """(ids, at, n): one file's token ids, each non-empty block tokenized on its own, up to the block that starts at
    `last` (nothing after it is read); at: {block start: the number of ids before it}; n: the blocks tokenized."""
    ids, at, n = [], {}, 0
    for a, b in blocks(text, starts):
        at[a] = len(ids)
        if a >= last:
            break
        ids += tok.encode(text[a:b])
        n += 1
    return ids, at, n


def cmd_tokens(args):
    check_out("--out", args.out)
    psha, block, p = read_prereg(args.prereg)
    tok = tokenizer(args.tokenizer, args.model)
    rows, files = read_inputs(args.view, args.export, p)
    out, entries, total, nblocks = [], [], 0, 0
    for k, src in enumerate(sorted(files)):
        text, starts = files[src]
        mine = [r for r in rows if r["src"] == src]
        ids, at, n = stream(tok, text, starts, max(r["state_end"] for r in mine))
        name = "%d.tok" % k
        out.append((name, u32(ids)))
        entries.append({"src": src, "file": name, "sha256": sha256(out[-1][1]), "tokens": len(ids), "blocks": n,
                        "rows": sorted(([r["id"], at[r["state_end"]]] for r in mine), key=lambda x: (x[1], x[0]))})
        total, nblocks = total + len(ids), nblocks + n
    cands = {r["candidate_sha256"]: r["candidate"] for r in rows}
    flat, spans = [], {}
    for h in sorted(cands):
        ids = tok.encode(p["candidate_block"].replace("{body}", R.body(cands[h])))   # a plain replace (R-3)
        spans[h] = {"offset": len(flat), "length": len(ids)}
        flat += ids
    out.append(("candidates.tok", u32(flat)))
    manifest = {"version": TOKENS_VERSION, "prereg_sha256": psha, "prereg_block": block,
                "inputs": {k: p[k] for k in SHA_KEYS}, "tokenizer": tok.identity(), "files": entries,
                "candidates": spans, "candidate_of": {r["id"]: r["candidate_sha256"] for r in rows},
                "question": tok.encode(p["question_block"]), "sha256": {n: sha256(b) for n, b in out}}
    write_out("--out", args.out, out + [("manifest.json", json_bytes(manifest))])
    print("s1-read tokens: %d files, %d rows, %d candidates, %d tokens in %d blocks"
          % (len(entries), len(rows), len(spans), total, nblocks))
    return 0


# ---------------------------------------------------------------- read (R-5)

def load_tokens(tdir):
    """(manifest, its sha256, {file name: ids}) of a tokens directory: every file's sha256 is checked against the
    manifest first, then the manifest's own shape."""
    mdata = _bytes(os.path.join(tdir, "manifest.json"), "--tokens %s: manifest.json" % tdir)
    try:
        m = json.loads(mdata.decode("utf-8"))
        named = sorted(m["sha256"].items())
    except (RecursionError, ValueError, KeyError, TypeError, AttributeError) as e:
        raise Refused("--tokens %s: manifest.json: %s: %s" % (tdir, type(e).__name__, e))
    ids = {}
    for name, want in named:
        data = _bytes(os.path.join(tdir, name), "--tokens %s: %s" % (tdir, name))
        if sha256(data) != want:
            raise Refused("--tokens %s: %s: its sha256 is not the manifest's" % (tdir, name))
        ids[name] = ids_of(data, name)
    try:
        bad = None if m["version"] == TOKENS_VERSION else "its version"
        size = len(ids["candidates.tok"])
        for h, s in m["candidates"].items():
            if not (type(s["offset"]) is int and type(s["length"]) is int and s["offset"] >= 0 and s["length"] > 0
                    and s["offset"] + s["length"] <= size):
                bad = "the span of candidate %s" % h
        for e in m["files"]:
            if m["sha256"].get(e["file"]) != e["sha256"] or len(ids[e["file"]]) != e["tokens"]:
                bad = "file %s" % e["file"]
            for rid, pos in e["rows"]:
                if not (type(pos) is int and 0 < pos <= e["tokens"]) or m["candidate_of"][rid] not in m["candidates"]:
                    bad = "row %s" % rid
        window = m["prereg_block"]["features"]["short_window_tokens"]
        if not (type(window) is int and window > 0) or not (m["question"] and all(type(i) is int for i in m["question"])):
            bad = "its window or question"
    except (KeyError, TypeError, ValueError, AttributeError) as e:
        raise Refused("--tokens %s: manifest.json: %s: %s" % (tdir, type(e).__name__, e))
    if bad:
        raise Refused("--tokens %s: manifest.json: %s is not a %s manifest's" % (tdir, bad, TOKENS_VERSION))
    return m, sha256(mdata), ids


def forward(backend, state, ids, segment):
    """`ids` read on `state` in forwards of at most `segment` ids: (state, the readout at the last id, forwards)."""
    n, out = 0, None
    for i in range(0, len(ids), segment):
        state, out = backend.read(state, ids[i:i + segment])
        n += 1
    return state, out, n


def read_file(backend, ids, rows, cand, q_ids, window, segment):
    """({row id: {array: readout}}, forwards) of one file's rows [(id, position, candidate sha256)] (R-5)."""
    out, n, state, at = {}, 0, backend.zero(), 0
    for pos in sorted({pos for _rid, pos, _h in rows}):
        state, s, k = forward(backend, state, ids[at:pos], segment)       # the last forward ends at the position
        at, n = pos, n + k
        for rid, _pos, h in sorted(r for r in rows if r[1] == pos):       # rows at one position share s
            cp = backend.copy(state)
            cp, c_ctx = backend.read(cp, cand[h])
            cp, q_ctx = backend.read(cp, q_ids)
            del cp                                                         # the copy is dropped; the original goes on
            out[rid] = {"s": s, "c_ctx": c_ctx, "q_ctx": q_ctx}
            n += 2
    for rid, pos, h in rows:
        w, s_w, k = forward(backend, backend.zero(), ids[max(0, pos - window):pos], segment)
        w, c_w = backend.read(w, cand[h])
        w, q_w = backend.read(w, q_ids)
        out[rid].update(s_w=s_w, c_ctx_w=c_w, q_ctx_w=q_w)
        n += k + 2
    return out, n


def open_work(work, binding):
    """--work: new or empty (it then gets this run's work.json), or the work directory of an earlier run with the same
    binding (tokens, backend, segment): the one non-empty --work taken (R-5, R-9)."""
    path = os.path.join(work, WORK_JSON)
    if os.path.isfile(path):
        try:
            held = json.loads(_bytes(path, "--work %s: %s" % (work, WORK_JSON)).decode("utf-8"))
        except (RecursionError, ValueError) as e:
            raise Refused("--work %s: %s: %s" % (work, WORK_JSON, e))
        if held != binding:
            raise Refused("--work %s holds another run's work: its %s is not this run's" % (work, WORK_JSON))
        check_out("--work", os.path.join(work, WORK_JSON + ".next"))       # D-10's git rule over what this run adds
        return
    check_out("--work", work)
    write_out("--work", work, [(WORK_JSON, json_bytes(binding))])


def load_record(work, k, entry, rids):
    """(readouts, forwards) of file k that a run with this --work finished, or None when it finished none."""
    path = os.path.join(work, str(k))
    if not os.path.lexists(path):
        return None
    try:
        index, mats = F.read(path)
    except F.Refused as e:
        raise Refused("--work %s: the record of %s: %s" % (work, entry["src"], e))
    meta = index["meta"]
    if not (isinstance(meta, dict) and meta.get("src") == entry["src"] and meta.get("sha256") == entry["sha256"]
            and index["rows"] == sorted(rids) and type(meta.get("forwards")) is int):
        raise Refused("--work %s: the record of %s is not this file's" % (work, entry["src"]))
    return {rid: {n: mats[n].get(rid) for n in F.ROW_ARRAYS} for rid in rids}, meta["forwards"]


def save_record(work, k, entry, vecs, forwards, dim):
    """File k's readouts under --work, written whole as <k>.part and then renamed <k> (features.write's format)."""
    part = os.path.join(work, "%d.part" % k)
    rids = sorted(vecs)
    arrays = {n: [vecs[r][n] for r in rids] for n in F.ROW_ARRAYS}
    arrays.update((n, []) for n in F.FREE_ARRAYS)
    try:
        if os.path.lexists(part):          # a run stopped while it wrote this record
            shutil.rmtree(part)
        F.write(part, rids, [], dim, arrays,
                {"version": WORK_VERSION, "src": entry["src"], "sha256": entry["sha256"], "forwards": forwards})
        os.rename(part, os.path.join(work, str(k)))
    except (F.Refused, OSError) as e:
        raise Refused("--work %s: %s" % (work, e))


def cmd_read(args):
    if args.segment < 1:
        raise Refused("--segment must be a positive int")
    _named("--out", args.out)                  # features.write's own rules, checked before the run (a GPU window)
    if os.path.lexists(args.out) and (not os.path.isdir(args.out) or os.path.islink(args.out) or os.listdir(args.out)):
        raise Refused("--out %s must not exist, or be an empty directory" % args.out)
    if args.work:
        _named("--work", args.work)
    m, msha, ids = load_tokens(args.tokens)
    only = set(args.only or [])
    unknown = sorted(only - {e["src"] for e in m["files"]})
    if unknown:
        raise Refused("--only %s: the tokens hold no such file" % unknown[0])
    cand = {h: ids["candidates.tok"][s["offset"]:s["offset"] + s["length"]] for h, s in m["candidates"].items()}
    q_ids, window = m["question"], m["prereg_block"]["features"]["short_window_tokens"]
    backend = make_backend(args.backend, args.model)
    ident = backend.identity()
    if args.work:
        open_work(args.work, {"version": WORK_VERSION, "tokens_manifest_sha256": msha, "backend": ident,
                              "segment": args.segment})
    vecs, counts, resumed, timings, t_all = {}, {"tokens": {}, "forwards": 0, "rows": 0}, 0, {}, time.monotonic()
    for k, e in enumerate(m["files"]):
        if only and e["src"] not in only:
            continue
        rows = [(rid, pos, m["candidate_of"][rid]) for rid, pos in e["rows"]]
        t0 = time.monotonic()
        got = load_record(args.work, k, e, [r[0] for r in rows]) if args.work else None
        was = got is not None
        if not was:
            got = read_file(backend, ids[e["file"]], rows, cand, q_ids, window, args.segment)
            if args.work:
                save_record(args.work, k, e, got[0], got[1], backend.dim())
        resumed += was
        vecs.update(got[0])
        counts["tokens"][e["src"]] = e["tokens"]
        counts["forwards"] += got[1]
        counts["rows"] += len(rows)
        timings[str(k)] = {"seconds": round(time.monotonic() - t0, 3), "resumed": was}
        print("s1-read: file %d: %s in %.3f s" % (k, "resumed" if was else "read", timings[str(k)]["seconds"]),
              file=sys.stderr)
    done = sorted(vecs)
    reads = {m["candidate_of"][rid]: cand[m["candidate_of"][rid]] for rid in done}    # per distinct candidate
    free = sorted(reads)
    t0, arrays = time.monotonic(), {n: [vecs[r][n] for r in done] for n in F.ROW_ARRAYS}
    arrays.update(c_free=[], q_free=[])
    for h in free:
        st, c_free = backend.read(backend.zero(), reads[h])
        st, q_free = backend.read(st, q_ids)
        arrays["c_free"].append(c_free)
        arrays["q_free"].append(q_free)
        counts["forwards"] += 2
    meta = {"backend": ident, "tokens_manifest_sha256": msha, "prereg_sha256": m["prereg_sha256"],
            "prereg_block": m["prereg_block"], "counts": counts}
    try:
        F.write(args.out, done, free, backend.dim(), arrays, meta)
    except F.Refused as e:
        raise Refused("--out %s: %s" % (args.out, e))
    timings.update(candidates={"seconds": round(time.monotonic() - t0, 3)},
                   total={"seconds": round(time.monotonic() - t_all, 3)})
    print("s1-read: candidates in %.3f s; %.3f s in all" % (timings["candidates"]["seconds"],
                                                            timings["total"]["seconds"]), file=sys.stderr)
    if args.work:
        try:
            _put(args.work, TIMINGS, json_bytes(timings))
        except OSError as e:
            raise Refused("--work %s: %s" % (args.work, e))
    print("s1-read read: %d files (%d resumed), %d rows, %d candidates, %d forwards, %d tokens"
          % (len(counts["tokens"]), resumed, counts["rows"], len(free), counts["forwards"],
             sum(counts["tokens"].values())))
    return 0


# ---------------------------------------------------------------- tails (R-7), compare and smoke (R-8)

def cmd_tails(args):
    check_out("--out", args.out)
    psha, _block, p = read_prereg(args.prereg)
    rows, files = read_inputs(args.view, args.export, p)
    n, lines = p["state_tail_chars"], []
    for r in sorted(rows, key=lambda r: r["id"]):
        text = files[r["src"]][0]
        lines.append(C.dumps({"id": r["id"], "tail": text[max(0, r["state_end"] - n):r["state_end"]]}) + "\n")
    data = "".join(lines).encode("utf-8")
    manifest = dict({k: p[k] for k in SHA_KEYS}, prereg_sha256=psha, count=len(lines), tails_sha256=sha256(data))
    write_out("--out", args.out, [("tails.jsonl", data), ("manifest.json", json_bytes(manifest))])
    print("s1-read tails: %d rows, %d characters at most each" % (len(lines), n))
    return 0


def cmd_compare(args):
    try:
        ia, a = F.read(args.a)
        ib, b = F.read(args.b)
    except F.Refused as e:
        raise Refused(str(e))
    if ia["dim"] != ib["dim"]:
        raise Refused("the two runs' dims differ: %d and %d" % (ia["dim"], ib["dim"]))
    arrays, every = {}, []
    for name in F.ROW_ARRAYS + F.FREE_ARRAYS:
        cos = [cosine(a[name].get(k), b[name].get(k)) for k in sorted(set(a[name].keys) & set(b[name].keys))]
        every += cos
        arrays[name] = {"n": len(cos), "min": min(cos) if cos else None,
                        "median": statistics.median(cos) if cos else None, "max": max(cos) if cos else None}
    if not every:
        raise Refused("the two runs hold no row and no candidate in common")
    print(json.dumps({"arrays": arrays, "min": min(every)}, sort_keys=True))
    return 0


def cmd_smoke(args):
    if os.path.lexists(args.out):
        raise Refused("--out %s exists: a smoke result is never written over another" % args.out)
    backend = make_backend(args.backend, args.model)
    tok = tokenizer("fake" if args.backend == "fake" else "hf", args.model)
    a, b, c = (tok.encode(t) for t in SMOKE)
    st, _ = backend.read(backend.zero(), a)
    cp, _ = backend.read(backend.copy(st), c)             # (1) C on a copy, then dropped: B's readout is A then B's
    del cp
    _, after_copy = backend.read(st, b)
    st, _ = backend.read(backend.zero(), a)
    _, plain = backend.read(st, b)
    _, whole = backend.read(backend.zero(), a + b)        # (2) A and B in one read against A then B
    split = cosine(whole, plain)
    checks = {"copy": {"ran": True, "pass": after_copy == plain},
              "split": {"ran": True, "cosine": split, "min": SPLIT_MIN, "pass": split >= SPLIT_MIN}}
    if backend.name == "fla":                             # (3) the readout is the hidden state model.lm_head reads
        mine, theirs = backend.head(a + b)
        cos = cosine(mine, theirs)
        same = max(range(len(mine)), key=mine.__getitem__) == max(range(len(theirs)), key=theirs.__getitem__)
        checks["head"] = {"ran": True, "argmax_equal": same, "cosine": cos, "min": HEAD_MIN,
                          "pass": same and cos >= HEAD_MIN}
    else:
        checks["head"] = {"ran": False}
    ok = all(v["pass"] for v in checks.values() if v["ran"])
    result = {"backend": backend.identity(), "tokenizer": tok.identity(), "checks": checks, "pass": ok}
    try:
        with open(args.out, "xb") as fh:
            fh.write(json_bytes(result))
    except OSError as e:
        raise Refused("--out %s: %s" % (args.out, e))
    print("s1-read smoke: %s; %s" % (", ".join("%s %s" % (n, ("pass" if v["pass"] else "FAIL") if v["ran"] else
                                                          "not run") for n, v in sorted(checks.items())),
                                     "pass" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("tokens", "tails"):
        s = sub.add_parser(name)
        s.add_argument("--view", required=True, help="the view of the S1 dataset (view.jsonl, summary.json)")
        s.add_argument("--export", required=True, help="the session export the view was made over")
        s.add_argument("--prereg", required=True, help="the pre-registration file (its only ```json block)")
        s.add_argument("--out", required=True, help="a new or empty directory, outside git, named without '..'")
        if name == "tokens":
            s.add_argument("--tokenizer", required=True, choices=("fake", "hf"))
            s.add_argument("--model", help="the checkpoint directory (hf)")
    s = sub.add_parser("read")
    s.add_argument("--tokens", required=True, help="the output of `read.py tokens`")
    s.add_argument("--backend", required=True, choices=("fake", "fla"))
    s.add_argument("--model", help="the checkpoint directory (fla)")
    s.add_argument("--only", action="append", help="read only this src (repeatable; the --only=SRC form)")
    s.add_argument("--segment", type=int, default=SEGMENT, help="tokens per forward, at most (default %(default)s)")
    s.add_argument("--work", help="a directory for each finished file's readouts; a later run resumes from it")
    s.add_argument("--out", required=True, help="the features directory (new or empty)")
    s = sub.add_parser("compare")
    s.add_argument("a", help="a features directory")
    s.add_argument("b", help="another features directory")
    s = sub.add_parser("smoke")
    s.add_argument("--backend", required=True, choices=("fake", "fla"))
    s.add_argument("--model", help="the checkpoint directory (fla)")
    s.add_argument("--out", required=True, help="the result file (JSON; must not exist)")
    args = ap.parse_args(argv)
    try:
        return {"tokens": cmd_tokens, "read": cmd_read, "tails": cmd_tails, "compare": cmd_compare,
                "smoke": cmd_smoke}[args.cmd](args)
    except Refused as e:
        print("s1-read: refused: %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
