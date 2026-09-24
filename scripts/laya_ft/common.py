"""Shared pieces of the Laya fine-tune tooling (task #233; D-075, D-078; brief tasks/briefs/jev-laya/FT1-brief.md).

Pure Python: nothing here imports torch, transformers or laya, so the project venv's tests import it directly. It holds
the three question types (D-6), the held-out identities (D-3), the dataset loader, the label format and the label join.
The J2 helpers are the committed modules themselves, loaded by path and never copied: j2c.py (the whole-finding blocks and
their `_mask`; it loads decide-harvest and v1_probe.py), ap_probe.py (the incident headings, the registry and the lexical
tokens) and transcript_export.py (`scrub`, the scrubber scripts/jev.py uses).
"""
import hashlib
import importlib.machinery
import importlib.util
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FINDINGS = ROOT / "docs" / "research" / "findings"
REVISION = "1c5edc17a7acd8701df6fc341c0d179f1c62c982"   # the pinned Laya snapshot (scripts/laya_systemone_server.py)
DEFAULT_MODEL_DIR = ("/root/hf-laya-probe/hub/models--convaiinnovations--laya/snapshots/%s/typed-decisions" % REVISION)
INCIDENT_LOG = "docs/INCIDENT-LOG.md"
DATASET_FILE = "dataset.jsonl"
MANIFEST_FILE = "manifest.json"


def load_module(name, path):
    """Load a committed script as a module by path (the j2c.py pattern); registered under `name` in sys.modules."""
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


J2C = load_module("laya_ft_j2c", FINDINGS / "j2c-fulltext" / "j2c.py")
V1 = J2C.V1   # docs/research/findings/j2-v1-probe/v1_probe.py, the instance j2c.py loaded
AP = load_module("laya_ft_ap_probe", FINDINGS / "ap-hawk-probe" / "ap_probe.py")
scrub = load_module("laya_ft_transcript_export", ROOT / "scripts" / "transcript_export.py").scrub

# D-6. (a) J2's own wording (v1_probe.py cmd_score) over v1_probe's six CLASSES, so the evaluator's J2 `choice` IS the
# trained question; (b) the brief's text verbatim; (c) ap_probe's INSTRUCTION, the question J2 scored per chunk.
V1_CLASS_INSTRUCTION = "Which class did the verifier give this finding?"
V1_BLOCKING_INSTRUCTION = ("Does this finding block the merge: a contract break reproduced through the real path, or a "
                           "contract that is itself wrong?")
QUESTIONS = {
    "v1.finding_class": {"type": "choice", "instructions": V1_CLASS_INSTRUCTION, "criteria": dict(V1.CLASSES)},
    "v1.blocking": {"type": "noul", "instructions": V1_BLOCKING_INSTRUCTION},
    "ap.violates_row": {"type": "noul", "instructions": AP.INSTRUCTION},
}

# D-3: the three held-out samples, pinned by the sha256 each was committed with before scoring.
HELDOUT = {
    "j2_v1": ("docs/research/findings/j2-v1-probe/sample.json",
              "b1cf7867f5995280f1c9298fa48e024b3039ee50ddca1e3626367717c9f27fc9"),
    "j2c": ("docs/research/findings/j2c-fulltext/sample.json",
            "af469599e3e1054241c75f7b81eec5ae0214136d88fbbbbf6b8701e404b44df3"),
    "ap": ("docs/research/findings/ap-hawk-probe/sample.json",
           "c07c581ad74201e19efe8b9da61eedd4a4cfcc81c3c10f7036ba20da3aaa2044"),
}


class HeldOutError(Exception):
    """The held-out samples cannot be read as pinned, or a held-out row cannot be found where the build looks."""


class HeldOutLeak(Exception):
    """A held-out row is in the training data (D-3)."""


class DatasetError(Exception):
    """A dataset directory is not what its manifest says."""


class LabelError(Exception):
    """A teacher answer or a stored label is malformed or does not match its dataset row."""


def dumps(obj):
    """Order-preserving compact JSON. Key order is meaningful here: a state's keys are serialized in order by
    laya.common.serialize_state, and a choice's criteria order is its option order (render_options)."""
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def sha256_hex(data):
    return hashlib.sha256(data if isinstance(data, bytes) else data.encode("utf-8")).hexdigest()


def sha256_file(path, chunk=1 << 22):
    """sha256 of a file read in 4 MiB chunks (the model's weights are 1.6 GB)."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for block in iter(lambda: fh.read(chunk), b""):
            h.update(block)
    return h.hexdigest()


def state_sha(state):
    return sha256_hex(dumps(state))


def question_sha(question):
    return sha256_hex(dumps(question))


def options(question):
    """Option names in laya.common.render_options order: a choice's criteria keys, a noul's [false, true]."""
    if question["type"] == "choice":
        return list(question["criteria"])
    if question["type"] == "noul":
        return ["false", "true"]
    raise LabelError("unsupported question type %r" % question["type"])


def label_key(item_id, question_id):
    return "%s|%s" % (item_id, question_id)


def model_fingerprint(model_dir):
    """What a dataset's window fit depends on: the checkpoint config's lengths (read as Agent.system_one reads them)
    and the digests of the config and the tokenizer; the snapshot revision when the path names one."""
    model_dir = Path(model_dir)
    config = (model_dir / "rl_agent_config.json").read_bytes()
    cfg = json.loads(config.decode("utf-8"))
    return {"revision": model_dir.parent.name if model_dir.parent.parent.name == "snapshots" else None,
            "max_len": cfg.get("max_len", 512), "head_max_len": cfg.get("head_max_len", 192),
            "config_sha256": sha256_hex(config),
            "tokenizer_sha256": sha256_hex((model_dir / "tokenizer" / "tokenizer.json").read_bytes())}


def jsonl_lines(text):
    """Split a JSONL text on "\\n" only: str.splitlines() also splits on U+2028/U+2029 and other separators."""
    return [line for line in text.split("\n") if line.strip()]


def heldout_identities(read, pins=None):
    """The D-3 identities, from the committed samples: `read(repo-relative path) -> bytes`.

    v1: "path#finding_id" for every J2c row (its `source`), and for every J2 v1 row through the J2c row with the same
    row_digest (J2c is the same 100 rows joined to their reports); v1_texts: the J2c states (masked whole findings);
    incident: the AP sample's states (masked incident headings; its line numbers are the sample commit's and drift).
    """
    pins = HELDOUT if pins is None else pins
    out = {"v1": set(), "v1_texts": set(), "incident": set(), "samples": {}}
    raw = {}
    for name, (path, pinned) in pins.items():
        data = read(path)
        got = sha256_hex(data)
        if got != pinned:
            raise HeldOutError("%s: sha256 %s is not the pinned %s" % (path, got, pinned))
        raw[name] = json.loads(data.decode("utf-8"))["sample"]
        out["samples"][path] = {"sha256": got, "rows": len(raw[name])}
    by_digest = {}
    for s in raw["j2c"]:
        out["v1"].add(s["source"])
        out["v1_texts"].add(s["state"])
        by_digest[s["row_digest"]] = s["source"]
    unmapped = [s["row_digest"] for s in raw["j2_v1"] if s["row_digest"] not in by_digest]
    if unmapped:
        raise HeldOutError("%d J2 v1 row(s) have no J2c row to name their source: %s" % (len(unmapped), unmapped[:3]))
    out["v1"].update(by_digest[s["row_digest"]] for s in raw["j2_v1"])
    out["incident"].update(s["state"] for s in raw["ap"])
    # "a count of excluded rows equal to the samples' sizes" needs one identity per sample row
    for name, kind in (("j2_v1", "v1"), ("j2c", "v1"), ("ap", "incident")):
        if len(raw[name]) != len(out[kind]):
            raise HeldOutError("%s: %d rows but %d distinct %s identities" % (pins[name][0], len(raw[name]),
                                                                                len(out[kind]), kind))
    out["v1_texts_scrubbed"] = {scrub(t) for t in out["v1_texts"]}
    return out


def worktree_reader(path):
    return (ROOT / path).read_bytes()


def row_identities(row):
    ids = set()
    for s in row.get("sources") or []:
        if s.get("kind") == "verify_finding":
            ids.add(("v1", "%s#%s" % (s["path"], s["finding_id"])))
        elif s.get("kind") == "incident":
            ids.add(("incident", s["heading"]))
        else:
            raise DatasetError("row %s: unknown source kind %r" % (row.get("item_id"), s.get("kind")))
    if not ids:
        raise DatasetError("row %s: no source identity" % row.get("item_id"))
    return ids


def check_no_heldout(rows, heldout):
    """Refuse (HeldOutLeak) if any row is a held-out row: by source identity, or a v1 state equal to a held-out one."""
    leaks = []
    for row in rows:
        for kind, ident in sorted(row_identities(row)):
            if ident in heldout[kind]:
                leaks.append("%s <- %s %s" % (label_key(row["item_id"], row["question_id"]), kind, ident[:90]))
        if isinstance(row["state"], str) and row["state"] in heldout["v1_texts_scrubbed"]:
            leaks.append("%s <- the text of a held-out J2c row" % label_key(row["item_id"], row["question_id"]))
    if leaks:
        raise HeldOutLeak("%d held-out row(s) in the dataset (D-3): %s" % (len(leaks), "; ".join(leaks[:5])))


def load_dataset(ddir, heldout=None):
    """Read a dataset directory, verify it against its manifest and refuse any held-out row. -> (rows, manifest)"""
    ddir = Path(ddir)
    manifest = json.loads((ddir / MANIFEST_FILE).read_text(encoding="utf-8"))
    data = (ddir / DATASET_FILE).read_bytes()
    got = sha256_hex(data)
    if got != manifest["dataset"]["sha256"]:
        raise DatasetError("%s: sha256 %s is not the manifest's %s" % (ddir / DATASET_FILE, got,
                                                                        manifest["dataset"]["sha256"]))
    rows = [json.loads(line) for line in jsonl_lines(data.decode("utf-8"))]
    if len(rows) != manifest["counts"]["rows_total"]:
        raise DatasetError("%d rows, the manifest says %d" % (len(rows), manifest["counts"]["rows_total"]))
    seen = set()
    for row in rows:
        key = label_key(row["item_id"], row["question_id"])
        if key in seen:
            raise DatasetError("duplicate row %s" % key)
        seen.add(key)
        if row["question_id"] not in QUESTIONS or row["question"] != QUESTIONS[row["question_id"]]:
            raise DatasetError("row %s: the question is not this code's %r" % (key, row["question_id"]))
        if row["state_sha"] != state_sha(row["state"]) or row["question_sha"] != question_sha(row["question"]):
            raise DatasetError("row %s: a digest does not match its content" % key)
        if row["options"] != options(row["question"]):
            raise DatasetError("row %s: options %r are not the question's" % (key, row["options"]))
    check_no_heldout(rows, heldout_identities(worktree_reader) if heldout is None else heldout)
    return rows, manifest


def distribution(answer, question):
    """A teacher answer's full probability distribution in option order, validated and renormalized (the soft target).

    choice: the answer's `probabilities` over exactly the question's options, its `choice` at the maximum;
    noul: [1 - p, p] with p = the answer's `noul`. Every value finite and in [0, 1]; the sum within 0.01 of 1 (a server
    rounds each probability to 4 decimals)."""
    if not isinstance(answer, dict):
        raise LabelError("answer is not an object")
    names = options(question)
    if question["type"] == "choice":
        probs = answer.get("probabilities")
        if not isinstance(probs, dict) or set(probs) != set(names):
            raise LabelError("choice probabilities must name exactly %s" % names)
        values = [probs[n] for n in names]
    else:
        values = [answer.get("noul")]
    for v in values:
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or not 0.0 <= v <= 1.0:
            raise LabelError("probability %r is not a finite number in [0, 1]" % (v,))
    if question["type"] == "noul":
        values = [1.0 - values[0], values[0]]
    else:
        chosen = answer.get("choice")
        if chosen not in names or values[names.index(chosen)] < max(values):
            raise LabelError("choice %r is not the most probable option" % (chosen,))
    total = sum(values)
    if abs(total - 1.0) > 0.01:
        raise LabelError("probabilities sum to %r, not 1" % total)
    return [v / total for v in values]


def read_labels(path):
    """Append-only labels JSONL -> ({key: record}, stats). An unparseable line (a torn write) is skipped and counted;
    a repeated key keeps its FIRST record."""
    path = Path(path)
    records, stats = {}, {"records": 0, "torn": 0, "duplicates": 0}
    if not path.exists():
        return records, stats
    for line in jsonl_lines(path.read_text(encoding="utf-8")):
        try:
            rec = json.loads(line)
            key = rec["key"]
        except (ValueError, KeyError, TypeError):
            stats["torn"] += 1
            continue
        if key in records:
            stats["duplicates"] += 1
            continue
        records[key] = rec
    stats["records"] = len(records)
    return records, stats


def join_labels(rows, labels):
    """(row, target, record) for every row with a label. Refuses (LabelError) a label that names a row but was given
    for another state or question (a stale label), and a target that is not a distribution over the row's options."""
    joined, stale = [], []
    for row in rows:
        rec = labels.get(label_key(row["item_id"], row["question_id"]))
        if rec is None:
            continue
        if rec.get("sent_state_sha") != row["state_sha"] or rec.get("question_sha") != row["question_sha"]:
            stale.append(rec["key"])
            continue
        target = rec.get("target")
        if not isinstance(target, list) or len(target) != len(row["options"]):
            raise LabelError("label %s: target %r does not cover the %d options" % (rec["key"], target,
                                                                                   len(row["options"])))
        for v in target:
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or v < 0:
                raise LabelError("label %s: target value %r" % (rec["key"], v))
        if abs(sum(target) - 1.0) > 1e-6:
            raise LabelError("label %s: target sums to %r" % (rec["key"], sum(target)))
        joined.append((row, target, rec))
    if stale:
        raise LabelError("%d stale label(s) name a row whose state or question changed: %s" % (len(stale), stale[:3]))
    return joined
