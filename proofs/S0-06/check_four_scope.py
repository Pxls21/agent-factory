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

The substrate identity is checked first: a bundle whose commit or version is not the pin in
upstream.lock.yaml, or whose ai-memory posture is not the safe posture of docs/04 §6, cannot
grade any assertion. That check is also why a bundle recorded against the tests' local recording
HTTP server can never mint: it carries no real substrate.json.
"""
from __future__ import annotations

import json
import stat
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

EXPECTED_VERSION = "1.39.0"
SCOPE_ORDER = ("agent", "project", "team", "company")
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

REASONS = {
    "deferred": "deferred: S0-06 evidence not captured",
    "file": "leg: {name} missing or not a regular file",
    "status": "leg: {name} status {got}, expected {want}",
    "substrate_pin": "substrate: not the pinned ai-memory ({got})",
    "posture": "substrate: unsafe posture {key}={value}",
    "nondet": "merge: nondeterministic",
    "collision": "precedence: raw scopes carry {n} four-way collisions, expected 1",
    "variants": "precedence: raw scopes do not carry four distinct variants",
    "winner": "precedence: {sid} resolved to {scope}, expected agent",
    "shadow": "precedence: {sid} provenance missing shadowed scope {scope}",
    "write_found": "write: record found in {scope}",
    "write_absent": "write: record absent from agent",
    "write_retry": "write: idempotent retry produced {n} records",
    "leak": "leak: honeytoken {token} surfaced from {scope}",
    "leak_vacuous": "leak: honeytoken absent from its own scope",
    "leak_empty": "leak: authorized honeytoken {token} absent from recall",
    "denied_status": "denied: leg did not record the tuple denial",
    "denied_request": "denied: adapter recorded a request for the unauthorized tuple",
    "denied_stream": "denied: event stream unreadable",
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


def _read_json(root: Path, rel: str):
    try:
        return json.loads(_read_text(root, rel))
    except json.JSONDecodeError:
        raise Fail("file", name=rel)


def _require_status(doc, name, want="ok"):
    got = doc.get("status")
    if got != want:
        raise Fail("status", name=name, got=got, want=want)


def _pinned_commit() -> str:
    import yaml

    lock = yaml.safe_load((REPO_ROOT / "upstream.lock.yaml").read_text(encoding="utf-8"))
    return lock["selected_core"]["ai-memory"]["commit"]


def check_substrate(root: Path) -> dict:
    """Identity + safe posture of the instance the evidence came from."""
    doc = _read_json(root, "substrate.json")
    pinned = _pinned_commit()
    commit = doc.get("commit")
    if commit != pinned:
        raise Fail("substrate_pin", got=f"commit={commit}")
    version = doc.get("version")
    if version != EXPECTED_VERSION:
        raise Fail("substrate_pin", got=f"version={version}")
    digest = doc.get("binary_sha256")
    if not isinstance(digest, str) or len(digest) != 64 or set(digest) - set("0123456789abcdef"):
        raise Fail("substrate_pin", got=f"binary_sha256={digest}")
    posture = doc.get("posture") or {}
    for key, want in sorted(SAFE_POSTURE.items()):
        value = posture.get(key, "<absent>")
        if value != want:
            raise Fail("posture", key=key, value=value)
    return doc


def check_precedence(root: Path) -> None:
    """Assertion 2 — deterministic Agent-first merge over a real four-way collision."""
    first = _read_text(root, "precedence/recall-1.json")
    second = _read_text(root, "precedence/recall-2.json")
    if first != second:
        raise Fail("nondet")
    recall = json.loads(first)
    _require_status(recall, "precedence/recall-1.json")
    # Second instrument: the raw per-project reads, bypassing the adapter entirely.
    raw = {s: _read_json(root, f"precedence/raw-{s}.json") for s in SCOPE_ORDER}
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
    shadowed = merged[0].get("provenance", {}).get("shadowed_scopes", [])
    for scope in SCOPE_ORDER[1:]:
        if scope not in shadowed:
            raise Fail("shadow", sid=sid, scope=scope)


def check_write_scope(root: Path) -> None:
    """Assertion 3 — the write landed in agent--A only, and the retry was a no-op."""
    write = _read_json(root, "write-scope/write.json")
    _require_status(write, "write-scope/write.json")
    retry = _read_json(root, "write-scope/retry.json")
    _require_status(retry, "write-scope/retry.json")
    page_path = write["page_path"]
    raw = {s: _read_json(root, f"write-scope/raw-{s}.json") for s in SCOPE_ORDER}
    for scope in SCOPE_ORDER[1:]:
        if any(e["path"] == page_path for e in raw[scope]):
            raise Fail("write_found", scope=scope)
    found = [e for e in raw["agent"] if e["path"] == page_path]
    if not found:
        raise Fail("write_absent")
    if len(found) != 1 or retry.get("page_path") != page_path:
        raise Fail("write_retry", n=len(found))


def check_leak(root: Path) -> None:
    """Assertion 4 — staged honeytokens never cross a scope boundary they are not authorized for.

    The oracle self-tests in both directions (AF-AP-52): the forbidden tokens must be PRESENT in
    their own scope's raw read (else the absence proves nothing) and the authorized tokens must be
    present in the recall (else the recall was empty and every absence is vacuous).
    """
    tokens = _read_json(root, "leak/honeytokens.json")
    recall_text = _read_text(root, "leak/recall.json")
    _require_status(json.loads(recall_text), "leak/recall.json")
    raw_text = {s: _read_text(root, f"leak/raw-{s}.json") for s in SCOPE_ORDER}
    for scope in LEAK_FORBIDDEN:
        token = tokens[scope]
        if token not in raw_text[scope]:
            raise Fail("leak_vacuous")
        if token in recall_text:
            raise Fail("leak", token=token, scope=scope)
    for scope in LEAK_AUTHORIZED:
        token = tokens[scope]
        if token not in recall_text:
            raise Fail("leak_empty", token=token)


def check_denied(root: Path) -> None:
    """Assertion 1 — the unauthorized tuple was refused, and no request left the adapter."""
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
    if any(e["event"] == "http_request" for e in events):
        raise Fail("denied_request")
    if not any(e["event"] == "scope_tuple_denied" for e in events):
        raise Fail("denied_status")


def run(root: Path) -> str:
    if not root.is_dir():
        raise Deferred()
    substrate = check_substrate(root)
    check_denied(root)
    check_precedence(root)
    check_write_scope(root)
    check_leak(root)
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
        print(run(Path(argv[0]).resolve()))
    except Deferred:
        print(REASONS["deferred"])
        return 2
    except Fail as failure:
        print(failure.reason)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
