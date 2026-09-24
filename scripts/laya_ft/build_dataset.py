#!/usr/bin/env python3
"""Build the Laya fine-tune dataset from the committed tree at ONE resolved commit (task #233; brief FT1 D-2, D-3, D-4, D-6).

  /root/venv-laya-probe/bin/python scripts/laya_ft/build_dataset.py --out DIR [--commit REV] [--model-dir DIR] [--repo PATH]

Run it with the Laya venv's python: the window fit reads Laya's own tokenizer and `build_sequence`.
Every source is read at one commit: `rev-parse --verify <REV>^{commit}` once, and every later read names that sha
(AF-AP-175). The sources:
  - every finding decide-harvest's grammar admits in the committed `tasks/briefs/**/VERIFY-*-report.md`: the WHOLE finding
    block as j2c.py cuts it (a table row keeps its title cell only), class words masked by j2c's `_mask`. Two rows each:
    `v1.finding_class` (one choice over v1_probe's six CLASSES, in J2's wording) and `v1.blocking` (one noul, D-6(b));
  - every anchored entry of `docs/INCIDENT-LOG.md`: the WHOLE entry (the anchor line and its continuation lines), AF-AP ids
    masked as ap_probe masks them. One `ap.violates_row` noul row per candidate, the candidates being the lexical top 16 of
    the registry ranked exactly as ap_probe.py ranks them, the state `{"query": entry, "chunk": row text}` (the local
    server's per-chunk fan-out shape, the one J2 scored).
The verifier's class is never stored and the ledger is never read (AF-AP-189). Every state string passes
transcript_export.scrub before it is stored: the dataset holds exactly what leaves the machine. The J2, J2c and AP samples
are held out by source identity (report path + finding id; the masked incident heading): the build refuses unless it
excluded exactly as many rows as the samples hold, and a second check refuses any held-out row left in the output. A state
longer than Laya's window is cut (the finding text, or the query; never the chunk) until build_sequence keeps all of it
(D-076(b), F-24: a long query pushed every chunk out of the window and tied their scores). Output: dataset.jsonl (one row
per item and question, ASCII JSON) and manifest.json; both are byte-identical for the same commit, code and model.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))   # scripts/: the laya_ft package
from laya_ft import common as C  # noqa: E402

REPORT_RX = re.compile(r"/VERIFY-[^/]*-report\.md$")   # j2c.py's report set (and the brief's premise count)
MASK_ID = "AF-AP-?"                                    # ap_probe.py cmd_sample's mask for an AF-AP id
CODE = ("scripts/laya_ft/build_dataset.py", "scripts/laya_ft/common.py", "docs/research/findings/j2c-fulltext/j2c.py",
        "docs/research/findings/j2-v1-probe/v1_probe.py", "docs/research/findings/ap-hawk-probe/ap_probe.py",
        "scripts/decide-harvest", "scripts/transcript_export.py")


def git_runner(repo):
    def git(*args):
        return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True).stdout
    return git


def entry_end(lines, start):
    """An incident entry runs from its anchor line to the next blank line, anchor or markdown heading."""
    j = start + 1
    while (j < len(lines) and lines[j].strip() and not C.AP.ANCHOR.match(lines[j])
           and not C.J2C.DH.MARKDOWN_HEADING_RE.match(lines[j])):
        j += 1
    return j


def rank(query, registry, row_tokens):
    """The lexical top 16, with ap_probe.py cmd_score's own sort key (overlap, then the row number)."""
    q = C.AP.tokens(query)
    return sorted(registry, key=lambda rid: (-len(q & row_tokens[rid]), int(rid.split("-")[-1])))[:C.AP.TOP_K]


def collect(git, rev="HEAD", pins=None):
    """Read the sources at one commit. -> (items, info); an item is (prefix, question_id, state, sources).
    `pins` defaults to the three committed held-out samples (common.HELDOUT); a test passes its own."""
    sha = git("rev-parse", "--verify", "%s^{commit}" % rev).decode("ascii").strip()

    def show(path):
        return git("show", "%s:%s" % (sha, path))

    heldout = C.heldout_identities(show, pins)
    listed = git("ls-tree", "-r", "-z", "--name-only", sha, "--", "tasks/briefs").decode("utf-8").split("\0")
    reports = sorted(p for p in listed if REPORT_RX.search(p))
    items = []
    src = {"verify_reports": len(reports), "reports_with_findings": 0, "verify_findings": 0, "incident_entries": 0,
           "entries_without_heading": 0}
    excluded_v1, excluded_incident, text_dups = set(), set(), 0
    for path in reports:
        blocks = C.J2C._blocks(path, show(path).decode("utf-8"))
        src["reports_with_findings"] += bool(blocks)
        for fid, _cls, _title, block in blocks:   # the class is the label: never stored (AF-AP-189)
            src["verify_findings"] += 1
            ident = "%s#%s" % (path, fid)
            if ident in heldout["v1"]:
                excluded_v1.add(ident)
                continue
            masked = C.J2C._mask(block)
            if masked in heldout["v1_texts"]:   # the same finding under another path or id
                text_dups += 1
                continue
            state = C.scrub(masked)
            for qid in ("v1.finding_class", "v1.blocking"):
                items.append(("v1", qid, state, [{"kind": "verify_finding", "path": path, "finding_id": fid}]))
    lines = show(C.INCIDENT_LOG).decode("utf-8").splitlines()   # as ap_probe.py reads the log
    registry = C.AP.registry(lines)
    row_tokens = {rid: C.AP.tokens(text) for rid, text in registry.items()}
    for i, line in enumerate(lines):
        if not C.AP.ANCHOR.match(line):
            continue
        src["incident_entries"] += 1
        heading = C.AP.heading(lines, i)
        if not heading:
            src["entries_without_heading"] += 1
            continue
        masked_heading = C.AP.AP_ID.sub(MASK_ID, heading)
        if masked_heading in heldout["incident"]:
            excluded_incident.add(masked_heading)
            continue
        query = C.scrub(C.AP.AP_ID.sub(MASK_ID, "\n".join(lines[i:entry_end(lines, i)])))
        for rid in rank(query, registry, row_tokens):
            items.append(("ap", "ap.violates_row", {"query": query, "chunk": C.scrub(registry[rid])},
                          [{"kind": "incident", "line": i + 1, "heading": masked_heading, "row": rid}]))
    if len(excluded_v1) != len(heldout["v1"]) or len(excluded_incident) != len(heldout["incident"]):
        raise C.HeldOutError(
            "at %s the build excluded %d of %d held-out findings and %d of %d held-out incident entries; not found: %s"
            % (sha, len(excluded_v1), len(heldout["v1"]), len(excluded_incident), len(heldout["incident"]),
               sorted(heldout["v1"] - excluded_v1)[:3] + sorted(heldout["incident"] - excluded_incident)[:3]))
    info = {"commit": sha, "heldout": heldout, "sources": dict(src, registry_rows=len(registry),
                                                               candidates_per_entry=C.AP.TOP_K),
            "excluded": {"verify_findings": len(excluded_v1), "incident_entries": len(excluded_incident),
                         "text_duplicates": text_dups}}
    return items, info


class Fitter:
    """Laya's window, read from the checkpoint: sequences exactly as Agent.system_one builds them."""

    def __init__(self, model_dir):
        from laya.agent import Agent
        from laya.common import build_sequence, serialize_state
        from transformers import AutoTokenizer

        self.model_dir = Path(model_dir)
        self.fingerprint = C.model_fingerprint(self.model_dir)
        self.max_len, self.head_max_len = self.fingerprint["max_len"], self.fingerprint["head_max_len"]
        self.tok = AutoTokenizer.from_pretrained(str(self.model_dir / "tokenizer"))
        self._build, self._serialize, self._internal = build_sequence, serialize_state, Agent._to_internal

    def _tokens(self, state):
        # build_sequence's own state tokenization (laya/common.py): the mask token blanked, no special tokens
        text = self._serialize(state).replace(self.tok.mask_token, " ")
        return len(self.tok(text, add_special_tokens=False)["input_ids"])

    def fit(self, state, question):
        """-> (state, cut); the state unchanged when build_sequence keeps all of it, else its text (a finding, or the
        query) cut to the longest prefix it keeps whole, and cut = {"chars_from", "chars_to"}."""
        q = self._internal(question)
        empty = len(self._build(self.tok, "", q, self.max_len, self.head_max_len)[0])

        def fits(s):   # the consumer's verdict: build_sequence dropped no state token
            return len(self._build(self.tok, s, q, self.max_len, self.head_max_len)[0]) == empty + self._tokens(s)

        if fits(state):
            return state, None
        text = state if isinstance(state, str) else state["query"]

        def cut_to(n):
            return text[:n] if isinstance(state, str) else {"query": text[:n], "chunk": state["chunk"]}

        if not fits(cut_to(0)):
            raise ValueError("the chunk alone overflows Laya's window: %r" % (state.get("chunk", "")[:80],))
        lo, hi = 0, len(text)   # cut_to(lo) fits, cut_to(hi) does not
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if fits(cut_to(mid)):
                lo = mid
            else:
                hi = mid
        return cut_to(lo), {"chars_from": len(text), "chars_to": lo}

def make_row(prefix, qid, state, sources, cut):
    q = C.QUESTIONS[qid]
    ssha = C.state_sha(state)
    row = {"item_id": "%s-%s" % (prefix, ssha[:20]), "question_id": qid, "question_sha": C.question_sha(q),
           "state_sha": ssha, "options": C.options(q), "question": q, "state": state, "sources": sources}
    if cut:
        row["cut"] = cut
    return row


def fit_rows(items, fitter):
    """Fit every item to the window and merge identical (state, question) rows (their sources are kept)."""
    rows, by_key, merged = [], {}, 0
    cuts = {qid: 0 for qid in C.QUESTIONS}
    for prefix, qid, state, sources in items:
        state, cut = fitter.fit(state, C.QUESTIONS[qid])
        cuts[qid] += cut is not None
        row = make_row(prefix, qid, state, sources, cut)
        key = C.label_key(row["item_id"], qid)
        if key in by_key:
            by_key[key]["sources"].extend(s for s in sources if s not in by_key[key]["sources"])
            merged += 1
            continue
        by_key[key] = row
        rows.append(row)
    return rows, {"cut_to_window": cuts, "merged_duplicates": merged}


def build(repo, rev, model_dir, out):
    items, info = collect(git_runner(repo), rev)
    fitter = Fitter(model_dir)
    rows, fitted = fit_rows(items, fitter)
    C.check_no_heldout(rows, info["heldout"])   # the second D-3 check, on the rows as written
    body = "".join(json.dumps(row, ensure_ascii=True) + "\n" for row in rows).encode("ascii")
    counts = {qid: sum(r["question_id"] == qid for r in rows) for qid in C.QUESTIONS}
    manifest = {
        "commit": info["commit"],
        "sources": info["sources"],
        "heldout": {"samples": info["heldout"]["samples"],
                    "verify_findings": {"identities": len(info["heldout"]["v1"]),
                                        "excluded": info["excluded"]["verify_findings"]},
                    "incident_entries": {"identities": len(info["heldout"]["incident"]),
                                         "excluded": info["excluded"]["incident_entries"]},
                    "text_duplicates_excluded": info["excluded"]["text_duplicates"]},
        "counts": {"rows": counts, "rows_total": len(rows),
                   "trainable_findings": len({r["item_id"] for r in rows if r["question_id"].startswith("v1.")}),
                   "trainable_entries": len({r["sources"][0]["line"] for r in rows
                                             if r["question_id"] == "ap.violates_row"}),
                   **fitted},
        "model": fitter.fingerprint,
        "questions": {qid: C.question_sha(q) for qid, q in C.QUESTIONS.items()},
        "code": {p: C.sha256_hex((C.ROOT / p).read_bytes()) for p in CODE},
        "dataset": {"file": C.DATASET_FILE, "sha256": C.sha256_hex(body), "bytes": len(body)},
    }
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for name, data in ((C.DATASET_FILE, body),
                       (C.MANIFEST_FILE, (json.dumps(manifest, indent=1, sort_keys=True) + "\n").encode("ascii"))):
        tmp = out / (name + ".tmp")
        tmp.write_bytes(data)
        os.replace(tmp, out / name)
    return manifest


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", required=True, help="output directory (dataset.jsonl, manifest.json)")
    ap.add_argument("--repo", default=str(C.ROOT))
    ap.add_argument("--commit", default="HEAD", help="the revision to resolve ONCE (default HEAD)")
    ap.add_argument("--model-dir", default=C.DEFAULT_MODEL_DIR, help="the Laya typed-decisions snapshot directory")
    args = ap.parse_args(argv)
    m = build(Path(args.repo), args.commit, Path(args.model_dir), Path(args.out))
    print(json.dumps({k: m[k] for k in ("commit", "sources", "heldout", "counts", "dataset")}, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
