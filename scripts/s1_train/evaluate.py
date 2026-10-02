#!/usr/bin/env python3
"""evaluate.py — the one evaluator of the first S1 training (task #441; docs/research/findings/s1-train/PREREG-441.md
§3 to §5 and §8; brief tasks/briefs/jev-laya/S4-3-HEADS-brief.md E-1 and E-5 to E-9).

  evaluate.py run --prereg <file> --view <dir> --features <dir> --tails <dir> [--read-repeat <file>] [--twice]
                  --out <file>
  evaluate.py explore --config <name> --prereg <file> --view <dir> --features <dir> --tails <dir> --out <file>

Every number comes from the pre-registration's one ```json block (§8). The inputs are checked against it first (E-1);
a mismatch is refused with its reason (exit 3) before any fit runs. `run` cross-validates the configurations of §3
(scripts/s1_train/heads.py), chooses one by out-of-fold accuracy, scores it once on the held-out rows against the kind
rule (§4), runs the controls of §5 and writes one JSON record with the verdict. `explore` scores one named
configuration the same way and marks the record exploratory: no verdict, no void checks, no claims. The pure parts
(the block, the input checks, the thresholds, the metrics, McNemar, the verdict, the controls' permutations, the
record) run in any Python; the fits need torch. The record has sorted keys, no clock, no host path and no session
text; stdout gets one line.
"""
import argparse
import hashlib
import json
import math
import os
import random
import re
import sys
import types
from bisect import bisect_left, bisect_right
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from s1_train import features, heads  # noqa: E402

VERSION = "s1-eval-v1"
Refused = heads.Refused
FENCE = re.compile(r"```json\n(.*?)\n```", re.S)
# E-1: the keys of the block the features' read must share with this one; a difference elsewhere is recorded
BLOCK_KEYS = ("inputs", "rows", "features", "cv", "grid", "bar", "controls", "word_overlap")
TEST = "one-sided exact McNemar against the kind rule"   # §4: the only test this code implements
CLIP = 1e-7   # E-5: the log loss clips probabilities to [CLIP, 1 - CLIP]
CLAIMS = {"C2": "the session state helps", "C3": "the whole stream helps over a short window"}   # §5's words
# PREREG-441's STATUS line: a deviation outside §4, §5 and the grid of §3 is reported in the run's record. None is
# left: the pre-registration's 2026-10-02 amendment made §3 name the same-state mask that pair_loss applies (brief
# E-4). A later deviation is listed here.
DEVIATIONS = []


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def _read(path, what):
    try:
        with open(path, "rb") as f:
            return f.read()
    except OSError as e:
        raise Refused("%s: %s" % (what, e))


def _no_constant(name):
    raise ValueError("%s is not a JSON number here" % name)


def _json(raw, what):
    try:
        return json.loads(raw, parse_constant=_no_constant)
    except ValueError as e:
        raise Refused("%s: not valid JSON (%s)" % (what, e))


def _lines(raw, what):
    """A JSONL file's lines, split on "\\n" only: str.splitlines also breaks on U+2028, U+2029, U+0085 and \\x0b to
    \\x1e, which a JSON string may hold raw, so it would cut a line of session text in two (AF-AP-132)."""
    try:
        lines = raw.decode("utf-8").split("\n")
    except UnicodeDecodeError:
        raise Refused("%s is not UTF-8" % what)
    if lines[-1] == "":
        lines.pop()
    return lines


# ---------- the pre-registration's block ----------

def prereg_block(text):
    """The file's only fenced ```json block, parsed; none, two or invalid JSON are refused."""
    found = FENCE.findall(text)
    if len(found) != 1:
        raise Refused("prereg: %d fenced json blocks, not one" % len(found))
    block = _json(found[0], "prereg: the json block")
    if not isinstance(block, dict):
        raise Refused("prereg: the json block is not an object")
    return block


def _at(block, path):
    v = block
    for key in path.split("."):
        if not isinstance(v, dict) or key not in v:
            raise Refused("prereg: the block has no %s" % path)
        v = v[key]
    return v


def _need(block, path, ok, what):
    v = _at(block, path)
    if not ok(v):
        raise Refused("prereg: %s must be %s, not %r" % (path, what, v))
    return v


def _hex64(v):
    return isinstance(v, str) and re.fullmatch(r"[0-9a-f]{64}", v) is not None


def _alpha(v):
    return heads.is_real(v) and 0 < v < 1


def check_block(block):
    """Every number of the block this evaluator reads, of its type and domain; returns the configurations (§3)."""
    _need(block, "prereg", lambda v: isinstance(v, str) and v != "", "a non-empty string")
    for key in ("view_jsonl_sha256", "view_summary_sha256", "export_manifest_sha256"):
        _need(block, "inputs." + key, _hex64, "a sha256")
    for key in ("train", "train_yes", "heldout", "heldout_yes"):
        low = 1 if key in ("train", "heldout") else 0   # a split with no row has no score
        _need(block, "rows." + key, lambda v: heads.is_int(v, low), "an int >= %d" % low)
    _need(block, "cv.folds", lambda v: heads.is_int(v, 2), "an int >= 2")
    _need(block, "cv.seed", lambda v: heads.is_int(v, 0), "an int >= 0")
    _need(block, "cv.std_floor", lambda v: heads.is_real(v) and v > 0, "a positive number")
    _need(block, "bar.kind_rule_heldout_correct", lambda v: heads.is_int(v, 0), "an int >= 0")
    _need(block, "bar.heldout_rows", lambda v: heads.is_int(v, 0) and v == block["rows"]["heldout"], "rows.heldout")
    _need(block, "bar.alpha", _alpha, "in (0, 1)")
    _need(block, "bar.test", lambda v: v == TEST, repr(TEST))
    _need(block, "controls.C1_seeds", lambda v: isinstance(v, list) and v != [] and all(heads.is_int(s, 0) for s in v),
          "a list of ints >= 0")
    _need(block, "controls.C1_void_if_passing_seeds_at_least", lambda v: heads.is_int(v, 1), "an int >= 1")
    _need(block, "controls.C1b_seed", lambda v: heads.is_int(v, 0), "an int >= 0")
    _need(block, "controls.state_claim_alpha", _alpha, "in (0, 1)")
    _need(block, "controls.window_claim_alpha", _alpha, "in (0, 1)")
    _need(block, "determinism.read_repeat_cosine_min", heads.is_real, "a finite number")
    _need(block, "word_overlap.min_word_len", lambda v: heads.is_int(v, 1), "an int >= 1")
    return heads.configurations(_at(block, "grid"))


# ---------- the inputs (E-1) ----------

def load_view(view_dir, block):
    """The view's rows, checked: its sha256 is the block's, and its counts are the block's rows."""
    raw = _read(os.path.join(view_dir, "view.jsonl"), "view")
    if _sha(raw) != block["inputs"]["view_jsonl_sha256"]:
        raise Refused("view: view.jsonl's sha256 is not the block's inputs.view_jsonl_sha256")
    rows = {}
    for n, line in enumerate(_lines(raw, "view: view.jsonl"), 1):
        r = _json(line, "view: line %d" % n)
        if not (isinstance(r, dict) and isinstance(r.get("id"), str) and r["id"] and r.get("split") in ("train", "heldout")
                and isinstance(r.get("label"), bool) and isinstance(r.get("source"), str) and r["source"]
                and isinstance(r.get("time"), str) and isinstance(r.get("candidate"), str)
                and isinstance(r.get("candidate_sha256"), str) and r["candidate_sha256"]
                and "src" in r and "state_end" in r):
            raise Refused("view: line %d lacks a field of the view's shape" % n)
        if r["id"] in rows:
            raise Refused("view: id %s repeats" % r["id"])
        heads.when(r["time"])
        rows[r["id"]] = {"split": r["split"], "label": r["label"], "kind": r["source"], "time": r["time"],
                         "cand": r["candidate_sha256"], "state": json.dumps([r["src"], r["state_end"]], sort_keys=True),
                         "candidate": r["candidate"]}
    got = {"train": 0, "train_yes": 0, "heldout": 0, "heldout_yes": 0}
    for r in rows.values():
        got[r["split"]] += 1
        got[r["split"] + "_yes"] += 1 if r["label"] else 0
    for key in ("train", "train_yes", "heldout", "heldout_yes"):
        if got[key] != block["rows"][key]:
            raise Refused("view: %d %s rows, not the block's %d" % (got[key], key.replace("_", " "), block["rows"][key]))
    return rows, _sha(raw)


def load_features(features_dir, block, rows):
    """The features (features.read, which checks every byte); the block their read used is this one on BLOCK_KEYS,
    and every view row has a vector in every row array and its candidate one in both free arrays."""
    try:
        index, mats = features.read(features_dir)
    except features.Refused as e:
        raise Refused("features: %s" % e)
    meta = index.get("meta")
    used = meta.get("prereg_block") if isinstance(meta, dict) else None
    if not isinstance(used, dict):
        raise Refused("features: the index's meta has no prereg_block")
    for key in BLOCK_KEYS:
        if used.get(key) != block.get(key):
            raise Refused("features: meta.prereg_block differs from the block on %s" % key)
    for i in sorted(rows):
        for name in features.ROW_ARRAYS:
            if i not in mats[name].at:
                raise Refused("features: row %s has no vector in %s" % (i, name))
        for name in features.FREE_ARRAYS:
            if rows[i]["cand"] not in mats[name].at:
                raise Refused("features: the candidate of row %s has no vector in %s" % (i, name))
    cands = {r["cand"] for r in rows.values()}
    return mats, {"features_index_sha256": _sha(_read(os.path.join(features_dir, features.INDEX), "features")),
                  "features_prereg_sha256": meta.get("prereg_sha256"),
                  "features_block_differences": sorted(k for k in set(used) | set(block)
                                                       if k not in BLOCK_KEYS and used.get(k) != block.get(k)),
                  "features_extra_rows": sum(1 for k in mats["s"].keys if k not in rows),
                  "features_extra_candidates": sum(1 for k in mats["c_free"].keys if k not in cands)}


def load_tails(tails_dir, block, rows):
    """The tails, checked: the manifest's view, summary and export sha256s are the block's, its tails_sha256 is its
    file's own and its count is the view's; tails.jsonl holds one {"id", "tail"} per view row, sorted by id."""
    mraw = _read(os.path.join(tails_dir, "manifest.json"), "tails")
    manifest = _json(mraw, "tails: manifest.json")
    if not isinstance(manifest, dict):
        raise Refused("tails: manifest.json is not an object")
    for key in ("view_jsonl_sha256", "view_summary_sha256", "export_manifest_sha256"):
        if manifest.get(key) != block["inputs"][key]:
            raise Refused("tails: the manifest's %s is not the block's" % key)
    traw = _read(os.path.join(tails_dir, "tails.jsonl"), "tails")
    if _sha(traw) != manifest.get("tails_sha256"):
        raise Refused("tails: tails.jsonl's sha256 is not the manifest's tails_sha256")
    if not heads.is_int(manifest.get("count"), 0) or manifest["count"] != len(rows):
        raise Refused("tails: the manifest's count %r is not the view's %d rows" % (manifest.get("count"), len(rows)))
    tails, ids = {}, []
    for n, line in enumerate(_lines(traw, "tails: tails.jsonl"), 1):
        t = _json(line, "tails: line %d" % n)
        if not (isinstance(t, dict) and isinstance(t.get("id"), str) and isinstance(t.get("tail"), str)):
            raise Refused("tails: line %d is not {\"id\", \"tail\"}" % n)
        tails[t["id"]] = t["tail"]
        ids.append(t["id"])
    if ids != sorted(rows):
        raise Refused("tails: the ids of tails.jsonl are not the view's, sorted")
    return tails, {"tails_manifest_sha256": _sha(mraw), "tails_jsonl_sha256": _sha(traw),
                   "tails_prereg_sha256": manifest.get("prereg_sha256")}


def load_read_repeat(path):
    """`read.py compare`'s output, {"arrays": {...}, "min": ...}: its sha256 and its min (finite)."""
    raw = _read(path, "read repeat")
    doc = _json(raw, "read repeat")
    if not (isinstance(doc, dict) and isinstance(doc.get("arrays"), dict) and heads.is_real(doc.get("min"))):
        raise Refused("read repeat: not {\"arrays\": {...}, \"min\": <a finite number>}")
    return {"sha256": _sha(raw), "min": doc["min"]}


def kind_rule(rows):
    """§4: each kind's majority label on the training rows; a tie is refused (E-1)."""
    counts = {}
    for i in sorted(rows):
        if rows[i]["split"] == "train":
            c = counts.setdefault(rows[i]["kind"], [0, 0])
            c[1 if rows[i]["label"] else 0] += 1
    rule = {}
    for kind in sorted(counts):
        no, yes = counts[kind]
        if yes == no:
            raise Refused("kind rule: kind %s has %d yes and %d no training rows (a tie)" % (kind, yes, no))
        rule[kind] = yes > no
    return rule


def words(text, n):
    """E-6: the set of re.findall(r"[a-z0-9_]{n,}", text.lower())."""
    return set(re.findall(r"[a-z0-9_]{%d,}" % n, text.lower()))


def jaccard(a, b):
    """|a & b| / |a | b|; two empty sets give 0 (§4 does not say)."""
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def load(prereg, view, feats, tails, read_repeat=None):
    """E-1: every input checked before a fit runs; returns what a run reads."""
    raw = _read(prereg, "prereg")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise Refused("prereg: not UTF-8")
    block = prereg_block(text)
    configs = check_block(block)
    rows, view_sha = load_view(view, block)
    mats, info = load_features(feats, block, rows)
    tail, tinfo = load_tails(tails, block, rows)
    info.update(tinfo, prereg_sha256=_sha(raw), view_jsonl_sha256=view_sha)
    rule = kind_rule(rows)
    heldout = [i for i in sorted(rows) if rows[i]["split"] == "heldout"]
    for i in heldout:
        if rows[i]["kind"] not in rule:
            raise Refused("kind rule: held-out row %s is of kind %s, which has no training row" % (i, rows[i]["kind"]))
    right = sum(1 for i in heldout if rule[rows[i]["kind"]] == rows[i]["label"])
    if right != block["bar"]["kind_rule_heldout_correct"]:
        raise Refused("kind rule: right on %d of %d held-out rows, not the block's %d"
                      % (right, len(heldout), block["bar"]["kind_rule_heldout_correct"]))
    rr = None if read_repeat is None else load_read_repeat(read_repeat)
    info["read_repeat_sha256"] = None if rr is None else rr["sha256"]
    cv = block["cv"]
    n = block["word_overlap"]["min_word_len"]
    return types.SimpleNamespace(
        block=block, configs=configs, rows=rows, rule=rule, info=info, read_repeat=rr,
        data=heads.Data(rows, mats, cv["folds"], cv["seed"], cv["std_floor"]),
        overlap={i: jaccard(words(rows[i]["candidate"], n), words(tail[i], n)) for i in sorted(rows)})


# ---------- the metrics (E-5) ----------

def threshold(probs, labels):
    """§3: the τ that maximizes accuracy (a row is yes when its probability is at least τ) over these rows. The
    candidates are 0, 1 and the midpoints between the sorted distinct probabilities; a tie goes to the τ closest to
    0.5, and a tie between two equally close (§3 does not say) to the smaller. Returns (τ, the rows right)."""
    distinct = sorted(set(probs))
    cands = {0.0, 1.0}
    cands.update((x + y) / 2 for x, y in zip(distinct, distinct[1:]))
    yes = sorted(p for p, y in zip(probs, labels) if y)
    no = sorted(p for p, y in zip(probs, labels) if not y)
    best = min((-(len(yes) - bisect_left(yes, t) + bisect_left(no, t)), abs(t - 0.5), t) for t in cands)
    return best[2], -best[0]


def log_loss(probs, labels):
    """E-5: the mean of -ln P(the label), each probability clipped to [CLIP, 1 - CLIP]."""
    total = math.fsum(-math.log(min(max(p, CLIP), 1 - CLIP) if y else 1 - min(max(p, CLIP), 1 - CLIP))
                      for p, y in zip(probs, labels))
    return total / len(probs)


def auc(scores, labels):
    """Mann-Whitney: the share of (yes, no) pairs the yes row scores higher, a tie counting one half; None without
    both classes."""
    no = sorted(s for s, y in zip(scores, labels) if not y)
    yes = [s for s, y in zip(scores, labels) if y]
    if not yes or not no:
        return None
    twice = sum(2 * bisect_left(no, s) + (bisect_right(no, s) - bisect_left(no, s)) for s in yes)
    return twice / (2 * len(yes) * len(no))


def metrics(ids, labels, kinds, scores, called, hard):
    """E-5 over `ids`: accuracy, balanced accuracy (the mean of the yes and no rates), AUC, log loss (null for a 0/1
    baseline, `hard`), the confusion counts and accuracy per kind."""
    tp = fp = tn = fn = 0
    per = {}
    for i in ids:
        y, c = labels[i], called[i]
        if y and c:
            tp += 1
        elif y:
            fn += 1
        elif c:
            fp += 1
        else:
            tn += 1
        k = per.setdefault(kinds[i], [0, 0])
        k[0] += 1
        k[1] += 1 if y == c else 0
    right = tp + tn
    return {"rows": len(ids), "right": right, "accuracy": right / len(ids) if ids else None,
            "balanced_accuracy": (tp / (tp + fn) + tn / (tn + fp)) / 2 if tp + fn and tn + fp else None,
            "auc": auc([scores[i] for i in ids], [labels[i] for i in ids]),
            "log_loss": None if hard else log_loss([scores[i] for i in ids], [labels[i] for i in ids]),
            "confusion": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
            "per_kind": {k: {"rows": v[0], "right": v[1], "accuracy": v[1] / v[0]} for k, v in sorted(per.items())}}


def mcnemar(a_right, b_right):
    """E-5: b = rows a gets right and b wrong, c = the reverse, n = b + c; the exact binomial tails at 1/2 in integers:
    one-sided P(X >= b), two-sided min(1, 2 min(P(X >= b), P(X <= b))); n = 0 gives 1 for both."""
    if len(a_right) != len(b_right):
        raise Refused("mcnemar: %d rows against %d" % (len(a_right), len(b_right)))
    b = sum(1 for x, y in zip(a_right, b_right) if x and not y)
    c = sum(1 for x, y in zip(a_right, b_right) if y and not x)
    n = b + c
    ge = Fraction(sum(math.comb(n, k) for k in range(b, n + 1)), 2 ** n)
    le = Fraction(sum(math.comb(n, k) for k in range(0, b + 1)), 2 ** n)
    return {"b": b, "c": c, "n": n, "p_one_sided": ge, "p_two_sided": min(Fraction(1), 2 * min(ge, le))}


def _mc(m, b_is):
    return {"b": m["b"], "c": m["c"], "n": m["n"], "b_is": b_is,
            "p_one_sided": float(m["p_one_sided"]), "p_two_sided": float(m["p_two_sided"])}


def _frac(x):
    return Fraction(repr(x))   # the decimal the block wrote: 0.05 is 1/20, not the double nearest it


def meets_pass_rule(block, right, mc):
    """§4's PASS rule: right on more than the kind rule's count AND the one-sided p below alpha."""
    bar = block["bar"]
    return right > bar["kind_rule_heldout_correct"] and mc["p_one_sided"] < _frac(bar["alpha"])


def verdict(block, right, mc, c1_passing, read_repeat_min, twice):
    """E-7: PASS, NOT SHOWN or FAILED from the counts and the one-sided p (§4); VOID when C1's rule fires, when the
    read-repeat min is below the block's, or when `twice` is False (the two records differ); otherwise INCOMPLETE when
    no read repeat was given. `twice` None is a run without --twice. Returns (verdict, the counts' outcome, reasons)."""
    if right <= block["bar"]["kind_rule_heldout_correct"]:
        counts = "FAILED"
    else:
        counts = "PASS" if meets_pass_rule(block, right, mc) else "NOT SHOWN"
    controls, void = block["controls"], []
    if c1_passing >= controls["C1_void_if_passing_seeds_at_least"]:
        void.append("C1: %d of %d seeds meet the PASS rule" % (c1_passing, len(controls["C1_seeds"])))
    floor = block["determinism"]["read_repeat_cosine_min"]
    if read_repeat_min is not None and read_repeat_min < floor:
        void.append("read repeat: the min cosine %r is below %r" % (read_repeat_min, floor))
    if twice is False:
        void.append("twice: the two records differ")
    if void:
        return "VOID", counts, void
    if read_repeat_min is None:
        return "INCOMPLETE", counts, []
    return counts, counts, []


# ---------- the choice, the scoring and the controls (§3 to §5, E-2, E-6, E-8) ----------

def choose(configs, results, labels):
    """§3's choice over the training rows (`labels` maps each to its label: the real one, or a control's): per
    configuration the threshold, the rows right and the log loss of its OUT-OF-FOLD probabilities; the most rows right,
    then the lower log loss, then the earlier configuration. Returns (the table, the chosen index)."""
    ids = sorted(labels)
    ys = [labels[i] for i in ids]
    table = []
    for cfg, res in zip(configs, results):
        ps = [res["oof"][i] for i in ids]
        tau, right = threshold(ps, ys)
        table.append({"name": cfg["name"], "family": cfg["family"], "head": cfg["head"], "threshold": tau,
                      "oof_right": right, "oof_accuracy": right / len(ids), "oof_log_loss": log_loss(ps, ys)})
    best = 0
    for j, row in enumerate(table):
        if (row["oof_right"], -row["oof_log_loss"]) > (table[best]["oof_right"], -table[best]["oof_log_loss"]):
            best = j
    return table, best


def judge(rows, ids, probs, tau):
    """One model's held-out score: a row is called yes when its probability is at least τ, the threshold its
    out-of-fold probabilities chose (§3). Returns (the metrics, right or not per row in `ids`' order)."""
    labels = {i: rows[i]["label"] for i in ids}
    called = {i: probs[i] >= tau for i in ids}
    m = metrics(ids, labels, {i: rows[i]["kind"] for i in ids}, probs, called, hard=False)
    m["threshold"] = tau
    return m, [called[i] == labels[i] for i in ids]


def permute_within_kind(rows, seed):
    """§5 C1 (E-8): the training labels permuted inside each kind: each kind's rows sorted by id, their labels shuffled
    by random.Random(seed)."""
    by_kind = {}
    for i in sorted(rows):
        if rows[i]["split"] == "train":
            by_kind.setdefault(rows[i]["kind"], []).append(i)
    out = {}
    for kind in sorted(by_kind):
        labels = [rows[i]["label"] for i in by_kind[kind]]
        random.Random(seed).shuffle(labels)
        out.update(zip(by_kind[kind], labels))
    return out


def permute_all(rows, seed):
    """§5 C1b: one permutation of all the training labels, the rows sorted by id, shuffled by random.Random(seed)."""
    ids = [i for i in sorted(rows) if rows[i]["split"] == "train"]
    labels = [rows[i]["label"] for i in ids]
    random.Random(seed).shuffle(labels)
    return dict(zip(ids, labels))


def _labels_note(rows, labels):
    yes = {}
    for i in sorted(labels):
        yes[rows[i]["kind"]] = yes.get(rows[i]["kind"], 0) + (1 if labels[i] else 0)
    return {"train_yes_by_kind": yes, "changed": sum(1 for i in labels if labels[i] != rows[i]["label"])}


def _procedure(inp, configs, labels):
    """§3 with `labels`: every configuration cross-validated and one chosen; its held-out probabilities."""
    results = [heads.cross_validate(cfg, inp.data, labels) for cfg in configs]
    table, j = choose(configs, results, labels)
    return table, j, results[j]


def _control(inp, labels, configs, rule_right, model_right, variant="full"):
    """A control through the same evaluator: the procedure (with `labels`, or one configuration on `variant`'s inputs),
    the held-out metrics, McNemar against the kind rule and against the full model."""
    if variant == "full":
        table, j, res = _procedure(inp, configs, labels)
    else:
        res = heads.cross_validate(configs[0], inp.data, labels, variant)
        table, j = choose(configs, [res], labels)
    m, right = judge(inp.rows, inp.data.heldout_ids, res["heldout"], table[j]["threshold"])
    vs_rule, vs_full = mcnemar(right, rule_right), mcnemar(model_right, right)
    return {"labels": _labels_note(inp.rows, labels), "configurations": table, "chosen": table[j]["name"],
            "heldout": m, "meets_pass_rule": meets_pass_rule(inp.block, m["right"], vs_rule),
            "vs_kind_rule": _mc(vs_rule, "this control right, the kind rule wrong"),
            "vs_full_model": _mc(vs_full, "the full model right, this control wrong")}, vs_full


def evaluate(inp, only=None):
    """One pass of §3 to §5 on checked inputs: the record without the void checks and the verdict (`run`), or, with
    `only` a configuration's name, the exploratory record (`explore`)."""
    block, rows, data = inp.block, inp.rows, inp.data
    configs = inp.configs
    if only is not None:
        configs = [c for c in configs if c["name"] == only]
        if not configs:
            raise Refused("explore: no configuration of the block is named %r" % only)
    ho = data.heldout_ids
    labels = {i: rows[i]["label"] for i in ho}
    kinds = {i: rows[i]["kind"] for i in ho}
    rule_called = {i: inp.rule[kinds[i]] for i in ho}
    rule_right = [rule_called[i] == labels[i] for i in ho]
    real = {i: rows[i]["label"] for i in data.train_ids}
    table, j, res = _procedure(inp, configs, real)
    chosen = configs[j]
    model, model_right = judge(rows, ho, res["heldout"], table[j]["threshold"])
    mc = mcnemar(model_right, rule_right)
    c = block["controls"]
    controls = {"C1": [], "C2": None, "C3": None}
    for seed in c["C1_seeds"]:
        rec, _ = _control(inp, permute_within_kind(rows, seed), configs, rule_right, model_right)
        controls["C1"].append(dict(rec, seed=seed))
    rec, _ = _control(inp, permute_all(rows, c["C1b_seed"]), configs, rule_right, model_right)
    controls["C1b"] = dict(rec, seed=c["C1b_seed"])
    beats = {}
    for name in ("C2", "C3"):
        controls[name], beats[name] = _control(inp, real, [chosen], rule_right, model_right, variant=name)
    wo_tau, _ = threshold([inp.overlap[i] for i in data.train_ids], [real[i] for i in data.train_ids])
    overlap = metrics(ho, labels, kinds, {i: inp.overlap[i] for i in ho}, {i: inp.overlap[i] >= wo_tau for i in ho},
                      hard=False)
    overlap["threshold"] = wo_tau
    folds = [0] * data.k
    for i in data.train_ids:
        folds[data.fold_of[i]] += 1
    record = {
        "version": VERSION, "exploratory": only is not None, "deviations": DEVIATIONS,
        "prereg": {"id": block["prereg"], "sha256": inp.info["prereg_sha256"]},
        "inputs": {k: v for k, v in inp.info.items() if k != "prereg_sha256"},
        "rows": dict(block["rows"], fold_sizes=folds),
        "kind_rule": {"rule": {k: "yes" if v else "no" for k, v in inp.rule.items()},
                      "heldout_right": sum(1 for r in rule_right if r)},
        "configurations": table, "chosen": chosen["name"], "model": model,
        "mcnemar_vs_kind_rule": _mc(mc, "the model right, the kind rule wrong"),
        "baselines": {"always_yes": metrics(ho, labels, kinds, {i: 1.0 for i in ho}, {i: True for i in ho}, hard=True),
                      "kind_rule": metrics(ho, labels, kinds, {i: 1.0 if rule_called[i] else 0.0 for i in ho},
                                           rule_called, hard=True),
                      "word_overlap": overlap},
        "controls": controls,
    }
    if only is None:
        record["claims"] = claims(block, beats)
    return record, mc


def claims(block, vs_full):
    """§5's two claims: "the session state helps" only when the full model beats C2, right on more of the rows where
    the two differ (b > c) with a two-sided exact McNemar p below state_claim_alpha; "the whole stream helps over a
    short window" the same against C3 with window_claim_alpha. `vs_full` maps C2 and C3 to McNemar(full, control)."""
    alpha = block["controls"]
    return [CLAIMS[name] for name, key in (("C2", "state_claim_alpha"), ("C3", "window_claim_alpha"))
            if vs_full[name]["b"] > vs_full[name]["c"] and vs_full[name]["p_two_sided"] < _frac(alpha[key])]


# ---------- the CLI (E-9) ----------

def _dumps(record):
    return json.dumps(record, sort_keys=True, indent=1, ensure_ascii=False, allow_nan=False) + "\n"


def _check_out(out):
    if not out or ".." in str(out).replace("\\", "/").split("/"):
        raise Refused("--out %r: the output must be named, and without a '..' part" % (out,))
    if os.path.lexists(out):
        raise Refused("--out %s: the output exists" % out)
    if not os.path.isdir(os.path.dirname(os.path.abspath(out))):
        raise Refused("--out %s: its directory does not exist" % out)


def run(args):
    """`run`: the record and its stdout line; with --twice the whole evaluation runs again and must give the same
    bytes (E-7)."""
    inp = load(args.prereg, args.view, args.features, args.tails, args.read_repeat)
    record, mc = evaluate(inp)
    twice = None
    if args.twice:
        again, _ = evaluate(load(args.prereg, args.view, args.features, args.tails, args.read_repeat))
        twice = _dumps(again) == _dumps(record)
    rr_min = None if inp.read_repeat is None else inp.read_repeat["min"]
    passing = sum(1 for r in record["controls"]["C1"] if r["meets_pass_rule"])
    v, counts, reasons = verdict(inp.block, record["model"]["right"], mc, passing, rr_min, twice)
    record.update(verdict=v, counts_outcome=counts, void_reasons=reasons, void_checks={
        "c1_seeds_meeting_pass_rule": passing, "read_repeat_min": rr_min,
        "twice": {None: "not run", True: "identical", False: "differ"}[twice]})
    line = ("evaluate run: VERDICT %s (counts %s): the model right on %d of %d held-out rows, the kind rule on %d; "
            "b %d, c %d, one-sided p %.6g; C1 seeds meeting the PASS rule %d of %d; read repeat min %s; twice %s"
            % (v, counts, record["model"]["right"], record["model"]["rows"], record["kind_rule"]["heldout_right"],
               mc["b"], mc["c"], float(mc["p_one_sided"]), passing, len(inp.block["controls"]["C1_seeds"]),
               "not given" if rr_min is None else repr(rr_min), record["void_checks"]["twice"]))
    return record, line


def explore(args):
    """`explore`: one named configuration, scored the same way; exploratory, no verdict, no claims."""
    record, mc = evaluate(load(args.prereg, args.view, args.features, args.tails), only=args.config)
    line = ("evaluate explore: EXPLORATORY %s: right on %d of %d held-out rows, the kind rule on %d; b %d, c %d, "
            "one-sided p %.6g" % (args.config, record["model"]["right"], record["model"]["rows"],
                                  record["kind_rule"]["heldout_right"], mc["b"], mc["c"], float(mc["p_one_sided"])))
    return record, line


def main(argv=None):
    ap = argparse.ArgumentParser(prog="evaluate.py", description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for cmd in ("run", "explore"):
        p = sub.add_parser(cmd)
        for flag in ("--prereg", "--view", "--features", "--tails", "--out"):
            p.add_argument(flag, required=True)
        if cmd == "run":
            p.add_argument("--read-repeat")
            p.add_argument("--twice", action="store_true")
        else:
            p.add_argument("--config", required=True)
    args = ap.parse_args(argv)
    try:
        _check_out(args.out)
        record, line = run(args) if args.cmd == "run" else explore(args)
        try:
            with open(args.out, "x", encoding="utf-8") as f:   # "x": never over a file made since the check
                f.write(_dumps(record))
        except OSError as e:
            raise Refused("--out %s: %s" % (args.out, e))
    except (Refused, heads.HeldOut) as e:
        print("evaluate: refused: %s" % e, file=sys.stderr)
        return 3
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
