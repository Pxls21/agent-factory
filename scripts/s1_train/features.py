#!/usr/bin/env python3
"""features.py — the one on-disk form of the S1 features (task #441; tasks/s1-heads-breakdown.md decisions 3 and 8;
docs/research/findings/s1-train/PREREG-441.md §2). scripts/s1_train/read.py writes it; scripts/s1_train/evaluate.py
reads it. Neither re-implements it.

A features directory holds `index.json` and one raw file per array: float32, little-endian, row-major, shape
[len(keys), dim]. A row array (ROW_ARRAYS) is keyed by the sorted view row ids, a free array (FREE_ARRAYS) by the sorted
candidate sha256s. The index names each array's file, its key list and the sha256 of the file's bytes. `read` refuses
a file whose bytes, size or values do not match: every value must be finite (a NaN compares false with everything, so
it would pass a threshold silently). No numpy: CI and the sandbox's main Python lack it, and the format needs none.

The same arrays give byte-identical files and index (no clock, no host path).
"""
import array
import hashlib
import json
import math
import os
import sys

VERSION = "s1-features-v1"
ROW_ARRAYS = ("s", "c_ctx", "q_ctx", "s_w", "c_ctx_w", "q_ctx_w")
FREE_ARRAYS = ("c_free", "q_free")
INDEX = "index.json"


class Refused(Exception):
    """An input or output the format does not accept; the reason is the message."""


def _f32(values):
    a = array.array("f", values)
    if a.itemsize != 4:
        raise Refused("this Python's array('f') is not 4 bytes")
    if sys.byteorder != "little":
        a.byteswap()
    return a


def _keys_ok(name, keys):
    if not isinstance(keys, list) or not all(isinstance(k, str) and k for k in keys):
        raise Refused("%s: the keys must be a list of non-empty strings" % name)
    if keys != sorted(set(keys)):
        raise Refused("%s: the keys must be sorted and distinct" % name)


def write(out_dir, rows, free, dim, arrays, meta):
    """Write the arrays under out_dir (missing or empty) and return the index. `arrays` maps every name of ROW_ARRAYS
    and FREE_ARRAYS to a list of vectors in key order (rows for a row array, free for a free array); `meta` is any
    JSON object (the backend's identity, counts, the pre-registration block the read used)."""
    _keys_ok("rows", rows)
    _keys_ok("free", free)
    if not isinstance(dim, int) or isinstance(dim, bool) or dim < 1:
        raise Refused("dim must be a positive int")
    if set(arrays) != set(ROW_ARRAYS + FREE_ARRAYS):
        raise Refused("arrays must be exactly %s" % ", ".join(ROW_ARRAYS + FREE_ARRAYS))
    # AF-AP-261: os.makedirs below creates missing parts, and a missing part before a '..' changes what the '..' names,
    # so a check on the text would not name the directory written. Without a '..' it does.
    if not out_dir or ".." in str(out_dir).replace("\\", "/").split("/"):
        raise Refused("%r: the output must be named, and without a '..' part" % (out_dir,))
    if os.path.lexists(out_dir) and (not os.path.isdir(out_dir) or os.path.islink(out_dir) or os.listdir(out_dir)):
        raise Refused("%s: the output must not exist, or be an empty directory" % out_dir)
    blobs = {}
    for name in ROW_ARRAYS + FREE_ARRAYS:
        keys = rows if name in ROW_ARRAYS else free
        vecs = arrays[name]
        if len(vecs) != len(keys):
            raise Refused("%s: %d vectors for %d keys" % (name, len(vecs), len(keys)))
        flat = []
        for i, v in enumerate(vecs):
            if len(v) != dim:
                raise Refused("%s[%d]: %d values, not %d" % (name, i, len(v), dim))
            flat.extend(v)
        a = _f32(flat)
        if not all(math.isfinite(x) for x in a):
            raise Refused("%s: a value is not finite" % name)
        blobs[name] = a.tobytes()
    index = {"version": VERSION, "dim": dim, "rows": rows, "free": free, "meta": meta,
             "arrays": {n: {"file": n + ".f32", "keys": "rows" if n in ROW_ARRAYS else "free",
                            "sha256": hashlib.sha256(b).hexdigest()} for n, b in blobs.items()}}
    os.makedirs(out_dir, exist_ok=True)
    for name, b in blobs.items():
        with open(os.path.join(out_dir, name + ".f32"), "wb") as f:
            f.write(b)
    with open(os.path.join(out_dir, INDEX), "w", encoding="utf-8") as f:
        f.write(json.dumps(index, sort_keys=True, indent=1, ensure_ascii=False) + "\n")
    return index


class Matrix:
    """One array, read and checked: `keys`, `dim`, and `row(i)` (a list of floats)."""

    def __init__(self, keys, dim, values):
        self.keys, self.dim, self.values = keys, dim, values
        self.at = {k: i for i, k in enumerate(keys)}

    def row(self, i):
        return list(self.values[i * self.dim:(i + 1) * self.dim])

    def get(self, key):
        return self.row(self.at[key])


def read(in_dir):
    """(index, {name: Matrix}) of a features directory, every file checked against the index."""
    try:
        with open(os.path.join(in_dir, INDEX), encoding="utf-8") as f:
            index = json.load(f)
    except (OSError, ValueError) as e:
        raise Refused("%s: no readable %s (%s)" % (in_dir, INDEX, e))
    if not isinstance(index, dict) or index.get("version") != VERSION:
        raise Refused("%s: not a %s index" % (in_dir, VERSION))
    rows, free, dim = index.get("rows"), index.get("free"), index.get("dim")
    _keys_ok("rows", rows)
    _keys_ok("free", free)
    if not isinstance(dim, int) or isinstance(dim, bool) or dim < 1:
        raise Refused("dim must be a positive int")
    if not isinstance(index.get("arrays"), dict) or set(index["arrays"]) != set(ROW_ARRAYS + FREE_ARRAYS):
        raise Refused("the index must name exactly %s" % ", ".join(ROW_ARRAYS + FREE_ARRAYS))
    out = {}
    for name in ROW_ARRAYS + FREE_ARRAYS:
        entry = index["arrays"][name]
        want = "rows" if name in ROW_ARRAYS else "free"
        if not isinstance(entry, dict) or entry.get("file") != name + ".f32" or entry.get("keys") != want:
            raise Refused("%s: the index entry is not {file: %s.f32, keys: %s}" % (name, name, want))
        keys = rows if want == "rows" else free
        try:
            with open(os.path.join(in_dir, entry["file"]), "rb") as f:
                b = f.read()
        except OSError as e:
            raise Refused("%s: %s" % (name, e))
        if hashlib.sha256(b).hexdigest() != entry.get("sha256"):
            raise Refused("%s: the file's sha256 is not the index's" % name)
        if len(b) != 4 * dim * len(keys):
            raise Refused("%s: %d bytes, not %d" % (name, len(b), 4 * dim * len(keys)))
        a = array.array("f")
        a.frombytes(b)
        if sys.byteorder != "little":
            a.byteswap()
        if not all(math.isfinite(x) for x in a):
            raise Refused("%s: a value is not finite" % name)
        out[name] = Matrix(keys, dim, a)
    return index, out
