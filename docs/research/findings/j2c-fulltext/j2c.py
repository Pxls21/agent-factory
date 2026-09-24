#!/usr/bin/env python3
"""J2c: the J2 v1 sample with the WHOLE finding instead of its 120-character title (J2b section 5.5 path 2; task #233 prep).

POST-HOC like J2b. The same 100 rows as `j2-v1-probe/sample.json` (same order, same labels), each re-joined to its verify
report's finding block through decide-harvest's own parsing helpers (loaded from `scripts/decide-harvest`, never copied), with
the class words masked by the same MASK J2 used (plus any parenthesised qualifier after a masked word; a table row keeps
its title cell only, since its other cells carry the verifier's class notation and dispositions). The output keeps J2's sample format, so the committed J2 scorer runs on it
unchanged: `python3 docs/research/findings/j2-v1-probe/v1_probe.py score --sample <this sample> --url ... --out ...`.
Local only: nothing leaves the machine (Laya answers on a loopback server; a comparator runs as a sandbox agent).

  j2c.py sample [--out sample.json]      join, mask, write (refuses unless all 100 rows join exactly once)
  j2c.py inputs --out DIR                label-free comparator inputs (id + finding text only)
  j2c.py score-answers --answers FILE    score a comparator's {"<id>": "<CLASS>"} answers against the sample's labels
"""
import argparse
import collections
import hashlib
import importlib.machinery
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
J2 = HERE.parent / "j2-v1-probe"
BLOCKING = {"BLOCKER", "CONTRACT-DEFECT"}


def _load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    loader.exec_module(mod)
    return mod


DH = _load("decide_harvest", ROOT / "scripts" / "decide-harvest")
V1 = _load("v1_probe", J2 / "v1_probe.py")


QUALIFIER = re.compile(r"\[CLASS\]\s*\([^)]*\)")


def _mask(text):
    """J2's MASK, then drop a parenthesised qualifier right after a masked class word ("[CLASS] (adjacent)")."""
    return QUALIFIER.sub("[CLASS]", V1.MASK.sub("[CLASS]", text))


def _key(text):
    """Join key: the masked title, whitespace collapsed, lower case, cut to the 120 characters the ledger keeps."""
    return re.sub(r"\s+", " ", V1.MASK.sub("[CLASS]", text)).strip().lower()[:120]


def _blocks(path, text):
    """(finding_id, class, title, block) for every finding decide-harvest's grammar admits (bullets and table rows)."""
    lines = DH._lines(text)
    out = []
    for index, line in enumerate(lines):
        match = DH.BULLET_FINDING_RE.match(line)
        if not match:
            continue
        heading, reason = DH._heading_text(lines, index)
        prefix = f"{match.group('id')} {match.group('class')} — "
        if reason or prefix not in (heading or ""):
            continue
        end = next((j for j in range(index + 1, len(lines))
                    if DH.BULLET_FINDING_RE.match(lines[j]) or DH.MARKDOWN_HEADING_RE.match(lines[j])), len(lines))
        out.append((match.group("id"), match.group("class"), heading.split(prefix, 1)[1], "\n".join(lines[index:end])))
    index = 0
    while index + 1 < len(lines):
        headers = DH._split_table_row(lines[index])
        if (headers and len(headers) >= 2 and headers[0].strip().lower() in {"#", "id"}
                and headers[1].strip().lower() == "class" and DH._is_separator(DH._split_table_row(lines[index + 1]))):
            title_index = DH._title_column(headers)
            row = index + 2
            while row < len(lines):
                cells = DH._split_table_row(lines[row])
                if cells is None:
                    break
                if len(cells) >= len(headers) and title_index is not None:
                    fid, cls = cells[0].strip(), DH._parse_class(cells[1])
                    if DH.FINDING_ID_RE.fullmatch(fid) and cls is not None:
                        # the title cell only: other cells carry the verifier's class notation and dispositions
                        out.append((fid, cls, cells[title_index], cells[title_index]))
                row += 1
            index = row
        else:
            index += 1
    return out


def cmd_sample(args):
    j2 = json.loads((J2 / "sample.json").read_text(encoding="utf-8"))
    git = ["git", "-C", str(ROOT)]
    head = subprocess.run(git + ["rev-parse", "--verify", "HEAD^{commit}"], capture_output=True, text=True,
                          check=True).stdout.strip()  # resolved ONCE; every read below names this commit (AF-AP-175)
    listed = subprocess.run(git + ["ls-tree", "-r", "--name-only", head, "--", "tasks/briefs"], capture_output=True,
                            text=True, check=True).stdout.split()
    paths = sorted(p for p in listed if re.search(r"/VERIFY-[^/]*-report\.md$", p))
    by_lane_class = collections.defaultdict(list)
    for path in paths:
        text = subprocess.run(git + ["show", f"{head}:{path}"], capture_output=True, text=True, check=True).stdout
        lane = DH._report_lane(path)
        for fid, cls, title, block in _blocks(path, text):
            by_lane_class[(lane, cls)].append((_key(title), {"path": path, "finding_id": fid, "block": block}))
    sample, misses, joins = [], [], collections.Counter()
    for row in j2["sample"]:
        key, pool = _key(row["state"]), by_lane_class.get((row["lane"], row["label"]), [])
        hits, how = [e for k, e in pool if k == key], "exact"
        if not hits:  # the ledger redacted or normalized past character 40: a UNIQUE 40-character prefix still joins
            hits, how = [e for k, e in pool if k[:40] == key[:40]], "prefix40"
        if len(hits) != 1:
            misses.append({"row_digest": row["row_digest"], "lane": row["lane"], "hits": len(hits)})
            continue
        joins[how] += 1
        sample.append({"row_digest": row["row_digest"], "label": row["label"], "lane": row["lane"], "join": how,
                       "source": f"{hits[0]['path']}#{hits[0]['finding_id']}",
                       "state": _mask(hits[0]["block"])})
    if misses:
        print(json.dumps({"joined": len(sample), "misses": misses}, indent=1))
        return 2
    body = json.dumps({"from": "j2-v1-probe/sample.json", "head": head, "joins": dict(joins), "n": len(sample),
                       "sample": sample}, sort_keys=True,
                      ensure_ascii=False, indent=1) + "\n"
    Path(args.out).write_text(body, encoding="utf-8")
    lengths = sorted(len(s["state"]) for s in sample)
    print(f"sample: {len(sample)} rows joined; state chars min {lengths[0]} median {lengths[len(lengths) // 2]} "
          f"max {lengths[-1]}; sha256 {hashlib.sha256(body.encode()).hexdigest()}")
    return 0


def cmd_inputs(args):
    sample = json.loads(Path(args.sample).read_text(encoding="utf-8"))["sample"]
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "v1_full_inputs.json").write_text(
        json.dumps([{"id": i, "finding": s["state"]} for i, s in enumerate(sample)], ensure_ascii=False) + "\n",
        encoding="utf-8")
    return 0


def cmd_score_answers(args):
    sample = json.loads(Path(args.sample).read_text(encoding="utf-8"))["sample"]
    answers = json.loads(Path(args.answers).read_text(encoding="utf-8"))
    per = collections.defaultdict(lambda: [0, 0])
    hits = split = tp = fn = fp = tn = 0
    for i, s in enumerate(sample):
        p, g = answers[str(i)], s["label"]
        per[g][1] += 1
        per[g][0] += p == g
        hits += p == g
        split += (p in BLOCKING) == (g in BLOCKING)
        tp += p in BLOCKING and g in BLOCKING
        fn += p not in BLOCKING and g in BLOCKING
        fp += p in BLOCKING and g not in BLOCKING
        tn += p not in BLOCKING and g not in BLOCKING
    n = len(sample)
    print(json.dumps({"n": n, "accuracy": round(hits / n, 4),
                      "balanced_accuracy": round(sum(h / c for h, c in per.values()) / len(per), 4),
                      "blocking_split": round(split / n, 4), "blocking_recall": f"{tp}/{tp + fn}",
                      "false_alarms": f"{fp}/{fp + tn}",
                      "per_class_recall": {k: f"{h}/{c}" for k, (h, c) in sorted(per.items())}}))
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sample")
    s.add_argument("--out", default=str(HERE / "sample.json"))
    i = sub.add_parser("inputs")
    i.add_argument("--sample", default=str(HERE / "sample.json"))
    i.add_argument("--out", required=True)
    a = sub.add_parser("score-answers")
    a.add_argument("--sample", default=str(HERE / "sample.json"))
    a.add_argument("--answers", required=True)
    args = ap.parse_args(argv)
    return {"sample": cmd_sample, "inputs": cmd_inputs, "score-answers": cmd_score_answers}[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
