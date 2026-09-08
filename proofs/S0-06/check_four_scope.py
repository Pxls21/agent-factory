#!/usr/bin/env python3
"""S0-06 checker — the four-scope adapter's assertions, graded over evidence captured against a
REAL pinned ai-memory instance.

    check_four_scope.py <evidence-root>

Exit 0 + the PASS line · exit 1 + ONE exact reason from REASONS · exit 2 + `deferred: …` when the
evidence root is absent. It is absent in the sandbox because no ai-memory instance runs here: the
seed defers the venue to the wave-0 spike (`seeds/seed-stage0-v1.yaml:447-449`, "spike decides
venue") and that spike ran on the PC (`spikes/rust-ai-memory/result.json`,
`env_fingerprint: "pc-bridge:fedora:x86_64:rustup-1.95.0"`), where it measured 618 MB + 306 MB
of built binaries against the ~3 GB free in this tree. The toolchain is NOT the obstacle — `rust-toolchain.toml`
is tracked at the pinned commit and pins `channel = "1.95"`, matching `Cargo.toml`'s
`rust-version = "1.95"`, and rustup resolves 1.95.0 here on demand.

The four seed assertions (seeds/seed-stage0-v1.yaml:449-453), each with TWO instruments — the
adapter's own output AND a raw `/api/v1` read that bypasses the adapter, so no assertion rests on
the subject's self-report (AF-AP-28):

  1. the auth tuple is validated outside model control  -> denied/
  2. Agent->Project->Team->Company precedence, byte-identical on a repeat run -> precedence/
  3. writes land only in the authorized active scope    -> write-scope/
  4. a honeytoken staged in one scope never surfaces in another scope's recall -> leak/

Assertion 1's second instrument is SUBSTRATE-SIDE, not the adapter's own event stream: the denied
leg records the instance port's socket table before and after the denied recall
(`denied/socket-witness.json`) and a connection that appeared there is a request the adapter
denies making. The pinned server has no per-request access log to count instead — there is no
`TraceLayer`/`tower_http::trace` anywhere in its crates, `crates/ai-memory-web/src/routes/api.rs`
emits no `tracing::` event at all, the only `info!` lines in that crate are mount-time
(`crates/ai-memory-web/src/mount.rs:387,407,453`), and the router's own layers are body limits and
auth (`crates/ai-memory-cli/src/commands/serve.rs:1134-1141,1182-1190`); logging init attaches
only fmt layers at `config.log_level` (`crates/ai-memory-cli/src/logging.rs:99-133`, default
"info", `crates/ai-memory-cli/src/config.rs:630`). The witness is PAIRED: the precedence leg
records the same before/after, and a bundle whose positive control saw no new connection is
refused as vacuous, so an instrument that never fires cannot pass by silence.

The substrate identity is checked first: a bundle whose commit or version is not the pin in
upstream.lock.yaml, or whose ai-memory posture is not the safe posture of docs/04 §6 AS READ BACK
FROM THE RUNNING CHILD'S ENVIRONMENT, cannot grade any assertion. That check is also why a bundle
recorded against the tests' local recording HTTP server can never mint: it carries no real
substrate.json.

This module deliberately re-derives what it grades (the write page path, the four scope projects)
instead of importing `adapter/factory_memory.py`: an oracle that imports its subject is a mirror
(anti-hollow-green §4). It imports `urllib.parse` for URL provenance and NOTHING that can issue a
request.
"""
from __future__ import annotations

import hashlib
import json
import stat
import sys
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]

SCOPE_ORDER = ("agent", "project", "team", "company")
LEGS = ("denied", "precedence", "write-scope", "leak")
# Re-derived here, never imported from the adapter (docs/03 §4, workspace fixed to `factory`).
WORKSPACE = "factory"
GLOBAL_PROJECT = "_global"
# The leak leg's binding authorises Agent+Project only; Team and Company are the scopes whose
# honeytokens must never appear in its recall.
LEAK_AUTHORIZED = ("agent", "project")
LEAK_FORBIDDEN = ("team", "company")
SAFE_POSTURE = {
    "AI_MEMORY_AUTO_IMPROVE__REQUIRE_APPROVAL": "true",
    "AI_MEMORY_AUTO_IMPROVE__SCHEDULER__ENABLED": "false",
    "AI_MEMORY_MAINTENANCE__ENABLED": "false",
    "AI_MEMORY_SLOTS__PER_USER": "false",
}
# The positive control for the socket witness: the precedence leg issues 2 recalls x 4 scopes x 2
# requests plus 4 raw reads, so a working instrument records far more than this floor. The floor
# exists to fail a bundle whose witness never fired, not to count requests.
WITNESS_CONTROL_FLOOR = 4

REASONS = {
    "deferred": "deferred: S0-06 evidence not captured",
    "root": "evidence: {got} is not a plain directory",
    "file": "leg: {name} missing or not a regular file",
    "shape": "leg: {leg} evidence shape invalid ({detail})",
    "status": "leg: {name} status {got}, expected {want}",
    "substrate_pin": "substrate: not the pinned ai-memory ({got})",
    "posture": "substrate: unsafe posture {key}={value}",
    "posture_drift": "substrate: posture {key} declared {declared}, child environment {observed}",
    "nondet": "merge: nondeterministic",
    "collision": "precedence: raw scopes carry {n} four-way collisions, expected 1",
    "variants": "precedence: raw scopes do not carry four distinct variants",
    "winner": "precedence: {sid} resolved to {scope}, expected agent",
    "winner_content": "precedence: {sid} winner carries {got}, not the agent record",
    "shadow": "precedence: {sid} provenance missing shadowed scope {scope}",
    "raw_provenance": "{leg}: raw {scope} read carries {workspace}/{project}, expected {want}",
    "raw_url": "{leg}: raw {scope} was fetched from {url}, expected {want}",
    "raw_origin": "{leg}: raw {scope} origin {got}, expected {want}",
    "event_stream": "{leg}: {name} event stream invalid ({detail})",
    "event_set": "{leg}: {name} events {got}, expected {want}",
    "event_path": "{leg}: {name} recorded {got}, expected {want}",
    "event_binding": "{leg}: {name} authorized scopes {got}, expected {want}",
    "event_complete": "{leg}: {name} degraded scopes {got}, expected {want}",
    "event_write": "{leg}: {name} write identity {got}, expected {want}",
    "write_record": "write: record.json {field} {got}, expected {want}",
    "write_found": "write: record found in {scope}",
    "write_absent": "write: record absent from agent",
    "write_retry": "write: idempotent retry produced {n} records",
    "write_path_derived": "write: page_path {got} is not derived from the idempotency key ({want})",
    "write_content": "write: written page is {got}, expected kind=fact tier=semantic",
    "leak": "leak: honeytoken {token} surfaced from {scope}",
    "leak_vacuous": "leak: honeytoken absent from its own scope",
    "leak_empty": "leak: authorized honeytoken {token} absent from recall",
    "denied_status": "denied: leg did not record the tuple denial",
    "denied_request": "denied: adapter recorded {got} for the unauthorized tuple",
    "denied_stream": "denied: event stream unreadable",
    "denied_witness": "denied: the substrate saw {n} new connection(s) during the denied recall",
    "denied_witness_vacuous": "denied: the socket witness never fired ({n} new connections on the "
                              "precedence leg)",
    "unexpected_file": "leg: unexpected evidence file {name}",
}

EXPECTED_FILES = {
    "denied": {
        "events.jsonl", "recall.json", "socket-witness.json", "substrate-observed.json",
    },
    "precedence": {
        "events-1.jsonl", "events-2.jsonl", "raw-agent.json", "raw-agent.url",
        "raw-company.json", "raw-company.url", "raw-project.json", "raw-project.url",
        "raw-team.json", "raw-team.url", "recall-1.json", "recall-2.json",
        "socket-witness.json", "substrate-observed.json", "tuple.json",
    },
    "write-scope": {
        "events-retry.jsonl", "events-write.jsonl", "raw-agent.json", "raw-agent.url",
        "raw-company.json", "raw-company.url", "raw-project.json", "raw-project.url",
        "raw-team.json", "raw-team.url", "record.json", "retry.json",
        "substrate-observed.json", "tuple.json", "write.json",
    },
    "leak": {
        "events.jsonl", "honeytokens.json", "raw-agent.json", "raw-agent.url",
        "raw-company.json", "raw-company.url", "raw-project.json", "raw-project.url",
        "raw-team.json", "raw-team.url", "recall.json", "substrate-observed.json", "tuple.json",
    },
}


class Fail(Exception):
    """Carries ONE exact reason from REASONS.

    `reason_key` is positional-only: a REASONS template whose own field is called `key` (the
    posture row) would otherwise collide with the selector and raise TypeError instead of
    reporting — an emitted-but-unreachable check, found by the posture mutant.
    """

    def __init__(self, reason_key, /, **fields):
        self.reason = REASONS[reason_key].format(**fields)
        super().__init__(self.reason)


class Deferred(Exception):
    pass


def _read_text(root: Path, rel: str) -> str:
    """Read one evidence file. A directory, a FIFO, a symlink to one, or an absent path is a
    failure, never a silent skip — S_ISREG on the lstat of the path itself."""
    path = root / rel
    try:
        mode = path.lstat().st_mode
    except OSError:
        raise Fail("file", name=rel)
    if not stat.S_ISREG(mode):
        raise Fail("file", name=rel)
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        raise Fail("file", name=rel)


def _reject_constant(name):
    """`NaN`/`Infinity`/`-Infinity` are not RFC-8259 JSON. Python's `json` accepts them silently,
    `jq` and `serde_json` do not — so evidence carrying one is unreadable to the next reader and
    is refused here as well as at the producer (F-15)."""
    raise ValueError("non-RFC-8259 constant %s" % name)


def _loads(text: str, rel: str):
    try:
        return json.loads(text, parse_constant=_reject_constant)
    except json.JSONDecodeError:
        raise Fail("file", name=rel)


def _read_json(root: Path, rel: str):
    return _loads(_read_text(root, rel), rel)


def _require_status(doc, name, want="ok"):
    got = doc.get("status")
    if got != want:
        raise Fail("status", name=name, got=got, want=want)


def _lock() -> dict:
    """`upstream.lock.yaml`'s ai-memory row, or a NAMED failure.

    A missing key, a renamed section and a duplicate `ai-memory:` block are all refusals: PyYAML
    resolves duplicate mapping keys last-one-wins, so a second block would silently re-pin the
    substrate the checker grades against (F-12).
    """
    try:
        text = (REPO_ROOT / "upstream.lock.yaml").read_text(encoding="utf-8")
    except OSError as exc:
        raise Fail("substrate_pin",
                   got="upstream.lock.yaml is unreadable (%s)" % type(exc).__name__)
    if text.count("\n  ai-memory:") != 1:
        raise Fail("substrate_pin", got="upstream.lock.yaml carries %d ai-memory blocks"
                                        % text.count("\n  ai-memory:"))
    try:
        row = yaml.safe_load(text)["selected_core"]["ai-memory"]
        if not isinstance(row["commit"], str) or not isinstance(row["observed_version"], str):
            raise KeyError("commit/observed_version")
    except (KeyError, TypeError, yaml.YAMLError) as exc:
        raise Fail("substrate_pin",
                   got="upstream.lock.yaml has no selected_core.ai-memory (%s)" % type(exc).__name__)
    return row


def _pinned_commit() -> str:
    return _lock()["commit"]


def _pinned_version() -> str:
    """The version half of the pin, read from the same declaration as the commit (F-3): a literal
    here would grade a bundle against a version the lock no longer pins."""
    return _lock()["observed_version"]


def _url_names(url: str, workspace: str, project: str) -> bool:
    """Does this fetched URL address exactly (workspace, project)?

    `/api/v1/search` carries them as query parameters; the page listing carries them as path
    segments (`/api/v1/workspaces/{ws}/projects/{p}/pages`), so both shapes are accepted — but the
    NAMES must be there, which is what makes four raw reads four scopes rather than four copies.
    """
    parsed = urlparse(url)
    query = parse_qs(parsed.query)
    segments = [unquote(part) for part in parsed.path.split("/")]
    return ((workspace in query.get("workspace", []) or workspace in segments)
            and (project in query.get("project", []) or project in segments))


def _leg_projects(root: Path, leg: str) -> dict:
    """The (workspace, project) each scope's raw read must carry, from the identity tuple the
    runner wrote into the leg (`<leg>/tuple.json`) — not from a constant in this file, so the
    leak leg's a-beta and the precedence leg's a-alpha are told apart."""
    tup = _read_json(root, "%s/tuple.json" % leg)
    return {
        "agent": (WORKSPACE, "agent--%s" % tup["agent"]),
        "project": (WORKSPACE, "project--%s" % tup["project"]),
        "team": (WORKSPACE, "team--%s" % tup["team"]),
        "company": (WORKSPACE, GLOBAL_PROJECT),
    }


def _require_raw_url(root: Path, leg: str, scope: str, workspace: str, project: str,
                     origin: str) -> None:
    url = _read_text(root, "%s/raw-%s.url" % (leg, scope)).strip()
    parsed = urlparse(url)
    got_origin = "%s://%s" % (parsed.scheme, parsed.netloc)
    if got_origin != origin:
        raise Fail("raw_origin", leg=leg, scope=scope, got=got_origin, want=origin)
    search_route = "/api/v1/search"
    pages_route = "/api/v1/workspaces/%s/projects/%s/pages" % (
        quote(workspace, safe=""), quote(project, safe=""))
    route_ok = (
        parsed.path == search_route
        and parse_qs(parsed.query).get("workspace") == [workspace]
        and parse_qs(parsed.query).get("project") == [project]
    ) or (parsed.path == pages_route and not parsed.query)
    if not route_ok:
        raise Fail("raw_url", leg=leg, scope=scope, url=url,
                   want="%s/%s" % (workspace, project))


def _require_raw_provenance(root: Path, leg: str, raw: dict, origin: str) -> None:
    """The independent instrument's OWN provenance (F-5).

    `ApiSearchHit` carries `workspace` and `project`
    (`crates/ai-memory-web/src/routes/api.rs:1254-1263`); without reading them, four copies of one
    project's search response satisfy a "four distinct scopes" assertion as long as the titles
    differ.
    """
    want = _leg_projects(root, leg)
    for scope in SCOPE_ORDER:
        workspace, project = want[scope]
        _require_raw_url(root, leg, scope, workspace, project, origin)
        for entry in raw[scope]:
            if entry["workspace"] != workspace or entry["project"] != project:
                raise Fail("raw_provenance", leg=leg, scope=scope,
                           workspace=entry["workspace"], project=entry["project"],
                           want="%s/%s" % (workspace, project))


def _new_connections(root: Path, leg: str) -> list:
    """The socket 4-tuples that appeared on the instance's port across one leg.

    A SET difference, not a count difference: a TIME-WAIT socket left over from an earlier leg can
    expire between the two snapshots, which makes a raw count delta go negative and would let an
    expiry mask a new connection. A 4-tuple that is in `after` and not in `before` is a connection
    that was opened during the leg.
    """
    doc = _read_json(root, "%s/socket-witness.json" % leg)
    before, after = doc["before"], doc["after"]
    if not isinstance(before, list) or not isinstance(after, list):
        raise TypeError("socket-witness before/after must be arrays")
    return sorted(set(after) - set(before))


def check_substrate(root: Path) -> dict:
    """Identity + safe posture of the instance the evidence came from.

    Every field graded here is an OBSERVATION the producer read back, never a constant it re-typed
    (F-4): `binary_sha256_observed` is re-hashed independently in every leg, `version_stdout` is
    the binary's own `--version` line, and `posture_observed` is read from the serving child's
    /proc/<pid>/environ. `binary_sha256_observed` is provenance, NOT a pin: a release build is not
    bit-reproducible across toolchains and hosts, so no constant in this repo can name the expected
    digest. What it can prove — and does — is that ONE binary served the whole run.
    """
    doc = _read_json(root, "substrate.json")
    pinned = _pinned_commit()
    commit = doc.get("commit")
    if commit != pinned:
        raise Fail("substrate_pin", got="commit=%s" % commit)
    expected_version = _pinned_version()
    version = doc.get("version")
    if version != expected_version:
        raise Fail("substrate_pin", got="version=%s" % version)
    if expected_version not in doc.get("version_stdout", ""):
        raise Fail("substrate_pin", got="version_stdout=%s" % doc.get("version_stdout"))
    digest = doc.get("binary_sha256_observed")
    if not isinstance(digest, str) or len(digest) != 64 or set(digest) - set("0123456789abcdef"):
        raise Fail("substrate_pin", got="binary_sha256_observed=%s" % digest)
    bin_path = doc.get("bin_path")
    for leg in LEGS:
        observed = _read_json(root, "%s/substrate-observed.json" % leg)
        if observed.get("binary_sha256_observed") != digest or observed.get("bin_path") != bin_path:
            raise Fail("substrate_pin", got="leg %s observed %s at %s" % (
                leg, observed.get("binary_sha256_observed"), observed.get("bin_path")))
    declared = doc.get("posture") or {}
    observed_posture = doc.get("posture_observed") or {}
    for key, want in sorted(SAFE_POSTURE.items()):
        value = observed_posture.get(key, "<absent>")
        if value != want:
            raise Fail("posture", key=key, value=value)
        if declared.get(key, "<absent>") != value:
            raise Fail("posture_drift", key=key,
                       declared=declared.get(key, "<absent>"), observed=value)
    origin = doc.get("origin")
    parsed_origin = urlparse(origin) if isinstance(origin, str) else None
    if (parsed_origin is None or parsed_origin.scheme not in {"http", "https"}
            or not parsed_origin.netloc or parsed_origin.path or parsed_origin.params
            or parsed_origin.query or parsed_origin.fragment):
        raise Fail("substrate_pin", got="origin=%s" % origin)
    doc["origin"] = "%s://%s" % (parsed_origin.scheme, parsed_origin.netloc)
    return doc


def _read_events(root: Path, leg: str, name: str) -> list[dict]:
    rows = []
    for line in _read_text(root, "%s/%s" % (leg, name)).splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line, parse_constant=_reject_constant)
        except (json.JSONDecodeError, ValueError) as exc:
            raise Fail("event_stream", leg=leg, name=name, detail=type(exc).__name__)
        if not isinstance(event, dict) or not isinstance(event.get("event"), str):
            raise Fail("event_stream", leg=leg, name=name, detail="event must be a named object")
        rows.append(event)
    if not rows:
        raise Fail("event_stream", leg=leg, name=name, detail="empty")
    if [row.get("seq") for row in rows] != list(range(1, len(rows) + 1)):
        raise Fail("event_stream", leg=leg, name=name, detail="sequence is not contiguous")
    return rows


def _require_events(leg: str, name: str, events: list[dict], expected: list[str]) -> None:
    got = [event["event"] for event in events]
    if got != expected:
        raise Fail("event_set", leg=leg, name=name, got=got, want=expected)


def _request_marker(event: dict) -> str:
    marker = "%s %s" % (event.get("method"), event.get("path"))
    if event.get("path") == "/api/v1/search":
        marker += " query_sha256_16=%s" % event.get("query_sha256_16")
    return marker


def _expected_page_route(workspace: str, project: str) -> str:
    return "/api/v1/workspaces/%s/projects/%s/pages" % (
        quote(workspace, safe=""), quote(project, safe=""))


def _require_request_paths(root: Path, leg: str, name: str, events: list[dict],
                           scopes: tuple[str, ...], query: str) -> None:
    requests = [event for event in events if event["event"] == "http_request"]
    digest = hashlib.sha256(query.encode("utf-8")).hexdigest()[:16]
    projects = _leg_projects(root, leg)
    want = []
    for scope in scopes:
        workspace, project = projects[scope]
        want.append("GET /api/v1/search query_sha256_16=%s" % digest)
        want.append("GET %s" % _expected_page_route(workspace, project))
    got = [_request_marker(event) for event in requests]
    if got != want:
        raise Fail("event_path", leg=leg, name=name, got=got, want=want)


def _grade_recall_events(root: Path, leg: str, name: str,
                         scopes: tuple[str, ...], query: str) -> None:
    events = _read_events(root, leg, name)
    expected = ["scope_tuple_authorized"]
    for _scope in scopes:
        expected += ["http_request", "http_request"]
    expected.append("recall_complete")
    _require_events(leg, name, events, expected)
    _require_request_paths(root, leg, name, events, scopes, query)
    authorized = events[0]
    if authorized.get("authorized_scopes") != list(scopes):
        raise Fail("event_binding", leg=leg, name=name,
                   got=authorized.get("authorized_scopes"), want=list(scopes))
    complete = events[-1]
    if complete.get("degraded_scopes") != []:
        raise Fail("event_complete", leg=leg, name=name,
                   got=complete.get("degraded_scopes"), want=[])


def _grade_write_events(root: Path, name: str, page_path: str, key: dict, retry: bool) -> None:
    events = _read_events(root, "write-scope", name)
    expected = ["scope_tuple_authorized", "write_intent", "http_request"]
    expected += ["write_noop"] if retry else ["http_request", "write_committed"]
    _require_events("write-scope", name, events, expected)
    authorized = events[0]
    if authorized.get("authorized_scopes") != list(SCOPE_ORDER):
        raise Fail("event_binding", leg="write-scope", name=name,
                   got=authorized.get("authorized_scopes"), want=list(SCOPE_ORDER))
    workspace, project = _leg_projects(root, "write-scope")["agent"]
    requests = [event for event in events if event["event"] == "http_request"]
    want_requests = [("GET", _expected_page_route(workspace, project))]
    if not retry:
        want_requests.append(("POST", "/admin/write-page"))
    got_requests = [(event.get("method"), event.get("path")) for event in requests]
    if got_requests != want_requests:
        raise Fail("event_path", leg="write-scope", name=name,
                   got=got_requests, want=want_requests)
    for event in events:
        if event["event"] in {"write_intent", "write_noop", "write_committed"}:
            got = [event.get("scope"), event.get("project"),
                   event.get("page_path"), event.get("key")]
            want = ["agent", project, page_path, key]
            if got != want:
                raise Fail("event_write", leg="write-scope", name=name, got=got, want=want)


def check_precedence(root: Path, origin: str) -> None:
    """Assertion 2 — deterministic Agent-first merge over a real four-way collision."""
    first = _read_text(root, "precedence/recall-1.json")
    second = _read_text(root, "precedence/recall-2.json")
    if first != second:
        # The one cause of this row that is NOT the adapter: `search_scopes` sorts by rank and then
        # `truncate(limit)` (`crates/ai-memory-web/src/routes/api.rs:416-423`), and Rust's HashMap
        # iteration order is randomised per instance, so with more than `limit` RANK-TIED hits the
        # surviving SET can differ between two recalls. The seeded corpus is 3 pages per scope
        # against a limit of 20, so it cannot fire here — diagnose a red against the corpus size
        # before blaming `merge` (F-24).
        raise Fail("nondet")
    recall = _loads(first, "precedence/recall-1.json")
    _require_status(recall, "precedence/recall-1.json")
    _grade_recall_events(root, "precedence", "events-1.jsonl", SCOPE_ORDER, "deploy window")
    _grade_recall_events(root, "precedence", "events-2.jsonl", SCOPE_ORDER, "deploy window")
    # Second instrument: the raw per-project reads, bypassing the adapter entirely.
    raw = {s: _read_json(root, "precedence/raw-%s.json" % s) for s in SCOPE_ORDER}
    _require_raw_provenance(root, "precedence", raw, origin)
    # SCOPE_ORDER is a non-empty constant, so the intersection always has four operands: an
    # `if ids else []` fallback here would be provably dead (class-16 sweep).
    ids = [{e["path"] for e in raw[s]} for s in SCOPE_ORDER]
    collisions = sorted(set.intersection(*ids))
    if len(collisions) != 1:
        raise Fail("collision", n=len(collisions))
    sid = collisions[0]
    titles = [next(e["title"] for e in raw[s] if e["path"] == sid) for s in SCOPE_ORDER]
    if len(set(titles)) != len(SCOPE_ORDER):
        raise Fail("variants")
    merged = [r for r in recall["records"] if r["stable_id"] == sid]
    if len(merged) != 1 or merged[0]["scope"] != "agent":
        raise Fail("winner", sid=sid, scope=(merged[0]["scope"] if merged else "<absent>"))
    # The winner's CONTENT, not just its label: four different bodies are staged precisely so that
    # "the Agent copy wins" is a statement about the bytes the caller receives (F-6).
    agent_hit = next((e for e in raw["agent"] if e["path"] == sid), None)
    provenance = merged[0].get("provenance", {})
    if (agent_hit is None or provenance.get("title") != agent_hit["title"]
            or provenance.get("snippet") != agent_hit["snippet"]):
        raise Fail("winner_content", sid=sid, got=provenance.get("title"))
    shadowed = provenance.get("shadowed_scopes", [])
    for scope in SCOPE_ORDER[1:]:
        if scope not in shadowed:
            raise Fail("shadow", sid=sid, scope=scope)


def check_write_scope(root: Path, origin: str) -> None:
    """Assertion 3 — the write landed in agent--A only, and the retry was a no-op."""
    write = _read_json(root, "write-scope/write.json")
    _require_status(write, "write-scope/write.json")
    retry = _read_json(root, "write-scope/retry.json")
    _require_status(retry, "write-scope/retry.json")
    page_path = write["page_path"]
    # The path is RE-DERIVED here from the recorded idempotency key — three deliberately duplicated
    # lines of `factory_memory.idempotency_path` (F-7). Importing the adapter would make this
    # assertion a mirror of the thing it grades, and "a retry with the same key targets the same
    # page" is the write contract's whole claim (docs/03 §4).
    key = write["idempotency_key"]
    want = "observations/" + hashlib.sha256(
        "\x1f".join([key["session"], key["turn"], key["event_id"]]).encode("utf-8")
    ).hexdigest()[:16] + ".md"
    if page_path != want:
        raise Fail("write_path_derived", got=page_path, want=want)
    record = _read_json(root, "write-scope/record.json")
    record_key = {field: record.get(field) for field in ("session", "turn", "event_id")}
    if record_key != key:
        raise Fail("write_record", field="idempotency key", got=record_key, want=key)
    expected_type = {
        "body": record.get("body"),
        "kind": record.get("kind", "fact"),
        "tier": record.get("tier", "semantic"),
    }
    if (not isinstance(expected_type["body"], str) or not expected_type["body"]
            or expected_type["kind"] != "fact" or expected_type["tier"] != "semantic"):
        raise Fail("write_record", field="content/type", got=expected_type,
                   want={"body": "non-empty string", "kind": "fact", "tier": "semantic"})
    _grade_write_events(root, "events-write.jsonl", page_path, key, retry=False)
    _grade_write_events(root, "events-retry.jsonl", page_path, key, retry=True)
    raw = {s: _read_json(root, "write-scope/raw-%s.json" % s) for s in SCOPE_ORDER}
    # `PageSummary` (`crates/ai-memory-store/src/reader.rs:1174-1185`) carries no project field, so
    # this leg's raw reads CANNOT be provenance-checked from their payload the way the search legs
    # are. The URL each read was fetched from is recorded beside it instead (F-5).
    want_projects = _leg_projects(root, "write-scope")
    for scope in SCOPE_ORDER:
        _require_raw_url(root, "write-scope", scope, *want_projects[scope], origin)
    for scope in SCOPE_ORDER[1:]:
        if any(e["path"] == page_path for e in raw[scope]):
            raise Fail("write_found", scope=scope)
    found = [e for e in raw["agent"] if e["path"] == page_path]
    if not found:
        raise Fail("write_absent")
    if len(found) != 1 or retry.get("page_path") != page_path:
        raise Fail("write_retry", n=len(found))
    if found[0].get("kind") != "fact" or found[0].get("tier") != "semantic":
        raise Fail("write_content",
                   got="kind=%s tier=%s" % (found[0].get("kind"), found[0].get("tier")))


def check_leak(root: Path, origin: str) -> None:
    """Assertion 4 — staged honeytokens never cross a scope boundary they are not authorized for.

    The oracle self-tests in both directions (AF-AP-52): the forbidden tokens must be PRESENT in
    their own scope's raw read (else the absence proves nothing) and the authorized tokens must be
    present in the recall's RECORDS (else the recall was empty and every absence is vacuous). The
    forbidden half stays a whole-file test, which is deliberately conservative: a token hidden in
    any stray field still fires.
    """
    tokens = _read_json(root, "leak/honeytokens.json")
    recall_text = _read_text(root, "leak/recall.json")
    recall = _loads(recall_text, "leak/recall.json")
    _require_status(recall, "leak/recall.json")
    _grade_recall_events(root, "leak", "events.jsonl", LEAK_AUTHORIZED, "honeytoken")
    raw_text = {s: _read_text(root, "leak/raw-%s.json" % s) for s in SCOPE_ORDER}
    _require_raw_provenance(root, "leak",
                            {s: _loads(raw_text[s], "leak/raw-%s.json" % s) for s in SCOPE_ORDER}, origin)
    for scope in LEAK_FORBIDDEN:
        token = tokens[scope]
        if token not in raw_text[scope]:
            raise Fail("leak_vacuous")
        if token in recall_text:
            raise Fail("leak", token=token, scope=scope)
    # Scoped to the records (F-9): an EMPTY recall with the token in a note, a debug field or
    # `scopes_queried` satisfies a whole-file substring and proves nothing.
    records_text = json.dumps(recall["records"], sort_keys=True)
    for scope in LEAK_AUTHORIZED:
        token = tokens[scope]
        if token not in records_text:
            raise Fail("leak_empty", token=token)


def check_denied(root: Path) -> None:
    """Assertion 1 — the unauthorized tuple was refused, and no request left the adapter.

    Two instruments: the adapter's own event stream (an ALLOWLIST — the denied leg's stream is a
    closed set of exactly one event, so any other name is a finding, F-8) and the substrate-side
    socket witness with its paired positive control (D-3b).
    """
    recall = _read_json(root, "denied/recall.json")
    if recall.get("status") != "denied" or recall.get("reason") != "denied: scope-tuple-unauthorized":
        raise Fail("denied_status")
    events = []
    for line in _read_text(root, "denied/events.jsonl").splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            raise Fail("denied_stream")
        if not isinstance(event, dict) or "event" not in event:
            raise Fail("denied_stream")
        events.append(event)
    seen = {json.dumps(e["event"], sort_keys=True) if not isinstance(e["event"], str)
            else e["event"] for e in events}
    if "scope_tuple_denied" not in seen:
        raise Fail("denied_status")
    if seen != {"scope_tuple_denied"}:
        raise Fail("denied_request", got=sorted(seen - {"scope_tuple_denied"}))
    # The witness is graded control-first: a zero on the denied leg means nothing until the same
    # instrument is shown to fire on a leg that DID talk to the substrate.
    control = _new_connections(root, "precedence")
    if len(control) < WITNESS_CONTROL_FLOOR:
        raise Fail("denied_witness_vacuous", n=len(control))
    opened = _new_connections(root, "denied")
    if opened:
        raise Fail("denied_witness", n=len(opened))


def _check_expected_files(root: Path) -> None:
    """Require exactly the runner's regular-file evidence leaves, including every graded event."""
    expected_root = {"substrate.json", "PROVENANCE.md"}
    actual_root = set()
    leg_entries = set()
    try:
        entries = list(root.iterdir())
    except OSError:
        raise Fail("file", name="evidence")
    for entry in entries:
        if entry.name in LEGS:
            try:
                if not stat.S_ISDIR(entry.lstat().st_mode):
                    raise Fail("file", name=entry.name)
            except OSError:
                raise Fail("file", name=entry.name)
            leg_entries.add(entry.name)
            continue
        actual_root.add(entry.name)
    for name in sorted(expected_root - actual_root):
        raise Fail("file", name=name)
    for name in sorted(actual_root - expected_root):
        raise Fail("unexpected_file", name=name)
    for leg in sorted(set(EXPECTED_FILES) - leg_entries):
        raise Fail("file", name=leg)
    for name in sorted(expected_root):
        _read_text(root, name)
    for leg, expected in EXPECTED_FILES.items():
        directory = root / leg
        try:
            entries = list(directory.rglob("*"))
        except OSError:
            raise Fail("file", name=leg)
        for entry in entries:
            rel = entry.relative_to(directory).as_posix()
            try:
                mode = entry.lstat().st_mode
            except OSError:
                raise Fail("file", name="%s/%s" % (leg, rel))
            if stat.S_ISDIR(mode):
                continue
            if rel not in expected:
                raise Fail("unexpected_file", name="%s/%s" % (leg, rel))
            if not stat.S_ISREG(mode):
                raise Fail("file", name="%s/%s" % (leg, rel))
        for name in sorted(expected):
            path = directory / name
            try:
                if not stat.S_ISREG(path.lstat().st_mode):
                    raise Fail("file", name="%s/%s" % (leg, name))
            except OSError:
                raise Fail("file", name="%s/%s" % (leg, name))


def _graded(leg: str, check, root: Path, *args):
    """Run one check; a hostile bundle SHAPE becomes a named reason, never a traceback (F-10).

    The module's contract is one reason line per failure — a traceback gives the operator nothing
    to paste and breaks every consumer that reads the last stdout line.
    """
    try:
        return check(root, *args)
    except (KeyError, TypeError, AttributeError, IndexError, ValueError) as exc:
        raise Fail("shape", leg=leg, detail="%s: %s" % (type(exc).__name__, exc))


def run(root: Path) -> str:
    if root.is_symlink():
        # The runner creates the bundle itself; a symlinked root is not evidence it produced.
        raise Fail("root", got=str(root))
    if not root.is_dir():
        raise Deferred()
    _check_expected_files(root)
    substrate = _graded("substrate", check_substrate, root)
    origin = substrate["origin"]
    _graded("denied", check_denied, root)
    _graded("precedence", check_precedence, root, origin)
    _graded("write-scope", check_write_scope, root, origin)
    _graded("leak", check_leak, root, origin)
    return "PASS: S0-06 four-scope - 4/4 assertions, substrate ai-memory %s@%s" % (
        substrate["version"],
        substrate["commit"][:8],
    )


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print("usage: check_four_scope.py <evidence-root>")
        return 1
    try:
        print(run(Path(argv[0])))
    except Deferred:
        print(REASONS["deferred"])
        return 2
    except Fail as failure:
        print(failure.reason)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
