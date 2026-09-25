"""FT1: the Laya fine-tune tooling (scripts/laya_ft/; task #233; brief tasks/briefs/jev-laya/FT1-brief.md).

Deterministic and LLM-free; no network beyond 127.0.0.1. Two venues:
- this interpreter: the masking, the scrub, the held-out rule (D-3), the commit resolved once (D-4), the ap ranking against
  the committed lexical picks, the label format and join, the evaluator's comparisons, and the teacher client (resume,
  rate limit, retry, key handling, scrub) against a local stand-in HTTP server, a double for the NETWORK only (the live
  API is exercised by the lane's `--limit 5` smoke, never here); FT1-F (VERIFY-FT1 F-1): train.main's parse-time
  refusal of --lr, --weight-decay and --max-grad-norm outside their domains, and the evaluator's refusal of a served
  probability that is not a finite float;
- the Laya venv, as subprocesses: the builder's determinism and window fit on the real tree, and the trainer on the REAL
  model on CPU (three steps lower the loss, the checkpoint round trip, head mode's frozen encoder, the loss's sign);
  FT1-F (F-1, F-4, F-6): the finiteness and free-space guards on crafted tensors (torch lives only in this venv, so they
  cannot run in CI), and train.main and evaluate.main on the real model with a fault injected by the test (a NaN written
  into a trained parameter after a real step or after the first served answer; a filesystem that reports 40 MiB free).
The Laya venv and snapshot are DECLARED inputs of the sandbox venue (S0_01_VENUE, which scripts/test_summary.sh exports):
absent there = FAIL. CI declares no venue, so those tests skip loudly; the PC's Laya paths are not declared to this file,
so they skip loudly there too.
"""
import argparse
import copy
import http.server
import json
import os
import re
import subprocess
import sys
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from laya_ft import build_dataset as BD  # noqa: E402
from laya_ft import common as C  # noqa: E402
from laya_ft import evaluate as EV  # noqa: E402
from laya_ft import teacher_label as TL  # noqa: E402
from laya_ft import train as TR  # noqa: E402   (imports no torch: its parse-time checks run in CI)

FINDINGS = ROOT / "docs" / "research" / "findings"
# the oracle's own copy of J2's class words (J2 section 2): none may survive in a v1 state
CLASS_WORDS = re.compile(r"\b(BLOCKER|FOLLOW-UP|INFO|UNVERIFIED|CONTRACT-DEFECT|KNOWN|BLOCKING|NON-BLOCKING)\b", re.I)
# FAKE secrets, never real ones (the brief's QZJ8/X4Z9 style); the value is what must never leave
FAKE_KEY = "QZJ8-fake-api-key-5c1d9e7a"
FAKE_SECRETS = {"token=QZJ8fakefakefake1234": "QZJ8fakefakefake1234",
                "Authorization: Bearer X4Z9fakefakefake5678": "X4Z9fakefakefake5678",
                "sk-QZJ8fakefakefakefake": "QZJ8fakefakefakefake"}
LAYA_PY = "/root/venv-laya-probe/bin/python"


# ---------- the question types (D-6) ----------

def test_questions_are_j2s_own_and_the_briefs():
    q = C.QUESTIONS
    assert q["v1.finding_class"]["criteria"] == C.V1.CLASSES
    assert list(q["v1.finding_class"]["criteria"]) == ["BLOCKER", "FOLLOW-UP", "INFO", "UNVERIFIED", "CONTRACT-DEFECT",
                                                         "KNOWN"]   # the option order, which is the target order
    assert q["v1.blocking"] == {"type": "noul", "instructions": "Does this finding block the merge: a contract break "
                                "reproduced through the real path, or a contract that is itself wrong?"}
    assert q["ap.violates_row"] == {"type": "noul", "instructions": "Does this incident show this anti-pattern?"}
    assert C.options(q["v1.blocking"]) == ["false", "true"]


def test_the_trained_class_question_is_the_one_j2_asked(tmp_path, monkeypatch, capsys):
    """Behavioral: the committed J2 scorer, run on a one-row sample, sends exactly QUESTIONS["v1.finding_class"]."""
    (tmp_path / "s.json").write_text(json.dumps({"sample": [{"row_digest": "r", "label": "INFO", "lane": "L",
                                                             "state": "a finding"}]}))
    seen = []

    def post(url, body):
        seen.append(body)
        qs = body["questions"]
        if "q" in qs:
            return {"answers": {"q": {"choice": list(qs["q"]["criteria"])[0]}}}
        return {"answers": {k: {"noul": 0.5} for k in qs}, "fan_out": len(qs)}

    monkeypatch.setattr(C.V1, "post", post)
    C.V1.cmd_score(argparse.Namespace(sample=str(tmp_path / "s.json"), url="x", out=str(tmp_path / "r.json")))
    capsys.readouterr()
    q = C.QUESTIONS["v1.finding_class"]
    sent = seen[0]["questions"]["q"]
    assert seen[0]["state"] == "a finding" and sent == {"type": "choice", "instructions": q["instructions"],
                                                        "criteria": q["criteria"]}
    assert list(sent["criteria"]) == C.options(q)


def test_rank_reproduces_the_committed_lexical_picks():
    """The builder's candidates are ap_probe's lexical order: its top 3 equal the committed J2 picks on all 100 rows."""
    data = json.loads((FINDINGS / "ap-hawk-probe" / "sample.json").read_text())
    committed = json.loads((FINDINGS / "ap-hawk-probe" / "results.json").read_text())["per_sample"]
    tokens = {rid: C.AP.tokens(text) for rid, text in data["rows"].items()}
    picks = [BD.rank(s["state"], data["rows"], tokens) for s in data["sample"]]
    assert len(picks) == len(committed) == 100 and all(len(p) == 16 for p in picks)
    assert [p[:3] for p in picks] == [c["lexical"] for c in committed]


def test_ap_state_is_the_servers_fan_out_shape(monkeypatch):
    """J2 scored `ap` through the server's per-chunk fan-out: system_one saw {"query", "chunk"} in that order. The server
    fits each per-chunk state with this builder's fit (K265 rev 2); the fit itself runs in the Laya venv
    (test_server_serves_the_state_the_builder_fits), so here it is replaced through its named seam, `_fit`."""
    server = C.load_module("laya_ft_server_under_test", ROOT / "scripts" / "laya_systemone_server.py")
    seen, fitted = [], []

    class Agent:
        def system_one(self, state, questions):
            seen.append(state)
            return {"model": "m", "answers": {k: {"noul": 0.5} for k in questions}, "usage": {}}

    monkeypatch.setattr(server.State, "agent", Agent())
    monkeypatch.setattr(server, "_fit", lambda agent, qid, q, state: fitted.append((qid, q, json.dumps(state))) or state)
    server._answer({"query": "Q", "chunks": [{"id": "r1", "text": "T"}]}, {"r1": C.QUESTIONS["ap.violates_row"]})
    row = BD.make_row("ap", "ap.violates_row", {"query": "Q", "chunk": "T"}, [], None)
    assert fitted == [("r1", C.QUESTIONS["ap.violates_row"], '{"query": "Q", "chunk": "T"}')]   # every state is fitted
    assert seen == [row["state"]] and list(seen[0]) == ["query", "chunk"]
    assert list(json.loads(json.dumps(row, ensure_ascii=True))["state"]) == ["query", "chunk"]   # the JSONL keeps it


# ---------- the builder on a fixture repository (D-2, D-3, D-4) ----------

REPORT = """# VERIFY-T report

## Findings

- **F-1 FOLLOW-UP — the gate reads a token file but never checks its mode** A BLOCKER (adjacent) was suspected
  first; it is known, info-level and NON-BLOCKING. During the probe the file held token=QZJ8fakefakefake1234 and
  Authorization: Bearer X4Z9fakefakefake5678.
- **F-2 INFO — held out: this finding is in the fixture's J2c sample** Measured; no defect.

## Table

| # | Class | Finding | Disposition |
|---|---|---|---|
| T-1 | BLOCKER | a table finding whose title cell alone is kept | BLOCKING because reproduced |
"""
LOG = """# Project incident log

**2026-09-01 10:0xZ — A gate trusted a mirror test (AF-AP-2).** The lane's test asserted the code's own assumption,
see AF-AP-1; its log held sk-QZJ8fakefakefakefake.

**2026-09-02 11:0xZ — Held out: the heading the fixture's AP sample names (AF-AP-1).** Body text.

## ANTI-PATTERN REGISTRY

| id | mechanism | greppable signature | proven instance | status |
|---|---|---|---|---|
| AF-AP-1 | a mirror test passes while production fails | test asserts the code assumption | x | y |
| AF-AP-2 | a gate trusts a mirror | gate trusts | x | y |
| AF-AP-3 | an unrelated row about disk space | df | x | y |
"""


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@example.invalid", "-c", "user.name=t", *args],
                          capture_output=True, check=True).stdout


def _fixture_repo(tmp_path):
    """A git repo with one report, an incident log and three held-out samples (one row each). -> (repo, pins)"""
    repo = tmp_path / "repo"
    (repo / "tasks" / "briefs" / "t").mkdir(parents=True)
    (repo / "docs").mkdir()
    report_path = "tasks/briefs/t/VERIFY-T-report.md"
    (repo / report_path).write_text(REPORT, encoding="utf-8")
    (repo / "docs" / "INCIDENT-LOG.md").write_text(LOG, encoding="utf-8")
    f2 = next(b for b in C.J2C._blocks(report_path, REPORT) if b[0] == "F-2")
    lines = LOG.splitlines()
    held = next(i for i, line in enumerate(lines) if line.startswith("**2026-09-02"))
    samples = {
        "j2_v1": {"sample": [{"row_digest": "d1", "label": "INFO", "lane": "VERIFY-T", "state": "held out: this"}]},
        "j2c": {"sample": [{"row_digest": "d1", "label": "INFO", "lane": "VERIFY-T",
                            "source": "%s#F-2" % report_path, "state": C.J2C._mask(f2[3])}]},
        "ap": {"rows": {}, "sample": [{"line": held + 1, "labels": ["AF-AP-1"],
                                       "state": C.AP.AP_ID.sub("AF-AP-?", C.AP.heading(lines, held))}]},
    }
    pins = {}
    for name, data in samples.items():
        rel = "samples/%s.json" % name
        (repo / "samples").mkdir(exist_ok=True)
        body = (json.dumps(data, sort_keys=True) + "\n").encode("utf-8")
        (repo / rel).write_bytes(body)
        pins[name] = (rel, C.sha256_hex(body))
    _git(repo.parent, "init", "-q", str(repo))
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "fixture")
    return repo, pins


def test_collect_masks_scrubs_and_excludes_on_a_fixture_repo(tmp_path):
    repo, pins = _fixture_repo(tmp_path)
    items, info = BD.collect(BD.git_runner(repo), "HEAD", pins=pins)
    assert info["excluded"] == {"verify_findings": 1, "incident_entries": 1, "text_duplicates": 0}
    v1 = [it for it in items if it[0] == "v1"]
    ap = [it for it in items if it[0] == "ap"]
    assert sorted({(s["path"], s["finding_id"]) for it in v1 for s in it[3]}) == [
        ("tasks/briefs/t/VERIFY-T-report.md", "F-1"), ("tasks/briefs/t/VERIFY-T-report.md", "T-1")]
    assert sorted(it[1] for it in v1) == ["v1.blocking", "v1.blocking", "v1.finding_class", "v1.finding_class"]
    assert len(ap) == 3 and {s["heading"] for it in ap for s in it[3]} == {
        "2026-09-01 10:0xZ — A gate trusted a mirror test (AF-AP-?)."}
    states = [it[2] for it in v1]
    assert all(not CLASS_WORDS.search(s) for s in states) and all("[CLASS]" in s for s in states if "F-1" in s)
    assert "a table finding whose title cell alone is kept" in states and not any("reproduced" in s for s in states)
    assert all(list(it[2]) == ["query", "chunk"] for it in ap)   # the fan-out order J2 scored
    queries = [it[2]["query"] for it in ap]
    assert all(not re.search(r"\bAF-AP-\d+\b", q) for q in queries) and "mirror test" in queries[0]
    for text in states + queries:
        for value in FAKE_SECRETS.values():
            assert value not in text


def test_collect_keeps_the_first_block_of_a_repeated_finding_id(tmp_path):
    """AF-AP-199 (stage0-ci run 36046249811, task #244): a reverify section that restated finding N-10 made collect
    count two findings under one path#id. The first block is the finding; a restatement is counted, never trained."""
    repo, pins = _fixture_repo(tmp_path)
    _, before = BD.collect(BD.git_runner(repo), "HEAD", pins=pins)
    report = repo / "tasks" / "briefs" / "t" / "VERIFY-T-report.md"
    report.write_text(REPORT + "\n## Reverify\n\n- **F-1 FOLLOW-UP — restated after the repair: the mode check now "
                      "holds** Re-run on the new blob.\n", encoding="utf-8")
    _git(repo, "commit", "-q", "-am", "a reverify restates F-1")
    items, info = BD.collect(BD.git_runner(repo), "HEAD", pins=pins)
    assert before["sources"]["repeated_finding_ids"] == 0 and info["sources"]["repeated_finding_ids"] == 1
    assert info["sources"]["verify_findings"] == before["sources"]["verify_findings"] == 3
    f1 = [it[2] for it in items if it[0] == "v1" and it[3][0]["finding_id"] == "F-1"]
    assert len(f1) == 2 and all("never checks its mode" in s and "restated" not in s for s in f1)


def test_collect_resolves_the_commit_once_even_when_the_ref_moves(tmp_path):
    """D-4 / AF-AP-175: one rev-parse; every later read names that sha; a commit landing mid-run changes nothing."""
    repo, pins = _fixture_repo(tmp_path)
    calls = []
    real = BD.git_runner(repo)

    def moving(*args):
        out = real(*args)
        calls.append(args)
        if args[0] == "rev-parse":   # the ref moves right after it was resolved
            path = repo / "tasks" / "briefs" / "t" / "VERIFY-T-report.md"
            path.write_text(REPORT + "\n- **F-3 BLOCKER — a finding committed mid-run** New.\n", encoding="utf-8")
            (repo / "docs" / "INCIDENT-LOG.md").write_text(
                LOG.replace("# Project incident log\n", "# Project incident log\n\n**2026-09-03 12:0xZ — Mid-run "
                            "entry.** New.\n"), encoding="utf-8")
            _git(repo, "commit", "-q", "-am", "moved")
        return out

    items, info = BD.collect(moving, "HEAD", pins=pins)
    sha = real("rev-parse", "--verify", "HEAD~1^{commit}").decode().strip()   # the commit before the move
    assert calls[0] == ("rev-parse", "--verify", "HEAD^{commit}") and info["commit"] == sha
    later = [" ".join(a) for a in calls[1:]]
    assert later and all(sha in a and "HEAD" not in a for a in later)
    assert not any(s.get("finding_id") == "F-3" for it in items for s in it[3])
    assert not any("Mid-run" in it[2]["query"] for it in items if it[0] == "ap")


def _heldout_by_the_brief():
    """The oracle's own reading of D-3 from the committed samples (not common.heldout_identities)."""
    j2c = json.loads((FINDINGS / "j2c-fulltext" / "sample.json").read_text())["sample"]
    j2 = json.loads((FINDINGS / "j2-v1-probe" / "sample.json").read_text())["sample"]
    apx = json.loads((FINDINGS / "ap-hawk-probe" / "sample.json").read_text())["sample"]
    by_digest = {s["row_digest"]: s["source"] for s in j2c}
    return ({s["source"] for s in j2c} | {by_digest[s["row_digest"]] for s in j2}, {s["state"] for s in apx},
            len(j2), len(j2c), len(apx))


def test_collect_excludes_every_heldout_row_on_the_real_tree():
    v1_ids, incident_ids, n_j2, n_j2c, n_ap = _heldout_by_the_brief()
    items, info = BD.collect(BD.git_runner(ROOT), "HEAD")
    assert (n_j2, n_j2c, n_ap) == (100, 100, 100) and len(v1_ids) == len(incident_ids) == 100
    assert info["excluded"] == {"verify_findings": n_j2c, "incident_entries": n_ap, "text_duplicates": 0}
    for _prefix, _qid, _state, sources in items:
        for s in sources:
            if s["kind"] == "verify_finding":
                assert "%s#%s" % (s["path"], s["finding_id"]) not in v1_ids
            else:
                assert s["heading"] not in incident_ids
    findings = {(s["path"], s["finding_id"]) for it in items if it[0] == "v1" for s in it[3]}
    entries = {s["line"] for it in items if it[0] == "ap" for s in it[3]}
    assert len(findings) + n_j2c == info["sources"]["verify_findings"]
    assert len(entries) + n_ap == info["sources"]["incident_entries"] - info["sources"]["entries_without_heading"]
    assert all(not CLASS_WORDS.search(it[2]) for it in items if it[0] == "v1")


# ---------- D-3 refusals ----------

def _write_dataset(ddir, rows, model=None):
    body = "".join(json.dumps(r, ensure_ascii=True) + "\n" for r in rows).encode("ascii")
    ddir.mkdir(parents=True, exist_ok=True)
    (ddir / "dataset.jsonl").write_bytes(body)
    (ddir / "manifest.json").write_text(json.dumps({"commit": "test", "counts": {"rows_total": len(rows)},
                                                    "model": model or {},   # train.py compares a model fingerprint
                                                    "dataset": {"file": "dataset.jsonl", "sha256": C.sha256_hex(body)}}))


def _v1_source(path="tasks/briefs/x/VERIFY-X-report.md", fid="F-9"):
    return [{"kind": "verify_finding", "path": path, "finding_id": fid}]


def test_a_planted_heldout_row_is_refused(tmp_path):
    heldout = C.heldout_identities(C.worktree_reader)
    j2c = json.loads((FINDINGS / "j2c-fulltext" / "sample.json").read_text())["sample"]
    ap_state = json.loads((FINDINGS / "ap-hawk-probe" / "sample.json").read_text())["sample"][0]["state"]
    clean = BD.make_row("v1", "v1.finding_class", "a clean finding text", _v1_source(), None)
    path, fid = j2c[0]["source"].rsplit("#", 1)
    planted = [
        BD.make_row("v1", "v1.finding_class", "other text", _v1_source(path, fid), None),   # a held-out source
        BD.make_row("ap", "ap.violates_row", {"query": "q", "chunk": "c"},
                    [{"kind": "incident", "line": 1, "heading": ap_state, "row": "AF-AP-1"}], None),   # held-out heading
        BD.make_row("v1", "v1.blocking", C.scrub(j2c[0]["state"]), _v1_source(), None),   # a held-out text, clean name
    ]
    C.check_no_heldout([clean], heldout)   # the control: a clean row passes
    for row in planted:
        with pytest.raises(C.HeldOutLeak, match=r"^1 held-out row\(s\) in the dataset \(D-3\)"):
            C.check_no_heldout([clean, row], heldout)
    _write_dataset(tmp_path / "ok", [clean])
    assert len(C.load_dataset(tmp_path / "ok")[0]) == 1
    _write_dataset(tmp_path / "leak", [clean, planted[0]])   # a manifest that agrees with the leaking rows
    with pytest.raises(C.HeldOutLeak):
        C.load_dataset(tmp_path / "leak")
    with open(tmp_path / "ok" / "dataset.jsonl", "a") as fh:   # appended after the build: the digest no longer matches
        fh.write(json.dumps(planted[0]) + "\n")
    with pytest.raises(C.DatasetError, match="is not the manifest's"):
        C.load_dataset(tmp_path / "ok")


# ---------- labels ----------

def test_distribution_orders_validates_and_normalizes():
    q = C.QUESTIONS["v1.finding_class"]
    names = list(q["criteria"])
    values = [0.05, 0.6, 0.1, 0.1, 0.1, 0.05]
    probs = dict(reversed(list(zip(names, values))))   # the teacher's key order is not ours
    assert C.distribution({"choice": "FOLLOW-UP", "probabilities": probs}, q) == pytest.approx(values)
    assert C.distribution({"noul": 0.25}, C.QUESTIONS["v1.blocking"]) == [0.75, 0.25]
    assert sum(C.distribution({"choice": "INFO", "probabilities": dict(zip(names, [0.1667] * 5 + [0.1665]))},
                              q)) == pytest.approx(1.0)   # 4-decimal rounding drift is renormalized
    bad = [({"choice": "FOLLOW-UP", "probabilities": dict(probs, INFO=float("nan"))}, q),
           ({"choice": "FOLLOW-UP", "probabilities": dict(probs, INFO=-0.1)}, q),
           ({"choice": "FOLLOW-UP", "probabilities": {k: v for k, v in probs.items() if k != "INFO"}}, q),
           ({"choice": "FOLLOW-UP", "probabilities": dict(probs, EXTRA=0.0)}, q),
           ({"choice": "INFO", "probabilities": probs}, q),                    # the choice is not the argmax
           ({"choice": "FOLLOW-UP", "probabilities": dict(probs, BLOCKER=0.2)}, q),   # sums to 1.15
           ({"noul": True}, C.QUESTIONS["v1.blocking"]), ({"noul": "0.5"}, C.QUESTIONS["v1.blocking"]),
           ({"noul": 1.5}, C.QUESTIONS["v1.blocking"]), ({}, C.QUESTIONS["v1.blocking"])]
    for answer, question in bad:
        with pytest.raises(C.LabelError):
            C.distribution(answer, question)


def test_join_refuses_a_stale_label():
    row = BD.make_row("v1", "v1.blocking", "a finding", _v1_source(), None)
    rec = {"key": C.label_key(row["item_id"], "v1.blocking"), "sent_state_sha": row["state_sha"],
           "question_sha": row["question_sha"], "target": [0.25, 0.75]}
    assert C.join_labels([row], {rec["key"]: rec}) == [(row, [0.25, 0.75], rec)]
    for field in ("sent_state_sha", "question_sha"):
        with pytest.raises(C.LabelError, match="1 stale label"):
            C.join_labels([row], {rec["key"]: dict(rec, **{field: "0" * 64})})
    with pytest.raises(C.LabelError, match="sums to"):
        C.join_labels([row], {rec["key"]: dict(rec, target=[0.5, 0.6])})


# ---------- the teacher client, against a local stand-in (the network double) ----------

class FakeClock:
    def __init__(self):
        self.t, self.slept = 0.0, []

    def now(self):
        return self.t

    def sleep(self, s):
        self.slept.append(round(s, 6))
        self.t += s


class StandIn:
    """A local HTTP server: answers POST /v1/systemone from `respond(body, n)` and records every request."""

    def __init__(self, respond):
        self.requests, self.respond = [], respond
        outer = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                raw = self.rfile.read(int(self.headers.get("content-length") or 0))
                outer.requests.append({"path": self.path, "headers": dict(self.headers), "raw": raw})
                status, headers, body = outer.respond(json.loads(raw), len(outer.requests))
                self.send_response(status)
                for k, v in headers.items():
                    self.send_header(k, v)
                self.send_header("content-length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, *args):
                pass

        self.httpd = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.url = "http://127.0.0.1:%d" % self.httpd.server_address[1]
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()


def _answer(body):
    (qid, q), = body["questions"].items()
    if q["type"] == "choice":
        names = list(q["criteria"])
        a = {"type": "choice", "choice": names[1], "probabilities": dict(zip(names, [0.1, 0.5] + [0.1] * 4)),
             "confidence": 0.3}
    else:
        a = {"type": "noul", "noul": 0.25, "confidence": 0.75}
    return {"model": "stand-in", "answers": {qid: a}, "usage": {"input_tokens": 7, "output_tokens": 0}}


def ok(body, n):
    return 200, {"content-type": "application/json"}, json.dumps(_answer(body)).encode()


@pytest.fixture
def standin():
    servers = []

    def make(respond):
        servers.append(StandIn(respond))
        return servers[-1]

    yield make
    for s in servers:
        s.close()


@pytest.fixture(autouse=True)
def _loopback_never_proxied(monkeypatch):
    for name in ("http_proxy", "HTTP_PROXY", "https_proxy", "HTTPS_PROXY"):
        monkeypatch.delenv(name, raising=False)


def _teacher_dataset(ddir, n_findings=2, extra_state=None):
    rows = []
    for i in range(n_findings):
        state = "finding %d: the gate reads the file but never checks its mode" % i
        for qid in ("v1.finding_class", "v1.blocking"):
            rows.append(BD.make_row("v1", qid, state, _v1_source(fid="F-%d" % i), None))
    rows.append(BD.make_row("ap", "ap.violates_row", {"query": "an incident", "chunk": "a registry row"},
                            [{"kind": "incident", "line": 1, "heading": "a clean heading", "row": "AF-AP-1"}], None))
    if extra_state is not None:
        rows.append(BD.make_row("v1", "v1.blocking", extra_state, _v1_source(fid="F-S"), None))
    _write_dataset(ddir, rows)
    return rows


def _env(tmp_path, url, key=FAKE_KEY):
    path = tmp_path / "api.env"
    path.write_text("TYPESAFE_BASE_URL=%s\nTYPESAFE_API_KEY=%s\n" % (url, key))
    return path


def _run(tmp_path, url, extra=(), clock=None, post=TL.http_post, out="labels.jsonl"):
    clock = clock or FakeClock()
    argv = ["--dataset", str(tmp_path / "ds"), "--out", str(tmp_path / out), "--env-file", str(_env(tmp_path, url))]
    return TL.main(argv + list(extra), clock=clock.now, sleep=clock.sleep, post=post), clock


def _key_of(request, rows):
    body = json.loads(request["raw"])
    (qid,) = body["questions"]
    sha = C.state_sha(body["state"])
    return next(C.label_key(r["item_id"], qid) for r in rows if r["state_sha"] == sha and r["question_id"] == qid)


def test_teacher_resume_skips_done_keys(tmp_path, standin, capsys):
    rows = _teacher_dataset(tmp_path / "ds")
    srv = standin(ok)
    rc, _ = _run(tmp_path, srv.url, ["--limit", "2"])
    assert rc == 0 and len(srv.requests) == 2
    first = [_key_of(r, rows) for r in srv.requests]
    assert sorted(json.loads(r["raw"])["questions"].popitem()[0] for r in srv.requests) == [
        "ap.violates_row", "v1.blocking"]   # round-robin: a small limit spans the question types
    rc, _ = _run(tmp_path, srv.url)
    assert rc == 0 and len(srv.requests) == len(rows)
    asked = [_key_of(r, rows) for r in srv.requests]
    assert len(set(asked)) == len(asked) and not set(first) & set(asked[2:])
    records, stats = C.read_labels(tmp_path / "labels.jsonl")
    assert set(records) == {C.label_key(r["item_id"], r["question_id"]) for r in rows} and stats["duplicates"] == 0
    by_q = {rec["question_id"]: rec["target"] for rec in records.values()}
    assert by_q["v1.finding_class"] == pytest.approx([0.1, 0.5, 0.1, 0.1, 0.1, 0.1])
    assert by_q["v1.blocking"] == by_q["ap.violates_row"] == [0.75, 0.25]
    assert "skipped_done=2" in capsys.readouterr().out.splitlines()[-1]


def test_teacher_rate_limit_never_exceeds_60_per_minute(tmp_path, standin):
    clock = FakeClock()
    limiter = TL.Limiter(clock.now, clock.sleep, min_gap=0.0)   # the window cap alone
    for _ in range(61):
        limiter.admit()
    assert clock.slept == [60.0] and clock.t == 60.0   # sixty at once, the 61st one minute after the first
    rows = _teacher_dataset(tmp_path / "ds", n_findings=32)   # 65 rows
    srv = standin(ok)
    stamps = []
    clock = FakeClock()

    def post(url, data, key, timeout):
        stamps.append(clock.t)
        return TL.http_post(url, data, key, timeout)

    rc, _ = _run(tmp_path, srv.url, clock=clock, post=post)
    assert rc == 0 and len(stamps) == len(rows) == 65
    assert all(b - a >= 1.0 for a, b in zip(stamps, stamps[1:]))   # at least 1 s apart
    assert all(stamps[i + 60] - stamps[i] >= 60.0 for i in range(len(stamps) - 60))   # never 61 in 60 s


def test_teacher_retries_429_and_5xx_with_backoff(tmp_path, standin):
    _teacher_dataset(tmp_path / "ds")
    script = {1: (429, {"Retry-After": "3"}), 2: (503, {})}

    def flaky(body, n):
        if n in script:
            status, headers = script[n]
            return status, headers, b'{"error": "busy"}'
        return ok(body, n)

    srv = standin(flaky)
    rc, clock = _run(tmp_path, srv.url, ["--limit", "1"])
    assert rc == 0 and len(srv.requests) == 3 and clock.slept == [3.0, 4.0]   # Retry-After, then 2 ** 2
    (rec,) = C.read_labels(tmp_path / "labels.jsonl")[0].values()
    assert rec["attempts"] == 3
    srv2 = standin(lambda body, n: (503, {}, b"down"))
    rc, _ = _run(tmp_path, srv2.url, ["--limit", "1"], out="labels2.jsonl")
    assert rc == 3 and len(srv2.requests) == TL.MAX_ATTEMPTS
    assert C.read_labels(tmp_path / "labels2.jsonl")[0] == {}


def test_teacher_key_stays_out_of_argv_output_and_labels(tmp_path, standin, capsys):
    _teacher_dataset(tmp_path / "ds")
    srv = standin(ok)
    rc, _ = _run(tmp_path, srv.url, ["--limit", "3"])
    assert rc == 0
    for r in srv.requests:
        assert r["headers"]["Authorization"] == "Bearer " + FAKE_KEY   # the key reaches the API, in the header only
        assert not r["headers"]["User-Agent"].startswith("Python-urllib")
        assert FAKE_KEY.encode() not in r["raw"]
    echo = standin(lambda body, n: (401, {}, ("bad key: %s" % FAKE_KEY).encode()))   # a server echoing it back
    rc, _ = _run(tmp_path, echo.url, ["--limit", "1"], out="labels2.jsonl")
    assert rc == 3 and len(echo.requests) == 1   # a 4xx other than 429 is never retried
    out = capsys.readouterr()
    assert "HTTP 401" in out.err and "<key>" in out.err
    assert FAKE_KEY not in out.out + out.err
    for name in ("labels.jsonl", "labels2.jsonl"):
        assert FAKE_KEY not in (tmp_path / name).read_text()
    with pytest.raises(SystemExit) as e:   # no argument takes a key
        TL.main(["--dataset", "x", "--out", "y", "--api-key", FAKE_KEY])
    assert e.value.code == 2
    (tmp_path / "nokey.env").write_text("TYPESAFE_BASE_URL=http://127.0.0.1:9\n")
    assert TL.main(["--dataset", str(tmp_path / "ds"), "--out", str(tmp_path / "l3.jsonl"),
                    "--env-file", str(tmp_path / "nokey.env")]) == 64
    assert "TYPESAFE_API_KEY" in capsys.readouterr().err


def test_teacher_scrubs_every_string_before_it_leaves(tmp_path, standin, capsys):
    secret_state = "The probe log held " + "; ".join(FAKE_SECRETS)
    rows = _teacher_dataset(tmp_path / "ds", extra_state=secret_state)   # a row that skipped the builder's scrub
    srv = standin(ok)
    rc, _ = _run(tmp_path, srv.url)
    assert rc == 0 and len(srv.requests) == len(rows)
    for r in srv.requests:
        for value in FAKE_SECRETS.values():
            assert value.encode() not in r["raw"]
    row = next(r for r in rows if r["state"] == secret_state)
    rec = C.read_labels(tmp_path / "labels.jsonl")[0][C.label_key(row["item_id"], "v1.blocking")]
    assert rec["sent_state_sha"] == C.state_sha(C.scrub(secret_state)) != row["state_sha"]
    assert "scrub_changed=1" in capsys.readouterr().out
    with pytest.raises(C.LabelError, match="stale"):   # and it never trains: its target was for another text
        C.join_labels(rows, C.read_labels(tmp_path / "labels.jsonl")[0])


def test_teacher_refuses_a_malformed_answer_without_storing_it(tmp_path, standin):
    _teacher_dataset(tmp_path / "ds")
    srv = standin(lambda body, n: (200, {}, json.dumps({"answers": {k: {"noul": float("nan")} for k in
                                                                    body["questions"]}}).encode()))
    rc, _ = _run(tmp_path, srv.url, ["--questions", "v1.blocking", "--limit", "1"])
    assert rc == 4 and C.read_labels(tmp_path / "labels.jsonl")[0] == {}


# ---------- the evaluator's own checks ----------

def test_positive_control_comparison_flags_any_changed_number():
    for run in ("v1", "v1_full", "ap"):
        committed = json.loads((FINDINGS / EV.J2_RUNS[run][1]).read_text())
        assert EV.compare(run, committed, committed) == []
        doctored = copy.deepcopy(committed)
        if run == "ap":
            doctored["rates"]["jev@1"] = 0.06
            assert EV.compare(run, doctored, committed) == ["ap.rates.jev@1: 0.06, committed 0.05"]
        else:
            doctored["methods"]["jev_choice"]["per_class_recall"]["BLOCKER"] = "3/7"
            assert EV.compare(run, doctored, committed) == [
                "%s.methods.jev_choice.per_class_recall: %r, committed %r" % (
                    run, doctored["methods"]["jev_choice"]["per_class_recall"],
                    committed["methods"]["jev_choice"]["per_class_recall"])]
        assert EV.agreement(run, committed, committed)


def test_kc_j3_lines_reject_at_or_under_the_bar():
    v1 = json.loads((FINDINGS / "j2-v1-probe" / "results.json").read_text())
    assert [line.endswith("REJECTED (at or under)") for line in EV.kc_j3("v1", v1)] == [True, True]
    tie = copy.deepcopy(v1)
    tie["methods"]["jev_choice"]["accuracy"] = 0.43   # equal to the majority: still rejected
    assert EV.kc_j3("v1", tie)[0].endswith("REJECTED (at or under)")
    tie["methods"]["jev_choice"]["accuracy"] = 0.44
    assert EV.kc_j3("v1", tie)[0].endswith("PASSES (above)")
    ap = json.loads((FINDINGS / "ap-hawk-probe" / "results.json").read_text())
    assert EV.kc_j3("ap", ap) == ["KC-J3 ap: Laya top-1 0.0500 vs max(majority 0.0900, lexical 0.5900) = 0.5900 -> "
                                  "REJECTED (at or under)"]
    assert EV.blocking_metrics([True, False, False, True], [True, True, False, False]) == {
        "n": 4, "blocking_split": 0.5, "blocking_recall": "1/2", "false_alarms": "1/2", "never_baseline_split": 0.5}


def test_evaluator_refuses_a_served_probability_that_is_not_finite():
    """VERIFY-FT1 F-1: J2's scorers counted a NaN checkpoint's answers (every prediction BLOCKER, ECE 0.0). The served
    shape is laya.Agent.system_one's: a choice's `probabilities` and a noul's `noul`, each a float."""
    choice = {"type": "choice", "choice": "FOLLOW-UP", "probabilities": {"BLOCKER": 0.1, "FOLLOW-UP": 0.9},
              "confidence": 0.8, "action": {"act_probability": 0.5}}
    noul = {"type": "noul", "noul": 0.25, "confidence": 0.75, "action": {"act_probability": 0.5}}
    served = {"model": "laya-rl-agent", "answers": {"q": choice, "r1": noul}, "usage": {"input_tokens": 9}}
    assert EV.check_served(served) is served   # the control: finite answers pass, unchanged
    for bad in (float("nan"), float("inf"), float("-inf"), None, "0.5", 1):
        for qid, answer in (("q", dict(choice, probabilities=dict(choice["probabilities"], BLOCKER=bad))),
                            ("r1", dict(noul, noul=bad))):
            with pytest.raises(EV.NonFiniteAnswer) as e:
                EV.check_served(dict(served, answers=dict(served["answers"], **{qid: answer})))
            assert str(e.value) == "answer %r serves the probability %r, not a finite float" % (qid, bad)


# ---------- the trainer's optimizer settings: usage errors before any model loads (VERIFY-FT1 F-1) ----------

def _tampered_dataset(ddir):
    """A dataset whose bytes are not its manifest's: train.run() refuses it (DatasetError, exit 64) before any model or
    torch import, so a setting the parser accepts reads 64 here and one it refuses reads 2."""
    _write_dataset(ddir, [])
    (ddir / "dataset.jsonl").write_bytes(b"{}\n")
    return ddir


def test_train_refuses_optimizer_settings_outside_their_domain_at_parse_time(tmp_path, capsys):
    (tmp_path / "model").mkdir()
    base = ["--dataset", str(_tampered_dataset(tmp_path / "ds")), "--labels", str(tmp_path / "labels.jsonl"),
            "--out", str(tmp_path / "out"), "--mode", "head", "--device", "cpu", "--model-dir", str(tmp_path / "model")]
    for extra in ([], ["--lr", "1e-4", "--weight-decay", "0", "--max-grad-norm", "1e-6"],
                  ["--lr", "1e300", "--weight-decay", "1e300", "--max-grad-norm", "1e300"]):
        assert TR.main(base + extra) == 64, extra   # the controls: parsed, then refused on the dataset
        assert capsys.readouterr().err.startswith("train: refused: DatasetError: "), extra
    for flag, value, shown in (("--lr", "inf", "inf"), ("--lr", "-inf", "-inf"), ("--lr", "nan", "nan"),
                               ("--lr", "0", "0.0"), ("--lr", "-1e-4", "-0.0001"), ("--lr", "1e-400", "0.0"),
                               ("--weight-decay", "inf", "inf"), ("--weight-decay", "nan", "nan"),
                               ("--weight-decay", "-0.01", "-0.01"), ("--max-grad-norm", "inf", "inf"),
                               ("--max-grad-norm", "nan", "nan"), ("--max-grad-norm", "0", "0.0"),
                               ("--max-grad-norm", "-1", "-1.0")):
        with pytest.raises(SystemExit) as e:
            TR.main(base + ["%s=%s" % (flag, value)])   # "=": argparse would read a bare "-inf" as an option
        rule = "finite and >= 0" if flag == "--weight-decay" else "finite and > 0"
        assert e.value.code == 2, (flag, value)
        assert capsys.readouterr().err.endswith("error: %s must be %s, not %s\n" % (flag, rule, shown)), (flag, value)
    assert not (tmp_path / "out").exists()


# ---------- the Laya venv (the builder's fit and determinism, the trainer on the real model) ----------

def _present(path):
    try:   # AF-AP-44: a venue probe returns absent on any OSError, never raises
        os.stat(path)
        return True
    except OSError:
        return False


@pytest.fixture(scope="module")
def laya_venue():
    venue = os.environ.get("S0_01_VENUE")
    if venue != "sandbox":
        pytest.skip("LOUD SKIP: the Laya venv and snapshot are declared inputs of the sandbox venue only (S0_01_VENUE=%r;"
                    " CI declares none, and the PC's Laya paths are not declared to this file)" % venue)
    missing = [p for p in (LAYA_PY, os.path.join(C.DEFAULT_MODEL_DIR, "model.safetensors")) if not _present(p)]
    if missing:
        pytest.fail("declared input missing on the sandbox venue: %s" % missing)
    return {"py": LAYA_PY, "model_dir": C.DEFAULT_MODEL_DIR}


def _laya(venue, script, *args, timeout=900):
    proc = subprocess.run([venue["py"], "-c", script, *args], capture_output=True, text=True, timeout=timeout,
                          env=dict(os.environ, HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1"))
    assert proc.returncode == 0, proc.stderr[-3000:]
    return json.loads(proc.stdout.strip().splitlines()[-1])


FIT_CHECK = r"""
import json, sys
sys.path.insert(0, sys.argv[1])
from laya_ft import common as C
from laya.agent import Agent
from laya.common import build_sequence, render_options
from transformers import AutoTokenizer
rows, manifest = C.load_dataset(sys.argv[2])
tok = AutoTokenizer.from_pretrained(sys.argv[3] + "/tokenizer")
L, H = manifest["model"]["max_len"], manifest["model"]["head_max_len"]
short = markers_bad = 0
for row in rows:   # the consumer's verdict, independent of the builder's Fitter: no state token dropped
    q = Agent._to_internal(row["question"])
    seq, markers = build_sequence(tok, row["state"], q, L, H)
    full, _ = build_sequence(tok, row["state"], q, 10 ** 6, H)
    short += len(seq) != len(full)
    markers_bad += len(markers) != len(render_options(q))
print(json.dumps({"rows": len(rows), "truncated": short, "markers_bad": markers_bad,
                  "cut": sum("cut" in r for r in rows)}))
"""


def test_builder_is_deterministic_and_every_state_fits_the_window(laya_venue, tmp_path):
    sha = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--verify", "HEAD^{commit}"], capture_output=True,
                         text=True, check=True).stdout.strip()   # resolved once: both builds read this commit
    outs = []
    for name in ("a", "b"):
        proc = subprocess.run([laya_venue["py"], str(ROOT / "scripts" / "laya_ft" / "build_dataset.py"), "--commit",
                               sha, "--out", str(tmp_path / name), "--model-dir", laya_venue["model_dir"]],
                              capture_output=True, text=True, timeout=600, env=dict(os.environ, HF_HUB_OFFLINE="1"))
        assert proc.returncode == 0, proc.stderr[-3000:]
        outs.append(tmp_path / name)
    for f in ("dataset.jsonl", "manifest.json"):
        assert (outs[0] / f).read_bytes() == (outs[1] / f).read_bytes(), f
    manifest = json.loads((outs[0] / "manifest.json").read_text())
    assert manifest["commit"] == sha
    assert manifest["heldout"]["verify_findings"] == {"identities": 100, "excluded": 100}
    assert manifest["heldout"]["incident_entries"] == {"identities": 100, "excluded": 100}
    fit = _laya(laya_venue, FIT_CHECK, str(ROOT / "scripts"), str(outs[0]), laya_venue["model_dir"])
    assert fit["rows"] == manifest["counts"]["rows_total"] > 0 and fit["truncated"] == 0 and fit["markers_bad"] == 0
    assert fit["cut"] == sum(manifest["counts"]["cut_to_window"].values())


WORDS = r"""
def words(tag, n):   # synthetic text of n characters: no session text
    out, size, i = [], 0, 0
    while size < n:
        out.append("%s%d" % (tag, i))
        size, i = size + len(out[-1]) + 1, i + 1
    return " ".join(out)[:n]
"""

FIT_DIFF = r"""
import json, sys
sys.path.insert(0, sys.argv[1])
from laya_ft import build_dataset as BD, common as C
from laya.agent import Agent
from laya.common import build_sequence, serialize_state
""" + WORDS + r"""

def pin_fit(tok, max_len, head_max_len, state, question):
    # the oracle: build_dataset.py Fitter.fit at 157ddd6 (K265's PIN), verbatim but for `self.` -> arguments
    q = Agent._to_internal(question)
    empty = len(build_sequence(tok, "", q, max_len, head_max_len)[0])

    def tokens(s):
        text = serialize_state(s).replace(tok.mask_token, " ")
        return len(tok(text, add_special_tokens=False)["input_ids"])

    def fits(s):
        return len(build_sequence(tok, s, q, max_len, head_max_len)[0]) == empty + tokens(s)

    if fits(state):
        return state, None
    text = state if isinstance(state, str) else state["query"]

    def cut_to(n):
        return text[:n] if isinstance(state, str) else {"query": text[:n], "chunk": state["chunk"]}

    if not fits(cut_to(0)):
        raise ValueError("the chunk alone overflows Laya's window: %r" % (state.get("chunk", "")[:80],))
    lo, hi = 0, len(text)
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if fits(cut_to(mid)):
            lo = mid
        else:
            hi = mid
    return cut_to(lo), {"chars_from": len(text), "chars_to": lo}


F = BD.Fitter(sys.argv[2])
odd = 'quotes " and \\ backslashes, [MASK], ' + chr(0xE9) + chr(0x4E2D) + ", tabs\t, "
cases = [("v1.finding_class", "The gate reads the token file but never checks its mode."),
         ("v1.blocking", words("finding", 9000)), ("v1.finding_class", (odd + words("f", 200)) * 30),
         ("ap.violates_row", {"query": "an incident heading", "chunk": "a registry row"}),
         ("ap.violates_row", {"query": words("incident", 6000), "chunk": words("row", 700)}),
         ("ap.violates_row", {"query": (odd + words("i", 100)) * 40, "chunk": odd}),
         ("ap.violates_row", {"query": "an incident", "chunk": words("row", 9000)})]
out = []
for qid, state in cases:
    rows = []
    for fn in (lambda s, q: pin_fit(F.tok, F.max_len, F.head_max_len, s, q), F.fit):
        try:
            rows.append(["returned", json.dumps(fn(state, C.QUESTIONS[qid]), ensure_ascii=False)])
        except ValueError as e:
            rows.append(["ValueError", str(e)])
    out.append({"qid": qid, "pin": rows[0], "new": rows[1]})
print(json.dumps(out))
"""


def test_fit_delegation_changes_no_dataset_output(laya_venue):
    """K265 rev 2: Fitter.fit delegates to laya_ft/fit.py (the fit the server applies too). On the dataset's two shapes,
    fitting and cut, the result equals the PIN's own Fitter.fit (the oracle above, verbatim), the error included."""
    out = _laya(laya_venue, FIT_DIFF, str(ROOT / "scripts"), laya_venue["model_dir"])
    assert [o["pin"] == o["new"] for o in out] == [True] * 7, [o for o in out if o["pin"] != o["new"]]
    kinds = [(o["pin"][0], '"chars_to"' in o["pin"][1]) for o in out]   # the cases do what they are there for
    assert kinds == [("returned", False), ("returned", True), ("returned", True), ("returned", False),
                     ("returned", True), ("returned", True), ("ValueError", False)]


SERVE_FIT = r"""
import json, sys
sys.path.insert(0, sys.argv[1])
from importlib.util import module_from_spec, spec_from_file_location
from laya_ft import build_dataset as BD, common as C
import laya.common as LC
from laya.agent import Agent
from transformers import AutoTokenizer
""" + WORDS + r"""
spec = spec_from_file_location("laya_systemone_server_in_venv", sys.argv[1] + "/laya_systemone_server.py")
server = module_from_spec(spec)
spec.loader.exec_module(server)
F = BD.Fitter(sys.argv[2])   # the dataset builder's own fit
with open(sys.argv[2] + "/rl_agent_config.json") as f:
    cfg = json.load(f)                                           # what Agent.cfg holds


class TokenizerOnlyAgent:   # Agent's own tokenizer, config and question form; the forward pass is a recorder
    _to_internal = staticmethod(Agent._to_internal)

    def __init__(self):
        self.tok, self.cfg, self.calls = AutoTokenizer.from_pretrained(sys.argv[2] + "/tokenizer"), cfg, []

    def system_one(self, state, questions):
        self.calls.append(state)
        qid = next(iter(questions))
        return {"model": "tokenizer-only", "answers": {qid: {"type": "noul", "noul": 0.5}},
                "usage": {"input_tokens": 0, "output_tokens": 0}}


q = C.QUESTIONS["ap.violates_row"]
iq = Agent._to_internal(q)
out = []
for query, row in ((words("incident", 6000), words("row", 700)), ("a short incident heading", "a short registry row")):
    agent = server.State.agent = TokenizerOnlyAgent()
    server._answer({"query": query, "chunks": [{"id": "r1", "text": row}]}, {"r1": q})
    sent = agent.calls[0]
    fitted, cut = F.fit({"query": query, "chunk": row}, q)
    out.append({"same": json.dumps(sent, ensure_ascii=False) == json.dumps(fitted, ensure_ascii=False),
                "keys": list(sent), "cut": cut, "query_chars_sent": len(sent["query"]),
                "whole": len(LC.build_sequence(agent.tok, sent, iq, F.max_len, F.head_max_len)[0])
                == len(LC.build_sequence(agent.tok, sent, iq, 10 ** 6, F.head_max_len)[0])})
print(json.dumps(out))
"""


def test_server_serves_the_state_the_builder_fits(laya_venue):
    """K265 rev 2, train/serve identity through the real tokenizer: for the same query and chunk, the server's per-chunk
    state is the dataset builder's fitted state, key order included; the first case is cut, the second fits whole."""
    cut_case, whole_case = _laya(laya_venue, SERVE_FIT, str(ROOT / "scripts"), laya_venue["model_dir"])
    assert cut_case["same"] is True and cut_case["keys"] == ["query", "chunk"] and cut_case["whole"] is True
    assert cut_case["cut"]["chars_from"] == 6000 and cut_case["cut"]["chars_to"] == cut_case["query_chars_sent"] < 6000
    assert whole_case == {"same": True, "keys": ["query", "chunk"], "cut": None, "query_chars_sent": 24, "whole": True}


TRAINER_CHECK = r"""
import json, sys
sys.path.insert(0, sys.argv[1])
from laya_ft import build_dataset as BD, train as T
import torch
torch.set_num_threads(4)
model_dir, ckpt = sys.argv[2], sys.argv[3]
agent = T.load_base(model_dir, "cpu")
model, tok, dev = agent.model, agent.tok, agent.device
finding = "The gate reads the token file but never checks its mode; a group-readable token passes the check."
rows = [BD.make_row("v1", "v1.finding_class", finding, [], None), BD.make_row("v1", "v1.blocking", finding, [], None),
        BD.make_row("ap", "ap.violates_row", {"query": "A test mirrored the code's own assumption and passed while "
                    "production failed.", "chunk": "a test written from the code's own assumption is a mirror"}, [],
                    None),
        BD.make_row("v1", "v1.finding_class", "Measured 42 ms per call on the sandbox CPU; nothing is wrong.", [], None)]
targets = [[0.1, 0.6, 0.1, 0.1, 0.05, 0.05], [0.8, 0.2], [0.3, 0.7], [0.02, 0.08, 0.8, 0.05, 0.03, 0.02]]
items = T.make_items(tok, agent.cfg, [(r, t, {}) for r, t in zip(rows, targets)])   # the fixed four-item batch
torch.manual_seed(0)
trainable = T.select_trainable(model, "head")
params = [p for _, p in trainable]
digest = {k: T.param_digest(model, k) for k in ("encoder.", "act_head.", "head.", "scorer.")}
opt = torch.optim.AdamW(params, lr=1e-4, weight_decay=0.01)
from laya.common import collate_items, proper_reward


def reward(m):   # the objective itself, through laya.common.proper_reward, never through train.loss_fn
    m.eval()
    with torch.no_grad():
        b = T.to_device(collate_items([items], tok.pad_token_id), dev)
        q = torch.softmax(T.forward(m, b, "head", dev).float(), -1)
        r = float(proper_reward(q, b["target"], b["qtype"], b["marker_mask"].float()).mean())
    T.set_train_modes(m, "head")
    return r


T.set_train_modes(model, "head")
out = {"before": T.eval_loss(model, items, "head", dev, tok.pad_token_id, 4), "reward_before": reward(model)}
out["steps"] = [T.train_step(model, opt, items, "head", dev, tok.pad_token_id, params, 1.0) for _ in range(3)]
out["after"] = T.eval_loss(model, items, "head", dev, tok.pad_token_id, 4)
out["reward_after"] = reward(model)
out["unchanged"] = {k: T.param_digest(model, k) == v for k, v in digest.items()}
out["trained_names"] = sorted({n.split(".")[0] for n, _ in trainable})
if "encoder" in out["trained_names"] or not out["unchanged"]["encoder."]:
    out["checkpoint"] = "not written: head mode trained the encoder, whose checkpoint would hold 1.6 GB"
    print(json.dumps(out))
    sys.exit(0)
T.save_checkpoint(T.trained_state_dict(trainable), ckpt)
b = T.to_device(collate_items([items], tok.pad_token_id), dev)
model.eval()
with torch.no_grad():
    trained = T.forward(model, b, "head", dev)
fresh = T.load_base(model_dir, "cpu").model.eval()
with torch.no_grad():
    base = T.forward(fresh, b, "head", dev)
out["ckpt"] = T.load_checkpoint(fresh, ckpt)
with torch.no_grad():
    loaded = T.forward(fresh, b, "head", dev)
out["base_differs"] = not torch.equal(base, trained)
out["loaded_equals_trained"] = torch.equal(loaded, trained)
out["full_trains"] = sorted({n.split(".")[0] for n, _ in T.select_trainable(fresh, "full")})
# the loss's direction: the negated proper reward is lowest where the distribution IS the target
t = torch.tensor([[0.7, 0.2, 0.1]])
batch = {"target": t, "qtype": torch.tensor([0]), "marker_mask": torch.tensor([[True, True, True]])}
at_target = float(T.loss_fn(torch.log(t), batch))
others = [float(T.loss_fn(torch.tensor([x]), batch)) for x in ([0.0, 0.0, 0.0], [3.0, 0.0, 0.0], [0.0, 3.0, 0.0])]
out["loss_at_target"], out["loss_elsewhere"] = at_target, others
print(json.dumps(out))
"""


@pytest.fixture(scope="module")
def trainer_run(laya_venue, tmp_path_factory):
    ckpt = tmp_path_factory.mktemp("ft1-trainer") / "checkpoint.pt"
    return _laya(laya_venue, TRAINER_CHECK, str(ROOT / "scripts"), laya_venue["model_dir"], str(ckpt))


def test_trainer_three_steps_lower_the_loss_on_the_real_model(trainer_run):
    r = trainer_run
    assert r["after"] < r["before"], r   # the optimizer lowers the loss it is given...
    assert r["reward_after"] > r["reward_before"], r   # ...and that raises the proper reward itself (sign-aware)
    assert r["loss_at_target"] < min(r["loss_elsewhere"]), r   # the sign: the target is the minimum


def test_trainer_head_mode_leaves_every_encoder_parameter_bitwise_unchanged(trainer_run):
    r = trainer_run
    assert r["unchanged"] == {"encoder.": True, "act_head.": True, "head.": False, "scorer.": False}, r
    assert r["trained_names"] == ["head", "scorer", "type_emb"]
    assert r["full_trains"] == ["encoder", "head", "scorer", "type_emb"]   # never the act head, in either mode


def test_trainer_checkpoint_loads_into_a_fresh_model_and_changes_its_outputs(trainer_run):
    r = trainer_run
    assert "checkpoint" not in r, r   # the driver wrote one
    assert r["base_differs"] and r["loaded_equals_trained"], r
    assert r["ckpt"][1] == ["head", "scorer", "type_emb"]


# ---------- FT1-F: non-finite results and the free-space order (VERIFY-FT1 F-1, F-4, F-6), in the Laya venv ----------

GUARD_CHECK = r"""
import json, shutil, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from laya_ft import train as T
import torch
tmp, nan, inf = Path(sys.argv[2]), float("nan"), float("inf")
out = {"tmp": str(tmp)}


def said(fn, *args):   # the refusal a guard raises, "Type: message"; None when it lets the input through
    try:
        fn(*args)
    except (T.Refusal, T.NonFinite) as e:
        return "%s: %s" % (type(e).__name__, e)
    return None


def poisoned(value, shape=(4, 5), at=0):
    t = torch.zeros(shape)
    t.view(-1)[at] = value
    return t


ok = {"head.w": torch.randn(4, 5), "scorer.b": torch.full((3,), 3.0e38), "type_emb.e": torch.zeros(0, 2),
      "head.h": torch.ones(2, dtype=torch.bfloat16)}   # a large, an empty and a bf16 tensor are finite too
out["finite"] = {"clean": T.non_finite_tensors(ok),
                 "one_nan": T.non_finite_tensors(dict(ok, **{"head.w": poisoned(nan, at=19)})),
                 "order": T.non_finite_tensors({"a": poisoned(inf), "b": torch.ones(2), "c": poisoned(-inf, at=7),
                                                "d": poisoned(nan).to(torch.bfloat16)})}
out["refuse"] = {"clean": said(T.refuse_non_finite, ok, 0.5), "unmeasured": said(T.refuse_non_finite, ok, None),
                 "tensor": said(T.refuse_non_finite, dict(ok, **{"scorer.b": poisoned(inf, (3,))}), 0.5),
                 "loss_nan": said(T.refuse_non_finite, ok, nan), "loss_inf": said(T.refuse_non_finite, ok, inf),
                 "premise": said(T.refuse_non_finite, {"t%02d" % i: poisoned(nan) for i in range(31)}, nan)}
m = torch.nn.Module()   # a crafted module: load_checkpoint reads only named_parameters and load_state_dict
m.head, m.act_head = torch.nn.Linear(5, 4), torch.nn.Linear(5, 1)
before = {k: v.detach().clone() for k, v in m.state_dict().items()}
good = {"head.weight": torch.randn(4, 5), "head.bias": torch.randn(4)}
torch.save(good, str(tmp / "good.pt"))
out["load"] = {"good": list(T.load_checkpoint(m, tmp / "good.pt")),
               "good_loaded": torch.equal(m.head.weight, good["head.weight"]) and torch.equal(m.head.bias, good["head.bias"])}
m.load_state_dict(before)
for name, sd in (("nan_weight", dict(good, **{"head.weight": poisoned(nan, (4, 5), 3)})),
                 ("inf_bias", dict(good, **{"head.bias": poisoned(-inf, (4,))}))):
    torch.save(sd, str(tmp / (name + ".pt")))
    out["load"][name] = said(T.load_checkpoint, m, tmp / (name + ".pt"))
out["load"]["model_unchanged"] = all(torch.equal(v, before[k]) for k, v in m.state_dict().items())
real, asked = shutil.disk_usage, []


def small(path):   # the filesystem reports 1 MiB free; the disk itself is real
    asked.append(str(path))
    return real(path)._replace(free=1 << 20)


shutil.disk_usage = small
(tmp / "ck").mkdir()
out["space"] = {"early": said(T.check_space, 4 << 10, tmp / "not" / "yet"), "early_asked": list(asked),
                "created": (tmp / "not").exists(), "save": said(T.save_checkpoint, good, tmp / "ck" / "checkpoint.pt")}
out["space"]["save_files"] = sorted(p.name for p in (tmp / "ck").iterdir())
shutil.disk_usage = real
out["space"]["early_real"] = said(T.check_space, 4 << 10, tmp / "not" / "yet")
out["space"]["save_real"] = said(T.save_checkpoint, good, tmp / "ck" / "checkpoint.pt")
out["space"]["save_real_files"] = sorted(p.name for p in (tmp / "ck").iterdir())
print(json.dumps(out))
"""


@pytest.fixture(scope="module")
def guard_run(laya_venue, tmp_path_factory):
    return _laya(laya_venue, GUARD_CHECK, str(ROOT / "scripts"), str(tmp_path_factory.mktemp("ft1f-guards")))


def test_finiteness_guards_on_crafted_tensors(guard_run):
    r = guard_run
    assert r["finite"] == {"clean": [], "one_nan": ["head.w"], "order": ["a", "c", "d"]}, r
    assert r["refuse"] == {
        "clean": None, "unmeasured": None,
        "tensor": "NonFinite: 1 of 4 trained tensors are not finite (scorer.b): nothing is saved",
        "loss_nan": "NonFinite: eval_loss_after is nan: nothing is saved",
        "loss_inf": "NonFinite: eval_loss_after is inf: nothing is saved",
        "premise": "NonFinite: 31 of 31 trained tensors are not finite (t00, t01, t02); eval_loss_after is nan: nothing "
                   "is saved"}, r


def test_load_checkpoint_refuses_a_non_finite_tensor_before_loading_it(guard_run):
    r, tmp = guard_run["load"], guard_run["tmp"]
    assert r["good"] == [2, ["head"]] and r["good_loaded"], r   # the control: a finite checkpoint loads
    assert r["nan_weight"] == "Refusal: checkpoint %s/nan_weight.pt: 1 of 2 tensors are not finite: ['head.weight']" % tmp
    assert r["inf_bias"] == "Refusal: checkpoint %s/inf_bias.pt: 1 of 2 tensors are not finite: ['head.bias']" % tmp
    assert r["model_unchanged"], r


def test_free_space_is_probed_without_writing_and_checked_again_at_save(guard_run):
    r, tmp = guard_run["space"], guard_run["tmp"]
    assert r["early"] == "Refusal: the checkpoint needs 64 MiB and %s/not/yet has 1 MiB free" % tmp, r
    assert r["early_asked"] == [tmp] and not r["created"], r   # the nearest existing ancestor; nothing created
    assert r["save"] == "Refusal: the checkpoint needs 64 MiB and %s/ck has 1 MiB free" % tmp and r["save_files"] == [], r
    assert (r["early_real"], r["save_real"], r["save_real_files"]) == (None, None, ["checkpoint.pt"]), r


POISONED = "head.layers.0.self_attn.in_proj_weight"   # the first trained parameter; a NaN there reaches every logit
TRAIN_CLI = r"""
import contextlib, io, json, shutil, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from laya_ft import train as T
import torch
scenario, argv = sys.argv[2], json.loads(sys.argv[3])
out_dir = Path(argv[argv.index("--out") + 1])
real_step, real_usage = T.train_step, shutil.disk_usage
seen = {"steps": 0, "poisoned": None, "asked": []}


def step(model, opt, items, *rest):   # the real step; the "nan" fault is written after the first one returns
    loss = real_step(model, opt, items, *rest)
    seen["steps"] += 1
    if scenario == "nan" and seen["steps"] == 1:
        name, p = next((n, p) for n, p in model.named_parameters() if p.requires_grad)
        with torch.no_grad():
            p.view(-1)[0] = float("nan")
        seen["poisoned"] = name
    return loss


def usage(path):   # "disk_full": the filesystem reports 40 MiB free (the verifier's tmpfs); the disk itself is real
    if scenario != "disk_full":
        return real_usage(path)
    seen["asked"].append(str(path))
    return real_usage(path)._replace(free=40 << 20)


T.train_step, shutil.disk_usage = step, usage
err = io.StringIO()
with contextlib.redirect_stderr(err):
    rc = T.main(argv)
res = dict(seen, rc=rc, said=[line for line in err.getvalue().splitlines() if line.startswith("train:")],
           files=sorted(p.name for p in out_dir.iterdir()) if out_dir.exists() else None)
if (out_dir / "checkpoint.pt").exists():   # the oracle's own reading, torch.isfinite, not the guard under test
    sd = torch.load(str(out_dir / "checkpoint.pt"), map_location="cpu", weights_only=True)
    res["tensors"], res["non_finite"] = len(sd), sum(not bool(torch.isfinite(t).all()) for t in sd.values())
    res["guards"] = json.loads((out_dir / "train-manifest.json").read_text())["guards"]
print(json.dumps(res))
"""


def _tiny_training_inputs(root, model_dir):
    """Two rows made by the real builder's make_row, in a dataset built for this model (its fingerprint), and a teacher
    label for each in the labels file's own record shape."""
    finding = "The gate reads the token file but never checks its mode; a group-readable token passes the check."
    rows = [BD.make_row("v1", qid, finding, _v1_source(fid="F-1"), None) for qid in ("v1.finding_class", "v1.blocking")]
    _write_dataset(root / "ds", rows, model=C.model_fingerprint(model_dir))
    targets = {"v1.finding_class": [0.1, 0.6, 0.1, 0.1, 0.05, 0.05], "v1.blocking": [0.8, 0.2]}
    with open(root / "labels.jsonl", "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps({"key": C.label_key(r["item_id"], r["question_id"]), "item_id": r["item_id"],
                                 "question_id": r["question_id"], "question_sha": r["question_sha"],
                                 "sent_state_sha": r["state_sha"], "options": r["options"],
                                 "target": targets[r["question_id"]], "answer": {}, "model": "stand-in",
                                 "endpoint": "none", "input_tokens": 0, "attempts": 1, "ts": 0.0}) + "\n")
    return root / "ds", root / "labels.jsonl"


def _train_cli(venue, tmp_path, scenario, *extra):
    ds, labels = _tiny_training_inputs(tmp_path, venue["model_dir"])
    argv = ["--dataset", str(ds), "--labels", str(labels), "--out", str(tmp_path / "out"), "--mode", "head",
            "--device", "cpu", "--model-dir", venue["model_dir"], "--batch-size", "1", "--threads", "4", *extra]
    return _laya(venue, TRAIN_CLI, str(ROOT / "scripts"), scenario, json.dumps(argv))


def test_train_cli_refuses_a_non_finite_trained_tensor_and_writes_nothing(laya_venue, tmp_path):
    """F-1: a NaN written into a trained parameter after the LAST real step, which train_step's loss check never sees."""
    r = _train_cli(laya_venue, tmp_path, "nan", "--limit", "1", "--eval-loss")
    assert (r["rc"], r["steps"], r["poisoned"], r["files"]) == (5, 1, POISONED, None), r   # no --out, no .tmp
    assert r["said"] == ["train: refused: NonFinite: 1 of 31 trained tensors are not finite (%s); eval_loss_after is "
                         "nan: nothing is saved" % POISONED], r


def test_train_cli_refuses_a_non_finite_loss_without_a_traceback(laya_venue, tmp_path):
    """F-4, the trainer half: the same fault before a second step is train_step's non-finite loss (rc 1 and a raw
    FloatingPointError traceback before FT1-F)."""
    r = _train_cli(laya_venue, tmp_path, "nan", "--limit", "2")
    assert (r["rc"], r["steps"], r["files"]) == (5, 1, None), r
    assert r["said"] == ["train: refused: FloatingPointError: non-finite loss nan: the step is refused"], r


def test_train_cli_refuses_a_full_disk_before_the_first_step(laya_venue, tmp_path):
    """F-6: --out on a filesystem with 40 MiB free is refused after the model load and before any step (it was refused
    at save, after the training)."""
    r = _train_cli(laya_venue, tmp_path, "disk_full", "--limit", "1")
    assert (r["rc"], r["steps"], r["files"]) == (64, 0, None), r
    assert r["said"] == ["train: refused: Refusal: the checkpoint needs 164 MiB and %s has 40 MiB free"
                         % (tmp_path / "out")], r
    assert r["asked"] == [str(tmp_path)], r   # one probe, of --out's nearest existing ancestor


def test_train_cli_saves_a_finite_checkpoint_when_nothing_is_wrong(laya_venue, tmp_path):
    """The control for the three refusals above: the same inputs, no fault, the real disk."""
    r = _train_cli(laya_venue, tmp_path, "none", "--limit", "1", "--eval-loss")
    assert (r["rc"], r["steps"], r["said"]) == (0, 1, []), r
    assert r["files"] == ["checkpoint.pt", "train-manifest.json"] and (r["tensors"], r["non_finite"]) == (31, 0), r
    assert r["guards"] == {"act_head_unchanged": True, "encoder_unchanged": True, "model_dir_unchanged": True}, r


EVAL_CLI = r"""
import contextlib, io, json, sys
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from laya_ft import evaluate as EV, train as T
import torch
out_dir, poison, real_load = Path(sys.argv[2]), sys.argv[3], T.load_base
seen = {"answers": 0}


def load_base(model_dir, device):   # the real load; the fault is written after the first served answer
    agent = real_load(model_dir, device)
    real_one = agent.system_one

    def system_one(state, questions):
        if seen["answers"] == 7:   # v1's first row takes 7 calls (a choice, then 6 per chunk); an 8th means it scored on
            raise RuntimeError("the evaluator went on past a non-finite answer: %d served" % seen["answers"])
        answer = real_one(state, questions)
        seen["answers"] += 1
        if seen["answers"] == 1:
            with torch.no_grad():
                dict(agent.model.named_parameters())[poison].view(-1)[0] = float("nan")
        return answer

    agent.system_one = system_one
    return agent


T.load_base = load_base
err = io.StringIO()
with contextlib.redirect_stderr(err):
    rc = EV.main(["--only", "v1", "--out-dir", str(out_dir), "--threads", "4"])
print(json.dumps(dict(seen, rc=rc, said=[line for line in err.getvalue().splitlines() if line.startswith("evaluate:")],
                      files=sorted(p.name for p in out_dir.iterdir()))))
"""


def test_evaluate_cli_refuses_a_non_finite_served_probability(laya_venue, tmp_path):
    """F-1, the evaluator: the real model serves one finite answer, then a NaN in a head parameter makes every served
    probability NaN, which J2's v1 scorer counted (VERIFY-FT1: every prediction BLOCKER, ECE 0.0)."""
    r = _laya(laya_venue, EVAL_CLI, str(ROOT / "scripts"), str(tmp_path / "eval"), POISONED)
    assert (r["rc"], r["answers"], r["files"]) == (5, 7, []), r   # the finite choice passed; no result was written
    assert r["said"] == ["evaluate: refused: NonFiniteAnswer: answer 'BLOCKER' serves the probability nan, not a finite "
                         "float: nothing is scored"], r


# ---------- DSV2: version 2 (task #251; D-083, D-085; tasks/briefs/jev-laya/DSV2-brief.md AMENDMENT 1) ----------

PIN = "434b727dfd2b6daa5aa3cf4d638e706f5dfa59cb"   # the brief's PIN: the version-2 record is built there (D-4)
V1_AT = ("0b342c7a29317d611a7f415eb411802276533f1a", "d7cd9b49abac267bb9b5290641ea353180a9a61047ce6c590809520b085cea1c")
RECORD = FINDINGS / "laya-ft-labels" / "2026-09-25-recorded"


def test_row_identities_know_a_commit_and_still_refuse_an_unknown_kind():
    row = {"item_id": "ap-x", "sources": [{"kind": "commit", "commit": "a" * 40, "row": "AF-AP-1"},
                                          {"kind": "incident", "heading": "h", "role": "linked"}]}
    assert C.row_identities(row) == {("commit", "a" * 40), ("incident", "h")}
    with pytest.raises(C.DatasetError, match=r"^row x: unknown source kind 'tweet'$"):
        C.row_identities({"item_id": "x", "sources": [{"kind": "tweet"}]})


def test_check_no_heldout_reads_a_kind_no_sample_holds_as_empty(tmp_path):
    heldout = C.heldout_identities(C.worktree_reader)
    ap_state = json.loads((FINDINGS / "ap-hawk-probe" / "sample.json").read_text())["sample"][0]["state"]
    commit_src = {"kind": "commit", "commit": "b" * 40, "row": "AF-AP-1"}
    clean = BD.make_row("ap", "ap.violates_row", {"query": "a FAKE commit message", "chunk": "c"}, [commit_src], None)
    linked = BD.make_row("ap", "ap.violates_row", {"query": "another FAKE message", "chunk": "c"},
                         [commit_src, {"kind": "incident", "heading": ap_state, "role": "linked"}], None)
    C.check_no_heldout([clean], heldout)   # no sample holds a commit: its identity reads as an empty set
    with pytest.raises(C.HeldOutLeak, match=r"^1 held-out row\(s\) in the dataset \(D-3\)"):
        C.check_no_heldout([clean, linked], heldout)   # a commit that added a held-out entry is held out with it
    incident = BD.make_row("ap", "ap.violates_row", {"query": "q", "chunk": "c"},
                           [{"kind": "incident", "line": 1, "heading": "h", "row": "AF-AP-1"}], None)
    with pytest.raises(KeyError):   # a SAMPLED kind missing from the held-out set is never read as empty
        C.check_no_heldout([incident], {k: v for k, v in heldout.items() if k != "incident"})
    _write_dataset(tmp_path / "ok", [clean])
    assert len(C.load_dataset(tmp_path / "ok")[0]) == 1
    _write_dataset(tmp_path / "leak", [clean, linked])
    with pytest.raises(C.HeldOutLeak):
        C.load_dataset(tmp_path / "leak")


V2_REPORT = REPORT + """
## Families

**F-5 — BLOCKER. A family paragraph finding: the probe reads a stale cache.** It was reproduced twice.

### F-6 — INFO — a heading finding about the timing table

The body line of F-6.
"""
V2_PC_REPORT = """# PC verify

1. BLOCKER — a numbered PC finding: the runner drops the exit code.

- **F-2 INFO — held out: this finding is in the fixture's J2c sample** Measured; no defect.
- **Q-7 FOLLOW-UP — held out: this finding is in the fixture's J2c sample, restated under a new id** Again.
"""
V2_TITLE = "held out: this finding is in the fixture's J2c sample"   # the J2 v1 sample's (masked) title: 53 characters
E_HELD = "**2026-09-02 11:0xZ — Held out: the heading the fixture's AP sample names (AF-AP-1).** Body text.\n"
E_NONE = "**2026-09-03 12:0xZ — A disk filled during a probe.** Nothing is named here.\n"
E_BOTH = "**2026-09-04 09:0xZ — The mirror again (AF-AP-2).** The body names AF-AP-2 too.\n"
ROW3 = "| AF-AP-3 | an unrelated row about disk space | df | x | y |\n"


def _v2_fixture_repo(tmp_path):
    """A repo whose history holds every version-2 source shape. -> (repo, pins, shas: message head -> sha)"""
    repo = tmp_path / "repo2"
    for d in ("tasks/briefs/t", "tasks/briefs/pc", "docs", "samples"):
        (repo / d).mkdir(parents=True)
    report_path = "tasks/briefs/t/VERIFY-T-report.md"
    (repo / report_path).write_text(V2_REPORT, encoding="utf-8")
    (repo / "tasks/briefs/pc/report-pc-verify-t.md").write_text(V2_PC_REPORT, encoding="utf-8")
    base = LOG.replace(E_HELD + "\n", "").replace(ROW3, "").replace("## ANTI-PATTERN", E_NONE + "\n## ANTI-PATTERN")
    (repo / "docs" / "INCIDENT-LOG.md").write_text(base, encoding="utf-8")
    f2 = next(b for b in C.J2C._blocks(report_path, V2_REPORT) if b[0] == "F-2")
    held = C.AP.AP_ID.sub("AF-AP-?", C.AP.heading([E_HELD.rstrip("\n")], 0))
    samples = {"j2_v1": {"sample": [{"row_digest": "d1", "label": "INFO", "lane": "VERIFY-T", "state": V2_TITLE}]},
               "j2c": {"sample": [{"row_digest": "d1", "label": "INFO", "lane": "VERIFY-T",
                                   "source": "%s#F-2" % report_path, "state": C.J2C._mask(f2[3])}]},
               "ap": {"rows": {}, "sample": [{"line": 5, "labels": ["AF-AP-1"], "state": held}]}}
    pins = {}
    for name, data in samples.items():
        body = (json.dumps(data, sort_keys=True) + "\n").encode("utf-8")
        (repo / "samples" / ("%s.json" % name)).write_bytes(body)
        pins[name] = ("samples/%s.json" % name, C.sha256_hex(body))
    _git(repo.parent, "init", "-q", str(repo))
    shas = {}

    def commit(message, edit):
        edit()
        _git(repo, "add", "-A")
        _git(repo, "commit", "-q", "-m", message)
        shas[message.split("\n")[0]] = _git(repo, "rev-parse", "HEAD").decode().strip()

    log = repo / "docs" / "INCIDENT-LOG.md"

    def insert(entry):
        return lambda: log.write_text(log.read_text().replace("## ANTI-PATTERN", entry + "\n## ANTI-PATTERN"))

    commit("fixture: base", lambda: None)
    commit("incident: log the held-out entry (AF-AP-1)", insert(E_HELD))
    commit("registry: AF-AP-3 (an unrelated row about disk space)",
           lambda: log.write_text(log.read_text() + ROW3))
    commit("incident: the mirror again (AF-AP-2)\n\nWhy: AF-AP-1 is named in the body only.", insert(E_BOTH))
    commit("docs: tidy the wording\n\nAF-AP-2 met again, in the body only.",
           lambda: (repo / "docs" / "notes.md").write_text("tidy\n"))
    commit("notes: the incident follow-up (AF-AP-2)\n\n2026-09-02 11:0xZ — Held out: the heading the fixture's AP "
           "sample names (AF-AP-1).", lambda: (repo / "docs" / "notes.md").write_text("follow-up\n"))
    return repo, pins, shas


def _by_source(items):
    out = {}
    for _prefix, qid, state, sources in items:
        s = sources[0]
        key = (s["kind"], s.get("path", "").split("/")[-1] + s.get("finding_id", "") if s["kind"] == "verify_finding"
               else s.get("heading", s.get("commit", ""))[:24], s.get("row"), qid)
        out[key] = (s.get("answer"), s.get("provenance"), state, sources)
    return out


def test_collect_v2_labels_every_source_with_its_recorded_answer(tmp_path):
    repo, pins, shas = _v2_fixture_repo(tmp_path)
    items, info = BD.collect_v2(BD.git_runner(repo), "HEAD", pins=pins)
    got = _by_source(items)
    finding = {k[1]: v for k, v in got.items() if k[0] == "verify_finding" and k[3] == "v1.finding_class"}
    blocking = {k[1]: v[0] for k, v in got.items() if k[0] == "verify_finding" and k[3] == "v1.blocking"}
    assert {k: v[0] for k, v in finding.items()} == {"VERIFY-T-report.mdF-1": "FOLLOW-UP", "VERIFY-T-report.mdT-1": "BLOCKER",
                                                   "VERIFY-T-report.mdF-5": "BLOCKER", "VERIFY-T-report.mdF-6": "INFO",
                                                   "report-pc-verify-t.md1": "BLOCKER"}
    assert blocking == {"VERIFY-T-report.mdF-1": "false", "VERIFY-T-report.mdT-1": "true",
                        "VERIFY-T-report.mdF-5": "true", "VERIFY-T-report.mdF-6": "false", "report-pc-verify-t.md1": "true"}
    assert {v[1] for v in finding.values()} == {"verifier-class"}
    assert {v[3][0]["family"] for v in finding.values()} == {"grammar", "F3", "F6", "F8"}
    for _a, _p, state, _s in finding.values():   # the state is masked and scrubbed; the label lives in the sources
        assert not CLASS_WORDS.search(state) and all(value not in state for value in FAKE_SECRETS.values())
    assert info["excluded"] == {"identity": {"verify_finding": 1, "incident": 1, "commit": 1},
                                "text": {"verify_finding": 2, "incident": 0, "commit": 1}}
    ap = {(k[1], k[2]): v for k, v in got.items() if k[0] in ("incident", "commit")}
    e1, e4 = "2026-09-01 10:0xZ — A gate", "2026-09-04 09:0xZ — The mi"
    assert {r: ap[(e1[:24], r)][:2] for r in ("AF-AP-1", "AF-AP-2", "AF-AP-3")} == {
        "AF-AP-1": ("true", "body-cite"), "AF-AP-2": ("true", "heading-cite"), "AF-AP-3": ("false", "not-cited")}
    assert {r: ap[(e4[:24], r)][:2] for r in ("AF-AP-1", "AF-AP-2", "AF-AP-3")} == {
        "AF-AP-1": ("false", "not-cited"), "AF-AP-2": ("true", "heading-cite+body-cite"), "AF-AP-3": ("false", "not-cited")}
    assert all(ap[("2026-09-03 12:0xZ — A disk"[:24], r)][:2] == (None, None) for r in ("AF-AP-1", "AF-AP-2", "AF-AP-3"))
    reg, subj = shas["registry: AF-AP-3 (an unrelated row about disk space)"], shas["incident: the mirror again (AF-AP-2)"]
    base = shas["fixture: base"]   # it creates the registry: a commit that adds rows is a source whatever its message says
    assert {r: ap[(base[:24], r)][:2] for r in ("AF-AP-1", "AF-AP-2", "AF-AP-3")} == {
        "AF-AP-1": ("true", "registry-commit"), "AF-AP-2": ("true", "registry-commit"), "AF-AP-3": ("false", "not-cited")}
    assert [s["heading"][:17] for s in ap[(base[:24], "AF-AP-1")][3][1:]] == ["2026-09-01 10:0xZ", "2026-09-03 12:0xZ"]
    assert {r: ap[(reg[:24], r)][:2] for r in ("AF-AP-1", "AF-AP-2", "AF-AP-3")} == {
        "AF-AP-1": ("false", "not-cited"), "AF-AP-2": ("false", "not-cited"), "AF-AP-3": ("true", "registry-commit")}
    assert {r: ap[(subj[:24], r)][:2] for r in ("AF-AP-1", "AF-AP-2", "AF-AP-3")} == {
        "AF-AP-1": (None, None), "AF-AP-2": ("true", "commit-subject"), "AF-AP-3": ("false", "not-cited")}
    assert ap[(subj[:24], "AF-AP-2")][3][1:] == [{"kind": "incident", "role": "linked",
                                                   "heading": C.AP.AP_ID.sub("AF-AP-?", C.AP.heading([E_BOTH], 0))}]
    assert all(s["commit"] in (base, reg, subj) for (_k, _r), v in ap.items() for s in v[3][:1] if s["kind"] == "commit")
    assert info["ap"]["commits_admitted"] == {"registry-commit": 2, "commit-subject": 1}
    assert (info["ap"]["commits_body_only_not_admitted"], info["ap"]["commit_rows_unlabeled_body_cite"]) == (1, 1)
    for _a, _p, state, _s in ap.values():
        assert not re.search(r"\bAF-AP-\d+\b", state["query"]) and list(state) == ["query", "chunk"]
        assert all(value not in state["query"] for value in FAKE_SECRETS.values())
    assert BD.collect_v2(BD.git_runner(repo), "HEAD", pins=pins) == (items, info)   # deterministic (D-4)


def test_a_commit_that_adds_a_heldout_entry_is_held_out_and_the_loader_is_the_backstop(tmp_path):
    """AMENDMENT 1 item 2: the builder leaves the commit out; a build that let it through is refused at load."""
    repo, pins, shas = _v2_fixture_repo(tmp_path)
    items, info = BD.collect_v2(BD.git_runner(repo), "HEAD", pins=pins)
    held_sha = shas["incident: log the held-out entry (AF-AP-1)"]
    heldout = C.heldout_identities(lambda p: BD.git_runner(repo)("show", "HEAD:" + p), pins)
    assert info["excluded"]["identity"]["commit"] == 1
    assert not any(s.get("commit") == held_sha for it in items for s in it[3])
    assert not any(s.get("heading") in heldout["incident"] for it in items for s in it[3])
    clean = [BD.make_row(*it, None) for it in items if it[3][0]["kind"] == "commit"]
    assert any(s.get("role") == "linked" for row in clean for s in row["sources"])   # a clean commit's link loads
    _write_dataset(tmp_path / "clean", clean)
    assert len(C.load_dataset(tmp_path / "clean", heldout)[0]) == len(clean) == 9
    planted = BD.make_row("ap", "ap.violates_row", {"query": "incident: log the held-out entry (AF-AP-?)",
                                                    "chunk": clean[0]["state"]["chunk"]},
                          [dict(clean[0]["sources"][0], commit=held_sha),   # what a builder without the rule would write
                           {"kind": "incident", "heading": sorted(heldout["incident"])[0], "role": "linked"}], None)
    _write_dataset(tmp_path / "planted", clean + [planted])
    with pytest.raises(C.HeldOutLeak, match=r"^1 held-out row\(s\) in the dataset \(D-3\).*incident 2026-09-02"):
        C.load_dataset(tmp_path / "planted", heldout)


def test_heldout_text_is_left_out_wherever_it_is_planted(tmp_path):
    """D-3 by text: the PC report restates the held-out F-2 verbatim (another path, so another identity) and Q-7 carries
    the held-out title under a new id; a commit message quotes the held-out heading. All three are left out by text."""
    repo, pins, _shas = _v2_fixture_repo(tmp_path)
    items, info = BD.collect_v2(BD.git_runner(repo), "HEAD", pins=pins)
    fids = {(s["path"].split("/")[-1], s["finding_id"]) for it in items for s in it[3] if s["kind"] == "verify_finding"}
    assert ("report-pc-verify-t.md", "F-2") not in fids and ("report-pc-verify-t.md", "Q-7") not in fids
    assert info["excluded"]["text"] == {"verify_finding": 2, "incident": 0, "commit": 1}
    overlap = BD.Overlap(BD.heldout_texts(lambda p: BD.git_runner(repo)("show", "HEAD:" + p), pins))
    assert overlap.hit("before " + V2_TITLE.upper() + " after") and not overlap.hit("a clean finding about a cache")
    for it in items:   # the second net holds on everything that stayed
        assert overlap.hit(*(it[2].values() if isinstance(it[2], dict) else [it[2]])) is None


def test_block_end_cap_is_carried_in_the_source(tmp_path):
    """AMENDMENT 1 item 5: a block over 60 lines is cut there and says so in its source."""
    repo, pins, _shas = _v2_fixture_repo(tmp_path)
    long_finding = "\n**F-9 — INFO. A long finding.** " + "\n".join("line %d of the body" % n for n in range(80)) + "\n"
    report = repo / "tasks/briefs/t/VERIFY-T-report.md"
    report.write_text(report.read_text() + long_finding, encoding="utf-8")
    _git(repo, "commit", "-q", "-am", "a long finding")
    items, info = BD.collect_v2(BD.git_runner(repo), "HEAD", pins=pins)
    f9 = [it for it in items if it[3][0].get("finding_id") == "F-9"]
    assert len(f9) == 2 and all(it[3][0]["block_end"] == "cap" for it in f9) and info["capped_blocks"] == 1
    assert f9[0][2].count("\n") == 59 and "line 59 of the body" in f9[0][2] and "line 60" not in f9[0][2]
    others = [it for it in items if it[3][0]["kind"] == "verify_finding" and it[3][0]["finding_id"] != "F-9"]
    assert others and all("block_end" not in it[3][0] for it in others)


def test_leak_flags_mark_the_rows_and_leave_none_out():
    """AMENDMENT 1 item 8: what a state still says about its label is flagged in every source, never dropped. DSV2-R1
    (VERIFY-DSV2 V-6): `blocking-words` also flags the five ruled forms, one state each (F-a to F-e), while a hook's
    "blocks" and a severity word stay unflagged; every alternative of the five forms flags on its own."""
    forms = ["Predicate: not contract-mapped; the contract names no file-type rule",   # F-a the predicate walk
             "No [CLASS] in this round.",                                             # F-b a class summary
             "The finding would not block on its own.",                              # F-c a negated block
             "This is a [CLASS] by the rule.",                                        # F-d the class stated
             "It is not material to the claim."]                                      # F-e materiality stated
    rows = [BD.make_row("v1", "v1.finding_class", "two [CLASS]s and some BLOCKERS remain", _v1_source(), None),
            BD.make_row("v1", "v1.blocking", "the gate says NOT-READY; it is not a [CLASS]", _v1_source(fid="F-8"), None),
            BD.make_row("v1", "v1.blocking", "a clean finding text", _v1_source(fid="F-7"), None),
            BD.make_row("ap", "ap.violates_row", {"query": "here a gate trusts a mirror test", "chunk": "row AF-AP-4"},
                        [{"kind": "incident", "line": 1, "heading": "h", "row": "AF-AP-2", "answer": "true",
                          "provenance": "heading-cite"}], None)]
    rows += [BD.make_row("v1", "v1.blocking", state, _v1_source(fid="F-%d" % n), None)
             for n, state in enumerate(forms + ["the hook blocks the call", "optional hardening"], 10)]
    counts = BD.flag_leaks(rows, {"AF-AP-2": "A gate trusts a mirror"})
    assert [[s.get("leak") for s in r["sources"]] for r in rows] == [
        ["class-word"], ["blocking-words"], [None], ["ap-id+row-name"]] + [["blocking-words"]] * 5 + [[None]] * 2
    assert counts == {"v1.finding_class|class-word": 1, "v1.blocking|blocking-words": 6, "ap.violates_row|ap-id": 1,
                      "ap.violates_row|row-name": 1}
    for words in ("Contract mapping: none.", "Canonical: yes.", "Canonical path: the real CLI.",
                  "canonical reproduction = the real CLI", "Material: yes.", "Material effect: none.",
                  "Discriminator: the probe.", "Task ownership: the lane.", "In boundary: yes.", "in-boundary: yes",
                  "No [CLASS].", "It does not block.", "It doesn't block.", "They do not block.", "It did not block.",
                  "It will not block.", "It cannot block.", "It is [CLASS].", "It is an [CLASS].",
                  "Filed as a [CLASS].", "Filed as an [CLASS].", "Filed as [CLASS].", "No material effect.",
                  "Not material.", "Immaterial."):
        row = BD.make_row("v1", "v1.blocking", words, _v1_source(), None)
        assert BD.flag_leaks([row], {}) == {"v1.blocking|blocking-words": 1}, words


def test_version_1_is_byte_identical_and_still_loads(laya_venue, tmp_path):
    """The brief's byte clause: version 1's dataset at 0b342c7 is d7cd9b49..., the committed OpenJev manifest's, and it
    loads through the trainer's loader after the common.py change."""
    commit, sha = V1_AT
    proc = subprocess.run([laya_venue["py"], str(ROOT / "scripts" / "laya_ft" / "build_dataset.py"), "--commit", commit,
                           "--out", str(tmp_path / "v1"), "--model-dir", laya_venue["model_dir"]],
                          capture_output=True, text=True, timeout=600, env=dict(os.environ, HF_HUB_OFFLINE="1"))
    assert proc.returncode == 0, proc.stderr[-3000:]
    committed = json.loads((FINDINGS / "laya-ft-labels" / "2026-09-24-openjev" / "dataset-manifest.json").read_text())
    assert C.sha256_hex((tmp_path / "v1" / "dataset.jsonl").read_bytes()) == sha == committed["dataset"]["sha256"]
    rows, _manifest = C.load_dataset(tmp_path / "v1")
    assert len(rows) == 1788


def test_version_2_record_rebuilds_byte_identically_at_the_pin(laya_venue, tmp_path):
    """D-4: the committed version-2 record (its manifest and labels) rebuilds byte for byte from the PIN; the labels
    join every labeled row with no stale label; a second build is identical."""
    outs = []
    for name in ("a", "b"):
        proc = subprocess.run([laya_venue["py"], str(ROOT / "scripts" / "laya_ft" / "build_dataset.py"), "--version", "2",
                               "--commit", PIN, "--out", str(tmp_path / name), "--model-dir", laya_venue["model_dir"]],
                              capture_output=True, text=True, timeout=600, env=dict(os.environ, HF_HUB_OFFLINE="1"))
        assert proc.returncode == 0, proc.stderr[-3000:]
        outs.append(tmp_path / name)
    for f in ("dataset.jsonl", "manifest.json", "summary.json"):
        assert (outs[0] / f).read_bytes() == (outs[1] / f).read_bytes(), f
    assert (outs[0] / "manifest.json").read_bytes() == (RECORD / "dataset-manifest.json").read_bytes()
    labels = tmp_path / "labels.jsonl"
    proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "laya_ft" / "recorded_labels.py"), "--dataset",
                           str(outs[0]), "--out", str(labels), "--summary", str(tmp_path / "summary.json")],
                          capture_output=True, text=True, timeout=600)
    assert proc.returncode == 0, proc.stderr[-3000:]
    assert labels.read_bytes() == (RECORD / "labels.jsonl").read_bytes()
    assert (tmp_path / "summary.json").read_bytes() == (RECORD / "summary.json").read_bytes()
    rows, _m = C.load_dataset(outs[0])
    records, stats = C.read_labels(labels)
    joined = C.join_labels(rows, records)
    assert len(joined) == len(records) == stats["records"] and stats["torn"] == stats["duplicates"] == 0
    fit = _laya(laya_venue, FIT_CHECK, str(ROOT / "scripts"), str(outs[0]), laya_venue["model_dir"])
    assert fit["rows"] == len(rows) and fit["truncated"] == 0 and fit["markers_bad"] == 0
