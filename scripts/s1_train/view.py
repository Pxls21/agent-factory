#!/usr/bin/env python3
"""view.py — the RWKV view of the S1 dataset (task #444, S3-5 in tasks/laya-s3-breakdown.md; brief
tasks/briefs/jev-laya/S3-5-VIEW-brief.md).

For every source id of a frozen S1 build (scripts/laya_ft/build_s1.py): WHERE in its transcript's exported stream the
injection sits, WHAT the agent had seen before it (the state: the stream rendered by render.py, up to state_end) and
WHAT was injected (the candidate), with the build's label and split, never recomputed (D-4).

The carrier (D-2). A build source id is found where the ONE reader finds a stamp: s1_scores.injections_of, then
s1_scores.stamp_of over each text it returns, in a hook event (the attachment its text holds) and in a tool_result event
(read as the user record it came from: an is_error result whose text HOOK_ERROR_RX matches, a hook that denied the
tool). An id with two carriers, in one file or two, is not found (ambiguous), never guessed. The stamp's source must be
the build source's, else refused. The candidate is build_s1.chunk_of(stamped, whole) under the body rules without the
cap (render.clean); `whole`: the stamped text's last line is hook_context.request(id).

The state (D-3) ends where the run of hook events that holds the carrier begins (for a tool_result carrier, the run
right before it): the hooks of one call run in parallel and never see each other's output. The run's first event (the
carrier when no hook precedes it) is state_event; state_end is the offset where its block starts. The rendered text must
hold the id nowhere before state_end (text.find(id) >= state_end, else refused). For a PreToolUse or PostToolUse
carrier and a tool_result carrier, the tool call with the carrier's call id before state_event is its step
(step_event: that call's seq; counted step_found).

Inputs are verified before use (D-5): each export file's sha256 against its manifest entry; its xz data read whole by
one lzma.LZMADecompressor, refused when the stream is cut or bytes follow it (AF-AP-255); every line one event of the
export's schema, seq strictly increasing; a manifest that names a src or an output twice is refused (AF-AP-254). Each
split loads through common.load_dataset; its labels.jsonl matches its manifest's sha256; every row joins its label
(common.join_labels), whose target is [0.0, 1.0] (true) or [1.0, 0.0] (false); a source id sits in one row only.

usage: view.py --build <S1 build dir> --export <export dir> --out <dir>
  --out must not exist, or be an empty directory; keep it outside git (view.jsonl holds injected texts). Writes
  view.jsonl (one row per found id, sorted by src, state_event, id) and summary.json (counts and digests, no session
  text); the same inputs give byte-identical outputs (no clock, no host path, no randomness).
exit: 0 done (stdout: one line of counts); 2 refused (the reason on stderr; nothing written).
"""
import argparse
import hashlib
import json
import lzma
import os
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
ROOT = SCRIPTS.parent
sys.path.insert(0, str(SCRIPTS))
from s1_train import render as R  # noqa: E402  the ONE render
import hook_context as HC  # noqa: E402  the ONE stamp format
import s1_scores as S  # noqa: E402  the ONE reading of what a hook handed the model and of a stamp
from laya_ft import build_s1 as B  # noqa: E402
from laya_ft import common as C  # noqa: E402

VERSION = "s1-view-v1"
SPLITS = ("train", "heldout")
LABELS_FILE = "labels.jsonl"
BUILD_FILES = ("summary.json",) + tuple("%s/%s" % (s, f) for s in SPLITS
                                        for f in (C.DATASET_FILE, LABELS_FILE, C.MANIFEST_FILE))
EVENT_KEYS = frozenset(("seq", "src", "line", "ts", "role", "kind", "tool", "call_id", "text", "truncated", "outcome",
                        "model", "stop_reason"))
TARGETS = {(0.0, 1.0): True, (1.0, 0.0): False}     # the joined target over the options ["false", "true"]
STEP_EVENTS = ("PreToolUse", "PostToolUse")
# render.py, view.py and every module they import from scripts/, as a fresh interpreter loads them (the test measures
# it): laya_ft/common.py loads docs/research/findings/j2c-fulltext/j2c.py, which loads scripts/decide-harvest
CODE = ("scripts/decide-harvest", "scripts/hook_context.py", "scripts/laya_ft/__init__.py", "scripts/laya_ft/build_s1.py",
        "scripts/laya_ft/common.py", "scripts/laya_ft/fit.py", "scripts/laya_ft/recorded_labels.py",
        "scripts/s1_scores.py", "scripts/s1_train/__init__.py", "scripts/s1_train/render.py",
        "scripts/s1_train/view.py", "scripts/transcript_export.py")


class Refused(Exception):
    """An input failed a check: exit 2, nothing written."""


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _flag(value):
    return "true" if value else "false"


def _inc(counter, key):
    counter[key] = counter.get(key, 0) + 1


# ---------------------------------------------------------------- the build (D-4, D-5)

def read_build(bdir):
    """({source id: {item_id, split, label, source, time, chunk}}, {"commit", "files"}): every source id of the build's
    two splits, with its row's split and label as the build wrote them."""
    bdir = Path(bdir)
    try:
        raw = {name: (bdir / name).read_bytes() for name in BUILD_FILES}   # each file read once, here
        commit = json.loads(raw["summary.json"].decode("utf-8"))["commit"]
    except (OSError, ValueError, KeyError, TypeError) as e:
        raise Refused("the build: %s" % e)
    files = {name: C.sha256_hex(data) for name, data in raw.items()}
    ids = {}
    for split in SPLITS:
        name = split + "/"
        try:
            rows, manifest = C.load_dataset(bdir / split)
        except (C.DatasetError, C.HeldOutError, C.HeldOutLeak, OSError, ValueError, KeyError, TypeError) as e:
            raise Refused("the build's %s split: %s" % (split, e))
        try:                       # load_dataset read its two files again: the bytes it verified are the bytes hashed
            same = json.loads(raw[name + C.MANIFEST_FILE].decode("utf-8")) == manifest \
                and manifest["dataset"]["sha256"] == files[name + C.DATASET_FILE]
            labels_sha = manifest["labels"]["sha256"]
        except (ValueError, KeyError, TypeError) as e:
            raise Refused("the build's %s manifest: %s" % (split, e))
        if not same:
            raise Refused("the build's %s split changed while it was read" % split)
        if files[name + LABELS_FILE] != labels_sha:
            raise Refused("the build's %s%s does not match its manifest's sha256" % (name, LABELS_FILE))
        try:
            labels = {}
            for line in C.jsonl_lines(raw[name + LABELS_FILE].decode("utf-8")):
                rec = json.loads(line)
                if rec["key"] in labels:
                    raise Refused("the build's %s labels hold two records for %s" % (split, rec["key"]))
                labels[rec["key"]] = rec
            joined = {C.label_key(r["item_id"], r["question_id"]): t for r, t, _rec in C.join_labels(rows, labels)}
            for row in rows:
                key = C.label_key(row["item_id"], row["question_id"])
                if key not in joined:
                    raise Refused("the build's %s row %s has no label record" % (split, key))
                label = TARGETS.get(tuple(joined[key]))
                if label is None:
                    raise Refused("the build's %s row %s: its target %r is neither true nor false"
                                  % (split, key, joined[key]))
                for s in row["sources"]:
                    if not (isinstance(s, dict) and s.get("kind") == "injection" and isinstance(s.get("id"), str)):
                        raise Refused("the build's %s row %s holds a source that is not an injection" % (split, key))
                    if s["id"] in ids:
                        raise Refused("source id %s is in two rows of the build" % s["id"])
                    ids[s["id"]] = {"item_id": row["item_id"], "split": split, "label": label,
                                    "source": s.get("source"), "time": s.get("time"), "chunk": row["state"]["chunk"]}
        except (C.LabelError, ValueError, KeyError, TypeError) as e:
            raise Refused("the build's %s labels: %s" % (split, e))
    return ids, {"commit": commit, "files": files}


# ---------------------------------------------------------------- the export (D-5)

def read_manifest(edir):
    """(manifest, sources): the export's manifest.json and its entries, each naming one src, its output file and that
    file's sha256."""
    try:
        manifest = json.loads((Path(edir) / "manifest.json").read_bytes().decode("utf-8"))
        sources = list(manifest["sources"])
        whole = all(isinstance(s.get(k), str) for s in sources for k in ("src", "output", "output_sha256"))
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
        raise Refused("the export's manifest.json: %s" % e)
    if not whole:
        raise Refused("the export's manifest.json: an entry without src, output and output_sha256")
    for k in ("src", "output"):                # AF-AP-254: a file named twice would be read twice
        if len({s[k] for s in sources}) != len(sources):
            raise Refused("the export's manifest.json names the same %s twice" % k)
    return manifest, sources


def stream_events(edir, entry):
    """The events of one export file, verified: the sha256 of its bytes, one xz stream read whole with nothing after it,
    one event of the export's schema per line, seq strictly increasing."""
    src = entry["src"]
    try:
        data = (Path(edir) / entry["output"]).read_bytes()   # one read: the hash and the xz data are the same bytes
    except OSError as e:
        raise Refused("%s: %s" % (src, e))
    if hashlib.sha256(data).hexdigest() != entry["output_sha256"]:
        raise Refused("%s: its bytes do not match the manifest's output_sha256" % src)
    dec = lzma.LZMADecompressor()
    try:
        raw = dec.decompress(data)
    except lzma.LZMAError as e:
        raise Refused("%s: %s" % (src, e))
    if not dec.eof:
        raise Refused("%s: the xz stream is cut" % src)
    if dec.unused_data:                        # AF-AP-255: lzma.open drops such bytes silently
        raise Refused("%s: %d bytes follow the xz stream" % (src, len(dec.unused_data)))
    events, last = [], None
    try:
        for n, line in enumerate(C.jsonl_lines(raw.decode("utf-8")), 1):
            ev = json.loads(line)
            if not (isinstance(ev, dict) and set(ev) == EVENT_KEYS and isinstance(ev["text"], str)
                    and type(ev["seq"]) is int):
                raise Refused("%s: line %d is not an event of the export's schema" % (src, n))
            if last is not None and ev["seq"] <= last:
                raise Refused("%s: seq %d comes after seq %d" % (src, ev["seq"], last))
            last = ev["seq"]
            events.append(ev)
    except ValueError as e:
        raise Refused("%s: %s" % (src, e))
    return events


# ---------------------------------------------------------------- carriers, states, candidates (D-2, D-3)

def carriers(events, ids):
    """[(index, carrier kind, hook event, call id, (id, source, stamped))]: every stamp of a build id that the ONE reader
    finds in one file's events."""
    out = []
    for i, ev in enumerate(events):
        if ev["kind"] == "hook":
            try:
                a = json.loads(ev["text"])
            except ValueError:
                continue
            found, call_id = R.injections(a), (a.get("toolUseID") if isinstance(a, dict) else None)
        elif ev["kind"] == "tool_result":
            outcome = ev["outcome"] if isinstance(ev["outcome"], dict) else {}
            found = S.injections_of({"type": "user", "message": {"content": [
                {"type": "tool_result", "is_error": outcome.get("is_error"), "content": ev["text"]}]}})
            call_id = ev["call_id"]
        else:
            continue
        for kind, event, _tool, text, _cmd in found:
            st = S.stamp_of(kind, text)
            if st is not None and st[0] in ids:
                out.append((i, kind, event, call_id, st))
    return out


def facts_of(src, events, text, starts, ids):
    """[(id, facts)]: for each carrier of a build id in one file, where its state ends, its step and its candidate."""
    calls = {}
    for k, ev in enumerate(events):
        if ev["kind"] == "tool_call" and ev["call_id"] is not None:
            calls.setdefault(ev["call_id"], []).append(k)
    out = []
    for i, kind, event, call_id, (sid, source, stamped) in carriers(events, ids):
        j = i
        while j > 0 and events[j - 1]["kind"] == "hook":     # back over the run of hooks that holds the carrier
            j -= 1
        has_step = kind == "tool_result" or event in STEP_EVENTS
        before = [k for k in calls.get(call_id, []) if k < j] if has_step else []
        whole = stamped.rstrip("\n").split("\n")[-1] == HC.request(sid)
        out.append((sid, {"src": src, "carrier": kind, "hook_event": event, "call_id": call_id, "has_step": has_step,
                          "step_event": events[before[-1]]["seq"] if before else None,
                          "state_event": events[j]["seq"], "state_end": starts[j], "run_before": i - j,
                          "source": source, "ts": events[i]["ts"], "whole": whole,
                          "candidate": R.clean(B.chunk_of(stamped, whole)), "first": text.find(sid)}))
    return out


# ---------------------------------------------------------------- the view

def view(build, export):
    """(rows, summary, line): the view of a frozen S1 build over a session export."""
    ids, build_inputs = read_build(build)
    manifest, sources = read_manifest(export)
    rendered = {"cut": 0, "hook_unparsed": 0, "scrub_changed": 0, "events": 0, "blocks": 0, "chars": 0}
    streams, found = {}, {}
    for entry in sources:
        events = stream_events(export, entry)
        try:
            text, starts = R.render(events, rendered)
        except R.UnknownPair as e:
            raise Refused("%s: %s" % (entry["src"], e))
        blocks = sum(1 for a, b in zip(starts, starts[1:] + [len(text)]) if b > a)
        streams[entry["src"]] = {"events": len(events), "rendered": blocks, "chars": len(text),
                                 "sha256": sha256_text(text)}
        rendered["events"] += len(events)
        rendered["blocks"] += blocks
        rendered["chars"] += len(text)
        for sid, facts in facts_of(entry["src"], events, text, starts, ids):
            found.setdefault(sid, []).append(facts)

    counts = {"build_ids": len(ids), "found": 0, "not_found": {"ambiguous": 0, "not_in_export": 0}, "carrier": {},
              "hook_event": {}, "split": {s: 0 for s in SPLITS}, "label": {"false": 0, "true": 0},
              "step_found": {"false": 0, "true": 0}, "time_equal": {"false": 0, "true": 0},
              "candidate_vs_chunk": {"differs": 0, "equal": 0, "equal_prefix": 0}, "hook_run_before": {"0": 0, "1+": 0},
              "whole": {"false": 0, "true": 0}, "render": rendered}
    rows = []
    for sid in sorted(ids):
        got = found.get(sid, [])
        if len(got) != 1:
            counts["not_found"]["ambiguous" if got else "not_in_export"] += 1
            continue
        f, b = got[0], ids[sid]
        if f["source"] != b["source"]:
            raise Refused("%s: the stamp's source %r is not the build's %r" % (sid, f["source"], b["source"]))
        if f["first"] < f["state_end"]:
            raise Refused("%s: the rendered stream of %s holds the id %s" % (
                sid, f["src"], "nowhere" if f["first"] < 0 else "before its state ends (offset %d < %d)" % (
                    f["first"], f["state_end"])))
        chunk = R.newlines(b["chunk"]).strip()
        _inc(counts["carrier"], f["carrier"])
        _inc(counts["hook_event"], str(f["hook_event"]))
        counts["split"][b["split"]] += 1
        counts["label"][_flag(b["label"])] += 1
        if f["has_step"]:
            counts["step_found"][_flag(f["step_event"] is not None)] += 1
        counts["time_equal"][_flag(b["time"] == f["ts"])] += 1
        counts["candidate_vs_chunk"]["equal" if f["candidate"] == chunk else
                                     "equal_prefix" if f["candidate"].startswith(chunk) else "differs"] += 1
        counts["hook_run_before"]["0" if f["run_before"] == 0 else "1+"] += 1
        counts["whole"][_flag(f["whole"])] += 1
        rows.append({"id": sid, "item_id": b["item_id"], "split": b["split"], "label": b["label"],
                     "source": b["source"], "time": b["time"], "src": f["src"], "carrier": f["carrier"],
                     "hook_event": f["hook_event"], "call_id": f["call_id"], "step_event": f["step_event"],
                     "state_event": f["state_event"], "state_end": f["state_end"], "candidate": f["candidate"],
                     "candidate_sha256": sha256_text(f["candidate"])})
    counts["found"] = len(rows)
    rows.sort(key=lambda r: (r["src"], r["state_event"], r["id"]))
    summary = {"version": VERSION, "render": {"version": R.VERSION, "cap": R.CAP, "head": R.HEAD, "tail": R.TAIL},
               "code": {p: C.sha256_hex((ROOT / p).read_bytes()) for p in CODE},
               "inputs": {"build": build_inputs,
                          "export": {"export_id": manifest.get("export_id"), "code_sha256": manifest.get("code_sha256"),
                                     "files_verified": len(sources)}},
               "counts": counts, "streams": streams}
    line = ("s1-view: %d build ids, %d found, %d not in the export, %d ambiguous; %d files, %d events, %d blocks, "
            "%d characters rendered" % (len(ids), len(rows), counts["not_found"]["not_in_export"],
                                        counts["not_found"]["ambiguous"], len(sources), rendered["events"],
                                        rendered["blocks"], rendered["chars"]))
    return rows, summary, line


def check_out(out):
    """--out must not exist, or be an empty directory."""
    try:
        if os.path.lexists(out) and not (os.path.isdir(out) and not os.listdir(out)):
            raise Refused("--out %s exists and is not an empty directory" % out)
    except OSError as e:
        raise Refused("--out %s: %s" % (out, e))


def write(out, rows, summary):
    check_out(out)                             # again, after the inputs: nothing is written over another output
    os.makedirs(out, exist_ok=True)
    blobs = (("view.jsonl", "".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in rows)),
             ("summary.json", json.dumps(summary, indent=1, sort_keys=True) + "\n"))
    for name, blob in blobs:
        part = os.path.join(out, name + ".part")
        with open(part, "w", encoding="utf-8") as fh:
            fh.write(blob)
        os.replace(part, os.path.join(out, name))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("--build", required=True, help="a frozen S1 build: train/, heldout/ and summary.json")
    ap.add_argument("--export", required=True, help="a session export (scripts/session_export.py export)")
    ap.add_argument("--out", required=True, help="a new or empty directory, outside git")
    args = ap.parse_args(argv)
    try:
        check_out(args.out)
        rows, summary, line = view(args.build, args.export)
        write(args.out, rows, summary)
    except Refused as e:
        print("s1-view: refused: %s" % e, file=sys.stderr)
        return 2
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
