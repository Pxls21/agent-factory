#!/usr/bin/env python3
"""Build the Laya fine-tune dataset from the committed tree at ONE resolved commit (task #233; brief FT1 D-2, D-3, D-4, D-6).

  /root/venv-laya-probe/bin/python scripts/laya_ft/build_dataset.py --out DIR [--commit REV] [--model-dir DIR] [--repo PATH]
      [--version 1|2]

Version 1 (the default) is described below and is unchanged. Version 2 (task #251; D-083, D-085; the DSV2 brief and its
AMENDMENT 1; `collect_v2`) keeps every row's recorded answer in its SOURCES and never in the state: every finding
decide-harvest admits in the verify reports (its grammar and its families), the incident entries as below, and the
commit messages that add a registry row or cite one in their subject line; it writes summary.json beside the manifest.

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
SUMMARY_FILE = "summary.json"                          # version 2 only: the counts by source, question and label
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
           "entries_without_heading": 0, "repeated_finding_ids": 0}
    excluded_v1, excluded_incident, text_dups, seen = set(), set(), 0, set()
    for path in reports:
        blocks = C.J2C._blocks(path, show(path).decode("utf-8"))
        src["reports_with_findings"] += bool(blocks)
        for fid, _cls, _title, block in blocks:   # the class is the label: never stored (AF-AP-189)
            ident = "%s#%s" % (path, fid)
            if ident in seen:     # a later section restating an id (a reverify's table): the first block is the finding
                src["repeated_finding_ids"] += 1
                continue
            seen.add(ident)
            src["verify_findings"] += 1
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


# ---------- version 2 (task #251; D-083, D-085; brief tasks/briefs/jev-laya/DSV2-brief.md and its AMENDMENT 1) ----------
# Labels are answers our process recorded, kept in each row's SOURCES (never in the state, AF-AP-189): a finding's class
# as its report wrote it; an ap candidate's citation in an incident entry or a commit. D-1 as amended: in a source that
# cites at least one registry row, a candidate it does not cite is a recorded `false` (not-cited), the truth J2's ap test
# scores (ap_probe.py:80). A source that cites nothing labels nothing.
PROVENANCES = ("verifier-class", "heading-cite", "body-cite", "registry-commit", "commit-subject", "not-cited")
MIN_OVERLAP = 40   # normalized characters; a shorter held-out text is too generic to test containment (counted, unused)
LEAKS = (   # AMENDMENT 1 item 8, flagged per row (never a reason to leave one out; task #238 decides)
    ("class-word", re.compile(r"(?i)\b(?:BLOCKER|FOLLOW-UP|INFO|UNVERIFIED|CONTRACT-DEFECT|KNOWN)(?:S|ES)?\b")),
    ("blocking-words", re.compile(r"(?i)\bblocks? (?:the )?(?:merge|landing|push)\b|\bdoes not block\b"
                                  r"|\bnot (?:a |an )?\[CLASS\]|\[CLASS\] predicate|\bblocking predicate\b"
                                  r"|\bgate recommendation\b|\b(?:MERGE-READY|NOT-READY|CONTRACT-INVALID)\b"
                                  # DSV2-R1 (VERIFY-DSV2 V-6): the five ruled forms, F-a to F-e, each with its own flags
                                  r"|\bcontract[- ]mapp|\bcanonical(?: path| reproduction)?\s*[:=]"   # F-a the walk
                                  r"|\bmaterial(?: effect)?\s*[:=]|\bdiscriminator\s*[:=]|\btask ownership\b"
                                  r"|\bin[- ]boundary\s*[:=]"
                                  r"|(?-i:\bNo \[CLASS\])"   # F-b a class summary (case-sensitive, as ruled)
                                  r"|\b(?:does not|doesn't|do not|did not|would not|will not|cannot) block\b"   # F-c
                                  r"|\b(?:is|as) (?:a |an )?\[CLASS\]"   # F-d the class stated
                                  r"|\bno material effect\b|\bnot material\b|\bimmaterial\b")),   # F-e materiality
)
AP_ID_LEAK = re.compile(r"AF-AP-\d")


def overlap_norm(text):
    """The overlap test's one normal form, for held-out texts and training states alike: class words and AF-AP ids
    masked as the states mask them, scrubbed, lower case, whitespace collapsed."""
    return " ".join(C.scrub(C.AP.AP_ID.sub(MASK_ID, C.J2C._mask(text))).lower().split())


class Overlap:
    """D-3 by text: a training state that CONTAINS a held-out finding's text (a J2c whole block or a J2 v1 title) or a
    held-out entry's text (an AP heading), after overlap_norm. Held-out texts under MIN_OVERLAP are not used."""

    def __init__(self, texts):
        normed = {overlap_norm(t) for t in texts}
        self.texts = sorted(t for t in normed if len(t) >= MIN_OVERLAP)
        self.unused = sorted(t for t in normed if len(t) < MIN_OVERLAP)

    def hit(self, *state_texts):
        normed = [overlap_norm(s) for s in state_texts]
        return next((t for t in self.texts for s in normed if t in s), None)


def heldout_texts(show, pins):
    """The texts D-3 holds out: every J2c state (whole blocks), every J2 v1 state (titles), every AP state (headings)."""
    pins = C.HELDOUT if pins is None else pins
    out = []
    for name in ("j2c", "j2_v1", "ap"):
        out += [s["state"] for s in json.loads(show(pins[name][0]).decode("utf-8"))["sample"]]
    return out


def registry_names(lines):
    """AF-AP id -> the registry row's name: its mechanism cell up to the first " — " (the row's title)."""
    out = {}
    for line in lines:
        m = C.AP.ROW.match(line)
        if m:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 2:
                out["AF-AP-" + m.group(1)] = cells[1].split(" — ", 1)[0].replace("**", "").replace("`", "").strip()
    return out


def v2_findings(path, text):
    """Every finding decide-harvest admits in one verify report, first occurrence per id: the grammar's blocks as j2c.py
    cuts them (version 1's states), then the families' (decide-harvest's _family_findings, whose block end is theirs).
    -> [(finding_id, class, block, family, block_end)], and the not-admitted counts by reason."""
    dh = C.J2C.DH
    lines = dh._lines(text)
    records = dh._grammar_records(lines)
    family = dh._family_findings(lines, records)
    grammar_refused = {r[0] for r in records if not r[1]}
    admitted = {f.line for f in family if f.reason is None}
    out, seen, refused = [], set(), {}
    for fid, cls, _title, block in C.J2C._blocks(path, text):
        if fid not in seen:
            seen.add(fid)
            out.append((fid, cls, block, "grammar", None))
    for f in family:   # as decide-harvest counts them: a grammar refusal no family admits keeps its own reason
        if f.reason is None:
            out.append((f.finding_id, f.finding_class, f.text, f.family, f.block_end))
        elif f.line not in grammar_refused:   # ambiguous-class, or restated (not a refusal; counted for the summary)
            refused[f.reason] = refused.get(f.reason, 0) + 1
    for r in records:
        if not r[1] and r[0] not in admitted:
            refused[r[4]] = refused.get(r[4], 0) + 1
    return out, refused


def commit_log(git, sha):
    """The commits reachable from sha, in git log order: [(sha, message)], and per commit the registry rows it adds and the
    masked headings of the incident entries it adds (anchors on its `+` lines, the heading read from the new side of the
    hunk; 10 lines of context keep a wrapped heading whole)."""
    raw = git("log", "--no-show-signature", "--format=%H%x00%B%x01", sha).decode("utf-8")
    commits = []
    for rec in raw.split("\x01"):
        rec = rec.lstrip("\n")
        if rec:
            h, msg = rec.split("\x00", 1)
            commits.append((h, msg.rstrip()))
    added, removed, linked = {}, {}, {}
    cur, hunk = None, None

    def close_hunk():
        if cur and hunk:
            new_side = [text for text, _plus in hunk]
            for k, (text, plus) in enumerate(hunk):
                if plus and C.AP.ANCHOR.match(text):
                    heading = C.AP.heading(new_side, k)
                    if heading:
                        linked.setdefault(cur, set()).add(C.AP.AP_ID.sub(MASK_ID, heading))

    patch = git("log", "-p", "-U10", "--no-color", "--no-ext-diff", "--no-show-signature", "--format=@@COMMIT %H", sha,
                "--", C.INCIDENT_LOG)
    for line in patch.decode("utf-8", "replace").split("\n"):
        if line.startswith("@@COMMIT "):
            close_hunk()
            cur, hunk = line.split()[1], None
        elif line.startswith("diff --git "):   # a file's headers follow, until its first hunk (AF-AP-200)
            close_hunk()
            hunk = None
        elif line.startswith("@@ "):
            close_hunk()
            hunk = []
        elif hunk is not None and line[:1] in ("+", " "):   # inside a hunk the first character is the whole type:
            hunk.append((line[1:], line[0] == "+"))           # an added line may itself start "++"
            m = re.match(r"^\+\|\s*AF-AP-(\d+)\s*\|", line)
            if m:
                added.setdefault(cur, set()).add("AF-AP-" + m.group(1))
        elif hunk is not None and line[:1] == "-":
            m = re.match(r"^-\|\s*AF-AP-(\d+)\s*\|", line)
            if m:
                removed.setdefault(cur, set()).add("AF-AP-" + m.group(1))
    close_hunk()
    adds = {h: rows - removed.get(h, set()) for h, rows in added.items()}
    return commits, adds, linked


def _ap_answer(rid, cited):
    """(answer, provenance) of one candidate against its source's citations {row: provenance}; None: no recorded answer."""
    if rid in cited:
        return ("true", cited[rid]) if cited[rid] else (None, None)
    return ("false", "not-cited") if any(cited.values()) else (None, None)


def collect_v2(git, rev="HEAD", pins=None):
    """Version 2's sources at one commit. -> (items, info); an item is (prefix, question_id, state, sources) as in
    collect, each source carrying its recorded `answer` and `provenance` when it has one."""
    sha = git("rev-parse", "--verify", "%s^{commit}" % rev).decode("ascii").strip()

    def show(path):
        return git("show", "%s:%s" % (sha, path))

    heldout = C.heldout_identities(show, pins)
    overlap = Overlap(heldout_texts(show, pins))
    listed = git("ls-tree", "-r", "-z", "--name-only", sha, "--", "tasks/briefs").decode("utf-8").split("\0")
    reports = sorted(p for p in listed if C.J2C.DH._kind(p) == "verify_report")
    items, notes = [], {"not_admitted": {}, "findings_by_family": {}, "capped_blocks": 0}
    excl = {"identity": {"verify_finding": 0, "incident": 0, "commit": 0},
            "text": {"verify_finding": 0, "incident": 0, "commit": 0}}
    excluded_v1, excluded_incident = set(), set()
    for path in reports:
        findings, refused = v2_findings(path, show(path).decode("utf-8"))
        for reason, n in refused.items():
            notes["not_admitted"][reason] = notes["not_admitted"].get(reason, 0) + n
        for fid, cls, block, family, block_end in findings:
            notes["findings_by_family"][family] = notes["findings_by_family"].get(family, 0) + 1
            ident = "%s#%s" % (path, fid)
            if ident in heldout["v1"]:
                excluded_v1.add(ident)
                continue
            masked = C.J2C._mask(block)
            if overlap.hit(masked):
                excl["text"]["verify_finding"] += 1
                continue
            state = C.scrub(masked)
            src = {"kind": "verify_finding", "path": path, "finding_id": fid, "family": family}
            if block_end == "cap":
                src["block_end"] = "cap"
                notes["capped_blocks"] += 1
            blocking = "true" if cls in C.V1.BLOCKING else "false"
            for qid, answer in (("v1.finding_class", cls), ("v1.blocking", blocking)):
                items.append(("v1", qid, state, [dict(src, answer=answer, provenance="verifier-class")]))
    lines = show(C.INCIDENT_LOG).decode("utf-8").splitlines()
    registry = C.AP.registry(lines)
    row_tokens = {rid: C.AP.tokens(text) for rid, text in registry.items()}
    stats = {"incident_entries": 0, "entries_without_heading": 0, "entries_citing": 0, "entries_all_cited_outside_16": 0,
             "commits": 0, "commits_citing": 0, "commits_admitted": {"registry-commit": 0, "commit-subject": 0},
             "commits_body_only_not_admitted": 0, "commits_all_cited_outside_16": 0,
             "commit_rows_unlabeled_body_cite": 0}
    agreement = {"entries_with_both": 0, "same_set": 0, "heading_subset_of_body": 0, "body_subset_of_heading": 0,
                 "other": 0}
    for i, line in enumerate(lines):
        if not C.AP.ANCHOR.match(line):
            continue
        stats["incident_entries"] += 1
        heading = C.AP.heading(lines, i)
        if not heading:
            stats["entries_without_heading"] += 1
            continue
        masked_heading = C.AP.AP_ID.sub(MASK_ID, heading)
        if masked_heading in heldout["incident"]:
            excluded_incident.add(masked_heading)
            continue
        entry = "\n".join(lines[i:entry_end(lines, i)])
        query = C.scrub(C.AP.AP_ID.sub(MASK_ID, entry))
        if overlap.hit(query):
            excl["text"]["incident"] += 1
            continue
        opening = line.find("**")
        rest = entry[opening + 2:]
        close = rest.find("**")
        body = entry[:opening] + rest[close + 2:]
        h_ids = {"AF-AP-" + n for n in C.AP.AP_ID.findall(heading)} & set(registry)
        b_ids = {"AF-AP-" + n for n in C.AP.AP_ID.findall(body)} & set(registry)
        if h_ids and b_ids:
            agreement["entries_with_both"] += 1
            agreement["same_set" if h_ids == b_ids else "heading_subset_of_body" if h_ids < b_ids
                      else "body_subset_of_heading" if b_ids < h_ids else "other"] += 1
        cited = {rid: "+".join(p for p, ids in (("heading-cite", h_ids), ("body-cite", b_ids)) if rid in ids)
                 for rid in h_ids | b_ids}
        candidates = rank(query, registry, row_tokens)
        stats["entries_citing"] += bool(cited)
        stats["entries_all_cited_outside_16"] += bool(cited) and not set(cited) & set(candidates)
        for rid in candidates:
            src = {"kind": "incident", "line": i + 1, "heading": masked_heading, "row": rid}
            answer, prov = _ap_answer(rid, cited)
            if answer:
                src.update(answer=answer, provenance=prov)
            items.append(("ap", "ap.violates_row", {"query": query, "chunk": C.scrub(registry[rid])}, [src]))
    commits, adds, linked = commit_log(git, sha)
    for h, msg in commits:
        stats["commits"] += 1
        ids = {"AF-AP-" + n for n in C.AP.AP_ID.findall(msg)} & set(registry)
        added = adds.get(h, set()) & set(registry)
        if not ids and not added:
            continue
        stats["commits_citing"] += 1
        subject = {"AF-AP-" + n for n in C.AP.AP_ID.findall(msg.split("\n", 1)[0])} & set(registry)
        if not added and not subject:
            stats["commits_body_only_not_admitted"] += 1
            continue
        heads = sorted(linked.get(h, set()))
        if set(heads) & heldout["incident"]:
            excl["identity"]["commit"] += 1
            continue
        query = C.scrub(C.AP.AP_ID.sub(MASK_ID, msg))
        if overlap.hit(query):
            excl["text"]["commit"] += 1
            continue
        stats["commits_admitted"]["registry-commit" if added else "commit-subject"] += 1
        cited = {rid: "registry-commit" for rid in added}
        cited.update({rid: "commit-subject" for rid in subject - added})
        cited.update({rid: "" for rid in ids - subject - added})   # cited in the body only: no recorded answer
        candidates = rank(query, registry, row_tokens)
        stats["commits_all_cited_outside_16"] += not {r for r, p in cited.items() if p} & set(candidates)
        linked_sources = [{"kind": "incident", "heading": hd, "role": "linked"} for hd in heads]
        for rid in candidates:
            src = {"kind": "commit", "commit": h, "row": rid}
            answer, prov = _ap_answer(rid, cited)
            if answer:
                src.update(answer=answer, provenance=prov)
            elif rid in cited:
                stats["commit_rows_unlabeled_body_cite"] += 1
            items.append(("ap", "ap.violates_row", {"query": query, "chunk": C.scrub(registry[rid])},
                          [src] + linked_sources))
    excl["identity"]["verify_finding"] = len(excluded_v1)
    excl["identity"]["incident"] = len(excluded_incident)
    if len(excluded_v1) != len(heldout["v1"]) or len(excluded_incident) != len(heldout["incident"]):
        raise C.HeldOutError(
            "at %s the build excluded %d of %d held-out findings and %d of %d held-out incident entries; not found: %s"
            % (sha, len(excluded_v1), len(heldout["v1"]), len(excluded_incident), len(heldout["incident"]),
               sorted(heldout["v1"] - excluded_v1)[:3] + sorted(heldout["incident"] - excluded_incident)[:3]))
    info = {"commit": sha, "heldout": heldout, "reports": len(reports), "ap": stats, "agreement": agreement,
            "excluded": excl, "overlap_texts": {"used": len(overlap.texts), "under_min": len(overlap.unused)},
            "registry_rows": len(registry), "names": registry_names(lines), **notes}
    return items, info


def flag_leaks(rows, names):
    """AMENDMENT 1 item 8: flag, in every source of a row, what its final state still says about the label."""
    counts = {}
    for row in rows:
        kinds = []
        if row["question_id"].startswith("v1."):
            kinds = [kind for kind, rx in LEAKS if rx.search(row["state"])]
        else:
            if AP_ID_LEAK.search(row["state"]["query"]) or AP_ID_LEAK.search(row["state"]["chunk"]):
                kinds.append("ap-id")
            rid = row["sources"][0]["row"]
            name = overlap_norm(names.get(rid, ""))
            if (any(s.get("answer") == "true" for s in row["sources"]) and len(name) >= 12
                    and name in overlap_norm(row["state"]["query"])):
                kinds.append("row-name")
        if kinds:
            for s in row["sources"]:
                if s.get("role") != "linked":
                    s["leak"] = "+".join(kinds)
            for kind in kinds:
                key = "%s|%s" % (row["question_id"], kind)
                counts[key] = counts.get(key, 0) + 1
    return counts


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


def _write(out, files):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for name, data in files:
        tmp = out / (name + ".tmp")
        tmp.write_bytes(data)
        os.replace(tmp, out / name)


def summarize_v2(rows):
    """Counts by source kind, question, recorded answer and provenance; the label's class balance per question (D-3:
    reported, never rebalanced); leaks by kind; unlabeled rows by source kind."""
    by, classes, unlabeled, leaks = {}, {}, {}, {}
    for row in rows:
        qid = row["question_id"]
        for s in row["sources"]:
            if s.get("role") == "linked":
                continue
            key = "%s|%s|%s|%s" % (s["kind"], qid, s.get("answer", "-"), s.get("provenance", "-"))
            by[key] = by.get(key, 0) + 1
            if "leak" in s:
                for kind in s["leak"].split("+"):
                    k = "%s|%s|%s|%s" % (s["kind"], qid, s.get("provenance", "-"), kind)
                    leaks[k] = leaks.get(k, 0) + 1
        answers = {s["answer"] for s in row["sources"] if "answer" in s}
        if len(answers) == 1:
            k = "%s|%s" % (qid, answers.pop())
            classes[k] = classes.get(k, 0) + 1
        else:
            k = "%s|%s" % (qid, "conflict" if answers else row["sources"][0]["kind"])
            unlabeled[k] = unlabeled.get(k, 0) + 1
    return {"rows_by_source_question_answer_provenance": by, "labels_by_question_answer": classes,
            "unlabeled_by_question": unlabeled, "leaks_by_source_question_provenance_kind": leaks}


def build_v2(repo, rev, model_dir, out):
    git = git_runner(repo)
    items, info = collect_v2(git, rev)
    fitter = Fitter(model_dir)
    rows, fitted = fit_rows(items, fitter)
    C.check_no_heldout(rows, info["heldout"])   # the loader's gate (identities; a commit's linked incident entries)
    overlap = Overlap(heldout_texts(lambda p: git("show", "%s:%s" % (info["commit"], p)), None))
    hits = [r["item_id"] for r in rows if overlap.hit(*(r["state"].values() if isinstance(r["state"], dict)
                                                        else [r["state"]]))]
    if hits:   # the second D-3 check by text, on the rows as written
        raise C.HeldOutLeak("%d row(s) hold a held-out text (D-3): %s" % (len(hits), hits[:3]))
    leak_counts = flag_leaks(rows, info["names"])
    body = "".join(json.dumps(row, ensure_ascii=True) + "\n" for row in rows).encode("ascii")
    counts = {qid: sum(r["question_id"] == qid for r in rows) for qid in C.QUESTIONS}
    summary = dict(summarize_v2(rows), commit=info["commit"], leaks=leak_counts)
    manifest = {
        "version": 2,
        "commit": info["commit"],
        "commit_time": int(git("show", "-s", "--no-show-signature", "--format=%ct", info["commit"]).decode().strip()),
        "sources": {"verify_reports": info["reports"], "findings_by_family": info["findings_by_family"],
                    "capped_blocks": info["capped_blocks"], "not_admitted": info["not_admitted"],
                    "registry_rows": info["registry_rows"], "ap": info["ap"], "candidates_per_source": C.AP.TOP_K},
        "heldout": {"samples": info["heldout"]["samples"],
                    "verify_findings": {"identities": len(info["heldout"]["v1"]),
                                        "excluded": info["excluded"]["identity"]["verify_finding"]},
                    "incident_entries": {"identities": len(info["heldout"]["incident"]),
                                         "excluded": info["excluded"]["identity"]["incident"]},
                    "excluded": info["excluded"], "overlap_texts": info["overlap_texts"]},
        "heading_body_agreement": info["agreement"],
        "counts": {"rows": counts, "rows_total": len(rows), **fitted},
        "model": fitter.fingerprint,
        "questions": {qid: C.question_sha(q) for qid, q in C.QUESTIONS.items()},
        "code": {p: C.sha256_hex((C.ROOT / p).read_bytes()) for p in CODE},
        "dataset": {"file": C.DATASET_FILE, "sha256": C.sha256_hex(body), "bytes": len(body)},
    }
    _write(out, ((C.DATASET_FILE, body),
                 (C.MANIFEST_FILE, (json.dumps(manifest, indent=1, sort_keys=True) + "\n").encode("ascii")),
                 (SUMMARY_FILE, (json.dumps(summary, indent=1, sort_keys=True) + "\n").encode("ascii"))))
    return manifest


def build(repo, rev, model_dir, out, version=1):
    if version == 2:
        return build_v2(repo, rev, model_dir, out)
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
    ap.add_argument("--version", type=int, choices=(1, 2), default=1,
                    help="1: the FT1 dataset (default, unchanged); 2: recorded answers in the sources (D-083, D-085)")
    args = ap.parse_args(argv)
    m = build(Path(args.repo), args.commit, Path(args.model_dir), Path(args.out), args.version)
    print(json.dumps({k: m[k] for k in ("commit", "sources", "heldout", "counts", "dataset")}, indent=1, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
