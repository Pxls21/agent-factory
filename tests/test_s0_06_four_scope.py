"""S0-06 — the four-scope adapter, its checker, and the two committed hostile bundles.

Deterministic and LLM-free. Every network interaction is against a recording `http.server` this
module starts on 127.0.0.1 and shuts down in a finally; nothing here reaches the PC, ai-memory, or
any other host. The recording server proves what the adapter SENDS (route, workspace, project,
bearer header, request body) — it is NOT proof evidence: `check_four_scope.check_substrate`
refuses any bundle whose `substrate.json` is not the pinned ai-memory, so a bundle recorded here
can never mint an artifact.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import os
import shutil
import socket
import stat
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import jsonschema
import pytest

REPO = Path(__file__).resolve().parents[1]
PROOF = REPO / "proofs" / "S0-06"
ADAPTER_PATH = PROOF / "adapter" / "factory_memory.py"
CHECKER_PATH = PROOF / "check_four_scope.py"
NEG_FIXTURE = REPO / "fixtures" / "s0-06" / "neg-unauthorized-tuple.json"

# The REAL ai-memory serialisations this proof's fixtures must match (AF-AP-42).
# ApiSearchHit  — crates/ai-memory-web/src/routes/api.rs:1254-1263 (built by enrich_hits :1009-1030)
SEARCH_HIT_KEYS = {"workspace", "project", "path", "title", "kind", "snippet", "rank"}
# PageSummary   — crates/ai-memory-store/src/reader.rs:1174-1185
PAGE_SUMMARY_KEYS = {"path", "title", "kind", "tier", "updated_at"}

AUTHORIZED_TUPLE = {"actor": "svc-agent-runner", "agent": "a-alpha",
                    "team": "t-core", "project": "p-atlas"}
LEAK_TUPLE = {"actor": "svc-agent-runner", "agent": "a-beta",
              "team": "t-core", "project": "p-atlas"}
TUPLE_DENIED = "denied: scope-tuple-unauthorized"
WRITE_DENIED = "denied: write-scope-not-active"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


fm = _load("s0_06_factory_memory", ADAPTER_PATH)
checker = _load("s0_06_check_four_scope", CHECKER_PATH)


# --------------------------------------------------------------------------- helpers

def _hit(scope, project, path, title, snippet, rank):
    return {"workspace": "factory", "project": project, "path": path, "title": title,
            "kind": "decision", "snippet": snippet, "rank": rank}


def _closed_port():
    """A port nothing is listening on: bind it, read it, release it."""
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    port = s.getsockname()[1]
    s.close()
    return port


class _Recorder(BaseHTTPRequestHandler):
    """Answers with REAL ai-memory response shapes and records every request."""

    protocol_version = "HTTP/1.1"

    def log_message(self, *_args):
        pass

    def _send(self, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        self.server.calls.append({"method": "GET", "path": parsed.path,
                                  "query": parse_qs(parsed.query),
                                  "auth": self.headers.get("Authorization"), "body": None})
        if parsed.path == "/api/v1/search":
            project = parse_qs(parsed.query)["project"][0]
            self._send([_hit("x", project, "notes/deploy-window.md",
                             f"Deploy window ({project})", f"body for {project}", -1.2)])
        elif parsed.path.endswith("/pages"):
            self._send([{"path": "notes/deploy-window.md", "title": "Deploy window",
                         "kind": "fact", "tier": "semantic",
                         "updated_at": "2026-09-05T09:14:02Z"}] + self.server.extra_pages)
        else:
            self._send([])

    def do_POST(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        parsed = urlparse(self.path)
        self.server.calls.append({"method": "POST", "path": parsed.path, "query": {},
                                  "auth": self.headers.get("Authorization"),
                                  "body": json.loads(raw)})
        self._send({"page_id": "3f8d1c66-9a2e-4b70-8d51-0c7a4e12b9f3",
                    "path": json.loads(raw)["path"]})


class _Server:
    def __init__(self, extra_pages=()):
        self.httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Recorder)
        self.httpd.calls = []
        self.httpd.extra_pages = list(extra_pages)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()

    @property
    def base_url(self):
        return "http://127.0.0.1:%d" % self.httpd.server_address[1]

    @property
    def calls(self):
        return self.httpd.calls

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(timeout=5)


@pytest.fixture
def server():
    srv = _Server()
    try:
        yield srv
    finally:
        srv.close()


def _repair_wrong_scope(dest: Path) -> Path:
    """A PASSING bundle built from the committed wrong-scope bundle by removing its ONE plant."""
    shutil.copytree(PROOF / "fixtures" / "evidence-wrong-scope-write", dest)
    page_path = json.loads((dest / "write-scope" / "write.json").read_text())["page_path"]
    raw = dest / "write-scope" / "raw-project.json"
    kept = [e for e in json.loads(raw.read_text()) if e["path"] != page_path]
    raw.write_text(json.dumps(kept, indent=2, sort_keys=True) + "\n")
    return dest


def _repair_leak(dest: Path) -> Path:
    """A PASSING bundle built from the committed leak bundle by removing its ONE plant."""
    shutil.copytree(PROOF / "fixtures" / "evidence-leak", dest)
    tokens = json.loads((dest / "leak" / "honeytokens.json").read_text())
    path = dest / "leak" / "recall.json"
    doc = json.loads(path.read_text())
    doc["records"] = [r for r in doc["records"]
                      if tokens["team"] not in json.dumps(r, sort_keys=True)]
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    return dest


@pytest.fixture
def good(tmp_path):
    return _repair_wrong_scope(tmp_path / "good")


def _run_checker(root):
    return subprocess.run([sys.executable, str(CHECKER_PATH), str(root)],
                          capture_output=True, text=True, timeout=120)


def _verdict(root):
    proc = _run_checker(root)
    return proc.returncode, proc.stdout.strip().splitlines()[-1]


def _edit(path: Path, fn):
    doc = json.loads(path.read_text())
    fn(doc)
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")


def _edit_recalls(root: Path, fn):
    """precedence/recall-1 and -2 must stay byte-identical, so mutate both."""
    for name in ("recall-1.json", "recall-2.json"):
        _edit(root / "precedence" / name, fn)


# --------------------------------------------------------------------------- tuple validation

def test_authorized_tuples_are_accepted():
    table = fm.load_bindings()
    for row in table:
        presented = {f: row[f] for f in fm.TUPLE_FIELDS}
        assert fm.authorize(presented, table) is row


@pytest.mark.parametrize("field", fm.TUPLE_FIELDS)
def test_every_single_field_corruption_is_denied(field):
    """One field wrong is the whole attack: a real-looking tuple with a borrowed value."""
    table = fm.load_bindings()
    borrowed = {"actor": "svc-eval-runner", "agent": "a-gamma",
                "team": "t-platform", "project": "p-borealis"}
    corrupted = dict(AUTHORIZED_TUPLE, **{field: borrowed[field]})
    assert corrupted != AUTHORIZED_TUPLE
    assert fm.authorize(corrupted, table) is None
    adapter = fm.FactoryMemory(base_url="http://127.0.0.1:1")
    assert adapter.recall(corrupted, "q")["reason"] == TUPLE_DENIED


@pytest.mark.parametrize("presented", [
    {f: AUTHORIZED_TUPLE[f] for f in ("actor", "agent", "team")},                 # missing field
    dict(AUTHORIZED_TUPLE, scopes=["agent", "project", "team", "company"]),       # extra field
    dict(AUTHORIZED_TUPLE, agent=""),                                             # empty value
    "not-a-mapping",
])
def test_shape_violations_are_denied(presented):
    assert fm.authorize(presented, fm.load_bindings()) is None


def test_the_committed_table_is_the_only_authorization_source():
    """A tuple the caller declares authorized, absent from the table, is still denied."""
    invented = {"actor": "svc-agent-runner", "agent": "a-omega",
                "team": "t-core", "project": "p-atlas"}
    assert fm.authorize(invented, fm.load_bindings()) is None
    forged_table = [dict(invented, scopes=list(fm.SCOPE_ORDER))]
    assert fm.authorize(invented, forged_table) is not None      # the table decides, nothing else
    adapter = fm.FactoryMemory(base_url="http://127.0.0.1:1")
    assert adapter.recall(invented, "q")["status"] == "denied"


def test_a_malformed_table_row_can_never_authorize_a_null_tuple():
    """Class-18 regression: `row.get(f)` returns None for a field a row omits, so a presented
    tuple carrying JSON `null` for that field would have matched a malformed row."""
    broken = [{"actor": "svc-agent-runner", "agent": "a-alpha", "team": "t-core"}]  # no project
    null_tuple = {"actor": "svc-agent-runner", "agent": "a-alpha",
                  "team": "t-core", "project": None}
    assert fm.authorize(null_tuple, broken) is None
    assert fm.authorize({f: None for f in fm.TUPLE_FIELDS}, [{}]) is None
    assert fm.authorize(dict(AUTHORIZED_TUPLE, project=""), [dict(AUTHORIZED_TUPLE, project="")]) is None
    # positive control on the same code path: a well-formed row still authorizes
    assert fm.authorize(AUTHORIZED_TUPLE, [dict(AUTHORIZED_TUPLE, scopes=["agent"])]) is not None


def test_cli_has_no_bindings_override_flag():
    """The authorization table is not caller-selectable: no CLI path can point elsewhere."""
    proc = subprocess.run(
        [sys.executable, str(ADAPTER_PATH), "recall", "--tuple-file", str(NEG_FIXTURE),
         "--query", "x", "--bindings", "/tmp/forged.json"],
        capture_output=True, text=True, timeout=60)
    assert proc.returncode == 2
    assert "unrecognized arguments" in proc.stderr


def test_seed_negative_fixture_is_a_real_looking_tuple_with_one_wrong_field():
    fixture = json.loads(NEG_FIXTURE.read_text())
    assert set(fixture) == set(fm.TUPLE_FIELDS)
    table = fm.load_bindings()
    assert fm.authorize(fixture, table) is None
    # the agent, the actor and the project are all real; only the team is not bound to this agent
    assert any(r["agent"] == fixture["agent"] for r in table)
    assert any(r["team"] == fixture["team"] for r in table)
    assert not any(r["agent"] == fixture["agent"] and r["team"] == fixture["team"] for r in table)


# --------------------------------------------------------------------------- scope mapping

def test_scopes_for_is_the_docs_03_mapping():
    binding = fm.Binding(**AUTHORIZED_TUPLE)
    assert fm.scopes_for(binding) == {
        "agent": ("factory", "agent--a-alpha"),
        "project": ("factory", "project--p-atlas"),
        "team": ("factory", "team--t-core"),
        "company": ("factory", "_global"),
    }


# --------------------------------------------------------------------------- merge

def _four_way(scope, rank):
    hit = _hit(scope, f"p-{scope}", "notes/deploy-window.md",
               f"Deploy window ({scope})", f"body for {scope}", rank)
    return fm.normalize_hit(hit, scope, f"2026-09-0{fm.SCOPE_ORDER.index(scope) + 1}T00:00:00Z")


def _collision_input():
    return {scope: [_four_way(scope, -1.0 - i * 0.1),
                    fm.normalize_hit(_hit(scope, f"p-{scope}", f"notes/{scope}-only.md",
                                          scope, scope, -0.5), scope, "2026-09-01T00:00:00Z")]
            for i, scope in enumerate(fm.SCOPE_ORDER)}


def test_merge_is_byte_identical_on_a_repeat_call():
    data = _collision_input()
    once = json.dumps(fm.merge(data), sort_keys=True)
    twice = json.dumps(fm.merge(data), sort_keys=True)
    assert once == twice


def test_merge_is_independent_of_input_order():
    data = _collision_input()
    shuffled = {}
    for scope in reversed(fm.SCOPE_ORDER):                 # scope insertion order reversed
        shuffled[scope] = list(reversed(data[scope]))      # record order reversed
    assert list(shuffled) != list(data)
    assert json.dumps(fm.merge(shuffled), sort_keys=True) == json.dumps(fm.merge(data), sort_keys=True)


def test_merge_resolves_a_four_way_collision_to_the_agent_record():
    merged = fm.merge(_collision_input())
    winner = [r for r in merged if r["stable_id"] == "notes/deploy-window.md"]
    assert len(winner) == 1
    assert winner[0]["scope"] == "agent"
    assert winner[0]["provenance"]["title"] == "Deploy window (agent)"
    assert winner[0]["provenance"]["shadowed_scopes"] == ["project", "team", "company"]


def test_merge_output_is_sorted_by_precedence_then_stable_id():
    merged = fm.merge(_collision_input())
    keys = [(fm.SCOPE_ORDER.index(r["scope"]), r["stable_id"]) for r in merged]
    assert keys == sorted(keys)


def test_merge_does_not_mutate_its_input():
    data = _collision_input()
    before = copy.deepcopy(data)
    fm.merge(data)
    assert data == before


def test_merge_carries_the_docs_03_read_contract_fields():
    for record in fm.merge(_collision_input()):
        assert set(record) == {"scope", "stable_id", "timestamp", "confidence", "provenance"}


def test_a_lower_precedence_only_record_survives_the_merge():
    """De-duplication must not swallow records that exist in one scope alone."""
    ids = {r["stable_id"] for r in fm.merge(_collision_input())}
    assert ids == {"notes/deploy-window.md", "notes/agent-only.md", "notes/project-only.md",
                   "notes/team-only.md", "notes/company-only.md"}


# --------------------------------------------------------------------------- adapter surface

def test_public_adapter_surface_is_recall_and_write_only():
    public = [n for n in dir(fm.FactoryMemory) if not n.startswith("_")]
    assert sorted(public) == ["recall", "write"]


def test_no_module_level_mutation_entry_point_exists():
    banned = ("delete", "purge", "promote", "approve", "forget", "reset")
    offenders = [n for n in dir(fm) if not n.startswith("_")
                 and any(word in n.lower() for word in banned)]
    assert offenders == []
    # positive control on the matcher itself: it DOES fire on a name of the banned shape
    assert [n for n in ["delete_page", "recall"] if any(w in n.lower() for w in banned)] == \
           ["delete_page"]
    source = ADAPTER_PATH.read_text()
    for route in ("/admin/delete-page", "/admin/purge-project", "/admin/purge-session",
                  "/admin/auto-improve", "/admin/forget-sweep"):
        assert route not in source
    # positive control on the scan: the ONE admin route the adapter does use IS found
    assert "/admin/write-page" in source


# --------------------------------------------------------------------------- write scope

@pytest.mark.parametrize("scope", ["team", "company", "", "AGENT", "agent--a-alpha", None])
def test_write_refuses_a_scope_the_binding_does_not_authorize(scope, server):
    """a-beta is bound to agent+project only, so team and company are refused, as is any
    non-scope string. Nothing reaches the substrate."""
    adapter = fm.FactoryMemory(base_url=server.base_url, token="t")
    result = adapter.write(LEAK_TUPLE, scope, {"session": "s", "turn": "1",
                                               "event_id": "e", "body": "b"})
    assert result == {"status": "denied", "reason": WRITE_DENIED}
    assert server.calls == []


def test_a_company_write_is_refused_even_when_the_table_authorizes_it(server):
    """docs/03 §4 write contract (`docs/03_INTEGRATION_CONTRACTS.md:96`): `_global` writes and all
    upward promotion require a reviewed companion workflow. None exists, so Company is read-only
    through this adapter even for a-alpha, whose row grants all four scopes."""
    assert "company" in fm.load_bindings()[0]["scopes"]
    adapter = fm.FactoryMemory(base_url=server.base_url, token="t")
    result = adapter.write(AUTHORIZED_TUPLE, "company",
                           {"session": "s", "turn": "1", "event_id": "e", "body": "b"})
    assert result == {"status": "denied", "reason": "denied: write-scope-requires-review"}
    assert server.calls == []
    # positive control on the same binding and the same server: an agent write DOES land
    assert adapter.write(AUTHORIZED_TUPLE, "agent",
                         {"session": "s", "turn": "1", "event_id": "e",
                          "body": "b"})["status"] == "ok"
    assert [c["path"] for c in server.calls if c["method"] == "POST"] == ["/admin/write-page"]


def test_write_lands_in_the_active_scope_only(server):
    adapter = fm.FactoryMemory(base_url=server.base_url, token="secret-token")
    record = {"session": "sess-7f2a", "turn": "12", "event_id": "evt-0003", "body": "# x\n"}
    result = adapter.write(AUTHORIZED_TUPLE, "agent", record)
    assert result["status"] == "ok"
    assert result["reason"] == "write: page written"
    posts = [c for c in server.calls if c["method"] == "POST"]
    assert len(posts) == 1
    assert posts[0]["path"] == "/admin/write-page"
    assert posts[0]["body"]["workspace"] == "factory"
    assert posts[0]["body"]["project"] == "agent--a-alpha"
    assert posts[0]["body"]["path"] == fm.idempotency_path("sess-7f2a", "12", "evt-0003")
    assert set(posts[0]["body"]) == {"workspace", "project", "path", "body", "kind", "tier",
                                     "tags", "pinned"}


def test_a_retry_with_the_same_key_is_a_recorded_no_op():
    record = {"session": "sess-7f2a", "turn": "12", "event_id": "evt-0003", "body": "# x\n"}
    page_path = fm.idempotency_path(**{k: record[k] for k in ("session", "turn", "event_id")})
    srv = _Server(extra_pages=[{"path": page_path, "title": "Retention decision", "kind": "fact",
                                "tier": "semantic", "updated_at": "2026-09-05T09:20:44Z"}])
    try:
        adapter = fm.FactoryMemory(base_url=srv.base_url, token="t")
        result = adapter.write(AUTHORIZED_TUPLE, "agent", record)
        assert result["status"] == "ok"
        assert result["reason"] == "write: idempotent no-op"
        assert result["page_path"] == page_path
        assert [c for c in srv.calls if c["method"] == "POST"] == []
    finally:
        srv.close()


def test_the_idempotency_key_covers_every_component():
    base = ("sess-7f2a", "12", "evt-0003")
    paths = {fm.idempotency_path(*base)}
    for i in range(3):
        other = list(base)
        other[i] = other[i] + "x"
        paths.add(fm.idempotency_path(*other))
    assert len(paths) == 4                       # the key discriminates on all three components
    assert fm.idempotency_path(*base) == fm.idempotency_path(*base)
    assert fm.idempotency_path(*base).startswith("observations/")
    assert not fm.idempotency_path(*base).startswith("/")
    assert ".." not in fm.idempotency_path(*base)


@pytest.mark.parametrize("missing", ["session", "turn", "event_id", "body"])
def test_an_incomplete_record_is_refused_before_the_write(missing, server):
    record = {"session": "s", "turn": "1", "event_id": "e", "body": "b"}
    del record[missing]
    adapter = fm.FactoryMemory(base_url=server.base_url, token="t")
    result = adapter.write(AUTHORIZED_TUPLE, "agent", record)
    assert result["reason"] == "denied: write-record-incomplete"
    assert [c for c in server.calls if c["method"] == "POST"] == []


# --------------------------------------------------------------------------- what the adapter sends

def test_recall_queries_every_authorized_scope_on_the_read_route(server):
    adapter = fm.FactoryMemory(base_url=server.base_url, token="secret-token")
    result = adapter.recall(AUTHORIZED_TUPLE, "deploy window")
    assert result["status"] == "ok"
    searches = [c for c in server.calls if c["path"] == "/api/v1/search"]
    assert [c["query"]["project"][0] for c in searches] == [
        "agent--a-alpha", "project--p-atlas", "team--t-core", "_global"]
    assert {c["query"]["workspace"][0] for c in searches} == {"factory"}
    assert {c["query"]["q"][0] for c in searches} == {"deploy window"}
    listings = [c["path"] for c in server.calls if c["path"].endswith("/pages")]
    assert listings == [
        "/api/v1/workspaces/factory/projects/agent--a-alpha/pages",
        "/api/v1/workspaces/factory/projects/project--p-atlas/pages",
        "/api/v1/workspaces/factory/projects/team--t-core/pages",
        "/api/v1/workspaces/factory/projects/_global/pages",
    ]


def test_a_partly_authorized_binding_never_touches_the_other_scopes(server):
    adapter = fm.FactoryMemory(base_url=server.base_url, token="t")
    result = adapter.recall(LEAK_TUPLE, "honeytoken")
    assert [s["scope"] for s in result["scopes_queried"]] == ["agent", "project"]
    projects = {c["query"]["project"][0] for c in server.calls if c["path"] == "/api/v1/search"}
    assert projects == {"agent--a-beta", "project--p-atlas"}
    assert "team--t-core" not in json.dumps(server.calls)
    assert "_global" not in json.dumps(server.calls)


def test_the_recording_server_answers_with_the_real_ai_memory_shapes(server):
    """The test double is pinned to the producer's serialisation, so a fixture that drifts from
    ai-memory's real response cannot pass here (AF-AP-42)."""
    adapter = fm.FactoryMemory(base_url=server.base_url, token="t")
    adapter.recall(AUTHORIZED_TUPLE, "q")
    import urllib.request
    with urllib.request.urlopen(
            server.base_url + "/api/v1/search?q=x&workspace=factory&project=agent--a-alpha",
            timeout=10) as resp:
        hits = json.loads(resp.read().decode())
    assert hits and all(set(h) == SEARCH_HIT_KEYS for h in hits)
    with urllib.request.urlopen(
            server.base_url + "/api/v1/workspaces/factory/projects/agent--a-alpha/pages",
            timeout=10) as resp:
        pages = json.loads(resp.read().decode())
    assert pages and all(set(p) == PAGE_SUMMARY_KEYS for p in pages)


def test_the_record_timestamp_comes_from_the_page_listing(server):
    """docs/03 §4 read contract 4 wants a timestamp; the search hit has none (ApiSearchHit has 7
    fields and no date), so the adapter joins the project's page listing for it."""
    adapter = fm.FactoryMemory(base_url=server.base_url, token="t")
    result = adapter.recall(AUTHORIZED_TUPLE, "q")
    winner = [r for r in result["records"] if r["stable_id"] == "notes/deploy-window.md"]
    assert len(winner) == 1
    assert winner[0]["timestamp"] == "2026-09-05T09:14:02Z"
    assert winner[0]["confidence"] == -1.2
    assert winner[0]["scope"] == "agent"
    assert winner[0]["provenance"]["shadowed_scopes"] == ["project", "team", "company"]


def test_every_request_carries_the_bearer_token(server):
    adapter = fm.FactoryMemory(base_url=server.base_url, token="secret-token")
    adapter.recall(AUTHORIZED_TUPLE, "q")
    adapter.write(AUTHORIZED_TUPLE, "agent", {"session": "s", "turn": "1",
                                              "event_id": "e", "body": "b"})
    assert server.calls
    assert {c["auth"] for c in server.calls} == {"Bearer secret-token"}


def test_a_failing_scope_degrades_visibly_and_names_the_scope(server, tmp_path):
    """docs/04 §4: a read outage is a NAMED degraded status, never a silent partial."""
    adapter = fm.FactoryMemory(base_url=server.base_url, token="t")
    dead = fm.FactoryMemory(base_url="http://127.0.0.1:%d" % _closed_port(), token="t",
                            timeout_s=2)
    assert adapter.recall(AUTHORIZED_TUPLE, "q")["status"] == "ok"
    degraded = dead.recall(AUTHORIZED_TUPLE, "q")
    assert degraded["status"] == "degraded"
    assert degraded["degraded_scopes"] == ["agent", "company", "project", "team"]
    assert degraded["reason"].startswith("recall: degraded: ")
    assert degraded["records"] == []


def test_the_token_never_reaches_the_event_stream(tmp_path, server):
    events = tmp_path / "events.jsonl"
    with open(events, "w", encoding="utf-8") as handle:
        adapter = fm.FactoryMemory(base_url=server.base_url, token="s3cr3t-value",
                                   events=handle)
        adapter.recall(AUTHORIZED_TUPLE, "q")
    text = events.read_text()
    # positive control: the stream really did record this run's requests, so the token's absence
    # is a fact about the token and not about an empty file
    assert "agent--a-alpha" in text
    assert '"http_request"' in text
    assert "s3cr3t-value" not in text
    for line in text.splitlines():
        assert "event" in json.loads(line)


def test_the_adapter_uses_no_clock_and_no_randomness():
    source = ADAPTER_PATH.read_text()
    for token in ("import time", "import random", "datetime", "time.time", "uuid"):
        assert token not in source


# --------------------------------------------------------------------------- offline negative control

def test_the_negative_control_denies_without_a_network_call(tmp_path):
    """The seed's negative fixture against a CLOSED port: the denial arrives first, in bounded
    time, and the event stream carries no request."""
    events = tmp_path / "events.jsonl"
    port = _closed_port()
    started = time.monotonic()
    proc = subprocess.run(
        [sys.executable, str(ADAPTER_PATH), "recall", "--tuple-file", str(NEG_FIXTURE),
         "--query", "x", "--base-url", "http://127.0.0.1:%d" % port,
         "--events", str(events)],
        capture_output=True, text=True, timeout=30)
    elapsed = time.monotonic() - started
    assert proc.returncode == 1
    assert proc.stdout.splitlines()[-1] == TUPLE_DENIED
    assert elapsed < 10
    events_seen = [json.loads(line) for line in events.read_text().splitlines()]
    assert [e["event"] for e in events_seen] == ["scope_tuple_denied"]
    assert "http_request" not in events.read_text()


def test_the_cli_denial_line_is_exactly_the_seed_reason():
    proc = subprocess.run(
        [sys.executable, str(ADAPTER_PATH), "recall", "--tuple-file", str(NEG_FIXTURE),
         "--query", "x"],
        capture_output=True, text=True, timeout=30, cwd=str(REPO))
    assert proc.returncode == 1
    assert proc.stdout == TUPLE_DENIED + "\n"


# --------------------------------------------------------------------------- fixture shapes

@pytest.mark.parametrize("bundle", ["evidence-leak", "evidence-wrong-scope-write"])
def test_committed_bundles_carry_the_real_ai_memory_record_shapes(bundle):
    root = PROOF / "fixtures" / bundle
    for leg in ("precedence", "leak"):
        for scope in fm.SCOPE_ORDER:
            for entry in json.loads((root / leg / f"raw-{scope}.json").read_text()):
                assert set(entry) == SEARCH_HIT_KEYS
                assert isinstance(entry["rank"], float)
    for scope in fm.SCOPE_ORDER:
        for entry in json.loads((root / "write-scope" / f"raw-{scope}.json").read_text()):
            assert set(entry) == PAGE_SUMMARY_KEYS
    assert (root / "PROVENANCE.md").is_file()


@pytest.mark.parametrize("bundle", ["evidence-leak", "evidence-wrong-scope-write"])
def test_committed_bundle_recall_records_match_the_adapters_own_shape(bundle):
    root = PROOF / "fixtures" / bundle
    raws = {s: json.loads((root / "precedence" / f"raw-{s}.json").read_text())
            for s in fm.SCOPE_ORDER}
    times = {r["scope"]: r["timestamp"]
             for r in json.loads((root / "precedence" / "recall-1.json").read_text())["records"]}
    rebuilt = fm.merge({s: [fm.normalize_hit(h, s, times.get(s)) for h in raws[s]]
                        for s in fm.SCOPE_ORDER})
    recorded = json.loads((root / "precedence" / "recall-1.json").read_text())["records"]
    assert [set(r) for r in recorded] == [set(r) for r in rebuilt]
    assert [r["stable_id"] for r in recorded] == [r["stable_id"] for r in rebuilt]
    assert [r["scope"] for r in recorded] == [r["scope"] for r in rebuilt]


def test_the_honeytoken_fixture_names_all_four_scopes():
    tokens = json.loads((PROOF / "fixtures" / "honeytokens.json").read_text())
    assert set(tokens) == set(fm.SCOPE_ORDER)
    for scope, token in tokens.items():
        assert token.startswith(f"HT-{scope}-")
    assert len(set(tokens.values())) == 4


# --------------------------------------------------------------------------- checker: PASS + deferred

def test_a_repaired_wrong_scope_bundle_passes(good):
    rc, line = _verdict(good)
    assert rc == 0
    assert line == ("PASS: S0-06 four-scope - 4/4 assertions, "
                    "substrate ai-memory 1.39.0@73715b6f")


def test_a_repaired_leak_bundle_passes(tmp_path):
    rc, line = _verdict(_repair_leak(tmp_path / "good-leak"))
    assert rc == 0
    assert line.startswith("PASS: S0-06 four-scope - 4/4 assertions")


def test_the_checker_prints_exactly_one_stdout_line(good, tmp_path):
    """Class-3 closure: every assertion here reads `splitlines()[-1]`, so a verdict preceded by
    a warning line would be invisible. The checker's stdout is ONE line in all three outcomes."""
    for root, expected_rc in ((good, 0), (tmp_path / "absent", 2),
                              (PROOF / "fixtures" / "evidence-leak", 1)):
        proc = _run_checker(root)
        assert proc.returncode == expected_rc
        assert len(proc.stdout.splitlines()) == 1, proc.stdout
        assert proc.stdout.endswith("\n")


def test_an_absent_evidence_root_defers(tmp_path):
    rc, line = _verdict(tmp_path / "never-captured")
    assert rc == 2
    assert line == "deferred: S0-06 evidence not captured"


def test_the_sandbox_tree_has_no_captured_evidence_so_the_spec_positive_leg_defers():
    rc, line = _verdict(PROOF / "evidence")
    assert (rc, line) == (2, "deferred: S0-06 evidence not captured")


# --------------------------------------------------------------------------- checker: committed negatives

def test_the_committed_leak_bundle_is_refused():
    rc, line = _verdict(PROOF / "fixtures" / "evidence-leak")
    assert rc == 1
    assert line == "leak: honeytoken HT-team-c52e6f04 surfaced from team"


def test_the_committed_wrong_scope_bundle_is_refused():
    rc, line = _verdict(PROOF / "fixtures" / "evidence-wrong-scope-write")
    assert rc == 1
    assert line == "write: record found in project"


# --------------------------------------------------------------------------- checker: one mutant per REASONS row

def test_substrate_commit_mutant(good):
    _edit(good / "substrate.json", lambda d: d.__setitem__("commit", "0" * 40))
    assert _verdict(good) == (1, "substrate: not the pinned ai-memory (commit=%s)" % ("0" * 40))


def test_substrate_version_mutant(good):
    _edit(good / "substrate.json", lambda d: d.__setitem__("version", "1.38.0"))
    assert _verdict(good) == (1, "substrate: not the pinned ai-memory (version=1.38.0)")


def test_substrate_binary_digest_mutant(good):
    _edit(good / "substrate.json", lambda d: d.__setitem__("binary_sha256", "deadbeef"))
    assert _verdict(good) == (1, "substrate: not the pinned ai-memory (binary_sha256=deadbeef)")


def test_posture_wrong_value_mutant(good):
    _edit(good / "substrate.json",
          lambda d: d["posture"].__setitem__("AI_MEMORY_AUTO_IMPROVE__REQUIRE_APPROVAL", "false"))
    assert _verdict(good) == (
        1, "substrate: unsafe posture AI_MEMORY_AUTO_IMPROVE__REQUIRE_APPROVAL=false")


def test_posture_absent_key_mutant(good):
    _edit(good / "substrate.json", lambda d: d["posture"].pop("AI_MEMORY_MAINTENANCE__ENABLED"))
    assert _verdict(good) == (1, "substrate: unsafe posture AI_MEMORY_MAINTENANCE__ENABLED=<absent>")


def test_denied_leg_status_mutant(good):
    _edit(good / "denied" / "recall.json", lambda d: d.__setitem__("status", "ok"))
    assert _verdict(good) == (1, "denied: leg did not record the tuple denial")


def test_denied_leg_missing_denial_event_mutant(good):
    (good / "denied" / "events.jsonl").write_text(
        json.dumps({"event": "scope_tuple_authorized", "reason": "authz: ok", "seq": 1}) + "\n")
    assert _verdict(good) == (1, "denied: leg did not record the tuple denial")


def test_denied_leg_request_event_mutant(good):
    path = good / "denied" / "events.jsonl"
    path.write_text(path.read_text() + json.dumps(
        {"event": "http_request", "reason": "substrate: request issued",
         "method": "GET", "path": "/api/v1/search", "seq": 2}) + "\n")
    assert _verdict(good) == (
        1, "denied: adapter recorded a request for the unauthorized tuple")


def test_denied_leg_unreadable_stream_mutant(good):
    path = good / "denied" / "events.jsonl"
    path.write_text(path.read_text() + "not json at all\n")
    assert _verdict(good) == (1, "denied: event stream unreadable")


def test_nondeterministic_merge_mutant(good):
    _edit(good / "precedence" / "recall-2.json",
          lambda d: d["records"][0].__setitem__("confidence", -9.99))
    assert _verdict(good) == (1, "merge: nondeterministic")


def test_recall_status_mutant(good):
    _edit_recalls(good, lambda d: d.__setitem__("status", "degraded"))
    assert _verdict(good) == (
        1, "leg: precedence/recall-1.json status degraded, expected ok")


def test_collision_absent_from_a_raw_scope_mutant(good):
    path = good / "precedence" / "raw-team.json"
    kept = [e for e in json.loads(path.read_text()) if e["path"] != "notes/deploy-window.md"]
    path.write_text(json.dumps(kept, indent=2, sort_keys=True) + "\n")
    assert _verdict(good) == (
        1, "precedence: raw scopes carry 0 four-way collisions, expected 1")


def test_indistinguishable_variants_mutant(good):
    agent_title = next(e["title"] for e in
                       json.loads((good / "precedence" / "raw-agent.json").read_text())
                       if e["path"] == "notes/deploy-window.md")
    path = good / "precedence" / "raw-team.json"
    doc = json.loads(path.read_text())
    for entry in doc:
        if entry["path"] == "notes/deploy-window.md":
            entry["title"] = agent_title
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    assert _verdict(good) == (1, "precedence: raw scopes do not carry four distinct variants")


def test_wrong_precedence_winner_mutant(good):
    def flip(doc):
        for record in doc["records"]:
            if record["stable_id"] == "notes/deploy-window.md":
                record["scope"] = "team"
    _edit_recalls(good, flip)
    assert _verdict(good) == (
        1, "precedence: notes/deploy-window.md resolved to team, expected agent")


def test_missing_shadowed_scope_mutant(good):
    def strip(doc):
        for record in doc["records"]:
            if record["stable_id"] == "notes/deploy-window.md":
                record["provenance"]["shadowed_scopes"] = ["project", "company"]
    _edit_recalls(good, strip)
    assert _verdict(good) == (
        1, "precedence: notes/deploy-window.md provenance missing shadowed scope team")


def test_write_absent_from_the_active_scope_mutant(good):
    page_path = json.loads((good / "write-scope" / "write.json").read_text())["page_path"]
    path = good / "write-scope" / "raw-agent.json"
    kept = [e for e in json.loads(path.read_text()) if e["path"] != page_path]
    path.write_text(json.dumps(kept, indent=2, sort_keys=True) + "\n")
    assert _verdict(good) == (1, "write: record absent from agent")


def test_retry_produced_a_second_record_mutant(good):
    page_path = json.loads((good / "write-scope" / "write.json").read_text())["page_path"]
    path = good / "write-scope" / "raw-agent.json"
    doc = json.loads(path.read_text())
    doc.append(dict(next(e for e in doc if e["path"] == page_path),
                    updated_at="2026-09-05T09:30:00Z"))
    path.write_text(json.dumps(doc, indent=2, sort_keys=True) + "\n")
    assert _verdict(good) == (1, "write: idempotent retry produced 2 records")


def test_write_leg_status_mutant(good):
    _edit(good / "write-scope" / "retry.json", lambda d: d.__setitem__("status", "degraded"))
    assert _verdict(good) == (
        1, "leg: write-scope/retry.json status degraded, expected ok")


def test_vacuous_leak_oracle_mutant(good):
    """The oracle self-test: a honeytoken missing from its OWN scope makes the absence proof
    worthless, so the checker refuses rather than passing (AF-AP-52)."""
    tokens = json.loads((good / "leak" / "honeytokens.json").read_text())
    path = good / "leak" / "raw-team.json"
    path.write_text(path.read_text().replace(tokens["team"], "HT-team-scrubbed"))
    assert _verdict(good) == (1, "leak: honeytoken absent from its own scope")


def test_empty_recall_makes_the_leak_test_vacuous_mutant(good):
    tokens = json.loads((good / "leak" / "honeytokens.json").read_text())
    path = good / "leak" / "recall.json"
    path.write_text(path.read_text().replace(tokens["agent"], "HT-agent-scrubbed"))
    assert _verdict(good) == (
        1, "leak: authorized honeytoken %s absent from recall" % tokens["agent"])


def test_missing_leg_file_mutant(good):
    (good / "precedence" / "recall-1.json").unlink()
    assert _verdict(good) == (1, "leg: precedence/recall-1.json missing or not a regular file")


def test_substrate_missing_mutant(good):
    (good / "substrate.json").unlink()
    assert _verdict(good) == (1, "leg: substrate.json missing or not a regular file")


def test_malformed_leg_json_mutant(good):
    (good / "leak" / "honeytokens.json").write_text("{ not json\n")
    assert _verdict(good) == (1, "leg: leak/honeytokens.json missing or not a regular file")


def test_a_fifo_in_place_of_a_leg_file_is_refused_not_read(good):
    """A read outside a regular file can block forever; the checker refuses in bounded time."""
    path = good / "leak" / "raw-team.json"
    path.unlink()
    os.mkfifo(path)
    try:
        proc = subprocess.run([sys.executable, str(CHECKER_PATH), str(good)],
                              capture_output=True, text=True, timeout=30)
    finally:
        path.unlink()
    assert proc.returncode == 1
    assert proc.stdout.strip().splitlines()[-1] == (
        "leg: leak/raw-team.json missing or not a regular file")


def test_a_directory_in_place_of_a_leg_file_is_refused(good):
    path = good / "write-scope" / "raw-project.json"
    path.unlink()
    path.mkdir()
    assert _verdict(good) == (
        1, "leg: write-scope/raw-project.json missing or not a regular file")


def test_every_reasons_row_is_asserted_by_a_mutant_in_this_module():
    """The mutant table is closed: no REASONS row may be unreachable (an emitted-but-unreachable
    check is a silent hollow green).

    Each row's template is turned into a pattern and matched against the string constants that
    appear inside `assert` statements here — a docstring or a comment mentioning the reason
    cannot satisfy it. It is a tripwire on coverage; the reachability itself is proven by the
    named mutant tests above, each of which asserts the COMPLETE reason.
    """
    import ast
    import re
    tree = ast.parse(Path(__file__).read_text())
    asserted = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Assert):
            for inner in ast.walk(node):
                if isinstance(inner, ast.Constant) and isinstance(inner.value, str):
                    asserted.add(inner.value)
    def unreached_rows(rows):
        out = []
        for key, template in rows.items():
            pattern = "^" + ".*".join(
                re.escape(part) for part in re.split(r"\{[a-z_]+\}", template)) + "$"
            if not any(re.match(pattern, value) for value in asserted):
                out.append(key)
        return out

    assert unreached_rows(checker.REASONS) == []
    # Positive control: a row nobody asserts IS reported unreached. The template is JOINED at
    # runtime so the string never exists as a literal here — written inline it would sit inside
    # this very assert and satisfy its own pattern (found by running it).
    planted = " ".join(["no", "assertion", "matches", "{x}", "here"])
    assert unreached_rows({"planted": planted}) == ["planted"]


# --------------------------------------------------------------------------- spec + contract

def test_spec_validates_against_the_committed_schema():
    spec = json.loads((PROOF / "spec.json").read_text())
    schema = json.loads((REPO / "proofs" / "schemas" / "spec.schema.json").read_text())
    jsonschema.validate(spec, schema)
    assert spec["proof_id"] == "S0-06"


def test_spec_pins_the_complete_reasons_the_tests_assert():
    """AF-AP-29: the canonical contract is at least as strong as the strongest test."""
    spec = json.loads((PROOF / "spec.json").read_text())
    negatives = {tuple(leg["cmd"][-1:]): leg["expect"]["failure_reason"]
                 for leg in spec["legs"] if leg["leg"] == "negative"}
    assert negatives[("x",)] == TUPLE_DENIED
    assert negatives[("proofs/S0-06/fixtures/evidence-leak",)] == (
        "leak: honeytoken HT-team-c52e6f04 surfaced from team")
    assert negatives[("proofs/S0-06/fixtures/evidence-wrong-scope-write",)] == (
        "write: record found in project")
    assert len(negatives) == 3       # the seed requires 1; this proof commits 3


def test_spec_negative_legs_reproduce_their_pinned_reason_exactly():
    spec = json.loads((PROOF / "spec.json").read_text())
    for leg in spec["legs"]:
        if leg["leg"] != "negative":
            continue
        cmd = [sys.executable] + leg["cmd"][1:]
        proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO),
                              timeout=leg["timeout_s"])
        assert proc.returncode == leg["expect"]["exit_code"]
        assert proc.stdout.strip().splitlines()[-1] == leg["expect"]["failure_reason"]


def test_spec_positive_leg_defers_in_this_venue():
    spec = json.loads((PROOF / "spec.json").read_text())
    leg = next(x for x in spec["legs"] if x["leg"] == "positive")
    proc = subprocess.run([sys.executable] + leg["cmd"][1:], capture_output=True, text=True,
                          cwd=str(REPO), timeout=leg["timeout_s"])
    assert proc.returncode == 2       # the runner reads exit 2 as Deferred and mints nothing


def test_the_pinned_commit_comes_from_upstream_lock_not_the_checker():
    """AF-AP-13: a declared-contract fact is read from the declaration, never hardcoded here."""
    import yaml
    lock = yaml.safe_load((REPO / "upstream.lock.yaml").read_text())
    assert checker._pinned_commit() == lock["selected_core"]["ai-memory"]["commit"]
    assert lock["selected_core"]["ai-memory"]["commit"] not in CHECKER_PATH.read_text()


def test_neither_adapter_nor_checker_can_spawn_a_process():
    """No cargo build, no shell-out anywhere on the graded path — an AST check, so the words in
    the docstrings that EXPLAIN the rule cannot satisfy it."""
    import ast
    for path in (ADAPTER_PATH, CHECKER_PATH):
        tree = ast.parse(path.read_text())
        imported = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported |= {a.name.split(".")[0] for a in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                assert node.func.attr not in ("system", "popen", "execv", "spawnv", "fork"), path
        assert not imported & {"subprocess", "shutil", "multiprocessing", "pty"}, path
    # positive control: the same AST scan DOES see the spawner this test module itself imports
    self_tree = ast.parse(Path(__file__).read_text())
    self_imports = {a.name.split(".")[0] for n in ast.walk(self_tree)
                    if isinstance(n, ast.Import) for a in n.names}
    assert "subprocess" in self_imports


def test_pc_runner_scripts_are_syntactically_valid():
    for script in sorted((PROOF / "tools" / "pc").glob("*.sh")):
        proc = subprocess.run(["bash", "-n", str(script)], capture_output=True, text=True,
                              timeout=60)
        assert proc.returncode == 0, proc.stderr


def test_pc_runner_never_kills_by_name():
    """AF-AP-34: on the owner's box a name-based kill also matches production containers."""
    for script in sorted((PROOF / "tools" / "pc").glob("*.sh")):
        # comments are stripped: the header that EXPLAINS the ban must not satisfy the test
        code = "\n".join(line.split("#", 1)[0] for line in script.read_text().splitlines())
        for banned in ("pkill", "killall", "pgrep"):
            assert banned not in code, f"{script.name} uses {banned}"
    # the stop path exists and reads the pid this run wrote, after confirming /proc/<pid>/exe
    runner = (PROOF / "tools" / "pc" / "run_s0_06_legs.sh").read_text()
    assert 'kill "$pid"' in runner
    assert "/proc/$pid/exe" in runner
    assert 'cat "$pidfile"' in runner


def test_pc_runner_refuses_a_bound_port():
    text = (PROOF / "tools" / "pc" / "start_ai_memory.sh").read_text()
    assert "already bound" in text
    assert "exit 65" in text


def test_the_seed_fixture_lives_at_the_seed_declared_path():
    assert stat.S_ISREG(NEG_FIXTURE.lstat().st_mode)
    assert NEG_FIXTURE.relative_to(REPO).as_posix() == "fixtures/s0-06/neg-unauthorized-tuple.json"
