"""tests/test_s1_train_heads.py — the heads and the one evaluator of the first S1 training (scripts/s1_train/heads.py,
scripts/s1_train/evaluate.py; task #472; brief tasks/briefs/jev-laya/S4-3-HEADS-brief.md; the spec is
docs/research/findings/s1-train/PREREG-441.md).

Every fixture is SYNTHETIC and built here: a view of three kinds (one with fewer than five training rows, whose
held-out majority is not its training majority), features written with features.write (dimension 8), a tails
directory and a pre-registration whose block is the real one with the fixture's sha256s, row counts, kind-rule count
(computed by this file's own kind rule) and small epochs. The real features do not exist yet.

Two venues:
- this interpreter (no torch, as in CI): the block, the input checks, the folds, the thresholds, the metrics, McNemar
  against hand values, the verdict table, the controls' permutations, the word overlap; the failure paths, each
  asserting its reason (a prereg with no block or two, a view, count, features, tails or kind-rule mismatch, a held-out
  row handed to a fit, an --out that exists or climbs out with '..').
- the Laya venv (/root/venv-laya-probe/bin/python, torch on CPU) as subprocesses: a planted signal gives PASS, C1 does
  not fire, two runs and --twice give byte-identical records, no signal is never PASS, no read repeat is INCOMPLETE,
  explore, the held-out mean of the five fold models, the batch order, family A's loss against a hand oracle.
  The Laya venv is a DECLARED input of the sandbox venue (S0_01_VENUE, which scripts/test_summary.sh exports): absent
  there = FAIL. CI declares no venue, so those tests skip loudly; the PC's paths are not declared to this file either.
Security boundary: no held-out row reaches a fit's training or the fold it scores (HeldOut); no record or stdout line
carries session text or a host path; --out never overwrites and never takes a '..' part.
"""
import collections
import copy
import datetime
import hashlib
import json
import math
import os
import random
import subprocess
import sys
import types
from fractions import Fraction
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from s1_train import evaluate as EV  # noqa: E402
from s1_train import features as F  # noqa: E402
from s1_train import heads as H  # noqa: E402

PREREG = ROOT / "docs" / "research" / "findings" / "s1-train" / "PREREG-441.md"
EVALUATE = ROOT / "scripts" / "s1_train" / "evaluate.py"
LAYA_PY = "/root/venv-laya-probe/bin/python"
DIM = 8
# (kind, training rows, training yes, held-out rows, held-out yes): kind-c has fewer than five training rows, and its
# held-out majority (no) is not its training majority (yes), so a kind rule taken from the held-out rows is caught
KINDS = (("kind-a", 70, 20, 30, 10), ("kind-b", 70, 50, 30, 20), ("kind-c", 3, 2, 6, 2))
MARK = "zqxjmarkword"   # in every candidate and every tail: no output may carry it
VOCAB = ["Alpha", "beta", "gamma_ray", "delta9", "epsilon", "zeta", "eta", "theta", "iota", "kappa", "lam", "mu",
         "nu", "xi", "omicron", "pi", "rho", "sigma", "tau", "upsilon", "phi", "chi", "psi", "omega", "ab", "cd"]
STATE = "the session state helps"
WINDOW = "the whole stream helps over a short window"


def _sha(b):
    return hashlib.sha256(b).hexdigest()


def real_block():
    return EV.prereg_block(PREREG.read_text(encoding="utf-8"))


def oracle_kind_rule_right(rows):
    """This file's own kind rule (not EV.kind_rule): each kind's training majority, counted right on held-out rows."""
    n, yes = collections.Counter(), collections.Counter()
    for r in rows:
        if r["split"] == "train":
            n[r["source"]] += 1
            yes[r["source"]] += 1 if r["label"] else 0
    majority = {k: 2 * yes[k] > n[k] for k in n}
    return sum(1 for r in rows if r["split"] == "heldout" and majority[r["source"]] == r["label"])


def build(root, signal=True, seed=7, block_edit=None, features_block_edit=None, drop_feature_row=None):
    """A synthetic view, features, tails and pre-registration under `root`. With `signal`, dimension 0 of s, c_ctx and
    q_ctx carries the label (+-1.5, noise sd 0.6); every other value is noise (the window and free arrays too)."""
    rng = random.Random(seed)
    root.mkdir(parents=True)
    specs = []
    for kind, ntr, ytr, nho, yho in KINDS:
        specs += [(kind, "train", j < ytr) for j in range(ntr)] + [(kind, "heldout", j < yho) for j in range(nho)]
    rng.shuffle(specs)
    seconds = rng.sample(range(10 ** 6), len(specs))   # distinct, in an order that is not the id order
    t0 = datetime.datetime(2026, 9, 1, tzinfo=datetime.timezone.utc)
    # a raw U+2028 inside a JSON string: a reader that splits lines with str.splitlines cuts the row in two
    cands = [" ".join(rng.choice(VOCAB) for _ in range(10)) + ",\u2028" + MARK + "!" for _ in range(30)]
    rows = []
    for j, (kind, split, label) in enumerate(specs):
        cand = cands[rng.randrange(len(cands))]
        rows.append({"id": "s1-%04d" % (j + 1), "split": split, "label": label, "source": kind,
                     "time": (t0 + datetime.timedelta(seconds=seconds[j])).strftime("%Y-%m-%dT%H:%M:%SZ"),
                     "src": "sess-%d" % rng.randrange(6), "state_end": rng.randrange(30), "candidate": cand,
                     "candidate_sha256": _sha(cand.encode("utf-8")), "turn": j})
    (root / "view").mkdir()
    vbytes = "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in rows).encode("utf-8")
    (root / "view" / "view.jsonl").write_bytes(vbytes)
    train = [r for r in rows if r["split"] == "train"]
    held = [r for r in rows if r["split"] == "heldout"]
    block = real_block()
    block["inputs"].update(view_jsonl_sha256=_sha(vbytes), view_summary_sha256=_sha(b"fixture view summary"),
                           export_manifest_sha256=_sha(b"fixture export manifest"))
    block["rows"] = {"train": len(train), "train_yes": sum(1 for r in train if r["label"]), "heldout": len(held),
                     "heldout_yes": sum(1 for r in held if r["label"])}
    block["bar"].update(kind_rule_heldout_correct=oracle_kind_rule_right(rows), heldout_rows=len(held))
    block["grid"]["A"]["epochs"] = [1, 2]
    block["grid"]["B"]["mlp"]["epochs"] = [1, 2]   # C is "same as B"
    if block_edit:
        block_edit(block)
    pbytes = ("# Fixture pre-registration (synthetic)\n\n```json\n" + json.dumps(block, indent=1) + "\n```\n").encode()
    (root / "prereg.md").write_bytes(pbytes)
    ids = [r["id"] for r in rows]
    free = sorted({r["candidate_sha256"] for r in rows})
    label = {r["id"]: r["label"] for r in rows}

    def vec(lab, carries):
        v = [rng.gauss(0.0, 1.0) for _ in range(DIM)]
        if carries:
            v[0] = (1.5 if lab else -1.5) + rng.gauss(0.0, 0.6)
        return v
    arrays = {name: [vec(label[i], signal and name in ("s", "c_ctx", "q_ctx")) for i in ids] for name in F.ROW_ARRAYS}
    arrays.update({name: [vec(None, False) for _ in free] for name in F.FREE_ARRAYS})
    fids = list(ids)
    if drop_feature_row:
        k = fids.index(drop_feature_row)
        del fids[k]
        for name in F.ROW_ARRAYS:
            del arrays[name][k]
    fblock = copy.deepcopy(block)
    if features_block_edit:
        features_block_edit(fblock)
    F.write(str(root / "features"), rows=fids, free=free, dim=DIM, arrays=arrays,
            meta={"prereg_block": fblock, "prereg_sha256": _sha(pbytes), "backend": {"name": "synthetic"}})
    (root / "tails").mkdir()
    tbytes = "".join(json.dumps({"id": i, "tail": " ".join(rng.choice(VOCAB) for _ in range(40)) + "\u2028" + MARK},
                                sort_keys=True, ensure_ascii=False) + "\n" for i in ids).encode("utf-8")
    (root / "tails" / "tails.jsonl").write_bytes(tbytes)
    (root / "tails" / "manifest.json").write_text(json.dumps({
        "prereg_sha256": _sha(pbytes), "view_jsonl_sha256": _sha(vbytes),
        "view_summary_sha256": block["inputs"]["view_summary_sha256"],
        "export_manifest_sha256": block["inputs"]["export_manifest_sha256"], "count": len(rows),
        "tails_sha256": _sha(tbytes)}, sort_keys=True, indent=1) + "\n")
    (root / "rr-ok.json").write_text(json.dumps({"arrays": {"s": 0.99995, "c_ctx": 0.9999, "q_ctx": 0.99993},
                                                 "min": 0.9999}))
    return types.SimpleNamespace(root=root, prereg=root / "prereg.md", view=root / "view", features=root / "features",
                                 tails=root / "tails", rr_ok=root / "rr-ok.json", rows=rows, block=block)


def cli(fx, out, *extra, prereg=None, cmd="run"):
    return [cmd, "--prereg", str(prereg or fx.prereg), "--view", str(fx.view), "--features", str(fx.features),
            "--tails", str(fx.tails), "--out", str(out), *extra]


def refused(capsys, argv):
    rc = EV.main(argv)
    err = capsys.readouterr().err
    assert rc == 3, err
    assert err.startswith("evaluate: refused: "), err
    return err


def load(fx, **kw):
    return EV.load(str(fx.prereg), str(fx.view), str(fx.features), str(fx.tails), **kw)


def flip(path, at=7):
    b = bytearray(path.read_bytes())
    b[at] ^= 1
    path.write_bytes(bytes(b))


# ---------- pure: the block, the configurations, the folds ----------

def test_the_real_block_gives_twenty_configurations_in_the_grid_order():
    names = [c["name"] for c in EV.check_block(real_block())]
    g = real_block()["grid"]
    want = ["A-h%d-lr%r-e%d" % (h, lr, e) for h in g["A"]["hidden_layers"] for lr in g["A"]["lr"]
            for e in g["A"]["epochs"]]
    for fam in ("B", "C"):   # "C": "same as B"
        want += ["%s-logreg-l2_%r" % (fam, lam) for lam in g["B"]["logreg_l2"]]
        want += ["%s-mlp-e%d" % (fam, e) for e in g["B"]["mlp"]["epochs"]]
    assert names == want and len(names) == 20
    assert names[:3] == ["A-h1-lr0.001-e20", "A-h1-lr0.001-e60", "A-h1-lr0.0003-e20"]


def test_a_block_number_outside_its_domain_is_refused():
    for path, value, why in (("bar.alpha", float("nan"), "bar.alpha must be in (0, 1)"),
                             ("cv.folds", 1, "cv.folds must be an int >= 2"),
                             ("bar.test", "two-sided", "bar.test must be"),
                             ("grid.A.lr", [0.001, -1.0], "grid: A.lr is missing or not valid")):
        block = real_block()
        keys = path.split(".")
        d = block
        for k in keys[:-1]:
            d = d[k]
        d[keys[-1]] = value
        with pytest.raises(H.Refused, match=why.replace("(", r"\(").replace(")", r"\)")):
            EV.check_block(block)


def test_folds_cut_each_kind_by_time_then_id():
    def t(minute, spelling="%Y-%m-%dT%H:%M:%SZ"):
        return (datetime.datetime(2026, 9, 1, tzinfo=datetime.timezone.utc)
                + datetime.timedelta(minutes=minute)).strftime(spelling)
    rows = {i: {"split": "train", "kind": "x", "time": t(m)} for i, m in
            (("x1", 30), ("x2", 10), ("x4", 5), ("x5", 55), ("x6", 40), ("x7", 20))}
    rows["x3"] = {"split": "train", "kind": "x", "time": t(50, "%Y-%m-%dT%H:%M:%S.000+00:00")}
    # kind y has three rows: one per part 0 to 2; y1 and y2 share a time, so the id breaks the tie
    rows.update({"y3": {"split": "train", "kind": "y", "time": t(1)}, "y1": {"split": "train", "kind": "y", "time": t(2)},
                 "y2": {"split": "train", "kind": "y", "time": t(2)}})
    got = H.folds(rows, 5)
    # time order x4 x2 x7 x1 x6 x3 x5; 7 rows in 5 parts: 2, 2, 1, 1, 1
    assert got == {"x4": 0, "x2": 0, "x7": 1, "x1": 1, "x6": 2, "x3": 3, "x5": 4, "y3": 0, "y1": 1, "y2": 2}
    rows["h1"] = {"split": "heldout", "kind": "x", "time": t(3)}
    with pytest.raises(H.HeldOut, match="folds: h1 is a held-out row"):
        H.folds(rows, 5)


def test_a_time_is_read_with_or_without_z_and_anything_else_is_refused():
    assert H.when("2026-09-01T00:00:00.123Z") == H.when("2026-09-01T00:00:00.123+00:00")
    for bad in (None, 5, "yesterday", "Z", ""):
        with pytest.raises(H.Refused, match="is not an ISO time"):
            H.when(bad)


# ---------- pure: the metrics, McNemar, the threshold, the choice ----------

def rights(b, c, both=3, neither=2):
    """Two right/wrong lists: b rows only the first gets right, c only the second; `both` and `neither` agree."""
    return ([True] * b + [False] * c + [True] * both + [False] * neither,
            [False] * b + [True] * c + [True] * both + [False] * neither)


def test_mcnemar_is_exact_against_hand_values():
    m = EV.mcnemar(*rights(9, 1))
    assert (m["b"], m["c"], m["n"]) == (9, 1, 10)
    assert m["p_one_sided"] == Fraction(11, 1024) and m["p_two_sided"] == Fraction(22, 1024)
    m = EV.mcnemar(*rights(8, 2))
    assert m["p_one_sided"] == Fraction(56, 1024) and m["p_two_sided"] == Fraction(112, 1024)
    m = EV.mcnemar(*rights(0, 0))
    assert m["n"] == 0 and m["p_one_sided"] == 1 and m["p_two_sided"] == 1
    m = EV.mcnemar(*rights(1, 9))
    assert (m["b"], m["c"]) == (1, 9)
    assert m["p_one_sided"] == Fraction(1023, 1024) and m["p_two_sided"] == Fraction(22, 1024)
    assert EV.mcnemar(*rights(5, 5))["p_two_sided"] == 1   # min(1, 2 * 638/1024)
    with pytest.raises(H.Refused, match="mcnemar: 2 rows against 1"):
        EV.mcnemar([True, False], [True])


def test_auc_counts_a_tie_as_one_half():
    assert EV.auc([0.8, 0.5, 0.5, 0.2], [True, True, False, False]) == 0.875
    assert EV.auc([1.0] * 4, [True, False, True, False]) == 0.5
    assert EV.auc([0.3, 0.7], [True, True]) is None


def test_metrics_count_the_confusion_and_each_kind():
    ids = ["a", "b", "c", "d", "e"]
    labels = {"a": True, "b": True, "c": False, "d": False, "e": True}
    kinds = {"a": "k", "b": "k", "c": "k", "d": "j", "e": "j"}
    scores = {"a": 0.9, "b": 0.2, "c": 0.7, "d": 0.1, "e": 0.6}
    called = {i: scores[i] >= 0.5 for i in ids}
    m = EV.metrics(ids, labels, kinds, scores, called, hard=False)
    assert m["confusion"] == {"tp": 2, "fp": 1, "tn": 1, "fn": 1} and m["right"] == 3 and m["accuracy"] == 0.6
    assert m["balanced_accuracy"] == (2 / 3 + 1 / 2) / 2
    assert m["per_kind"] == {"j": {"rows": 2, "right": 2, "accuracy": 1.0}, "k": {"rows": 3, "right": 1,
                                                                                 "accuracy": 1 / 3}}
    want = -(math.log(0.9) + math.log(0.2) + math.log(0.3) + math.log(0.9) + math.log(0.6)) / 5
    assert abs(m["log_loss"] - want) < 1e-12
    assert EV.metrics(ids, labels, kinds, scores, called, hard=True)["log_loss"] is None
    assert abs(EV.log_loss([0.0, 1.0], [True, False]) + math.log(1e-7)) < 1e-9   # clipped to [1e-7, 1 - 1e-7]


def test_threshold_rule_takes_the_tie_closest_to_one_half():
    # τ = 0.2 and τ = 0.75 both get three rows right; 0.75 is closer to 0.5
    assert EV.threshold([0.1, 0.3, 0.6, 0.9], [False, True, False, True]) == (0.75, 3)
    assert EV.threshold([0.2, 0.2, 0.8], [False, False, True]) == (0.5, 3)
    # 0 and 1 are equally close to 0.5 (§3 does not say): the smaller
    assert EV.threshold([0.4] * 4, [True, False, True, False]) == (0.0, 2)


def test_the_choice_reads_out_of_fold_accuracy_then_log_loss_then_order():
    labels = {"t1": True, "t2": False, "t3": True, "t4": False}
    configs = [{"name": n, "family": "B", "head": "logreg"} for n in ("first", "second", "third", "fourth")]
    results = [{"oof": {"t1": 0.9, "t2": 0.6, "t3": 0.4, "t4": 0.2}},     # 3 right
               {"oof": {"t1": 0.7, "t2": 0.3, "t3": 0.6, "t4": 0.4}},     # 4 right
               {"oof": {"t1": 0.9, "t2": 0.1, "t3": 0.8, "t4": 0.2}},     # 4 right, the lowest log loss
               {"oof": {"t1": 0.9, "t2": 0.1, "t3": 0.8, "t4": 0.2}}]     # the same: the earlier one stays
    table, j = EV.choose(configs, results, labels)
    assert [r["oof_right"] for r in table] == [3, 4, 4, 4] and j == 2
    assert table[2]["oof_accuracy"] == 1.0 and table[0]["threshold"] == (0.2 + 0.4) / 2


def test_held_out_rows_are_called_at_the_out_of_fold_threshold():
    rows = {"h1": {"label": True, "kind": "k"}, "h2": {"label": False, "kind": "k"}, "h3": {"label": True, "kind": "j"}}
    probs = {"h1": 0.6, "h2": 0.3, "h3": 0.52}
    # the out-of-fold τ 0.55 calls h3 no; the held-out rows alone would choose τ 0.41 and get all three right
    m, right = EV.judge(rows, ["h1", "h2", "h3"], probs, 0.55)
    assert m["threshold"] == 0.55 and m["right"] == 2 and right == [True, True, False]


def test_kind_rule_is_the_training_majority_and_a_tie_is_refused():
    def r(split, label, kind):
        return {"split": split, "label": label, "kind": kind}
    rows = {"a1": r("train", True, "k"), "a2": r("train", True, "k"), "a3": r("train", False, "k"),
            "h1": r("heldout", False, "k"), "h2": r("heldout", False, "k"), "h3": r("heldout", True, "k"),
            "b1": r("train", False, "j"), "b2": r("heldout", True, "j")}
    assert EV.kind_rule(rows) == {"j": False, "k": True}
    rows["a4"] = r("train", False, "k")
    with pytest.raises(H.Refused, match="kind rule: kind k has 2 yes and 2 no training rows"):
        EV.kind_rule(rows)


@pytest.mark.parametrize("case,right,b,c,c1,rr,twice,want,counts", [
    ("PASS", 187, 9, 2, 0, 0.9995, True, "PASS", "PASS"),   # one-sided 67/2048 < 0.05 <= two-sided 134/2048
    ("NOT SHOWN", 186, 8, 2, 0, 0.9995, True, "NOT SHOWN", "NOT SHOWN"),   # one-sided 56/1024
    ("FAILED", 178, 9, 2, 0, 0.9995, True, "FAILED", "FAILED"),   # 178 is not more than 178
    ("VOID by C1", 187, 9, 2, 2, 0.9995, True, "VOID", "PASS"),
    ("VOID by the read repeat", 187, 9, 2, 0, 0.9989, True, "VOID", "PASS"),
    ("VOID by --twice", 187, 9, 2, 0, 0.9995, False, "VOID", "PASS"),
    ("INCOMPLETE", 187, 9, 2, 0, None, True, "INCOMPLETE", "PASS"),
    ("one C1 seed is not enough", 187, 9, 2, 1, 0.9995, True, "PASS", "PASS"),
    ("the read repeat at its floor", 187, 9, 2, 0, 0.999, True, "PASS", "PASS"),
    ("no --twice (E-7's letter)", 187, 9, 2, 0, 0.9995, None, "PASS", "PASS"),
    ("FAILED stays INCOMPLETE without a read repeat", 170, 0, 8, 0, None, None, "INCOMPLETE", "FAILED"),
])
def test_the_verdict_table(case, right, b, c, c1, rr, twice, want, counts):
    got, got_counts, reasons = EV.verdict(real_block(), right, EV.mcnemar(*rights(b, c)), c1, rr, twice)
    assert (got, got_counts) == (want, counts), case
    cause = {"VOID by C1": "C1: 2 of 3 seeds", "VOID by the read repeat": "read repeat: the min cosine 0.9989",
             "VOID by --twice": "twice: the two records differ"}.get(case)
    if cause is None:
        assert reasons == []
    else:
        assert len(reasons) == 1 and reasons[0].startswith(cause), reasons


def test_a_claim_needs_the_full_model_ahead_and_a_two_sided_p_below_alpha():
    block = real_block()
    ahead, behind, close = EV.mcnemar(*rights(12, 1)), EV.mcnemar(*rights(1, 12)), EV.mcnemar(*rights(9, 3))
    assert ahead["p_two_sided"] == behind["p_two_sided"] == Fraction(28, 8192)   # below 0.05 either way round
    assert close["p_two_sided"] == Fraction(598, 4096)
    assert EV.claims(block, {"C2": ahead, "C3": ahead}) == [STATE, WINDOW]
    assert EV.claims(block, {"C2": behind, "C3": close}) == []   # C2 ahead of the full model; C3 behind, p 0.146
    assert EV.claims(block, {"C2": close, "C3": ahead}) == [WINDOW]


def test_c1_permutes_inside_each_kind_and_c1b_across_kinds():
    rows = {}
    for n in range(40):
        kind = ("k", "j", "m")[n % 3]
        rows["r%02d" % n] = {"split": "train" if n < 36 else "heldout", "label": (kind == "k") == (n % 2 == 0),
                             "kind": kind}

    def yes_by_kind(labels):
        out = collections.Counter()
        for i, v in labels.items():
            out[rows[i]["kind"]] += 1 if v else 0
        return out
    real = {i: r["label"] for i, r in rows.items() if r["split"] == "train"}
    for seed in (1, 2, 3):
        c1 = EV.permute_within_kind(rows, seed)
        assert set(c1) == set(real) and yes_by_kind(c1) == yes_by_kind(real)
        assert c1 != real   # the permutation moved labels
        kind_k = sorted(i for i in real if rows[i]["kind"] == "k")
        labels = [rows[i]["label"] for i in kind_k]
        random.Random(seed).shuffle(labels)
        assert [c1[i] for i in kind_k] == labels   # E-8: random.Random(seed).shuffle over the kind's rows by id
    c1b = EV.permute_all(rows, 4)
    assert set(c1b) == set(real) and sum(c1b.values()) == sum(real.values())
    assert yes_by_kind(c1b) != yes_by_kind(real)


def test_word_overlap_words_and_jaccard():
    assert EV.words("Hello, World_42 ab abc A1B2 caf\u00e9-x\u2028dot.com", 3) == {"hello", "world_42", "abc", "a1b2",
                                                                                  "caf", "dot", "com"}
    assert EV.words("ab cd", 3) == set() and EV.words("ab cd", 2) == {"ab", "cd"}
    assert EV.jaccard({"a", "b"}, {"b", "c"}) == 1 / 3
    assert EV.jaccard(set(), set()) == 0.0


# ---------- the inputs (E-1), in this interpreter: every refusal comes before a fit ----------

def test_the_fixture_passes_every_input_check(tmp_path):
    fx = build(tmp_path / "fx")
    inp = load(fx)
    assert inp.block["bar"]["kind_rule_heldout_correct"] == 42 and inp.rule == {"kind-a": False, "kind-b": True,
                                                                                 "kind-c": True}
    assert len(inp.data.train_ids) == 143 and len(inp.data.heldout_ids) == 66
    assert sorted(inp.data.fold_of[i] for i in inp.data.train_ids if inp.rows[i]["kind"] == "kind-c") == [0, 1, 2]
    assert inp.info["features_block_differences"] == [] and inp.read_repeat is None
    assert inp.info["view_jsonl_sha256"] == fx.block["inputs"]["view_jsonl_sha256"]
    assert MARK in inp.rows["s1-0001"]["candidate"]   # the U+2028 inside a JSON string did not cut the row


def test_a_features_block_difference_outside_the_checked_keys_is_recorded(tmp_path):
    fx = build(tmp_path / "fx", features_block_edit=lambda b: b["comparison"].update(rows=104))
    assert load(fx).info["features_block_differences"] == ["comparison"]


def test_a_prereg_with_no_block_two_blocks_or_bad_json_is_refused(tmp_path, capsys):
    fx = build(tmp_path / "fx")
    text = fx.prereg.read_text()
    for name, bad, why in (("none", text.replace("```json", "```text"), "prereg: 0 fenced json blocks, not one"),
                           ("two", text + "\n" + text, "prereg: 2 fenced json blocks, not one"),
                           ("bad", text.replace('"prereg": ', '"prereg" '), "prereg: the json block: not valid JSON"),
                           ("nan", text.replace('"alpha": 0.05', '"alpha": NaN'), "not valid JSON (NaN is not")):
        (tmp_path / (name + ".md")).write_text(bad)
        err = refused(capsys, cli(fx, tmp_path / (name + ".json"), prereg=tmp_path / (name + ".md")))
        assert why in err, (name, err)
        assert not (tmp_path / (name + ".json")).exists()


def test_a_view_whose_sha256_is_not_the_blocks_is_refused(tmp_path, capsys):
    fx = build(tmp_path / "fx")
    flip(fx.view / "view.jsonl", at=40)
    err = refused(capsys, cli(fx, tmp_path / "out.json"))
    assert "view: view.jsonl's sha256 is not the block's inputs.view_jsonl_sha256" in err


def test_a_row_count_off_is_refused(tmp_path, capsys):
    fx = build(tmp_path / "fx", block_edit=lambda b: b["rows"].update(train_yes=b["rows"]["train_yes"] + 1))
    err = refused(capsys, cli(fx, tmp_path / "out.json"))
    assert "view: 72 train yes rows, not the block's 73" in err


def test_a_changed_features_byte_is_refused_by_features_read(tmp_path, capsys):
    fx = build(tmp_path / "fx")
    flip(fx.features / "c_ctx.f32")
    err = refused(capsys, cli(fx, tmp_path / "out.json"))
    assert "features: c_ctx: the file's sha256 is not the index's" in err


def test_a_features_block_that_differs_on_bar_is_refused(tmp_path, capsys):
    fx = build(tmp_path / "fx", features_block_edit=lambda b: b["bar"].update(alpha=0.01))
    err = refused(capsys, cli(fx, tmp_path / "out.json"))
    assert "features: meta.prereg_block differs from the block on bar" in err


def test_a_row_missing_from_the_row_arrays_is_refused(tmp_path, capsys):
    fx = build(tmp_path / "fx", drop_feature_row="s1-0005")
    err = refused(capsys, cli(fx, tmp_path / "out.json"))
    assert "features: row s1-0005 has no vector in s" in err


def test_a_tails_file_whose_sha256_is_not_its_manifests_is_refused(tmp_path, capsys):
    fx = build(tmp_path / "fx")
    flip(fx.tails / "tails.jsonl", at=30)
    err = refused(capsys, cli(fx, tmp_path / "out.json"))
    assert "tails: tails.jsonl's sha256 is not the manifest's tails_sha256" in err


def test_a_kind_rule_count_that_is_not_the_blocks_is_refused(tmp_path, capsys):
    fx = build(tmp_path / "fx", block_edit=lambda b: b["bar"].update(
        kind_rule_heldout_correct=b["bar"]["kind_rule_heldout_correct"] + 1))
    err = refused(capsys, cli(fx, tmp_path / "out.json"))
    assert "kind rule: right on 42 of 66 held-out rows, not the block's 43" in err


def test_a_read_repeat_without_a_finite_min_is_refused(tmp_path, capsys):
    fx = build(tmp_path / "fx")
    for name, text, why in (("nan.json", '{"arrays": {}, "min": NaN}', "read repeat: not valid JSON"),
                            ("big.json", '{"arrays": {}, "min": 1e999}', "read repeat: not {"),
                            ("nomin.json", '{"arrays": {}}', "read repeat: not {")):
        (tmp_path / name).write_text(text)
        err = refused(capsys, cli(fx, tmp_path / "out.json", "--read-repeat", str(tmp_path / name)))
        assert why in err, (name, err)


def test_a_held_out_row_handed_to_a_fit_is_refused(tmp_path):
    inp = load(build(tmp_path / "fx"))
    data, cfg = inp.data, inp.configs[8]
    labels = {i: inp.rows[i]["label"] for i in inp.rows}
    with pytest.raises(H.HeldOut, match="train: %s is a held-out row" % data.heldout_ids[0]):
        H.train(cfg, data, labels, data.train_ids[:20] + data.heldout_ids[:1], 0)
    try:   # the control: without the held-out row the same call goes on to the fit (torch is absent here)
        H.train(cfg, data, labels, data.train_ids[:20], 0)
    except ModuleNotFoundError as e:
        assert e.name == "torch"


def test_an_out_that_exists_climbs_or_has_no_directory_is_refused(tmp_path, capsys):
    fx = build(tmp_path / "fx")
    (tmp_path / "taken.json").write_text("OLDER RECORD\n")
    err = refused(capsys, cli(fx, tmp_path / "taken.json"))
    assert "the output exists" in err and (tmp_path / "taken.json").read_text() == "OLDER RECORD\n"
    for out in (str(tmp_path / "missing") + "/../out.json", "../out.json"):
        assert "without a '..' part" in refused(capsys, cli(fx, out))
    assert "its directory does not exist" in refused(capsys, cli(fx, tmp_path / "missing" / "out.json"))
    assert not (tmp_path / "missing").exists() and not (tmp_path / "out.json").exists()


# ---------- the Laya venv (torch on CPU) as subprocesses ----------

def _present(path):
    try:   # AF-AP-44: a venue probe returns absent on any OSError, never raises
        os.stat(path)
        return True
    except OSError:
        return False


@pytest.fixture(scope="module")
def laya():
    venue = os.environ.get("S0_01_VENUE")
    if venue != "sandbox":
        pytest.skip("LOUD SKIP: the Laya venv (torch) is a declared input of the sandbox venue only (S0_01_VENUE=%r;"
                    " CI declares none, and the PC's paths are not declared to this file)" % venue)
    if not _present(LAYA_PY):
        pytest.fail("declared input missing on the sandbox venue: %s" % LAYA_PY)
    return LAYA_PY


def evaluate_in_laya(py, argv):
    return subprocess.run([py, str(EVALUATE), *argv], capture_output=True, text=True, timeout=900,
                          env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))


def script_in_laya(py, script, *args):
    proc = subprocess.run([py, "-c", script, str(ROOT / "scripts"), *args], capture_output=True, text=True,
                          timeout=900, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    assert proc.returncode == 0, proc.stderr[-3000:]
    return json.loads(proc.stdout.strip().splitlines()[-1])


@pytest.fixture(scope="module")
def planted(laya, tmp_path_factory):
    """The planted-signal fixture, evaluated twice with --read-repeat and --twice."""
    root = tmp_path_factory.mktemp("planted")
    fx = build(root / "fx", signal=True)
    runs = []
    for n in (1, 2):
        out = root / ("record-%d.json" % n)
        proc = evaluate_in_laya(laya, cli(fx, out, "--read-repeat", str(fx.rr_ok), "--twice"))
        assert proc.returncode == 0, proc.stderr[-3000:]
        runs.append((proc, out))
    return fx, runs


def test_a_planted_signal_passes_and_c1_does_not_fire(planted):
    fx, runs = planted
    rec = json.loads(runs[0][1].read_text())
    assert rec["verdict"] == "PASS" and rec["counts_outcome"] == "PASS" and rec["void_reasons"] == []
    checks = rec["void_checks"]
    assert (checks["read_repeat_min"], checks["twice"]) == (0.9999, "identical")
    # C1 does not fire: fewer seeds than the void rule's count meet the PASS rule. A seed may meet it on this clean a
    # signal, when its permuted labels keep a chance correlation with the true ones (seed 1 here, measured)
    assert checks["c1_seeds_meeting_pass_rule"] == sum(1 for c in rec["controls"]["C1"] if c["meets_pass_rule"])
    assert checks["c1_seeds_meeting_pass_rule"] < fx.block["controls"]["C1_void_if_passing_seeds_at_least"]
    assert rec["model"]["right"] > fx.block["bar"]["kind_rule_heldout_correct"] == rec["kind_rule"]["heldout_right"]
    mc = rec["mcnemar_vs_kind_rule"]
    assert mc["b"] > mc["c"] and mc["p_one_sided"] < 0.05 and rec["exploratory"] is False
    assert rec["claims"] == [STATE, WINDOW]   # C2 and C3 read noise only
    assert runs[0][0].stdout.startswith("evaluate run: VERDICT PASS (counts PASS)") and runs[0][0].stdout.count("\n") == 1


def test_two_runs_give_byte_identical_records(planted):
    _, runs = planted
    assert runs[0][1].read_bytes() == runs[1][1].read_bytes()
    assert runs[0][0].stdout == runs[1][0].stdout


def test_the_record_follows_the_rules_it_reports(planted):
    fx, runs = planted
    rec = json.loads(runs[0][1].read_text())
    table, train = rec["configurations"], fx.block["rows"]["train"]
    assert [r["name"] for r in table] == [c["name"] for c in EV.check_block(fx.block)]
    # §3's choice, restated: the most rows right out of fold, then the lower log loss, then the earlier configuration
    best = max(range(len(table)), key=lambda j: (table[j]["oof_right"], -table[j]["oof_log_loss"], -j))
    assert rec["chosen"] == table[best]["name"]
    assert all(r["oof_accuracy"] == r["oof_right"] / train for r in table)   # scored on the training rows
    assert rec["model"]["threshold"] == table[best]["threshold"]   # held-out rows called at the out-of-fold τ
    # kind-a and kind-b: 70 rows, 14 per part; kind-c: 3 rows, parts 0 to 2
    assert rec["model"]["rows"] == fx.block["rows"]["heldout"] and rec["rows"]["fold_sizes"] == [29, 29, 29, 28, 28]
    real = collections.Counter()
    for r in fx.rows:
        real[r["source"]] += 1 if r["split"] == "train" and r["label"] else 0
    for c in rec["controls"]["C1"]:
        assert c["labels"]["train_yes_by_kind"] == dict(real) and c["labels"]["changed"] > 0
    c1b = rec["controls"]["C1b"]["labels"]
    assert c1b["train_yes_by_kind"] != dict(real) and sum(c1b["train_yes_by_kind"].values()) == sum(real.values())
    for name in ("C2", "C3"):
        assert rec["controls"][name]["chosen"] == rec["chosen"] and rec["controls"][name]["labels"]["changed"] == 0
    assert rec["deviations"] == EV.DEVIATIONS and rec["prereg"]["sha256"] == _sha(fx.prereg.read_bytes())
    # McNemar's b - c is the difference of the rows right, so each comparison is against the model it names
    rule = rec["kind_rule"]["heldout_right"]
    assert rec["mcnemar_vs_kind_rule"]["b"] - rec["mcnemar_vs_kind_rule"]["c"] == rec["model"]["right"] - rule
    for c in rec["controls"]["C1"] + [rec["controls"][k] for k in ("C1b", "C2", "C3")]:
        assert c["vs_kind_rule"]["b"] - c["vs_kind_rule"]["c"] == c["heldout"]["right"] - rule
        assert c["vs_full_model"]["b"] - c["vs_full_model"]["c"] == rec["model"]["right"] - c["heldout"]["right"]
    # the controls' labels, by this file's own E-8 shuffles with the block's seeds
    train_rows = sorted((r for r in fx.rows if r["split"] == "train"), key=lambda r: r["id"])
    lab = {r["id"]: r["label"] for r in train_rows}
    assert [c["seed"] for c in rec["controls"]["C1"]] == fx.block["controls"]["C1_seeds"]
    for c in rec["controls"]["C1"]:
        moved = 0
        for kind in sorted({r["source"] for r in train_rows}):
            ids = [r["id"] for r in train_rows if r["source"] == kind]
            labels = [lab[i] for i in ids]
            random.Random(c["seed"]).shuffle(labels)
            moved += sum(1 for i, v in zip(ids, labels) if v != lab[i])
        assert c["labels"]["changed"] == moved
    labels = [r["label"] for r in train_rows]
    random.Random(fx.block["controls"]["C1b_seed"]).shuffle(labels)
    want = collections.Counter()
    for r, v in zip(train_rows, labels):
        want[r["source"]] += 1 if v else 0
    assert rec["controls"]["C1b"]["seed"] == 4 and c1b["train_yes_by_kind"] == dict(want)
    # the baselines; the word overlap recomputed with this file's own words and Jaccard, fit on the training rows
    base, held = rec["baselines"], [r for r in fx.rows if r["split"] == "heldout"]
    assert base["always_yes"]["right"] == fx.block["rows"]["heldout_yes"] and base["always_yes"]["log_loss"] is None
    assert base["kind_rule"]["right"] == rule and base["kind_rule"]["log_loss"] is None
    tails = {}
    for line in (fx.tails / "tails.jsonl").read_text(encoding="utf-8").split("\n")[:-1]:
        t = json.loads(line)
        tails[t["id"]] = t["tail"]
    n = fx.block["word_overlap"]["min_word_len"]
    overlap = {r["id"]: own_jaccard(own_words(r["candidate"], n), own_words(tails[r["id"]], n)) for r in fx.rows}
    tau, _ = EV.threshold([overlap[r["id"]] for r in train_rows], [r["label"] for r in train_rows])
    assert base["word_overlap"]["threshold"] == tau
    assert base["word_overlap"]["right"] == sum(1 for r in held if (overlap[r["id"]] >= tau) == r["label"])


def own_words(text, n):
    """This file's own word split (no regex): runs of a-z, 0-9 and _ after lowercasing, at least n long."""
    out, word = set(), ""
    for ch in text.lower() + " ":
        if ch in "abcdefghijklmnopqrstuvwxyz0123456789_":
            word += ch
            continue
        if len(word) >= n:
            out.add(word)
        word = ""
    return out


def own_jaccard(a, b):
    return len(a & b) / len(a | b) if a | b else 0.0


def test_no_output_carries_session_text_or_a_host_path(planted):
    fx, runs = planted
    for proc, out in runs:
        for text in (out.read_text(), proc.stdout):
            assert MARK not in text and str(fx.root) not in text and "\u2028" not in text


def test_no_signal_is_never_pass(laya, tmp_path):
    fx = build(tmp_path / "fx", signal=False, seed=11)
    proc = evaluate_in_laya(laya, cli(fx, tmp_path / "rec.json", "--read-repeat", str(fx.rr_ok)))
    assert proc.returncode == 0, proc.stderr[-3000:]
    rec = json.loads((tmp_path / "rec.json").read_text())
    assert rec["counts_outcome"] in ("FAILED", "NOT SHOWN") and rec["verdict"] == rec["counts_outcome"]
    assert rec["void_checks"]["twice"] == "not run"


def test_without_a_read_repeat_a_passing_count_is_incomplete(laya, tmp_path):
    fx = build(tmp_path / "fx", signal=True)
    proc = evaluate_in_laya(laya, cli(fx, tmp_path / "rec.json"))
    assert proc.returncode == 0, proc.stderr[-3000:]
    rec = json.loads((tmp_path / "rec.json").read_text())
    assert (rec["verdict"], rec["counts_outcome"]) == ("INCOMPLETE", "PASS")
    assert rec["void_checks"]["read_repeat_min"] is None and rec["inputs"]["read_repeat_sha256"] is None


def test_explore_scores_one_named_configuration_with_no_verdict(laya, tmp_path):
    fx = build(tmp_path / "fx", signal=True)
    proc = evaluate_in_laya(laya, cli(fx, tmp_path / "rec.json", "--config", "A-h2-lr0.001-e2", cmd="explore"))
    assert proc.returncode == 0, proc.stderr[-3000:]
    rec = json.loads((tmp_path / "rec.json").read_text())
    assert rec["exploratory"] is True and rec["chosen"] == "A-h2-lr0.001-e2"
    assert [r["name"] for r in rec["configurations"]] == ["A-h2-lr0.001-e2"]
    for key in ("verdict", "counts_outcome", "void_checks", "void_reasons", "claims"):
        assert key not in rec
    assert set(rec["controls"]) == {"C1", "C1b", "C2", "C3"} and rec["controls"]["C2"]["chosen"] == "A-h2-lr0.001-e2"
    assert proc.stdout.startswith("evaluate explore: EXPLORATORY A-h2-lr0.001-e2: ")
    err = evaluate_in_laya(laya, cli(fx, tmp_path / "rec2.json", "--config", "Z-none", cmd="explore")).stderr
    assert "explore: no configuration of the block is named 'Z-none'" in err


AVERAGE = r"""
import json, sys
sys.path.insert(0, sys.argv[1])
from s1_train import evaluate as EV, heads as H
inp = EV.load(*sys.argv[2:6])
data = inp.data
cfg = [c for c in inp.configs if c["name"] == sys.argv[6]][0]
labels = {i: data.rows[i]["label"] for i in data.train_ids}
cv = H.cross_validate(cfg, data, labels)
own_oof, own_heldout = {}, []
for k in range(data.k):   # this script's own split: train on the other folds, score fold k and the held-out rows
    fit = H.train(cfg, data, labels, [i for i in data.train_ids if data.fold_of[i] != k], k)
    own_oof.update(H.score(fit, data, [i for i in data.train_ids if data.fold_of[i] == k]))
    own_heldout.append(H.score_heldout(fit, data, data.heldout_ids))
again = H.score_heldout(H.train(cfg, data, labels, [i for i in data.train_ids if data.fold_of[i] != 0], 0), data,
                        data.heldout_ids)
mean = {i: sum(p[i] for p in own_heldout) / len(own_heldout) for i in data.heldout_ids}
rows0 = [i for i in data.train_ids if data.fold_of[i] != 0]
fit0, fit1 = H.train(cfg, data, labels, rows0, 0), H.train(cfg, data, labels, rows0, 1)   # fold 1's seed, same rows
seed_follows_fold = H.score_heldout(fit0, data, data.heldout_ids) != H.score_heldout(fit1, data, data.heldout_ids)
repeatable = H.score_heldout(fit0, data, data.heldout_ids) == H.score_heldout(fit0, data, data.heldout_ids)
cols = list(zip(*[data.mats["c_ctx"].get(i) for i in rows0]))   # this script's own mean and population sd
mu = [sum(c) / len(c) for c in cols]
sd = [max((sum((x - u) ** 2 for x in c) / len(c)) ** 0.5, data.floor) for c, u in zip(cols, mu)]
stats_gap = max(abs(a - b) for a, b in zip(mu + sd, fit0["stats"][0][0].tolist() + fit0["stats"][0][1].tolist()))
from s1_train import features as F   # a constant column: its sd is the floor
mini_rows = {"t%d" % n: {"split": "train", "label": n % 2 == 0, "kind": "k", "time": "2026-09-01T00:00:0%dZ" % n,
                         "cand": "c%d" % n, "state": "s%d" % n} for n in range(6)}
mini = H.Data(mini_rows, {"c_ctx": F.Matrix(sorted(mini_rows), 2, [v for n in range(6) for v in (0.5, float(n))])},
              2, data.seed, data.floor)
logreg = [c for c in inp.configs if c["head"] == "logreg"][0]
floor_sd = H.train(logreg, mini, {i: r["label"] for i, r in mini_rows.items()}, mini.train_ids, 0)["stats"][0][1].tolist()
refusals = []
for call in (lambda: H.train(cfg, data, labels, data.train_ids[:20] + data.heldout_ids[:1], 0),
             lambda: H.score(fit, data, data.train_ids[:3] + data.heldout_ids[:1]),
             lambda: H.score_heldout(fit, data, data.train_ids[:1])):
    try:
        call()
        refusals.append(None)
    except (H.HeldOut, H.Refused) as e:
        refusals.append(type(e).__name__ + ": " + str(e))
print(json.dumps({"oof_is_the_other_folds_model": cv["oof"] == own_oof,
                  "mean_gap": max(abs(cv["heldout"][i] - mean[i]) for i in data.heldout_ids),
                  "fold0_gap": max(abs(cv["heldout"][i] - own_heldout[0][i]) for i in data.heldout_ids),
                  "repeat_identical": again == own_heldout[0], "refusals": refusals,
                  "heldout": data.heldout_ids[0], "train": data.train_ids[0], "seed_follows_fold": seed_follows_fold,
                  "repeatable": repeatable, "stats_gap": stats_gap, "floor_sd": floor_sd, "floor": data.floor}))
"""


def test_the_held_out_probability_is_the_mean_of_the_five_fold_models(laya, tmp_path):
    fx = build(tmp_path / "fx", signal=True)
    got = script_in_laya(laya, AVERAGE, str(fx.prereg), str(fx.view), str(fx.features), str(fx.tails), "B-mlp-e2")
    assert got["oof_is_the_other_folds_model"] is True and got["repeat_identical"] is True
    assert got["mean_gap"] <= 1e-12 and got["fold0_gap"] > 1e-6   # the five models differ, and the mean is theirs
    assert got["refusals"] == ["HeldOut: train: %s is a held-out row" % got["heldout"],
                               "HeldOut: score: %s is a held-out row" % got["heldout"],
                               "Refused: score_heldout: %s is a training row" % got["train"]]
    assert got["seed_follows_fold"] is True    # torch.manual_seed(seed + fold): another fold, another init
    assert got["repeatable"] is True           # scoring runs in eval mode (dropout off)
    assert got["stats_gap"] < 1e-9             # standardized with the training rows' mean and population sd
    assert got["floor_sd"][0] == got["floor"] and got["floor_sd"][1] > 1   # a constant column gets the floor


SIGNATURE = r"""
import json, sys
sys.path.insert(0, sys.argv[1])
from s1_train import evaluate as EV, heads as H
inp = EV.load(*sys.argv[2:6])
data = inp.data
labels = {i: data.rows[i]["label"] for i in data.train_ids}
out = {}
for name in sys.argv[6:]:
    cfg = [c for c in inp.configs if c["name"] == name][0]
    ho = {v: H.cross_validate(cfg, data, labels, v)["heldout"] for v in ("full", "C2", "C3")}
    for v in ("full", "C2"):
        by_cand = {}
        for i in data.heldout_ids:
            by_cand.setdefault(data.rows[i]["cand"], []).append(ho[v][i])
        out[name + " " + v] = {"within": max(max(p) - min(p) for p in by_cand.values()),
                               "across": max(ho[v].values()) - min(ho[v].values())}
    out[name + " C3 is full"] = ho["C3"] == ho["full"]
print(json.dumps(out))
"""


def test_c2_reads_no_state_and_c3_another_input(laya, tmp_path):
    """C2's signature: with no session state (c_free or q_free; for A, zeros for s) the held-out rows with the same
    candidate get the same probability, the full model's do not; C3 reads other inputs than the full model. "The same"
    is within 1e-6: a CPU kernel rounds two equal rows apart by their place in a batch (measured: 1.2e-8 for C's C2
    here, against a spread of at least 0.5 within a candidate for the full models and 0.2 across candidates for C2)."""
    fx = build(tmp_path / "fx", signal=True)
    names = ["A-h1-lr0.001-e1", "B-logreg-l2_0.1", "C-logreg-l2_0.1"]
    got = script_in_laya(laya, SIGNATURE, str(fx.prereg), str(fx.view), str(fx.features), str(fx.tails), *names)
    for name in names:
        assert got[name + " C2"]["within"] < 1e-6 and got[name + " C2"]["across"] > 0.01, got
        assert got[name + " full"]["within"] > 0.01, got
        assert got[name + " C3 is full"] is False


ARCH = r"""
import json, math, sys, torch
sys.path.insert(0, sys.argv[1])
from s1_train import evaluate as EV, heads as H
inp = EV.load(*sys.argv[2:6])
data = inp.data
labels = {i: data.rows[i]["label"] for i in data.train_ids}
def layers(seq):
    out = []
    for m in seq:
        d = {"type": type(m).__name__}
        for key, attr in (("in", "in_features"), ("out", "out_features"), ("p", "p"), ("approximate", "approximate")):
            if hasattr(m, attr):
                d[key] = getattr(m, attr)
        if hasattr(m, "normalized_shape"):
            d["shape"] = list(m.normalized_shape)
        out.append(d)
    return out
got = {}
for name in sys.argv[6:]:
    cfg = [c for c in inp.configs if c["name"] == name][0]
    m = H.train(cfg, data, labels, data.train_ids, 0)["model"]
    if cfg["head"] == "pair":
        x = torch.zeros(2, data.mats["s"].dim)
        m.t.data.fill_(math.log(1000.0))
        got[name] = {"state": layers(m.state), "action": layers(m.action),
                     "scalars": sorted(n for n, _ in m.named_parameters() if "." not in n),
                     "scale_at_1000": H._pair(torch, m, x, x, cfg)[2].item()}
    else:
        got[name] = layers([m] if cfg["head"] == "logreg" else m)
print(json.dumps(got))
"""


def test_the_heads_are_the_models_e4_names(laya, tmp_path):
    fx = build(tmp_path / "fx", signal=True)
    a, b = fx.block["grid"]["A"], fx.block["grid"]["B"]["mlp"]
    got = script_in_laya(laya, ARCH, str(fx.prereg), str(fx.view), str(fx.features), str(fx.tails),
                         "A-h2-lr0.001-e1", "B-logreg-l2_0.1", "B-mlp-e1")
    w = a["hidden_width"]

    def block_of(d_in):
        return [{"type": "Linear", "in": d_in, "out": w}, {"type": "LayerNorm", "shape": [w]},
                {"type": "GELU", "approximate": "none"}, {"type": "Dropout", "p": a["dropout"]}]
    tower = block_of(DIM) + block_of(w) + [{"type": "Linear", "in": w, "out": a["out_dim"]}]
    pair = got["A-h2-lr0.001-e1"]
    assert pair["state"] == tower and pair["action"] == tower and pair["scalars"] == ["a", "b", "t"]
    assert pair["scale_at_1000"] == a["logit_scale_max"]   # exp(t) clamped at logit_scale_max
    assert got["B-logreg-l2_0.1"] == [{"type": "Linear", "in": DIM, "out": 1}]
    assert got["B-mlp-e1"] == [{"type": "Linear", "in": DIM, "out": b["hidden_width"]},
                               {"type": "GELU", "approximate": "none"}, {"type": "Dropout", "p": b["dropout"]},
                               {"type": "Linear", "in": b["hidden_width"], "out": 1}]


TWICE = r"""
import json, sys
sys.path.insert(0, sys.argv[1])
from s1_train import evaluate as EV, heads as H
passes, real_evaluate, real_cv = [], EV.evaluate, H.cross_validate
def evaluate(inp, only=None):
    passes.append(1)
    return real_evaluate(inp, only)
def cross_validate(config, data, labels, variant="full"):
    out = real_cv(config, data, labels, variant)
    if len(passes) == 2:   # the injected fault: in the second pass one out-of-fold probability moves by 1e-6
        first = data.train_ids[0]
        out["oof"][first] = out["oof"][first] * (1 - 1e-6)
    return out
EV.evaluate, H.cross_validate = evaluate, cross_validate
rc = EV.main(sys.argv[2:])
print(json.dumps({"rc": rc, "passes": len(passes)}))
"""


def test_twice_voids_a_run_whose_two_passes_differ(laya, tmp_path):
    """--twice through the real path, with a fault the test injects into the second pass only (the planted runs are
    the control: identical)."""
    fx = build(tmp_path / "fx", signal=True)
    got = script_in_laya(laya, TWICE, *cli(fx, tmp_path / "rec.json", "--read-repeat", str(fx.rr_ok), "--twice"))
    assert got == {"rc": 0, "passes": 2}
    rec = json.loads((tmp_path / "rec.json").read_text())
    assert (rec["verdict"], rec["counts_outcome"]) == ("VOID", "PASS")
    assert rec["void_reasons"] == ["twice: the two records differ"] and rec["void_checks"]["twice"] == "differ"


BATCHES = r"""
import json, sys, torch
sys.path.insert(0, sys.argv[1])
from s1_train import heads as H
def order(seed):
    return [b.tolist() for b in H._batches(torch, 10, 4, 2, seed)]
print(json.dumps({"a": order(441), "b": order(441), "c": order(442)}))
"""


def test_the_batch_order_follows_the_seed(laya):
    got = script_in_laya(laya, BATCHES)
    a = got["a"]
    assert a == got["b"] and a != got["c"]
    assert [len(x) for x in a] == [4, 4, 2, 4, 4, 2]   # batches of 4, the last partial one kept, per epoch
    assert sorted(a[0] + a[1] + a[2]) == list(range(10)) == sorted(a[3] + a[4] + a[5])
    assert a[0] + a[1] + a[2] != a[3] + a[4] + a[5]   # a fresh permutation each epoch


LOSS = r"""
import json, sys, torch
sys.path.insert(0, sys.argv[1])
from s1_train import heads as H
out = []
for case in json.loads(sys.argv[2]):
    t = lambda key, dt: torch.tensor(case[key], dtype=dt)
    out.append(H.pair_loss(torch, t("L", torch.float64), t("y", torch.float64), t("a", torch.float64),
                           t("b", torch.float64), t("cand", torch.long), t("state", torch.long)).item())
print(json.dumps(out))
"""


def oracle_pair_loss(L, y, a, b, cand, state, mask_cand=True, mask_state=True):
    """E-4's loss in plain math: the mean of the two InfoNCE directions over the yes rows, plus the BCE."""
    def sig(z):
        return 1 / (1 + math.exp(-z))
    n = len(y)
    bce = -sum(y[i] * math.log(sig(a * L[i][i] + b)) + (1 - y[i]) * math.log(1 - sig(a * L[i][i] + b))
               for i in range(n)) / n
    yes = [i for i in range(n) if y[i]]
    if len(yes) < 2:
        return bce

    def keep(i, j):
        return i == j or ((not mask_cand or cand[i] != cand[j]) and (not mask_state or state[i] != state[j]))
    s2a = [math.log(sum(math.exp(L[i][j]) for j in yes if keep(i, j))) - L[i][i] for i in yes]
    a2s = [math.log(sum(math.exp(L[j][i]) for j in yes if keep(i, j))) - L[i][i] for i in yes]
    return (sum(s2a) / len(yes) + sum(a2s) / len(yes)) / 2 + bce


def test_pair_loss_masks_same_candidate_and_same_state(laya):
    L = [[3.0, 2.5, -1.0, 0.5, 1.2], [0.7, 2.0, 1.5, -0.3, 0.4], [-0.2, 1.1, 1.8, 0.9, -1.4],
         [0.3, -0.8, 0.6, 1.0, 0.2], [1.6, 0.1, -0.5, 0.8, 2.2]]
    # rows 0 and 1 share a candidate; rows 1 and 2 share a state; rows 0, 2 and 4 share neither; row 3 is a no row
    mixed = {"L": L, "y": [1, 1, 1, 0, 1], "a": 1.3, "b": -0.4, "cand": [0, 0, 1, 2, 3], "state": [0, 1, 1, 2, 3]}
    single = dict(mixed, y=[0, 1, 0, 0, 0])
    got = script_in_laya(laya, LOSS, json.dumps([mixed, single]))
    args = [mixed[k] for k in ("L", "y", "a", "b", "cand", "state")]
    want = oracle_pair_loss(*args)
    assert abs(got[0] - want) < 1e-9
    assert abs(want - oracle_pair_loss(*args, mask_state=False)) > 1e-3   # the case needs the state clause
    assert abs(want - oracle_pair_loss(*args, mask_cand=False)) > 1e-3    # and the candidate clause
    single_args = [single[k] for k in ("L", "y", "a", "b", "cand", "state")]
    assert abs(got[1] - oracle_pair_loss(*single_args)) < 1e-9   # one yes row: the BCE alone
