#!/usr/bin/env python3
"""S0-06 — `factory_memory`: the first-party composite memory adapter over ai-memory.

The component under proof. ai-memory is single-tenant by design: its own source says so
(`crates/ai-memory-core/src/actor.rs:2-3` "the wiki is single-tenant (no per-page RBAC; everyone
with auth sees the same pages)" and `:27-29` "Attribution records *who* did a write; it does not
gate *whether* they could do it"). A bearer token therefore authenticates a SERVER, never a
project, so the four logical scopes of docs/01 §6 / docs/03 §4 / D-006 exist only because THIS
adapter is an authorization boundary (D-007).

Logical mapping (docs/03 §4, workspace fixed to `factory`):

    Company  -> (factory, _global)
    Team     -> (factory, team--<team-id>)
    Project  -> (factory, project--<project-id>)
    Agent    -> (factory, agent--<agent-id>)

Read surface  : GET /api/v1/search?q&workspace&project&limit
                (routes `crates/ai-memory-web/src/routes/api.rs:42-45`; the scoped branch
                `scoped_search_mode` `:352-360` resolves exactly ONE (workspace, project) pair and
                `search_scopes` `:388-405` searches only the scopes it was given — no `_global`
                union) plus GET /api/v1/workspaces/{ws}/projects/{p}/pages for the record
                timestamp (`api.rs:33-36`, `PageSummary` `crates/ai-memory-store/src/reader.rs:1174-1185`).
Write surface : POST /admin/write-page (`crates/ai-memory-mcp/src/admin.rs:636`, request body
                `WritePageAdminRequest` `:6332-6358`, response `WritePageResponse` `:6366-6374`) —
                the same route ai-memory's own `ai-memory write-page` CLI posts to
                (`crates/ai-memory-cli/src/commands/write_page.rs:1-5, 61-74`). `/api/v1` is
                read-only (docs/02:73), so a write has to leave it.

Public adapter surface: `FactoryMemory.recall` and `FactoryMemory.write`. There is deliberately
no delete, purge, promote or approve entry point anywhere in this module (docs/03 §4 write
contract 2; docs/04 §5; STANDING PROJECT RULE 10).

CLI:
    factory_memory.py recall --tuple-file F --query Q [--base-url U] [--token-file T]
                             [--limit N] [--out FILE] [--events FILE]
    factory_memory.py write  --tuple-file F --scope S --record-file R [--base-url U]
                             [--token-file T] [--out FILE] [--events FILE]

Exit: 0 ok · 1 denied · 3 degraded · 70 unexpected (a crash never shares an exit code with a
decision, F-11). The final stdout line is the bare status reason, so a proof
spec can pin the COMPLETE reason string (AF-AP-29). `--out` receives the result JSON; `--events`
receives the decision event stream (one JSON object per line, also mirrored to stderr).

There is no `--bindings` flag on purpose: the authorization table is not caller-selectable.
No clock and no randomness anywhere in this module — every byte of a result and of the event
stream is a pure function of (bindings table, caller tuple, substrate responses).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import NamedTuple

ADAPTER_DIR = Path(__file__).resolve().parent
BINDINGS_PATH = ADAPTER_DIR / "bindings.json"

WORKSPACE = "factory"
GLOBAL_PROJECT = "_global"  # ai_memory_core::GLOBAL_SCOPE_PROJECT (crates/ai-memory-core/src/lib.rs:41)

# Agent -> Project -> Team -> Company (docs/03 §4 read contract 3, docs/04 §2, docs/01 §6).
SCOPE_ORDER = ("agent", "project", "team", "company")
TUPLE_FIELDS = ("actor", "agent", "team", "project")
# docs/03 §4 write contract: "`_global` writes and all upward promotion require a reviewed
# companion workflow" (docs/03_INTEGRATION_CONTRACTS.md:96), and STANDING PROJECT RULE 10 says
# upward promotion needs an explicit reviewed proposal. No such workflow exists yet, so the
# Company scope is READ-ONLY through this adapter regardless of what the table authorizes.
WRITE_REVIEWED_SCOPES = ("company",)

DEFAULT_BASE_URL = "http://127.0.0.1:8765"
DEFAULT_LIMIT = 20
DEFAULT_TIMEOUT_S = 10

# Every reason this module can emit. The two pinned by the seed
# (seeds/seed-stage0-v1.yaml:456-458 and docs/03 §4 write contract 1) are the first two.
REASONS = {
    "tuple_unauthorized": "denied: scope-tuple-unauthorized",
    "write_scope": "denied: write-scope-not-active",
    "write_review": "denied: write-scope-requires-review",
    "record_incomplete": "denied: write-record-incomplete",
    "recall_ok": "recall: complete",
    "recall_degraded": "recall: degraded",
    "write_ok": "write: page written",
    "write_noop": "write: idempotent no-op",
    "write_degraded": "write: degraded",
}


class Binding(NamedTuple):
    """The caller-supplied identity tuple. Ordering matches TUPLE_FIELDS."""

    actor: str
    agent: str
    team: str
    project: str


def scopes_for(binding: Binding) -> dict:
    """The four (workspace, project) pairs of docs/03 §4. Pure; workspace is fixed."""
    return {
        "agent": (WORKSPACE, f"agent--{binding.agent}"),
        "project": (WORKSPACE, f"project--{binding.project}"),
        "team": (WORKSPACE, f"team--{binding.team}"),
        "company": (WORKSPACE, GLOBAL_PROJECT),
    }


def load_bindings(path: Path = BINDINGS_PATH) -> list:
    """Read the committed authorization table.

    Every failure is a NAMED ValueError, never a bare OSError traceback: an absent table is the
    same class of event as a directory or a FIFO in its place, and the caller's exit contract has
    to be able to report it (F-10). A row naming a scope this adapter does not know is a hard load
    failure too — intersecting it away would turn a typo in the committed table into a quietly
    NARROWER binding with no refusal anywhere (F-14).
    """
    path = Path(path)
    try:
        mode = path.lstat().st_mode
    except OSError as exc:
        raise ValueError(f"bindings table is unreadable: {path} ({type(exc).__name__})")
    if not stat.S_ISREG(mode):
        raise ValueError(f"bindings table is not a regular file: {path}")
    table = json.loads(path.read_text(encoding="utf-8"))
    rows = list(table["bindings"])
    for row in rows:
        unknown = sorted(set(row.get("scopes", [])) - set(SCOPE_ORDER))
        if unknown:
            raise ValueError(
                f"bindings row {row.get('agent')} names unknown scopes: {', '.join(unknown)}")
    return rows


def authorize(tuple_obj: dict, table: list) -> dict | None:
    """Return the matching table row, or None.

    A tuple is authorized iff it carries EXACTLY the four fields and every one matches a row
    verbatim. Extra fields, missing fields and wrong values are all unauthorized: an allow-list
    over the whole input domain, never a filter (AF-AP-23, AF-AP-47).
    """
    if not isinstance(tuple_obj, dict):
        return None
    if set(tuple_obj) != set(TUPLE_FIELDS):
        return None
    for row in table:
        # A row that does not carry all four fields as non-empty strings can never authorize
        # anything. Without this, `row.get(f)` returns None for a field the row omits and a
        # presented tuple carrying JSON `null` for that field would MATCH — a malformed table
        # row turning into an authorization (class-18 fail-open, found by the class sweep).
        if any(not isinstance(row.get(f), str) or not row[f] for f in TUPLE_FIELDS):
            continue
        if all(tuple_obj[f] == row[f] for f in TUPLE_FIELDS):
            return row
    return None


def normalize_hit(hit: dict, scope: str, updated_at: str | None) -> dict:
    """One ai-memory search hit -> the adapter's record shape (docs/03 §4 read contract 4).

    `stable_id` is the page path: ai-memory identifies a page by (workspace, project, path)
    (`ApiSearchHit` `crates/ai-memory-web/src/routes/api.rs:1255-1263`), so the path is the part
    that is stable ACROSS the four scopes and is therefore the de-duplication key.
    `confidence` is the substrate's own FTS5 `rank`, carried verbatim — but only when it is a
    FINITE number. `serde_json` serialises a non-finite f64 as `null`, and Python would carry NaN
    or Infinity straight into the result file as non-RFC-8259 JSON that `jq`/`serde_json` refuse
    to read; the whole unusable class is rejected here (F-15).
    """
    rank = hit["rank"]
    if not isinstance(rank, (int, float)) or isinstance(rank, bool) or not math.isfinite(rank):
        raise ValueError(f"search hit {hit.get('path')!r} carries a non-finite rank: {rank!r}")
    return {
        "scope": scope,
        "stable_id": hit["path"],
        "timestamp": updated_at,
        "confidence": rank,
        "provenance": {
            "workspace": hit["workspace"],
            "project": hit["project"],
            "title": hit["title"],
            "kind": hit["kind"],
            "snippet": hit["snippet"],
            "shadowed_scopes": [],
        },
    }


def merge(records_by_scope: dict) -> list:
    """Agent -> Project -> Team -> Company precedence with deterministic de-duplication.

    A pure function of its input: no clock, no randomness, no dependence on dict insertion order
    or on the order of the records inside a scope. The higher-precedence copy of a stable id wins
    and names every scope it shadowed; the output is sorted by (precedence rank, stable id).
    """
    winners: dict = {}
    shadowed: dict = {}   # stable_id -> the SET of scopes that carried a lower-precedence copy
    for rank, scope in enumerate(SCOPE_ORDER):
        for record in sorted(records_by_scope.get(scope, []), key=lambda r: r["stable_id"]):
            sid = record["stable_id"]
            if sid in winners:
                shadowed.setdefault(sid, set()).add(scope)
                continue
            winner = json.loads(json.dumps(record, sort_keys=True, allow_nan=False))
            winner["scope"] = scope
            winner["_rank"] = rank
            winners[sid] = winner
    out = []
    for sid, winner in sorted(winners.items(), key=lambda kv: (kv[1]["_rank"], kv[0])):
        rank = winner.pop("_rank")
        winner["provenance"] = dict(winner["provenance"])
        # The winner's OWN scope is subtracted: two records with one stable id inside a single
        # scope would otherwise make that scope shadow itself, with duplicates (F-13).
        winner["provenance"]["shadowed_scopes"] = sorted(
            shadowed.get(sid, set()) - {winner["scope"]}, key=SCOPE_ORDER.index
        )
        winner["provenance"]["precedence_rank"] = rank
        out.append(winner)
    return out


def idempotency_path(session: str, turn: str, event_id: str) -> str:
    """The wiki path a (session, turn, event_id) key writes to.

    Derived, not caller-supplied, so a retry with the same key targets the same page and cannot
    escape the wiki root: ai-memory's `PagePath::new` rejects absolute, dot-segment, backslash and
    drive-prefixed paths (`crates/ai-memory-core/src/ids.rs:138-170`), and a hex digest satisfies
    `ensure_portable` (`:130-135`) on every platform.
    """
    key = "\x1f".join([str(session), str(turn), str(event_id)])
    return "observations/" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:16] + ".md"


class _Denied(Exception):
    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


class FactoryMemory:
    """The composite provider. Public surface: recall, write. Nothing else."""

    def __init__(self, base_url=DEFAULT_BASE_URL, token=None, bindings_path=BINDINGS_PATH,
                 timeout_s=DEFAULT_TIMEOUT_S, events=None):
        self._base_url = base_url.rstrip("/")
        self._token = token
        self._bindings_path = bindings_path
        self._timeout_s = timeout_s
        self._events = events
        self._seq = 0

    # ---- decision telemetry -------------------------------------------------
    def _emit(self, event, reason, **fields):
        """One JSON event per decision, carrying the reason (telemetry rule 1).

        Never carries the token: only the fields named here are serialised.
        """
        self._seq += 1
        payload = {"event": event, "reason": reason, "seq": self._seq}
        payload.update(fields)
        line = json.dumps(payload, sort_keys=True)
        print(line, file=sys.stderr)
        if self._events is not None:
            self._events.write(line + "\n")
            self._events.flush()

    # ---- authorization (no network) ----------------------------------------
    def _bind(self, tuple_obj):
        row = authorize(tuple_obj, load_bindings(self._bindings_path))
        if row is None:
            self._emit("scope_tuple_denied", REASONS["tuple_unauthorized"],
                       presented_fields=sorted(tuple_obj) if isinstance(tuple_obj, dict) else None)
            raise _Denied(REASONS["tuple_unauthorized"])
        binding = Binding(*[row[f] for f in TUPLE_FIELDS])
        authorized = [s for s in SCOPE_ORDER if s in set(row.get("scopes", []))]
        self._emit("scope_tuple_authorized", "authz: tuple matched the committed table",
                   agent=binding.agent, authorized_scopes=authorized)
        return binding, authorized

    # ---- HTTP ---------------------------------------------------------------
    def _request(self, method, path, body=None, event_path=None, event_fields=None):
        url = self._base_url + path
        data = None
        headers = {"Accept": "application/json"}
        if body is not None:
            data = json.dumps(body, sort_keys=True).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if self._token:
            headers["Authorization"] = "Bearer " + self._token
        self._emit("http_request", "substrate: request issued", method=method,
                   path=path if event_path is None else event_path, **(event_fields or {}))
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=self._timeout_s) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def _search(self, workspace, project, query, limit):
        qs = urllib.parse.urlencode(
            {"q": query, "workspace": workspace, "project": project, "limit": limit}
        )
        # The request carries the caller's query; telemetry carries only the route and a stable
        # digest, so event sinks can correlate equal searches without receiving query text (F-25).
        query_sha256_16 = hashlib.sha256(query.encode("utf-8")).hexdigest()[:16]
        return self._request("GET", "/api/v1/search?" + qs,
                             event_path="/api/v1/search",
                             event_fields={"query_sha256_16": query_sha256_16})

    def _page_times(self, workspace, project):
        listing = self._request(
            "GET",
            "/api/v1/workspaces/%s/projects/%s/pages"
            % (urllib.parse.quote(workspace, safe=""), urllib.parse.quote(project, safe="")),
        )
        return {p["path"]: p["updated_at"] for p in listing}

    # ---- public -------------------------------------------------------------
    def recall(self, tuple_obj, query, limit=DEFAULT_LIMIT):
        """Query every AUTHORIZED scope, merge with precedence, return an explicit status."""
        try:
            binding, authorized = self._bind(tuple_obj)
        except _Denied as denial:
            return {"status": "denied", "reason": denial.reason, "records": [],
                    "scopes_queried": [], "degraded_scopes": []}
        mapping = scopes_for(binding)
        by_scope, queried, degraded = {}, [], []
        for scope in authorized:
            workspace, project = mapping[scope]
            queried.append({"scope": scope, "workspace": workspace, "project": project})
            try:
                hits = self._search(workspace, project, query, limit)
                times = self._page_times(workspace, project)
                # The normalisation is INSIDE the try: a malformed 200 (a hit without `rank`,
                # an object where the route returns an array, a `null` body) is a read outage for
                # this scope, not a crash that exits with the same code as a denial (F-11).
                by_scope[scope] = [normalize_hit(h, scope, times.get(h["path"])) for h in hits]
            except (urllib.error.URLError, OSError, ValueError, TypeError, KeyError) as exc:
                # Any scope authorization ambiguity or read outage fails closed FOR THAT SCOPE and
                # is named in the status (docs/04 §4); never a silent partial.
                degraded.append(scope)
                self._emit("scope_degraded", "recall: scope unavailable",
                           scope=scope, error_type=type(exc).__name__)
                continue
        status = "degraded" if degraded else "ok"
        reason = REASONS["recall_degraded"] if degraded else REASONS["recall_ok"]
        if degraded:
            reason = reason + ": " + ",".join(sorted(degraded))
        result = {
            "status": status,
            "reason": reason,
            "binding": dict(zip(TUPLE_FIELDS, binding)),
            "scopes_queried": queried,
            "degraded_scopes": sorted(degraded),
            "records": merge(by_scope),
        }
        self._emit("recall_complete", reason,
                   record_count=len(result["records"]), degraded_scopes=result["degraded_scopes"])
        return result

    def write(self, tuple_obj, active_scope, record):
        """Append one attributed observation to the explicitly authorized ACTIVE scope only.

        Company (`_global`) is refused even to a binding the table authorizes for it: docs/03 §4
        reserves those writes for a reviewed companion workflow that does not exist yet.
        """
        try:
            binding, authorized = self._bind(tuple_obj)
        except _Denied as denial:
            return {"status": "denied", "reason": denial.reason}
        if active_scope not in SCOPE_ORDER or active_scope not in authorized:
            self._emit("write_scope_denied", REASONS["write_scope"],
                       requested_scope=active_scope, authorized_scopes=authorized)
            return {"status": "denied", "reason": REASONS["write_scope"]}
        if active_scope in WRITE_REVIEWED_SCOPES:
            self._emit("write_review_denied", REASONS["write_review"],
                       requested_scope=active_scope)
            return {"status": "denied", "reason": REASONS["write_review"]}
        missing = [k for k in ("session", "turn", "event_id", "body")
                   if not isinstance(record, dict) or not record.get(k)]
        if missing:
            self._emit("write_record_denied", REASONS["record_incomplete"], missing=sorted(missing))
            return {"status": "denied", "reason": REASONS["record_incomplete"]}
        workspace, project = scopes_for(binding)[active_scope]
        page_path = idempotency_path(record["session"], record["turn"], record["event_id"])
        key = {"session": record["session"], "turn": record["turn"],
               "event_id": record["event_id"]}
        base = {"status": "ok", "scope": active_scope, "workspace": workspace,
                "project": project, "page_path": page_path, "idempotency_key": key}
        # The durable intent is emitted BEFORE the side effect and keyed by the pre-action id, so a
        # crash between intent and commit is visible in the event stream rather than silent.
        self._emit("write_intent", "write: intent recorded",
                   scope=active_scope, project=project, page_path=page_path, key=key)
        try:
            existing = self._page_times(workspace, project)
        except (urllib.error.URLError, OSError, ValueError, TypeError, KeyError) as exc:
            self._emit("write_degraded", REASONS["write_degraded"],
                       scope=active_scope, error_type=type(exc).__name__)
            return dict(base, status="degraded", reason=REASONS["write_degraded"], page_id=None)
        if page_path in existing:
            self._emit("write_noop", REASONS["write_noop"], scope=active_scope,
                       project=project, page_path=page_path, key=key)
            return dict(base, reason=REASONS["write_noop"], page_id=None)
        body = {
            "workspace": workspace,
            "project": project,
            "path": page_path,
            "body": record["body"],
            "kind": record.get("kind", "fact"),
            "tier": record.get("tier", "semantic"),
            "tags": list(record.get("tags", [])),
            "pinned": False,
        }
        try:
            resp = self._request("POST", "/admin/write-page", body)
        except (urllib.error.URLError, OSError, ValueError, TypeError, KeyError) as exc:
            self._emit("write_degraded", REASONS["write_degraded"],
                       scope=active_scope, error_type=type(exc).__name__)
            return dict(base, status="degraded", reason=REASONS["write_degraded"], page_id=None)
        self._emit("write_committed", REASONS["write_ok"], scope=active_scope,
                   page_path=page_path, project=project, key=key)
        return dict(base, reason=REASONS["write_ok"], page_id=resp.get("page_id"))


def _read_json_file(path):
    p = Path(path)
    if not stat.S_ISREG(p.lstat().st_mode):
        raise ValueError(f"not a regular file: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def _read_token(path):
    """Read the bearer token at call time. The value is never printed or logged."""
    if path is None:
        return None
    p = Path(path)
    if not stat.S_ISREG(p.lstat().st_mode):
        raise ValueError(f"not a regular file: {p}")
    return p.read_text(encoding="utf-8").strip()


def _build_parser():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="verb", required=True)
    for verb in ("recall", "write"):
        p = sub.add_parser(verb)
        p.add_argument("--tuple-file", required=True)
        p.add_argument("--base-url", default=DEFAULT_BASE_URL)
        p.add_argument("--token-file")
        p.add_argument("--out")
        p.add_argument("--events")
        p.add_argument("--timeout-s", type=float, default=DEFAULT_TIMEOUT_S)
        if verb == "recall":
            p.add_argument("--query", required=True)
            p.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
        else:
            p.add_argument("--scope", required=True)
            p.add_argument("--record-file", required=True)
    return parser


def _main(argv=None):
    args = _build_parser().parse_args(argv)
    # DOCUMENTED LIMIT (F-21): every READ path in this module is lstat+S_ISREG guarded, but these
    # two writes follow symlinks and hardlinks. `--events`/`--out` are chosen by the runner, never
    # by a model or a request, so the asymmetry is a limit of this CLI, not a reachable hole; a
    # caller that lets an untrusted party pick either path needs O_NOFOLLOW|O_CREAT|O_EXCL here.
    events = open(args.events, "w", encoding="utf-8") if args.events else None
    try:
        tuple_obj = _read_json_file(args.tuple_file)
        adapter = FactoryMemory(base_url=args.base_url, token=_read_token(args.token_file),
                                timeout_s=args.timeout_s, events=events)
        if args.verb == "recall":
            result = adapter.recall(tuple_obj, args.query, args.limit)
        else:
            result = adapter.write(tuple_obj, args.scope, _read_json_file(args.record_file))
    finally:
        if events is not None:
            events.close()
    if args.out:
        Path(args.out).write_text(
            json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8")
    # The bare reason is the ONLY stdout line, so a spec can pin the complete string (AF-AP-29).
    print(result["reason"])
    return {"ok": 0, "denied": 1, "degraded": 3}[result["status"]]


def main(argv=None):
    """Exit 0 ok · 1 denied · 3 degraded · 70 unexpected.

    A crash must never share an exit code with a decision: a spec leg pinning
    `denied: scope-tuple-unauthorized` on exit 1 could not otherwise tell a refusal from a bug
    (F-11). `SystemExit` is re-raised so argparse keeps its own usage exit.
    """
    try:
        return _main(argv)
    except SystemExit:
        raise
    except Exception as exc:                                  # noqa: BLE001 - the top-level net
        print(f"factory_memory: unexpected {type(exc).__name__}: {exc}", file=sys.stderr)
        return 70


if __name__ == "__main__":
    sys.exit(main())
