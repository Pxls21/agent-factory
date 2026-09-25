#!/usr/bin/env python3
"""Write the labels file of a version-2 dataset from the answers its rows record (task #251; D-083, D-085).

  python3 scripts/laya_ft/recorded_labels.py --dataset DIR --out LABELS.jsonl [--summary SUMMARY.json]

One record per row with a recorded answer, in the record shape teacher_label.py writes and common.join_labels checks:
key, item_id, question_id, question_sha, sent_state_sha (the row's state_sha: nothing is sent), options, target (one-hot
on the recorded answer, in option order), answer (the teacher's answer shape: a choice's `choice` and `probabilities`, a
noul's `noul`), model "recorded", endpoint = the answer's provenance, input_tokens 0, attempts 0, ts = the dataset
commit's time. A row whose sources record no answer gets no label, and so does a row whose sources disagree (counted);
the linked incident sources of a commit row carry no answer. The dataset is read through common.load_dataset (its digest,
its row count and the held-out gate). Pure Python (no torch, no laya); the same dataset gives the same bytes (D-4).
Exit: 0 written; 64 a refused dataset (not version 2, or a load_dataset refusal) or a malformed recorded answer.
"""
import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # scripts/: the laya_ft package
from laya_ft import common as C  # noqa: E402

MODEL = "recorded"
PROVENANCES = ("verifier-class", "heading-cite", "body-cite", "registry-commit", "commit-subject", "not-cited")


def label_record(row, answer, provenance, ts):
    """The label record of one row whose recorded answer is `answer` (an option name)."""
    question, options = row["question"], row["options"]
    if answer not in options:
        raise C.LabelError("row %s: recorded answer %r is not one of its options %s" % (row["item_id"], answer, options))
    target = [1.0 if name == answer else 0.0 for name in options]
    if question["type"] == "choice":
        shaped = {"choice": answer, "probabilities": dict(zip(options, target))}
    else:
        shaped = {"noul": target[1]}
    if C.distribution(shaped, question) != target:   # the teacher path's own reading of the answer gives the same target
        raise C.LabelError("row %s: the answer %r does not read back as its target" % (row["item_id"], shaped))
    return {"key": C.label_key(row["item_id"], row["question_id"]), "item_id": row["item_id"],
            "question_id": row["question_id"], "question_sha": row["question_sha"], "sent_state_sha": row["state_sha"],
            "options": options, "target": target, "answer": shaped, "model": MODEL, "endpoint": provenance,
            "input_tokens": 0, "attempts": 0, "ts": ts}


def recorded(rows, ts):
    """-> (records, stats). A row's answer is the one answer its sources record, its provenance every source's."""
    out, stats = [], {"rows": len(rows), "labeled": 0, "conflicts": 0, "unlabeled": {}, "by_question_answer": {},
                      "by_question_provenance": {}}
    for row in rows:
        sources = [s for s in row["sources"] if s.get("role") != "linked"]
        answers = {s["answer"] for s in sources if "answer" in s}
        if len(answers) != 1:
            if answers:
                stats["conflicts"] += 1
            else:
                key = "%s|%s" % (row["question_id"], sources[0]["kind"])
                stats["unlabeled"][key] = stats["unlabeled"].get(key, 0) + 1
            continue
        answer = answers.pop()
        provs = {p for s in sources if "answer" in s for p in s["provenance"].split("+")}
        unknown = provs - set(PROVENANCES)
        if unknown:
            raise C.LabelError("row %s: unknown provenance %s" % (row["item_id"], sorted(unknown)))
        provenance = "+".join(p for p in PROVENANCES if p in provs)
        out.append(label_record(row, answer, provenance, ts))
        stats["labeled"] += 1
        for field, value in (("by_question_answer", answer), ("by_question_provenance", provenance)):
            key = "%s|%s" % (row["question_id"], value)
            stats[field][key] = stats[field].get(key, 0) + 1
    return out, stats


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dataset", required=True, help="a build_dataset.py --version 2 output directory")
    ap.add_argument("--out", required=True, help="the labels JSONL to write (replaced)")
    ap.add_argument("--summary", help="also write the dataset's summary with the label counts (JSON)")
    args = ap.parse_args(argv)
    try:
        rows, manifest = C.load_dataset(args.dataset)
        if manifest.get("version") != 2:
            raise C.DatasetError("%s is not a version-2 dataset (its rows record no answers)" % args.dataset)
        commit_time = manifest.get("commit_time")
        if type(commit_time) is not int or commit_time <= 0:   # the builder writes git's %ct; nothing else is coerced
            raise C.DatasetError("manifest commit_time %r is not a positive integer" % (commit_time,))
        dsum = Path(args.dataset) / "summary.json"
        if args.summary and not dsum.is_file():   # a version-2 build always writes it: absent is a broken dataset
            raise C.DatasetError("%s has no summary.json" % args.dataset)
        records, stats = recorded(rows, float(commit_time))
    except (C.DatasetError, C.HeldOutLeak, C.HeldOutError, C.LabelError) as e:
        print("recorded_labels: refused: %s: %s" % (type(e).__name__, e), file=sys.stderr)
        return 64
    body = "".join(json.dumps(rec, ensure_ascii=True) + "\n" for rec in records).encode("ascii")
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    tmp = out.with_name(out.name + ".tmp")
    tmp.write_bytes(body)
    os.replace(tmp, out)
    stats["labels"] = {"file": out.name, "sha256": C.sha256_hex(body), "bytes": len(body)}
    stats["dataset"] = {"sha256": manifest["dataset"]["sha256"], "commit": manifest["commit"],
                        "rows_total": manifest["counts"]["rows_total"]}
    if args.summary:
        summary = {"labels": stats, "manifest": {k: manifest[k] for k in ("sources", "heldout", "heading_body_agreement",
                                                                            "counts")},
                   "dataset_summary": json.loads(dsum.read_text(encoding="utf-8"))}
        Path(args.summary).write_text(json.dumps(summary, indent=1, sort_keys=True) + "\n", encoding="ascii")
    print(json.dumps({k: stats[k] for k in ("rows", "labeled", "conflicts", "unlabeled", "labels")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
