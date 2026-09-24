"""scripts/jev_context.py: the parsers on captured instrument output, the D-2 merge, the D-3 pre-filter and Jev call,
the KC-J5 reorder, the D-4 budget and determinism, and run_tool's fail-open paths (tasks #227/#229, the JT2 brief).

The instrument fixtures below are the lane's LIVE captures of 2026-09-24 (the lane report, section 0), trimmed; the two
built from a live shape rather than captured whole say so. The loopback Jev double returns the Laya server's reply
SHAPE (scripts/laya_systemone_server.py: answers keyed by chunk id, fan_out) with scores the test chooses; no number it
returns is a model answer (the live Jev runs are the report's A1, A3 and A4). No test here calls the real endpoint or
the bridge. Every secret below is a fake string.
"""
import http.server
import importlib.util
import json
import pathlib
import random
import socket
import sys
import threading
import time

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
LIB = ROOT / "scripts" / "jev_context.py"


def _load():
    spec = importlib.util.spec_from_file_location("jev_context_under_test", LIB)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


jc = _load()


# ---------- the Jev double ----------

class JevDouble:
    """Records every request; answers each chunk id with scorer(query, chunk text). Routed like the real server
    (laya_systemone_server.py do_POST): only POST /v1/systemone answers, any other path is 404 (AF-AP-139). A scorer
    that raises makes that request a 500, as the server's model error is."""

    def __init__(self, scorer):
        self.requests, self.paths = [], []
        outer = self

        class H(http.server.BaseHTTPRequestHandler):
            def _send(self, code, obj):
                body = json.dumps(obj).encode()
                self.send_response(code)
                self.send_header("content-type", "application/json")
                self.send_header("content-length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_POST(self):
                outer.paths.append(self.path)
                if self.path != "/v1/systemone":
                    return self._send(404, {"error": "not found"})
                req = json.loads(self.rfile.read(int(self.headers.get("content-length") or 0)))
                outer.requests.append(req)
                texts = {c["id"]: c["text"] for c in req["state"]["chunks"]}
                answers = {}
                try:
                    for qid in req["questions"]:
                        v = float(scorer(req["state"]["query"], texts[qid]))
                        answers[qid] = {"type": "noul", "noul": v, "confidence": max(v, 1 - v)}
                except Exception as e:
                    return self._send(500, {"error": "system_one failed: %s" % type(e).__name__})
                self._send(200, {"model": "double", "answers": answers, "fan_out": len(answers), "latency_ms": 1.0})

            def log_message(self, *args):
                pass

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), H)
        self.url = "http://127.0.0.1:%d" % self.server.server_address[1]
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()


@pytest.fixture
def double():
    made = []

    def make(scorer):
        d = JevDouble(scorer)
        made.append(d)
        return d
    yield make
    for d in made:
        d.close()


def closed_port_url():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return "http://127.0.0.1:%d" % port


def touch(root, *rels):
    for rel in rels:
        p = pathlib.Path(root) / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("x = 1\n")


def H(inst, path, line, text="t"):
    return {"instrument": inst, "path": path, "line": line, "text": text}


# ---------- captured instrument output (2026-09-24) ----------

GRAFT_STRUCTURAL = """graft ask — "who calls merged in install_session_hooks"  (structural)

callers / references of merged

- main  scripts/install_session_hooks.py:L83-L126  (calls) — def main(argv: list[str]) -> int
"""

GRAFT_LEXICAL = """[graft] refreshed the graph (1 file changed) before answering
graft ask — "the bridge stderr bind warning lands on the data line and a grep -v drops it"  (lexical)

1. pc_bridge_exec.py · file  [symbol]
   scripts/pc_bridge_exec.py

2. bind_text · function  [symbol]
   sandbox-kit/codebase-memory-mcp/src/store/store.c:L95-L97
   static int bind_text(sqlite3_stmt *s, int col, const char *v)

6. parse_pc_reply · function  [symbol]
   scripts/jev.py:L318-L339
   def parse_pc_reply(env)

matched in: (root) (4) · sandbox-kit/aleph/ (4)
"""

GN_QUERY = json.dumps({
    "processes": [{"id": "proc:1", "summary": "sign a review", "priority": 1.2}],
    # process_symbols: built on the live definitions' fields + process_id (local-backend.js:2187-2191), not captured
    "process_symbols": [{"id": "Method:tests/test_governance_review.py:_Key.sign#2", "name": "sign",
                         "filePath": "tests/test_governance_review.py", "startLine": 66, "endLine": 71,
                         "process_id": "proc:1", "step_index": 1}],
    "definitions": [
        {"id": "Class:tests/test_governance_review.py:_Key", "name": "_Key",
         "filePath": "tests/test_governance_review.py", "startLine": 47, "endLine": 75},
        {"id": "Struct:sandbox-kit/codebase-memory-mcp/src/store/store.h:cbm_package_summary_t",
         "name": "cbm_package_summary_t", "filePath": "sandbox-kit/codebase-memory-mcp/src/store/store.h",
         "startLine": 471, "endLine": 476}],
    "timing": {"wall": 6528.2}})

GN_CONTEXT_AMBIGUOUS = json.dumps({
    "status": "ambiguous", "message": "Found 2 symbols matching 'merged'. Use uid, file_path, or kind to disambiguate.",
    "totalCandidates": 2,
    "candidates": [
        {"uid": "Function:scripts/install_session_hooks.py:merged", "name": "merged", "kind": "Function",
         "filePath": "scripts/install_session_hooks.py", "line": 64, "score": 0.56},
        {"uid": "Property:src/agent_factory/decisions/volatile.py:_redact_str.merged@464:4", "name": "merged",
         "kind": "", "filePath": "src/agent_factory/decisions/volatile.py", "line": 465, "score": 0.5}]})

GN_CONTEXT_FOUND = json.dumps({
    "status": "found",
    "symbol": {"uid": "Function:scripts/transcript_export.py:scrub", "name": "scrub", "kind": "Function",
               "filePath": "scripts/transcript_export.py", "startLine": 85, "endLine": 88},
    "incoming": {"calls": [{"uid": "Function:scripts/hiccup_scan.py:excerpt", "name": "excerpt",
                            "filePath": "scripts/hiccup_scan.py"},
                           {"uid": "Function:scripts/transcript_export.py:export", "name": "export",
                            "filePath": "scripts/transcript_export.py"}]},
    "outgoing": {}})

CBM_OUT = """total: 100
search_mode: bm25
results: 50  (cols: qn label file lines rank)
  home-user-agent-factory.sandbox-kit.aleph.tests.test_helpers.TestChunk.test_chunk_large_chunk_size Method sandbox-kit/aleph/tests/test_helpers.py 179-182 -23.56
  home-user-agent-factory.tests.test_laya_systemone_server.test_chunk_map_accepts_only_a_complete_chunk_list Function tests/test_laya_systemone_server.py 44-50 -23.14
  home-user-agent-factory.scripts.laya_systemone_server._chunk_map Function scripts/laya_systemone_server.py 118-127 -22.76
"""

CRG_OK = json.dumps({
    "status": "ok", "pattern": "callers_of",
    "target": "/home/user/agent-factory/scripts/install_session_hooks.py::merged", "result_count": 2,
    "results": [
        {"id": 57308, "kind": "Function", "name": "main",
         "qualified_name": "/home/user/agent-factory/scripts/install_session_hooks.py::main",
         "file_path": "/home/user/agent-factory/scripts/install_session_hooks.py", "line_start": 83, "line_end": 126,
         "is_test": False},
        {"id": 57335, "kind": "Test", "name": "test_a_repo_path_that_needs_quoting_stays_idempotent_and_removable",
         "file_path": "/home/user/agent-factory/tests/test_session_hooks.py", "line_start": 223, "line_end": 229,
         "is_test": True}]})

# built on the live `ambiguous` reply's fields (412 fuzzy candidates for `_result`), trimmed to three
CRG_AMBIGUOUS = json.dumps({
    "status": "ambiguous", "summary": "'merged' matches 173 node(s). Re-run with a qualified_name from disambiguation.",
    "candidates": [
        {"id": 231, "kind": "Function", "name": "cmd_merge",
         "qualified_name": "/home/user/agent-factory/.agents/skills/arbor/scripts/tree.py::cmd_merge",
         "file_path": "/home/user/agent-factory/.agents/skills/arbor/scripts/tree.py", "line_start": 10},
        {"id": 57300, "kind": "Function", "name": "merged",
         "qualified_name": "/home/user/agent-factory/scripts/install_session_hooks.py::merged",
         "file_path": "/home/user/agent-factory/scripts/install_session_hooks.py", "line_start": 64},
        {"id": 999, "kind": "Function", "name": "merged_rows",
         "qualified_name": "/home/user/agent-factory/scripts/x.py::merged_rows",
         "file_path": "/home/user/agent-factory/scripts/x.py", "line_start": 5}]})


# ---------- the parsers ----------

def test_graft_both_shapes_give_the_existing_non_vendored_sites(tmp_path):
    touch(tmp_path, "scripts/install_session_hooks.py", "scripts/pc_bridge_exec.py", "scripts/jev.py",
          "sandbox-kit/codebase-memory-mcp/src/store/store.c")
    got = [(h["path"], h["line"]) for h in jc.parse_graft(GRAFT_STRUCTURAL + GRAFT_LEXICAL, str(tmp_path))]
    # the vendored store.c EXISTS here and is still dropped; the three project sites keep graft's line
    assert got == [("scripts/install_session_hooks.py", 83), ("scripts/pc_bridge_exec.py", 0), ("scripts/jev.py", 318)]


def test_graft_names_no_site_that_does_not_exist(tmp_path):
    # negative control: the same output over an empty root yields nothing (graft names paths; the parser checks them)
    assert jc.parse_graft(GRAFT_STRUCTURAL + GRAFT_LEXICAL, str(tmp_path)) == []


def test_gitnexus_query_keeps_symbols_and_drops_vendored():
    got = [(h["path"], h["line"], h["text"]) for h in jc.parse_gitnexus_query(GN_QUERY, "/r")]
    assert got == [("tests/test_governance_review.py", 66, "Method sign (flow: sign a review)"),
                   ("tests/test_governance_review.py", 47, "Class _Key")]
    assert jc.parse_gitnexus_query("Error: LadybugDB unavailable", "/r") is None      # not JSON: unmapped upstream


def test_gitnexus_context_found_gives_definition_and_file_level_callers():
    got = [(h["path"], h["line"], h["text"]) for h in jc.parse_gitnexus_context(GN_CONTEXT_FOUND, "/r", "scrub")]
    assert got == [("scripts/transcript_export.py", 85, "Function scrub: the definition"),
                   ("scripts/hiccup_scan.py", 0, "Function excerpt calls scrub"),
                   ("scripts/transcript_export.py", 0, "Function export calls scrub")]


def test_gitnexus_context_ambiguous_gives_the_candidates():
    got = [(h["path"], h["line"]) for h in jc.parse_gitnexus_context(GN_CONTEXT_AMBIGUOUS, "/r", "merged")]
    assert got == [("scripts/install_session_hooks.py", 64), ("src/agent_factory/decisions/volatile.py", 465)]
    assert jc.parse_gitnexus_context('{"error": "Symbol \'zz\' not found"}', "/r", "zz") == []


def test_gitnexus_context_not_found_is_an_answer_but_a_lock_is_unmapped(tmp_path):
    """Live 2026-09-24: `context CalledProcessError` exits 1 with `{"error": "Symbol ... not found"}` on stdout (an
    answer), and a locked index exits 1 with `Error: LadybugDB unavailable` on stderr (an outage)."""
    (tmp_path / ".gitnexus").mkdir()
    (tmp_path / ".gitnexus" / "run.cjs").write_text("")
    node = tmp_path / "node"
    node.write_text("#!%s\nimport json, sys\n"
                    "if sys.argv[2] == 'query':\n    print(json.dumps({'processes': [], 'definitions': []}))\n"
                    "elif sys.argv[3] == 'Missing':\n    print(json.dumps({'error': \"Symbol 'Missing' not found\"}))\n"
                    "    sys.exit(1)\n"
                    "else:\n    print('Error: LadybugDB unavailable for /r. Another process may be rebuilding the index.',"
                    " file=sys.stderr)\n    sys.exit(1)\n" % sys.executable)
    node.chmod(0o755)
    ctx = jc.Context(str(tmp_path), {"node": [str(node)]})
    hits, notes, ok = jc.inst_gitnexus("q", [("ident", "Missing", None)], ctx)
    assert (hits, notes, ok) == ([], [], True)
    hits, notes, ok = jc.inst_gitnexus("q", [("ident", "Locked", None)], ctx)
    assert hits == [] and ok is True          # the query answered; the context call did not
    assert notes == ["unmapped — gitnexus context Locked unavailable (rc 1: Error: LadybugDB unavailable for /r. "
                     "Another process may be rebuilding the index.)"]


def test_cbm_rows_parse_and_vendored_rows_drop():
    got = [(h["path"], h["line"], h["text"]) for h in jc.parse_cbm(CBM_OUT, "/r", "home-user-agent-factory")]
    assert got == [
        ("tests/test_laya_systemone_server.py", 44,
         "Function tests.test_laya_systemone_server.test_chunk_map_accepts_only_a_complete_chunk_list"),
        ("scripts/laya_systemone_server.py", 118, "Function scripts.laya_systemone_server._chunk_map")]


def test_crg_ok_lists_callers_with_repo_relative_paths():
    hits, again = jc.parse_crg(CRG_OK, "/home/user/agent-factory", "merged")
    assert [(h["path"], h["line"]) for h in hits] == [("scripts/install_session_hooks.py", 83),
                                                     ("tests/test_session_hooks.py", 223)]
    assert again == []


def test_crg_ambiguous_takes_only_exact_names_and_re_asks_them():
    hits, again = jc.parse_crg(CRG_AMBIGUOUS, "/home/user/agent-factory", "merged")
    assert [(h["path"], h["line"], h["text"]) for h in hits] == [
        ("scripts/install_session_hooks.py", 64, "Function merged: the definition")]
    assert again == ["/home/user/agent-factory/scripts/install_session_hooks.py::merged"]


def test_crg_wrapper_re_asks_the_qualified_name(tmp_path):
    """The real inst_crg over a stand-in binary that answers like crg did live: ambiguous for the bare name, ok for
    the qualified one. Proves the re-ask path end to end (the parser tests above prove the shapes)."""
    (tmp_path / ".code-review-graph").mkdir()
    (tmp_path / ".code-review-graph" / "graph.db").write_text("")
    live_root = "/home/user/agent-factory"          # the captures' root, moved to this test's root
    fake = tmp_path / "crg"
    fake.write_text("#!%s\nimport sys\nprint(%r if '::' in sys.argv[-1] else %r)\n"
                    % (sys.executable, CRG_OK.replace(live_root, str(tmp_path)),
                       CRG_AMBIGUOUS.replace(live_root, str(tmp_path))))
    fake.chmod(0o755)
    ctx = jc.Context(str(tmp_path), {"crg": [str(fake)]})
    hits, notes, ok = jc.inst_crg("who calls merged_x", [("ident", "merged", None)], ctx)
    assert ok and notes == []
    assert [(h["path"], h["line"]) for h in hits] == [("scripts/install_session_hooks.py", 64),
                                                     ("scripts/install_session_hooks.py", 83),
                                                     ("tests/test_session_hooks.py", 223)]


def test_rg_lines_parse():
    out = "scripts/a.py:12:    x = foo_bar()\ntests/test_a.py:3:foo_bar\nsandbox-kit/v.py:1:foo_bar\nnoise\n"
    assert [(h["path"], h["line"]) for h in jc.parse_rg(out, "/r")] == [("scripts/a.py", 12), ("tests/test_a.py", 3)]


# built with chr(), never typed as escapes (CLAUDE.md: the tools turn a typed U+2028 escape into the literal bytes)
SEPARATORS = [chr(0x0C), chr(0x0B), chr(0x1C), chr(0x85), chr(0x2028)]


@pytest.mark.parametrize("sep", SEPARATORS, ids=["ff", "vt", "fs", "nel", "ls"])
def test_rg_keeps_a_matched_line_whole_across_a_line_separator(sep):
    """JT3's finding (AF-AP-132's class): rg prints a matched line raw and ends it with "\\n" only, so a form feed (or
    another character str.splitlines() breaks on) inside it must not cut it. splitlines() gave the snippet's head only
    and turned the tail, shaped like `path:NN:`, into a hit of its own (3 hits here instead of 2)."""
    out = "scripts/a.py:12:x = 1" + sep + "scripts/evil.py:99:y\nscripts/b.py:3:z\n"
    got = [(h["path"], h["line"], h["text"]) for h in jc.parse_rg(out, "/r")]
    assert got == [("scripts/a.py", 12, "x = 1 scripts/evil.py:99:y"), ("scripts/b.py", 3, "z")]


def test_graft_keeps_an_entry_whole_across_a_form_feed(tmp_path):
    touch(tmp_path, "scripts/a.py", "scripts/b.py")
    out = ("1. real · function  [symbol]\n   scripts/a.py:L5-L9\n   def real(x):" + chr(0x0C) +
           "2. bogus · file\n   scripts/b.py\n")
    # splitlines() would start a second entry at the fragment and report scripts/b.py as its own site
    assert [(h["path"], h["line"]) for h in jc.parse_graft(out, str(tmp_path))] == [("scripts/a.py", 5)]


def test_git_log_keeps_a_subject_whole_across_a_form_feed(tmp_path):
    git = tmp_path / "git"
    git.write_text("#!%s\nprint('abc1234 fix the reader' + chr(12) + 'deadbee not a commit')\n" % sys.executable)
    git.chmod(0o755)
    ctx = jc.Context(str(tmp_path), {"git": [str(git)]})
    hits, notes, ok = jc.inst_gitlog("q", [("ident", "some_token", None)], ctx)
    assert ok and notes == []
    assert [h["path"] for h in hits] == ["git:abc1234"]        # splitlines() made `git:deadbee` a second commit


# ---------- tokens ----------

TRACE = '''Traceback (most recent call last):
  File "/home/user/agent-factory/scripts/jev.py", line 454, in rank
    return _api("rank", (query, chunks, instructions), opts)
tests/test_proof_status.py:192: FileNotFoundError: `gpg --quick-generate-key` failed; see parse_pc_reply and os.path.exists'''


def test_tokens_of_a_trace_in_distinctive_order():
    assert jc.tokens(TRACE) == [
        ("quoted", "gpg --quick-generate-key", None),
        ("ident", "os.path.exists", None), ("ident", "parse_pc_reply", None),
        ("error", "FileNotFoundError", None), ("flag", "--quick-generate-key", None),
        ("fileref", "/home/user/agent-factory/scripts/jev.py", 454), ("fileref", "tests/test_proof_status.py", 192)]
    assert jc.identifiers(jc.tokens(TRACE)) == ["parse_pc_reply", "exists"]


def test_prose_falls_back_to_long_words():
    toks = jc.tokens("total-isolation instrument offered as a selective-egress negative control")
    assert [k for k, _, _ in toks] == ["word"] * 6
    assert [t for _, t, _ in toks] == ["instrument", "isolation", "selective", "negative", "control", "offered"]


# ---------- D-2 merge ----------

def test_same_path_within_five_lines_merges_and_keeps_every_instrument():
    hits = [H("rg", "a.py", 10, "ten"), H("graft", "a.py", 15, "fifteen"), H("cbm", "a.py", 16, "sixteen"),
            H("rg", "b.py", 3, "three")]
    got = [(c["path"], c["line"], c["instruments"], c["agreement"], c["text"]) for c in jc.merge(hits, set())]
    # 15 - 10 = 5 merges; 16 - 10 = 6 does not (the span is anchored at the cluster's first line)
    assert got == [("a.py", 10, ["graft", "rg"], 2, "ten | fifteen"), ("a.py", 16, ["cbm"], 1, "sixteen"),
                   ("b.py", 3, ["rg"], 1, "three")]


def test_record_rows_never_merge_and_are_not_files_to_read():
    hits = [H("registry", "docs/INCIDENT-LOG.md", 10, "row one"), H("registry", "docs/INCIDENT-LOG.md", 11, "row two"),
            H("rg", "a.py", 1, "x")]
    chunks = jc.merge(hits, set())
    assert [(c["path"], c["line"], c["record"]) for c in chunks] == [
        ("a.py", 1, False), ("docs/INCIDENT-LOG.md", 10, True), ("docs/INCIDENT-LOG.md", 11, True)]
    assert [f["path"] for f in jc.files_to_read(jc.order_unranked(chunks), "unranked")] == ["a.py"]


def test_a_merged_chunk_text_is_capped_at_400():
    hits = [H("rg", "a.py", 1, "x" * 300), H("graft", "a.py", 2, "y" * 300)]
    (c,) = jc.merge(hits, set())
    assert len(c["text"]) == jc.TEXT_CAP == 400


# ---------- D-3 pre-filter, the Jev call, the orders ----------

def _chunks(n):
    """n code chunks: chunk i has lexical i and agreement 1 (so the unranked order is by lexical, descending)."""
    return [{"id": "k%d" % i, "path": "f%02d.py" % i, "line": 1, "instruments": ["rg"], "agreement": 1,
             "record": False, "text": "chunk %d" % i, "lexical": i} for i in range(n)]


def test_prefilter_sends_48_protected_first_then_by_lexical():
    ch = _chunks(60)
    protect = [ch[0], ch[1]]                      # the two WORST by lexical, protected
    sent = jc.prefilter(ch, protect=protect)
    assert len(sent) == jc.MAX_JEV_CHUNKS == 48
    assert [c["id"] for c in sent[:2]] == ["k0", "k1"]
    assert [c["id"] for c in sent[2:]] == ["k%d" % i for i in range(59, 13, -1)]
    assert "k2" not in {c["id"] for c in sent}     # negative control: an unprotected low chunk is not sent


def _by_index(q, t):
    """A varied score per chunk (the `chunk N` in its text): the test double never answers all-equal by accident."""
    return 0.1 + int(t.rsplit("chunk ", 1)[1]) / 100.0


def test_jev_call_is_per_chunk_with_the_query_capped_to_its_tail(double):
    d = double(_by_index)
    question = "HEAD " + "alpha beta gamma " * 240 + "TAIL"         # prose: the scrubber leaves it whole
    assert len(question) > 4000
    scores, reason, sent = jc.jev_rank(question, _chunks(3), url=d.url, timeout=5, log=False)
    assert reason is None and set(scores) == {"k0", "k1", "k2"}
    (req,) = d.requests
    assert d.paths == ["/v1/systemone"]
    assert req["state"]["query"] == question[-jc.JEV_QUERY_CHARS:] and len(req["state"]["query"]) == 1200
    assert req["state"]["query"].endswith("TAIL") and "HEAD" not in req["state"]["query"]
    assert [c["id"] for c in req["state"]["chunks"]] == ["k2", "k1", "k0"]
    assert req["questions"] == {cid: {"type": "noul", "instructions": "Does this chunk answer, match or explain the query?"}
                                for cid in ("k0", "k1", "k2")}


def test_jev_is_asked_in_batches_of_8_and_every_sent_chunk_is_scored(double):
    d = double(_by_index)
    scores, reason, sent = jc.jev_rank("q", _chunks(20), url=d.url, timeout=5, log=False)
    assert reason is None and len(sent) == 20 and set(scores) == {c["id"] for c in sent}
    assert [len(r["state"]["chunks"]) for r in d.requests] == [8, 8, 4]
    assert sorted(c["id"] for r in d.requests for c in r["state"]["chunks"]) == sorted(c["id"] for c in sent)


def test_a_failed_batch_fails_the_whole_ranking(double):
    def scorer(q, t):
        if t.startswith("f05.py"):          # the chunk with lexical 5 sits in the second batch of 8
            raise ValueError("model error")
        return 0.5
    d = double(scorer)
    scores, reason, sent = jc.jev_rank("q", _chunks(20), url=d.url, timeout=5, log=False)
    assert scores is None and reason.startswith("call 2 of 3: url: HTTP 500")


def test_all_equal_scores_are_no_ranking(double):
    """VERIFY-JT1 F-24: every chunk cut out of the window scores the same, with fan_out intact. Such a ranking is
    refused (the pack falls back to its base order with the reason); one chunk alone is not judged."""
    d = double(lambda q, t: 0.4958)
    scores, reason, sent = jc.jev_rank("q", _chunks(3), url=d.url, timeout=5, log=False)
    assert scores is None and len(sent) == 3
    assert reason == "all 3 scores are equal (0.4958): no signal (a query over the window cuts every chunk)"
    scores, reason, sent = jc.jev_rank("q", _chunks(1), url=d.url, timeout=5, log=False)
    assert scores == {"k0": 0.4958} and reason is None
    d2 = double(_by_index)                      # negative control: a spread of scores is a ranking
    scores, reason, sent = jc.jev_rank("q", _chunks(3), url=d2.url, timeout=5, log=False)
    assert reason is None and {k: round(v, 6) for k, v in scores.items()} == {"k0": 0.1, "k1": 0.11, "k2": 0.12}


def test_the_query_bound_leaves_room_for_a_chunk():
    """The measured budget behind JEV_QUERY_CHARS (the lane report, section 10: the model's own tokenizer and
    build_sequence): 1,200 characters of the densest real query text plus the longest real chunk took 668 of 986
    tokens; a trace-like query cut the chunk only at about 2,400. Pin the bound and the chunk cap it was measured with."""
    assert jc.JEV_QUERY_CHARS == 1200 and jc.TEXT_CAP == 400


def test_jev_down_is_a_reason_not_an_exception():
    scores, reason, sent = jc.jev_rank("q", _chunks(2), url=closed_port_url(), timeout=5, log=False)
    assert scores is None and reason == "call 1 of 1: url: connection refused"


def test_the_pure_jev_order_follows_the_scores(double):
    """Mutant 1's target: the D-3 order (A3's `jev` column) must follow Jev's scores, not the unranked order."""
    ch = _chunks(5)
    d = double(lambda q, t: 1.0 - int(t.split("chunk ")[1]) / 10.0)     # the reverse of the lexical order
    scores, reason, _ = jc.jev_rank("q", ch, url=d.url, timeout=5, log=False)
    assert [c["id"] for c in jc.order_unranked(ch)] == ["k4", "k3", "k2", "k1", "k0"]
    assert [c["id"] for c in jc.order_ranked(ch, scores)] == ["k0", "k1", "k2", "k3", "k4"]
    ranked = [f["path"] for f in jc.files_to_read(jc.order_ranked(ch, scores), "jev", scores)]
    assert ranked == ["f00.py", "f01.py", "f02.py", "f03.py", "f04.py"]


def test_jev_reorders_the_base_selection_and_never_drops_an_item():
    """KC-J5 (the coordinator's rule 3): with Jev's highest scores on chunks OUTSIDE the base order's top k, every fit
    level shows exactly the base's top-k set, reordered by score."""
    ch = _chunks(20)
    scores = {c["id"]: (0.99 if c["lexical"] < 10 else c["lexical"] / 100.0) for c in ch}
    pack = jc.build_pack("t", [("question", "q")], ch, "unranked", scores, "ranking", [], [])
    base_top = [c["id"] for c in jc.order_unranked(ch)[:5]]
    assert base_top == ["k19", "k18", "k17", "k16", "k15"]
    pure_top = [c["id"] for c in jc.order_ranked(ch, scores)[:5]]
    assert set(pure_top).isdisjoint(base_top)       # de-vacuoused: the pure order WOULD drop the whole base top 5
    items, files = jc.select(pack, 5, 5)
    assert [c["id"] for c in items] == ["k19", "k18", "k17", "k16", "k15"]          # same set; scores agree here
    for k in range(1, 13):
        items, files = jc.select(pack, k, k)
        assert {c["id"] for c in items} == {c["id"] for c in jc.order_unranked(ch)[:k]}
        assert {f["path"] for f in files} == {f["path"] for f in pack["files"][:k]}


def test_the_reorder_inside_the_selection_follows_the_scores():
    ch = _chunks(6)
    scores = {"k5": 0.1, "k4": 0.9, "k3": 0.5}         # k2, k1, k0 unscored
    pack = jc.build_pack("t", [("question", "q")], ch, "unranked", scores, "ranking", [], [])
    items, files = jc.select(pack, 4, 4)
    assert [c["id"] for c in items] == ["k4", "k3", "k5", "k2"]     # scored by score, then the unscored in base order
    assert [f["path"] for f in files] == ["f04.py", "f03.py", "f05.py", "f02.py"]


def test_the_default_order_is_lexical_and_jev_reorders_lexical():
    """D-077 (the coordinator): Jev is opt-in; the default and the base Jev reorders are both the lexical order."""
    assert (jc.DEFAULT_ORDER, jc.JEV_BASE) == ("lexical", "lexical")
    assert jc.ORDERS == ("unranked", "lexical", "jev")


def test_lexical_order_ignores_agreement():
    ch = _chunks(3)
    ch[0]["agreement"] = 5
    assert [c["id"] for c in jc.order_base(ch, "lexical")] == ["k2", "k1", "k0"]
    assert [c["id"] for c in jc.order_base(ch, "unranked")] == ["k0", "k2", "k1"]


# ---------- D-4 budget and determinism ----------

def _huge_pack(scored):
    rnd = random.Random(7)
    # spaced words, not one long run: the scrubber would collapse a 40+ character run to `<opaque-redacted>`
    text = " ".join("word%d" % j for j in range(70))[:400]
    hits = [H(rnd.choice(["rg", "graft", "cbm"]), "scripts/%s/%s.py" % ("d" * 80, i % 700), rnd.randint(1, 900),
              text) for i in range(5000)]
    hits += [H("registry", "docs/INCIDENT-LOG.md", i, text) for i in range(8)]
    chunks = jc.merge(hits, set())
    scores = {c["id"]: 0.5 for c in chunks[:48]} if scored else None
    notes = ["unmapped — tool%d unavailable (%s)" % (i, "e" * 300) for i in range(12)]
    return jc.build_pack("jev locate", [("question", "Q" * 4000)], chunks, "unranked", scores, "r" * 900,
                         ["rg"], notes, extra=["x" * 900])


@pytest.mark.parametrize("scored", [False, True])
def test_a_pack_never_exceeds_its_budget_or_the_hard_cap(scored):
    """A5 (and mutant 3's target): oversized instrument output never yields a pack over its budget, in markdown or
    JSON, and a requested budget over 9,000 is clamped to 9,000."""
    pack = _huge_pack(scored)
    budget, note = jc.clamp_budget(50000)
    assert (budget, note) == (9000, "budget clamped to the 9000-character hard cap")
    for b in (jc.BUDGET_MIN, 1500, 3000, jc.BUDGET_DEFAULT, budget):
        md = jc.render(pack, 12, b)
        js = jc.render(pack, 12, b, as_json=True)
        assert len(md) <= b and len(js) <= b
        json.loads(js)
    assert len(jc._md(pack, 240, 48, 10)) > 9000       # de-vacuoused: the uncut first layout is over the hard cap


def test_a_pack_is_deterministic_for_the_same_hits_in_any_order():
    hits = [H("rg", "a.py", 10, "x"), H("graft", "a.py", 12, "y"), H("cbm", "b.py", 3, "z"),
            H("registry", "docs/INCIDENT-LOG.md", 5, "row"), H("git-log", "git:abc1234", 0, "abc1234 fix")]
    outs = set()
    for seed in range(5):
        h = list(hits)
        random.Random(seed).shuffle(h)
        chunks = jc.merge(h, jc.words("x y z row fix"))
        pack = jc.build_pack("t", [("question", "q")], chunks, "unranked", None, "r", ["rg"], [])
        outs.add(jc.render(pack, 12, 6000) + jc.render(pack, 12, 6000, as_json=True))
    assert len(outs) == 1


def test_displayed_text_is_scrubbed():
    fake = "sk-3c3d5f1e8a2b4c6d9e0f1234567890ab"
    chunks = jc.merge([H("rg", "a.py", 1, "key = %s" % fake)], set())
    pack = jc.build_pack("t", [("question", "why does token=%s fail" % ("Q" * 44))], chunks, "unranked", None, "r",
                         [], ["unmapped — x unavailable (%s)" % fake])
    out = jc.render(pack, 12, 6000) + jc.render(pack, 12, 6000, as_json=True)
    assert fake not in out and "Q" * 44 not in out
    assert "sk-<redacted>" in out


# ---------- run_tool ----------

def test_run_tool_names_a_missing_tool():
    assert jc.run_tool(["/nonexistent/dir/graft"], "/", 5) == (None, "", "not found: graft")


def test_run_tool_reports_the_error_line_of_a_failing_tool(tmp_path):
    script = tmp_path / "t.py"
    script.write_text("import sys\nprint('file:///x.js:1', file=sys.stderr)\n"
                      "print('    throw new Error(`boom ${x}`)', file=sys.stderr)\n"
                      "print('Error: LadybugDB unavailable for /r', file=sys.stderr)\nsys.exit(1)\n")
    rc, out, reason = jc.run_tool([sys.executable, str(script)], str(tmp_path), 10)
    assert rc == 1 and reason == "rc 1: Error: LadybugDB unavailable for /r"


def _proc_state(pid):
    """One read (AF-AP-181's fixed form): the state letter, or "gone"."""
    try:
        with open("/proc/%d/stat" % pid) as fh:
            return fh.read().rsplit(")", 1)[1].split()[0]
    except (OSError, IndexError):
        return "gone"


def test_run_tool_timeout_kills_the_whole_process_group(tmp_path):
    pidfile = tmp_path / "gc.pid"
    script = tmp_path / "t.py"
    script.write_text("import subprocess, sys, time\n"
                      "p = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)'])\n"
                      "open(%r, 'w').write(str(p.pid))\ntime.sleep(60)\n" % str(pidfile))
    t0 = time.monotonic()
    rc, out, reason = jc.run_tool([sys.executable, str(script)], str(tmp_path), 2)
    assert rc is None and reason == "timeout after 2s" and time.monotonic() - t0 < 10
    gc = int(pidfile.read_text())
    deadline = time.monotonic() + 5
    while _proc_state(gc) not in ("Z", "gone") and time.monotonic() < deadline:
        time.sleep(0.1)
    assert _proc_state(gc) in ("Z", "gone")          # the grandchild died with the group


def test_an_instrument_exception_is_one_unmapped_line():
    def boom(question, toks, ctx):
        raise KeyError("x")
    ctx = jc.Context("/", {})
    hits, notes, answered = jc.collect("q", ctx, ("rg",), fns={"rg": boom})
    assert hits == [] and answered == []
    assert notes[0] == "unmapped — rg unavailable (internal error: KeyError)"
    assert "not run — graft: not selected (--instruments)" in notes


# ---------- the in-process instruments ----------

def test_registry_and_quirks_take_the_lexical_top_rows(tmp_path):
    (tmp_path / "docs").mkdir()
    rows = ["| AF-AP-%d | %s | sig | inst | OPEN |" % (i, "alpha beta" if i == 3 else "gamma") for i in range(1, 12)]
    (tmp_path / "docs" / "INCIDENT-LOG.md").write_text("# log\n\n" + "\n".join(rows) + "\n")
    (tmp_path / "CLAUDE.md").write_text("intro\n**alpha thing (bit 2026-09-01).** other\n**zeta (bit 2026-09-02)**\n")
    ctx = jc.Context(str(tmp_path), {})
    hits, notes, ok = jc.inst_registry("alpha beta AF-AP-7", [], ctx)
    assert ok and [h["line"] for h in hits] == [9, 5]        # AF-AP-7 named (bonus), then the lexical match AF-AP-3
    hits, notes, ok = jc.inst_quirks("alpha", [], ctx)
    assert ok and [(h["line"], h["text"]) for h in hits] == [(2, "alpha thing (bit 2026-09-01).** other")]


def test_absent_records_are_unmapped(tmp_path):
    ctx = jc.Context(str(tmp_path), {})
    assert jc.inst_registry("q", [], ctx) == ([], ["unmapped — registry unavailable (docs/INCIDENT-LOG.md absent)"], False)
    assert jc.inst_quirks("q", [], ctx) == ([], ["unmapped — quirks unavailable (CLAUDE.md absent)"], False)
